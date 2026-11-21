# Sensibilidad de la simulación

Estado: corrida de la madrugada del sábado 21 de noviembre de 2026, sin revisar todavía por el equipo.

**Estos números no son el resultado principal de la simulación.** Salen de una referencia propia de este análisis y sirven para ver si las conclusiones cambian cuando cambia un supuesto. El resultado principal lo corre otra sesión, en otra máquina, con su propia implementación de las velocidades medidas. Por eso la fila de referencia de este documento puede no coincidir con su cifra. En las 30 semillas que comparte con la corrida de velocidades medidas de la rama `simulacion`, las líneas base dan cifras idénticas y DespachoX cifras muy cercanas (sección 5).

## 1. Qué pregunta responde

La simulación de `docs/SIMULACION.md` compara cuatro formas de despachar la misma jornada, y varios de sus supuestos son nuestros, entre ellos la velocidad de las vías, la demanda, el tamaño de la flota y el peso que el optimizador les da a los puntos críticos. Este análisis cambia esos supuestos uno a uno y mide si DespachoX conserva su ventaja en los dos indicadores del reto, los pedidos críticos entregados a tiempo y el perecedero vencido.

Cada variante cambia un solo supuesto respecto de la referencia. La referencia usa la velocidad medida en Manizales, la carga media, la flota completa y el factor crítico 3. Todas las variantes usan las mismas 60 semillas, así que cada diferencia se calcula jornada por jornada.

## 2. Resultados

Las tres tablas tienen la misma forma. Cada fila es una variante, con su número de semillas, la media de cada política y la diferencia pareada de `despachox` menos cada línea base, con el intervalo de confianza del 95 % entre corchetes. Las dos primeras tablas son los indicadores del reto. La tercera, las entregas a tiempo en todos los puntos, se incluye porque ahí la política experta le ganaba a DespachoX en la corrida del 20 de noviembre. Todas las métricas, también las de `optimiza_una_vez`, la espera del punto peor atendido y los kilómetros, están en `analisis/sensibilidad/resultados/resumen.md`.

### 2.1 Pedidos de puntos críticos entregados a tiempo (%)

| Variante | Semillas | `despachox` | `ingenua` | `experta` | `despachox` − `ingenua` (IC 95 %) | `despachox` − `experta` (IC 95 %) |
|---|---:|---:|---:|---:|---|---|
| Referencia de la sensibilidad (no es el resultado principal) | 60 | 99,3 | 54,7 | 96,1 | 44,6 [40,4; 48,8] | 3,2 [2,1; 4,4] |
| Velocidad medida × 0,8 | 60 | 99,1 | 43,3 | 94,0 | 55,8 [51,9; 59,7] | 5,1 [3,6; 6,6] |
| Velocidad medida × 1,2 | 60 | 99,5 | 62,6 | 97,5 | 36,9 [32,4; 41,3] | 1,9 [1,1; 2,8] |
| Demanda × 0,75 | 60 | 99,4 | 83,8 | 98,4 | 15,5 [11,9; 19,2] | 0,9 [0,0; 1,8] |
| Demanda × 1,5 | 60 | 98,5 | 29,2 | 88,1 | 69,4 [67,0; 71,7] | 10,5 [8,3; 12,6] |
| Flota con un campero menos | 60 | 98,0 | 37,4 | 91,6 | 60,6 [57,1; 64,0] | 6,3 [4,4; 8,3] |
| Flota con dos camperos menos | 60 | 96,2 | 29,6 | 83,9 | 66,6 [63,6; 69,6] | 12,3 [9,8; 14,7] |
| Factor crítico 1 | 60 | 96,5 | 54,7 | 96,1 | 41,8 [38,0; 45,6] | 0,4 [−1,0; 1,9] |
| Factor crítico 5 | 60 | 99,4 | 54,7 | 96,1 | 44,7 [40,4; 49,0] | 3,3 [2,1; 4,6] |

### 2.2 Kilos perecederos vencidos (%)

| Variante | Semillas | `despachox` | `ingenua` | `experta` | `despachox` − `ingenua` (IC 95 %) | `despachox` − `experta` (IC 95 %) |
|---|---:|---:|---:|---:|---|---|
| Referencia de la sensibilidad (no es el resultado principal) | 60 | 0,0 | 3,3 | 0,0 | −3,3 [−3,9; −2,7] | 0,0 [0,0; 0,0] |
| Velocidad medida × 0,8 | 60 | 0,0 | 4,5 | 0,0 | −4,5 [−5,3; −3,8] | 0,0 [0,0; 0,0] |
| Velocidad medida × 1,2 | 60 | 0,0 | 2,2 | 0,0 | −2,2 [−2,7; −1,7] | 0,0 [0,0; 0,0] |
| Demanda × 0,75 | 60 | 0,0 | 1,0 | 0,0 | −1,0 [−1,4; −0,6] | 0,0 [0,0; 0,0] |
| Demanda × 1,5 | 60 | 0,0 | 8,2 | 0,0 | −8,2 [−9,1; −7,2] | 0,0 [0,0; 0,0] |
| Flota con un campero menos | 60 | 0,0 | 5,7 | 0,0 | −5,7 [−6,5; −4,9] | 0,0 [0,0; 0,0] |
| Flota con dos camperos menos | 60 | 0,0 | 7,8 | 0,0 | −7,8 [−8,6; −7,1] | 0,0 [0,0; 0,0] |
| Factor crítico 1 | 60 | 0,0 | 3,3 | 0,0 | −3,3 [−3,9; −2,7] | 0,0 [0,0; 0,0] |
| Factor crítico 5 | 60 | 0,0 | 3,3 | 0,0 | −3,3 [−3,9; −2,7] | 0,0 [0,0; 0,0] |

### 2.3 Pedidos entregados a tiempo, todos los puntos (%)

| Variante | Semillas | `despachox` | `ingenua` | `experta` | `despachox` − `ingenua` (IC 95 %) | `despachox` − `experta` (IC 95 %) |
|---|---:|---:|---:|---:|---|---|
| Referencia de la sensibilidad (no es el resultado principal) | 60 | 87,2 | 79,2 | 87,5 | 8,0 [6,7; 9,3] | −0,3 [−1,4; 0,9] |
| Velocidad medida × 0,8 | 60 | 80,8 | 69,7 | 79,0 | 11,1 [9,5; 12,7] | 1,8 [0,7; 3,0] |
| Velocidad medida × 1,2 | 60 | 90,7 | 85,2 | 92,3 | 5,5 [4,4; 6,6] | −1,5 [−2,5; −0,6] |
| Demanda × 0,75 | 60 | 97,6 | 94,0 | 97,4 | 3,6 [2,7; 4,4] | 0,1 [−0,3; 0,5] |
| Demanda × 1,5 | 60 | 60,9 | 46,5 | 54,0 | 14,4 [13,0; 15,8] | 6,9 [5,5; 8,2] |
| Flota con un campero menos | 60 | 73,9 | 62,4 | 71,3 | 11,5 [10,2; 12,9] | 2,6 [1,1; 4,1] |
| Flota con dos camperos menos | 60 | 61,6 | 47,7 | 55,2 | 13,9 [12,5; 15,3] | 6,4 [4,9; 7,9] |
| Factor crítico 1 | 60 | 86,9 | 79,2 | 87,5 | 7,7 [6,3; 9,0] | −0,6 [−1,7; 0,6] |
| Factor crítico 5 | 60 | 86,9 | 79,2 | 87,5 | 7,7 [6,3; 9,0] | −0,6 [−1,8; 0,6] |

En la referencia, una jornada tiene en promedio 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres. La demanda × 0,75 baja a 99 pedidos y la demanda × 1,5 sube a 198. La flota baja a 7,0 vehículos con un campero menos y a 6,2 con dos menos. Ninguna de las 37.228 llamadas al optimizador terminó en error.

## 3. Qué conclusión aguanta y cuál no

**Aguanta: DespachoX le gana con claridad al despacho por orden de llegada en puntos críticos.** En las nueve variantes la diferencia es positiva y su intervalo queda lejos del cero. Va de 15,5 puntos, con la demanda × 0,75, a 69,4 puntos, con la demanda × 1,5. DespachoX fue mejor en las 60 semillas en siete variantes, y no fue peor en ninguna semilla de ninguna variante. La magnitud depende tanto del supuesto que una cifra suelta no describe el resultado. Cualquier número de esta comparación que vaya al pitch debe decir en qué escenario se midió.

**Aguanta: el perecedero vencido lo resuelve la regla de bodega.** DespachoX y la experta sacan primero lo que vence primero, y las dos quedan en 0,0 % en las 540 jornadas de cada una. La ingenua, que saca por orden de ingreso, pierde entre 1,0 % y 8,2 % en promedio, y en una jornada llegó al 26,4 %. Además, pasa la meta del 5 % del reto en tres variantes: la demanda × 1,5 y las dos flotas reducidas. Frente a la experta, el ruteo de DespachoX no añade nada medible en este indicador, porque las dos ya están en cero.

**Cambia: con las velocidades medidas, DespachoX le gana a la experta en puntos críticos, y la ventaja crece cuando el sistema se aprieta.** En la referencia le saca 3,2 puntos, con un intervalo de 2,1 a 4,4. La corrida de velocidades medidas de la rama `simulacion`, con 30 de estas mismas semillas, da 3,7 puntos, con un intervalo de 1,7 a 5,7. En cambio, en la corrida del 20 de noviembre, con las velocidades del modelo y la red urbana, los dos empataban (`docs/SIMULACION.md`, sección 8.3). Esa comparación no es pareada con esta, porque cambian la red y las velocidades. Si se ordenan las siete variantes con factor 3 por lo que cumple la ingenua, la ventaja sobre la experta crece a medida que la ingenua cumple menos. Hay una sola inversión, entre dos variantes casi empatadas, la demanda × 1,5 y la flota con dos camperos menos, donde la ingenua cumple el 29,2 % y el 29,6 %. En el extremo holgado, con la demanda × 0,75, la ingenua cumple el 83,8 % y la ventaja es de 0,9 puntos, con un intervalo que apenas se separa del cero. Con dos camperos menos llega a 12,3 puntos. Una lectura posible es que, con poca holgura, ordenar la cola por urgencia no basta y pesa más planear la ruta con el plazo de cada pedido, que es lo que hace el optimizador.

**No aguanta en general: la comparación con la experta en entregas a tiempo de todos los puntos.** En la referencia empatan, con −0,3 puntos y un intervalo de −1,4 a 0,9. DespachoX gana cuando el sistema se aprieta, por 1,8 puntos con la velocidad × 0,8, por 2,6 y 6,4 con uno y dos camperos menos y por 6,9 con la demanda × 1,5. Con la velocidad × 1,2 pierde 1,5 puntos, y el intervalo, de −2,5 a −0,6, queda entero del lado desfavorable. Así que la desventaja de cerca de 2 puntos que midió la corrida del 20 de noviembre reaparece cuando las vías son rápidas, y se invierte cuando escasean el tiempo o la flota.

**Aguanta: el factor crítico 3 hace falta para ganarle a la experta en críticos, y subirlo a 5 no añade nada.** Con factor 1, DespachoX empata con la experta (0,4 puntos, con el cero dentro del intervalo) y entrega a tiempo el 96,5 % de los críticos, frente al 99,3 % con factor 3. Con factor 5 queda como con 3, en el 99,4 %. Es lo mismo que mostró el barrido de la sección 8.2 de `docs/SIMULACION.md`. El factor no mueve las entregas a tiempo de todos los puntos.

**También aguantan tres resultados secundarios de la corrida del 20 de noviembre.** Recalcular aporta, porque DespachoX entrega a tiempo entre 9,3 y 52,0 puntos más de pedidos críticos que `optimiza_una_vez`, que usa el mismo optimizador una sola vez. La prioridad tiene un costo en equidad, ya que el punto peor atendido espera entre 1,05 y 3,69 horas más que con la ingenua. Y DespachoX recorre entre 22 y 66 km menos por jornada que la experta. En los tres casos el intervalo excluye el cero en las nueve variantes.

**Salvedades.** Las tres tablas suman 54 intervalos sin corrección por comparaciones múltiples, así que alguno puede excluir el cero por azar. Por eso las conclusiones de arriba se apoyan en patrones que se repiten en varias variantes y no en un intervalo aislado. Las variantes cambian un supuesto a la vez y no exploran combinaciones, por ejemplo vías lentas con flota corta. La demanda, la flota, los cierres y los plazos siguen siendo sintéticos, y ningún dato viene de una operación real del Banco de Alimentos ni de los organismos de socorro.

## 4. Línea base, escenarios y supuestos

**Líneas base.** Son las dos de `docs/SIMULACION.md`. La política `ingenua` atiende por orden de llegada, le asigna al pedido más antiguo el vehículo libre que llega más rápido, ordena las entregas por vecino más cercano y saca de bodega por orden de ingreso. La política `experta` es la ingenua con dos reglas de un despachador con oficio, que atiende primero lo más urgente y saca primero lo que vence primero. Las dos deciden al instante, mientras que cada plan de `despachox` espera 2 minutos la aprobación del despachador. También se corrió `optimiza_una_vez`, que no es línea base. Sus cifras están en `analisis/sensibilidad/resultados/resumen.md`.

**Escenarios.** Son 60 semillas, de 20261150 a 20261209, las mismas para las nueve variantes y las cuatro políticas. En total se simularon 2.160 jornadas, 540 por política.

**Supuestos.** Son los de la sección 6 de `docs/SIMULACION.md`, con dos cambios. La velocidad por tipo de vía y el factor por vehículo se reemplazan por las velocidades de `datos_publicos/velocidades.csv`. La red es la ampliada, `manizales_region.graphml`, que es la que usan hoy el producto y la simulación por defecto. Se mantienen los 3 a 8 cierres por jornada, el segundo de búsqueda por llamada al optimizador y la carga media de 2,5 pedidos por punto. El factor crítico de la referencia es 3, el valor por defecto de `despacho/optimizar.py`.

**Qué es medido y qué es supuesto.** Las cifras de las tablas son resultados de la simulación, medidos por nosotros sobre jornadas sintéticas. Las velocidades del bus vienen de una fuente. Aplicarlas al camión, al campero y a la moto, los multiplicadores de cada variante, la demanda, la flota, los cierres y los plazos son supuestos nuestros.

**De dónde salen las velocidades.** Una tesis de maestría de la UNAL Manizales (2019) midió con GPS un bus diésel en vías de la ciudad, por tipo de vía y por pendiente. `velocidades.csv` toma la media de esas mediciones para el camión, por ejemplo 23,3 km/h en vía primaria y 17,1 en terciaria. Darle al campero la misma velocidad y a la moto un 11 % más son supuestos del CSV, y también lo es asignar cada tipo de vía de OpenStreetMap a una clase de la tesis. El detalle y las fuentes están en `docs/datos/flota_perecederos_costos.md`, sección 3. Esas velocidades son mucho menores que las del modelo. Por ejemplo, en vía terciaria el campero pasa de 30,0 a 17,1 km/h, y en primaria de 38,2 a 23,3 km/h. La tabla completa está en `analisis/sensibilidad/verificacion_velocidades.md`. Ahí la media del modelo es el largo total entre el tiempo total de cada tipo de vía. `docs/datos/flota_perecederos_costos.md` usa otra media y da cifras algo mayores, por ejemplo 39,0 km/h en primaria.

## 5. Cómo se implementó cada variante

Todo se hizo desde `analisis/sensibilidad/`, sin editar `despacho/`. Cada tarea llama a `despacho.sim.correr.una_corrida` tal como está, con carga media, red y optimizador por defecto y 1 segundo de búsqueda. Las semillas son las de `--base 20261150` y el factor de la referencia es el de `--factor-critico 3`. Lo que la CLI no expone se cambia en memoria dentro de cada proceso.

Se usa esa función, que es la que corre cada semilla dentro de la CLI, en lugar de la CLI entera. La razón es técnica. En macOS los procesos hijos arrancan de cero (`spawn`) y no heredan los cambios hechos en memoria, así que el envoltorio arma su propio grupo de procesos y aplica la velocidad medida al arrancar cada uno.

| Variante | Qué se cambió y cómo |
|---|---|
| Velocidad medida (referencia, × 0,8 y × 1,2) | Para cada tramo, segundos = largo / (km/h del CSV para su tipo de vía y su vehículo × multiplicador). El cambio se aplica igual al mundo simulado, que reconstruye `red_sim.Red` desde el grafo, y al optimizador, al que se le reemplaza `despacho.matriz._red_del_tipo`. Se ignoran el `maxspeed` de OpenStreetMap y `FACTOR_TIEMPO`, porque el CSV ya trae una columna por vehículo. En las vías medidas el camión va igual que el campero. El tipo `ladder` (2 tramos, 0,1 km) no está en el CSV y conserva el supuesto del modelo. |
| Demanda × 0,75 y × 1,5 | `pedidos_por_punto` = 2,5 × multiplicador (1,875 y 3,75), aplicado después de `NIVELES_CARGA`, porque se pasa por el argumento `extra` de `una_corrida`, que pisa el nivel de carga. El inventario perecedero crece con la demanda, ya que la bodega tiene tantos kilos perecederos como piden los pedidos. La flota no cambia. |
| Flota con uno y dos vehículos menos | Se quitan camperos con `camperos_menos` = 1 y 2, el mismo parámetro de `--camperos-menos`. El generador deja al menos un campero, así que en las jornadas chicas la flota con dos menos es igual a la de uno menos. Pasó en 12 de las 60 jornadas, y por eso la flota media baja de 8,0 vehículos a 7,0 con uno menos y a 6,2 con dos menos. |
| Factor crítico 1 y 5 | La variable `DESPACHOX_FACTOR_CRITICO`, igual que `--factor-critico`. `ingenua` y `experta` no llaman al optimizador (usan `_asignar_fifo` de `despacho/sim/politicas.py`), así que no dependen del factor. Igual se volvieron a correr, y sus filas salieron idénticas a las de la referencia. |

**Verificación de la velocidad medida.** `python -m analisis.sensibilidad.verificar` comprueba tres cosas y deja el resultado en `analisis/sensibilidad/verificacion_velocidades.md`. La velocidad media por tipo de vía de la red parcheada coincide con el CSV, con diferencia de 0,000 km/h. La única excepción es el camión en vía residencial, que no puede usarla y solo pasa por tramos paralelos de otro tipo. Las matrices de tiempos de la simulación y del optimizador coinciden con 0,5 s de diferencia como máximo, que es el redondeo del optimizador, en 3 semillas, 3 multiplicadores y 3 vehículos. Escalar todas las velocidades por el mismo número no cambia los caminos más cortos, de modo que los puntos, los cierres, los pedidos y la flota de cada semilla quedan iguales en las tres variantes de velocidad.

**Contraste con la corrida de velocidades medidas de la rama `simulacion`.** Esa rama implementa por su cuenta la misma regla y corrió, entre otras, la carga media con las semillas 20261150 a 20261179 y factor 3 (commit `f52ea33`, `despacho/sim/resultados_velocidades/`). En esas 30 semillas, las filas de `ingenua` y `experta` de la referencia son idénticas a las suyas en las 30 jornadas. Esas dos políticas no dependen del reloj, así que la coincidencia indica que las dos implementaciones describen la misma ciudad. `despachox` coincide en 15 de las 30 jornadas y difiere en las demás por la búsqueda cortada por reloj. En promedio, la referencia da 0,6 puntos más de críticos a tiempo, 0,8 puntos más de entregas a tiempo en todos los puntos y 4 km menos.

## 6. Cómo reproducirlo

Desde la raíz del repositorio, con el grafo en `despacho/cache/`:

```
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.verificar
PY=python N=60 sh analisis/sensibilidad/correr_todo.sh
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.tabla --semillas 60
```

`correr_todo.sh` corre las tandas en orden y se puede cortar y volver a lanzar, porque cada tanda salta las tareas que ya están en `analisis/sensibilidad/resultados/<variante>/`. Una variante sola se corre así:

```
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.correr --variantes velocidad_x0.8 --desde 0 --semillas 60
```

Los datos por semilla quedan en `analisis/sensibilidad/resultados/<variante>/tanda_*.csv`, el registro de cada tanda en `tandas.txt` y la tabla completa, con todas las métricas, en `resultados/resumen.md`. La búsqueda del optimizador se corta por tiempo de reloj, así que repetir la corrida da cifras muy cercanas, pero no idénticas (`docs/SIMULACION.md`, sección 8.2).

## 7. Tiempo de cómputo

Antes de elegir el número de semillas se midió una tanda de la referencia. Siete semillas con las cuatro políticas, en 7 procesos, tardaron 114 s. Por semilla, `despachox` tardó entre 56 y 112 s, `optimiza_una_vez` entre 1,4 y 2,0 s, y `experta` e `ingenua` menos de 1 s. Una semilla de la referencia costaba así unos 85 s de proceso, unos 12 s de reloj con 7 procesos. A ese ritmo, 60 semillas de las nueve variantes cabían en unas dos horas de cómputo antes del plazo de las 4:30 a. m., y por eso se eligieron 60. Se corrieron en dos fases de 30, para tener temprano una tabla completa. La primera fue de 00:11 a 01:23 y la segunda de 01:23 a 02:34.

Por variante, la tarea de `despachox` tardó en promedio entre 63 s por semilla, con la demanda × 0,75, y 121 s, con la demanda × 1,5. En la referencia tardó 88 s. Llamó al optimizador entre 52 y 86 veces por jornada, a 1,20 a 1,38 s por llamada con 1 s de búsqueda.

## 8. Frase para el pitch (por aprobar)

La frase dice solo lo que sostienen todas las filas de las tablas. No menciona a la experta, porque esa ventaja depende del escenario y habría que decir cuál.

**Por aprobar.** «En nueve escenarios simulados que cambian la velocidad de las vías, la demanda, la flota y el peso de los puntos críticos, DespachoX entregó a tiempo, en promedio, más del 96 % de los pedidos críticos y no dejó vencer perecederos, mientras que el despacho por orden de llegada se quedó entre el 29 % y el 84 % en críticos.»
