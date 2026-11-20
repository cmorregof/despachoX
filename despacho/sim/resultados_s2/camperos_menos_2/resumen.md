# Resultados de la simulación

Generado el 2026-11-20 16:52 con `python -m despacho.sim.correr`. Commit `04257b8`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 1 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.
- Variante: flota con 2 camperos menos.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 6,5 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `ingenua` | `experta` | `despachox` |
|---|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 33,0 (15,7) | 91,3 (8,6) | 90,8 (11,9) |
| Kilos perecederos que vencieron sin entregarse (%) | 5,7 (3,2) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 61,7 (14,4) | 69,2 (15,5) | 72,6 (12,4) |
| Pedidos entregados dentro de la jornada (%) | 94,1 (7,7) | 94,1 (7,7) | 93,6 (7,4) |
| Kilos pedidos que no llegaron en buen estado (%) | 8,2 (8,9) | 7,0 (8,8) | 8,4 (9,3) |
| Tiempo medio del pedido a la entrega (h) | 4,25 (0,73) | 4,08 (0,63) | 3,91 (0,60) |
| Tiempo máximo del pedido a la entrega (h) | 8,65 (1,36) | 12,42 (1,40) | 12,93 (1,26) |
| Tiempo medio de espera en el punto peor atendido (h) | 7,76 (1,46) | 11,05 (1,88) | 11,03 (1,74) |
| Kilómetros recorridos por la flota | 732,7 (295,7) | 730,5 (291,6) | 693,6 (269,9) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 2,3 (1,6) | 2,0 (1,3) | 1,3 (1,2) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 0,0 (0,0) | 68,5 (14,6) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 0,00 (0,00) | 1,43 (0,13) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 0,00 (0,00) | 1,71 (0,20) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 57,7 | [52,2; 63,3] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −5,7 | [−6,9; −4,5] | 28 / 2 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 10,9 | [9,2; 12,7] | 30 / 0 / 0 |
| `despachox` − `ingenua` | Kilos pedidos que no llegaron en buen estado (%) | 0,2 | [−1,0; 1,4] | 17 / 1 / 12 |
| `despachox` − `ingenua` | Tiempo medio del pedido a la entrega (h) | −0,34 | [−0,44; −0,24] | 28 / 0 / 2 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,26 | [2,62; 3,91] | 1 / 0 / 29 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −39,0 | [−54,2; −23,9] | 22 / 0 / 8 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,6 | [−4,1; 3,0] | 10 / 7 / 13 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,4 | [1,3; 5,5] | 23 / 1 / 6 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 1,4 | [0,2; 2,5] | 6 / 8 / 16 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,17 | [−0,24; −0,11] | 26 / 0 / 4 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | −0,02 | [−0,59; 0,55] | 11 / 2 / 17 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −36,9 | [−50,2; −23,6] | 25 / 0 / 5 |

