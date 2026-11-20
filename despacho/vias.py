"""Tramos viales con nombre coloquial, amarrados a una arista del grafo.

Uso:  .venv/bin/python -m despacho.vias
Escribe datos/semilla/vias.csv con cabecera nombre,lat,lon,osm_u,osm_v y muestra la verificación.

Para añadir un tramo, agrega una entrada a TRAMOS:
    nombre   nombre coloquial que usaría quien reporta
    patron   regex (sin distinguir mayúsculas) sobre `name` y `ref` de la arista
    bbox     (lon_min, lon_max) opcional, para acotar el tramo por geografía
    urbana   True si es avenida urbana (se exige desvío cuando exista una arista candidata con desvío)
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import networkx as nx
import numpy as np

from despacho import red

SALIDA = Path(__file__).resolve().parent.parent / "datos" / "semilla" / "vias.csv"
CATEGORIAS = {"motorway", "trunk", "primary", "secondary", "tertiary",
              "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link"}

TRAMOS = [
    {"nombre": "Panamericana", "patron": r"^Carretera Panamericana|^50$", "bbox": (-75.5300, -75.4500), "urbana": False},
    {"nombre": "salida a Letras", "patron": r"^50$", "bbox": (-75.4300, -75.4200), "urbana": False,
     "nota": "ruta 50 al oriente de Maltería (geografía, sin nombre en OSM)"},
    {"nombre": "avenida Santander", "patron": r"^Avenida Santander$", "urbana": True},
    {"nombre": "avenida Kevin Ángel", "patron": r"^Avenida Kevin Ángel$", "urbana": True},
    {"nombre": "vía a Chinchiná", "patron": r"^Vía A Chinchina$", "urbana": False},
    {"nombre": "avenida Paralela", "patron": r"^Avenida Paralela$", "urbana": True},
    {"nombre": "avenida del Centro", "patron": r"^Avenida Gilberto Alzate Avendaño$", "urbana": True},
    {"nombre": "avenida 12 de Octubre", "patron": r"^Avenida 12 de Octubre$", "urbana": True},
    {"nombre": "avenida Alberto Mendoza", "patron": r"^Avenida Alberto Mendoza Hoyos$", "urbana": True},
    {"nombre": "avenida Bernardo Arango", "patron": r"^Avenida Bernardo Arango$", "urbana": True},
    {"nombre": "vía a Villamaría", "patron": r"^Carretera a Villamaria$", "urbana": False},
]
# Sin ubicar con confianza (el grafo no los cubre o no tienen nombre en OSM): La Siria, vía a Neira.


def _lista(x):
    return x if isinstance(x, list) else [x]


def _punto_medio(g, u, v):
    geom = red.geometria_arista(g, u, v)
    p = geom.interpolate(0.5, normalized=True)
    return p.y, p.x


def tiene_desvio(g, u, v) -> bool:
    """Sin ninguna arista entre u y v (ambos sentidos), ¿se puede ir de u a v y de v a u?"""
    h = g.copy()
    for a, b in ((u, v), (v, u)):
        while h.has_edge(a, b):
            h.remove_edge(a, b)
    return nx.has_path(h, u, v) and nx.has_path(h, v, u)


def candidatas(g, t):
    rx = re.compile(t["patron"], re.I)
    out = {}
    for u, v, d in g.edges(data=True):
        if red.tipo_via(d) not in CATEGORIAS:
            continue
        textos = [str(s) for k in ("name", "ref") for s in _lista(d.get(k, "")) if s]
        if not any(rx.search(s) for s in textos):
            continue
        lat, lon = _punto_medio(g, u, v)
        if "bbox" in t and not (t["bbox"][0] <= lon <= t["bbox"][1]):
            continue
        out[frozenset((u, v))] = (u, v, lat, lon, d["length"])
    return list(out.values())


def elegir(g, t):
    c = candidatas(g, t)
    if not c:
        return None
    xy = np.array([[r[3], r[2]] for r in c])
    xy = xy - xy.mean(axis=0)
    eje = np.linalg.svd(xy, full_matrices=False)[2][0]
    proy = xy @ eje
    orden = np.argsort(np.abs(proy - np.median(proy)))
    cercanas = [c[i] for i in orden[: max(5, len(c) // 5)] if c[i][4] >= 60] or [c[orden[0]]]
    con = [r for r in cercanas if tiene_desvio(g, r[0], r[1])]
    r = (con if (t["urbana"] and con) else cercanas)[0]
    return r + (tiene_desvio(g, r[0], r[1]),)


def main():
    g = red.cargar()
    filas, info = [], []
    for t in TRAMOS:
        r = elegir(g, t)
        if r is None:
            print(f"SIN TRAMO: {t['nombre']}")
            continue
        u, v, lat, lon, _, desvio = r
        filas.append([t["nombre"], f"{lat:.6f}", f"{lon:.6f}", u, v])
        info.append((t["nombre"], u, v, lat, lon, desvio))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre", "lat", "lon", "osm_u", "osm_v"])
        w.writerows(filas)
    print(f"{len(filas)} tramos -> {SALIDA}")
    for nombre, u, v, lat, lon, desvio in info:
        d = min(g[u][v].values(), key=lambda d: d["length"])
        _, _, m = red.arista_cercana(g, round(lat, 6), round(lon, 6))
        print(f"{nombre:24} has_edge={g.has_edge(u, v)} name={d.get('name')} ref={d.get('ref')} "
              f"hw={red.tipo_via(d)} dist={m:.1f} m desvío={'sí' if desvio else 'no'}")


if __name__ == "__main__":
    main()
