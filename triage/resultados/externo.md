# Reporte de triage

- Archivo: `externo_sucio.csv`
- Hora simulada: 2026-11-20T08:25:00-05:00
- Hora del evento: no dada
- Filas leídas: 12; nuevas: 11; duplicado exacto: 1; errores internos: 0
- Integrar en pedidos: no

## Este lote

**Por estado**

- `confirmada_regla`: 3
- `consolidada`: 2
- `en_cola`: 6

**Por marca**

- `asignacion_aproximada`: 8
- `concentracion_remitente`: 1
- `familias_supuestas`: 2
- `inyeccion`: 1
- `sin_texto`: 1
- `sin_ubicar`: 3

## Estado de la base

Total de solicitudes en la base: **11**

**Por estado**

- `confirmada_regla`: 3
- `consolidada`: 2
- `en_cola`: 6

**Por marca**

- `asignacion_aproximada`: 8
- `concentracion_remitente`: 1
- `familias_supuestas`: 2
- `inyeccion`: 1
- `sin_texto`: 1
- `sin_ubicar`: 3

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 6 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| Altos de Capri | 1 | 25 | 75.45 | asignacion_aproximada:1, concentracion_remitente:1 | 4 |
| 20 de Julio | 1 | 10 | 10.375 | asignacion_aproximada:1, familias_supuestas:1 | 5 |
| sin zona | 3 | 10 | 10.375 | sin_ubicar:3 | 6, 9, 10 |
| Aranjuez | 1 | 10 | 10.167 | asignacion_aproximada:1, familias_supuestas:1, sin_texto:1 | 8 |

## Errores de lectura

| fila | campo | motivo | tipo |
|---|---|---|---|
| 5 | familias | familias_invalidas: muchas | aviso |
| 6 | recibida_en | fecha_invalida: ayer por la tarde | rechazada |
| 7 | remitente | falta_remitente | rechazada |
| 10 | familias | familias_invalidas: -3 | aviso |
| 11 | recibida_en | fecha_invalida: 31/02/2026 08:10 | rechazada |
| 12 | lat | no_numerico | aviso |
| 12 | lugar_confirmado | no_booleano | aviso |
| 0 | columna_rara | columna_desconocida | aviso |

_Datos sintéticos o de prueba. Parámetros SUPUESTO en triage/config.py._
