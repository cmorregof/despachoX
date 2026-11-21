"""Cola de revisión humana: prioridad y lotes por zona (B.7, paso 11)."""
from __future__ import annotations

import json
import random
import sqlite3
from datetime import datetime

from triage import censo, config
from triage.entrada_datos import parsear_fecha

TIPOS_CRITICOS = ("critico", "punto_critico", "punto critico")


def u_punto(tipo_punto, zona, params: dict) -> float:
    tp = (tipo_punto or "").strip().lower()
    if tp == "albergue" or (zona is not None and zona.tipo == "albergue"):
        return params["u_albergue"]
    if tp in TIPOS_CRITICOS or (zona is not None and zona.critico):
        return params["u_critico"]
    return params["u_otro"]


def familias_para_cola(sol) -> int:
    fe = sol["familias_efectivas"]
    if fe is None:
        fe = sol["familias_declaradas"]
    try:
        return max(0, int(fe or 0))
    except (TypeError, ValueError):
        return 0


def prioridad(sol, zona, ahora: datetime, params: dict) -> float:
    """u_punto × familias_efectivas × (1 + beta_ais × aislada) + gamma × horas_en_cola."""
    t = parsear_fecha(sol["recibida_en"])
    horas = max(0.0, (ahora - t).total_seconds() / 3600) if t and ahora else 0.0
    ais = (zona.aislada or 0) if zona is not None else 0
    return (u_punto(sol["tipo_punto"], zona, params) * familias_para_cola(sol)
            * (1 + params["beta_ais"] * ais) + params["gamma"] * horas)


def cola_ordenada(con: sqlite3.Connection, ahora: datetime, params: dict | None = None) -> list[dict]:
    p = params or config.cargar(con)
    zonas = {z.id: z for z in censo.zonas_de_base(con)}
    filas = []
    for f in con.execute("SELECT * FROM solicitudes WHERE estado='en_cola' ORDER BY id"):
        d = dict(f)
        d["prioridad"] = prioridad(f, zonas.get(f["zona_id"]), ahora, p)
        filas.append(d)
    return sorted(filas, key=lambda d: (-d["prioridad"], d["id"]))


def lotes(con: sqlite3.Connection, ahora: datetime | None = None, params: dict | None = None) -> list[dict]:
    """La cola agrupada por zona, con conteos hechos en código y una muestra de ids."""
    from datos import db as datos_db
    p = params or config.cargar(con)
    ahora = ahora or parsear_fecha(datos_db.ahora())
    zonas = {z.id: z for z in censo.zonas_de_base(con)}
    grupos: dict = {}
    for d in cola_ordenada(con, ahora, p):
        g = grupos.setdefault(d["zona_id"], {"zona_id": d["zona_id"], "ids": [], "familias": 0,
                                             "marcas": {}, "prioridad": 0.0})
        g["ids"].append(d["id"])
        g["familias"] += familias_para_cola(d)
        g["prioridad"] += d["prioridad"]
        try:
            marcas = json.loads(d["marcas"] or "[]")
        except (TypeError, ValueError):
            marcas = []
        for m in marcas:
            g["marcas"][m] = g["marcas"].get(m, 0) + 1
    salida = []
    for zid, g in grupos.items():
        ids = sorted(g["ids"])
        rng = random.Random(f"{p['semilla']}:{zid}")
        muestra = sorted(rng.sample(ids, min(p["muestra_lote"], len(ids))))
        z = zonas.get(zid)
        salida.append({"zona_id": zid, "zona": z.nombre if z else "sin zona",
                       "solicitudes": len(ids), "familias": g["familias"],
                       "marcas": dict(sorted(g["marcas"].items())),
                       "prioridad": round(g["prioridad"], 3), "muestra": muestra})
    return sorted(salida, key=lambda x: (-x["prioridad"], str(x["zona"])))
