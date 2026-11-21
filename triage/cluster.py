"""ST-DBSCAN propio con scipy.spatial.cKDTree (B.3.2). Etiqueta −1 = ruido (no se penaliza)."""
from __future__ import annotations

from collections import deque

import numpy as np
from scipy.spatial import cKDTree

from triage import geo

RUIDO = -1


def vecinos_st(lat, lon, t_horas, eps_s_m: float, eps_t_h: float) -> list[np.ndarray]:
    """Vecinos espacio-temporales de cada punto (incluido él mismo). Puntos sin coordenadas: solo él."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    t = np.asarray(t_horas, dtype=float)
    n = len(lat)
    validos = np.isfinite(lat) & np.isfinite(lon) & np.isfinite(t)
    vecinos = [np.array([i]) for i in range(n)]
    idx = np.flatnonzero(validos)
    if len(idx) == 0:
        return vecinos
    lat0, lon0 = float(np.mean(lat[idx])), float(np.mean(lon[idx]))
    x, y = geo.proyectar(lat[idx], lon[idx], lat0, lon0)
    arbol = cKDTree(np.c_[x, y])
    for k, cerca in enumerate(arbol.query_ball_point(np.c_[x, y], eps_s_m)):
        cerca = np.asarray(cerca, dtype=int)
        cerca = cerca[np.abs(t[idx[cerca]] - t[idx[k]]) <= eps_t_h]
        vecinos[idx[k]] = np.sort(idx[cerca])
    return vecinos


def dbscan_desde_vecinos(vecinos: list[np.ndarray], min_samples: int) -> np.ndarray:
    """DBSCAN estándar: núcleo con ≥ min_samples vecinos, expansión BFS, etiquetas en orden."""
    n = len(vecinos)
    etiquetas = np.full(n, RUIDO, dtype=int)
    nucleo = np.array([len(v) >= min_samples for v in vecinos], dtype=bool)
    actual = 0
    for i in range(n):
        if etiquetas[i] != RUIDO or not nucleo[i]:
            continue
        etiquetas[i] = actual
        cola = deque([i])
        while cola:
            j = cola.popleft()
            if not nucleo[j]:
                continue
            for k in vecinos[j]:
                if etiquetas[k] == RUIDO:
                    etiquetas[k] = actual
                    cola.append(k)
        actual += 1
    return etiquetas


def st_dbscan(lat, lon, t_horas, eps_s_m: float, eps_t_h: float, min_samples: int) -> np.ndarray:
    """Etiquetas de clúster (−1 = ruido) para solicitudes en espacio y tiempo."""
    lat = np.atleast_1d(np.asarray(lat, dtype=float))
    n = len(lat)
    if n == 0:
        return np.array([], dtype=int)
    if n == 1:
        return np.array([RUIDO], dtype=int)
    v = vecinos_st(lat, lon, t_horas, eps_s_m, eps_t_h)
    return dbscan_desde_vecinos(v, max(1, int(min_samples)))
