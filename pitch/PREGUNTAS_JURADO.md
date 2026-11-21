# Convite (antes DespachoX) · Preguntas probables del jurado

Son 30 preguntas para ensayar la defensa del sábado, agrupadas por criterio de la rúbrica. Esta versión es del sábado 21 de noviembre de 2026, de madrugada, en la rama `defensa-noche`. Cada respuesta cabe en dos o tres frases, y debajo va el archivo que la respalda. Las cinco preguntas que dejó la mentoría 1 llevan la marca «mentoría 1».

**Marcas.** [F] dato de una fuente, que alguien del equipo debe abrir en `docs/FUENTES.md` antes de decirlo en voz alta. [M] medido por el equipo. [E] estimado. [I] inferencia nuestra. [H] hipótesis por validar. Las cifras de simulación salen de `docs/SIMULACION.md`, sección 9, y de `despacho/sim/resultados_velocidades/tablas.md`. [P5] se actualiza con el resultado de la visita al Banco, que el integrante de Ingeniería Industrial reporta a las 12:30 p. m.

**Regla para responder.** Si no sabemos algo, lo decimos y nombramos el hito del piloto que lo va a medir. Toda cifra de simulación se dice con su línea base y con la palabra simulación.

**Propuesta de reparto, por confirmar con Carlos.** Samuel responde los criterios 1 y 5, Jacobo el 2, Carlos el 3 y el 6, y el integrante de Ingeniería Industrial el 4.

## Criterio 1 · Problema y vertical (20 puntos)

**1. ¿Cuál es el problema, en una frase?**

Después del sismo, la comida donada llegó a la región y se atascó en el despacho. Según Portafolio, el 16 de agosto los bancos de alimentos tenían 404.587 kg en acopio y 157.164 kg en tránsito, y habían entregado 41.163 kg [F]. Según las fuentes que revisamos, ninguna herramienta en uso une el pedido de cada barrio o vereda, el vehículo, la vía abierta y la confirmación de entrega.

*Respaldo.* `docs/FICHA_CORTA.md`, componente 1. La cifra sale de Portafolio, del 16 de agosto, y está en `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 1. La nota no dice «sexto día» ni «en todo el país», no da fecha de corte y atribuye las cifras a «los Bancos de Alimentos» (`docs/FUENTES.md`, rama `fuentes-noche`, D3).

**2. ¿Por qué es un problema de Manizales y no solo del sismo?**

Porque en Manizales las vías se cierran también sin sismo. La salida a Letras suma 87 registros de cierre por deslizamiento o derrumbe entre 2017 y 2026. De ellos, 4 son del sismo, así que sin el sismo quedan 83, aunque un mismo derrumbe puede tener varios registros [F, cálculo nuestro]. Y en febrero de 2026, casi seis meses antes del sismo, la ciudad ya había declarado alerta amarilla por lluvias, con un umbral de 200 mm [F].

*Respaldo.* `docs/PILOTO.md`, sección 3; `docs/FICHA.md`, componente 1.

**3. La calamidad fue en agosto. ¿Por qué importa ahora?**

Porque la comida en especie sigue importando donde el efectivo no sirve, como en albergues, comedores, hogares infantiles y veredas que quedan aisladas cuando se cae una vía [I]. Además, ABACO proyectó que la emergencia duraría de 6 a 24 meses, y la calamidad pública de Manizales sigue vigente hasta el 9 de agosto de 2027 [F]. Por eso montamos el piloto sobre la operación diaria del Banco y sobre la temporada de lluvias.

*Respaldo.* `docs/FICHA.md`, componente 1, «Por qué ahora»; `docs/investigacion/11_voz_publica_actores.md`, sección 2.8.

**4. ¿Quiénes la van a usar? (mentoría 1)**

La usa quien despacha en el Banco Arquidiocesano de Alimentos de Manizales, que opera todo el año y fue uno de los principales puntos de acopio de ABACO en agosto [F, I]. Las 204 juntas de acción comunal de la ciudad, los comedores, los hogares y los albergues piden y confirman, y los conductores reportan las vías cerradas [F]. El Banco todavía no lo ha confirmado, y esa conversación es el primer hito del plan [P5].

*Respaldo.* `docs/FICHA.md`, componente 1, tabla de papeles; `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 4.

**5. ¿Hay evidencia de comida perdida o vencida en Manizales?**

No hay una cifra pública de comida dañada o vencida en Manizales ni en Caldas, así que no la damos [F]. Lo documentado es que desde el 11 de agosto el punto oficial de donaciones de la Alcaldía, en el Coliseo Menor, no recibía perecederos, y que a escala nacional ABACO pidió no donarlos por falta de refrigeración [F]. Por eso la línea base de desperdicio sale del inventario del Banco en los días 0 a 15 del piloto.

*Respaldo.* `docs/investigacion/11_voz_publica_actores.md`, sección 2.4; `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 3; `docs/PLAN_30_90.md`, día 15. El comunicado de la Alcaldía del 11 de agosto pone los perecederos bajo «No se recibe» en el punto del Coliseo Menor (`docs/FUENTES.md`, rama `fuentes-noche`, D10). Lo de ABACO es de la gerente de logística de la red, en Noticias RCN del 12 de agosto, y todavía no tiene fila en `docs/FUENTES.md`.

## Criterio 2 · Prototipo de solución (25 puntos)

**6. ¿Qué funciona hoy, de verdad?**

El bot de Telegram y el tablero corren en la nube desde el viernes a las 3:45 p. m. En la revisión de las 23:50 pasaron 345 pruebas automáticas [M]. El flujo va de punta a punta, del pedido por chat al plan para una flota mixta y al recálculo después de un cierre. El despachador aprueba cada plan con su nombre, y cada paquete se cierra con «ENTREGADO» y su código, por chat o por SMS [M].

*Respaldo.* `docs/FICHA.md`, componente 2; `torre/CANAL.md` en `main`, entrada de las 23:50. Repetimos el conteo después del congelamiento de las 8:30 a. m.

**7. ¿Qué mide el prototipo? (mentoría 1)**

La tabla por territorio resume, por comuna y vereda, los pedidos, las entregas, los críticos a tiempo y la espera, y lista los barrios y veredas sin pedidos registrados [M]. La bitácora guarda cada decisión con su hora y con quién la tomó, y el código de cada paquete fecha la entrega. Con esos tres registros, en el piloto calculamos los dos indicadores del reto con datos del Banco.

*Respaldo.* `encargos/T1_TERRITORIO.md`; `despacho/territorio.py`; `docs/PLAN_30_90.md`, sección 5. Después del congelamiento de las 8:30 a. m. confirmamos si la pestaña entró al tablero.

**8. ¿Qué pasa si el modelo entiende mal un pedido?**

Hay dos controles humanos. Ningún pedido entra al plan sin un lugar confirmado por quien escribió, y lo que el modelo no entiende queda como texto para el despachador. Después, el despachador revisa y aprueba cada plan con su nombre. En quince mensajes sintéticos escritos por nosotros, el extractor acertó 62 de 64 campos [M].

*Respaldo.* `entrada/pruebas/reporte_campos.md`; `docs/FICHA.md`, componente 2, pasos 1 y 2.

**9. ¿El sistema decide solo? ¿Y si manda un camión por una ladera inestable?**

No decide solo. El modelo lee y estructura, el optimizador y las reglas calculan, y el despachador decide. Una persona confirma cada cierre antes del recálculo y aprueba cada plan con su nombre, que queda en la bitácora [M]. Para las laderas, en el piloto y si el IDEA entrega sus datos, el A25 encarecerá, sin cerrarlas, las vías con historial de deslizamientos que estén en alerta naranja o roja.

*Respaldo.* `CLAUDE.md`, regla de arquitectura; `docs/FICHA.md`, componentes 2 y 3.

**10. ¿Y sin internet?**

Convite recibe pedidos, cierres y entregas por SMS leídos por reglas. Eso importa porque la mañana del 11 de agosto el 28 % de las estaciones base de Caldas estaba sin servicio, según MinTIC, y la CRC recomendó priorizar los mensajes de texto, igual que la página de MinTIC sobre la emergencia [F]. Con la red bloqueada, un portátil llegó a la hoja de ruta impresa y a una entrega registrada en 23 s [M]. Falta la prueba con el wifi apagado y con un celular real, y el mapa del tablero todavía necesita internet.

*Respaldo.* `docs/SIN_CONEXION.md`; `docs/investigacion/09_canales_sin_internet.md`, sección 1; `docs/RIESGOS.md`, R1. Noticias RCN, 11 de agosto, cita el informe de MinTIC para las estaciones y a la CRC para los mensajes de texto; la página de MinTIC es del 13 de agosto (`docs/FUENTES.md`, rama `fuentes-noche`, sección 7).

**11. ¿Cuánto mejora frente a como se despacha hoy?**

Todavía no sabemos cómo despacha hoy el Banco, y por eso el piloto lo mide con su propia línea base y con la reconstrucción de un mes. En simulación, con las velocidades de la tesis UNAL de 2019 y 30 jornadas por política, comparamos contra dos líneas base. Frente al despacho por orden de llegada, Convite sube los críticos a tiempo 23,3, 44,7 y 57,9 puntos, según la carga. Frente a un despachador con oficio, que atiende primero lo urgente y saca primero lo que vence, recorre 46,0, 56,0 y 42,2 km menos por jornada. En el total de entregas a tiempo empata con carga holgada y media, y con carga alta gana 3,0 puntos, con un intervalo de 0,7 a 5,3.

*Respaldo.* `docs/SIMULACION.md`, secciones 3 y 9; `docs/PLAN_30_90.md`, días 15 y 30.

*Nota para quien responde.* No presentes como resultado la ventaja en críticos frente al despachador con oficio. Esa corrida cambia a la vez la red y la velocidad, y todavía no llega la corrida que separa los dos efectos (`docs/SIMULACION.md`, sección 9.3). Además, la simulación no mide el valor de saber qué se pidió, dónde está cerrado y qué se entregó (`docs/SUGERENCIAS.md`, sección 4).

**12. ¿Cómo saben que un paquete llegó, y qué pasa si alguien pide dos veces?**

Cada paquete nace con un código al aprobar el plan y se cierra cuando alguien escribe «ENTREGADO» y el código. En el piloto solo cuenta la confirmación del destino o del conductor [M]. Si el mismo punto pide otra vez en menos de dos horas, el segundo pedido queda marcado como duplicado. Además, el módulo de filtro marca ráfagas y textos coordinados para que una persona decida, aunque todavía corre aparte del bot [M].

*Respaldo.* `docs/FICHA.md`, componentes 2 y 5; `docs/RIESGOS.md`, R13.

## Criterio 3 · Conocimiento utilizado (15 puntos)

**13. ¿Qué de la UNAL hay aquí, y qué está ya en el código?**

Lo principal es el indicador A25 del IDEA, la lluvia acumulada en 25 días por estación [F]. Con él, el optimizador encarece, sin cerrarlas, las vías con historial de deslizamientos que están en alerta naranja o roja (`docs/A25.md`, sección 2). Ya está en el código, con lluvia de prueba y apagado por defecto, y entra con datos del IDEA en los días 60 a 90. Estamos pidiendo el visto bueno de un profesor del instituto. Además, la patente 37476 ya está en el código como parámetro supuesto de vida útil [M], y la simulación ya usa velocidades derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48) [F].

*Respaldo.* `docs/FICHA.md`, componente 3; `encargos/P5_ALIADO_PILOTO.pdf`, sección 5.

**14. ¿Qué método usan?**

El núcleo es un ruteo de vehículos con capacidad y ventanas de tiempo. Lo resolvemos con OR-Tools sobre una matriz de tiempos por tipo de vehículo, y el vencimiento de cada lote perecedero entra como ventana dura. El plan se rehace con cada cierre confirmado, cada tanda de pedidos y cada regreso de un vehículo al acopio. La simulación es de eventos discretos, con semillas comunes, diferencias pareadas, intervalos del 95 % y una regla de decisión que escribimos antes de correrla.

*Respaldo.* `docs/FICHA.md`, componente 3, «Métodos»; `docs/SIMULACION.md`, secciones 2 a 4.

*Nota para quien responde.* Si preguntan qué tan lejos del óptimo queda OR-Tools, decimos que no tenemos una cota inferior. Si preguntan por los viajes, un solo viaje por vehículo y por plan es una simplificación declarada, que la simulación compensa recalculando cuando el vehículo vuelve (`docs/SUGERENCIAS.md`, sección 4).

**15. ¿La simulación no está hecha a su favor?**

Pusimos como línea base a un despachador con oficio que prioriza lo urgente y rota la bodega, porque una regla intuitiva puede quedar cerca del óptimo (Cook y Lodree, 2017). También encontramos dos supuestos optimistas. Uno eran los 39,0 km/h en vías primarias, frente a 22,6 km/h de media en la ruta de un bus diésel en Manizales (tesis UNAL de 2019, p. 50). El otro, un huevo que vencía en horas cuando dura días [M, F]. Esta noche repetimos la corrida con las velocidades de la tesis UNAL de 2019 (`docs/SIMULACION.md`, sección 9), pero la vida útil por producto todavía no se corrió.

*Respaldo.* `docs/SIMULACION.md`, sección 3; `docs/datos/flota_perecederos_costos.md`, secciones 1 y 3; `docs/RIESGOS.md`, R6.

**16. ¿Pueden usar la patente 37476?**

En el prototipo entra solo como parámetro supuesto, un factor de 1,2 sobre el tiempo que le queda a la fruta perecedera de un acopio con frío [M]. Su único respaldo es una cota inferior medida en gulupa a 8 °C en la solicitud de la patente, y su uso real hay que acordarlo con la oficina de propiedad intelectual de la UNAL. La anualidad de 2026 está pendiente, dentro del plazo de gracia [F].

*Respaldo.* `docs/FICHA.md`, componentes 3 y 5; `docs/investigacion/06_patentes_sipi.md`; `docs/investigacion/07_patentes_a_fondo.md`.

## Criterio 4 · Plan de 30 a 90 días (15 puntos)

**17. ¿Cómo es el piloto para la recuperación del territorio, y cómo miden el efecto si la calamidad fue en agosto?**

Durante 90 días, Convite entra a la operación diaria del Banco en una comuna y una vereda. La UGR acompaña el simulacro y las lluvias, y la Gobernación es la ruta hacia los municipios. El efecto lo medimos contra la línea base del propio Banco con cuatro instrumentos: su operación diaria, un simulacro con un cierre planeado, los cierres reales de las lluvias y la reconstrucción de agosto. Los datos salen de la tabla por territorio, de la bitácora y del código QR de cada entrega.

*Respaldo.* `docs/PLAN_30_90.md`, secciones 1 y 5; `docs/MENTORIA_1.md`, «En discusión: el piloto».

**18. ¿Por qué Ciudadela del Norte y El Manantial?**

Ciudadela del Norte es la comuna más poblada, con 58.776 habitantes según el ASIS de 2023, y el PMA ya recorrió con la Alcaldía las veredas con más daño para identificar necesidades de seguridad alimentaria [F]. En Pueblo Hondo el sismo dejó cuatro viviendas con pérdida total, y en la vía a Neira el registro de Maracas de enero de 2023 dice que no hay ruta alterna [F]. Además, dos CDI, un centro de salud y un CISCO quedan a entre 2,4 y 4,1 km del Banco, y Alto Bonito a 8,8 km [M]. Aun así, al final el Banco elige el territorio donde ya tenga más organizaciones.

*Respaldo.* `docs/PILOTO_TERRITORIOS.md`, propuesta 2 y recomendación; decisión de Carlos del 21 de noviembre a las 6:10 a. m.; `figuras_pitch/png/a_territorio_propuesta2.png`.

*Nota para quien responde.* Si preguntan por La Macarena y El Tablazo, esa es la propuesta 1, que pone comuna y vereda sobre una sola ruta. En la 2, la ruta a Alto Bonito sale por la comuna San José [M]. Elegimos la 2 porque el PMA ya levantó necesidades allí y porque las juntas de Alto del Guamo y Alto Bonito hablaron en la nota de la Alcaldía del 20 de agosto [F].

**19. ¿Qué pasa si la solución cambia? (mentoría 1)**

Cambia según una regla que ya está escrita. Si el Banco no responde o confirma que nadie reparte, el piloto pasa al flujo de requerimientos de la UGR o de la Gobernación, con los mismos instrumentos de medición. Y la solución ya cambió una vez después de la mentoría 1, cuando pasó de atender los barrios del sismo a la operación diaria del Banco.

*Respaldo.* `docs/DECISIONES_9PM.md`, decisión 1; `docs/PLAN_30_90.md`, sección 3; `docs/MENTORIA_1.md`, «La idea».

**20. ¿Cuándo dirían que el piloto falló, y quién responde por cada hito?**

Cada hito tiene escrito un criterio para seguir, ajustar o parar. El más duro es el del día 30. Si Convite no ahorra kilómetros ni reduce el desperdicio frente a lo que ya hace el Banco, el día en paralelo se rediseña. El integrante de Ingeniería Industrial lleva la relación con el Banco y la medición, Samuel las juntas y la UGR, Jacobo el tablero y la bitácora, y Carlos el optimizador y la simulación.

*Respaldo.* `docs/PLAN_30_90.md`, sección 6.

## Criterio 5 · Viabilidad y aliados (15 puntos)

**21. ¿Hay algo parecido? (mentoría 1)**

Hay piezas sueltas. El RUD dice quién es damnificado, la Cruz Roja registra hogares con AccessRC y KoboCollect, SUMA de la OPS lleva inventario y entregas, y la plataforma de ABACO recauda y le reporta al donante [F]. También hay programas abiertos que calculan rutas, como VROOM, pero ninguna fuente consultada describe uno que una pedido, vehículo, vía y entrega [F].

*Respaldo.* `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 2; `docs/ESTADO_DEL_ARTE.md`, sección 1.

*Nota para quien responde.* En la región, los Bomberos de Chinchiná usan un mapa con zonas y jefes de despacho por jornada (La Patria, 21 de agosto; investigación 11, sección 2.8). Si preguntan por Google Maps o Waze, se responde que dan una ruta para un carro, pero no reparten veinte pedidos entre vehículos distintos ni saben qué se vence [I].

**22. ¿Por qué no se usa aquí? (mentoría 1)**

Porque cada pieza sirve a su dueño y a otro fin. El RUD sirve para subsidios y cerró el 4 de septiembre dejando por fuera a familias rurales dispersas, SUMA no planea rutas y las herramientas de la Cruz Roja focalizan a sus propios beneficiarios [F]. Las barreras locales de costo, capacitación, nombres de los lugares y confianza son hipótesis nuestras, y cada una tiene su pregunta de validación para los aliados [H].

*Respaldo.* `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 3; `docs/PILOTO.md`, sección 1.

**23. ¿Tienen un aliado confirmado?**

Todavía no, y ningún aliado ha visto la propuesta completa. Esta mañana el integrante de Ingeniería Industrial llamó al Banco Arquidiocesano para pedir una visita con demostración, y su respuesta se dice tal cual [P5]. Si el Banco no responde, la regla de cambio lleva el piloto a la UGR o a la Gobernación.

*Respaldo.* `encargos/P5_ALIADO_PILOTO.pdf`; `docs/FICHA.md`, componente 5, tabla de aliados.

**24. ¿Por qué Telegram y no WhatsApp?**

Porque Telegram se despliega en una hora y no cobra por mensaje, así que con él tuvimos la demo corriendo hoy. WhatsApp queda para el piloto, y como la lectura del mensaje es un módulo aparte, cambiar de canal no toca el optimizador ni el tablero [I]. Quien no tenga datos escribe por SMS, que cualquier celular envía [F].

*Respaldo.* `torre/TORRE_CAPITAN.md`, decisiones; `docs/FICHA_4_5_6_BORRADOR.md`, costos; `docs/investigacion/09_canales_sin_internet.md`, sección 3.

**25. ¿Cuánto cuesta y quién lo paga?**

Leer 10.000 mensajes con el modelo costaría entre 1,75 y 4,50 USD, un estimado que no medimos con el modelo real [E]. Como el piloto usa la flota del Banco, el único gasto en efectivo que podemos estimar son los vehículos del simulacro si nadie los presta, entre 718.800 y 3.112.353 COP a precios de 2019 y 2021 [E]. Faltan por cotizar el servidor, el plan de SMS y las horas del equipo. El acompañamiento al piloto lo prevén las bases para los equipos premiados.

*Respaldo.* `entrada/ESCALA.md`; `docs/PLAN_30_90.md`, sección 7; `datos_publicos/costos.csv`.

**26. ¿Qué pasa después del día 90?**

El sistema corre en un portátil del acopio con software abierto, en Python con SQLite y OR-Tools, así que no exige pagar licencias [M]. El plan lo deja en manos del Banco y de la UGR, sin una estructura paralela como las gerencias del FOREC de 1999. Su autonomía frente a las autoridades locales debilitó la gobernanza territorial [I, F]. El Banco de Alimentos de Bogotá ya cobra 270 COP por kilo de fruta y verdura para cubrir costos logísticos, así que la operación podría caber en un esquema así [F, I].

*Respaldo.* `docs/RIESGOS.md`, R9; `docs/FICHA.md`, componente 5; `datos_publicos/costos.csv`.

**27. ¿Y los datos personales?**

El bot no lee el nombre, el usuario ni el teléfono de la cuenta, y el remitente queda como un código que no se puede revertir sin una sal guardada fuera del repositorio [M]. El texto se limpia antes de llamar al modelo y antes de guardarlo. Lo limpia una heurística que quita lo que tiene forma de dato personal, aunque no garantiza que no quede ninguno. A los aliados no les pedimos datos personales de beneficiarios, en línea con la Ley 1581 de 2012.

*Respaldo.* `entrada/README.md`, sección «Privacidad (Ley 1581)»; `docs/RIESGOS.md`, R4.

## Criterio 6 · Impactos esperados (10 puntos)

**28. ¿A cuántas personas beneficia?**

Todavía no lo sabemos para el territorio del piloto. Lo medimos en los días 0 a 15 con el catálogo de puntos del Banco. Para dar una escala, al cierre de agosto ABACO reportaba más de 2.000 toneladas para más de 9.470 familias en 36 municipios y comunidades, y Ciudadela del Norte, la comuna del piloto, tiene 58.776 habitantes según el ASIS de 2023 [F]. Los beneficiarios directos son el despachador, los voluntarios y las juntas, y los finales son quienes comen en comedores, hogares, albergues y veredas.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/PILOTO_TERRITORIOS.md`, propuesta 2.

**29. ¿Qué metas ponen a los dos indicadores del reto?**

Las entregas a tiempo en puntos críticos deben quedar iguales o mejores que la línea base del Banco, medida en sus dos semanas de bitácora. El desperdicio de perecederos debe quedar por debajo del 5 %, que es la meta del reto, y lo medimos con el inventario y sus vencimientos. La simulación solo sirve de referencia, porque ninguno de sus números viene de una operación real.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/PLAN_30_90.md`, sección 5.

**30. ¿Priorizar lo crítico no deja peor a otros?**

Sí tiene un costo, y la simulación lo mide como la espera adicional del punto peor atendido frente al despacho por orden de llegada. En simulación, con carga media y 30 jornadas por política, ese punto espera 3,07 horas más que con el despacho por orden de llegada y 0,53 horas más que con el despachador con oficio. Ese indicador no tiene meta, y lo reportamos cada semana por comuna y vereda en la tabla por territorio. El despachador puede cambiar cualquier plan que deje a un punto esperando demasiado.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/RIESGOS.md`, R14.
