"""Zonas débiles: silencio, aislamiento, tareas de campo y escalamiento (B.6).

Definición única de silencio (aviso del canal, 20/11 23:30, igual que entrada/silencio.py):
una zona con afectación > 0 está en silencio cuando lleva `silencio_h` horas o más (6 h, SUPUESTO)
sin contacto, contadas desde la hora más tardía entre el inicio de la jornada (06:00 de Bogotá) y
la hora del evento. Contacto = una solicitud de la zona por chat con lugar confirmado, o cualquier
solicitud de un agente, que no esté en cuarentena ni descartada: un ataque de bots en cuarentena
no apaga la alerta.

La prueba de Poisson ya no decide si hay silencio: solo ordena las tareas de campo,
prioridad = H_af × (1 + aislada) × (1 − exp(−mu)), con mu = lambda × horas de silencio.
"""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, time as hora_del_dia, timedelta

import networkx as nx

from datos import db as datos_db
from triage import antifraude, censo, config
from triage import db as tdb
from triage.entrada_datos import a_iso, parsear_fecha

QUIEN = "regla:triage"
ESTADOS_TAREA_ABIERTA = ("abierta", "asignada", "escalada")
ESTADOS_SIN_CONTACTO = ("cuarentena", "descartada")


def inicio_jornada(ahora: datetime, jornada_inicio: str) -> datetime:
    """La última vez que dio la hora de inicio (hoy, o ayer si aún no es la hora), en Bogotá."""
    try:
        h, m = (int(x) for x in str(jornada_inicio).split(":"))
    except ValueError:
        h, m = (int(x) for x in config.JORNADA_INICIO.split(":"))
    local = ahora.astimezone(datos_db.BOGOTA)
    inicio = datetime.combine(local.date(), hora_del_dia(h, m), tzinfo=datos_db.BOGOTA)
    return inicio if inicio <= local else inicio - timedelta(days=1)


def ultimo_contacto(con: sqlite3.Connection, zona_id: int, hasta: datetime) -> datetime | None:
    """La solicitud más reciente que cuenta como contacto de la zona, hasta `hasta`."""
    marcas = ",".join("?" * len(ESTADOS_SIN_CONTACTO))
    f = con.execute(
        f"SELECT MAX(recibida_en) FROM solicitudes WHERE zona_id=? AND recibida_en <= ? "
        f"AND estado NOT IN ({marcas}) AND ((canal='chat' AND lugar_confirmado=1) OR canal='agente')",
        (zona_id, a_iso(hasta), *ESTADOS_SIN_CONTACTO)).fetchone()
    return parsear_fecha(f[0]) if f and f[0] else None


def horas_de_silencio(con: sqlite3.Connection, zona, ahora: datetime, params: dict) -> float | None:
    """Horas sin contacto desde max(inicio de jornada, hora del evento, último contacto).

    None si no hay hora de evento: sin evento no se evalúa el silencio en triage.
    """
    evento = parsear_fecha(params.get("hora_evento"))
    if evento is None or ahora is None:
        return None
    desde = max(inicio_jornada(ahora, params["jornada_inicio"]), evento)
    contacto = ultimo_contacto(con, zona.id, ahora)
    if contacto is not None:
        desde = max(desde, contacto)
    return max(0.0, (ahora - desde).total_seconds() / 3600)


def prioridad_tarea(zona, horas: float, params: dict) -> float:
    """H_af × (1 + aislada) × (1 − exp(−mu)), mu = lambda × horas de silencio."""
    mu = antifraude.lambda_zona(zona, params) * max(0.0, horas or 0.0)
    return censo.hogares_afectados(zona, params) * (1 + (zona.aislada or 0)) * (1 - math.exp(-mu))


def aislada(grafo, nodo_zona, nodos_acopio, aristas_cerradas) -> bool:
    """True si ningún acopio llega a la zona después de quitar las aristas cerradas."""
    if grafo is None or nodo_zona is None:
        return False
    try:
        if nodo_zona not in grafo:
            return False
        g = grafo.copy()
        for arista in aristas_cerradas or []:
            u, v = arista[0], arista[1]
            for a, b in ((u, v), (v, u)):       # una vía cerrada se cierra en los dos sentidos
                while g.has_edge(a, b):
                    g.remove_edge(a, b)
        acopios = [a for a in (nodos_acopio or []) if a in g]
        if not acopios:
            return True
        return not any(nx.has_path(g, a, nodo_zona) for a in acopios)
    except (nx.NetworkXException, TypeError, IndexError):
        return False


def _cerrar(con, commit):
    if commit:
        con.commit()


def crear_tarea(con: sqlite3.Connection, zona, t: datetime, motivo: str, params: dict,
                horas: float = 0.0) -> int:
    cur = con.execute("INSERT INTO tareas_campo(zona_id, creada_en, motivo, prioridad) "
                      "VALUES (?,?,?,?)", (zona.id, a_iso(t), motivo, prioridad_tarea(zona, horas, params)))
    return cur.lastrowid


def tarea_para_zona(con: sqlite3.Connection, zona, t: datetime, params: dict) -> int:
    """La tarea abierta de la zona; si no hay, una nueva."""
    marcas = ",".join("?" * len(ESTADOS_TAREA_ABIERTA))
    f = con.execute(f"SELECT id FROM tareas_campo WHERE zona_id=? AND estado IN ({marcas}) "
                    "ORDER BY id DESC LIMIT 1", (zona.id, *ESTADOS_TAREA_ABIERTA)).fetchone()
    if f:
        return f["id"]
    horas = horas_de_silencio(con, zona, t, params) or 0.0
    return crear_tarea(con, zona, t, "solicitud_en_zona_debil", params, horas)


def detectar(con: sqlite3.Connection, ahora: datetime, params: dict | None = None,
             commit: bool = True) -> list[int]:
    """B.6.1: marca como débiles las zonas afectadas en silencio y crea sus tareas."""
    p = params or config.cargar(con)
    if parsear_fecha(p.get("hora_evento")) is None or ahora is None:
        return []
    nuevas = []
    for zona in censo.zonas_de_base(con):
        if not zona.afectacion or zona.afectacion <= 0 or zona.es_debil:
            continue
        horas = horas_de_silencio(con, zona, ahora, p)
        if horas is None or horas < p["silencio_h"]:
            continue
        con.execute("UPDATE zonas SET es_debil=1 WHERE id=?", (zona.id,))
        tarea = crear_tarea(con, zona, ahora, "zona_silenciosa", p, horas)
        tdb.anotar_regla(con, QUIEN, "zona_debil",
                         {"zona_id": zona.id, "horas_sin_contacto": round(horas, 2),
                          "tarea_id": tarea}, ahora)
        nuevas.append(zona.id)
    _cerrar(con, commit)
    return nuevas


def tareas_ordenadas(con: sqlite3.Connection) -> list[dict]:
    """Tareas de campo abiertas, de la que se verifica primero a la última."""
    marcas = ",".join("?" * len(ESTADOS_TAREA_ABIERTA))
    return [dict(f) for f in con.execute(
        f"SELECT * FROM tareas_campo WHERE estado IN ({marcas}) ORDER BY prioridad DESC, id",
        ESTADOS_TAREA_ABIERTA)]


def escalar(con: sqlite3.Connection, ahora: datetime, params: dict | None = None,
            commit: bool = True) -> list[int]:
    """Tareas abiertas o asignadas durante t_escala_h o más pasan a 'escalada'."""
    p = params or config.cargar(con)
    escaladas = []
    for f in con.execute("SELECT id, creada_en FROM tareas_campo WHERE estado IN "
                         "('abierta','asignada')").fetchall():
        creada = parsear_fecha(f["creada_en"])
        if creada and ahora - creada >= timedelta(hours=p["t_escala_h"]):
            con.execute("UPDATE tareas_campo SET estado='escalada' WHERE id=?", (f["id"],))
            tdb.anotar_regla(con, QUIEN, "escalar_tarea", {"tarea_id": f["id"]}, ahora)
            escaladas.append(f["id"])
    _cerrar(con, commit)
    return escaladas


def reabrir(con: sqlite3.Connection, zona_id: int, quien: str,
            ahora: datetime | None = None) -> None:
    """La zona deja de ser débil. Solo una persona o un agente."""
    if not config.es_humano(quien):
        raise PermissionError("Solo una persona o un agente puede reabrir una zona débil.")
    momento = a_iso(ahora) if ahora else datos_db.ahora()
    con.execute("UPDATE zonas SET es_debil=0 WHERE id=?", (zona_id,))
    con.execute("UPDATE tareas_campo SET estado='cerrada', cerrada_en=? WHERE zona_id=? "
                "AND estado IN ('abierta','asignada','escalada')", (momento, zona_id))
    con.commit()
    datos_db.anotar(con, quien, "reabrir_zona", json.dumps({"zona_id": zona_id}))


def actualizar_aislamiento(con: sqlite3.Connection, grafo, nodo_por_zona: dict, nodos_acopio,
                           aristas_cerradas, commit: bool = True) -> list[int]:
    """Marca `aislada` en las zonas según el grafo. Sin grafo no cambia nada."""
    if grafo is None:
        return []
    aisladas = []
    for zona_id, nodo in (nodo_por_zona or {}).items():
        a = aislada(grafo, nodo, nodos_acopio, aristas_cerradas)
        con.execute("UPDATE zonas SET aislada=? WHERE id=?", (1 if a else 0, zona_id))
        if a:
            aisladas.append(zona_id)
    _cerrar(con, commit)
    return aisladas
