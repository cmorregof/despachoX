# Torre de control · Carlos · capitán
Última actualización: viernes 20 de noviembre de 2026, 16:55

## Estado en una frase
El módulo B corre de punta a punta: semilla cargada, plan en 10 s y recálculo que evita la vía cerrada. Faltan las pruebas (agente en curso) y, esta noche, la simulación.

## Hecho
- Lectura completa del sitio de la hackathon: bases, rúbrica, fichas de las ocho verticales, patentes, banco de capacidades, equipos. Resumen en `docs/ESTRATEGIA.md`.
- Propuesta de producto para la vertical 04 y horario de las dos jornadas.
- Prompt del equipo en `CLAUDE.md` y `docs/PROMPT_EQUIPO.md`.
- Revisión del estado del arte con cinco agentes: síntesis en `docs/ESTADO_DEL_ARTE.md`, informes en `docs/investigacion/`.
- 16:55 · Datos de Railway reiniciados para la segunda prueba de Jacobo, por SSH y sin redesplegar (`railway ssh` y `python -m despacho.semilla --cargar --reiniciar`). Antes había 20 pedidos asignados, 3 planes y 20 paquetes; quedan 20 pedidos (17 confirmados y 3 nuevos), sin planes, paquetes ni cierres. Respaldo de lo anterior en `/data/respaldo_antes_prueba2.db`.

## Rol B · despacho (viernes)
Hecho:
- `despacho/red.py`: grafo de conducción de Manizales y Villamaría (6.395 nodos, 15.634 aristas) en `despacho/cache/manizales.graphml`, con copia en pickle que abre en 0,05 s.
- `despacho/semilla.py` y `datos/semilla/`: 138 barrios con comuna (OpenStreetMap), 15 puntos (3 críticos), 2 acopios, 5 vehículos, 34 lotes, 20 pedidos (17 confirmados, 3 nuevos). Todo sintético, semilla 2026.
- `despacho/vias.py` y `vias.csv`: 11 tramos verificados contra el grafo. **No están La Siria ni la vía a Neira**: el grafo no llega hasta allá. «salida a Letras» es la ruta 50 al oriente de Maltería, con confianza media.
- `despacho/matriz.py`, `optimizar.py`, `cierres.py`, `recalcular.py`. Medido en este computador con la semilla: 17 de 17 pedidos atendidos, 3 de 3 críticos a tiempo, 10,2 s en total (8 s de búsqueda). Con un cierre sobre la avenida más usada del plan, el recálculo tardó 9,9 s y el plan nuevo no pasa por ahí.

Decisiones del modelo (quedan en el `resumen` de cada plan como supuestos):
- El inventario lo asignan reglas antes del solver: primero el pedido más urgente, primero el lote que vence primero, y cada pedido sale de un solo acopio. El solver solo rutea.
- Ventana dura: vencimiento del perecedero menos 30 minutos. `limite_en` es blando, con retraso ponderado por urgencia (1, 3, 10 por segundo). El encargo decía «ventana dura hasta el vencimiento o limite_en»; lo dejé así para que la penalización por retraso tenga sentido. Por revisar con el ingeniero industrial.
- Un viaje por vehículo y por plan. El vehículo `en_ruta` arranca desde su posición y conserva solo lo que ya lleva.
- El camión no entra a vías residenciales; llega si hay una vía apta a menos de 300 m. Velocidades y factores por tipo son supuestos, no mediciones.
- Límite de búsqueda de 8 s por defecto (tope 10) para que el comando completo quede por debajo de 15 s.
- `python -m despacho.optimizar` planea solo pedidos `confirmado` y no toca un plan aprobado. `recalcular` vuelve a planear también los `asignado`. Desde la ronda 3, el aprobado solo pasa a `reemplazado` cuando se aprueba el nuevo.
- El regreso al acopio no es una fila de `paradas`: su geometría va en `resumen.vehiculos[].regreso`.
- Añadí `scipy` a `requirements.txt` (Dijkstra rápido).

Lo que no sirvió: Overpass tiene dos IP y una rechaza conexiones; osmnx se queda con esa. `red._evitar_ip_caida()` le entrega la que sí conecta. El Python 3.15 del sistema no tiene osmnx; usar `.venv` (3.12, creado con `uv venv --python 3.12 .venv`).

Cómo correr:
```
.venv/bin/python -m despacho.red                          # una vez, baja el grafo
.venv/bin/python -m despacho.semilla --cargar --reiniciar # crea y llena datos/despachox.db
.venv/bin/python -m despacho.optimizar                    # imprime el id del plan
.venv/bin/python -m despacho.optimizar --aprobar 3        # lo hace un humano
.venv/bin/python -m despacho.recalcular                   # tras confirmar un cierre
```

### Encargo B2 (cerrado a las 14:33)
- Pruebas de B: `despacho/tests`, 13 pasan (8 del optimizador y 5 de la carga). Un punto cortado por un cierre ahora queda aislado en vez de saltar a otra vía cercana (`matriz.calcular`).
- Red ampliada: `despacho/cache/manizales_region.graphml`, 7.825 nodos y 18.821 aristas (antes 6.395 y 15.634). Casco urbano completo más vías principales de los accesos (área `red.AREA`). Matriz de 15 lugares por tres tipos: 0,22 s. `python -m despacho.optimizar`: 10,8 s. `DESPACHOX_GRAFO` fija otro archivo; el urbano original sigue en el caché y es el de la primera simulación.
- `vias.csv`: 15 tramos, todos con arista verificada. La Siria y la vía a Neira no tienen nombre en OSM; se fijaron por geografía y la validación está en `despacho/vias.py`.
- Nomenclátor: `datos/semilla/lugares_extra.csv`, 100 lugares (33 vías, 58 sitios, 9 veredas) hechos por un agente Sonnet con el grafo y Nominatim; el origen de cada coordenada está en `lugares_extra_fuentes.csv` y se regenera con `python -m lugares.construir_extra`. Revisado: todos dentro del área, a 241 m o menos de la red, las vías con arista existente y sin apodos repetidos. Quité tres apodos ambiguos («la policia», «venecia», «tablazo»). No se ubicaron: la Galería, kilómetro 41, peajes, túneles, viaductos, estaciones del cable, Estación Uribe.
- Resolvedor medido con 44 frases, sin modelo: 30 aciertos seguros, 5 por opciones, 9 «no sé» (los 9 eran lugares inexistentes) y 0 errores seguros. Umbrales sin cambio (0,90 y 0,08). Las frases las escribimos nosotros: no es una muestra de usuarios.
- Datos reales: `python -m despacho.semilla --cargar --reiniciar --origen datos_privados/`; formato en `datos/README.md`.

Salida de `python -m lugares.nomenclator "la siria" "la pana" "por la terminal"` (452 apodos):
```
«la siria» -> exacto, seguro=True    Ubiqué «la siria» en: La Siria (via). ¿Es correcto?
«la pana» -> exacto, seguro=True     Ubiqué «la pana» en: Panamericana (via). ¿Es correcto?
«por la terminal» -> exacto, seguro=True   Ubiqué «por la terminal» en: Terminal de Transportes (sitio). ¿Es correcto?
```

### Ronda 3 (cerrada a las 16:10, rama `carlos-despacho`, sin fusionar a `main`)
1. **Empaque activo.** `surtir` usa `vence_efectivo`: si un lote perecedero tiene `empaque_activo=1`, el tiempo que le queda hasta `vence_en` se multiplica por `FACTOR_EMPAQUE_ACTIVO` (1,5 por defecto; `DESPACHOX_FACTOR_EMPAQUE`). El orden «primero lo que vence primero» y la ventana dura usan ese vencimiento. Va en `resumen.supuestos.factor_empaque_activo` con la nota «supuesto, pendiente de datos del ICTA; patente UNAL 37476». La semilla tiene 2 lotes con empaque de 20 perecederos.
2. **Trazabilidad.** `despacho/paquetes.py`. `optimizar.aprobar` crea un paquete `en_ruta` por parada (código `DX-XXXX`, sin letras que se confundan al dictarlas), con el lote que más kilos aporta. Un pedido tiene un solo paquete vivo: si un recálculo lo mueve, conserva su código. Si el plan aprobado nuevo deja fuera un pedido del anterior (y no va en un vehículo `en_ruta`), el pedido vuelve a `confirmado` y su paquete a `en_bodega`. `entregar(con, codigo, quien)` y `python -m despacho.paquetes --entregar CODIGO`; sin argumentos lista los paquetes del plan aprobado. `paquetes.listar(con)` es lo que puede leer el tablero.
3. **Cantidad supuesta.** `_demanda(p, notas)` dice qué completó la red de seguridad. Cada parada lleva `cantidad_supuesta` (texto o `None`) en el resultado del solver; en la base queda en `resumen.cantidad_supuesta` (`{pedido_id: motivo}`) y como aviso legible en `resumen.avisos`, que el tablero ya muestra. No toqué el esquema de `paradas`. Los 20 pedidos de la semilla traen kilos: ninguno sale marcado.
4. **Plan vigente.** `planificar` ya no marca `reemplazado` el aprobado; solo las propuestas anteriores. `resumen.reemplaza_a` sigue nombrando el aprobado, así que la comparación «qué cambió» del tablero no cambia. `aprobar` es el único que pasa el aprobado a `reemplazado`.

Pruebas: `despacho/tests` 25 pasan (12 nuevas en `test_ronda3.py`); simulación 24 pasan con el grafo urbano; `tablero`, `lugares` y `entrada` 64 pasan y 1 se omite. Punta a punta en una base temporal con la semilla y el grafo regional: plan 1 con 17 de 17 y 3 de 3 críticos a tiempo; aprobado, 17 paquetes; un pedido sintético sin cantidad en un albergue entra al recálculo marcado «sin kilos ni familias: se supuso 1 familia, 10 kg»; rechazar ese recálculo deja el plan 1 aprobado; aprobar el siguiente lo reemplaza y crea 18 paquetes (los 17 conservan código); entregar por línea de órdenes funciona y la segunda vez se rechaza.

## En curso
- Nada de B. Pendiente de otra sesión: encargo S2 de la simulación (barrido de `FACTOR_CRITICO`), que no se ejecutó, y el indicador A25 como riesgo de tramo.

## Siguiente paso exacto
- **Ahora:** cada uno corre su encargo de `encargos/` en Claude Code con Fable 5.2. Carlos corre además `encargos/0_MAESTRO.md`. Lo primero de B es la semilla, que desbloquea a los otros dos.
0. **Tarea 0 (antes de las 2:30 p. m.):** cada integrante verifica un informe de `docs/investigacion/`. Instrucciones y reparto en `docs/TAREA_0.md`. Cierre de diez minutos a las 2:15 p. m.
1. Confirmar con Samuel que la vertical inscrita es la 04.
2. Preguntar en la mesa: duración del pitch, forma de entrega, jurados, acceso real al software de ruteo UNAL y a los datos de la ficha.
3. Asignar roles A, B, C y D con nombre.
4. A las 2:30 p. m.: esqueleto de punta a punta (pedido por chat → ruta en el mapa).

## Decisiones y por qué
- La organización permite programar antes de las 2:00 p. m. (lo confirmó Carlos). Se empieza ya.
- Hoy trabajan tres: se recortan voz y QR, y la simulación se corre después de la mentoría.
- Los módulos se comunican solo por SQLite (`datos/esquema.sql`).
- Usuario principal: ABACO y el Banco de Alimentos. Es quien ya opera desde Manizales y ya dijo en prensa que su reto es el transporte.
- No repetir «desabastecimiento en 48 horas» como hecho: no tiene fuente para este sismo.
- Capacidad UNAL principal: indicador A25 del IDEA como riesgo de tramo. Segunda: patente del empaque captador de etileno, como supuesto de vida útil.
- Pila: python-telegram-bot, Claude Haiku, SQLite, osmnx, OR-Tools, Streamlit. Simulación con tres políticas y 30 semillas.
- Vertical 04: es la que Samuel inscribió (por confirmar) y su entregable coincide con el nombre del equipo.
- Telegram para la demo: se despliega en una hora. WhatsApp queda para el piloto.
- OR-Tools sobre OpenStreetMap como motor mientras no haya acceso confirmado al software de ruteo UNAL.
- La decisión de despacho es humana siempre.

## Bloqueos y preguntas
- ¿Existen de verdad el software de ruteo UNAL, ERIS-UNAL y los datos de la ficha 04? Varias entradas del sitio parecen de plantilla.
- Duración del pitch y mecanismo de entrega.
- Ruta piloto: la noticia de la Sede dice 20 a 30 días y el sitio, 30 a 90.

## Observaciones de mentores
(vacío hasta la mentoría 1, viernes 7:00 p. m.)

## Roles (viernes, tres personas; detalle en `docs/ROLES_VIERNES.md`)
| Rol | Quién |
|---|---|
| A · Entrada y D · Ficha | Samuel |
| B · Despacho y capitán | Carlos |
| C · Tablero | Jacobo |
| Por sumarse | Nicolás y José Manuel |

## Aporte a la rúbrica
| Criterio | Evidencia hoy | Falta |
|---|---|---|
| 1 Problema (20) | Ficha 04 | Cifras con fuente, cita de un usuario real |
| 2 Prototipo (25) | Optimizador y recálculo corren con la semilla | Unir con bot y tablero |
| 3 Conocimiento (15) | Candidatas listadas | Confirmar una capacidad UNAL y usarla |
| 4 Plan (15) | Borrador 30/60/90 | Responsables, recursos |
| 5 Viabilidad y aliados (15) | Lista de padrinos | Contacto real, costos, riesgos |
| 6 Impactos (10) | Indicadores de la ficha | Línea base y meta medidas |
