# Cuánta comida necesita cada zona de Manizales

Este documento estima la demanda de ayuda alimentaria por comuna de Manizales y para un albergue tipo. Reúne las fuentes públicas que encontramos, separa lo que dice cada fuente de lo que calculamos y de lo que suponemos, y propone un cambio a `entrada/raciones.py`. Consulta de todas las fuentes: 20 de noviembre de 2026. Los datos van en dos archivos: `datos_publicos/raciones.csv` y `datos_publicos/demanda_comunas.csv`. El cálculo se reproduce con el script `generar.py` del agente 2, guardado fuera del repositorio (`/home/claude/trabajo/agente-2/`).

Sobre la verificación. Un agente leyó cada fuente con una herramienta de lectura automática y pidió las cifras textuales dos veces en las tablas clave (ASIS 2023, ICBF, Logistics Cluster). Ninguna persona del equipo ha abierto aún los enlaces. Por la regla de `docs/PROBLEMA.md`, ninguna cifra va al pitch sin esa revisión humana.

Convenciones: **[F]** lo dice la fuente; **[C]** lo calculamos a partir de fuentes; **[S]** es un supuesto nuestro.

## 1. Resumen

- **No hay desglose público de damnificados por comuna ni por barrio.** La prensa y la Defensoría reproducen cifras de ciudad, puntos de censo y albergues de la Alcaldía, pero ninguna da la distribución por zona. **[F]** Fuentes en la sección 4.
- **No encontramos publicada la composición del kit de alimentos de la UNGRD.** El manual que la define existe, porque lo cita la Resolución UNGRD 0382 de 2025, pero no logramos abrirlo. **[F]**
- **Ración seca propuesta: 555 g por persona y día.** Sale de la tabla de raciones de ACNUR (cereal 450 g, leguminosas 60 g, aceite 25 g, azúcar 15 g, sal 5 g). La tabla pone esa cantidad de cereal junto a 2.100 kcal, el mínimo de Esfera. **[F]** + **[C]**
- **Una semana para una familia de Manizales pesa 11,3 kg.** Usamos 2,9 personas por hogar, el promedio del censo DANE 2018 para Manizales. El optimizador supone hoy 10 kg por familia, un 11 % menos. **[C]**
- **La «familia» cambia de tamaño según quién cuenta.** Son 1,8 personas en el registro nacional de damnificados del sismo, 2,9 en el censo de Manizales y 4 en la tabla del equipo. Conviene que la mesa pida personas y no familias, porque los kilos dependen de las personas. **[C]**
- **Si falla el acueducto, el agua pesa 5,4 veces lo que pesa la comida.** Los 8.240 damnificados censados necesitan 4,6 t diarias de ración seca y 24,7 t diarias de agua para beber y cocinar. **[C]**
- **Al albergue del Coliseo Mayor habían llegado cerca de 300 personas el 13 de agosto; el 25 de agosto quedaban 90.** Con 300 personas necesita 166,5 kg diarios de ración seca; con 90, 50 kg. **[F]** + **[C]**

## 2. Ración por persona y por familia

Esta sección responde cuánto pesa la comida que necesita una persona y una familia, y con qué fuente.

### 2.1 Qué dicen las fuentes

| Fuente | Qué dice | Enlace |
|---|---|---|
| ACNUR, norma de asistencia alimentaria de emergencia (25 jun 2025) | La necesidad básica es 2.100 kcal por persona y día, citando el Manual Esfera 2018. No da gramos por producto. | [emergency.unhcr.org](https://emergency.unhcr.org/es/print/pdf/node/504) |
| Logistics Cluster, tabla de raciones (g/persona/día) por agencia | Columna ACNUR: cereal 400 g (450 g), leguminosas 60 g, aceite 25 g; energía 1.930 kcal (2.100 kcal). Leemos los paréntesis como la versión de 2.100 kcal, con 450 g de cereal **[S]**. Azúcar 15 a 20 g y sal 5 g, sin columna clara. | [log.logcluster.org](https://log.logcluster.org/sites/default/files/pages/199/en/main-types-of-in-kind-commodities.pdf) |
| OPS/INCAP, seguridad alimentaria en emergencias (10 dic 2019) | Para la distribución inmediata a grupos de alto riesgo nutricional recomienda 3 a 4 kg de alimentos por persona para una semana. Prefiere raciones secas por familia para un periodo fijo, con una semana como ejemplo. | [paho.org](https://www.paho.org/es/emergencias-salud/seguridad-alimentaria-nutricional-situaciones-emergencia) |
| OPS, nota técnica 9 de agua en emergencias | Supervivencia (beber y cocinar alimentos): 2,5 a 3 L por persona y día. Total con higiene y cocina: 7,5 a 15 L. Cita las normas Esfera. | [paho.org](https://paho.org/sites/default/files/2019-12/Nota-tecnica-sobre-agua-saneamiento-higiene-09.pdf) |
| ICBF, minuta patrón de la Ración Familiar Para Preparar, v2 (16 ene 2026) | Ración mensual por familia: grano (maíz, arroz) 6 kg, harinas 2 kg, pasta 2 kg, tubérculos 3 kg, fruta 4 kg, verdura 3 kg, leche 12 L, 4 cubetas de 30 huevos de 60 g, leguminosas 4 kg, aceite 2 L, panela 1 lb, Bienestarina 2 bolsas de 900 g. No dice cuántas personas tiene la familia. Es un programa contra la desnutrición infantil, no de emergencia. | [icbf.gov.co](https://www.icbf.gov.co/system/files/procesos/A26.G36.PP%20Anexo%20minuta%20patr%C3%B3n%20modalidad%20de%20atenci%C3%B3n%20y%20prevenci%C3%B3n%20de%20la%20desnutrici%C3%B3n%20-%20RFPP%20_v2.pdf) |
| Cruz Roja, vía Infobae (14 ago 2026) | Tras el sismo pidió no donar alimentos perecederos. Recomendó granos, aceite, pasta, enlatados, frijol, lenteja, harina, panela y leche en polvo. | [infobae.com](https://www.infobae.com/colombia/2026/08/14/cruz-roja-aclaro-que-donaciones-necesitan-las-victimas-del-terremoto-y-que-no-kits-de-habitat/) |
| Resolución UNGRD 0382 de 2025 | Crea los Comedores Populares de Emergencia: hasta dos raciones diarias de comida caliente por 90 días para inscritos en el Registro Único de Damnificados. Los describe como complemento de los kits alimentarios y las canastas populares. Cita el Manual de Estandarización de Ayuda Humanitaria de la UNGRD. | [cancilleria.gov.co](https://cancilleria.gov.co/normograma/compilacion/docs/resolucion_ungrd_0382_2025.htm) |
| Alcaldía de Medellín, orden de compra 93437 (14 jul 2022) | Compra de kits alimentarios para hogares vulnerables. Al dividir cada cantidad entre las 314 cajas, cada caja trae 3 kg de arroz, 1 kg de frijol, 0,5 kg de lenteja, 1 L de aceite, 1 kg de panela, 1,5 kg de pasta, 0,5 kg de harina de maíz, 1,08 kg de leche en polvo, 4 latas de atún de 160 g, azúcar, café, chocolate, sal y harina de trigo. Son 12,2 kg de sólidos más el aceite **[C]**. No dice personas ni días. | [colombiacompra.gov.co](https://operaciones.colombiacompra.gov.co/tienda-virtual-del-estado-colombiano/ordenes-compra/93437/1) |
| Fundación Angelitos de Luz, vía Publimetro (11 sep 2026) | 8.000 kits de mercado; la nota cita entregas en Manizales. Cada kit trae 3,5 kg y casi dos tercios son cárnicos **[C]**. La nota da un total de «más de 12 toneladas»; con 3,5 kg por kit, 8.000 kits serían unas 28 t **[C]**. No dice personas ni días. | [publimetro.co](https://www.publimetro.co/noticias/2026/09/11/asi-avanza-la-ayuda-para-las-familias-afectadas-por-el-terremoto-destinan-3000-millones-de-pesos-y-entregan-miles-de-kits-de-alimentos/) |
| Repositorio UNGRD, recorte de prensa (8 feb 2019) | Unas 100 t de ayuda llegadas a Cúcuta se empacaron en bolsas para una familia de 5 personas durante 7 días. Por la fecha y el medio (Crónica Uno, de Venezuela), parece la ayuda para Venezuela de 2019 **[S]**. No es un estándar colombiano. | [repositorio.gestiondelriesgo.gov.co](https://repositorio.gestiondelriesgo.gov.co/handle/20.500.11762/33628) |

Los kits de Cali (agosto de 2026) y de Bogotá (2020) traen arroz, harina, panela, pasta, aceite, café, frijol, lenteja, atún, sal y azúcar, pero sus páginas no dan cantidades ([Cali](https://www.cali.gov.co/publicaciones/193748/alcaldia-de-cali-requiere-mantener-reserva-de-mercados-para-garantizar-la-atencion-humanitaria-durante-los-proximos-tres-meses/), [Bogotá](https://bogota.gov.co/mi-ciudad/integracion-social/como-son-las-ayudas-alimentarias-que-entrega-integracion-social)).

### 2.2 Ración propuesta

La ración base es seca, porque así la recomiendan la OPS y la Cruz Roja y porque los cortes de energía impidieron mantener la cadena de frío, según el director de ABACO ([La República, 18 ago 2026](https://www.larepublica.co/empresas/entrevista-con-juan-carlos-buitrago-director-ejecutivo-de-abaco-4458863)). Los gramos por persona vienen de la columna ACNUR. Usamos 450 g de cereal porque la tabla pone ese valor junto a 2.100 kcal. El cereal se reparte 6:2:2 entre grano, harinas y pasta, la misma proporción de la ración del ICBF (6, 2 y 2 kg al mes). Las leguminosas se reparten mitad frijol y mitad lenteja **[S]**, porque el ICBF las agrupa.

| Producto | g/persona/día | kg/familia/día (2,9 personas) | kg por kit de 7 días | Origen |
|---|---:|---:|---:|---|
| arroz | 270 | 0,783 | 5,48 | [F] ACNUR + [C] reparto ICBF |
| harina de maíz | 90 | 0,261 | 1,83 | [F] ACNUR + [C] reparto ICBF |
| pasta (nuevo) | 90 | 0,261 | 1,83 | [F] ACNUR + [C] reparto ICBF |
| frijol | 30 | 0,087 | 0,61 | [F] ACNUR + [S] mitad de leguminosas |
| lenteja | 30 | 0,087 | 0,61 | [F] ACNUR + [S] mitad de leguminosas |
| aceite | 25 | 0,073 | 0,51 | [F] ACNUR |
| panela | 15 | 0,044 | 0,30 | [F] tabla: azúcar 15 a 20 g; tomamos 15 |
| sal (nuevo) | 5 | 0,015 | 0,10 | [F] tabla |
| **Total seco** | **555** | **1,610** | **11,27** | [C] |
| agua | 3 L | 8,7 L | 60,9 L | [F] OPS + [S] solo si falla el acueducto |

Chequeo cruzado **[C]**. La ración da 3,9 kg por persona y semana, dentro del rango de 3 a 4 kg de OPS/INCAP. El kit de Medellín 2022 pesa 12,2 kg de sólidos, cerca de los 11,3 kg de nuestra semana familiar.

Los frescos no tienen ración de emergencia con fuente. Para fruta, verdura, huevos, leche y papa dejamos como referencia la ración mensual del ICBF dividida por 30: fruta 0,133 kg, verdura 0,100 kg, huevos 0,240 kg, leche 0,4 L y papa 0,100 kg por familia y día. El ICBF no dice cuántas personas tiene esa familia, así que estos valores no son comparables con la ración seca. **Pollo y pan no tienen ninguna fuente.** Atún, azúcar, café y chocolate aparecen en kits colombianos, pero sin ración estándar por persona.

### 2.3 Tamaño de la familia

El número de personas por familia cambia el número de kits, pero no los kilos. Los kilos dependen de las personas. Estas son las cifras que encontramos:

| Fuente | Personas por familia | Tipo |
|---|---:|---|
| DANE, CNPV 2018, Manizales: 395.818 personas en 136.806 hogares ([presentación](https://www.dane.gov.co/files/censo2018/informacion-tecnica/presentaciones-territorio/190801-CNPV-presentacion-Caldas-Manizales.pdf)) | 2,9 | [F] |
| DANE, mismo censo, año 2005 (misma presentación) | 3,5 | [F] |
| UNGRD, reporte 36 del sismo (19 ago 2026): 262.154 personas damnificadas en 147.464 familias, en el país ([Decreto 1261](https://camacol.co/sites/default/files/descargables/DECRETO%201261de%202026_EMERGENCIA_compressed.pdf)) | 1,8 | [C] |
| UNGRD en La Guajira: 56.000 kits para más de 220.000 personas ([Radio Nacional, 29 ene 2025](https://radionacional.co/noticias-colombia/la-ungrd-entrego-ayudas-humanitarias-en-la-guajira)) | 3,9 | [C] |
| Tabla actual del equipo (`entrada/raciones.py`) | 4 | [S] |
| Recorte de 2019 del repositorio UNGRD (probable ayuda para Venezuela) | 5 | [F] |

Proponemos 2,9 personas por familia como valor por defecto para Manizales, para los mensajes que traen familias y no personas. Cuando el mensaje trae personas, lo más exacto es calcular los kilos por persona. El tamaño del hogar bajó de 3,5 a 2,9 entre 2005 y 2018, así que en 2026 podría ser menor **[S]**.

### 2.4 Lo que no encontramos

- La composición del kit de alimentos de la UNGRD: productos, kilos, personas y días. La Resolución 0382 de 2025 cita el Manual de Estandarización de Ayuda Humanitaria (capítulo 4, página 66), pero el buscador del repositorio de la UNGRD rechazó la consulta automática.
- La composición del mercado del Banco de Alimentos de Manizales o de ABACO. ABACO habló de toneladas y familias, no de kilos por mercado.
- Cuántos kits recibió cada familia damnificada en Manizales y cada cuánto.
- No alcanzamos dos notas de Diario del Sur (subsidios de arriendo en Manizales y sectores afectados) ni una de HSB Noticias: los sitios rechazan la lectura automática.
- El presupuesto de búsquedas web se agotó antes de terminar. No buscamos más la población por barrio ni el lineamiento del ICBF que diría el tamaño de su familia.

### 2.5 Comparación con la tabla actual del código

La tabla actual suma 14 kg de comida por familia de 4 personas. Si un pedido cubre 7 días, son 500 g por persona y día, un 10 % menos que la ración propuesta **[C]**. El peso total, entonces, estaba en el rango correcto. La composición no: el 54 % de esos kilos son perecederos (leche, pan, huevos, fruta, verdura y pollo), y la ración de emergencia no trae ninguno **[C]**. El agua actual (3 kg por familia y pedido) cubre un día de una sola persona.

## 3. Población y hogares por comuna

Esta sección da la población de cada comuna y la equivalencia de nombres con la semilla.

La fuente es el Análisis de Situación de Salud de Manizales 2023 de la Secretaría de Salud Pública ([ASIS 2023](https://salud.manizales.gov.co/wp-content/uploads/2024/07/ASIS_MANIZALES_2023.pdf), tablas 26 a 38, fila TOTAL). Cada tabla dice «Manizales 2023». El texto extraído no muestra la línea de fuente de esas tablas. Los hogares son estimados: población dividida por 2,9 **[C]**. La semilla no tiene barrios rurales; la fila «Área rural» agrupa los siete corregimientos.

| N.º | Comuna en la semilla | Nombre en ASIS 2023 | Nombre en OSM | Población 2023 | Hogares estimados |
|---:|---|---|---|---:|---:|
| 1 | Atardeceres | Atardeceres | Comuna Atardeceres | 39.250 | 13.534 |
| 2 | San José | San José | Comuna San José | 8.276 | 2.854 |
| 3 | Cumanday | Cumanday | Comuna Cumanday | 23.417 | 8.075 |
| 4 | La Estación | La Estación | Comuna La Estación | 25.901 | 8.931 |
| 5 | Ciudadela del Norte | Ciudadela del Norte | Comuna Ciudadela del Norte | 58.776 | 20.268 |
| 6 | Ecoturística Cerro de Oro | Ecoturístico Cerro de Oro | Comuna Ecoturística Cerro de Oro | 36.745 | 12.671 |
| 7 | Tesorito | Tesorito | Comuna Tesorito | 26.179 | 9.027 |
| 8 | Palogrande | Palogrande | Comuna Palogrande | 33.451 | 11.535 |
| 9 | Universitaria | Universitaria | Comuna Universitaria | 37.155 | 12.812 |
| 10 | La Fuente | La Fuente | Comuna La Fuente | 49.345 | 17.016 |
| 11 | La Macarena | La Macarena | Comuna La Macarena | 42.063 | 14.504 |
| 12 | Nuevo Horizonte | Nuevo Horizonte | Comuna Nuevo Horizonte | 49.702 | 17.139 |
| | (sin equivalente) | Área rural | | 24.235 | 8.357 |
| | **Total** | | | **454.495** | **156.722** |

Equivalencias:
- Los números 1 a 11 son los que el [ASIS 2020](https://salud.manizales.gov.co/wp-content/uploads/2024/08/ASIS_MANIZALES_2020.pdf) da como numeración anterior de cada comuna. El ASIS 2023 dice que Nuevo Horizonte se llamaba antes «comuna Doce», y la [Policía Nacional](https://www.policia.gov.co/noticia/habitantes-comuna-nuevo-horizonte-acompanaron-campana-policia-nacional-en-contra-del) la llama comuna 12 (10 may 2024).
- La semilla y OpenStreetMap dicen «Ecoturística Cerro de Oro». El ASIS 2023 dice «Ecoturístico», y un artículo de 2015 dice solo «Cerro de Oro».

Discrepancias que no resolvimos:
- San José tenía 24.022 habitantes en 2015 según el Centro de Información y Estadística de la Alcaldía ([Arteaga Botero, 2015](https://dialnet.unirioja.es/descarga/articulo/8961296.pdf)). El ASIS 2023 le da 8.276. No sabemos si la diferencia viene de reubicaciones o de un cambio de límites entre comunas. Hay que preguntarlo a Planeación.
- El total urbano pasa de 368.655 (2015, 11 comunas) a 430.260 (2023, 12 comunas). No sabemos cuánto de la diferencia es crecimiento y cuánto es cambio de límites.
- Para toda la ciudad, el DANE da 400.436 personas censadas y 434.403 ajustadas por omisión en 2018 ([infografía DANE](https://sitios.dane.gov.co/cnpv/app/views/informacion/perfiles/17001_infografia.pdf)). El ASIS 2023 suma 454.495 en 2023.

## 4. Damnificados y albergues

Esta sección reúne lo que hay sobre dónde están los damnificados y cuántas personas hubo en los albergues. Las cifras de ciudad están en `docs/investigacion/04_evidencia_del_problema.md` y no se repiten aquí, salvo el censo de 8.240 personas, que usamos para el cálculo ([Noticias RCN, 24 ago 2026](https://www.noticiasrcn.com/colombia/manizales-prepara-la-demolicion-de-7-edificios-que-presentan-danos-estructurales-1053593)).

### 4.1 Desglose por comuna o barrio

No encontramos ninguno. Revisamos el informe 27 de Asocapitales (reporte directo de la Alcaldía y la UGR), Noticias RCN, Blu Radio, La Silla Vacía, Minuto30, Publimetro, BBC Mundo, la Defensoría del Pueblo y un análisis de la Universidad Javeriana Cali sobre clústeres de afectación. Ninguno da damnificados por comuna o barrio. Según el análisis de la Javeriana, Manizales sumó 361 puntos de reportes de prensa y ningún píxel de imagen satelital interpretado ([Javeriana Cali](https://www.javerianacali.edu.co/sites/default/files/2026-08/clu%CC%81steres%20de%20afectacio%CC%81n%20del%20sismo%20del%2010%20de%20agosto%20de%202026.pdf)).

### 4.2 Lugares nombrados en las fuentes

Las fuentes nombran lugares sin cifras. Los ubicamos en su comuna con `datos/semilla/barrios.csv`.

| Lugar | Qué pasó | Comuna | Fuente |
|---|---|---|---|
| Milán | Punto de censo de damnificados (13 ago). Torres 1 a 3 de un conjunto evacuadas desde el sismo (20 ago), sin número de familias | Palogrande | [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10); [Noticias RCN](https://www.noticiasrcn.com/colombia/preocupacion-en-manizales-por-edifico-que-podria-colapsar-1052222) |
| Chipre | Punto de censo (13 ago) | Atardeceres | [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10) |
| Centro | Punto de censo (13 ago); daño en la catedral y el centro histórico | Cumanday | [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10); [Publimetro](https://www.publimetro.co/noticias/2026/08/10/terremoto-golpea-a-manizales-sube-a-tres-el-numero-de-muertos-y-continuan-los-reportes-de-danos/) |
| Avenida Santander | Punto de censo (13 ago); un edificio de estudiantes colapsó frente a la Universidad Católica | Cruza varias comunas | [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10); [BBC Mundo vía Prensa.com](https://www.prensa.com/mundo/como-vivio-el-terremoto-manizales-una-ciudad-entre-edificios-derrumbados-y-fachadas-rotas/) |
| El Cable | Sector descrito como uno de los más afectados; un comercio quedó sin agua ni luz | Palogrande | [BBC Mundo vía Prensa.com](https://www.prensa.com/mundo/como-vivio-el-terremoto-manizales-una-ciudad-entre-edificios-derrumbados-y-fachadas-rotas/) |

### 4.3 Ocupación de los albergues

Ninguna fuente da familias por albergue. Todas dan personas, y no siempre dicen si es ocupación del momento o el acumulado de quienes pasaron por allí.

| Fecha | Albergue | Personas | Qué mide | Fuente |
|---|---|---:|---|---|
| 10 ago | Coliseo Mayor | sin cifra | Se habilita como albergue temporal | [Minuto30](https://www.minuto30.com/?p=1715806) |
| 11 ago (nota actualizada el 13) | Todos los de la ciudad | 142 | Personas en albergues, según el Presidente | [La Silla Vacía](https://www.lasillavacia.com/?p=438017) |
| 12 ago | Junto al Coliseo Menor | de 114 a 245 | Ocupación | [Noticias RCN](https://www.noticiasrcn.com/colombia/manizales-convierte-al-coliseo-menor-en-centro-de-acopio-tras-el-terremoto-1049719) |
| 13 ago | Coliseo Mayor | cerca de 300 | Personas que «ya han accedido»; parece acumulado | [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10) |
| 15 ago | Uno sin nombre | unas 200 | Ocupación que «cambia constantemente» | [Noticias RCN](https://www.noticiasrcn.com/colombia/artesano-sobrevivio-al-terremoto-y-ahora-reconstruye-su-vida-desde-un-albergue-en-manizales-1050760) |
| 24 ago | Coliseo Mayor | sin cifra | Sigue como uno de los albergues principales | [Noticias RCN](https://www.noticiasrcn.com/colombia/manizales-prepara-la-demolicion-de-7-edificios-que-presentan-danos-estructurales-1053593) |
| 25 ago | Coliseo Mayor | 90 alojadas; más de 300 atendidas | Ocupación y acumulado; la Defensoría verificó que había alimentación | [Defensoría del Pueblo](https://www.defensoria.gov.co/w/familias-afectadas-por-el-terremoto-en-caldas-acceden-a-educacion-y-ayudas-humanitarias) |

El Coliseo Mayor y el Coliseo Menor quedan en la comuna Palogrande, según Nominatim de OpenStreetMap: el Mayor en el barrio Palogrande (5,0580 N; -75,4884) y el Menor en Guayacanes (5,0560 N; -75,4886) **[F]**. El Coliseo Menor funcionó además como centro de acopio para más de 4.000 damnificados, según la gestora social (12 ago, Noticias RCN).

## 5. Demanda esperada

Esta sección traduce personas en kilos. La regla es una sola: 555 g de ración seca por persona y día, y 3 L de agua si falla el acueducto.

### 5.1 Por comuna

Como no hay desglose por comuna, repartimos los 8.240 damnificados del censo en proporción a la población de cada comuna **[S]**. Este reparto es un supuesto, no un dato: las fuentes nombran zonas más golpeadas que otras (sección 4.2). Sirve para dimensionar y para tener la tabla lista. Cuando la UGR entregue el censo por comuna, basta con cambiar la columna de damnificados.

| Comuna | Población 2023 | Damnificados (reparto proporcional) [S] | Ración seca kg/día [C] | Agua L/día [C] | Kits de 7 días por semana [C] |
|---|---:|---:|---:|---:|---:|
| Atardeceres | 39.250 | 712 | 395 | 2.135 | 245 |
| San José | 8.276 | 150 | 83 | 450 | 52 |
| Cumanday | 23.417 | 425 | 236 | 1.274 | 146 |
| La Estación | 25.901 | 470 | 261 | 1.409 | 162 |
| Ciudadela del Norte | 58.776 | 1.066 | 591 | 3.197 | 367 |
| Ecoturística Cerro de Oro | 36.745 | 666 | 370 | 1.999 | 230 |
| Tesorito | 26.179 | 475 | 263 | 1.424 | 164 |
| Palogrande | 33.451 | 606 | 337 | 1.819 | 209 |
| Universitaria | 37.155 | 674 | 374 | 2.021 | 232 |
| La Fuente | 49.345 | 895 | 497 | 2.684 | 308 |
| La Macarena | 42.063 | 763 | 423 | 2.288 | 263 |
| Nuevo Horizonte | 49.702 | 901 | 500 | 2.703 | 311 |
| Área rural | 24.235 | 439 | 244 | 1.318 | 152 |
| **Total** | **454.495** | **8.240** | **4.573** | **24.720** | **2.841** |

Regla para cualquier otra cifra: por cada 1.000 personas atendidas se necesitan 555 kg diarios de ración seca, 3.885 kg por semana y 3.000 L diarios de agua **[C]**.

Lectura logística **[C]**. Una semana de ración seca para toda la ciudad pesa 32,0 t. Un día pesa 4,6 t, un poco menos que los dos camiones de la semilla juntos (3 t y 2 t, capacidades sintéticas). El agua de un día pesa 24,7 t, casi cinco veces la capacidad de esos dos camiones.

### 5.2 Albergue tipo: Coliseo Mayor

Este apartado calcula la demanda de un albergue con las ocupaciones que reportaron las fuentes.

| Escenario | Personas | Ración seca kg/día | kg/semana | Agua L/día | Familias de 2,9 |
|---|---:|---:|---:|---:|---:|
| Alto: personas que habían pasado por el albergue al 13 ago | 300 | 166,5 | 1.165,5 | 900 | 103 |
| Junto al Coliseo Menor, 12 ago | 245 | 136,0 | 951,8 | 735 | 84 |
| Ocupación del 25 ago | 90 | 50,0 | 349,7 | 270 | 31 |

Por producto, con 300 personas, el día pide 81 kg de arroz, 27 kg de harina de maíz, 27 kg de pasta, 9 kg de frijol, 9 kg de lenteja, 7,5 kg de aceite, 4,5 kg de panela y 1,5 kg de sal **[C]**. Una semana (1,2 t) cabe en un solo viaje del camión de 2 t de la semilla. Si el albergue funciona como Comedor Popular de Emergencia (hasta dos comidas calientes al día, Resolución UNGRD 0382 de 2025), los insumos van a su cocina. No encontramos gramos por plato para ajustar esos kilos.

### 5.3 Por producto, toda la ciudad

Para los 8.240 damnificados, un día de ración seca es: arroz 2.224,8 kg; harina de maíz 741,6 kg; pasta 741,6 kg; frijol 247,2 kg; lenteja 247,2 kg; aceite 206,0 kg; panela 123,6 kg; sal 41,2 kg **[C]**.

## 6. De comuna a punto de entrega

Esta sección explica cómo repartir la demanda de una comuna entre sus puntos de entrega. No depende de la lista de puntos reales que prepara otro agente: sirve para cualquier lista con nombre y coordenadas.

1. **Ubicar cada punto en su comuna.** Se consulta Nominatim en modo inverso (`/reverse`, `zoom=16`) con la latitud y longitud del punto. La comuna viene en el campo `suburb` con la forma «Comuna X». Medimos el método sobre los 138 barrios de la semilla: los 138 devuelven la misma comuna que trae `barrios.csv` (consulta del 20 nov 2026; caché en `/home/claude/trabajo/agente-2/reverso_cache.json`). La semilla probablemente salió de OpenStreetMap, así que esto prueba consistencia, no exactitud. Si el punto llega por nombre de barrio, se busca en `barrios.csv`.
2. **Personas por comuna.** Si hay censo de damnificados por comuna, se usa. Si no, se reparte el total en proporción a la población (sección 5.1) y se marca como supuesto.
3. **Separar los albergues.** Quien está en un albergue come allí. El albergue es un punto con demanda propia (ocupación × 555 g). Como no se sabe de qué comuna vienen sus ocupantes, se descuenta de cada comuna su parte proporcional. Ejemplo **[C]**: 300 personas en el Coliseo Mayor restan 22 a Palogrande, que queda con 584.
4. **Repartir entre los puntos de la comuna.** Cada barrio de la comuna se asigna a su punto más cercano, por la red vial si está el grafo y si no en línea recta. Como no hay población por barrio, cada barrio pesa lo mismo **[S]**. La parte de un punto es la fracción de barrios de la comuna que le tocan. Con datos del DANE por manzana, el peso sería la población real.
5. **Pasar a kilos y kits.** Kilos diarios del punto = personas × 0,555. Kits semanales = personas ÷ 2,9, redondeado hacia arriba. El agua va aparte (3 L por persona y día).
6. **Contrastar con los pedidos.** Si un barrio pide mucho más que su demanda esperada, puede ser un pedido repetido. Si una comuna con damnificados no pide nada, puede ser un punto sin canal. Ambas señales le sirven al despachador.

## 7. Cambio propuesto a `entrada/raciones.py`

El cambio reemplaza las constantes del inicio del archivo. Las funciones quedan iguales: `familias_desde` acepta un divisor decimal y `completar_kilos` sigue leyendo `KG_POR_FAMILIA`. Para que la bodega y el bot «hablen igual», el mismo cambio debe ir en `despacho/semilla.py` (línea 45). En `despacho/optimizar.py`, `KG_POR_FAMILIA = 10.0` podría pasar a 11,3, la suma de la ración seca semanal de una familia de 2,9 personas.

```python
"""Reglas escritas para completar un pedido que no trae familias o kilos. Las aplica el código, no el modelo.

FUENTES (detalle en docs/datos/demanda.md; consulta del 20 nov 2026). La ración seca por persona y día
sale de la columna ACNUR de la tabla de raciones del Logistics Cluster: cereal 450 g (valor que la tabla
pone junto a 2.100 kcal, el mínimo de Esfera según ACNUR), leguminosas 60 g, aceite 25 g, azúcar 15 g y sal 5 g.
El cereal se reparte 6:2:2 entre arroz, harina de maíz y pasta, como la Ración Familiar Para Preparar del
ICBF (v2, 2026). Una familia son 2,9 personas (DANE, CNPV 2018, Manizales). Un pedido cubre 7 días, el
ejemplo de ración seca semanal de OPS/INCAP. Cada bebé sigue contando como una familia aparte.
SUPUESTOS (marcados): frijol y lenteja a partes iguales; el agua de un pedido cubre 1 día; los frescos
usan la ración mensual del ICBF como referencia, sin tamaño de familia conocido. Pollo y pan no tienen
fuente y no se completan. Todo lo que sale de aquí queda marcado `supuesto` en el producto y en `dudas`.
"""
from __future__ import annotations

import math
import re
import unicodedata

# Gramos por persona y día de la ración seca.
# Fuente: https://log.logcluster.org/sites/default/files/pages/199/en/main-types-of-in-kind-commodities.pdf
# Reparto del cereal: https://www.icbf.gov.co/system/files/procesos/A26.G36.PP%20Anexo%20minuta%20patr%C3%B3n%20modalidad%20de%20atenci%C3%B3n%20y%20prevenci%C3%B3n%20de%20la%20desnutrici%C3%B3n%20-%20RFPP%20_v2.pdf
G_POR_PERSONA_DIA = {"arroz": 270, "harina de maíz": 90, "pasta": 90,   # cereal 450 g, reparto 6:2:2 (ICBF)
                     "frijol": 30, "lenteja": 30,                       # leguminosas 60 g, mitad y mitad (supuesto)
                     "aceite": 25, "panela": 15, "sal": 5}              # ACNUR; azúcar 15 a 20 g, se toma 15
# Agua para beber y cocinar: 2,5 a 3 L por persona y día (OPS, nota técnica 9, citando Esfera).
# https://paho.org/sites/default/files/2019-12/Nota-tecnica-sobre-agua-saneamiento-higiene-09.pdf
AGUA_L_POR_PERSONA_DIA = 3
# DANE, CNPV 2018, Manizales: 395.818 personas en 136.806 hogares, 2,9 por hogar.
# https://www.dane.gov.co/files/censo2018/informacion-tecnica/presentaciones-territorio/190801-CNPV-presentacion-Caldas-Manizales.pdf
PERSONAS_POR_FAMILIA = 2.9
# OPS/INCAP: ración seca por familia para un periodo fijo; el ejemplo es una semana (3 a 4 kg por persona).
# https://www.paho.org/es/emergencias-salud/seguridad-alimentaria-nutricional-situaciones-emergencia
DIAS_POR_PEDIDO = 7
DIAS_AGUA_POR_PEDIDO = 1          # supuesto: el agua se reparte a diario o por carrotanque

KG_POR_FAMILIA = {p: round(g * PERSONAS_POR_FAMILIA * DIAS_POR_PEDIDO / 1000, 2)
                  for p, g in G_POR_PERSONA_DIA.items()}
# -> arroz 5.48, harina de maíz 1.83, pasta 1.83, frijol 0.61, lenteja 0.61, aceite 0.51, panela 0.3, sal 0.1
KG_POR_FAMILIA["agua"] = round(AGUA_L_POR_PERSONA_DIA * PERSONAS_POR_FAMILIA * DIAS_AGUA_POR_PEDIDO, 1)  # 8.7
# Frescos: referencia, no estándar de emergencia. Ración mensual del ICBF (RFPP v2, 16/01/2026) llevada a
# 7 días: fruta 4 kg, verdura 3 kg, huevos 4 cubetas de 30 de 60 g (7,2 kg) y leche 12 L al mes.
KG_POR_FAMILIA |= {"fruta": round(4 * DIAS_POR_PEDIDO / 30, 2),       # 0.93
                   "verdura": round(3 * DIAS_POR_PEDIDO / 30, 2),     # 0.7
                   "huevos": round(7.2 * DIAS_POR_PEDIDO / 30, 2),    # 1.68
                   "leche": round(12 * DIAS_POR_PEDIDO / 30, 2)}      # 2.8 (1 L = 1 kg)
# Sin fuente: "pollo" y "pan". No están en la tabla, así que completar_kilos los deja sin kilos.
```

Probamos el bloque con las funciones actuales de la rama `samuel-bot`: corre, y con 3 familias completa 16,4 kg de arroz y 26,1 kg de agua, y deja el pollo sin kilos. Tres detalles al aplicarlo:

- El mensaje de `familias_desde` imprime «1 familia cada 2.9». Con `f"{PERSONAS_POR_FAMILIA:g}".replace(".", ",")` se lee «2,9».
- Si el mensaje trae personas, conviene calcular los kilos por persona (personas × gramos × días) en vez de redondear familias hacia arriba. Con 10 personas, `math.ceil` da 4 familias, que equivalen a 11,6 personas: un 16 % de más.
- `despacho/semilla.py` usa `KG_POR_FAMILIA[x]` para todos los productos de sus listas, pollo y pan incluidos. Si se copia esta tabla allí sin quitar esos dos productos de `PERECEDEROS`, la semilla falla con `KeyError`.

## 8. Supuestos

Esta sección junta en una lista los supuestos marcados **[S]** en el documento. Cada uno se puede cambiar en `generar.py` o en el bloque de código de la sección 7.

1. Los paréntesis de la tabla del Logistics Cluster son la versión de 2.100 kcal, con 450 g de cereal.
2. Azúcar (panela) 15 g por persona y día, el extremo bajo del rango de 15 a 20 g.
3. Leguminosas mitad frijol y mitad lenteja.
4. Un kit o pedido cubre 7 días, según el ejemplo de OPS/INCAP. No vimos el estándar de la UNGRD.
5. Una familia son 2,9 personas, el promedio de Manizales en 2018, aunque el tamaño del hogar viene bajando y las familias damnificadas del país promedian 1,8.
6. El agua (3 L por persona y día) solo cuenta si falla el acueducto, y un pedido de agua cubre 1 día.
7. Un litro de leche pesa un kilo.
8. Los frescos usan la ración mensual del ICBF como referencia, aunque es un programa contra la desnutrición y no de emergencia.
9. Los damnificados se reparten entre comunas en proporción a la población.
10. Los ocupantes de los albergues se descuentan de las comunas en la misma proporción.
11. Dentro de una comuna, cada barrio pesa lo mismo.
12. Las 300 personas del Coliseo Mayor son un escenario alto, porque la cifra parece acumulada.

## 9. Preguntas que solo una persona puede responder

- **Unidad de Gestión del Riesgo de la Alcaldía de Manizales.** ¿Cuántos damnificados del censo cerrado el 24 de agosto hay por comuna y por barrio? ¿Cuántas personas durmieron cada noche en el Coliseo Mayor y en el albergue del Coliseo Menor?
- **UNGRD, Subdirección para el Manejo de Desastres.** ¿Qué trae el kit de alimentos estándar (productos y kilos), para cuántas personas y para cuántos días? ¿Dónde se publica el Manual de Estandarización de Ayuda Humanitaria?
- **Banco de Alimentos de Manizales.** ¿Cuánto pesa su mercado, para cuántas personas y para cuántos días? ¿Cuántos mercados salieron por semana tras el sismo y hacia qué barrios?
- **Secretaría de Planeación de Manizales (Centro de Información y Estadística).** ¿Hay población por barrio para 2023 a 2026? ¿Por qué San José pasó de 24.022 habitantes en 2015 a 8.276 en 2023?
- **Gestora social de Manizales (centro de acopio del Coliseo Menor).** ¿Cuántos mercados entregó por día y con qué contenido?
