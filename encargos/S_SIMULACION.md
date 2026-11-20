# Encargo S · Simulación (sesión aparte, Carlos)

Soy Carlos. Esta sesión se llama `simulacion` en el canal. Corre en paralelo con la sesión `B-despacho`, que escribe el optimizador en esta misma máquina.

## Para no pisar a la otra sesión

No trabajes en esta carpeta. Crea un árbol de trabajo aparte y usa solo rutas dentro de él:

```
git pull --rebase
git worktree add ../despachoX-sim -b simulacion
```

Todo lo que escribas va en `../despachoX-sim/despacho/sim/` y en `../despachoX-sim/docs/SIMULACION.md`. No edites `optimizar.py`, `matriz.py`, `red.py` ni `recalcular.py`: son de `B-despacho`. Si necesitas algo de ellos, pídelo por el canal.

Lee `CLAUDE.md`, `datos/esquema.sql`, la sección 3 de `docs/ESTADO_DEL_ARTE.md` y, en `docs/investigacion/01_estado_del_arte_tecnico.md`, la parte de evaluación y diseño de simulación.

## Objetivo

Medir cuánto mejora DespachoX frente a un despacho ingenuo en los dos indicadores del reto, de forma que un jurado de ingeniería industrial no lo pueda tumbar.

## Mientras el optimizador no exista

Revisa el canal. Si `B-despacho` todavía no ha escrito LISTO para `optimizar.py`, avanza con todo lo que no depende de él:

1. `sim/escenario.py`: generador con semilla. Sobre la red de `despacho/cache/` (o una malla sintética si aún no está): 30 a 80 puntos con cerca del 20 % críticos, pedidos que llegan a lo largo de una jornada, lotes perecederos con vencimiento entre 6 y 48 horas, flota mixta, y cierres viales que aparecen en momentos aleatorios y solo se conocen cuando un vehículo los reporta.
2. `sim/motor.py`: simulador de eventos discretos. Avanza el reloj, mueve vehículos por la red, registra entregas, vencimientos y cierres descubiertos.
3. `sim/politicas.py` con una interfaz común `planificar(estado) -> rutas`:
   - `ingenua`: orden de llegada, vehículo libre más cercano, desvío solo al toparse el cierre;
   - `optimiza_una_vez`: llama al optimizador al inicio y no recalcula;
   - `despachox`: optimiza y recalcula con cada cierre confirmado y cada tanda de pedidos.
   Para las dos últimas deja un adaptador que llame al optimizador de B cuando exista, y mientras tanto una heurística de inserción propia, marcada como provisional.
4. `sim/metricas.py`: porcentaje a tiempo en puntos críticos, porcentaje de kilos perecederos vencidos, llegada media y máxima, demanda no atendida, tiempo de llegada al punto peor atendido, kilómetros, y segundos de cada recálculo.
5. `sim/correr.py`: 30 semillas, las mismas para las tres políticas, diferencia pareada con intervalo de confianza del 95 %, salida en CSV y una tabla en Markdown.

## Cuando el optimizador exista

Trae los cambios de `main` a tu rama, conecta el adaptador, corre las 30 semillas y escribe `docs/SIMULACION.md`: diseño, supuestos, tabla de resultados tal como salieron, y una sección «Lo que esta simulación no prueba». Si DespachoX no gana en algún indicador, se reporta igual y me lo dices.

## Reglas

- La línea base tiene que ser razonable. Si la política ingenua pierde por un margen absurdo, sospecha de tu simulador antes de celebrarlo.
- Pruebas con pytest para el motor: un vehículo no entrega más de su capacidad, un lote vencido no cuenta como entregado, un cierre desconocido no altera la ruta hasta que se descubre.
- Escribe en el canal LISTO en cada etapa y abre un pull request de `simulacion` a `main` cuando haya resultados. No hagas merge tú.

**Aporta a:** criterio 6 (indicadores medidos), criterio 2 (evidencia del prototipo) y criterio 3 (método).
