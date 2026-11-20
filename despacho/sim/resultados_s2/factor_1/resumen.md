# Resultados de la simulación

Generado el 2026-11-20 14:57 con `python -m despacho.sim.correr`. Commit `3ffdf69`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: FACTOR_CRITICO = 1.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `experta` | `despachox` |
|---|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 98,5 (2,6) | 98,2 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 95,6 (5,3) | 93,8 (5,8) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,40 (0,55) | 2,37 (0,53) |
| Tiempo máximo del pedido a la entrega (h) | 8,75 (1,50) | 9,71 (1,47) |
| Tiempo medio de espera en el punto peor atendido (h) | 7,09 (1,88) | 7,23 (1,76) |
| Kilómetros recorridos por la flota | 834,3 (297,9) | 776,1 (266,9) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,9 (1,4) | 1,3 (1,3) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 69,0 (16,1) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 1,42 (0,11) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 1,67 (0,18) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,4 | [−1,8; 1,0] | 5 / 16 / 9 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,8 | [−2,6; −1,0] | 3 / 2 / 25 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,09; 0,03] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,14 | [−0,38; 0,67] | 12 / 1 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −58,2 | [−76,5; −39,9] | 25 / 0 / 5 |

## Carga alta

Escenarios: 56 puntos, 166 pedidos, 52,8 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `experta` | `despachox` |
|---|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 97,6 (3,7) | 95,9 (4,2) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 85,9 (8,2) | 83,8 (7,1) |
| Pedidos entregados dentro de la jornada (%) | 99,7 (0,8) | 99,8 (0,5) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,4 (1,1) | 0,3 (0,6) |
| Tiempo medio del pedido a la entrega (h) | 3,28 (0,58) | 3,28 (0,59) |
| Tiempo máximo del pedido a la entrega (h) | 10,74 (1,40) | 12,00 (1,22) |
| Tiempo medio de espera en el punto peor atendido (h) | 9,12 (1,76) | 10,12 (1,34) |
| Kilómetros recorridos por la flota | 1000,3 (361,3) | 953,4 (324,4) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,1 (1,6) | 1,3 (1,2) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 82,5 (19,1) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 1,39 (0,11) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 1,61 (0,20) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −1,8 | [−3,6; 0,0] | 7 / 8 / 15 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,2 | [−3,6; −0,7] | 7 / 2 / 21 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | −0,1 | [−0,4; 0,2] | 3 / 24 / 3 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | 0,00 | [−0,07; 0,06] | 15 / 0 / 15 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,99 | [0,50; 1,49] | 6 / 1 / 23 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −46,8 | [−73,3; −20,4] | 22 / 0 / 8 |

