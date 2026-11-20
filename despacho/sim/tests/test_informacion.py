"""Información imperfecta: pedidos registrados en un punto equivocado."""
from despacho.sim.escenario import Parametros, generar
from despacho.sim.metricas import calcular
from despacho.sim.motor import Motor
from despacho.sim.politicas import Ingenua


class IngenuaQueConfirma(Ingenua):
    confirma_ubicacion = True


def test_sin_error_no_hay_viajes_en_falso():
    r = Motor(generar(4, "malla"), Ingenua()).correr()
    assert r.viajes_en_falso == 0


def test_sin_confirmar_el_error_cuesta_un_viaje_y_luego_se_corrige():
    esc = generar(4, "malla", Parametros(p_error=0.2))
    motor = Motor(esc, Ingenua())
    r = motor.correr()
    assert len(motor.con_error) > 0 and r.viajes_en_falso > 0
    assert r.viajes_en_falso <= len(motor.con_error)          # cada error se paga una sola vez
    # todo lo entregado llegó al punto real, nunca al equivocado
    assert all(motor.ped[pid].punto_id == motor.punto_real[pid] for pid in r.entregas)


def test_con_confirmacion_no_hay_viajes_en_falso_y_el_pedido_entra_despues():
    esc = generar(4, "malla", Parametros(p_error=0.2))
    motor = Motor(esc, IngenuaQueConfirma())
    r = motor.correr()
    assert r.viajes_en_falso == 0
    assert all(motor.ped[q.id].punto_id == q.punto_id for q in esc.pedidos)
    demora = esc.p.min_confirma_pedido * 60
    for pid in motor.con_error & set(r.entregas):
        assert r.entregas[pid]["t"] >= esc.pedidos[pid - 1].creado + demora


def test_los_mismos_pedidos_fallan_con_p_mayor():
    """El sorteo es común: quien falla con p = 0,1 también falla con p = 0,2."""
    a = Motor(generar(4, "malla", Parametros(p_error=0.1)), Ingenua()).con_error
    b = Motor(generar(4, "malla", Parametros(p_error=0.2)), Ingenua()).con_error
    assert a <= b


def test_p_cero_reproduce_la_corrida_sin_errores():
    a = calcular(Motor(generar(4, "malla"), Ingenua()).correr())
    b = calcular(Motor(generar(4, "malla", Parametros(p_error=0.0)), IngenuaQueConfirma()).correr())
    assert a == b
