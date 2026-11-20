# Torre de control · Carlos · sesión `simulacion` (rol B, medición)
Última actualización: viernes 20 de noviembre de 2026, 12:00 m.

## Estado en una frase
Simulación terminada y medida con el optimizador de B; pull request 1 abierto de `simulacion` a `main`, sin fusionar.

## Hecho (con el commit o archivo que lo prueba)
- Rama `simulacion` (commit ac731d2), pull request https://github.com/cmorregof/despachoX/pull/1.
- `despacho/sim/`: escenario, motor, políticas, métricas, corrida pareada, adaptador a `optimizar.py` y 19 pruebas.
- Corrida oficial: 30 semillas por tres niveles de carga, 360 jornadas, cero errores del optimizador. `despacho/sim/resultados/resumen.md` y `resultados.csv`.
- `docs/SIMULACION.md`: diseño, supuestos, resultados y «Lo que esta simulación no prueba».
- Resultado: DespachoX supera al orden de llegada en críticos a tiempo por 12,0, 28,9 y 46,3 puntos. No supera a la línea base `experta` en los indicadores del reto; le gana en kilómetros.

## En curso (qué, hasta dónde llegó, qué falta)
- Descarga de la red de Caldas, Risaralda y Quindío (`despacho/cache/eje_cafetero.graphml`): Overpass no ha respondido.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
- Carlos revisa y fusiona el pull request 1.
- Si B cambia los pesos del objetivo, repetir: `python -m despacho.sim.correr --semillas 30 --carga todas --optimizador b --limite 1 --procesos 9` y actualizar la sección 5 de `docs/SIMULACION.md`.
- Pendiente opcional: probar el optimizador con 8 s de búsqueda en una carga (cuesta cerca de dos horas).

## Decisiones y por qué
- La sesión corre en el árbol `.claude/worktrees/simulacion-completa-e82eb3`, que ya está aislado de la carpeta de B. No se creó `../despachoX-sim`. La rama se publica como `simulacion`.
- Las entradas del canal y esta torre se suben a `main`; el código va solo en la rama.
- Se añadió una línea base `experta` (prioridad por urgencia y primero lo que vence) además de la `ingenua` del encargo. En los ensayos casi empata con DespachoX en puntos críticos; la ventaja de DespachoX aparece en las entregas a tiempo de todos los puntos.
- El tope de paradas de la línea base se calibró a su favor (sin tope) con semillas 100 a 111, distintas de las de evaluación (20261120 a 20261149).
- Tres niveles de carga (2, 2,5 y 3 pedidos por punto), elegidos mirando solo a la política ingenua: 86 %, 74 % y 52 % a tiempo en críticos.
- El adaptador llama a `optimizar._resolver` con filas armadas en memoria, sin base de datos. Como ese modelo planea un viaje por vehículo, `despachox` también recalcula cuando un vehículo vuelve al acopio.
- Un camión sin regreso por su red sale por cualquier vía al doble del tiempo. Sin esa regla, los sentidos únicos de la red de camión «atrapaban» vehículos y su carga contaba como desperdicio.

## Bloqueos y preguntas para el capitán
- Ninguno. El fallo de `SetAllowedVehiclesForIndex` ya lo corrigió B (commit 188c7e2).
- Para decidir: cómo se presenta en el pitch que la línea base `experta` iguala a DespachoX en los indicadores del reto.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Intérprete: `.venv` de la carpeta principal. El grafo debe estar en `despacho/cache/manizales.graphml`.
- `python -m pytest despacho/sim/tests -q`
- `python -m despacho.sim.correr --semillas 30 --carga todas` (opciones: `--red malla|osm`, `--optimizador provisional|b`, `--limite`, `--procesos`).

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 6: indicadores medidos con línea base, 30 semillas e IC del 95 % (`docs/SIMULACION.md`, sección 5).
- Criterio 3: diseño pareado con dos líneas base, supuestos escritos y límites declarados.
- Criterio 2: 19 pruebas del motor y del adaptador; el optimizador corrió 360 jornadas sin errores.
