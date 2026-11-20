"""Lo que no debe llegar a la base ni al modelo: teléfonos, cédulas, correos, nombres y el id del chat.

`limpiar` es una heurística, no una garantía: quita lo que tiene forma de dato personal. Se aplica
antes de llamar al modelo y antes de guardar, así el texto crudo nunca sale del proceso del bot.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
from pathlib import Path

from datos import db

# Tres formas de número largo: celular colombiano con separadores, corrida de 7 o más dígitos, y
# grupos separados por punto, espacio o guion donde cada grupo después del primero tiene 3 o más
# dígitos (cédula «1.053.123.456», fijo «606 887 1234»). «20 30 40 kilos» no coincide.
_NUMERO = re.compile(
    r"(?<![\d.,])(?:\+?57[\s.-]?)?(?:"
    r"3\d{2}[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}"
    r"|\d{7,13}"
    r"|\d{1,4}(?:[\s.-]\d{3,4}){2,4}"
    r")(?!\d)")
_CORREO = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_ETIQUETA_DOC = re.compile(r"\b(?:c\.?\s?c\.?|c[eé]dula|tel[eé]fono|tel\.?|cel\.?|celular|whatsapp|nit)\s*"
                           r"(?:n[uú]mero|no\.?|#|:)?\s*(?=\[)", re.I)
# Después de estas fórmulas viene un nombre propio.
_PRESENTACION = re.compile(
    r"\b(me llamo|mi nombre es|le escribe|les escribe|le habla|les habla|habla|atentamente|att\.?|"
    r"firma|pregunten por|preguntar por|llamar a|llamen a|contacto)\b[\s:,]*", re.I)
_SOY = re.compile(r"\b(soy|somos)\s+(?:(?:el|la)\s+)?(?:(?:se[ñn]or|se[ñn]ora|don|do[ñn]a|sr\.?|sra\.?|"
                  r"profe|profesor|profesora|padre|pastor)\s+)?", re.I)
# Palabras que cortan el nombre: lo que sigue ya es contenido del mensaje.
_NO_NOMBRE = {"de", "del", "la", "el", "los", "las", "y", "en", "un", "una", "presidente", "presidenta",
              "lider", "líder", "lideresa", "vecino", "vecina", "comite", "comité", "junta", "conductor",
              "conductora", "voluntario", "voluntaria", "familias", "personas", "necesitamos", "somos",
              "aqui", "aquí", "que", "por", "para", "con", "al", "a", "no", "hay", "desde"}
_PALABRA = re.compile(r"[^\W\d_]+", re.UNICODE)


def _quitar_nombre(texto: str, desde: int, solo_mayusculas: bool) -> str:
    """Reemplaza hasta tres palabras que siguen a una fórmula de presentación."""
    pos, quitadas, fin = desde, 0, desde
    while quitadas < 3:
        m = _PALABRA.match(texto, pos)
        if not m or m.group().lower() in _NO_NOMBRE:
            break
        if solo_mayusculas and not m.group()[0].isupper():
            break
        quitadas, fin = quitadas + 1, m.end()
        siguiente = re.match(r"[ \t]+", texto[fin:])
        if not siguiente:
            break
        pos = fin + siguiente.end()
    return texto if quitadas == 0 else texto[:desde] + "[nombre]" + texto[fin:]


def limpiar(texto: str | None) -> str:
    """Devuelve el texto sin lo que parezca teléfono, cédula, correo o nombre propio presentado."""
    t = " ".join((texto or "").split())
    t = _CORREO.sub("[correo]", t)
    t = _NUMERO.sub("[número]", t)
    t = _ETIQUETA_DOC.sub("", t)
    pos = 0
    while (m := _PRESENTACION.search(t, pos)):
        t = _quitar_nombre(t, m.end(), solo_mayusculas=False)
        pos = m.end()
    pos = 0
    while (m := _SOY.search(t, pos)):     # «soy María» sí; «soy del comité» y «somos 40» no
        t = _quitar_nombre(t, m.end(), solo_mayusculas=True)
        pos = m.end()
    return t.strip()


def _sal() -> bytes:
    """La sal vive fuera del repositorio: variable DESPACHOX_SAL o un archivo junto a la base.
    Se crea sola la primera vez. Si se pierde, /estado deja de reconocer a quien ya escribió."""
    if os.environ.get("DESPACHOX_SAL"):
        return os.environ["DESPACHOX_SAL"].encode()
    ruta = Path(os.environ.get("DESPACHOX_DB") or db.RUTA_DB).with_suffix(".sal")
    if not ruta.exists():
        ruta.write_text(secrets.token_hex(32), encoding="utf-8")
        ruta.chmod(0o600)
    return ruta.read_text(encoding="utf-8").strip().encode()


def hash_remitente(chat_id: int | str) -> str:
    """Hash con sal del id del chat. Mismo chat, mismo hash; no se puede volver al id sin la sal."""
    return hmac.new(_sal(), str(chat_id).encode(), hashlib.sha256).hexdigest()[:32]
