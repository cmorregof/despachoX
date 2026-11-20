# Ficha · componentes 4, 5 y 6 (borrador para la mentoría 1)

Borrador del capitán, viernes 10:55 a. m. En la mentoría 1 estos tres componentes se aceptan como borrador; en la mentoría 2 deben estar completos. Suman 40 puntos. Lo marcado **[por llenar]** depende de una conversación de hoy o de la simulación de esta noche. Cuando esté maduro se pasa a `docs/FICHA.md`.

## 4. Plan de 30 a 90 días (15 puntos)

La rúbrica pide hitos, entregables, responsables, recursos y mecanismo de validación.

| Día | Hito | Entregable | Responsable | Recursos | Validación |
|---|---|---|---|---|---|
| 0 a 15 | Acuerdo con un operador (Banco de Alimentos de Manizales o un organismo de socorro) | Carta de intención y acceso a registros de despachos de agosto, sin datos personales | Samuel | Acompañamiento del Parque de Innovación | Carta firmada |
| 15 a 30 | Reconstrucción en frío | Informe que compara los despachos reales de agosto con el plan que habría dado DespachoX | Carlos y el ingeniero industrial | Registros del operador, cómputo propio | Entregas a tiempo, kilómetros y kilos vencidos: real contra reconstruido |
| 30 a 45 | Canal de WhatsApp y modo sin conexión | Bot en WhatsApp Business; la confirmación de entrega se guarda en el teléfono y sincroniza después | Samuel | Cuenta de WhatsApp Business, servidor pequeño | Veinte pedidos de prueba de punta a punta |
| 45 a 60 | Simulacro en territorio | Jornada con un comité barrial (Comuna San José), dos o tres vehículos, pedidos por chat, QR y un cierre vial simulado | Jacobo y el equipo | Vehículos del aliado, territorio de prueba que ofrece la hackathon | Tiempo de pedido a entrega, porcentaje de paquetes trazados, encuesta corta al despachador |
| 60 a 75 | Riesgo de ladera en las rutas | Indicador de lluvia acumulada del IDEA-UNAL conectado como penalización por tramo | Carlos | Datos del IDEA | Rutas que evitan tramos en alerta en una semana de lluvias registrada |
| 75 a 90 | Operación en sombra y decisión | Dos semanas junto al despachador real: el sistema propone, él decide. Informe final y acuerdo de adopción o cierre | Todo el equipo | Horas del operador | Porcentaje de planes que el despachador aprueba sin cambios; decisión de adopción |

Criterio de parada honesto: si en la reconstrucción en frío DespachoX no mejora al despacho real en entregas a tiempo, el piloto se rediseña antes del simulacro.

**[por llenar]** Nombre del operador aliado y de la persona de contacto.

## 5. Viabilidad y aliados (15 puntos)

### Factibilidad técnica

- Todo el sistema corre en un portátil: Python, SQLite, red vial de OpenStreetMap en disco y un optimizador abierto (OR-Tools). No requiere infraestructura nueva del aliado.
- El usuario final no instala nada: escribe por un chat que ya usa.
- Si falla internet o el modelo de lenguaje, el pedido entra como texto y el despachador lo digita. El optimizador sigue funcionando sin conexión; el fondo del mapa necesita red.

### Factibilidad operativa

- No reemplaza al despachador: le propone un plan y registra su decisión.
- Se monta sobre lo que el operador ya hace. Según prensa, la red de bancos de alimentos ya registra productos y vencimientos **[verificar fuente en el informe 02]**.

### Costos (estimaciones, con supuestos)

| Rubro | Estimación | Supuesto |
|---|---|---|
| Lectura de un mensaje con el modelo | Fracciones de centavo de dólar | Modelo pequeño, unos 1.500 tokens de entrada y 300 de salida; precio por verificar en la página oficial |
| Servidor | **[por llenar]** | Una máquina pequeña en la nube o un equipo del aliado |
| Mensajería | Telegram no cobra; WhatsApp Business cobra por conversación **[tarifa por verificar]** | |
| Personas | Cinco integrantes a tiempo parcial durante 90 días | Acompañamiento de la ruta piloto |

### Riesgos

| Riesgo | Mitigación |
|---|---|
| El modelo entiende mal un pedido, sobre todo si es urgente o está mal escrito | Esquema estricto, respuesta de confirmación al remitente, revisión humana antes de despachar, banco de mensajes de prueba con errores |
| El mapa no refleja un cierre o una vía nueva | Los cierres los reporta la gente en campo y los confirma el despachador; la red se actualiza desde OpenStreetMap |
| El aliado no adopta la herramienta | Operación en sombra antes de pedir ningún cambio de proceso |
| Datos personales | No se guardan nombres ni teléfonos; el remitente queda como un código. Ley 1581 de 2012 |
| Dependencia de un proveedor de IA | La extracción es un módulo aislado; se puede cambiar de modelo o digitar a mano |
| Uso de una patente sin condiciones claras | La patente del empaque entra al prototipo solo como un parámetro supuesto del modelo. Su uso real se acuerda en el piloto con la oficina de propiedad intelectual |

### Aliados y padrinos

| Aliado | Papel | Qué se le pide | Estado |
|---|---|---|---|
| Banco de Alimentos de Manizales y la red nacional de bancos de alimentos | Usuario del piloto | Registros de despachos de agosto y un despachador para probar | **[por contactar]** |
| Unidad de Gestión del Riesgo de Manizales | Fuente de datos y aval | Albergues y vías cerradas | **[por contactar]** |
| Cruz Roja y Defensa Civil, seccional Caldas | Operadores en campo | Un conductor y un vehículo para el simulacro | **[por contactar]** |
| IDEA-UNAL | Capacidad UNAL | Datos de lluvia acumulada por estación | **[por contactar]** |
| Profesores de logística de la Sede Manizales | Asesoría | Validar la formulación del ruteo | **[por contactar]** |
| Parque de Innovación Empresarial | Acompañamiento | Ruta piloto y enlace con entidades | Ofrecido por la hackathon |
| Empresas de alimentos y transporte de la región | Patrocinio | Vehículos, combustible o bodega | **[por definir]** |

## 6. Impactos esperados (10 puntos)

La rúbrica pide beneficiarios, resultados, magnitud e indicadores verificables.

### Beneficiarios

- **Directos:** despachadores y voluntarios de los centros de acopio; familias que reciben ayuda alimentaria en Manizales.
- **Indirectos:** donantes, que pueden ver a dónde llegó lo que dieron; entidades que coordinan la emergencia.
- **Magnitud [por llenar con fuente verificada]:** familias damnificadas en Manizales y familias atendidas por la red de bancos de alimentos. Las cifras candidatas están en `docs/investigacion/04_evidencia_del_problema.md` y cambian según la fecha de corte.

### Indicadores

| Indicador | Definición | Línea base | Meta | Cómo se verifica |
|---|---|---|---|---|
| Entregas a tiempo en puntos críticos | Pedidos de puntos críticos entregados antes de su hora límite, sobre el total | **[simulación de esta noche]** | **[simulación]** | Simulación ahora; registros reales en el día 30 |
| Desperdicio de perecederos | Kilos de perecederos vencidos antes de entregarse, sobre kilos perecederos despachables | **[simulación]** | Menos del 5 % (meta de la ficha del reto) | Igual |
| Tiempo de recálculo | Segundos entre confirmar un cierre vial y tener un plan nuevo | No aplica: hoy se hace por teléfono | Menos de 30 segundos | Medición directa en el prototipo |
| Trazabilidad | Paquetes con confirmación de entrega registrada, sobre paquetes despachados | **[por preguntar al aliado]** | Más del 90 % en el simulacro | Bitácora del sistema |
| Equidad (costo conocido) | Tiempo de espera en el punto peor atendido | Medido en simulación | Sin meta: priorizar lo crítico lo aumenta entre 0,9 y 4,3 horas según la carga. Se reporta y se vigila | Simulación |

Regla del equipo: los números de la simulación se presentan como simulación, con sus supuestos y el número de escenarios. No se presentan como resultados de campo.
