# Figuras del pitch

Esta carpeta trae seis figuras listas para proyectar, en PNG de 1920 × 1080 px (`png/`) y en SVG (`svg/`). Son las cinco del encargo y una variante del mapa con solo la propuesta recomendada. Usan la paleta del informe: tinta `#4F4086`, ámbar `#A36752`, crema `#EBD3A2` y ceniza `#6E6878`. Ningún texto mide menos de 24 px en el PNG, y cada figura lleva su fuente al pie.

Cada figura tiene su script en `scripts/`. Los datos propios quedan en `datos/`, y el resto se lee del repositorio sin cambiarlo.

## Regenerar todo con un comando

Con un Python que tenga matplotlib, osmnx, geopandas y scipy:

```bash
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py
```

Tarda unos 15 segundos y no usa la red. Dos corridas seguidas dan archivos idénticos, así que después de regenerar `git status` solo muestra cambios si cambió algo de verdad. El Python del proyecto no trae matplotlib, de modo que conviene un entorno aparte, fuera del repositorio:

```bash
python3 -m venv ~/.venvs/figuras && ~/.venvs/figuras/bin/pip install matplotlib osmnx geopandas scipy
DESPACHOX_SIN_RED=1 ~/.venvs/figuras/bin/python figuras_pitch/scripts/todas.py
```

El mapa necesita el grafo vial en `despacho/cache/manizales_region.graphml`, que git ignora. Si no está, el script usa `despliegue/grafo/manizales_region.graphml`, que sí está en el repositorio.

## Las líneas AVISO

Cada script revisa sus textos antes de guardar. Si uno queda por debajo de 24 px, se sale del lienzo o se encima con otro, imprime una línea `AVISO` que dice cuál. Los archivos se escriben igual, para poder mirarlos, pero el script termina con código 1. `todas.py` cierra con un resumen por figura («bien», «N AVISO» o «falló») y también sale con código 1 si alguna figura no quedó bien. Así nadie regenera en otro computador y proyecta una figura con textos encimados sin enterarse.

Para que una letra más ancha no produzca avisos, el pie se dibuja primero y los ejes y la leyenda se acomodan encima de él. Las seis figuras salen sin ningún AVISO con Ancízar Serif, con PT Serif y con DejaVu Serif.

La revisión solo compara textos entre sí. No ve un texto que tape una barra, un punto del mapa o un recuadro, así que conviene mirar cada PNG antes de proyectarlo.

## Dónde va cada figura

El encargo pedía el orden de la decisión 4 de `docs/DECISIONES_9PM.md`: (b) en el porqué, (d) en el para qué, (c) en por qué no basta lo que existe, (e) en qué medimos y (a) en el piloto. El plan de diapositivas de Fable (`pitch/DIAPOSITIVAS.md`, versión 1, rama `pitch-noche`) es más reciente y cambia el uso de varias. Esta tabla cruza los dos, y la decisión final es de Fable.

| Diapositiva del plan | Figura de esta carpeta | Cómo encaja |
|---|---|---|
| 1 · Por qué | `b_cuello_despacho` | Puede reemplazar a `barras_abaco.pdf`. Trae las mismas tres cifras (fila P01 de `pitch/CIFRAS_PITCH.md`), con letra más grande y el sello «Cifras por verificar». |
| 2 · Las vías se cierran sin sismo | `d_cierres_sin_sismo` | El plan usa `mapa_manizales.pdf` con dos etiquetas y descarta una gráfica por año. (d) ya no compara años, así que sirve de respaldo o de reemplazo del mapa. Su total de 152 registros sin sismo no tiene fila en `CIFRAS_PITCH.md`; los 83 de la salida a Letras salen de la fila C05. |
| 4 · Lo que existe | `c_regla_arquitectura` | El plan usa `piezas_sueltas.tex`. (c) queda de respaldo, para una pregunta por la arquitectura o para la versión de cinco minutos. |
| 6 · Qué medimos | `sim_resultados.py --panel criticos` | El plan pide un solo panel de críticos a tiempo, para la carga que se cite, con la etiqueta «Simulación: [SIM] jornadas». El comando está en la sección (e). `e_simulacion_ejemplo` no se cita. |
| 7 · El piloto | `a_territorio_propuesta1` | Es la «opción con más tiempo» del plan: el Banco, los tres CDI de La Macarena a entre 2,9 y 3,3 km y Bajo Tablazo a 9,3 km (fila P10). `a_territorios_piloto`, con las tres propuestas, queda de respaldo. |

## Las figuras

### (b) El cuello de botella del despacho

- **Mensaje.** Seis días después del sismo, los bancos de alimentos tenían 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados.
- **Datos.** `datos/cuello_despacho.csv`, con las tres cifras, la nota y el enlace.
- **Fuente.** Portafolio, «Flypass paga peajes de 57 camiones para acelerar la entrega de ayudas tras el terremoto en Colombia», 16 de agosto de 2026. La nota atribuye las cifras a «los Bancos de Alimentos» y no dice hacia dónde iban los kilos en tránsito. Tampoco dice «seis días», que sale de la fecha de publicación.
- **Estado.** Por verificar. El script busca la fila de «404.587» en `docs/FUENTES.md` y, si no la halla, en la rama `origin/fuentes-noche`, con `git show` y sin tocarla (`--ref-fuentes` elige otra referencia). La celda solo decide el sello. Si empieza por «Verificada por <nombre>», la figura no lleva sello y el pie dice que una persona cotejó las cifras. Con cualquier otro estado lleva el sello «Cifras por verificar» y un pie fijo. Por eso la figura no cambia cuando alguien reescribe la celda sin cambiar el estado: con la celda de `eeb515f` y con la de `2261013` el PNG y el SVG salen idénticos. El estado leído sale en la consola y nunca en la figura.
- **Regenerar.** `python figuras_pitch/scripts/cuello_despacho.py`

### (d) Cierres viales sin sismo

- **Mensaje.** Las vías de Manizales y sus accesos se cierran también sin sismo. Entre 2017 y 2026 hay 152 registros de derrumbe o deslizamiento sin contar los del sismo. La salida a Letras tiene 83 y algún registro en cada uno de los 10 años.
- **Por qué no hay gráfica por año.** Según `docs/datos/vias_y_riesgo.md`, sección 3, el #767 no registra todos los eventos y su cobertura cambia de un año a otro, así que estos conteos son mínimos y no sirven para comparar años. Por eso la figura solo dice en cuántos años hay algún registro en la salida a Letras, y el pie copia esa salvedad. El conteo por corredor y año queda en `datos/d_cierres_sin_sismo.csv` para consulta, sin dibujarlo.
- **Datos.** `datos_publicos/cierres_historicos.csv`.
- **Fuente.** El registro #767 de INVÍAS y notas de prensa, reunidos en ese CSV con la fuente de cada fila (consulta del 20 de noviembre de 2026). El conteo es nuestro.
- **Regla del conteo.** Entra la fila cuya causa es remoción en masa (deslizamiento, derrumbe, deslave, desprendimiento o caída de lodo o de rocas). Sale toda fila cuya causa menciona el sismo, y también las dos que dicen «no es derrumbe» (A019 y A078).
- **Detalles que cambian el conteo.**
  - Queda fuera A007 (vía a Chinchiná), porque no tiene `fecha_inicio`, aunque su tramo dice «noviembre de 2017». Está marcada «no verificado», y `vias_y_riesgo.md` tampoco la cuenta.
  - Cada fila es un registro, y un mismo derrumbe puede tener varios. Por ejemplo, A154 es la demolición preventiva de rocas que siguió al deslave de A153, en la Panamericana. Las dos cuentan, como en `vias_y_riesgo.md`, y el pie lo dice.
  - Las filas sin corredor en `via_nombre` van como «otras vías de la región»: el corredor norte hacia Neira, Aranzazu y Salamina, tramos entre Estación Uribe, Tres Puertas y Puente La Libertad, y una variante de Pereira.
  - El conteo pasa de Manizales. La salida a Letras incluye tramos del Tolima (Padua, Herveo, Petaqueros, Cerro Bravo), y hay filas de Santa Rosa de Cabal (S22), de La Felisa y La Pintada y de Marmato. Por eso el título dice «Manizales y sus accesos».
- **Verificación.** De las 152 filas contadas, la columna `verificado` marca 142 como «sí», 9 como «parcial» y 1 como «no verificado» (A003). Esa columna la llenó un agente, y todavía ninguna persona ha revisado las filas.
- **Diferencia con `docs/datos/vias_y_riesgo.md`.** Esa tabla da 35 registros en la vía a Medellín y esta figura da 33, porque allá entran A019 y A078. En la salida a Letras coinciden, con 87 registros si se cuentan los 4 del sismo y 83 sin ellos.
- **Regenerar.** `python figuras_pitch/scripts/cierres_sin_sismo.py`

### (c) La regla de arquitectura

- **Mensaje.** Los canales llegan al modelo, que lee y estructura. El optimizador y las reglas calculan, y el despachador decide. Después salen el despacho, el QR de cada paquete y la entrega confirmada.
- **Datos.** No usa datos.
- **Fuente.** La regla de `docs/ESTRATEGIA.md`. Según `docs/FICHA.md`, los SMS los lee un programa de reglas sin modelo, y ese lector toma el lugar del modelo si este falla. Por eso el primer bloque dice «o un lector por reglas».
- **Regenerar.** `python figuras_pitch/scripts/regla_arquitectura.py`

### (e) Plantilla de resultados de la simulación

- **Mensaje.** Lo dirán los resultados nuevos. La figura dibuja, por grupo y política, la media de pedidos críticos entregados a tiempo y de kilos perecederos vencidos, con el intervalo del 95 % entre escenarios y la meta del reto (menos del 5 % de perecederos).
- **Datos de hoy.** `despacho/sim/resultados/resultados.csv`, la corrida d33dd27 del 20 de noviembre a las 11:52, que no se cita. Por eso el render se llama `e_simulacion_ejemplo` y lleva la marca «Ejemplo con resultados anteriores, no citar». El resumen numérico queda en `datos/e_simulacion_ejemplo_resumen.csv`, con la diferencia pareada por semilla contra la línea base.
- **Cifras.** Llevan un decimal, como `resumen.md`. Una media que no es 100 nunca se escribe 100, y una que no es 0 nunca se escribe 0. Si el redondeo la lleva ahí, se agregan decimales. Por ejemplo, la media de DespachoX con carga holgada es 99,71 % y la figura dice 99,7. La línea del intervalo se corta en 0 y en 100 %. El CSV de resumen guarda el intervalo calculado, que puede pasar de 100 (100,16 en ese caso).
- **La marca «no citar».** La decide el contenido del CSV, así que da igual cómo se escriba la ruta. `sim_resultados.py` guarda en `CORRIDAS_ANTERIORES` la huella SHA-256 de cada corrida que no se cita, y hoy la lista tiene solo la d33dd27. Si algún archivo de la entrada coincide, la figura lleva la marca con la ruta relativa, con `./` o completa, y también si se pide `--marca ""`. Una corrida nueva tiene otra huella y sale sin marca, aunque sobrescriba `despacho/sim/resultados/`. Aun así, conviene que cada corrida nueva vaya a su propia carpeta, como `despacho/sim/resultados_velocidades/` en la rama `simulacion`. Las corridas de `resultados_8s` y `resultados_s2` no están en la lista. Si tampoco se deben citar, se agrega su huella o se usa `--marca`.
- **Pie automático.** Dice el archivo, el número de filas, los escenarios por grupo y política, las semillas, la línea base y que los supuestos están en `docs/SIMULACION.md`.
- **Con los resultados nuevos, las seis figuras de una vez.** `todas.py` mira el contenido del CSV. Si no es una corrida de la lista, la figura se llama `e_simulacion` y no lleva marca. `--marca-sim` pone una advertencia visible y `--titulo-sim` el título.

  ```bash
  DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py \
      --sim despacho/sim/<carpeta nueva>/resultados.csv --titulo-sim "<lo que muestran los resultados>"
  ```

- **Para la diapositiva 6, un solo panel.** `--panel criticos` dibuja solo los críticos a tiempo, `--filtro` deja la carga que se cite y `--etiqueta` pone la línea de la simulación bajo el título. En la etiqueta, `{jornadas}` se cambia por el número de filas dibujadas y `{semillas}` por el de semillas distintas.

  ```bash
  DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/sim_resultados.py \
      --entrada despacho/sim/<carpeta nueva>/resultados.csv --salida figuras_pitch --nombre e_criticos_alta \
      --panel criticos --filtro carga=alta --politicas ingenua,experta,despachox \
      --titulo "<lo que muestran los resultados>" \
      --etiqueta "Simulación: {jornadas} jornadas sintéticas sobre la red vial de Manizales"
  ```

  La corrida con las velocidades de la tesis de 2019 ya está en la rama `simulacion`, en `despacho/sim/resultados_velocidades/confirmacion_factor_3/resultados.csv` (generada el 21 de noviembre a las 12:33 a. m., commit `1489760`). La plantilla la dibuja sin marca y sin ningún AVISO, probada con una copia fuera del repositorio. Cuando esa carpeta llegue a `main`, basta con pasar su ruta en los comandos de arriba.
- **Sensibilidad.** Si la entrada es una carpeta, la plantilla lee todos los `resultados*.csv` de debajo y cada archivo queda como una variante con el nombre de su carpeta. `--filtro` evita mezclar cargas dentro de una variante.

  ```bash
  DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/sim_resultados.py \
      --entrada analisis/sensibilidad/resultados --salida figuras_pitch --nombre e_sensibilidad \
      --agrupar variante --filtro carga=alta
  ```

  Con muchas variantes, los rótulos del eje se parten en líneas y, si ni así caben, van verticales. Los números de las barras van verticales o, si no caben, se omiten con un aviso en la consola, porque están en el CSV de resumen. Con `despacho/sim/resultados_s2` (14 variantes) la figura sale sin ningún AVISO.
- **Opciones.** `--grupos` y `--politicas` eligen qué se dibuja y en qué orden; si ningún valor pedido está en los datos, el script lo dice y muestra los que hay. Columnas mínimas: `politica`, `a_tiempo_criticos_pct` y `perecedero_vencido_pct`.
- **Regenerar el ejemplo.** `python figuras_pitch/scripts/todas.py`, o `sim_resultados.py --entrada despacho/sim/resultados/resultados.csv --nombre e_simulacion_ejemplo`.

### (a) Tres territorios para el piloto

- **Mensaje.** Cada propuesta une una comuna y un corregimiento. La recomendada, La Macarena con El Tablazo, pone tres CDI a unos 3 km del Banco y Bajo Tablazo a 9,3 km sobre un mismo corredor. Decide el Banco.
- **Datos.** Las propuestas y sus razones son de `docs/PILOTO_TERRITORIOS.md`. Los puntos críticos y los acopios salen de `datos_publicos/puntos.csv` y `datos_publicos/acopios.csv`. La coordenada de Bajo Tablazo es de `datos/semilla/lugares_extra.csv`, geocodificada con Nominatim. Los límites de comunas y corregimientos están en `datos/limites_osm.geojson`, y la red vial es el grafo del equipo.
- **Lectura.** Los territorios van con relleno suave y borde punteado y delgado, y las rutas van gruesas y continuas, para que no se confundan. La convención separa el punto crítico de una propuesta, del color de su número, de los otros puntos críticos, en gris.
- **Rutas.** Son el camino más corto por longitud en el grafo dirigido, desde el nodo del Banco hasta el nodo más cercano a cada lugar. Dan 9,28 km a Bajo Tablazo, 8,76 km a Alto Bonito y 7,39 km a La Aurora, iguales a los del documento. El grafo no llega a Bajo Tablazo, cuyo nodo más cercano queda a 701 m, y ese tramo va punteado. Las distancias quedan en `datos/a_territorios_rutas.csv`.
- **Kilómetro 41.** No tiene coordenada con fuente en el repositorio (`lugares/README.md`), así que va como flecha desde La Aurora hacia el occidente. En el grafo, todos los nodos a unos 36 km del Banco por esa rama quedan al occidente de La Aurora. Los 36,4 km son los del documento, porque no pudimos recalcularlos.
- **Nombres.** OpenStreetMap llama «Corredor Agroturístico» al corregimiento El Tablazo, y Nominatim ubica Bajo Tablazo dentro de él. El corregimiento Colombia no está en los límites de OpenStreetMap que tenemos. La propuesta 3 dice «alertas de lluvia A25 del IDEA (UNAL)» para que el jurado no necesite la sigla.
- **Fuente al pie.** `docs/PILOTO_TERRITORIOS.md`, con sus razones por verificar. El mapa base es © colaboradores de OpenStreetMap (ODbL), sin teselas de internet.
- **Regenerar.** `python figuras_pitch/scripts/mapa_territorios.py`. Para rehacer el GeoJSON de límites hace falta un Python con pyarrow, como el del proyecto: `python figuras_pitch/scripts/extraer_limites.py`.

### (a) Variante: la propuesta 1

- **Mensaje.** Desde el Banco, un solo corredor llega a los tres CDI de La Macarena, a entre 2,9 y 3,3 km, y sigue a Bajo Tablazo, a 9,3 km.
- **Datos.** Los mismos de (a). Los CDI son los tres puntos críticos de la comuna en `datos_publicos/puntos.csv` (ids 16, 17 y 25). Las distancias por la red dan 2,90, 3,24 y 3,26 km a los CDI y 9,28 km a Bajo Tablazo, y quedan en `datos/a_territorio_propuesta1_rutas.csv`. Coinciden con la propuesta 1 de `docs/PILOTO_TERRITORIOS.md` y con la fila P10 de `pitch/CIFRAS_PITCH.md`.
- **Regenerar.** `python figuras_pitch/scripts/mapa_territorios.py --solo 1`

## Fuente tipográfica

La del informe es Ancízar Serif, que no está en el repositorio. Si está instalada en el computador, las figuras la usan. Si no, usan PT Serif, de licencia OFL, que viene con macOS, y si tampoco está, DejaVu Serif, que trae matplotlib. Los PNG y SVG de esta carpeta se hicieron con Ancízar Serif, que está instalada en el computador de Carlos.

La familia se busca también en las carpetas de fuentes del sistema, porque la caché de matplotlib puede ser anterior a la instalación de la fuente. Con `--fuente` se elige otra familia instalada, sin importar tildes ni mayúsculas, o un archivo de fuente del disco:

```bash
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py --fuente "PT Serif"
DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py --fuente /ruta/a/AncizarSerif-Regular.ttf
```

Si la familia pedida no existe, el script lo avisa y usa la de siempre. Para probarlo, `--fuente "Familia Que No Existe"` imprime «aviso: la fuente «Familia Que No Existe» no está instalada; uso Ancizar Serif», o la que haya.

Ningún archivo de fuente se copia al repositorio. Los SVG guardan el texto como trazos, así que se ven igual en un computador sin la fuente. Si una familia es más ancha, los títulos y los textos de las cajas se achican hasta caber, nunca por debajo de 24 px.

## Origen de los scripts

`mapa_territorios.py` y `cuello_despacho.py` se adaptaron de `docs/informe/figuras/scripts/mapa_manizales.py` y `barras_abaco.py`, que quedaron sin cambios. `estilo.py` reúne la paleta, la fuente, el tamaño de proyección y la revisión de textos.
