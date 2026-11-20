# Simulación: cuánto mejora DespachoX frente a un despacho sin optimizador

Estado: resultados de la primera corrida y de la segunda ronda (sección 8), del 20 de noviembre de 2026, sin revisar todavía por el equipo.

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

- **No prueba que DespachoX supere a un buen despachador humano cuando la información es perfecta.** Una regla simple de prioridad y de rotación de bodega iguala a DespachoX en críticos a tiempo y le gana por cerca de 2 puntos en entregas a tiempo de todos los puntos. Subir el peso de los puntos críticos no cambió eso (sección 8.2). DespachoX gana esa comparación con la flota corta (8.6) y cuando hay pedidos mal ubicados (8.4).
- **Mide solo en parte el valor de la entrada por chat.** La sección 8.4 modela un tipo de error, el pedido registrado en otro punto, y una corrección, la confirmación de ubicación. La tasa de error de 10 % o 20 % es nuestra y no tiene fuente. Además se supone que el despachador experto no confirma; uno que llame a cada comité tendría el mismo beneficio, a costa de un tiempo que no se modela.
- **No modela cierres registrados tarde ni falsos.** El encargo S2 lo proponía y se dejó por fuera: exige separar lo que sabe cada conductor de lo que sabe el despacho. Todo cierre reportado es cierto y se confirma en 5 minutos.
- **No mide la trazabilidad.** El código QR y la confirmación de entrega no entran en la simulación.
- **No valida los supuestos.** Las velocidades, los tiempos de carga y de entrega, los plazos por urgencia, la flota, la demanda y los cierres son nuestros. Ningún dato viene de una operación real del Banco de Alimentos ni de los organismos de socorro.
- **No dice cuál es la carga real.** Los niveles de carga se eligieron para que la línea base no quedara ni holgada ni colapsada. La magnitud de la ventaja sobre la política ingenua depende mucho de ese nivel y de la flota: va de 10 a 58 puntos en críticos a tiempo.
- **No representa bien los perecederos.** Hay un solo acopio, tanto inventario perecedero como demanda y lotes que vencen entre 6 y 48 horas. El efecto del empaque activo (patente UNAL), que `optimizar.py` ya modela, no se midió: con rotación por vencimiento el desperdicio ya es 0,0 % en estos escenarios, así que el empaque no tendría margen para mostrarse.
- **Describe la red urbana, no la ampliada.** Casi todas las corridas usan `manizales.graphml`, la red de Manizales y Villamaría con que se hizo la primera ronda. El producto usa ahora `manizales_region.graphml`, con los accesos; la sección 8.8 repite la carga media sobre esa red.
- **No incluye otros errores humanos.** El despachador aprueba siempre en 2 minutos y los conductores siguen el plan.
- **No cubre varios días.** Es una jornada de 14 horas, sin reabastecimiento ni cierres que se levanten.
- **No es exactamente reproducible.** La búsqueda del optimizador se corta por tiempo de reloj, así que repetir una corrida con las mismas semillas da cifras muy cercanas, pero no idénticas (sección 8.2).

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
