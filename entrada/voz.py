"""Notas de voz a texto. El modelo de Anthropic no transcribe audio, así que se usa un servicio aparte.

Sirve cualquier servicio con la interfaz `POST /audio/transcriptions` de OpenAI (Whisper de OpenAI,
Groq y otros). Se configura en `.env`:

    DESPACHOX_VOZ_CLAVE=...                                         # sin clave, el bot pide escribir
    DESPACHOX_VOZ_URL=https://api.openai.com/v1/audio/transcriptions   # opcional
    DESPACHOX_VOZ_MODELO=whisper-1                                   # opcional

Privacidad: el audio se envía al servicio y no se guarda en ninguna parte. Lo que se guarda es la
transcripción, que pasa por `privacidad.limpiar` como cualquier texto. Nunca lanza excepción.
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger("entrada.voz")
URL = "https://api.openai.com/v1/audio/transcriptions"
MODELO = "whisper-1"
SEGUNDOS = 20.0
MAX_SEGUNDOS_AUDIO = 120        # una nota más larga se pide más corta: tarda y cuesta más


def disponible() -> bool:
    return bool(os.environ.get("DESPACHOX_VOZ_CLAVE"))


def transcribir(audio: bytes, nombre: str = "nota.ogg") -> str | None:
    """Texto de la nota, o None si no hay servicio o falló."""
    clave = os.environ.get("DESPACHOX_VOZ_CLAVE")
    if not clave or not audio:
        return None
    try:
        import httpx
        r = httpx.post(os.environ.get("DESPACHOX_VOZ_URL") or URL,
                       headers={"Authorization": f"Bearer {clave}"},
                       data={"model": os.environ.get("DESPACHOX_VOZ_MODELO") or MODELO, "language": "es"},
                       files={"file": (nombre, audio, "audio/ogg")}, timeout=SEGUNDOS)
        r.raise_for_status()
        texto = (r.json().get("text") or "").strip()
        return texto or None
    except Exception as e:                       # sin red, clave mala, límite, respuesta rara
        log.warning("no se pudo transcribir la nota (%s)", type(e).__name__)
        return None
