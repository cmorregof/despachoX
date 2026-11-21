# Simulación: cuánto mejora DespachoX frente a un despacho sin optimizador

Estado: resultados de la primera corrida y de la segunda ronda (sección 8), del 20 de noviembre de 2026, y de la corrida con las velocidades de la tesis UNAL de 2019 (sección 9), de la noche del 20 al 21. Sin revisar todavía por el equipo.

Código en `despacho/sim/`. Se reproduce con `python -m despacho.sim.correr --carga todas`.

## 1. Qué pregunta responde

La ficha del reto fija dos indicadores: el porcentaje de entregas a tiempo en puntos críticos y el desperdicio de perecederos, que debe quedar por debajo del 5 %. La simulación mide esos dos indicadores para cuatro formas de despachar la misma jornada, con los mismos pedidos, la misma flota y los mismos cierres viales. La diferencia entre ellas es lo que se le puede atribuir a DespachoX.

## 2. Diseño

**Red.** El grafo de conducción de Manizales y Villamaría de OpenStreetMap, el mismo archivo que usa el optimizador (`despacho/cache/manizales.graphml`). La simulación aplica las velocidades y las reglas de acceso de `despacho/red.py` y `despacho/matriz.py`, de modo que el plan y la jornada simulada describen la misma ciudad. Una prueba compara las dos matrices de tiempos y falla si difieren en más de un segundo.

**Escenario.** Cada semilla genera una jornada completa:

- Entre 30 y 80 puntos de entrega sobre nodos de la red, a 6 km del centro como máximo y separados al menos 250 m. El 20 % son críticos.
- Un acopio, sobre la vía apta para camión más cercana a la plaza de Bolívar.
- Pedidos: el 40 % ya está en cola al empezar y el resto llega en momentos uniformes durante las primeras 8 horas. Cada pedido atiende entre 3 y 50 familias, a 12 kg por familia, y entre el 20 % y el 50 % de su peso es perecedero.
- Urgencia y plazo: los puntos críticos piden con urgencia 3 el 80 % de las veces. El plazo de entrega es de 3 horas para urgencia 3, 5 horas para urgencia 2 y 8 horas para urgencia 1.
- Inventario perecedero: tantos kilos como piden los pedidos, en lotes de 100 a 400 kg que vencen entre 6 y 48 horas después del inicio.
- Flota mixta: un camión de 3.000 kg por cada 30 puntos, un campero de 700 kg por cada 15 y una moto de 60 kg por cada 20.
- Cierres: entre 3 y 8 tramos cerrados por jornada, en los dos sentidos. El 30 % existe desde la hora cero y los demás ocurren durante las primeras 8 horas. Cada cierre bloquea siempre al camión, al campero con probabilidad 0,7 y a la moto con probabilidad 0,3. No se levantan durante la jornada.

**Cómo se conoce un cierre.** Nadie lo sabe hasta que un vehículo intenta pasar. El conductor pierde 3 minutos, reporta y se desvía. El reporte desvía también a los vehículos que iban hacia ese tramo, en todas las políticas. El despacho confirma el cierre 5 minutos después del reporte.

**Motor.** Simulador de eventos discretos. Los vehículos avanzan tramo a tramo por la red verdadera, mientras que los caminos se calculan con la red conocida, que no incluye los cierres sin reportar. El motor impone tres reglas a cualquier política: ningún vehículo carga más que su capacidad, un kilo perecedero que llega después del vencimiento de su lote no cuenta como entregado, y un cierre desconocido no cambia ninguna ruta. Las tres están cubiertas por pruebas en `despacho/sim/tests/`.

**Jornada.** La simulación se corta a las 14 horas. Lo que no se entregó para entonces cuenta como no entregado.

## 3. Políticas comparadas

| Política | Qué hace |
|---|---|
| `ingenua` | Atiende por orden de llegada. Al pedido más antiguo le asigna el vehículo libre que llega más rápido y lo llena con los siguientes pedidos de la cola. El conductor ordena sus entregas por vecino más cercano. Saca los lotes de bodega por orden de ingreso. Se desvía solo al toparse un cierre. |
| `experta` | La ingenua con dos reglas de un despachador con oficio: atiende primero lo más urgente y saca de bodega primero lo que vence primero. |
| `optimiza_una_vez` | El optimizador planea al inicio con los pedidos que hay y no vuelve a calcular. Lo demás se atiende con la regla ingenua. |
| `despachox` | El optimizador planea al inicio y recalcula con cada cierre confirmado, con cada tanda de pedidos (cada 30 minutos) y cada vez que un vehículo vuelve al acopio. |

La política `experta` no estaba en el encargo. Se añadió porque un despachador real no ignora la urgencia, y porque la literatura muestra que una política intuitiva puede quedar cerca del óptimo (Cook y Lodree, 2017). La comparación de `optimiza_una_vez` con `despachox` aísla lo que aporta recalcular.

**El optimizador** es el de `despacho/optimizar.py`: OR-Tools con capacidad, una red por tipo de vehículo, ventana dura hasta el vencimiento del perecedero, retraso ponderado por urgencia y penalización por pedido sin atender. La simulación llama a su modelo con un límite de búsqueda de 1 segundo por llamada. El modelo planea un viaje por vehículo y solo asigna pedidos nuevos a los vehículos que están en el acopio, por eso `despachox` lo vuelve a llamar cuando un vehículo regresa.

**Ventajas que se le dieron a la línea base.** Decide al instante, mientras que cada plan del optimizador espera 2 minutos la aprobación del despachador y solo se revisa un plan a la vez. Ve cada pedido apenas llega, mientras que `despachox` lo ve en la siguiente tanda o cuando regresa un vehículo. Sus conductores reciben el aviso de cada cierre igual que los de DespachoX. Su tope de paradas por viaje se eligió con semillas de calibración, distintas de las de evaluación, y se dejó en el valor que mejor le fue, que es no tener tope.

## 4. Métricas y estadística

- **Entregas a tiempo en puntos críticos:** pedidos de puntos críticos entregados antes de su hora límite, sobre el total de pedidos de puntos críticos. Un pedido sin entregar cuenta como tarde.
- **Perecederos vencidos:** kilos de lotes que vencen dentro de la jornada y no se entregaron antes de vencer, sobre el total de kilos perecederos en bodega. Incluye lo que venció en bodega, a bordo o al llegar tarde.
- Además: entregas a tiempo en todos los puntos, pedidos entregados, kilos que no llegaron en buen estado, tiempo medio y máximo del pedido a la entrega, espera media en el punto peor atendido, kilómetros de la flota y segundos de cada llamada al optimizador.

Cada nivel de carga se corre con 30 semillas (20261120 a 20261149), las mismas para todas las políticas. Se reporta la diferencia pareada por semilla con su intervalo de confianza del 95 % (t de Student, 29 grados de libertad) y el número de semillas en que cada política gana, empata o pierde.

**Niveles de carga.** La demanda se fija en 2, 2,5 o 3 pedidos por punto en la jornada (carga holgada, media y alta). Los niveles se eligieron con las semillas de calibración 100 a 111, mirando solo a la política ingenua: cumple cerca del 86 %, el 74 % y el 52 % de los pedidos críticos a tiempo. Con una demanda menor todas las políticas entregan casi todo a tiempo y la comparación no mide nada.

## 5. Resultados

Corrida del 20 de noviembre de 2026, commit `d33dd27`: 30 semillas por nivel de carga, 360 jornadas simuladas en total. Ninguna llamada al optimizador terminó en error. La tabla completa, con todas las métricas y todas las comparaciones, está en `despacho/sim/resultados/resumen.md`, y los datos por semilla en `despacho/sim/resultados/resultados.csv`. Las cifras de abajo se copiaron de ahí sin cambios.

Los escenarios tienen en promedio 56 puntos, 8,3 vehículos y 5,0 cierres. La carga holgada son 111 pedidos y 35,3 t, la media 138 pedidos y 44,1 t, y la alta 166 pedidos y 52,8 t.

### Medias por política (desviación estándar entre semillas)

| Carga | Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---|---:|---:|---:|---:|
| Holgada | Críticos a tiempo (%) | 87,7 (12,2) | 99,5 (1,8) | 93,0 (8,3) | 99,7 (1,2) |
| Holgada | Perecederos vencidos (%) | 0,5 (1,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Holgada | A tiempo, todos los puntos (%) | 96,4 (3,0) | 99,3 (1,2) | 98,0 (2,1) | 99,3 (1,7) |
| Holgada | Espera en el punto peor atendido (h) | 4,06 (0,93) | 5,13 (1,45) | 4,00 (1,27) | 4,99 (1,46) |
| Holgada | Kilómetros de la flota | 703,8 (241,5) | 707,9 (240,9) | 677,5 (227,9) | 632,8 (208,4) |
| Media | Críticos a tiempo (%) | 69,1 (15,7) | 98,5 (2,6) | 80,6 (14,0) | 98,1 (3,1) |
| Media | Perecederos vencidos (%) | 1,8 (1,9) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Media | A tiempo, todos los puntos (%) | 89,4 (5,9) | 95,6 (5,3) | 93,5 (4,5) | 93,8 (5,8) |
| Media | Espera en el punto peor atendido (h) | 5,00 (1,13) | 7,09 (1,88) | 4,88 (0,94) | 7,27 (1,78) |
| Media | Kilómetros de la flota | 836,5 (304,2) | 834,3 (297,9) | 802,6 (282,6) | 778,9 (269,0) |
| Alta | Críticos a tiempo (%) | 49,6 (17,5) | 97,6 (3,7) | 60,1 (17,6) | 95,9 (4,2) |
| Alta | Perecederos vencidos (%) | 3,5 (2,4) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Alta | A tiempo, todos los puntos (%) | 78,3 (9,3) | 85,9 (8,2) | 82,3 (9,1) | 83,7 (7,1) |
| Alta | Espera en el punto peor atendido (h) | 5,83 (1,24) | 9,12 (1,76) | 5,80 (1,26) | 10,08 (1,34) |
| Alta | Kilómetros de la flota | 1004,9 (360,9) | 1000,3 (361,3) | 976,3 (340,3) | 953,6 (325,3) |

El optimizador tardó entre 1,20 y 1,31 segundos por llamada en promedio, con un máximo medio de 1,45 segundos, y `despachox` lo llamó entre 55 y 82 veces por jornada. El límite de búsqueda fue de 1 segundo.

### Diferencias pareadas de DespachoX (puntos porcentuales o kilómetros, con IC del 95 %)

| Comparación | Indicador | Holgada | Media | Alta |
|---|---|---|---|---|
| `despachox` − `ingenua` | Críticos a tiempo | 12,0 [7,5; 16,5] | 28,9 [23,2; 34,7] | 46,3 [40,0; 52,6] |
| `despachox` − `ingenua` | Perecederos vencidos | −0,5 [−0,9; −0,1] | −1,8 [−2,6; −1,1] | −3,5 [−4,4; −2,6] |
| `despachox` − `ingenua` | A tiempo, todos los puntos | 2,9 [2,1; 3,7] | 4,4 [3,1; 5,7] | 5,4 [4,0; 6,8] |
| `despachox` − `ingenua` | Espera en el punto peor atendido (h) | 0,93 [0,52; 1,35] | 2,27 [1,61; 2,94] | 4,25 [3,67; 4,84] |
| `despachox` − `experta` | Críticos a tiempo | 0,2 [−0,6; 1,1] | −0,5 [−1,8; 0,9] | −1,8 [−3,6; 0,0] |
| `despachox` − `experta` | Perecederos vencidos | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| `despachox` − `experta` | A tiempo, todos los puntos | −0,1 [−0,5; 0,4] | −1,8 [−2,7; −1,0] | −2,2 [−3,7; −0,8] |
| `despachox` − `experta` | Kilómetros de la flota | −75,1 [−92,8; −57,4] | −55,5 [−73,1; −37,9] | −46,7 [−72,2; −21,2] |
| `despachox` − `optimiza_una_vez` | Críticos a tiempo | 6,7 [3,7; 9,7] | 17,5 [12,4; 22,5] | 35,7 [29,5; 42,0] |

### Lectura

**Frente al despacho por orden de llegada, DespachoX gana con claridad en puntos críticos.** La diferencia es de 12, 29 y 46 puntos porcentuales según la carga, y el intervalo nunca toca el cero. En carga alta DespachoX fue mejor en las 30 semillas.

**Frente a un despachador con oficio, DespachoX no gana en los indicadores del reto.** La política `experta` empata con DespachoX en puntos críticos en carga holgada y media. En carga alta queda 1,8 puntos por encima, con un intervalo que llega justo al cero. En entregas a tiempo de todos los puntos, `experta` es mejor en carga media y alta, por 1,8 y 2,2 puntos, y ahí el intervalo sí excluye el cero. Lo que DespachoX le gana a `experta` son kilómetros: entre 47 y 75 km menos por jornada, del 5 % al 11 % del recorrido.

**El desperdicio de perecederos lo resuelve la regla de bodega, no el ruteo.** Toda política que saca primero lo que vence primero queda en 0,0 %. La política ingenua, que saca por orden de ingreso, pierde 0,5 %, 1,8 % y 3,5 %. Incluso ella queda en promedio por debajo del 5 % de la meta del reto en estos escenarios.

**Recalcular aporta.** Con el mismo optimizador, recalcular sube los críticos a tiempo en 7, 18 y 36 puntos frente a planear una sola vez. Esa comparación tiene una salvedad: `optimiza_una_vez` atiende con la regla ingenua todo lo que llega después del plan inicial, de modo que la diferencia mezcla el efecto de recalcular con el de priorizar los pedidos nuevos.

**La prioridad tiene un costo en equidad.** DespachoX y `experta` hacen esperar más al punto peor atendido que la política ingenua: 2,3 horas más en carga media y 4,3 horas más en carga alta, en el caso de DespachoX. Atender primero lo crítico deja para el final a los puntos de baja urgencia.

## 6. Supuestos

Todos son supuestos nuestros, no datos medidos, salvo el trazado de la red vial.

| Supuesto | Valor |
|---|---|
| Velocidad por tipo de vía | La de `despacho/red.py`: 40 km/h en vía primaria, 35 en secundaria, 30 en terciaria, 20 en residencial, o el `maxspeed` de OpenStreetMap si existe |
| Factor por vehículo | Camión 1,25 veces el tiempo base, campero 1,0, moto 0,9 |
| Acceso del camión | No entra a vías residenciales ni de servicio. Atiende un punto si hay una vía apta a 300 m o menos |
| Vehículo sin regreso por su red | Sale por cualquier vía de conducción, también en contravía, al doble del tiempo |
| Vehículo sin ningún regreso | Sale de servicio, su carga se pierde y sus pedidos vuelven a la cola |
| Tiempo de carga en el acopio | 10 minutos por viaje |
| Tiempo por entrega | 10 minutos, igual que en el optimizador |
| Tiempo perdido al toparse un cierre | 3 minutos |
| Confirmación humana de un cierre | 5 minutos |
| Aprobación humana de un plan | 2 minutos, un plan a la vez |
| Tanda de pedidos | cada 30 minutos |
| Extracción de pedidos y cierres por el modelo de lenguaje | sin errores |
| Pedidos | no se parten entre vehículos |
| Inventario no perecedero | ilimitado |
| Acopios | uno solo |
| Demanda, flota, inventario y cierres | sintéticos |

Los cierres se sortean entre los tramos que usan los caminos más cortos del acopio a los puntos, con probabilidad proporcional al número de caminos que pasan por cada uno. Se hizo así porque un cierre en una calle que ningún vehículo usa no pone a prueba a ninguna política. La consecuencia es que los cierres de la simulación estorban más que cierres sorteados al azar sobre toda la red.

## 7. Lo que esta simulación no prueba

Actualizada el 20 de noviembre de 2026 con la segunda ronda (sección 8).

- **No prueba que DespachoX supere a un buen despachador humano cuando la información es perfecta.** Con la red urbana y las velocidades del modelo (sección 8.3), una regla simple de prioridad y de rotación de bodega iguala a DespachoX en críticos a tiempo. Con carga media y alta, le gana por cerca de 2 puntos en entregas a tiempo de todos los puntos. Subir el peso de los puntos críticos no cambió eso (sección 8.2). Con las velocidades de la tesis UNAL de 2019 en la red ampliada (sección 9), DespachoX gana en críticos y empata en el total, salvo con carga alta. En la misma red, con las velocidades del modelo, la ventaja en críticos solo excluye el cero con carga alta, y con las de la tesis crece 2,8 y 3,7 puntos en carga media y alta, pareado por semilla (sección 9.3). DespachoX también gana con la flota corta (8.6) y cuando hay pedidos mal ubicados (8.4).
- **Mide solo en parte el valor de la entrada por chat.** La sección 8.4 modela un tipo de error, el pedido registrado en otro punto, y una corrección, la confirmación de ubicación. La tasa de error de 10 % o 20 % es nuestra y no tiene fuente. Además, suponemos que el despachador experto no confirma. Uno que llame a cada comité tendría el mismo beneficio, a costa de un tiempo que no modelamos.
- **No modela cierres registrados tarde ni falsos.** El encargo S2 lo proponía y lo dejamos por fuera, porque exige separar lo que sabe cada conductor de lo que sabe el despacho. Todo cierre reportado es cierto y se confirma en 5 minutos.
- **No mide la trazabilidad.** El código QR y la confirmación de entrega no entran en la simulación.
- **No valida los supuestos.** Las velocidades, los tiempos de carga y de entrega, los plazos por urgencia, la flota, la demanda y los cierres son nuestros. Ningún dato viene de una operación real del Banco de Alimentos ni de los organismos de socorro.
- **No dice cuál es la carga real.** Los niveles de carga se eligieron para que la línea base no quedara ni holgada ni colapsada. La magnitud de la ventaja sobre la política ingenua depende mucho de ese nivel y de la flota, y va de 10 a 58 puntos en críticos a tiempo.
- **No representa bien los perecederos.** Hay un solo acopio, tanto inventario perecedero como demanda y lotes que vencen entre 6 y 48 horas. El efecto del empaque activo (patente UNAL), que `optimizar.py` ya modela, no se midió. Con rotación por vencimiento el desperdicio ya es 0,0 % en estos escenarios, así que el empaque no tendría margen para mostrarse.
- **Describe la red urbana, no la ampliada.** Casi todas las corridas usan `manizales.graphml`, la red de Manizales y Villamaría con que se hizo la primera ronda. El producto usa ahora `manizales_region.graphml`, con los accesos. La sección 8.8 repite la carga media sobre esa red.
- **No incluye otros errores humanos.** El despachador aprueba siempre en 2 minutos y los conductores siguen el plan.
- **No cubre varios días.** Es una jornada de 14 horas, sin reabastecimiento ni cierres que se levanten.
- **No es reproducible al pie de la letra.** La búsqueda del optimizador se corta por tiempo de reloj, así que repetir una corrida con las mismas semillas da cifras muy cercanas, pero no idénticas (sección 8.2).

## 8. Segunda ronda: peso de los puntos críticos (encargo S2, 20 de noviembre de 2026)

Las secciones 1 a 6 describen la primera corrida y no se modifican. La sección 7 se actualizó con lo que se midió después, que está en esta sección.

### 8.1 Regla de elección de `FACTOR_CRITICO`, escrita antes de correr

`despacho/optimizar.py` tiene ahora la constante `FACTOR_CRITICO`, que multiplica el peso del retraso y la penalización por no atender de los pedidos de puntos críticos. Se barre con los valores 1, 3, 10 y 30, en carga media y alta, con las 30 semillas de la primera corrida (20261120 a 20261149) y 1 segundo de búsqueda por llamada.

La regla es esta. Se elige el menor factor con el que `despachox` no es peor que `experta` en dos métricas a la vez, críticos a tiempo y entregas a tiempo de todos los puntos, tanto en carga media como en carga alta. «No es peor» significa que el intervalo de confianza del 95 % de la diferencia pareada `despachox` − `experta` incluye el cero o queda entero del lado favorable. Si ningún factor lo cumple, se reporta así y no se elige ninguno.

El factor elegido se confirma después en 30 semillas nuevas (20261150 a 20261179), que no intervinieron en la elección. Las cifras para el pitch salen de esas semillas.

### 8.2 Resultado del barrido

Corrida del 20 de noviembre de 2026, de 2:45 a 3:33 p. m.: 30 semillas por factor y por carga, 1 segundo de búsqueda, sin errores del optimizador. La tabla completa está en `despacho/sim/resultados_s2/barrido_factor.md`. Cada celda es la diferencia pareada `despachox` − `experta` con su IC del 95 %.

| Factor | Carga | Críticos a tiempo (puntos) | A tiempo, todos los puntos (puntos) | Espera en el punto peor atendido (h) | Kilómetros |
|---:|---|---|---|---|---|
| 1 | media | −0,4 [−1,8; 1,0] | −1,8 [−2,6; −1,0] | 0,14 [−0,38; 0,67] | −58,2 [−76,5; −39,9] |
| 1 | alta | −1,8 [−3,6; 0,0] | −2,2 [−3,6; −0,7] | 0,99 [0,50; 1,49] | −46,8 [−73,3; −20,4] |
| 3 | media | 1,2 [0,0; 2,3] | −2,2 [−3,1; −1,4] | 0,16 [−0,35; 0,67] | −55,0 [−77,0; −33,1] |
| 3 | alta | 2,2 [0,8; 3,6] | −1,7 [−2,9; −0,5] | 0,91 [0,44; 1,37] | −53,1 [−74,3; −32,0] |
| 10 | media | 1,4 [0,4; 2,4] | −2,3 [−3,2; −1,3] | 0,12 [−0,44; 0,68] | −58,4 [−80,3; −36,5] |
| 10 | alta | 2,2 [0,8; 3,6] | −2,0 [−3,1; −0,9] | 0,93 [0,47; 1,39] | −53,9 [−74,6; −33,2] |
| 30 | media | 1,3 [0,3; 2,3] | −2,2 [−3,1; −1,2] | 0,23 [−0,27; 0,74] | −53,2 [−73,7; −32,7] |
| 30 | alta | 2,2 [0,7; 3,6] | −2,0 [−3,2; −0,9] | 0,91 [0,45; 1,36] | −52,0 [−70,3; −33,7] |

**Ningún factor cumple la regla, y por eso no se elige ninguno.** Con todos los valores, `despachox` queda cerca de 2 puntos por debajo de `experta` en entregas a tiempo de todos los puntos, y el intervalo excluye el cero.

El factor sí cambia el indicador del reto. Con factor 1, `despachox` empata o queda por debajo de `experta` en críticos a tiempo. Con factor 3 queda por encima: 99,7 % contra 98,5 % en carga media y 99,8 % contra 97,6 % en carga alta. Subir de 3 a 10 o a 30 no añade nada, porque con 3 ya se entregan a tiempo casi todos los pedidos críticos. El factor no mueve las entregas a tiempo de todos los puntos, ni la espera del punto peor atendido, ni los kilómetros.

La corrida con factor 1 repite la primera corrida con las mismas semillas y da cifras casi iguales, pero no idénticas (−0,4 contra −0,5 en críticos, carga media). La búsqueda del optimizador se corta por tiempo de reloj y por eso no es exactamente reproducible.

### 8.3 Factor 3 en semillas nuevas

Esta parte se sale de la regla. Como ningún factor la cumplió, la elección del 3 es posterior a los datos: es el menor valor con el que `despachox` supera a `experta` en críticos a tiempo. Para que la cifra no esté inflada por esa elección, se midió en 30 semillas nuevas (20261150 a 20261179), que no intervinieron en ella.

Corrida de 3:36 a 3:49 p. m., en los tres niveles de carga, con factor 3 y 1 segundo de búsqueda. Los escenarios de estas semillas son algo más chicos que los de la primera ronda: 49 puntos y 7,5 vehículos en promedio.

| Carga | Comparación | Críticos a tiempo (puntos) | A tiempo, todos los puntos (puntos) | Espera en el punto peor atendido (h) | Kilómetros |
|---|---|---|---|---|---|
| Holgada | `despachox` − `ingenua` | 10,1 [5,8; 14,4] | 3,1 [1,9; 4,2] | 1,41 [0,90; 1,92] | −53,1 [−64,6; −41,5] |
| Media | `despachox` − `ingenua` | 28,6 [22,4; 34,7] | 4,0 [2,4; 5,6] | 2,84 [2,31; 3,37] | −50,9 [−67,6; −34,2] |
| Alta | `despachox` − `ingenua` | 47,5 [41,2; 53,7] | 7,0 [5,0; 8,9] | 3,81 [3,08; 4,53] | −55,5 [−72,4; −38,6] |
| Holgada | `despachox` − `experta` | 0,3 [−0,6; 1,2] | −0,2 [−0,7; 0,4] | 0,23 [−0,21; 0,67] | −51,1 [−62,6; −39,5] |
| Media | `despachox` − `experta` | 1,7 [−0,7; 4,0] | −1,9 [−3,5; −0,3] | 0,81 [0,37; 1,25] | −59,5 [−73,0; −46,0] |
| Alta | `despachox` − `experta` | 0,8 [−0,6; 2,2] | −1,7 [−3,2; −0,2] | 0,89 [0,33; 1,45] | −46,9 [−65,0; −28,7] |

**La ventaja del factor 3 sobre `experta` en críticos no se confirma.** En las semillas nuevas la diferencia es positiva en los tres niveles, pero todos los intervalos incluyen el cero. Lo que sí se repite es la desventaja de cerca de 2 puntos en entregas a tiempo de todos los puntos en carga media y alta, y la ventaja de 47 a 60 km.

Frente a la política ingenua, el resultado de la primera ronda se repite casi igual en semillas que no intervinieron en ninguna decisión: 10, 29 y 48 puntos más de críticos a tiempo. Los perecederos vencidos quedan en 0,0 % para `despachox` y en 1,0 %, 1,8 % y 3,2 % para la ingenua.

**Propuesta para `optimizar.py`:** subir `FACTOR_CRITICO` de 1 a 3. No cumple la regla de la sección 8.1 y su efecto sobre `experta` no es significativo en semillas nuevas. Se propone porque su efecto medio en críticos fue positivo en las cinco comparaciones (2 cargas del barrido y 3 de la confirmación), porque no empeoró ninguna otra métrica de forma medible frente al factor 1, y porque el indicador del reto premia justo los puntos críticos. La decisión es de B o de Carlos.

### 8.4 Información imperfecta: pedidos registrados en el punto equivocado

Hasta aquí todas las políticas recibían cada pedido en su punto correcto. Esta corrida añade un error de registro. Con probabilidad p, un pedido queda anotado en otro punto de la jornada, elegido al azar.

- **Sin confirmación** (`ingenua`, `experta` y `despachox_sin_confirmar`), el error se descubre cuando el vehículo llega al punto equivocado. Ahí pierde 10 minutos, el registro se corrige y la carga vuelve al acopio para salir de nuevo.
- **Con confirmación** (`despachox`), el chat le devuelve la ubicación a quien pidió y espera su «sí». El error se corrige antes de despachar y el pedido entra 5 minutos más tarde.

Los pedidos que fallan con p = 0,1 también fallan con p = 0,2, porque el sorteo es común. El valor de p es un supuesto nuestro: no tenemos una medición de cuántos pedidos llegan mal ubicados. Carga media, semillas 20261120 a 20261149, factor 1, 1 segundo de búsqueda.

| p | Comparación | Críticos a tiempo (puntos) | A tiempo, todos los puntos (puntos) | Espera en el punto peor atendido (h) |
|---|---|---|---|---|
| 0 | `despachox` − `despachox_sin_confirmar` | 0,2 [−0,2; 0,6] | 0,1 [−0,1; 0,2] | 0,02 [−0,09; 0,12] |
| 0,1 | `despachox` − `despachox_sin_confirmar` | 3,3 [1,0; 5,7] | 6,0 [4,5; 7,5] | −1,45 [−1,84; −1,05] |
| 0,2 | `despachox` − `despachox_sin_confirmar` | 7,0 [4,9; 9,2] | 10,7 [9,0; 12,5] | −2,04 [−2,61; −1,47] |
| 0 | `despachox` − `experta` | −0,4 [−1,8; 1,0] | −1,8 [−2,6; −1,0] | 0,19 [−0,34; 0,71] |
| 0,1 | `despachox` − `experta` | 3,0 [0,9; 5,2] | 3,4 [2,1; 4,8] | −1,04 [−1,69; −0,40] |
| 0,2 | `despachox` − `experta` | 4,4 [2,2; 6,5] | 9,1 [7,2; 11,0] | −1,91 [−2,44; −1,38] |

Con p = 0,1 hubo 13,7 llegadas a un punto equivocado por jornada en las políticas sin confirmación, y 26,9 con p = 0,2.

La primera comparación aísla el valor de confirmar la ubicación: es el mismo sistema, con y sin ese paso. Con p = 0 la confirmación no cuesta nada medible. Con p = 0,1 sube las entregas a tiempo de todos los puntos en 6 puntos, y con p = 0,2 en 10,7. Además reduce la espera del punto peor atendido en 1,5 y 2,0 horas.

La segunda comparación es la primera en que `despachox` le gana a `experta` en todas las métricas del reto. Hay que leerla con cuidado, porque depende de un supuesto: que el despachador experto no confirma la ubicación. Un despachador que llame a cada comité a confirmar tendría el mismo beneficio, a costa de su tiempo, que aquí no se modela.

### 8.5 Sensibilidad al número de cierres

Carga media, mismas semillas, factor 1, 1 segundo de búsqueda.

| Cierres por jornada | `despachox` − `ingenua`, críticos (puntos) | `despachox` − `experta`, críticos (puntos) | `despachox` − `experta`, todos los puntos (puntos) |
|---:|---|---|---|
| 0 | 29,5 [23,9; 35,0] | 0,6 [−0,8; 2,1] | −2,1 [−3,0; −1,3] |
| 5 | 29,8 [24,0; 35,7] | 0,7 [−0,7; 2,1] | −1,5 [−2,3; −0,6] |
| 10 | 28,2 [22,7; 33,6] | −0,9 [−2,6; 0,8] | −1,8 [−2,7; −0,9] |

El número de cierres casi no mueve las comparaciones. La ventaja de DespachoX sobre la política ingenua viene de priorizar los pedidos críticos, y esquivar cierres aporta poco. Con estos supuestos los cierres cuestan poco a todas las políticas, porque la red urbana tiene caminos alternos y el aviso por radio desvía a todos los conductores por igual.

### 8.6 Sensibilidad al tamaño de la flota

Carga media, mismas semillas, factor 1, 1 segundo de búsqueda, con dos camperos menos: 6,5 vehículos en promedio en lugar de 8,3.

| Comparación | Críticos a tiempo (puntos) | A tiempo, todos los puntos (puntos) | Kilómetros |
|---|---|---|---|
| `despachox` − `ingenua` | 57,7 [52,2; 63,3] | 10,9 [9,2; 12,7] | −39,0 [−54,2; −23,9] |
| `despachox` − `experta` | −0,6 [−4,1; 3,0] | 3,4 [1,3; 5,5] | −36,9 [−50,2; −23,6] |

Las medias son de 33,0 %, 91,3 % y 90,8 % de críticos a tiempo para `ingenua`, `experta` y `despachox`. En entregas a tiempo de todos los puntos son 61,7 %, 69,2 % y 72,6 %.

Con la flota corta, DespachoX supera a `experta` en entregas a tiempo de todos los puntos y empata en críticos. Es el único escenario con información perfecta en que eso pasa. La política ingenua deja vencer el 5,7 % de los perecederos y pasa la meta del 5 % del reto; las otras tres quedan en 0,0 %.

### 8.7 Tiempo de búsqueda del optimizador

Carga media, mismas semillas, factor 1. La demo usa hasta 8 segundos por llamada y la simulación usa 1.

| Búsqueda por llamada | Segundos medios por llamada | `despachox` − `experta`, críticos (puntos) | `despachox` − `experta`, todos los puntos (puntos) | `despachox` − `experta`, kilómetros |
|---:|---:|---|---|---|
| 1 s | 1,26 | −0,5 [−1,8; 0,9] | −1,8 [−2,7; −1,0] | −55,5 [−73,1; −37,9] |
| 3 s | 3,40 | −0,4 [−1,8; 0,9] | −1,9 [−2,6; −1,2] | −56,8 [−74,8; −38,8] |
| 8 s | 8,24 | −0,2 [−1,5; 1,2] | −1,8 [−2,6; −1,0] | −61,4 [−79,9; −42,9] |

Buscar más tiempo ahorra algunos kilómetros y no cambia los indicadores del reto. Los resultados de la simulación con 1 segundo valen, por lo tanto, para la demo con 8. La fila de 1 s es de la primera corrida; las de 3 y 8 s, de esta ronda.

### 8.8 Red ampliada

`despacho/red.py` lee ahora `manizales_region.graphml` (7.825 nodos), que añade a la red urbana los accesos: La Siria, Neira, Letras y la autopista del Café. Se repitió la carga media sobre esa red con las cuatro políticas, las semillas 20261120 a 20261149, factor 1 y 1 segundo de búsqueda. Una prueba confirmó antes de correr que la simulación y el optimizador calculan los mismos tiempos sobre esta red.

Con otra red, la misma semilla pone los puntos y los cierres en otros lugares. Por eso esta corrida compara bien las políticas entre sí, pero no se puede parear contra la de la red urbana.

| Comparación | Críticos a tiempo (puntos) | Perecederos vencidos (puntos) | A tiempo, todos los puntos (puntos) | Kilómetros |
|---|---|---|---|---|
| `despachox` − `ingenua` | 28,0 [22,4; 33,6] | −2,1 [−2,9; −1,4] | 3,7 [2,4; 5,0] | −72,9 [−100,7; −45,0] |
| `despachox` − `experta` | −0,8 [−1,9; 0,3] | 0,0 [0,0; 0,0] | −2,1 [−2,9; −1,3] | −60,1 [−79,8; −40,5] |
| `despachox` − `optimiza_una_vez` | 17,5 [11,7; 23,2] | 0,0 [0,0; 0,0] | 0,9 [−0,4; 2,3] | −29,6 [−40,1; −19,0] |

Las conclusiones de la red urbana se mantienen. DespachoX supera a la política ingenua por 28 puntos en críticos a tiempo (70,4 % contra 98,3 %), empata con `experta` en críticos, queda 2 puntos debajo de ella en el total y le ahorra 60 km por jornada. Ninguna llamada al optimizador terminó en error.

## 9. Con las velocidades de la tesis UNAL de 2019 (noche del 20 al 21 de noviembre de 2026)

Las secciones 1 a 8 no se modifican. Esta sección repite la confirmación de la sección 8.3 con velocidades más lentas. Son velocidades derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48). En adelante se llaman «velocidades de la tesis».

**Por qué.** Dos agentes encontraron que la velocidad supuesta estaba inflada. Según `docs/datos/flota_perecederos_costos.md`, una tesis de maestría de la UNAL Manizales de 2019 da para un bus diésel 22,6 km/h de media en su ruta de Manizales (p. 50), y de 21,8 a 24,2 km/h en vías principales (tabla 14, p. 48). El grafo, en cambio, le daba al campero 39,0 km/h de media en `primary` y 54,7 en `trunk` (medido por un agente sobre el grafo, en el mismo documento). Fuera de la ciudad, el SICE-TAC del Ministerio de Transporte supone 15 km/h para un camión de dos ejes en terreno montañoso. Ese valor no se usó.

**De dónde salen las velocidades. Estado: revisado por máquina; falta que una persona abra la tesis.** Un agente de Fable leyó las páginas impresas de la tesis. La p. 27 nombra un registrador GPS V-900, y la p. 29, un GPS en cada bus. En las pp. 46 y 47, las velocidades salen de procesar los datos del GPS y se asignan a la red por tipo de vía y pendiente. La tabla 14, en la p. 48, se titula «velocidades asignadas». Por eso esta sección no las llama medidas a secas.

### 9.1 Qué cambió y cómo se corrió

- **Velocidad de cada tramo.** Con `python -m despacho.sim.correr --velocidades medidas`, o con la variable de entorno `DESPACHOX_SIM_VELOCIDADES=medidas`, cada tramo toma la velocidad de su tipo de vía y de vehículo en `datos_publicos/velocidades.csv`. Donde hay dato, ese archivo trae las velocidades de la tesis. `medidas` es solo el nombre de la opción en el código. Sin la opción, o con `--velocidades modelo`, todo queda como antes.
- **Sin `maxspeed`.** Se ignora el límite de OpenStreetMap, que en `trunk` llegaba a 80 km/h. Solo 31 de las 18.821 aristas, 13,7 de 4.262 km, traen un límite menor que la velocidad de la tesis.
- **Por vehículo.** El camión va a la misma velocidad que el campero, sin el factor 1,25 del modelo, y la moto va 11 % más rápido. Así lo trae el CSV. El camión sigue sin entrar a vías residenciales.
- **Vías sin fila en el CSV.** Solo `ladder`, con 2 aristas y 0,1 km. Queda con el supuesto del modelo, 20 km/h.
- **El optimizador planea con las mismas velocidades.** El adaptador le pasa a `matriz.calcular` una copia del grafo por tipo de vehículo. No se tocaron `optimizar.py` ni `matriz.py`. Una prueba confirma que la simulación y el optimizador calculan los mismos segundos entre sitios, con una diferencia máxima de 0,5 s por el redondeo.
- **Los viajes se alargan.** En los escenarios de carga media, el tiempo medio entre sitios sube 44 % para el campero y la moto, y 23 % para el camión. Del acopio a un punto, el campero pasa de 7,1 a 9,8 minutos en promedio, el camión de 9,8 a 11,5 y la moto de 6,4 a 8,8 (medido por nosotros en los 30 escenarios).
- **Apagada, nada cambia.** Es el valor por defecto. Con la opción apagada, `ingenua` y `experta` dan un `resultados.csv` idéntico byte a byte al del código anterior, en 5 semillas de las tres cargas. Antes del cambio, ese código reprodujo sin diferencias las 60 filas de esas dos políticas en la sección 8.8, así que la red es la misma. Las políticas con optimizador no se pueden comparar byte a byte, porque su búsqueda se corta por reloj (sección 7). Con la opción apagada, el optimizador recibe el grafo y las matrices de siempre. Las pruebas están en `despacho/sim/tests/test_velocidades.py`.

**Red.** Se usó `manizales_region.graphml` (7.825 nodos), la red del producto. La sección 8.3 corrió sobre la red urbana `manizales.graphml` (6.395 nodos). Ese archivo no está en esta máquina y no lo pudimos bajar, porque Overpass no respondió. Con otra red, la misma semilla pone los puntos y los cierres en otros lugares (sección 8.8). Por eso la comparación con la sección 8.3 no es pareada y mezcla dos cambios: la velocidad y la red. Para separarlos, la sección 9.3 repite la confirmación con las velocidades del modelo sobre la misma red y las mismas semillas. Así quedan las dos versiones, como pide la decisión 3 de `docs/DECISIONES_9PM.md`.

**Semillas.** 20261150 a 20261179, 30 por carga. Son las semillas de confirmación de la sección 8.3, que no intervinieron en la elección del factor 3. Esa elección se hizo con las semillas 20261120 a 20261149. Se usan las mismas tres cargas, las mismas cuatro políticas y las mismas líneas base de la sección 8.3, con `FACTOR_CRITICO` = 3 y 1 s de búsqueda por llamada. Con la misma semilla y la misma red, las dos versiones de velocidad tienen los mismos puntos, pedidos, lotes y flota. Los cierres se sortean con la misma regla sobre los caminos más cortos de cada versión, así que pueden caer en otros tramos.

**Tiempo.** Antes de la corrida principal, 3 semillas tardaron 9,5 minutos en las tres cargas. Con eso, 30 semillas cabían antes de las 5:00 a. m., y no se bajó a 20. La corrida principal duró de las 11:11 p. m. a las 12:33 a. m., con 2 procesos en una máquina de 2 núcleos. La corrida sin cierres empezó a las 12:33 a. m. y se detuvo hacia la 1:00 a. m., cuando se apagó el servidor de la sesión. A las 6:03 a. m., Fable relanzó solo la corrida de la misma red con las velocidades del modelo. Terminó a las 7:23 a. m.

| Corrida | Qué cambia | Jornadas | Estado | Carpeta en `despacho/sim/resultados_velocidades/` |
|---|---|---:|---|---|
| Principal (9.2) | Velocidades de la tesis, 3 a 8 cierres, las tres cargas | 360 | Terminada. Ninguna llamada al optimizador terminó en error | `confirmacion_factor_3` |
| Misma red (9.3) | Velocidades del modelo | 360 | Terminada a las 7:23 a. m. Ninguna llamada al optimizador terminó en error | `modelo_misma_red` |
| Sin cierres (9.4) | 0 cierres por jornada | 0 | No se hizo | ninguna |
| Vida útil por producto (9.5) | Vencimientos de `datos_publicos/vida_util.csv` | 0 | No se hizo | ninguna |

Las tablas completas, con todas las métricas, están en el `resumen.md` de cada carpeta, y los datos por semilla en su `resultados.csv`. Las tablas de esta sección salen de `tablas.md`, que escribe `python -m despacho.sim.comparar despacho/sim/resultados_velocidades`, y se copiaron sin cambios. El código de la simulación es el del commit `1489760`. La corrida de la misma red registra en su `resumen.md` el commit `513b88a`, posterior, con el mismo código de simulación.

### 9.2 Resultados con las velocidades de la tesis

Corrida principal: 30 escenarios por carga, 90 en total, cuatro políticas y 360 jornadas. Los escenarios tienen en promedio 49 puntos, 7,5 vehículos y 5,6 cierres. La carga holgada son 100 pedidos, la media 125 y la alta 149.

En cada tabla, las tres primeras columnas de cifras son medias por política. Las líneas base son `ingenua`, que atiende por orden de llegada, y `experta`, que atiende primero lo más urgente y saca primero lo que vence primero. Las diferencias son la media pareada por semilla con su IC del 95 % (t de Student, 29 grados de libertad). Las dos últimas columnas dan la misma diferencia `despachox` − `experta` con las velocidades del modelo: sobre la misma red y las mismas semillas (9.3), y la que se reportó en la sección 8.3, sobre la red urbana. Los supuestos están en la sección 9.6.

**Críticos a tiempo (%).** Pedidos de puntos críticos entregados antes de su hora límite. 30 escenarios por carga.

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 75,9 | 97,7 | 99,2 | 23,3 [17,4; 29,1] | 1,5 [0,2; 2,8] | 8 / 20 / 2 | 0,3 [−0,9; 1,4] | 0,3 [−0,6; 1,2] |
| Media | 53,6 | 94,6 | 98,3 | 44,7 [37,7; 51,6] | 3,7 [1,7; 5,7] | 15 / 13 / 2 | 0,9 [−0,2; 2,1] | 1,7 [−0,7; 4,0] |
| Alta | 40,5 | 91,9 | 98,4 | 57,9 [52,7; 63,1] | 6,5 [4,4; 8,7] | 23 / 6 / 1 | 2,8 [0,8; 4,7] | 0,8 [−0,6; 2,2] |

**A tiempo, todos los puntos (%).** 30 escenarios por carga.

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 90,4 | 95,2 | 94,8 | 4,3 [2,4; 6,3] | −0,5 [−1,9; 0,9] | 9 / 6 / 15 | −0,8 [−1,8; 0,2] | −0,2 [−0,7; 0,4] |
| Media | 76,4 | 84,8 | 84,0 | 7,6 [5,2; 9,9] | −0,8 [−3,1; 1,4] | 10 / 3 / 17 | −2,6 [−4,1; −1,0] | −1,9 [−3,5; −0,3] |
| Alta | 62,4 | 70,3 | 73,2 | 10,8 [8,4; 13,3] | 3,0 [0,7; 5,3] | 23 / 0 / 7 | −2,7 [−4,2; −1,1] | −1,7 [−3,2; −0,2] |

**Perecederos vencidos (%).** Kilos de lotes que vencen en la jornada y no se entregaron antes de vencer. 30 escenarios por carga.

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 1,4 | 0,0 | 0,0 | −1,4 [−2,1; −0,8] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Media | 3,4 | 0,0 | 0,0 | −3,4 [−4,4; −2,4] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Alta | 5,6 | 0,0 | 0,0 | −5,6 [−6,8; −4,3] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |

**Kilómetros de la flota por jornada.** 30 escenarios por carga.

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 623,0 | 615,9 | 569,9 | −53,1 [−71,2; −34,9] | −46,0 [−63,3; −28,7] | 27 / 0 / 3 | −62,6 [−82,0; −43,2] | −51,1 [−62,6; −39,5] |
| Media | 760,5 | 755,8 | 699,8 | −60,6 [−82,4; −38,9] | −56,0 [−77,9; −34,0] | 26 / 0 / 4 | −51,5 [−70,6; −32,3] | −59,5 [−73,0; −46,0] |
| Alta | 842,3 | 840,5 | 798,3 | −44,0 [−59,4; −28,7] | −42,2 [−56,8; −27,6] | 26 / 0 / 4 | −44,6 [−66,2; −23,0] | −46,9 [−65,0; −28,7] |

**Espera en el punto peor atendido (h).** 30 escenarios por carga.

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 5,14 | 6,96 | 7,09 | 1,95 [1,36; 2,53] | 0,13 [−0,36; 0,63] | 13 / 0 / 17 | 0,28 [−0,17; 0,73] | 0,23 [−0,21; 0,67] |
| Media | 6,46 | 9,00 | 9,53 | 3,07 [2,46; 3,68] | 0,53 [0,04; 1,02] | 9 / 0 / 21 | 0,62 [0,21; 1,03] | 0,81 [0,37; 1,25] |
| Alta | 7,56 | 10,77 | 11,37 | 3,82 [3,21; 4,43] | 0,61 [0,17; 1,04] | 10 / 2 / 18 | 0,75 [0,38; 1,12] | 0,89 [0,33; 1,45] |

**Frente al despacho por orden de llegada, DespachoX gana con claridad en puntos críticos.** Entrega a tiempo 23,3, 44,7 y 57,9 puntos más de pedidos críticos que la política ingenua, según la carga, y el intervalo nunca toca el cero. Con las velocidades del modelo en la misma red eran 13,3, 32,5 y 48,9 puntos, y en la sección 8.3, 10,1, 28,6 y 47,5. La ingenua cae a 75,9 %, 53,6 % y 40,5 % de críticos a tiempo.

**Frente al despachador con oficio, DespachoX gana en puntos críticos en las tres cargas.** La diferencia es de 1,5, 3,7 y 6,5 puntos, y los tres intervalos excluyen el cero. DespachoX fue mejor en 8, 15 y 23 de los 30 escenarios, y peor en 2, 2 y 1. Con las velocidades del modelo en la misma red, la diferencia era de 0,3, 0,9 y 2,8 puntos, y solo en carga alta el intervalo excluía el cero. En la sección 8.3 los tres intervalos incluían el cero.

**En el total de entregas a tiempo, empata en carga holgada y media y gana en carga alta.** Las diferencias son de −0,5 y −0,8 puntos, con intervalos que incluyen el cero, aunque DespachoX fue peor en más escenarios que mejor: 15 y 17 de 30. En carga alta gana 3,0 puntos, con IC de [0,7; 5,3]. Con las velocidades del modelo en la misma red, DespachoX quedaba 0,8, 2,6 y 2,7 puntos debajo, y en carga media y alta el intervalo excluía el cero. En la sección 8.3 quedaba 1,9 y 1,7 puntos debajo en carga media y alta.

**Los kilómetros se mantienen.** DespachoX recorre 46,0, 56,0 y 42,2 km menos que `experta` por jornada, del 5,0 % al 7,5 % de su recorrido. Con las velocidades del modelo en la misma red eran 62,6, 51,5 y 44,6 km, y en la sección 8.3, 51,1, 59,5 y 46,9 km.

**El desperdicio sigue resuelto por la regla de bodega.** `experta` y DespachoX dejan vencer 0,0 % de los perecederos en los 90 escenarios. La ingenua pierde 1,4 %, 3,4 % y 5,6 %. En carga alta pasa en promedio la meta del 5 % del reto, y 17 de sus 30 escenarios quedan por encima. En carga holgada y media son 2 y 9 de 30. Con las velocidades del modelo en la misma red perdía 1,1 %, 2,2 % y 3,9 %, y pasaba el 5 % en 1, 3 y 11 escenarios. En la sección 8.3 perdía 1,0 %, 1,8 % y 3,2 %.

**La prioridad sigue costando en equidad.** DespachoX hace esperar al punto peor atendido 0,13, 0,53 y 0,61 horas más que `experta`, y en carga media y alta el intervalo excluye el cero. Con las velocidades del modelo eran 0,28, 0,62 y 0,75 horas. Frente a la ingenua son 1,95, 3,07 y 3,82 horas más.

El optimizador se llamó entre 56 y 78 veces por jornada en promedio, según la carga. Tardó entre 1,37 y 1,64 segundos por llamada en promedio, con 1 s de búsqueda. Con las velocidades del modelo en la misma red tardó entre 1,48 y 1,55 segundos, y en la sección 8.3, 1,28.

### 9.3 Comparación con la sección 8: el efecto de la velocidad

La corrida con las velocidades del modelo sobre la misma red y las mismas semillas terminó a las 7:23 a. m.: 360 jornadas, sin errores del optimizador. Entre las dos corridas solo cambia la velocidad, así que la comparación es pareada por semilla. Los puntos, pedidos, lotes y flota son los mismos; los cierres pueden caer en otros tramos (9.1).

**Con las velocidades del modelo, la red ampliada repite la sección 8.** DespachoX empata con `experta` en críticos a tiempo en carga holgada y media, con 0,3 y 0,9 puntos, y le gana 2,8 [0,8; 4,7] en carga alta. En el total de entregas a tiempo queda 0,8, 2,6 y 2,7 puntos debajo, y en carga media y alta el intervalo excluye el cero. Le ahorra de 45 a 63 km por jornada. Es casi lo mismo que la sección 8.3 sobre la red urbana, así que, con carga holgada y media, el cambio de red no explica lo que cambió en la sección 9.2.

**Con las velocidades de la tesis, la ventaja de DespachoX sobre `experta` crece.** En críticos a tiempo crece 1,2 [−0,2; 2,7], 2,8 [0,9; 4,6] y 3,7 [2,0; 5,5] puntos, según la carga. En el total de entregas a tiempo crece 0,3 [−1,1; 1,7], 1,7 [−0,8; 4,3] y 5,7 [3,6; 7,7] puntos. Solo excluyen el cero el cambio en críticos con carga media y alta, y el del total con carga alta. En los kilómetros no hay cambio medible.

**Con viajes más largos, `experta` pierde más que DespachoX.** En críticos a tiempo baja 1,4, 3,3 y 3,8 puntos, y DespachoX entre 0,0 y 0,5, con intervalos que incluyen el cero. En el total de entregas a tiempo, `experta` baja 3,4, 8,5 y 12,2 puntos, y DespachoX 3,1, 6,7 y 6,6. Una lectura posible, que la simulación no prueba, es que con los mismos plazos y viajes más largos atender por urgencia sin planear las rutas deja llegar tarde a más pedidos y planear pesa más.

La comparación con la sección 8.3 no es pareada y mezcla la velocidad con la red. Con carga alta, `experta` baja ahí de 98,1 % a 91,9 % en críticos a tiempo y DespachoX de 98,9 % a 98,4 %. En el total de entregas a tiempo con carga alta, `experta` baja de 85,2 % a 70,3 % y DespachoX de 83,5 % a 73,2 %.

**Efecto de las velocidades de la tesis en la misma red.** Diferencia pareada por semilla, velocidades de la tesis menos velocidades del modelo, con IC del 95 %. 30 escenarios por carga. La última columna es el cambio de la diferencia `despachox` − `experta`.

| Carga | Indicador | `ingenua` | `experta` | `despachox` | Cambio de la brecha `despachox` − `experta` |
|---|---|---|---|---|---|
| Holgada | Críticos a tiempo (%) | −10,1 [−13,6; −6,6] | −1,4 [−3,0; 0,2] | −0,2 [−0,8; 0,4] | 1,2 [−0,2; 2,7] |
| Holgada | A tiempo, todos los puntos (%) | −4,5 [−6,8; −2,3] | −3,4 [−5,9; −0,9] | −3,1 [−4,9; −1,2] | 0,3 [−1,1; 1,7] |
| Holgada | Perecederos vencidos (%) | 0,4 [0,1; 0,7] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Holgada | Kilómetros de la flota | −54,6 [−85,9; −23,4] | −50,0 [−76,9; −23,0] | −33,3 [−61,0; −5,7] | 16,6 [−2,7; 35,9] |
| Holgada | Espera en el punto peor atendido (h) | 0,71 [0,25; 1,18] | 1,83 [1,37; 2,29] | 1,68 [1,04; 2,32] | −0,15 [−0,80; 0,51] |
| Media | Críticos a tiempo (%) | −12,6 [−16,1; −9,2] | −3,3 [−4,8; −1,7] | −0,5 [−1,5; 0,5] | 2,8 [0,9; 4,6] |
| Media | A tiempo, todos los puntos (%) | −9,4 [−12,2; −6,6] | −8,5 [−11,2; −5,7] | −6,7 [−9,0; −4,4] | 1,7 [−0,8; 4,3] |
| Media | Perecederos vencidos (%) | 1,3 [0,6; 1,9] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Media | Kilómetros de la flota | −45,5 [−75,5; −15,4] | −45,7 [−70,8; −20,5] | −50,2 [−81,6; −18,8] | −4,5 [−24,8; 15,8] |
| Media | Espera en el punto peor atendido (h) | 1,13 [0,57; 1,68] | 1,62 [1,21; 2,03] | 1,53 [1,02; 2,04] | −0,09 [−0,67; 0,49] |
| Alta | Críticos a tiempo (%) | −9,0 [−11,8; −6,1] | −3,8 [−5,2; −2,4] | 0,0 [−1,3; 1,2] | 3,7 [2,0; 5,5] |
| Alta | A tiempo, todos los puntos (%) | −11,5 [−14,2; −8,8] | −12,2 [−14,6; −9,9] | −6,6 [−8,2; −4,9] | 5,7 [3,6; 7,7] |
| Alta | Perecederos vencidos (%) | 1,6 [1,0; 2,3] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Alta | Kilómetros de la flota | −94,5 [−130,4; −58,6] | −89,2 [−118,5; −60,0] | −86,9 [−122,2; −51,6] | 2,4 [−16,4; 21,2] |
| Alta | Espera en el punto peor atendido (h) | 1,20 [0,88; 1,52] | 1,46 [1,07; 1,86] | 1,32 [0,96; 1,68] | −0,14 [−0,67; 0,38] |

**Medias con las velocidades del modelo en la misma red.** 30 escenarios por carga, semillas 20261150 a 20261179, factor 3.

| Carga | Indicador | `ingenua` | `experta` | `despachox` |
|---|---|---:|---:|---:|
| Holgada | Críticos a tiempo (%) | 86,0 | 99,1 | 99,3 |
| Holgada | A tiempo, todos los puntos (%) | 95,0 | 98,6 | 97,8 |
| Holgada | Perecederos vencidos (%) | 1,1 | 0,0 | 0,0 |
| Holgada | Kilómetros de la flota | 677,6 | 665,9 | 603,3 |
| Holgada | Espera en el punto peor atendido (h) | 4,43 | 5,13 | 5,41 |
| Media | Críticos a tiempo (%) | 66,2 | 97,9 | 98,8 |
| Media | A tiempo, todos los puntos (%) | 85,9 | 93,3 | 90,7 |
| Media | Perecederos vencidos (%) | 2,2 | 0,0 | 0,0 |
| Media | Kilómetros de la flota | 805,9 | 801,5 | 750,0 |
| Media | Espera en el punto peor atendido (h) | 5,33 | 7,38 | 8,00 |
| Alta | Críticos a tiempo (%) | 49,5 | 95,6 | 98,4 |
| Alta | A tiempo, todos los puntos (%) | 73,9 | 82,5 | 79,8 |
| Alta | Perecederos vencidos (%) | 3,9 | 0,0 | 0,0 |
| Alta | Kilómetros de la flota | 936,8 | 929,8 | 885,2 |
| Alta | Espera en el punto peor atendido (h) | 6,36 | 9,30 | 10,05 |

**Medias de la sección 8.3 (red urbana, velocidades del modelo).** 30 escenarios por carga, semillas 20261150 a 20261179, factor 3.

| Carga | Indicador | `ingenua` | `experta` | `despachox` |
|---|---|---:|---:|---:|
| Holgada | Críticos a tiempo (%) | 89,7 | 99,5 | 99,8 |
| Holgada | A tiempo, todos los puntos (%) | 95,8 | 99,1 | 98,9 |
| Holgada | Perecederos vencidos (%) | 1,0 | 0,0 | 0,0 |
| Holgada | Kilómetros de la flota | 625,5 | 623,5 | 572,4 |
| Holgada | Espera en el punto peor atendido (h) | 3,90 | 5,07 | 5,30 |
| Media | Críticos a tiempo (%) | 70,9 | 97,8 | 99,5 |
| Media | A tiempo, todos los puntos (%) | 88,8 | 94,7 | 92,8 |
| Media | Perecederos vencidos (%) | 1,8 | 0,0 | 0,0 |
| Media | Kilómetros de la flota | 745,8 | 754,4 | 694,9 |
| Media | Espera en el punto peor atendido (h) | 5,04 | 7,07 | 7,88 |
| Alta | Críticos a tiempo (%) | 51,4 | 98,1 | 98,9 |
| Alta | A tiempo, todos los puntos (%) | 76,5 | 85,2 | 83,5 |
| Alta | Perecederos vencidos (%) | 3,2 | 0,0 | 0,0 |
| Alta | Kilómetros de la flota | 883,8 | 875,2 | 828,3 |
| Alta | Espera en el punto peor atendido (h) | 5,82 | 8,74 | 9,63 |

### 9.4 Un día sin cierres (pedido de Samuel)

No se midió con las velocidades de la tesis. La corrida empezó a las 12:33 a. m. y se detuvo hacia la 1:00 a. m. con el servidor de la sesión, sin escribir resultados. Esta mañana Fable decidió no repetirla. El pedido de Samuel (canal, 8:00 p. m.) sigue pendiente con estas velocidades.

Lo más cercano que ya está medido es la corrida de 0 cierres de la sección 8.5: carga media, velocidades del modelo, red urbana, factor 1 y semillas 20261120 a 20261149. Ahí DespachoX recorrió 65,0 km menos que `experta` por jornada, con IC del 95 % de [−83,8; −46,2], y fue mejor en 28 de los 30 escenarios. Son 762,4 km contra 827,4, un 7,9 % menos. En esa corrida empató en críticos a tiempo, con 0,6 [−0,8; 2,1], y quedó 2,1 puntos debajo en el total de entregas a tiempo, con [−3,0; −1,3]. Los kilómetros salen de `despacho/sim/resultados_s2/cierres_0/resultados.csv`, porque la sección 8.5 no los reportó.

### 9.5 Vida útil por producto

La corrida con los vencimientos de `datos_publicos/vida_util.csv`, en lugar del rango de 6 a 48 horas, no se hizo. Los perecederos vencidos de esta sección siguen saliendo de ese rango, que es un supuesto nuestro (sección 6). Según `docs/datos/flota_perecederos_costos.md`, sección 4, la evidencia da a algunos perecederos más vida útil que ese rango, como el huevo, de 15 a 30 días, y a otros menos, como el pollo crudo sin frío, 2 horas.

### 9.6 Supuestos de esta sección

Todo lo demás es igual que en las secciones 2 y 6.

| Supuesto | Valor | Estado |
|---|---|---|
| Velocidad por tipo de vía y vehículo | `datos_publicos/velocidades.csv`, donde hay dato: velocidades derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48). Asignar `tertiary` a colectora y `unclassified` y `residential` a vía local es un supuesto del CSV | revisado por máquina; falta que una persona abra la tesis |
| Pendiente | La simulación no usa la pendiente de cada tramo. Cada tipo de vía lleva una sola velocidad, la media de las cuatro clases de pendiente de la tabla 14. Por ejemplo, `primary` lleva 23,3 km/h, la media de 23,8, 21,8, 23,4 y 24,2 | cálculo del CSV |
| `trunk` | Se asimila a vía nacional, con 26,5 km/h en todos los tramos. La tesis solo da ese valor con pendiente de 8 % o más | supuesto del CSV |
| `unclassified` | Se asimila a vía local urbana, con 21,9 km/h. Son 2.251 de los 4.262 km de la red, un 53 %, sobre todo caminos rurales de los accesos. En vía destapada la velocidad puede ser menor | supuesto del CSV |
| Campero y moto | El campero, igual que el camión; la moto, 11 % más rápido | supuesto del CSV |
| Hora del día | La velocidad del bus en horas de entrada, almuerzo y salida vale para toda la jornada y para los tres vehículos | supuesto nuestro |
| `maxspeed` de OpenStreetMap | No se usa | supuesto nuestro |
| Lo que sabe el optimizador | Planea con las mismas velocidades de la jornada simulada, igual que las líneas base. El producto no cambió: `despacho/red.py` sigue con las velocidades del modelo, así que sus tiempos de llegada salen más cortos que estos. Cambiar `red.py` es decisión de B. No se midió un optimizador que planee con velocidades equivocadas | supuesto nuestro |
| Velocidades del producto | El producto sigue con las velocidades del modelo. `despacho/red.py`, líneas 36 a 44, fija `VELOCIDADES` (por ejemplo, `primary` 40 km/h) y la línea 95 las aplica con `maxspeed` de OpenStreetMap donde lo hay. `despacho/matriz.py`, líneas 33 y 122, saca de ahí los tiempos de cada vehículo. Ningún archivo del producto lee `datos_publicos/velocidades.csv`. Solo la simulación lo lee, con `DESPACHOX_SIM_VELOCIDADES=medidas` (`despacho/sim/red_sim.py`, líneas 49 a 66 y 303 a 304), y `despacho/sim/adaptador_b.py` (línea 37) le pasa esas velocidades al optimizador. En esta sección el optimizador planea con las velocidades de la tesis. En el producto planea con las del modelo, más rápidas (`primary` 23,3 km/h en el CSV) | medido en el código |
| Cuándo se recalcula | La política simulada recalcula con cada cierre confirmado, con cada tanda de 30 minutos y cada vez que un vehículo vuelve al acopio (sección 3). El producto recalcula con un cierre confirmado o cuando lo pide el despachador (`despacho/recalcular.py`) | supuesto nuestro |
| Red | `manizales_region.graphml`, la del producto | trazado de OpenStreetMap |
| Máquina | 2 núcleos, compartidos con otras sesiones. La búsqueda del optimizador se corta por reloj, así que con la máquina cargada busca menos | condición de la corrida |

### 9.7 Qué decir en el pitch (por aprobar)

Todo lo que sigue es simulación medida por nosotros. Cada diferencia compara 30 jornadas por política en cada carga, con las semillas 20261150 a 20261179, factor crítico 3 e IC del 95 %. La línea base es `ingenua` (orden de llegada) o `experta` (el despachador con oficio), y cada frase dice cuál. En prosa para el jurado el producto se llama Convite.

**Lo que ahora se puede decir.**

1. Con velocidades derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48), Convite entrega a tiempo 23,3, 44,7 y 57,9 puntos porcentuales más de pedidos críticos que el despacho por orden de llegada, según la carga. Son 90 escenarios simulados con cierres de vías, 30 por carga.
2. Frente al despachador con oficio, con las velocidades de la tesis, Convite entrega a tiempo 1,5, 3,7 y 6,5 puntos más de pedidos críticos con carga holgada, media y alta. Los tres intervalos excluyen el cero.
3. En la misma red y con las mismas semillas, con las velocidades del modelo, esa ventaja es de 0,3, 0,9 y 2,8 puntos. Solo con carga alta el intervalo excluye el cero, con [0,8; 4,7].
4. Al pasar a las velocidades de la tesis, la ventaja en críticos crece 2,8 [0,9; 4,6] puntos con carga media y 3,7 [2,0; 5,5] con carga alta, pareado por semilla. Con carga holgada crece 1,2 [−0,2; 2,7], y ese intervalo incluye el cero.
5. Por eso, con carga media la ventaja en críticos aparece cuando los viajes son lentos. Con carga alta ya existe con las velocidades del modelo y crece con las de la tesis. Con carga holgada la simulación no permite atribuirla a la velocidad.
6. Convite recorre 46,0, 56,0 y 42,2 km menos por jornada que el despachador con oficio con las velocidades de la tesis, y 62,6, 51,5 y 44,6 km menos con las del modelo.
7. En el total de entregas a tiempo, con las velocidades de la tesis, Convite empata con el despachador con oficio en carga holgada y media, con −0,5 y −0,8 puntos, y gana 3,0 [0,7; 5,3] con carga alta. Con las velocidades del modelo queda 0,8, 2,6 y 2,7 puntos debajo, y en carga media y alta el intervalo excluye el cero.
8. Con Convite y con el despachador con oficio, los perecederos vencidos quedan en 0,0 % en las dos corridas. El despacho por orden de llegada pierde en promedio 5,6 % con carga alta y las velocidades de la tesis, por encima de la meta del 5 % del reto.

**Lo que sigue sin poderse decir.**

- Que Convite supera a un despachador humano. `experta` es una regla que escribimos nosotros y que tiene información perfecta.
- Que la ventaja en críticos «viene de la velocidad y no de la red» en todas las cargas. En la misma red, la velocidad suma 2,8 y 3,7 puntos con carga media y alta. Con carga alta y las velocidades del modelo, la red ampliada ya daba 2,8 puntos y la urbana 0,8 (sección 8.3), y esa comparación no es pareada.
- Que el cambio medido es solo de la velocidad. Con cada versión de velocidad los cierres se sortean sobre otros caminos y pueden caer en otros tramos (9.1). El número de cierres por semilla es el mismo.
- Que las velocidades de la tesis son las de un camión de ayuda. Vienen de un bus, sin la pendiente de cada tramo, y el 53 % de la red es `unclassified` asimilada a vía local (9.6).
- Que el producto logra hoy estas cifras. En la simulación el optimizador planea con las velocidades de la tesis, y el producto planea con las del modelo (9.6).
- Que Convite gana en el total de entregas a tiempo, salvo con carga alta y las velocidades de la tesis.
- Que el 0,0 % de vencidos es mérito del optimizador. Lo logra la regla de bodega, que también usa `experta`.
- Que Convite es más equitativo. Con las velocidades de la tesis, el punto peor atendido espera 0,53 y 0,61 horas más que con el despachador con oficio en carga media y alta, y los dos intervalos excluyen el cero.
- Nada de un día sin cierres (9.4) ni de vida útil por producto (9.5) con estas velocidades. No se corrieron.

**Frase de voz para el bloque 6 (34 palabras).**

> En simulación, con 30 jornadas por política y carga alta, Convite entrega a tiempo de 2,8 a 6,5 puntos más de pedidos críticos que un despachador con oficio, según la velocidad de las vías.

**Fila para la diapositiva de respaldo.** Críticos a tiempo, Convite menos despachador con oficio (`despachox` − `experta`), en puntos porcentuales, con IC del 95 %. Simulación, 30 jornadas por política y carga, misma red y mismas semillas.

| Carga | Velocidades de la tesis UNAL 2019 | Velocidades del modelo | Cuánto suma la velocidad (pareado) |
|---|---|---|---|
| Holgada | 1,5 [0,2; 2,8] | 0,3 [−0,9; 1,4] | 1,2 [−0,2; 2,7] |
| Media | 3,7 [1,7; 5,7] | 0,9 [−0,2; 2,1] | 2,8 [0,9; 4,6] |
| Alta | 6,5 [4,4; 8,7] | 2,8 [0,8; 4,7] | 3,7 [2,0; 5,5] |

**Si preguntan «si una regla simple empata, ¿qué aporta el optimizador?».**

> Con viajes cortos y carga holgada o media, la regla simple empata con Convite en críticos a tiempo. Lo medimos y lo decimos. Aun así, en simulación Convite recorre de 42,2 a 56,0 km menos por jornada que esa regla, con 30 jornadas por política en cada carga. Además, cuando los viajes se alargan, la regla pierde más. Con carga alta y las velocidades de la tesis UNAL, la regla baja 3,8 puntos en críticos a tiempo y Convite no cambia de forma medible. Por eso la ventaja de Convite crece 3,7 puntos en esa carga. Esa regla la escribimos nosotros, con toda la información a la vista. En una operación real alguien tendría que aplicarla a mano y rehacer las rutas con cada cierre, y Convite lo hace solo.

Marcas: por aprobar. Fuente de las velocidades: revisado por máquina; falta que una persona abra la tesis. La comparación entre las dos velocidades es pareada, sobre la misma red y las mismas semillas (9.3). La comparación con la sección 8.3 no es pareada.
