# Encargo A · Entrada (Samuel)

Soy Samuel, líder del equipo. Mi rol hoy es A (entrada) y además llevo la ficha de los seis componentes. Crea mi torre `torre/TORRE_SAMUEL.md` desde la plantilla y mantenla al día.

Lee `CLAUDE.md`, `docs/ROLES_VIERNES.md`, `datos/esquema.sql` y `datos/db.py`.

## Objetivo

Un bot de Telegram al que cualquiera le escribe en lenguaje libre y que deja en la base un pedido de ayuda o un cierre vial bien estructurado, y le contesta al remitente lo que entendió.

## Reglas de este módulo

- Trabajo solo dentro de `entrada/`. Me comunico con los demás únicamente por la base, usando `datos.db.conectar()`. Escribo en `pedidos` y `cierres`; no toco otras tablas.
- El modelo solo extrae. No asigna prioridad final ni decide nada.
- No guardo nombres, teléfonos ni el id del chat en claro: `remitente_hash` es un hash.
- Claves en `.env` (`TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`).

## Pasos

1. `entrada/extraer.py`: función `extraer(texto) -> dict` que llama a Claude Haiku y devuelve un objeto validado con pydantic:
   - `tipo`: `pedido`, `cierre` u `otro`;
   - pedido: `lugar`, `familias`, `productos` (lista de producto y kg si se dice), `urgencia` 1 a 3, `horas_limite` si se menciona;
   - cierre: `lugar`, `descripcion`, `tipos_bloqueados` (subconjunto de camion, campero, moto);
   - `dudas`: lo que el mensaje no dice y haría falta.
   Si el modelo falla o no hay clave, devuelve `tipo="otro"` con el texto crudo, sin lanzar excepción.
2. `entrada/lugares.py`: `ubicar(lugar) -> (punto_id o None, lat, lon)` contra `datos/semilla/barrios.csv` y `datos/semilla/vias.csv` (los genera Carlos; mientras llegan, usa tres filas de prueba). Coincidencia sin tildes ni mayúsculas y por similitud. Si no encuentra, deja las coordenadas vacías y lo anota en `dudas`.
3. `entrada/bot.py` con `python-telegram-bot` en modo polling:
   - recibe texto, extrae, ubica y guarda la fila con estado `nuevo` (pedido) o `reportado` (cierre);
   - marca `duplicado_de` si hay un pedido del mismo punto en las últimas dos horas;
   - responde: «Entendí: 40 familias en San José, arroz y leche, urgente. Queda en revisión del despachador.» Si hay dudas, las pregunta.
   - comando `/estado` que devuelve el estado de los pedidos de ese remitente.
4. `entrada/pruebas/`: quince mensajes de ejemplo, varios con errores de tipeo, sin puntuación o mezclando pedido y cierre, y una prueba con pytest que mide cuántos campos extrae bien. Ese número va a la ficha.
5. Cuando funcione de punta a punta, propón commit y push, y dime qué sigue.

## Hecho cuando

Escribo «somos 40 familias en san jose no hay arroz ni leche» desde mi teléfono, y en menos de diez segundos hay una fila en `pedidos` con punto, familias y productos, y el bot me contesta lo que entendió.

## En paralelo

Lanza un agente Sonnet que redacte en `docs/FICHA.md` los componentes 1, 2 y 3, usando `docs/ESTADO_DEL_ARTE.md` y `docs/investigacion/04_evidencia_del_problema.md`. Cada cifra con su enlace, y marcadas las que nadie del equipo ha verificado todavía. Yo reviso el texto antes del commit.

**Aporta a:** criterio 2 (demo en vivo con el teléfono de un jurado) y criterio 1 (ficha).
