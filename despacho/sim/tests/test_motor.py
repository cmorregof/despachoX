"""Pruebas del motor. Correr desde la raíz: python -m pytest despacho/sim/tests -q"""
import pytest

from despacho.sim.escenario import Cierre, Lote, Pedido, Vehiculo, generar
from despacho.sim.metricas import calcular
from despacho.sim.motor import Motor, simular
from despacho.sim.politicas import POLITICAS, InsercionProvisional, crear
from despacho.sim.red_sim import Conocimiento, Red

H = 3600.0


class Fija:
    """Política de prueba: entrega un plan fijo al inicio y no vuelve a opinar."""
    disparadores = {"inicio"}
    ultimo_fue_optimizador = False
    nombre = "fija"

    def __init__(self, rutas, regla_lotes="fefo"):
        self.rutas, self.regla_lotes = rutas, regla_lotes

    def planificar(self, estado):
        return self.rutas

    def demora_s(self, estado):
        return 0.0


@pytest.fixture(scope="module")
def red():
    return Red.malla(lado=12, semilla=7)


def mini(red, pedidos, vehiculos, lotes=(), cierres=()):
    esc = generar(11, red, n_puntos=6, n_cierres=0)
    esc.pedidos, esc.vehiculos, esc.lotes, esc.cierres = list(pedidos), list(vehiculos), list(lotes), list(cierres)
    return esc


def pedido(i, punto, kg, per=0.0, creado=0.0, urg=2):
    return Pedido(i, creado, punto, 5, kg, per, urg, creado + 5 * H)


# ---------- capacidad ----------
def test_no_carga_mas_que_la_capacidad_aunque_el_plan_lo_pida(red):
    pedidos = [pedido(i, 1 + i % 6, 300.0) for i in range(1, 7)]      # 1800 kg en total
    esc = mini(red, pedidos, [Vehiculo(1, "campero", 700.0)])
    r = simular(esc, Fija({1: [1, 2, 3, 4, 5, 6]}))                   # todo en un solo viaje
    assert r.vehiculos[0].max_carga <= 700.0
    assert len(r.entregas) == 6                                       # los entrega en tres viajes


def test_pedido_mayor_que_el_vehiculo_se_rechaza(red):
    esc = mini(red, [pedido(1, 1, 200.0)], [Vehiculo(1, "moto", 60.0)])
    r = simular(esc, Fija({1: [1]}))
    assert r.entregas == {} and r.invalidas == 1


@pytest.mark.parametrize("nombre", POLITICAS)
def test_las_politicas_respetan_capacidad_y_conservan_los_kilos(nombre):
    esc = generar(5, "malla")
    motor = Motor(esc, crear(nombre, InsercionProvisional(0.2)))
    r = motor.correr()
    for v in r.vehiculos:
        assert v.max_carga <= v.cap + 1e-6
    assert r.invalidas == 0
    # cada kilo perecedero está en bodega, a bordo o entregado (válido o vencido)
    a_bordo = sum(kg for v in r.vehiculos for items in v.carga.values() for l, kg in items if l is not None)
    entregado = sum(r.kg_valido_por_lote.values()) + sum(e["kg_vencido"] for e in r.entregas.values())
    if not any(v.estado == "fuera" for v in r.vehiculos):     # la carga de un vehículo aislado se pierde
        assert sum(motor.inv.values()) + a_bordo + entregado == pytest.approx(sum(l.kg for l in esc.lotes))
    assert all(kg >= -1e-6 for kg in motor.inv.values())


# ---------- vencimientos ----------
def test_lote_vencido_no_cuenta_como_entregado(red):
    # el lote vence un minuto después de cargar: llega vencido a cualquier punto
    esc = mini(red, [pedido(1, 1, 100.0, per=40.0)], [Vehiculo(1, "campero", 700.0)],
               lotes=[Lote(1, 40.0, 11 * 60.0)])
    r = simular(esc, Fija({1: [1]}))
    e = r.entregas[1]
    assert e["t"] > 11 * 60.0
    assert e["kg_ok"] == pytest.approx(60.0) and e["kg_vencido"] == pytest.approx(40.0)
    m = calcular(r)
    assert m["perecedero_vencido_pct"] == pytest.approx(100.0)
    assert m["demanda_no_atendida_pct"] == pytest.approx(40.0)


def test_lote_ya_vencido_no_se_carga_y_fefo_saca_primero_lo_que_vence_antes(red):
    lotes = [Lote(1, 40.0, 40 * H), Lote(2, 40.0, 9 * H), Lote(3, 40.0, 0.0)]
    esc = mini(red, [pedido(1, 1, 100.0, per=40.0)], [Vehiculo(1, "campero", 700.0)], lotes=lotes)
    fefo = simular(esc, Fija({1: [1]}, "fefo"))
    fifo = simular(esc, Fija({1: [1]}, "fifo"))
    assert fefo.kg_valido_por_lote == {1: 0.0, 2: 40.0, 3: 0.0}
    assert fifo.kg_valido_por_lote == {1: 40.0, 2: 0.0, 3: 0.0}
    # con fifo el lote 2 vence en bodega dentro de la jornada; el 3 ya estaba vencido en ambos
    assert calcular(fefo)["perecedero_vencido_pct"] == pytest.approx(100 * 40 / 120)
    assert calcular(fifo)["perecedero_vencido_pct"] == pytest.approx(100 * 80 / 120)


# ---------- cierres ----------
def _camino_previsto(esc, tipo, punto):
    con = Conocimiento(esc.red, esc.sitios)
    return con.camino(tipo, esc.acopio_nodo, esc.puntos[punto - 1].nodo)


def _punto_lejano(esc):
    return max(esc.puntos, key=lambda q: len(_camino_previsto(esc, "campero", q.id) or [])).id


def test_cierre_desconocido_no_altera_la_ruta_hasta_que_se_descubre(red):
    base = mini(red, [], [Vehiculo(1, "campero", 700.0)])
    punto = _punto_lejano(base)
    camino = _camino_previsto(base, "campero", punto)
    assert len(camino) >= 5
    k = len(camino) // 2                                    # se cierra un tramo a mitad de camino
    a, b = camino[k], camino[k + 1]
    cierre = Cierre(1, (red.arista[(a, b)], red.arista[(b, a)]), 0.0, ("camion", "campero"))
    libre = simular(mini(red, [pedido(1, punto, 100.0)], [Vehiculo(1, "campero", 700.0)]), Fija({1: [1]}))
    cerrado = simular(mini(red, [pedido(1, punto, 100.0)], [Vehiculo(1, "campero", 700.0)], cierres=[cierre]),
                      Fija({1: [1]}))
    t_libre, t_cerrado = libre.vehiculos[0].traza, cerrado.vehiculos[0].traza
    # hasta el nodo donde se topa el cierre, la ruta es la misma que sin cierre
    assert t_cerrado[:k] == camino[1:k + 1] == t_libre[:k]
    # el cierre se descubre al llegar a ese nodo, no antes
    seg = red.segundos["campero"]
    t_tope = base.p.min_carga * 60 + sum(seg[red.arista[(u, v)]] for u, v in zip(camino[:k], camino[1:k + 1]))
    assert cerrado.descubiertos[1] == pytest.approx(t_tope)
    # después se desvía: nunca cruza el tramo cerrado y entrega más tarde
    pasos = list(zip([base.acopio_nodo] + t_cerrado, t_cerrado))
    assert (a, b) not in pasos and (b, a) not in pasos
    assert cerrado.entregas[1]["t"] > libre.entregas[1]["t"]


def test_cierre_fuera_de_la_ruta_no_se_descubre_ni_cambia_nada(red):
    base = mini(red, [], [Vehiculo(1, "campero", 700.0)])
    punto = _punto_lejano(base)
    usados = set(_camino_previsto(base, "campero", punto)) | set(
        Conocimiento(red, base.sitios).camino("campero", base.puntos[punto - 1].nodo, base.acopio_nodo))
    a, b = next((int(u), int(v)) for u, v in zip(red.eu, red.ev) if u not in usados and v not in usados)
    cierre = Cierre(1, (red.arista[(a, b)],), 0.0, ("camion", "campero", "moto"))
    arma = lambda cs: mini(red, [pedido(1, punto, 100.0)], [Vehiculo(1, "campero", 700.0)], cierres=cs)
    libre, cerrado = simular(arma([]), Fija({1: [1]})), simular(arma([cierre]), Fija({1: [1]}))
    assert cerrado.descubiertos == {}
    assert cerrado.vehiculos[0].traza == libre.vehiculos[0].traza


def test_cierre_que_ocurre_despues_de_pasar_no_afecta(red):
    base = mini(red, [], [Vehiculo(1, "campero", 700.0)])
    punto = _punto_lejano(base)
    camino = _camino_previsto(base, "campero", punto)
    a, b = camino[1], camino[2]
    cierre = Cierre(1, (red.arista[(a, b)],), 10 * H, ("campero",))      # ocurre en la hora 10
    r = simular(mini(red, [pedido(1, punto, 100.0)], [Vehiculo(1, "campero", 700.0)], cierres=[cierre]),
                Fija({1: [1]}))
    assert r.descubiertos == {} and r.vehiculos[0].traza[:len(camino) - 1] == camino[1:]


def test_cierre_solo_para_camion_deja_pasar_la_moto(red):
    base = mini(red, [], [Vehiculo(1, "moto", 60.0)])
    punto = _punto_lejano(base)
    camino = _camino_previsto(base, "moto", punto)
    a, b = camino[1], camino[2]
    cierre = Cierre(1, (red.arista[(a, b)],), 0.0, ("camion",))
    r = simular(mini(red, [pedido(1, punto, 30.0)], [Vehiculo(1, "moto", 60.0)], cierres=[cierre]), Fija({1: [1]}))
    assert r.descubiertos == {} and 1 in r.entregas


# ---------- reproducibilidad ----------
def test_misma_semilla_mismo_resultado():
    a = calcular(simular(generar(3, "malla"), crear("ingenua")))
    b = calcular(simular(generar(3, "malla"), crear("ingenua")))
    assert a == b


def test_el_escenario_cumple_el_diseno():
    esc = generar(8, "malla")
    assert 30 <= len(esc.puntos) <= 80
    assert 0.15 <= sum(q.critico for q in esc.puntos) / len(esc.puntos) <= 0.25
    assert all(6 * H <= l.vence <= 48 * H for l in esc.lotes)
    assert {v.tipo for v in esc.vehiculos} == {"camion", "campero", "moto"}
    assert esc.p.cierres_min <= len(esc.cierres) <= esc.p.cierres_max


def test_vehiculo_aislado_devuelve_sus_pedidos_a_la_cola(red):
    # mientras el campero descarga, se cierran todos los tramos que tocan el punto: no puede salir
    base = mini(red, [], [Vehiculo(1, "campero", 700.0)])
    punto = _punto_lejano(base)
    nodo = base.puntos[punto - 1].nodo
    otro = next(q.id for q in base.puntos if q.id != punto)
    arma = lambda cs: mini(red, [pedido(1, punto, 100.0), pedido(2, otro, 100.0)],
                           [Vehiculo(1, "campero", 700.0), Vehiculo(2, "moto", 60.0)], cierres=cs)
    llegada = simular(arma([]), Fija({1: [1, 2]})).entregas[1]["t"]
    tocan = tuple(i for i, (u, v) in enumerate(zip(red.eu, red.ev)) if u == nodo or v == nodo)
    motor = Motor(arma([Cierre(1, tocan, llegada + 60.0, ("campero",))]), Fija({1: [1, 2]}))
    r = motor.correr()
    assert r.vehiculos[0].estado == "fuera"
    assert 1 in r.entregas and 2 not in r.entregas
    assert motor.estado_ped[2] == "pendiente"           # queda disponible para otro vehículo


def test_vehiculo_sin_regreso_por_su_red_sale_en_emergencia(red):
    # se cierran las salidas del punto, pero no el tramo de entrada: el campero vuelve en contravía
    base = mini(red, [], [Vehiculo(1, "campero", 700.0)])
    punto = _punto_lejano(base)
    nodo = base.puntos[punto - 1].nodo
    salidas = tuple(i for i, (u, v) in enumerate(zip(red.eu, red.ev)) if u == nodo)
    esc = mini(red, [pedido(1, punto, 100.0)], [Vehiculo(1, "campero", 700.0)],
               cierres=[Cierre(1, salidas, 0.0, ("campero",))])
    r = simular(esc, Fija({1: [1]}))
    v = r.vehiculos[0]
    assert v.estado == "libre" and v.emergencias == 1 and 1 in r.entregas
