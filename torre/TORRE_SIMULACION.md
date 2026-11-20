# Torre de control · Carlos · sesión `simulacion` (rol B, medición)
Última actualización: viernes 20 de noviembre de 2026, 5:00 p. m.

## Estado en una frase
Encargo S2 casi completo y en `main`: el factor crítico no alcanza a la línea base `experta`, la confirmación de ubicación sí la supera cuando hay pedidos mal ubicados. Faltan la búsqueda de 3 s y la red ampliada.

## Hecho (con el commit o archivo que lo prueba)
- Primera ronda: pull request 1, fusionado. 360 jornadas, `despacho/sim/resultados/`.
- S2, en `main` (commit 4cece34) y en `despacho/sim/resultados_s2/`:
  - regla de elección del factor escrita antes de correr (`docs/SIMULACION.md`, 8.1, commit 3ffdf69);
  - barrido de `FACTOR_CRITICO` 1, 3, 10 y 30: ninguno cumple la regla (`barrido_factor.md`);
  - factor 3 en semillas nuevas 20261150 a 20261179: no supera a `experta` de forma significativa;
  - error de ubicación de pedidos con p 0, 0,1 y 0,2: confirmar sube las entregas a tiempo de todos los puntos 6,0 y 10,7 puntos;
  - 0, 5 y 10 cierres: casi no cambia nada;
  - dos camperos menos: DespachoX supera a `experta` en el total por 3,4 puntos y la ingenua pasa la meta de perecederos (5,7 %);
  - carga media con 8 s de búsqueda: igual que con 1 s (`despacho/sim/resultados_8s/`).
- Red del Eje Cafetero (Caldas, Risaralda, Quindío) en `despacho/cache/eje_cafetero.graphml` de este árbol. No está en git (62 MB, carpeta ignorada).

## En curso (qué, hasta dónde llegó, qué falta)
- Carga media con 3 s de búsqueda y carga media sobre `manizales_region.graphml`. Terminan hacia las 5:45 p. m.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
- Pasar esas dos corridas a `docs/SIMULACION.md` (secciones 8.6 y 8.7) y actualizar la sección 7.
- Las corridas del S2 necesitan `DESPACHOX_GRAFO=despacho/cache/manizales.graphml`, porque `red.py` ahora lee `manizales_region.graphml` por defecto.

## Decisiones y por qué
- La sesión corre en el árbol `.claude/worktrees/simulacion-completa-e82eb3`, que ya está aislado de la carpeta de B. No se creó `../despachoX-sim`. La rama se publica como `simulacion`.
- Las entradas del canal y esta torre se suben a `main`; el código va solo en la rama.
- Se añadió una línea base `experta` (prioridad por urgencia y primero lo que vence) además de la `ingenua` del encargo. En los ensayos casi empata con DespachoX en puntos críticos; la ventaja de DespachoX aparece en las entregas a tiempo de todos los puntos.
- El tope de paradas de la línea base se calibró a su favor (sin tope) con semillas 100 a 111, distintas de las de evaluación (20261120 a 20261149).
- Tres niveles de carga (2, 2,5 y 3 pedidos por punto), elegidos mirando solo a la política ingenua: 86 %, 74 % y 52 % a tiempo en críticos.
- El adaptador llama a `optimizar._resolver` con filas armadas en memoria, sin base de datos. Como ese modelo planea un viaje por vehículo, `despachox` también recalcula cuando un vehículo vuelve al acopio.
- Un camión sin regreso por su red sale por cualquier vía al doble del tiempo. Sin esa regla, los sentidos únicos de la red de camión «atrapaban» vehículos y su carga contaba como desperdicio.

## Bloqueos y preguntas para el capitán
- Para B o Carlos: cambiar `FACTOR_CRITICO` de 1 a 3 en `optimizar.py` (canal).
- Carlos autorizó a las 4:55 p. m. el empuje directo de esta sesión a `main`, pese a la regla de las 4:05 p. m. de no subir directo.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Intérprete: `.venv` de la carpeta principal. El grafo debe estar en `despacho/cache/manizales.graphml`.
- `python -m pytest despacho/sim/tests -q`
- `python -m despacho.sim.correr --semillas 30 --carga todas` (opciones: `--red malla|osm`, `--optimizador provisional|b`, `--limite`, `--procesos`, `--factor-critico`, `--p-error`, `--cierres`, `--camperos-menos`, `--politicas`, `--base`).
- `python -m despacho.sim.barrido despacho/sim/resultados_s2` rehace la tabla del barrido.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 6: indicadores medidos con línea base, 30 semillas e IC del 95 % (`docs/SIMULACION.md`, sección 5).
- Criterio 3: diseño pareado con dos líneas base, supuestos escritos y límites declarados.
- Criterio 2: 19 pruebas del motor y del adaptador; el optimizador corrió 360 jornadas sin errores.
