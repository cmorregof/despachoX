"""Revisión QA de la noche (rama qa-noche): ENTREGADO con el modelo activo, frases que el lector de SMS
confundía con una entrega, botones de familias forjados desde otro chat y entradas malformadas en la
pasarela de SMS. Ninguna prueba sale de esta máquina. Detalle y contexto en docs/QA_NOCHE.md."""
import http.client
import json
import socket
import threading
import time
from urllib.request import Request, urlopen

import pytest

from datos import db
from entrada import pasarela_sms, sms
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
    con.execute("INSERT INTO pedidos(id, creado_en, estado) VALUES (?, ?, 'asignado')", (pedido, db.ahora()))
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


# ---------- 4. Pasarela de SMS: cuerpos y cabeceras malformados ----------

@pytest.fixture
def receptor(con, tmp_path):
    servidor = pasarela_sms.Pasarela(("127.0.0.1", 0), ruta_db=tmp_path / "prueba.db")
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield servidor.server_address
    servidor.shutdown()
    servidor.server_close()


def _crudo(direccion, cuerpo: bytes, largo: str | None = None) -> int:
    c = http.client.HTTPConnection(*direccion, timeout=5)
    c.putrequest("POST", "/sms")
    c.putheader("Content-Type", "application/json")
    c.putheader("Content-Length", largo if largo is not None else str(len(cuerpo)))
    c.endheaders(cuerpo)
    estado = c.getresponse().status
    c.close()
    return estado


def _salud(direccion) -> bool:
    with urlopen(f"http://{direccion[0]}:{direccion[1]}/salud", timeout=5) as r:
        return json.loads(r.read()) == {"ok": True}


@pytest.mark.parametrize("cuerpo", [b"[]", b'"x"', b"5", b'{"event": "sms:received", "payload": "x"}'])
def test_json_que_no_es_objeto_da_400(receptor, cuerpo):
    assert _crudo(receptor, cuerpo) == 400 and _salud(receptor)


@pytest.mark.parametrize("largo", ["-1", "abc"])
def test_content_length_invalido_da_400_sin_colgarse(receptor, largo):
    assert _crudo(receptor, b"", largo) == 400 and _salud(receptor)


def test_un_cliente_lento_no_bloquea_el_receptor(receptor, monkeypatch):
    assert pasarela_sms.Receptor.timeout and pasarela_sms.Receptor.timeout <= 30   # sin él, se colgaba
    monkeypatch.setattr(pasarela_sms.Receptor, "timeout", 0.5)                    # para que la prueba sea corta
    lento = socket.create_connection(receptor, timeout=5)        # anuncia 100 bytes y no manda ninguno
    lento.sendall(b"POST /sms HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\nContent-Length: 100\r\n\r\n")
    inicio = time.monotonic()
    assert _salud(receptor) and time.monotonic() - inicio < 3
    lento.close()


def test_token_por_la_direccion_y_en_el_registro_del_celular(receptor, monkeypatch):
    monkeypatch.setenv("DESPACHOX_SMS_TOKEN", "se cret/&")
    base = f"http://{receptor[0]}:{receptor[1]}/sms"
    datos = json.dumps({"de": "sms-qa-3", "texto": "PEDIDO 5 CHIPRE AGUA"}).encode()
    for sufijo, esperado in (("?token=malo", 401), ("?token=se%20cret%2F%26", 200)):
        try:
            with urlopen(Request(base + sufijo, data=datos, headers={"Content-Type": "application/json"}),
                         timeout=5) as r:
                estado = r.status
        except Exception as e:                                   # HTTPError trae el código
            estado = getattr(e, "code", None)
        assert estado == esperado
    registrados = []

    class Respuesta:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b"{}"
    monkeypatch.setattr(pasarela_sms, "urlopen", lambda req, timeout=0: registrados.append(json.loads(req.data)) or Respuesta())
    pasarela_sms.registrar("http://celular.local:8080", "sms", "c", 8081, ip="192.168.1.10")
    assert registrados[0]["url"] == "http://192.168.1.10:8081/sms?token=se%20cret%2F%26"
