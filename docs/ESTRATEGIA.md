# DespachoX · Estrategia para la Hackathon UNAL Manizales 2026

Versión 2 · viernes 20 de noviembre de 2026, 7:55 a. m. · Cambio frente a la v1: la vertical es la 04, Logística y abastecimiento.

Equipo 19: Samuel Rosso (líder), Carlos Orrego, Nicolás Ramírez, Jacobo Vasco, José Manuel Aristizábal. Repositorio: github.com/cmorregof/despachoX

## 1. Lo que pide la hackathon

- **Entregable:** un prototipo para un problema verificable de una sola vertical, que use al menos una capacidad UNAL y traiga una ruta de piloto de 30 a 90 días. Las preguntas frecuentes dicen que no se puede trabajar en dos verticales.
- **Pasaporte UNAL:** problema verificable, capacidad UNAL, prototipo funcional, impacto medible. La capacidad puede ser una base de datos, una metodología, software, un laboratorio o la experiencia de un profesor. La patente no es obligatoria, y usar una exige verificar sus condiciones de uso.
- **Competencia:** 22 equipos. Hay un pitch de selección (sábado 2:00 p. m.) y un pitch final (4:00 p. m.), así que primero hay que pasar el corte.
- **Premios:** $8, $5 y $2 millones, más acompañamiento al piloto. Los ganadores presentan otra vez el jueves 26 en Conecta+.
- **Sin definir todavía:** duración del pitch, mecanismo de entrega y regla de desempate. La organización los anuncia en el evento.

### Rúbrica del jurado (100 puntos)

| # | Componente | Puntos | Qué mira |
|---|---|---|---|
| 1 | Problema y vertical | 20 | Claridad, evidencia, beneficiarios, relación con la vertical |
| 2 | Prototipo de solución | 25 | Creatividad, pertinencia, funcionamiento, demostración |
| 3 | Conocimiento utilizado | 15 | Patentes, métodos, bases de datos, TIC: identificación, pertinencia y aplicación |
| 4 | Plan de 30 a 90 días | 15 | Hitos, entregables, responsables, recursos, validación |
| 5 | Viabilidad y aliados | 15 | Factibilidad, riesgos, padrinos y patrocinadores |
| 6 | Impactos esperados | 10 | Beneficiarios, resultados, magnitud, indicadores verificables |

Escala por criterio: excelente 100 %, sólido 75 %, parcial 50 %, incipiente 25 %, no evidenciado 0 %.

Dos lecturas de esta tabla. El prototipo y el problema suman 45 puntos, y ambos premian evidencia y demostración. Los componentes 4, 5 y 6 suman 40 puntos y casi ningún equipo de estudiantes los trabaja antes del sábado. Un equipo que llegue «excelente» en esos tres le saca diez puntos al que llegue «sólido», con mucho menos esfuerzo que el que cuesta mejorar el software.

### Hitos del evento

| Momento | Qué exige |
|---|---|
| Viernes 2:30 p. m. | Empieza el trabajo de equipos |
| Viernes 4:00 p. m. | Charla (problema, prototipo, imágenes satelitales, prompting, pitch). Mandar dos personas, no cinco |
| Viernes 7:00 p. m. | Mentoría 1: componentes 1, 2 y 3 sustentados; 4, 5 y 6 en borrador |
| Sábado 10:30 a. m. | Mentoría 2: los seis integrados, los ajustes de la mentoría 1 a la vista y la presentación lista |
| Sábado 2:00 p. m. | Pitch de selección |
| Sábado 4:00 p. m. | Pitch final |

## 2. La vertical 04 según su ficha

- **Problema:** los derrumbes en las vías de acceso a Manizales (La Siria, vía a Chinchiná, Letras) generan embotellamientos y desabastecimiento de alimentos de primera necesidad en 48 horas.
- **Usuarios:** Cruz Roja, Defensa Civil, Banco de Alimentos, transportadores y comités barriales de abastecimiento.
- **Capacidades UNAL asignadas:** Grupo de Investigación en Logística y Transporte Multimodal, software UNAL de ruteo vehicular adaptativo ante bloqueos viales, Laboratorio de Embalajes y Conservación de Alimentos Perecederos, convenios con asociaciones de productores campesinos de Caldas.
- **Datos de entrada:** red vial terciaria georreferenciada con pendientes y susceptibilidad de deslizamiento, censo de centros de acopio y bodegas con frío, demanda calórica y alimentaria por cuadrante urbano.
- **Restricción:** flotas mixtas (camiones livianos, camperos 4x4, drones y tracción animal en tramos colapsados).
- **Entregable esperado:** plataforma o protocolo de despacho en tiempo real con optimización de rutas y trazabilidad de paquetes de ayuda.
- **Indicadores:** porcentaje de entregas a tiempo en puntos críticos y desperdicio de perecederos por debajo del 5 %.
- **Patentes asociadas (3):** plataforma para el control inteligente de vehículos de transporte público; composición que captura etileno para retardar la maduración; película antimicrobiana de empaque.

El nombre del equipo coincide con el entregable de la ficha. Eso ayuda en el criterio 1.

## 3. Propuesta: qué construir

### DespachoX en una frase

Una mesa de despacho de ayuda alimentaria para el Banco de Alimentos y los organismos de socorro: los barrios piden por chat, los conductores reportan bloqueos por chat, y el despachador ve en un mapa las rutas recalculadas con lo que hay en bodega y lo que vence primero.

Regla de arquitectura, la misma de CARMEN y del bot de la Facultad:

> El modelo lee y estructura. El optimizador y las reglas calculan. El despachador decide.

### Flujo

1. **Demanda.** Un líder de comité barrial escribe o dicta por Telegram lo que falta («somos 40 familias en San José, no hay leche ni arroz»). El modelo lo convierte en un pedido validado: punto, familias, productos, urgencia. Las reglas unen pedidos duplicados del mismo punto.
2. **Oferta.** Inventario por centro de acopio, con fecha de vencimiento por lote. Para la demo basta una tabla cargada a mano.
3. **Vías.** Un conductor o un socorrista reporta «derrumbe en La Siria, no pasa camión, sí pasa moto». El modelo lo convierte en un cierre de tramo por tipo de vehículo, y un humano lo confirma.
4. **Despacho.** Un optimizador (OR-Tools sobre la red vial de OpenStreetMap) asigna pedidos a vehículos de flota mixta y calcula rutas con capacidad, ventanas de tiempo y prioridad a lo que vence primero. Cuando se confirma un cierre, recalcula.
5. **Trazabilidad.** Cada paquete lleva un código QR. Sale de bodega, se entrega y el receptor confirma por chat con una foto. El tablero muestra el estado de cada paquete.
6. **Tablero.** Mapa de Manizales con centros de acopio, puntos de entrega, tramos cerrados y rutas. El despachador aprueba o ajusta cada plan. Queda registro.
7. **Degradación.** Sin internet, el conductor guarda la confirmación y sincroniza después. Sin modelo, el pedido entra como texto y lo digita el despachador.

### Por qué esto puede ganar

- **Demo en vivo con el jurado adentro.** Un jurado dicta por su teléfono un derrumbe en una vía y ve en la pantalla cómo las rutas cambian en segundos. Otro hace un pedido y lo ve entrar a la cola. Eso responde al criterio de 25 puntos mejor que cualquier diapositiva.
- **Un número propio contra los dos indicadores de la ficha.** Simulamos varias decenas de escenarios (pedidos, inventario con vencimientos, cierres viales aleatorios) y comparamos DespachoX contra un despacho ingenuo: por orden de llegada, por la ruta habitual y sin recalcular. Reportamos entregas a tiempo y desperdicio de perecederos en ambos. El resultado se presenta como simulación con supuestos declarados, pendiente de validar en el piloto.
- **Un equipo con ingeniero industrial.** El modelo de ruteo y los indicadores logísticos tienen dueño natural, y las bases exigen interdisciplinariedad.
- **La decisión es humana.** Nadie quiere que una IA mande sola un camión por una ladera inestable.

### Lo que no hay que hacer

Aplicación móvil nativa, drones reales, predicción de deslizamientos, entrenamiento de modelos. La flota mixta se resuelve con tipos de vehículo y tramos permitidos por tipo, que es una columna en una tabla. Un solo corte vertical que funcione de punta a punta. Si sobra tiempo el sábado, se pule; no se agrega.

## 4. Cómo llegar a «excelente» en cada criterio

| # | Evidencia que mostramos | Responsable |
|---|---|---|
| 1 | El problema en una frase con el texto de la ficha 04. Dos o tres cifras con fuente sobre cierres viales y abastecimiento después del 10 de agosto. Un usuario con nombre y cargo (Banco de Alimentos, Cruz Roja o Defensa Civil). Ideal: una cita de alguien real conseguida hoy | Rol D |
| 2 | Demo en vivo, video de respaldo de 60 a 90 segundos y tabla de la simulación | Roles A, B, C |
| 3 | Capacidades UNAL con nombre, responsable y uso concreto dentro del sistema. Método: formulación del ruteo, reglas, decisión humana | Carlos y rol B |
| 4 | Tabla 30/60/90 con hito, entregable, responsable, recurso y criterio de validación por fila | Rol D |
| 5 | Costo por despacho, riesgos con mitigación, cumplimiento de Ley 1581, padrinos con lo que se le pide a cada uno | Rol D y Samuel |
| 6 | Los dos indicadores de la ficha con línea base y meta, más familias atendidas por jornada | Rol B |

### Capacidades UNAL candidatas (verificar hoy en la mesa)

Algunas entradas del sitio parecen texto de plantilla. **Antes de construir sobre una hay que confirmar con la organización que el dato o el acceso existe.** Si el software no está disponible, la capacidad puede ser la asesoría del grupo y el conocimiento de un profesor, que también cuenta.

- Software UNAL de ruteo vehicular adaptativo ante bloqueos, y el simulador ERIS-UNAL de innovaTE (API de rutas con probabilidad de bloqueo). Si entregan acceso, se usa como motor o como referencia de comparación. Si no, se usa OR-Tools y se declara.
- Grupo de Logística y Transporte Multimodal: pedir quince minutos de asesoría para validar la formulación. Su visto bueno es evidencia para el criterio 3.
- Red vial terciaria con pendientes y susceptibilidad de deslizamiento: pesos de riesgo en los tramos.
- Censo de centros de acopio y demanda por cuadrante: datos de entrada reales para la simulación.
- Patentes de conservación de perecederos (captura de etileno, película antimicrobiana): se mencionan como línea del piloto para el indicador de desperdicio, sin prometer su uso hasta verificar condiciones.
- Experiencia académica directa: Carlos es profesor de la Sede, y la arquitectura viene de CARMEN (proyecto 56031, Minciencias).

### Plan 30/60/90 (borrador)

| Día | Hito | Validación |
|---|---|---|
| 30 | Reconstrucción en frío con el Banco de Alimentos o un organismo de socorro: tomar despachos reales de agosto y comparar contra el plan que habría dado DespachoX | Entregas a tiempo y kilómetros, reales contra simulados |
| 60 | Simulacro con un comité barrial (Comuna San José) y dos o tres vehículos: pedidos por chat, QR, confirmación de entrega, un cierre vial simulado | Tiempo de pedido a entrega, paquetes trazados, desperdicio |
| 90 | Operación en sombra durante entregas reales, informe y acuerdo de adopción | Concordancia con el despachador, decisión de adopción |

### Padrinos posibles

Banco de Alimentos de Manizales, Cruz Roja Seccional Caldas, Defensa Civil, Unidad de Gestión del Riesgo, asociaciones de productores y Comité de Cafeteros, una empresa de transporte de carga local. A cada uno se le pide algo concreto: datos históricos, un vehículo para el simulacro o un operador para probar el tablero.

## 5. Roles y jornada

Carlos asigna nombres cuando conozca a todo el equipo.

- **A · Entrada:** bot, voz, extracción de pedidos, cierres viales y confirmaciones de entrega.
- **B · Optimización y medición:** formulación del ruteo, OR-Tools, simulación contra la línea base. Dueño natural: el ingeniero industrial, con Carlos.
- **C · Tablero:** mapa, rutas, cola de pedidos, estado de paquetes, botones de aprobación.
- **D · Ficha y pitch:** los seis componentes por escrito, cifras con fuente, plan, aliados, diapositivas.
- **Capitán (Carlos):** integración, mentores, capacidades UNAL, video, ensayo del pitch.

### Viernes

| Hora | Qué |
|---|---|
| 8:00 a 2:00 | Confirmar la vertical con Samuel. Preguntar en la mesa: duración del pitch, forma de entrega, quiénes son jurados, acceso real al software de ruteo y a los datos. Buscar a alguien del Banco de Alimentos, Cruz Roja o Defensa Civil y pedirle cinco minutos. Montar la torre de control en el repositorio |
| 2:30 a 4:00 | Esqueleto de punta a punta: un pedido entra por chat y sale una ruta dibujada en el mapa, aunque sea fea |
| 4:00 a 4:45 | Charla: van dos personas |
| 4:45 a 7:00 | Cierre vial que recalcula la ruta, ficha de componentes 1 a 3, primera corrida de la simulación |
| 7:00 | Mentoría 1. Una persona anota todas las observaciones en la torre de control |
| 8:00 en adelante | Ajustes de mentoría, simulación completa, QR, tablero presentable, borradores 4 a 6. Quien presenta el sábado duerme |

### Sábado

| Hora | Qué |
|---|---|
| 8:30 | Se congelan las funciones. Desde aquí solo se arregla |
| 8:30 a 10:30 | Diapositivas, video de respaldo, primer ensayo cronometrado |
| 10:30 | Mentoría 2 con la presentación real |
| 1:00 a 2:00 | Dos ensayos cronometrados. Probar la demo con datos móviles, no con el wifi del campus |

## 6. Riesgos del equipo

- **Construir de más.** Se controla con la congelación del sábado a las 8:30.
- **Demo que falla en vivo.** Video de respaldo, datos móviles y la red vial descargada en disco.
- **El optimizador tarda.** Límite de tiempo de pocos segundos y una instancia de demo pequeña (cinco vehículos, veinte pedidos).
- **Simulación a favor nuestro.** La línea base debe ser razonable y los supuestos van escritos. Un jurado de ingeniería industrial lo va a preguntar.
- **Datos personales.** Ningún nombre, teléfono o dirección exacta de afectados entra al repositorio. Los pedidos de prueba son sintéticos.
- **Capacidad UNAL decorativa.** Hay que poder señalar en qué línea de código o en qué decisión se usa.
- **Detalle por aclarar.** La noticia de la Sede habla de una ruta piloto de 20 a 30 días y el sitio, de 30 a 90. Vale lo que diga la organización hoy.
