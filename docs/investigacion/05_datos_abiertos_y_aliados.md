# 05 · Datos abiertos, piezas técnicas y aliados (DespachoX)

Fecha de la investigación: 20 nov 2026. Leyenda: **[V]** = abrí la página o el resultado de búsqueda la confirma. **[NV]** = no verificado (de memoria o solo por título de búsqueda). Las fuentes web fallaron a mitad de la investigación (pedían aprobación que nadie dio), así que varios enlaces técnicos quedan [NV].

## Parte A · Datos abiertos

### A1 · Red vial

| Dato | Qué contiene / formato / licencia | Acceso | Uso en DespachoX |
|---|---|---|---|
| OpenStreetMap | Vías con `highway`, `surface`, `maxweight`, `bridge`, `oneway`. Licencia ODbL (atribuir "© OpenStreetMap contributors"). | `osmnx` por lugar o bbox (ver B). [Wiki de descargas](https://wiki.openstreetmap.org/wiki/Download) [V en búsqueda] | Grafo base y tiempos de viaje. |
| Geofabrik Colombia | Extracto del país en `.osm.pbf` y `.shp`. Mismo ODbL. | Portal [download.geofabrik.de](https://download.geofabrik.de) [V]. Página del país: `/south-america/colombia.html` [NV]. | Plan B sin depender de la API Overpass. Recortar con `osmium` o `pyrosm` [NV]. |
| INVÍAS | Red vial nacional y estado de vías. | [hermes.invias.gov.co](https://hermes.invias.gov.co) [NV] | Contexto de vías nacionales. No para calles urbanas. |
| datos.gov.co | Portal de datos abiertos (Socrata, API SODA, CSV/JSON). Incluye "Emergencias UNGRD" según el estudio de la Javeriana [V]. | [datos.gov.co](https://www.datos.gov.co) [NV] | Emergencias históricas y otros listados. Buscar "red vial", "puentes" a mano. |

Calidad del mapeo en Manizales: no pude medirla. Hay que comprobarlo hoy: contar arcos con `surface`, `maxweight` y `bridge` en el grafo. La activación de HOT dice que el mapeo coordinado busca mejorar el mapa base en las zonas más afectadas, y nombra a Manizales entre las ciudades con daños graves; no confirma que Manizales sea área de tareas ([wiki HOT](https://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Team/Open_Mapping_Hub_-_Latin_America_and_The_Caribbean/Activations/2026_Colombia_Earthquake_Response) [V]).

### A2 · Relieve y amenaza

| Dato | Qué es | Enlace | Uso |
|---|---|---|---|
| DEM SRTM 30 m / Copernicus GLO-30 / ALOS | Elevación global, GeoTIFF. Licencias distintas por producto. | Portales de USGS, Copernicus y JAXA [NV] | Pendiente por arco (OSM `incline` casi no existe). Opcional para el MVP. |
| SGC: amenaza por movimientos en masa y SIMMA | Mapas de amenaza (1:100.000 y 1:25.000) e inventario de movimientos en masa. | Actas de "productos geocientíficos oficializados": [Acta 256, oct 2025](https://www2.sgc.gov.co/Publicaciones/actasdeoficializacion/2025/Acta-256-Octubre-20-de-2025.pdf) [V en búsqueda]. Servicio de descarga de SIMMA [NV]. | Marcar arcos en zonas de amenaza alta como "riesgo". Solo si da tiempo. |
| Alcaldía de Manizales / Corpocaldas / IDEA-UNAL | Geoportales y estaciones de lluvia (SIMAC). | Sin enlace verificado. El portal IDEA-UNAL aparece en [publicaciones](https://idea.manizales.unal.edu.co/publicaciones/eventos/Foro_Simposio_2019/dia3/3.pdf) [V en búsqueda]. | Alerta de lluvia: [NV]. |

La Alcaldía publicó un "Plan de apertura de datos 2025", pero su inventario son filas de ejemplo, sin datasets reales ([PDF](https://manizales.gov.co/wp-content/uploads/2025/02/4.Plan_de_Apertura_de_Datos_Vr5_2025.pdf) [V]). No cuenten con un portal de geodatos municipal.

### A3 · Población y demanda

| Dato | Contenido | Enlace | Uso |
|---|---|---|---|
| DANE · Marco Geoestadístico Nacional (MGN) 2018 y Censo 2018 | Polígonos de manzana, sección y sector; población y hogares por manzana (integrado CNPV 2018). | [Instructivo MGN2018 integrado](https://www.dane.gov.co/files/geoportal-provisional/MGN2018_Integrado_CNPV2018_InstructivoUso.pdf) [V en búsqueda]; descargas en [geoportal.dane.gov.co](https://geoportal.dane.gov.co/descargas/descarga_mgn/fichatecnicamgn2017.pdf) [V en búsqueda]. | Estimar demanda por barrio (personas × ración). |
| Juntas de Acción Comunal | 204 JAC: 12 comunas y 7 corregimientos; 131 barrios urbanos y 73 veredas. Sin nombres ni coordenadas en el documento. | [Consolidado JAC/JAL](https://manizales.gov.co/wp-content/uploads/2025/08/CONSOLIDADO-JUNTAS-ACCION-COMUNAL-Y-ADMINISTRADORAS-LOCALES-JAC-JAL.pdf) [V] | Define la lista de "clientes" (comités barriales). |
| SISBÉN, IPM | Pobreza multidimensional por manzana (DANE) [NV el enlace]. Microdatos SISBÉN: no encontré público útil [NV]. | | Priorizar barrios vulnerables. |

Contexto de demanda del 15 ago (preliminar): en Manizales 4.000 damnificados, 2.707 viviendas colapsadas, 3.993 averiadas y 40 instituciones educativas afectadas ([Asocapitales, informe 27](https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-27.pdf) [V]). El informe no trae vías cerradas, acopios ni abastecimiento.

### A4 · Puntos de oferta y entrega

No encontré un dataset oficial de albergues, acopios o comedores de Manizales. Ruta práctica:

- **OSM** con `osmnx.features_from_place`: `amenity=marketplace|school|community_centre|social_facility|place_of_worship|townhall`, `shop=supermarket`, `emergency=assembly_point`. Cubre escuelas y plazas. [NV el contenido real en Manizales: verificarlo.]
- **Candidatos a entrega**: instituciones educativas (40 afectadas, así que descartar las dañadas), coliseos y sedes comunales.
- **Albergues y acopios del sismo**: los define la UGR; pedirlos en el piloto (parte C).
- **ABACO** usa Manizales como centro de recepción ([Portafolio](https://www.portafolio.co/historias-portafolio/abaco-2-000-toneladas-de-ayuda-movilizadas-502977) [V]).

### A5 · Emergencia 2026

| Fuente | Qué hay | Enlace | Uso |
|---|---|---|---|
| Copernicus EMS EMSR916 | Activación Rapid Mapping por el sismo M7,4 del 10 ago 2026, 12:30 UTC. Cita daños en Manizales. | [Página](https://mapping.emergency.copernicus.eu/news/earthquake-in-colombia-emsr916/) [V] | Citar en el informe. **No hay área de interés satelital para Manizales** según la Javeriana (abajo). |
| Javeriana Cali · clústeres de afectación | Tipifica clústeres. Manizales: clúster III "urbano de ladera", 361 puntos, a 81 km del epicentro. Usa el registro abierto de Naboo Intelligence (3.110 puntos, ~350 municipios; no oficial; sin enlace en el PDF). | [PDF](https://www.javerianacali.edu.co/sites/default/files/2026-08/clu%CC%81steres%20de%20afectacio%CC%81n%20del%20sismo%20del%2010%20de%20agosto%20de%202026.pdf) [V] | Argumento del problema. Buscar el registro de Naboo: [NV]. |
| HOT / OSM | Hashtag `#2026_LACH_CO_EQ`; proyecto de edificios 61749 en el Tasking Manager. Datos de OSM recortados en HDX. Imágenes Vantor (CC-BY-NC-4.0, con excepción para OSM), IGAC a 10 cm en 11 municipios y **dron de 5 cm de Manizales del 19 ago**. ChatMap para daños y refugios. | [Wiki de la activación](https://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Team/Open_Mapping_Hub_-_Latin_America_and_The_Caribbean/Activations/2026_Colombia_Earthquake_Response) [V] | Fondo de imagen y datos de edificios. Enlaces HDX/OAM exactos: [NV] (están en la wiki). |
| ReliefWeb / HDX | El hub [response.reliefweb.int/colombia/data](https://response.reliefweb.int/colombia/data) [V] listó conjuntos generales (EM-DAT, GDACS, IDMC, HAPI). No vi un dataset del sismo ahí. | | Contexto humanitario. |
| UNGRD / SGC | Geovisor UNGRD y "Emergencias UNGRD" en datos.gov.co (citados por la Javeriana [V]). Catálogo sísmico SGC [NV]. | | Contexto. |

### A6 · Precios y abastecimiento (SIPSA-DANE)

**Sí hay datos de Manizales.** El boletín de abastecimiento de enero 2026 incluye "Manizales, Centro Galerías" entre 32 mercados mayoristas de 23 ciudades; publica toneladas por mes, grupo de alimentos, procedencia y destino ([boletín ene 2026](https://www.dane.gov.co/files/operaciones/SIPSA/bol-SIPSAabastecimiento-ene2026.pdf) [V]). Hay boletines diarios, p. ej. [13 ago 2026](https://www.dane.gov.co/files/operaciones/SIPSA/bol-SIPSADiario-13ago2026.pdf) [V que existe; no lo abrí]. Uso: línea base de oferta y precio de la canasta. Es mensual o diario y mayorista, no por barrio.

## Parte B · Piezas técnicas

| Pieza | Recomendación y trampas | Docs |
|---|---|---|
| Bot Telegram | `python-telegram-bot` (async) con **polling** para la demo. No requiere URL pública. Webhook solo si se despliega con HTTPS. Trampa: un solo proceso hace polling por token; dos instancias dan error 409. `aiogram` es equivalente. | [python-telegram-bot](https://docs.python-telegram-bot.org) [NV] · [Bot API](https://core.telegram.org/bots/api) [NV] |
| Voz a texto (español) | Opción local gratis: `faster-whisper` (modelo `small` o `medium`) en CPU; descargar el modelo antes de la demo. Opción API: Whisper de OpenAI o Scribe de ElevenLabs. Precios: [NV]. Telegram entrega notas de voz en OGG/Opus: convertir con `ffmpeg`. | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) [NV] |
| OR-Tools Routing | CVRP: `AddDimensionWithVehicleCapacity` acepta una **lista** de capacidades, así que sirve para flota mixta [V]. Ventanas: dimensión de tiempo con enteros y *slack* positivo [V]. Nodos opcionales: `AddDisjunction(..., penalty)`. Una penalización mayor que la suma de distancias solo omite lo imprescindible [V]. Poner un límite de tiempo de búsqueda (p. ej. 5 s) y `GUIDED_LOCAL_SEARCH`. | [CVRP](https://developers.google.com/optimization/routing/cvrp) [V] · [VRPTW](https://developers.google.com/optimization/routing/vrptw) [V] · [Penalizaciones](https://developers.google.com/optimization/routing/penalties) [V] |
| osmnx | `graph_from_place("Manizales, Caldas, Colombia", network_type="drive")` o `graph_from_bbox`. Luego `add_edge_speeds` y `add_edge_travel_times`. Matriz de tiempos: un Dijkstra por origen con `networkx.single_source_dijkstra_path_length(G, n, weight="travel_time")`; con ~50 nodos son 50 corridas, segundos. Cierres: trabajar sobre una **copia** y quitar arcos con `G.remove_edges_from`; recalcular la matriz. Trampas: nombre de lugar depende de Nominatim (si falla, usar bbox o un `.osm` local); pendientes fuertes hacen que las velocidades por defecto sean optimistas; entregar solo nodos de la componente fuertemente conexa mayor. | [osmnx](https://osmnx.readthedocs.io/en/stable/user-reference.html) [NV: el fetch fue bloqueado] |
| Mapa web | **Streamlit + `streamlit-folium`** (todo en Python, sin front). Alternativa más rápida de servir: Folium genera un HTML estático. MapLibre solo si se necesita estilo vectorial. | [Folium](https://python-visualization.github.io/folium/) [NV] · [streamlit-folium](https://github.com/randyzwitch/streamlit-folium) [NV] |
| QR | `segno`: Python puro, sin Pillow, exporta SVG/PNG. `qrcode` también sirve (usa Pillow). El QR lleva solo un ID corto de la entrega; el detalle vive en la base de datos. | [segno](https://segno.readthedocs.io) [NV] |
| Despliegue | Demo: todo en un portátil. Para jurados remotos, túnel `cloudflared` o `ngrok` hacia Streamlit. Con polling el bot no necesita túnel. Railway, Render y Fly.io sirven para el piloto; planes gratuitos cambian y duermen: [NV]. | [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) [NV] |
| Geocodificación | Política de Nominatim (de memoria): máximo 1 petición por segundo, `User-Agent` propio, caché obligatoria, sin geocodificación masiva ([política](https://operations.osmfoundation.org/policies/nominatim/) [NV: fetch bloqueado]). Alternativa segura: **gazetteer propio** de ~131 barrios (CSV nombre, comuna, lat, lon) armado una vez con OSM `place=neighbourhood|suburb` y completado a mano. El LLM normaliza el nombre y se busca con coincidencia aproximada (`rapidfuzz`). | |

### Pila mínima recomendada

1. **Bot**: `python-telegram-bot` con polling.
2. **LLM**: Claude Haiku para extraer JSON (pedido, barrio, cantidad, vía bloqueada). Ver costos.
3. **Datos**: SQLite compartido + `gazetteer_barrios.csv`.
4. **Grafo**: osmnx `drive`, guardado en disco (`.graphml`) para no depender de la red en la demo.
5. **Optimizador**: OR-Tools con capacidades por vehículo, ventanas y `AddDisjunction`.
6. **Tablero**: Streamlit + `streamlit-folium`.
7. **QR**: `segno`.
8. **Voz**: `faster-whisper` local, solo si sobra tiempo.

Por qué: todo es Python, no hay front aparte, no hay URL pública que configurar, y la demo funciona aun si la red falla (grafo y gazetteer en disco). Un solo repositorio, dos procesos (bot y tablero) y una base SQLite.

## Parte C · Aliados y padrinos

Solo información institucional pública. Enlaces: [V] confirmados por una fuente que leí; el resto, [NV].

| Aliado | Rol posible | Qué pedirle (piloto 30–90 días) | Enlace |
|---|---|---|---|
| ABACO (red de bancos de alimentos) | Usuario, oferta de alimentos, validación | Datos de acopio y rutas actuales; probar el tablero en el corredor humanitario. Maneja >2.000 t, 9.470 familias, 36 municipios; Manizales es centro de recepción. | [Portafolio](https://www.portafolio.co/historias-portafolio/abaco-2-000-toneladas-de-ayuda-movilizadas-502977) [V] · [noticiasrcn](https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906) [V] · donaciones: donahoy.abaco.org.co/colombia2026 [V como cita] |
| Banco de Alimentos de Manizales / Arquidiócesis | Usuario y oferta | Nombre y canal oficial: **no pude confirmarlos**. Pedir inventario y lista de comités atendidos. | [NV] |
| Unidad de Gestión del Riesgo de Manizales (Alcaldía) | Datos y validación | Lista de albergues, vías cerradas, familias censadas; aval para operar como herramienta de apoyo. Es la fuente del reporte municipal de Asocapitales. | [Informe 27](https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-27.pdf) [V]; sitio manizales.gov.co [V que existe] |
| Gobernación de Caldas · Consejo Departamental de Gestión del Riesgo | Datos, validación | Acceso a actas y mapa de riesgo departamental. Existe un acta del consejo (15 may 2026). | [caldas.gov.co](https://caldas.gov.co/2-normativa/2-1-normativa-de-la-entidad/2-1-6-agenda-regulatoria/8612-acta-n4-consejo-departamental-de-gestion-de-riesgo-15052026/download) [V en búsqueda] |
| Cruz Roja Colombiana (Caldas) | Usuario, vehículos, voluntarios | Prueba en reparto; una nota de prensa la vincula con subsidios de arrendamiento. Confirmar rol local. | [Blu Radio](https://lakalle.bluradio.com/noticias/economia/te-toca-ir-a-la-cruz-roja-reclama-hoy-el-subsidio-de-arrendamiento-por-terremoto-so35) [titular V, no abierto] |
| PMA / WFP Colombia | Financiación, validación | Asistencia alimentaria: se anunció apoyo para 100.000 afectados. Pedir piloto de trazabilidad. | [telesur](https://www.telesurtv.net/colombia-onu-asistencia-100000-personas/) [titular V] · [Cambio](https://cambiocolombia.com/pais/articulo/2026/8/podemos-llegar-adonde-el-gobierno-tiene-dificil-acceso-nils-grede-director-en-colombia-del-programa-mundial-de-alimentos) [titular V] |
| Federación Internacional de la Cruz Roja (IFRC) | Financiación | Lanzó un llamamiento de 25 millones de francos suizos; explorar fondos para logística local. | [IFRC](https://www.ifrc.org/es/press-release/terremoto-en-colombia-ifrc-lanza-llamamiento-25-millones-francos-suizos-mientras) [titular V] |
| HOT (Humanitarian OpenStreetMap Team) | Datos, validación técnica | Mapear Manizales y vías; usar el dron de 5 cm. | [Wiki](https://wiki.openstreetmap.org/wiki/Humanitarian_OSM_Team/Open_Mapping_Hub_-_Latin_America_and_The_Caribbean/Activations/2026_Colombia_Earthquake_Response) [V] |
| Asocapitales | Difusión, réplica a otras capitales | Presentar el tablero como herramienta replicable; ya consolida reportes de ciudades. | [Informe](https://www.asocapitales.co/sites/default/files/2026-08/informe-terremoto-capitales-no-27.pdf) [V] |
| Universidad Nacional, IDEA-UNAL | Validación, datos de lluvia y amenaza | Aval académico, estaciones de lluvia, tesis o semilleros. | [idea.manizales.unal.edu.co](https://idea.manizales.unal.edu.co/publicaciones/eventos/Foro_Simposio_2019/dia3/3.pdf) [V en búsqueda] |
| Defensa Civil, Bomberos, UNGRD, Corpocaldas, SGC | Usuarios y datos | Puntos de coordinación y mapas de amenaza. | Sin enlace verificado [NV] |
| Cámara de Comercio de Manizales, Comité de Cafeteros, ANDI, Fenalco, Tecnoparque SENA, MinTIC/iNNpulsa | Financiación, vehículos, convocatoria de empresas | Flota de reparto y patrocinio de un piloto. | [NV] |
| Empresas locales (Luker, Normandy, Mabe, Efigas, CHEC-EPM, Súper de Alimentos) y sus fundaciones | Vehículos, alimentos, patrocinio | Camiones, bodegas, cofinanciar el piloto. Una nota general dice que el sector privado donó toneladas y kits; no verifiqué empresas de Caldas. | [La República](https://www.larepublica.co/empresas/la-ayuda-del-sector-privado-se-mide-en-toneladas-litros-y-kits-4460543) [titular V] |

## Parte D · Costos (estimación)

Fuente de precios: [página de precios de Claude Platform](https://platform.claude.com/docs/en/about-claude/pricing) [V]. Precios por millón de tokens: **Haiku 5.5** entrada US$0,10 y salida US$0,50; **Sonnet 5.5** US$2 y US$10. Batch: 50 % menos. La página advierte que los modelos recientes generan ~30 % más tokens para el mismo texto.

**Supuestos**: 1.500 tokens de entrada por pedido (instrucciones y ejemplos, más el mensaje) y 300 de salida (JSON). Sin caché.

| Modelo | Costo por pedido | 1.000 pedidos al día |
|---|---|---|
| Haiku 5.5 | ≈ US$0,0003 | ≈ US$0,30 |
| Sonnet 5.5 | ≈ US$0,006 | ≈ US$6 |

Con +30 % de tokens, sube proporcionalmente. El orden de magnitud: **centavos de dólar por cada 100 pedidos con Haiku**. El LLM no es el costo dominante.

| Rubro | Estimación |
|---|---|
| Telegram | Gratis (Bot API) [NV el enlace de política]. |
| Transcripción | Local con `faster-whisper`: sin costo por minuto, solo cómputo. Por API: precio [NV]. |
| Hosting | Plan básico de Railway/Render/Fly: precio [NV]. Un servidor pequeño basta. |
| WhatsApp Business API | Cobro por mensaje o conversación según categoría; tarifa para Colombia [NV]. Consultar la lista de tarifas de Meta antes de prometer cifras. |
| Datos y OR-Tools / osmnx | Gratis (código abierto; ODbL para OSM). |

## Qué no pude verificar

- Página de descarga de Geofabrik Colombia, política de Nominatim y docs de osmnx (fetch bloqueado).
- Nombre y canal del Banco de Alimentos de Manizales.
- Sitios de Cruz Roja Caldas, Defensa Civil, Bomberos, Corpocaldas, Cámara de Comercio, Cafeteros, ANDI, Fenalco, SENA, empresas.
- Registro de Naboo Intelligence (sin URL).
- SIMMA, mapas de amenaza SGC descargables, SIMAC en tiempo real.
- Precios de transcripción, hosting y WhatsApp.
- Cobertura real de OSM en Manizales (hay que medirla en el grafo).
