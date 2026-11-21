# Torre de control · A-entrada · rol A (entrada)
Última actualización: 2026-11-21 01:30 (hora de Colombia)

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

- 17:15 · Encargo A2, etapa 2 (rama `samuel-bot`): `/start` en tres líneas con dos ejemplos que se copian con un toque (HTML `<code>`); notas de voz en `entrada/voz.py` con un servicio compatible con Whisper, apagadas sin `DESPACHOX_VOZ_CLAVE`; `/estado` dice «recibido», «en revisión», «va en camino» (con la llegada del plan aprobado, leída de `paradas`) o «entregado». `entrada/pruebas/test_etapa2.py`. 62 pasan, 1 se omite. El aviso de vuelta (punto 3) espera respuesta en el canal.

- 18:00 · Encargo A2, etapa 3 (rama `samuel-bot`): `entrada/carga.py` y `entrada/ESCALA.md`. Medido con extractor falso (1,8 s de media): 5.000 mensajes a la vez, 914 por minuto, 0 errores, 0 perdidos; con 5 % de fallos de la API, 59 guardados crudos y 0 perdidos. Cuello de botella: `lugares/nomenclator.buscar` (97 % de 65 ms por mensaje en el hilo del bot). Cambios: un solo cliente de Anthropic con 2 reintentos del SDK, `concurrent_updates(32)`, `Mesa.atender_seguro` guarda crudo si falla la base. Falta la corrida de 100 con el modelo real (sin clave aquí). 66 pasan, 1 se omite.

- 19:00 · Alerta por silencio, pedida por Samuel (rama `samuel-bot`): columna `pedidos.origen` ('mensaje' | 'silencio') en `datos/esquema.sql`, con migración idempotente en `datos/db.py` (`_migrar`); `entrada/silencio.py` (umbral 6 h, jornada desde las 06:00, solo puntos críticos, una alerta viva por punto, urgencia 2, sin familias ni kilos); un pedido real ubicado en el punto la descarta; reloj en el bot cada 10 minutos; `python -m entrada.silencio`. `entrada/pruebas/test_silencio.py`: 8 pruebas. Suite completa del repositorio: 146 pasan, 3 se omiten.

- 20:00 · `docs/PILOTO.md`, pedido por Samuel: tesis del uso diario (banco de alimentos), casos RUD, Providencia y Salva RS, cierres viales de 2017 a 2023 con enlace, A25, doble propuesta de valor con las cifras de `docs/SIMULACION.md`, plan 30/60/90 con el día 60 como día normal de reparto en paralelo y los tres datos que se le piden al operador. Tres cifras nuevas en `docs/FUENTES.md` (DNP 2016, ABACO 2025, Banco de Manizales en ABACO), todas de resumen de búsqueda y sin abrir. Pendiente: el escenario sin cierres, que corre simulacion.

- 21:00 · Encargo A3, parte 1 (rama `samuel-bot`): `entrada/sms.py`, lector por reglas que devuelve el mismo `Extraccion`; `ENTREGADO CODIGO` llama a `despacho.paquetes.entregar`; respaldo del bot cuando el modelo falla o con `DESPACHOX_SIN_RED=1`; respuesta en un SMS ≤160 caracteres sin tildes (GSM-7). `entrada/pruebas/test_sms.py`: 20 SMS con errores, 20 de 20 bien, **no independiente** (casos y reglas de la misma sesión). Suite de entrada: 104 pasan, 1 se omite.

- 21:30 · Encargo A3, parte 2: `entrada/pasarela_sms.py`, receptor HTTP sin dependencias nuevas, que acepta el formato genérico, formulario y los avisos `sms:received` de SMS Gateway for Android (capcom6, Apache 2.0). Responde en el cuerpo y, si se configura, pide al celular enviar la respuesta. Probado con `curl` de punta a punta; **sin celular real ni video**. `entrada/SMS.md`: montaje sin internet y comparación con Twilio, sin precios (no consultados). `test_pasarela.py`: 5 pruebas. Suite de entrada: 109 pasan, 1 se omite.

- 22:30 · Verificación de las trece cifras candidatas en `docs/FUENTES.md`, con frase literal, publicación, corte y resultado. Abierta por tres agentes lectores, **pendiente de visto bueno de Samuel**. Nueve coinciden; cuatro CIFRA DUDOSA en el canal (formato azul «después de revisar la vivienda», 204 JAC por PDF escaneado, Banco de Manizales en ABACO por 403, «tres camiones en ruta»); los 87 registros de Letras son cálculo propio, por recalcular.

- 23:00 · Raciones con fuente en `entrada/raciones.py` (de `docs/datos/demanda.md`, sección 7): 555 g de ración seca por persona y día (ACNUR, Logistics Cluster), cereal 6:2:2 (ICBF), 2,9 personas por hogar (DANE 2018), pedido de 7 días (OPS/INCAP), agua de 1 día; frescos con la referencia del ICBF; pollo, pan, atún, azúcar, café, chocolate y papa se reconocen sin kilos. `despacho/semilla.py` no se tocó: la bodega sigue con la tabla vieja (aviso en el canal). Pruebas ahora leen las constantes. 110 pasan, 1 se omite.

- 23:30 · `ENTREGADO` solo desde el destino o el conductor (`guardar.quien_confirma`, `flujo._entregar`): vale quien hizo el pedido o quien ya pidió para el mismo punto con origen `mensaje`; el conductor, cuando exista `vehiculos.conductor_hash` (pedida a B). Misma respuesta para código inexistente y no autorizado; rechazos en la bitácora. `test_entregado.py`: 6 pruebas. 116 pasan, 1 se omite. Es arreglo de seguridad: puede entrar después del congelamiento.

- 01:30 (21 nov) · Encargo P4, carga de 15.000 a la vez, solo local: 0 perdidos, base íntegra, 91 a 98 MB. Sin caché 1.032/min; con `entrada/cache_lugares.py` 1.641/min con 50 a la vez y 6.050/min con 200. Espera de la persona con caché y 50: mediana 269 s y máximo 548 s. Se corrigió el arnés: antes no contaba la espera en fila (las filas de 5.000 la subestiman). Telegram: unos 30 mensajes por segundo en masivos (FAQ oficial), así que 15.000 respuestas toman unos 8 minutos. 120 pasan, 1 se omite.

## En curso (qué, hasta dónde llegó, qué falta)
- Prueba desde un teléfono con el bot real: nadie le ha escrito todavía.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
1. Con `.env`: `python -m entrada.carga --n 100 --concurrencia 10 --extractor real` y pasar tokens y costo medidos a `entrada/ESCALA.md` (reemplaza el supuesto).
2. Con `.env`: `python -m entrada.extraer "hay 6 bebes sin leche desde ayer en la enea necesitamos urgente"`.
3. Respuestas pendientes en el canal: columna `pedidos.dudas`, clave de voz y aviso de vuelta.
4. Sábado 8:30 a. m. congelamiento: después solo arreglos.

## Decisiones y por qué
- La conversación vive en `flujo.Mesa`, sin Telegram, y `bot.py` solo traduce. Así el flujo completo se prueba sin red ni token.
- El texto se limpia antes de llamar al modelo, no solo antes de guardar: el dato personal no sale del proceso del bot.
- Un mensaje que el modelo no pudo leer se guarda como pedido `nuevo` sin datos, para que el despachador lo vea. Un mensaje que el modelo clasifica como `otro` (un saludo) no se guarda.
- Los kilos solo se guardan si el mensaje los dio para todos los productos. Si no, `kg_estimado` queda vacío y `despacho/` aplica su regla por familia. El modelo no calcula.
- `duplicado_de` se llena al confirmar el lugar, porque antes no hay punto. Solo marca.
- Al re-resolver por texto libre, la propuesta anterior en `ubicaciones` pasa a `rechazada`. Es la única escritura de `entrada/` fuera de `pedidos` y `cierres`; avisado en el canal.
- La sal del hash vive en `DESPACHOX_SAL` o en `datos/despachox.sal` junto a la base (ignorado por git).
- Con un reporte pendiente de ubicar, un texto que el modelo clasifica como `otro` se toma como respuesta de lugar.

- Los kilos y las familias que completa la mesa son reglas del código, escritas en `entrada/raciones.py` con su fuente (desde las 23:00) y visibles en `dudas`. El modelo solo cuenta lo que el mensaje dice (`personas`, `bebes`); no estima.
- La pregunta de familias va después de ubicar, para no cambiar el orden que ya funciona y hacer una sola pregunta a la vez. Si nadie responde, el pedido ya está guardado con lo que había.
- Un botón de familias vale aunque hayan pasado los dos minutos (es inequívoco); un número escrito solo dentro de los dos minutos.
- Las dudas se guardan en `pedidos.dudas` solo si la columna existe; mientras tanto quedan en la respuesta al remitente y en la marca `supuesto` de cada producto.

- Voz: se eligió la interfaz de OpenAI `/audio/transcriptions` porque la ofrecen varios proveedores y no pide dependencias nuevas (`httpx` ya viene con `python-telegram-bot`). El bot muestra lo que escuchó para que la persona pueda corregir.
- `/estado` lee `paradas` y `planes` solo para mostrar la llegada estimada; no escribe en ellas.

- Reintentos: se usa el del SDK (`max_retries=2`, espera creciente, respeta `retry-after`) en vez de escribir uno propio.
- No se tocó `lugares/` aunque es el cuello de botella: se avisó por el canal con el perfil.

- `datos/esquema.sql` y `datos/db.py` los tocó entrada/ por decisión de Samuel como líder, aunque el encargo A2 decía pedir columnas por el canal. Se avisó.
- La alerta solo cuenta un pedido con lugar confirmado como contacto: un mensaje sin lugar no se sabe de qué punto es.
- Una alerta de un punto que nunca escribió no se descarta sola al empezar la jornada siguiente; solo la descarta un mensaje posterior o el despachador.
- No se agregó `pedidos.dudas`: no hubo confirmación.

## Bloqueos y preguntas para el capitán
- Resuelto 14:56: `.env` creado en la carpeta principal con las dos claves.
- `lugares/nomenclator.py` tiene el mismo problema del modelo vacío si `DESPACHOX_MODELO_LUGARES=` queda sin valor en `.env`. No lo toqué; dejé la línea comentada en `.env.example`.
- Observación para `lugares/` (no lo toqué): «bajo prado» escrito exacto no sale como seguro, porque «El Prado» puntúa 0,93 y el margen exigido es 0,08. Sin modelo se ofrecen las dos opciones.

- 16:30 · PREGUNTA en el canal: columna `pedidos.dudas TEXT` (JSON) para que el despachador vea qué completó la mesa.

- 17:15 · PREGUNTA en el canal: clave de un servicio de transcripción (`DESPACHOX_VOZ_CLAVE`).
- 17:15 · PREGUNTA en el canal: propuesta del aviso de vuelta (tabla `avisos` con consentimiento, borrado al entregar).

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Variables: `TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`, `DESPACHOX_DB`; opcionales `DESPACHOX_SAL`, `DESPACHOX_MODELO_ENTRADA`.
- `python -m entrada.bot` · `python -m pytest entrada/pruebas -q` · detalle en `entrada/README.md`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2, prototipo: el flujo chat → base → confirmación de lugar corre y tiene 39 pruebas que pasan. La demo con el teléfono de un jurado depende de las claves.
- Criterio 3, conocimiento: extracción estructurada con validación y confirmación humana del lugar. Medido por nosotros: 62 de 64 campos (96,9 %) en 15 mensajes sintéticos, una corrida (`entrada/pruebas/reporte_campos.md`).
- Criterio 5, viabilidad: tratamiento de datos personales (Ley 1581) implementado y probado en `test_privacidad.py` y `test_flujo.py`.
