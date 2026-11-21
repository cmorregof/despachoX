"""Revisión QA de la noche (rama qa-noche): ENTREGADO con el modelo activo, frases que el lector de SMS
confundía con una entrega y botones de familias forjados desde otro chat. Ninguna prueba toca la red.
Detalle y contexto en docs/QA_NOCHE.md."""
import pytest

from datos import db
from entrada import sms
from entrada.extraer import Extraccion
from entrada.flujo import Mesa
from entrada.privacidad import hash_remitente


def _modelo_sin_codigo(llamadas: list):
    """Como el modelo real: su esquema (`Lectura`) no tiene campo para un código de paquete."""
    def extraer(texto):
        llamadas.append(texto)
        return Extraccion(tipo="otro", texto=texto)
    return extraer


def _paquete(con, codigo="DX-7K2Q", pedido=77):
    # El pedido es del chat 123: desde la tarea C, ENTREGADO solo vale del destino o del conductor.
    con.execute("INSERT INTO pedidos(id, creado_en, estado, remitente_hash) VALUES (?, ?, 'asignado', ?)",
                (pedido, db.ahora(), hash_remitente(123)))
    con.execute("INSERT INTO paquetes(codigo, pedido_id, kg, estado) VALUES (?, ?, 30, 'en_ruta')", (codigo, pedido))
    con.commit()


def _estado(con, codigo="DX-7K2Q"):
    return con.execute("SELECT estado FROM paquetes WHERE codigo=?", (codigo,)).fetchone()[0]


# ---------- 1. ENTREGADO por Telegram con el modelo activo ----------

@pytest.mark.parametrize("texto", ["ENTREGADO DX-7K2Q", "entregado dx 7k2q", "DX-7K2Q", "Entregado DX7K2Q, gracias"])
def test_entregado_por_telegram_queda_registrado_sin_pasar_por_el_modelo(con, texto):
    _paquete(con)
    llamadas = []
    r = Mesa(con, extraer=_modelo_sin_codigo(llamadas), elegir=None).recibir_texto(123, texto)
    assert "DX-7K2Q quedó entregado" in r[0].texto
    assert _estado(con) == "entregado" and llamadas == []


def test_un_pedido_normal_sigue_yendo_al_modelo(con):
    llamadas = []
    Mesa(con, extraer=_modelo_sin_codigo(llamadas), elegir=None).recibir_texto(1, "entreguen arroz en la enea")
    assert llamadas == ["entreguen arroz en la enea"]


# ---------- 2. Frases que el lector de SMS tomaba como entrega ----------

@pytest.mark.parametrize("texto", [
    "entrega de mercado en la enea",                     # antes: DX-ENEA, y el pedido se perdía
    "entrega urgente de leche para la enea",             # antes: DX-PARA
    "Entregamos? necesitamos mercado en la enea",        # antes: DX-ENEA
    "todavia no nos han entregado el paquete DX-7K2Q",   # un reclamo, no una entrega
    "no ha llegado el paquete DX-7K2Q",                  # antes lo marcaba entregado
])
def test_no_es_una_entrega(texto):
    assert sms.leer_sms(texto).entregado is None


@pytest.mark.parametrize("texto,codigo", [
    ("ENTREGADO DX7K2Q", "DX-7K2Q"), ("ENTRGADO DX9PRT", "DX-9PRT"), ("ENTREGADO 7KQ3", "DX-7KQ3"),
    ("entregado kqtw gracias", "DX-KQTW"), ("dx7k2q entregado", "DX-7K2Q"), ("DX-7K2Q", "DX-7K2Q"),
])
def test_las_entregas_de_verdad_se_siguen_leyendo(texto, codigo):
    assert sms.leer_sms(texto).entregado == codigo


def test_el_reclamo_no_cierra_el_paquete_y_queda_para_el_despachador(con):
    _paquete(con)
    mesa = Mesa(con, extraer=sms.leer_sms, elegir=None)
    sms.atender_sms(mesa, "sms-qa-1", "todavia no nos han entregado el paquete DX-7K2Q")
    assert _estado(con) == "en_ruta"
    assert con.execute("SELECT COUNT(*) FROM pedidos WHERE texto_original LIKE 'todavia no%'").fetchone()[0] == 1


def test_el_pedido_que_empieza_por_entrega_no_se_pierde(con):
    mesa = Mesa(con, extraer=sms.leer_sms, elegir=None)
    sms.atender_sms(mesa, "sms-qa-2", "entrega de mercado en la enea")
    assert con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == 1


# ---------- 3. Botón «¿para cuántas familias?» forjado ----------

def _pedido_de(con, chat_id, pedido=5):
    con.execute("INSERT INTO pedidos(id, creado_en, familias, estado, remitente_hash) VALUES (?, ?, 10, 'confirmado', ?)",
                (pedido, db.ahora(), hash_remitente(chat_id)))
    con.commit()


def _familias(con, pedido=5):
    return con.execute("SELECT familias FROM pedidos WHERE id=?", (pedido,)).fetchone()[0]


def test_otro_chat_no_cambia_las_familias_de_un_pedido_ajeno(con, mesa):
    _pedido_de(con, 111)
    r = mesa.pulsar(999, "f:5:8")
    assert "No encontré ese reporte" in r.texto and _familias(con) == 10


@pytest.mark.parametrize("n", ["0", "-3", "99999"])
def test_familias_fuera_de_rango_no_se_guardan(con, mesa, n):
    _pedido_de(con, 111)
    mesa.pulsar(111, f"f:5:{n}")
    assert _familias(con) == 10


def test_quien_hizo_el_pedido_si_puede_fijar_las_familias(con, mesa):
    _pedido_de(con, 111)
    r = mesa.pulsar(111, "f:5:8")
    assert "quedó para 8 familias" in r.texto and _familias(con) == 8
