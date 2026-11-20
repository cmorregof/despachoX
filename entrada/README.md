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

Comandos: `/estado` muestra los últimos pedidos de ese chat; `/start` y `/ayuda` explican cómo escribir.

## Archivos

| Archivo | Qué hace |
|---|---|
| `bot.py` | Adaptador de Telegram (polling). Solo traduce entre Telegram y `flujo.Mesa` |
| `flujo.py` | La conversación: qué se guarda y qué se contesta ante texto, botones y ubicaciones |
| `extraer.py` | Llamada a Claude Haiku con salida validada por pydantic. Nunca lanza excepción |
| `raciones.py` | Raciones por familia, conversión de personas y bebés a familias, productos para bebés. El supuesto está escrito arriba |
| `guardar.py` | Escritura en `pedidos` y `cierres`, duplicados y consulta de `/estado` |
| `privacidad.py` | Limpieza del texto y hash con sal del id del chat |
| `pruebas/` | Quince mensajes de ejemplo, Telegram simulado y pruebas |

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

- Solo texto. Los mensajes de voz reciben una respuesta que pide escribir.
- Los reportes pendientes de ubicar se llevan en memoria. Si el bot se reinicia, los botones de los mensajes anteriores siguen funcionando, pero una respuesta en texto libre o un pin ya no se asocian al reporte anterior.
- `cierres` no tiene `remitente_hash`, así que `/estado` solo muestra pedidos.
- La consulta a la base y el desempate de lugares con modelo corren en el hilo del bot. Para una demostración con pocos chats alcanza.
