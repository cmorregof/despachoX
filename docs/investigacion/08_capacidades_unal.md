# 08 · Capacidades UNAL de las nueve sedes para DespachoX

Agente 6, viernes 20 de noviembre de 2026, de 5:00 a 5:25 p. m. Todas las consultas son del 2026-11-20.

Este informe completa el 03 y el 06. No repite la revisión por título de los 246 expedientes de la Universidad Nacional en SIPI. Tampoco analiza las patentes 37476 (empaque que captura etileno) y 33335 (RFID), porque las lee otro agente.

**Cómo leer las tablas**

- **[F]**: lo dice la fuente enlazada. **[C]**: lo calculamos o comparamos a partir de fuentes. **[S]**: es un supuesto nuestro. **No verificado**: no se pudo confirmar.
- **Fuerza.** **Alta** si cambia una decisión del sistema o un número del modelo. **Media** si entra en el piloto. **Decorativa** si solo adorna.
- **Dónde entra.** Las partes de DespachoX son entrada, ubicación, despacho, tablero, simulación y piloto.
- **Responsable.** Solo nombre y cargo tal como aparecen en una página o documento oficial de la UNAL. Cada fila dice de qué documento sale el nombre y de qué año es, porque algunos son viejos.

## 0. Qué fuentes respondieron

Esta sección dice qué se pudo consultar, porque eso limita lo que se afirma después.

| Fuente | Resultado | Consecuencia |
|---|---|---|
| SIPI de la SIC (`sipi.sic.gov.co`) | Error del servidor en tres intentos entre las 5:01 y las 5:10 p. m. (raíz, `Default.aspx` y `Browse.aspx`) | La entidad «universidad nacional de colombia sede medellin» queda **sin revisar**. Ver sección 1 |
| GrupLAC de Minciencias (`scienti.minciencias.gov.co`) | No alcanzable: la herramienta no pudo leer las reglas de acceso del sitio. Dos direcciones probadas | Líderes y categorías de GrupLAC **no verificados** |
| Hermes de la UNAL (`hermes.unal.edu.co`) | No alcanzable, mismo error. Dos direcciones probadas | Inventario de laboratorios de Hermes **no consultado** |
| Buscador web | El cupo de búsquedas, compartido entre agentes, se agotó hacia las 5:11 p. m. | Desde ahí solo se abrieron páginas ya encontradas. Ver sección 8 |

Así que los responsables salen del repositorio institucional, de páginas de institutos, de los informes de gestión 2024 de cada sede («La UNAL cuenta») y de la Agencia de Noticias UNAL. Ninguno sale de GrupLAC.

## 1. Patentes de la entidad «Sede Medellín» en SIPI

Esta sección responde el punto 1 del encargo: la entidad separada de la Sede Medellín en SIPI.

- **No se pudo revisar**, porque SIPI no respondió.
- Por otra vía apareció una sola patente de esa sede. Es la de polvo de aguacate y de guacamole, concedida a la UNAL Sede Medellín junto con HRA Uniquímica e Inversora Diavi, vigente hasta 2036 [F] ([Agronegocios, 12-nov-2019](https://www.agronegocios.co/agricultura/la-sic-entrego-patente-a-productos-a-base-de-aguacate-a-la-unal-para-usos-alternativos-2931456), consultado 2026-11-20). El número **no está verificado**. No sirve al despacho.
- Una búsqueda en Google Patents con ese titular devolvió documentos ajenos. Por ejemplo, CO2018010774A1 es de Banco Davivienda [F] ([Google Patents](https://patents.google.com/patent/CO2018010774A1/es), consultado 2026-11-20). Esto es falta de evidencia, no prueba de que no haya patentes pertinentes.
- El procedimiento de patentes de la Sede Medellín está publicado, pero no lista patentes [F] ([infografía](https://scda.medellin.unal.edu.co/vicedecanaturadeinvestigacion/images/pdf/Gesti%C3%B3n_Tecnol%C3%B3gica/INFOGRAFIA_PATENTES.pdf), consultado 2026-11-20).
- Dato lateral: el informe 2024 de la Sede Manizales reporta dos patentes concedidas y cinco registros de software en el año, sin títulos [F] ([informe Manizales 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Manizales/2024/SEDE_MANIZALES__2024.pdf), consultado 2026-11-20).

**Para quien reintente desde el campus.** Filtrar por el titular «universidad nacional de colombia sede medellin». Si el filtro por clasificación pide sesión, buscar por título con estos términos:

| Clase | Términos de título |
|---|---|
| B65 | empaque, envase, embalaje, bolsa, película |
| A23 | conservación, maduración, poscosecha, recubrimiento, deshidratado |
| G06Q | logística, ruta, inventario, trazabilidad, distribución |
| G08G | tráfico, vehículo, transporte |
| G01 | sensor, pluviómetro, deslizamiento, medición, monitoreo |
| H04 | radio, inalámbrica, red, mensaje, antena |

## 2. Logística humanitaria y ruteo

Esta sección reúne lo que la UNAL sabe sobre cómo se reparte ayuda en la última milla y cómo se rutea.

| Capacidad | Qué es | Sede | Responsable (fuente) | Dónde entra | Fuerza | Fuente y fecha |
|---|---|---|---|---|---|---|
| **Reglas de prioridad de la última milla** (tesis doctoral, 2021) | Los actores reparten ayuda con 16 reglas; cinco explican el 78 % de las decisiones de campo [F]. Las cinco más usadas son concentración de daño, concentración en albergues, pertenencia a un grupo poblacional, asignación de contraflujo y vinculación a una red [F]. Hay un modelo de agentes en NetLogo que mide costo de privación y entregas redundantes [F]. En el caso de Vichada, con un solo actor, la regla de máxima privación costó 1.440.599 y la regla observada de concentración de daño 2.103.313 [F]. Es un 31,5 % menos [C]. Con dos actores e información centralizada, la redundancia bajo concentración de daño pasó de 0,137 a 0 [F] | Bogotá, Facultad de Ingeniería, grupo SEPRO [F] | Autor: Feizar Javier Rueda Velasco. Directores: Miguel Ángel Jaller Martello y Wilson Adarme Jaimes [F] (registro de la tesis, 2021) | **Simulación:** la línea base deja de ser inventada y copia la regla observada en campo. **Despacho:** prioridad por privación. **Tablero:** indicador de entregas redundantes | **Alta** | [Repositorio UNAL](https://repositorio.unal.edu.co/handle/unal/80456); [PDF de la tesis](https://bffrepositorio.unal.edu.co/server/api/core/bitstreams/4c365deb-35a7-43df-a424-221858b41546/content); [registro en Kujane](https://kujane.minciencias.gov.co/Record/UNACIONAL2_ad73802f151323dc70b5d3397e5a1676/Details). Consultado 2026-11-20 |
| **Coordinación de la red de ayuda de Manizales** | Una tesis de maestría de 2017 mapeó la red de ayuda humanitaria de Manizales como un grafo de 39 actores [F]. La red tiene densidad baja (0,35) [F]. Donantes, ONG y proveedores quedaron en la periferia, con la menor centralidad [F]. Por ejemplo, los donantes tienen grado 5 y centralidad de vector propio de 0,253, frente a grado 17 y 0,674 de los medios de comunicación [F]. La mayoría de los actores centrales tiene poco contacto directo con los afectados, salvo la Unidad de Gestión del Riesgo y Corpocaldas [F]. En la escala de la tesis, la capacidad más fuerte de la red es la coordinación (3,42) y las más débiles son la planeación de la ayuda (2,96) y el enfoque en el afectado (2,91) [F]. La tesis cita como grupos «GTA Innovación y Desarrollo Tecnológico» y «Producción, Operaciones y Logística» [F]. Hay además una tesis de 2022 sobre la red local de preparación (ver informe 03). Nuevo: un artículo de 2025 compara coordinación centralizada, descentralizada y por clústeres con un modelo de agentes. La descentralizada rindió más en eficiencia y flexibilidad; la centralizada y la de clústeres cubrieron mejor los requerimientos [F] | Manizales, Departamento de Ingeniería Industrial [F] | Tesis de 2017: director William Ariel Sarache Castro; codirector Rafael Rentería [F]. Diana María Cárdenas Aguirre y Juan Camilo López Vargas (informe 03). El artículo de 2025 lo firman López-Vargas, Meisel, Cárdenas-Aguirre y Medina; su afiliación **no aparece** en el registro consultado | **Tablero:** quién aprueba y con qué información. **Piloto:** mapa de actores de Manizales | Media | [Tesis 2017 (PDF)](https://core.ac.uk/download/427644456.pdf) y [artículo JHLSCM 2025 en Kujane](https://kujane.minciencias.gov.co/Record/UNIBAGUE2_c9ff08e96d8ffc3a35bc3a67a215ca9f/Details), consultados 2026-11-20. Del informe 03, consultadas allí el 2026-11-20: [NOVUM 2016](https://revistas.unal.edu.co/index.php/novum/article/view/65371) y [tesis 2022](https://repositorio.unal.edu.co/items/3d2ca0b2-72a0-4588-a83c-fa1f031a0c4b/full) |
| **Grupo Ciencias de la Decisión** | Grupo de la Facultad de Minas. Líneas: optimización aplicada, heurísticas y metaheurísticas, logística y producción, planificación del transporte y simulación [F]. Su presentación de 2019 lo da como A1 en Colciencias [F]. Categoría actual **no verificada** | Medellín [F] | La presentación no nombra director. Da como contacto a Santiago Arango Aramburo [F] (presentación de 2019) | **Simulación:** revisión del diseño de experimentos | Decorativa | [Presentación del grupo, encuentro 2019](https://minas.medellin.unal.edu.co/vicedecanaturadeinvestigacion/images/encuentro_grupos_2019/1_Ciencias_de_la_Decisin.pdf). Consultado 2026-11-20 |
| **Ruteo para reparto de alimentos en la región cafetera** | Tesis de ruteo con NSGA-II (ver informe 03) | Manizales | Santiago Ruiz Herrera, director de la tesis (informe 03) | **Despacho:** antecedente local del objetivo «menos desperdicio» | Media | [Repositorio UNAL](https://repositorio.unal.edu.co/handle/unal/78373), consultado el 2026-11-20 por el informe 03; no reabierto aquí |

Advertencia sobre la primera fila. Las cifras de Vichada vienen de otro modelo: inundaciones, kits de ayuda y otra geografía [F]. Sirven para justificar la dirección del efecto, no para prometer un porcentaje en Manizales [S].

## 3. Conservación de alimentos y poscosecha

Esta sección reúne laboratorios y grupos que pueden convertir en dato la vida útil que hoy el modelo supone.

| Capacidad | Qué es | Sede | Responsable (fuente) | Dónde entra | Fuerza | Fuente y fecha |
|---|---|---|---|---|---|---|
| **Laboratorio de Empaques y Vida Útil de Alimentos (ICTA)** | Estima vida útil microbiológica y fisicoquímica de frescos y procesados a distintas temperaturas y humedades. Mide permeabilidad de películas. Evalúa empaques activos, entre ellos los de captura de etileno [F] | Bogotá [F] | Prof. Diego Alberto Castellanos Espinosa, «Coordinator Food Packaging and Shelf Life Laboratory» [F]. Trabaja modelación de vida útil y almacenamiento poscosecha [F] (página del ICTA sin fecha, consultada hoy) | **Despacho:** la fecha límite de cada lote sale de una tabla de vida útil por producto y temperatura. Hoy esa tabla es supuesta [S] | **Alta** si entrega la tabla; Media si no | [Laboratorio](https://icta.unal.edu.co/en/infrastructure/labs/packaging); [perfil de Castellanos](https://icta.unal.edu.co/en/institute/staff-icta/diego-castellanos). Consultado 2026-11-20 |
| **ActiPack (ICTA)** | Bolsa biodegradable con microperforaciones para fruta fresca, como la gulupa. TRL 7. Conserva entre 40 y 60 días en transporte refrigerado de 6 a 8 °C y alarga la vida útil hasta el doble [F]. Se hizo con financiación de la Sede Bogotá (iniciativa MENTOR) y la empresa Agrobol S.A. [F] | Bogotá [F] | Contacto: Prof. Diego Alberto Castellanos Espinosa [F]. La página no dice que dirija el proyecto | **Piloto.** Exige frío, y tras el sismo la cadena de frío se rompió (ver `ESTADO_DEL_ARTE.md`). En el modelo solo aplicaría a rutas con vehículo refrigerado [S] | Media | [ActiPack](https://icta.unal.edu.co/en/research/developed-technologies/actipack). Consultado 2026-11-20 |
| **Patente 37476, empaque que captura etileno** | Solo se menciona. La analiza otro agente (ver informe 06) | Bogotá | Ver informe 06 | Despacho y piloto, según el informe 06 | Ver informe 06 | `06_patentes_sipi.md` |
| **Laboratorio de Frutas y Hortalizas, Facultad de Ciencias Agrarias** | Recubrimiento comestible con cisteína que mantuvo aguacate hasta ocho días después de madurar, a 10 °C [F] | Medellín [F] | Carlos Julio Márquez, director del laboratorio [F] (nota de 2017). Cargo actual **no verificado** | **Piloto:** dato de vida útil del aguacate, si la canasta lo lleva | Decorativa | [Agencia de Noticias UNAL, 26-ene-2017](https://agenciadenoticias.unal.edu.co/detalle/useful-life-of-avocados-extended). Consultado 2026-11-20 |
| **GIPA y Laboratorio de Tecnología de Frutas y Hortalizas** | El portafolio de 2016 lista el Grupo de Investigación en Procesos Agroindustriales (GIPA), con una línea de empaques, envases y embalajes para la agroindustria [F]. Una nota de 2011 reporta un ensayo de 12 días con banano en rodajas a 11 °C y 85 % de humedad relativa, sin cifra de vida útil ganada [F]. El informe 2024 de la sede no menciona poscosecha ni empaques [F] | Palmira [F] | Luis Eduardo Ordóñez Santos, líder del grupo y del laboratorio [F] (portafolio de 2016). Saúl Dussán Sarria dirigió el estudio de 2011 [F]. Vigencia **no verificada** | **Piloto:** solo si el sistema se replica en el Valle del Cauca [S] | Decorativa | [Portafolio de servicios 2016](https://palmira.unal.edu.co/images/descargas/Portafolio_de_servicios.pdf); [Agencia UNAL, 13-sep-2011](https://agenciadenoticias.unal.edu.co/detalle/new-techniques-will-prolong-life-of-banana); [informe Palmira 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Palmira/2024/SEDE_PALMIRA_2024.pdf). Consultado 2026-11-20 |
| **Poscosecha de mango en comunidades vulnerables del Cesar** | Proyecto activo en 2024, registrado en Hermes [F] | La Paz [F] | El informe no nombra responsable [F] | Ninguna directa | Decorativa | [Informe La Paz 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Cesar/2024/SEDE_LA_PAZ__2024.pdf). Consultado 2026-11-20 |
| **Productos pesqueros artesanales** | Fortalecimiento de productos pesqueros de Tumaco con apoyo de la FAO. El informe no menciona cadena de frío [F] | Tumaco [F] | No nombra responsable [F] | Ninguna | Decorativa | [Informe Tumaco 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Tumaco/2024/SEDE_TUMACO_2024.pdf). Consultado 2026-11-20 |

## 4. Monitoreo de vías y laderas

Esta sección reúne las capacidades que dicen qué tramo puede cerrarse por lluvia. Es el tema más fuerte, y casi todo está en Manizales.

| Capacidad | Qué es | Sede | Responsable (fuente) | Dónde entra | Fuerza | Fuente y fecha |
|---|---|---|---|---|---|---|
| **Indicador A25 del SAT por deslizamientos** | Lluvia acumulada de 25 días por estación. Alerta amarilla de 200 a menos de 300 mm; naranja de 300 a menos de 400 mm; roja desde 400 mm [F]. El reporte de 2020 cubre 14 estaciones, de CHEC, EMAS, la UNAL y la Alcaldía con su Unidad de Gestión del Riesgo [F]. Es parte del proyecto «Estaciones hidrometeorológicas para la gestión del riesgo por deslizamientos en Manizales», dentro del SIMAC [F] | Manizales. Créditos: G.T.A. en Ingeniería Hidráulica y Ambiental e IDEA [F] | El reporte lo elaboró el Ing. John Alexander Pachón G. [F] (reporte de 2020). Director del IDEA: **no verificado** | **Despacho:** el costo de cada tramo sube según el color de la estación más cercana. **Ubicación:** a cada tramo se le asigna su estación por distancia [S]. **Tablero:** semáforo por estación | **Alta** | [Reporte A25 2020](https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf). Consultado 2026-11-20 |
| **SIMAC y CDIAC** | El CDIAC ofrece un sistema de consultas con usuario, un generador de indicadores, mapas de redes y un listado de estaciones descargable [F]. En su sitio hay boletines climatológicos de Caldas mensuales de 2024 y 2025 y semanales de 2025 [F]. Muestra mapas estáticos de cinco redes, entre ellas una red acelerográfica de Manizales y una red de estaciones comunitarias de Caldas, sin coordenadas descargables en esa página [F]. El geoportal del SIMAC y el generador de indicadores necesitan JavaScript y no se pudieron revisar | Manizales [F] | Boletín semanal 18 de 2025: Fernando Mejía Fernández, «Asesor SIMAC», y Lorena Giraldo Gómez, «Operadora de redes de monitoreo en el SIMAC» [F]. La página de personas nombra como coordinadores de proyecto a Jeannette Zambrano y Freddy Leonardo Franco Idárraga [F], pero el pie del sitio dice «31/05/16», así que puede estar desactualizada | **Entrada:** lluvia diaria por estación para calcular el A25. **Tablero** | **Alta** (es el dato que alimenta la fila anterior) | [CDIAC](https://cdiac.manizales.unal.edu.co/); [mapas](https://cdiac.manizales.unal.edu.co/mapas.php); [personas](https://cdiac.manizales.unal.edu.co/personas.php); [boletín semanal 2025-18](https://cdiac.manizales.unal.edu.co/publicaciones/2025/Semanales/2025-18_Boletin_28abrila04mayo02025_VF.pdf). Consultado 2026-11-20 |
| **SAT comunitario de inundaciones y deslizamientos** | Miras con códigos amarillo y rojo que lee la comunidad, pluviómetros con panel solar y batería, y radios para que los residentes reporten cambios [F]. Está en Lusitania, Providencia, la cuenca del río Chinchiná, las quebradas El Guamo y Manizales, el km 41 y zonas rurales de Manizales y Villamaría [F] | Manizales, Departamento de Ingeniería Civil [F] | Jeannette del Carmen Zambrano Nájera. El cargo de profesora de Ingeniería Civil sale de la nota de 2024, que no es fuente oficial. En fuentes UNAL figura como codirectora de la tesis de 2025 de la fila siguiente y como coordinadora de proyecto en la página del CDIAC [F] | **Entrada:** un vigía con radio avisa un derrumbe o una crecida y el despachador lo marca como cierre probable [S]. **Piloto** | Media | [iAgua, 13-nov-2024](https://www.iagua.es/noticias/universidad-nacional-colombia/unal-desarrolla-sistema-alertas-inundaciones-y-deslizamientos). Es un medio externo que reproduce la noticia de la UNAL; la nota original no se abrió. Consultado 2026-11-20 |
| **Umbrales dinámicos para el SAT por inundaciones** (tesis de maestría, 2025) | Encuentra que los umbrales fijos se quedan cortos. Propone umbrales según el nivel inicial del río Chinchiná y la lluvia en ventanas móviles [F] | Manizales, grupo GTA en Ingeniería Hidráulica y Ambiental [F] | Directores de la tesis: Jorge Julián Vélez Upegui y Jeannette Zambrano Nájera [F] (registro de 2025) | **Simulación:** escenarios de cierre por crecida en vías junto al Chinchiná [S] | Decorativa hoy; Media en el piloto | [Repositorio UNAL](https://repositorio.unal.edu.co/items/7db93ba1-fd46-4430-8f75-9b2600785a99/full). Consultado 2026-11-20 |
| **Estudio multiamenaza de Manizales** | Susceptibilidad a deslizamiento y microzonificación sísmica (ver informe 03) | Manizales, IDEA | Omar Darío Cardona (informe 03) | **Despacho:** peso de riesgo por tramo, si se consiguen las capas | Media | [IJDRS 2017](https://link.springer.com/article/10.1007/s13753-017-0135-8), consultado el 2026-11-20 por el informe 03; no reabierto aquí |
| **Inventario de movimientos en masa del Semillero Geohazards** | SIATA calcula la probabilidad de deslizamiento por barrio y vereda con lluvia antecedente de 1 a 7 y de 15 a 90 días y 35 pluviómetros. Usa inventarios del DAGRD y del Semillero Geohazards de la UNAL [F] | Medellín [F] | El informe no nombra responsable [F] | **Piloto:** solo si el sistema se replica en el Valle de Aburrá [S] | Decorativa | [SIATA, anexo geotecnia, enero de 2026](https://siata.gov.co/geotecnia/Documentacion2026/202601_AnexoWP132_InformeMensual_CCT261_2025.pdf). Consultado 2026-11-20 |
| **Observatorio del Hábitat, reporte de riesgo de desastres** | Reporte de julio de 2025. Dice que cerca del 30 % de los habitantes de Medellín vive en polígonos de amenaza alta o muy alta [F] | Medellín, grupo Escuela del Hábitat-Cehap (A1, según el reporte) [F] | No nombra director. Firma un artículo Hernán E. Martínez Carvajal, profesor de la Facultad de Minas [F] | Ninguna directa | Decorativa | [Reporte 1, 2025](https://arquitectura.medellin.unal.edu.co/escuelas/habitat/images/pdf/REPORTE_1_-_OBSERVATORIO_DEL_HBITAT-_RIESGO_DE_DESASTRES_20250807.pdf). Consultado 2026-11-20 |

**El umbral del A25 se usó en 2026.** El 16 de febrero de 2026 el Consejo Municipal de Gestión del Riesgo de Manizales declaró alerta amarilla. El umbral preventivo citado fue 200 mm acumulados en menos de 25 días, y la estación La Palma llegó a 300 mm [F] ([Blu Radio](https://www.bluradio.com/nacion/manizales-entra-en-alerta-amarilla-por-lluvias-que-superan-niveles-historicos-rg10); [Noticias RCN](https://www.noticiasrcn.com/colombia/declaran-alerta-amarilla-en-manizales-por-lluvias-extremas-992470); ambas del 16-feb-2026, consultadas 2026-11-20). Ninguna nota nombra a la UNAL ni al IDEA [F]. En cambio, el umbral es el mismo de la alerta amarilla del A25 [C]. Además, siete de las nueve estaciones que nombran las notas tienen el mismo nombre en el reporte A25 de 2020: Hospital de Caldas, Chec, Alcázares, El Carmen, Emas, Bosques del Norte y La Palma [C]. Niza puede ser «Milán-Planta Niza»; Maltería no aparece en 2020 [C].

Nota de conciliación con el informe 03. Ese informe cita una red de 20 estaciones con datos cada 5 minutos. El reporte A25 de 2020 trae 14. No se contradicen: son documentos y años distintos [C].

## 5. Comunicaciones sin internet

Esta sección busca capacidades UNAL para que un pedido o un cierre llegue cuando no hay datos. El hallazgo es más débil que en los temas anteriores.

| Capacidad | Qué es | Sede | Responsable (fuente) | Dónde entra | Fuerza | Fuente y fecha |
|---|---|---|---|---|---|---|
| **Radios del SAT comunitario** | Los residentes reportan cambios del entorno por radio [F]. Es el único canal sin internet ya en uso que se encontró | Manizales [F] | Jeannette del Carmen Zambrano Nájera (ver sección 4) | **Entrada** y **piloto** (ver sección 4) | Media | [iAgua, 13-nov-2024](https://www.iagua.es/noticias/universidad-nacional-colombia/unal-desarrolla-sistema-alertas-inundaciones-y-deslizamientos). Consultado 2026-11-20 |
| **Radioaficionados en la red de emergencias de Manizales** | La tesis de 2017 sobre la red de ayuda de Manizales lista a la Liga y Federación de Radioaficionados (FRACOL) entre los actores de la Estrategia Municipal de Respuesta a Emergencias [F]. Anota que en emergencias pasadas la radio fue el único medio de comunicación disponible [F]. En cambio, FRACOL mostró poco conocimiento de su papel en la función logística [F] | Manizales [F] | William Ariel Sarache Castro, director de la tesis [F] (2017) | **Entrada** y **piloto:** canal de radio de reserva hacia el acopio cuando caen datos y SMS (nivel 3 de `docs/SIN_CONEXION.md`) [S] | Media | [Tesis 2017 (PDF)](https://core.ac.uk/download/427644456.pdf). Consultado 2026-11-20 |
| **Arquitectura LoRaWAN** (tesis de maestría, 2025) | Red que une sensores cableados y LoRaWAN, con gateway propio, ChirpStack, Node-RED e InfluxDB. Se validó en el campus de Bogotá midiendo agua, energía, gas y aire. No trata emergencias [F] | Bogotá, Departamento de Ingeniería Eléctrica y Electrónica [F] | Director de la tesis: Ph.D. Carlos Iván Camargo Bareño [F] (tesis de 2025) | **Piloto:** un nodo LoRa en un punto de entrega rural podría mandar mensajes cortos del formato de `docs/SIN_CONEXION.md`, como «ENTREGADO DX7K2Q» o «CIERRE» [S] | Media | [Tesis en el repositorio UNAL](https://bffrepositorio.unal.edu.co/server/api/core/bitstreams/ae61c6a5-24e7-4256-b05e-46117e515825/content). Consultado 2026-11-20 |
| **Redes ad hoc del sistema TLÖN** | Redes inalámbricas ad hoc para procesamiento distribuido. Una tesis de 2019 diseñó un mecanismo de agrupamiento y probó tres clústeres encadenados con latencia y rendimiento. No trata desastres [F] | Bogotá, Facultad de Ingeniería [F] | Director de la tesis: Jorge Eduardo Ortiz Triviño [F] (registro de 2019). Que TLÖN sea un grupo de GrupLAC: **no verificado** | **Piloto:** red local entre acopio y vehículos [S] | Decorativa | [Repositorio UNAL](https://repositorio.unal.edu.co/items/a1ba9419-2f7a-4b9c-a76e-e1aa741628f8/full). Consultado 2026-11-20 |
| **Centro de Producción Radiofónica** | El informe 2024 dice que algunos equipos requieren mantenimiento [F] | Orinoquía [F] | No nombra responsable [F] | Ninguna directa | Decorativa | [Informe Orinoquía 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Orinoquia/2024/SEDE_ORINOQUIA_2024.pdf). Consultado 2026-11-20 |
| **SMS** | No se buscó: el cupo del buscador se agotó antes. Queda abierto | | | | | |

**No citar como UNAL.** La aplicación Conecta2, que arma una red ad hoc entre celulares de sobrevivientes de un desastre, salió en la revista *Ingeniería e Investigación* de la UNAL en 2024. Sus tres autores son de la Universidad Antonio Nariño [F] ([artículo](https://revistas.unal.edu.co/index.php/ingeinv/article/download/110710/93978/716263), consultado 2026-11-20). Por eso queda fuera de este portafolio.

## 6. Cobertura de las nueve sedes

Esta tabla dice qué se encontró en cada sede. En las cinco sedes de presencia nacional no se encontraron capacidades que cambien el sistema; se listan para mostrar que se revisaron.

| Sede | Lo encontrado | Fuerza máxima | Dirección de la sede, si el informe 2024 la nombra | Fuente y fecha |
|---|---|---|---|---|
| Bogotá | Reglas de prioridad (SEPRO); laboratorio de empaques del ICTA y ActiPack; patentes 37476 y 33335 (otro agente); LoRaWAN; redes ad hoc | Alta | No consultado | Secciones 2, 3 y 5 |
| Medellín | Ciencias de la Decisión; Laboratorio de Frutas y Hortalizas; Semillero Geohazards; Observatorio del Hábitat; grupo VITRA (informe 03); patente de aguacate. La entidad de SIPI quedó sin revisar | Decorativa | No consultado | Secciones 1 a 4 |
| Manizales | A25, SIMAC y CDIAC; SAT comunitario con radios; umbrales dinámicos; red de ayuda de Manizales, con radioaficionados entre sus actores; ruteo con NSGA-II; estudio multiamenaza | Alta | El informe 2024 no nombra a la persona en la Vicerrectoría ni en la dirección del IDEA [F]. La agenda PreCOP16 del 2 de octubre de 2024 da como «Vicerrectora de Sede» a Belizza Ruiz Mendoza [F]; vigencia en 2026 **no verificada** | Secciones 2 y 4; [informe Manizales 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Manizales/2024/SEDE_MANIZALES__2024.pdf); [agenda PreCOP16](https://unal.edu.co/fileadmin/user_upload/docs/COP16/Manizales-AgendaPreCOP16.pdf). Consultados 2026-11-20 |
| Palmira | GIPA y Laboratorio de Tecnología de Frutas y Hortalizas (datos de 2011 y 2016) | Decorativa | No la nombra [F] | Sección 3 |
| La Paz | Poscosecha de mango; Laboratorio de Ciencias de la Información Geográfica [F] | Decorativa | No la nombra [F] | [Informe La Paz 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Cesar/2024/SEDE_LA_PAZ__2024.pdf), consultado 2026-11-20 |
| Orinoquía | Proyecto financiado por el Programa Mundial de Alimentos en Arauquita, sobre seguridad alimentaria campesina, terminado en 2024 [F]; Centro de Producción Radiofónica | Decorativa | Adriana Isabel Orjuela Martínez, «Directora de Sede, desde el 12 de junio de 2024» [F] | [Informe Orinoquía 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Orinoquia/2024/SEDE_ORINOQUIA_2024.pdf), consultado 2026-11-20 |
| Amazonía | Apoyo a la iniciativa nacional de Red Sismológica [F]. Nada de logística ni cadena de frío [F] | Decorativa | Eliana María Jiménez Rojas, «Directora de Sede»; el IMANI lo dirige Samuel Arturo Gómez Insuasti [F] | [Informe Amazonía 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Amazonia/2024/SEDE_AMAZONIA_2024.pdf), consultado 2026-11-20 |
| Caribe | Proyecto de riesgo de desastres e innovación social para fortalecer la respuesta comunitaria; simposio de gestión del riesgo en islas pequeñas [F] | Decorativa | Adriana Santos Martínez, «Directora de sede»; Raúl Román Romero, «Coordinador de investigación y Extensión» [F] | [Informe Caribe 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Caribe/2024/SEDE_CARIBE_2024.pdf), consultado 2026-11-20 |
| Tumaco | Productos pesqueros artesanales. Nada de logística, cadena de frío ni alerta temprana [F] | Decorativa | No la nombra [F] | [Informe Tumaco 2024](https://launalcuenta.unal.edu.co/fileadmin/user_upload/documentos/Informes/Tumaco/2024/SEDE_TUMACO_2024.pdf), consultado 2026-11-20 |

El proyecto de la Orinoquía con el Programa Mundial de Alimentos sirve como antecedente si el equipo busca al PMA como aliado (ver `ESTADO_DEL_ARTE.md`, sección 4) [S].

## 7. Paquete recomendado

Esta sección elige cinco capacidades. El criterio fue que cada una cambie una decisión o un número de DespachoX, o que tenga un responsable que se pueda buscar hoy.

**1. Indicador A25 y datos del SIMAC (Manizales).**
- *Por qué.* Es la única capacidad cuyo umbral ya aparece en una decisión de la ciudad: la alerta de febrero de 2026 usó 200 mm en 25 días, igual que el amarillo del A25 [C]. Además cambia un número del modelo, el costo de cada tramo.
- *Componente de la ficha.* 2, prototipo: penalización por tramo. 3, conocimiento: dato y método UNAL con nombre. 4, plan: el hito de los días 60 a 75 ya existe en `FICHA_4_5_6_BORRADOR.md`.
- *Qué pedir.* Lluvia diaria de agosto de 2026 por estación, o acceso al sistema de consultas del CDIAC. Coordenadas de las estaciones vigentes. Confirmar que los umbrales de 200, 300 y 400 mm siguen vigentes. Permiso para citar al SIMAC en el pitch.
- *A quién.* Fernando Mejía Fernández, Asesor SIMAC según el boletín de 2025. Si no está, Jorge Julián Vélez Upegui o Jeannette Zambrano Nájera, directores de tesis del GTA en Ingeniería Hidráulica y Ambiental.

**2. Reglas de prioridad de la última milla (SEPRO, Bogotá).**
- *Por qué.* Le da a la simulación una línea base observada en campo, así que deja de ser un hombre de paja. También trae una métrica, las entregas redundantes, que el tablero puede mostrar.
- *Componente de la ficha.* 2, simulación: la política 1 asigna por concentración de daño y por albergues. 3, método. 6, impactos: costo de privación y redundancia como indicadores.
- *Qué pedir.* Que confirme que nuestra línea base representa bien las reglas observadas. Si el modelo NetLogo y sus parámetros se pueden compartir.
- *A quién.* Wilson Adarme Jaimes, director de la tesis, por correo institucional.

**3. Laboratorio de Empaques y Vida Útil del ICTA (Bogotá).**
- *Por qué.* Puede convertir en dato un supuesto: hoy las ventanas de vencimiento del optimizador son supuestas.
- *Componente de la ficha.* 2, despacho: fecha límite por lote. 4, plan: piloto con ActiPack o con la patente 37476. 5, aliados: respaldo técnico.
- *Qué pedir.* Vida útil, aunque sea en rangos, de cinco a diez productos de la canasta a temperatura ambiente y con empaque activo. Condiciones para un piloto. Lo legal de la patente lo ve el agente de patentes con Fernando Bernal.
- *A quién.* Prof. Diego Alberto Castellanos Espinosa, coordinador del laboratorio, por el correo del laboratorio publicado en su página.

**4. SAT comunitario con radios (Ingeniería Civil, Manizales).**
- *Por qué.* Ya tiene vigías con radio en barrios de ladera. Es la vía más directa para que un cierre llegue al acopio sin internet.
- *Componente de la ficha.* 2, entrada: reporte de cierre probable. 4, plan: simulacro con vigías. 5, riesgos: conectividad.
- *Qué pedir.* Si los vigías podrían reportar cierres viales al acopio y con qué protocolo. En qué barrios están; la nota nombra Lusitania y Providencia.
- *A quién.* Jeannette del Carmen Zambrano Nájera, codirectora de tesis del GTA en Ingeniería Hidráulica y Ambiental, en la Sede Manizales.

**5. Red de ayuda humanitaria de Manizales (ver informe 03).**
- *Por qué.* Valida el papel del despachador y la lista de actores con quien estudió esa red en Manizales. La tesis de 2017 que dirigió Sarache encontró a donantes y proveedores en la periferia de la red [F]. Ese es el tramo que DespachoX conecta con los puntos de entrega [S].
- *Componente de la ficha.* 3, conocimiento. 5, aliados.
- *Qué pedir.* Quince minutos de mentoría para revisar el flujo de aprobación. Si los radioaficionados de FRACOL siguen en la Estrategia Municipal de Respuesta y si podrían pasar pedidos al acopio.
- *A quién.* William Ariel Sarache Castro, Diana María Cárdenas Aguirre o Juan Camilo López Vargas, en la Sede Manizales.

## 8. Lo que falta

Esta sección lista lo que no se cerró, para que nadie lo cite como verificado.

- La entidad «universidad nacional de colombia sede medellin» en SIPI. Hay que reintentar desde el campus o preguntarle a Fernando Bernal.
- Líderes y categorías de GrupLAC de todos los grupos citados.
- El nombre de quien dirige hoy el IDEA de Manizales y el ICTA.
- Capacidades UNAL en SMS. No se alcanzó a buscar.
- El Observatorio de Soberanía y Seguridad Alimentaria y Nutricional (OBSSAN) de la Sede Bogotá. Podría respaldar la prioridad por grupo poblacional. No se alcanzó a buscar, así que su existencia y sus responsables quedan **no verificados**.
- Los títulos de los dos registros de patente y de los cinco de software de la Sede Manizales en 2024.
- La frecuencia de cada una de las 16 reglas de prioridad. Está en las tablas 7 y 9 de la tesis, que no se leyeron.
- La afiliación actual de Miguel Ángel Jaller Martello.
- La nota original de la Agencia de Noticias UNAL sobre el SAT comunitario.
