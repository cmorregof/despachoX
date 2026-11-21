"""Opción de velocidades medidas de la simulación (datos_publicos/velocidades.csv).

Apagada, que es el valor por defecto, la simulación y el optimizador quedan como antes.
Encendida, los dos usan los mismos segundos por tramo, sacados del CSV.
"""
import numpy as np
import pytest

from despacho.sim import red_sim
from despacho.sim.red_sim import VARIABLE_VELOCIDADES, ruta_cache

sin_grafo = pytest.mark.skipif(ruta_cache() is None, reason="falta el grafo de Manizales en despacho/cache")


def test_por_defecto_es_el_modelo(monkeypatch):
    monkeypatch.delenv(VARIABLE_VELOCIDADES, raising=False)
    assert red_sim.modo_velocidades() == "modelo"
    monkeypatch.setenv(VARIABLE_VELOCIDADES, "")
    assert red_sim.modo_velocidades() == "modelo"
    monkeypatch.setenv(VARIABLE_VELOCIDADES, "Medidas")
    assert red_sim.modo_velocidades() == "medidas"
    monkeypatch.setenv(VARIABLE_VELOCIDADES, "rapidas")
    with pytest.raises(ValueError):
        red_sim.modo_velocidades()


def test_el_csv_cubre_las_vias_del_modelo():
    tabla = red_sim.velocidades_medidas()
    assert set(red_sim.VELOCIDADES) <= set(tabla)
    assert all(v > 0 for fila in tabla.values() for v in fila.values())
    # vía sin fila: el supuesto del modelo, 20 km/h con el factor del vehículo
    assert red_sim.velocidad_medida(tabla, "ladder", "camion") == pytest.approx(16.0)


@sin_grafo
def test_apagada_da_los_mismos_segundos_que_la_formula_anterior(monkeypatch):
    """Sin la variable, cada tramo vale `travel_time` del grafo por el factor del vehículo."""
    import networkx as nx

    monkeypatch.delenv(VARIABLE_VELOCIDADES, raising=False)
    r = red_sim.cargar_red("osm")
    g = nx.read_graphml(ruta_cache())
    idx = {n: i for i, n in enumerate(g.nodes)}
    general, camion = {}, {}
    for u, v, d in g.edges(data=True):
        if u == v:
            continue
        par, t = (idx[u], idx[v]), float(d["travel_time"])
        apta = red_sim._apta_camion(red_sim._via(d.get("highway", "")), d.get("hgv", ""), d.get("maxweight", "99"))
        general[par] = min(general.get(par, np.inf), t)
        camion[par] = min(camion.get(par, np.inf), t if apta else np.inf)
    pares = list(zip(r.eu.tolist(), r.ev.tolist()))
    esperado = {"campero": np.array([general[p] for p in pares]),
                "moto": np.array([general[p] for p in pares]) * 0.9,
                "camion": np.array([camion[p] for p in pares]) * 1.25}
    for tipo in red_sim.TIPOS:
        assert np.array_equal(r.segundos[tipo], np.maximum(esperado[tipo], 0.01))
    assert "velocidades medidas" not in r.origen


@sin_grafo
def test_encendida_cada_tramo_va_a_la_velocidad_del_csv(monkeypatch):
    monkeypatch.setenv(VARIABLE_VELOCIDADES, "medidas")
    r = red_sim.cargar_red("osm")
    tabla = red_sim.velocidades_medidas()
    import networkx as nx

    g = nx.read_graphml(ruta_cache())
    idx = {n: i for i, n in enumerate(g.nodes)}
    vistos = set()
    for u, v, d in g.edges(data=True):
        via = red_sim._via(d.get("highway", ""))
        if u == v or len(g[u][v]) > 1 or via in vistos or via not in tabla:
            continue
        e = r.arista[(idx[u], idx[v])]
        for tipo in ("campero", "moto"):
            assert r.largo_m[e] / r.segundos[tipo][e] * 3.6 == pytest.approx(tabla[via][tipo])
        if np.isfinite(r.segundos["camion"][e]):
            assert r.largo_m[e] / r.segundos["camion"][e] * 3.6 == pytest.approx(tabla[via]["camion"])
        else:
            assert via in red_sim.VIAS_SIN_CAMION
        vistos.add(via)
    assert {"trunk", "primary", "secondary", "tertiary", "residential"} <= vistos
    assert "velocidades medidas" in r.origen


@sin_grafo
def test_encendida_misma_matriz_que_el_optimizador(monkeypatch):
    """Con velocidades medidas, el modelo de B ve los mismos segundos que la jornada simulada."""
    matriz = pytest.importorskip("despacho.matriz")
    from despacho.sim.adaptador_b import OptimizadorB
    from despacho.sim.escenario import generar
    from despacho.sim.red_sim import Conocimiento

    monkeypatch.setenv(VARIABLE_VELOCIDADES, "medidas")
    esc = generar(1, "osm", n_puntos=30)
    con = Conocimiento(esc.red, esc.sitios)
    r = esc.red
    lugares = [matriz.Lugar(f"s{i}", float(r.lat[n]), float(r.lon[n])) for i, n in enumerate(esc.sitios)]
    opt = OptimizadorB(1)
    assert "velocidades medidas" in opt.nombre
    suyas = opt.matrices(lugares)
    for tipo in red_sim.TIPOS:
        mia = con.tiempos(tipo).copy()
        suya = suyas[tipo].segundos.astype(float)
        suya[suya >= matriz.INALCANZABLE] = np.inf
        np.fill_diagonal(mia, 0.0)
        assert np.array_equal(np.isinf(mia), np.isinf(suya))
        ok = np.isfinite(mia)
        assert np.abs(mia[ok] - suya[ok]).max() <= 1.0


@sin_grafo
def test_apagada_el_optimizador_recibe_el_grafo_de_siempre(monkeypatch):
    matriz = pytest.importorskip("despacho.matriz")
    from despacho import red
    from despacho.sim.adaptador_b import OptimizadorB

    monkeypatch.delenv(VARIABLE_VELOCIDADES, raising=False)
    opt = OptimizadorB(1)
    assert opt._por_tipo is None and opt.g is red.cargar()
    assert matriz.calcular is opt.mod.mod_matriz.calcular
    r = red_sim.cargar_red("osm")
    lugares = [matriz.Lugar(f"s{i}", float(r.lat[n]), float(r.lon[n])) for i, n in enumerate([0, 50, 500])]
    for tipo, m in opt.matrices(lugares).items():
        assert np.array_equal(m.segundos, matriz.calcular(red.cargar(), lugares)[tipo].segundos)
