"""El /start en una pantalla, sus cuatro botones, los errores amables y /borrar. Sin red."""
import pytest

from entrada import guardar
from entrada.flujo import EJEMPLOS, MENU
from entrada.pruebas.simulador import ClienteSimulado
from entrada.privacidad import hash_remitente

TEXTO = "somos 40 familias en san jose no hay arroz ni leche"


@pytest.fixture
def chat(mesa):
    return ClienteSimulado(mesa)


def test_start_trae_los_cuatro_botones_antes_del_ejemplo(chat, monkeypatch):
    monkeypatch.delenv("DESPACHOX_VOZ_CLAVE", raising=False)
    bienvenida, ejemplo = chat.comando("inicio")
    assert [t for t, _ in bienvenida.botones] == ["Pedir comida", "Reportar una vía cerrada",
                                                 "Confirmar una entrega", "¿Cómo va mi pedido?"]
    assert "Ley 1581 de 2012" in bienvenida.texto and "/borrar" in bienvenida.texto
    assert ejemplo.texto.endswith(f"<code>{EJEMPLOS[0]}</code>") and ejemplo.parse_mode == "HTML"
    assert not ejemplo.botones


@pytest.mark.parametrize("boton,dice", [("Pedir comida", "para cuántas familias"),
                                        ("Reportar una vía", "qué vía está cerrada"),
                                        ("Confirmar una entrega", "ENTREGADO")])
def test_cada_boton_explica_que_escribir_con_un_ejemplo_copiable(chat, boton, dice):
    chat.comando("inicio")
    r, = chat.pulsar(boton)
    assert dice in r.texto and "<code>" in r.texto and r.parse_mode == "HTML"


def test_boton_como_va_mi_pedido_es_el_estado(chat):
    chat.comando("inicio")
    assert "No tengo pedidos" in chat.pulsar("¿Cómo va")[0].texto


def test_si_no_entiende_no_culpa_y_vuelve_a_ofrecer_los_botones(chat):
    r, = chat.escribir("hola buenas")
    assert r.texto.startswith("No alcancé a entender") and r.botones == MENU
    assert "inválid" not in r.texto.lower()


def test_el_resumen_pregunta_si_esta_bien_antes_de_ubicar(chat):
    r, = chat.escribir(TEXTO)
    assert r.texto.startswith("Entendí: 40 familias en san jose") and "¿Está bien?" in r.texto
    assert any(t.startswith("Sí") for t, _ in r.botones)


def test_borrar_pregunta_primero_y_luego_suprime(con, chat):
    chat.escribir(TEXTO); chat.pulsar("Sí")
    rem = hash_remitente(chat.chat.id)
    assert con.execute("SELECT COUNT(*) FROM pedidos WHERE remitente_hash=?", (rem,)).fetchone()[0] == 1
    pregunta, = chat.comando("borrar")
    assert "No se puede deshacer" in pregunta.texto
    assert chat.pulsar("No")[0].texto == "Listo, no borré nada."
    assert con.execute("SELECT COUNT(*) FROM pedidos WHERE remitente_hash=?", (rem,)).fetchone()[0] == 1
    chat.comando("borrar")
    r, = chat.pulsar("Sí, borrar")
    assert "Borré" in r.texto
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert p["remitente_hash"] is None and p["texto_original"] is None and p["estado"] == "descartado"
    assert con.execute("SELECT texto FROM ubicaciones WHERE tabla='pedidos'").fetchone()[0] == guardar.BORRADO
    assert not con.execute("SELECT 1 FROM bitacora WHERE detalle LIKE '%san jose%'").fetchall()
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='supresión pedida por el titular'").fetchone()[0] == 1
    assert "No tengo pedidos" in chat.comando("estado")[0].texto


def test_borrar_no_cancela_lo_que_va_en_camino(con, chat):
    chat.escribir(TEXTO); chat.pulsar("Sí")
    con.execute("UPDATE pedidos SET estado='asignado'"); con.commit()
    chat.comando("borrar"); chat.pulsar("Sí, borrar")
    p = con.execute("SELECT estado, texto_original FROM pedidos").fetchone()
    assert p["estado"] == "asignado" and p["texto_original"] is None
