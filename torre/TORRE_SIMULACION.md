# Torre de control · Carlos · sesión `simulacion` (rol B, medición)
Última actualización: sábado 21 de noviembre de 2026, 7:30 a. m. (agente de simulación de Fable).

## Estado en una frase
Sección 9 de `docs/SIMULACION.md` en la rama `simulacion`, sin fusionar a `main`: con las velocidades de la tesis UNAL de 2019 (tabla 14), DespachoX gana a `experta` en críticos a tiempo en las tres cargas y le ahorra de 42 a 56 km por jornada.

## Hecho (con el commit o archivo que lo prueba)
- Noche del 20 al 21, rama `simulacion` (encargo de Fable, aprobado por Carlos):
  - opción `--velocidades medidas` (variable `DESPACHOX_SIM_VELOCIDADES`) que toma `datos_publicos/velocidades.csv` por tipo de vía, también en el optimizador, sin tocar `optimizar.py` ni `matriz.py`; apagada por defecto y probada idéntica a antes (commit 1489760, `despacho/sim/tests/test_velocidades.py`);
  - confirmación de la sección 8.3 con esas velocidades: semillas 20261150 a 20261179, las tres cargas, factor 3, 360 jornadas, 0 errores del optimizador (`despacho/sim/resultados_velocidades/confirmacion_factor_3/`);
  - la misma confirmación con las velocidades del modelo sobre la misma red, para separar la velocidad de la red: 360 jornadas, 0 errores, de 6:03 a 7:23 a. m. (`resultados_velocidades/modelo_misma_red/`). Con esas velocidades DespachoX empata con `experta` en críticos salvo en carga alta y queda 2,6 y 2,7 puntos debajo en el total con carga media y alta; con las de la tesis le gana en críticos en las tres cargas y en el total con carga alta;
  - tablas con `python -m despacho.sim.comparar` (`resultados_velocidades/tablas.md`) y sección 9 de `docs/SIMULACION.md`.
- No se hicieron: el día sin cierres (se cortó con el servidor a la 1:00 a. m. y Fable decidió no repetirlo) ni la vida útil por producto. La opción `--vida-util csv` quedó escrita y probada en la rama local `sim-dev` de `/home/claude/sim-dev` (commit f81db71), sin empujar.
- Primera ronda: pull request 1, fusionado. 360 jornadas, `despacho/sim/resultados/`.
- S2, en `main` (commit 4cece34) y en `despacho/sim/resultados_s2/`:
  - regla de elección del factor escrita antes de correr (`docs/SIMULACION.md`, 8.1, commit 3ffdf69);
  - barrido de `FACTOR_CRITICO` 1, 3, 10 y 30: ninguno cumple la regla (`barrido_factor.md`);
  - factor 3 en semillas nuevas 20261150 a 20261179: no supera a `experta` de forma significativa;
  - error de ubicación de pedidos con p 0, 0,1 y 0,2: confirmar sube las entregas a tiempo de todos los puntos 6,0 y 10,7 puntos;
  - 0, 5 y 10 cierres: casi no cambia nada;
  - dos camperos menos: DespachoX supera a `experta` en el total por 3,4 puntos y la ingenua pasa la meta de perecederos (5,7 %);
  - carga media con 3 y 8 s de búsqueda: igual que con 1 s (`resultados_s2/busqueda_3s/`, `despacho/sim/resultados_8s/`);
  - carga media sobre `manizales_region.graphml`: mismas conclusiones que en la red urbana (`resultados_s2/red_ampliada/`);
  - sección 7 de `docs/SIMULACION.md` actualizada.
- Red del Eje Cafetero (Caldas, Risaralda, Quindío) en `despacho/cache/eje_cafetero.graphml` de este árbol. No está en git (62 MB, carpeta ignorada).

## En curso (qué, hasta dónde llegó, qué falta)
- Nada. Las corridas de la noche terminaron y están en la rama `simulacion`.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
- Fable o Carlos deciden si la rama `simulacion` se fusiona a `main` y si la frase de la sección 9.7 entra al pitch (está «por aprobar»).
- Una persona debe abrir la tesis (tabla 14, pp. 46 a 48) y confirmar de dónde salen las velocidades. Hoy: revisado por máquina.
- Para B: `despacho/red.py` sigue con las velocidades del modelo. La simulación de la sección 9 le da al optimizador las de la tesis.
- Pendientes, si se piden: día sin cierres con estas velocidades (`--cierres 0`, pedido de Samuel) y vida útil por producto (rama local `sim-dev`).
- Las corridas sobre la red urbana necesitan `DESPACHOX_GRAFO=despacho/cache/manizales.graphml`, porque `red.py` lee `manizales_region.graphml` por defecto. Ese archivo no estaba en la máquina de la noche.

## Decisiones y por qué
- La sesión corre en el árbol `.claude/worktrees/simulacion-completa-e82eb3`, que ya está aislado de la carpeta de B. No se creó `../despachoX-sim`. La rama se publica como `simulacion`.
- Las entradas del canal y esta torre se suben a `main`; el código va solo en la rama.
- Se añadió una línea base `experta` (prioridad por urgencia y primero lo que vence) además de la `ingenua` del encargo. En los ensayos casi empata con DespachoX en puntos críticos; la ventaja de DespachoX aparece en las entregas a tiempo de todos los puntos.
- El tope de paradas de la línea base se calibró a su favor (sin tope) con semillas 100 a 111, distintas de las de evaluación (20261120 a 20261149).
- Tres niveles de carga (2, 2,5 y 3 pedidos por punto), elegidos mirando solo a la política ingenua: 86 %, 74 % y 52 % a tiempo en críticos.
- El adaptador llama a `optimizar._resolver` con filas armadas en memoria, sin base de datos. Como ese modelo planea un viaje por vehículo, `despachox` también recalcula cuando un vehículo vuelve al acopio.
- Un camión sin regreso por su red sale por cualquier vía al doble del tiempo. Sin esa regla, los sentidos únicos de la red de camión «atrapaban» vehículos y su carga contaba como desperdicio.
- Noche del 20 al 21: nada va a `main` (Fable, 6:03 a. m.). La sección 9 usa la red ampliada porque la urbana no estaba en la máquina, y repite la corrida con las velocidades del modelo sobre esa misma red para separar el efecto de la velocidad del de la red.
- Las velocidades se describen como «derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48)», no como «medidas» a secas (Fable, 6:22 a. m.).

## Bloqueos y preguntas para el capitán
- Para B o Carlos: cambiar `FACTOR_CRITICO` de 1 a 3 en `optimizar.py` (canal).
- Carlos autorizó a las 4:55 p. m. el empuje directo de esta sesión a `main`, pese a la regla de las 4:05 p. m. de no subir directo.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Intérprete: `.venv` de la carpeta principal. El grafo debe estar en `despacho/cache/manizales.graphml`.
- `python -m pytest despacho/sim/tests -q`
- `python -m despacho.sim.correr --semillas 30 --carga todas` (opciones: `--red malla|osm`, `--optimizador provisional|b`, `--limite`, `--procesos`, `--factor-critico`, `--p-error`, `--cierres`, `--camperos-menos`, `--politicas`, `--base`).
- `python -m despacho.sim.barrido despacho/sim/resultados_s2` rehace la tabla del barrido.
- Sección 9: copiar `despliegue/grafo/manizales_region.graphml` a `despacho/cache/`, y correr `python -m despacho.sim.correr --semillas 30 --base 20261150 --carga todas --factor-critico 3 --procesos 2 --velocidades medidas` (o `modelo`). Las tablas: `python -m despacho.sim.comparar despacho/sim/resultados_velocidades`. Cada corrida de 360 jornadas tarda cerca de 1 h 20 min con 2 procesos.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 6: indicadores medidos con línea base, 30 semillas e IC del 95 % (`docs/SIMULACION.md`, sección 5).
- Criterio 3: diseño pareado con dos líneas base, supuestos escritos y límites declarados.
- Criterio 2: 19 pruebas del motor y del adaptador; el optimizador corrió 360 jornadas sin errores.
- Criterios 3 y 6: la sección 9 repite las cifras con velocidades de una tesis de la UNAL Manizales, con línea base, 90 escenarios, IC del 95 % y supuestos con su estado.
