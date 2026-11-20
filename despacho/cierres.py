"""Ubica en el grafo los cierres viales: llena `cierres.osm_u` y `cierres.osm_v`."""
from __future__ import annotations

import csv
import sqlite3
import unicodedata
from pathlib import Path

import networkx as nx

from despacho import red

RUTA_VIAS = Path(__file__).resolve().parent.parent / "datos" / "semilla" / "vias.csv"
MAX_METROS = 500.0      # un cierre más lejos que esto de cualquier vía no se ubica solo


def normalizar(texto: str | None) -> str:
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


def vias_conocidas() -> dict[str, tuple[int, int]]:
    """nombre normalizado -> (osm_u, osm_v), desde datos/semilla/vias.csv."""
    if not RUTA_VIAS.exists():
        return {}
    with open(RUTA_VIAS, encoding="utf-8") as f:
        return {normalizar(r["nombre"]): (int(r["osm_u"]), int(r["osm_v"]))
                for r in csv.DictReader(f) if r.get("osm_u") and r.get("osm_v")}


def ubicar(con: sqlite3.Connection, g: nx.MultiDiGraph) -> list[str]:
    """Llena osm_u y osm_v de los cierres vigentes que no los traen. Devuelve avisos."""
    avisos: list[str] = []
    vias = vias_conocidas()
    filas = con.execute("SELECT * FROM cierres WHERE estado != 'levantado' "
                        "AND (osm_u IS NULL OR osm_v IS NULL)").fetchall()
    pendientes = {r["fila_id"] for r in con.execute(
        "SELECT fila_id FROM ubicaciones u WHERE tabla='cierres' AND estado='propuesta' AND NOT EXISTS "
        "(SELECT 1 FROM ubicaciones c WHERE c.tabla='cierres' AND c.fila_id=u.fila_id AND c.estado='confirmada')")}
    for c in filas:
        if c["id"] in pendientes:        # nadie ha confirmado dónde es: no entra al plan
            avisos.append(f"cierre {c['id']}: su ubicación sigue sin confirmar; no se aplicó")
            continue
        arista = None
        lugar = normalizar(c["lugar"])
        if lugar:
            arista = vias.get(lugar) or next(
                (uv for nombre, uv in vias.items() if nombre in lugar or lugar in nombre), None)
            if arista and not g.has_edge(*arista):
                arista = (arista[1], arista[0]) if g.has_edge(arista[1], arista[0]) else None
        if arista is None and c["lat"] is not None and c["lon"] is not None:
            u, v, d = red.arista_cercana(g, c["lat"], c["lon"])
            if d <= MAX_METROS:
                arista = (u, v)
            else:
                avisos.append(f"cierre {c['id']}: la vía más cercana está a {d:.0f} m; no se ubicó")
                continue
        if arista is None:
            avisos.append(f"cierre {c['id']}: sin vía conocida ni coordenadas; no se ubicó")
            continue
        con.execute("UPDATE cierres SET osm_u=?, osm_v=? WHERE id=?", (arista[0], arista[1], c["id"]))
    con.commit()
    return avisos
