# Resultados de la simulación

Generado el 2026-11-20 16:46 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: 10 cierres por jornada.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 10,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox` |
|---|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,3 (16,0) | 98,4 (3,3) | 97,5 (3,8) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,9 (1,9) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 89,1 (5,9) | 94,5 (6,3) | 92,7 (6,8) |
| Pedidos entregados dentro de la jornada (%) | 99,9 (0,6) | 99,9 (0,6) | 99,9 (0,6) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,8 (1,1) | 0,2 (0,8) | 0,2 (0,8) |
| Tiempo medio del pedido a la entrega (h) | 2,43 (0,51) | 2,48 (0,57) | 2,46 (0,59) |
| Tiempo máximo del pedido a la entrega (h) | 6,12 (0,89) | 8,84 (1,59) | 9,77 (1,24) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,23 (1,71) | 7,44 (2,05) | 7,71 (2,04) |
| Kilómetros recorridos por la flota | 841,0 (305,1) | 846,8 (304,3) | 794,0 (273,9) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 3,0 (1,6) | 3,2 (2,0) | 2,3 (1,6) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 74,2 (15,8) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,41 (0,11) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,62 (0,16) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 28,2 | [22,7; 33,6] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,9 | [−2,6; −1,2] | 22 / 8 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,5 | [2,2; 4,9] | 26 / 1 / 3 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,7 | [−0,9; −0,4] | 21 / 9 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | 0,03 | [−0,04; 0,10] | 14 / 0 / 16 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,48 | [1,86; 3,11] | 2 / 1 / 27 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −47,0 | [−68,9; −25,1] | 25 / 0 / 5 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,9 | [−2,6; 0,8] | 6 / 15 / 9 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,7; −0,9] | 6 / 2 / 22 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,02 | [−0,09; 0,05] | 20 / 0 / 10 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,27 | [−0,22; 0,76] | 10 / 1 / 19 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −52,8 | [−73,0; −32,6] | 27 / 0 / 3 |

