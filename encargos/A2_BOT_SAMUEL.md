# Encargo A2 · El bot, para vecinos de verdad y para miles de mensajes (Samuel)

Pégalo en Claude Code abierto en la carpeta del repositorio, con el modelo que tengas (Opus 5.5 si tu plan lo permite). Tienes plan Pro: no leas archivos que no hagan falta y no lances agentes en paralelo salvo que ahorren tiempo de verdad.

---

Soy Samuel, líder de DespachoX y dueño de `entrada/` (el bot de Telegram). Te llamas `A-entrada` en `torre/CANAL.md`; mi torre es `torre/TORRE_ENTRADA.md`. Desde ahora soy yo quien dirige este módulo.

Lee, en este orden y nada más: `docs/PROBLEMA.md`, `entrada/README.md`, `torre/TORRE_ENTRADA.md`, las entradas de `torre/CANAL.md` desde las 15:05 y `entrada/flujo.py`.

**Rama de trabajo.** No trabajes en `main`: cada push a `main` redespliega el servidor y corta las pruebas de todos. Haz `git pull --rebase`, crea la rama `samuel-bot` y sube ahí. Cuando una etapa esté probada, abre un pull request a `main` y avísale a Carlos por el canal: él fusiona a horas fijas.

## Etapa 1 · Que entienda a un vecino (lo primero, antes de las 6:30 p. m.)

Caso real que falló en la nube: «hay 6 bebes sin leche desde ayer en la enea necesitamos urgente». El bot dejó familias y kilos vacíos y el pedido salió con 10 kg de mercado genérico, sin leche.

1. Personas, bebés, niños o adultos mayores se convierten en familias aproximadas (regla escrita y visible en el código, por ejemplo 1 familia cada 4 personas, mínimo 1) y la conversión queda en `dudas`.
2. Si falta la cantidad o el número de familias en un pedido, el bot **pregunta una sola cosa**, con botones cuando se pueda: «¿Para cuántas familias?» con 1–5, 6–10, 11–20, más de 20. Si no responden en dos minutos, se guarda con lo que hay y se marca la duda.
3. Productos sin kilos: una tabla de raciones por familia en `entrada/raciones.py` (arroz, leche, agua, panela, frijol, aceite y los que salgan en la semilla), con el supuesto escrito arriba. Un producto para bebés (leche, pañales) se conserva aunque no esté en la tabla.
4. Pruebas nuevas en `entrada/pruebas/` con el mensaje de La Enea y nueve variantes parecidas.

**Hecho cuando:** ese mensaje deja un pedido con familias, leche con kilos y una duda anotada, y el bot preguntó lo que faltaba.

## Etapa 2 · Que sea cómodo para quien escribe (antes del congelamiento, sábado 8:30 a. m.)

Elige en este orden y para cuando se acabe el tiempo:

1. **Primer mensaje claro.** `/start` explica en tres líneas qué puede hacer y da dos ejemplos para copiar. Sin tecnicismos.
2. **Notas de voz.** Mucha gente dicta en vez de escribir. Transcribe la nota (el modelo de Anthropic no transcribe audio: usa el servicio que ya prevé `.env.example` o, si no hay, dile a Carlos qué clave hace falta) y sigue el flujo normal mostrando la transcripción.
3. **Aviso de vuelta.** Cuando el despachador aprueba un plan que incluye el pedido, el bot le escribe a quien pidió: «Tu pedido va en camino, llegada estimada 4:30 p. m.». Necesita guardar el chat de forma reversible solo para responder: propón cómo hacerlo sin romper la regla de privacidad (por ejemplo, una tabla aparte que se borra al entregar) y pregúntalo por el canal antes de hacerlo.
4. **`/estado`** con lenguaje humano: «recibido», «en revisión», «va en camino», «entregado».

## Etapa 3 · Que aguante miles de mensajes

Diez mil mensajes al día son unos siete por minuto: eso ya lo aguanta. Lo que tumba un bot en una emergencia es el pico, por ejemplo quinientos mensajes en diez minutos. No reescribas la arquitectura: **mide** y arregla lo que se rompa.

1. Script `entrada/carga.py` que manda N mensajes sintéticos por el flujo con el Telegram simulado y el extractor real o falso, con concurrencia configurable. Reporta: mensajes por minuto, tiempo de respuesta medio y máximo, errores, y costo estimado con el precio público del modelo.
2. Corre 100 con el extractor real y 5.000 con el falso. Reporta tal como salga.
3. Arregla lo que aparezca. Lo esperable:
   - procesar mensajes en paralelo (`concurrent_updates` en python-telegram-bot);
   - reintentos con espera creciente cuando la API de Anthropic devuelve límite de tasa o error temporal, sin perder el mensaje: si falla tres veces, se guarda como texto crudo para el despachador;
   - escrituras cortas a SQLite y un solo `commit` por mensaje.
4. Escribe en `entrada/ESCALA.md`: la medición, el costo por cada 10.000 mensajes, qué aguanta hoy y qué haría falta para cien mil (webhook en vez de polling, una cola, PostgreSQL). Eso va al componente 5 de la ficha.

**Hecho cuando:** hay una tabla medida en `entrada/ESCALA.md` y ningún mensaje se pierde cuando la API falla.

## Reglas

- La regla del proyecto no cambia: el modelo lee y estructura; no decide prioridades ni despacha.
- No toques `despacho/`, `lugares/`, `tablero/` ni `datos/esquema.sql`. Si necesitas una columna, pídela por el canal.
- Ninguna clave en el repositorio. Ningún dato personal real en las pruebas.
- Al cerrar cada etapa: torre al día, entrada LISTO en el canal, push a `samuel-bot` y aviso a Carlos.
