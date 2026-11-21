# Convite (antes DespachoX) · Ficha de los seis componentes

Equipo 19 · Hackathon UNAL Manizales 2026 · Vertical 04, Logística y abastecimiento
Samuel Rosso (líder) · Carlos Orrego · Jacobo Vasco · Nicolás Ramírez · José Manuel Aristizábal

El anexo técnico, con todas las cifras, supuestos y riesgos, está en `docs/FICHA.md`. [M] medido por el equipo, [E] estimado, [I] inferencia nuestra. Las cifras de fuentes externas están por verificar.

## 1. Problema y vertical (20 puntos)

**El problema.** Después del sismo, la comida donada llegó a la región y se atascó en el despacho. Según las fuentes que revisó el equipo, ninguna herramienta en uso une el pedido de cada barrio o vereda, el vehículo, la vía abierta y la confirmación de entrega.

**La evidencia.** En Manizales, el censo del 24 de agosto contó 8.240 damnificados (Noticias RCN; por verificar). La red de bancos de alimentos, ABACO, hizo de la ciudad uno de sus principales puntos de acopio (Noticias RCN; por verificar). Según Portafolio, el 16 de agosto la red tenía 404.587 kg en acopio y 157.164 kg en tránsito, y había entregado 41.163 kg (por verificar). En Manizales la comida se repartió por listas. Para recibir mercados había que llevar el formato azul de Bomberos, y los kits se entregaron por turnos en la sede de la Cruz Roja Seccional Caldas (Alcaldía; por verificar). La Gobernación dejó los kits en su centro logístico, donde los recogieron los vehículos de cada municipio (Gobernación; por verificar).

**Las vías.** El 12 de agosto seguían cerradas la vía Pereira–Chinchiná, entre los kilómetros 22 y 24, y la vía Manizales–Fresno en Herveo, entre los kilómetros 36+800 y 40+300 (Semana; por verificar). Las vías se cierran también sin sismo. La salida a Letras suma 87 registros de cierre por deslizamiento o derrumbe entre 2017 y 2026, y 4 de ellos son del sismo. Un mismo derrumbe puede tener varios registros (INVÍAS y prensa; cálculo nuestro; por verificar). Además, el registro oficial del cierre Pereira–Chinchiná apareció 9 horas y 46 minutos después del sismo (cálculo nuestro; por verificar).

**Lo que existe no despacha.** El Registro Único de Damnificados cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas (Vanguardia; por verificar). La Cruz Roja registra hogares con AccessRC y KoboCollect, y el sistema SUMA de la OPS lleva inventario y entregas. ABACO recauda y le reporta al donante. Ninguna de estas piezas asigna pedidos a vehículos ni recalcula rutas.

**Para quién.** El usuario principal es quien despacha en el Banco Arquidiocesano de Alimentos de Manizales, que opera todo el año y fue nodo del corredor en agosto [I]. Piden las 204 juntas de acción comunal de la ciudad, 131 de barrios y 73 de veredas (Alcaldía; por verificar), junto con comedores, hogares y albergues.

**Vertical 04.** La ficha de la vertical pide una plataforma de despacho en tiempo real, con rutas optimizadas y trazabilidad de paquetes, para una flota mixta. Mide entregas a tiempo en puntos críticos y desperdicio de perecederos bajo el 5 %, los mismos indicadores que mide Convite.

## 2. Prototipo de solución (25 puntos)

**Qué es.** Convite es una mesa de despacho de ayuda alimentaria. El modelo de lenguaje lee los mensajes; el optimizador y las reglas calculan; el despachador decide.

**Lo que funciona hoy.** El bot de Telegram y el tablero corren en la nube desde el viernes, y las 306 pruebas automáticas del repositorio pasan [M].

- Un líder pide por chat, y en quince mensajes sintéticos el extractor acertó 62 de 64 campos [M].
- El ubicador conoce 452 nombres y apodos de Manizales y pide confirmar el lugar. En 44 frases de prueba no propuso con seguridad ningún lugar equivocado [M].
- El optimizador, con OR-Tools, reparte entre camión, campero y moto según capacidad y vencimiento. Con 50 lugares reales y pedidos sintéticos, atendió 25 de 25 pedidos y 23 de 23 críticos a tiempo, en 3,5 s [M].
- Un conductor reporta un derrumbe que deja al camión sin acceso. El despachador confirma, y el plan nuevo manda un campero.
- El despachador aprueba cada plan con su nombre. Cada paquete lleva un código y se cierra cuando alguien escribe «ENTREGADO» y el código por chat o SMS [M].

**Demostración.** La demo de tres minutos recorre ese flujo y está ensayada. El jurado puede escribirle al bot con el QR.

**Sin internet.** Pedidos, cierres y entregas entran también por SMS, que un programa de reglas lee sin red. Leyó 20 de 20 SMS sintéticos, en una prueba no independiente [M]. Con la red bloqueada, un portátil llegó a la hoja de ruta con QR y a una entrega registrada en 23 s [M]. Falta probarlo con el wifi apagado y con un celular real.

**Simulación.** Con 30 escenarios por nivel de carga y 360 jornadas sobre la red real de Manizales, Convite sube los críticos a tiempo en 23,3, 44,7 y 57,9 puntos frente al despacho por orden de llegada [M]. Cada diferencia compara 30 jornadas por política, y ningún intervalo del 95 % toca el cero. Frente a un despachador con oficio, recorre 46,0, 56,0 y 42,2 km menos por jornada. En el total de entregas a tiempo empata con carga holgada y media, y con carga alta gana 3,0 puntos. Los perecederos vencidos quedan en 0,0 %, frente a 1,4 %, 3,4 % y 5,6 % por orden de ingreso, por una regla de bodega que el despachador con oficio también cumple. Priorizar hace esperar al punto peor atendido entre 1,95 y 3,82 horas más que por orden de llegada. Las velocidades son derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48). La simulación usa la media por tipo de vía. La vida útil no se repitió con lo medido, y la corrida le sigue dando al huevo horas cuando dura días.

## 3. Conocimiento utilizado (15 puntos)

**El A25 del IDEA, capacidad principal.** La capacidad UNAL principal es el indicador A25 del IDEA, Sede Manizales, que mide la lluvia acumulada en 25 días por estación. La Unidad de Gestión del Riesgo lo adoptó a partir de la tesis de Terlien (1996), que asoció unos 200 mm en 25 días con alta probabilidad de deslizamientos (IDEA; por verificar). Sus umbrales de alerta son 200, 300 y 400 mm, y el reporte de 2020 cubre 14 estaciones (IDEA; por verificar). El 16 de febrero de 2026 Manizales declaró alerta amarilla con el umbral de 200 mm (Blu Radio; por verificar). En Convite, el optimizador encarece, sin cerrarlas, las vías con historial de deslizamientos en alerta naranja o roja. Ya está en el código, con lluvia de prueba y apagado por defecto, y en los días 60 a 90 del piloto entra con los datos diarios del IDEA. El equipo está pidiendo cinco minutos a un profesor del IDEA para que revise ese uso y dé su visto bueno.

**Otras capacidades UNAL.**

- **Patente 37476**, composición que captura etileno. Está en el optimizador como parámetro supuesto que alarga la vida útil de un lote. Su único respaldo es una cota inferior de 1,2 en gulupa a 8 °C (cálculo nuestro sobre la solicitud; por verificar). Su ensayo por producto se propone con el laboratorio de empaques del ICTA.
- **Velocidades de la tesis.** Una tesis de maestría de la UNAL Manizales da 22,6 km/h de media en la ruta de un bus de transporte de trabajadores de la CHEC (p. 50; por verificar). La simulación usa sus velocidades por tipo de vía (tabla 14).
- **Logística humanitaria.** Una tesis de 2017 sobre la red de ayuda de Manizales, dirigida por William Ariel Sarache Castro, orienta el mapa de actores del piloto.
- **Arquitectura.** La regla del modelo que lee, el código que calcula y la persona que decide viene de CARMEN, proyecto 56031 de Minciencias, y la aporta Carlos Orrego, profesor de la Sede.

**Métodos y datos.** El núcleo es un ruteo de vehículos con capacidad y ventanas de tiempo en OR-Tools, que se rehace con cada cierre, tanda de pedidos o regreso de un vehículo. La simulación usa semillas comunes, diferencias pareadas y una regla de decisión escrita antes de correr. Los datos son la red de OpenStreetMap de Manizales y sus accesos, 50 puntos de entrega reales con fuente y 178 registros de cierres viales. Pedidos y lotes son sintéticos y no contienen datos personales.

## 4. Plan de 30 a 90 días (15 puntos)

**El piloto.** Convite entra a la operación diaria del Banco Arquidiocesano de Alimentos, en una comuna y una vereda [por definir con el Banco]. La Unidad de Gestión del Riesgo (UGR) acompaña los simulacros y la temporada de lluvias, y la Gobernación es la ruta de escalamiento. Así el piloto sirve a la recuperación del territorio, porque deja la capacidad en manos locales y se usa entre desastres. Se mide contra la línea base del Banco, con la tabla por territorio, la bitácora y el QR de cada entrega.

| Días | Hito y entregables | Responsables | Recursos | Validación |
|---|---|---|---|---|
| 0 a 15 | **Acuerdo y línea base.** Carta de intención del Banco y aval de la UGR. Catálogo de puntos, inventario con vencimientos y un mes de despachos, sin datos personales. Dos semanas de bitácora del despacho actual | Samuel (acuerdo), Jacobo (bitácora), Carlos (datos) | Horas del despachador; acompañamiento previsto para los premiados | Carta firmada; línea base de entregas a tiempo, kilómetros y kilos vencidos |
| 15 a 30 | **Reconstrucción en frío.** Lo que habría planeado Convite para cada día del mes registrado, frente a lo que se hizo. Simulación con velocidades de la tesis | Carlos; por asignar la revisión externa | Registros del Banco y un portátil | Real contra reconstruido. Sin mejora en kilómetros ni desperdicio, se rediseña el piloto |
| 30 a 60 | **Uso en paralelo.** Las organizaciones piden por chat o SMS. En un día normal, el Banco reparte como siempre y Convite planea en sombra | Samuel (juntas), Jacobo (tablero), Carlos (optimizador) | Celular con SIM, impresora y vehículos del Banco | Veinte pedidos reales de punta a punta; kilómetros y kilos vencidos frente a la forma actual |
| 60 a 90 | **Prueba de esfuerzo y decisión.** Simulacro con la UGR y un cierre planeado. A25 por tramo. Dos semanas en sombra e informe para el Consejo Municipal de Gestión del Riesgo | Todo el equipo; por asignar el informe | Datos del IDEA; horas de la UGR y del Banco | Rutas que evitan tramos en alerta; planes aprobados sin cambios; decisión escrita del Banco |

**Regla de cambio.** Si el Banco confirma que las organizaciones recogen en su bodega y nadie reparte, el piloto pasa al flujo de requerimientos de la UGR y de la Gobernación.

**Marco.** El piloto cabe en la calamidad pública de Manizales, vigente hasta el 9 de agosto de 2027 (Alcaldía; por verificar).

## 5. Viabilidad y aliados (15 puntos)

**Factibilidad.** Convite corre en un servidor pequeño o en un portátil del acopio, con la red vial en disco [M]. Quien pide no instala nada, porque escribe por Telegram o manda un SMS. Con un lector simulado, el bot procesó 914 mensajes por minuto sin perder ninguno [M]. Convite entra a la rutina del Banco, porque una herramienta que solo se enciende en el desastre llega sin usuarios entrenados ni datos [I]. El RUD y el registro web de Providencia en 2020 exigieron un trámite nuevo en plena emergencia y dejaron gente por fuera (Vanguardia; El Colombiano; por verificar).

**Qué pedimos y qué damos.** Al Banco le pedimos el catálogo de puntos, el inventario con vencimientos y un mes de despachos, sin datos personales. A cambio recibe el informe con sus propios números y la herramienta con sus datos, que siguen siendo suyos.

**Costos.** Leer 10.000 mensajes costaría entre 1,75 y 4,50 USD con el precio público de claude-haiku-5-5, sin medición real [E]. El servidor y el plan de SMS están por cotizar.

**Riesgos.**

- **El Banco no reparte.** Se aplica la regla de cambio.
- **El modelo entiende mal un pedido.** Quien pide confirma el lugar, y el despachador revisa cada plan.
- **Se cae internet.** Quedan los SMS y la hoja impresa, aunque el mapa del tablero todavía necesita red.
- **Una entrega se confirma en falso.** El código admite 390.625 combinaciones, así que en el piloto solo cuenta la confirmación del destino o del conductor.
- **Datos personales.** El remitente queda como un código, y los pedidos de prueba son sintéticos, según la Ley 1581 de 2012.
- **La patente.** Entra como parámetro supuesto, y su uso se acuerda con la oficina de propiedad intelectual.

**Aliados.** Ninguno ha visto todavía la propuesta.

| Aliado | Qué se le pide | Estado |
|---|---|---|
| Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | Llamada el sábado a las 8:00 a. m. |
| UGR de Manizales | Aval, fecha del próximo simulacro y reportes de cierres | Por contactar |
| Gobernación de Caldas | Cómo llega y cuánto tarda un requerimiento municipal | Por contactar |
| Cruz Roja Seccional Caldas | Un conductor para el simulacro | Por contactar |
| IDEA y SIMAC, UNAL Manizales | Visto bueno del A25 y datos diarios por estación | En gestión |

## 6. Impactos esperados (10 puntos)

**Beneficiarios.** Los directos son el despachador y los voluntarios del Banco, y las organizaciones y juntas del territorio. Los finales son las personas que comen en comedores, hogares, albergues y veredas. Los donantes reciben la confirmación de cada entrega.

**Magnitud.** En el sismo, ABACO movió más de 2.000 toneladas para 9.470 familias en 36 municipios (Portafolio; por verificar). En 2025 su red manejó unas 54.000 toneladas (La República; por verificar), mientras Colombia pierde o desperdicia 9,76 millones de toneladas de alimentos al año (DNP; por verificar). Cuántas personas atiende el Banco en el territorio del piloto se mide en los días 0 a 15.

**Indicadores.** Todos se miden contra la línea base del Banco, y la simulación solo sirve de referencia.

| Indicador | Línea base | Meta | Verificación |
|---|---|---|---|
| Entregas a tiempo en puntos críticos | La del Banco. En simulación, con carga media y 30 jornadas por política, 53,6 % por orden de llegada y 94,6 % con un despachador con oficio | Igual o mayor que la del Banco | Bitácora y código de cada entrega |
| Desperdicio de perecederos | Kilos vencidos del registro del Banco | Menos del 5 % | Inventario con vencimientos |
| Kilos entregados sobre kilos en acopio | La del Banco. Según Portafolio (16 ago), 41.163 kg entregados frente a 404.587 kg en acopio y 157.164 kg en tránsito | Mayor que la línea base | Inventario y confirmaciones |
| Kilómetros con la misma flota | Odómetro del día en paralelo | Menos que la forma actual | Odómetro o GPS |
| Entregas confirmadas | Por preguntar al Banco | Más del 90 % | Bitácora |
| Espera del punto peor atendido | En simulación, con 30 jornadas por política, 1,95 a 3,82 horas más que por orden de llegada, según la carga | Sin meta. Se vigila | Tabla por territorio |

## Cifras usadas

| Cifra | Fuente | Estado |
|---|---|---|
| 8.240 damnificados; uno de los principales acopios | Noticias RCN, 10 y 24 ago 2026 | Por verificar |
| 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados (16 ago); más de 2.000 t para más de 9.470 familias | Portafolio, 16 ago y 21 sep 2026 | Por verificar |
| 204 juntas; calamidad hasta agosto de 2027 | Alcaldía de Manizales | Por verificar |
| Cierres del 12 de agosto | Semana, 12 ago 2026 | Por verificar |
| 87 registros en Letras; 9 h 46 min | INVÍAS, registro #767, y prensa | Por verificar |
| RUD cerrado el 4 de septiembre | Vanguardia, 5 oct 2026 | Por verificar |
| A25, sus umbrales y su origen; alerta del 16 de febrero | IDEA, 2018 y 2020; Blu Radio | Por verificar |
| Cota de 1,2 del empaque | Solicitud de la patente 37476; cálculo nuestro | Por verificar |
| 22,6 km/h de un bus en Manizales | Tesis UNAL Manizales, 2019 | Por verificar |
| 50 puntos reales; 178 registros de cierres | `datos_publicos/`, fila por fila | Por verificar |
| 54.000 t; 9,76 millones de t | La República; DNP, 2016 | Por verificar |
| Mediciones del prototipo | Repositorio; detalle en `docs/FICHA.md` | Medidas |
| Simulación con velocidades de la tesis UNAL de 2019 | `docs/SIMULACION.md`, sección 9 | Medidas; falta 9.3 |
| 1,75 a 4,50 USD por 10.000 mensajes | `entrada/ESCALA.md` | Estimada |
| 390.625 combinaciones del código | Cálculo nuestro | Calculada |
