# Encargo S3 · Que la mesa aguante muchos pedidos

Pedido por Carlos el sábado 21 de noviembre a las 11:39 a. m. Lo ejecuta una sesión de Claude Code. Fable revisa y fusiona.

## Por qué

Nadie necesita ayuda para repartir 20 pedidos. La ayuda hace falta cuando llegan miles. Hoy el bot recibe 15.000 mensajes a la vez sin perder ninguno (`entrada/ESCALA.md`), pero nadie ha probado qué pasa después: el tablero nunca se ha abierto con 15.000 pedidos y el optimizador solo está probado con planes del tamaño de la demo.

## Objetivo

Que 15.000 pedidos recibidos se conviertan en algo que una persona pueda ver y despachar: agrupados por punto de entrega, con un resumen legible por grupo, y con un plan de rutas sobre los grupos.

## Regla de arquitectura, que no se negocia

El modelo lee y estructura; el optimizador y las reglas calculan; el despachador decide.

- **Agrupar es una regla.** Los pedidos se agrupan por punto de entrega confirmado y ventana de tiempo, con código determinista. Ya existe: `triage/cluster.py` (ST-DBSCAN) y `triage/embudo.consolidar`. El modelo no decide qué pedidos van juntos.
- **El modelo resume.** Para cada grupo, el modelo puede escribir dos o tres líneas para el despachador a partir de los textos de los pedidos: qué piden, qué casos especiales hay (bebés, adultos mayores, frío) y qué no se entiende. Es lectura. No cambia familias, kilos, urgencia ni prioridad, y el resumen se marca como «leído por el modelo».
- **Los kilos y las familias de un grupo son sumas**, hechas por código, con tope por zona (los `T_z` de `triage/censo.py`), para que 200 mensajes del mismo barrio no se vuelvan 200 mercados.
- **El despachador confirma cada grupo** antes de que entre al plan, igual que hoy confirma cada pedido.

Si algo de lo que construyes necesita romper esta regla, para y escríbelo en el canal.

## Lo que debes leer primero

1. `CLAUDE.md`, `docs/ESTRATEGIA.md`, `torre/CANAL.md` (el final).
2. `triage/README.md` y `triage/ESPEC_TRIAGE.md`. El triage ya filtra, agrupa y consolida, pero no está conectado al tablero ni al optimizador.
3. `entrada/ESCALA.md` y `entrada/carga.py`.
4. `despacho/optimizar.py` (`planificar`, `_leer`, `_resolver`) y `tablero/datos.py`.

## Qué hacer, en este orden

**Parte 1 · Medir (30 minutos, sin cambiar el producto).** Entrégala aunque no alcances el resto.

- Genera 15.000 pedidos sintéticos en una base temporal, repartidos entre los barrios y veredas de `datos/semilla/barrios.csv`. Nada de datos reales.
- Mide cuánto tardan las consultas de `tablero/datos.py` con esa base y, con `streamlit.testing.v1.AppTest`, cuánto tarda en pintar cada pestaña.
- Mide `planificar` con 50, 100, 250, 500 y 1.000 pedidos, con el límite de tiempo que usa hoy. Reporta segundos, pedidos atendidos y críticos a tiempo. Si no termina, dilo.
- Escribe el resultado en `docs/ESCALA_DESPACHO.md`, tal como salió, con la máquina, las condiciones y lo que no se midió.

**Parte 2 · Agrupar y planear sobre grupos.**

- Un módulo nuevo, `despacho/agrupar.py`, que tome los pedidos confirmados y devuelva grupos por punto de entrega: familias y kilos sumados con tope, urgencia máxima, límite más cercano y la lista de pedidos que lo forman. Usa lo que ya hay en `triage/`; no lo reescribas.
- `planificar` recibe los grupos como si fueran pedidos, detrás de la variable `DESPACHOX_AGRUPAR=1`. Apagada, todo se comporta como hoy.
- Repite la medición de la parte 1 con 15.000 pedidos agrupados y añádela al documento. Di cuántos grupos salieron.
- Si los grupos no caben en la flota del día, el plan lo dice como faltante, igual que hoy. No inventes vehículos.

**Parte 3 · El resumen del modelo y la vista (solo si sobran 30 minutos).**

- `despacho/resumen_grupo.py`: una función que arma el texto de entrada para el modelo y otra que guarda el resumen. Con extractor falso en las pruebas. No llames a la API de Anthropic desde esta sesión.
- En el tablero, una vista de grupos en «Por revisar», con el resumen, los números sumados y «Ver los pedidos del grupo». También detrás de `DESPACHOX_AGRUPAR`.

## Qué entregar y dónde

- Rama `escala`, desde `main`. Empuja al menos cada 30 minutos, aunque esté a medias.
- `docs/ESCALA_DESPACHO.md` con las mediciones.
- Pruebas nuevas junto al código. La suite completa debe seguir pasando: `python -m pytest -q -p no:cacheprovider`.
- Una entrada LISTO en `torre/CANAL.md` con los archivos, cómo probarlo y las cifras medidas.

## Qué no debes tocar

- `main`. No fusionas ni empujas allí. Fable revisa la rama y decide.
- El bot de Railway, Telegram real y la API de Anthropic. Todo en local, con extractor falso.
- El flujo de la demo: con `DESPACHOX_AGRUPAR` apagada, la demo por terminal debe seguir dando lo mismo.
- Las torres de otros, el historial (`reset --hard`, `--force`) y los documentos del jurado.

## Horario

- 12:15 · parte 1 empujada.
- 12:50 · lo que haya de las partes 2 y 3 empujado, con LISTO en el canal.
- 1:30 a 3:30 p. m. no se empuja nada a `main`. Lo que no esté revisado a la 1:15 se queda en la rama y se cuenta en el pitch como siguiente paso.

## Criterios del jurado

Le suma al criterio 2 (prototipo que funciona con carga real) y al 5 (viabilidad). La evidencia es una tabla medida en `docs/ESCALA_DESPACHO.md`.

## Cifras

Toda cifra que escribas es medida por ti en esta sesión, con su condición. Si algo salió mal o lento, se reporta igual.
