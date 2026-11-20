"""Bot de Telegram en modo polling. Arranca con:  python -m entrada.bot

Este archivo solo traduce entre Telegram y `entrada.flujo.Mesa`. Del remitente usa el id del chat,
que se convierte en hash; no lee nombre, usuario ni teléfono, y no escribe el texto en el registro.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, Update)
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from entrada.flujo import AYUDA, Mesa, Respuesta

log = logging.getLogger("entrada.bot")
RAIZ = Path(__file__).resolve().parent.parent
SOLO_TEXTO = ("Por ahora solo leo texto. Escríbeme qué necesitan y dónde, o qué vía está cerrada. "
              "Si quieres fijar un lugar, envíame la ubicación con el clip del chat.")
ERROR = "Tuve un problema al procesar eso. Inténtalo de nuevo en un momento, por favor."


def _teclado(r: Respuesta):
    if r.pedir_ubicacion:
        return ReplyKeyboardMarkup([[KeyboardButton("Enviar mi ubicación", request_location=True)]],
                                   resize_keyboard=True, one_time_keyboard=True)
    if r.botones:
        return InlineKeyboardMarkup([[InlineKeyboardButton(etiqueta, callback_data=dato)]
                                     for etiqueta, dato in r.botones])
    return None


class Manejadores:
    """Las funciones que atienden cada tipo de actualización. Se prueban con un Telegram simulado."""

    def __init__(self, mesa: Mesa):
        self.mesa = mesa

    async def _enviar(self, mensaje, r: Respuesta, quitar_teclado: bool = False) -> None:
        marca = _teclado(r) or (ReplyKeyboardRemove() if quitar_teclado else None)
        await mensaje.reply_text(r.texto, reply_markup=marca)

    async def inicio(self, update: Update, context) -> None:
        await update.effective_message.reply_text(AYUDA)

    async def estado(self, update: Update, context) -> None:
        await self._enviar(update.effective_message, self.mesa.estado(update.effective_chat.id))

    async def texto(self, update: Update, context) -> None:
        mensaje = update.effective_message
        lectura = await asyncio.to_thread(self.mesa.leer, mensaje.text or "")   # la llamada al modelo
        for r in self.mesa.atender(update.effective_chat.id, lectura):
            await self._enviar(mensaje, r)

    async def ubicacion(self, update: Update, context) -> None:
        mensaje = update.effective_message
        r = self.mesa.recibir_ubicacion(update.effective_chat.id, mensaje.location.latitude,
                                        mensaje.location.longitude)
        await self._enviar(mensaje, r, quitar_teclado=True)

    async def boton(self, update: Update, context) -> None:
        q = update.callback_query
        await q.answer()
        r = self.mesa.pulsar(update.effective_chat.id, q.data)
        if not r.pedir_ubicacion and not r.botones:
            try:                                    # la pregunta ya se respondió: se quitan sus botones
                await q.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass
        await self._enviar(q.message, r)

    async def otro(self, update: Update, context) -> None:
        await update.effective_message.reply_text(SOLO_TEXTO)

    async def error(self, update, context) -> None:
        log.error("error al atender una actualización: %s", type(context.error).__name__, exc_info=context.error)
        if isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(ERROR)
            except Exception:
                pass


def construir(token: str, mesa: Mesa) -> Application:
    m = Manejadores(mesa)
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler(["start", "ayuda", "help"], m.inicio))
    app.add_handler(CommandHandler("estado", m.estado))
    app.add_handler(CallbackQueryHandler(m.boton))
    app.add_handler(MessageHandler(filters.LOCATION, m.ubicacion))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, m.texto))
    app.add_handler(MessageHandler(~filters.COMMAND, m.otro))
    app.add_error_handler(m.error)
    return app


def main() -> int:
    from dotenv import load_dotenv
    load_dotenv(RAIZ / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)      # sus líneas llevan el token en la URL
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Falta TELEGRAM_BOT_TOKEN en .env. Cómo obtenerlo: entrada/README.md", file=sys.stderr)
        return 1
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.warning("Sin ANTHROPIC_API_KEY: los mensajes se guardan sin leer y los revisa el despachador.")
    from datos import db
    mesa = Mesa(db.conectar())
    log.info("Bot en marcha. Base: %s", os.environ.get("DESPACHOX_DB") or db.RUTA_DB)
    construir(token, mesa).run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
