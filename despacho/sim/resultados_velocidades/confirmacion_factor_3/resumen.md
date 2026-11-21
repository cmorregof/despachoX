# Resultados de la simulación

Generado el 2026-11-21 00:33 con `python -m despacho.sim.correr`. Commit `1489760`.

- Red: OpenStreetMap (manizales_region.graphml, 7825 nodos), velocidades medidas de datos_publicos/velocidades.csv.
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo, velocidades medidas).
- Semillas: 30 por nivel de carga, de 20261150 a 20261179, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: velocidades medidas de datos_publicos/velocidades.csv, también en el optimizador; FACTOR_CRITICO = 3.

## Carga holgada

Escenarios: 49 puntos, 100 pedidos, 32,1 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 75,9 (15,4) | 97,7 (3,9) | 86,4 (14,9) | 99,2 (3,0) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,4 (1,8) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 90,4 (8,8) | 95,2 (8,6) | 92,9 (9,5) | 94,8 (6,9) |
| Pedidos entregados dentro de la jornada (%) | 99,9 (0,6) | 99,8 (0,6) | 99,9 (0,6) | 99,9 (0,5) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (1,0) | 0,2 (0,8) | 0,2 (0,9) | 0,2 (0,7) |
| Tiempo medio del pedido a la entrega (h) | 2,22 (0,67) | 2,19 (0,70) | 2,04 (0,69) | 2,15 (0,68) |
| Tiempo máximo del pedido a la entrega (h) | 6,24 (1,60) | 7,99 (1,88) | 6,14 (1,46) | 8,35 (2,13) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,14 (1,41) | 6,96 (1,97) | 4,91 (1,06) | 7,09 (2,33) |
| Kilómetros recorridos por la flota | 623,0 (184,6) | 615,9 (184,3) | 585,9 (179,9) | 569,9 (173,6) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,3 (1,3) | 1,1 (1,4) | 1,2 (1,2) | 1,0 (1,1) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 55,7 (11,0) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,46 (0,18) | 1,37 (0,13) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,46 (0,18) | 1,72 (0,28) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 23,3 | [17,4; 29,1] | 26 / 4 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,4 | [−2,1; −0,8] | 20 / 10 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,3 | [2,4; 6,3] | 25 / 3 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,5 | [−0,9; 0,0] | 19 / 10 / 1 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,07 | [−0,18; 0,03] | 18 / 0 / 12 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 1,95 | [1,36; 2,53] | 3 / 0 / 27 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −53,1 | [−71,2; −34,9] | 27 / 0 / 3 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 1,5 | [0,2; 2,8] | 8 / 20 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,5 | [−1,9; 0,9] | 9 / 6 / 15 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | −0,1 | [−0,5; 0,3] | 2 / 26 / 2 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,10; 0,01] | 19 / 0 / 11 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,13 | [−0,36; 0,63] | 13 / 0 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −46,0 | [−63,3; −28,7] | 27 / 0 / 3 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 12,7 | [7,5; 18,0] | 22 / 8 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,8 | [0,3; 3,4] | 17 / 5 / 8 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,5; 0,4] | 1 / 27 / 2 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,10 | [0,07; 0,14] | 5 / 0 / 25 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,18 | [1,54; 2,82] | 5 / 0 / 25 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −16,0 | [−29,6; −2,4] | 20 / 0 / 10 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,5 | [6,8; 14,2] | 22 / 6 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,4 | [−2,1; −0,8] | 20 / 10 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,5 | [1,0; 4,0] | 23 / 1 / 6 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,4 | [−0,7; −0,2] | 18 / 11 / 1 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,18 | [−0,28; −0,08] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,23 | [−0,55; 0,09] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −37,1 | [−51,4; −22,7] | 26 / 0 / 4 |

## Carga media

Escenarios: 49 puntos, 125 pedidos, 40,3 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 53,6 (18,2) | 94,6 (5,8) | 66,7 (15,8) | 98,3 (3,0) |
| Kilos perecederos que vencieron sin entregarse (%) | 3,4 (2,7) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 76,4 (13,6) | 84,8 (12,0) | 82,2 (12,4) | 84,0 (10,2) |
| Pedidos entregados dentro de la jornada (%) | 98,9 (3,3) | 99,2 (2,3) | 99,3 (2,3) | 99,1 (2,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 2,4 (3,9) | 1,0 (2,8) | 0,8 (2,6) | 1,2 (3,1) |
| Tiempo medio del pedido a la entrega (h) | 3,32 (0,81) | 3,24 (0,70) | 3,08 (0,74) | 3,17 (0,68) |
| Tiempo máximo del pedido a la entrega (h) | 7,80 (1,75) | 11,09 (1,58) | 7,37 (1,74) | 11,41 (1,70) |
| Tiempo medio de espera en el punto peor atendido (h) | 6,46 (1,77) | 9,00 (1,65) | 6,03 (1,67) | 9,53 (2,26) |
| Kilómetros recorridos por la flota | 760,5 (232,3) | 755,8 (238,3) | 715,0 (220,9) | 699,8 (212,1) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,4 (1,4) | 1,4 (1,4) | 1,4 (1,5) | 1,1 (1,2) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 67,0 (13,3) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,29) | 1,55 (0,19) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,29) | 2,11 (0,49) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 44,7 | [37,7; 51,6] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,4 | [−4,4; −2,4] | 25 / 5 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 7,6 | [5,2; 9,9] | 26 / 1 / 3 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,2 | [−2,3; −0,1] | 23 / 4 / 3 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,15 | [−0,26; −0,04] | 24 / 0 / 6 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,07 | [2,46; 3,68] | 1 / 0 / 29 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −60,6 | [−82,4; −38,9] | 27 / 0 / 3 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 3,7 | [1,7; 5,7] | 15 / 13 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,8 | [−3,1; 1,4] | 10 / 3 / 17 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,2 | [−0,4; 0,8] | 2 / 23 / 5 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,07 | [−0,18; 0,05] | 22 / 0 / 8 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,53 | [0,04; 1,02] | 9 / 0 / 21 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −56,0 | [−77,9; −34,0] | 26 / 0 / 4 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 31,6 | [25,5; 37,7] | 30 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,8 | [0,1; 3,5] | 17 / 3 / 10 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,4 | [−0,5; 1,2] | 3 / 21 / 6 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,09 | [0,02; 0,16] | 10 / 0 / 20 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,49 | [3,02; 3,97] | 0 / 0 / 30 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −15,1 | [−32,2; 1,9] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 13,1 | [9,0; 17,2] | 26 / 3 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,4 | [−4,4; −2,4] | 25 / 5 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,7 | [3,9; 7,5] | 26 / 3 / 1 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,6 | [−2,2; −0,9] | 24 / 5 / 1 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,24 | [−0,33; −0,15] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,42 | [−0,79; −0,06] | 21 / 0 / 9 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −45,5 | [−61,9; −29,2] | 27 / 0 / 3 |

## Carga alta

Escenarios: 49 puntos, 149 pedidos, 47,8 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 40,5 (13,4) | 91,9 (6,9) | 56,0 (15,0) | 98,4 (2,8) |
| Kilos perecederos que vencieron sin entregarse (%) | 5,6 (3,3) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 62,4 (14,6) | 70,3 (13,9) | 68,2 (14,7) | 73,2 (10,8) |
| Pedidos entregados dentro de la jornada (%) | 94,9 (7,0) | 95,0 (7,1) | 96,0 (6,3) | 94,8 (6,6) |
| Kilos pedidos que no llegaron en buen estado (%) | 7,1 (8,0) | 6,3 (8,9) | 4,7 (7,5) | 6,9 (8,9) |
| Tiempo medio del pedido a la entrega (h) | 4,21 (0,81) | 4,00 (0,54) | 3,97 (0,81) | 3,80 (0,46) |
| Tiempo máximo del pedido a la entrega (h) | 9,02 (1,49) | 12,31 (1,30) | 8,54 (1,43) | 12,89 (0,84) |
| Tiempo medio de espera en el punto peor atendido (h) | 7,56 (1,71) | 10,77 (1,86) | 7,20 (1,67) | 11,37 (2,29) |
| Kilómetros recorridos por la flota | 842,3 (248,7) | 840,5 (251,6) | 813,0 (237,6) | 798,3 (241,7) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,4 (1,4) | 1,5 (1,6) | 1,5 (1,6) | 1,2 (1,1) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 77,9 (14,2) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,66 (0,35) | 1,64 (0,19) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,66 (0,35) | 2,45 (0,60) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 57,9 | [52,7; 63,1] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −5,6 | [−6,8; −4,3] | 29 / 1 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 10,8 | [8,4; 13,3] | 29 / 0 / 1 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,2 | [−1,4; 1,1] | 18 / 0 / 12 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,41 | [−0,59; −0,24] | 25 / 0 / 5 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,82 | [3,21; 4,43] | 0 / 0 / 30 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −44,0 | [−59,4; −28,7] | 26 / 0 / 4 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 6,5 | [4,4; 8,7] | 23 / 6 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,0 | [0,7; 5,3] | 23 / 0 / 7 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,6 | [−0,7; 1,9] | 9 / 10 / 11 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,20 | [−0,30; −0,09] | 24 / 0 / 6 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,61 | [0,17; 1,04] | 10 / 2 / 18 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −42,2 | [−56,8; −27,6] | 26 / 0 / 4 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 42,4 | [36,6; 48,1] | 30 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,0 | [2,7; 7,3] | 21 / 1 / 8 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 2,2 | [0,9; 3,6] | 4 / 11 / 15 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | −0,17 | [−0,35; 0,01] | 14 / 0 / 16 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 4,17 | [3,51; 4,84] | 0 / 0 / 30 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −14,7 | [−27,5; −1,8] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 15,5 | [12,9; 18,1] | 28 / 2 / 0 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −5,6 | [−6,8; −4,3] | 29 / 1 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,8 | [3,7; 8,0] | 23 / 3 / 4 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −2,4 | [−3,5; −1,3] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,24 | [−0,32; −0,16] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,36 | [−0,74; 0,02] | 20 / 0 / 10 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −29,4 | [−43,7; −15,0] | 23 / 0 / 7 |

