"""El embudo de triage (B.7): de la solicitud cruda a confirmada por regla, cola o cuarentena.

El modelo (extractor) solo lee y estructura; las reglas calculan; una persona decide.
Ninguna regla confirma (estado 'confirmada') ni descarta: eso lo hace cambiar_estado con un humano.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

import numpy as np

from datos import db as datos_db
from triage import antifraude, censo, cluster, cola, config, debiles, geo, puntaje
from triage import db as tdb
from triage.entrada_datos import (a_iso, normalizar_fila, parsear_bool, parsear_familias,
                                  parsear_fecha, parsear_productos)

ESTADOS = ("recibida", "cuarentena", "espera_agente", "consolidada", "confirmada_regla", "en_cola",
           "confirmada", "descartada")
ESTADOS_CONFIRMADOS = ("confirmada_regla", "confirmada")
ESTADOS_RETRO = ("recibida", "en_cola", "confirmada_regla", "consolidada")
FUERA_DE_CONSOLIDACION = ("descartada", "cuarentena", "espera_agente")
MARCAS_RECALCULADAS = ("extraccion_fallida", "familias_supuestas", "sin_texto", "extractor_fallo",
                       "sin_ubicar", "asignacion_aproximada", "sobre_tope", "familias_absurdas",
                       "concentracion_remitente", "salto_ubicacion", "auditoria")
QUIEN_REGLA = "regla:triage"


@dataclass
class Contexto:
    params: dict
    version: int
    ahora: datetime
    extractor: Callable | None = None
    integrar: bool = False
    zonas: list = field(default_factory=list)
    zonas_por_id: dict = field(default_factory=dict)
    tejas: dict = field(default_factory=dict)
    zonas_confirmadas: set = field(default_factory=set)
    umbral: dict | None = None


def _contexto(con, params, ahora, extractor, integrar) -> Contexto:
    version, vigentes = config.version_vigente(con)
    p = config.completar(params) if params is not None else vigentes
    t = parsear_fecha(ahora) if ahora is not None else parsear_fecha(datos_db.ahora())
    zonas = censo.zonas_de_base(con)
    return Contexto(params=p, version=version, ahora=t, extractor=extractor, integrar=integrar,
                    zonas=zonas, zonas_por_id={z.id: z for z in zonas})


def _lista_json(v) -> list:
    try:
        x = json.loads(v) if isinstance(v, str) else (v or [])
    except (TypeError, ValueError):
        return []
    return x if isinstance(x, list) else []


def hash_mensaje(remitente_hash: str, texto, t: datetime) -> str:
    minuto = a_iso(t)[:16]
    return hashlib.sha256(f"{remitente_hash}{antifraude.normalizar_texto(texto)}{minuto}".encode()
                          ).hexdigest()


# ---------- paso 1: ingesta ----------
def _ingestar(con, fila: dict) -> int | None:
    t = parsear_fecha(fila["recibida_en"])
    iso = a_iso(t)
    rem = fila["remitente_hash"]
    con.execute("INSERT OR IGNORE INTO remitentes(remitente_hash, primer_contacto) VALUES (?,?)",
                (rem, iso))
    con.execute("UPDATE remitentes SET primer_contacto=? WHERE remitente_hash=? AND "
                "(primer_contacto IS NULL OR primer_contacto > ?)", (iso, rem, iso))
    cur = con.execute(
        "INSERT OR IGNORE INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, canal, texto, "
        "lat, lon, tipo_punto, productos, familias_declaradas, lugar_confirmado) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (iso, hash_mensaje(rem, fila.get("texto"), t), rem, fila.get("canal") or "chat",
         fila.get("texto") or "", fila.get("lat"), fila.get("lon"), fila.get("tipo_punto"),
         json.dumps(fila.get("productos") or [], ensure_ascii=False), fila.get("familias"),
         1 if fila.get("lugar_confirmado") else 0))
    return cur.lastrowid if cur.rowcount else None


# ---------- utilidades de estado ----------
def _cargar(con, sid) -> dict:
    f = con.execute("SELECT * FROM solicitudes WHERE id=?", (sid,)).fetchone()
    s = dict(f)
    s["marcas"] = set(_lista_json(f["marcas"]))
    s["productos"] = parsear_productos(f["productos"])
    s["senales"] = {}
    return s


def _guardar(con, s: dict) -> None:
    con.execute(
        "UPDATE solicitudes SET canal=?, zona_id=?, lat=?, lon=?, tipo_punto=?, productos=?, "
        "familias_declaradas=?, familias_efectivas=?, lugar_confirmado=?, estado=?, "
        "motivo_cuarentena=?, marcas=?, senales=?, p_real=?, cluster_id=?, consolidada_en=?, "
        "pedido_id=?, tarea_id=? WHERE id=?",
        (s["canal"], s["zona_id"], s["lat"], s["lon"], s["tipo_punto"],
         json.dumps(s["productos"], ensure_ascii=False), s["familias_declaradas"],
         s["familias_efectivas"], 1 if s["lugar_confirmado"] else 0, s["estado"],
         s["motivo_cuarentena"], json.dumps(sorted(s["marcas"])),
         json.dumps(s["senales"], sort_keys=True), s["p_real"], s["cluster_id"],
         s["consolidada_en"], s["pedido_id"], s["tarea_id"], s["id"]))


def _cuarentena(con, s, motivo) -> None:
    s["estado"] = "cuarentena"
    s["motivo_cuarentena"] = motivo
    _guardar(con, s)


def _remitente(con, rem_hash):
    return con.execute("SELECT * FROM remitentes WHERE remitente_hash=?", (rem_hash,)).fetchone()


# ---------- paso 2: prefiltro sin modelo ----------
def _prefiltro(con, s, rem, t, p) -> str | None:
    if rem is not None and rem["estado"] != "activo":
        return f"remitente_{rem['estado']}"
    if s["canal"] == "agente":
        return None
    previos = [parsear_fecha(r[0]) for r in con.execute(
        "SELECT recibida_en FROM solicitudes WHERE remitente_hash=? AND id != ? AND "
        "(recibida_en < ? OR (recibida_en = ? AND id < ?)) ORDER BY recibida_en, id",
        (s["remitente_hash"], s["id"], s["recibida_en"], s["recibida_en"], s["id"]))]
    registrado = rem is not None and rem["rol"] in ("lider", "agente")
    capacidad = p["B_registrado"] if registrado else p["B_ciudadano"]
    if not antifraude.CubetaFichas(capacidad, p["recarga_h"]).admite(previos, t):
        return "limite_remitente"
    if antifraude.cadencia(previos + [t], p["cv_min"], p["n_min_cadencia"]):
        return "cadencia"
    return None


# ---------- paso 3: extracción ----------
def _extraer(s, ctx: Contexto) -> None:
    if ctx.extractor is not None:
        try:
            r = ctx.extractor(s["texto"] or "")
        except Exception:       # extractor ausente o roto: nunca tumba el lote
            r = None
        if not isinstance(r, dict):
            s["marcas"].add("extractor_fallo")
        else:
            fam = parsear_familias(r.get("familias"))
            if fam is not None:
                s["familias_declaradas"] = fam
            prods = parsear_productos(r.get("productos"))
            if prods:
                s["productos"] = prods
            lat, lon = geo.numero(r.get("lat")), geo.numero(r.get("lon"))
            if lat is not None and lon is not None:
                s["lat"], s["lon"] = lat, lon
            lc = parsear_bool(r.get("lugar_confirmado"))
            if lc is not None:
                s["lugar_confirmado"] = lc
            if r.get("tipo_punto"):
                s["tipo_punto"] = str(r["tipo_punto"]).strip().lower()
    if parsear_familias(s["familias_declaradas"]) is None:
        s["familias_declaradas"] = None
    if not str(s["texto"] or "").strip():
        s["marcas"].add("sin_texto")
    sin_lugar = s["lat"] is None or s["lon"] is None
    if sin_lugar and s["familias_declaradas"] is None and not s["productos"]:
        s["marcas"].add("extraccion_fallida")
    if s["familias_declaradas"] is None:
        s["marcas"].add("familias_supuestas")


def _familias(s, p) -> int:
    return s["familias_declaradas"] if s["familias_declaradas"] else p["f_bar"]


# ---------- paso 6: retroactividad del texto coordinado ----------
def _retro_cuarentena(con, grupo, t, motivo) -> list[int]:
    ids = []
    for g in grupo:
        if g["estado"] in ESTADOS_RETRO and g["pedido_id"] is None:
            con.execute("UPDATE solicitudes SET estado='cuarentena', motivo_cuarentena=? WHERE id=?",
                        (motivo, g["id"]))
            ids.append(g["id"])
    if ids:
        tdb.anotar_regla(con, QUIEN_REGLA, "cuarentena_retroactiva", {"ids": ids, "motivo": motivo}, t)
    return ids


# ---------- paso 7: consolidación ----------
def consolidar(grupo: list[dict], umbral: float = 0.5) -> list[tuple[int, int]]:
    """Pares (hija, madre) dentro de cada clúster: la más antigua con Jaccard de productos ≥ umbral.

    Cada elemento de `grupo`: {id, recibida_en, productos, cluster_id, estado}. Interfaz v0.3.
    """
    pares = []
    por_cluster: dict = {}
    for g in grupo:
        if g.get("cluster_id", cluster.RUIDO) == cluster.RUIDO:
            continue
        por_cluster.setdefault(g["cluster_id"], []).append(g)
    for miembros in por_cluster.values():
        raices = []
        for m in sorted(miembros, key=lambda x: (x["recibida_en"], x["id"])):
            if m.get("estado") == "consolidada":
                continue
            madre = next((r for r in raices if antifraude.jaccard(r["productos"], m["productos"])
                          >= umbral), None)
            if madre is not None:
                pares.append((m["id"], madre["id"]))
            else:
                raices.append(m)
    return pares


def _buscar_madre(con, s, zona, t, p) -> tuple[int | None, int | None]:
    marcas = ",".join("?" * len(FUERA_DE_CONSOLIDACION))
    filas = con.execute(
        f"SELECT id, lat, lon, recibida_en, productos, estado FROM solicitudes WHERE zona_id=? "
        f"AND recibida_en >= ? AND recibida_en <= ? AND estado NOT IN ({marcas}) "
        f"AND lat IS NOT NULL AND lon IS NOT NULL ORDER BY recibida_en, id",
        (zona.id, a_iso(t - timedelta(hours=p["eps_t_h"])), a_iso(t), *FUERA_DE_CONSOLIDACION)
    ).fetchall()
    if not any(f["id"] == s["id"] for f in filas):
        return None, None
    tiempos = [(parsear_fecha(f["recibida_en"]) - t).total_seconds() / 3600 for f in filas]
    etiquetas = cluster.st_dbscan(np.array([f["lat"] for f in filas], dtype=float),
                                  np.array([f["lon"] for f in filas], dtype=float),
                                  np.array(tiempos), p["eps_s_m"], p["eps_t_h"], p["min_samples"])
    grupo = [{"id": f["id"], "recibida_en": f["recibida_en"], "estado": f["estado"],
              "productos": set(parsear_productos(f["productos"])), "cluster_id": int(e)}
             for f, e in zip(filas, etiquetas)]
    propio = next(g for g in grupo if g["id"] == s["id"])
    if propio["cluster_id"] == cluster.RUIDO:
        return None, None
    raiz_cluster = min(g["id"] for g in grupo if g["cluster_id"] == propio["cluster_id"])
    madre = dict(consolidar(grupo, p["jaccard_productos"])).get(s["id"])
    return madre, raiz_cluster


def _raiz(con, sid) -> int:
    vistos = set()
    while sid not in vistos:
        vistos.add(sid)
        f = con.execute("SELECT consolidada_en FROM solicitudes WHERE id=?", (sid,)).fetchone()
        if f is None or f["consolidada_en"] is None:
            return sid
        sid = f["consolidada_en"]
    return sid


def _consolidar_en(con, s, madre_id, t, ctx: Contexto) -> None:
    p = ctx.params
    s["estado"] = "consolidada"
    s["consolidada_en"] = madre_id
    s["familias_efectivas"] = 0
    m = con.execute("SELECT * FROM solicitudes WHERE id=?", (madre_id,)).fetchone()
    valores = [v for v in (m["familias_declaradas"], s["familias_declaradas"]) if v]
    nuevo = max(valores) if valores else None
    if nuevo is not None and nuevo != m["familias_declaradas"]:
        con.execute("UPDATE solicitudes SET familias_declaradas=? WHERE id=?", (nuevo, madre_id))
        if m["estado"] in ESTADOS_CONFIRMADOS and m["zona_id"] is not None:
            zona = censo.zona_por_id(con, m["zona_id"])
            disp = censo.tope_familias(zona, p) - censo.cupo_consumido(
                con, zona.id, parsear_fecha(m["recibida_en"]), p, excluir_id=madre_id)
            efectivas = max(0, min(nuevo, disp))
            con.execute("UPDATE solicitudes SET familias_efectivas=? WHERE id=?", (efectivas, madre_id))
            if ctx.integrar and m["pedido_id"] is not None:
                con.execute("UPDATE pedidos SET familias=?, kg_estimado=? WHERE id=?",
                            (efectivas, efectivas * p["kg_por_familia"], m["pedido_id"]))
    _guardar(con, s)


# ---------- paso 8: topes ----------
def _topes(con, s, rem, zona, t, ctx: Contexto) -> None:
    p = ctx.params
    if s["familias_declaradas"] is None:
        s["marcas"].add("familias_supuestas")
    fam = _familias(s, p)
    if zona is None:
        s["familias_efectivas"] = fam
        return
    T = censo.tope_familias(zona, p)
    disp = T - censo.cupo_consumido(con, zona.id, t, p, excluir_id=s["id"])
    s["familias_efectivas"] = max(0, min(fam, disp))
    if fam > disp:
        s["marcas"].add("sobre_tope")
    if fam > p["factor_absurdo"] * T:
        s["marcas"].update({"sobre_tope", "familias_absurdas"})
    exento = rem is not None and (rem["rol"] == "agente" or antifraude.es_lider_de(rem, zona.id))
    if not exento:
        previas = con.execute(
            "SELECT COALESCE(SUM(familias_efectivas), 0) FROM solicitudes WHERE remitente_hash=? "
            "AND zona_id=? AND estado IN (?, ?) AND recibida_en > ? AND recibida_en <= ? AND id != ?",
            (s["remitente_hash"], zona.id, *ESTADOS_CONFIRMADOS,
             a_iso(t - timedelta(hours=p["ciclo_h"])), a_iso(t), s["id"])).fetchone()[0]
        if previas + fam > p["phi"] * T:
            s["marcas"].add("concentracion_remitente")
    if s["canal"] != "agente" and antifraude.hay_salto(con, s["id"], rem, zona, t,
                                                       ctx.zonas_por_id, p):
        s["marcas"].add("salto_ubicacion")


# ---------- paso 9: señales ----------
def _senales(s, rem, zona) -> list[str]:
    activas = []
    if zona is not None and antifraude.es_lider_de(rem, zona.id):
        activas.append("lider_registrado")
    if s["lugar_confirmado"]:
        activas.append("lugar_confirmado")
    if zona is not None and "sobre_tope" not in s["marcas"]:
        activas.append("dentro_de_tope")
    for m in ("sobre_tope", "concentracion_remitente", "salto_ubicacion", "inyeccion",
              "validada_agente"):
        if m in s["marcas"]:
            activas.append(m)
    return activas


# ---------- paso 10: decisión ----------
def _sin_numeros_largos(texto) -> str:
    return re.sub(r"\+?\d[\d\s\-]{6,}\d", "[número]", str(texto or ""))


def _integrar_pedido(con, s, zona, ctx: Contexto) -> None:
    """Crea o actualiza el pedido confirmado (solo con integrar=True)."""
    p = ctx.params
    if zona is None:
        return
    f = con.execute("SELECT id FROM puntos WHERE nombre=? ORDER BY id LIMIT 1", (zona.nombre,)).fetchone()
    punto_id = f["id"] if f else con.execute(
        "INSERT INTO puntos(nombre, barrio, comuna, lat, lon, critico) VALUES (?,?,?,?,?,?)",
        (zona.nombre, zona.nombre, zona.comuna, zona.lat, zona.lon, zona.critico or 0)).lastrowid
    fam = s["familias_efectivas"] or 0
    productos = json.dumps([{"producto": x, "kg": None} for x in s["productos"]], ensure_ascii=False)
    urgencia = 3 if cola.u_punto(s["tipo_punto"], zona, p) > p["u_otro"] else 2
    if s["pedido_id"]:
        con.execute("UPDATE pedidos SET familias=?, kg_estimado=?, productos=?, estado='confirmado' "
                    "WHERE id=?", (fam, fam * p["kg_por_familia"], productos, s["pedido_id"]))
    else:
        s["pedido_id"] = con.execute(
            "INSERT INTO pedidos(creado_en, punto_id, familias, kg_estimado, productos, urgencia, "
            "estado, texto_original, remitente_hash) VALUES (?,?,?,?,?,?, 'confirmado', ?, ?)",
            (s["recibida_en"], punto_id, fam, fam * p["kg_por_familia"], productos, urgencia,
             _sin_numeros_largos(s["texto"]), s["remitente_hash"])).lastrowid


def _decidir(con, s, zona, t, ctx: Contexto) -> None:
    p = ctx.params
    vals = [r[0] for r in con.execute(
        "SELECT p_real FROM solicitudes WHERE recibida_en > ? AND recibida_en <= ? AND id != ? "
        "AND p_real IS NOT NULL", (a_iso(t - timedelta(hours=p["ventana_umbral_h"])), a_iso(t), s["id"]))]
    det = puntaje.umbral_detalle(vals, p)
    ctx.umbral = det
    bloqueo = s["marcas"] & set(p["bloqueantes"])
    if s["p_real"] >= det["tau"] and not bloqueo:
        if random.Random(f"{p['semilla']}:{s['hash_mensaje']}").random() < p["epsilon"]:
            s["estado"] = "en_cola"
            s["marcas"].add("auditoria")
            return
        s["estado"] = "confirmada_regla"
        tdb.anotar_regla(con, f"regla:v{ctx.version}", "confirmar_solicitud",
                         {"id": s["id"], "p_real": round(s["p_real"], 4),
                          "tau": round(det["tau"], 4)}, t)
        if zona is not None:
            ctx.zonas_confirmadas.add(zona.id)
        if ctx.integrar:
            _integrar_pedido(con, s, zona, ctx)
    else:
        s["estado"] = "en_cola"


# ---------- recorrido de una solicitud ----------
def _procesar(con, sid: int, ctx: Contexto, desde: int = 2, liberada: bool = False) -> None:
    p = ctx.params
    s = _cargar(con, sid)
    t = parsear_fecha(s["recibida_en"])
    rem = _remitente(con, s["remitente_hash"])
    s["marcas"] -= set(MARCAS_RECALCULADAS)
    if s["canal"] == "agente" and (rem is None or rem["rol"] != "agente"):
        s["canal"] = "chat"
        s["marcas"].add("canal_no_verificado")
    if liberada:
        s["marcas"].add("liberada")

    # 2. Prefiltro sin modelo (B.4.1, B.4.5, B.4.7)
    if antifraude.detectar_inyeccion(s["texto"]):
        s["marcas"].add("inyeccion")
    if desde <= 2:
        motivo = _prefiltro(con, s, rem, t, p)
        if motivo:
            s["zona_id"] = geo.asignar_zona(s["lat"], s["lon"], ctx.zonas, params=p)[0]
            return _cuarentena(con, s, motivo)
    # 3. Extracción
    if desde <= 3:
        _extraer(s, ctx)
    # 4. Zona
    if desde <= 4:
        zid, marcas = geo.asignar_zona(s["lat"], s["lon"], ctx.zonas, params=p)
        s["zona_id"] = zid
        s["marcas"].update(marcas)
    elif s["zona_id"] is None:
        s["marcas"].add("sin_ubicar")
    con.execute("UPDATE solicitudes SET zona_id=?, lat=?, lon=? WHERE id=?",
                (s["zona_id"], s["lat"], s["lon"], sid))
    zona = censo.zona_por_id(con, s["zona_id"])

    # 5. Zona débil: solo entra por el agente
    if zona is not None and desde <= 5 and zona.es_debil and s["canal"] != "agente":
        s["tarea_id"] = debiles.tarea_para_zona(con, zona, t, p)
        s["estado"] = "espera_agente"
        return _guardar(con, s)

    # 6. Ráfaga y coordinación
    madre_forzada = None
    if zona is not None and desde <= 6 and s["canal"] != "agente":
        r = antifraude.evaluar_rafaga(con, zona, t, p)
        registrado = rem is not None and rem["rol"] in ("lider", "agente")
        nuevo = antifraude.es_nuevo(rem, t, p)
        if r["en_rafaga"] and not r["global"] and nuevo and not registrado and not liberada:
            return _cuarentena(con, s, "rafaga_zona")
        grupo = antifraude.grupo_coordinado(con, sid, s["remitente_hash"], s["texto"], t, p, ctx.tejas)
        hashes = {s["remitente_hash"]} | {g["remitente_hash"] for g in grupo}
        if len(hashes) >= p["k_coordinado"] and not liberada:
            rems = {h: _remitente(con, h) for h in hashes}
            nuevos = sum(antifraude.es_nuevo(rems[h], t, p) for h in hashes)
            if nuevos >= p["min_nuevos_coord"]:
                if any(antifraude.es_lider_de(rems[h], zona.id) for h in hashes):
                    vivos = [g for g in grupo if g["estado"] not in ("descartada", "cuarentena")]
                    if vivos:
                        primero = min(vivos, key=lambda g: (g["recibida_en"], g["id"]))
                        madre_forzada = _raiz(con, primero["id"])
                else:
                    _retro_cuarentena(con, grupo, t, "texto_coordinado")
                    return _cuarentena(con, s, "texto_coordinado")

    # 7. Consolidación
    if zona is not None and desde <= 7:
        madre, raiz_cluster = (madre_forzada, None) if madre_forzada else _buscar_madre(con, s, zona, t, p)
        if raiz_cluster is not None:
            s["cluster_id"] = raiz_cluster
        if madre is not None and madre != sid:
            return _consolidar_en(con, s, madre, t, ctx)

    # 8. Topes
    _topes(con, s, rem, zona, t, ctx)
    # 9. Puntaje
    s["p_real"], s["senales"] = puntaje.p_real(_senales(s, rem, zona), p)
    # 10. Decisión
    _decidir(con, s, zona, t, ctx)
    _guardar(con, s)


def _rescatar(con, fila: dict, error: str) -> None:
    """Tras un error interno, la solicitud se conserva en cruda y va a la cola humana."""
    try:
        sid = _ingestar(con, fila)
        if sid is not None:
            con.execute("UPDATE solicitudes SET estado='en_cola', marcas=? WHERE id=?",
                        (json.dumps(["error_interno"]), sid))
    except Exception:   # si ni siquiera se puede guardar, queda solo en el resumen
        pass


def _actualizar_lambdas(con, ctx: Contexto) -> None:
    """Promedio móvil exponencial de lambda con solicitudes confirmadas (nunca en cuarentena)."""
    p = ctx.params
    w = p["w_rafaga_h"]
    for zid in sorted(ctx.zonas_confirmadas):
        zona = censo.zona_por_id(con, zid)
        n = con.execute("SELECT COUNT(*) FROM solicitudes WHERE zona_id=? AND estado IN (?, ?) "
                        "AND recibida_en > ? AND recibida_en <= ?",
                        (zid, *ESTADOS_CONFIRMADOS, a_iso(ctx.ahora - timedelta(hours=w)),
                         a_iso(ctx.ahora))).fetchone()[0]
        viejo = antifraude.lambda_zona(zona, p)
        nuevo = (1 - p["eta"]) * viejo + p["eta"] * (n / w)
        con.execute("UPDATE zonas SET lambda_h=? WHERE id=?", (max(p["lambda_min"], nuevo), zid))


def _contar(filas) -> dict:
    por_estado, por_marca, motivos = {}, {}, {}
    for f in filas:
        por_estado[f["estado"]] = por_estado.get(f["estado"], 0) + 1
        for m in _lista_json(f["marcas"]):
            por_marca[m] = por_marca.get(m, 0) + 1
        if f["motivo_cuarentena"]:
            motivos[f["motivo_cuarentena"]] = motivos.get(f["motivo_cuarentena"], 0) + 1
    return {"por_estado": dict(sorted(por_estado.items())), "por_marca": dict(sorted(por_marca.items())),
            "motivos_cuarentena": dict(sorted(motivos.items()))}


def resumen_base(con) -> dict:
    """Conteos de toda la tabla de solicitudes."""
    filas = con.execute("SELECT estado, marcas, motivo_cuarentena FROM solicitudes").fetchall()
    return {"total": len(filas), **_contar(filas)}


def procesar_lote(con: sqlite3.Connection, solicitudes: list[dict], params: dict | None = None,
                  ahora: datetime | None = None, extractor: Callable | None = None,
                  integrar: bool = False) -> dict:
    """Corre los pasos 1 a 11 sobre un lote. Devuelve un resumen por estado y por marca."""
    ctx = _contexto(con, params, ahora, extractor, integrar)
    p = ctx.params
    resumen = {"recibidas": len(solicitudes or []), "nuevas": 0, "duplicado_exacto": 0,
               "filas_invalidas": [], "error_interno": [], "zonas_debiles_nuevas": [],
               "tareas_escaladas": [], "eventos_globales": 0, "umbral": None}
    filas = []
    for i, s in enumerate(solicitudes or [], start=1):
        try:
            fila, errores = normalizar_fila(s, i)
        except Exception as e:
            fila, errores = None, [{"fila": i, "campo": "fila", "motivo": f"error: {type(e).__name__}",
                                    "rechazada": True}]
        if fila is None:
            resumen["filas_invalidas"].extend(errores)
        else:
            filas.append(fila)
    filas.sort(key=lambda f: (f["recibida_en"], f["fila"]))
    eventos_antes = con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='posible_nuevo_evento'"
                                ).fetchone()[0]
    if con.in_transaction:
        con.commit()
    con.execute("BEGIN")
    ids = []
    try:
        primero = parsear_fecha(filas[0]["recibida_en"]) if filas else ctx.ahora
        debiles.detectar(con, min(primero, ctx.ahora), p, commit=False)
        for fila in filas:
            con.execute("SAVEPOINT solicitud")
            try:
                sid = _ingestar(con, fila)
                if sid is None:
                    resumen["duplicado_exacto"] += 1
                else:
                    _procesar(con, sid, ctx, desde=2)
                    ids.append(sid)
                con.execute("RELEASE solicitud")
            except Exception as e:      # un error inesperado no tumba el lote
                con.execute("ROLLBACK TO solicitud")
                con.execute("RELEASE solicitud")
                resumen["error_interno"].append({"fila": fila["fila"], "error": f"{type(e).__name__}: {e}"})
                _rescatar(con, fila, str(e))
        resumen["zonas_debiles_nuevas"] = debiles.detectar(con, ctx.ahora, p, commit=False)
        resumen["tareas_escaladas"] = debiles.escalar(con, ctx.ahora, p, commit=False)
        _actualizar_lambdas(con, ctx)
        con.commit()
    except Exception:
        con.rollback()
        raise
    resumen["nuevas"] = len(ids)
    if ids:
        marcas = ",".join("?" * len(ids))
        filas_lote = con.execute(f"SELECT estado, marcas, motivo_cuarentena FROM solicitudes "
                                 f"WHERE id IN ({marcas})", ids).fetchall()
    else:
        filas_lote = []
    resumen.update(_contar(filas_lote))
    resumen["eventos_globales"] = con.execute(
        "SELECT COUNT(*) FROM bitacora WHERE accion='posible_nuevo_evento'").fetchone()[0] - eventos_antes
    resumen["umbral"] = ctx.umbral
    resumen["base"] = resumen_base(con)
    return resumen


def reprocesar(con: sqlite3.Connection, sid: int, desde: int = 3, params: dict | None = None,
               ahora: datetime | None = None, extractor: Callable | None = None,
               integrar: bool = False, commit: bool = True, liberada: bool = False) -> None:
    """Vuelve a pasar una solicitud por el embudo desde el paso `desde`."""
    ctx = _contexto(con, params, ahora, extractor, integrar)
    _procesar(con, sid, ctx, desde=desde, liberada=liberada)
    if commit:
        con.commit()


def procesar_paso(con, sid, desde, params, ahora) -> None:
    """Pasos `desde`…10 sin commit (lo usa agentes.validar para los pasos 7 a 10)."""
    reprocesar(con, sid, desde=desde, params=params, ahora=ahora, commit=False)


def cambiar_estado(con: sqlite3.Connection, ids, estado: str, quien: str, motivo: str | None = None
                   ) -> list[int]:
    """Cambio de estado hecho por alguien. Confirmar o descartar exige una persona."""
    if estado not in ESTADOS:
        raise ValueError(f"Estado desconocido: {estado}")
    if estado in ("confirmada", "descartada") and not config.es_humano(quien):
        raise PermissionError("Solo una persona puede confirmar o descartar una solicitud.")
    p = config.cargar(con)
    cambiados = []
    for sid in ids or []:
        f = con.execute("SELECT * FROM solicitudes WHERE id=?", (sid,)).fetchone()
        if f is None:
            continue
        efectivas = f["familias_efectivas"]
        if estado == "confirmada" and efectivas is None:
            fam = f["familias_declaradas"] or p["f_bar"]
            zona = censo.zona_por_id(con, f["zona_id"])
            if zona is not None:
                disp = censo.tope_familias(zona, p) - censo.cupo_consumido(
                    con, zona.id, parsear_fecha(f["recibida_en"]), p, excluir_id=sid)
                efectivas = max(0, min(fam, disp))
            else:
                efectivas = fam
        con.execute("UPDATE solicitudes SET estado=?, familias_efectivas=? WHERE id=?",
                    (estado, efectivas, sid))
        cambiados.append(sid)
    con.commit()
    accion = {"confirmada": "confirmar_humano", "descartada": "descartar_humano"}.get(estado,
                                                                                       "cambiar_estado")
    datos_db.anotar(con, quien, accion, json.dumps({"ids": cambiados, "estado": estado,
                                                   "motivo": motivo}, ensure_ascii=False))
    return cambiados
