"""ST-DBSCAN contra una referencia por fuerza bruta (independiente del cKDTree)."""
import numpy as np

from triage import cluster, geo


def dbscan_fuerza_bruta(lat, lon, t, eps_s, eps_t, min_samples):
    """Referencia: matriz completa de distancias y el DBSCAN clásico de libro."""
    lat0, lon0 = lat.mean(), lon.mean()
    x, y = geo.proyectar(lat, lon, lat0, lon0)
    n = len(lat)
    d = np.sqrt((x[:, None] - x[None, :]) ** 2 + (y[:, None] - y[None, :]) ** 2)
    adj = (d <= eps_s) & (np.abs(t[:, None] - t[None, :]) <= eps_t)
    etiquetas = [-1] * n
    visitado = [False] * n
    c = -1
    for i in range(n):
        if visitado[i] or etiquetas[i] != -1:
            continue
        vec = list(np.flatnonzero(adj[i]))
        if len(vec) < min_samples:
            continue
        c += 1
        etiquetas[i] = c
        visitado[i] = True
        frontera = [j for j in vec if j != i]
        en_frontera = set(frontera)
        k = 0
        while k < len(frontera):
            j = frontera[k]
            k += 1
            if etiquetas[j] == -1:
                etiquetas[j] = c
            if visitado[j]:
                continue
            visitado[j] = True
            vj = np.flatnonzero(adj[j])
            if len(vj) >= min_samples:
                for m in vj:
                    if etiquetas[m] == -1 and m not in en_frontera:
                        frontera.append(m)
                        en_frontera.add(m)
    return np.array(etiquetas)


def _mismas_particiones(a, b):
    """Igualdad de agrupación: mismo ruido y mismos pares juntos."""
    assert np.array_equal(a == -1, b == -1)
    juntos_a = a[:, None] == a[None, :]
    juntos_b = b[:, None] == b[None, :]
    mask = (a != -1)[:, None] & (a != -1)[None, :]
    assert np.array_equal(juntos_a & mask, juntos_b & mask)


def test_igual_a_fuerza_bruta_200_puntos():
    rng = np.random.default_rng(2026)
    n = 200
    # Mezcla de focos y puntos sueltos sobre Manizales.
    centros = np.array([[5.068, -75.517], [5.055, -75.49], [5.08, -75.50]])
    k = rng.integers(0, 3, n)
    lat = centros[k, 0] + rng.normal(0, 0.003, n)
    lon = centros[k, 1] + rng.normal(0, 0.003, n)
    t = rng.uniform(0, 24, n)
    for eps_s, eps_t, ms in [(250, 6, 3), (400, 3, 4), (150, 12, 2)]:
        a = cluster.st_dbscan(lat, lon, t, eps_s, eps_t, ms)
        b = dbscan_fuerza_bruta(lat, lon, t, eps_s, eps_t, ms)
        _mismas_particiones(a, b)
        assert np.array_equal(a, b)          # mismo orden de descubrimiento
        assert a.max() >= 1


def test_vacio_y_un_punto():
    assert cluster.st_dbscan([], [], [], 250, 6, 3).size == 0
    assert list(cluster.st_dbscan([5.06], [-75.5], [0.0], 250, 6, 3)) == [-1]


def test_todos_ruido():
    lat = np.array([5.00, 5.05, 5.10, 5.15])
    lon = np.array([-75.5, -75.5, -75.5, -75.5])
    assert list(cluster.st_dbscan(lat, lon, np.zeros(4), 250, 6, 3)) == [-1] * 4


def test_condicion_de_tiempo():
    lat = np.full(6, 5.06)
    lon = np.full(6, -75.5)
    juntos = cluster.st_dbscan(lat, lon, np.array([0, 0.5, 1, 1.5, 2, 2.5]), 250, 6, 3)
    assert len(set(juntos)) == 1 and juntos[0] == 0
    separados = cluster.st_dbscan(lat, lon, np.array([0, 10, 20, 30, 40, 50]), 250, 6, 3)
    assert list(separados) == [-1] * 6
    dos = cluster.st_dbscan(lat, lon, np.array([0, 0.1, 0.2, 30, 30.1, 30.2]), 250, 6, 3)
    assert list(dos) == [0, 0, 0, 1, 1, 1]


def test_coordenadas_nan_son_ruido():
    lat = np.array([5.06, 5.06, 5.06, np.nan])
    lon = np.array([-75.5, -75.5, -75.5, -75.5])
    assert list(cluster.st_dbscan(lat, lon, np.zeros(4), 250, 6, 3)) == [0, 0, 0, -1]
