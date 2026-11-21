"""El caso que falló en la nube («hay 6 bebes sin leche desde ayer en la enea…») y nueve variantes.

Todos los mensajes son sintéticos. El extractor falso devuelve lo que un buen lector sacaría del
texto, y en dos casos imita el fallo visto: el modelo deja la leche por fuera.
"""
import json

import pytest

from entrada import raciones
from entrada.flujo import Mesa
from entrada.pruebas.conftest import extractor_falso
from entrada.pruebas.simulador import ClienteSimulado

ENEA = "hay 6 bebes sin leche desde ayer en la enea necesitamos urgente"
LECHE = raciones.KG_POR_FAMILIA["leche"]          # kg por familia y pedido; sale de raciones.py


def leche(familias):
    return round(LECHE * familias, 1)


def _p(lugar, productos, urgencia=2, familias=None, personas=None, bebes=None):
    return {"tipo": "pedido", "pedido": {
        "lugar": lugar, "familias": familias, "personas": personas, "bebes": bebes, "urgencia": urgencia,
        "horas_limite": None, "productos": [{"producto": x, "kg": None} for x in productos]}}


# (texto, lectura, familias que deben quedar, kilos de leche esperados o None si no hay leche)
CASOS = [
    (ENEA, _p("la enea", ["leche"], 3, bebes=6), 6, leche(6)),
    ("en la enea hay 6 bebes sin leche urgente", _p("la enea", [], 3), 6, leche(6)),     # el modelo omite leche y bebés
    ("hay 4 bebes en villa hermosa necesitan pañales y leche", _p("villa hermosa", ["pañal", "leche"], 3, bebes=4), 4, leche(4)),
    ("somos 12 personas en san jose sin comida", _p("san jose", [], personas=12), 5, None),          # 12 / 2,9 -> 5
    ("somos 9 adultos mayores en el albergue de san jorge sin arroz", _p("albergue de san jorge", ["arroz"], 3, personas=9), 4, None),
    ("necesitamos agua para 20 personas en chipre", _p("chipre", ["agua"], personas=20), 7, None),
    ("hay 3 niños y 2 bebes sin comer en fatima urgente", _p("fatima", [], 3, personas=3, bebes=2), 2, leche(2)),
    ("somos 30 personas en el carmen sin panela ni frijol", _p("el carmen", ["panela", "frijol"], personas=30), 11, None),
    ("5 bebes en belen sin formula ni leche", _p("belen", ["fórmula"], 3, bebes=5), 5, leche(5)),        # omite la leche
    ("en la enea hay bebes sin leche desde ayer", _p("la enea", ["leche"], 3), None, None),       # sin cifra: se pregunta
]


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


@pytest.fixture
def reloj():
    return Reloj()


@pytest.fixture
def con_dudas(con):
    """La base con la columna `pedidos.dudas` pedida por el canal; sin ella el flujo también funciona."""
    con.execute("ALTER TABLE pedidos ADD COLUMN dudas TEXT")
    return con


def _mesa(con, reloj):
    return Mesa(con, extraer=extractor_falso({t: l for t, l, *_ in CASOS}), elegir=None, reloj=reloj)


def _kg(fila, producto):
    return next((q["kg"] for q in json.loads(fila["productos"] or "[]") if q["producto"] == producto), None)


@pytest.mark.parametrize("texto,lectura,familias,kg_leche", CASOS, ids=[f"caso{i}" for i in range(1, 11)])
def test_personas_y_bebes_se_vuelven_familias(con_dudas, reloj, texto, lectura, familias, kg_leche):
    chat = ClienteSimulado(_mesa(con_dudas, reloj))
    r, = chat.escribir(texto)
    p = con_dudas.execute("SELECT * FROM pedidos").fetchone()
    dudas = json.loads(p["dudas"])
    assert p["familias"] == familias
    if "leche" in texto:
        assert _kg(p, "leche") == kg_leche           # la leche se conserva aunque el modelo la omita
    if familias:
        assert f"unas {familias} familias" in r.texto and any(d.startswith("Familias estimadas") for d in dudas)
    else:
        assert any(d.startswith("Falta el número de familias") for d in dudas)

    fin, = chat.enviar_ubicacion(5.06, -75.5)        # al ubicar, la única pregunta que falta
    assert "¿Para cuántas familias" in fin.texto
    etiquetas = [e for e, _ in fin.botones]
    assert etiquetas[-4:] == ["1 a 5", "6 a 10", "11 a 20", "Más de 20"]
    assert (etiquetas[0] == f"Sí, unas {familias}") == bool(familias)


def test_la_enea_de_punta_a_punta(con_dudas, reloj):
    """Hecho cuando: pedido con familias, leche con kilos, una duda anotada y el bot preguntó."""
    chat = ClienteSimulado(_mesa(con_dudas, reloj))
    r, = chat.escribir(ENEA)
    assert "unas 6 familias en la enea" in r.texto and f"leche ({leche(6):g} kg aprox.)" in r.texto and "urgente" in r.texto
    assert "1 familia por bebé" in r.texto
    fin, = chat.enviar_ubicacion(5.07, -75.49)
    assert "¿Para cuántas familias es? Calculé unas 6." in fin.texto
    ok, = chat.pulsar("6 a 10")
    assert "quedó para 8 familias" in ok.texto
    p = con_dudas.execute("SELECT * FROM pedidos").fetchone()
    assert (p["familias"], _kg(p, "leche"), p["kg_estimado"], p["urgencia"]) == (8, leche(8), leche(8), 3)
    dudas = json.loads(p["dudas"])
    assert any("6 a 10" in d for d in dudas) and any(d.startswith(f"Kilos de leche estimados: {leche(8):g}") for d in dudas)
    assert not any(d.startswith("Familias estimadas") for d in dudas)          # la estimación vieja se reemplaza


def test_numero_escrito_vale_y_tras_dos_minutos_ya_no(con, reloj):
    mesa = _mesa(con, reloj)
    chat = ClienteSimulado(mesa)
    chat.escribir(CASOS[-1][0])
    chat.enviar_ubicacion(5.07, -75.49)
    reloj.t = 60
    ok, = chat.escribir("somos 14 familias")
    assert "quedó para 14 familias" in ok.texto
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert (p["familias"], _kg(p, "leche")) == (14, leche(14))

    otro = ClienteSimulado(mesa, chat_id=2002)
    otro.escribir(CASOS[-1][0])
    otro.enviar_ubicacion(5.07, -75.49)
    reloj.t += 121
    r, = otro.escribir("14")                         # tarde: ya no se toma como respuesta
    assert "quedó para" not in r.texto
    p = con.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchone()
    assert p["familias"] is None                     # se queda con lo que había; la duda ya estaba anotada


def test_pedido_con_familias_no_pregunta_nada_mas(con, reloj):
    chat = ClienteSimulado(_mesa(con, reloj))
    chat.escribir("somos 40 familias en san jose no hay arroz ni leche")
    fin, = chat.pulsar("Sí")
    assert "¿Para cuántas" not in fin.texto and not fin.botones


def test_sin_columna_dudas_tambien_guarda(con, reloj):
    chat = ClienteSimulado(_mesa(con, reloj))
    chat.escribir(ENEA)
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert (p["familias"], _kg(p, "leche")) == (6, leche(6))


def test_reglas_de_raciones():
    assert raciones.familias_desde(None, None) == (None, None)
    assert raciones.familias_desde(1, None)[0] == 1                  # mínimo una familia
    assert raciones.familias_desde(9, None)[0] == 4                  # 9 / 2,9
    assert raciones.familias_desde(3, 2)[0] == 2
    assert raciones.contar_en_texto("hay 3 niños y 2 bebés sin comer, 6 familias") == (3, 2)
    assert raciones.contar_en_texto("40 familias sin arroz") == (None, None)
    assert raciones.faltantes_para_bebes("bebés sin leche ni pañales", ["agua"]) == ["leche", "pañales"]
    assert raciones.faltantes_para_bebes("no hay panela", []) == []
    lineas = [{"producto": "arroz", "kg": 50}, {"producto": "agua", "kg": None}, {"producto": "pañales", "kg": None}]
    raciones.completar_kilos(lineas, 10)
    assert [q["kg"] for q in lineas] == [50, round(raciones.KG_POR_FAMILIA["agua"] * 10, 1), None]             # lo dicho no se toca; lo que no está en la tabla tampoco
