# Resultados de la simulación

Generado el 2026-11-20 11:52 con `python -m despacho.sim.correr`. Commit `d33dd27`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.

## Carga holgada

Escenarios: 56 puntos, 111 pedidos, 35,3 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 87,7 (12,2) | 99,5 (1,8) | 93,0 (8,3) | 99,7 (1,2) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,5 (1,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 96,4 (3,0) | 99,3 (1,2) | 98,0 (2,1) | 99,3 (1,7) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,2 (0,4) | 0,0 (0,1) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 1,55 (0,39) | 1,60 (0,45) | 1,50 (0,38) | 1,59 (0,40) |
| Tiempo máximo del pedido a la entrega (h) | 4,94 (0,90) | 6,30 (1,49) | 4,87 (1,16) | 6,53 (1,54) |
| Tiempo medio de espera en el punto peor atendido (h) | 4,06 (0,93) | 5,13 (1,45) | 4,00 (1,27) | 4,99 (1,46) |
| Kilómetros recorridos por la flota | 703,8 (241,5) | 707,9 (240,9) | 677,5 (227,9) | 632,8 (208,4) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,5 (1,4) | 1,8 (1,6) | 1,7 (1,4) | 1,3 (1,2) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 55,4 (12,9) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,33 (0,11) | 1,20 (0,08) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,33 (0,11) | 1,36 (0,10) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 12,0 | [7,5; 16,5] | 25 / 5 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −0,5 | [−0,9; −0,1] | 8 / 22 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,9 | [2,1; 3,7] | 28 / 2 / 0 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,2 | [−0,3; 0,0] | 8 / 22 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | 0,04 | [0,00; 0,08] | 10 / 0 / 20 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 0,93 | [0,52; 1,35] | 6 / 1 / 23 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −70,9 | [−88,1; −53,7] | 29 / 0 / 1 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,2 | [−0,6; 1,1] | 3 / 25 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,1 | [−0,5; 0,4] | 6 / 21 / 3 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,01 | [−0,05; 0,03] | 12 / 0 / 18 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | −0,13 | [−0,55; 0,28] | 15 / 1 / 14 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −75,1 | [−92,8; −57,4] | 29 / 0 / 1 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 6,7 | [3,7; 9,7] | 17 / 13 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,3 | [0,7; 1,9] | 18 / 10 / 2 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,10 | [0,07; 0,13] | 2 / 0 / 28 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 0,99 | [0,41; 1,57] | 6 / 1 / 23 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −44,7 | [−56,9; −32,4] | 28 / 0 / 2 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 5,3 | [2,2; 8,4] | 17 / 12 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −0,5 | [−0,9; −0,1] | 8 / 22 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,6 | [0,9; 2,3] | 23 / 5 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,2 | [−0,3; 0,0] | 8 / 22 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,06 | [−0,09; −0,02] | 22 / 0 / 8 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,06 | [−0,47; 0,35] | 20 / 1 / 9 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −26,3 | [−37,9; −14,7] | 24 / 0 / 6 |

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,1 (15,7) | 98,5 (2,6) | 80,6 (14,0) | 98,1 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,8 (1,9) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,4 (5,9) | 95,6 (5,3) | 93,5 (4,5) | 93,8 (5,8) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (0,7) | 0,0 (0,1) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,39 (0,48) | 2,40 (0,55) | 2,25 (0,50) | 2,37 (0,53) |
| Tiempo máximo del pedido a la entrega (h) | 6,16 (0,96) | 8,75 (1,50) | 5,56 (0,87) | 9,70 (1,50) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,00 (1,13) | 7,09 (1,88) | 4,88 (0,94) | 7,27 (1,78) |
| Kilómetros recorridos por la flota | 836,5 (304,2) | 834,3 (297,9) | 802,6 (282,6) | 778,9 (269,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,7 (1,4) | 1,9 (1,4) | 1,7 (1,5) | 1,3 (1,2) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 69,0 (16,1) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,34 (0,10) | 1,26 (0,09) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,34 (0,10) | 1,39 (0,11) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 28,9 | [23,2; 34,7] | 29 / 1 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,6; −1,1] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,4 | [3,1; 5,7] | 28 / 0 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 20 / 10 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,02 | [−0,07; 0,03] | 20 / 0 / 10 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,27 | [1,61; 2,94] | 4 / 1 / 25 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −57,6 | [−77,1; −38,2] | 28 / 0 / 2 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,5 | [−1,8; 0,9] | 5 / 15 / 10 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,7; −1,0] | 3 / 2 / 25 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,09; 0,03] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,18 | [−0,34; 0,71] | 12 / 1 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −55,5 | [−73,1; −37,9] | 25 / 0 / 5 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 17,5 | [12,4; 22,5] | 25 / 5 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,3 | [−0,6; 1,2] | 15 / 2 / 13 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,12 | [0,08; 0,16] | 3 / 0 / 27 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,39 | [1,77; 3,01] | 1 / 1 / 28 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −23,7 | [−36,7; −10,7] | 21 / 0 / 9 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 11,5 | [8,6; 14,4] | 29 / 1 / 0 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,6; −1,1] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,1 | [3,0; 5,2] | 28 / 2 / 0 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 20 / 10 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,14 | [−0,18; −0,10] | 28 / 0 / 2 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,12 | [−0,36; 0,12] | 16 / 1 / 13 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −33,9 | [−46,7; −21,2] | 25 / 0 / 5 |

## Carga alta

Escenarios: 56 puntos, 166 pedidos, 52,8 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 49,6 (17,5) | 97,6 (3,7) | 60,1 (17,6) | 95,9 (4,2) |
| Kilos perecederos que vencieron sin entregarse (%) | 3,5 (2,4) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 78,3 (9,3) | 85,9 (8,2) | 82,3 (9,1) | 83,7 (7,1) |
| Pedidos entregados dentro de la jornada (%) | 99,8 (0,6) | 99,7 (0,8) | 99,8 (0,5) | 99,8 (0,5) |
| Kilos pedidos que no llegaron en buen estado (%) | 1,3 (1,0) | 0,4 (1,1) | 0,2 (0,6) | 0,3 (0,6) |
| Tiempo medio del pedido a la entrega (h) | 3,26 (0,51) | 3,28 (0,58) | 3,13 (0,54) | 3,28 (0,59) |
| Tiempo máximo del pedido a la entrega (h) | 7,40 (1,04) | 10,74 (1,40) | 6,90 (1,03) | 12,04 (1,21) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,83 (1,24) | 9,12 (1,76) | 5,80 (1,26) | 10,08 (1,34) |
| Kilómetros recorridos por la flota | 1004,9 (360,9) | 1000,3 (361,3) | 976,3 (340,3) | 953,6 (325,3) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,0 (1,7) | 2,1 (1,6) | 1,8 (1,5) | 1,3 (1,2) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 82,4 (19,1) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,39 (0,12) | 1,31 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,39 (0,12) | 1,45 (0,13) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 46,3 | [40,0; 52,6] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,5 | [−4,4; −2,6] | 28 / 2 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,4 | [4,0; 6,8] | 27 / 1 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,0 | [−1,3; −0,8] | 26 / 2 / 2 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | 0,02 | [−0,05; 0,09] | 19 / 0 / 11 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 4,25 | [3,67; 4,84] | 0 / 1 / 29 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −51,4 | [−77,7; −25,0] | 24 / 0 / 6 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −1,8 | [−3,6; 0,0] | 7 / 8 / 15 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,2 | [−3,7; −0,8] | 7 / 2 / 21 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | −0,1 | [−0,4; 0,2] | 3 / 24 / 3 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,07; 0,06] | 15 / 0 / 15 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,96 | [0,47; 1,45] | 6 / 1 / 23 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −46,7 | [−72,2; −21,2] | 23 / 0 / 7 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 35,7 | [29,5; 42,0] | 30 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,4 | [0,0; 2,7] | 20 / 2 / 8 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [0,0; 0,2] | 1 / 24 / 5 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,15 | [0,09; 0,21] | 6 / 0 / 24 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 4,28 | [3,74; 4,82] | 0 / 1 / 29 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −22,7 | [−39,5; −5,8] | 21 / 0 / 9 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,6 | [7,9; 13,3] | 28 / 0 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,5 | [−4,4; −2,6] | 28 / 2 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,0 | [2,8; 5,2] | 27 / 1 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,1 | [−1,4; −0,9] | 28 / 2 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,13 | [−0,18; −0,08] | 22 / 0 / 8 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,03 | [−0,37; 0,31] | 14 / 1 / 15 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −28,7 | [−44,6; −12,7] | 22 / 0 / 8 |

