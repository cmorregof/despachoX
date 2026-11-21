# ESPEC_TRIAGE · Encargo para Claude Code: módulo de triage de solicitudes

Versión 0.3 · 2026-11-20 (B.6.1: definición única de silencio) · Autor: Jacobo Vasco (rol C) con Claude
Ubicación de este archivo: `triage/ESPEC_TRIAGE.md`

Este documento tiene tres partes:
- **Parte A:** cómo trabajar (reglas, rama, archivos, orden y verificación).
- **Parte B:** qué construir (la especificación técnica).
- **Parte C:** cómo se prueba y cuándo está terminado.

Léelo completo antes de escribir código.

---

# PARTE A · Cómo trabajar

## A.1 Antes de empezar
1. Lee `CLAUDE.md` (reglas del equipo), `datos/esquema.sql` y `datos/db.py`. No hace falta leer nada más del repositorio para este encargo.
2. Crea la rama de trabajo y trabaja solo en ella:
   ```powershell
   git checkout -b jacobo-triage
   ```
3. **No hagas `git push`.** Jacobo lo hace a mano al final. Sí puedes hacer commits locales en la rama, con mensajes `[C-triage] qué cambió`.
4. Entorno: Windows, PowerShell, Python 3.12 en `.venv`. Usa siempre `.venv\Scripts\python` (no `python` a secas) para no depender de la activación.

## A.2 Reglas que no se rompen
1. **Arquitectura:** el modelo de lenguaje lee y estructura, las reglas calculan y una persona decide. En este módulo, ningún modelo confirma ni descarta una solicitud.
2. **Carpeta:** todo va dentro de `triage/`. No modifiques `entrada/`, `despacho/`, `tablero/`, `datos/`, `docs/`, `requirements.txt` ni `CLAUDE.md`. Solo los lees.
3. **Esquema:** las tablas nuevas van en `triage/esquema_triage.sql` y se crean con `CREATE TABLE IF NOT EXISTS`. No se tocan `datos/esquema.sql` ni las tablas existentes.
4. **Sin dependencias nuevas.** Solo la biblioteca estándar y lo que ya está en `requirements.txt`: `numpy`, `scipy`, `shapely`, `networkx`, `pandas`, `pytest`. DBSCAN se implementa a mano con `scipy.spatial.cKDTree` (sección B.3.2). No se usa `scikit-learn`.
5. **Sin red ni claves en las pruebas.** Ninguna prueba llama a un modelo de lenguaje ni a internet. El extractor es opcional e inyectable (sección B.7, paso 3).
6. **Sin datos personales reales** (Ley 1581). Los datos de prueba son sintéticos. El remitente se guarda como hash SHA-256 con sal, nunca en claro.
7. **Base aislada por defecto.** Todo el módulo recibe la ruta de la base como parámetro. Las pruebas usan bases temporales (`tmp_path` de pytest). Nunca escribas en `datos/despachox.db` salvo con la opción explícita `--integrar` (sección B.7, paso 10).
8. **Determinismo:** semilla fija `2026` y la hora siempre inyectable (parámetro `ahora`), para que las pruebas no dependan del reloj.
9. **Parámetros:** todo número marcado `SUPUESTO` vive en `triage/config.py` dentro de `PARAMETROS_DEFECTO` y se puede sobrescribir. No hay números mágicos dentro de las funciones.
10. **Robustez ante cualquier dato:** ningún dato de entrada debe tumbar el programa. Una fila mala se reporta y se salta; nunca se lanza una excepción sin manejar (sección B.12).

## A.3 Estructura de archivos que debes crear
```
triage/
  __init__.py
  ESPEC_TRIAGE.md          (este archivo; ya existe)
  README.md                qué hace, cómo correrlo, cómo probarlo
  esquema_triage.sql       tablas nuevas (B.8)
  config.py                PARAMETROS_DEFECTO y carga/guardado de versiones
  db.py                    conectar(ruta) = datos.db.conectar(ruta) + esquema_triage
  geo.py                   distancias, proyección local, asignación a zona
  censo.py                 zonas, población, topes T_z y S_z
  cluster.py               ST-DBSCAN propio con cKDTree
  antifraude.py            cubeta de fichas, ráfagas, texto coordinado, cadencia, inyección
  puntaje.py               log-odds, Beta, umbrales, actualización
  debiles.py               zonas silenciosas, aislamiento, tareas de campo, escalamiento
  agentes.py               enrolamiento y validación de agentes
  cola.py                  prioridad y lotes por zona
  embudo.py                orquesta los 13 pasos
  entrada_datos.py         lectura y validación de CSV o JSON de cualquier origen
  sinteticos.py            generador de los escenarios de prueba (C.1)
  correr.py                línea de comandos
  tests/
    __init__.py
    conftest.py            fixtures: base temporal, zonas sintéticas, hora fija
    test_geo.py
    test_censo.py
    test_cluster.py
    test_antifraude.py
    test_puntaje.py
    test_debiles.py
    test_agentes.py
    test_cola.py
    test_embudo.py
    test_entrada_datos.py
    test_escenarios.py     los 10 escenarios de aceptación (C.1)
  resultados/              reportes que genera correr.py (agregar a .gitignore local de triage si pesan)
```

## A.4 Orden de trabajo (cada fase termina verificada)
Implementa en este orden. **No pases a la fase siguiente hasta que las pruebas de la fase actual pasen.**

| Fase | Archivos | Verificación |
|---|---|---|
| 1 | `config.py`, `esquema_triage.sql`, `db.py` | `pytest triage/tests/test_*.py -q` con una prueba que crea la base temporal y comprueba que existen las 5 tablas nuevas y que las tablas originales siguen igual |
| 2 | `geo.py`, `censo.py`, `entrada_datos.py` | `test_geo`, `test_censo`, `test_entrada_datos` |
| 3 | `cluster.py` | `test_cluster`: resultados iguales a un DBSCAN de referencia por fuerza bruta en 200 puntos aleatorios con semilla 2026 |
| 4 | `antifraude.py`, `puntaje.py` | `test_antifraude`, `test_puntaje` |
| 5 | `debiles.py`, `agentes.py`, `cola.py` | `test_debiles`, `test_agentes`, `test_cola` |
| 6 | `embudo.py` | `test_embudo` |
| 7 | `sinteticos.py`, `correr.py`, `README.md` | `test_escenarios` (los 10 de C.1) y una corrida completa de `correr.py` |
| 8 | Revisión final | Toda la sección C.3 |

Al final de cada fase, haz un commit en la rama.

---

# PARTE B · Qué construir

## B.1 Conceptos y estados
- **Solicitud:** un mensaje crudo que llega por chat, por un agente o a mano.
- **Pedido:** una necesidad consolidada, es decir, una fila de la tabla existente `pedidos`.
- **Zona:** la unidad territorial con datos de censo (barrio, vereda o albergue).
- **Zona débil:** una zona afectada sin señal. Solo entra información por un agente en terreno.

Estados de `solicitudes.estado`:

| Estado | Lo asigna | Significado |
|---|---|---|
| `recibida` | sistema | Guardada en crudo |
| `cuarentena` | reglas | Sospecha de automatización o fraude. Reversible por una persona |
| `espera_agente` | reglas | Viene de una zona débil. Solo avanza con la validación de un agente |
| `consolidada` | reglas | Unida a otra solicitud o pedido existente |
| `confirmada_regla` | reglas | Superó el umbral sin marcas que lo impidan |
| `en_cola` | reglas | Espera revisión humana |
| `confirmada` | persona | Confirmada por el despachador |
| `descartada` | persona | Descartada por el despachador |

**Solo una persona puede descartar.** La función `cambiar_estado()` debe rechazar el paso a `descartada` o `confirmada` si `quien` empieza con `regla:`.

## B.2 Datos censales y demográficos

### B.2.1 Formato de entrada de zonas (`zonas.csv` o `zonas.json`)
Columnas (solo `nombre`, `lat` y `lon` son obligatorias):

| Columna | Tipo | Si falta |
|---|---|---|
| `nombre` | texto | fila inválida |
| `tipo` | `barrio`, `vereda` o `albergue` | `barrio` |
| `comuna` | texto | vacío |
| `lat`, `lon` | float (centroide) | fila inválida |
| `geom_wkt` | polígono WKT en EPSG:4326 | se asigna por centroide más cercano (B.2.4) |
| `area_km2` | float | se calcula del polígono; sin polígono, `null` |
| `personas`, `hogares` | int | se estima (B.2.3) y `calidad_dato = 'estimado'` |
| `tamano_hogar` | float | `PARAMETROS.tamano_hogar_defecto = 3.0` (SUPUESTO) |
| `afectacion` | float en [0, 1] | la de su comuna; si no hay, `a_prior = 0.10` (SUPUESTO) |
| `ocupacion` | int (solo albergues) | `null` |
| `fuente`, `fecha_corte` | texto | vacío; `calidad_dato = 'estimado'` |

**Datos de prueba por defecto:** si no se pasa un archivo de zonas, `censo.zonas_desde_semilla()` construye las zonas a partir de `datos/semilla/barrios.csv` (columnas `nombre, comuna, lat, lon`). La población es sintética, sale de la semilla 2026 y queda marcada `calidad_dato = 'estimado'`.

### B.2.2 Cálculos por zona
```
rho_z  = personas_z / area_km2_z                 (si hay área)
H_af,z = hogares_z × a_z
```

### B.2.3 Respaldo sin censo
```
hogares_z ≈ personas_z / tamano_hogar_z
personas_z (sin dato) ≈ mediana de personas de las zonas de su comuna
```
Si tampoco hay comuna, se usa la mediana de todas las zonas, con `calidad_dato = 'estimado'`.

### B.2.4 Asignación de un punto a una zona (`geo.asignar_zona`)
Firma: `asignar_zona(lat: float, lon: float, zonas: list[Zona], r_max_m: float) -> tuple[int | None, list[str]]` (devuelve el id de zona y una lista de marcas).
1. Si hay polígonos: la zona cuyo polígono contiene el punto (`shapely`). Si dos lo contienen, la de centroide más cercano.
2. Si no lo contiene ningún polígono, o no hay polígonos: la zona de centroide más cercano, siempre que esté a menos de `r_max_m` (por defecto 500 m con polígonos y 1.500 m sin ellos, SUPUESTO). Marca `asignacion_aproximada`.
3. Más lejos, o con lat/lon nulas, fuera de rango o fuera del recuadro de Manizales (`lat` entre 4.90 y 5.20, `lon` entre −75.70 y −75.30): `(None, ['sin_ubicar'])`.

## B.3 Clusterización espacial y topes

### B.3.1 Dos niveles
| Nivel | Método | Para qué |
|---|---|---|
| Fijo | Zonas (B.2) | Topes |
| Dinámico | ST-DBSCAN sobre las solicitudes | Focos, consolidación y ráfagas |

DBSCAN en lugar de K-Means: no hay que fijar el número de grupos, acepta formas irregulares (una ciudad en ladera) y deja los puntos aislados como ruido en vez de forzarlos dentro de un grupo ajeno. **Un punto marcado como ruido no se penaliza.**

### B.3.2 ST-DBSCAN propio (`cluster.st_dbscan`)
Firma: `st_dbscan(lat: np.ndarray, lon: np.ndarray, t_horas: np.ndarray, eps_s_m: float, eps_t_h: float, min_samples: int) -> np.ndarray` (etiquetas; −1 = ruido).

Implementación:
1. Proyectar a metros con una proyección local equirectangular centrada en la media:
   ```
   x = R × radians(lon − lon0) × cos(radians(lat0)),   y = R × radians(lat − lat0),   R = 6_371_000
   ```
   El error es despreciable a la escala de Manizales.
2. Con `cKDTree(np.c_[x, y]).query_ball_point(p, eps_s_m)`, obtener los vecinos espaciales de cada punto y quedarse solo con los que cumplen `|t_i − t_j| ≤ eps_t_h`. El punto cuenta como vecino de sí mismo.
3. Correr el algoritmo DBSCAN estándar sobre esa lista: núcleo si tiene `≥ min_samples` vecinos, expansión en anchura (BFS) y etiquetas en orden de descubrimiento.
4. Entradas vacías devuelven un arreglo vacío. Un solo punto devuelve `[-1]`.

Parámetros por defecto: `eps_s = 250 m`, `eps_t = 6 h`, `min_samples = 3` (todos SUPUESTO).

### B.3.3 Tope de familias por zona
```
T_z = ceil( H_af,z × (1 + delta) )                                    delta = 0.20 (SUPUESTO)
T_z (albergue) = ceil( ocupacion_z / tamano_hogar_z × (1 + delta) )
T_z = max(T_z, T_min)                                                 T_min = 5 familias (SUPUESTO)
```
`T_min` evita que una vereda pequeña, o una con datos en cero, tenga tope cero.

### B.3.4 Consumo del cupo
**Las solicitudes crudas NO consumen cupo.** Solo lo consumen los pedidos confirmados (por regla o por una persona) dentro del ciclo vigente (`ciclo_h = 72 h`, SUPUESTO).
```
C_z = Σ familias_efectivas de las solicitudes confirmadas de z con recibida_en en las últimas ciclo_h horas
familias_efectivas = max(0, min(familias_declaradas, T_z − C_z))
sobre_tope = familias_declaradas > T_z − C_z
```

### B.3.5 Tope de solicitudes por ventana de 24 h
```
S_z = max( S_min, ceil( m × T_z / f_bar ) )          f_bar = 10, m = 2, S_min = 3 (SUPUESTO)
```
Superar `S_z` no bloquea nada: activa la revisión de ráfaga de B.4.2 en esa zona.

### B.3.6 Participación máxima por remitente
```
familias_confirmadas_del_remitente_en_z + familias_declaradas > phi × T_z  →  marca concentracion_remitente
phi = 0.25 (SUPUESTO). No aplica a rol 'agente' ni a 'lider' con z en sus zonas.
```

## B.4 Filtro antibots y antifraude
Este filtro va antes de cualquier extractor. Nunca borra: su peor resultado es `cuarentena`.

### B.4.1 Cubeta de fichas por remitente (`antifraude.CubetaFichas`)
Capacidad `B = 3` y recarga de 1 ficha cada 2 h (SUPUESTO). Para `lider` y `agente`, `B = 20`. El estado de la cubeta se reconstruye con las solicitudes del remitente en la base, sin guardar memoria aparte. Sin fichas: `cuarentena` con motivo `limite_remitente`.

### B.4.2 Ráfaga por zona (Poisson)
```
lambda_z = max( lambda_min, H_af,z × q / 24 )        q = 0.05, lambda_min = 0.1 por hora (SUPUESTO)
p = 1 − scipy.stats.poisson.cdf(N − 1, lambda_z × w)  w = 1 h, N = solicitudes de z en la última hora
p < alpha_rafaga (0.001) → zona en ráfaga durante 2 h
```
Durante la ráfaga, las solicitudes de remitentes **nuevos** (primer contacto hace menos de 72 h) van a `cuarentena` con motivo `rafaga_zona`. Las de líderes y agentes siguen normal.

`lambda_z` se actualiza con un promedio móvil exponencial (`eta = 0.2`) usando solo solicitudes confirmadas, nunca las que están en cuarentena.

### B.4.3 Ráfaga global (evento real)
Si más del 40 % de las zonas con `afectacion > 0` están en ráfaga en la misma hora:
- no se aplica la cuarentena de B.4.2;
- `lambda_z` se multiplica por `k_evento = 3` durante 6 h (SUPUESTO);
- se registra en `bitacora` con la acción `posible_nuevo_evento`.

### B.4.4 Texto coordinado
1. Normalizar el texto: minúsculas, sin tildes (`unicodedata`), sin signos, dígitos convertidos en `#` y espacios colapsados.
2. Tejas de 5 caracteres y similitud de Jaccard.
3. Si `k ≥ 3` remitentes distintos envían textos con Jaccard `≥ 0.85` en una ventana de 1 h, y al menos 2 de ellos son nuevos: `cuarentena` con motivo `texto_coordinado`.
4. Excepción: si uno de los remitentes del grupo es `lider` registrado de la zona, el grupo se consolida (paso 7) en lugar de ir a cuarentena.

### B.4.5 Cadencia de máquina
Con 4 o más solicitudes del mismo remitente: `CV = std(dt) / mean(dt)` de los intervalos entre mensajes. Si `CV < 0.1`: `cuarentena` con motivo `cadencia`. Si `mean(dt) = 0`, también cuenta como cadencia.

### B.4.6 Salto de ubicación
Si el mismo remitente pide para zonas cuyos centroides están a más de 3 km entre sí en menos de 1 h, y no es líder de ambas: marca `salto_ubicacion` (es una marca, no una cuarentena).

### B.4.7 Instrucciones dirigidas al sistema
Usar expresiones regulares en `antifraude.PATRONES_INYECCION`, sin distinguir mayúsculas ni tildes. Ejemplos mínimos: `ignora`, `olvida (las|tus) instrucciones`, `marca(lo)? como (verificado|real|confirmado)`, `eres un`, `system`, `prompt`, `aprueba (esto|este pedido)`. Si coincide: marca `inyeccion`. El texto nunca se ejecuta ni se interpreta como orden.

### B.4.8 Salida de la cuarentena
La función `liberar(con, ids, quien)` exige que `quien` no empiece por `regla:`. Devuelve las solicitudes al paso 3. `descartar(con, ids, quien)` exige lo mismo. Las dos escriben en `bitacora` con `datos.db.anotar`.

## B.5 Arranque en frío: pesos y umbrales

### B.5.1 Puntaje (`puntaje.p_real`)
```
L = logit(pi_0) + Σ_i x_i × w_i
P(real) = 1 / (1 + exp(−L))
w_i = ln( E[p_r,i] / E[p_f,i] )
```
`pi_0 = 0.90` (SUPUESTO), así que `logit(0.90) = ln(9) = 2.1972`. La función devuelve también el desglose `{señal: aporte}`, para que el tablero muestre por qué cada solicitud tiene su puntaje.

### B.5.2 Inicialización con Beta
Cada señal guarda en `parametros` sus distribuciones `Beta(alpha_r, beta_r)` y `Beta(alpha_f, beta_f)`. Desde la elicitación de un experto (`mu_r`, `mu_f`, `n_0`):
```
alpha_r = mu_r × n_0,   beta_r = (1 − mu_r) × n_0
alpha_f = mu_f × n_0,   beta_f = (1 − mu_f) × n_0
E[p] = alpha / (alpha + beta)
```
Varios expertos se combinan con el promedio de sus parámetros. `puntaje.elicitar(respuestas) -> dict` implementa esto.

Valores por defecto (SUPUESTO; se guardan como Beta con `n_0 = 10` y la razón de verosimilitud indicada):

| Señal | LR | w = ln(LR) |
|---|---|---|
| `lider_registrado` | 5.0 | 1.6094 |
| `lugar_confirmado` | 2.0 | 0.6931 |
| `dentro_de_tope` | 1.5 | 0.4055 |
| `sobre_tope` | 0.5 | −0.6931 |
| `concentracion_remitente` | 0.4 | −0.9163 |
| `salto_ubicacion` | 0.3 | −1.2040 |
| `inyeccion` | 0.1 | −2.3026 |
| `validada_agente` | 50.0 | 3.9120 |

Para expresar `LR` como Beta con `n_0 = 10`: elegir `mu_f = 0.1` y `mu_r = min(0.99, LR × 0.1)`. Si `LR × 0.1 > 0.99`, fijar `mu_r = 0.99` y `mu_f = 0.99 / LR`. Prueba obligatoria: `w` reconstruido igual a `ln(LR)` con error menor que `1e-6`.

### B.5.3 Umbral (`puntaje.umbral`)
```
tau_c   = r / (r + 1)                      r = 4 → tau_c = 0.80 (SUPUESTO)
tau_cap = cuantil de P(real) de la última hora en K / V   (si V = 0 o K ≥ V: tau_cap = 1.0)
tau*    = max( tau_piso, min(tau_c, tau_cap) )            tau_piso = 0.70 (SUPUESTO)
```
`K` es la capacidad de revisión por hora. Por defecto `K = 60` (SUPUESTO), configurable.

### B.5.4 Aprendizaje con auditoría
- `epsilon = 0.05`: con generador aleatorio de semilla fija, esa fracción de las solicitudes que superan `tau*` va igual a `en_cola` con marca `auditoria`.
- `puntaje.actualizar(parametros, etiquetas) -> parametros_nuevos`: suma aciertos a `alpha` y fallos a `beta`. Cada `w_i` puede cambiar como máximo ±0.5 por actualización. Devuelve una versión nueva **sin aplicarla**. Aplicarla requiere `config.aprobar_version(con, version, quien)` con un `quien` humano.

## B.6 Zonas débiles, casos borde y agentes

### B.6.1 Zona silenciosa (`debiles.detectar`)
Definición única de silencio, acordada en el aviso de `torre/CANAL.md` del 20/11 a las 23:30 (Jacobo y Samuel) y compartida con `entrada/silencio.py` y `despacho.territorio.silencio()`:

- Una zona con `afectacion > 0` está **en silencio** cuando lleva `silencio_h` horas o más sin contacto (6 h, SUPUESTO), contadas desde la hora más tardía entre el inicio de la jornada (`jornada_inicio`, 06:00 de Bogotá) y `hora_evento`, o desde el último contacto si es posterior.
- **Contacto** = una solicitud de la zona con canal `chat` y `lugar_confirmado = 1`, o cualquier solicitud de canal `agente`, en un estado distinto de `cuarentena` y `descartada`. Un mensaje en cuarentena no cuenta: un ataque de bots no apaga la alerta.
- `silencio_h` y `jornada_inicio` se importan de `entrada.silencio` (`UMBRAL_H`, `DESPACHOX_JORNADA_INICIO`); una prueba comprueba que coinciden.
- Sin `hora_evento` el triage no evalúa silencio. La hora del evento es un parámetro que se guarda en `parametros`.
- La prueba de Poisson **ya no decide** si hay silencio; solo ordena las tareas de campo:
```
mu_z = lambda_z × horas_de_silencio
prioridad_tarea = H_af,z × (1 + aislada) × (1 − exp(−mu_z))
```
`alpha_sil` y `T_min_sil_h` siguen en `config.py`, obsoletos para la decisión, para poder leer versiones guardadas de parámetros.

### B.6.2 Zona aislada (opcional, solo si hay grafo)
`debiles.aislada(grafo, nodo_zona, nodos_acopio, aristas_cerradas) -> bool`: devuelve verdadero si no hay camino en `networkx` desde ningún acopio después de quitar las aristas cerradas. Sin grafo, devuelve `False` y no falla. Las pruebas usan un grafo pequeño hecho a mano.

### B.6.3 Regla de negocio: solo entra por el agente
- Al marcar una zona como débil, se crea una tarea de campo con la `prioridad_tarea` de B.6.1.
- Una solicitud que no venga de un agente y caiga en una zona débil pasa a `espera_agente` y se liga a la tarea.
- **Escalamiento:** si una tarea sigue en estado `abierta` o `asignada` más de `t_escala = 6 h` (SUPUESTO), pasa a `escalada` y se anota en la bitácora. Una persona puede entonces confirmar a mano las solicitudes en espera.
- La zona deja de ser débil solo con `debiles.reabrir(con, zona_id, quien)`, que requiere un humano o un agente.

### B.6.4 Agentes (`agentes.py`)
- `enrolar(con, remitente_hash, organizacion, zonas, quien)`: crea o actualiza el remitente con rol `agente`. `quien` debe ser humano.
- `validar(con, agente_hash, tarea_id, lat, lon, necesidades, ahora)`: valida y devuelve el resultado.
  - Rechaza si el remitente no es agente activo (motivo `no_es_agente`).
  - Rechaza si la ubicación está a más de 500 m del polígono de la zona, o a más de 1.500 m del centroide si no hay polígono (`ubicacion_agente`).
  - Por cada necesidad crea una solicitud con `canal = 'agente'` y la señal `validada_agente`, y la pasa por los pasos 7 a 10 del embudo. Los topes siguen aplicando.
  - Las solicitudes en `espera_agente` de esa tarea se marcan `consolidada` dentro de lo validado, o pasan a `en_cola` si el agente no las cubrió.
  - El 10 % de las validaciones (generador con semilla) lleva la marca `auditoria_agente`.

### B.6.5 Casos borde (todos con prueba)
| Caso | Tratamiento |
|---|---|
| Sin ubicación o con coordenadas inválidas | `en_cola` con marca `sin_ubicar` |
| Familias faltantes, en cero, negativas o no numéricas | `f_bar` con marca `familias_supuestas`. Nunca se confirma por regla |
| Familias absurdas (más de 10 × `T_z`) | Marca `sobre_tope` y `familias_absurdas` |
| Texto vacío o solo espacios | Se procesa con texto vacío y marca `sin_texto` |
| Extractor ausente o que lanza excepción | Se usan los campos estructurados de la fila. Si no hay, `en_cola` con marca `extraccion_fallida`. Nunca se cae el lote |
| Zona sin censo | B.2.3 |
| Mensaje repetido idéntico | Idempotencia por `hash_mensaje = sha256(remitente_hash + texto_normalizado + minuto)` |
| Fechas en formatos distintos | `entrada_datos` acepta ISO 8601 y `dd/mm/aaaa hh:mm`. Sin zona horaria, se asume Bogotá (UTC−5). Fecha inválida: fila rechazada en el reporte |
| Texto con caracteres raros o emojis | Se conserva; la normalización los quita solo para comparar textos |
| Archivo en UTF-8 con BOM, Latin-1 o separador `;` | `entrada_datos` lo detecta |

## B.7 El embudo (`embudo.procesar_lote`)
Firma: `procesar_lote(con, solicitudes: list[dict], params: dict, ahora: datetime, extractor: Callable | None = None, integrar: bool = False) -> dict` (devuelve un resumen por estado y por marca).

Las solicitudes se procesan en orden de `recibida_en`. Los pasos:

1. **Ingesta.** Insertar en `solicitudes` con `hash_mensaje`. Si el hash ya existe, se omite y cuenta como `duplicado_exacto` en el resumen.
2. **Prefiltro sin modelo.** B.4.1, B.4.5 y B.4.7. Si va a cuarentena, se detiene aquí.
3. **Extracción.** Si hay `extractor`, `extractor(texto) -> dict` con `familias`, `productos`, `lugar`, `lat`, `lon`, `lugar_confirmado`, envuelto en `try/except`. Si no hay, se usan los campos de la fila.
4. **Zona.** B.2.4.
5. **Zona débil.** Si la zona es débil y el canal no es `agente`: `espera_agente`, se liga a la tarea y se detiene aquí.
6. **Ráfaga y coordinación.** B.4.2, B.4.3 y B.4.4.
7. **Consolidación.** ST-DBSCAN sobre las solicitudes de la ventana `eps_t`. Dentro de un mismo clúster y una misma zona, una solicitud nueva se consolida en la más antigua no descartada si la similitud de Jaccard de sus productos (como conjuntos) es al menos 0.5. Las familias se toman como el máximo entre las dos, no la suma. Se guarda `consolidada_en`. Interfaz para la versión 0.3: `consolidar(grupo) -> list[(id_hija, id_madre)]`.
8. **Topes.** B.3.4 y B.3.6.
9. **Puntaje.** B.5.1. Se guardan `p_real` y `senales`.
10. **Decisión.**
    ```
    BLOQUEANTES = {sobre_tope, familias_supuestas, familias_absurdas, inyeccion, sin_ubicar, extraccion_fallida}
    si P(real) ≥ tau* y marcas ∩ BLOQUEANTES = ∅:
        con probabilidad epsilon → en_cola + marca auditoria
        si no → confirmada_regla; anotar(con, 'regla:v<version>', 'confirmar_solicitud', detalle)
                si integrar=True: crear o actualizar la fila de pedidos con estado 'confirmado'
    si no:
        en_cola
    ```
    Con `integrar=False` (por defecto) **no se toca la tabla `pedidos`**.
11. **Cola** (`cola.prioridad`, `cola.lotes`):
    ```
    prioridad = u_punto × familias_efectivas × (1 + beta_ais × aislada) + gamma × horas_en_cola
    u_punto: albergue = 3, punto crítico = 3, otro = 1        beta_ais = 1.0, gamma = 0.5 (SUPUESTO)
    ```
    `lotes(con)` agrupa la cola por zona y devuelve, por lote, conteos calculados en código (solicitudes, familias, marcas) y una muestra de 3 ids elegida con la semilla.
12. **Plan.** Fuera del alcance: lo hace `despacho/` y lo aprueba una persona.
13. **Retroalimentación.** `puntaje.etiquetas_desde_bitacora(con)` lee las confirmaciones y descartes humanos para B.5.4.

## B.8 Esquema (`triage/esquema_triage.sql`)
```sql
CREATE TABLE IF NOT EXISTS zonas (
  id INTEGER PRIMARY KEY, nombre TEXT NOT NULL,
  tipo TEXT NOT NULL DEFAULT 'barrio' CHECK(tipo IN ('barrio','vereda','albergue')),
  comuna TEXT, lat REAL NOT NULL, lon REAL NOT NULL, geom_wkt TEXT, area_km2 REAL,
  personas INTEGER, hogares INTEGER, tamano_hogar REAL, afectacion REAL, ocupacion INTEGER,
  critico INTEGER DEFAULT 0,
  calidad_dato TEXT DEFAULT 'fuente' CHECK(calidad_dato IN ('fuente','estimado')),
  fuente TEXT, fecha_corte TEXT,
  es_debil INTEGER DEFAULT 0, aislada INTEGER DEFAULT 0,
  lambda_h REAL, rafaga_hasta TEXT
);
CREATE TABLE IF NOT EXISTS remitentes (
  remitente_hash TEXT PRIMARY KEY,
  rol TEXT NOT NULL DEFAULT 'ciudadano' CHECK(rol IN ('ciudadano','lider','agente')),
  zonas TEXT DEFAULT '[]', organizacion TEXT, primer_contacto TEXT,
  estado TEXT DEFAULT 'activo' CHECK(estado IN ('activo','suspendido','bloqueado')),
  auditorias_fallidas INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tareas_campo (
  id INTEGER PRIMARY KEY, zona_id INTEGER REFERENCES zonas(id),
  creada_en TEXT NOT NULL, motivo TEXT, prioridad REAL,
  agente_hash TEXT REFERENCES remitentes(remitente_hash),
  estado TEXT NOT NULL DEFAULT 'abierta'
    CHECK(estado IN ('abierta','asignada','validada','escalada','cerrada')),
  cerrada_en TEXT
);
CREATE TABLE IF NOT EXISTS solicitudes (
  id INTEGER PRIMARY KEY, recibida_en TEXT NOT NULL,
  hash_mensaje TEXT UNIQUE NOT NULL, remitente_hash TEXT NOT NULL,
  canal TEXT NOT NULL DEFAULT 'chat' CHECK(canal IN ('chat','agente','manual')),
  texto TEXT, zona_id INTEGER REFERENCES zonas(id), lat REAL, lon REAL,
  tipo_punto TEXT, productos TEXT DEFAULT '[]',
  familias_declaradas INTEGER, familias_efectivas INTEGER,
  lugar_confirmado INTEGER DEFAULT 0,
  estado TEXT NOT NULL DEFAULT 'recibida' CHECK(estado IN
    ('recibida','cuarentena','espera_agente','consolidada','confirmada_regla','en_cola','confirmada','descartada')),
  motivo_cuarentena TEXT, marcas TEXT DEFAULT '[]', senales TEXT DEFAULT '{}',
  p_real REAL, cluster_id INTEGER, consolidada_en INTEGER REFERENCES solicitudes(id),
  pedido_id INTEGER REFERENCES pedidos(id), tarea_id INTEGER REFERENCES tareas_campo(id)
);
CREATE TABLE IF NOT EXISTS parametros (
  version INTEGER PRIMARY KEY, creada_en TEXT NOT NULL,
  aprobada_por TEXT, aplicada INTEGER DEFAULT 0, valores TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_sol_zona_t ON solicitudes(zona_id, recibida_en);
CREATE INDEX IF NOT EXISTS ix_sol_rem_t ON solicitudes(remitente_hash, recibida_en);
CREATE INDEX IF NOT EXISTS ix_sol_estado ON solicitudes(estado);
```
`triage/db.py`: `conectar(ruta)` llama a `datos.db.conectar(ruta)` y luego a `executescript` con este archivo. Si `parametros` está vacía, inserta la versión 1 con `PARAMETROS_DEFECTO`, `aprobada_por = 'inicial'` y `aplicada = 1`.

## B.9 Parámetros por defecto (`config.PARAMETROS_DEFECTO`)
```python
PARAMETROS_DEFECTO = {
    "a_prior": 0.10, "tamano_hogar_defecto": 3.0,
    "r_max_poligono_m": 500, "r_max_centroide_m": 1500,
    "eps_s_m": 250, "eps_t_h": 6, "min_samples": 3,
    "delta": 0.20, "T_min": 5, "ciclo_h": 72,
    "f_bar": 10, "m": 2, "S_min": 3, "phi": 0.25,
    "B_ciudadano": 3, "B_registrado": 20, "recarga_h": 2,
    "q": 0.05, "lambda_min": 0.1, "alpha_rafaga": 0.001, "rafaga_dur_h": 2, "eta": 0.2,
    "umbral_global": 0.40, "k_evento": 3, "evento_dur_h": 6,
    "jaccard_texto": 0.85, "k_coordinado": 3, "ventana_coord_h": 1,
    "cv_min": 0.1, "salto_km": 3, "ventana_salto_h": 1,
    "pi_0": 0.90, "r_costo": 4, "tau_piso": 0.70, "K_revision_h": 60,
    "epsilon": 0.05, "max_cambio_w": 0.5,
    "silencio_h": 6, "jornada_inicio": "06:00",   # importados de entrada.silencio
    "alpha_sil": 0.01, "T_min_sil_h": 3,          # obsoletos para la decisión (B.6.1)
    "t_escala_h": 6, "auditoria_agente": 0.10,
    "agente_r_poligono_m": 500, "agente_r_centroide_m": 1500,
    "jaccard_productos": 0.5,
    "u_albergue": 3, "u_critico": 3, "u_otro": 1, "beta_ais": 1.0, "gamma": 0.5,
    "semilla": 2026, "hora_evento": None,
    "senales": { ... },   # Beta por señal según B.5.2
}
```
Todos son SUPUESTO salvo `semilla`.

## B.10 Formato de entrada de solicitudes (`entrada_datos.leer`)
Acepta CSV (con separador `,` o `;`) y JSON (lista de objetos). Columnas reconocidas, sin distinguir mayúsculas y con alias:

| Campo | Alias aceptados | Obligatorio |
|---|---|---|
| `recibida_en` | `fecha`, `hora`, `timestamp` | sí |
| `remitente` | `remitente_hash`, `chat_id`, `telefono` | sí (si viene en claro, se convierte a hash al leer y nunca se guarda en claro) |
| `texto` | `mensaje` | no |
| `lat`, `lon` | `latitud`, `longitud` | no |
| `familias` | `familias_declaradas` | no |
| `productos` | — (JSON o lista separada por comas) | no |
| `tipo_punto` | — | no |
| `canal` | — | no (por defecto `chat`) |
| `lugar_confirmado` | — (1/0, sí/no, true/false) | no |

Devuelve `(filas_validas: list[dict], errores: list[dict])`. Cada error lleva el número de fila, el campo y el motivo. Nunca lanza una excepción por contenido; solo por un archivo inexistente, con un mensaje claro.

## B.11 Línea de comandos (`python -m triage.correr`)
```
--db RUTA                 base SQLite (obligatoria; usa una temporal para pruebas)
--zonas ARCHIVO           zonas.csv o .json (por defecto: las de la semilla)
--solicitudes ARCHIVO     solicitudes.csv o .json
--escenario NOMBRE|todos  genera un escenario de C.1 en lugar de leer un archivo
--ahora ISO               hora simulada (por defecto, la de la última solicitud)
--hora-evento ISO         hora del sismo, para B.6.1
--reiniciar               borra solo las tablas de triage antes de correr
--integrar                escribe en pedidos (NO usar en pruebas)
--reporte ARCHIVO.md      escribe el reporte
```
El reporte incluye: conteo por estado y por marca, las zonas en ráfaga, las zonas débiles y sus tareas, el umbral `tau*` usado, los 10 lotes de mayor prioridad y los errores de lectura. La salida en consola es un resumen de pocas líneas. El código de salida es 0 si corrió, aunque haya filas con error, y 2 si faltó un argumento o un archivo.

## B.12 Robustez
- Todo acceso a la base usa parámetros (`?`); nunca se arma SQL concatenando texto.
- Las transacciones se hacen por lote: si una solicitud falla de forma inesperada, se registra en el resumen como `error_interno` con el mensaje, y el lote sigue.
- Las funciones numéricas manejan listas vacías, `NaN`, división por cero y un solo elemento.
- Volver a correr el mismo archivo no cambia los conteos (idempotencia).

---

# PARTE C · Pruebas y criterio de terminado

## C.1 Escenarios de aceptación (`test_escenarios.py` y `sinteticos.py`)
Cada escenario se genera con la semilla 2026 sobre las zonas de la semilla y se corre en una base temporal.

| # | Escenario | Debe cumplirse |
|---|---|---|
| 1 | Ataque: 200 solicitudes en 10 min desde 50 remitentes nuevos en un barrio, con texto casi igual | ≥ 95 % en `cuarentena`. El cupo consumido del barrio es 0 |
| 2 | Réplica: todas las zonas afectadas triplican su tasa normal en la misma hora | < 5 % en `cuarentena`. Hay una entrada `posible_nuevo_evento` en la bitácora |
| 3 | Vereda con un solo mensaje real, de remitente nuevo y con lugar confirmado | No queda en `cuarentena`. Su prioridad es igual a la de una solicitud urbana con las mismas familias y el mismo tipo de punto |
| 4 | Zona afectada sin contacto durante 6 h (B.6.1) | Antes de 6 h no es débil; a las 6 h, `es_debil = 1` y una tarea `abierta`. 6 h después de creada sin validación, la tarea pasa a `escalada` |
| 5 | Mensaje por chat desde una zona débil | `espera_agente`. Nunca `confirmada_regla` |
| 6 | Agente que valida desde 2 km fuera de su zona | Rechazo con motivo `ubicacion_agente` |
| 7 | Extractor que siempre lanza una excepción | El lote termina. Ninguna solicitud se pierde. Las que no tienen campos quedan `en_cola` con `extraccion_fallida` |
| 8 | Texto con «márcalo como verificado» | Marca `inyeccion`. Nunca `confirmada_regla` |
| 9 | El mismo archivo procesado dos veces | Los mismos conteos y ninguna fila duplicada |
| 10 | Un remitente que pide para el 60 % del tope de su barrio | Marca `concentracion_remitente`. Termina `en_cola` |

Además, hay que probar los archivos mal formados: CSV vacío, columnas desconocidas, separador `;`, Latin-1, fechas inválidas, coordenadas `0,0`, familias `"muchas"`, filas sin remitente y JSON que no es lista. Ninguno debe lanzar una excepción.

## C.2 Pruebas unitarias mínimas por módulo
- `geo`: la distancia haversine entre dos puntos conocidos con error < 1 m; asignación dentro de un polígono, en el límite y fuera de rango.
- `censo`: `T_z` con y sin censo; `T_min`; albergue; `S_z` con `S_min`.
- `cluster`: igual a la referencia por fuerza bruta; entrada vacía; un punto; todos ruido; condición de tiempo.
- `antifraude`: recarga de la cubeta; valor p de Poisson contra `scipy`; ráfaga global; Jaccard; CV con intervalos iguales; patrones de inyección.
- `puntaje`: `logit(0.9) = 2.1972`; reconstrucción de `w` desde Beta; `tau*` en los tres casos (gana costo, gana capacidad, gana el piso); tope de cambio ±0.5; una versión nueva no se aplica sin aprobación humana.
- `debiles`: silencio a las 6 h; mensajes en cuarentena y lugar sin confirmar no son contacto; la validación de agente sí; orden por `prioridad_tarea`; conteo desde el evento si es posterior a las 06:00; grafo aislado y no aislado; escalamiento.
- `agentes`: no agente; fuera de zona; validación correcta.
- `cola`: orden por prioridad; aumento con la espera; lotes con conteos exactos.
- `embudo`: cada estado se alcanza; con `integrar=False`, la tabla `pedidos` no cambia; solo un humano puede descartar.

## C.3 Definición de terminado
Todo esto debe cumplirse, en este orden, y Claude Code debe mostrar la salida de cada comando:

1. Pruebas del módulo:
   ```powershell
   .venv\Scripts\python -m pytest triage -q
   ```
   Todas pasan, sin pruebas saltadas.
2. **No se rompió nada del resto del proyecto:**
   ```powershell
   .venv\Scripts\python -m pytest -q
   ```
   El mismo número de pruebas que antes de empezar pasa igual. Anota ese número antes de la fase 1.
3. Corrida completa con todos los escenarios:
   ```powershell
   .venv\Scripts\python -m triage.correr --db $env:TEMP\triage_prueba.db --reiniciar --escenario todos --reporte triage\resultados\reporte.md
   ```
   Termina con código 0, y el reporte existe y muestra los 10 escenarios.
4. Corrida con un archivo externo cualquiera (crea `triage\tests\datos\externo_sucio.csv` con filas buenas y malas mezcladas):
   ```powershell
   .venv\Scripts\python -m triage.correr --db $env:TEMP\triage_prueba.db --reiniciar --solicitudes triage\tests\datos\externo_sucio.csv --reporte triage\resultados\externo.md
   ```
   Termina con código 0. Las filas malas aparecen en la sección de errores del reporte.
5. Ningún archivo fuera de `triage/` aparece modificado:
   ```powershell
   git status --porcelain
   ```
   Todas las rutas empiezan por `triage/`.
6. No hay secretos ni datos personales: busca `ANTHROPIC`, `TOKEN`, `+57` y números de 10 dígitos en `triage/` y confirma que no aparecen.
7. `triage/README.md` explica en menos de una página qué hace el módulo, los comandos anteriores y la lista de parámetros SUPUESTO.
8. Commit final en la rama `jacobo-triage`: `[C-triage] Módulo de triage con pruebas y escenarios`. **Sin push.**

Al terminar, Claude Code entrega a Jacobo:
- la salida de los comandos 1 a 5;
- el número de pruebas que pasan;
- lo que no pudo cumplir, si algo quedó pendiente, y por qué;
- el comando de push para que Jacobo lo ejecute: `git push -u origin jacobo-triage`.

## C.4 Fuera de alcance
- Integración con el tablero (botones de cuarentena, lotes): lo decide la sesión C-tablero después del visto bueno del capitán.
- Integración en vivo con el bot de `entrada/`.
- Datos reales de censo: el formato está listo (B.2.1), pero cargarlos y citarlos en `docs/FUENTES.md` es un paso aparte.
- La versión 0.3 de la consolidación de duplicados.
