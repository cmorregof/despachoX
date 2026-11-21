# Tablas de la sección 9 (velocidades de la tesis UNAL de 2019, tabla 14)

Generadas con `python -m despacho.sim.comparar despacho/sim/resultados_velocidades`. 30 semillas por carga (20261150 en adelante), las mismas en todas las corridas y políticas. FACTOR_CRITICO = 3. Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.

- velocidades de la tesis: 360 jornadas, 0 llamadas al optimizador con error.
- sección 8.3: 360 jornadas, 0 llamadas al optimizador con error.

- Carga holgada: 49 puntos, 100 pedidos, 7,5 vehículos, 5,6 cierres en promedio.
- Carga media: 49 puntos, 125 pedidos, 7,5 vehículos, 5,6 cierres en promedio.
- Carga alta: 49 puntos, 149 pedidos, 7,5 vehículos, 5,6 cierres en promedio.

## Velocidades de la tesis: medias y diferencias pareadas

### Críticos a tiempo (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red | Misma diferencia en la sección 8.3 |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 75,9 | 97,7 | 99,2 | 23,3 [17,4; 29,1] | 1,5 [0,2; 2,8] | 8 / 20 / 2 | s. d. | 0,3 [−0,6; 1,2] |
| Media | 53,6 | 94,6 | 98,3 | 44,7 [37,7; 51,6] | 3,7 [1,7; 5,7] | 15 / 13 / 2 | s. d. | 1,7 [−0,7; 4,0] |
| Alta | 40,5 | 91,9 | 98,4 | 57,9 [52,7; 63,1] | 6,5 [4,4; 8,7] | 23 / 6 / 1 | s. d. | 0,8 [−0,6; 2,2] |

### A tiempo, todos los puntos (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red | Misma diferencia en la sección 8.3 |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 90,4 | 95,2 | 94,8 | 4,3 [2,4; 6,3] | −0,5 [−1,9; 0,9] | 9 / 6 / 15 | s. d. | −0,2 [−0,7; 0,4] |
| Media | 76,4 | 84,8 | 84,0 | 7,6 [5,2; 9,9] | −0,8 [−3,1; 1,4] | 10 / 3 / 17 | s. d. | −1,9 [−3,5; −0,3] |
| Alta | 62,4 | 70,3 | 73,2 | 10,8 [8,4; 13,3] | 3,0 [0,7; 5,3] | 23 / 0 / 7 | s. d. | −1,7 [−3,2; −0,2] |

### Perecederos vencidos (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red | Misma diferencia en la sección 8.3 |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 1,4 | 0,0 | 0,0 | −1,4 [−2,1; −0,8] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | s. d. | 0,0 [0,0; 0,0] |
| Media | 3,4 | 0,0 | 0,0 | −3,4 [−4,4; −2,4] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | s. d. | 0,0 [0,0; 0,0] |
| Alta | 5,6 | 0,0 | 0,0 | −5,6 [−6,8; −4,3] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | s. d. | 0,0 [0,0; 0,0] |

### Kilómetros de la flota

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red | Misma diferencia en la sección 8.3 |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 623,0 | 615,9 | 569,9 | −53,1 [−71,2; −34,9] | −46,0 [−63,3; −28,7] | 27 / 0 / 3 | s. d. | −51,1 [−62,6; −39,5] |
| Media | 760,5 | 755,8 | 699,8 | −60,6 [−82,4; −38,9] | −56,0 [−77,9; −34,0] | 26 / 0 / 4 | s. d. | −59,5 [−73,0; −46,0] |
| Alta | 842,3 | 840,5 | 798,3 | −44,0 [−59,4; −28,7] | −42,2 [−56,8; −27,6] | 26 / 0 / 4 | s. d. | −46,9 [−65,0; −28,7] |

### Espera en el punto peor atendido (h)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red | Misma diferencia en la sección 8.3 |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 5,14 | 6,96 | 7,09 | 1,95 [1,36; 2,53] | 0,13 [−0,36; 0,63] | 13 / 0 / 17 | s. d. | 0,23 [−0,21; 0,67] |
| Media | 6,46 | 9,00 | 9,53 | 3,07 [2,46; 3,68] | 0,53 [0,04; 1,02] | 9 / 0 / 21 | s. d. | 0,81 [0,37; 1,25] |
| Alta | 7,56 | 10,77 | 11,37 | 3,82 [3,21; 4,43] | 0,61 [0,17; 1,04] | 10 / 2 / 18 | s. d. | 0,89 [0,33; 1,45] |

## Medias de la sección 8.3 (red urbana, velocidades del modelo)

| Carga | Indicador | `ingenua` | `experta` | `despachox` |
|---|---|---:|---:|---:|
| Holgada | Críticos a tiempo (%) | 89,7 | 99,5 | 99,8 |
| Holgada | A tiempo, todos los puntos (%) | 95,8 | 99,1 | 98,9 |
| Holgada | Perecederos vencidos (%) | 1,0 | 0,0 | 0,0 |
| Holgada | Kilómetros de la flota | 625,5 | 623,5 | 572,4 |
| Holgada | Espera en el punto peor atendido (h) | 3,90 | 5,07 | 5,30 |
| Media | Críticos a tiempo (%) | 70,9 | 97,8 | 99,5 |
| Media | A tiempo, todos los puntos (%) | 88,8 | 94,7 | 92,8 |
| Media | Perecederos vencidos (%) | 1,8 | 0,0 | 0,0 |
| Media | Kilómetros de la flota | 745,8 | 754,4 | 694,9 |
| Media | Espera en el punto peor atendido (h) | 5,04 | 7,07 | 7,88 |
| Alta | Críticos a tiempo (%) | 51,4 | 98,1 | 98,9 |
| Alta | A tiempo, todos los puntos (%) | 76,5 | 85,2 | 83,5 |
| Alta | Perecederos vencidos (%) | 3,2 | 0,0 | 0,0 |
| Alta | Kilómetros de la flota | 883,8 | 875,2 | 828,3 |
| Alta | Espera en el punto peor atendido (h) | 5,82 | 8,74 | 9,63 |

