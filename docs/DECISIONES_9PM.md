# Decisiones para las 9:00 p. m. · viernes 20 de noviembre

Lo escribió Fable a las 6:20 p. m. con lo que trajeron once agentes. Se decide con Carlos, Samuel y Jacobo, y con lo que ellos escuchen hoy de personas reales (encargo P1). Cada afirmación remite a un documento del repositorio; ninguna cifra ha sido abierta todavía por una persona.

## Lo que sabemos ahora

1. **El cuello de botella fue despachar.** Al sexto día, la red de bancos de alimentos tenía 404.587 kg en acopio y había entregado 41.163 kg (Portafolio, 16 de agosto; investigación 10).
2. **En Manizales se repartió por listas.** Para recibir mercados en las carpas había que llevar el formato azul de Bomberos, y la Cruz Roja Seccional Caldas entregó los kits por turnos. La Gobernación dejó los kits cargados en el Centro Logístico Humanitario de San Rafael, y los recogieron vehículos de cada municipio. Desde el 11 de agosto la Alcaldía no recibió perecederos (investigación 11).
3. **Lo que existe no despacha.** El RUD dice quién es damnificado, KoboCollect y AccessRC registran hogares, SUMA lleva inventario y entregas, y ABACO recauda. Ninguna pieza une el pedido, el vehículo, la vía y la entrega (investigación 10).
4. **En el casco urbano la agenda pública es vivienda.** Además, en ciudades con comercio abierto el PMA y la Cruz Roja prefieren dar efectivo. La comida en especie importa en albergues, comedores, hogares infantiles y veredas aisladas (investigación 10).
5. **Las vías se cierran sin sismo.** La salida a Letras tiene 87 registros de deslizamiento entre 2017 y 2026, con horas de cierre total y semanas a un carril. El 21 de octubre la autopista del Café quedó a un carril y solo pasaban livianos. El cierre del sismo tardó 9 h 46 min en aparecer en el registro oficial de INVÍAS, que en 2025 se actualizaba en minutos (`docs/datos/vias_y_riesgo.md`).
6. **La UNAL ya mide la ladera.** El indicador A25 del IDEA tiene umbrales de 200, 300 y 400 mm y 14 estaciones (investigación 08). ALLO, de Carlos y coautores, calcula la probabilidad de deslizamiento por lluvia y corre en vivo.
7. **La simulación estaba optimista** en velocidades y vida útil. La corrida se repite con lo medido (`docs/datos/flota_perecederos_costos.md`).

## Decisión 1 · ¿Para quién es DespachoX?

| Opción | A favor | En contra |
|---|---|---|
| **A. Banco Arquidiocesano de Alimentos** | Despacha todos los días a organizaciones inscritas; fue nodo regional hacia Caldas; ahí vive el desperdicio de perecederos | Nunca habló en público: no sabemos si reparte o si las organizaciones recogen |
| **B. Gobernación y unidades de gestión del riesgo municipales** | El flujo de requerimientos ya existe; la calamidad sigue vigente; los cierres de vía pegan en el tramo hacia municipios y veredas | En agosto los municipios recogieron en bodega; no sabemos cuántos requerimientos hay fuera del sismo |

**Propuesta de Fable.** Piloto con el Banco y la Unidad de Gestión del Riesgo de Manizales, y la Gobernación como ruta de escalamiento a los municipios de Caldas. Regla de cambio escrita desde hoy: si el Banco confirma que las organizaciones recogen y nadie reparte, el piloto pasa al flujo de requerimientos de la UGR y la Gobernación. Así la solución puede cambiar sin improvisar.

## Decisión 2 · El piloto de 30 a 90 días

Sobre la rutina real del aliado, en un territorio con nombre (una comuna y una vereda), medido de cuatro formas: contra su propia línea base, con un simulacro con la UGR, con los cierres reales de la temporada de lluvias y con la reconstrucción de agosto si hay registros. La tabla por territorio (encargo T1) es el instrumento. La tabla de hitos, entregables, responsables, recursos y validación la escribe Fable en la ficha apenas se decida esto.

## Decisión 3 · Qué cambia en el prototipo antes del congelamiento (sábado 8:30 a. m.)

| Cambio | Quién | Recomendación |
|---|---|---|
| Vista por territorio (T1) | B-despacho y Jacobo | Ya aprobado |
| El bot pregunta por personas, no por familias (una «familia» vale 1,8, 2,9 o 4 personas según la fuente) | Samuel | Sí, es pequeño |
| Casilla para digitar un pedido en el tablero (listas, radio, SMS sin bot) | Jacobo | Sí, si cabe tras la etapa 1 de C2 |
| Factor del empaque: 1,2 solo para fruta en frío | B-despacho | Sí, por honestidad |
| Alerta de ladera del día leída de ALLO, sin cambiar rutas | Carlos | Solo si el servicio de ALLO está en vivo y cuesta menos de una hora |
| Escenario con lugares reales en la nube | Carlos | Todavía no: el guion de la demo depende de la semilla; el mapa real va como figura |
| Simulación con velocidades medidas | simulacion | Sí, y se reportan las dos versiones |

## Decisión 4 · El orden del pitch

1. Por qué: la donación llegó y el despacho se atascó (404.587 kg contra 41.163 kg al sexto día).
2. Para qué: que la comida llegue a quien no puede ir a buscarla, aunque la vía esté cerrada.
3. Para quién: el Banco, las juntas, los conductores y la UGR.
4. Por qué no basta lo que existe: piezas sueltas, ninguna despacha.
5. Qué medimos y cómo: la tabla por territorio, la bitácora y el QR de cada entrega.
6. El piloto de 30 a 90 días para la recuperación del territorio.

## Llamadas, en orden de prioridad

1. **Banco Arquidiocesano de Alimentos, o ABACO:** ¿reparten o recogen? ¿Con qué sistema? ¿Siguen despachando ayuda del sismo? ¿Tienen cuarto frío? ¿Aceptarían 30 días de prueba en paralelo?
2. **Unidad de Gestión del Riesgo de Manizales:** quién despachó y con qué, qué dice la estrategia de respuesta sobre el abastecimiento, cuándo es el próximo simulacro y si avalaría el piloto.
3. **Centro Logístico Humanitario de la Gobernación:** cómo llega un requerimiento municipal y cuánto tarda.
4. **Cruz Roja Seccional Caldas:** cómo manejó los kits, los turnos y las rutas.
5. **IDEA y SIMAC (UNAL):** A25 diario por estación de agosto a noviembre y permiso para citarlo.
6. **Un profesor de logística de la Sede:** quince minutos para validar la formulación.
7. **Fernando Bernal:** resolución de concesión y anualidad 2026 de la patente 37476.
8. **INVÍAS, Dirección Territorial Caldas:** exportación del registro 767 con horas de reapertura.

Los nombres de las personas de contacto que figuran en fuentes públicas están en las investigaciones 08, 10 y 11.

## Lo que falta en el repositorio

- **La ficha.** La rama `ficha` del agente de las 4:25 p. m. no ha llegado. Si a las 9:00 sigue sin aparecer, Fable escribe `docs/FICHA.md` con estas decisiones para la fusión de las 11:00 p. m.
- **`docs/FUENTES.md` sigue vacío.** Estas diez cifras son las candidatas al pitch, y alguien del equipo tiene que abrir su enlace: 404.587 y 41.163 kg; 8.240 damnificados en Manizales; sismo de 7,4 el 10 de agosto a las 7:34 a. m.; 262.154 damnificados en el país; cierre Pereira–Chinchiná, km 22 a 24; 87 registros en la salida a Letras; 28 % de estaciones base caídas en Caldas; reparto por listas en Manizales; 18.847 unidades entregadas por la Gobernación; 204 juntas de acción comunal.
