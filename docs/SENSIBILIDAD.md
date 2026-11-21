# Sensibilidad de la simulación

Estado: corrida de la madrugada del sábado 21 de noviembre de 2026. Tuvo una revisión independiente y falta la del equipo.

**Estos números no son el resultado principal de la simulación.** Salen de una referencia propia de este análisis y sirven para ver si las conclusiones cambian cuando cambia un supuesto. El resultado principal sale de la corrida principal de `docs/SIMULACION.md`, que implementa por su cuenta las velocidades medidas. Por eso la fila de referencia de este documento puede no coincidir con su cifra. En las 30 semillas que comparte con la corrida de velocidades medidas de la rama `simulacion`, las líneas base dan cifras idénticas y DespachoX cifras muy cercanas (sección 5).

## 1. Qué pregunta responde

La simulación de `docs/SIMULACION.md` compara cuatro formas de despachar la misma jornada. Varios de sus supuestos son nuestros, entre ellos la velocidad de las vías, la demanda y el tamaño de la flota. El peso que el optimizador les da a los puntos críticos, en cambio, es un parámetro de DespachoX que fijamos nosotros. Este análisis cambia esos cuatro valores uno a uno y mide si DespachoX conserva su ventaja en los dos indicadores del reto, los pedidos críticos entregados a tiempo y el perecedero vencido.

Cada variante cambia un solo valor respecto de la referencia. La referencia usa la velocidad medida en Manizales, la carga media, la flota completa y el factor crítico 3. Todas las variantes usan las mismas 60 semillas, así que cada diferencia se calcula jornada por jornada.

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

En la demanda × 0,75, el límite inferior frente a la experta se imprime 0,0 porque la tabla usa un decimal. Vale 0,02 (`analisis/sensibilidad/resultados/tabla.csv`), así que el intervalo no llega a tocar el cero.

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

**Aguanta: el perecedero vencido lo resuelve la regla de bodega.** DespachoX y la experta sacan primero lo que vence primero, y las dos quedan en 0,0 % en las 540 jornadas de cada una. La ingenua, que saca por orden de ingreso, pierde entre 1,0 % y 8,2 % en promedio, y en una jornada llegó al 26,4 %. Además, pasa la meta del 5 % del reto en tres variantes, la demanda × 1,5 y las dos flotas reducidas. Frente a la experta, el ruteo de DespachoX no añade nada medible en este indicador, porque las dos ya están en cero.

**Cambia: en esta referencia (red ampliada, velocidades medidas y factor 3), DespachoX le gana a la experta en puntos críticos, y la ventaja crece cuando el sistema se aprieta.** En la referencia le saca 3,2 puntos, con un intervalo de 2,1 a 4,4. La corrida de velocidades medidas de la rama `simulacion`, con 30 de estas mismas semillas, da 3,7 puntos, con un intervalo de 1,7 a 5,7. En cambio, en la corrida del 20 de noviembre los dos empataban (`docs/SIMULACION.md`, sección 8.3). Esa corrida usó la red urbana y las velocidades del modelo, así que frente a ella cambian dos cosas a la vez y la comparación no es pareada.

Falta separar el efecto de la red del de las velocidades. Con factor 1, DespachoX empata con la experta en la red ampliada con los dos juegos de velocidades. Con las velocidades del modelo, la diferencia es de −0,8 puntos, con un intervalo de −1,9 a 0,3 (`docs/SIMULACION.md`, sección 8.8, con otras semillas). Con las medidas, es de 0,4 puntos, con un intervalo de −1,0 a 1,9 (variante de factor 1). Con factor 3, en cambio, no hay todavía una corrida de la red ampliada con las velocidades del modelo. Lo dirá la corrida principal, y hasta entonces la ventaja de esta referencia no se puede atribuir a las velocidades medidas.

Dentro de este análisis, la ventaja sobre la experta crece a medida que la ingenua cumple menos. Para verlo se ordenan las siete variantes con factor 3 por lo que cumple la ingenua en críticos. En el extremo holgado, con la demanda × 0,75, la ingenua cumple el 83,8 % y la ventaja es de 0,9 puntos, con un intervalo de 0,02 a 1,8, que apenas se separa del cero. Con dos camperos menos, la ingenua cumple el 29,6 % y la ventaja llega a 12,3 puntos. El orden se rompe una sola vez, con la demanda × 1,5. Ahí la ingenua cumple el 29,2 %, casi lo mismo que con dos camperos menos, y la ventaja es de 10,5 puntos. Una lectura posible es que, con poca holgura, ordenar la cola por urgencia no basta y pesa más planear la ruta con el plazo de cada pedido, que es lo que hace el optimizador.

**No aguanta en general: la ventaja de la experta en entregas a tiempo de todos los puntos.** En la corrida del 20 de noviembre, la experta le ganaba a DespachoX por cerca de 2 puntos en este indicador (`docs/SIMULACION.md`, sección 7). En esta referencia empatan, con −0,3 puntos y un intervalo de −1,4 a 0,9. También empatan con la demanda × 0,75 y con los factores 1 y 5. DespachoX gana cuando el sistema se aprieta, por 1,8 puntos con la velocidad × 0,8, por 2,6 y 6,4 con uno y dos camperos menos y por 6,9 con la demanda × 1,5. La desventaja solo reaparece con la velocidad × 1,2, donde DespachoX pierde 1,5 puntos, con un intervalo de −2,5 a −0,6.

**Con factor 1, DespachoX empata con la experta en críticos. Con 3 le gana, y con 5 queda igual que con 3.** Con factor 1 la diferencia es de 0,4 puntos, con el cero dentro del intervalo, y DespachoX entrega a tiempo el 96,5 % de los críticos. Con factor 3 entrega el 99,3 %, y con factor 5, el 99,4 %. Como solo se probaron 1, 3 y 5, la tabla muestra que hace falta un factor mayor que 1, pero no cuál es el mejor. El barrido de la sección 8.2 de `docs/SIMULACION.md` dio el mismo patrón con la red urbana y las velocidades del modelo. En cambio, la confirmación de la sección 8.3, con la red urbana y semillas que no intervinieron en la elección del 3, no sostuvo la ventaja en críticos. En carga media fue de 1,7 puntos, con un intervalo de −0,7 a 4,0. Aquí sí aparece, con la red ampliada y las velocidades medidas. En entregas a tiempo de todos los puntos, DespachoX empata con la experta con los tres factores.

**También aguantan tres resultados secundarios de la corrida del 20 de noviembre.** Recalcular aporta, porque DespachoX entrega a tiempo entre 9,3 y 52,0 puntos más de pedidos críticos que `optimiza_una_vez`, que usa el mismo optimizador una sola vez. La prioridad tiene un costo en equidad, ya que el punto peor atendido espera entre 1,05 y 3,70 horas más que con la ingenua. Y DespachoX recorre entre 22 y 66 km menos por jornada que la experta. En los tres casos el intervalo excluye el cero en las nueve variantes.

**Salvedades.** Las tres tablas suman 54 intervalos sin corrección por comparaciones múltiples, así que alguno puede excluir el cero por azar. Por eso las conclusiones de arriba se apoyan en patrones que se repiten en varias variantes y no en un intervalo aislado. Las variantes cambian un supuesto a la vez y no exploran combinaciones, por ejemplo vías lentas con flota corta. La demanda, la flota, los cierres y los plazos siguen siendo sintéticos, y ningún dato viene de una operación real del Banco de Alimentos ni de los organismos de socorro.

## 4. Línea base, escenarios y supuestos

**Líneas base.** Son las dos de `docs/SIMULACION.md`. La política `ingenua` atiende por orden de llegada, le asigna al pedido más antiguo el vehículo libre que llega más rápido, ordena las entregas por vecino más cercano y saca de bodega por orden de ingreso. La política `experta` es la ingenua con dos reglas de un despachador con oficio, que atiende primero lo más urgente y saca primero lo que vence primero. Las dos deciden al instante, mientras que cada plan de `despachox` espera 2 minutos la aprobación del despachador. También se corrió `optimiza_una_vez`, que no es línea base. Sus cifras están en `analisis/sensibilidad/resultados/resumen.md`.

**Escenarios.** Son 60 semillas, de 20261150 a 20261209, las mismas para las nueve variantes y las cuatro políticas. En total se simularon 2.160 jornadas, 540 por política.

**Supuestos.** Son los de la sección 6 de `docs/SIMULACION.md`, con dos cambios. La velocidad por tipo de vía y el factor por vehículo se reemplazan por las velocidades de `datos_publicos/velocidades.csv`. La red es la ampliada, `manizales_region.graphml`, que es la que usan hoy el producto y la simulación por defecto. Se mantienen los 3 a 8 cierres por jornada, el segundo de búsqueda por llamada al optimizador y la carga media de 2,5 pedidos por punto. El factor crítico de la referencia es 3, el valor por defecto de `despacho/optimizar.py`.

**Qué es medido y qué es supuesto.** Las cifras de las tablas son resultados de la simulación, medidos por nosotros sobre jornadas sintéticas. Las velocidades del bus vienen de una fuente. Aplicarlas al camión, al campero y a la moto, los multiplicadores de cada variante, la demanda, la flota, los cierres y los plazos son supuestos nuestros.

**De dónde salen las velocidades.** Una tesis de maestría de la UNAL Manizales (2019) midió con GPS un bus a combustión en vías de la ciudad, por tipo de vía y por pendiente. `velocidades.csv` toma la media de esas mediciones para el camión, por ejemplo 23,3 km/h en vía primaria y 17,1 en terciaria. Darle al campero la misma velocidad y a la moto un 11 % más son supuestos del CSV, y también lo es asignar cada tipo de vía de OpenStreetMap a una clase de la tesis. El detalle y las fuentes están en `docs/datos/flota_perecederos_costos.md`, sección 3.

**Cuánto cambian frente al modelo.** Para el campero, las velocidades medidas son mucho menores que las del modelo en las vías troncales, primarias, secundarias y terciarias. Por ejemplo, en vía terciaria pasa de 30,0 a 17,1 km/h, y en primaria de 38,2 a 23,3 km/h. En esos cuatro tipos de vía el camión baja menos, porque el modelo ya le daba 1,25 veces el tiempo del campero. En cambio, en las vías residenciales la medida del campero es algo mayor, 21,9 frente a 20,0 km/h. En las no clasificadas baja poco, de 25,2 a 21,9 km/h, y la del camión sube de 20,2 a 21,9. Esos dos tipos suman el 70 % de los kilómetros del grafo.

**Cómo se promedian.** La tabla completa, con los tres vehículos, está en `analisis/sensibilidad/verificacion_velocidades.md`. Ahí la media del modelo es el largo total entre el tiempo total de cada tipo de vía. `docs/datos/flota_perecederos_costos.md` usa otra media y da cifras iguales o mayores. La diferencia es grande en las troncales, con 54,7 km/h frente a 47,8, y pequeña en las demás, por ejemplo 39,0 frente a 38,2 en primaria.

## 5. Cómo se implementó cada variante

Todo se hizo desde `analisis/sensibilidad/`, sin editar `despacho/`. Cada tarea llama a `despacho.sim.correr.una_corrida` tal como está, con carga media, red y optimizador por defecto y 1 segundo de búsqueda. Las semillas son las de `--base 20261150` y el factor de la referencia es el de `--factor-critico 3`. Lo que la CLI no expone se cambia en memoria dentro de cada proceso.

En macOS los procesos hijos arrancan de cero (`spawn`) y no heredan los cambios hechos en memoria. Por eso se llama a esa función, que es la que corre cada semilla dentro de la CLI, en lugar de usar la CLI entera. El envoltorio arma su propio grupo de procesos y aplica la velocidad medida al arrancar cada uno.

| Variante | Qué se cambió y cómo |
|---|---|
| Velocidad medida (referencia, × 0,8 y × 1,2) | Para cada tramo, segundos = largo / (km/h del CSV para su tipo de vía y su vehículo × multiplicador). El cambio se aplica igual al mundo simulado, que reconstruye `red_sim.Red` desde el grafo, y al optimizador, al que se le reemplaza `despacho.matriz._red_del_tipo`. Se ignoran el `maxspeed` de OpenStreetMap y `FACTOR_TIEMPO`, porque el CSV ya trae una columna por vehículo. En las vías medidas el camión va igual que el campero. El tipo `ladder` (2 tramos, 0,1 km) no está en el CSV y conserva el supuesto del modelo. |
| Demanda × 0,75 y × 1,5 | `pedidos_por_punto` = 2,5 × multiplicador (1,875 y 3,75), aplicado después de `NIVELES_CARGA`, porque se pasa por el argumento `extra` de `una_corrida`, que pisa el nivel de carga. El inventario perecedero crece con la demanda, ya que la bodega tiene tantos kilos perecederos como piden los pedidos. La flota no cambia. |
| Flota con uno y dos vehículos menos | Se quitan camperos con `camperos_menos` = 1 y 2, el mismo parámetro de `--camperos-menos`. El generador deja al menos un campero, así que en las jornadas chicas la flota con dos menos es igual a la de uno menos. Pasó en 12 de las 60 jornadas, y por eso la flota media baja de 8,0 vehículos a 7,0 con uno menos y a 6,2 con dos menos. |
| Factor crítico 1 y 5 | La variable `DESPACHOX_FACTOR_CRITICO`, igual que `--factor-critico`. `ingenua` y `experta` no llaman al optimizador (usan `_asignar_fifo` de `despacho/sim/politicas.py`), así que no dependen del factor. Igual se volvieron a correr, y sus filas salieron idénticas a las de la referencia. |

**Verificación de la velocidad medida.** `python -m analisis.sensibilidad.verificar` comprueba tres cosas y deja el resultado en `analisis/sensibilidad/verificacion_velocidades.md`. La velocidad media por tipo de vía de la red parcheada coincide con el CSV, con diferencia de 0,000 km/h. La única excepción es el camión en vía residencial, que no puede usarla y solo pasa por tramos paralelos de otro tipo. Las matrices de tiempos de la simulación y del optimizador coinciden con 0,5 s de diferencia como máximo, que es el redondeo del optimizador, en 3 semillas, 3 multiplicadores y 3 vehículos. Escalar todas las velocidades por el mismo número no cambia los caminos más cortos, de modo que los puntos, los cierres, los pedidos y la flota de cada semilla quedan iguales en las tres variantes de velocidad.

**Contraste con la corrida de velocidades medidas de la rama `simulacion`.** Esa rama implementa por su cuenta la misma regla y corrió, entre otras, la carga media con las semillas 20261150 a 20261179 y factor 3 (commit `f52ea33`, `despacho/sim/resultados_velocidades/`). En esas 30 semillas, las filas de `ingenua` y `experta` de la referencia son idénticas a las suyas en las 30 jornadas. Esas dos políticas no dependen del reloj, así que la coincidencia indica que las dos implementaciones describen la misma ciudad. `despachox` coincide en 15 de las 30 jornadas y difiere en las demás, probablemente por la búsqueda cortada por reloj. No se descarta otra causa, porque las dos ramas arman de forma distinta la matriz que recibe el optimizador. En promedio, la referencia da 0,6 puntos más de críticos a tiempo, 0,8 puntos más de entregas a tiempo en todos los puntos y 4 km menos.

## 6. Cómo reproducirlo

Hace falta el grafo en `despacho/cache/` y la orden `timeout`, de GNU coreutils. En macOS se instala con `brew install coreutils`, y sin ella `correr_todo.sh` se detiene antes de empezar. Desde la raíz del repositorio:

```
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.verificar
PY=python N=60 sh analisis/sensibilidad/correr_todo.sh
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.tabla --semillas 60
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.repetir
```

`correr_todo.sh` corre las tandas en orden y al final arma la tabla. Cada tanda deja de arrancar tareas a los 300 s, y `timeout` la corta a los 480 s. Si la corta, las filas terminadas ya están en disco y la tanda siguiente completa el resto, aunque la tanda cortada no deja su línea en `tandas.txt`. La tercera orden rehace solo la tabla, y la cuarta repite las tandas sin versionar (sección 7).

El script se puede cortar y volver a lanzar, porque cada tanda salta las tareas que ya están en `analisis/sensibilidad/resultados/<variante>/`. Por lo mismo, para repetir todo desde cero hay que apartar antes esa carpeta, por ejemplo con `mv analisis/sensibilidad/resultados analisis/sensibilidad/resultados_previos`. Si no se aparta, todas las tandas dicen «0 tareas pendientes» y solo se rehace la tabla. Con 7 procesos, las tandas de esta corrida sumaron unas 2,2 horas, así que una repetición completa debería tomar algo más de dos horas.

Una variante sola se corre así:

```
DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.correr --variantes velocidad_x0.8 --desde 0 --semillas 60
```

Los datos por semilla quedan en `analisis/sensibilidad/resultados/<variante>/tanda_*.csv`, el registro de cada tanda en `tandas.txt` y la tabla completa, con todas las métricas, en `resultados/resumen.md`. La búsqueda del optimizador se corta por tiempo de reloj, así que repetir la corrida puede cambiar algunas jornadas de `optimiza_una_vez` y `despachox` (`docs/SIMULACION.md`, sección 8.2).

## 7. Tiempo de cómputo

Antes de elegir el número de semillas se midió una tanda de la referencia. Siete semillas con las cuatro políticas, en 7 procesos, tardaron 114 s. Por semilla, `despachox` tardó entre 56 y 112 s, `optimiza_una_vez` entre 1,4 y 2,0 s, y `experta` e `ingenua` menos de 1 s. Una semilla de la referencia costaba así unos 85 s de proceso, unos 12 s de reloj con 7 procesos. A ese ritmo, 60 semillas de las nueve variantes cabían en unas dos horas de cómputo antes del plazo de las 4:30 a. m., y por eso se eligieron 60. Se corrieron en dos fases de 30, para tener temprano una tabla completa. La primera fue de 00:11 a 01:23 y la segunda de 01:23 a 02:34.

Por variante, la tarea de `despachox` tardó en promedio entre 63 s por semilla, con la demanda × 0,75, y 121 s, con la demanda × 1,5. En la referencia tardó 88 s. Llamó al optimizador entre 52 y 86 veces por jornada, a 1,20 a 1,38 s por llamada con 1 s de búsqueda.

Las tandas registradas duraron entre 114 y 499 s. La de la 01:23 pasó de los 8 minutos que se habían fijado por tanda, y por eso `correr_todo.sh` corta ahora cada tanda a los 480 s.

**Tandas con el envoltorio sin versionar.** Las tandas de las 00:11 a las 00:52 corrieron antes de que el envoltorio entrara al repositorio, en el commit 1e74acc. Por eso su línea de `tandas.txt` registra el commit 7131261, que es el de `main` del que sale la rama. De ellas salen las semillas 20261150 a 20261179 de la referencia, de las dos demandas y de las dos flotas, y las semillas 20261150 a 20261165 de la velocidad × 0,8. Para comprobar que el código era el mismo, `python -m analisis.sensibilidad.repetir` volvió a correr esas tareas con el código versionado (commit 89a65f0). Las 332 filas de `ingenua` y `experta` salieron idénticas. También salieron idénticas 163 de las 166 filas de `optimiza_una_vez` y las 7 de `despachox` que se repitieron, que son las semillas 20261150 a 20261156 de la referencia. Las otras 3 de `optimiza_una_vez` difieren, probablemente porque su búsqueda se corta por reloj. En dos repeticiones anteriores con el mismo código de simulación fueron 6, y solo dos coinciden con las de ahora. El detalle está en `analisis/sensibilidad/resultados/repeticion.md` y en `resultados/repeticion/repeticiones_previas.txt`.

## 8. Frase para el pitch (por aprobar)

La frase dice solo lo que sostienen todas las filas de las tablas 2.1 y 2.2. En críticos no se compara con la experta, porque esa ventaja depende de la variante y todavía no se puede atribuir a las velocidades medidas (sección 3). En el perecedero reconoce que un despachador con la misma regla de bodega logra lo mismo, porque la experta también queda en 0,0 %.

**Por aprobar.** «Probamos nueve variantes de la simulación, con 60 jornadas sintéticas cada una. Cada una cambia un solo valor, sea la velocidad de las vías, la demanda, la flota o el peso que DespachoX les da a los puntos críticos. En todas, DespachoX entregó a tiempo en promedio más del 96 % de los pedidos críticos, frente al 29 % a 84 % del despacho por orden de llegada. Igual que un despachador que saca primero lo que vence primero, no dejó vencer perecederos.»

Si se aprueba, la frase necesita su fila en `docs/FUENTES.md`, de tipo M, con fuente en las tablas 2.1 y 2.2 de este documento.
