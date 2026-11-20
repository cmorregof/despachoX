# Resultados de la simulación

Generado el 2026-11-20 15:49 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261150 a 20261179, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: FACTOR_CRITICO = 3.

## Carga holgada

Escenarios: 49 puntos, 100 pedidos, 32,1 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 89,7 (11,9) | 99,5 (2,0) | 94,6 (5,7) | 99,8 (1,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,0 (1,3) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 95,8 (5,1) | 99,1 (1,8) | 97,7 (3,3) | 98,9 (2,7) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,0) | 99,9 (0,3) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,3 (0,5) | 0,0 (0,0) | 0,0 (0,0) | 0,1 (0,2) |
| Tiempo medio del pedido a la entrega (h) | 1,63 (0,50) | 1,60 (0,49) | 1,52 (0,43) | 1,63 (0,46) |
| Tiempo máximo del pedido a la entrega (h) | 4,77 (1,10) | 6,08 (1,62) | 4,56 (0,86) | 6,57 (1,65) |
| Tiempo medio de espera en el punto peor atendido (h) | 3,90 (1,03) | 5,07 (1,65) | 3,72 (0,95) | 5,30 (1,85) |
| Kilómetros recorridos por la flota | 625,5 (188,8) | 623,5 (185,8) | 603,0 (182,8) | 572,4 (172,2) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,2 (1,5) | 2,0 (1,4) | 2,3 (1,7) | 1,8 (1,5) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 54,2 (11,9) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,29 (0,08) | 1,21 (0,08) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,29 (0,08) | 1,33 (0,08) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,1 | [5,8; 14,4] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,0 | [−1,5; −0,5] | 16 / 14 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,1 | [1,9; 4,2] | 23 / 7 / 0 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,3 | [−0,5; −0,1] | 14 / 14 / 2 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,04; 0,05] | 11 / 0 / 19 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 1,41 | [0,90; 1,92] | 4 / 0 / 26 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −53,1 | [−64,6; −41,5] | 29 / 0 / 1 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,3 | [−0,6; 1,2] | 2 / 27 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,2 | [−0,7; 0,4] | 9 / 15 / 6 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [0,0; 0,2] | 0 / 28 / 2 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,03 | [−0,02; 0,07] | 10 / 0 / 20 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,23 | [−0,21; 0,67] | 13 / 0 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −51,1 | [−62,6; −39,5] | 29 / 0 / 1 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 5,2 | [3,2; 7,2] | 18 / 12 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,2 | [0,6; 1,8] | 16 / 13 / 1 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [0,0; 0,2] | 0 / 28 / 2 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,11 | [0,08; 0,14] | 2 / 0 / 28 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 1,58 | [1,06; 2,11] | 3 / 0 / 27 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −30,6 | [−41,3; −19,8] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 4,9 | [1,5; 8,2] | 16 / 10 / 4 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,0 | [−1,5; −0,5] | 16 / 14 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,8 | [0,9; 2,8] | 18 / 9 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,3 | [−0,5; −0,2] | 15 / 15 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,11 | [−0,15; −0,07] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,18 | [−0,52; 0,17] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −22,5 | [−31,2; −13,8] | 24 / 0 / 6 |

## Carga media

Escenarios: 49 puntos, 125 pedidos, 40,3 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 70,9 (17,0) | 97,8 (6,1) | 80,7 (14,3) | 99,5 (1,6) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,8 (1,8) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 88,8 (8,2) | 94,7 (7,5) | 91,6 (7,0) | 92,8 (6,8) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,0) | 99,9 (0,3) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,6 (0,6) | 0,0 (0,0) | 0,0 (0,0) | 0,1 (0,3) |
| Tiempo medio del pedido a la entrega (h) | 2,49 (0,67) | 2,47 (0,64) | 2,36 (0,62) | 2,47 (0,63) |
| Tiempo máximo del pedido a la entrega (h) | 6,07 (1,52) | 8,71 (1,77) | 5,73 (1,21) | 9,64 (1,65) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,04 (1,17) | 7,07 (1,73) | 4,74 (1,01) | 7,88 (2,00) |
| Kilómetros recorridos por la flota | 745,8 (237,8) | 754,4 (236,7) | 721,3 (224,0) | 694,9 (220,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,3 (1,6) | 2,3 (1,9) | 2,3 (1,8) | 2,0 (1,4) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 65,3 (12,2) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,36 (0,11) | 1,30 (0,09) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,36 (0,11) | 1,48 (0,12) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 28,6 | [22,4; 34,7] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,5; −1,1] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,0 | [2,4; 5,6] | 26 / 0 / 4 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,8; −0,3] | 20 / 8 / 2 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,08; 0,03] | 18 / 0 / 12 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,84 | [2,31; 3,37] | 1 / 0 / 29 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −50,9 | [−67,6; −34,2] | 27 / 0 / 3 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 1,7 | [−0,7; 4,0] | 6 / 22 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,9 | [−3,5; −0,3] | 7 / 6 / 17 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [0,0; 0,2] | 0 / 28 / 2 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,06; 0,06] | 14 / 0 / 16 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,81 | [0,37; 1,25] | 6 / 0 / 24 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −59,5 | [−73,0; −46,0] | 28 / 0 / 2 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 18,8 | [13,8; 23,9] | 27 / 3 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,2 | [0,0; 2,5] | 19 / 3 / 8 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [0,0; 0,2] | 0 / 28 / 2 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,11 | [0,07; 0,15] | 4 / 0 / 26 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,13 | [2,62; 3,64] | 0 / 0 / 30 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −26,5 | [−40,9; −12,0] | 24 / 0 / 6 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 9,7 | [5,8; 13,6] | 21 / 8 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,5; −1,1] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,8 | [1,6; 4,0] | 21 / 6 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,14 | [−0,18; −0,09] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,29 | [−0,57; −0,02] | 21 / 0 / 9 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −24,5 | [−38,0; −10,9] | 22 / 0 / 8 |

## Carga alta

Escenarios: 49 puntos, 149 pedidos, 47,8 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 51,4 (17,1) | 98,1 (3,3) | 63,3 (17,5) | 98,9 (2,9) |
| Kilos perecederos que vencieron sin entregarse (%) | 3,2 (2,8) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 76,5 (12,1) | 85,2 (10,8) | 80,9 (11,9) | 83,5 (10,0) |
| Pedidos entregados dentro de la jornada (%) | 99,7 (0,8) | 99,8 (0,4) | 99,9 (0,3) | 99,4 (1,3) |
| Kilos pedidos que no llegaron en buen estado (%) | 1,4 (1,4) | 0,2 (0,5) | 0,1 (0,5) | 0,7 (1,7) |
| Tiempo medio del pedido a la entrega (h) | 3,36 (0,78) | 3,31 (0,72) | 3,20 (0,77) | 3,27 (0,73) |
| Tiempo máximo del pedido a la entrega (h) | 7,27 (1,26) | 10,60 (1,67) | 6,90 (1,09) | 11,60 (1,59) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,82 (1,18) | 8,74 (1,83) | 5,54 (1,16) | 9,63 (2,42) |
| Kilómetros recorridos por la flota | 883,8 (286,6) | 875,2 (285,0) | 857,4 (266,7) | 828,3 (257,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,7 (1,9) | 2,7 (2,3) | 2,6 (2,0) | 1,9 (1,5) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 76,6 (14,9) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,39 (0,11) | 1,34 (0,08) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,39 (0,11) | 1,52 (0,12) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 47,5 | [41,2; 53,7] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,2 | [−4,3; −2,2] | 25 / 5 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 7,0 | [5,0; 8,9] | 27 / 0 / 3 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,7 | [−1,3; 0,0] | 21 / 4 / 5 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,10 | [−0,16; −0,03] | 24 / 0 / 6 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,81 | [3,08; 4,53] | 1 / 0 / 29 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −55,5 | [−72,4; −38,6] | 27 / 0 / 3 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,8 | [−0,6; 2,2] | 8 / 19 / 3 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,7 | [−3,2; −0,2] | 7 / 5 / 18 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,5 | [0,0; 1,1] | 2 / 20 / 8 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,11; 0,04] | 17 / 0 / 13 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,89 | [0,33; 1,45] | 9 / 0 / 21 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −46,9 | [−65,0; −28,7] | 24 / 0 / 6 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 35,6 | [29,4; 41,8] | 30 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,6 | [1,0; 4,2] | 22 / 1 / 7 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,6 | [0,1; 1,1] | 0 / 22 / 8 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,07 | [0,03; 0,12] | 9 / 0 / 21 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 4,10 | [3,40; 4,79] | 0 / 0 / 30 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −29,1 | [−38,7; −19,4] | 26 / 0 / 4 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 11,8 | [8,9; 14,7] | 26 / 3 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,2 | [−4,3; −2,2] | 25 / 5 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,4 | [3,0; 5,7] | 27 / 2 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,3 | [−1,8; −0,8] | 25 / 5 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,17 | [−0,22; −0,11] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,29 | [−0,55; −0,03] | 22 / 0 / 8 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −26,4 | [−40,8; −12,0] | 25 / 0 / 5 |

