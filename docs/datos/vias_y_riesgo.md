# Vías y riesgo de derrumbe en Manizales y sus accesos

Este documento reúne los cierres de vías de Manizales y sus accesos antes y después del sismo del 10 de agosto de 2026, y lo que hallamos sobre amenaza por movimientos en masa. Amplía la sección 3 de `docs/investigacion/04_evidencia_del_problema.md`. Al final propone escenarios de cierre para la simulación y los compara con `despacho/sim/escenario.py`. Consulta hecha el 20 de noviembre de 2026.

Archivos que acompañan este documento:

- `datos_publicos/cierres_historicos.csv`, con 178 filas. Las filas S01 a S23 son de después del sismo, R01 es una restricción vigente y A001 a A154 son antecedentes de 2017 a 2026.
- No entregamos `datos_publicos/amenaza_tramos.csv`, porque no hallamos una fuente que asigne nivel de amenaza por sector a nuestros tramos (sección 4).

## 1. Fuentes y cómo se leyeron

Esta sección dice de dónde sale cada dato y qué tan confiable es.

**La fuente principal es el registro #767 de INVÍAS.** INVÍAS publica sus incidentes viales en un servicio de mapas que acepta consultas directas: `https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0`. Cada registro trae la vía, el PR, el tipo de cierre, la causa, la hora de inicio, la fecha estimada de apertura, la hora de creación y la de última edición. Según la definición de la capa, las horas están en UTC; las pasamos a hora de Colombia (UTC-5). La página pública de consulta del #767 no se deja leer sin navegador, pero el servicio sí responde.

Lo que tiene el #767 para nuestros corredores:

- Caldas: 386 registros de todo tipo. De ellos, 62 tienen causa "Deslizamiento" y 46 "Derrumbe".
- Tolima: 80 registros con causa "Deslizamiento" y 53 con causa "Derrumbe". De ellos, 47 y 27 están en vías cuyo nombre incluye Fresno, Manizales, Letras, Mariquita, Padua o Herveo.
- Códigos que usamos: tipo 2 es cierre total, 3 es paso a un carril, 12 es cierre parcial y 19 es inactivo. El tipo de evento 2 es deslizamiento y el 8, derrumbe. El estado 0 es activo y el 1, inactivo. La fuente 04 es la Policía de Tránsito (DITRA), la 05 son las concesiones y la 08, las territoriales de INVÍAS.

El #767 tiene cuatro límites:

1. Los registros viejos guardan el tipo como "Inactivo". Por eso, en la mayoría no sabemos si el cierre fue total o parcial.
2. La fecha estimada de apertura casi nunca está llena. En cinco registros de 2025, esa fecha y la última edición del registro difieren en un minuto o menos, así que la usamos como fin cuando existe.
3. Un mismo derrumbe puede tener varios registros, por ejemplo uno de cierre total y otro de paso a un carril.
4. En 2017 y 2018 varias fechas de apertura se repiten idénticas en registros distintos, lo que sugiere cierres administrativos en lote. En esos casos no las usamos.

**Las páginas se leyeron con un extractor automático, no a mano.** Para el #767 pedimos los valores numéricos crudos de las fechas y los convertimos nosotros. Algunos campos cambiaron entre dos lecturas de la misma consulta, así que solo usamos valores que coincidieron. En S21 la hora cambió entre lecturas y en S20 no obtuvimos el valor crudo; por eso las dos quedaron como "parcial". Antes de llevar un número al pitch, una persona debe abrir su enlace.

Las demás fuentes son la Alcaldía de Manizales, la ANI, la Policía de Tránsito citada por prensa, la Sala de Crisis de la UNGRD, el IDEA de la UNAL Manizales, el Servicio Geológico Colombiano y prensa nacional y regional. De La Patria solo leímos notas reproducidas por Pulzo. Cada fila del CSV trae su enlace.

**Convenciones del CSV:**

- `via_nombre` es el nombre exacto de `datos/semilla/vias.csv` o de `lugares_extra.csv` cuando el cierre corta ese corredor. Que el corredor coincida no quiere decir que el punto caiga sobre la arista; la sección 5 da las distancias.
- `fecha_inicio` es la hora que da la fuente. Si la fuente solo da el día, va solo la fecha. Si el #767 no trae hora de inicio, usamos la hora de creación del registro y lo decimos en `tramo`. Si una nota no da la fecha del hecho, usamos la fecha de publicación y la fila queda como "parcial".
- `fecha_fin` va vacía salvo que la fuente dé el fin. La última edición de un registro inactivo no se usa como fin; esas cotas están en la sección 2.
- `duracion_horas` es un cálculo nuestro, fin menos inicio. En A033 y A066 es la duración aproximada que da la propia nota.
- `verificado` vale "sí" si el dato está en la fuente enlazada, "parcial" si algún campo es aproximado o ambiguo, y "no verificado" si la fuente es secundaria. Las dos filas no verificadas vienen de una tesis que cita prensa.

## 2. Cierres después del sismo del 10 de agosto de 2026

Esta sección reconstruye qué se cerró, cuándo se supo y cuánto duró.

### Día 1: dos salidas cortadas

El sismo fue a las 7:34 a. m. Esa mañana se cortaron dos salidas de Manizales: la vía a Fresno por el Alto de Letras y la autopista del Café entre Pereira y Chinchiná. En cambio, la vía a Medellín no tenía cierres reportados al mediodía ([Minuto60](https://www.minuto60.com/colombia/asi-puede-llegar-eje-cafetero-tras-terremoto-hoy/13318), citando a Invías).

| Hora del 10 ago | Qué se supo | Fuente |
|---|---|---|
| 12:03 p. m. | La Policía de Tránsito reporta cierre total en Pereira-Chinchiná, km 22 a 24, y en Manizales-Fresno, sector Alto de Letras. | [Minuto30](https://www.minuto30.com/vias-cerradas-por-sismo-colombia/1715765/) |
| 12:12 p. m. | Hora de inicio que guarda el #767 para el cierre total del PR 28+200, Alto de Letras. El registro se creó a las 12:52 p. m. | #767, objectid 5073065 (fila S04) |
| mediodía | Invías lista cuatro puntos en la Ruta 5006: el PR 36 en cierre total y los PR 33, 43 y 47 ya con paso a un carril. | [Bloomberg Línea](https://www.bloomberglinea.com/latinoamerica/colombia/lista-de-vias-cerradas-en-colombia-por-el-sismo-hoy-caldas-quindio-risaralda-tolima-y-valle/) (filas S05 a S08) |
| 1:00 p. m. | Hora de inicio que guarda el #767 para Pereira-Chinchiná. El registro se creó a las 5:20 p. m. | #767, objectid 5074664 (fila S01) |
| 5:31 p. m. | Canal Trece reporta restricciones preventivas en Manizales-Chinchiná-Pereira. | [Canal Trece](https://canaltrece.com.co/noticias/mapa-de-movilidad-tras-el-sismo-estos-son-los-principales-corredores-viales-afectados-y-cerrados-en-colombia/) (fila S03) |

Calculado con esas horas: el primer reporte público que hallamos llegó 4 horas y 29 minutos después del sismo. El registro oficial de Pereira-Chinchiná se creó 9 horas y 46 minutos después del sismo. En cambio, en seis registros de deslizamiento de 2025 el #767 tardó entre 0 y 6 minutos en crear el registro desde la hora de inicio. Así que el día del sismo el canal oficial tardó horas en mostrar lo que la Policía ya había anunciado.

La ANI reportó además derrumbes sobre la calzada en el corredor Armenia-Pereira-Manizales: Tarapacá I-Intersección Chinchiná (PR 22+100 y 23+200), Tarapacá II-Intersección Chinchiná (PR 30+000), Jazmín-Tarapacá I (PR 19+800) y Paso Nacional Santa Rosa (PR 10+600). No dijo si cerraba la vía ([ANI](https://www.ani.gov.co/w/cuatro-corredores-viales-concesionados-presentaron-afectaciones-y-activaron-protocolos-de-seguridad-por-eventos-sismol%C3%B3gicos), fila S02).

Dentro de Manizales, el alcalde dijo que las vías estaban habilitadas "en términos generales" y pidió dejar las calles libres para los organismos de socorro ([La Patria](https://www.lapatria.com/manizales/continua-balance-de-danos-en-manizales-ya-se-suman-5-muertes-en-caldas-4-en-manizales-y), 10 ago). El 12 de agosto a las 7:30 a. m., la Sala de Crisis Nacional contaba nueve vías afectadas en Caldas: una en Manizales, una en Chinchiná, dos en Villamaría, tres en Anserma, una en Filadelfia y una en Victoria. El reporte no da sus nombres ([Reporte Situacional 015, UNGRD](https://www.lasillavacia.com/wp-content/uploads/2026/08/REPORTE-SITUACIONAL-15-TERRITORIOS-SISMO-7.4-CHOCO.pdf)).

### Días 2 a 4: los cierres siguen

En la mañana del 12 de agosto, la Policía seguía reportando cierre total en Pereira-Chinchiná y en Manizales-Fresno entre los km 36+800 y 40+300, en Herveo ([Semana](https://www.semana.com/nacion/articulo/actualizacion-de-las-vias-que-siguen-cerradas-tras-el-terremoto-en-colombia/202602/); [RCN Radio](https://newsroom.rcnradio.com/colombia/estas-son-las-vias-que-presentan-cierres-en-colombia-tras-el-terremoto-de-magnitud-7-4), fila S09). El 13 de agosto, hacia las 2 a. m., el #767 abrió dos registros para ese tramo: el PR 36+800 con paso a un carril y el PR 40+300 en cierre total (filas S10 y S11). Los tres registros de cierre total (Pereira-Chinchiná, PR 28+200 y PR 40+300) tuvieron su última edición el 14 de agosto, entre las 6:27 y las 6:35 p. m., y hoy figuran como inactivos.

Cotas calculadas para la duración de los cierres totales:

- Pereira-Chinchiná: al menos 44 horas, desde la hora registrada hasta el reporte de la Policía de la mañana del 12 de agosto. Como máximo 101,5 horas, si la última edición del registro marcó la reapertura.
- Manizales-Fresno, km 36+800 a 40+300: al menos unas 50 horas desde el sismo, por el mismo reporte. Como máximo 107 horas desde el sismo, con el mismo supuesto.
- Los tres registros se editaron por última vez dentro de los mismos ocho minutos. Puede ser una reapertura real o una depuración administrativa; no lo sabemos.

El registro del paso a un carril del PR 36+800 tuvo su última edición el 28 de agosto a las 10:48 p. m. Si esa edición marcó el levantamiento, fueron 15,9 días de paso restringido, que terminan 18,6 días después del sismo.

El 19 de agosto, la UNGRD aún contaba Fresno-Manizales y Pereira-Chinchiná entre los corredores estratégicos afectados, sin decir el tipo de restricción ([Portafolio](https://www.portafolio.co/economia/regiones/servicios-tras-el-terremoto-energia-llega-al-99-pero-siguen-restricciones-en-vias-y-aeropuertos-500954), 21 ago). La ANI mantuvo sin cobro de peaje el corredor Armenia-Pereira-Manizales para la ayuda humanitaria y la maquinaria amarilla ([ANI](https://www.ani.gov.co/ca/w/ani-mantiene-permanente-monitoreo-de-corredores-viales-concesionados-para-garantizar-movilizaci%C3%B3n-de-maquinaria-amarilla-y-ayudas-humanitarias-a-damnificados-del-terremoto-del-pasado-10-de-agosto), 17 ago). Para el fin de semana festivo del 15 al 17 de agosto, el #767 muestra una restricción en horarios definidos a vehículos de carga de 3,4 t o más en Manizales-Mariquita (fila S20).

### Día 16: ocho restricciones dentro de la ciudad

El 26 de agosto la Alcaldía publicó los cierres que seguían vigentes 16 días después del sismo ([Alcaldía de Manizales](https://centrodeinformacion.manizales.gov.co/estos-son-los-cierres-viales-que-permanecen-vigentes-16-dias-despues-del-sismo/), filas S12 a S19):

- Centro: la carrera 23 entre calles 21 y 31, solo peatonal; cierres en las calles 27, 28, 29 y 23; la calle 24 entre carreras 22 y 23 (Calle del Tango); la calle 23 entre carreras 23 y 24.
- Chipre: la calle 12 (avenida 12 de Octubre) junto a la Torre de Chipre, entre carreras 15 y 13A; la carrera 13 en sentido hacia el CAI, entre calles 10 y 9.
- Milán: el corredor principal del Bulevar, del Alto del Perro a La Vicenta; el giro a la derecha en la carrera 20 entre calles 77 y 76.

La Alcaldía los atribuye a "afectaciones en infraestructura" y no da la causa de cada uno. Los tres sectores están entre los barrios con más daños según Asocapitales: Milán, Chipre y el Centro Histórico, entre otros ([Infobae](https://www.infobae.com/colombia/2026/08/18/estos-son-los-municipios-y-ciudades-mas-afectados-por-el-terremoto-del-10-de-agosto-en-colombia-segun-el-ultimo-reporte-de-las-autoridades/), 18 ago). Como la Alcaldía los publicaba, estos cierres se conocían al empezar cada jornada.

### Septiembre a noviembre

El #767 no muestra deslizamientos nuevos en la vía Manizales-Fresno ni en Caldas después del 13 de agosto. Sí registra tres eventos en nuestros corredores:

- 20 de septiembre, en la noche: paso controlado en el km 41 de la vía Manizales-Medellín por un accidente (fila S21).
- 21 de octubre: cierre total con paso a carril en la autopista del Café (Ruta 29RSC, PR 19+300, El Jazmín, Santa Rosa de Cabal) por un deslizamiento. Desde las 11:26 p. m. pasaban solo vehículos livianos y la ruta alterna era la vía antigua por La Siria. Los dos registros tuvieron su última edición el 24 de octubre (fila S22).
- 8 de noviembre: cierre total programado de la vía Manizales-Fresno entre los km 23 y 81, de 4 a. m. a 12 m., por una carrera ciclística (fila S23).

## 3. Antecedentes de 2017 a 2026

Esta sección resume los cierres por deslizamiento en los mismos corredores antes del sismo y cuánto duraron.

La tabla cuenta filas del CSV con causa de remoción en masa (deslizamiento, derrumbe, deslave o desprendimiento). Mezcla registros del #767 y notas de prensa; cuando una nota y un registro describen el mismo evento, cuentan una vez. Son registros y no eventos únicos, porque un derrumbe puede tener más de un registro. El año 2026 incluye las filas del sismo.

| Corredor | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| salida a Letras | 1 | 14 | 9 | 4 | 11 | 17 | 10 | 4 | 12 | 5 | 87 |
| vía a Medellín | 5 | 18 | 2 | 0 | 1 | 7 | 1 | 0 | 1 | 0 | 35 |
| otros corredores | 4 | 1 | 3 | 1 | 0 | 3 | 1 | 0 | 0 | 0 | 13 |
| vía a Chinchiná | 1 | 0 | 1 | 1 | 1 | 2 | 0 | 0 | 1 | 0 | 7 |
| autopista del Café | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 6 |
| vía a Neira | 1 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 5 |
| La Siria | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 3 |
| avenida Kevin Ángel | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Panamericana | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 |
| Total | 15 | 34 | 19 | 6 | 13 | 30 | 13 | 4 | 16 | 10 | 160 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| salida a Letras | 1 | 4 | 4 | 3 | 6 | 17 | 10 | 4 | 11 | 4 | 64 |
| vía a Medellín | 0 | 4 | 1 | 0 | 1 | 5 | 1 | 0 | 1 | 0 | 13 |
| otros corredores | 2 | 1 | 1 | 1 | 0 | 3 | 1 | 0 | 0 | 0 | 9 |
| autopista del Café | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 3 | 6 |
| vía a Chinchiná | 0 | 0 | 0 | 1 | 1 | 2 | 0 | 0 | 1 | 0 | 5 |
| La Siria | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 3 |
| vía a Neira | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 3 |
| avenida Kevin Ángel | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| Panamericana | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 |
| Total | 6 | 9 | 10 | 5 | 8 | 28 | 13 | 4 | 15 | 9 | 107 |

Lo que muestra el conteo:

- La salida a Letras, que es la vía a Fresno y a Bogotá, concentra 87 de las 147 filas de nuestros tramos. Tuvo registros todos los años.
- De esas 147 filas, 65 son de marzo a mayo y 42 de octubre a diciembre. Coinciden con las temporadas de lluvia, aunque no cruzamos el conteo con datos de lluvia.
- El #767 no registra todos los eventos y su cobertura cambia de un año a otro, así que estos conteos son mínimos y no sirven para comparar años.
- Los eventos llegan en racimos. Entre el 6 y el 24 de marzo de 2023 hubo 7 filas en la salida a Letras (A122 a A128). Una de ellas cuenta cuatro deslizamientos en menos de 24 horas en Sabinas y en los km 8 y 11 ([Radio Nacional](https://www.radionacional.co/noticias-colombia/cierre-manizales-bogota-deslizamientos-en-la), fila A125). Entre el 23 de noviembre y el 4 de diciembre de 2022 hubo 5 (A110 a A113 y A115).

Duraciones conocidas, sin contar el sismo:

| Fila | Corredor | Qué pasó | Duración |
|---|---|---|---|
| A033 | vía a Medellín | Derrumbe en La Felisa-Manizales (2018) | casi 1 hora, según la ANI citada por Portafolio |
| A149 | salida a Letras | Cierre total en el km 14+700 (15 nov 2025) | 3,6 horas |
| A066 | avenida Kevin Ángel | Derrumbe de un talud (8 nov 2019) | unas 5 horas, según El Tiempo |
| A079 | salida a Letras | Derrumbe en el km 63+100 (30 abr 2021) | 10,0 horas |
| A131 | salida a Letras | Cierre total en El Ocho, km 24 (7 jun 2023) | 10,4 horas hasta el paso a un carril (inicio del #767, fin de Infobae) |
| A038 | salida a Letras | Derrumbe en Letras, km 30+950 (26 may 2018) | 14,2 horas |
| A151 | salida a Letras | Petaqueros, PR 70+410 a 71+900 (17 dic 2025) | 25,4 horas |
| A049 | salida a Letras | Sabinas, km 6+800 (5 dic 2018) | 27,2 horas |
| A152 | salida a Letras | Paso a un carril por derrumbe en Cerro Bravo, PR 38 (31 ene 2026) | 28,7 horas |
| A148 | salida a Letras | Cierre parcial en Padua, km 64+300 (oct 2025) | 20,4 días |
| A147 | salida a Letras | Paso a un carril en Padua y Herveo, km 30 (oct 2025) | 30,3 días |
| A025 | vía a Medellín | Derrumbe en el túnel de Irra, km 52 (abr 2018) | 31,9 días |
| A150 | salida a Letras | Paso a un carril en el km 14+700, después del cierre total de A149 | 37 días |
| A004 | corredor norte | Derrumbe en La Unión, vía Neira-Salamina (2017) | 77 días |
| A006 | vía a Medellín | Derrumbe en Irra-Manizales, km 4 (sep 2017) | 112 días; la apertura registrada es el 31 de diciembre a las 11:45 p. m., así que puede ser un cierre administrativo |

El patrón que se repite es un cierre total de horas seguido de semanas de paso a un carril. Así pasó el 15 de noviembre de 2025 en el km 14+700 de la vía a Fresno: 3,6 horas de cierre total y luego 37 días con un carril. Entre octubre y diciembre de 2025 hubo dos veces dos restricciones activas a la vez en ese corredor (A147 con A148, y A150 con A151).

La hora de inicio también cuenta. De 123 registros del #767 con hora de inicio en nuestros corredores, 54 (44 %) empezaron entre las 8 p. m. y las 6 a. m.; 46 (37 %), entre las 6 a. m. y las 2 p. m.; y 23 (19 %), entre las 2 p. m. y las 8 p. m. Hay un pico a las 7 a. m. (13 registros), que puede ser de eventos nocturnos registrados en la mañana; eso es una interpretación nuestra.

Restricciones por tipo de vehículo que encontramos:

- Permanente: en Chinchiná-Estación Uribe no pasan vehículos de más de 26 t (tractocamiones y doble troques), las 24 horas. El registro sigue activo en el #767 (fila R01).
- Fines de semana festivos: restricción a vehículos de carga de 3,4 t o más en horarios definidos, en Manizales-Mariquita (fila S20).
- Desvíos distintos por tipo de vehículo: en el cierre de Padua de diciembre de 2024, Invías mandó los pesados por Pereira-Armenia-Ibagué y los livianos por Murillo-Líbano-Cambao (fila A135). En el cierre del puente del Irra en 2018, los autos fueron por Supía-Riosucio-Anserma y la carga por La Virginia-Pereira (fila A019).
- Solo livianos: autopista del Café, PR 19+300, en octubre de 2026 (fila S22).
- Prioridad para la carga: en la Panamericana, en marzo de 2026, el paso por un carril dio prioridad a la carga pesada (fila A153).
- Ruta alterna con límite de peso: en 2021 la alterna Pácora-Aguadas-La Pintada no admitía vehículos de más de 16 t (fila A078).
- La alterna de los livianos también falla: el #767 de Tolima registra cinco derrumbes en la vía Manizales-Murillo-Líbano-Cambao entre el 8 de diciembre de 2022 y el 1 de junio de 2023 (objectids 3602763, 3794647, 3818090, 3834362 y 3925426). No los pusimos en el CSV porque esa vía no está en nuestros archivos.

## 4. Amenaza por movimientos en masa

Esta sección dice qué fuentes de amenaza existen y cuáles pudimos usar.

**El indicador A25 del IDEA está documentado con umbrales.** El A25 es la lluvia acumulada en los 25 días anteriores, en milímetros. La Unidad de Gestión del Riesgo de Manizales lo adoptó a partir de la tesis de Terlien (1996), que asoció unos 200 mm en 25 días con alta probabilidad de deslizamientos ([IDEA, Boletín Ambiental 145](https://idea.manizales.unal.edu.co/publicaciones/boletines_ambientales/boletin145.pdf), marzo de 2018). Los umbrales de la UGR aparecen en ese boletín y en el [registro del SAT de deslizamientos de 2020](https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf):

| Alerta | A25 |
|---|---|
| Amarilla | desde 200 mm y menos de 300 mm |
| Naranja | desde 300 mm y menos de 400 mm |
| Roja | 400 mm o más |

La red tiene 14 estaciones en Manizales; sus propietarios son la CHEC, Emas, la UNAL Manizales y la Alcaldía. El 16 de febrero de 2026 la Alcaldía declaró alerta amarilla por lluvias: ocho estaciones superaban 200 mm en menos de 25 días y La Palma registraba 300 mm ([Noticias RCN](https://www.noticiasrcn.com/colombia/declaran-alerta-amarilla-en-manizales-por-lluvias-extremas-992470)). No encontramos la serie diaria del A25 de agosto a noviembre de 2026, ni un estudio que cruce el A25 con cierres de vías.

**El Servicio Geológico Colombiano publica mapas de amenaza que no alcanzamos a procesar.** El SGC ofrece el mapa nacional de amenaza por movimientos en masa a escala 1:100.000, versión 2 de diciembre de 2019, y un archivo para Caldas (`Caldas.zip`) en su [página de descargas](https://www2.sgc.gov.co/sgc/mapas/Paginas/Imagenes-de-amenazas-.aspx). No lo procesamos, porque desde nuestra terminal solo responde Nominatim y el extractor web no abre archivos comprimidos. Cruzar ese mapa con las 15 aristas de `vias.csv` daría un nivel de amenaza por tramo con fuente oficial.

**No consultamos el SIMMA ni hallamos una zonificación de Corpocaldas por sector.** El cupo de búsquedas web se agotó antes de llegar al inventario SIMMA del SGC. Una [tesis de 2019 de la Universidad Católica de Colombia](https://core.ac.uk/download/250408561.pdf) zonifica la amenaza de Chinchiná a escala 1:25.000, pero no asigna nivel a nuestros tramos.

Por eso no entregamos `amenaza_tramos.csv`. La recurrencia de la sección 3 no reemplaza un nivel de amenaza, porque cuenta reportes, y los reportes dependen del tráfico y de la vigilancia de cada vía.

## 5. Correspondencia con nuestros tramos

Esta sección dice qué tan cerca cae cada cierre de la arista que lo representa en nuestros archivos. Las coordenadas de los cierres vienen de la geometría del #767 o de Nominatim. Las distancias son en línea recta y son un cálculo nuestro.

| Cierre | `via_nombre` | Punto usado | Distancia a la arista |
|---|---|---|---|
| Avenida 12 de Octubre junto a la Torre de Chipre (S16) | avenida 12 de Octubre | "Torre al Cielo, Avenida 12 de Octubre" en Nominatim | 21 m |
| Panamericana, sector Cámbulos-La Enea (A153, A154) | Panamericana | Los Cámbulos en Nominatim | 0,2 km; La Enea queda a 5,1 km |
| El Ocho, km 24 (A131) | salida a Letras | La Esperanza (El Ocho) en Nominatim | 2,0 km |
| Sabinas (A049, A125) | salida a Letras | Sabinas en Nominatim | 3,9 km |
| Alto de Letras, PR 28+200 (S04) | salida a Letras | geometría del #767, vereda Letras de Herveo | 6,2 km al oriente |
| Pereira-Chinchiná, PR 22 a 24 (S01) | autopista del Café | geometría del #767, San Andrés (Chinchiná) | 4,9 km al sur |
| Autopista del Café, PR 19+300 (S22) | autopista del Café | geometría del #767, El Jazmín (Santa Rosa de Cabal) | 9,3 km al sur |
| Bulevar de Milán (S18) | vacío | "Vía del Alto del Perro" en Nominatim | 0,4 km de la arista "avenida Alberto Mendoza"; no sabemos si es la misma vía |

Dos consecuencias para la simulación:

- Las aristas de la salida a Letras, la autopista del Café, La Siria y la vía a Neira están a 15,7; 12,3; 7,7 y 8,6 km del centro que usa `escenario.py`. Ese generador pone los puntos a 6 km del centro como máximo y sortea cierres solo en tramos de esos caminos. Por eso los cierres intermunicipales del sismo no entran en la simulación actual: afectan la llegada de ayuda al acopio y no el reparto urbano.
- Los cierres urbanos del día 16 sí caen dentro del radio. La arista "avenida 12 de Octubre" está a 0,9 km del centro y coincide con un cierre real.

## 6. Escenarios de cierre para la simulación

Esta sección propone cinco escenarios. Cada parámetro trae su fuente o dice "supuesto".

### E1. Día del sismo: salidas cortadas y nadie lo sabe

- Tramos: salida a Letras y autopista del Café con cierre total; vía a Chinchiná con restricción preventiva; vía a Medellín abierta. Fuentes: filas S01, S03, S04 y S09; Minuto60 para Medellín.
- Cuántos a la vez: dos corredores de salida cerrados y uno restringido. Dentro de la ciudad no hay dato del día 1. Supuesto: mantener el rango actual de 3 a 8.
- Cuándo empiezan: todos en la hora 0, porque los causa el sismo. Fuente: las descripciones del #767 dicen "a causa del sismo".
- Cuántos se conocen al empezar: ninguno. El primer reporte público llegó 4,5 horas después del sismo y el registro oficial de Pereira-Chinchiná, 9,8 horas después. Calculado con Minuto30 y el #767.
- Duración: no se levantan en la jornada. Fuente: seguían cerrados en la mañana del 12 de agosto (Semana; RCN Radio).
- Vehículos: con cierre total no pasa ninguno, así que `p_bloquea` vale 1 para los tres tipos. Los PR 33, 43 y 47 de la Ruta 5006 tenían un carril antes del mediodía (Bloomberg Línea, citando a Invías).
- Cómo modelarlo: como estas aristas están fuera del radio de 6 km, el efecto entra mejor como un retraso en la llegada de lotes al acopio. Supuesto.

### E2. Semanas 1 a 3: cierres urbanos conocidos

- Tramos: los ocho de la Alcaldía (filas S12 a S19). Tres tienen arista en nuestros archivos: "avenida 12 de Octubre", "carrera 23" y "calle 23".
- Cuántos a la vez: 8. Fuente: Alcaldía, 26 de agosto.
- Cuántos se conocen al empezar: todos, porque la Alcaldía los publicaba. Fuente: Alcaldía.
- Duración: al menos 16 días, así que no se levantan en la jornada. Fuente: Alcaldía.
- Vehículos: la carrera 23 queda solo para peatones, la carrera 13 cerrada en un sentido y la carrera 20 sin giro a la derecha. Para los demás la fuente no da detalle. Supuesto: no pasa ningún vehículo.
- Cierres nuevos durante la jornada: supuesto, 0 a 2 por réplicas o caída de fachadas. No hallamos datos.

### E3. Temporada de lluvias en los accesos

- Tramos: salida a Letras, que es la más frecuente, y además vía a Medellín, vía a Chinchiná, autopista del Café, La Siria y vía a Neira. Fuente: sección 3.
- Cuántos a la vez: de 1 a 4 en un mismo corredor. Fuentes: cuatro deslizamientos en menos de 24 horas en marzo de 2023 (fila A125); dos restricciones simultáneas en la vía a Fresno a finales de 2025 (#767).
- Cuándo empiezan: 44 % antes de la jornada, 37 % en sus primeras 8 horas y 19 % en las 6 horas finales, para una jornada de 6 a. m. a 8 p. m. Calculado con 123 registros del #767.
- Duración: entre los eventos con inicio y fin que duraron menos de dos días, el rango va de 1 a 28,7 horas, y cinco de nueve duraron 10,4 horas o menos. Después puede quedar un carril durante 16 a 37 días. Fuentes: tabla de duraciones de la sección 3 y fila S10.
- Vehículos: con cierre total, ninguno; con un carril, todos, porque la mayoría de registros no distingue tipos; a veces solo livianos (fila S22).
- Disparador: supuesto, subir la tasa de cierres cuando el A25 pase de 200 mm en varias estaciones, que es el umbral de alerta amarilla de la UGR.

### E4. Autopista solo para livianos, desvío por La Siria

- Tramos: autopista del Café con un carril solo para livianos, y La Siria como alterna. Fuente: fila S22. En 2021 el cierre de la doble calzada Manizales-Chinchiná en el km 11+500 también se desvió por La Siria (fila A076, fuente ANI).
- Cuántos a la vez: uno, con riesgo de que la alterna también falle. La Siria tuvo registros de deslizamiento en abril y junio de 2025 (#767).
- Cuándo empieza: a las 3:32 p. m. con cierre total; desde las 11:26 p. m., un carril. Fuente: #767.
- Duración: unas 80 horas hasta la última edición de los registros. Calculado; el fin es una cota.
- Vehículos: el camión no pasa; el campero y la moto sí. Fuente: el #767 dice "solo vehículos livianos". Contar el campero como liviano es un supuesto.

### E5. Derrumbe en una avenida urbana de ladera

- Tramos: avenida Kevin Ángel o Panamericana, las dos dentro del radio de 6 km. Fuentes: filas A002, A066, A153 y A154.
- Cuántos a la vez: uno.
- Cuándo empieza: en cualquier momento. El de la Kevin Ángel de 2019 fue hacia las 2 p. m. (El Tiempo).
- Duración: unas 5 horas en la Kevin Ángel (2019). En la Panamericana (2026) hubo bloqueo de las dos calzadas, luego paso intermitente por un carril, y luego un cierre total para demoler rocas hasta al menos el mediodía del 4 de marzo.
- Vehículos: con cierre total, ninguno. Con un carril, en la Panamericana se dio prioridad a la carga pesada (La Patria, vía Pulzo). Eso va en contra del supuesto de que el camión es siempre el más bloqueado.
- Levantamiento: supuesto, pasar a un carril a las 5 horas, como en la Kevin Ángel.

## 7. Comparación con `escenario.py`

Esta sección pone cada parámetro de cierres de la simulación junto a lo que encontramos.

| Parámetro | Valor actual | Lo que encontramos | Lectura |
|---|---|---|---|
| `cierres_min`, `cierres_max` | 3 a 8 por jornada | 8 restricciones urbanas el día 16; 2 salidas cortadas el día 1; hasta 4 deslizamientos en 24 horas en un corredor | El rango cabe en la evidencia urbana del día 16. Del día 1 dentro de la ciudad no hay dato. |
| `frac_cierres_inicio` | 0,30, presentes en la hora 0 y desconocidos | Día 1: todos presentes en la hora 0 y desconocidos durante horas. Día 16: todos presentes y conocidos. Lluvias: 44 % empiezan antes de la jornada | Para lluvias, el 44 % calculado queda por encima de 0,30. Para el sismo faltan dos casos: todos ocultos (día 1) y todos conocidos (días siguientes). |
| Hora de los demás cierres | uniforme entre la hora 0 y la 8 | 37 % en las primeras 8 horas y 19 % en las 6 finales | El generador no produce cierres en las últimas 6 horas de la jornada. |
| Levantamiento | ningún cierre se levanta | Sismo: ninguno en días. Lluvias: 5 de 9 eventos cortos con inicio y fin duraron 10,4 horas o menos, y varios quedaron luego a un carril | Coincide con el sismo. Para lluvias conviene permitir que un cierre total pase a un carril. |
| `p_bloquea` | camión 1,0; campero 0,7; moto 0,3 | Cierre total: bloquea a todos. Un carril: pasan todos. "Solo livianos": bloquea solo al camión. Límites de peso de 26 t, 16 t y 3,4 t | El orden camión, campero, moto tiene respaldo. Los valores 0,7 y 0,3 no tienen fuente. |
| `min_reporte` + `min_confirmacion` | 3 + 5 minutos | Canal oficial el día 1: 4,5 horas hasta el primer reporte público y 9,8 horas hasta el registro del #767. En 2025, el #767 registraba en 0 a 6 minutos | Los 8 minutos son un supuesto sobre el canal de DespachoX. Sin ese canal, en la emergencia la información tardó horas. |
| `radio_libre_acopio_m` | 400 m | Los cierres del Centro quedan a pocas cuadras de la plaza de Bolívar, donde el generador pone el acopio. Los puntos de referencia de "calle 23" y "carrera 23" están a 442 y 613 m de ese centro | Parte de los cierres reales del Centro no podría sortearse. No lo medimos sobre la red. |
| `radio_km` | puntos a 6 km del centro como máximo | Las 4 aristas intermunicipales con cierres están a entre 7,7 y 15,7 km | Los cierres de acceso no tocan el reparto simulado. |

## 8. Vacíos y a quién preguntar

Esta sección lista lo que faltó y quién puede conseguirlo.

Lo que no conseguimos:

- La hora real de reapertura de los cierres del sismo. El #767 solo deja ver la última edición de cada registro inactivo.
- Los cierres urbanos de Manizales entre el 10 y el 25 de agosto, y su fecha de levantamiento. Solo hallamos la lista del día 16.
- Qué vehículos pasaban por cada cierre urbano.
- La serie diaria del A25 de 2026 y su cruce con los cierres.
- Un nivel de amenaza por tramo, porque el mapa del SGC quedó sin procesar y el SIMMA y Corpocaldas sin consultar.
- Las notas originales de La Patria, Eje21 y Caracol Radio. El cupo de búsquedas se agotó y solo leímos La Patria reproducida por Pulzo.
- Páginas que no respondieron al extractor: la consulta pública del #767, los boletines climatológicos del CDIAC del IDEA, Contexto Ganadero y un informe de Data Friendly Space en ReliefWeb.

Lo que solo una persona puede conseguir:

1. Dirección Territorial Caldas de INVÍAS o línea #767: pedir la exportación del #767 para Caldas y Tolima entre el 10 de agosto y el 30 de septiembre de 2026, con hora real de apertura. Preguntar si la última edición del 14 de agosto, entre las 6:27 y las 6:35 p. m., fue una reapertura.
2. Secretaría de Movilidad de Manizales: pedir la lista diaria de cierres por el sismo, con fecha de inicio y de fin, y qué vehículos podían pasar.
3. Unidad de Gestión del Riesgo de Manizales o IDEA de la UNAL: pedir el A25 diario por estación de agosto a noviembre de 2026 y el inventario de deslizamientos urbanos después del sismo.
4. Concesión Autopistas del Café o ANI: pedir la bitácora de los PR 10 a 30 entre el 10 y el 14 de agosto, con horas de cierre y de paso a un carril.
5. Cualquier persona del equipo, desde un navegador: descargar `Caldas.zip` del SGC y cruzarlo con las aristas de `vias.csv` en QGIS.

Para repetir las consultas al #767, las URL completas están en la columna `fuente_url` del CSV. El servicio respondió bien con `outFields=*`; con una lista de campos, el extractor devolvió a veces la respuesta de la consulta anterior.
