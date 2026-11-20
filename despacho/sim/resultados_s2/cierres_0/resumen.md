# Resultados de la simulación

Generado el 2026-11-20 16:33 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: 0 cierres por jornada.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 0,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox` |
|---|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,8 (15,0) | 98,6 (2,6) | 99,3 (2,6) |
| Kilos perecederos que vencieron sin entregarse (%) | 1,9 (1,8) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 90,4 (5,6) | 96,4 (5,0) | 94,3 (5,3) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,0) | 100,0 (0,0) | 100,0 (0,0) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,7 (0,6) | 0,0 (0,0) | 0,0 (0,0) |
| Tiempo medio del pedido a la entrega (h) | 2,32 (0,48) | 2,33 (0,55) | 2,29 (0,52) |
| Tiempo máximo del pedido a la entrega (h) | 5,85 (1,03) | 8,33 (1,53) | 9,29 (1,49) |
| Tiempo medio de espera en el punto peor atendido (h) | 4,72 (0,95) | 6,65 (1,68) | 7,21 (1,55) |
| Kilómetros recorridos por la flota | 826,7 (297,9) | 827,4 (304,6) | 762,4 (266,6) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 0,2 (0,5) | 0,3 (0,8) | 0,0 (0,0) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 62,0 (15,0) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,37 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,58 (0,16) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 29,5 | [23,9; 35,0] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,9 | [−2,6; −1,2] | 23 / 7 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,8 | [2,9; 4,8] | 28 / 1 / 1 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,7 | [−0,9; −0,4] | 22 / 8 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,08; 0,01] | 18 / 0 / 12 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,49 | [1,90; 3,08] | 3 / 0 / 27 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −64,2 | [−81,2; −47,2] | 30 / 0 / 0 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,6 | [−0,8; 2,1] | 8 / 19 / 3 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,1 | [−3,0; −1,3] | 4 / 4 / 22 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,09; 0,02] | 17 / 0 / 13 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,56 | [0,14; 0,98] | 5 / 0 / 25 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −65,0 | [−83,8; −46,2] | 28 / 0 / 2 |

