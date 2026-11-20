# Torre de control · A-entrada · rol A (entrada)
Última actualización: 2026-11-20 16:30 (hora de Colombia)

Desde las 16:05 el módulo lo dirige Samuel con `encargos/A2_BOT_SAMUEL.md`. Se trabaja en la rama `samuel-bot`; Carlos fusiona a `main` a las 6:30 p. m., 11:00 p. m. y 8:00 a. m.

## Estado en una frase
Etapa 1 del encargo A2 hecha en `samuel-bot` y probada con el extractor falso: «6 bebés sin leche en La Enea» deja 6 familias estimadas, leche con 12 kg, dudas anotadas y la pregunta «¿Para cuántas familias?» con botones. Falta medirla con el modelo real (no hay `.env` en el equipo de Samuel).

## Hecho (con el commit o archivo que lo prueba)
- `entrada/extraer.py`: Claude Haiku (`claude-haiku-5-5`) con `messages.parse` a un modelo pydantic; nunca lanza excepción.
- `entrada/privacidad.py`: limpieza de teléfonos, cédulas, correos y nombres presentados; hash HMAC con sal del id del chat.
- `entrada/guardar.py`: filas en `pedidos` (nuevo) y `cierres` (reportado), `duplicado_de`, `/estado`.
- `entrada/flujo.py`: conversación completa con `lugares.resolver`, `confirmar` y `corregir_con_pin`.
- `entrada/bot.py`: adaptador de Telegram en polling. `python -m entrada.bot`.
- `entrada/pruebas/`: 15 mensajes sintéticos, simulador de Telegram, 40 pruebas; `python -m pytest entrada/pruebas -q` da 39 pasan y 1 se omite (la medición con el modelo real).
- Prueba simulada de punta a punta sobre la base compartida (14:23): quedaron el pedido #21 (San José, confirmado por el remitente) y los cierres #2 (vía a Chinchiná, ubicación propuesta) y #3 (la siria, sin candidatos). Son sintéticos.

- 15:00 · Medición con el modelo real (`claude-haiku-5-5`, una corrida): 62 de 64 campos correctos (96,9 %), 0 llamadas fallidas, 26 s para los 15 mensajes. Detalle en `entrada/pruebas/reporte_campos.md`. Los mensajes son sintéticos y los escribió el equipo.
- 15:00 · Corregido: una variable opcional vacía en `.env` dejaba el modelo en blanco y todo se guardaba sin leer.

- 16:30 · Encargo A2, etapa 1 (rama `samuel-bot`): `entrada/raciones.py` (raciones por familia iguales a `despacho/semilla.py`, 1 familia cada 4 personas, 1 por bebé, productos para bebés que se conservan); el extractor lee `personas` y `bebes`; el código, no el modelo, los convierte en familias, con respaldo por expresión regular si el modelo no contó; kilos por ración marcados `supuesto` en el JSON de `productos`; tras ubicar el pedido, una sola pregunta «¿Para cuántas familias?» con botones o número escrito, que vence a los dos minutos. `entrada/pruebas/test_enea.py`: el mensaje de La Enea y nueve variantes. `python -m pytest entrada/pruebas -q`: 54 pasan, 1 se omite.

## En curso (qué, hasta dónde llegó, qué falta)
- Prueba desde un teléfono con el bot real: nadie le ha escrito todavía.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
1. Con `.env` (clave de Anthropic): `python -m entrada.extraer "hay 6 bebes sin leche desde ayer en la enea necesitamos urgente"` y revisar que salga `bebes: 6` y `leche`. Si no, el respaldo del código lo cubre, pero hay que anotarlo.
2. Etapa 2 del encargo A2: `/start` en tres líneas con dos ejemplos (`AYUDA` en `entrada/flujo.py`).
3. Si Carlos agrega `pedidos.dudas`, el código ya la llena sin cambios.

## Decisiones y por qué
- La conversación vive en `flujo.Mesa`, sin Telegram, y `bot.py` solo traduce. Así el flujo completo se prueba sin red ni token.
- El texto se limpia antes de llamar al modelo, no solo antes de guardar: el dato personal no sale del proceso del bot.
- Un mensaje que el modelo no pudo leer se guarda como pedido `nuevo` sin datos, para que el despachador lo vea. Un mensaje que el modelo clasifica como `otro` (un saludo) no se guarda.
- Los kilos solo se guardan si el mensaje los dio para todos los productos. Si no, `kg_estimado` queda vacío y `despacho/` aplica su regla por familia. El modelo no calcula.
- `duplicado_de` se llena al confirmar el lugar, porque antes no hay punto. Solo marca.
- Al re-resolver por texto libre, la propuesta anterior en `ubicaciones` pasa a `rechazada`. Es la única escritura de `entrada/` fuera de `pedidos` y `cierres`; avisado en el canal.
- La sal del hash vive en `DESPACHOX_SAL` o en `datos/despachox.sal` junto a la base (ignorado por git).
- Con un reporte pendiente de ubicar, un texto que el modelo clasifica como `otro` se toma como respuesta de lugar.

- Los kilos y las familias que completa la mesa son reglas del código, escritas en `entrada/raciones.py` y visibles en `dudas`. El modelo solo cuenta lo que el mensaje dice (`personas`, `bebes`); no estima.
- La pregunta de familias va después de ubicar, para no cambiar el orden que ya funciona y hacer una sola pregunta a la vez. Si nadie responde, el pedido ya está guardado con lo que había.
- Un botón de familias vale aunque hayan pasado los dos minutos (es inequívoco); un número escrito solo dentro de los dos minutos.
- Las dudas se guardan en `pedidos.dudas` solo si la columna existe; mientras tanto quedan en la respuesta al remitente y en la marca `supuesto` de cada producto.

## Bloqueos y preguntas para el capitán
- Resuelto 14:56: `.env` creado en la carpeta principal con las dos claves.
- `lugares/nomenclator.py` tiene el mismo problema del modelo vacío si `DESPACHOX_MODELO_LUGARES=` queda sin valor en `.env`. No lo toqué; dejé la línea comentada en `.env.example`.
- Observación para `lugares/` (no lo toqué): «bajo prado» escrito exacto no sale como seguro, porque «El Prado» puntúa 0,93 y el margen exigido es 0,08. Sin modelo se ofrecen las dos opciones.

- 16:30 · PREGUNTA en el canal: columna `pedidos.dudas TEXT` (JSON) para que el despachador vea qué completó la mesa.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Variables: `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `DESPACHOX_DB`; opcionales `DESPACHOX_SAL`, `DESPACHOX_MODELO_ENTRADA`.
- `python -m entrada.bot` · `python -m pytest entrada/pruebas -q` · detalle en `entrada/README.md`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2, prototipo: el flujo chat → base → confirmación de lugar corre y tiene 39 pruebas que pasan. La demo con el teléfono de un jurado depende de las claves.
- Criterio 3, conocimiento: extracción estructurada con validación y confirmación humana del lugar. Medido por nosotros: 62 de 64 campos (96,9 %) en 15 mensajes sintéticos, una corrida (`entrada/pruebas/reporte_campos.md`).
- Criterio 5, viabilidad: tratamiento de datos personales (Ley 1581) implementado y probado en `test_privacidad.py` y `test_flujo.py`.
