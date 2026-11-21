"""El caché de lugares no cambia ningún resultado, y se invalida cuando el nomenclátor cambia."""
import pytest

import lugares
from entrada import cache_lugares
from entrada.flujo import TIPOS
from entrada.pruebas.mensajes import MENSAJES
from entrada.pruebas.simulador import ClienteSimulado
from lugares import nomenclator

TEXTOS = ["san jose", "la enea", "villa hermosa", "albergue de san jorge", "chipre", "comedor de belen",
          "el carmen", "fatima", "via a chinchina", "avenida santander", "panamericana", "salida a letras",
          "la siria", "avenida paralela", "bajo prado", "san josé", "SAN JOSE", "por la terminal", "xyz123"]


@pytest.fixture
def cache(con):
    lugares.cargar_semilla(con)                 # sin el nomenclátor, todo daría listas vacías
    assert con.execute("SELECT COUNT(*) FROM lugares").fetchone()[0] > 100
    cache_lugares.instalar()
    yield cache_lugares
    cache_lugares.quitar()


def _como_tuplas(cands):
    return [(c.lugar_id, c.nombre, c.tipo, c.puntaje, c.punto_id) for c in cands]


def test_mismos_candidatos_con_y_sin_cache(con, cache):
    original = cache_lugares._original
    for tipos in (TIPOS["pedidos"], TIPOS["cierres"], None):
        for t in TEXTOS:
            sin = _como_tuplas(original(con, t, tipos))
            con1 = _como_tuplas(nomenclator.buscar(con, t, tipos))      # primera vez: calcula
            con2 = _como_tuplas(nomenclator.buscar(con, t, tipos))      # segunda: del caché
            assert sin == con1 == con2, (t, tipos)
    assert cache.aciertos["si"] == cache.aciertos["no"] == len(TEXTOS) * 3
    con_candidatos = sum(bool(original(con, t, None)) for t in TEXTOS)
    assert con_candidatos >= len(TEXTOS) - 3        # la comparación no es entre listas vacías


def test_aprender_un_apodo_invalida_el_cache(con, cache):
    antes = nomenclator.buscar(con, "donde dona rosa", TIPOS["pedidos"])
    lugar = con.execute("SELECT * FROM lugares WHERE tipo='barrio' ORDER BY id LIMIT 1").fetchone()
    nomenclator.aprender(con, "donde dona rosa", lugar)
    con.commit()
    despues = nomenclator.buscar(con, "donde dona rosa", TIPOS["pedidos"])
    assert _como_tuplas(despues) == _como_tuplas(cache_lugares._original(con, "donde dona rosa", TIPOS["pedidos"]))
    assert despues and despues[0].nombre == lugar["nombre"] and _como_tuplas(antes) != _como_tuplas(despues)


def test_modificar_lo_devuelto_no_toca_el_cache(con, cache):
    a = nomenclator.buscar(con, "san jose", TIPOS["pedidos"])
    a[0].puntaje = -1
    a.clear()
    b = nomenclator.buscar(con, "san jose", TIPOS["pedidos"])
    assert b and b[0].puntaje > 0


def test_el_flujo_da_las_mismas_respuestas_con_cache(con, mesa):
    sin = [ClienteSimulado(mesa, chat_id=100 + i).escribir(m["texto"]) for i, m in enumerate(MENSAJES)]
    cache_lugares.instalar()
    try:
        con_cache = [ClienteSimulado(mesa, chat_id=200 + i).escribir(m["texto"]) for i, m in enumerate(MENSAJES)]
    finally:
        cache_lugares.quitar()
    normal = lambda rs: [(r.texto.split("#")[0], [e for e, _ in r.botones]) for r in rs]   # sin ids de fila
    assert [normal(x) for x in sin] == [normal(x) for x in con_cache]
    assert lugares.nomenclator.buscar is not cache_lugares._buscar_con_cache          # quitar() la devolvió
