# Torre de control · Carlos · sesión `simulacion` (rol B, medición)
Última actualización: viernes 20 de noviembre de 2026, 11:40 a. m.

## Estado en una frase
La simulación corre de punta a punta sobre la red real y ya habla con el modelo de `optimizar.py`; falta que B publique el optimizador corregido para la corrida oficial de 30 semillas.

## Hecho (con el commit o archivo que lo prueba)
- Rama `simulacion` (commit 76447e9): `despacho/sim/` con `escenario.py`, `motor.py`, `politicas.py`, `metricas.py`, `correr.py`, `red_sim.py`, `adaptador_b.py` y pruebas en `despacho/sim/tests/`.
- La simulación usa el mismo grafo, las mismas velocidades y las mismas reglas de acceso que `despacho/red.py` y `despacho/matriz.py`. `tests/test_supuestos.py` compara las dos matrices de tiempos.
- `docs/SIMULACION.md` en borrador: diseño, políticas, métricas y supuestos. Faltan resultados y la sección «Lo que esta simulación no prueba».

## En curso (qué, hasta dónde llegó, qué falta)
- Ensayo de 30 semillas, carga media, con una copia local de `optimizar.py` parchada. Sirve para medir tiempos; no se cita.
- Espera: B debe corregir `SetAllowedVehiclesForIndex` (ver BLOQUEO de las 11:30 en el canal) y publicar LISTO.
- Descarga de la red de Caldas, Risaralda y Quindío (`despacho/cache/eje_cafetero.graphml`): Overpass no ha respondido.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
1. Cuando `despacho/optimizar.py` esté en `main`: en la rama, borrar las copias locales sin seguimiento (`despacho/__init__.py`, `cierres.py`, `matriz.py`, `optimizar.py`, `red.py`), `git merge origin/main`, `python -m pytest despacho/sim/tests -q`.
2. `python -m despacho.sim.correr --semillas 30 --carga todas --optimizador b --limite 1 --procesos 9` (unos 100 s por corrida de `despachox`).
3. Copiar `despacho/sim/resultados/resumen.md` a la sección 5 de `docs/SIMULACION.md`, redactar la sección 7, abrir el pull request de `simulacion` a `main` y escribir LISTO en el canal.

## Decisiones y por qué
- La sesión corre en el árbol `.claude/worktrees/simulacion-completa-e82eb3`, que ya está aislado de la carpeta de B. No se creó `../despachoX-sim`. La rama se publica como `simulacion`.
- Las entradas del canal y esta torre se suben a `main`; el código va solo en la rama.
- Se añadió una línea base `experta` (prioridad por urgencia y primero lo que vence) además de la `ingenua` del encargo. En los ensayos casi empata con DespachoX en puntos críticos; la ventaja de DespachoX aparece en las entregas a tiempo de todos los puntos.
- El tope de paradas de la línea base se calibró a su favor (sin tope) con semillas 100 a 111, distintas de las de evaluación (20261120 a 20261149).
- Tres niveles de carga (2, 2,5 y 3 pedidos por punto), elegidos mirando solo a la política ingenua: 86 %, 74 % y 52 % a tiempo en críticos.
- El adaptador llama a `optimizar._resolver` con filas armadas en memoria, sin base de datos. Como ese modelo planea un viaje por vehículo, `despachox` también recalcula cuando un vehículo vuelve al acopio.
- Un camión sin regreso por su red sale por cualquier vía al doble del tiempo. Sin esa regla, los sentidos únicos de la red de camión «atrapaban» vehículos y su carga contaba como desperdicio.

## Bloqueos y preguntas para el capitán
- BLOQUEO para B (canal, 11:30): `SetAllowedVehiclesForIndex` falla con OR-Tools 9.15. Alternativa: `routing.VehicleVar(i).SetValues([-1] + permitidos)`.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Intérprete: `.venv` de la carpeta principal. El grafo debe estar en `despacho/cache/manizales.graphml`.
- `python -m pytest despacho/sim/tests -q`
- `python -m despacho.sim.correr --semillas 30 --carga todas` (opciones: `--red malla|osm`, `--optimizador provisional|b`, `--limite`, `--procesos`).

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 6: pendiente de la corrida oficial. Criterio 3: diseño pareado con dos líneas base y supuestos escritos en `docs/SIMULACION.md`. Criterio 2: 19 pruebas del motor y del adaptador.
