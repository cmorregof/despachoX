# Citas del manuscrito: qué se verificó, qué falta y qué no cuadra

Rama `manuscrito`, 21 de noviembre de 2026, madrugada. Lo escribió un agente de Fable para Carlos.

**Cómo leer esto.** `refs.bib` solo trae referencias verificadas: los artículos, en el registro de Crossref de su DOI (`https://api.crossref.org/works/<DOI>`) o en la página del editor o del repositorio; la prensa y los documentos oficiales, abriendo la página con un lector automático. Lo que no se pudo verificar se cita en `main.tex` como `\cite{PORVERIFICAR_<clave>}` y sale como «(?)» en el PDF, a propósito. La regla del equipo sigue en pie: antes de usar en público una cifra de prensa, una persona del equipo abre el enlace y la pasa a `docs/FUENTES.md`. La lectura automática no la reemplaza.

## 1. Pendientes: las dos citas «(?)» del PDF

| Clave en `main.tex` | Qué respalda | Qué hay en el repositorio | Qué falta |
|---|---|---|---|
| `PORVERIFICAR_carmen` | Origen de la regla «el modelo lee, el código calcula, una persona decide» (sección 4.1) | `docs/ESTRATEGIA.md` y `docs/FICHA.md`: CARMEN, proyecto 56031 de Minciencias | Decisión de Carlos: si se nombra CARMEN y cómo se cita (informe, artículo o código del proyecto) |
| `PORVERIFICAR_patente37476` | Factor 1,2 del empaque captador de etileno, cota inferior en gulupa a 8 °C (sección 5.2) | `docs/investigacion/06_patentes_sipi.md` y `07_patentes_a_fondo.md`: certificado 37476, solicitud CO 14-245775, folio 18, figuras 1 y 2; PCT WO2016071875A1 | Registro de la SIC con titular, fecha y estado (anualidad 2026), y el texto de la solicitud. Una búsqueda web de WO2016071875A1 no lo encontró esta noche. Decidir si el manuscrito menciona la patente: hoy el empaque no actúa en la simulación (ver sección 4) |

Resueltas esta noche, después del primer borrador: la tesis de Terlien (1996) quedó verificada en el portal de la Universidad de Twente (`terlien1996modelling`), y la ración de 555 g quedó apoyada en la tabla comparativa de raciones que aloja el Logistics Cluster (`logcluster_commodities`). Sobre esa tabla: el texto extraído da para ACNUR cereal 400 g (450 g en la variante de 2.100 kcal), leguminosas 60 g y aceite 25 g; el azúcar (15 g) y la sal (5 g) aparecen sin agencia clara. Los 555 g son la suma del equipo (450 + 60 + 25 + 15 + 5), y así lo dice el manuscrito. La página de ACNUR que cita `docs/datos/demanda.md` (`https://emergency.unhcr.org/es/print/pdf/node/504`) no trae la tabla.

## 2. Verificadas (están en `refs.bib`)

| Clave | Cómo se verificó (21 nov 2026, salvo indicación) | Nota |
|---|---|---|
| `holguinveras2013objective`, `holguinveras2012unique`, `holguinveras2016deprivation`, `campbell2008routing`, `balcik2008lastmile`, `huang2012relief`, `ozdamar2004emergency`, `pillac2013review`, `anayaarenas2014relief`, `delatorre2012disaster`, `beamon2008performance`, `cook2017dispatching`, `escribanomacias2020endogenous`, `munro2013crowdsourcing`, `imran2014aidr`, `boeing2017osmnx` | Registro de Crossref del DOI (autores, título, revista, volumen, número, páginas) | `munro2013crowdsourcing`: en línea desde julio de 2012, número impreso de abril de 2013; se cita 2013 |
| `gralla2018humanitarian` | Búsqueda en Crossref y registro del DOI; resumen en RePEc (`ideas.repec.org/a/eee/ejores/v269y2018i2p436-450.html`) | El DOI correcto es 10.1016/j.ejor.2018.02.012. El 10.1016/j.ejor.2018.02.023 es otro artículo |
| `holguinveras2014material` | Búsqueda en Crossref; resumen en la ficha de UC Davis ITS (`itspubs.ucdavis.edu/publication_detail.php?id=2380`) | Crossref titula «Material Convergence: Important and Understudied Disaster Phenomenon»; UC Davis antepone «An» |
| `hsu2007vehicle` | Búsqueda en Crossref; resumen en el repositorio de NYCU | |
| `balcik2008lastmile`, `huang2012relief`, `campbell2008routing` (contenido) | Resúmenes en IAOR (`iaorifors.com/paper/66066`) y RePEc | Lo que el manuscrito les atribuye coincide con el resumen |
| `terlien1996modelling` | Portal de investigación de la Universidad de Twente | Tesis doctoral, Universidad de Utrecht, 1996, serie ITC Dissertation, ISBN 90-6164-115-2. El portal escribe «Columbia» en el título |
| `logcluster_commodities` | PDF alojado por el Logistics Cluster | Sin editor ni fecha en el documento; ver la sección 1 |
| `cook2017dispatching` (contenido) | Resumen en RePEc | La política simple es «óptima o cercana a la óptima en la mayoría de las situaciones» |
| `imran2016twitter` | Página del recurso en CrisisNLP | LREC 2016, Portorož, pp. 1638–1643 |
| `mcdaniel2024zeroshot` | Página de arXiv 2410.00182 | Preprint, no revisado por pares |
| `imran2025robustness` | Página de QCRI con el DOI 10.1145/3696410.3714511 | Sin páginas en la ficha |
| `engineroom2023chatbots` | Página de The Engine Room | Publicado el 2 ago 2023; investigación «con apoyo» de la IFRC y del Global Disaster Preparedness Center |
| `ortools_routing`, `ortools_routing_options` | Página «How to cite OR-Tools» y página «Routing options» de Google | La página de cita recomienda la v9.12; en el entorno del equipo está la 9.15 y `requirements.txt` no fija versión. Conviene fijarla antes de publicar |
| `rueda2021coordinacion` | Ficha del repositorio UNAL (`repositorio.unal.edu.co/handle/unal/80456`) | 16 reglas, cinco explican el 78 % de las decisiones: lo dice el resumen |
| `ocampo2019costos` | Portada y tabla 14 de la tesis (repositorio UNAL) | Ver discrepancia (i) |
| `ley1581` | Normograma de la DIAN | 17 oct 2012; Diario Oficial 48.587 del 18 oct 2012; art. 26 prohíbe transferir datos a países sin nivel adecuado de protección, con excepciones |
| `decreto2026emergencia` | PDF alojado por Camacol | Ver discrepancia (f) |
| `ifrc2026dref` | PDF de la IFRC, descargado y leído (texto extraído) | DREF publicado el 14 ago 2026; AccessRC para identificar hogares y KoboCollect como contingencia sin conexión |
| `invias767` | Enlace y descripción completos en `docs/datos/vias_y_riesgo.md`; no se volvió a consultar esta noche | Las tres cifras del texto (87 registros, 9 h 46 min, 0 a 6 min) son cálculos del equipo |
| `idea2020a25` | PDF del IDEA | Umbrales de 200, 300 y 400 mm; 14 estaciones; elaboró Ing. John Alexander Pachón G. |
| `idea2018boletin145` | PDF del IDEA | Marzo de 2018; autores Pachón Gómez, Mejía Fernández y Zambrano Nájera |
| `dane2019manizales` | PDF del DANE | 2,9 personas por hogar en Manizales y 3,0 en Caldas |
| `paho_lss` | Página de la OPS | Ver discrepancia (c) |
| `alcaldia2026carpas`, `alcaldia2026turnos`, `alcaldia2026concejo`, `ani2021cierre` | Página de cada fuente | `alcaldia2026concejo`: calamidad pública vigente hasta el 9 ago 2027 |
| `portafolio2026flypass`, `rcn2026demolicion`, `rcn2026corredor`, `rcn2026abaco`, `rcn2026campin`, `rcn2026senal`, `larepublica2026abaco`, `semana2026vias`, `escaldas2026kits`, `vanguardia2026procuraduria`, `elcolombiano2020providencia`, `delira2024salvars`, `heigit2026venezuela` | Página de cada nota: titular, fecha y la frase que respalda la cifra | Ver discrepancias (a), (b), (d), (e), (g), (h), (k) y (l) |

## 3. Discrepancias entre las fuentes y los documentos del equipo

El manuscrito sigue a la fuente. Conviene corregir también `docs/FICHA.md`, `docs/FICHA_CORTA.md` y el guion del pitch.

- **(a) Cierre de Letras.** Semana (12 ago) da cierre total de Manizales–Fresno entre los km 36+800 y 40+300, en Herveo (Tolima), y no nombra el Alto de Letras. La ficha dice «Manizales–Fresno en el Alto de Letras, entre los kilómetros 36 y 40». El nombre de Letras sale de otras fuentes (Minuto30, #767).
- **(b) SMS.** Noticias RCN (11 ago) atribuye la recomendación de priorizar mensajes de texto a la CRC, no al MinTIC. Las cifras de estaciones caídas (3.403 de 7.379 en siete departamentos; 28 % en Caldas) sí son del informe del MinTIC.
- **(c) SUMA/LSS.** La página de la OPS dice que en LSS «los sitios pueden registrar solicitudes de artículos» (en la aplicación de Windows). La ficha y `docs/PROBLEMA.md` dicen que SUMA «no recibe pedidos». Lo que la página no menciona es planear rutas.
- **(d) Retos de ABACO.** La nota de RCN del 18 de agosto cita como reto principal «el transporte, la articulación y la llegada al territorio». El almacenamiento y las vías rurales aparecen como condiciones para mover la ayuda, no como una lista ordenada. La ficha los presenta en otro orden.
- **(e) Cruz Roja como operador.** La nota de la Alcaldía del 31 de agosto habla de «nuestro operador logístico» desde las instalaciones de la Cruz Roja y de turnos organizados, pero no nombra a la Cruz Roja Seccional Caldas como operador. La investigación 11 lo afirma con otra fuente del 12 de agosto, que no se abrió.
- **(f) Decreto.** La copia de Camacol deja en blanco el número y la fecha («DECRETO NÚMERO DE 2026»); el número 1261 sale del nombre del archivo. Da dos profundidades: 103,4 km (boletín del SGC) y unos 94 km (citando el Decreto 1171). Hay que revisar el Diario Oficial.
- **(g) Retraso del #767.** Las 9 h 46 min se cuentan desde el sismo; desde la hora de inicio que guarda el propio registro (1:00 p. m.) son 4 h 20 min. Los 0 a 6 minutos de 2025 se cuentan desde la hora de inicio. La ficha compara las dos cosas como si fueran la misma; el manuscrito da las dos.
- **(h) Es Caldas.** La nota de los kits del 18 de agosto está en `escaldas.com`, que se presenta como «Es Caldas | Noticias de la región», con autora. La ficha la cita como «Gobernación». Confirmar si es el medio oficial de la Gobernación.
- **(i) Velocidades.** La tabla 14 de la tesis de 2019 da «velocidades asignadas» al bus a combustión por tipo de vía y pendiente: principal 21,8 a 24,2 km/h, colectora 16,2 a 17,5 km/h, y 22,6 km/h de media en la ruta (sección 5.3). La ficha dice «medido con GPS»; no se confirmó el método. Autora: Daniela Ocampo González; director: Diego Alexander Escobar García.
- **(k) Portafolio.** Además de 41.163 kg entregados y 404.587 kg en acopio, la nota da 157.164 kg en tránsito. El manuscrito incluye las tres cifras.
- **(l) El Campín.** La nota pide montacargas, camiones y transportadores a empresas, y voluntarios para clasificar y empacar. No dice «para despachar».

## 4. Lo que encontré en el código y no está en los documentos

Van como comentarios `% CODE-vs-DOC` en `main.tex`.

- El surtido (primero lo que vence primero) es una regla que corre **antes** del optimizador, y el optimizador no puede cambiarlo. Asignación y ruteo son secuenciales, no conjuntos.
- El costo de cada arco incluye el tiempo de servicio del nodo de origen (600 s por parada atendida), además del tiempo de viaje.
- Cada vehículo hace un solo viaje por plan. En el producto el recálculo lo dispara un cierre confirmado o el despachador; las tandas de 30 minutos y el regreso de cada vehículo son de la política simulada.
- El esquema admite vehículos `a_pie`, pero el optimizador solo modela camión, campero y moto. Drones y tracción animal, que nombra la ficha del reto, no están.
- En la simulación el factor del empaque nunca actúa: los productos se llaman «abarrotes» y «perecedero», que no son fruta.
- Personas por familia: 4 en `entrada/raciones.py` (supuesto sin fuente) y 2,9 en el escenario público (DANE). Kilos por familia: 10 en el optimizador y 12 en la simulación.
- `FACTOR_CRITICO = 3` se adoptó después de un barrido que no cumplió la regla escrita antes de correrlo. Si la corrida de esta noche usa semillas de 20261120 a 20261179, se solapa con las del barrido y la confirmación, y hay que decirlo.
