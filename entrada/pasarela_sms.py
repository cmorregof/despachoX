"""Receptor de SMS: un celular Android hace de pasarela y le reenvía cada SMS por la red local.

    python -m entrada.pasarela_sms                 # escucha en el puerto 8081 de este portátil
    curl -X POST http://localhost:8081/sms -H "Content-Type: application/json" \\
         -d '{"de": "sms-prueba-1", "texto": "PEDIDO 40 SAN JOSE ARROZ LECHE"}'

Funciona sin internet: el celular y el portátil solo tienen que estar en el mismo wifi del acopio.
Cada SMS pasa por `sms.leer_sms` y por el mismo flujo del bot, y la respuesta (un SMS de 160
caracteres o menos) vuelve en el cuerpo de la respuesta HTTP.

Formatos que acepta (`entrada/SMS.md` dice cómo configurar cada uno):
- Genérico: JSON `{"de": ..., "texto": ...}` o formulario `from=...&message=...`.
- SMS Gateway for Android (capcom6, Apache 2.0), aviso `sms:received`: JSON
  `{"event": "sms:received", "payload": {"message": ..., "sender"|"phoneNumber": ...}}`. Esa
  aplicación no manda la respuesta HTTP como SMS. Para contestar, el receptor llama a la API local
  del celular si se configuran DESPACHOX_PASARELA_URL, _USUARIO y _CLAVE. El formato de ese envío
  está **por verificar** con la documentación de la versión instalada.

Privacidad: el número del remitente se convierte en hash dentro del flujo y no se guarda. El
registro del proceso no escribe ni el número ni el texto.
"""
from __future__ import annotations

import argparse
import base64
import hmac
import json
import logging
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen

from datos import db
from entrada import sms
from entrada.flujo import Mesa

log = logging.getLogger("entrada.pasarela_sms")
PUERTO = int(os.environ.get("DESPACHOX_SMS_PUERTO") or 8081)
MAX_BYTES = 10_000


def extraer_sms(cuerpo: bytes, tipo: str) -> tuple[str | None, str | None, bool]:
    """(remitente, texto, es_sms) desde el cuerpo que manda la pasarela. es_sms=False para avisos
    que no son un SMS recibido (por ejemplo, «sms:sent»), que se contestan sin hacer nada."""
    if "json" in tipo:
        d = json.loads(cuerpo or b"{}")
        if not isinstance(d, dict):                        # «[]», «"x"» o «5»: ilegible, no un error 500
            raise ValueError("se esperaba un objeto JSON")
        if "event" in d:                                   # SMS Gateway for Android
            if d.get("event") != "sms:received":
                return None, None, False
            p = d.get("payload") or {}
            if not isinstance(p, dict):
                raise ValueError("payload no es un objeto JSON")
            return p.get("sender") or p.get("phoneNumber"), p.get("message") or p.get("text"), True
        return d.get("de") or d.get("from"), d.get("texto") or d.get("message") or d.get("text"), True
    f = {k: v[0] for k, v in parse_qs(cuerpo.decode("utf-8", "replace")).items()}
    return f.get("de") or f.get("from"), f.get("texto") or f.get("message") or f.get("text"), True


def enviar_por_el_celular(numero: str, texto: str) -> bool:
    """Le pide al celular pasarela que envíe la respuesta. Solo si está configurado. Nunca lanza."""
    url = os.environ.get("DESPACHOX_PASARELA_URL")
    if not url:
        return False
    try:
        credencial = base64.b64encode(f"{os.environ.get('DESPACHOX_PASARELA_USUARIO', '')}:"
                                      f"{os.environ.get('DESPACHOX_PASARELA_CLAVE', '')}".encode()).decode()
        cuerpo = json.dumps({"textMessage": {"text": texto}, "phoneNumbers": [numero]}).encode()
        req = Request(url, data=cuerpo, method="POST",
                      headers={"Content-Type": "application/json", "Authorization": f"Basic {credencial}"})
        with urlopen(req, timeout=5) as r:
            return 200 <= r.status < 300
    except Exception as e:
        log.warning("el celular no aceptó la respuesta (%s)", type(e).__name__)
        return False


class Receptor(BaseHTTPRequestHandler):
    server_version = "DespachoX-SMS"
    timeout = 15        # el servidor tiene un solo hilo: un cliente que no termina de enviar no lo bloquea

    def log_message(self, formato, *args):           # el registro por defecto escribiría la ruta y la IP
        pass

    def _responder(self, codigo: int, datos: dict) -> None:
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if urlparse(self.path).path == "/salud":
            return self._responder(200, {"ok": True})
        self._responder(404, {"error": "use POST /sms"})

    def do_POST(self):
        if urlparse(self.path).path not in ("/sms", "/webhook/sms-received"):
            return self._responder(404, {"error": "use POST /sms"})
        # El cuerpo se lee siempre antes de contestar: si se contesta con datos sin leer, Windows corta la
        # conexión y la pasarela ve un error de red en vez del 401 o el 413.
        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            largo = -1
        if largo < 0:               # con -1, rfile.read esperaría hasta que el cliente cierre
            self.close_connection = True
            return self._responder(400, {"error": "Content-Length inválido"})
        cuerpo = self.rfile.read(min(largo, 1_000_000))
        token = os.environ.get("DESPACHOX_SMS_TOKEN")
        dado = self.headers.get("X-Token") or parse_qs(urlparse(self.path).query).get("token", [None])[0]
        if token and not hmac.compare_digest(str(dado or "").encode(), token.encode()):
            return self._responder(401, {"error": "token"})
        if largo > MAX_BYTES:
            self.close_connection = True
            return self._responder(413, {"error": "muy largo"})
        try:
            numero, texto, es_sms = extraer_sms(cuerpo, self.headers.get("Content-Type") or "")
        except (ValueError, UnicodeDecodeError):
            return self._responder(400, {"error": "cuerpo ilegible"})
        if not es_sms:
            return self._responder(200, {"ignorado": True})
        if not numero or texto is None:
            return self._responder(400, {"error": "faltan remitente o texto"})
        respuesta = sms.atender_sms(self.server.mesa(), str(numero), str(texto))
        enviado = enviar_por_el_celular(str(numero), respuesta)
        log.info("SMS atendido (%d caracteres de respuesta)", len(respuesta))
        self._responder(200, {"respuesta": respuesta, "para": numero, "enviado_por_el_celular": enviado})


class Pasarela(HTTPServer):
    """Un solo hilo: la base y la memoria de la conversación se usan desde el hilo que atiende."""

    def __init__(self, direccion, ruta_db: Path | str | None = None):
        super().__init__(direccion, Receptor)
        self.ruta_db = ruta_db or os.environ.get("DESPACHOX_DB") or db.RUTA_DB
        self._mesa = None

    def mesa(self) -> Mesa:
        if self._mesa is None:                          # se crea en el hilo que atiende
            self._mesa = Mesa(db.conectar(self.ruta_db), extraer=sms.leer_sms, elegir=None)
        return self._mesa


def _ip_local() -> str:
    """La IP de este portátil en el wifi del acopio. No envía nada: solo pregunta la ruta."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def registrar(celular: str, usuario: str, clave: str, puerto: int, ip: str | None = None) -> tuple[int, str]:
    """Le pide a SMS Gateway for Android (modo servidor local) que reenvíe cada SMS recibido a este
    portátil. Devuelve el código HTTP y lo que contestó el celular, para leer un error si lo hay."""
    destino = f"http://{ip or _ip_local()}:{puerto}/sms"
    if os.environ.get("DESPACHOX_SMS_TOKEN"):           # sin esto, con token el celular recibiría 401
        destino += "?token=" + quote(os.environ["DESPACHOX_SMS_TOKEN"], safe="")
    cuerpo = json.dumps({"id": "despachox", "url": destino, "event": "sms:received"}).encode()
    credencial = base64.b64encode(f"{usuario}:{clave}".encode()).decode()
    req = Request(celular.rstrip("/") + "/webhooks", data=cuerpo, method="POST",
                  headers={"Content-Type": "application/json", "Authorization": f"Basic {credencial}"})
    try:
        with urlopen(req, timeout=10) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except Exception as e:
        codigo = getattr(e, "code", 0)
        detalle = e.read().decode("utf-8", "replace") if hasattr(e, "read") else f"{type(e).__name__}: {e}"
        return codigo, detalle


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Receptor de SMS de DespachoX en la red local.")
    ap.add_argument("--puerto", type=int, default=PUERTO)
    ap.add_argument("--registrar", metavar="URL_CELULAR",
                    help="registra el aviso sms:received en el celular, por ejemplo http://192.168.1.20:8080, y sale")
    ap.add_argument("--usuario", default="sms")
    ap.add_argument("--clave", default="")
    a = ap.parse_args(argv)
    if a.registrar:
        codigo, respuesta = registrar(a.registrar, a.usuario, a.clave, a.puerto)
        print(f"El celular respondió {codigo}: {respuesta[:500]}")
        print(f"Reenviará los SMS a http://{_ip_local()}:{a.puerto}/sms" if 200 <= codigo < 300
              else "No quedó registrado. Revise la IP, el usuario y la clave que muestra la aplicación.")
        return 0 if 200 <= codigo < 300 else 1
    from dotenv import load_dotenv
    load_dotenv(db.RAIZ.parent / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    if not os.environ.get("DESPACHOX_SMS_TOKEN"):
        log.warning("Sin DESPACHOX_SMS_TOKEN: cualquiera en este wifi puede enviar SMS falsos, también "
                    "«ENTREGADO». Defínalo antes de --registrar el celular.")
    servidor = Pasarela(("0.0.0.0", a.puerto))
    print(f"Receptor de SMS en http://{_ip_local()}:{a.puerto}/sms  (configure esa dirección en el celular)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
