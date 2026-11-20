# Resultados de la simulación

Generado el 2026-11-20 16:28 con `python -m despacho.sim.correr`. Commit `c73c1bf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: error de ubicación de pedidos p = 0.2.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox_sin_confirmar` | `despachox` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 52,1 (16,6) | 94,1 (5,2) | 91,5 (6,0) | 98,5 (2,8) |
| Kilos perecederos que vencieron sin entregarse (%) | 3,6 (2,2) | 0,0 (0,0) | 0,0 (0,1) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 78,3 (9,1) | 84,5 (10,1) | 82,9 (8,7) | 93,6 (6,3) |
| Pedidos entregados dentro de la jornada (%) | 99,7 (0,9) | 99,6 (1,0) | 99,5 (1,0) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 1,6 (1,4) | 0,5 (1,4) | 0,6 (1,3) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 3,28 (0,65) | 3,31 (0,66) | 3,31 (0,63) | 2,38 (0,54) |
| Tiempo máximo del pedido a la entrega (h) | 8,33 (1,41) | 11,11 (1,54) | 12,05 (1,18) | 9,56 (1,44) |
| Tiempo medio de espera en el punto peor atendido (h) | 6,78 (1,46) | 9,31 (1,95) | 9,44 (1,99) | 7,40 (1,87) |
| Kilómetros recorridos por la flota | 988,1 (355,6) | 987,6 (354,8) | 937,3 (325,6) | 773,8 (276,2) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,9 (1,5) | 1,9 (1,5) | 1,4 (1,4) | 1,3 (1,3) |
| Llegadas a un punto equivocado por error de registro | 26,9 (10,1) | 26,9 (10,1) | 26,9 (10,1) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 92,6 (23,6) | 67,7 (16,3) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,44 (0,12) | 1,39 (0,12) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,71 (0,27) | 1,58 (0,23) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 46,4 | [40,4; 52,3] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,6 | [−4,5; −2,8] | 27 / 3 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 15,3 | [13,4; 17,3] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | −1,6 | [−2,1; −1,0] | 27 / 3 / 0 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,90 | [−1,01; −0,78] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 0,62 | [0,03; 1,21] | 11 / 0 / 19 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −214,3 | [−249,9; −178,8] | 30 / 0 / 0 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 4,4 | [2,2; 6,5] | 19 / 8 / 3 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 9,1 | [7,2; 11,0] | 28 / 2 / 0 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | −0,5 | [−1,0; 0,0] | 4 / 26 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,92 | [−1,04; −0,81] | 30 / 0 / 0 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | −1,91 | [−2,44; −1,38] | 27 / 0 / 3 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −213,9 | [−251,0; −176,7] | 29 / 0 / 1 |
| `despachox` − `despachox_sin_confirmar` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 7,0 | [4,9; 9,2] | 25 / 5 / 0 |
| `despachox` − `despachox_sin_confirmar` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [−0,1; 0,0] | 3 / 27 / 0 |
| `despachox` − `despachox_sin_confirmar` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 10,7 | [9,0; 12,5] | 30 / 0 / 0 |
| `despachox` − `despachox_sin_confirmar` | Kilos pedidos que no llegaron en buen estado (%) | −0,6 | [−1,1; −0,1] | 9 / 21 / 0 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio del pedido a la entrega (h) | −0,92 | [−1,02; −0,83] | 30 / 0 / 0 |
| `despachox` − `despachox_sin_confirmar` | Tiempo medio de espera en el punto peor atendido (h) | −2,04 | [−2,61; −1,47] | 29 / 0 / 1 |
| `despachox` − `despachox_sin_confirmar` | Kilómetros recorridos por la flota | −163,5 | [−193,5; −133,6] | 30 / 0 / 0 |
| `despachox_sin_confirmar` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −2,6 | [−4,8; −0,5] | 9 / 5 / 16 |
| `despachox_sin_confirmar` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,1] | 0 / 27 / 3 |
| `despachox_sin_confirmar` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,6 | [−2,9; −0,3] | 7 / 2 / 21 |
| `despachox_sin_confirmar` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,1 | [−0,3; 0,5] | 1 / 21 / 8 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,06; 0,05] | 16 / 0 / 14 |
| `despachox_sin_confirmar` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,13 | [−0,31; 0,58] | 12 / 0 / 18 |
| `despachox_sin_confirmar` − `experta` | Kilómetros recorridos por la flota | −50,3 | [−70,1; −30,6] | 26 / 0 / 4 |

