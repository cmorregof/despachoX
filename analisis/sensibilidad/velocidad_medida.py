"""Velocidades medidas de `datos_publicos/velocidades.csv`, aplicadas en memoria sin editar `despacho/`.

La simulación y el optimizador calculan tiempos de viaje por caminos distintos:

- el mundo simulado usa `despacho.sim.red_sim.Red.segundos[tipo]`, que sale del `travel_time` del
  grafo (el `maxspeed` de OpenStreetMap donde existe y, si no, `VELOCIDADES` por tipo de vía)
  multiplicado por `FACTOR_TIEMPO` de cada vehículo;
- el optimizador arma su matriz en cada llamada con `despacho.matriz._red_del_tipo`, con la misma
  regla sobre el grafo de `despacho.red.cargar()`.

Aquí los dos pasan a usar la misma regla: segundos = largo / (velocidad del CSV para ese tipo de vía
y ese vehículo × multiplicador). Se ignoran el `maxspeed` de OSM y `FACTOR_TIEMPO`, porque el CSV
ya trae una columna por vehículo. Un tipo de vía que no está en el CSV (en el grafo de la región
solo `ladder`, 2 aristas) conserva el supuesto del modelo: 20 km/h dividido por `FACTOR_TIEMPO`.

`aplicar(multiplicador)` deja los dos parches puestos en el proceso que lo llama. Con el arranque
`spawn` de macOS los procesos hijos no heredan parches, así que cada hijo lo llama al arrancar.
"""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix

from despacho.sim import red_sim

RAIZ = Path(__file__).resolve().parents[2]
RUTA_CSV = RAIZ / "datos_publicos" / "velocidades.csv"
COLUMNA = {"camion": "vel_kmh_camion", "campero": "vel_kmh_campero", "moto": "vel_kmh_moto"}

_ESTADO = {"multiplicador": None}


def leer_velocidades(ruta: Path = RUTA_CSV) -> dict:
    """{tipo de vía: {tipo de vehículo: km/h}} tal como vienen en el CSV."""
    with open(ruta, newline="") as fh:
        return {f["tipo_via"]: {t: float(f[c]) for t, c in COLUMNA.items()} for f in csv.DictReader(fh)}


def kmh(vel: dict, via: str, tipo: str, multiplicador: float) -> float:
    """Velocidad del CSV por el multiplicador; fuera del CSV, el supuesto del modelo."""
    if via in vel:
        base = vel[via][tipo]
    else:
        base = red_sim.VELOCIDAD_POR_DEFECTO / red_sim.FACTOR_TIEMPO[tipo]
    return base * multiplicador


# ------------------------------------------------------------------ mundo simulado
def red_medida(ruta, multiplicador: float, vel: dict | None = None) -> red_sim.Red:
    """La `Red` de `Red.desde_graphml` con los segundos de cada vehículo tomados del CSV.

    Entre aristas paralelas de un mismo par de nodos se queda, para cada vehículo, la más rápida
    (como `desde_graphml` y como `matriz._red_del_tipo`). El camión solo usa las aptas para él.
    """
    import networkx as nx

    vel = vel or leer_velocidades()
    g = nx.read_graphml(ruta)
    ids = list(g.nodes)
    idx = {nodo: i for i, nodo in enumerate(ids)}
    lat = [float(g.nodes[n]["y"]) for n in ids]
    lon = [float(g.nodes[n]["x"]) for n in ids]
    mejor = {}      # par -> [largo, via, campero, moto, camión apto, camión en cualquier vía]
    for u, v, d in g.edges(data=True):
        if u == v:
            continue
        via = red_sim._via(d.get("highway", ""))
        largo = float(d.get("length", 0.0)) or 1.0
        t = {tipo: largo / (kmh(vel, via, tipo, multiplicador) / 3.6) for tipo in red_sim.TIPOS}
        apta = red_sim._apta_camion(via, d.get("hgv", ""), d.get("maxweight", "99"))
        par = (idx[u], idx[v])
        tc = t["camion"] if apta else np.inf
        if par not in mejor:
            mejor[par] = [largo, via, t["campero"], t["moto"], tc, t["camion"]]
            continue
        m = mejor[par]
        if t["campero"] < m[2]:
            m[0], m[1], m[2] = largo, via, t["campero"]
        m[3] = min(m[3], t["moto"])
        m[4] = min(m[4], tc)
        m[5] = min(m[5], t["camion"])
    pares = list(mejor)
    largo = np.array([mejor[p][0] for p in pares], float)
    campero = np.array([mejor[p][2] for p in pares], float)
    moto = np.array([mejor[p][3] for p in pares], float)
    camion = np.array([mejor[p][4] for p in pares], float)
    camion_todas = np.array([mejor[p][5] for p in pares], float)
    r = red_sim.Red(lat, lon, [p[0] for p in pares], [p[1] for p in pares], largo, campero, camion,
                    origen=f"OpenStreetMap ({Path(ruta).name}, {len(ids)} nodos), velocidad medida "
                           f"x{multiplicador:g}", osm_id=[int(n) for n in ids])
    r.segundos = {"camion": np.maximum(camion, 0.01), "campero": np.maximum(campero, 0.01),
                  "moto": np.maximum(moto, 0.01)}
    todas = {"camion": camion_todas, "campero": campero, "moto": moto}
    r.segundos_emergencia = {
        t: np.where(np.isfinite(r.segundos[t]), r.segundos[t],
                    np.maximum(todas[t] * red_sim.FACTOR_EMERGENCIA, 0.01)) for t in red_sim.TIPOS}
    r._nodos_tipo, r._acceso = {}, {}
    r.via = [mejor[p][1] for p in pares]          # solo para verificar velocidades por tipo de vía
    return r


# ------------------------------------------------------------------ lo que ve el optimizador
_BASE: dict = {}


def _base_optimizador(g, tipo: str, multiplicador: float, vel: dict):
    """Aristas del tipo de vehículo con segundos medidos, calculadas una vez por proceso."""
    from despacho import matriz, red

    clave = (id(g), tipo, multiplicador)
    if clave not in _BASE:
        ids = list(g.nodes)
        pos = {n: k for k, n in enumerate(ids)}
        mejor = {}
        for u, v, datos in g.edges(data=True):
            if u == v:
                continue
            if tipo == "camion" and not matriz._apta_camion(datos):
                continue
            largo = float(datos.get("length", 0.0)) or 1.0
            t = largo / (kmh(vel, red.tipo_via(datos), tipo, multiplicador) / 3.6)
            if (u, v) not in mejor or t < mejor[(u, v)]:
                mejor[(u, v)] = t
        pares = list(mejor)
        filas = np.array([pos[u] for u, _ in pares], np.int64)
        cols = np.array([pos[v] for _, v in pares], np.int64)
        vals = np.maximum(np.array([mejor[p] for p in pares], float), 0.01)
        _BASE[clave] = (ids, pos, {p: k for k, p in enumerate(pares)}, filas, cols, vals)
    return _BASE[clave]


def _red_del_tipo_medida(g, tipo, cerradas, _original=None):
    """Reemplazo de `despacho.matriz._red_del_tipo`: misma salida, con segundos medidos."""
    if tipo not in red_sim.TIPOS:
        return _original(g, tipo, cerradas)
    ids, pos, indice, filas, cols, vals = _base_optimizador(g, tipo, _ESTADO["multiplicador"], _ESTADO["vel"])
    n = len(ids)
    if not len(vals):
        return csr_matrix((n, n)), ids, pos, set()
    ok = np.ones(len(vals), bool)
    for par in cerradas:
        k = indice.get(par)
        if k is not None:
            ok[k] = False
    m = csr_matrix((vals[ok], (filas[ok], cols[ok])), shape=(n, n))
    tocados = np.unique(np.concatenate([filas[ok], cols[ok]]))
    return m, ids, pos, {ids[k] for k in tocados.tolist()}


# ------------------------------------------------------------------ aplicar
def aplicar(multiplicador: float) -> None:
    """Pone los dos parches en este proceso: la red de la simulación y la matriz del optimizador."""
    from functools import partial

    from despacho import matriz

    vel = leer_velocidades()
    ruta = red_sim.ruta_cache()
    if ruta is None:
        raise FileNotFoundError("No está el grafo vial en despacho/cache/")
    red_sim._RED_CACHE["auto"] = red_medida(ruta, multiplicador, vel)
    if not hasattr(matriz, "_red_del_tipo_original"):
        matriz._red_del_tipo_original = matriz._red_del_tipo
    matriz._red_del_tipo = partial(_red_del_tipo_medida, _original=matriz._red_del_tipo_original)
    _ESTADO.update(multiplicador=multiplicador, vel=vel)


def multiplicador_activo():
    return _ESTADO["multiplicador"]
