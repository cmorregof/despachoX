# Resultados de la simulación

Generado el 2026-11-20 17:13 con `python -m despacho.sim.correr`. Commit `48a35ea`.

- Red: OpenStreetMap (manizales_region.graphml, 7825 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 70,4 (15,0) | 99,1 (1,7) | 80,9 (15,7) | 98,3 (2,5) |
| Kilos perecederos que vencieron sin entregarse (%) | 2,1 (2,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,1 (5,6) | 94,9 (5,4) | 91,8 (6,6) | 92,8 (5,7) |
| Pedidos entregados dentro de la jornada (%) | 99,8 (0,5) | 99,9 (0,5) | 99,9 (0,5) | 99,9 (0,4) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,9 (0,8) | 0,1 (0,5) | 0,1 (0,5) | 0,1 (0,3) |
| Tiempo medio del pedido a la entrega (h) | 2,48 (0,45) | 2,48 (0,53) | 2,35 (0,54) | 2,47 (0,54) |
| Tiempo máximo del pedido a la entrega (h) | 6,35 (1,10) | 9,15 (1,64) | 6,23 (1,37) | 9,64 (1,35) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,83 (1,77) | 7,57 (1,79) | 5,42 (1,78) | 7,59 (2,06) |
| Kilómetros recorridos por la flota | 893,1 (351,3) | 880,4 (333,4) | 849,8 (322,5) | 820,3 (315,1) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,8 (1,4) | 1,9 (1,3) | 2,0 (1,4) | 1,8 (1,5) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 70,1 (17,8) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,65 (0,18) | 1,49 (0,14) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,65 (0,18) | 1,73 (0,19) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 28,0 | [22,4; 33,6] | 29 / 1 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,1 | [−2,9; −1,4] | 23 / 7 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,7 | [2,4; 5,0] | 25 / 1 / 4 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,8 | [−1,1; −0,5] | 22 / 8 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,01 | [−0,09; 0,07] | 16 / 0 / 14 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 1,76 | [0,95; 2,57] | 6 / 1 / 23 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −72,9 | [−100,7; −45,0] | 27 / 0 / 3 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,8 | [−1,9; 0,3] | 4 / 18 / 8 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,1 | [−2,9; −1,3] | 3 / 4 / 23 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | −0,1 | [−0,2; 0,1] | 1 / 29 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,01 | [−0,07; 0,05] | 15 / 0 / 15 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,02 | [−0,51; 0,56] | 12 / 1 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −60,1 | [−79,8; −40,5] | 27 / 0 / 3 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 17,5 | [11,7; 23,2] | 25 / 5 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,9 | [−0,4; 2,3] | 15 / 5 / 10 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,1; 0,0] | 1 / 29 / 0 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,12 | [0,08; 0,15] | 4 / 0 / 26 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,17 | [1,40; 2,93] | 4 / 1 / 25 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −29,6 | [−40,1; −19,0] | 26 / 0 / 4 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,5 | [6,8; 14,2] | 25 / 2 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,1 | [−2,9; −1,4] | 23 / 7 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,8 | [1,6; 3,9] | 25 / 2 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,8 | [−1,0; −0,5] | 22 / 8 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,13 | [−0,20; −0,05] | 24 / 0 / 6 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,40 | [−0,82; 0,01] | 19 / 2 / 9 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −43,3 | [−67,3; −19,3] | 23 / 0 / 7 |

