"""Red vial de la simulación.

`Red` es la red verdadera (aristas dirigidas con largo y clase de vía).
`Conocimiento` es lo que el despacho cree de la red: la misma red menos los cierres ya
reportados. Las políticas y los conductores solo calculan caminos con `Conocimiento`.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra

TIPOS = ("camion", "campero", "moto")
CLASES = ("principal", "local", "estrecha")

# Supuesto declarado: velocidades en km/h por tipo de vehículo y clase de vía, ciudad después
# del sismo. 0 significa que ese tipo no puede usar esa clase de vía.
VELOCIDAD_KMH = {
    "camion": {"principal": 30.0, "local": 18.0, "estrecha": 0.0},
    "campero": {"principal": 35.0, "local": 22.0, "estrecha": 12.0},
    "moto": {"principal": 40.0, "local": 28.0, "estrecha": 15.0},
}

_PRINCIPAL = {"motorway", "trunk", "primary", "secondary",
              "motorway_link", "trunk_link", "primary_link", "secondary_link"}
_LOCAL = {"tertiary", "tertiary_link", "residential", "unclassified"}

CENTRO_MANIZALES = (5.0689, -75.5174)  # lat, lon de la plaza de Bolívar (aproximado)
SIN_CAMINO = -9999


def _clase_de(highway) -> int:
    texto = str(highway)
    etiquetas = [e.strip(" '\"[]") for e in texto.split(",")]
    if any(e in _PRINCIPAL for e in etiquetas):
        return 0
    if any(e in _LOCAL for e in etiquetas):
        return 1
    return 2


class Red:
    """Red verdadera. Nodos 0..n-1 y aristas dirigidas 0..m-1."""

    def __init__(self, lat, lon, eu, ev, largo_m, clase, origen: str):
        self.lat = np.asarray(lat, float)
        self.lon = np.asarray(lon, float)
        self.eu = np.asarray(eu, np.int32)
        self.ev = np.asarray(ev, np.int32)
        self.largo_m = np.asarray(largo_m, float)
        self.clase = np.asarray(clase, np.int8)
        self.origen = origen
        self.n = len(self.lat)
        self.m = len(self.eu)
        self.arista = {(int(u), int(v)): i for i, (u, v) in enumerate(zip(self.eu, self.ev))}
        self.segundos = {}
        for tipo in TIPOS:
            vel = np.array([VELOCIDAD_KMH[tipo][c] for c in CLASES])[self.clase]
            with np.errstate(divide="ignore"):
                self.segundos[tipo] = np.where(vel > 0, self.largo_m / (vel / 3.6), np.inf)

    # ---------- constructores ----------
    @classmethod
    def malla(cls, lado: int = 22, paso_m: float = 350.0, semilla: int = 0) -> "Red":
        """Malla sintética con avenidas cada cinco cuadras, vías estrechas y cuadras sin paso."""
        rng = np.random.default_rng(semilla)
        lat0, lon0 = CENTRO_MANIZALES
        xs, ys = np.meshgrid(np.arange(lado), np.arange(lado))
        x = (xs.ravel() - lado / 2) * paso_m + rng.normal(0, paso_m * 0.08, lado * lado)
        y = (ys.ravel() - lado / 2) * paso_m + rng.normal(0, paso_m * 0.08, lado * lado)
        lat = lat0 + y / 111_320.0
        lon = lon0 + x / (111_320.0 * math.cos(math.radians(lat0)))
        eu, ev, largo, clase = [], [], [], []
        for i in range(lado):
            for j in range(lado):
                a = i * lado + j
                for di, dj in ((0, 1), (1, 0)):
                    ii, jj = i + di, j + dj
                    if ii >= lado or jj >= lado:
                        continue
                    b = ii * lado + jj
                    avenida = (di == 0 and i % 5 == 0) or (dj == 0 and j % 5 == 0)
                    if avenida:
                        c = 0
                    else:
                        r = rng.random()
                        if r < 0.08:
                            continue  # cuadra sin paso
                        c = 2 if r < 0.20 else 1
                    d = float(np.hypot(x[a] - x[b], y[a] - y[b])) * 1.15  # las vías no son rectas
                    eu += [a, b]
                    ev += [b, a]
                    largo += [d, d]
                    clase += [c, c]
        return cls(lat, lon, eu, ev, largo, clase, origen=f"malla sintética {lado}x{lado}")

    @classmethod
    def desde_graphml(cls, ruta, radio_km: float = 6.0, centro=CENTRO_MANIZALES) -> "Red":
        """Lee el grafo de osmnx y se queda con la parte conectada a `radio_km` del centro."""
        import networkx as nx

        g = nx.read_graphml(ruta)
        lat0, lon0 = centro
        kx = 111.32 * math.cos(math.radians(lat0))
        ids, lat, lon = [], [], []
        for nodo, d in g.nodes(data=True):
            la, lo = float(d["y"]), float(d["x"])
            if math.hypot((la - lat0) * 111.32, (lo - lon0) * kx) <= radio_km:
                ids.append(nodo)
                lat.append(la)
                lon.append(lo)
        idx = {nodo: i for i, nodo in enumerate(ids)}
        mejor = {}
        for u, v, d in g.edges(data=True):
            if u not in idx or v not in idx or u == v:
                continue
            largo = float(d.get("length", 0.0)) or 1.0
            clave = (idx[u], idx[v])
            if clave not in mejor or largo < mejor[clave][0]:
                mejor[clave] = (largo, _clase_de(d.get("highway", "")))
        eu = np.array([k[0] for k in mejor], np.int32)
        ev = np.array([k[1] for k in mejor], np.int32)
        largo = np.array([v[0] for v in mejor.values()])
        clase = np.array([v[1] for v in mejor.values()], np.int8)
        # mayor componente fuertemente conexa, para que todo nodo sirva de punto o de acopio
        n = len(ids)
        _, etiqueta = connected_components(
            csr_matrix((np.ones(len(eu)), (eu, ev)), shape=(n, n)), connection="strong")
        grande = np.bincount(etiqueta).argmax()
        vivos = np.flatnonzero(etiqueta == grande)
        nuevo = -np.ones(n, np.int64)
        nuevo[vivos] = np.arange(len(vivos))
        ok = (nuevo[eu] >= 0) & (nuevo[ev] >= 0)
        return cls(np.array(lat)[vivos], np.array(lon)[vivos], nuevo[eu[ok]], nuevo[ev[ok]],
                   largo[ok], clase[ok], origen=f"OpenStreetMap, {Path(ruta).name}, radio {radio_km} km")

    # ---------- utilidades ----------
    def xy_m(self):
        lat0 = float(self.lat.mean())
        return ((self.lon - self.lon.mean()) * 111_320.0 * math.cos(math.radians(lat0)),
                (self.lat - lat0) * 111_320.0)

    def nodo_mas_cercano(self, lat: float, lon: float) -> int:
        kx = math.cos(math.radians(lat))
        return int(np.argmin(((self.lon - lon) * kx) ** 2 + (self.lat - lat) ** 2))

    def matriz(self, tipo: str, cerradas=()) -> csr_matrix:
        seg = self.segundos[tipo]
        ok = np.isfinite(seg)
        if len(cerradas):
            ok = ok.copy()
            ok[np.fromiter(cerradas, int)] = False
        return csr_matrix((seg[ok], (self.eu[ok], self.ev[ok])), shape=(self.n, self.n))


def ruta_cache() -> Path | None:
    """Busca el grafo de Manizales: variable de entorno, este árbol o la carpeta principal."""
    candidatas = [os.environ.get("DESPACHOX_GRAFO", ""),
                  Path(__file__).resolve().parents[1] / "cache" / "manizales.graphml"]
    aqui = Path(__file__).resolve()
    for padre in aqui.parents:  # si se corre desde un árbol de trabajo, mirar el repositorio principal
        if padre.name == ".claude":
            candidatas.append(padre.parent / "despacho" / "cache" / "manizales.graphml")
    for c in candidatas:
        if c and Path(c).is_file():
            return Path(c)
    return None


_RED_CACHE: dict = {}


def cargar_red(preferencia: str = "auto") -> Red:
    """`auto`: OpenStreetMap si el grafo está en disco; si no, la malla. `malla` la fuerza."""
    if preferencia not in _RED_CACHE:
        ruta = None if preferencia == "malla" else ruta_cache()
        if preferencia == "osm" and ruta is None:
            raise FileNotFoundError("No está despacho/cache/manizales.graphml")
        _RED_CACHE[preferencia] = Red.desde_graphml(ruta) if ruta else Red.malla()
    return _RED_CACHE[preferencia]


class Conocimiento:
    """La red tal como la conoce el despacho: sin los cierres ya reportados.

    `sitios` son los nodos del acopio (índice 0) y de los puntos. Mantiene, por tipo de
    vehículo, la matriz de tiempos entre sitios y los predecesores para reconstruir caminos.
    """

    def __init__(self, red: Red, sitios):
        self.red = red
        self.sitios = np.asarray(sitios, np.int32)
        self.cerradas = {t: set() for t in TIPOS}  # aristas cerradas conocidas, por tipo
        self.version = 0
        self._csr, self._t, self._pred, self._fila = {}, {}, {}, {}

    def agregar_cierre(self, aristas, tipos) -> None:
        for t in tipos:
            self.cerradas[t].update(aristas)
            for cache in (self._csr, self._t, self._pred):
                cache.pop(t, None)
        self._fila.clear()
        self.version += 1

    def _matriz(self, tipo):
        if tipo not in self._csr:
            self._csr[tipo] = self.red.matriz(tipo, self.cerradas[tipo])
        return self._csr[tipo]

    def _calcular(self, tipo):
        d, p = dijkstra(self._matriz(tipo), directed=True, indices=self.sitios,
                        return_predecessors=True)
        self._t[tipo] = d[:, self.sitios]
        self._pred[tipo] = p

    def tiempos(self, tipo: str) -> np.ndarray:
        """Matriz de segundos entre sitios (inf si no hay camino conocido)."""
        if tipo not in self._t:
            self._calcular(tipo)
        return self._t[tipo]

    def desde_nodo(self, tipo: str, nodo: int):
        """Tiempos y predecesores desde un nodo cualquiera a toda la red."""
        clave = (tipo, int(nodo))
        if clave not in self._fila:
            self._fila[clave] = dijkstra(self._matriz(tipo), directed=True, indices=int(nodo),
                                         return_predecessors=True)
        return self._fila[clave]

    def tiempos_desde_nodo(self, tipo: str, nodo: int) -> np.ndarray:
        """Segundos desde un nodo cualquiera hasta cada sitio."""
        return self.desde_nodo(tipo, nodo)[0][self.sitios]

    def camino(self, tipo: str, origen: int, destino: int):
        """Lista de nodos de `origen` a `destino` por la red conocida, o None si no hay."""
        origen, destino = int(origen), int(destino)
        if origen == destino:
            return [origen]
        pos = np.flatnonzero(self.sitios == origen)
        if len(pos):
            if tipo not in self._pred:
                self._calcular(tipo)
            pred = self._pred[tipo][pos[0]]
        else:
            pred = self.desde_nodo(tipo, origen)[1]
        if pred[destino] == SIN_CAMINO:
            return None
        camino = [destino]
        while camino[-1] != origen:
            camino.append(int(pred[camino[-1]]))
        camino.reverse()
        return camino
