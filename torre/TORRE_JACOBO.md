# Torre de control · Jacobo · rol C (tablero y triage)
Última actualización: 2026-11-21 00:35 (hora de Colombia, UTC−5)

## Estado en una frase
El triage está en `main`; el silencio unificado del triage espera fusión en el PR #6 (rama `jacobo-silencio`), y el tablero con Territorio, alertas por silencio, el nombre Convite y el diseño nuevo está en la rama `jacobo-tablero`, listo para push y revisión antes del congelamiento de las 8:30 a. m.

## Hecho (con el commit o archivo que lo prueba)
- **Triage en `main`** (`triage/`, commits `adaedff` a `1c8ad91`): filtro antibots y antifraude, topes por zona con censo, ST-DBSCAN propio, puntaje con log-odds, zonas débiles, agentes y cola. 10 de 10 escenarios de aceptación cumplen (`triage/resultados/reporte.md`).
- **Nombre y silencio en el canal** (`41d472e`, `9978818`): aviso del nombre Convite y de la definición única de silencio (20/11, 23:30), y aviso de que el triage ya la usa (20/11, 23:45; en el canal quedó escrito «04:45» por error: era la hora UTC).
- **Silencio unificado en el triage, PR #6** (rama `jacobo-silencio`, commit `5792fc8`, sin fusionar): `triage/debiles.py` marca una zona en silencio tras 6 h sin contacto confirmado; los mensajes en cuarentena no cuentan; Poisson solo ordena las tareas de campo. Umbral y jornada importados de `entrada/silencio.py`. 132 pruebas de triage en verde.
- **Tablero en `jacobo-tablero`** (sin fusionar):
  - Pestaña «Territorio» (T1, parte C): tabla por comuna con los peor atendidos arriba, color bajo la meta, «Barrios y veredas sin pedidos registrados» y «Descargar CSV» (`0193d65`).
  - Alertas por silencio en «Por revisar»: «Sin contacto: verificar», con «Mandar a verificar» y «Descartar», anotadas en la bitácora (`755efe2`).
  - Nombre visible Convite (`ffd9476`).
  - Diseño: tarjetas, fichas con meta, tablas con estado, paleta del informe en `.streamlit/config.toml`, mapa claro (`1c8df2e`).
  - «Pedidos pendientes» ya no cuenta las alertas por silencio; salen aparte como «N sin contacto». README del tablero al día (este commit).

## En curso (qué, hasta dónde llegó, qué falta)
- `jacobo-tablero`: falta el push, abrir el PR y que Carlos lo revise y fusione antes de las 8:30 a. m.
- PR #6 (`jacobo-silencio`): falta la revisión de Carlos y su respuesta a las preguntas de abajo.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
1. `git push -u origin jacobo-tablero` y abrir el PR hacia `main`.
2. Arrancar el tablero (`.venv\Scripts\python -m streamlit run tablero/app.py`), tomar la captura de la pestaña Territorio y publicarla en el canal (lo pide T1).

## Pendientes de la mañana
- Captura de la pestaña Territorio para el canal.
- Revisión del tablero en el celular (P4, punto 6): el jurado puede ver capturas pequeñas.
- Imagen del héroe.
- Video de respaldo de la demo a las 7:00 a. m., con el guion de `docs/GUION_DEMO.md`.

## Decisiones y por qué
- `META_CRITICOS_PCT = 100` en `tablero/datos.py`: no hay meta numérica de críticos a tiempo en el código ni en `CLAUDE.md`; se usa el umbral que ya tenía la ficha de puntualidad. Se cambia en un solo lugar si Carlos fija otra.
- «Mandar a verificar» deja la alerta en `confirmado`, porque `despacho/optimizar.py` ya lista esas alertas en `resumen.verificar` como visita sin comida. No se inventan familias ni kilos.
- Tipografía del tablero: la sans-serif del sistema, para que la demo funcione sin internet.
- Triage: sin hora del evento no evalúa silencio, para no marcar débiles todas las zonas afectadas después del mediodía.
- `tablero/` volvió a mí esta noche por pedido de Jacobo (antes, desde el 20/11 a las 14:20, lo llevaba la sesión `C-tablero` de Carlos).

## Bloqueos y preguntas para el capitán
- **PR #6, pregunta abierta para Carlos (1):** un mensaje por chat con lugar confirmado desde una zona débil queda en `espera_agente`, aunque por la definición única ese mensaje ya es contacto. La zona solo sale del silencio con `reabrir`, que exige una persona o un agente. ¿Debe ese mensaje sacar la zona del silencio?
- **PR #6, pregunta abierta para Carlos (2):** el triage no evalúa silencio si no se da la hora del evento; `entrada/silencio.py` sí cuenta desde las 06:00. ¿Lo dejamos así o lo igualamos? Es un cambio de una línea.

## Observaciones de mentores (textuales, con hora)
- Mentoría 1 (citada en `encargos/T1_TERRITORIO.md`): pidieron saber qué prototipo va a medir el efecto en la región y pensar en personas y territorio. La pestaña Territorio responde a eso.

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- `.venv\Scripts\python -m pytest -q` (todo el proyecto) y `.venv\Scripts\python -m pytest tablero -q`.
- Tablero: `$env:DESPACHOX_DB = "<ruta a la base compartida>"` y `.venv\Scripts\python -m streamlit run tablero/app.py`.
- Triage: `.venv\Scripts\python -m triage.correr --db $env:TEMP\triage_prueba.db --reiniciar --escenario todos --reporte triage\resultados\reporte.md`.
- Variables: `DESPACHOX_DB`, y la sal del hash en `DESPACHOX_SAL` o en el archivo `.sal` junto a la base (fuera de git). El tablero no usa claves de `.env`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2 (prototipo): tablero que corre, con Territorio y alertas por silencio; triage con 10 escenarios medidos (`triage/resultados/reporte.md`).
- Criterio 6 (impactos verificables): % de críticos a tiempo por comuna y CSV descargable para el piloto.
- Criterio 4 (plan de 30 a 90 días): el piloto se evalúa con la tabla por territorio.
- Criterio 5 (viabilidad y riesgos): antibots y cuarentena reversible; el despachador decide cada alerta y cada plan.
