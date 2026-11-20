# T1 · Vista por territorio

Aprobado por Carlos el viernes a las 5:10 p. m. Entra antes del congelamiento del sábado a las 8:30 a. m. Lo escribió Fable.

## Por qué

En la mentoría 1 preguntaron qué prototipo va a medir el efecto de la solución en la región, y pidieron pensar en personas y territorio. Hoy el tablero mide la ciudad entera. Esta vista mide por comuna y vereda, y muestra además qué barrios no han pedido nada. Esa lista le sirve a la Unidad de Gestión del Riesgo, porque un barrio callado puede ser un barrio sin señal o sin líder.

Le suma al criterio 2 (un prototipo que mide), al 6 (indicadores verificables por territorio) y al 4 (el piloto se evalúa con esta tabla).

## Parte B · `despacho/territorio.py` (sesión B-despacho, rama `carlos-despacho`)

Solo lee la base. No cambia el esquema ni el optimizador.

`resumen(con, desde=None, hasta=None, ahora=None) -> list[dict]` devuelve una fila por comuna, y una fila `"sin comuna"` para los puntos que no la tienen. Columnas:

| Columna | Qué es |
|---|---|
| `territorio` | La comuna del punto de entrega |
| `puntos`, `puntos_criticos` | Puntos con al menos un pedido en el periodo, y cuántos de ellos son críticos |
| `pedidos`, `familias`, `kg_pedidos` | Pedidos del periodo, sin los `descartado` ni los que tienen `duplicado_de` |
| `entregados`, `kg_entregados` | Pedidos en estado `entregado` |
| `a_tiempo`, `pct_a_tiempo` | Entregados con hora de entrega menor o igual a `limite_en`. La hora de entrega es el `entregado_en` más tardío de sus paquetes. Los pedidos sin `limite_en` no cuentan en el denominador |
| `criticos_a_tiempo`, `pct_criticos_a_tiempo` | Lo mismo, solo en puntos críticos. Es el indicador del reto, por territorio |
| `espera_mediana_h` | Mediana de horas entre `creado_en` y la entrega, en los pedidos entregados |
| `pendiente_mas_viejo_h` | Horas que lleva esperando el pedido abierto más antiguo, a la hora `ahora` |

`silencio(con, desde=None) -> list[dict]` devuelve los barrios y veredas del nomenclátor (tabla `lugares`, tipos `barrio` y `vereda`) sin ningún pedido en el periodo, con su comuna si se conoce. En pantalla se dice «sin pedidos registrados», nunca «sin necesidad».

Línea de comandos: `python -m despacho.territorio [--desde 2026-11-21T00:00] [--csv salida.csv]` imprime la tabla y la lista de barrios sin pedidos. Con `--csv` la exporta para el informe del piloto.

Sin datos personales: no salen `texto_original` ni `remitente_hash`.

Pruebas en `despacho/tests/test_territorio.py`, con una base temporal: una comuna sin pedidos, un pedido entregado tarde, un duplicado que no cuenta, un punto sin comuna y un pedido sin `limite_en`.

Hecho cuando las pruebas pasan, `python -m despacho.territorio` corre sobre la semilla y hay una entrada LISTO en el canal con un ejemplo de la salida.

## Parte C · pestaña «Territorio» en el tablero (Jacobo, rama `jacobo-tablero`)

- Una pestaña nueva que llama `despacho.territorio.resumen(con)` y `despacho.territorio.silencio(con)`.
- La tabla va ordenada por porcentaje de críticos a tiempo, con los territorios peor atendidos arriba. Un color suave marca lo que está por debajo de la meta.
- Debajo, la lista «Barrios y veredas sin pedidos registrados».
- Un botón «Descargar CSV».
- Si la parte B no ha llegado, la pestaña dice «Pendiente: despacho.territorio» y el tablero no se rompe.

Hecho cuando las pruebas del tablero pasan y hay una captura de la pestaña en el canal.

## Qué no tocar

El optimizador, el esquema de la base y el bot.
