# Resultados de la simulación

Generado el 2026-11-20 16:39 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: 5 cierres por jornada.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox` |
|---|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 68,9 (16,1) | 98,1 (2,9) | 98,8 (2,8) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,9 (1,9) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,8 (6,0) | 95,4 (5,8) | 93,9 (6,2) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,3) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (0,7) | 0,0 (0,0) | 0,0 (0,2) |
| Tiempo medio del pedido a la entrega (h) | 2,38 (0,49) | 2,41 (0,56) | 2,35 (0,52) |
| Tiempo máximo del pedido a la entrega (h) | 6,07 (0,95) | 8,82 (1,58) | 9,58 (1,38) |
| Tiempo medio de espera en el punto peor atendido (h) | 4,91 (0,98) | 7,17 (1,92) | 7,39 (1,73) |
| Kilómetros recorridos por la flota | 839,8 (302,2) | 837,8 (303,3) | 771,8 (267,4) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,8 (1,2) | 2,1 (1,4) | 1,2 (1,0) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 68,1 (16,1) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,40 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,62 (0,17) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 29,8 | [24,0; 35,7] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,9 | [−2,6; −1,2] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,2 | [2,9; 5,4] | 27 / 1 / 2 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−0,9; −0,4] | 19 / 10 / 1 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,08; 0,02] | 19 / 0 / 11 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,48 | [1,88; 3,09] | 3 / 0 / 27 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −68,0 | [−88,5; −47,5] | 29 / 0 / 1 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,7 | [−0,7; 2,1] | 9 / 14 / 7 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,5 | [−2,3; −0,6] | 6 / 3 / 21 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,1] | 0 / 29 / 1 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,05 | [−0,11; 0,00] | 21 / 0 / 9 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,22 | [−0,27; 0,71] | 15 / 0 / 15 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −66,0 | [−86,4; −45,6] | 27 / 0 / 3 |

