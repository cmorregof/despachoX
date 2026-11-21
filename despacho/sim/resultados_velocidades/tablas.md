# Tablas de la sección 9 (velocidades de la tesis UNAL de 2019, tabla 14)

Generadas con `python -m despacho.sim.comparar despacho/sim/resultados_velocidades`. 30 semillas por carga (20261150 en adelante), las mismas en todas las corridas y políticas. FACTOR_CRITICO = 3. Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.

- velocidades de la tesis: 360 jornadas, 0 llamadas al optimizador con error.
- velocidades del modelo, misma red: 360 jornadas, 0 llamadas al optimizador con error.
- sección 8.3: 360 jornadas, 0 llamadas al optimizador con error.

- Carga holgada: 49 puntos, 100 pedidos, 7,5 vehículos, 5,6 cierres en promedio.
- Carga media: 49 puntos, 125 pedidos, 7,5 vehículos, 5,6 cierres en promedio.
- Carga alta: 49 puntos, 149 pedidos, 7,5 vehículos, 5,6 cierres en promedio.

## Velocidades de la tesis: medias y diferencias pareadas

### Críticos a tiempo (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 75,9 | 97,7 | 99,2 | 23,3 [17,4; 29,1] | 1,5 [0,2; 2,8] | 8 / 20 / 2 | 0,3 [−0,9; 1,4] | 0,3 [−0,6; 1,2] |
| Media | 53,6 | 94,6 | 98,3 | 44,7 [37,7; 51,6] | 3,7 [1,7; 5,7] | 15 / 13 / 2 | 0,9 [−0,2; 2,1] | 1,7 [−0,7; 4,0] |
| Alta | 40,5 | 91,9 | 98,4 | 57,9 [52,7; 63,1] | 6,5 [4,4; 8,7] | 23 / 6 / 1 | 2,8 [0,8; 4,7] | 0,8 [−0,6; 2,2] |

### A tiempo, todos los puntos (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 90,4 | 95,2 | 94,8 | 4,3 [2,4; 6,3] | −0,5 [−1,9; 0,9] | 9 / 6 / 15 | −0,8 [−1,8; 0,2] | −0,2 [−0,7; 0,4] |
| Media | 76,4 | 84,8 | 84,0 | 7,6 [5,2; 9,9] | −0,8 [−3,1; 1,4] | 10 / 3 / 17 | −2,6 [−4,1; −1,0] | −1,9 [−3,5; −0,3] |
| Alta | 62,4 | 70,3 | 73,2 | 10,8 [8,4; 13,3] | 3,0 [0,7; 5,3] | 23 / 0 / 7 | −2,7 [−4,2; −1,1] | −1,7 [−3,2; −0,2] |

### Perecederos vencidos (%)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 1,4 | 0,0 | 0,0 | −1,4 [−2,1; −0,8] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Media | 3,4 | 0,0 | 0,0 | −3,4 [−4,4; −2,4] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Alta | 5,6 | 0,0 | 0,0 | −5,6 [−6,8; −4,3] | 0,0 [0,0; 0,0] | 0 / 30 / 0 | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |

### Kilómetros de la flota

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 623,0 | 615,9 | 569,9 | −53,1 [−71,2; −34,9] | −46,0 [−63,3; −28,7] | 27 / 0 / 3 | −62,6 [−82,0; −43,2] | −51,1 [−62,6; −39,5] |
| Media | 760,5 | 755,8 | 699,8 | −60,6 [−82,4; −38,9] | −56,0 [−77,9; −34,0] | 26 / 0 / 4 | −51,5 [−70,6; −32,3] | −59,5 [−73,0; −46,0] |
| Alta | 842,3 | 840,5 | 798,3 | −44,0 [−59,4; −28,7] | −42,2 [−56,8; −27,6] | 26 / 0 / 4 | −44,6 [−66,2; −23,0] | −46,9 [−65,0; −28,7] |

### Espera en el punto peor atendido (h)

| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` | `despachox` − `experta`, velocidades del modelo, misma red (9.3) | `despachox` − `experta` en la sección 8.3 (red urbana) |
|---|---:|---:|---:|---|---|---|---|---|
| Holgada | 5,14 | 6,96 | 7,09 | 1,95 [1,36; 2,53] | 0,13 [−0,36; 0,63] | 13 / 0 / 17 | 0,28 [−0,17; 0,73] | 0,23 [−0,21; 0,67] |
| Media | 6,46 | 9,00 | 9,53 | 3,07 [2,46; 3,68] | 0,53 [0,04; 1,02] | 9 / 0 / 21 | 0,62 [0,21; 1,03] | 0,81 [0,37; 1,25] |
| Alta | 7,56 | 10,77 | 11,37 | 3,82 [3,21; 4,43] | 0,61 [0,17; 1,04] | 10 / 2 / 18 | 0,75 [0,38; 1,12] | 0,89 [0,33; 1,45] |

## Efecto de las velocidades de la tesis en la misma red

Diferencia pareada por semilla, velocidades de la tesis menos velocidades del modelo. Mismos puntos, pedidos, lotes y flota; los cierres se sortean con la misma regla sobre los caminos de cada red de velocidades, así que pueden caer en otros tramos.

| Carga | Indicador | `ingenua` | `experta` | `despachox` | Cambio de la brecha `despachox` − `experta` |
|---|---|---|---|---|---|
| Holgada | Críticos a tiempo (%) | −10,1 [−13,6; −6,6] | −1,4 [−3,0; 0,2] | −0,2 [−0,8; 0,4] | 1,2 [−0,2; 2,7] |
| Holgada | A tiempo, todos los puntos (%) | −4,5 [−6,8; −2,3] | −3,4 [−5,9; −0,9] | −3,1 [−4,9; −1,2] | 0,3 [−1,1; 1,7] |
| Holgada | Perecederos vencidos (%) | 0,4 [0,1; 0,7] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Holgada | Kilómetros de la flota | −54,6 [−85,9; −23,4] | −50,0 [−76,9; −23,0] | −33,3 [−61,0; −5,7] | 16,6 [−2,7; 35,9] |
| Holgada | Espera en el punto peor atendido (h) | 0,71 [0,25; 1,18] | 1,83 [1,37; 2,29] | 1,68 [1,04; 2,32] | −0,15 [−0,80; 0,51] |
| Media | Críticos a tiempo (%) | −12,6 [−16,1; −9,2] | −3,3 [−4,8; −1,7] | −0,5 [−1,5; 0,5] | 2,8 [0,9; 4,6] |
| Media | A tiempo, todos los puntos (%) | −9,4 [−12,2; −6,6] | −8,5 [−11,2; −5,7] | −6,7 [−9,0; −4,4] | 1,7 [−0,8; 4,3] |
| Media | Perecederos vencidos (%) | 1,3 [0,6; 1,9] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Media | Kilómetros de la flota | −45,5 [−75,5; −15,4] | −45,7 [−70,8; −20,5] | −50,2 [−81,6; −18,8] | −4,5 [−24,8; 15,8] |
| Media | Espera en el punto peor atendido (h) | 1,13 [0,57; 1,68] | 1,62 [1,21; 2,03] | 1,53 [1,02; 2,04] | −0,09 [−0,67; 0,49] |
| Alta | Críticos a tiempo (%) | −9,0 [−11,8; −6,1] | −3,8 [−5,2; −2,4] | 0,0 [−1,3; 1,2] | 3,7 [2,0; 5,5] |
| Alta | A tiempo, todos los puntos (%) | −11,5 [−14,2; −8,8] | −12,2 [−14,6; −9,9] | −6,6 [−8,2; −4,9] | 5,7 [3,6; 7,7] |
| Alta | Perecederos vencidos (%) | 1,6 [1,0; 2,3] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] | 0,0 [0,0; 0,0] |
| Alta | Kilómetros de la flota | −94,5 [−130,4; −58,6] | −89,2 [−118,5; −60,0] | −86,9 [−122,2; −51,6] | 2,4 [−16,4; 21,2] |
| Alta | Espera en el punto peor atendido (h) | 1,20 [0,88; 1,52] | 1,46 [1,07; 1,86] | 1,32 [0,96; 1,68] | −0,14 [−0,67; 0,38] |

Medias con velocidades del modelo en la misma red:

| Carga | Indicador | `ingenua` | `experta` | `despachox` |
|---|---|---:|---:|---:|
| Holgada | Críticos a tiempo (%) | 86,0 | 99,1 | 99,3 |
| Holgada | A tiempo, todos los puntos (%) | 95,0 | 98,6 | 97,8 |
| Holgada | Perecederos vencidos (%) | 1,1 | 0,0 | 0,0 |
| Holgada | Kilómetros de la flota | 677,6 | 665,9 | 603,3 |
| Holgada | Espera en el punto peor atendido (h) | 4,43 | 5,13 | 5,41 |
| Media | Críticos a tiempo (%) | 66,2 | 97,9 | 98,8 |
| Media | A tiempo, todos los puntos (%) | 85,9 | 93,3 | 90,7 |
| Media | Perecederos vencidos (%) | 2,2 | 0,0 | 0,0 |
| Media | Kilómetros de la flota | 805,9 | 801,5 | 750,0 |
| Media | Espera en el punto peor atendido (h) | 5,33 | 7,38 | 8,00 |
| Alta | Críticos a tiempo (%) | 49,5 | 95,6 | 98,4 |
| Alta | A tiempo, todos los puntos (%) | 73,9 | 82,5 | 79,8 |
| Alta | Perecederos vencidos (%) | 3,9 | 0,0 | 0,0 |
| Alta | Kilómetros de la flota | 936,8 | 929,8 | 885,2 |
| Alta | Espera en el punto peor atendido (h) | 6,36 | 9,30 | 10,05 |

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

