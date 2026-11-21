# Tres territorios para el piloto de 30 a 90 días

**Decisiones de Carlos (21 de noviembre).** A las 6:10 a. m., el piloto empieza en la propuesta 2. A las 8:05 a. m., el piloto suma una zona cada 30 días: la propuesta 1 el día 30 y la 3 el día 60.

Cada propuesta une una comuna y un corregimiento para el piloto con el Banco Arquidiocesano de Alimentos y la UGR. Consulta del 20 de noviembre de 2026. **[F]** lo dice la fuente, abierta hoy con un lector automático y pendiente de revisión humana; **[M]** lo calculé con datos del repositorio; **[I]** es inferencia nuestra.

## Lo común a los tres

- No hay damnificados por comuna ni por vereda en fuentes públicas, ni lista de comedores comunitarios (`docs/datos/demanda.md`; `puntos_y_acopios.md`). Los albergues de los coliseos cerraron el 29 de agosto (`docs/investigacion/11`; no verificado hoy), así que los puntos críticos de hoy son CDI, hogares infantiles, centros de salud y Centros Vida [I].
- Hay 204 juntas de acción comunal, 131 de barrio y 73 de vereda, sin reparto público por comuna [F] ([Alcaldía, 2025](https://manizales.gov.co/wp-content/uploads/2025/08/CONSOLIDADO-JUNTAS-ACCION-COMUNAL-Y-ADMINISTRADORAS-LOCALES-JAC-JAL.pdf)).
- El catálogo es `datos_publicos/puntos.csv`, y las distancias son por la red vial del equipo desde el Banco [M]. La línea base es la bitácora de dos semanas y el mes de despachos del Banco (`docs/FICHA_CORTA.md`, componente 4).
- En los tres hay que llamar al Banco y a la UGR (director, Diego Armando Rivera Gutiérrez).

## 1. La Macarena y el corregimiento El Tablazo

**Por qué.**
- La Patria cuenta a El Carmen entre los sectores urbanos con daños. Además, pone a Bajo Tablazo entre los puntos rurales más afectados, y allí se planea demoler dos viviendas [F] ([13 sep 2026](https://www.lapatria.com/manizales/un-mes-del-sismo-en-manizales-estas-son-las-cifras-de-viviendas-afectadas-ayudas-y)).
- Los accesos se caen sin sismo. INVÍAS registra derrumbes en la vía Manizales–Chinchiná, sector Bajo Tablazo, el 17 de noviembre de 2017 y el 10 de mayo de 2019 [F] ([#767](https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0/query?where=objectid%20IN%20%28280769,1432078%29&outFields=*&f=json)). En la vereda Java colapsó la banca de la vía y unas 150 familias quedaron incomunicadas, según un líder local [F] ([La Patria, 19 mar 2025](https://www.lapatria.com/manizales/sin-paso-en-vereda-de-manizales-colapsa-y-150-familias-quedan-incomunicadas)).
- La comuna tiene 42.063 habitantes (ASIS 2023) y tres CDI en el catálogo, a entre 2,9 y 3,3 km del Banco [M]. Java tiene Centro Vida [F] ([Desarrollo Social](https://manizales.gov.co/wp-content/uploads/2025/08/GRUPOS-DE-INTERES.pdf)) y el corregimiento, junta [F] ([La Patria, 20 dic 2024](https://www.lapatria.com/manizales/vendedores-informales-del-bajo-tablazo-podrian-ser-desalojados-de-manizales-chinchina)). Bajo Tablazo queda a 9,3 km, por una ruta que cruza La Macarena y sigue por la vía a Chinchiná [M].

**Qué mediría.** Entregas a tiempo en los CDI y el Centro Vida, contra la bitácora del Banco. Entregas semanales a Bajo Tablazo y Java según el vehículo que entra, porque el grafo no llega a la vereda (nodo más cercano a 701 m) [M]. Tiempo de replanificación en un simulacro de cierre en Bajo Tablazo, contra las 9 h 46 min que tardó en aparecer el registro oficial de un cierre el día del sismo (`vias_y_riesgo.md`, rama `datos`).

**Riesgos y lo que falta.** No sabemos si el Banco atiende hoy a alguien aquí, ni cuántas familias de Bajo Tablazo perdieron la vivienda. La nota de Java es anterior al sismo, y el nombre del corregimiento varía entre fuentes.

**A quién llamar.** Corregiduría de El Tablazo, junta del corregimiento, ICBF y Dirección Territorial Caldas de INVÍAS.

## 2. Ciudadela del Norte y el corregimiento El Manantial

**Por qué.**
- La Alcaldía reportó intervenciones en San Sebastián y Bosques del Norte [F] ([15 ago](https://centrodeinformacion.manizales.gov.co/manizales-continua-con-la-evaluacion-de-viviendas-y-prepara-el-plan-de-retorno-tras-el-sismo/)), y el 21 de octubre revisó sus laderas por lluvias [F] ([Alcaldía](https://centrodeinformacion.manizales.gov.co/aumentan-las-lluvias-en-manizales-y-hay-varios-sectores-con-acumulados-de-mas-de-300-mm/)).
- En Pueblo Hondo, cuatro viviendas tuvieron pérdida total [F] ([Alcaldía, 27 ago](https://centrodeinformacion.manizales.gov.co/alcaldia-de-manizales-acompana-a-familias-afectadas-por-el-sismo-en-pueblo-hondo/)). El PMA recorrió con la Alcaldía las veredas con más daño para identificar necesidades de seguridad alimentaria, y en la nota hablan las juntas de Alto del Guamo y Alto Bonito [F] ([Alcaldía, 20 ago](https://centrodeinformacion.manizales.gov.co/alcaldia-de-manizales-y-programa-mundial-de-alimentos-recorren-la-zona-rural-para-identificar-afectaciones-tras-el-sismo/)).
- INVÍAS registra cinco derrumbes o deslizamientos en la vía Manizales–Neira entre 2017 y 2023, uno en Alto Bonito. El de Maracas (15 ene 2023) dice que no hay ruta alterna [F] ([#767](https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0/query?where=objectid%20IN%20%28285482,449685,1363400,1799896,3680182%29&outFields=*&f=json)).
- Es la comuna más poblada, con 58.776 habitantes (ASIS 2023). Tiene dos CDI, un centro de salud y un CISCO en el catálogo, a entre 2,4 y 4,1 km del Banco [M], y un Centro Día [F]. Alto Bonito, con Centro Vida [F] ([Desarrollo Social](https://manizales.gov.co/wp-content/uploads/2025/08/GRUPOS-DE-INTERES.pdf)), queda a 8,8 km [M].

**Qué mediría.** Pedidos que hacen y confirman las juntas de Alto Bonito y Alto del Guamo, y entregas a tiempo en los puntos urbanos. Un simulacro de cierre en Maracas. Si el PMA comparte su levantamiento de agosto, sirve de línea base de necesidad.

**Riesgos y lo que falta.** OpenStreetMap pone Pueblo Hondo en Neira, y la Alcaldía en El Manantial. Por el grafo, la ruta a Alto Bonito sale por la comuna San José [M]. Del daño urbano no hay cifras.

**A quién llamar.** Área de análisis y cartografía de la vulnerabilidad del PMA, juntas de Alto Bonito y Alto del Guamo y Secretaría de Agricultura.

## 3. Atardeceres y el corregimiento Colombia (Kilómetro 41)

**Por qué.**
- Chipre está entre los sectores con mayores daños [F] ([Infobae, 18 ago](https://www.infobae.com/colombia/2026/08/18/estos-son-los-municipios-y-ciudades-mas-afectados-por-el-terremoto-del-10-de-agosto-en-colombia-segun-el-ultimo-reporte-de-las-autoridades/)). El 26 de agosto seguía cerrada la avenida 12 de Octubre junto a la Torre de Chipre [F] ([Alcaldía](https://centrodeinformacion.manizales.gov.co/estos-son-los-cierres-viales-que-permanecen-vigentes-16-dias-despues-del-sismo/)).
- El 21 de octubre la comuna superó 300 mm de lluvia acumulada y quedó en alerta naranja [F] ([Alcaldía](https://centrodeinformacion.manizales.gov.co/aumentan-las-lluvias-en-manizales-y-hay-varios-sectores-con-acumulados-de-mas-de-300-mm/)), que es el umbral naranja del A25 del IDEA [I].
- En el km 41 colapsaron estructuras sin cimientos y hubo un deslizamiento. Según un vecino, algunas personas dormían en carpas o sobre plásticos [F] ([Alcaldía, 18 ago](https://centrodeinformacion.manizales.gov.co/alcaldia-de-manizales-verifica-viviendas-afectadas-por-el-sismo-en-el-kilometro-41-y-acompana-a-las-familias-rurales/)). En septiembre, los recorridos por Colombia, El Remanso y La Cristalina hallaron viviendas para demoler [F] ([Alcaldía, 16 sep](https://centrodeinformacion.manizales.gov.co/continuan-recorridos-en-la-zona-rural-para-atender-afectaciones-por-el-sismo/)).
- La ruta del Banco al km 41 sale por Morrogacho y pasa por La Aurora [M]. INVÍAS registra diez derrumbes o deslizamientos en la vía Manizales–Medellín entre 2017 y 2019, siete de ellos en Irra o entre los km 48 y 66 [F] ([#767](https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0/query?where=departamento%3D%2717%27%20AND%20nom_via%20LIKE%20%27%25Medell%25%27%20AND%20tipo_evento%20IN%20%282,8%29&outFields=*&f=json)).
- La comuna tiene 39.250 habitantes (ASIS 2023) y cuatro críticos a entre 4,2 y 7,2 km del Banco: dos hospitales y dos hogares infantiles [M]. En lo rural están el salón comunal de La Aurora, a 7,4 km, y la junta y el Centro Vida del Kilómetro 41, a 36,4 km [F] [M].

**Qué mediría.** Rutas que evitan tramos en alerta del A25, en la comuna donde la alerta ya ocurrió. Entregas a tiempo en los hospitales y hogares infantiles, y kilómetros por jornada en la ruta larga al km 41.

**Riesgos y lo que falta.** El km 41 puede quedar fuera de la rutina del Banco. No sabemos si los hospitales le piden comida, ni hallamos cierres registrados en la vía a La Aurora.

**A quién llamar.** IDEA-UNAL por el A25, junta del Kilómetro 41 y Coordinación Social de la Alcaldía, que hizo los recorridos rurales.

## Recomendación

Carlos decidió a las 6:10 a. m. del 21 de noviembre que el piloto empieza en la propuesta 2. A las 8:05 a. m. decidió que crece por zonas, una cada 30 días.

| Días | Zona que entra | Por qué en ese orden |
|---|---|---|
| 0 a 30 | Ciudadela del Norte y El Manantial (propuesta 2) | Es la comuna más poblada, con 58.776 habitantes (ASIS 2023). Además, el PMA ya levantó necesidades en sus veredas y sus juntas hablaron en público [F] |
| 30 a 60 | La Macarena y El Tablazo (propuesta 1) | El sismo dejó daño con fuente en sus dos partes, y sus accesos se caen también sin sismo [F], lo que respalda la tesis del día normal (`docs/PILOTO.md`). Comuna y vereda quedan sobre una sola ruta [M], aunque la distancia a Bajo Tablazo está por confirmar |
| 60 a 90 | Atardeceres y Kilómetro 41 (propuesta 3) | La comuna ya tuvo alerta naranja por lluvia [F], así que ahí se prueba el A25 del IDEA con el simulacro, si el IDEA lo respalda [I] |

Cada zona nueva entra solo si la anterior cumplió su criterio de validación y si el Banco lo confirma (`docs/PLAN_30_90.md`, sección 4). En la propuesta 2 la ruta a la vereda sale por otra comuna [M], así que las entregas urbanas y las rurales van por corredores distintos. Si el Banco no tiene organizaciones inscritas en una zona, le proponemos cambiar el orden, y lo decide con Carlos.

## Para la diapositiva

**1. La Macarena y El Tablazo**
- El sismo golpeó El Carmen y Bajo Tablazo, uno de los puntos rurales con más daño.
- La vía se cae sin sismo: 150 familias incomunicadas en Java (2025) y derrumbes en 2017 y 2019.
- Tres CDI a 3 km del Banco y la vereda en el mismo corredor (distancia por confirmar).

**2. Ciudadela del Norte y El Manantial**
- La comuna más poblada (58.776) y veredas donde el PMA levantó necesidades tras el sismo.
- Cuatro casas perdidas en Pueblo Hondo; en Maracas, la vía a Neira no tiene ruta alterna.
- Mide pedidos por junta y entregas a CDI, centro de salud y Centro Vida.

**3. Atardeceres y Kilómetro 41**
- Chipre, entre los sectores con más daño; alerta naranja por lluvia en octubre.
- En el km 41 colapsaron estructuras y hubo un deslizamiento.
- Prueba el A25 de la UNAL donde la alerta ocurrió, con dos hospitales y dos hogares infantiles.
