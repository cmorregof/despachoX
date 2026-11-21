"""Zonas débiles: silencio estadístico, aislamiento, tareas de campo y escalamiento (B.6)."""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timedelta

import networkx as nx

from triage import antifraude, censo, config
from triage import db as tdb
from triage.entrada_datos import a_iso, parsear_fecha

QUIEN = "regla:triage"
ESTADOS_TAREA_ABIERTA = ("abierta", "asignada", "escalada")


def es_silenciosa(mu: float, alpha_sil: float) -> bool:
    """exp(−mu) < alpha_sil: no haber recibido nada sería muy improbable si hubiera señal."""
    if mu is None or not math.isfinite(mu) or mu < 0:
        return False
    return math.exp(-mu) < alpha_sil


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


def crear_tarea(con: sqlite3.Connection, zona, t: datetime, motivo: str, params: dict) -> int:
    prioridad = censo.hogares_afectados(zona, params) * (1 + (zona.aislada or 0))
    cur = con.execute("INSERT INTO tareas_campo(zona_id, creada_en, motivo, prioridad) "
                      "VALUES (?,?,?,?)", (zona.id, a_iso(t), motivo, prioridad))
    return cur.lastrowid


def tarea_para_zona(con: sqlite3.Connection, zona, t: datetime, params: dict) -> int:
    """La tarea abierta de la zona; si no hay, una nueva."""
    marcas = ",".join("?" * len(ESTADOS_TAREA_ABIERTA))
    f = con.execute(f"SELECT id FROM tareas_campo WHERE zona_id=? AND estado IN ({marcas}) "
                    "ORDER BY id DESC LIMIT 1", (zona.id, *ESTADOS_TAREA_ABIERTA)).fetchone()
    if f:
        return f["id"]
    return crear_tarea(con, zona, t, "solicitud_en_zona_debil", params)


def detectar(con: sqlite3.Connection, ahora: datetime, params: dict | None = None,
             commit: bool = True) -> list[int]:
    """B.6.1: marca como débiles las zonas afectadas que callan demasiado. Crea sus tareas."""
    p = params or config.cargar(con)
    evento = parsear_fecha(p.get("hora_evento"))
    if evento is None or ahora is None:
        return []
    T = (ahora - evento).total_seconds() / 3600
    if T < p["T_min_sil_h"]:
        return []
    nuevas = []
    for zona in censo.zonas_de_base(con):
        if not zona.afectacion or zona.afectacion <= 0 or zona.es_debil:
            continue
        n = con.execute("SELECT COUNT(*) FROM solicitudes WHERE zona_id=? AND recibida_en >= ? "
                        "AND recibida_en <= ?", (zona.id, a_iso(evento), a_iso(ahora))).fetchone()[0]
        if n:
            continue
        mu = antifraude.lambda_zona(zona, p) * T
        if es_silenciosa(mu, p["alpha_sil"]):
            con.execute("UPDATE zonas SET es_debil=1 WHERE id=?", (zona.id,))
            tarea = crear_tarea(con, zona, ahora, "zona_silenciosa", p)
            tdb.anotar_regla(con, QUIEN, "zona_debil",
                             {"zona_id": zona.id, "mu": round(mu, 3), "tarea_id": tarea}, ahora)
            nuevas.append(zona.id)
    _cerrar(con, commit)
    return nuevas


def escalar(con: sqlite3.Connection, ahora: datetime, params: dict | None = None,
            commit: bool = True) -> list[int]:
    """Tareas abiertas o asignadas por más de t_escala_h pasan a 'escalada'."""
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
    from datos import db as datos_db
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
