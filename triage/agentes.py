"""Agentes en terreno: enrolamiento y validación de tareas de campo (B.6.4)."""
from __future__ import annotations

import hashlib
import json
import random
import sqlite3
from datetime import datetime

from datos import db as datos_db
from triage import antifraude, censo, config, geo
from triage import db as tdb
from triage.entrada_datos import a_iso, parsear_familias, parsear_productos


def _exigir_humano(quien):
    if not config.es_humano(quien):
        raise PermissionError("Solo una persona puede enrolar agentes o líderes.")


def _registrar(con, remitente_hash, rol, zonas, organizacion, quien, ahora):
    _exigir_humano(quien)
    momento = a_iso(ahora) if ahora else datos_db.ahora()
    zonas_json = json.dumps(sorted({int(z) for z in (zonas or [])}))
    con.execute("INSERT INTO remitentes(remitente_hash, rol, zonas, organizacion, primer_contacto) "
                "VALUES (?,?,?,?,?) ON CONFLICT(remitente_hash) DO UPDATE SET rol=excluded.rol, "
                "zonas=excluded.zonas, organizacion=excluded.organizacion, estado='activo'",
                (remitente_hash, rol, zonas_json, organizacion, momento))
    con.commit()
    datos_db.anotar(con, quien, f"enrolar_{rol}",
                    json.dumps({"remitente": remitente_hash[:8], "zonas": json.loads(zonas_json)}))


def enrolar(con: sqlite3.Connection, remitente_hash: str, organizacion: str, zonas, quien: str,
            ahora: datetime | None = None) -> None:
    """Crea o actualiza el remitente con rol 'agente'. `quien` debe ser una persona."""
    _registrar(con, remitente_hash, "agente", zonas, organizacion, quien, ahora)


def registrar_lider(con: sqlite3.Connection, remitente_hash: str, zonas, quien: str,
                    organizacion: str | None = None, ahora: datetime | None = None) -> None:
    """Registra un líder comunitario para sus zonas. `quien` debe ser una persona."""
    _registrar(con, remitente_hash, "lider", zonas, organizacion, quien, ahora)


def _rechazo(motivo):
    return {"ok": False, "motivo": motivo, "solicitudes": [], "consolidadas": [], "en_cola": [],
            "auditoria": False}


def validar(con: sqlite3.Connection, agente_hash: str, tarea_id: int, lat, lon, necesidades,
            ahora: datetime, params: dict | None = None, procesar=None) -> dict:
    """Valida una tarea de campo desde el terreno y crea las solicitudes del agente.

    `procesar(con, sid, desde, params, ahora)` corre los pasos 7 a 10 del embudo; por defecto
    embudo.reprocesar.
    """
    p = params or config.cargar(con)
    rem = con.execute("SELECT * FROM remitentes WHERE remitente_hash=?", (agente_hash,)).fetchone()
    if rem is None or rem["rol"] != "agente" or rem["estado"] != "activo":
        return _rechazo("no_es_agente")
    tarea = con.execute("SELECT * FROM tareas_campo WHERE id=?", (tarea_id,)).fetchone()
    if tarea is None or tarea["estado"] in ("validada", "cerrada"):
        return _rechazo("tarea_invalida")
    zona = censo.zona_por_id(con, tarea["zona_id"])
    if zona is None or not geo.coordenada_valida(lat, lon):
        return _rechazo("ubicacion_agente")
    la, lo = geo.numero(lat), geo.numero(lon)
    limite = p["agente_r_poligono_m"] if zona.poligono is not None else p["agente_r_centroide_m"]
    if geo.distancia_a_zona_m(la, lo, zona) > limite:
        return _rechazo("ubicacion_agente")

    if procesar is None:
        from triage import embudo
        procesar = embudo.procesar_paso
    auditoria = random.Random(f"{p['semilla']}:{agente_hash}:{tarea_id}").random() < p["auditoria_agente"]
    creadas, cubiertas = [], []
    for i, nec in enumerate(necesidades or []):
        nec = nec if isinstance(nec, dict) else {}
        productos = parsear_productos(nec.get("productos"))
        texto = str(nec.get("texto") or "")
        marcas = ["validada_agente"] + (["auditoria_agente"] if auditoria else [])
        firma = f"{agente_hash}{tarea_id}{i}{a_iso(ahora)[:16]}{antifraude.normalizar_texto(texto)}"
        cur = con.execute(
            "INSERT OR IGNORE INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, canal, "
            "texto, zona_id, lat, lon, tipo_punto, productos, familias_declaradas, lugar_confirmado, "
            "marcas, tarea_id) VALUES (?,?,?,'agente',?,?,?,?,?,?,?,1,?,?)",
            (a_iso(ahora), hashlib.sha256(firma.encode()).hexdigest(), agente_hash, texto, zona.id,
             la, lo, nec.get("tipo_punto"), json.dumps(productos),
             parsear_familias(nec.get("familias")), json.dumps(marcas), tarea_id))
        if cur.rowcount == 0:
            continue
        sid = cur.lastrowid
        procesar(con, sid, 7, p, ahora)
        creadas.append(sid)
        cubiertas.append((sid, set(productos)))

    consolidadas, en_cola = [], []
    for f in con.execute("SELECT id, productos FROM solicitudes WHERE tarea_id=? "
                         "AND estado='espera_agente'", (tarea_id,)).fetchall():
        prods = set(parsear_productos(f["productos"]))
        madre = next((sid for sid, ps in cubiertas
                      if antifraude.jaccard(prods, ps) >= p["jaccard_productos"]), None)
        if madre is not None:
            con.execute("UPDATE solicitudes SET estado='consolidada', consolidada_en=? WHERE id=?",
                        (madre, f["id"]))
            consolidadas.append(f["id"])
        else:
            con.execute("UPDATE solicitudes SET estado='en_cola' WHERE id=?", (f["id"],))
            en_cola.append(f["id"])
    con.execute("UPDATE tareas_campo SET estado='validada', agente_hash=?, cerrada_en=? WHERE id=?",
                (agente_hash, a_iso(ahora), tarea_id))
    tdb.anotar_regla(con, "regla:triage", "tarea_validada",
                     {"tarea_id": tarea_id, "solicitudes": creadas, "auditoria": auditoria}, ahora)
    con.commit()
    return {"ok": True, "motivo": None, "solicitudes": creadas, "consolidadas": consolidadas,
            "en_cola": en_cola, "auditoria": auditoria}
