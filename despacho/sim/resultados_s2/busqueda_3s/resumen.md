# Resultados de la simulación

Generado el 2026-11-20 17:06 con `python -m despacho.sim.correr`. Commit `48a35ea`.

- Red: OpenStreetMap (manizales.graphml, 6395 nodos).
- Optimizador de `optimiza_una_vez` y `despachox`: despacho/optimizar.py (OR-Tools, 3 s por llamada, un viaje por vehículo).
- Semillas: 30 por nivel de carga, de 20261120 a 20261149, las mismas para todas las políticas.
- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.
- Llamadas al optimizador que terminaron en error: 0.

## Carga media

Escenarios: 56 puntos, 138 pedidos, 44,1 t, 8,3 vehículos y 5,0 cierres en promedio.

### Media por política (desviación estándar entre semillas)

| Métrica | `experta` | `despachox` |
|---|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 98,5 (2,6) | 98,1 (3,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 95,6 (5,3) | 93,7 (5,5) |
| Pedidos entregados dentro de la jornada (%) | 100,0 (0,2) | 100,0 (0,2) |
| Kilos pedidos que no llegaron en buen estado (%) | 0,0 (0,1) | 0,0 (0,1) |
| Tiempo medio del pedido a la entrega (h) | 2,40 (0,55) | 2,37 (0,52) |
| Tiempo máximo del pedido a la entrega (h) | 8,75 (1,50) | 9,75 (1,35) |
| Tiempo medio de espera en el punto peor atendido (h) | 7,09 (1,88) | 7,37 (1,78) |
| Kilómetros recorridos por la flota | 834,3 (297,9) | 777,5 (268,0) |
| Vehículos que un cierre dejó sin ningún camino de regreso | 0,0 (0,0) | 0,0 (0,0) |
| Regresos al acopio por vías no aptas para el vehículo | 1,9 (1,4) | 1,3 (1,3) |
| Llegadas a un punto equivocado por error de registro | 0,0 (0,0) | 0,0 (0,0) |
| Llamadas al optimizador | 0,0 (0,0) | 69,6 (16,5) |
| Segundos de cálculo por llamada, media | 0,00 (0,00) | 3,40 (0,13) |
| Segundos de cálculo por llamada, máximo | 0,00 (0,00) | 3,67 (0,19) |

### Diferencias pareadas (los dos primeros indicadores son los del reto)

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | −0,4 | [−1,8; 0,9] | 5 / 15 / 10 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,9 | [−2,6; −1,2] | 2 / 2 / 26 |
| `despachox` − `experta` | Kilos pedidos que no llegaron en buen estado (%) | 0,0 | [0,0; 0,0] | 0 / 30 / 0 |
| `despachox` − `experta` | Tiempo medio del pedido a la entrega (h) | −0,03 | [−0,09; 0,02] | 18 / 0 / 12 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,28 | [−0,25; 0,81] | 8 / 0 / 22 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −56,8 | [−74,8; −38,8] | 26 / 0 / 4 |

