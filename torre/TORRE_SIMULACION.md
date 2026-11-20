# Torre de control · Carlos · sesión `simulacion` (rol B, medición)
Última actualización: viernes 20 de noviembre de 2026, 11:15 a. m.

## Estado en una frase
Etapa 1 lista en la rama `simulacion` (commit 05e019c): corre de punta a punta en malla sintética con heurística provisional. Faltan la red real y el optimizador de B.

## Hecho (con el commit o archivo que lo prueba)
- Encargo `encargos/S_SIMULACION.md` leído. Pregunta a B-despacho en el canal sobre la firma de `optimizar.py`.
- `despacho/sim/` completo y 14 pruebas en verde (commit 05e019c, rama `simulacion`).

## En curso (qué, hasta dónde llegó, qué falta)
- Descarga de la red de Manizales con osmnx: Overpass no responde; se reintenta. También se pidió Caldas, Risaralda y Quindío en `despacho/cache/eje_cafetero.graphml`.
- Adaptador `despacho/sim/adaptador_b.py`: espera la firma de `optimizar.py`.
- Calibración de la carga del sistema sobre la red real, con semillas 100 a 107 (distintas de las de evaluación, 20261120 en adelante).

## Siguiente paso exacto (el comando o el archivo por donde seguir)
- Rama `simulacion` en el remoto. Seguir por `despacho/sim/correr.py`.

## Decisiones y por qué
- La sesión corre en el árbol `.claude/worktrees/simulacion-completa-e82eb3`, que ya está aislado de la carpeta de B. No se creó `../despachoX-sim`. La rama se publica como `simulacion`.
- Las entradas del canal y esta torre se suben a `main`; el código va solo en la rama.
- Se añadió una línea base `experta` (prioridad por urgencia y primero lo que vence) además de la `ingenua` del encargo, para que la comparación no sea contra un hombre de paja.
- El tope de paradas de la línea base se calibró a su favor (sin tope).
- Tres niveles de carga (pedidos por punto 2, 3 y 4). Con la demanda original todas las políticas entregaban el 100 % y la comparación no medía nada.

## Bloqueos y preguntas para el capitán
- Ninguno.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- Intérprete: `.venv` de la carpeta principal.
- `python -m pytest despacho/sim/tests -q`
- `python -m despacho.sim.correr --semillas 30 --carga todas` (opciones: `--red malla|osm`, `--optimizador provisional|b`).

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 6, 2 y 3: pendiente de resultados.
