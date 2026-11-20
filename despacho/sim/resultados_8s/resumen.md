# Resultados de la simulación

Generado el 2026-11-20 14:44 con `python -m despacho.sim.correr`. Commit `3ffdf69`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 8 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `optimiza_una_vez` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,1 (15,7) | 98,5 (2,6) | 80,0 (14,9) | 98,4 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,8 (1,9) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,4 (5,9) | 95,6 (5,3) | 93,2 (4,6) | 93,8 (5,6) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (0,7) | 0,0 (0,1) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,39 (0,48) | 2,40 (0,55) | 2,24 (0,49) | 2,35 (0,52) |
| Tiempo máximo del pedido a la entrega (h) | 6,16 (0,96) | 8,75 (1,50) | 5,69 (0,98) | 9,62 (1,38) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,00 (1,13) | 7,09 (1,88) | 4,74 (0,94) | 7,30 (1,80) |
| Kilómetros recorridos por la flota | 836,5 (304,2) | 834,3 (297,9) | 803,3 (281,7) | 772,9 (262,5) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,7 (1,4) | 1,9 (1,4) | 1,8 (1,6) | 1,4 (1,2) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 1,0 (0,0) | 68,9 (16,5) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 8,40 (0,13) | 8,24 (0,21) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 8,40 (0,13) | 8,57 (0,19) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 29,2 | [23,7; 34,8] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,6; −1,1] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,4 | [3,2; 5,5] | 26 / 2 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 20 / 10 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,09; 0,01] | 21 / 0 / 9 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,30 | [1,61; 2,99] | 5 / 0 / 25 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −63,6 | [−83,3; −43,9] | 28 / 0 / 2 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,2 | [−1,5; 1,2] | 5 / 17 / 8 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,6; −1,0] | 2 / 5 / 23 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,05 | [−0,10; 0,00] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,21 | [−0,37; 0,79] | 10 / 0 / 20 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −61,4 | [−79,9; −42,9] | 27 / 0 / 3 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 18,3 | [12,9; 23,7] | 28 / 2 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,6 | [−0,4; 1,6] | 17 / 0 / 13 |
| `despachox` − `optimiza_una_vez` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `optimiza_una_vez` | Tiempo medio del pedido a la entrega (h) | 0,12 | [0,08; 0,15] | 3 / 0 / 27 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,56 | [1,93; 3,20] | 2 / 0 / 28 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −30,4 | [−42,5; −18,2] | 25 / 0 / 5 |
| `optimiza_una_vez` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,9 | [7,7; 14,1] | 26 / 2 / 2 |
| `optimiza_una_vez` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,6; −1,1] | 21 / 9 / 0 |
| `optimiza_una_vez` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,8 | [2,7; 4,8] | 26 / 1 / 3 |
| `optimiza_una_vez` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 20 / 10 / 0 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,15 | [−0,20; −0,11] | 27 / 0 / 3 |
| `optimiza_una_vez` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | −0,26 | [−0,49; −0,02] | 18 / 1 / 11 |
| `optimiza_una_vez` − `ingenua` | Kilómetros recorridos por la flota | −33,2 | [−44,5; −21,9] | 25 / 0 / 5 |

