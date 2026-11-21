# Repetición de las tandas sin versionar

Generado el 2026-11-21 a las 03:22 con `python -m analisis.sensibilidad.repetir`, commit `89a65f0`, 7 procesos, 145 s.

Las tandas que registran el commit 7131261 corrieron antes de que el envoltorio entrara al repositorio en 1e74acc. Aquí se repiten con el código versionado y se compara cada fila con la original, columna por columna. Solo se dejan fuera las que miden tiempo de reloj (recalculo_max_s, recalculo_medio_s, segundos_tarea).

| Variante | Política | Filas repetidas | Idénticas | Semillas |
|---|---|---:|---:|---|
| referencia | `despachox` | 7 | 7 | 20261150 a 20261156 |
| referencia | `optimiza_una_vez` | 30 | 29 | 20261150 a 20261179 |
| referencia | `experta` | 30 | 30 | 20261150 a 20261179 |
| referencia | `ingenua` | 30 | 30 | 20261150 a 20261179 |
| velocidad_x0.8 | `optimiza_una_vez` | 16 | 15 | 20261150 a 20261165 |
| velocidad_x0.8 | `experta` | 16 | 16 | 20261150 a 20261165 |
| velocidad_x0.8 | `ingenua` | 16 | 16 | 20261150 a 20261165 |
| demanda_x0.75 | `optimiza_una_vez` | 30 | 30 | 20261150 a 20261179 |
| demanda_x0.75 | `experta` | 30 | 30 | 20261150 a 20261179 |
| demanda_x0.75 | `ingenua` | 30 | 30 | 20261150 a 20261179 |
| demanda_x1.5 | `optimiza_una_vez` | 30 | 30 | 20261150 a 20261179 |
| demanda_x1.5 | `experta` | 30 | 30 | 20261150 a 20261179 |
| demanda_x1.5 | `ingenua` | 30 | 30 | 20261150 a 20261179 |
| flota_menos_1 | `optimiza_una_vez` | 30 | 30 | 20261150 a 20261179 |
| flota_menos_1 | `experta` | 30 | 30 | 20261150 a 20261179 |
| flota_menos_1 | `ingenua` | 30 | 30 | 20261150 a 20261179 |
| flota_menos_2 | `optimiza_una_vez` | 30 | 29 | 20261150 a 20261179 |
| flota_menos_2 | `experta` | 30 | 30 | 20261150 a 20261179 |
| flota_menos_2 | `ingenua` | 30 | 30 | 20261150 a 20261179 |

Filas distintas, original y repetición:

| Variante | Semilla | Política | a_tiempo_criticos_pct (original → repetición) | a_tiempo_todos_pct (original → repetición) | perecedero_vencido_pct (original → repetición) | km (original → repetición) |
|---|---|---|---|---|---|---|
| velocidad_x0.8 | 20261155 | `optimiza_una_vez` | 55,9 → 64,7 | 65,3 → 71,1 | 0,0 → 0,0 | 1008,5 → 987,0 |
| referencia | 20261150 | `optimiza_una_vez` | 68,0 → 68,0 | 90,6 → 88,0 | 0,0 → 0,0 | 746,7 → 750,2 |
| flota_menos_2 | 20261179 | `optimiza_una_vez` | 31,4 → 31,4 | 42,2 → 42,2 | 0,0 → 0,0 | 772,3 → 771,6 |

`optimiza_una_vez`: 163 de 166 filas idénticas; diferencia media en críticos a tiempo, repetición menos original, 0,05 puntos (de 0,0 a 8,8).
`despachox`: 7 de 7 filas idénticas; diferencia media en críticos a tiempo, repetición menos original, 0,00 puntos (de 0,0 a 0,0).

