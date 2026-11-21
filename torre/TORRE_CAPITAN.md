# Torre de control · Carlos · capitán
Última actualización: viernes 20 de noviembre de 2026, 23:00

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

### Nube (16:25; nota de las 22:50)
- Ronda 3 fusionada a `main` (2681c97) con 113 pruebas en verde; Railway la desplegó sin errores.
- Fallo encontrado y corregido: la variable `DESPACHOX_DB` de Railway valía `samcarjac`, una ruta relativa dentro del contenedor y no en el volumen `/data`. Cada despliegue arrancaba sin base y recargaba la semilla. Así se perdieron el pedido real de La Enea y el plan 2 de las 3:55 p. m.; no se pueden recuperar. Ahora vale `/data/despachox.db`. El despliegue de las 4:17 p. m. cargó la semilla una última vez y el bot dice «Base: /data/despachox.db». Por SSH: la base está en `/data` y la red vial lleva en `/data/cache` desde las 3:37 p. m., así que el volumen sí persiste entre despliegues. No reinicié para confirmarlo: la acción se negó en esta sesión. A las 16:55 el capitán reinició los datos por SSH para la segunda prueba, así que el estado de la nube ya no es la semilla de las 4:17 p. m.

### Encargo B3 · sin conexión (cerrado a las 16:50, rama `carlos-despacho`, sin fusionar a `main`)
1. **Hoja de ruta impresa.** `despacho/hoja.py`. `python -m despacho.hoja [--plan ID] [--salida carpeta]`; para el tablero, `hoja.generar(con, plan_id) -> list[Path]`. Un PDF carta por vehículo, en blanco y negro: encabezado (vehículo, acopio, salida y regreso estimados, carga, conductor en blanco), mapa con la red vial del disco, una fila por parada con QR, hora, productos y kilos sumados del surtido, crítico, firma y hora; al final los cierres con que se calculó el plan que bloquean a ese tipo de vehículo y las reglas del conductor. Paradas en el mismo punto comparten marcador («6-7»). Más de 5 paradas siguen en otra hoja. Sin red vial en disco, el mapa sale solo con la ruta. Deja «imprimir hojas de ruta» en la bitácora. Por defecto escribe en `hojas/plan_N/` junto a la base (en la nube, el volumen).
   - Decisiones: `fpdf2` (puro Python) en vez de `reportlab`; mapa y QR dibujados como vectores, así que no hacen falta matplotlib ni imágenes. El QR lleva el código tal como está en `paquetes` (`DX-7KQ3`, con guion). Solo imprime planes aprobados.
   - **Regla del conductor ante una vía cerrada, redactada por mí y sin validar con nadie:** no intentar pasar, seguir a la parada siguiente por otra vía, anotar dónde estaba el cierre, avisar por SMS si hay señal y, si no hay otra vía, volver al acopio con lo no entregado. Revisarla con un organismo de socorro.
   - Medido con la semilla: 17 paquetes en 3 hojas, los 17 QR se leen con zxing-cpp desde el PDF renderizado a 150 y 200 ppp. Generar las tres hojas: 2,6 s, casi todo en cargar la red vial.
2. **Arranque sin red.** `despliegue/local.sh`, con `DESPACHOX_SIN_RED=1` por defecto: sin bot, la red vial se copia de `despliegue/grafo/` y nunca se descarga (`red.descargar` falla de inmediato en vez de insistir 60 veces), y `lugares.elegir_con_modelo` no llama al modelo. El tablero escucha en 0.0.0.0 para abrirlo desde otro equipo por la wifi local.
3. **Prueba con la red bloqueada** (`sandbox-exec`, solo localhost; no es el wifi apagado): semilla, confirmar el pedido 18, ubicar tres frases sin modelo, calcular (12 s), aprobar, imprimir tres hojas y registrar `DX-HGFF` entregado: 23 s. `local.sh` levantó el tablero.
   - **Falló:** el mapa del tablero. Folium pide Leaflet, jQuery y Bootstrap a tres CDN además de las teselas; sin internet no se dibuja nada del mapa. Avisado a Jacobo.
   - **Pendiente:** la lectura de mensajes aún llama al modelo (sin red cae a texto crudo, que es seguro); el lector por reglas de Samuel no existe todavía. Pedido por el canal.
   - **Pendiente para Carlos:** la prueba con el wifi apagado de verdad, en el portátil de la demo.
4. Pruebas: `despacho/tests/test_hoja.py`, 9. Incluye que cada QR del PDF decodifica a su código de `paquetes` y que la generación falla si toca un socket. Dependencias nuevas: `fpdf2`; para las pruebas, `pypdfium2` y `zxing-cpp`. No hay Docker en este computador: no construí la imagen. Sí comprobé con `uv pip compile` que todo `requirements.txt` resuelve con ruedas binarias para Linux y Python 3.12, que es la base del `Dockerfile`.
   - El `.venv` compartido de la carpeta principal no tiene `fpdf2`: instalarlo me fue bloqueado. Trabajé con un `.venv` propio en el worktree. Para correr la hoja desde la carpeta principal: `.venv/bin/pip install -r requirements.txt`.

### Pendientes de la noche (23:00, rama `carlos-despacho`, sin fusionar)
- `FACTOR_CRITICO` vale 3 por defecto (aprobado a las 5:22 p. m.). La simulación sin `--factor-critico` ahora corre con 3.
- Un producto con la clave `supuesto` (kilos que pone el bot por ración) cuenta como cantidad supuesta: «kilos por ración (leche: 2 kg por familia)».
- Una alerta por silencio confirmada (`pedidos.origen='silencio'`) entra al plan como parada de verificación de 0 kg: no gasta inventario, no lleva paquete, no cuenta como entrega a un crítico y sale en `resumen.visitas` y en los avisos.
- T1, parte B: `despacho/territorio.py` con `resumen()` y `silencio()`, más línea de órdenes y CSV. Comuna de los barrios: la de `puntos` y, si no, `datos/semilla/barrios.csv`. Dos decisiones mías: las alertas por silencio no cuentan como pedidos, y los pedidos sin punto salen en una fila «sin ubicar». Con la semilla, un plan aprobado y cuatro entregas: diez comunas y 132 barrios y veredas sin pedidos registrados.
- Uní a esta rama el B3 que otra sesión había subido a `carlos-despacho` (hoja de ruta con QR). Trae `fpdf2`, `pypdfium2` y `zxing-cpp`; los instalé en `.venv`.
- Pruebas: 326 pasan y 1 se omite en todo el repositorio.
- Sin hacer: el empaque a 1,2 solo para fruta en frío, porque quedó como «decide Carlos», y a las 22:30 la capacidad UNAL pasó a ser el A25.

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
