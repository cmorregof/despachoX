"""Matrices de tiempo de viaje por tipo de vehículo, con los cierres confirmados ya quitados.

Cada tipo de vehículo ve una red distinta:
  - camión: sin vías residenciales, de servicio ni peatonales compartidas, y sin tramos con
    `hgv=no` o peso máximo menor al del camión. Si el punto queda a menos de `TOLERANCIA_M`
    de una vía apta, el camión parquea ahí y se descarga a mano.
  - campero y moto: toda la red de conducción.
Los cierres con estado `confirmado` quitan su arista (en los dos sentidos) para los tipos que
aparecen en `tipos_bloqueados`.

`riesgo` (opcional, gancho del A25 en `despacho/a25.py`): arista dirigida -> factor >= 1. El
camino se elige con el tiempo de cada arista multiplicado por su factor; `segundos` sigue siendo
el tiempo real de ese camino y `costo`, el tiempo encarecido que minimiza el solver. Sin `riesgo`
(o con todas sus aristas fuera de la red del tipo) todo queda igual que antes y `costo` es None.

Unidades: segundos enteros. Par inalcanzable: `INALCANZABLE` y un aviso.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

import networkx as nx
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

from despacho import red

INALCANZABLE = 10_000_000          # segundos; costo prohibitivo
TIPOS = ("camion", "campero", "moto")
# Supuestos nuestros, no medidos: el camión va más lento que el límite y la moto algo más rápido.
FACTOR_TIEMPO = {"camion": 1.25, "campero": 1.0, "moto": 0.9, "a_pie": 1.0}
VIAS_SIN_CAMION = {"residential", "living_street", "service", "track", "path", "pedestrian"}
TOLERANCIA_M = {"camion": 300.0, "campero": 400.0, "moto": 400.0, "a_pie": 400.0}


@dataclass
class Lugar:
    """Un sitio que entra en la matriz: acopio, punto de entrega o posición de un vehículo."""
    clave: str
    lat: float
    lon: float


@dataclass
class Matriz:
    tipo: str
    claves: list[str]
    segundos: np.ndarray                      # [i, j] entero; INALCANZABLE si no hay camino
    nodos: list[int | None]                   # nodo del grafo de cada lugar (None = fuera de la red)
    avisos: list[str] = field(default_factory=list)
    _pred: np.ndarray | None = None
    _ids: list[int] | None = None
    _pos: dict[int, int] | None = None
    costo: np.ndarray | None = None           # tiempo encarecido por el A25; None sin gancho

    def tiempo(self, a: str, b: str) -> int:
        return int(self.segundos[self.claves.index(a), self.claves.index(b)])

    def alcanzable(self, a: str, b: str) -> bool:
        return self.tiempo(a, b) < INALCANZABLE

    def camino(self, a: str, b: str) -> list[int]:
        """Nodos del grafo del camino más corto de a hacia b (vacío si no hay)."""
        i, j = self.claves.index(a), self.claves.index(b)
        if self.nodos[i] is None or self.nodos[j] is None or self.segundos[i, j] >= INALCANZABLE:
            return []
        origen, k = self._pos[self.nodos[i]], self._pos[self.nodos[j]]
        ruta = [k]
        while k != origen:
            k = int(self._pred[i, k])
            if k < 0:
                return []
            ruta.append(k)
        return [self._ids[n] for n in reversed(ruta)]

    def geometria(self, g: nx.MultiDiGraph, a: str, b: str) -> list[list[float]]:
        return red.geometria(g, self.camino(a, b))


def aristas_cerradas(cierres: list[dict]) -> dict[str, set[tuple[int, int]]]:
    """Por tipo de vehículo, las aristas (u, v) cerradas. Cada cierre bloquea los dos sentidos."""
    cerradas: dict[str, set[tuple[int, int]]] = {t: set() for t in FACTOR_TIEMPO}
    for c in cierres:
        if c.get("estado", "confirmado") != "confirmado" or c.get("osm_u") is None or c.get("osm_v") is None:
            continue
        try:
            tipos = json.loads(c.get("tipos_bloqueados") or '["camion","campero","moto"]')
        except (TypeError, ValueError):
            tipos = list(TIPOS)
        u, v = int(c["osm_u"]), int(c["osm_v"])
        for t in tipos:
            cerradas.setdefault(t, set()).update({(u, v), (v, u)})
    return cerradas


def _apta_camion(datos: dict) -> bool:
    if red.tipo_via(datos) in VIAS_SIN_CAMION:
        return False
    if str(datos.get("hgv", "")).lower() in {"no", "private"}:
        return False
    try:
        if float(str(datos.get("maxweight", "99")).split()[0]) < 5:
            return False
    except ValueError:
        pass
    return True


def _red_del_tipo(g: nx.MultiDiGraph, tipo: str, cerradas: set[tuple[int, int]]):
    """Matriz dispersa de tiempos de la subred del tipo y el conjunto de nodos que toca."""
    ids = list(g.nodes)
    pos = {n: k for k, n in enumerate(ids)}
    mejor: dict[tuple[int, int], float] = {}
    factor = FACTOR_TIEMPO.get(tipo, 1.0)
    for u, v, datos in g.edges(data=True):
        if u == v or (u, v) in cerradas:
            continue
        if tipo == "camion" and not _apta_camion(datos):
            continue
        t = float(datos.get("travel_time", 0.0)) * factor
        par = (pos[u], pos[v])
        if par not in mejor or t < mejor[par]:
            mejor[par] = t
    if not mejor:
        return csr_matrix((len(ids), len(ids))), ids, pos, set()
    filas, cols = zip(*mejor.keys())
    m = csr_matrix((np.maximum(list(mejor.values()), 0.01), (filas, cols)), shape=(len(ids), len(ids)))
    usados = {ids[k] for k in set(filas) | set(cols)}
    return m, ids, pos, usados


def _encarecer(m: csr_matrix, pos: dict[int, int], riesgo: dict[tuple[int, int], float] | None):
    """Copia de `m` con el tiempo de las aristas en riesgo multiplicado por su factor.

    Devuelve (matriz, extra) con extra[(a, b)] = segundos añadidos a la arista de índices a -> b,
    o (m, {}) si ninguna arista en riesgo está en esta red.
    """
    extra: dict[tuple[int, int], float] = {}
    if not riesgo:
        return m, extra
    mc = None
    for (u, v), f in riesgo.items():
        if f <= 1.0 or u not in pos or v not in pos:
            continue
        a, b = pos[u], pos[v]
        t = float(m[a, b])
        if t <= 0:                       # la arista no existe en la red de este tipo
            continue
        if mc is None:
            mc = m.copy()
        mc[a, b] = t * f
        extra[(a, b)] = t * (f - 1.0)
    return (mc, extra) if mc is not None else (m, extra)


def _extra_del_camino(pred_fila: np.ndarray, origen: int, destino: int, extra: dict) -> float:
    """Segundos de encarecimiento que suma el camino origen -> destino del árbol `pred_fila`."""
    total, k = 0.0, destino
    while k != origen:
        p = int(pred_fila[k])
        if p < 0:
            break
        total += extra.get((p, k), 0.0)
        k = p
    return total


def calcular(g: nx.MultiDiGraph, lugares: list[Lugar], cierres: list[dict] | None = None,
             tipos: tuple[str, ...] = TIPOS,
             riesgo: dict[tuple[int, int], float] | None = None) -> dict[str, Matriz]:
    """Una `Matriz` por tipo de vehículo entre todos los `lugares`. `riesgo`: ver el encabezado."""
    cerradas = aristas_cerradas(cierres or [])
    resultado: dict[str, Matriz] = {}
    for tipo in tipos:
        m, ids, pos, usados = _red_del_tipo(g, tipo, cerradas.get(tipo, set()))
        mc, extra = _encarecer(m, pos, riesgo)
        if cerradas.get(tipo):
            # Cada lugar se amarra a la red sin cierres: si un cierre lo corta, queda aislado
            # en vez de "saltar" a otra vía cercana.
            usados = _red_del_tipo(g, tipo, set())[3]
        avisos: list[str] = []
        nodos: list[int | None] = []
        for l in lugares:
            if not usados:
                nodos.append(None)
                continue
            n, d = red.nodo_cercano(g, l.lat, l.lon, usados)
            if d > TOLERANCIA_M.get(tipo, 400.0):
                nodos.append(None)
                avisos.append(f"{l.clave}: la vía apta para {tipo} más cercana está a {d:.0f} m")
            else:
                nodos.append(n)
        n_l = len(lugares)
        seg = np.full((n_l, n_l), INALCANZABLE, dtype=np.int64)
        costo = np.full((n_l, n_l), INALCANZABLE, dtype=np.int64) if extra else None
        pred = np.full((n_l, len(ids)), -9999, dtype=np.int32)
        con_nodo = [i for i, n in enumerate(nodos) if n is not None]
        if con_nodo:
            dist, pr = dijkstra(mc, directed=True, indices=[pos[nodos[i]] for i in con_nodo],
                                return_predecessors=True)
            for fila, i in enumerate(con_nodo):
                pred[i] = pr[fila]
                for j in con_nodo:
                    d = dist[fila, pos[nodos[j]]]
                    if np.isfinite(d):
                        if costo is None:
                            seg[i, j] = int(round(d))
                        else:
                            costo[i, j] = int(round(d))
                            seg[i, j] = int(round(d - _extra_del_camino(pr[fila], pos[nodos[i]],
                                                                         pos[nodos[j]], extra)))
        np.fill_diagonal(seg, 0)
        if costo is not None:
            np.fill_diagonal(costo, 0)
        claves = [l.clave for l in lugares]
        for i in con_nodo:
            sin = [claves[j] for j in con_nodo if seg[i, j] >= INALCANZABLE]
            if sin and len(sin) < len(con_nodo) - 1:
                avisos.append(f"{tipo}: desde {claves[i]} no hay camino hacia {', '.join(sin)}")
            elif sin:
                avisos.append(f"{tipo}: {claves[i]} quedó aislado de la red")
        resultado[tipo] = Matriz(tipo, claves, seg, nodos, avisos, pred, ids, pos, costo)
    return resultado
