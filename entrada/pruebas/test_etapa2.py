"""Etapa 2 del encargo A2: primer mensaje, notas de voz y /estado en lenguaje humano. Sin red."""
import pytest

from datos import db
from entrada import voz
from entrada.flujo import ayuda
from entrada.pruebas.simulador import ClienteSimulado

TEXTO_1 = "somos 40 familias en san jose no hay arroz ni leche"


@pytest.fixture
def chat(mesa):
    return ClienteSimulado(mesa)


def test_start_solo_nombra_la_voz_si_hay_servicio(chat, monkeypatch):
    monkeypatch.delenv("DESPACHOX_VOZ_CLAVE", raising=False)
    r, ejemplo = chat.comando("inicio")
    assert "nota de voz" not in r.texto and "<code>" in ejemplo.texto
    assert "nota de voz" in ayuda(con_voz=True)


def test_nota_de_voz_sin_servicio_pide_escribir(con, chat, monkeypatch):
    monkeypatch.delenv("DESPACHOX_VOZ_CLAVE", raising=False)
    r, = chat.enviar_voz()
    assert "Escríbeme" in r.texto
    assert con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 0


def test_nota_de_voz_sigue_el_flujo_normal(con, chat, monkeypatch):
    monkeypatch.setenv("DESPACHOX_VOZ_CLAVE", "clave-de-prueba")
    recibido = {}

    def transcribir(audio, nombre="nota.ogg"):
        recibido["audio"] = audio
        return TEXTO_1
    monkeypatch.setattr(voz, "transcribir", transcribir)
    escuche, pedido = chat.enviar_voz()
    assert escuche.texto == f"Escuché: «{TEXTO_1}»" and recibido["audio"].startswith(b"OggS")
    assert "40 familias en san jose" in pedido.texto and pedido.botones[0][0] == "Sí, es ahí"
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert (p["familias"], p["texto_original"]) == (40, TEXTO_1)       # se guarda el texto, no el audio


def test_nota_de_voz_quita_datos_personales_antes_de_mostrarla(chat, monkeypatch):
    monkeypatch.setenv("DESPACHOX_VOZ_CLAVE", "x")
    monkeypatch.setattr(voz, "transcribir", lambda a, nombre="": "me llamo Ana Ruiz mi cel 3105551234 hola")
    escuche = chat.enviar_voz()[0].texto
    assert "3105551234" not in escuche and "Ana Ruiz" not in escuche


def test_nota_larga_o_ilegible(chat, monkeypatch):
    monkeypatch.setenv("DESPACHOX_VOZ_CLAVE", "x")
    assert "menos de dos minutos" in chat.enviar_voz(duracion=600)[0].texto
    monkeypatch.setattr(voz, "transcribir", lambda a, nombre="": None)
    assert "escribes" in chat.enviar_voz()[0].texto


def test_transcribir_sin_clave_no_llama_a_nadie(monkeypatch):
    monkeypatch.delenv("DESPACHOX_VOZ_CLAVE", raising=False)
    assert voz.transcribir(b"audio") is None and not voz.disponible()


def test_transcribir_con_servicio_caido_no_lanza(monkeypatch):
    import httpx
    monkeypatch.setenv("DESPACHOX_VOZ_CLAVE", "x")

    def caido(*a, **k):
        raise httpx.ConnectError("sin red")
    monkeypatch.setattr(httpx, "post", caido)
    assert voz.transcribir(b"audio") is None


def test_estado_en_lenguaje_humano(con, chat):
    assert "No tengo pedidos" in chat.comando("estado")[0].texto
    chat.escribir(TEXTO_1)
    assert "Falta que confirmes el lugar" in chat.comando("estado")[0].texto
    chat.pulsar("Sí")
    pid = con.execute("SELECT id FROM pedidos").fetchone()[0]
    assert "recibido" in chat.comando("estado")[0].texto

    con.execute("UPDATE pedidos SET estado='confirmado' WHERE id=?", (pid,))
    assert "en revisión" in chat.comando("estado")[0].texto

    con.execute("UPDATE pedidos SET estado='asignado' WHERE id=?", (pid,))
    plan = con.execute("INSERT INTO planes(creado_en, estado) VALUES (?, 'aprobado')", (db.ahora(),)).lastrowid
    con.execute("INSERT INTO paradas(plan_id, orden, pedido_id, llegada_estimada) VALUES (?,1,?,?)",
                (plan, pid, "2026-11-20T16:30:00-05:00"))
    assert "va en camino, llegada estimada 4:30 p. m." in chat.comando("estado")[0].texto

    con.execute("UPDATE pedidos SET estado='entregado' WHERE id=?", (pid,))
    assert ": entregado" in chat.comando("estado")[0].texto
