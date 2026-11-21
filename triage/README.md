# triage · filtro de solicitudes antes del despacho

Recibe solicitudes crudas (chat, agente o archivo), las limpia y decide con **reglas** si van a
`confirmada_regla`, a la cola humana (`en_cola`), a `cuarentena` (posible bot o fraude), a
`espera_agente` (zona sin señal) o se consolidan con otra. Un modelo puede extraer campos del
texto, pero nunca confirma ni descarta: solo una persona confirma (`confirmada`) o descarta.
Escribe en tablas propias (`esquema_triage.sql`) y solo toca `pedidos` con `--integrar`.
Especificación completa: [ESPEC_TRIAGE.md](ESPEC_TRIAGE.md).

**Piezas:** `entrada_datos` (CSV/JSON sucios, hash del remitente) → `antifraude` (cubeta de fichas,
cadencia, inyección, ráfaga Poisson, texto coordinado) → `geo`/`censo` (zona, topes T_z y S_z) →
`debiles` (zonas silenciosas, tareas, escalamiento) → `cluster` (ST-DBSCAN con cKDTree) →
`puntaje` (log-odds desde Beta, umbral tau*) → `cola` (prioridad y lotes). `embudo` orquesta;
`agentes` valida en terreno; `sinteticos` genera los 10 escenarios de aceptación.

## Comandos (PowerShell, desde la raíz del repositorio)

```powershell
.venv\Scripts\python -m pytest triage -q                       # pruebas del módulo
.venv\Scripts\python -m pytest -q                              # todo el proyecto
.venv\Scripts\python -m triage.correr --db $env:TEMP\triage_prueba.db --reiniciar --escenario todos --reporte triage\resultados\reporte.md
.venv\Scripts\python -m triage.correr --db $env:TEMP\triage_prueba.db --reiniciar --solicitudes triage\tests\datos\externo_sucio.csv --reporte triage\resultados\externo.md
```

Otras opciones: `--zonas zonas.csv` (por defecto, barrios de la semilla con población sintética),
`--ahora ISO`, `--hora-evento ISO` (activa la detección de zonas débiles), `--integrar` (escribe en
`pedidos`; no usar en pruebas). Salida 0 si corrió, 2 si falta un argumento o archivo.
La sal del hash sale de `DESPACHOX_SAL` o de un archivo `.sal` junto a la base (fuera de git).

## Parámetros SUPUESTO (`config.PARAMETROS_DEFECTO`, se versionan en la tabla `parametros`)

| Grupo | Valores |
|---|---|
| Censo | `a_prior` 0.10 · `tamano_hogar_defecto` 3.0 · `r_max_poligono_m` 500 · `r_max_centroide_m` 1500 |
| Clústeres y topes | `eps_s_m` 250 · `eps_t_h` 6 · `min_samples` 3 · `delta` 0.20 · `T_min` 5 · `ciclo_h` 72 · `f_bar` 10 · `m` 2 · `S_min` 3 · `phi` 0.25 · `ventana_S_h` 24 · `factor_absurdo` 10 |
| Antibots | `B_ciudadano` 3 · `B_registrado` 20 · `recarga_h` 2 · `q` 0.05 · `lambda_min` 0.1 · `alpha_rafaga` 0.001 · `rafaga_dur_h` 2 · `eta` 0.2 · `w_rafaga_h` 1 · `nuevo_h` 72 · `umbral_global` 0.40 · `k_evento` 3 · `evento_dur_h` 6 · `jaccard_texto` 0.85 · `k_coordinado` 3 · `ventana_coord_h` 1 · `min_nuevos_coord` 2 · `teja` 5 · `min_largo_coord` 30 · `cv_min` 0.1 · `n_min_cadencia` 4 · `salto_km` 3 · `ventana_salto_h` 1 |
| Puntaje | `pi_0` 0.90 · `r_costo` 4 · `tau_piso` 0.70 · `K_revision_h` 60 · `epsilon` 0.05 · `max_cambio_w` 0.5 · razones de verosimilitud por señal (`LR_DEFECTO`, Beta con `n_0` 10) |
| Zonas débiles | `alpha_sil` 0.01 · `T_min_sil_h` 3 · `t_escala_h` 6 · `auditoria_agente` 0.10 · `agente_r_poligono_m` 500 · `agente_r_centroide_m` 1500 |
| Decisión y cola | `jaccard_productos` 0.5 · `bloqueantes` · `u_albergue` 3 · `u_critico` 3 · `u_otro` 1 · `beta_ais` 1.0 · `gamma` 0.5 · `muestra_lote` 3 · `kg_por_familia` 12 |

Solo `semilla` (2026) no es supuesto. La población de la semilla es sintética (`calidad_dato =
'estimado'`); cargar censo real y citarlo en `docs/FUENTES.md` es un paso aparte.

## Decisiones propias (no estaban en la especificación)

- `concentracion_remitente` es bloqueante: con los pesos por defecto daba P = 0.84 > tau* = 0.80 y
  el escenario 10 exige que termine en cola.
- Textos de menos de 30 caracteres no cuentan como «coordinados» (`min_largo_coord`): «necesitamos
  ayuda» se repite por azar en un sismo.
- La cuarentena por texto coordinado es retroactiva sobre las del grupo aún no confirmadas por una
  persona; así el cupo consumido por un ataque queda en 0.
- Una solicitud liberada por una persona no vuelve a cuarentena por ráfaga o texto coordinado.
- Superar S_z no bloquea: la prueba de Poisson corre siempre y el reporte lista esas zonas.
- `--reiniciar` borra también las entradas de bitácora escritas por reglas de triage.
