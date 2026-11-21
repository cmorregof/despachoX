# DespachoX en un día normal

**Tesis.** Un sistema que solo se enciende el día del desastre, ese día no sirve. Nadie lo ha usado, nadie confía en él y no tiene datos cargados. DespachoX tiene que ganarse el puesto en la operación de todos los días: repartir lo que el banco de alimentos recibe antes de que se venza. Así, el día del sismo ya es la herramienta de siempre.

Etiquetas: **[F]** tomado de una fuente, **[M]** medido por nosotros, **[E]** estimado, **[I]** inferencia nuestra y **[pendiente]**, que falta. Ninguna persona del equipo ha abierto todavía las fuentes de los informes de `docs/investigacion/`. Las marcadas «resumen de búsqueda» las encontró una sesión de Claude el 20 de noviembre y nadie ha leído la nota completa. Antes de usar cualquiera en el pitch, se abre y se pasa a `docs/FUENTES.md`.

## 1. Por qué las herramientas que nacen con la emergencia llegan tarde

**El Registro Único de Damnificados (RUD), 2026.** Cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas y étnicas. Tampoco permitía reclasificar viviendas ni registrar daños por réplicas, y la Procuraduría pidió reabrirlo [F] ([Vanguardia, 5 oct 2026](https://www.vanguardia.com/colombia/2026/10/05/procuraduria-pide-a-la-ungrd-agilizar-ayudas-para-damnificados-por-el-terremoto/)). Fue una herramienta pensada para el momento: quien no alcanzó a registrarse no existió para ella.

**Providencia, huracán Iota, 2020.** Para recibir un kit había que hacer un registro web en una isla sin servicios. Los encargados no conocían el territorio, la entrega fue desigual y aparecieron fundaciones «de la noche a la mañana» [F] ([El Colombiano](https://www.elcolombiano.com/colombia/providencia-padece-un-viacrucis-por-las-ayudas-humanitarias-HG14216890)). La herramienta y la gente que la operaba llegaron con la emergencia, sin conocer el lugar.

**El contraste: Salva RS, Rio Grande do Sul, 2024.** Dieciséis voluntarios la hicieron en unas 48 horas para ordenar los pedidos de rescate que circulaban por WhatsApp. Facilitó 21.500 rescates, y desde el tercer día la usaban la Defensa Civil y la Fuerza Aérea. Era una web y no una aplicación, por la mala conectividad, y los casos graves se confirmaban por teléfono [F] ([Fast Company Brasil](https://fastcompanybrasil.com/impacto/aplicativo-gaucho-feito-em-menos-de-48-horas-ajuda-no-resgate-de-215-mil-pessoas/)).

**Lo que sacamos de los tres [I].** Salva RS también nació con la emergencia, y funcionó. La lección no es «nunca construyas en la emergencia». Es que se adopta, bajo presión, lo que no le pide nada nuevo a nadie: usa el canal que la gente ya tiene, no exige instalar ni registrarse y deja una persona confirmando. El RUD y Providencia exigieron un trámite nuevo justo cuando nadie podía hacerlo. Salva RS tuvo suerte de ser simple. DespachoX no quiere depender de la suerte: si se usa a diario, el día del sismo el despachador ya sabe operarlo, los puntos de entrega ya están cargados y los comités ya conocen el chat.

## 2. El uso diario: el banco de alimentos

Un banco de alimentos recibe excedentes de supermercados, industria y centrales de abasto, muchos cerca de vencer, y los reparte a fundaciones, comedores y hogares de paso.

- En 2025 los bancos de la red ABACO manejaron unas 54.000 toneladas: cerca de 42.000 rescatadas y 12.000 compradas. Según su director, lo rescatado es del orden del 0,5 % de la comida que se bota en el país [F, resumen de búsqueda; nota por abrir] ([La República](https://www.larepublica.co/responsabilidad-social/que-ocurre-con-los-alimentos-que-no-logran-vender-los-supermercados-de-colombia-4330123)).
- Colombia pierde y desperdicia 9,76 millones de toneladas de alimentos al año, el 34 % de la oferta disponible. La cifra es del estudio del DNP de 2016 y no se ha actualizado [F] ([DNP](https://dnp.gov.co/Prensa_/Noticias/Paginas/el-dnp-se-une-con-las-centrales-de-abastos-para-fortalecer-los-procesos-logisticos-y-la-reduccion-de-perdida-de-alimentos.aspx); [estudio, 2016](https://www.minsalud.gov.co/sites/rid/Lists/BibliotecaDigital/RIDE/INEC/IGUB/perdida-y-desperdicio-de-alimentos-en-colombia-2016.pdf?ID=18402)).
- ABACO atiende comedores, ollas comunitarias, albergues y hospitales [F] ([La República, 18 ago 2026](https://www.larepublica.co/empresas/entrevista-con-juan-carlos-buitrago-director-ejecutivo-de-abaco-4458863)). El Banco de Alimentos de Manizales es uno de los que opera la Iglesia a través de su arquidiócesis dentro de ABACO [F, resumen de búsqueda] ([Las2orillas](https://www.las2orillas.co/?p=904404)). **Cómo despacha hoy el banco de Manizales, con qué flota y con qué registros: [pendiente]**, y no lo vamos a suponer.

**Repartir lo que hay en bodega es el problema que DespachoX ya resuelve:**

| En un día normal del banco | Lo que DespachoX ya hace |
|---|---|
| Una fundación o un comedor pide por teléfono o por chat | El bot lee el pedido, confirma el lugar y lo guarda (`entrada/`) |
| La bodega tiene lotes con fecha de vencimiento | Cada lote tiene vencimiento y sale primero lo que vence primero (`despacho/`) |
| Pocos vehículos, rutas por ladera | Optimizador con flota mixta y capacidad por vehículo |
| Una vía se cierra por lluvia | Cierre reportado por chat y recálculo del plan |
| Demostrarle al donante a dónde llegó lo que dio | Paquete con código y confirmación de entrega |

**Lo que no hace sin cambios.** Recoger las donaciones en cada donante y llevarlas a bodega es un problema de recogida y entrega, y el optimizador de hoy no lo modela: todos los viajes salen del acopio. Tampoco tiene pedidos recurrentes, como «el comedor recibe cada martes». El piloto empieza por el reparto desde la bodega, que sí corre hoy. La recogida es un desarrollo aparte, después del día 90.

**El desperdicio es su indicador de todos los días.** En la simulación, sacar de bodega primero lo que vence primero deja los perecederos vencidos en 0,0 %. Sacarlos por orden de ingreso pierde 0,5 %, 1,8 % y 3,5 % según la carga [M] (`docs/SIMULACION.md`, 30 semillas por carga). Esa regla la cumple cualquier despachador cuidadoso. Lo que pone DespachoX es que se cumpla aunque esté de turno el voluntario que llegó ayer.

## 3. Las vías del Eje Cafetero se cierran sin sismo

| Año | Qué pasó | Fuente |
|---|---|---|
| Marzo de 2017 | Un derrumbe cierra la vía Manizales–Fresno en el sector Brisas | [F] [La FM, 21 mar 2017](https://www.lafm.com.co/colombia/via-manizales-bogota-cerrada-derrumbe) |
| Abril de 2017 | Deslizamientos en laderas de Manizales: 17 muertos y calamidad pública | [F] [El País, 19 abr 2017](https://www.elpais.com.co/colombia/aumentan-a-17-los-muertos-tras-derrumbes-en-manizales-y-declaran-la-calamidad-publica.html) |
| Marzo de 2021 | Cierre total de la doble calzada Manizales–Chinchiná en el km 11+500 por un deslizamiento de unos 4.000 m³; desvío por la vía antigua, sector La Siria | [F] [ANI, 22 mar 2021](https://www.ani.gov.co/w/se-mantiene-el-cierre-total-de-la-v%C3%ADa-manizales-chinchin%C3%A1-debido-a-las-fuertes-lluvias) |
| Marzo de 2023 | Cierre total e indefinido de la vía Manizales–Mariquita por lluvias; desvío por el Alto de La Línea | [F] [Infobae, 16 mar 2023](https://www.infobae.com/colombia/2023/03/16/cierre-total-en-la-via-manizales-bogota-por-deslizamientos/) |
| Junio de 2023 | Un deslizamiento en el Alto de Letras (km 24) vuelve a cerrar la salida a Bogotá | [F] [La FM, 7 jun 2023](https://www.lafm.com.co/colombia/manizales-bogota-esta-completamente-cerrada) |
| Agosto de 2026 | Dos días después del sismo seguían cerradas Pereira–Chinchiná (km 22 a 24) y Manizales–Fresno por Letras (km 36 a 40) | [F] [Semana](https://www.semana.com/nacion/articulo/actualizacion-de-las-vias-que-siguen-cerradas-tras-el-terremoto-en-colombia/202602/) |

**El indicador A25 del IDEA-UNAL existe porque el riesgo es permanente.** Mide la lluvia acumulada en 25 días por estación, con alerta amarilla de 200 a 300 mm, naranja de 300 a 400 y roja desde 400. El reporte de 2020 cubre 14 estaciones de Manizales [F] ([reporte A25 de 2020, IDEA](https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf)). El 16 de febrero de 2026, seis meses antes del sismo, Manizales declaró alerta amarilla por lluvias con el mismo umbral de 200 mm [F] ([Blu Radio](https://www.bluradio.com/nacion/manizales-entra-en-alerta-amarilla-por-lluvias-que-superan-niveles-historicos-rg10)). Que el umbral sea el del A25 es una coincidencia que notamos nosotros; la nota no nombra al IDEA [I].

Recalcular cuando se cierra una vía no es una función de emergencia: en Manizales sirve cualquier temporada de lluvias [I].

## 4. Doble propuesta de valor

| | Operación diaria | Emergencia |
|---|---|---|
| Qué gana el operador | Menos kilómetros con la misma flota | Más entregas a tiempo en puntos críticos |
| Número que tenemos [M] | Frente a un despachador con oficio (`experta`), entre 47 y 75 km menos por jornada, del 5 % al 11 % del recorrido: −75,1 [−92,8; −57,4] en carga holgada, −55,5 [−73,1; −37,9] en media y −46,7 [−72,2; −21,2] en alta | Frente a despacho por orden de llegada (`ingenua`): +12,0, +28,9 y +46,3 puntos en críticos a tiempo según la carga. Frente a `experta`, empate con el factor por defecto; con factor crítico 3, 99,7 % contra 98,5 % en carga media |
| Escenario | Simulado con 3 a 8 cierres por jornada. **Sin cierres, que es el día normal: [pendiente], lo corre el equipo de simulación** | El mismo |
| Desperdicio de perecederos | 0,0 % con la regla de bodega, frente a 0,5–3,5 % por orden de ingreso | El mismo |

Todo es simulación: 30 semillas por nivel de carga, red real de Manizales, pedidos y lotes sintéticos. Las diferencias son pareadas, con intervalo del 95 % (`docs/SIMULACION.md`). Dos salvedades abiertas inflan las cifras:

- Las velocidades del grafo (39 km/h en vías primarias) superan los 22,6 km/h medidos con GPS en un bus de Manizales.
- La vida útil del huevo en la semilla es de horas, cuando debería ser de días (canal, 17:31).

Lo que cuesta priorizar: el punto peor atendido espera entre 0,9 y 4,3 horas más que con la política ingenua [M].

El bot aguanta unos 900 mensajes por minuto, medido con un extractor falso. Leer 10.000 mensajes con el modelo costaría entre 1,75 y 4,50 USD, estimado sin medir (`entrada/ESCALA.md`).

## 5. Cómo cambia el plan de 30 a 90 días

El cambio de fondo: **el hito del día 60 deja de ser un simulacro inventado y pasa a ser un día normal de reparto en paralelo.** El operador reparte como siempre. DespachoX planea esa misma jornada en sombra, con los mismos pedidos, la misma bodega y la misma flota. Después se comparan los dos.

| Día | Hito | Entregable | Responsable | Validación |
|---|---|---|---|---|
| 0 a 15 | Acuerdo con el Banco de Alimentos de Manizales | Carta de intención y entrega de los tres datos de la sección 6 | Samuel | Carta firmada y datos recibidos |
| 15 a 30 | Reconstrucción en frío de un mes | Plan que habría dado DespachoX para cada día del mes registrado, contra lo que se hizo | Carlos | Kilómetros, kilos vencidos y entregas a tiempo: real contra reconstruido |
| 30 a 45 | Puntos y canal del operador cargados | Catálogo de puntos en el sistema; las fundaciones del banco piden por el chat | Samuel y Jacobo | Veinte pedidos reales de punta a punta |
| **45 a 60** | **Un día normal de reparto en paralelo** | El despachador reparte como siempre y DespachoX planea el mismo día; informe de la comparación | Todo el equipo | **Kilómetros (odómetro o GPS) y kilos que vencieron esa semana, contra la forma actual del operador** |
| 60 a 75 | Riesgo de ladera en las rutas | Indicador A25 conectado como penalización por tramo | Carlos | Rutas que evitan tramos en alerta durante una semana de lluvia registrada |
| 75 a 90 | Dos semanas de operación en sombra y decisión | El sistema propone y el despachador decide; acuerdo de adopción o cierre | Todo el equipo | Porcentaje de planes aprobados sin cambios; decisión del operador |

El simulacro con un comité barrial y un cierre simulado sale del día 60. Si el operador lo pide, entra en las dos semanas finales.

**Criterio de parada.** Si en la reconstrucción en frío DespachoX no ahorra kilómetros ni reduce el desperdicio frente a lo que ya hace el operador, el día en paralelo se rediseña antes de pedirle tiempo a nadie.

## 6. Qué le pedimos al operador

Sin estos tres datos no hay piloto. Ninguno necesita datos personales de quienes reciben la ayuda (Ley 1581). Cualquier formato sirve: una hoja de cálculo, una exportación o fotos del cuaderno.

1. **Catálogo de puntos de entrega.** Fundaciones, comedores, albergues y hogares que el banco atiende: nombre, dirección o coordenadas, tipo de punto, si es prioritario, qué vehículo entra y horario de recepción.
2. **Inventario con fechas de vencimiento.** Producto, kilos, fecha de ingreso, fecha de vencimiento, si necesita frío y en qué bodega está. Lo ideal es un corte por día del mismo mes del registro.
3. **Registro de despachos de un mes.** Fecha, punto, productos y kilos, vehículo y, si existen, hora de salida, hora de entrega y kilómetros. Sin nombres de beneficiarios ni de conductores.

**Lo que el operador recibe:**

- el informe de la reconstrucción en frío, con sus propios números;
- la herramienta, funcionando con sus datos;
- el compromiso de que los datos siguen siendo suyos y no salen del proyecto.

**Lo que no sabemos y no vamos a inventar:** si el banco registra hoy los vencimientos, si guarda el registro de despachos, cuántos vehículos tiene y cuántos puntos atiende. Todo eso es [pendiente] hasta la primera conversación.

## 7. Para la ficha: componente 5, viabilidad y aliados

1. DespachoX se gana el puesto en la operación diaria del Banco de Alimentos de Manizales, no solo el día del desastre.
2. Razón: el RUD y Providencia exigieron un trámite nuevo en plena emergencia y excluyeron gente. Salva RS fue adoptado al tercer día porque era simple [F].
3. Uso diario: repartir desde bodega a fundaciones y comedores lo que está por vencer. Es el problema que el prototipo ya resuelve, sin cambios.
4. No cubre todavía la recogida en donantes ni los pedidos recurrentes; quedan para después del día 90.
5. Escala del problema diario: la red ABACO manejó unas 54.000 t en 2025 [F, por abrir], frente a 9,76 Mt perdidas o desperdiciadas al año en Colombia [F, DNP 2016].
6. Las vías se cierran sin sismo: Manizales–Chinchiná en 2021, Manizales–Mariquita y Letras en 2023 y los deslizamientos de 2017 [F]. Por eso existe el A25 del IDEA-UNAL.
7. Valor diario: entre 47 y 75 km menos por jornada que un despachador con oficio, del 5 % al 11 % [M, simulación con cierres]. Sin cierres: [pendiente].
8. Valor en emergencia: críticos a tiempo +12 a +46 puntos frente al orden de llegada; empate frente a un despachador con oficio [M].
9. Hito del día 60: un día normal de reparto en paralelo, midiendo kilómetros y desperdicio contra la forma actual del operador.
10. Al operador le pedimos el catálogo de puntos, el inventario con vencimientos y un mes de despachos, sin datos personales.
