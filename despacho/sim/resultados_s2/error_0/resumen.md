# Resultados de la simulación

Generado el 2026-11-20 16:00 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: error de ubicación de pedidos p = 0.0.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox_sin_confirmar` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,1 (15,7) | 98,5 (2,6) | 98,0 (3,2) | 98,2 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,8 (1,9) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,4 (5,9) | 95,6 (5,3) | 93,8 (5,7) | 93,8 (5,8) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (0,7) | 0,0 (0,1) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,39 (0,48) | 2,40 (0,55) | 2,37 (0,53) | 2,37 (0,53) |
| Tiempo máximo del pedido a la entrega (h) | 6,16 (0,96) | 8,75 (1,50) | 9,74 (1,47) | 9,69 (1,47) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,00 (1,13) | 7,09 (1,88) | 7,26 (1,77) | 7,28 (1,78) |
| Kilómetros recorridos por la flota | 836,5 (304,2) | 834,3 (297,9) | 775,9 (267,6) | 775,9 (269,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,7 (1,4) | 1,9 (1,4) | 1,3 (1,3) | 1,3 (1,3) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 69,0 (16,1) | 68,9 (16,0) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,35 (0,10) | 1,33 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,52 (0,13) | 1,49 (0,12) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 29,0 | [23,4; 34,7] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,8 | [−2,6; −1,1] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,4 | [3,1; 5,7] | 28 / 1 / 1 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 20 / 10 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,02 | [−0,07; 0,03] | 21 / 0 / 9 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,28 | [1,62; 2,94] | 4 / 1 / 25 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −60,6 | [−80,7; −40,5] | 28 / 0 / 2 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,4 | [−1,8; 1,0] | 5 / 16 / 9 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,6; −1,0] | 3 / 2 / 25 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,09; 0,02] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,19 | [−0,34; 0,71] | 11 / 1 / 18 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −58,4 | [−76,4; −40,5] | 25 / 0 / 5 |
| `despachox` − `despachox_sin_confirmar` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,2 | [−0,2; 0,6] | 1 / 29 / 0 |
| `despachox` − `despachox_sin_confirmar` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `despachox_sin_confirmar` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,1 | [−0,1; 0,2] | 2 / 27 / 1 |
| `despachox` − `despachox_sin_confirmar` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,01; 0,00] | 2 / 26 / 2 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio de espera en el punto peor atendido (h) | 0,02 | [−0,09; 0,12] | 2 / 27 / 1 |
| `despachox` − `despachox_sin_confirmar` | Kilómetros recorridos por la flota | 0,0 | [−2,5; 2,6] | 1 / 26 / 3 |
| `despachox_sin_confirmar` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,6 | [−2,0; 0,9] | 5 / 15 / 10 |
| `despachox_sin_confirmar` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox_sin_confirmar` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,6; −1,0] | 3 / 2 / 25 |
| `despachox_sin_confirmar` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,09; 0,03] | 18 / 0 / 12 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,17 | [−0,36; 0,69] | 12 / 0 / 18 |
| `despachox_sin_confirmar` − `experta` | Kilómetros recorridos por la flota | −58,5 | [−76,5; −40,5] | 25 / 0 / 5 |

