# Verificar las cifras del pitch · Samuel, sábado en la mañana

Esta lista trae las 15 cifras que más pesan en el pitch, en el orden en que conviene abrirlas. Las cinco primeras son las que ya sabemos dudosas. Después van las del guion nuevo (`pitch/GUION.md` en la rama `pitch-noche`), en el orden en que se dicen, y al final las de la ficha. Toma unos 45 minutos.

**Por qué importa.** La regla del equipo es que toda cifra del pitch tenga una fuente abierta por una persona. Una máquina ya revisó casi todas la noche del viernes, y lo que encontró va en cada ficha como «Lo que vio la máquina». Eso no cuenta como verificación, porque usted es la primera persona que las abre. Según el guion nuevo, la cifra con asterisco que nadie haya abierto a la 1:00 p. m. sale del pitch. Conviene terminar antes de la mentoría 2, a las 10:30 a. m.

**Cómo marcar.** En cada cifra, marque una casilla y anote la hora.

- Si coincide, en `docs/FUENTES.md` cambie su estado por «Verificada por Samuel, <hora>».
- Si no coincide, copie lo que dice la fuente y avise en `torre/CANAL.md`. No cambie la cifra en la ficha ni en el guion, porque eso lo hacen Fable o Carlos.
- Si la página no abre, anote el error y siga con la siguiente.

Si la rama `fuentes-noche` todavía no está en `main`, marque las casillas en este archivo y Fable pasa los resultados a `docs/FUENTES.md`.

## Las cinco dudosas

### 1. 404.587 kg en acopio y 41.163 kg entregados al sexto día

- **Lo que decimos.** «Al sexto día, la red tenía 404.587 kg en acopio y había entregado 41.163 kg en todo el país.» Está en la FICHA, la ficha corta, la ficha de la mentoría y el informe corto. El guion abre con ella, en toneladas truncadas (404 y 41).
- **Abrir.** https://www.portafolio.co/economia/regiones/flypass-paga-peajes-de-57-camiones-para-acelerar-la-entrega-de-ayudas-tras-el-terremoto-en-colombia-500521
- **Buscar.** «41.163 kilos», «404.587 kilos» y «157.164 kilos». La fecha de la nota. Si dice que son cifras de toda la red de bancos.
- **Por qué es dudosa.** La comparación deja fuera los 157.164 kg en tránsito. La nota no dice «sexto día», que sale de contar los días entre el sismo y la publicación (16 de agosto). Tampoco dice de forma explícita «en todo el país».
- **Lo que vio la máquina.** Las tres cifras, atribuidas a «los Bancos de Alimentos», más 460.317 kg anunciados. Publicada el 16 de agosto a las 4:20 p. m.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 2. Cuántas personas tiene una familia (1,8, 2,9 o 4)

- **Lo que decimos.** La FICHA usa 2,9 personas por hogar (DANE, censo de 2018). El bot y la semilla usan 4 (`entrada/raciones.py`, línea 15, sin fuente). El registro de damnificados del sismo da 1,8.
- **Abrir.** El Decreto 1261: https://normograma.dian.gov.co/dian/compilacion/docs/decreto_1261_2026.htm · La presentación del DANE: https://www.dane.gov.co/files/censo2018/informacion-tecnica/presentaciones-territorio/190801-CNPV-presentacion-Caldas-Manizales.pdf
- **Buscar.** En el decreto, «147.464 familias y 262.154 personas damnificadas». En el DANE, la fila de Manizales en la columna «Personas por hogar (promedio)».
- **Por qué es dudosa.** Tres fuentes dan tres tamaños, y los kilos de un pedido dependen de las personas.
- **Lo que vio la máquina.** El decreto dice lo que citamos, y 262.154 ÷ 147.464 da 1,78. El DANE da 2,9 en 2018 y 3,5 en 2005, con 136.806 hogares y 400.436 personas censadas. `docs/datos/demanda.md` usa 395.818 personas.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 3. La patente 37476 y la cota de 1,2

- **Lo que decimos.** «El único respaldo es una cota inferior de 1,2, en gulupa a 8 °C, derivada de las figuras 1 y 2 de la solicitud de la patente (cálculo nuestro).» Está en la FICHA, la ficha corta y la ficha de la mentoría. El guion viejo dice que «vigente» solo se dice si Fernando Bernal confirma la anualidad 2026.
- **Abrir.** SIPI, en https://sipi.sic.gov.co, con el expediente 14245775. El PDF de la solicitud CO 14-245775, que Carlos adjuntó en el proyecto de Claude, folio 18.
- **Buscar.** En SIPI, el certificado 37476, la Universidad Nacional como titular, la concesión del 6 de julio de 2020, el vencimiento del 6 de noviembre de 2034 y el estado de la anualidad 2026. En el folio 18, la figura 1 muestra que sin empaque el pico de etileno llega en la semana 5, y que con 2 % de escualeno no hay pico hasta la semana 6. La figura 2 muestra lo mismo con diludina.
- **Por qué es dudosa.** El 1,2 no está escrito en la patente. Es 6 ÷ 5, calculado por nosotros con el pico de etileno como indicador del fin de la vida útil. Vale solo para gulupa a 8 °C, y es el texto de 2014, no el concedido.
- **Lo que vio la máquina.** Nada. SIPI no responde a los lectores automáticos, y el PDF no está en el repositorio.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 4. Viviendas colapsadas en Manizales, con dos cortes

- **Lo que decimos.** El informe largo da 1.449 viviendas colapsadas con corte al 13 de agosto y 2.707 con corte al 15. La investigación 02 pone las 2.707 el 13. No está en la ficha ni en el guion, pero puede salir en una pregunta del jurado.
- **Abrir.** https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-22.pdf · https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-24.pdf · https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-27.pdf
- **Buscar.** En cada uno, la sección de Manizales y la línea «Corte».
- **Lo que vio la máquina.** El n.º 22, con corte a las 10:00 a. m. del 13 de agosto, da 1.449 colapsadas y 1.970 averiadas. El n.º 24, con corte a las 9:00 p. m. del 13, da 2.707 y 3.993. El n.º 27, con corte a las 10:00 a. m. del 15, repite 2.707 y 3.993.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 5. Velocidades, 22,6 km/h medidos contra 39 a 55 km/h del modelo

- **Lo que decimos.** «El modelo le da al campero 39,0 km/h de media en vías primarias, y un bus medido con GPS en Manizales promedió 22,6 km/h (tesis de maestría de la UNAL Manizales, 2019).» Está en la FICHA, la ficha corta, el piloto y el informe corto. En vías troncales el modelo da 54,7 km/h.
- **Abrir.** https://bffrepositorio.unal.edu.co/server/api/core/bitstreams/46d4a283-1bb5-4027-9a7d-6b0831aec2d8/content
- **Buscar.** En la página 50, sección 5.3, «la del bus a combustión es de 22.6 km/h». En la página 48, la columna «Principal» de la tabla 14 debe dar 23,8, 21,8, 23,4 y 24,2. En la portada, la autora y el director, porque la FICHA dice que están «por confirmar».
- **Por qué es dudosa.** Los 39,0 y 54,7 km/h del modelo los midió un agente sobre el grafo, con un script que quedó fuera del repositorio. Por esta diferencia se repite la simulación esta noche, y sus números van como [SIM].
- **Lo que vio la máquina.** Los 22,6 km/h en la página 50 y la tabla 14 en la página 48, con esos valores. La autora es Daniela Ocampo González y el director, Diego Alexander Escobar García.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

## Las cifras del guion

### 6. Manizales, uno de los principales puntos de acopio

- **Lo que decimos.** El guion nuevo abre con «Manizales fue uno de los principales puntos de acopio de la red de bancos de alimentos». La FICHA dice lo mismo. En cambio, `docs/PROBLEMA.md` dice «su principal punto de acopio para el Eje Cafetero».
- **Abrir.** Noticias RCN, 10 de agosto: https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906 · La página de ABACO: https://abaco.org.co/fondoparaemergencias/
- **Buscar.** En RCN, «uno de los principales puntos de acopio». En ABACO, la tarjeta de Manizales.
- **Lo que vio la máquina.** RCN dice «uno de los principales». ABACO dice «Sismo, agosto de 2026: principal punto de acopio». Ninguno de los dos pasajes dice «para el Eje Cafetero».

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 7. El registro #767 de INVÍAS, con los 87 registros, el 21 de octubre y las 9 h 46 min

- **Lo que decimos.** «La salida a Letras suma 87 registros de cierre por derrumbe o deslizamiento desde 2017» (guion, bloque 2). «El 21 de octubre, la autopista del Café quedó a un carril y solo pasaban livianos» (guion, bloque 5). «El registro oficial apareció 9 horas y 46 minutos después del sismo» (guion, versión de cinco minutos).
- **Abrir.** La consulta del cierre del sismo: https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0/query?where=objectid%20IN%20%285074664%2C5073065%29&outFields=*&returnGeometry=false&f=json · La del 21 de octubre: https://hermes2.invias.gov.co/server/rest/services/N_767/Consulta767/FeatureServer/0/query?where=objectid%20IN%20%285166664%2C5168264%29&outFields=*&returnGeometry=false&f=json · Para los 87, el archivo `datos_publicos/cierres_historicos.csv`, filtrado por `via_nombre` igual a «salida a Letras».
- **Buscar.** En la primera consulta, el registro 5074664. Su `creationdate` es 1786400416000, en milisegundos desde 1970 y en UTC. En un convertidor de tiempo Unix eso da el 10 de agosto de 2026 a las 10:20 p. m. UTC, que son las 5:20 p. m. en Colombia, 9 h 46 min después de las 7:34 a. m. En la segunda consulta, «solo paso a vehículos livianos». En el CSV, abra el enlace de tres filas al azar.
- **Por qué hay que mirar.** Cuatro de las 87 filas son del sismo, así que sin el sismo quedan 83. Son registros y no eventos, porque un derrumbe puede tener varios. El registro del 21 de octubre nombra la vía «Puente La Libertad – Tres Puertas», en Risaralda, y llamarla autopista del Café es lectura nuestra.
- **Lo que vio la máquina.** Inicio a la 1:00 p. m. y creación a las 5:20 p. m. del 10 de agosto. El 21 de octubre, paso a un carril y solo livianos, con ruta alterna por La Siria. 87 filas en el CSV, 4 de ellas del sismo.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 8. El registro de damnificados cerró el 4 de septiembre

- **Lo que decimos.** «El registro de damnificados cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas» (guion, bloque 4, y FICHA).
- **Abrir.** https://www.vanguardia.com/colombia/2026/10/05/procuraduria-pide-a-la-ungrd-agilizar-ayudas-para-damnificados-por-el-terremoto/
- **Buscar.** «cerrado el pasado 4 de septiembre» y «zonas rurales dispersas».
- **Por qué hay que mirar.** La nota habla de auxilios económicos y no de comida.
- **Lo que vio la máquina.** Coincide. La nota dice «zonas rurales dispersas y territorios étnicos», y que la Procuraduría pidió una apertura extraordinaria y condicionada.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 9. El A25 del IDEA, la capacidad UNAL principal

- **Lo que decimos.** «La UGR lo adoptó a partir de la tesis de Terlien (1996), que asoció unos 200 mm en 25 días con alta probabilidad de deslizamientos.» «La alerta es amarilla desde 200 mm, naranja desde 300 mm y roja desde 400 mm, y el reporte de 2020 cubre 14 estaciones.» «El 16 de febrero de 2026 Manizales declaró alerta amarilla con el mismo umbral de 200 mm.» Está en la FICHA y la ficha corta, y el guion la nombra en el bloque 7.
- **Abrir.** El boletín 145: https://idea.manizales.unal.edu.co/publicaciones/boletines_ambientales/boletin145.pdf · El reporte de 2020: https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf · Blu Radio: https://www.bluradio.com/nacion/manizales-entra-en-alerta-amarilla-por-lluvias-que-superan-niveles-historicos-rg10
- **Buscar.** En el boletín, «Terlien», «200 mm» y «UGR». En el reporte, la tabla de alertas y la lista de estaciones, para contarlas. En Blu Radio, «200 milímetros acumulados en un periodo inferior a 25 días».
- **Por qué hay que mirar.** La máquina contó 13 estaciones con nombre más el promedio de Manizales, no 14. Ninguna nota de febrero nombra al IDEA, así que la coincidencia del umbral es lectura nuestra.
- **Lo que vio la máquina.** Los umbrales, Terlien y la adopción por la UGR coinciden. Blu Radio dice que la declaró el Consejo Municipal de Gestión del Riesgo y que La Palma llegó a 300 mm.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

## Las cifras de la versión de cinco minutos y de la ficha

### 10. En Manizales la comida se repartió por listas

- **Lo que decimos.** «Para recibir un mercado había que llevar el formato azul de Bomberos, y la Cruz Roja Seccional Caldas entregó los kits por turnos» (guion de cinco minutos). La FICHA añade que el formato se entrega «después de revisar la vivienda» y que la Cruz Roja «fue el operador logístico».
- **Abrir.** Alcaldía, 15 de agosto: https://centrodeinformacion.manizales.gov.co/carpas-de-atencion-cable-aereo-y-linea-de-atencion/ · Alcaldía, 31 de agosto: https://centrodeinformacion.manizales.gov.co/alcaldia-ugr-y-cruz-roja-intensifican-entrega-de-auxilios-y-alimentos-a-familias-damnificadas-por-el-sismo/
- **Buscar.** En la del 15, «formato azul entregado por Bomberos». En la del 31, «operador logístico», «turnos» y «kit de alimentos», y si nombra a la Cruz Roja como operador.
- **Por qué hay que mirar.** La máquina no encontró «después de revisar la vivienda» en la nota del 15, porque ese detalle sale de La Patria (13 de agosto). En la del 31, el director de la UGR dice «nuestro operador logístico» sin nombrarlo, y la entrega fue en la sede de la Cruz Roja.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 11. La calamidad pública sigue hasta el 9 de agosto de 2027

- **Lo que decimos.** «El piloto cabe en la calamidad pública de Manizales, vigente hasta el 9 de agosto de 2027» (guion de cinco minutos, FICHA y ficha corta).
- **Abrir.** https://centrodeinformacion.manizales.gov.co/manizales-presento-informe-al-concejo-de-las-acciones-adelantadas-tras-sismo-del-10-de-agosto/
- **Buscar.** «vigente hasta el 9 de agosto de 2027» y «plan de acción específico».
- **Lo que vio la máquina.** Coincide. Lo presentó al Concejo Diego Armando Rivera Gutiérrez, director de la UGR, y la nota es del 16 de octubre.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 12. 8.240 damnificados en Manizales

- **Lo que decimos.** «En Manizales, el censo que cerró el 24 de agosto registró 8.240 personas damnificadas y 3.080 predios evacuados» (FICHA, ficha corta, problema e informe corto).
- **Abrir.** https://www.noticiasrcn.com/colombia/manizales-prepara-la-demolicion-de-7-edificios-que-presentan-danos-estructurales-1053593
- **Buscar.** «3.080 predios evacuados para 8.240 personas damnificadas» y «24 de agosto».
- **Lo que vio la máquina.** Coincide. La nota dice «según las cifras oficiales» y no le atribuye el censo al alcalde. Del Coliseo Mayor dice que es «uno de los principales albergues temporales».

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 13. Magnitud, hora y epicentro del sismo

- **Lo que decimos.** «El sismo del 10 de agosto de 2026 tuvo magnitud 7,4 y ocurrió a las 7:34 a. m., con epicentro en San José del Palmar, Chocó» (FICHA, problema e informe corto). `docs/PROBLEMA.md` suma «más de 262.000 damnificados, 314 personas fallecidas y 449 vías afectadas».
- **Abrir.** https://normograma.dian.gov.co/dian/compilacion/docs/decreto_1261_2026.htm
- **Buscar.** «magnitud 7,4», «7:34», «San José del Palmar», «314 personas fallecidas» y «449 vías». La fecha del decreto.
- **Lo que vio la máquina.** Todo coincide, con el decreto fechado el 19 de agosto. Da dos profundidades, 103,4 km y unos 94 km.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 14. Las dos salidas cerradas el 12 de agosto

- **Lo que decimos.** «El 12 de agosto seguían cerradas por completo la vía Pereira–Chinchiná, entre los kilómetros 22 y 24, y la vía Manizales–Fresno en el Alto de Letras, entre los kilómetros 36 y 40» (FICHA, ficha corta, problema, piloto e informe corto). El guion de cinco minutos dice que la Policía anunció el cierre de Pereira–Chinchiná al mediodía.
- **Abrir.** Semana: https://www.semana.com/nacion/articulo/actualizacion-de-las-vias-que-siguen-cerradas-tras-el-terremoto-en-colombia/202602/ · Minuto30, para el mediodía: https://www.minuto30.com/vias-cerradas-por-sismo-colombia/1715765/
- **Buscar.** En Semana, «Pereira-Chinchiná, entre los kilómetros 22 y 24», «Manizales-Fresno» con sus kilómetros, la hora y quién reporta. En Minuto30, la hora del reporte de la Policía (12:03 p. m., según `docs/datos/vias_y_riesgo.md`).
- **Por qué hay que mirar.** Semana no nombra el Alto de Letras, y ubica el cierre en Herveo (Tolima), entre los km 36+800 y 40+300. Además, la vía Pereira–Chinchiná une a Chinchiná con Pereira, y llamarla una salida de Manizales es lectura nuestra.
- **Lo que vio la máquina.** En Semana, los dos cierres y la fuente, que es la Dirección de Tránsito y Transporte de la Policía, con hora de las 9:24 a. m. Minuto30 se publicó a las 12:03 p. m. del 10 de agosto, con los dos cierres y el «sector Alto de Letras», y atribuye el reporte a la Policía Nacional.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

### 15. 204 juntas de acción comunal

- **Lo que decimos.** «Las 204 juntas de acción comunal de Manizales, 131 de barrios y 73 de veredas» (FICHA, ficha corta, informe corto y territorios). Son quienes piden.
- **Abrir.** https://manizales.gov.co/wp-content/uploads/2025/08/CONSOLIDADO-JUNTAS-ACCION-COMUNAL-Y-ADMINISTRADORAS-LOCALES-JAC-JAL.pdf
- **Buscar.** «204 Juntas de Acción Comunal», «131 barrios», «73 veredas» y «12 Comunas y 7 Corregimientos».
- **Lo que vio la máquina.** Coincide. El documento no trae fecha, y la ruta del archivo dice agosto de 2025.

- [ ] Coincide
- [ ] No coincide. La fuente dice:
- Hora y nota:

## Si sobra tiempo

Estas cifras están en la ficha y pesan menos en el pitch. Las ocho tienen su fila completa en `docs/FUENTES.md`.

| Cifra | Abrir | Buscar o fijarse en |
|---|---|---|
| Gerencias del FOREC y gobernanza territorial (guion de cinco minutos) | https://www.javerianacali.edu.co/sites/default/files/2026-09/Reconstruir%20desde%20el%20dia%CC%81logo%20social.pdf | «operaron con autonomía respecto a las autoridades locales». Cita a Cuervo Restrepo (2002) |
| 28 % de estaciones base sin servicio en Caldas | https://www.noticiasrcn.com/colombia/senal-movil-en-colombia-46-esta-afectada-1049064 | «28 %» y «3.403 ... de un total de 7.379». La recomendación de SMS es de la CRC; la de MinTIC está en https://www.mintic.gov.co/portal/715/w3-article-440280.html |
| 18.847 unidades de la Gobernación | https://escaldas.com/gobierno-de-caldas-ha-movilizado-esta-semana-al-menos-6-800-ayudas-humanitarias-ya-completa-mas-de-18-000-entregas-tras-el-sismo/ | Que las unidades suman tejas, frazadas y baldes, no solo comida |
| Más de 2.000 t para 9.470 familias en 36 municipios | https://www.portafolio.co/historias-portafolio/abaco-2-000-toneladas-de-ayuda-movilizadas-502977 | El titular dice «cerca de 2.000» y el texto, «más de 2.000» |
| 54.000 t de la red ABACO en 2025 | https://www.larepublica.co/responsabilidad-social/que-ocurre-con-los-alimentos-que-no-logran-vender-los-supermercados-de-colombia-4330123 | Si las 12.000 t compradas van aparte de las 42.000 rescatadas o dentro de ellas |
| 9,76 millones de toneladas al año (DNP, 2016) | https://dnp.gov.co/Prensa_/Noticias/Paginas/el-dnp-se-une-con-las-centrales-de-abastos-para-fortalecer-los-procesos-logisticos-y-la-reduccion-de-perdida-de-alimentos.aspx | «9,76 millones de toneladas» y «34 %» |
| SUMA «no recibe pedidos» | https://www.paho.org/es/temas/respuesta-emergencias-salud-desastres/sistema-lss | La página dice que registra «solicitudes de artículos necesarios» |
| El PMA «entregó efectivo» | https://www.telesurtv.net/colombia-onu-asistencia-100000-personas/ | La nota dice «prevé ampliar las transferencias de efectivo» |

## Lo que no va en esta lista

Las cifras medidas por el equipo, como los 3 de 3 críticos a tiempo de la demo o la hoja de ruta impresa sin internet, se verifican corriendo el código y no abriendo un enlace. Las ensaya quien opere la demo, con `docs/GUION_DEMO.md`. Los números de la simulación van como [SIM] hasta que llegue la corrida nueva, hacia las 6:00 a. m. Si `pitch/CIFRAS_PITCH.md` trae una cifra que no está aquí, ábrala también y anótela en `docs/FUENTES.md`.
