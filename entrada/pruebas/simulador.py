"""Un Telegram de mentira: entrega actualizaciones a los manejadores del bot y recoge lo que contestan."""
import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace

from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup

from entrada.bot import Manejadores


@dataclass
class Enviado:
    texto: str
    botones: list = field(default_factory=list)      # (etiqueta, dato)
    pide_ubicacion: bool = False
    botones_quitados: bool = False


class ClienteSimulado:
    """Una persona en un chat. `escribir`, `pulsar` y `enviar_ubicacion` devuelven lo que contestó el bot."""

    def __init__(self, mesa, chat_id=1001):
        self.m = Manejadores(mesa)
        self.chat = SimpleNamespace(id=chat_id)
        self.enviados: list[Enviado] = []

    def _mensaje(self, **campos):
        async def reply_text(texto, reply_markup=None):
            e = Enviado(texto)
            if isinstance(reply_markup, InlineKeyboardMarkup):
                e.botones = [(b.text, b.callback_data) for fila in reply_markup.inline_keyboard for b in fila]
            e.pide_ubicacion = isinstance(reply_markup, ReplyKeyboardMarkup)
            self.enviados.append(e)
        return SimpleNamespace(text=None, location=None, reply_text=reply_text, **campos)

    def _correr(self, manejador, **update):
        antes = len(self.enviados)
        asyncio.run(manejador(SimpleNamespace(effective_chat=self.chat, **update), None))
        return self.enviados[antes:]

    def escribir(self, texto):
        m = self._mensaje()
        m.text = texto
        return self._correr(self.m.texto, effective_message=m)

    def comando(self, nombre):
        return self._correr(getattr(self.m, nombre), effective_message=self._mensaje())

    def enviar_ubicacion(self, lat, lon):
        m = self._mensaje()
        m.location = SimpleNamespace(latitude=lat, longitude=lon)
        return self._correr(self.m.ubicacion, effective_message=m)

    def enviar_foto(self):
        return self._correr(self.m.otro, effective_message=self._mensaje())

    def pulsar(self, etiqueta, de: Enviado | None = None):
        """Pulsa el botón cuya etiqueta empieza por `etiqueta` en el último mensaje con botones."""
        origen = de or next(e for e in reversed(self.enviados) if e.botones)
        dato = next(d for t, d in origen.botones if t.startswith(etiqueta))

        async def answer():
            pass

        async def quitar(reply_markup=None):
            origen.botones_quitados = True
        q = SimpleNamespace(data=dato, answer=answer, edit_message_reply_markup=quitar, message=self._mensaje())
        return self._correr(self.m.boton, callback_query=q)
