# DespachoX · Estado del arte y decisiones que salen de él

Viernes 20 de noviembre de 2026, 8:15 a. m. Síntesis de cinco informes hechos por agentes de investigación. Cada dato tiene su enlace en el informe de origen, en `docs/investigacion/`:

| Informe | Tema |
|---|---|
| `01_estado_del_arte_tecnico.md` | Logística humanitaria, ruteo con vías dañadas, herramientas abiertas, diseño de simulación |
| `02_referentes_latinoamerica.md` | Qué se hizo en la región y en Colombia, y la respuesta al sismo de 2026 |
| `03_capacidades_y_patentes_unal.md` | Qué patentes, grupos y datos de la UNAL existen de verdad y cuáles usar |
| `04_evidencia_del_problema.md` | Cifras con fuente para el componente 1 |
| `05_datos_abiertos_y_aliados.md` | Datos, pila técnica, aliados y costos |

**Advertencia de uso.** Los agentes verificaron en la web, pero nadie del equipo ha abierto todavía los enlaces. Antes de poner una cifra en el pitch, quien la use abre la fuente y la pasa a `docs/FUENTES.md`. Las cifras del sismo son preliminares y cambian según el corte: se citan siempre con fecha.

## 1. Lo que cambia en la estrategia

### El problema se cuenta distinto

La frase de la ficha («desabastecimiento en 48 horas», «embotellamientos críticos») **no tiene fuente pública** que la respalde para este sismo. No conviene repetirla como hecho. Lo que sí está documentado es más fuerte:

- La red de bancos de alimentos (ABACO) montó un corredor humanitario con Manizales como punto principal de acopio. Movió más de 2.000 toneladas para más de 9.000 familias. Su gerente nombra como reto principal el transporte y el acceso por vías rurales.
- Los cortes de energía rompieron la cadena de frío, y por eso se priorizaron enlatados. Eso justifica directamente ordenar el despacho por vencimiento.
- Dos salidas de Manizales seguían cerradas dos días después del sismo: Pereira–Chinchiná y Manizales–Fresno por Letras. Hay antecedentes de cierres por derrumbe en 2017, 2021 y 2023.
- En el centro de acopio de Bogotá se juntaron 933 toneladas en seis días y luego faltaban camiones y manos para despachar. El cuello de botella fue el despacho, no la donación.
- Las plataformas digitales que aparecieron en 2026 informan o recaudan. No se encontró ninguna que despache.

**Frase candidata para el pitch:** la reconstrucción tiene fondo y la donación tiene plataformas; a la última milla de la comida le falta una mesa de despacho.

### El usuario principal es ABACO y el Banco de Alimentos

Es el actor que ya opera desde Manizales, ya registra vencimientos y ya dijo en prensa cuál es su problema. El primer padrino que hay que buscar hoy es ese.

### El hueco que ocupamos es la integración

Hay herramientas que rutean (openrouteservice para desastres de HeiGIT, VROOM, Valhalla), otras que registran entregas (LMMS de World Vision, SCOPE del PMA, KoBo) y otras que recogen reportes (Ushahidi). No se encontró una abierta que una el flujo completo: pedido por chat, despacho de flota mixta que prioriza perecederos, recálculo ante cierres y trazabilidad. Nuestro aporte es ese flujo unido y medido. No hay que presentar el algoritmo como novedad.

Referentes para citar: Mission 4636 en Haití (2010) estructuraba y geolocalizaba mensajes de texto en minutos; Salva RS en Brasil (2024) se hizo en 48 horas, como web y sin aplicación, y unía los pedidos duplicados que circulaban por WhatsApp; HeiGIT montó ruteo con vías bloqueadas para el sismo de Venezuela de junio de 2026.

## 2. Conocimiento UNAL: qué usar y qué no

Hallazgo incómodo: el «banco de capacidades» del sitio parece de plantilla. **ERIS-UNAL, el software de ruteo adaptativo, el grupo de Logística y Transporte Multimodal y los datos de la ficha 04 no tienen rastro público.** No se construye sobre ellos salvo que la mesa los entregue hoy.

Paquete recomendado, en orden de fuerza:

| # | Capacidad | Dónde entra en el sistema | Qué confirmar hoy |
|---|---|---|---|
| 1 | Indicador A25 del sistema de alerta temprana de Manizales (IDEA-UNAL): lluvia acumulada de 25 días, con umbrales amarillo, naranja y rojo | Penalización de riesgo en cada tramo de la red vial: el optimizador evita laderas en alerta | Con Cristian Veloza: contacto en el IDEA para datos recientes por estación |
| 2 | Patente UNAL del empaque captador de etileno (solicitud PCT WO2016071875A1, Sede Bogotá) y el Laboratorio de Empaques y Vida Útil del ICTA | Campo `empaque_activo` en el lote, que alarga la vida útil en el modelo. Va como supuesto declarado, no como medición nuestra | Con Fernando Bernal: número y estado en la SIC, condiciones de uso. Google Patents la marca como cesada |
| 3 | Investigadores de la Sede Manizales en logística humanitaria: William Sarache, Diana Cárdenas, Juan Camilo López Vargas (tesis sobre la red de ayuda de Manizales) | Asesoría para validar la formulación y el papel del despachador | Pedir quince minutos de mentoría con alguno |
| 4 | Patente UNAL de control de vehículos con RFID (Ingeniería Bogotá) | Solo en el piloto: registro de llegada en acopios | Número y vigencia |
| 5 | Experiencia directa: Carlos es profesor de la Sede y la arquitectura viene de CARMEN | Todo el diseño | Nada |

No usar: ERIS y el software de ruteo si no se confirman, la patente de guadua del banco de capacidades (su número no tiene formato de la SIC), las patentes de zonas inseguras y de pararrayos, la película antimicrobiana por sí sola, y cifras de vida útil presentadas como resultados propios.

## 3. Diseño técnico que sale de la revisión

### Pila mínima

Todo en Python, sin front aparte y sin URL pública que configurar:

- **Bot:** python-telegram-bot con polling.
- **Extracción:** Claude Haiku con esquema JSON estricto y mensaje de confirmación de vuelta a quien pidió.
- **Datos:** SQLite y un listado propio de barrios de Manizales con coordenadas (131 barrios, 12 comunas). No depender de un geocodificador en línea.
- **Red vial:** osmnx, grafo de conducción recortado a Manizales y guardado en disco para que la demo no dependa de la red.
- **Optimizador:** OR-Tools. Plan B: VROOM.
- **Tablero:** Streamlit con streamlit-folium.
- **QR:** segno.
- **Voz:** solo si sobra tiempo.

Costo estimado de la extracción: del orden de US$0,0003 por pedido con Haiku, bajo el supuesto de 1.500 tokens de entrada y 300 de salida. Es una estimación.

### Receta del optimizador

- Una matriz de tiempos por tipo de vehículo, filtrando las vías que cada tipo puede usar.
- Capacidad por vehículo y acceso permitido por punto.
- Perecederos: ventana dura hasta el vencimiento menos un margen, y penalización por retraso según prioridad.
- Los pedidos pueden quedar sin atender con una penalización alta, para que el modelo siempre devuelva un plan.
- Búsqueda guiada con límite de tiempo de 10 a 30 segundos. Sin límite no se detiene.
- Cierre de vía: se borra el tramo, se recalculan las filas afectadas, cada vehículo arranca desde donde está y se vuelve a resolver. Si un punto queda sin acceso, se avisa al despachador.
- Unidades enteras: segundos y gramos.

**Función objetivo.** La literatura de logística humanitaria (Holguín-Veras, Campbell, Balcik) recomienda no minimizar costo sino tiempo de llegada y privación. Usamos un sustituto declarado: retraso ponderado por prioridad más una penalización fuerte por no entregar.

### Simulación defendible

- Red real de OpenStreetMap, entre 30 y 80 puntos, cerca del 20 % críticos.
- Pedidos que llegan en el tiempo, vencimientos entre 6 y 48 horas, cierres que solo se conocen cuando alguien los reporta.
- Al menos 30 semillas por escenario, las mismas para todas las políticas, con diferencia pareada e intervalo de confianza.
- **Tres políticas:** (1) línea base por orden de llegada, vehículo libre más cercano y desvío al toparse el cierre; (2) el optimizador sin recalcular; (3) DespachoX completo. La intermedia aísla cuánto aporta recalcular.
- Métricas: porcentaje a tiempo en puntos críticos, porcentaje de kilos perecederos vencidos, llegada media y máxima, demanda no atendida, equidad, kilómetros y tiempo de recálculo.
- La línea base no puede ser un hombre de paja: hay literatura que muestra políticas intuitivas casi óptimas.

### Advertencias sobre el modelo de lenguaje

Un estudio de 2025 muestra que los modelos fallan más justo en los mensajes de necesidad urgente y con errores de tipeo. Por eso: esquema estricto, confirmación al remitente, aprobación humana y mensajes con errores dentro de las pruebas.

## 4. Aliados para buscar hoy

| Aliado | Qué pedirle |
|---|---|
| ABACO y Banco de Alimentos de Manizales | Ser el usuario del piloto; datos de despachos de agosto |
| Unidad de Gestión del Riesgo de Manizales | Lista de albergues y vías cerradas; aval |
| PMA en Colombia | Financiación y validación |
| Cruz Roja (seccional Caldas) | Operador para probar el tablero |
| Equipo humanitario de OpenStreetMap (HOT) | Mapeo de vías y la ortofoto de dron de Manizales del 19 de agosto |
| IDEA-UNAL | Datos de lluvia y respaldo académico |

Compatibilidad que da legitimidad: el sistema de suministros humanitarios de la OPS (SUMA/LSS) está en la normativa colombiana. Exportar la trazabilidad en un formato compatible es un buen hito del día 60.

## 5. Vacíos que hay que cerrar hoy en persona

- ¿Cuánto duraron los cierres de las vías de Manizales y cuáles fueron? Solo hay prensa de los dos primeros días.
- ¿Hubo faltantes de alimentos o donaciones vencidas en Manizales? No hay cifra pública.
- ¿Cuántas familias recibieron ayuda alimentaria en Manizales y desde qué centros de acopio?
- ¿Quién dirige el Banco de Alimentos de Manizales y cómo despacha hoy?
- ¿Existen ERIS-UNAL, el software de ruteo y los datos de la ficha 04?

Cualquiera de estas respuestas, dicha por alguien de gestión del riesgo o de un organismo de socorro y citada con nombre y cargo, vale más que una cifra de prensa.

## 6. Límites de esta revisión

- Varias consultas web de los agentes quedaron bloqueadas. Lo no verificado está marcado en cada informe.
- La prensa local (La Patria, BC Noticias) y los sitios de la Alcaldía y la Gobernación no se consultaron directamente.
- Las cifras de víctimas y damnificados difieren entre fuentes y fechas. Los informes registran todas las versiones.
