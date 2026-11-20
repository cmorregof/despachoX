# Resultados de la simulación

Generado el 2026-11-20 15:21 con `python -m despacho.sim.correr`. Commit `d31fcaf`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: FACTOR_CRITICO = 10.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `experta` | `despachox` |
|---|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 98,5 (2,6) | 99,9 (0,5) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 95,6 (5,3) | 93,3 (5,9) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,40 (0,55) | 2,39 (0,52) |
| Tiempo máximo del pedido a la entrega (h) | 8,75 (1,50) | 9,61 (1,22) |
| Tiempo medio de espera en el punto peor atendido (h) | 7,09 (1,88) | 7,21 (1,75) |
| Kilómetros recorridos por la flota | 834,3 (297,9) | 775,9 (263,4) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,9 (1,4) | 1,3 (1,2) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 68,7 (16,6) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 1,37 (0,10) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 1,55 (0,17) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 1,4 | [0,4; 2,4] | 8 / 22 / 0 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,3 | [−3,2; −1,3] | 3 / 4 / 23 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,02 | [−0,07; 0,04] | 15 / 0 / 15 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,12 | [−0,44; 0,68] | 13 / 1 / 16 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −58,4 | [−80,3; −36,5] | 27 / 0 / 3 |

## Carga alta

Escenarios: 56 puntos, 166 pedidos, 52,8 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `experta` | `despachox` |
|---|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 97,6 (3,7) | 99,8 (0,8) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 85,9 (8,2) | 84,0 (8,2) |
| Pedidos entregados dentro de la jornada (%) | 99,7 (0,8) | 99,7 (0,7) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,4 (1,1) | 0,4 (0,9) |
| Tiempo medio del pedido a la entrega (h) | 3,28 (0,58) | 3,24 (0,60) |
| Tiempo máximo del pedido a la entrega (h) | 10,74 (1,40) | 11,93 (1,27) |
| Tiempo medio de espera en el punto peor atendido (h) | 9,12 (1,76) | 10,06 (1,53) |
| Kilómetros recorridos por la flota | 1000,3 (361,3) | 946,4 (326,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,1 (1,6) | 1,3 (1,2) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 82,3 (18,4) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 1,40 (0,11) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 1,56 (0,16) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 2,2 | [0,8; 3,6] | 12 / 17 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −2,0 | [−3,1; −0,9] | 8 / 0 / 22 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [−0,3; 0,3] | 4 / 23 / 3 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,04 | [−0,10; 0,02] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,93 | [0,47; 1,39] | 7 / 1 / 22 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −53,9 | [−74,6; −33,2] | 27 / 0 / 3 |

