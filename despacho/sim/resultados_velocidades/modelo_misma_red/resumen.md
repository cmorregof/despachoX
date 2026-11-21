# Resultados de la simulación

Generado el 2026-11-21 07:23 con `python -m despacho.sim.correr`. Commit `513b88a`.

- Red: OpenStreetMap (manizales_region.graphml, 7825 nodos).
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
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 86,0 (12,4) | 99,1 (2,9) | 93,2 (9,9) | 99,3 (3,7) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,1 (1,6) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 95,0 (5,1) | 98,6 (4,3) | 96,9 (5,4) | 97,8 (4,7) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,0) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,4 (0,5) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Tiempo medio del pedido a la entrega (h) | 1,73 (0,52) | 1,69 (0,54) | 1,60 (0,52) | 1,72 (0,51) |
| Tiempo máximo del pedido a la entrega (h) | 5,38 (1,54) | 6,60 (1,95) | 5,21 (1,64) | 6,90 (1,85) |
| Tiempo medio de espera en el punto peor atendido (h) | 4,43 (1,13) | 5,13 (1,70) | 4,08 (1,21) | 5,41 (1,95) |
| Kilómetros recorridos por la flota | 677,6 (210,5) | 665,9 (213,0) | 647,8 (206,7) | 603,3 (187,6) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,2 (0,9) | 1,4 (1,0) | 1,5 (1,1) | 1,0 (1,1) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 51,9 (11,2) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,77 (0,89) | 1,48 (0,12) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,77 (0,89) | 1,95 (0,30) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 13,3 | [8,6; 18,0] | 23 / 7 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,1 | [−1,7; −0,5] | 15 / 15 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,9 | [1,6; 4,1] | 21 / 6 / 3 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,4 | [−0,6; −0,2] | 14 / 16 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,01 | [−0,09; 0,06] | 15 / 0 / 15 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 0,98 | [0,38; 1,58] | 9 / 0 / 21 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −74,3 | [−95,2; −53,4] | 26 / 0 / 4 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,3 | [−0,9; 1,4] | 2 / 27 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,8 | [−1,8; 0,2] | 6 / 16 / 8 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,03 | [−0,03; 0,09] | 14 / 0 / 16 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,28 | [−0,17; 0,73] | 15 / 0 / 15 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −62,6 | [−82,0; −43,2] | 27 / 0 / 3 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 6,2 | [2,6; 9,8] | 15 / 15 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,9 | [0,1; 1,7] | 14 / 10 / 6 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,12 | [0,08; 0,16] | 1 / 0 / 29 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 1,33 | [0,87; 1,78] | 2 / 0 / 28 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −44,5 | [−59,8; −29,2] | 28 / 0 / 2 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 7,1 | [3,3; 10,9] | 21 / 7 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,1 | [−1,7; −0,5] | 15 / 15 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,9 | [0,8; 3,1] | 20 / 7 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,4 | [−0,6; −0,2] | 14 / 16 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,13 | [−0,20; −0,06] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,35 | [−0,73; 0,03] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −29,8 | [−48,6; −11,1] | 24 / 0 / 6 |

## Carga media

Escenarios: 49 puntos, 125 pedidos, 40,3 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 66,2 (19,9) | 97,9 (3,4) | 76,8 (15,3) | 98,8 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 2,2 (2,1) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 85,9 (10,8) | 93,3 (9,0) | 89,8 (9,3) | 90,7 (7,8) |
| Pedidos entregados dentro de la jornada (%) | 99,9 (0,5) | 99,9 (0,6) | 99,9 (0,4) | 99,8 (0,8) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,9 (1,0) | 0,1 (0,6) | 0,1 (0,5) | 0,2 (1,1) |
| Tiempo medio del pedido a la entrega (h) | 2,67 (0,73) | 2,59 (0,68) | 2,49 (0,67) | 2,61 (0,66) |
| Tiempo máximo del pedido a la entrega (h) | 6,65 (1,60) | 9,38 (1,76) | 6,51 (1,54) | 9,89 (1,86) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,33 (1,37) | 7,38 (1,91) | 5,19 (1,20) | 8,00 (2,32) |
| Kilómetros recorridos por la flota | 805,9 (269,9) | 801,5 (259,5) | 768,6 (251,0) | 750,0 (247,5) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,2) |
| Regresos al acopio por vías no aptas para el vehículo | 1,5 (1,0) | 1,5 (1,3) | 1,4 (1,1) | 1,0 (0,9) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 65,8 (13,5) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,15) | 1,52 (0,14) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,15) | 1,93 (0,31) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 32,5 | [25,1; 39,9] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,2 | [−3,0; −1,4] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,9 | [2,8; 6,9] | 24 / 3 / 3 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,7 | [−1,1; −0,3] | 20 / 9 / 1 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,06 | [−0,16; 0,05] | 20 / 0 / 10 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,67 | [2,13; 3,21] | 2 / 0 / 28 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −55,9 | [−82,1; −29,8] | 26 / 0 / 4 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,9 | [−0,2; 2,1] | 6 / 22 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,6 | [−4,1; −1,0] | 6 / 2 / 22 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [−0,1; 0,3] | 0 / 28 / 2 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,02 | [−0,07; 0,11] | 16 / 0 / 14 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,62 | [0,21; 1,03] | 8 / 0 / 22 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −51,5 | [−70,6; −32,3] | 26 / 0 / 4 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 22,0 | [16,4; 27,6] | 27 / 3 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,9 | [−0,5; 2,3] | 15 / 4 / 11 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [−0,3; 0,4] | 1 / 27 / 2 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,12 | [0,06; 0,18] | 3 / 0 / 27 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,81 | [2,23; 3,40] | 2 / 0 / 28 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −18,6 | [−34,0; −3,2] | 20 / 0 / 10 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,6 | [6,7; 14,4] | 25 / 2 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,2 | [−3,0; −1,4] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,0 | [2,5; 5,4] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,8 | [−1,1; −0,5] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,18 | [−0,25; −0,11] | 24 / 0 / 6 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,15 | [−0,44; 0,15] | 19 / 0 / 11 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −37,3 | [−54,8; −19,9] | 25 / 0 / 5 |

## Carga alta

Escenarios: 49 puntos, 149 pedidos, 47,8 t, 7,5 vehículos y 5,6 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 49,5 (18,5) | 95,6 (5,5) | 64,1 (15,3) | 98,4 (3,3) |
| Kilos perecederos que vencieron sin entregarse (%) | 3,9 (2,7) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 73,9 (13,6) | 82,5 (12,4) | 79,3 (12,0) | 79,8 (9,9) |
| Pedidos entregados dentro de la jornada (%) | 98,9 (3,1) | 98,8 (3,5) | 99,2 (2,4) | 98,5 (3,6) |
| Kilos pedidos que no llegaron en buen estado (%) | 2,5 (3,4) | 1,5 (4,1) | 1,0 (3,1) | 1,8 (4,6) |
| Tiempo medio del pedido a la entrega (h) | 3,53 (0,79) | 3,42 (0,69) | 3,32 (0,75) | 3,38 (0,63) |
| Tiempo máximo del pedido a la entrega (h) | 7,87 (1,49) | 10,91 (1,52) | 7,63 (1,67) | 12,08 (1,35) |
| Tiempo medio de espera en el punto peor atendido (h) | 6,36 (1,46) | 9,30 (2,03) | 6,08 (1,29) | 10,05 (2,35) |
| Kilómetros recorridos por la flota | 936,8 (296,3) | 929,8 (299,2) | 900,8 (289,2) | 885,2 (289,4) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,6 (1,1) | 1,7 (1,6) | 1,3 (1,3) | 0,9 (1,0) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 76,6 (15,9) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,17) | 1,55 (0,12) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,17) | 1,89 (0,20) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 48,9 | [42,0; 55,9] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,9 | [−5,0; −2,9] | 27 / 3 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,9 | [4,0; 7,9] | 26 / 2 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,7 | [−1,4; 0,0] | 25 / 3 / 2 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,14 | [−0,26; −0,02] | 23 / 0 / 7 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,69 | [3,02; 4,37] | 0 / 0 / 30 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −51,6 | [−71,3; −32,0] | 28 / 0 / 2 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 2,8 | [0,8; 4,7] | 13 / 14 / 3 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,7 | [−4,2; −1,1] | 7 / 1 / 22 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,3 | [−0,1; 0,7] | 2 / 22 / 6 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,11; 0,03] | 20 / 0 / 10 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,75 | [0,38; 1,12] | 9 / 1 / 20 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −44,6 | [−66,2; −23,0] | 24 / 0 / 6 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 34,3 | [28,6; 40,0] | 30 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,5 | [−1,1; 2,0] | 14 / 4 / 12 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,8 | [0,0; 1,6] | 4 / 19 / 7 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,07 | [−0,02; 0,15] | 9 / 0 / 21 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,97 | [3,30; 4,65] | 0 / 0 / 30 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −15,6 | [−29,2; −2,0] | 20 / 0 / 10 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 14,6 | [10,0; 19,2] | 27 / 1 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,9 | [−5,0; −2,9] | 27 / 3 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,5 | [3,9; 7,0] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,5 | [−2,1; −0,9] | 25 / 3 / 2 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,21 | [−0,28; −0,14] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,28 | [−0,51; −0,05] | 21 / 0 / 9 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −36,0 | [−55,0; −17,1] | 21 / 0 / 9 |

