# Resultados de la simulación

Generado el 2026-11-20 16:13 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: error de ubicación de pedidos p = 0.1.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox_sin_confirmar` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 58,8 (16,3) | 95,6 (4,7) | 95,3 (5,5) | 98,6 (2,9) |
| Kilos perecederos que vencieron sin entregarse (%) | 2,4 (2,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 84,2 (7,7) | 90,2 (7,0) | 87,6 (7,5) | 93,6 (5,5) |
| Pedidos entregados dentro de la jornada (%) | 99,9 (0,3) | 100,0 (0,2) | 99,9 (0,3) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,9 (0,9) | 0,0 (0,2) | 0,1 (0,3) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,86 (0,56) | 2,88 (0,61) | 2,91 (0,62) | 2,40 (0,50) |
| Tiempo máximo del pedido a la entrega (h) | 7,69 (1,03) | 10,16 (1,73) | 11,01 (1,31) | 9,69 (1,15) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,80 (1,26) | 8,22 (2,05) | 8,62 (1,74) | 7,17 (1,67) |
| Kilómetros recorridos por la flota | 916,2 (326,9) | 912,2 (320,8) | 869,0 (289,2) | 776,5 (269,5) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,8 (1,7) | 1,9 (1,5) | 1,3 (1,3) | 1,4 (1,2) |
| Llegadas a un punto equivocado por error de registro | 13,7 (5,4) | 13,7 (5,4) | 13,7 (5,4) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 81,5 (19,3) | 68,3 (16,3) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,38 (0,10) | 1,34 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,56 (0,15) | 1,51 (0,15) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 39,8 | [34,3; 45,3] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,4 | [−3,1; −1,6] | 26 / 4 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 9,5 | [8,0; 11,0] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −0,9 | [−1,2; −0,6] | 26 / 4 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,46 | [−0,53; −0,38] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 1,38 | [0,79; 1,97] | 7 / 1 / 22 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −139,7 | [−169,3; −110,1] | 29 / 0 / 1 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 3,0 | [0,9; 5,2] | 16 / 11 / 3 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,4 | [2,1; 4,8] | 23 / 1 / 6 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,1; 0,0] | 1 / 29 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,47 | [−0,58; −0,37] | 29 / 0 / 1 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | −1,04 | [−1,69; −0,40] | 23 / 0 / 7 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −135,6 | [−165,4; −105,8] | 29 / 0 / 1 |
| `despachox` − `despachox_sin_confirmar` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 3,3 | [1,0; 5,7] | 18 / 10 / 2 |
| `despachox` − `despachox_sin_confirmar` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `despachox_sin_confirmar` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 6,0 | [4,5; 7,5] | 30 / 0 / 0 |
| `despachox` − `despachox_sin_confirmar` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,1; 0,1] | 1 / 29 / 0 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio del pedido a la entrega (h) | −0,51 | [−0,59; −0,42] | 30 / 0 / 0 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio de espera en el punto peor atendido (h) | −1,45 | [−1,84; −1,05] | 29 / 0 / 1 |
| `despachox` − `despachox_sin_confirmar` | Kilómetros recorridos por la flota | −92,5 | [−111,5; −73,6] | 29 / 0 / 1 |
| `despachox_sin_confirmar` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,3 | [−2,2; 1,6] | 8 / 13 / 9 |
| `despachox_sin_confirmar` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox_sin_confirmar` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,6 | [−3,7; −1,4] | 4 / 4 / 22 |
| `despachox_sin_confirmar` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,1; 0,1] | 1 / 28 / 1 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,03 | [−0,04; 0,11] | 12 / 0 / 18 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,40 | [−0,11; 0,91] | 10 / 0 / 20 |
| `despachox_sin_confirmar` − `experta` | Kilómetros recorridos por la flota | −43,1 | [−66,6; −19,7] | 27 / 0 / 3 |

