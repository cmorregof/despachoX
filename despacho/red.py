"""Red vial de Manizales desde OpenStreetMap, guardada en disco para no depender de la red.

Uso:
    python -m despacho.red            # baja el grafo si no está en caché y muestra su tamaño
    python -m despacho.red --forzar   # lo vuelve a bajar
"""
from __future__ import annotations

import argparse
import os
import pickle
import socket
import sys
import time
from functools import lru_cache
from pathlib import Path

import networkx as nx
import numpy as np
import osmnx as ox
import shapely
from shapely.geometry import LineString, Point

CACHE = Path(__file__).resolve().parent / "cache"
# Red ampliada (casco urbano completo + vías principales de los accesos). La variable de entorno
# DESPACHOX_GRAFO permite fijar otro archivo, por ejemplo el grafo urbano original
# `manizales.graphml` con el que se midió la primera simulación.
RUTA_GRAFO = Path(os.environ.get("DESPACHOX_GRAFO") or CACHE / "manizales_region.graphml")
RUTA_PICKLE = RUTA_GRAFO.with_suffix(".pkl")
LUGARES = ["Manizales, Caldas, Colombia", "Villamaría, Caldas, Colombia"]
# Accesos: Chinchiná y Palestina (autopista del Café, vía antigua por La Siria), kilómetro 41,
# Neira al norte y el alto de Letras al oriente. (oeste, sur, este, norte)
AREA = (-75.74, 4.93, -75.30, 5.20)
FILTRO_ACCESOS = '["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified)(_link)?$"]'

# Velocidades supuestas (km/h) cuando la vía no trae `maxspeed`. Son un supuesto nuestro
# para ciudad de ladera; no vienen de una medición.
VELOCIDADES = {
    "motorway": 60, "trunk": 50, "primary": 40, "secondary": 35, "tertiary": 30,
    "unclassified": 25, "residential": 20, "living_street": 10, "service": 15,
    "motorway_link": 40, "trunk_link": 35, "primary_link": 30,
    "secondary_link": 25, "tertiary_link": 25,
}
VELOCIDAD_POR_DEFECTO = 20
INTENTOS = 60


def _evitar_ip_caida() -> None:
    """Overpass reparte la carga entre varias IP y a veces una rechaza conexiones.

    osmnx fija la primera que resuelve; aquí se le entrega una que sí conecta.
    """
    from urllib.parse import urlparse
    host = urlparse(ox.settings.overpass_url).hostname
    original = socket.gethostbyname
    try:
        ips = [r[4][0] for r in socket.getaddrinfo(host, 443, socket.AF_INET, socket.SOCK_STREAM)]
    except OSError:
        return
    for ip in ips:
        try:
            socket.create_connection((ip, 443), timeout=8).close()
        except OSError:
            continue
        socket.gethostbyname = lambda h, ip=ip: ip if h == host else original(h)
        return


def descargar() -> nx.MultiDiGraph:
    """Baja el grafo de conducción, deja el mayor componente fuertemente conexo y lo guarda."""
    if os.environ.get("DESPACHOX_SIN_RED", "").strip().lower() in ("1", "si", "sí", "true"):
        raise RuntimeError(f"DESPACHOX_SIN_RED=1 y no hay red vial en {RUTA_GRAFO}: copie "
                           "despliegue/grafo/manizales_region.graphml o fije DESPACHOX_GRAFO")
    ox.settings.use_cache = True
    ox.settings.cache_folder = str(CACHE / "http")
    ox.settings.requests_timeout = 120
    def insistir(f):
        for intento in range(1, INTENTOS + 1):   # Overpass público se satura; se insiste con pausa
            try:
                _evitar_ip_caida()
                return f()
            except Exception as e:  # noqa: BLE001  (red caída, 502, cola llena)
                print(f"intento {intento}/{INTENTOS} falló: {type(e).__name__}: {str(e)[:120]}",
                      file=sys.stderr, flush=True)
                if intento == INTENTOS:
                    raise
                time.sleep(8)

    # Sin simplificar, para poder unir las dos descargas por sus nodos de OSM y simplificar después.
    urbano = insistir(lambda: ox.graph_from_place(LUGARES, network_type="drive", simplify=False))
    accesos = insistir(lambda: ox.graph_from_bbox(AREA, custom_filter=FILTRO_ACCESOS, simplify=False,
                                                  truncate_by_edge=True))
    g = ox.simplify_graph(nx.compose(accesos, urbano))
    g = ox.truncate.largest_component(g, strongly=True)
    g = ox.add_edge_speeds(g, hwy_speeds=VELOCIDADES, fallback=VELOCIDAD_POR_DEFECTO)
    g = ox.add_edge_travel_times(g)
    CACHE.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(g, RUTA_GRAFO)
    return g


@lru_cache(maxsize=1)
def cargar() -> nx.MultiDiGraph:
    """Grafo con `length` (m), `speed_kph` y `travel_time` (s) en cada arista.

    La primera vez lee el graphml (lento) y deja una copia en pickle que abre en menos de un segundo.
    """
    if not RUTA_GRAFO.exists():
        descargar()
    if RUTA_PICKLE.exists() and RUTA_PICKLE.stat().st_mtime >= RUTA_GRAFO.stat().st_mtime:
        with open(RUTA_PICKLE, "rb") as f:
            return pickle.load(f)
    g = ox.load_graphml(RUTA_GRAFO)
    with open(RUTA_PICKLE, "wb") as f:
        pickle.dump(g, f, protocol=pickle.HIGHEST_PROTOCOL)
    return g


def tipo_via(datos: dict) -> str:
    """Etiqueta `highway` de una arista como texto (OSM a veces trae una lista)."""
    h = datos.get("highway", "")
    return h[0] if isinstance(h, list) else str(h)


def metros(lat1, lon1, lat2, lon2):
    """Distancia en metros (aproximación plana, suficiente a escala de ciudad). Acepta arreglos."""
    kx = 111_320 * np.cos(np.radians(lat1))
    return np.hypot((np.asarray(lon2) - lon1) * kx, (np.asarray(lat2) - lat1) * 110_540)


def nodo_cercano(g: nx.MultiDiGraph, lat: float, lon: float, nodos=None) -> tuple[int, float]:
    """Nodo más cercano y su distancia en metros. `nodos` restringe la búsqueda (p. ej. red de camión)."""
    ids = list(g.nodes) if nodos is None else list(nodos)
    ys = np.array([g.nodes[n]["y"] for n in ids])
    xs = np.array([g.nodes[n]["x"] for n in ids])
    d = metros(lat, lon, ys, xs)
    k = int(d.argmin())
    return int(ids[k]), float(d[k])


def geometria_arista(g: nx.MultiDiGraph, u: int, v: int) -> LineString:
    datos = min(g[u][v].values(), key=lambda d: d.get("travel_time", 1e18))
    geom = datos.get("geometry")
    if geom is None:
        geom = LineString([(g.nodes[u]["x"], g.nodes[u]["y"]), (g.nodes[v]["x"], g.nodes[v]["y"])])
    return geom


def arista_cercana(g: nx.MultiDiGraph, lat: float, lon: float) -> tuple[int, int, float]:
    """Arista (u, v) más cercana a un punto y su distancia en metros."""
    pares = list({(u, v) for u, v in g.edges()})
    geoms = np.array([geometria_arista(g, u, v) for u, v in pares], dtype=object)
    kx = np.cos(np.radians(lat))          # grados de longitud "encogidos" para medir en plano
    escalar = lambda geo: shapely.transform(geo, lambda c: c * [kx, 1.0])
    d = shapely.distance(escalar(geoms), escalar(Point(lon, lat)))
    k = int(np.argmin(d))
    return int(pares[k][0]), int(pares[k][1]), float(d[k] * 110_540)


def geometria(g: nx.MultiDiGraph, nodos: list[int]) -> list[list[float]]:
    """[[lat, lon], ...] de un camino de nodos, siguiendo la forma real de cada tramo."""
    if not nodos:
        return []
    pts = [[g.nodes[nodos[0]]["y"], g.nodes[nodos[0]]["x"]]]
    for u, v in zip(nodos[:-1], nodos[1:]):
        pts.extend([y, x] for x, y in list(geometria_arista(g, u, v).coords)[1:])
    return [[round(a, 6), round(b, 6)] for a, b in pts]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--forzar", action="store_true", help="vuelve a bajar el grafo")
    args = ap.parse_args()
    if args.forzar or not RUTA_GRAFO.exists():
        descargar()
    grafo = cargar()
    print(f"{grafo.number_of_nodes()} nodos, {grafo.number_of_edges()} aristas -> {RUTA_GRAFO}")
