"""Red vial de la simulación.

`Red` es la red verdadera. `Conocimiento` es lo que el despacho cree de ella: la misma red
menos los cierres ya reportados. Políticas y conductores solo calculan caminos con `Conocimiento`.

Las velocidades y las reglas de acceso son las mismas de `despacho/red.py` y
`despacho/matriz.py` (el optimizador de B), para que el plan y la simulación hablen de la
misma ciudad: tiempo base por tipo de vía, un factor por tipo de vehículo, y el camión fuera
de las vías residenciales pero con permiso de parquear a 300 m del punto y descargar a mano.
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

TIPOS = ("camion", "campero", "moto")

# Copia de los supuestos de B. `tests/test_supuestos.py` falla si dejan de coincidir.
VELOCIDADES = {
    "motorway": 60, "trunk": 50, "primary": 40, "secondary": 35, "tertiary": 30,
    "unclassified": 25, "residential": 20, "living_street": 10, "service": 15,
    "motorway_link": 40, "trunk_link": 35, "primary_link": 30,
    "secondary_link": 25, "tertiary_link": 25,
}
VELOCIDAD_POR_DEFECTO = 20
FACTOR_TIEMPO = {"camion": 1.25, "campero": 1.0, "moto": 0.9}
VIAS_SIN_CAMION = {"residential", "living_street", "service", "track", "path", "pedestrian"}
TOLERANCIA_M = {"camion": 300.0, "campero": 400.0, "moto": 400.0}
# Supuesto de la simulación: un vehículo sin regreso por su red sale por cualquier vía de
# conducción, al doble del tiempo en las que no son aptas para él, y puede devolverse en
# contravía por donde vino, también al doble del tiempo.
FACTOR_EMERGENCIA = 2.0

CENTRO_MANIZALES = (5.0689, -75.5174)  # lat, lon de la plaza de Bolívar (aproximado)
SIN_CAMINO = -9999


def _via(highway) -> str:
    return str(highway).split(",")[0].strip(" '\"[]")


def _apta_camion(via: str, hgv="", maxweight="99") -> bool:
    if via in VIAS_SIN_CAMION or str(hgv).lower() in {"no", "private"}:
        return False
    try:
        return float(str(maxweight).split()[0]) >= 5
    except (ValueError, IndexError):
        return True


class Red:
    """Red verdadera. Nodos 0..n-1 y aristas dirigidas 0..m-1 (una por par de nodos)."""

    def __init__(self, lat, lon, eu, ev, largo_m, seg_general, seg_camion, origen: str, osm_id=None):
        self.lat = np.asarray(lat, float)
        self.lon = np.asarray(lon, float)
        self.eu = np.asarray(eu, np.int32)
        self.ev = np.asarray(ev, np.int32)
        self.largo_m = np.asarray(largo_m, float)
        self.origen = origen
        self.n, self.m = len(self.lat), len(self.eu)
        self.osm_id = np.arange(self.n) if osm_id is None else np.asarray(osm_id)
        self.arista = {(int(u), int(v)): i for i, (u, v) in enumerate(zip(self.eu, self.ev))}
        general, camion = np.asarray(seg_general, float), np.asarray(seg_camion, float)
        self.segundos = {"camion": np.maximum(camion * FACTOR_TIEMPO["camion"], 0.01),
                         "campero": np.maximum(general * FACTOR_TIEMPO["campero"], 0.01),
                         "moto": np.maximum(general * FACTOR_TIEMPO["moto"], 0.01)}
        # salida de emergencia: todas las vías; las no aptas para el tipo, al doble de tiempo
        self.segundos_emergencia = {
            t: np.where(np.isfinite(self.segundos[t]), self.segundos[t],
                        np.maximum(general * FACTOR_TIEMPO[t] * FACTOR_EMERGENCIA, 0.01)) for t in TIPOS}
        self._nodos_tipo, self._acceso = {}, {}

    # ---------- constructores ----------
    @classmethod
    def malla(cls, lado: int = 22, paso_m: float = 350.0, semilla: int = 0) -> "Red":
        """Malla sintética para pruebas: avenidas cada cinco cuadras, calles y callejones."""
        rng = np.random.default_rng(semilla)
        lat0, lon0 = CENTRO_MANIZALES
        xs, ys = np.meshgrid(np.arange(lado), np.arange(lado))
        x = (xs.ravel() - lado / 2) * paso_m + rng.normal(0, paso_m * 0.08, lado * lado)
        y = (ys.ravel() - lado / 2) * paso_m + rng.normal(0, paso_m * 0.08, lado * lado)
        lat = lat0 + y / 110_540.0
        lon = lon0 + x / (111_320.0 * math.cos(math.radians(lat0)))
        eu, ev, largo, general, camion = [], [], [], [], []
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
                        via = "secondary"
                    else:
                        r = rng.random()
                        if r < 0.08:
                            continue  # cuadra sin paso
                        via = "residential" if r < 0.20 else "tertiary"
                    d = float(np.hypot(x[a] - x[b], y[a] - y[b])) * 1.15  # las vías no son rectas
                    t = d / (VELOCIDADES[via] / 3.6)
                    eu += [a, b]
                    ev += [b, a]
                    largo += [d, d]
                    general += [t, t]
                    camion += [t if _apta_camion(via) else np.inf] * 2
        return cls(lat, lon, eu, ev, largo, general, camion, origen=f"malla sintética {lado}x{lado}")

    @classmethod
    def desde_graphml(cls, ruta) -> "Red":
        """Lee el grafo que guarda `despacho/red.py` (osmnx). Si no trae `travel_time`, lo calcula."""
        import networkx as nx

        g = nx.read_graphml(ruta)
        ids = list(g.nodes)
        idx = {nodo: i for i, nodo in enumerate(ids)}
        lat = [float(g.nodes[n]["y"]) for n in ids]
        lon = [float(g.nodes[n]["x"]) for n in ids]
        mejor = {}       # par -> [largo, segundos general, segundos camión]
        for u, v, d in g.edges(data=True):
            if u == v:
                continue
            via = _via(d.get("highway", ""))
            largo = float(d.get("length", 0.0)) or 1.0
            if "travel_time" in d:
                t = float(d["travel_time"])
            else:
                t = largo / (VELOCIDADES.get(via, VELOCIDAD_POR_DEFECTO) / 3.6)
            tc = t if _apta_camion(via, d.get("hgv", ""), d.get("maxweight", "99")) else np.inf
            par = (idx[u], idx[v])
            if par not in mejor:
                mejor[par] = [largo, t, tc]
            else:
                if t < mejor[par][1]:
                    mejor[par][0], mejor[par][1] = largo, t
                mejor[par][2] = min(mejor[par][2], tc)
        pares = list(mejor)
        vals = np.array([mejor[p] for p in pares])
        return cls(lat, lon, [p[0] for p in pares], [p[1] for p in pares], vals[:, 0], vals[:, 1], vals[:, 2],
                   origen=f"OpenStreetMap ({Path(ruta).name}, {len(ids)} nodos)",
                   osm_id=[int(n) for n in ids])

    # ---------- utilidades ----------
    def metros_a(self, lat: float, lon: float) -> np.ndarray:
        """Distancia en metros de cada nodo a un punto (misma aproximación plana que usa B)."""
        kx = 111_320 * math.cos(math.radians(lat))
        return np.hypot((self.lon - lon) * kx, (self.lat - lat) * 110_540)

    def nodos_del_tipo(self, tipo: str) -> np.ndarray:
        """Nodos que tocan alguna vía por la que ese tipo de vehículo puede pasar."""
        if tipo not in self._nodos_tipo:
            ok = np.isfinite(self.segundos[tipo])
            self._nodos_tipo[tipo] = np.unique(np.concatenate([self.eu[ok], self.ev[ok]]))
        return self._nodos_tipo[tipo]

    def nodo_de_acceso(self, tipo: str, nodo: int):
        """Nodo desde el que ese tipo de vehículo atiende un sitio, o None si no tiene acceso."""
        clave = (tipo, int(nodo))
        if clave not in self._acceso:
            cand = self.nodos_del_tipo(tipo)
            d = self.metros_a(self.lat[nodo], self.lon[nodo])[cand]
            k = int(d.argmin())
            self._acceso[clave] = int(cand[k]) if d[k] <= TOLERANCIA_M[tipo] else None
        return self._acceso[clave]

    def matriz(self, tipo: str, cerradas=()) -> csr_matrix:
        seg = self.segundos[tipo]
        ok = np.isfinite(seg)
        if len(cerradas):
            ok = ok.copy()
            ok[np.fromiter(cerradas, int)] = False
        return csr_matrix((seg[ok], (self.eu[ok], self.ev[ok])), shape=(self.n, self.n))


def ruta_cache() -> Path | None:
    """Busca el grafo de Manizales: variable de entorno, este árbol o la carpeta principal."""
    aqui = Path(__file__).resolve()
    candidatas = [os.environ.get("DESPACHOX_GRAFO", ""), aqui.parents[1] / "cache" / "manizales.graphml"]
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

    `sitios` son los nodos del acopio (índice 0) y de los puntos. Cada tipo de vehículo llega
    a un sitio por su propio nodo de acceso. Mantiene, por tipo, la matriz de segundos entre
    sitios y los predecesores para reconstruir caminos.
    """

    def __init__(self, red: Red, sitios):
        self.red = red
        self.sitios = [int(s) for s in sitios]
        self.nodos = {t: [red.nodo_de_acceso(t, s) for s in self.sitios] for t in TIPOS}
        self.cerradas = {t: set() for t in TIPOS}  # aristas cerradas conocidas, por tipo
        self.version = 0
        self._csr, self._t, self._pred, self._fila = {}, {}, {}, {}

    def nodo_sitio(self, tipo: str, sitio: int):
        return self.nodos[tipo][sitio]

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
        nodos = self.nodos[tipo]
        con = [i for i, n in enumerate(nodos) if n is not None]
        t = np.full((len(nodos), len(nodos)), np.inf)
        pred = {}
        if con:
            d, p = dijkstra(self._matriz(tipo), directed=True, indices=[nodos[i] for i in con],
                            return_predecessors=True)
            t[np.ix_(con, con)] = d[:, [nodos[i] for i in con]]
            pred = {nodos[i]: p[k] for k, i in enumerate(con)}
        self._t[tipo], self._pred[tipo] = t, pred

    def tiempos(self, tipo: str) -> np.ndarray:
        """Matriz de segundos entre sitios (inf si no hay camino conocido o no hay acceso)."""
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
        d = self.desde_nodo(tipo, nodo)[0]
        return np.array([d[n] if n is not None else np.inf for n in self.nodos[tipo]])

    def camino_emergencia(self, tipo: str, origen: int, destino: int):
        """Camino por cualquier vía de conducción, en cualquier sentido, menos los cierres conocidos."""
        r = self.red
        seg = r.segundos_emergencia[tipo]
        ok = np.ones(r.m, bool)
        if self.cerradas[tipo]:
            ok[np.fromiter(self.cerradas[tipo], int)] = False
        filas = np.concatenate([r.eu[ok], r.ev[ok]]).astype(np.int64)
        cols = np.concatenate([r.ev[ok], r.eu[ok]]).astype(np.int64)
        datos = np.concatenate([seg[ok], seg[ok] * FACTOR_EMERGENCIA])
        orden = np.lexsort((datos, filas * r.n + cols))          # por par, el sentido más rápido
        clave = (filas * r.n + cols)[orden]
        primero = np.concatenate([[True], clave[1:] != clave[:-1]])
        sel = orden[primero]
        m = csr_matrix((datos[sel], (filas[sel], cols[sel])), shape=(r.n, r.n))
        pred = dijkstra(m, directed=True, indices=int(origen), return_predecessors=True)[1]
        if int(origen) != int(destino) and pred[destino] == SIN_CAMINO:
            return None
        camino = [int(destino)]
        while camino[-1] != int(origen):
            camino.append(int(pred[camino[-1]]))
        camino.reverse()
        return camino

    def camino(self, tipo: str, origen: int, destino):
        """Lista de nodos de `origen` a `destino` por la red conocida, o None si no hay."""
        if destino is None:
            return None
        origen, destino = int(origen), int(destino)
        if origen == destino:
            return [origen]
        if tipo not in self._pred:
            self._calcular(tipo)
        pred = self._pred[tipo].get(origen)
        if pred is None:
            pred = self.desde_nodo(tipo, origen)[1]
        if pred[destino] == SIN_CAMINO:
            return None
        camino = [destino]
        while camino[-1] != origen:
            camino.append(int(pred[camino[-1]]))
        camino.reverse()
        return camino
