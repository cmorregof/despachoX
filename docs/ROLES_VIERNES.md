# Roles del viernes (tres personas)

Hoy trabajan Samuel, Jacobo y Carlos. Nicolás y José Manuel se suman después; al final está lo que les espera.

| Quién | Rol | Carpeta | Entrega para la mentoría de las 7:00 p. m. |
|---|---|---|---|
| **Samuel** | A · Entrada, y D · Ficha | `entrada/`, `docs/FICHA.md` | Bot de Telegram que recibe un pedido o un cierre vial en texto libre, lo convierte en una fila de `pedidos` o `cierres` y le responde al remitente lo que entendió; componentes 1 a 3 de la ficha escritos |
| **Carlos** | B · Despacho, y capitán | `despacho/` | Red vial de Manizales en disco, optimizador que lee la base y escribe un plan, y recálculo cuando un cierre pasa a `confirmado` |
| **Jacobo** | C · Tablero | `tablero/` | Mapa con acopios, pedidos, cierres y rutas; botones de confirmar y aprobar |

Samuel lleva además la ficha porque como líder presenta. Los encargos listos para Claude Code están en `encargos/`.

## El contrato

Los tres módulos solo se comunican por la base SQLite definida en `datos/esquema.sql`. Nadie llama funciones de la carpeta de otro. Así cada uno avanza con datos falsos sin esperar a los demás.

## Primera hora de cada uno

**Samuel (A y D)**
1. Crear el bot con BotFather y dejar el token en `.env`.
2. Bot mínimo con `python-telegram-bot` en modo polling que responde «recibido».
3. Función `extraer(texto)` con Claude Haiku que devuelve JSON validado: tipo (`pedido` o `cierre`), lugar, familias, productos, urgencia.
4. Ubicar el lugar contra `datos/semilla/barrios.csv` y `vias.csv` (los genera Carlos), sin geocodificador.
5. Escribir la fila en la base y contestar: «Entendí: 40 familias en San José, arroz y leche. ¿Correcto?»
6. En paralelo, con un agente: pasar a `docs/FICHA.md` los componentes 1 a 3 usando `docs/ESTADO_DEL_ARTE.md` y el informe 04.

**Carlos (B)**
1. `despacho/red.py`: bajar el grafo de Manizales con osmnx y guardarlo en `despacho/cache/`.
2. `datos/semilla/`: 2 acopios, 5 vehículos de tipos distintos, 15 puntos, 20 pedidos, lotes con vencimientos.
3. `despacho/optimizar.py`: lee la base, arma la matriz de tiempos, resuelve con OR-Tools con límite de 10 segundos y escribe `planes` y `paradas`.
4. `despacho/recalcular.py`: quita la arista de cada cierre confirmado y vuelve a resolver.

**Jacobo (C)**
1. `tablero/app.py` con Streamlit y streamlit-folium: mapa centrado en Manizales con los puntos y acopios de la semilla.
2. Tabla de pedidos y de cierres con botón de confirmar. Botón «Calcular plan» que llama al script de despacho, y botón «Aprobar».
3. Dibujar las rutas desde `paradas.geometria`.

## Qué se recorta hoy por ser tres

- Notas de voz: mañana, si sobra tiempo.
- Códigos QR: mañana.
- Simulación de 30 semillas: esta noche después de la mentoría, la corre Carlos.
- Tarea 0: cada uno verifica solo las cifras fuertes de un informe (veinte minutos). Carlos el 03, Samuel el 04, Jacobo el 05 (sin cambios). El 01 y el 02 quedan para Nicolás y José Manuel.

## Meta de las 4:00 p. m.

Un mensaje escrito en Telegram termina como una ruta dibujada en el mapa. Fea, pero de punta a punta.

## Cuando lleguen Nicolás y José Manuel

- El ingeniero industrial: revisar la formulación del optimizador con Carlos, diseñar la línea base de la simulación y escribir los componentes 4 y 5 de la ficha (plan y viabilidad).
- El otro: QR y trazabilidad, pruebas con mensajes mal escritos, y el video de respaldo.
- Los dos: verificar los informes 01 y 02 de la Tarea 0.
