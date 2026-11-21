"""Etapa 3 del encargo A2: que ningún mensaje se pierda cuando la API o la base fallan. Sin red."""
import asyncio

from entrada import carga, extraer as E
from entrada.flujo import SIN_LEER
from entrada.pruebas.simulador import ClienteSimulado

TEXTO = "somos 40 familias en san jose no hay arroz ni leche"


def test_api_caida_tras_reintentos_guarda_el_texto(con, mesa, monkeypatch):
    import anthropic
    creados = {}

    class Caido:
        def __init__(self, **k):
            creados.update(k)
            self.messages = self

        def parse(self, **k):
            raise anthropic.APIConnectionError(request=None)
    monkeypatch.setattr(anthropic, "Anthropic", Caido)
    mesa.extraer = E.extraer
    raro = "hola buenas como hago para ser voluntario"             # tampoco lo leen las reglas
    r, = ClienteSimulado(mesa).escribir(raro)
    assert creados["max_retries"] == E.REINTENTOS == 2            # 3 intentos con espera creciente del SDK
    assert r.texto == SIN_LEER
    assert con.execute("SELECT texto_original FROM pedidos").fetchone()[0] == raro
    r, = ClienteSimulado(mesa, chat_id=7).escribir(TEXTO)          # este sí lo leen las reglas
    assert "40 familias en san jose" in r.texto


def test_el_cliente_se_reutiliza(monkeypatch):
    import anthropic
    veces = []

    class Contado:
        def __init__(self, **k):
            veces.append(1)
    monkeypatch.setattr(anthropic, "Anthropic", Contado)
    assert E._cliente() is E._cliente() and len(veces) == 1


def test_falla_la_base_y_el_mensaje_queda_crudo(con, mesa, monkeypatch):
    from entrada import guardar

    def ocupada(*a, **k):
        raise __import__("sqlite3").OperationalError("database is locked")
    monkeypatch.setattr(guardar, "guardar_pedido", ocupada)
    r, = ClienteSimulado(mesa).escribir(TEXTO)
    assert r.texto == SIN_LEER
    assert con.execute("SELECT COUNT(*) FROM pedidos WHERE texto_original=?", (TEXTO,)).fetchone()[0] == 1


def test_carga_pequena_no_pierde_mensajes():
    r = asyncio.run(carga._correr(60, 16, carga.extractor_falso(0.0, 0.1)))
    guardadas = r["filas"]["pedidos"] + r["filas"]["cierres"]
    assert not r["errores"] and r["sin_respuesta"] == 0
    assert r["crudos"] > 0 and guardadas == r["esperadas"]
