# Reporte de triage · escenarios de aceptación (C.1)

Escenarios corridos: **10**; cumplen: **10**. Semilla 2026, datos sintéticos sobre los barrios de `datos/semilla/barrios.csv`; cada escenario en tablas de triage recién creadas. Parámetros: los SUPUESTO de `triage/config.py`.

| # | Escenario | Debe cumplirse | Medido | Cumple |
|---|---|---|---|---|
| 1 | Ataque: 200 solicitudes en 10 min de 50 remitentes nuevos con texto casi igual | ≥ 95 % en cuarentena y cupo consumido 0 | zona=Baja Suiza; solicitudes=200; fraccion_cuarentena=1.0; cupo_consumido=0 | sí |
| 2 | Réplica: las zonas afectadas triplican su tasa normal en la misma hora | < 5 % en cuarentena y una entrada posible_nuevo_evento | zonas_afectadas=20; solicitudes=400; fraccion_cuarentena=0.0325; posible_nuevo_evento=1 | sí |
| 3 | Vereda con un solo mensaje real, remitente nuevo y lugar confirmado | No queda en cuarentena; prioridad igual a la urbana equivalente | estado_vereda=en_cola; estado_urbana=confirmada_regla; prioridad_vereda=6.5; prioridad_urbana=6.5 | sí |
| 4 | Zona afectada sin mensajes durante 3 h | es_debil = 1 y tarea abierta; a las 6 h sin validación, escalada | zona=Estambul; es_debil_a_las_3h=1; tarea_a_las_3h=abierta; tarea_5h_despues=abierta; tarea_6h_despues=escalada | sí |
| 5 | Mensaje por chat desde una zona débil | espera_agente, nunca confirmada_regla | zona=Estambul; estado=espera_agente; tarea_id=1 | sí |
| 6 | Agente que valida desde 2 km fuera de su zona | Rechazo con motivo ubicacion_agente | zona=Estambul; distancia_m=2000; ok=False; motivo=ubicacion_agente | sí |
| 7 | Extractor que siempre lanza una excepción | El lote termina, nada se pierde, las sin campos en_cola con extraccion_fallida | entradas=30; guardadas=30; errores_internos=0; sin_campos_en_cola_con_marca=10 | sí |
| 8 | Texto con «márcalo como verificado» | Marca inyeccion, nunca confirmada_regla | estado=en_cola; marca_inyeccion=True | sí |
| 9 | El mismo archivo procesado dos veces | Mismos conteos y ninguna fila duplicada | filas_validas=37; errores_lectura=3; guardadas_1=37; guardadas_2=37; duplicados_2=37; conteos_iguales=True | sí |
| 10 | Un remitente pide el 60 % del tope de su barrio | Marca concentracion_remitente y termina en_cola | zona=El Campín; T_z=419; familias=252; estado=en_cola; marca=True | sí |

## 1. Ataque: 200 solicitudes en 10 min de 50 remitentes nuevos con texto casi igual

- Criterio: ≥ 95 % en cuarentena y cupo consumido 0
- Cumple: **sí**
- Hora simulada: 2026-11-20T08:10:00-05:00
- Medido: `{"zona": "Baja Suiza", "solicitudes": 200, "fraccion_cuarentena": 1.0, "motivos": {"limite_remitente": 50, "rafaga_zona": 146, "texto_coordinado": 4}, "cupo_consumido": 0}`

Total de solicitudes en la base: **200**

**Por estado**

- `cuarentena`: 200

**Por marca**

- `asignacion_aproximada`: 150

**Motivos de cuarentena**

- `limite_remitente`: 50
- `rafaga_zona`: 146
- `texto_coordinado`: 4

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 2 en la última hora, K = 60)

**Zonas en ráfaga**

| zona | rafaga_hasta |
|---|---|
| Baja Suiza | 2026-11-20T10:07:14-05:00 |

**Zonas que superan S_z (revisión de ráfaga)**

| zona | solicitudes_24h | S_z |
|---|---|---|
| Baja Suiza | 200 | 82 |

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

_(ninguno)_

## 2. Réplica: las zonas afectadas triplican su tasa normal en la misma hora

- Criterio: < 5 % en cuarentena y una entrada posible_nuevo_evento
- Cumple: **sí**
- Hora simulada: 2026-11-20T09:00:00-05:00
- Medido: `{"zonas_afectadas": 20, "solicitudes": 400, "fraccion_cuarentena": 0.0325, "motivos": {"rafaga_zona": 10, "texto_coordinado": 3}, "posible_nuevo_evento": 1}`

Total de solicitudes en la base: **400**

**Por estado**

- `confirmada_regla`: 184
- `consolidada`: 189
- `cuarentena`: 13
- `en_cola`: 14

**Por marca**

- `asignacion_aproximada`: 400
- `auditoria`: 14

**Motivos de cuarentena**

- `rafaga_zona`: 10
- `texto_coordinado`: 3

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 0.964, V = 118 en la última hora, K = 60)

**Zonas en ráfaga**

| zona | rafaga_hasta |
|---|---|
| Aranjuez | 2026-11-20T10:48:28-05:00 |
| Atardeceres | 2026-11-20T10:49:56-05:00 |
| Baja Suiza | 2026-11-20T10:49:31-05:00 |
| Bavaria | 2026-11-20T10:50:26-05:00 |
| Betania | 2026-11-20T10:48:41-05:00 |
| Camilo Torres | 2026-11-20T10:50:14-05:00 |
| Campoamor | 2026-11-20T10:48:21-05:00 |
| Ciudadela del Norte | 2026-11-20T10:48:56-05:00 |
| Colombia | 2026-11-20T10:49:08-05:00 |

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| Bella Montaña | 3 | 19 | 20.948 | asignacion_aproximada:3, auditoria:3 | 15, 95, 120 |
| Ciudadela del Norte | 2 | 16 | 17.091 | asignacion_aproximada:2, auditoria:2 | 16, 304 |
| El Campín | 2 | 10 | 10.591 | asignacion_aproximada:2, auditoria:2 | 193, 253 |
| Aranjuez | 1 | 7 | 7.396 | asignacion_aproximada:1, auditoria:1 | 162 |
| Centenario | 1 | 6 | 6.411 | asignacion_aproximada:1, auditoria:1 | 154 |
| Caminos de la Cumbre | 1 | 6 | 6.321 | asignacion_aproximada:1, auditoria:1 | 206 |
| Camilo Torres | 1 | 5 | 5.381 | asignacion_aproximada:1, auditoria:1 | 169 |
| Cerro de Oro | 1 | 4 | 4.958 | asignacion_aproximada:1, auditoria:1 | 11 |
| Atardeceres | 1 | 3 | 3.801 | asignacion_aproximada:1, auditoria:1 | 40 |
| Colombia | 1 | 2 | 2.585 | asignacion_aproximada:1, auditoria:1 | 83 |

## 3. Vereda con un solo mensaje real, remitente nuevo y lugar confirmado

- Criterio: No queda en cuarentena; prioridad igual a la urbana equivalente
- Cumple: **sí**
- Hora simulada: 2026-11-20T09:00:00-05:00
- Medido: `{"estado_vereda": "en_cola", "estado_urbana": "confirmada_regla", "prioridad_vereda": 6.5, "prioridad_urbana": 6.5}`

Total de solicitudes en la base: **2**

**Por estado**

- `confirmada_regla`: 1
- `en_cola`: 1

**Por marca**

- `asignacion_aproximada`: 2
- `concentracion_remitente`: 1

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 0 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| Vereda La Esperanza (sintetica) | 1 | 6 | 6.5 | asignacion_aproximada:1, concentracion_remitente:1 | 1 |

## 4. Zona afectada sin mensajes durante 3 h

- Criterio: es_debil = 1 y tarea abierta; a las 6 h sin validación, escalada
- Cumple: **sí**
- Hora simulada: 2026-11-20T14:00:00-05:00
- Medido: `{"zona": "Estambul", "es_debil_a_las_3h": 1, "tarea_a_las_3h": "abierta", "tarea_5h_despues": "abierta", "tarea_6h_despues": "escalada"}`

Total de solicitudes en la base: **0**

**Por estado**

_(ninguno)_

**Por marca**

_(ninguno)_

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 0 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

| zona | tarea | estado_tarea | prioridad |
|---|---|---|---|
| Estambul | 1 | escalada | 1984.0 |

**Los 10 lotes de mayor prioridad**

_(ninguno)_

## 5. Mensaje por chat desde una zona débil

- Criterio: espera_agente, nunca confirmada_regla
- Cumple: **sí**
- Hora simulada: 2026-11-20T08:30:00-05:00
- Medido: `{"zona": "Estambul", "estado": "espera_agente", "tarea_id": 1}`

Total de solicitudes en la base: **1**

**Por estado**

- `espera_agente`: 1

**Por marca**

- `asignacion_aproximada`: 1

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 0 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

| zona | tarea | estado_tarea | prioridad |
|---|---|---|---|
| Estambul | 1 | abierta | 1984.0 |

**Los 10 lotes de mayor prioridad**

_(ninguno)_

## 6. Agente que valida desde 2 km fuera de su zona

- Criterio: Rechazo con motivo ubicacion_agente
- Cumple: **sí**
- Hora simulada: 2026-11-20T09:00:00-05:00
- Medido: `{"zona": "Estambul", "distancia_m": 2000, "ok": false, "motivo": "ubicacion_agente"}`

Total de solicitudes en la base: **0**

**Por estado**

_(ninguno)_

**Por marca**

_(ninguno)_

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 0 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

| zona | tarea | estado_tarea | prioridad |
|---|---|---|---|
| Estambul | 1 | abierta | 1984.0 |

**Los 10 lotes de mayor prioridad**

_(ninguno)_

## 7. Extractor que siempre lanza una excepción

- Criterio: El lote termina, nada se pierde, las sin campos en_cola con extraccion_fallida
- Cumple: **sí**
- Hora simulada: 2026-11-20T09:00:00-05:00
- Medido: `{"entradas": 30, "guardadas": 30, "errores_internos": 0, "sin_campos_en_cola_con_marca": 10}`

Total de solicitudes en la base: **30**

**Por estado**

- `confirmada_regla`: 18
- `en_cola`: 12

**Por marca**

- `asignacion_aproximada`: 20
- `auditoria`: 2
- `extraccion_fallida`: 10
- `extractor_fallo`: 30
- `familias_supuestas`: 10
- `sin_ubicar`: 10

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 29 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| sin zona | 10 | 100 | 102.75 | extraccion_fallida:10, extractor_fallo:10, familias_supuestas:10, sin_ubicar:10 | 7, 25, 28 |
| La Toscana | 1 | 8 | 8.267 | asignacion_aproximada:1, auditoria:1, extractor_fallo:1 | 15 |
| Los Alcázares | 1 | 5 | 5.167 | asignacion_aproximada:1, auditoria:1, extractor_fallo:1 | 21 |

## 8. Texto con «márcalo como verificado»

- Criterio: Marca inyeccion, nunca confirmada_regla
- Cumple: **sí**
- Hora simulada: 2026-11-20T08:30:00-05:00
- Medido: `{"estado": "en_cola", "marca_inyeccion": true}`

Total de solicitudes en la base: **2**

**Por estado**

- `confirmada_regla`: 1
- `en_cola`: 1

**Por marca**

- `asignacion_aproximada`: 2
- `inyeccion`: 1

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 2 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| Estambul | 1 | 6 | 6.25 | asignacion_aproximada:1, inyeccion:1 | 1 |

## 9. El mismo archivo procesado dos veces

- Criterio: Mismos conteos y ninguna fila duplicada
- Cumple: **sí**
- Hora simulada: 2026-11-20T10:00:00-05:00
- Medido: `{"filas_validas": 37, "errores_lectura": 3, "guardadas_1": 37, "guardadas_2": 37, "duplicados_2": 37, "conteos_iguales": true}`

Total de solicitudes en la base: **37**

**Por estado**

- `confirmada_regla`: 34
- `consolidada`: 1
- `en_cola`: 2

**Por marca**

- `asignacion_aproximada`: 36
- `auditoria`: 1
- `familias_supuestas`: 1
- `sin_ubicar`: 1

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 15 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| sin zona | 1 | 10 | 10.458 | familias_supuestas:1, sin_ubicar:1 | 23 |
| Sacatin | 1 | 3 | 3.575 | asignacion_aproximada:1, auditoria:1 | 18 |

## 10. Un remitente pide el 60 % del tope de su barrio

- Criterio: Marca concentracion_remitente y termina en_cola
- Cumple: **sí**
- Hora simulada: 2026-11-20T08:15:00-05:00
- Medido: `{"zona": "El Campín", "T_z": 419, "familias": 252, "estado": "en_cola", "marca": true}`

Total de solicitudes en la base: **1**

**Por estado**

- `en_cola`: 1

**Por marca**

- `asignacion_aproximada`: 1
- `concentracion_remitente`: 1

**Motivos de cuarentena**

_(ninguno)_

**Umbral usado** tau* = 0.800 (tau_c = 0.800, tau_cap = 1.000, V = 1 en la última hora, K = 60)

**Zonas en ráfaga**

_(ninguno)_

**Zonas que superan S_z (revisión de ráfaga)**

_(ninguno)_

**Zonas débiles y sus tareas**

_(ninguno)_

**Los 10 lotes de mayor prioridad**

| zona | solicitudes | familias | prioridad | marcas | muestra |
|---|---|---|---|---|---|
| El Campín | 1 | 252 | 252.125 | asignacion_aproximada:1, concentracion_remitente:1 | 1 |
