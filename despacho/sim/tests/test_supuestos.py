"""La simulación y el optimizador de B deben describir la misma ciudad y entenderse."""
import pytest

from despacho.sim import red_sim
from despacho.sim.red_sim import ruta_cache

matriz = pytest.importorskip("despacho.matriz", reason="el optimizador de B todavía no está en esta rama")


def test_mismas_velocidades_y_reglas_de_acceso_que_el_optimizador():
    from despacho import red
    assert red_sim.VELOCIDADES == red.VELOCIDADES
    assert red_sim.VELOCIDAD_POR_DEFECTO == red.VELOCIDAD_POR_DEFECTO
    assert red_sim.VIAS_SIN_CAMION == matriz.VIAS_SIN_CAMION
    for tipo in red_sim.TIPOS:
        assert red_sim.FACTOR_TIEMPO[tipo] == matriz.FACTOR_TIEMPO[tipo]
        assert red_sim.TOLERANCIA_M[tipo] == matriz.TOLERANCIA_M[tipo]


@pytest.mark.skipif(ruta_cache() is None, reason="falta despacho/cache/manizales.graphml")
def test_misma_matriz_de_tiempos_que_el_optimizador():
    """Los segundos entre sitios de la simulación coinciden con los de `matriz.calcular`."""
    import numpy as np
    from despacho import red
    from despacho.sim.escenario import generar
    from despacho.sim.red_sim import Conocimiento

    esc = generar(1, "osm", n_puntos=30)
    con = Conocimiento(esc.red, esc.sitios)
    r = esc.red
    lugares = [matriz.Lugar(f"s{i}", float(r.lat[n]), float(r.lon[n])) for i, n in enumerate(esc.sitios)]
    suyas = matriz.calcular(red.cargar(), lugares)
    for tipo in red_sim.TIPOS:
        mia = con.tiempos(tipo).copy()
        suya = suyas[tipo].segundos.astype(float)
        suya[suya >= matriz.INALCANZABLE] = np.inf
        np.fill_diagonal(mia, 0.0)                          # B deja en 0 la diagonal aun sin acceso
        assert np.array_equal(np.isinf(mia), np.isinf(suya))
        ok = np.isfinite(mia)
        assert np.abs(mia[ok] - suya[ok]).max() <= 1.0      # B redondea a segundos enteros


@pytest.mark.skipif(ruta_cache() is None, reason="falta despacho/cache/manizales.graphml")
def test_el_adaptador_devuelve_rutas_validas():
    from despacho.sim.adaptador_b import OptimizadorB
    from despacho.sim.escenario import generar
    from despacho.sim.motor import Motor
    from despacho.sim.politicas import crear

    esc = generar(2, "osm", n_puntos=30)
    opt = OptimizadorB(1)
    motor = Motor(esc, crear("optimiza_una_vez", opt))
    r = motor.correr()
    assert opt.fallos == 0 and opt.llamadas == 1
    assert r.invalidas == 0 and len(r.entregas) > 0
    assert all(v.max_carga <= v.cap + 1e-6 for v in r.vehiculos)
