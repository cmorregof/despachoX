"""El receptor HTTP de SMS con peticiones como las de la pasarela. Servidor real en un puerto libre."""
import json
import threading
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pytest

from entrada import pasarela_sms


@pytest.fixture
def url(con, tmp_path):
    """El fixture `con` ya dejó la base con los puntos en tmp_path/prueba.db; el receptor abre la suya."""
    servidor = pasarela_sms.Pasarela(("127.0.0.1", 0), ruta_db=tmp_path / "prueba.db")
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()
    yield f"http://127.0.0.1:{servidor.server_address[1]}"
    servidor.shutdown()
    servidor.server_close()


def _post(url, cuerpo, tipo="application/json", cabeceras=None):
    datos = json.dumps(cuerpo).encode() if tipo == "application/json" else urlencode(cuerpo).encode()
    req = Request(url, data=datos, method="POST", headers={"Content-Type": tipo, **(cabeceras or {})})
    with urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def test_formato_generico_como_un_curl(con, url):
    r = _post(f"{url}/sms", {"de": "sms-prueba-1", "texto": "PEDIDO 40 SAN JOSE ARROZ LECHE"})
    assert r["respuesta"].startswith("Recibido: pedido 40 fam") and len(r["respuesta"]) <= 160
    assert r["enviado_por_el_celular"] is False                      # no hay celular configurado
    r2 = _post(f"{url}/sms", {"de": "sms-prueba-1", "texto": "si"})    # la misma conversación sigue
    assert "San Jose" in r2["respuesta"]
    p = con.execute("SELECT familias, punto_id, remitente_hash FROM pedidos").fetchone()
    assert p["familias"] == 40 and p["punto_id"] is not None and "sms-prueba" not in p["remitente_hash"]


def test_formato_de_sms_gateway_for_android(con, url):
    aviso = {"event": "sms:received", "deviceId": "x", "id": "1",
             "payload": {"messageId": "m1", "message": "ciere via a chinchina no pasan camiones", "sender": "sms-prueba-2"}}
    r = _post(f"{url}/webhook/sms-received", aviso)
    assert "cierre" in r["respuesta"]
    assert con.execute("SELECT COUNT(*) FROM cierres").fetchone()[0] == 1
    viejo = {"event": "sms:received", "payload": {"message": "PEDIDO 10 CHIPRE AGUA", "phoneNumber": "sms-prueba-3"}}
    assert "10 fam" in _post(f"{url}/sms", viejo)["respuesta"]
    assert _post(f"{url}/sms", {"event": "sms:sent", "payload": {}}) == {"ignorado": True}


def test_formulario(con, url):
    r = _post(f"{url}/sms", {"from": "sms-prueba-4", "message": "hola como estan"}, "application/x-www-form-urlencoded")
    assert "despachador" in r["respuesta"]
    assert con.execute("SELECT texto_original FROM pedidos").fetchone()[0] == "hola como estan"


def test_errores_no_tumban_el_receptor(url, monkeypatch):
    with pytest.raises(HTTPError) as e:
        _post(f"{url}/sms", {"texto": "sin remitente"})
    assert e.value.code == 400
    monkeypatch.setenv("DESPACHOX_SMS_TOKEN", "secreto")
    with pytest.raises(HTTPError) as e:
        _post(f"{url}/sms", {"de": "sms-prueba-5", "texto": "PEDIDO 5 CHIPRE AGUA"})
    assert e.value.code == 401
    assert "Recibido" in _post(f"{url}/sms", {"de": "sms-prueba-5", "texto": "PEDIDO 5 CHIPRE AGUA"},
                               cabeceras={"X-Token": "secreto"})["respuesta"]
    with urlopen(f"{url}/salud", timeout=5) as r:
        assert json.loads(r.read()) == {"ok": True}


def test_envio_por_el_celular_cuando_esta_configurado(url, monkeypatch):
    enviados = []

    class Respuesta:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def falso_urlopen(req, timeout=0):
        enviados.append((req.full_url, json.loads(req.data), req.headers["Authorization"]))
        return Respuesta()
    monkeypatch.setenv("DESPACHOX_PASARELA_URL", "http://celular.local:8080/message")
    monkeypatch.setenv("DESPACHOX_PASARELA_USUARIO", "u")
    monkeypatch.setenv("DESPACHOX_PASARELA_CLAVE", "c")
    monkeypatch.setattr(pasarela_sms, "urlopen", falso_urlopen)
    assert pasarela_sms.enviar_por_el_celular("sms-prueba-6", "Recibido")
    destino, cuerpo, auth = enviados[0]
    assert destino.endswith("/message") and cuerpo == {"textMessage": {"text": "Recibido"}, "phoneNumbers": ["sms-prueba-6"]}
    assert auth.startswith("Basic ")
