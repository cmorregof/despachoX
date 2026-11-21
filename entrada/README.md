# entrada/ · del chat a la base

Un bot de Telegram al que se le escribe en lenguaje libre. Deja en la base un pedido de ayuda o un cierre vial estructurado, le contesta a la persona lo que entendió y le pide confirmar el lugar.

El modelo solo lee y estructura. No asigna prioridad final, no ubica y no despacha: el lugar lo propone `lugares/` y lo confirma una persona, y el plan lo aprueba el despachador.

## Arrancar

```bash
pip install -r requirements.txt
cp .env.example .env        # y pon TELEGRAM_BOT_TOKEN y ANTHROPIC_API_KEY
export DESPACHOX_DB=/ruta/absoluta/a/datos/despachox.db    # la misma que usan despacho/ y tablero/
python -m entrada.bot
```

Sin `TELEGRAM_BOT_TOKEN` el bot no arranca y lo dice. Sin `ANTHROPIC_API_KEY`, o si el modelo falla, el bot sigue en pie: guarda el texto como pedido `nuevo` sin datos y responde que un despachador lo revisará.

## Crear el bot en BotFather

1. En Telegram, abre el chat con `@BotFather` y envía `/newbot`.
2. Dale un nombre visible (por ejemplo «DespachoX Manizales») y un usuario que termine en `bot`.
3. BotFather responde con el token. Cópialo en `.env` como `TELEGRAM_BOT_TOKEN=...`. No lo pegues en el chat del equipo ni en el repositorio; si se filtra, `/revoke` en BotFather da uno nuevo.
4. Opcional, con `/setcommands`: `estado - cómo van mis pedidos` y `ayuda - cómo escribirle a la mesa`.
5. Arranca el bot y escríbele desde el teléfono.

## Qué pasa con cada mensaje

1. `privacidad.limpiar` quita lo que parezca teléfono, cédula, correo o nombre presentado («me llamo…»). Lo hace antes de llamar al modelo y antes de guardar.
2. `extraer.extraer` llama a Claude Haiku y devuelve un objeto pydantic: `tipo` (`pedido`, `cierre` u `otro`), el pedido (lugar, familias, productos con kilos si se dicen, urgencia de 1 a 3, horas de plazo), el cierre (lugar, descripción, vehículos que no pasan) y las `dudas`. Un mensaje puede traer pedido y cierre a la vez.
3. `raciones` completa lo que el mensaje no dijo, con reglas escritas en el código: personas o bebés se vuelven familias aproximadas (1 familia cada 4 personas; 1 por bebé; mínimo 1), los productos para bebés (leche, pañales, fórmula) se conservan aunque el modelo los omita, y los productos de la tabla reciben kilos por ración. Todo lo completado lleva la marca `supuesto` en el JSON de `productos` y queda en `dudas`.
4. `guardar` escribe la fila de inmediato: pedido en estado `nuevo` con `punto_id` vacío, o cierre en estado `reportado` sin coordenadas.
5. `lugares.resolver` propone la ubicación. El bot responde lo que entendió más la pregunta, con botones: «Sí, es ahí», uno por cada alternativa y «Enviar mi ubicación».
6. «Sí» o una alternativa llaman `lugares.confirmar`. Un mensaje de ubicación de Telegram llama `lugares.corregir_con_pin`. Si la persona contesta con texto («no, es en Bajo Prado»), se vuelve a resolver con ese texto y la propuesta anterior queda `rechazada`. Un «sí» escrito vale como el botón.
7. Al confirmar un pedido, si hay otro pedido vivo del mismo punto en las últimas dos horas se llena `duplicado_de`. Solo se marca; el despachador decide.

8. Si el mensaje no dijo cuántas familias, al ubicar el pedido el bot hace una sola pregunta: «¿Para cuántas familias es?», con botones 1 a 5, 6 a 10, 11 a 20 y más de 20 (se guarda 3, 8, 15 o 25) o el número escrito. Si nadie responde en dos minutos, un número escrito ya no se toma como respuesta y el pedido queda con lo que había y su duda anotada.

Un pedido sin lugar confirmado se queda con `punto_id` vacío. El despachador lo ve en el tablero y lo ubica ahí.

Comandos: `/start` y `/ayuda` explican en tres líneas qué hace el bot y dan dos ejemplos que se copian con un toque. `/estado` dice cómo va cada pedido de ese chat: «recibido», «en revisión», «va en camino» (con la llegada estimada del plan aprobado) o «entregado».

**Notas de voz.** Con `DESPACHOX_VOZ_CLAVE` en `.env`, la nota se transcribe con un servicio compatible con Whisper (`entrada/voz.py`), el bot muestra «Escuché: …» ya sin datos personales y sigue el flujo normal. El audio no se guarda. Sin clave, el bot pide escribir. Notas de más de dos minutos se piden más cortas.

## Archivos

| Archivo | Qué hace |
|---|---|
| `bot.py` | Adaptador de Telegram (polling). Solo traduce entre Telegram y `flujo.Mesa` |
| `flujo.py` | La conversación: qué se guarda y qué se contesta ante texto, botones y ubicaciones |
| `extraer.py` | Llamada a Claude Haiku con salida validada por pydantic. Nunca lanza excepción |
| `raciones.py` | Raciones por familia, conversión de personas y bebés a familias, productos para bebés. El supuesto está escrito arriba |
| `voz.py` | Transcripción de notas de voz con un servicio externo. Nunca lanza excepción |
| `carga.py` | Prueba de carga: N mensajes sintéticos por el camino del bot, con concurrencia configurable. Resultados en `ESCALA.md` |
| `silencio.py` | Alerta por silencio: un punto crítico sin pedidos en 6 horas recibe una fila `origen='silencio'` para que el despachador decida si manda a verificar. `python -m entrada.silencio` |
| `sms.py` | Lector de SMS por reglas, sin modelo ni red: `PEDIDO 40 SAN JOSE ARROZ LECHE`, `CIERRE AV DEL CENTRO CAMION`, `ENTREGADO DX7K2Q`. Respuesta en un SMS de 160 caracteres. Respaldo del bot si el modelo falla o con `DESPACHOX_SIN_RED=1` |
| `pasarela_sms.py` | Receptor HTTP de SMS en la red local, para un celular Android que hace de pasarela. `python -m entrada.pasarela_sms`. Guía en `SMS.md` |
| `cache_lugares.py` | Caché por texto delante de la búsqueda de lugares: baja el tiempo del hilo del bot de 57,5 a 7,6 ms por mensaje sin cambiar resultados. Se apaga con `DESPACHOX_CACHE_LUGARES=0` |
| `guardar.py` | Escritura en `pedidos` y `cierres`, duplicados y consulta de `/estado` |
| `privacidad.py` | Limpieza del texto y hash con sal del id del chat |
| `pruebas/` | Quince mensajes de ejemplo, Telegram simulado y pruebas |

## Alerta por silencio

Un barrio que no escribe no debe desaparecer de la lista. Cada 10 minutos, el bot revisa los puntos con `critico = 1`. Si uno lleva 6 horas sin un pedido con lugar confirmado (contadas desde las 06:00 si nunca escribió), deja en `pedidos` una fila con `origen='silencio'`, estado `nuevo`, urgencia 2 y el texto «Sin contacto hace 7 h. Visita de verificación.». No trae familias, kilos ni remitente. Cada punto tiene a lo sumo una alerta viva: la revisión siguiente actualiza sus horas. Cuando llega un pedido real con lugar confirmado en ese punto, la alerta pasa a `descartado`, y las dos cosas quedan en la bitácora. Umbral, inicio de jornada e intervalo: `DESPACHOX_SILENCIO_HORAS`, `DESPACHOX_JORNADA_INICIO` y `DESPACHOX_SILENCIO_MIN`. Son supuestos del equipo, declarados en la cabecera de `silencio.py`. Para la demostración: `python -m entrada.silencio --ahora 2026-11-21T14:00:00`.

Esto no despacha nada. El despachador ve la fila y decide si manda a verificar o la descarta.

## Privacidad (Ley 1581)

- `remitente_hash` es un HMAC-SHA256 del id del chat con una sal que vive fuera del repositorio: la variable `DESPACHOX_SAL` o, si falta, un archivo `.sal` que se crea junto a la base. Sin la sal no se puede volver al id.
- El bot no lee el nombre, el usuario ni el teléfono de la cuenta de Telegram. El registro del proceso no incluye el texto de los mensajes.
- `texto_original` se guarda ya limpio. La limpieza es una heurística: quita lo que tiene forma de dato personal, no garantiza que no quede ninguno.
- La ubicación que alguien envía sí se guarda, porque es el punto de entrega.

## Pruebas

```bash
python -m pytest entrada/pruebas -q                      # sin red: extractor falso y Telegram simulado
python -m pytest entrada/pruebas/test_campos.py -s       # con ANTHROPIC_API_KEY: mide el extractor real
python -m entrada.extraer "somos 40 familias en san jose no hay arroz ni leche"
```

`test_campos.py` corre los quince mensajes contra el modelo real, cuenta cuántos campos salen bien y deja el resultado en `pruebas/reporte_campos.md`. Sin clave se omite. Ese número todavía no se ha medido.

## Límites conocidos

- Las notas de voz necesitan la clave de un servicio de transcripción; sin ella se pide escribir.
- Los reportes pendientes de ubicar se llevan en memoria. Si el bot se reinicia, los botones de los mensajes anteriores siguen funcionando, pero una respuesta en texto libre o un pin ya no se asocian al reporte anterior.
- `cierres` no tiene `remitente_hash`, así que `/estado` solo muestra pedidos.
- La base y la ubicación de lugares corren en el hilo del bot, uno a la vez; el modelo se llama en paralelo (`DESPACHOX_CONCURRENCIA`, 32 por defecto). La medición está en `ESCALA.md`.
- Si la API de Anthropic falla, el SDK reintenta dos veces con espera creciente (429, 5xx, red). Si fallan los tres intentos, o si falla la base, el mensaje se guarda como texto crudo para el despachador: no se pierde.
