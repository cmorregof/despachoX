# Figuras del pitch

Esta carpeta trae cinco figuras listas para proyectar, en PNG de 1920 × 1080 px (`png/`) y en SVG (`svg/`). Usan la paleta del informe: tinta `#4F4086`, ámbar `#A36752`, crema `#EBD3A2` y ceniza `#6E6878`. Ningún texto mide menos de 24 px en el PNG, y cada una lleva su fuente al pie.

Cada figura tiene su script en `scripts/`. Los datos propios quedan en `datos/`, y el resto se lee del repositorio sin cambiarlo.

## Regenerar todo con un comando

Desde la raíz del repositorio, con un Python que tenga matplotlib, osmnx, geopandas y scipy:

```bash
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py
```

Tarda unos 10 segundos y no usa la red. El Python del proyecto no trae matplotlib, así que conviene un entorno aparte, fuera del repositorio:

```bash
python3 -m venv ~/.venvs/figuras && ~/.venvs/figuras/bin/pip install matplotlib osmnx geopandas scipy
DESPACHOX_SIN_RED=1 ~/.venvs/figuras/bin/python figuras_pitch/scripts/todas.py
```

El mapa necesita el grafo vial en `despacho/cache/manizales_region.graphml`, que git ignora. Si no está, el script usa `despliegue/grafo/manizales_region.graphml`, que sí está en el repositorio.

Cada script avisa con una línea `AVISO` si un texto queda por debajo de 24 px, se sale del lienzo o se encima con otro.

## Las figuras, en el orden del pitch

El orden es el de la decisión 4 de `docs/DECISIONES_9PM.md`.

| Parte del pitch | Figura | Mensaje |
|---|---|---|
| 1. Por qué | (b) `b_cuello_despacho` | La donación llegó y el despacho se atascó. |
| 2. Para qué | (d) `d_cierres_sin_sismo` | Las vías se cierran también sin sismo, sobre todo la salida a Letras. |
| 4. Por qué no basta lo que existe | (c) `c_regla_arquitectura` | DespachoX une el pedido, el plan, la decisión y la entrega, y el modelo nunca decide. |
| 5. Qué medimos y cómo | (e) `e_simulacion_ejemplo` | Plantilla para los resultados nuevos de la simulación. El render de hoy no se cita. |
| 6. El piloto de 30 a 90 días | (a) `a_territorios_piloto` | Hay tres territorios posibles, y el recomendado pone tres CDI y la vereda en un mismo corredor. |

La parte 3 (para quién) no tiene figura.

### (b) El cuello de botella del despacho

- **Mensaje.** Al sexto día había 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados.
- **Datos.** `datos/cuello_despacho.csv`, con las tres cifras, la nota y el enlace.
- **Fuente.** Portafolio, «Flypass paga peajes de 57 camiones para acelerar la entrega de ayudas tras el terremoto en Colombia», 16 de agosto de 2026. La nota atribuye las cifras a «los Bancos de Alimentos», y «sexto día» sale de la fecha de publicación.
- **Estado.** Por verificar. El script lee el estado de la fila «404.587» en `docs/FUENTES.md` y, si no la halla, en la rama `origin/fuentes-noche` (con `git show`, sin tocarla). Hoy dice «Revisada por máquina, 20 nov». El sello «Cifras por verificar» desaparece solo cuando esa fila diga «Verificada por <nombre>, <hora>».
- **Regenerar.** `python figuras_pitch/scripts/cuello_despacho.py`

### (d) Cierres viales sin sismo

- **Mensaje.** Entre 2017 y 2026 hay 152 registros de derrumbe o deslizamiento sin contar los del sismo. La salida a Letras tiene 83 y aparece todos los años.
- **Datos.** `datos_publicos/cierres_historicos.csv`. El conteo queda en `datos/d_cierres_sin_sismo.csv`, por corredor y año.
- **Fuente.** El registro #767 de INVÍAS y notas de prensa, reunidos en ese CSV con la fuente de cada fila (consulta del 20 de noviembre de 2026). El conteo es nuestro.
- **Regla del conteo.** Entra la fila cuya causa es remoción en masa (deslizamiento, derrumbe, deslave, desprendimiento o caída de lodo o de rocas). Sale toda fila cuya causa menciona el sismo, y también las dos que dicen «no es derrumbe» (A019 y A078). Se cuentan registros y no eventos, porque un derrumbe puede tener varios registros y el #767 no registra todo.
- **Salvedad.** Un agente marcó la columna `verificado` del CSV, y ninguna persona ha revisado las filas.
- **Regenerar.** `python figuras_pitch/scripts/cierres_sin_sismo.py`

### (c) La regla de arquitectura

- **Mensaje.** Los canales llegan al modelo, que lee y estructura. El optimizador y las reglas calculan, y el despachador decide. Después salen el despacho, el QR de cada paquete y la entrega confirmada.
- **Datos.** No usa datos.
- **Fuente.** La regla de `docs/ESTRATEGIA.md`. Según `docs/FICHA.md`, los SMS los lee un programa de reglas sin modelo, y ese lector toma el lugar del modelo si este falla. Por eso el primer bloque dice «o un lector por reglas».
- **Regenerar.** `python figuras_pitch/scripts/regla_arquitectura.py`

### (e) Plantilla de resultados de la simulación

- **Mensaje.** Lo dirán los resultados nuevos. La figura dibuja, por grupo y política, la media de pedidos críticos entregados a tiempo y de kilos perecederos vencidos, con el intervalo del 95 % entre escenarios y la meta del reto (menos del 5 % de perecederos).
- **Datos de hoy.** `despacho/sim/resultados/resultados.csv`, la corrida del 20 de noviembre que está en revisión. Por eso el render se llama `e_simulacion_ejemplo` y lleva la marca «Ejemplo con resultados anteriores, no citar». El resumen numérico queda en `datos/e_simulacion_ejemplo_resumen.csv`, con la diferencia pareada por semilla contra la línea base.
- **Pie automático.** Dice el archivo, el número de filas, los escenarios por grupo y política, las semillas, la línea base y que los supuestos están en `docs/SIMULACION.md`.
- **Con los resultados nuevos.**

  ```bash
  DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/sim_resultados.py \
      --entrada despacho/sim/<carpeta nueva>/resultados.csv --salida figuras_pitch \
      --titulo "<lo que muestran los resultados>"
  ```

  También sirve para `analisis/sensibilidad/resultados/`. Si la entrada es una carpeta, lee todos los `resultados*.csv` de debajo y cada archivo queda como una variante con el nombre de su carpeta. Por ejemplo:

  ```bash
  DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/sim_resultados.py \
      --entrada analisis/sensibilidad/resultados --salida figuras_pitch --nombre e_sensibilidad \
      --agrupar variante --filtro carga=alta
  ```

  `--filtro` evita mezclar cargas dentro de una variante. `--grupos` y `--politicas` eligen qué se dibuja y en qué orden, y `--marca` pone una advertencia visible. Columnas mínimas: `politica`, `a_tiempo_criticos_pct` y `perecedero_vencido_pct`.
- **Regenerar el ejemplo.** `python figuras_pitch/scripts/todas.py`, o el script con `--marca "Ejemplo con resultados anteriores, no citar"`.

### (a) Tres territorios para el piloto

- **Mensaje.** Cada propuesta une una comuna y un corregimiento. La recomendada, La Macarena con El Tablazo, pone tres CDI a unos 3 km del Banco y Bajo Tablazo a 9,3 km sobre un mismo corredor.
- **Datos.** Las propuestas y sus razones son de `docs/PILOTO_TERRITORIOS.md`. Los puntos críticos y los acopios salen de `datos_publicos/puntos.csv` y `datos_publicos/acopios.csv`. La coordenada de Bajo Tablazo es de `datos/semilla/lugares_extra.csv`, geocodificada con Nominatim. Los límites de comunas y corregimientos están en `datos/limites_osm.geojson`, y la red vial es el grafo del equipo.
- **Rutas.** Son el camino más corto por longitud en el grafo dirigido, desde el nodo del Banco hasta el nodo más cercano a cada lugar. Dan 9,28 km a Bajo Tablazo, 8,76 km a Alto Bonito y 7,39 km a La Aurora, iguales a los del documento. El grafo no llega a Bajo Tablazo, cuyo nodo más cercano queda a 701 m, y ese tramo va punteado. Las distancias quedan en `datos/a_territorios_rutas.csv`.
- **Kilómetro 41.** No tiene coordenada con fuente en el repositorio (`lugares/README.md`), así que va como flecha desde La Aurora hacia el occidente. En el grafo, todos los nodos a unos 36 km del Banco por esa rama quedan al occidente de La Aurora. Los 36,4 km son los del documento, porque no pudimos recalcularlos.
- **Nombres.** OpenStreetMap llama «Corredor Agroturístico» al corregimiento El Tablazo, y Nominatim ubica Bajo Tablazo dentro de él. El corregimiento Colombia no está en los límites de OpenStreetMap que tenemos.
- **Fuente al pie.** `docs/PILOTO_TERRITORIOS.md`, con sus razones por verificar. El mapa base es © colaboradores de OpenStreetMap (ODbL), sin teselas de internet.
- **Regenerar.** `python figuras_pitch/scripts/mapa_territorios.py`. Para rehacer el GeoJSON de límites hace falta un Python con pyarrow, como el del proyecto: `python figuras_pitch/scripts/extraer_limites.py`.

## Fuente tipográfica

La del informe es Ancízar Serif, que no está en el repositorio. Las figuras usan PT Serif, de licencia OFL, que viene con macOS. Si no está, usan DejaVu Serif, que trae matplotlib. Con `--fuente` se elige otra familia instalada o un archivo de fuente del disco:

```bash
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py --fuente "Ancizar Serif"
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py --fuente /ruta/a/AncizarSerif-Regular.ttf
```

Ningún archivo de fuente se copia al repositorio. Los SVG guardan el texto como trazos, así que se ven igual en un computador sin la fuente. Si una familia es más ancha, los textos de las cajas se achican hasta caber, nunca por debajo de 24 px.

## Origen de los scripts

`mapa_territorios.py` y `cuello_despacho.py` se adaptaron de `docs/informe/figuras/scripts/mapa_manizales.py` y `barras_abaco.py`, que quedaron sin cambios. `estilo.py` reúne la paleta, la fuente, el tamaño de proyección y la revisión de textos.
