# Encargo B · Despacho (Carlos)

Soy Carlos, capitán. Mi rol hoy es B (despacho). Mi torre es `torre/TORRE_CAPITAN.md`.

Lee `CLAUDE.md`, `docs/ROLES_VIERNES.md`, `datos/esquema.sql`, `datos/db.py` y la sección 3 de `docs/ESTADO_DEL_ARTE.md`. La receta detallada de OR-Tools está en `docs/investigacion/01_estado_del_arte_tecnico.md`.

## Objetivo

Leer de la base los pedidos confirmados, el inventario, la flota y los cierres confirmados, y escribir un plan de rutas que el despachador pueda aprobar. Recalcular cuando se confirma un cierre.

## Reglas de este módulo

- Trabajo solo dentro de `despacho/` y `datos/semilla/`. Escribo en `planes` y `paradas`, lleno `cierres.osm_u` y `cierres.osm_v`, y pongo `pedidos.estado='asignado'` cuando un plan se aprueba. No toco el bot ni el tablero.
- El plan siempre nace `propuesto`. Solo el humano lo aprueba.
- Unidades enteras dentro del solver: segundos y gramos.
- Límite de búsqueda de 10 segundos. Si no hay solución, devuelvo un plan vacío con el motivo, nunca una excepción.

## Pasos

1. **Primero la semilla, porque desbloquea a Samuel y a Jacobo.** `despacho/red.py`: baja con osmnx el grafo de conducción de Manizales, lo guarda en `despacho/cache/manizales.graphml` (ignorado por git) y añade tiempos de viaje. `despacho/semilla.py` genera en `datos/semilla/`, todo sintético y con semilla fija:
   - `barrios.csv` (nombre, comuna, lat, lon) desde los lugares de OpenStreetMap;
   - `vias.csv` (nombre, lat, lon, osm_u, osm_v) con una decena de tramos con nombre que la gente usaría: La Siria, Panamericana, avenida Santander, avenida Kevin Ángel, vía a Chinchiná, vía a Neira, salida a Letras. Verifica cada uno contra el grafo y dime cuáles no encontraste;
   - `puntos.csv` (15, tres críticos), `acopios.csv` (2), `vehiculos.csv` (5: dos camiones, dos camperos, una moto), `lotes.csv` (con vencimientos entre 6 y 48 horas para los perecederos), `pedidos.csv` (20);
   - `python -m despacho.semilla --cargar` crea la base y la llena. Commit y push apenas exista, y aviso por el grupo.
2. `despacho/matriz.py`: matriz de tiempos entre acopios y puntos, una por tipo de vehículo. Camión: sin vías residenciales estrechas ni tramos cerrados para camión. Quita las aristas de los cierres con estado `confirmado` según `tipos_bloqueados`. Par inalcanzable: costo prohibitivo y aviso.
3. `despacho/optimizar.py` con OR-Tools: capacidad por vehículo, ventana dura hasta el vencimiento o `limite_en`, penalización por retraso ponderada por urgencia, disyunción con penalización alta para pedidos que no caben, `PATH_CHEAPEST_ARC` más `GUIDED_LOCAL_SEARCH`. Escribe `planes` (con `segundos_calculo` y un `resumen` JSON) y `paradas` con la geometría de cada tramo. Los vehículos `en_ruta` arrancan desde su posición actual.
4. `despacho/recalcular.py`: ubica en el grafo cada cierre confirmado (arista más cercana si no viene de `vias.csv`), marca el plan vigente como `reemplazado` y resuelve de nuevo con motivo `cierre N`.
5. Línea de órdenes para el tablero: `python -m despacho.optimizar` y `python -m despacho.recalcular`, que imprimen el id del plan.
6. Pruebas con pytest: el plan respeta capacidades; un cierre en una arista usada cambia la ruta; un punto aislado no rompe nada.

## Hecho cuando

Con la semilla cargada, `python -m despacho.optimizar` escribe un plan en menos de 15 segundos, y después de confirmar un cierre sobre una vía usada, `python -m despacho.recalcular` escribe otro plan que no pasa por ahí.

## Para esta noche, no ahora

`despacho/simular.py`: tres políticas (orden de llegada con vehículo más cercano; optimizador sin recalcular; DespachoX completo), 30 semillas compartidas, y las métricas de la sección 3 de `docs/ESTADO_DEL_ARTE.md`. Y el indicador A25 del IDEA como penalización de riesgo por tramo.

## En paralelo

Mientras escribes el optimizador, lanza un agente Sonnet para las pruebas y otro para `vias.csv`. Revisa lo que devuelvan.

**Aporta a:** criterio 2 (el recálculo en vivo es el centro de la demo), criterio 3 (método) y criterio 6 (indicadores medidos).
