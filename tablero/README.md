# tablero/ · la pantalla del despachador (Convite)

Un mapa de Manizales con pedidos, cierres y rutas, y a la derecha lo que espera una decisión. El tablero no calcula rutas: se las pide a `despacho/` y el despachador las aprueba.

## Arrancar

Desde la raíz del repositorio, con el `.venv` activo:

```bash
export DESPACHOX_DB=/ruta/absoluta/a/despachoX/datos/despachox.db   # la misma base del bot y de despacho
python -m despacho.red                          # una vez: baja la red vial
python -m despacho.semilla --cargar --reiniciar # una vez: carga la semilla (borra lo que haya)
streamlit run tablero/app.py
```

En PowerShell la primera línea es `$env:DESPACHOX_DB = "C:\ruta\a\despachoX\datos\despachox.db"`. Sin esa variable se usa `datos/despachox.db` de la copia donde se ejecuta. El tablero no usa claves de `.env`. Necesita internet para las teselas del mapa (CARTO sobre OpenStreetMap).

## Qué hace cada parte

| En pantalla | Qué muestra o hace |
|---|---|
| Cuatro indicadores | Pedidos pendientes (nuevos y confirmados, sin las alertas por silencio, que salen aparte como «N sin contacto»), kilos de perecederos que vencen en menos de 12 horas, cierres confirmados y porcentaje de pedidos del plan que llegan antes de su límite, con los puntos críticos aparte. Un pedido que el plan deja sin atender cuenta como no entregado a tiempo. |
| Mapa | Acopios, puntos (los críticos con aro rojo), pedidos por color según estado y tamaño según urgencia, cierres en rojo (punteados si falta confirmarlos), rutas por vehículo desde `paradas.geometria` con el orden de las paradas, y el regreso al acopio en línea punteada. |
| Plan | «Calcular plan» ejecuta `python -m despacho.optimizar`; «Recalcular», `python -m despacho.recalcular`; «Aprobar», `python -m despacho.optimizar --aprobar ID --quien NOMBRE` con el nombre escrito arriba a la derecha. «Rechazar» cambia el estado del plan. Lo que el plan no atiende y su motivo salen en rojo. |
| Aviso de cierre | Si hay un cierre confirmado que el plan vigente no tuvo en cuenta, aparece «Hay un cierre nuevo: recalcular». Tras recalcular se lee qué vehículos cambiaron de ruta y cuántos minutos se movió la llegada más afectada. |
| Por revisar | Cierres reportados, propuestas de ubicación (texto original, lugar propuesto, alternativas, «Corregir en el mapa») y pedidos nuevos con sus repetidos. Un pedido sin punto sale marcado «sin ubicar» y no se puede confirmar hasta ubicarlo. |
| Alertas por silencio | Pedidos con `origen='silencio'` (los crea `entrada/silencio.py`), en «Por revisar» con la etiqueta «Sin contacto: verificar». No traen familias ni kilos y el tablero no los inventa. «Mandar a verificar» pasa la alerta a `confirmado`: `despacho/optimizar.py` la lista en `resumen.verificar` como visita de verificación, sin comida. «Descartar» la pasa a `descartado`. Las dos acciones quedan en la bitácora con el nombre del despachador. |
| Plan en detalle | Tabla por vehículo: orden, punto, llegada, límite, kilos. |
| Territorio | Una fila por comuna, de `despacho.territorio.resumen`, con los peor atendidos arriba (menor % de críticos a tiempo). En color suave, los que están por debajo de `META_CRITICOS_PCT`. Debajo, «Barrios y veredas sin pedidos registrados» (`despacho.territorio.silencio`) y el botón «Descargar CSV» con la tabla. Si falta `despacho.territorio`, la pestaña dice «Pendiente: despacho.territorio». No muestra texto de los mensajes ni hash del remitente. |
| Bitácora | Las últimas decisiones: quién, cuándo y qué. |

La pantalla se actualiza sola cada cinco segundos y conserva el zoom y la posición del mapa.

Para corregir una ubicación: «Corregir en el mapa», clic en el mapa donde queda y «Guardar punto». Eso llama `lugares.corregir_con_pin(..., quien="despachador")`.

## Meta de críticos a tiempo

`META_CRITICOS_PCT = 100` en `datos.py`. Es el umbral que ya usaba la ficha de puntualidad para ponerse en alerta; no hay otra meta numérica en el código ni en `CLAUDE.md`. La usan la ficha «Pedidos del plan a tiempo» («meta 100 %») y el color de la pestaña Territorio. Si el equipo fija otra meta, se cambia solo ahí.

## Diseño

El tema está en `.streamlit/config.toml` (paleta del informe: tinta #4F4086, ámbar #A36752, crema #EBD3A2, ceniza #6E6878, y la sans-serif del sistema para no depender de internet). Colores de estado: pendiente en ámbar, en ruta en tinta, entregado en verde apagado y silencio en ceniza; los cierres y los puntos críticos siguen en rojo. El mapa usa el fondo claro de CARTO sobre OpenStreetMap.

## Cómo se comparan dos planes

Las llegadas se comparan en minutos desde la hora de cálculo de cada plan. Así el tiempo que pasa entre un cálculo y el siguiente no cuenta como retraso. Un vehículo «cambia de ruta» si atiende paradas distintas, si las atiende en otro orden o si el trazado cambia aunque el orden sea el mismo (desvío).

## Archivos

- `app.py`: solo interfaz.
- `datos.py`: todo lo que lee o cambia la base. El tablero solo cambia estados de pedidos, cierres y planes, y cada cambio queda en la bitácora.
- `tests/test_datos.py`, `tests/test_territorio.py` y `tests/test_silencio.py`: `python -m pytest tablero -q`. Usan una base temporal; no necesitan red vial ni optimizador.

## Límites conocidos

- El tablero no edita el contenido de un pedido (familias, productos). Un mensaje que el modelo no pudo leer aparece con su texto y solo se puede descartar o ubicar.
- Un pedido sin punto y sin propuesta de ubicación no se puede ubicar desde aquí: la propuesta la crea `entrada/` con `lugares.resolver`.
- Si se rechaza el plan que salió de un recálculo, no queda plan vigente, porque `despacho/` ya marcó el anterior como reemplazado. Hay que calcular de nuevo.
