# Puntos de entrega y centros de acopio reales de Manizales

Este documento explica de dónde salen tres archivos de `datos_publicos/`: `puntos.csv`, `acopios.csv` y `puntos_acopios_fuentes.csv`. Todas las fuentes se consultaron el 20 de noviembre de 2026. Cada fila de los dos primeros archivos tiene su fuente, su origen de coordenada y su nivel de verificación en `puntos_acopios_fuentes.csv`.

Leyenda usada en todo el documento: **[Fuente]** es lo que dice una fuente; **[Cálculo]** es algo que calculé a partir de fuentes; **[Supuesto]** es una decisión mía que una persona debería confirmar.

## 1. Resumen

Esta sección da las cifras del entregable.

- 50 puntos de entrega. 35 son críticos y 15 no lo son.
- 43 puntos están en el área urbana y cubren las 12 comunas de `barrios.csv`. Los otros 7 son salones comunales de veredas.
- 2 centros de acopio: el Banco de Alimentos de Manizales (id 1) y el Coliseo Menor (id 2).
- De las 52 filas (50 puntos y 2 acopios), 40 quedan con `verificado=si` y 12 con `verificado=parcial`. La sección 5 explica qué significa cada valor.
- El cargador del sistema acepta los archivos. Lo probé sobre una base temporal fuera del repositorio con `DESPACHOX_DB=<ruta temporal> python -m despacho.semilla --cargar --reiniciar --origen datos_publicos/`. La salida fue `puntos.csv real 50 filas` y `acopios.csv real 2 filas`.

## 2. Centros de acopio

Esta sección dice qué respalda cada acopio y cómo se obtuvo su coordenada.

| id | Acopio | Qué dice la fuente | Coordenada | `tiene_frio` |
|---|---|---|---|---|
| 1 | Banco de Alimentos de Manizales (Calle 49 # 27A-85) | [Fuente] La República lo nombra entre los puntos principales de acopio del corredor humanitario de ABACO ([10 ago 2026](https://www.larepublica.co/economia/gremios-apoyaran-el-corredor-humanitario-por-sismo-de-la-mano-de-abaco-4454919)). Noticias RCN dice que Manizales se consolidó como uno de los principales puntos de acopio de la red ([10 ago 2026](https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906)). Minuto60 publica la dirección Calle 49 No. 27A-85 ([10 ago 2026](https://www.minuto60.com/colombia/puntos-acopio-llevar-ayudas-terremoto-colombia/13301)). | 5.060203, -75.501243. Esquina de la Calle 49 con la Carrera 28 en OSM (way 28160903). | vacío |
| 2 | Centro de acopio Coliseo Menor | [Fuente] La Alcaldía lo acondicionó como «centro humanitario y de acopio». Recibe mercados, aseo, cobijas y colchonetas. La gestora social de Manizales dijo que reparte entre más de 4.000 damnificados ([Noticias RCN, 12 ago 2026](https://www.noticiasrcn.com/colombia/manizales-convierte-al-coliseo-menor-en-centro-de-acopio-tras-el-terremoto-1049719)). | 5.055962, -75.488616. OSM relation 7923252. | vacío |

Cómo se ubicó el Banco de Alimentos. OSM no tiene el Banco como lugar con nombre, así que partí de la dirección.

- [Cálculo] En OSM, la placa 27A-85 queda en la cuadra de la Calle 49 entre las carreras 27A y 28. Esa cuadra está en la Zona Industrial El Campín, comuna La Estación.
- [Cálculo] En OSM la cuadra mide unos 94 m. La placa 85 indica unos 85 m desde la Carrera 27A, así que el predio queda a pocos metros de la esquina con la Carrera 28. Uso el nodo de esa esquina. El error esperado es menor de 50 m.
- [Cálculo] Como control, el ICBF ubica otra dirección de la misma calle (Calle 49 # 26-65) sobre ese mismo tramo de OSM.
- [Supuesto] La dirección de Minuto60 es la de la bodega actual. Es una sola fuente y debe confirmarse por teléfono.

`tiene_frio` va vacío en los dos acopios, porque ninguna fuente consultada menciona cuarto frío en Manizales.

[Cálculo] Los dos acopios están a 1,5 km en línea recta. Desde el Banco de Alimentos, la mediana de distancia en línea recta a los puntos urbanos es 1,8 km y la máxima es 5,2 km. A los salones rurales hay entre 5,3 y 13,3 km.

## 3. Puntos de entrega por tipo

Esta tabla resume qué tipos de sitio entraron, cuántos hay y de dónde sale cada coordenada.

| Tipo | Puntos | Críticos | Fuente del sitio | Coordenada |
|---|---|---|---|---|
| Albergue del sismo | 2 | 2 | Alcaldía vía [RCN Radio, 10 ago](https://newsroom.rcnradio.com/colombia/recomendaciones-para-ciudadanos-de-manizales-tras-el-terremoto-de-7-4-donde-acudir-por-ayuda-y-que-hacer-ante-replicas); [Blu Radio, 13 ago](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10); [Noticias RCN, 12 y 24 ago](https://www.noticiasrcn.com/colombia/manizales-prepara-la-demolicion-de-7-edificios-que-presentan-danos-estructurales-1053593) | OSM |
| CDI del ICBF | 19 | 19 | [ICBF, datos.gov.co i8ww-5mcf](https://www.datos.gov.co/resource/i8ww-5mcf.json?codigo_dane_municipio=17001), vigencia 2026, estado ACTIVA | ICBF |
| Hogar infantil del ICBF | 5 | 5 | Igual que la fila anterior | ICBF |
| Hospital | 3 | 3 | OSM; criterio de prioridad de ABACO ([Noticias RCN, 10 ago](https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906)) | OSM |
| Hospital geriátrico (centro de bienestar con convenio) | 1 | 1 | [Secretaría de Desarrollo Social](https://manizales.gov.co/wp-content/uploads/2025/08/GRUPOS-DE-INTERES.pdf) | OSM |
| Centro de salud de Assbasalud | 4 | 4 | [Informe de gestión de Assbasalud, jun 2025](https://manizales.gov.co/wp-content/uploads/2025/07/ASSBASALUD.pdf) para dos sedes; OSM para las otras dos | OSM |
| Centro Día del adulto mayor | 1 | 1 | ICBF (la unidad funciona en el Centro Día Solferino) | ICBF |
| CISCO (sede comunitaria municipal) | 3 | 0 | ICBF y OSM | OSM (2) e ICBF (1) |
| Casa de la cultura | 2 | 0 | ICBF y OSM | ICBF (1) y OSM (1) |
| Colegio usado como albergue en 2017 | 3 | 0 | [La FM, 22 abr 2017](https://www.lafm.com.co/colombia/habilitan-coliseo-menor-manizales-albergue-damnificados) | OSM |
| Salón comunal rural | 7 | 0 | ICBF (unidades que se reúnen en casetas y salones de juntas) | ICBF |

## 4. Método

Esta sección cuenta los pasos en el orden en que los hice.

1. Leí `docs/PROBLEMA.md`, las partes A3 y A4 de `docs/investigacion/05_datos_abiertos_y_aliados.md`, `04_evidencia_del_problema.md` y `datos/semilla/lugares_extra_fuentes.csv` para no repetir trabajo.
2. Busqué en prensa y documentos oficiales los albergues, acopios y la sede del Banco de Alimentos. Abrí cada página citada.
3. Consulté datos.gov.co con WebFetch. El dataset del ICBF i8ww-5mcf trae 120 unidades en Manizales con dirección y coordenada. Bajé las coordenadas dos veces, por consultas distintas, y coinciden dígito por dígito. Las 24 unidades usadas tienen vigencia 2026 y estado ACTIVA.
4. Saqué de OpenStreetMap, con Nominatim desde la terminal, las coordenadas de coliseos, hospitales, centros de salud, CISCO y colegios. Hice como máximo una consulta por segundo y guardé todo en caché.
5. Contrasté cada coordenada del ICBF con un geocodificado inverso de Nominatim. En los 24 CDI y hogares infantiles, la vía que devuelve OSM es la de la dirección oficial o una contigua. Tres casos coinciden además con un jardín infantil mapeado en OSM: el CDI Aranjuez queda a 6 m, el CDI Cervantes 1 a 7 m y el Hogar Infantil Florida Blanca a 61 m. El CISCO Bosques del Norte queda a 3 m entre el ICBF y OSM.
6. Barrio y comuna salen de Nominatim inverso sobre la coordenada final. Solo los acepto si el nombre existe en `datos/semilla/barrios.csv`; si no, la celda va vacía.
7. Validé los archivos con un script corto: cabecera exacta, ids únicos, coordenadas dentro de la caja de Manizales, `critico` en {0,1}, barrios y comunas presentes en `barrios.csv` y una fila de fuente por cada fila de datos. Después hice la carga de prueba de la sección 1.
8. [Cálculo] Medí la distancia de cada coordenada al nodo más cercano del grafo vial del equipo (`despliegue/grafo/manizales_region.graphml`, solo lectura). La mediana es 29 m y el Banco de Alimentos queda a 0 m, porque su coordenada es un nodo de OSM. Cuatro puntos quedan a más de 200 m: la caseta de Mina Rica (494 m), la de El Guineo (438 m), el Hospital Geriátrico San Isidro (212 m) y la caseta de Cuchilla del Salado (211 m). [Supuesto] En esas veredas el último tramo puede requerir moto o ir a pie.

Los scripts de trabajo (`construir.py`, `validar.py` y la caché de Nominatim) quedaron fuera del repositorio, en `trabajo/agente-1/`. El coordinador decide si los sube.

## 5. Qué significa `verificado`

Esta sección define los dos valores de la columna.

- `si`: el nombre, el tipo y la coordenada salen de una fuente consultada hoy. La coordenada es de OSM con nombre y etiqueta coincidentes, o es del ICBF y pasó el contraste del paso 5.
- `parcial`: la coordenada tiene fuente, pero hay una duda declarada en `coordenada_de`. Las dudas son de cinco clases: ubicación aproximada, sede confirmada solo en OSM, nombre distinto entre fuentes, uso como albergue solo en 2017 o coincidencia solo por nombre.

## 6. Supuestos y decisiones

Esta sección lista lo que decidí y por qué, para que una persona lo pueda revisar.

- [Supuesto] Excluí los hogares comunitarios del ICBF (HCB y HCBF). Funcionan en la casa de la madre comunitaria, así que su coordenada señala una vivienda. Eso choca con la regla de no publicar direcciones de viviendas.
- [Supuesto] Excluí las unidades familiares del ICBF (EIH) que no dicen dónde se reúnen. Solo usé las que se reúnen en un salón comunal, un CISCO, una casa de la cultura o un centro día.
- Descarté coordenadas del ICBF que no pasaron el contraste. La del CISCO La Enea cae en el aeropuerto La Nubia, así que usé la de OSM. Las de la sede comunal de La Sultana, el CISCO Betania y el salón de la junta de la Calle 48H caen en otra calle. La de la junta de El Arenillo cae sobre la vía Panamericana. La de la caseta de La Garrucha queda a 914 m del caserío. La de la casa de la cultura de Bosques del Norte comparte dirección con el CISCO y queda a unos 340 m de él.
- [Supuesto] El albergue «junto al Coliseo Menor» usa la coordenada del coliseo, porque la fuente no nombra el edificio. Por eso ese punto y el acopio 2 tienen la misma coordenada.
- Los hospitales son críticos porque ABACO dio prioridad a «albergues oficiales, hospitales y familias autoalbergadas» ([Noticias RCN, 10 ago 2026](https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906)).
- Los tres colegios de 2017 van con `critico=0`. Son un precedente y no un albergue activo. Además, Asocapitales reportó 24 colegios públicos de Manizales con daño crítico al 13 de agosto ([informe n.º 22](https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-22.pdf)), y no sé si estos tres están entre ellos.
- En las veredas, la coordenada del ICBF queda entre 24 y 628 m del nodo del caserío en OSM. Puede marcar el caserío y no la caseta exacta.
- No crucé los puntos con el daño de cada edificio tras el sismo. No encontré una lista pública de edificios dañados con nombre.
- Dos barrios que devuelve OSM no están en `barrios.csv` (Villapilar II y la Zona Industrial El Campín). Por eso el Hospital Geriátrico San Isidro va sin barrio.

## 7. Puntos críticos por comuna

Esta tabla cuenta los puntos de `puntos.csv` por comuna, según la columna `comuna`.

| Comuna | Críticos | De qué tipo | No críticos |
|---|---|---|---|
| Atardeceres | 4 | 2 hogar infantil, 1 hospital, 1 hospital geriátrico | 0 |
| Ciudadela del Norte | 3 | 2 CDI, 1 centro de salud | 1 |
| Cumanday | 4 | 4 CDI | 0 |
| Ecoturística Cerro de Oro | 2 | 2 CDI | 0 |
| La Estación | 3 | 2 hospital, 1 hogar infantil | 0 |
| La Fuente | 2 | 1 centro de salud, 1 CDI | 2 |
| La Macarena | 3 | 3 CDI | 0 |
| Nuevo Horizonte | 4 | 3 CDI, 1 centro día | 1 |
| Palogrande | 2 | 2 albergue | 1 |
| San José | 2 | 1 centro de salud, 1 CDI | 1 |
| Tesorito | 2 | 1 centro de salud, 1 hogar infantil | 1 |
| Universitaria | 4 | 3 CDI, 1 hogar infantil | 1 |
| Rural (sin comuna) | 0 | | 7 |
| **Total** | **35** | | **15** |

Todas las comunas urbanas tienen al menos dos puntos críticos. En cambio, solo 5 de las 12 tienen una sede comunitaria (CISCO o casa de la cultura): Ciudadela del Norte, La Fuente, Nuevo Horizonte, Tesorito y Universitaria. Palogrande y San José tienen un colegio y no una sede comunitaria. Atardeceres, Cumanday, Ecoturística Cerro de Oro, La Estación y La Macarena no tienen ninguno de los dos.

## 8. Sitios sin coordenada

Esta sección lista sitios con fuente que no entraron al CSV porque no encontré su ubicación con fuente.

| Sitio | Tipo | Qué se sabe | Fuente | Qué falta |
|---|---|---|---|---|
| Albergue de Aranjuez | Albergue del sismo | La Alcaldía ofreció servicio de albergue en Aranjuez el 10 de agosto. Asocapitales reportó el 11 de agosto que la ciudad estaba habilitando 3 albergues. En los deslizamientos de 2017 también hubo un albergue oficial llamado Aranjuez. | [RCN Radio](https://newsroom.rcnradio.com/colombia/recomendaciones-para-ciudadanos-de-manizales-tras-el-terremoto-de-7-4-donde-acudir-por-ayuda-y-que-hacer-ante-replicas); [Asocapitales n.º 14](https://www.asocapitales.co/sites/default/files/2026-08/informe-no.14-4pm-asocapitales.pdf); [La FM, 2017](https://www.lafm.com.co/colombia/habilitan-coliseo-menor-manizales-albergue-damnificados) | El edificio. En OSM existe el Polideportivo Aranjuez (way 115721063), pero ninguna fuente lo nombra como albergue. |
| Albergue sin nombre | Albergue del sismo | Unas 200 personas el 15 de agosto. Puede ser uno de los ya listados. | [Noticias RCN](https://www.noticiasrcn.com/colombia/artesano-sobrevivio-al-terremoto-y-ahora-reconstruye-su-vida-desde-un-albergue-en-manizales-1050760) | Nombre y lugar. |
| Fundación El Edén del Abuelo | Hogar de adultos mayores | Más de 50 residentes. Daño de cerca del 70 % del edificio; los residentes durmieron en carpas en una zona declarada segura. | [Noticias RCN, 15 ago](https://www.noticiasrcn.com/colombia/fundacion-de-abuelitos-en-manizales-quedo-70-afectada-por-el-terremoto-1050776); [Minuto60, 14 ago](https://www.minuto60.com/colombia/terremoto-colombia-fue-un-momento-muy-duro-relato-una-fundacion/13529) | Dirección. No sé si es la misma «El Edén» de la Sociedad Evangélica que lista la Alcaldía. |
| 9 Centros Día | Adulto mayor | Bengala, Bosques del Norte, La Cuchilla del Salado, La Linda, La Sultana, La Cumbre, Las Colinas, San Jorge y Sinaí. | [Secretaría de Desarrollo Social](https://manizales.gov.co/wp-content/uploads/2025/08/GRUPOS-DE-INTERES.pdf) | Dirección de cada uno. Solo se conoce el barrio. |
| Centros Vida | Adulto mayor | Urbanos: La Aurora y La Isla (comuna La Fuente). Rurales: Alto Bonito, Arenillo, Java, Km 41, La Cuchilla, Lisboa y Pava. | Igual que la fila anterior | Dirección. Las veredas La Aurora y Alto Bonito tienen salón en el CSV, pero no sé si el Centro Vida funciona ahí. |
| 5 centros de bienestar con convenio | Ancianato | Sociedad Evangélica de Acción Social de Manizales (El Edén), Fundación Geriátrica Guadalupe, Corporación Hogar Gerontológico Nuevo Despertar, Fundación Hogar San Francisco de Asís y Asoviejos. | Igual que la fila anterior | Dirección. Ninguno está en OSM. |
| Comedores comunitarios | Comedor | No encontré ninguna fuente con comedores comunitarios de Manizales. | | Lista y direcciones. |
| Salones comunales urbanos | Salón comunal | La Alcaldía cuenta 204 juntas de acción comunal, 131 de ellas en barrios urbanos, sin nombres ni direcciones. Nominatim no devolvió ningún salón comunal ni centro comunitario en Manizales. | [Consolidado JAC/JAL](https://manizales.gov.co/wp-content/uploads/2025/08/CONSOLIDADO-JUNTAS-ACCION-COMUNAL-Y-ADMINISTRADORAS-LOCALES-JAC-JAL.pdf) (citado en `05_datos_abiertos_y_aliados.md`; no verificado hoy) | Direcciones por comuna. |
| Pastoral Social Cáritas Arquidiocesana Manizales | Posible aliado | Sede en la Calle 45 No. 24 B 50. No hay fuente de que haya sido acopio en 2026. | [Directorio COPOLAD](https://fase2.copolad.eu/c/directorio-de-centros-y-servicios/ficha/395) | Su papel tras el sismo. |

Los puntos de censo de Milán, Chipre, la avenida Santander y el Centro ([Blu Radio, 13 ago](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10)) no entraron porque eran puntos de registro y no de entrega.

## 9. Fuentes que no sirvieron o no respondieron

Esta sección deja constancia de lo que probé y descarté.

- Directorio de sedes educativas del MEN en datos.gov.co (x5ay-984n). Trae coordenadas con dos decimales, es decir, con un error cercano a 1 km, y su último año es 2019. No sirve para ubicar.
- Una hoja de Google que aparecía con la dirección «27A-85» no se pudo abrir. Tampoco abrieron la nota de Cambio sobre centros de acopio ni la de Diario del Sur sobre subsidios.
- Según el encargo, Overpass no responde desde la terminal, así que no lo usé y no pude listar todos los objetos de OSM por etiqueta. Nominatim no encontró ningún `amenity=community_centre` en la caja de Manizales.
- El cupo compartido de búsquedas web se agotó durante la sesión. La última búsqueda pendiente era sobre comedores comunitarios.

## 10. Lo que solo una persona puede conseguir

Esta sección dice a quién llamar y qué preguntarle.

- **Banco de Alimentos de Manizales (Arquidiócesis).** ¿La bodega sigue en la Calle 49 # 27A-85? ¿Tiene cuarto frío y de qué capacidad? ¿A qué puntos entregó tras el sismo y con cuántos vehículos?
- **Unidad de Gestión del Riesgo de Manizales.** ¿Cuál fue el albergue de Aranjuez? ¿Cuántas personas hubo en cada albergue por fecha y cuáles siguen abiertos?
- **Secretaría de Desarrollo Social de la Alcaldía.** ¿Cuáles son las direcciones de los 9 Centros Día, los Centros Vida y los centros de bienestar con convenio? ¿Hay comedores comunitarios activos? ¿Dónde queda El Edén del Abuelo?
- **ICBF, Centro Zonal Manizales 1.** ¿Qué CDI y hogares infantiles cerraron o se dañaron con el sismo?
- **Oficina de Acción Comunal de la Alcaldía.** ¿Dónde queda el salón comunal de cada barrio, al menos uno por comuna?

## Anexo. Por qué es crítico cada punto

Esta tabla da la razón de cada punto con `critico=1`. Los salones comunales, los CISCO, las casas de la cultura y los colegios de 2017 van con `critico=0`.

| id | Punto | Comuna | Por qué es crítico |
|---|---|---|---|
| 1 | Albergue Coliseo Mayor | Palogrande | Albergue activo tras el sismo: las familias alojadas dependen de raciones diarias. |
| 2 | Albergue junto al Coliseo Menor | Palogrande | Albergue activo tras el sismo: las familias alojadas dependen de raciones diarias. |
| 3 | ESE Hospital Departamental Universitario Santa Sofía | Atardeceres | Hospital: ABACO puso a los hospitales entre sus tres prioridades de entrega tras el sismo. |
| 4 | Hospital de Caldas | La Estación | Hospital: ABACO puso a los hospitales entre sus tres prioridades de entrega tras el sismo. |
| 5 | Hospital Infantil Universitario Rafael Henao Toro | La Estación | Hospital: ABACO puso a los hospitales entre sus tres prioridades de entrega tras el sismo. |
| 6 | Hospital Geriátrico San Isidro | Atardeceres | Hospital geriátrico que la Alcaldía lista como centro de bienestar del adulto mayor con convenio: residentes dependientes. |
| 7 | Assbasalud Clínica San Cayetano | Ciudadela del Norte | Centro de salud de la red pública municipal (Assbasalud): pacientes y personal no pueden salir a buscar comida. |
| 8 | Assbasalud La Enea | Tesorito | Centro de salud de la red pública municipal (Assbasalud): pacientes y personal no pueden salir a buscar comida. |
| 9 | Assbasalud Centro Piloto | San José | Centro de salud de la red pública municipal (Assbasalud): pacientes y personal no pueden salir a buscar comida. |
| 10 | Assbasalud Cervantes (Calle 36A) | La Fuente | Centro de salud de la red pública municipal (Assbasalud): pacientes y personal no pueden salir a buscar comida. |
| 11 | CDI Angelitos sede 1 | Nuevo Horizonte | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 12 | CDI Aranjuez | Universitaria | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 13 | CDI Campoamor | Cumanday | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 14 | CDI Cervantes 1 | Cumanday | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 15 | CDI El Caribe | Ciudadela del Norte | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 16 | CDI El Carmen 1 | La Macarena | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 17 | CDI Jesús de la Buena Esperanza | La Macarena | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 18 | CDI La Isla | La Fuente | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 19 | CDI Las Palomas | Ecoturística Cerro de Oro | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 20 | CDI La Toscana | Ecoturística Cerro de Oro | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 21 | CDI Malhabar | Universitaria | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 22 | CDI Mariela Quintero | Universitaria | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 23 | CDI Mundo de Colores | Cumanday | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 24 | CDI Pelusa | San José | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 25 | CDI Pulgarcito | La Macarena | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 26 | CDI San José | Cumanday | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 27 | CDI San Sebastián | Ciudadela del Norte | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 28 | CDI Solferino | Nuevo Horizonte | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 29 | CDI Villahermosa | Nuevo Horizonte | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 30 | Hogar Infantil Bellavista | Atardeceres | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 31 | Hogar Infantil Florida Blanca | Tesorito | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 32 | Hogar Infantil Los Ositos | Universitaria | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 33 | Hogar Infantil Los Ositos sede Versalles | La Estación | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 34 | Hogar Infantil Santa Bernardita | Atardeceres | Unidad de primera infancia del ICBF: atiende a diario a niños pequeños, población que no puede esperar la ración. |
| 35 | Centro Día Solferino (adulto mayor) | Nuevo Horizonte | Centro Día del adulto mayor: atiende personas mayores, grupo de riesgo alto. |

