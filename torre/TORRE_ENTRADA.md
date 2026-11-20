# Torre de control · A-entrada · rol A (entrada)
Última actualización: 2026-11-20 14:30 (hora de Colombia)

Sesión de Claude Code que lanzó Carlos para adelantar el módulo de Samuel. Samuel no tenía código local de `entrada/`.

## Estado en una frase
`entrada/` está completo y probado sin red (extractor falso y Telegram simulado); falta correrlo con el bot real porque no hay `.env` con `TELEGRAM_BOT_TOKEN` ni `ANTHROPIC_API_KEY`.

## Hecho (con el commit o archivo que lo prueba)
- `entrada/extraer.py`: Claude Haiku (`claude-haiku-5-5`) con `messages.parse` a un modelo pydantic; nunca lanza excepción.
- `entrada/privacidad.py`: limpieza de teléfonos, cédulas, correos y nombres presentados; hash HMAC con sal del id del chat.
- `entrada/guardar.py`: filas en `pedidos` (nuevo) y `cierres` (reportado), `duplicado_de`, `/estado`.
- `entrada/flujo.py`: conversación completa con `lugares.resolver`, `confirmar` y `corregir_con_pin`.
- `entrada/bot.py`: adaptador de Telegram en polling. `python -m entrada.bot`.
- `entrada/pruebas/`: 15 mensajes sintéticos, simulador de Telegram, 40 pruebas; `python -m pytest entrada/pruebas -q` da 39 pasan y 1 se omite (la medición con el modelo real).
- Prueba simulada de punta a punta sobre la base compartida (14:23): quedaron el pedido #21 (San José, confirmado por el remitente) y los cierres #2 (vía a Chinchiná, ubicación propuesta) y #3 (la siria, sin candidatos). Son sintéticos.

## En curso (qué, hasta dónde llegó, qué falta)
- Nada a medias. Lo pendiente depende de las claves.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
1. Crear `.env` en la carpeta principal con `TELEGRAM_BOT_TOKEN` y `ANTHROPIC_API_KEY`.
2. `export DESPACHOX_DB=/Users/cmorregof/Personal/despachoX/datos/despachox.db && python -m entrada.bot`
3. Escribir desde un teléfono «somos 40 familias en san jose no hay arroz ni leche» y medir el tiempo de respuesta.
4. `python -m pytest entrada/pruebas/test_campos.py -s` y pasar el número de `entrada/pruebas/reporte_campos.md` a la ficha.

## Decisiones y por qué
- La conversación vive en `flujo.Mesa`, sin Telegram, y `bot.py` solo traduce. Así el flujo completo se prueba sin red ni token.
- El texto se limpia antes de llamar al modelo, no solo antes de guardar: el dato personal no sale del proceso del bot.
- Un mensaje que el modelo no pudo leer se guarda como pedido `nuevo` sin datos, para que el despachador lo vea. Un mensaje que el modelo clasifica como `otro` (un saludo) no se guarda.
- Los kilos solo se guardan si el mensaje los dio para todos los productos. Si no, `kg_estimado` queda vacío y `despacho/` aplica su regla por familia. El modelo no calcula.
- `duplicado_de` se llena al confirmar el lugar, porque antes no hay punto. Solo marca.
- Al re-resolver por texto libre, la propuesta anterior en `ubicaciones` pasa a `rechazada`. Es la única escritura de `entrada/` fuera de `pedidos` y `cierres`; avisado en el canal.
- La sal del hash vive en `DESPACHOX_SAL` o en `datos/despachox.sal` junto a la base (ignorado por git).
- Con un reporte pendiente de ubicar, un texto que el modelo clasifica como `otro` se toma como respuesta de lugar.

## Bloqueos y preguntas para el capitán
- BLOQUEO parcial: no existe `.env` en esta copia ni en `/Users/cmorregof/Personal/despachoX/`. Faltan `TELEGRAM_BOT_TOKEN` y `ANTHROPIC_API_KEY`.
- Observación para `lugares/` (no lo toqué): «bajo prado» escrito exacto no sale como seguro, porque «El Prado» puntúa 0,93 y el margen exigido es 0,08. Sin modelo se ofrecen las dos opciones.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Variables: `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `DESPACHOX_DB`; opcionales `DESPACHOX_SAL`, `DESPACHOX_MODELO_ENTRADA`.
- `python -m entrada.bot` · `python -m pytest entrada/pruebas -q` · detalle en `entrada/README.md`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2, prototipo: el flujo chat → base → confirmación de lugar corre y tiene 39 pruebas que pasan. La demo con el teléfono de un jurado depende de las claves.
- Criterio 3, conocimiento: extracción estructurada con validación y confirmación humana del lugar. El porcentaje de campos correctos está por medir; no hay cifra todavía.
- Criterio 5, viabilidad: tratamiento de datos personales (Ley 1581) implementado y probado en `test_privacidad.py` y `test_flujo.py`.
