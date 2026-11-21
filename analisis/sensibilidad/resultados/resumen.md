# Sensibilidad: resultados por variante

Estos números no son el resultado principal de la simulación. Miden si las conclusiones aguantan cuando cambia un supuesto, frente a una referencia propia de este análisis.

- Semillas: 20261150 a 20261209 (60), las mismas para todas las variantes y políticas.
- Carga media, red y optimizador por defecto, 1 s de búsqueda por llamada, velocidad medida de `datos_publicos/velocidades.csv` salvo donde la variante la escala.
- Intervalos: `ic95` de `despacho/sim/correr.py` sobre la diferencia pareada por semilla.

## Referencia de la sensibilidad (no es el resultado principal)

Parámetros: velocidad medida × 1,00, demanda × 1,00, 0 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 68,7 veces al optimizador por jornada, 1,27 s por llamada; la tarea de `despachox` tardó 88,4 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 99,3 (2,1) | 68,7 (15,6) | 96,1 (4,9) | 54,7 (16,4) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 3,3 (2,4) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 87,2 (9,6) | 84,8 (11,0) | 87,5 (10,6) | 79,2 (11,8) |
| Tiempo medio de espera en el punto peor atendido (h) | 9,25 (2,24) | 5,93 (1,43) | 8,84 (1,84) | 6,23 (1,51) |
| Kilómetros recorridos por la flota | 751,7 (244,9) | 771,1 (260,2) | 804,7 (264,9) | 809,6 (256,2) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 44,6 | [40,4; 48,8] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,3 | [−3,9; −2,7] | 51 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 8,0 | [6,7; 9,3] | 56 / 2 / 2 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,02 | [2,54; 3,50] | 2 / 0 / 58 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −58,0 | [−71,3; −44,6] | 54 / 0 / 6 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 3,2 | [2,1; 4,4] | 28 / 31 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,3 | [−1,4; 0,9] | 25 / 8 / 27 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,41 | [0,05; 0,77] | 24 / 0 / 36 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −53,0 | [−66,3; −39,7] | 53 / 0 / 7 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 30,7 | [26,7; 34,7] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,4 | [1,3; 3,4] | 37 / 6 / 17 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,32 | [2,88; 3,75] | 1 / 0 / 59 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −19,4 | [−31,2; −7,6] | 39 / 0 / 21 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 9,78.

## Velocidad medida × 0,8

Parámetros: velocidad medida × 0,80, demanda × 1,00, 0 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 70,8 veces al optimizador por jornada, 1,28 s por llamada; la tarea de `despachox` tardó 92,4 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 99,1 (2,4) | 59,4 (15,5) | 94,0 (5,9) | 43,3 (14,9) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 4,5 (2,9) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 80,8 (10,5) | 76,2 (12,4) | 79,0 (12,5) | 69,7 (12,9) |
| Tiempo medio de espera en el punto peor atendido (h) | 10,57 (1,94) | 6,85 (1,50) | 9,99 (1,84) | 7,27 (1,66) |
| Kilómetros recorridos por la flota | 730,2 (234,5) | 751,0 (242,7) | 774,0 (245,7) | 773,6 (241,5) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 55,8 | [51,9; 59,7] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −4,5 | [−5,3; −3,8] | 57 / 3 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 11,1 | [9,5; 12,7] | 58 / 0 / 2 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,31 | [2,92; 3,69] | 0 / 0 / 60 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −43,4 | [−54,0; −32,8] | 50 / 0 / 10 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 5,1 | [3,6; 6,6] | 37 / 21 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,8 | [0,7; 3,0] | 38 / 3 / 19 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,58 | [0,26; 0,91] | 19 / 1 / 40 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −43,8 | [−53,0; −34,6] | 55 / 0 / 5 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 39,7 | [35,7; 43,6] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 4,5 | [3,3; 5,8] | 49 / 2 / 9 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,73 | [3,31; 4,14] | 0 / 0 / 60 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −20,8 | [−28,4; −13,2] | 46 / 0 / 14 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 11,50.

## Velocidad medida × 1,2

Parámetros: velocidad medida × 1,20, demanda × 1,00, 0 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 66,5 veces al optimizador por jornada, 1,26 s por llamada; la tarea de `despachox` tardó 84,9 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 99,5 (1,6) | 77,0 (16,3) | 97,5 (3,8) | 62,6 (17,4) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 2,2 (2,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 90,7 (8,7) | 89,7 (9,4) | 92,3 (8,9) | 85,2 (10,0) |
| Tiempo medio de espera en el punto peor atendido (h) | 8,09 (2,11) | 5,30 (1,42) | 7,91 (1,77) | 5,54 (1,38) |
| Kilómetros recorridos por la flota | 754,1 (253,5) | 779,0 (258,2) | 811,0 (265,4) | 824,3 (269,9) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 36,9 | [32,4; 41,3] | 59 / 1 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −2,2 | [−2,7; −1,7] | 50 / 10 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,5 | [4,4; 6,6] | 53 / 4 / 3 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,56 | [2,12; 3,00] | 4 / 0 / 56 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −70,1 | [−83,0; −57,2] | 55 / 0 / 5 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 1,9 | [1,1; 2,8] | 18 / 42 / 0 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −1,5 | [−2,5; −0,6] | 12 / 13 / 35 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,19 | [−0,17; 0,54] | 27 / 0 / 33 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −56,9 | [−70,0; −43,7] | 53 / 0 / 7 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 22,4 | [18,3; 26,5] | 54 / 6 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,1 | [0,2; 1,9] | 37 / 6 / 17 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 2,80 | [2,35; 3,24] | 3 / 0 / 57 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −24,8 | [−35,4; −14,3] | 49 / 0 / 11 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 8,55.

## Demanda × 0,75

Parámetros: velocidad medida × 1,00, demanda × 0,75, 0 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 99 pedidos, 31,5 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 51,8 veces al optimizador por jornada, 1,20 s por llamada; la tarea de `despachox` tardó 62,9 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 99,4 (2,0) | 90,1 (10,6) | 98,4 (3,5) | 83,8 (14,1) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 1,0 (1,5) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 97,6 (4,7) | 96,0 (5,4) | 97,4 (5,0) | 94,0 (5,4) |
| Tiempo medio de espera en el punto peor atendido (h) | 5,75 (1,89) | 4,38 (1,20) | 5,72 (1,82) | 4,69 (1,27) |
| Kilómetros recorridos por la flota | 569,8 (181,9) | 594,0 (182,7) | 635,7 (211,6) | 632,1 (196,5) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 15,5 | [11,9; 19,2] | 47 / 13 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −1,0 | [−1,4; −0,6] | 31 / 29 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 3,6 | [2,7; 4,4] | 49 / 7 / 4 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 1,05 | [0,68; 1,43] | 10 / 0 / 50 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −62,3 | [−72,7; −51,9] | 55 / 0 / 5 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,9 | [0,0; 1,8] | 13 / 43 / 4 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 0,1 | [−0,3; 0,5] | 20 / 27 / 13 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,03 | [−0,29; 0,35] | 27 / 0 / 33 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −65,9 | [−77,2; −54,7] | 58 / 0 / 2 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 9,3 | [6,6; 11,9] | 44 / 15 / 1 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 1,5 | [1,1; 2,0] | 43 / 14 / 3 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 1,37 | [0,98; 1,77] | 9 / 1 / 50 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −24,3 | [−34,6; −13,9] | 46 / 0 / 14 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 8,49.

## Demanda × 1,5

Parámetros: velocidad medida × 1,00, demanda × 1,50, 0 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 198 pedidos, 63,2 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 86,0 veces al optimizador por jornada, 1,38 s por llamada; la tarea de `despachox` tardó 120,9 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 98,5 (2,3) | 46,5 (10,1) | 88,1 (8,5) | 29,2 (8,5) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 8,2 (3,5) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 60,9 (9,5) | 52,2 (10,9) | 54,0 (11,9) | 46,5 (10,5) |
| Tiempo medio de espera en el punto peor atendido (h) | 12,42 (1,50) | 8,59 (1,40) | 12,11 (1,62) | 8,93 (1,45) |
| Kilómetros recorridos por la flota | 927,7 (279,1) | 956,3 (293,4) | 975,3 (294,2) | 973,7 (301,4) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 69,4 | [67,0; 71,7] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −8,2 | [−9,1; −7,2] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 14,4 | [13,0; 15,8] | 59 / 0 / 1 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,49 | [3,11; 3,87] | 0 / 1 / 59 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −46,0 | [−58,3; −33,7] | 53 / 0 / 7 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 10,5 | [8,3; 12,6] | 53 / 6 / 1 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 6,9 | [5,5; 8,2] | 50 / 3 / 7 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,31 | [0,02; 0,60] | 18 / 13 / 29 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −47,6 | [−56,7; −38,6] | 57 / 0 / 3 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 52,0 | [49,4; 54,7] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 8,7 | [7,5; 9,9] | 58 / 1 / 1 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,82 | [3,45; 4,20] | 0 / 1 / 59 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −28,7 | [−36,5; −20,8] | 53 / 0 / 7 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 26,39.

## Flota con un campero menos

Parámetros: velocidad medida × 1,00, demanda × 1,00, 1 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 7,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 67,9 veces al optimizador por jornada, 1,30 s por llamada; la tarea de `despachox` tardó 89,8 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 98,0 (3,8) | 53,0 (12,3) | 91,6 (9,4) | 37,4 (14,0) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 5,7 (3,0) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 73,9 (13,7) | 68,6 (15,2) | 71,3 (16,2) | 62,4 (15,2) |
| Tiempo medio de espera en el punto peor atendido (h) | 11,60 (1,89) | 7,52 (1,70) | 10,89 (1,64) | 7,91 (1,67) |
| Kilómetros recorridos por la flota | 701,5 (259,5) | 715,1 (266,3) | 733,6 (265,6) | 738,1 (271,0) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 60,6 | [57,1; 64,0] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −5,7 | [−6,5; −4,9] | 58 / 2 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 11,5 | [10,2; 12,9] | 59 / 1 / 0 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,70 | [3,27; 4,12] | 1 / 0 / 59 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −36,6 | [−47,3; −25,9] | 50 / 0 / 10 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 6,3 | [4,4; 8,3] | 37 / 21 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,6 | [1,1; 4,1] | 40 / 3 / 17 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,71 | [0,39; 1,04] | 16 / 3 / 41 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −32,2 | [−43,0; −21,3] | 50 / 0 / 10 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 45,0 | [41,8; 48,2] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 5,3 | [4,0; 6,5] | 52 / 1 / 7 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 4,08 | [3,66; 4,50] | 0 / 0 / 60 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −13,6 | [−23,0; −4,3] | 40 / 0 / 20 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 13,67.

## Flota con dos camperos menos

Parámetros: velocidad medida × 1,00, demanda × 1,00, 2 camperos menos, factor crítico 3. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 6,2 vehículos y 5,4 cierres en promedio. `despachox` llamó 63,0 veces al optimizador por jornada, 1,28 s por llamada; la tarea de `despachox` tardó 82,0 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 96,2 (6,9) | 46,7 (11,6) | 83,9 (11,9) | 29,6 (10,7) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 7,8 (2,8) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 61,6 (14,1) | 53,7 (13,2) | 55,2 (14,5) | 47,7 (12,4) |
| Tiempo medio de espera en el punto peor atendido (h) | 12,91 (1,35) | 8,95 (1,42) | 12,42 (1,54) | 9,25 (1,52) |
| Kilómetros recorridos por la flota | 611,9 (223,6) | 621,0 (233,7) | 634,3 (233,2) | 635,1 (240,1) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 66,6 | [63,6; 69,6] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −7,8 | [−8,6; −7,1] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 13,9 | [12,5; 15,3] | 59 / 0 / 1 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,66 | [3,28; 4,04] | 0 / 0 / 60 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −23,2 | [−32,2; −14,2] | 48 / 0 / 12 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 12,3 | [9,8; 14,7] | 50 / 8 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 6,4 | [4,9; 7,9] | 50 / 2 / 8 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,49 | [0,22; 0,76] | 11 / 11 / 38 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −22,4 | [−29,6; −15,1] | 49 / 0 / 11 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 49,5 | [46,4; 52,5] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 8,0 | [6,8; 9,1] | 57 / 1 / 2 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,96 | [3,60; 4,32] | 0 / 0 / 60 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −9,1 | [−15,6; −2,6] | 43 / 0 / 17 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 14,85.

Jornadas en que la flota con dos camperos menos es igual a la de uno menos (el generador deja al menos un campero): 12 de 60.

## Factor crítico 1

Parámetros: velocidad medida × 1,00, demanda × 1,00, 0 camperos menos, factor crítico 1. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 68,2 veces al optimizador por jornada, 1,27 s por llamada; la tarea de `despachox` tardó 88,1 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 96,5 (5,0) | 67,8 (16,7) | 96,1 (4,9) | 54,7 (16,4) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 3,3 (2,4) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 86,9 (9,5) | 84,7 (10,7) | 87,5 (10,6) | 79,2 (11,8) |
| Tiempo medio de espera en el punto peor atendido (h) | 9,17 (2,19) | 5,94 (1,55) | 8,84 (1,84) | 6,23 (1,51) |
| Kilómetros recorridos por la flota | 750,0 (243,7) | 773,9 (256,3) | 804,7 (264,9) | 809,6 (256,2) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 41,8 | [38,0; 45,6] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,3 | [−3,9; −2,7] | 51 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 7,7 | [6,3; 9,0] | 56 / 0 / 4 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 2,94 | [2,49; 3,40] | 3 / 0 / 57 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −59,7 | [−74,0; −45,3] | 50 / 0 / 10 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 0,4 | [−1,0; 1,9] | 20 / 22 / 18 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,6 | [−1,7; 0,6] | 18 / 10 / 32 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,34 | [−0,06; 0,74] | 22 / 0 / 38 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −54,7 | [−68,9; −40,5] | 50 / 0 / 10 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 28,7 | [24,9; 32,6] | 59 / 1 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,2 | [1,0; 3,3] | 35 / 3 / 22 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,24 | [2,81; 3,66] | 1 / 0 / 59 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −23,9 | [−34,8; −13,0] | 43 / 0 / 17 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 9,78.

Control: filas de `ingenua` y `experta` distintas de las de la referencia: 0.

## Factor crítico 5

Parámetros: velocidad medida × 1,00, demanda × 1,00, 0 camperos menos, factor crítico 5. Semillas completas: 60 de 60.

Escenarios: 53 puntos, 132 pedidos, 42,4 t, 8,0 vehículos y 5,4 cierres en promedio. `despachox` llamó 68,5 veces al optimizador por jornada, 1,27 s por llamada; la tarea de `despachox` tardó 88,6 s por semilla. Llamadas con error: 0.

| Métrica | `despachox` | `optimiza_una_vez` | `experta` | `ingenua` |
|---|---:|---:|---:|---:|
| Pedidos de puntos críticos entregados antes de su hora límite (%) | 99,4 (2,0) | 68,3 (15,5) | 96,1 (4,9) | 54,7 (16,4) |
| Kilos perecederos que vencieron sin entregarse (%) | 0,0 (0,0) | 0,0 (0,0) | 0,0 (0,0) | 3,3 (2,4) |
| Pedidos entregados antes de su hora límite, todos los puntos (%) | 86,9 (9,6) | 84,7 (10,8) | 87,5 (10,6) | 79,2 (11,8) |
| Tiempo medio de espera en el punto peor atendido (h) | 9,24 (2,24) | 5,93 (1,46) | 8,84 (1,84) | 6,23 (1,51) |
| Kilómetros recorridos por la flota | 749,9 (243,9) | 773,3 (260,1) | 804,7 (264,9) | 809,6 (256,2) |

| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |
|---|---|---:|---|---|
| `despachox` − `ingenua` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 44,7 | [40,4; 49,0] | 60 / 0 / 0 |
| `despachox` − `ingenua` | Kilos perecederos que vencieron sin entregarse (%) | −3,3 | [−3,9; −2,7] | 51 / 9 / 0 |
| `despachox` − `ingenua` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 7,7 | [6,3; 9,0] | 55 / 1 / 4 |
| `despachox` − `ingenua` | Tiempo medio de espera en el punto peor atendido (h) | 3,01 | [2,51; 3,51] | 3 / 0 / 57 |
| `despachox` − `ingenua` | Kilómetros recorridos por la flota | −59,7 | [−73,8; −45,7] | 54 / 0 / 6 |
| `despachox` − `experta` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 3,3 | [2,1; 4,6] | 29 / 29 / 2 |
| `despachox` − `experta` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `experta` | Pedidos entregados antes de su hora límite, todos los puntos (%) | −0,6 | [−1,8; 0,6] | 23 / 7 / 30 |
| `despachox` − `experta` | Tiempo medio de espera en el punto peor atendido (h) | 0,40 | [0,04; 0,76] | 24 / 0 / 36 |
| `despachox` − `experta` | Kilómetros recorridos por la flota | −54,8 | [−69,0; −40,5] | 52 / 0 / 8 |
| `despachox` − `optimiza_una_vez` | Pedidos de puntos críticos entregados antes de su hora límite (%) | 31,1 | [27,1; 35,2] | 60 / 0 / 0 |
| `despachox` − `optimiza_una_vez` | Kilos perecederos que vencieron sin entregarse (%) | 0,0 | [0,0; 0,0] | 0 / 60 / 0 |
| `despachox` − `optimiza_una_vez` | Pedidos entregados antes de su hora límite, todos los puntos (%) | 2,2 | [1,1; 3,3] | 38 / 6 / 16 |
| `despachox` − `optimiza_una_vez` | Tiempo medio de espera en el punto peor atendido (h) | 3,31 | [2,83; 3,79] | 2 / 0 / 58 |
| `despachox` − `optimiza_una_vez` | Kilómetros recorridos por la flota | −23,4 | [−35,2; −11,5] | 42 / 0 / 18 |

Máximo de perecedero vencido en una jornada (%): `despachox` 0,00, `optimiza_una_vez` 0,00, `experta` 0,00, `ingenua` 9,78.

Control: filas de `ingenua` y `experta` distintas de las de la referencia: 0.

