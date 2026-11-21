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
import json
import logging
import os
import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
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
        if "event" in d:                                   # SMS Gateway for Android
            if d.get("event") != "sms:received":
                return None, None, False
            p = d.get("payload") or {}
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
        token = os.environ.get("DESPACHOX_SMS_TOKEN")
        dado = self.headers.get("X-Token") or parse_qs(urlparse(self.path).query).get("token", [None])[0]
        if token and dado != token:
            return self._responder(401, {"error": "token"})
        largo = int(self.headers.get("Content-Length") or 0)
        if largo > MAX_BYTES:
            return self._responder(413, {"error": "muy largo"})
        try:
            numero, texto, es_sms = extraer_sms(self.rfile.read(largo), self.headers.get("Content-Type") or "")
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Receptor de SMS de DespachoX en la red local.")
    ap.add_argument("--puerto", type=int, default=PUERTO)
    a = ap.parse_args(argv)
    from dotenv import load_dotenv
    load_dotenv(db.RAIZ.parent / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    servidor = Pasarela(("0.0.0.0", a.puerto))
    print(f"Receptor de SMS en http://{_ip_local()}:{a.puerto}/sms  (configure esa dirección en el celular)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
