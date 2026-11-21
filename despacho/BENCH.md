# Medición de tiempos del optimizador

**Aporta a:** criterio 2 (prototipo y demostración) y, con el número medido, criterio 6 (indicadores verificables).
**Estado: la medición de esta noche NO es la definitiva.** Se corrió con la máquina ocupada por la simulación larga (carga del sistema cerca de 3 con 2 núcleos, y el proceso a `nice -n 19`). Falta correr el comando completo con la máquina libre.

## Qué se mide

`despacho/bench.py`, con la red vial ya cargada y una base nueva en cada repetición:

- **Primera optimización:** `optimizar.planificar` con todos los pedidos confirmados (matrices por tipo de vehículo, solver y escritura del plan).
- **Reoptimización tras cerrar un tramo:** se aprueba ese plan, se confirma el cierre de la avenida del Centro y se mide `recalcular.recalcular`. Es el número del pitch: «cuánto tarda el sistema en recalcular cuando se cierra una vía».

Tres tamaños, con pedidos sintéticos de semilla fija. Los puntos de entrega son los 15 de la semilla, así que varios pedidos comparten punto. La flota crece con los pedidos.

| tamaño | pedidos | vehículos |
|---|---|---|
| demo | 18 (la semilla con el pedido 21 confirmado, como en el guion) | 5 |
| medio | 60 | 12 |
| grande | 150 | 25 |

Por cada medición se reportan: mediana y p90 de cinco repeticiones, mínimo y máximo, el «extra» (tiempo total menos el límite del solver), pedidos atendidos, uso de CPU de toda la máquina y carga del sistema. El encabezado del informe trae nproc, CPU, memoria, versión de OR-Tools y carga al empezar y al terminar.

## Cómo leer los números

El solver de OR-Tools (búsqueda local guiada) corre hasta su límite de tiempo, que aquí es `--segundos 3`, el mismo de la demo. Por eso cada tiempo total vale cerca de 3 s más un extra de matrices y escritura. Esto implica dos cosas:

1. Con el límite fijo, el tiempo de recalcular no crece con el tamaño en estas pruebas. Lo que cambia con el tamaño es la **calidad** del plan que alcanza en esos 3 s, que esta medición no evalúa.
2. Con solo 15 puntos distintos las matrices son pequeñas. Un tamaño real con cientos de puntos distintos cambiaría el extra, y esto no lo mide.

Los tiempos se reportan tal como salieron. No se promedian con otras corridas.

## Medición de esta noche (corta, no definitiva)

Viernes 20 de noviembre, hacia las 23:35 (hora de Colombia). nproc=2, Intel Xeon @ 2,10 GHz, 8 GB (unos 6,9 GB disponibles), OR-Tools 9.15.6755, Python 3.13. Carga del sistema entre 2,9 y 3,2 durante las mediciones, con la simulación larga corriendo y el uso de CPU de la máquina en 100 %. **Una sola repetición por tamaño**, así que no hay mediana ni p90 reales: es solo la prueba de que el script funciona.

| tamaño | pedidos | vehículos | paso | tiempo (s) | atendidos |
|---|---|---|---|---|---|
| demo | 18 | 5 | primera optimización | 3,35 | 18/18 |
| demo | 18 | 5 | reoptimización tras cierre | 3,41 | 18/18 |
| medio | 60 | 12 | primera optimización | 3,36 | 60/60 |
| medio | 60 | 12 | reoptimización tras cierre | 3,26 | 60/60 |
| grande | 150 | 25 | primera optimización | 3,32 | 150/150 |
| grande | 150 | 25 | reoptimización tras cierre | 3,40 | 150/150 |

Lo único que se puede decir con esto: con el límite de 3 s, el recálculo de la demo tardó 3,4 s en una máquina cargada. El ensayo completo de la demo por terminal (`python -m demo.correr`) dio 3,4 s para el recálculo con el guion real.

## Comando para la medición definitiva (con la máquina libre)

Antes: que la simulación haya terminado, `uptime` con carga cercana a 0 y `free -m` con más de 1.500 MB disponibles. Desde la raíz del repositorio, con el entorno del proyecto:

```
.venv/bin/python -m despacho.bench --repeticiones 5 --segundos 3 --salida despacho/bench_resultado.md
```

Es el comando por defecto: tamaños demo, medio y grande, cinco repeticiones. Dura unos dos minutos. Sin `nice` y sin otros procesos pesados. Para ver el efecto del límite del solver, repetir con `--segundos 1` y `--segundos 8` (8 es el valor por defecto del optimizador). Luego pegar la tabla del archivo en la sección anterior y borrar la advertencia de esta noche.

Prueba rápida (un tamaño, una repetición): `.venv/bin/python -m despacho.bench --rapido`.

## Qué se puede decir en el pitch

Solo lo medido con la máquina libre. Mientras tanto: «el plan sale en unos 3 a 4 segundos con el límite de búsqueda de la demo, medido en una máquina cargada». No decir que escala a más pedidos ni a más puntos: esta medición no lo prueba.
