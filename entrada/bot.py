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

from entrada import silencio, voz
from entrada.flujo import Mesa, Respuesta, ayuda

log = logging.getLogger("entrada.bot")
RAIZ = Path(__file__).resolve().parent.parent
SIN_VOZ = ("Todavía no puedo escuchar notas de voz. Escríbeme qué necesitan, para cuántas familias y dónde, "
           "o qué vía está cerrada.")
VOZ_LARGA = "La nota es muy larga. Mándame una de menos de dos minutos, o escríbeme."
VOZ_FALLO = "No pude escuchar bien la nota. ¿Me la escribes, por favor?"
SOLO_TEXTO = ("Por ahora solo leo texto. Escríbeme qué necesitan y dónde, o qué vía está cerrada. "
              "Si quieres fijar un lugar, envíame la ubicación con el clip del chat.")
CONCURRENCIA = int(os.environ.get("DESPACHOX_CONCURRENCIA") or 32)
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
        await update.effective_message.reply_text(ayuda(voz.disponible()), parse_mode="HTML")

    async def estado(self, update: Update, context) -> None:
        await self._enviar(update.effective_message, self.mesa.estado(update.effective_chat.id))

    async def texto(self, update: Update, context) -> None:
        mensaje = update.effective_message
        lectura = await asyncio.to_thread(self.mesa.leer, mensaje.text or "")   # la llamada al modelo
        for r in self.mesa.atender_seguro(update.effective_chat.id, lectura):
            await self._enviar(mensaje, r)

    async def nota_de_voz(self, update: Update, context) -> None:
        """Nota de voz: se transcribe, se le muestra a la persona lo que se escuchó y sigue el flujo
        normal, como si lo hubiera escrito. El audio no se guarda."""
        mensaje = update.effective_message
        nota = mensaje.voice or mensaje.audio
        if not voz.disponible():
            await mensaje.reply_text(SIN_VOZ)
            return
        if (nota.duration or 0) > voz.MAX_SEGUNDOS_AUDIO:
            await mensaje.reply_text(VOZ_LARGA)
            return
        archivo = await nota.get_file()
        audio = bytes(await archivo.download_as_bytearray())
        texto = await asyncio.to_thread(voz.transcribir, audio)
        if not texto:
            await mensaje.reply_text(VOZ_FALLO)
            return
        lectura = await asyncio.to_thread(self.mesa.leer, texto)          # limpia y llama al modelo
        await mensaje.reply_text(f"Escuché: «{lectura.texto}»")
        for r in self.mesa.atender_seguro(update.effective_chat.id, lectura):
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


async def vigilar_silencio(mesa: Mesa, cada_s: float | None = None, vueltas: int | None = None) -> None:
    """El reloj de la alerta por silencio: revisa al arrancar y luego cada `cada_s`. Corre en el hilo
    del bot, el mismo que usa la base, así que no compite con los mensajes por la conexión."""
    cada_s = silencio.CADA_MIN * 60 if cada_s is None else cada_s
    n = 0
    while vueltas is None or n < vueltas:
        try:
            h = silencio.revisar(mesa.con)
            if h["creadas"] or h["descartadas"]:
                log.info("silencio: %d alertas nuevas, %d descartadas", len(h["creadas"]), len(h["descartadas"]))
        except Exception as e:                  # una revisión fallida no tumba el bot
            log.error("falló la revisión de silencio (%s)", type(e).__name__)
        n += 1
        if vueltas is None or n < vueltas:
            await asyncio.sleep(cada_s)


def construir(token: str, mesa: Mesa) -> Application:
    m = Manejadores(mesa)

    async def al_arrancar(app: Application) -> None:
        app.create_task(vigilar_silencio(mesa))
    # Varios mensajes a la vez: mientras uno espera al modelo, otros avanzan. La base y la memoria
    # de la conversación solo se tocan en el hilo del bot, así que no hay escrituras simultáneas.
    app = Application.builder().token(token).concurrent_updates(CONCURRENCIA).post_init(al_arrancar).build()
    app.add_handler(CommandHandler(["start", "ayuda", "help"], m.inicio))
    app.add_handler(CommandHandler("estado", m.estado))
    app.add_handler(CallbackQueryHandler(m.boton))
    app.add_handler(MessageHandler(filters.LOCATION, m.ubicacion))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, m.texto))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, m.nota_de_voz))
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
    if not voz.disponible():
        log.warning("Sin DESPACHOX_VOZ_CLAVE: las notas de voz reciben una respuesta que pide escribir.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        log.warning("Sin ANTHROPIC_API_KEY: los mensajes se guardan sin leer y los revisa el despachador.")
    from datos import db
    if os.environ.get("DESPACHOX_CACHE_LUGARES", "1") != "0":      # rendimiento; no cambia resultados
        from entrada import cache_lugares
        cache_lugares.instalar()
    mesa = Mesa(db.conectar())
    log.info("Bot en marcha. Base: %s", os.environ.get("DESPACHOX_DB") or db.RUTA_DB)
    construir(token, mesa).run_polling(allowed_updates=Update.ALL_TYPES)
    return 0


if __name__ == "__main__":
    sys.exit(main())
