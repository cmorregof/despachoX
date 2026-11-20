# 03 · Capacidades y patentes UNAL para DespachoX

Investigación del 20 nov 2026. Vertical 04, "Logística y abastecimiento".
Regla: cada dato lleva enlace. Lo que no pude confirmar dice **no verificado**.

## 0. Primero, qué es real en el sitio de la hackathon

Revisé el código del sitio (bundle `assets/index-*.js` de https://8wf9bsh8.insforge.site/). Hay dos fuentes distintas:

- **Lista de patentes por vertical.** Los tres títulos de la vertical 04 están ahí, tal cual. Al menos dos corresponden a tecnologías reales de la UNAL (ver sección 1).
- **"Banco de capacidades" (fichas UNAL-CAP-001 a 008).** Aquí está ERIS-UNAL (UNAL-CAP-004), la red acelerográfica (003), la metodología de Cardona (005) y una "Patente NC2019/00481" de guadua (002). Varias fichas parecen plantilla: correos genéricos, cifras redondas, formatos raros. El número "NC2019/00481" no tiene el formato usual de la SIC (siete dígitos tras el año). **No verificado.**
- **Ficha de la vertical 04.** Lista "Grupo de Investigación en Logística y Transporte Multimodal", "Software UNAL de ruteo vehicular adaptativo", "Laboratorio de Embalajes y Conservación de Alimentos Perecederos" y "Red vial terciaria georreferenciada". No encontré ninguno con ese nombre exacto en fuentes públicas.

Conclusión: tratar el banco de capacidades como **hipótesis**, no como hecho. Confirmar en la mesa antes de nombrarlo en el pitch.

## 1. Las tres patentes de la vertical 04

| | (a) Control inteligente de vehículos de transporte público | (b) Composición captadora de etileno | (c) Película antimicrobiana contra antracnosis |
|---|---|---|---|
| ¿Existe? | Sí. Tecnología con patente de invención otorgada por la SIC, según la [Agencia de Noticias UNAL (2018)](https://agenciadenoticias.unal.edu.co/detalle/sistema-para-control-vehicular-recibe-patente-de-invencion). Aparece con este título en el [portafolio de tecnologías de Extensión Bogotá](https://extension.bogota.unal.edu.co/index.php/portafolio-de-tecnologias/plataforma-para-el-control-inteligente-de-vehiculos-de-transporte) (hoy da 404). | Sí, como solicitud. [WO2016071875A1](https://patents.google.com/patent/WO2016071875A1/es), "Empaque polimérico que retarda el proceso de maduración y senescencia de productos vegetales frescos". | Hay tesis y prensa. **No encontré número de patente.** [Tesis 2019](https://repositorio.unal.edu.co/handle/unal/75629); [Agencia UNAL 2023](https://agenciadenoticias.unal.edu.co/detalle/bolsas-antihongos-para-frutas-tropicales). |
| Número | **No verificado.** La nota no da el número. | PCT/IB2015/058582; prioridad colombiana CO14245775 ([Google Patents](https://patents.google.com/patent/WO2016071875A1/es)). Número de concesión SIC **no verificado**. | **No verificado.** |
| Inventores / equipo | Profesores y estudiantes de Ingeniería, con la empresa Data Tools S.A.; cita a Félix Vega (Ing. Eléctrica y Electrónica) ([nota](https://agenciadenoticias.unal.edu.co/detalle/sistema-para-control-vehicular-recibe-patente-de-invencion)). Un póster afín firma Figueroa, Vega Stavro y Pedraza Bonilla ([EATIS 2016](https://www.eatis.org/eatis2016/EATIS-2016/posters/EATIS_2016_submission_33.pdf)). | César Augusto Sierra Ávila, Sugey Maryuri Martínez Gómez, Luis Alejandro Gutiérrez Carranza, Ricaurte Rodríguez Angulo ([Google Patents](https://patents.google.com/patent/WO2016071875A1/es)). | Tesis de Richard José Solano Gómez, dir. César A. Sierra Ávila y Mónica C. Ávila Murillo ([repositorio](https://repositorio.unal.edu.co/handle/unal/75629)). Nota 2023: Lissette Ariza Corredor, con César Sierra y Diego Alzate ([Agencia UNAL](https://agenciadenoticias.unal.edu.co/detalle/bolsas-antihongos-para-frutas-tropicales)). |
| Sede / facultad | Bogotá, Facultad de Ingeniería. | Bogotá (Sierra es de Ciencias, según la [nota 2023](https://agenciadenoticias.unal.edu.co/detalle/bolsas-antihongos-para-frutas-tropicales)). | Bogotá; tesis en Ciencias Agrarias (Maestría en Ciencia y Tecnología de Alimentos). |
| Año | Patente anunciada el 1 mar 2018. | Prioridad 2014; PCT publicada 2016. | Tesis 2019; nota 2023. |
| Qué protege, en llano | Etiquetas RFID pasivas en el parabrisas. Lectores fijos en paraderos registran ID, hora y lugar, y suben a la nube. Sirve para auditar rutas y horarios sin GPS. Probado con 600 vehículos en el campus y 150 buses Bogotá–Chía. | Película de polietileno o polipropileno con 0,5–5 % de un agente que capta etileno (escualeno, diludina, AOA, ésteres). La reivindicación 10 habla de más de 4 semanas de vida útil a menos de 10 °C. | LDPE con ácido láurico. Inhibe *Colletotrichum*. Con 5 % la fruta duró dos semanas más sin síntomas ([nota](https://agenciadenoticias.unal.edu.co/detalle/bolsas-antihongos-para-frutas-tropicales)). |
| Estado | Concedida en Colombia según la nota. Vigencia **no verificada**. | Google Patents la marca "Ceased"; la fase europea no prosperó. Estado en Colombia **no verificado**. | **No verificado** que exista como patente. |

### Pertinencia honesta para DespachoX

| Patente | Pertinencia | Integración real |
|---|---|---|
| (b) Captadora de etileno | **Media-alta.** Ataca el indicador "desperdicio de perecederos < 5 %". | **Prototipo (24 h):** en el modelo de producto, campo `empaque_activo`. Si es verdadero, la ventana de vida útil se alarga. El optimizador lo usa como restricción de tiempo. El factor debe ir marcado como supuesto, porque los datos son de gulupa en frío, no de mercado de ayuda a temperatura ambiente. **Piloto (30-90 días):** prueba física con el laboratorio de empaques. |
| (c) Antimicrobiana antracnosis | **Baja-media.** Es solo para tomate de árbol y otros frutales con antracnosis. No es la canasta típica de ayuda. | Solo como categoría de producto en el catálogo de perecederos. Mencionarla junto a (b), no sola. Piloto. |
| (a) Control de transporte público (RFID) | **Baja para hoy.** Necesita lectores fijos en la vía. Tras un sismo eso no existe. El seguimiento de flota en el prototipo será por chat y GPS del celular. | **Piloto:** lectores RFID en centros de acopio y puntos de entrega como "check-in" automático, que alimenta la trazabilidad QR. Decirlo así, no como base de la plataforma. |
| Monitoreo de zonas inseguras; IoT pararrayos | **Decorativas.** No encontré fuentes públicas de ninguna de las dos. No se relacionan con el despacho. | No usar. |

## 2. Grupos e investigadores reales

| Persona / grupo | Sede | Línea verificada | Por qué sirve |
|---|---|---|---|
| **William Ariel Sarache Castro**, Ing. Industrial | Manizales | Logística humanitaria. Coautor de "Algunas tendencias de investigación en logística humanitaria" ([NOVUM 2016](https://revistas.unal.edu.co/index.php/novum/article/view/65371)). Dirigió la tesis sobre capacidades de la red de ayuda humanitaria de Manizales ([tesis 2017](https://core.ac.uk/download/427644456.pdf)). | El asesor más directo. Conoce los actores de la respuesta en Manizales. |
| **Diana María Cárdenas Aguirre** y **Juan Camilo López Vargas** | Manizales | Coordinación interorganizacional en preparación de emergencias, con modelo basado en agentes para Manizales ([tesis doctoral 2021](https://redcol.minciencias.gov.co/Record/UNACIONAL2_78312a5d1058d34019dbf1c3c6a288ee/Details)). Red local de preparación de Manizales ([tesis 2022](https://repositorio.unal.edu.co/items/3d2ca0b2-72a0-4588-a83c-fa1f031a0c4b/full)). | Validan quién decide y cómo fluye la información. Respaldan el "despachador humano" y el canal por chat. |
| Grupo "Innovación y Desarrollo Tecnológico" / "Producción, Operaciones y Logística" | Manizales | Citados en la [tesis 2017](https://core.ac.uk/download/427644456.pdf). Código y categoría GrupLAC **no verificados**. | Nombre institucional para el pitch, si la mesa lo confirma. |
| **Santiago Ruiz Herrera** | Manizales | Dirigió tesis de VRP con NSGA-II para reparto de alimentos en la región cafetera ([repositorio](https://repositorio.unal.edu.co/handle/unal/78373)). | Antecedente local de ruteo con objetivo de menos desperdicio. |
| **Omar Darío Cardona**, IDEA | Manizales | Gestión del riesgo. Coautor del estudio multiamenaza de Manizales (sismo, deslizamiento, volcán) ([IJDRS 2017](https://link.springer.com/article/10.1007/s13753-017-0135-8)). | Asesor para el peso de riesgo de los tramos. Su metodología holística es de vulnerabilidad social, no de ruteo. |
| **IDEA – SIMAC / red SAT** | Manizales | Red de 20 estaciones; datos cada 5 minutos ([boletín IDEA](https://idea.manizales.unal.edu.co/publicaciones/boletines_ambientales/boletin147.pdf)). | Fuente de lluvia para riesgo de cierre de vías. |
| **César A. Sierra Ávila** y **Diego A. Castellanos** (ICTA) | Bogotá | Empaques activos. ICTA tiene un Laboratorio de Empaques y Vida Útil que evalúa empaques captadores de etileno y antimicrobianos ([ICTA](https://icta.unal.edu.co/en/infrastructure/labs/packaging)). ActiPack: bolsa de atmósfera controlada, TRL7, de 40 a 60 días a 6–8 °C ([ICTA ActiPack](https://icta.unal.edu.co/en/research/developed-technologies/actipack)). | Es el laboratorio real más cercano al "Laboratorio de Embalajes" del sitio. Contacto para el piloto. |
| **Grupo VITRA (Vías y Transporte)** | Medellín, Facultad de Minas | Planeación de transporte, infraestructura vial; estudio de carga del Valle de Aburrá ([presentación](https://minas.medellin.unal.edu.co/vicedecanaturadeinvestigacion/images/encuentro_grupos_2019/13_Vitra.pdf)). | Aliado secundario para la red vial. No trabajan logística humanitaria. |
| Félix Vega / Data Tools | Bogotá | Patente (a). | Solo si se usa la patente (a) en el piloto. |

No verificados: "Grupo de Investigación en Logística y Transporte Multimodal", grupo SEPRO con línea humanitaria, GICO Medellín. No encontré fuentes que los confirmen.

## 3. Datos y recursos abiertos

| Recurso | Qué ofrece | Uso en DespachoX |
|---|---|---|
| **Indicador A25 de lluvia** (IDEA/SIMAC) | Lluvia antecedente de 25 días. Umbrales: amarilla 200–300 mm, naranja 300–400 mm, roja ≥ 400 mm. 14 estaciones en el reporte 2020 ([PDF IDEA](https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf)). | **Lo mejor para hoy.** Asignar a cada tramo la estación más cercana. Penalizar el tramo según el nivel de alerta. Así el optimizador evita rutas que quizá se cierren. |
| Boletines climatológicos CDIAC | Mensuales y semanales de Caldas ([ejemplo 2025](https://cdiac.manizales.unal.edu.co/publicaciones/2025/Semanales/2025-19_Boletin_05al11mayo02025_VF.pdf)). | Calibrar escenarios de lluvia para la demo. |
| Estudio multiamenaza de Manizales | Susceptibilidad a deslizamiento con red neuronal de 29 variables. Umbral detonante de 150 mm en 25 días. Microzonificación sísmica con 1275 nodos. Red acelerográfica de 12 sitios ([IJDRS 2017](https://link.springer.com/article/10.1007/s13753-017-0135-8)). | Justifica el peso de riesgo por tramo. Las capas en sí no son públicas: pedirlas. |
| Repositorio UNAL | Tesis citadas arriba ([repositorio](https://repositorio.unal.edu.co/handle/unal/78373)). | Antecedentes y citas para el pitch. |

Nota: el umbral del artículo (150 mm) no coincide con el del SAT (200 mm). Usar los niveles del SAT y citar la fuente.

No verificados: geoportal UNAL con red terciaria y pendientes; censo de bodegas frías; demanda calórica por cuadrante. Solo aparecen en el sitio de la hackathon.

## 4. ERIS-UNAL y el "software de ruteo adaptativo"

- **ERIS-UNAL:** solo existe en el sitio de la hackathon (ficha UNAL-CAP-004). Busqué el nombre y el nombre largo. **No hay rastro público.** La ficha lo atribuye a "innovate (Facultad de Ingeniería Bogotá)". Existe un sitio "innovate" de esa facultad, pero no pude revisarlo, y no hay evidencia de que tenga este software.
- **"Software UNAL de ruteo vehicular adaptativo ante bloqueos viales dinámicos":** **no hay rastro público.**
- Recomendación: preguntar en la mesa. Si existen y dan token, se integran como servicio. Si no, **no nombrarlos**. Un jurado UNAL lo detectaría.

## 5. Paquete de conocimiento UNAL recomendado

Ordenado por fuerza.

**1. A25 del SAT Manizales (IDEA-UNAL / SIMAC) como riesgo de tramo.**
- Dónde: grafo vial. Costo del tramo = tiempo × (1 + penalización por nivel A25). Rojo ≥ 400 mm puede bloquear preventivamente.
- Pedir hoy (Cristian Veloza, charlas y retos): contacto IDEA para datos recientes o en tiempo real. Si no llegan, usar los reportes públicos.
- Pitch: "Nuestras rutas esquivan las laderas que la red de lluvias de la UNAL ya marca en alerta, antes de que se caigan."

**2. Patente de empaque captador de etileno (Sierra Ávila et al., UNAL) + Laboratorio de Empaques y Vida Útil del ICTA.**
- Dónde: modelo de perecederos. Campo `empaque_activo` que alarga la ventana de vida útil. El optimizador prioriza lo que vence antes. El tablero mide desperdicio contra la meta de 5 %.
- Pedir hoy (Fernando Bernal, patentes): número y estado en la SIC; condiciones de uso académico; contacto del ICTA para el piloto.
- Pitch: "Combinamos un empaque patentado por la UNAL, que retrasa la maduración, con rutas que despachan primero lo que vence primero."

**3. Logística humanitaria en Manizales: Sarache, Cárdenas y López Vargas.**
- Dónde: diseño del rol del despachador humano y de los actores (Cruz Roja, Defensa Civil, comités barriales). Respaldo para el piloto.
- Pedir hoy (Fernando Bernal, mentorías): si alguno puede dar mentoría hoy o mañana.
- Pitch: "El flujo de decisión se basa en el mapa de actores de la red de ayuda de Manizales, estudiado por la UNAL."

**4. Patente RFID de control de vehículos (Ingeniería Bogotá), solo para el piloto.**
- Dónde: lectores en centros de acopio y puntos de entrega. Registran llegada sin intervención y alimentan la trazabilidad QR.
- Pedir hoy (Fernando Bernal): número de patente, vigencia, condiciones de licencia.
- Pitch: "En el piloto, la patente RFID de la UNAL cierra la trazabilidad: cada llegada queda registrada sola."

**5. (Condicional) ERIS-UNAL.** Solo si la mesa confirma que existe y entrega acceso.

### Qué NO usar

- ERIS-UNAL y el "software de ruteo adaptativo" si no se confirman en la mesa.
- "Patente NC2019/00481" de guadua: es de otra vertical y su número no tiene formato SIC.
- Dispositivo de zonas inseguras y pararrayos IoT: sin relación con el despacho.
- La patente (c) sola: es para tomate de árbol.
- La metodología holística de Cardona como "modelo de ruteo": mide vulnerabilidad social, no rutas. Sirve como mucho para priorizar barrios, y solo si hay datos.
- Cifras de vida útil como resultados propios. Son de laboratorio en frío. Presentarlas como supuesto del modelo.
