"""Opción de vida útil por producto (datos_publicos/vida_util.csv). Por defecto no cambia nada."""
import numpy as np
import pytest

from despacho.sim.escenario import H, NIVELES_CARGA, Parametros, generar, vida_util_csv


def test_canasta_sale_de_los_csv():
    canasta = {p: (h, w) for p, h, w in vida_util_csv()}
    # leche pasteurizada con frío 72 h; huevos, la menor de dos filas; verdura, el tomate maduro;
    # papa con frío. La fruta no tiene cifra en horas y el pollo y el pan no tienen ración.
    assert canasta == {"leche": (72.0, 0.4), "huevos": (360.0, 0.24), "verdura": (96.0, 0.1),
                       "papa": (2920.0, 0.1)}


def test_solo_cambia_el_vencimiento_de_los_lotes():
    base = generar(7, "malla", Parametros(**NIVELES_CARGA["media"]))
    otro = generar(7, "malla", Parametros(**NIVELES_CARGA["media"], vida_util="csv"))
    assert [(l.id, l.kg) for l in base.lotes] == [(l.id, l.kg) for l in otro.lotes]
    assert [(q.id, q.punto_id, q.kg, q.kg_perecedero, q.limite) for q in base.pedidos] == \
           [(q.id, q.punto_id, q.kg, q.kg_perecedero, q.limite) for q in otro.pedidos]
    assert [c.aristas for c in base.cierres] == [c.aristas for c in otro.cierres]
    vida = {p: h for p, h, _ in vida_util_csv()}
    assert all(0 <= l.vence <= vida[l.producto] * H for l in otro.lotes)
    assert all(l.producto == "" and 6 * H <= l.vence <= 48 * H for l in base.lotes)
    assert not np.allclose([l.vence for l in base.lotes], [l.vence for l in otro.lotes])


def test_valor_desconocido_falla():
    with pytest.raises(ValueError):
        generar(7, "malla", Parametros(vida_util="semanas"))
