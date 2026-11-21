# DespachoX · Preguntas probables del jurado

Banco de 30 preguntas para ensayar la defensa del sábado, agrupadas por criterio de la rúbrica. Versión del sábado 21 de noviembre de 2026, en la madrugada, rama `defensa-noche`. Cada respuesta cabe en dos o tres frases y nombra el archivo que la respalda. Las cinco preguntas que dejó la mentoría 1 llevan la marca «mentoría 1».

**Marcas.** [F] dato de una fuente, que alguien del equipo debe abrir en `docs/FUENTES.md` antes de decirlo en voz alta. [M] medido por el equipo. [E] estimado. [I] inferencia nuestra. [H] hipótesis por validar. Las cifras de simulación salen de `docs/SIMULACION.md`, sección 9, y de `despacho/sim/resultados_velocidades/tablas.md`. [P5] se actualiza con el resultado de la visita al Banco, que el integrante de Ingeniería Industrial reporta a las 12:30 p. m.

**Regla para responder.** Si no sabemos algo, lo decimos y nombramos el hito del piloto que lo va a medir. Toda cifra de simulación se dice con su línea base y con la palabra simulación.

**Propuesta de reparto, por confirmar con Carlos.** Samuel responde los criterios 1 y 5, Jacobo el 2, Carlos el 3 y el 6, y el integrante de Ingeniería Industrial el 4.

## Criterio 1 · Problema y vertical (20 puntos)

**1. ¿Cuál es el problema, en una frase?**

Después del sismo, la comida donada llegó a la región y se atascó en el despacho. Según Portafolio, el 16 de agosto los bancos de alimentos tenían 404.587 kg en acopio y 157.164 kg en tránsito, y habían entregado 41.163 kg [F]. Según las fuentes que revisamos, ninguna herramienta en uso une el pedido de cada barrio o vereda, el vehículo, la vía abierta y la confirmación de entrega.

*Respaldo.* `docs/FICHA_CORTA.md`, componente 1. La cifra es de Portafolio, 16 de agosto, en `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 1. La nota no dice «sexto día» ni «en todo el país», no da fecha de corte y atribuye las cifras a «los Bancos de Alimentos» (`docs/FUENTES.md`, rama `fuentes-noche`, D3).

**2. ¿Por qué es un problema de Manizales y no solo del sismo?**

Las vías de Manizales se cierran también sin sismo. La salida a Letras suma 87 registros de cierre por deslizamiento o derrumbe entre 2017 y 2026, y 4 de ellos son del sismo, así que sin el sismo quedan 83. Un mismo derrumbe puede tener varios registros [F, C]. En febrero de 2026, casi seis meses antes del sismo, la ciudad ya había declarado alerta amarilla por lluvias con un umbral de 200 mm [F].

*Respaldo.* `docs/PILOTO.md`, sección 3; `docs/FICHA.md`, componente 1.

**3. La calamidad fue en agosto. ¿Por qué importa ahora?**

La comida en especie sigue importando donde el efectivo no sirve, como en albergues, comedores, hogares infantiles y veredas que quedan aisladas cuando se cae una vía [I]. ABACO proyectó que la emergencia duraría de 6 a 24 meses, y la calamidad pública de Manizales sigue vigente hasta el 9 de agosto de 2027 [F]. Por eso el piloto se monta sobre la operación diaria del Banco y sobre la temporada de lluvias.

*Respaldo.* `docs/FICHA.md`, componente 1, «Por qué ahora»; `docs/investigacion/11_voz_publica_actores.md`, sección 2.8.

**4. ¿Quiénes la van a usar? (mentoría 1)**

La usa quien despacha en el Banco Arquidiocesano de Alimentos de Manizales, que opera todo el año y fue uno de los principales puntos de acopio de ABACO en agosto [F, I]. Piden y confirman las 204 juntas de acción comunal de la ciudad, los comedores, los hogares y los albergues, mientras los conductores reportan las vías cerradas [F]. El Banco todavía no lo ha confirmado, y esa conversación es el primer hito del plan [P5].

*Respaldo.* `docs/FICHA.md`, componente 1, tabla de papeles; `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 4.

**5. ¿Hay evidencia de comida perdida o vencida en Manizales?**

No hay una cifra pública de comida dañada o vencida en Manizales ni en Caldas, así que no la damos [F]. Lo documentado es que desde el 11 de agosto el punto oficial de donaciones de la Alcaldía, en el Coliseo Menor, no recibía perecederos, y que a escala nacional ABACO pidió no donarlos por falta de refrigeración [F]. La línea base de desperdicio sale del inventario del Banco en los días 0 a 15 del piloto.

*Respaldo.* `docs/investigacion/11_voz_publica_actores.md`, sección 2.4; `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 3; `docs/PLAN_30_90.md`, día 15. El comunicado de la Alcaldía del 11 de agosto pone los perecederos bajo «No se recibe» en el punto del Coliseo Menor (`docs/FUENTES.md`, rama `fuentes-noche`, D10). Lo de ABACO es de la gerente de logística de la red, en Noticias RCN del 12 de agosto, y todavía no tiene fila en `docs/FUENTES.md`.

## Criterio 2 · Prototipo de solución (25 puntos)

**6. ¿Qué funciona hoy, de verdad?**

El bot de Telegram y el tablero corren en la nube desde el viernes a las 3:45 p. m., y en la revisión de las 23:50 pasaron 345 pruebas automáticas [M]. El flujo corre de punta a punta, del pedido por chat al plan para una flota mixta y al recálculo después de un cierre. El despachador aprueba cada plan con su nombre, y cada paquete se cierra con «ENTREGADO» y su código, por chat o por SMS [M].

*Respaldo.* `docs/FICHA.md`, componente 2; `torre/CANAL.md` en `main`, entrada de las 23:50. El conteo se repite después del congelamiento de las 8:30 a. m.

**7. ¿Qué mide el prototipo? (mentoría 1)**

La tabla por territorio resume por comuna y vereda los pedidos, las entregas, los críticos a tiempo y la espera, y lista los barrios y veredas sin pedidos registrados [M]. La bitácora guarda cada decisión con su hora y con quién la tomó, y el código de cada paquete fecha la entrega. Con esos tres registros, en el piloto los dos indicadores del reto se calculan con datos del Banco.

*Respaldo.* `encargos/T1_TERRITORIO.md`; `despacho/territorio.py`; `docs/PLAN_30_90.md`, sección 5. Que la pestaña del tablero haya entrado se confirma después del congelamiento de las 8:30 a. m.

**8. ¿Qué pasa si el modelo entiende mal un pedido?**

En quince mensajes sintéticos escritos por el equipo, el extractor acertó 62 de 64 campos [M]. Ningún pedido entra al plan sin un lugar confirmado por quien escribió, y lo que el modelo no entiende queda como texto para el despachador. Después, el despachador revisa y aprueba cada plan con su nombre.

*Respaldo.* `entrada/pruebas/reporte_campos.md`; `docs/FICHA.md`, componente 2, pasos 1 y 2.

**9. ¿El sistema decide solo? ¿Y si manda un camión por una ladera inestable?**

No decide solo, porque el modelo lee y estructura, el optimizador y las reglas calculan, y el despachador decide. Una persona confirma cada cierre antes del recálculo y aprueba cada plan con su nombre, que queda en la bitácora [M]. En el piloto, si el IDEA entrega sus datos, el A25 subirá el costo de los tramos en alerta para que las rutas eviten las laderas.

*Respaldo.* `CLAUDE.md`, regla de arquitectura; `docs/FICHA.md`, componentes 2 y 3.

**10. ¿Y sin internet?**

La mañana del 11 de agosto el 28 % de las estaciones base de Caldas estaba sin servicio, según MinTIC. La CRC recomendó priorizar los mensajes de texto, y la página de MinTIC sobre la emergencia también los recomienda [F]. DespachoX recibe pedidos, cierres y entregas por SMS leídos por reglas, y con la red bloqueada un portátil llegó a la hoja de ruta impresa y a una entrega registrada en 23 s [M]. Falta la prueba con el wifi apagado y con un celular real, y el mapa del tablero todavía necesita internet.

*Respaldo.* `docs/SIN_CONEXION.md`; `docs/investigacion/09_canales_sin_internet.md`, sección 1; `docs/RIESGOS.md`, R1. Noticias RCN, 11 de agosto, cita el informe de MinTIC para las estaciones y a la CRC para los mensajes de texto; la página de MinTIC es del 13 de agosto (`docs/FUENTES.md`, rama `fuentes-noche`, sección 7).

**11. ¿Cuánto mejora frente a como se despacha hoy?**

No sabemos todavía cómo despacha hoy el Banco, y por eso el piloto lo mide con su propia línea base y con la reconstrucción de un mes. En simulación comparamos contra dos líneas base, el despacho por orden de llegada y un despachador con oficio que atiende primero lo urgente y saca primero lo que vence. En simulación, con las velocidades de la tesis UNAL de 2019 y 30 jornadas por política, DespachoX sube los críticos a tiempo 23,3, 44,7 y 57,9 puntos frente al despacho por orden de llegada, según la carga. Frente al despachador con oficio recorre 46,0, 56,0 y 42,2 km menos por jornada. En el total de entregas a tiempo empata con carga holgada y media, y con carga alta gana 3,0 puntos, con un intervalo de 0,7 a 5,3.

*Respaldo.* `docs/SIMULACION.md`, secciones 3 y 9; `docs/PLAN_30_90.md`, días 15 y 30.

*Nota para quien responde.* La ventaja en críticos frente al despachador con oficio no se da como resultado. Esa corrida cambia a la vez la red y la velocidad, y la corrida que separa los dos efectos (`docs/SIMULACION.md`, sección 9.3) no ha llegado. Lo que la simulación no mide es el valor de saber qué se pidió, dónde está cerrado y qué se entregó (`docs/SUGERENCIAS.md`, sección 4).

**12. ¿Cómo saben que un paquete llegó, y qué pasa si alguien pide dos veces?**

Cada paquete nace con un código al aprobar el plan y se cierra cuando alguien escribe «ENTREGADO» y el código, y en el piloto solo cuenta la confirmación del destino o del conductor [M]. Un segundo pedido del mismo punto en menos de dos horas queda marcado como duplicado. El módulo de filtro, que todavía corre aparte del bot, marca ráfagas y textos coordinados para que una persona decida [M].

*Respaldo.* `docs/FICHA.md`, componentes 2 y 5; `docs/RIESGOS.md`, R13.

## Criterio 3 · Conocimiento utilizado (15 puntos)

**13. ¿Qué de la UNAL hay aquí, y qué está ya en el código?**

La capacidad principal es el indicador A25 del IDEA, la lluvia acumulada en 25 días por estación, que en el piloto subirá el costo de cada tramo según la alerta de la estación más cercana [F]. Hoy no está en el código, porque entra en los días 60 a 90 con datos del IDEA, y estamos pidiendo el visto bueno de un profesor del instituto. En el código ya está la patente 37476 como parámetro supuesto de vida útil [M], y la simulación se recalibra con velocidades medidas con GPS en una tesis de la Sede [F].

*Respaldo.* `docs/FICHA.md`, componente 3; `encargos/P5_ALIADO_PILOTO.pdf`, sección 5.

**14. ¿Qué método usan?**

El núcleo es un ruteo de vehículos con capacidad y ventanas de tiempo, resuelto con OR-Tools sobre una matriz de tiempos por tipo de vehículo, con el vencimiento de cada lote perecedero como ventana dura. El plan se rehace con cada cierre confirmado, cada tanda de pedidos y cada regreso de un vehículo al acopio. La simulación es de eventos discretos, con semillas comunes, diferencias pareadas, intervalos del 95 % y una regla de decisión escrita antes de correr.

*Respaldo.* `docs/FICHA.md`, componente 3, «Métodos»; `docs/SIMULACION.md`, secciones 2 a 4.

*Nota para quien responde.* Si preguntan qué tan lejos del óptimo queda OR-Tools, no tenemos una cota inferior, y se dice así. Un solo viaje por vehículo y por plan es una simplificación declarada, que la simulación compensa recalculando cuando el vehículo vuelve (`docs/SUGERENCIAS.md`, sección 4).

**15. ¿La simulación no está hecha a su favor?**

Pusimos como línea base a un despachador con oficio que prioriza lo urgente y rota la bodega, porque una regla intuitiva puede quedar cerca del óptimo (Cook y Lodree, 2017). Encontramos dos supuestos optimistas, 39,0 km/h en vías primarias cuando un bus medido con GPS en Manizales promedió 22,6 km/h, y un huevo que vencía en horas cuando dura días [M, F]. La corrida se repitió esta noche con las velocidades de la tesis UNAL de 2019 (`docs/SIMULACION.md`, sección 9). La vida útil por producto todavía no se corrió.

*Respaldo.* `docs/SIMULACION.md`, sección 3; `docs/datos/flota_perecederos_costos.md`, secciones 1 y 3; `docs/RIESGOS.md`, R6.

**16. ¿Pueden usar la patente 37476?**

En el prototipo entra solo como parámetro supuesto, un factor de 1,2 sobre el tiempo que le queda a la fruta perecedera de un acopio con frío [M]. Su único respaldo es una cota inferior medida en gulupa a 8 °C en la solicitud de la patente, y su uso real se acuerda con la oficina de propiedad intelectual de la UNAL. La anualidad de 2026 está pendiente, dentro del plazo de gracia [F].

*Respaldo.* `docs/FICHA.md`, componentes 3 y 5; `docs/investigacion/06_patentes_sipi.md`; `docs/investigacion/07_patentes_a_fondo.md`.

## Criterio 4 · Plan de 30 a 90 días (15 puntos)

**17. ¿Cómo es el piloto para la recuperación del territorio, y cómo miden el efecto si la calamidad fue en agosto?**

DespachoX entra 90 días a la operación diaria del Banco en una comuna y una vereda, con la UGR en el simulacro y las lluvias y con la Gobernación como ruta hacia los municipios. El efecto se mide contra la línea base del propio Banco con cuatro instrumentos, que son su operación diaria, un simulacro con un cierre planeado, los cierres reales de las lluvias y la reconstrucción de agosto. Los datos salen de la tabla por territorio, la bitácora y el código QR de cada entrega.

*Respaldo.* `docs/PLAN_30_90.md`, secciones 1 y 5; `docs/MENTORIA_1.md`, «En discusión: el piloto».

**18. ¿Por qué Ciudadela del Norte y El Manantial?**

Ciudadela del Norte es la comuna más poblada, con 58.776 habitantes según el ASIS de 2023, y el PMA ya recorrió con la Alcaldía las veredas con más daño para identificar necesidades de seguridad alimentaria [F]. El sismo dejó cuatro viviendas con pérdida total en Pueblo Hondo, y en la vía a Neira el registro de Maracas de enero de 2023 dice que no hay ruta alterna [F]. Además, dos CDI, un centro de salud y un CISCO quedan a entre 2,4 y 4,1 km del Banco, y Alto Bonito a 8,8 km [M], aunque al final el Banco elige el territorio donde ya tenga más organizaciones.

*Respaldo.* `docs/PILOTO_TERRITORIOS.md`, propuesta 2 y recomendación; decisión de Carlos del 21 de noviembre a las 6:10 a. m.; `figuras_pitch/png/a_territorio_propuesta2.png`.

*Nota para quien responde.* Si preguntan por La Macarena y El Tablazo, la propuesta 1 pone comuna y vereda sobre una sola ruta, y en la 2 la ruta a Alto Bonito sale por la comuna San José [M]. Se eligió la 2 porque el PMA ya levantó necesidades allí y las juntas de Alto del Guamo y Alto Bonito hablaron en la nota de la Alcaldía del 20 de agosto [F].

**19. ¿Qué pasa si la solución cambia? (mentoría 1)**

La regla de cambio está escrita desde ahora. Si el Banco no responde o confirma que nadie reparte, el piloto pasa al flujo de requerimientos de la UGR o de la Gobernación, con los mismos instrumentos de medición. La solución ya cambió una vez después de la mentoría 1, cuando pasó de atender los barrios del sismo a la operación diaria del Banco.

*Respaldo.* `docs/DECISIONES_9PM.md`, decisión 1; `docs/PLAN_30_90.md`, sección 3; `docs/MENTORIA_1.md`, «La idea».

**20. ¿Cuándo dirían que el piloto falló, y quién responde por cada hito?**

Cada hito tiene un criterio escrito para seguir, ajustar o parar. El más duro es el del día 30, cuando el día en paralelo se rediseña si DespachoX no ahorra kilómetros ni reduce el desperdicio frente a lo que ya hace el Banco. El integrante de Ingeniería Industrial lleva la relación con el Banco y la medición, Samuel las juntas y la UGR, Jacobo el tablero y la bitácora, y Carlos el optimizador y la simulación.

*Respaldo.* `docs/PLAN_30_90.md`, sección 6.

## Criterio 5 · Viabilidad y aliados (15 puntos)

**21. ¿Hay algo parecido? (mentoría 1)**

Hay piezas sueltas. El RUD dice quién es damnificado, la Cruz Roja registra hogares con AccessRC y KoboCollect, SUMA de la OPS lleva inventario y entregas, y la plataforma de ABACO recauda y le reporta al donante [F]. Hay además programas abiertos que calculan rutas, como VROOM, pero ninguna fuente consultada describe uno que una pedido, vehículo, vía y entrega [F].

*Respaldo.* `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 2; `docs/ESTADO_DEL_ARTE.md`, sección 1.

*Nota para quien responde.* En la región, los Bomberos de Chinchiná usan un mapa con zonas y jefes de despacho por jornada (La Patria, 21 de agosto; investigación 11, sección 2.8). Si preguntan por Google Maps o Waze, dan una ruta para un carro y no reparten veinte pedidos entre vehículos distintos ni saben qué se vence [I].

**22. ¿Por qué no se usa aquí? (mentoría 1)**

Cada pieza sirve a su dueño y a otro fin. El RUD sirve para subsidios y cerró el 4 de septiembre dejando por fuera a familias rurales dispersas, SUMA no planea rutas y las herramientas de la Cruz Roja focalizan a sus propios beneficiarios [F]. Las barreras locales de costo, capacitación, nombres de los lugares y confianza son hipótesis nuestras, y cada una tiene su pregunta de validación para los aliados [H].

*Respaldo.* `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 3; `docs/PILOTO.md`, sección 1.

**23. ¿Tienen un aliado confirmado?**

Todavía no, y ningún aliado ha visto la propuesta completa. Esta mañana el integrante de Ingeniería Industrial llamó al Banco Arquidiocesano para pedir una visita con demostración, y su respuesta se dice tal cual [P5]. Si el Banco no responde, la regla de cambio lleva el piloto a la UGR o a la Gobernación.

*Respaldo.* `encargos/P5_ALIADO_PILOTO.pdf`; `docs/FICHA.md`, componente 5, tabla de aliados.

**24. ¿Por qué Telegram y no WhatsApp?**

Telegram se despliega en una hora y no cobra por mensaje, así que permitió tener la demo corriendo hoy. WhatsApp queda para el piloto, y como la lectura del mensaje es un módulo aparte, cambiar de canal no toca el optimizador ni el tablero [I]. Quien no tenga datos escribe por SMS, que cualquier celular envía [F].

*Respaldo.* `torre/TORRE_CAPITAN.md`, decisiones; `docs/FICHA_4_5_6_BORRADOR.md`, costos; `docs/investigacion/09_canales_sin_internet.md`, sección 3.

**25. ¿Cuánto cuesta y quién lo paga?**

Leer 10.000 mensajes con el modelo costaría entre 1,75 y 4,50 USD, estimado sin medir con el modelo real [E]. Como el piloto usa la flota del Banco, su único gasto en efectivo estimable son los vehículos del simulacro si nadie los presta, entre 718.800 y 3.112.353 COP a precios de 2019 y 2021 [E]. El servidor, el plan de SMS y las horas del equipo están por cotizar, y el acompañamiento al piloto está previsto en las bases para los equipos premiados.

*Respaldo.* `entrada/ESCALA.md`; `docs/PLAN_30_90.md`, sección 7; `datos_publicos/costos.csv`.

**26. ¿Qué pasa después del día 90?**

El sistema corre en un portátil del acopio con software abierto, en Python con SQLite y OR-Tools, así que no exige pagar licencias [M]. El plan lo deja en manos del Banco y de la UGR, sin una estructura paralela como las gerencias del FOREC de 1999, cuya autonomía frente a las autoridades locales debilitó la gobernanza territorial [I, F]. El Banco de Alimentos de Bogotá ya cobra 270 COP por kilo de fruta y verdura para cubrir costos logísticos, así que la operación podría caber en un esquema así [F, I].

*Respaldo.* `docs/RIESGOS.md`, R9; `docs/FICHA.md`, componente 5; `datos_publicos/costos.csv`.

**27. ¿Y los datos personales?**

El bot no lee el nombre, el usuario ni el teléfono de la cuenta, y el remitente queda como un código que no se puede revertir sin una sal guardada fuera del repositorio [M]. El texto se limpia antes de llamar al modelo y antes de guardarlo, con una heurística que quita lo que tiene forma de dato personal aunque no garantiza que no quede ninguno. A los aliados no les pedimos datos personales de beneficiarios, en línea con la Ley 1581 de 2012.

*Respaldo.* `entrada/README.md`, sección «Privacidad (Ley 1581)»; `docs/RIESGOS.md`, R4.

## Criterio 6 · Impactos esperados (10 puntos)

**28. ¿A cuántas personas beneficia?**

Todavía no lo sabemos para el territorio del piloto, y se mide en los días 0 a 15 con el catálogo de puntos del Banco. Como escala, al cierre de agosto ABACO reportaba más de 2.000 toneladas para más de 9.470 familias en 36 municipios y comunidades, y Ciudadela del Norte, la comuna del piloto, tiene 58.776 habitantes según el ASIS de 2023 [F]. Los beneficiarios directos son el despachador, los voluntarios y las juntas, y los finales son quienes comen en comedores, hogares, albergues y veredas.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/PILOTO_TERRITORIOS.md`, propuesta 2.

**29. ¿Qué metas ponen a los dos indicadores del reto?**

Las entregas a tiempo en puntos críticos deben quedar iguales o mejores que la línea base del Banco, medida en sus dos semanas de bitácora. El desperdicio de perecederos debe quedar por debajo del 5 %, la meta del reto, medido con el inventario y sus vencimientos. La simulación solo sirve de referencia, porque ninguno de sus números viene de una operación real.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/PLAN_30_90.md`, sección 5.

**30. ¿Priorizar lo crítico no deja peor a otros?**

Sí tiene un costo, que la simulación mide como la espera adicional del punto peor atendido frente al despacho por orden de llegada. En simulación, con carga media y 30 jornadas por política, el punto peor atendido espera 3,07 horas más que con el despacho por orden de llegada y 0,53 horas más que con el despachador con oficio. Ese indicador no tiene meta, y se reporta cada semana por comuna y vereda en la tabla por territorio. El despachador puede cambiar cualquier plan que deje a un punto esperando demasiado.

*Respaldo.* `docs/FICHA.md`, componente 6; `docs/RIESGOS.md`, R14.
