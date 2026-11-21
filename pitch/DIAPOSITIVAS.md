# Diapositivas del pitch · DespachoX

Versión 1, viernes 20 de noviembre en la noche, rama `pitch-noche`. Contenido de cada diapositiva, listo para montar. El orden y los tiempos salen de `pitch/GUION.md`, y las cifras, de `pitch/CIFRAS_PITCH.md`.

## Cómo usar este documento

- **Conteo de palabras.** El texto en pantalla tiene 15 palabras como mucho, contando el título. No cuentan el pie de fuente ni las etiquetas del visual (ejes, mapa, recuadros), que se listan aparte y van cortas.
- **Asterisco.** Marca una cifra por verificar. Si a la 1:00 p. m. nadie ha abierto su fuente, la cifra se quita de la diapositiva.
- **[SIM].** Marca un número de la simulación nueva, que llega hacia las 6:00 a. m. Toda figura con [SIM] lleva la etiqueta «Simulación», su línea base y su número de jornadas.
- **Estilo.** La paleta del informe corto: tinta #4F4086, ámbar #A36752, crema #EBD3A2 y ceniza #6E6878, sobre fondo claro. La letra es Ancízar Serif si está instalada; sus archivos no están en el repositorio público y los tiene Carlos. Si no está, una serif del sistema.
- **Plantilla.** El kit de la hackathon trae una «plantilla de presentación» que el viernes dio acceso denegado (`docs/PLATAFORMA_INNOVO.md`). Si la organización la comparte, estas diapositivas se montan en ella.
- **Entrega.** iNNOVO pide un enlace de Drive, con permiso para que el jurado lo abra, antes de las 2:30 p. m. Conviene subir el PDF de las diapositivas.
- **Figuras existentes.** Están en `docs/informe/figuras/`: `barras_abaco.pdf`, `mapa_manizales.pdf` y `piezas_sueltas.tex`. Los dos PDF se regeneran con los scripts de `docs/informe/figuras/scripts/`. La figura TikZ se compila suelta con los colores definidos en `docs/informe/informe_corto.tex`.

## Orden en el pitch de tres minutos

| Diapositiva | Bloque del guion | Tiempo |
|---|---|---|
| 1 · Por qué | 1 | 0:00 a 0:19 |
| 2 · Las vías se cierran sin sismo | 2 | 0:19 a 0:33 |
| 3 · Para quién | 3 | 0:33 a 0:51 |
| 4 · Lo que existe | 4 | 0:51 a 1:06 |
| 5 · En vivo, y luego el tablero | 5 | 1:06 a 2:09 |
| 6 · Qué medimos | 6 | 2:09 a 2:30 |
| 7 · El piloto | 7 y 8 | 2:30 a 2:57 |
| 8 · Cierre | 8 | 2:57 a 3:00 |

Las diapositivas A a H son de respaldo. Solo salen si un jurado pregunta, o en la versión de cinco minutos.

---

## Diapositiva 1 · Por qué

**Texto en pantalla (9 palabras).** «La comida llegó. Lo que se atascó fue despacharla.»

**Visual.** Figura existente `docs/informe/figuras/barras_abaco.pdf`, la figura 2 del informe corto. Son tres barras horizontales con los kilos de la red de bancos de alimentos al sexto día: 404.587 en acopio, 157.164 en tránsito y 41.163 entregados*. La genera `docs/informe/figuras/scripts/barras_abaco.py`.

**Pie de fuente.** «Red de bancos de alimentos, todo el país, al sexto día del sismo. Portafolio, 16 de agosto de 2026*.»

**Nota del orador.** La cifra es de todo el país, así que se dice «en todo el país». Si preguntan por Manizales, la ciudad fue uno de los principales puntos de acopio de la red (Noticias RCN, 10 de agosto*). No hay cifra pública de lo que despachó el Banco de Manizales, y eso se dice así.

**Criterio.** 1, problema y vertical: evidencia.

**Evidencia que deja.** Una cifra con fuente citada, en pantalla.

---

## Diapositiva 2 · Las vías se cierran sin sismo

**Texto en pantalla (7 palabras).** «Las vías se cierran también sin sismo.»

**Etiquetas del mapa.** Sobre la flecha de la salida a Letras: «87 registros de cierre desde 2017, 4 del sismo*». Sobre la flecha de la autopista del Café: «21 oct 2026: un carril, solo livianos*».

**Visual.** Figura existente `docs/informe/figuras/mapa_manizales.pdf`, la figura 1 del informe corto. Muestra la red vial, los 50 puntos de entrega reales del escenario público (35 críticos), los dos acopios y dos flechas hacia los corredores cerrados del 10 al 12 de agosto. Las dos etiquetas se añaden en el editor de diapositivas, sin tocar el script. Datos de las etiquetas:

- Letras: `docs/datos/vias_y_riesgo.md`, sección 3, tabla por corredor, fila «salida a Letras» (total 87). Las 4 del sismo son las filas S04, S09, S10 y S11 de `datos_publicos/cierres_historicos.csv` (conteo nuestro sobre ese archivo).
- Autopista del Café: `docs/datos/vias_y_riesgo.md`, sección 2, «Septiembre a noviembre», y la fila S22 del mismo archivo.

No conviene una gráfica de registros por año, porque esos conteos son mínimos y no sirven para comparar años (`docs/datos/vias_y_riesgo.md`, sección 3).

**Pie de fuente.** «INVÍAS, registro #767, y prensa, 2017 a 2026. Un derrumbe puede tener varios registros. Red vial: © colaboradores de OpenStreetMap (ODbL).»

**Nota del orador.** Son registros y no eventos, y hay registros todos los años desde 2017. Si preguntan cuánto dura un cierre, el patrón es un cierre total de horas seguido de semanas a un carril. Por ejemplo, el 15 de noviembre de 2025, en el km 14+700 de la vía a Fresno, hubo 3,6 horas de cierre total y luego 37 días a un carril*.

**Criterio.** 1, problema y vertical: la ficha de la vertical 04 habla de derrumbes en las vías de acceso.

**Evidencia que deja.** Un conteo propio sobre una fuente pública, que se repite con el CSV del repositorio.

---

## Diapositiva 3 · Para quién

**Texto en pantalla (11 palabras).** «Para quien despacha y para quienes piden, en barrios y veredas.»

**Visual por hacer.** Cuatro columnas con un ícono cada una y etiquetas cortas.

| Despacha | Pide | Reporta las vías | Avala |
|---|---|---|---|
| Banco Arquidiocesano de Alimentos | Comedores, hogares infantiles y 204 juntas de acción comunal, 73 de vereda* | Conductores y socorristas | Unidad de Gestión del Riesgo |

Debajo, en ceniza: «Reciben quienes comen en comedores, hogares y veredas».

Datos: `docs/informe/informe_corto.tex`, tabla 1 («Quién despacha, quién pide, quién reporta vías y quién decide»), y `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 4.5. Las juntas vienen del consolidado de la Alcaldía de Manizales de 2025.

**Pie de fuente.** «Juntas: Alcaldía de Manizales, 2025*. Papeles propuestos por el equipo con la investigación 10; el Banco aún no ha visto la propuesta.» Si hubo visita al Banco, la última frase se cambia por lo que pasó.

**Nota del orador.** Que el Banco sea el usuario principal es inferencia nuestra, y depende de la conversación con el Banco. Según `docs/PILOTO_TERRITORIOS.md`, los albergues de los coliseos cerraron el 29 de agosto (dato de la investigación 11, no verificado). Por eso los puntos críticos de hoy serían CDI, hogares infantiles, centros de salud y Centros Vida, que es una inferencia de ese documento.

**Criterio.** 1, beneficiarios, y 6, beneficiarios.

**Evidencia que deja.** Un mapa de actores con fuente y la cifra de juntas con su fuente.

---

## Diapositiva 4 · Lo que existe

**Texto en pantalla (9 palabras).** «Piezas sueltas. Ninguna une pedido, vehículo, vía y entrega.»

**Visual.** Figura existente `docs/informe/figuras/piezas_sueltas.tex`, la figura 3 del informe corto. Son cuatro recuadros morados con su dueño y su fin: el RUD de la UNGRD dice quién es damnificado, KoboCollect y AccessRC de la Cruz Roja registran hogares, SUMA/LSS de la OPS lleva inventario y entregas, y la plataforma de ABACO recauda y le reporta al donante. Debajo va el recuadro ámbar de la pieza que falta, «pedido → vehículo → vía → entrega», con una flecha «exporta» hacia SUMA.

**Pie de fuente.** «Elaborado con la investigación 10 del equipo. El RUD cerró el 4 de septiembre (Vanguardia, 5 de octubre de 2026*).»

**Nota del orador.** Las barreras con evidencia son de propósito y de dueño, porque cada pieza sirve a su dueño y a otro fin (investigación 10, sección 3). Costo, capacitación, nombres locales y confianza son hipótesis sin fuente pública. Si preguntan por Google Maps o Waze, la respuesta es que dan una ruta para un carro, pero no reparten pedidos entre vehículos distintos ni saben qué se vence.

**Criterio.** 1, si hay algo parecido, y 2, pertinencia y creatividad, porque el aporte es la integración.

**Evidencia que deja.** Un inventario de alternativas con fuente (investigación 10, sección 2).

---

## Diapositiva 5 · En vivo

Sale uno o dos segundos mientras el operador cambia al tablero. Si el cambio es inmediato, se salta.

**Texto en pantalla (9 palabras).** «En vivo. Un jurado reporta un derrumbe por chat.»

**Visual.** El tablero a pantalla completa. Aparte, una tarjeta impresa que no es diapositiva, con el QR del bot y el mensaje «derrumbe en la avenida del centro, no pasa camion, si pasa moto». El QR lo genera rol A con el enlace real del bot.

**Nota del orador.** El bloque 5 de `pitch/GUION.md`. Si algo falla, se pasa al video de respaldo.

**Criterio.** 2, funcionamiento y demostración.

**Evidencia que deja.** Algo que corre, en vivo, con un jurado adentro.

---

## Diapositiva 6 · Qué medimos

**Texto en pantalla (14 palabras).** «Cada entrega confirmada entra a la tabla de su comuna y vereda.» Y sobre la barra de la derecha, «Simulación: [SIM]».

**Visual por hacer, en dos paneles.**

- **Izquierda, la tabla por territorio.** Una captura de la pestaña «Territorio» del tablero, si está lista antes de las 8:30 a. m. Si no, una tabla hecha con `python -m despacho.territorio --csv /tmp/t.csv` sobre la base de la demo, con las columnas `territorio`, `pedidos`, `kg_entregados`, `pct_criticos_a_tiempo` y `espera_mediana_h`. Al lado va la lista de barrios y veredas «sin pedidos registrados», del archivo `_sin_pedidos` que el comando escribe junto a la tabla. Etiqueta obligatoria: «Datos sintéticos de la demo».
- **Derecha, la simulación.** Barras de entregas a tiempo en puntos críticos por política (orden de llegada, despachador con oficio y DespachoX), con su intervalo del 95 %, para el nivel de carga que se cite en voz alta. Datos: la corrida nueva con velocidades medidas, en la sección nueva de `docs/SIMULACION.md` y en su carpeta de resultados de `despacho/sim/`. Etiqueta obligatoria: «Simulación: [SIM] jornadas sintéticas sobre la red vial de Manizales. Supuestos en docs/SIMULACION.md».

**Pie de fuente.** «Tabla: `despacho/territorio.py`, con datos sintéticos. Simulación del equipo, 21 de noviembre de 2026 [SIM].»

**Nota del orador.** La tabla dice «sin pedidos registrados» y nunca «sin necesidad», porque que un barrio no pida no quiere decir que esté bien (`despacho/territorio.py`). Si un punto crítico deja de pedir, entra a la cola una visita de verificación, que nunca sale con comida. Si preguntan por la simulación, se dicen la línea base, el número de jornadas y los supuestos. También lo que no prueba: no mide el valor de recibir pedidos por chat ni el de la trazabilidad (`docs/SIMULACION.md`, sección 7).

**Criterio.** 2, porque el prototipo mide, y 6, indicadores verificables.

**Evidencia que deja.** Algo que corre, la tabla, y un número medido con su línea base, la simulación.

---

## Diapositiva 7 · El piloto

**Texto en pantalla (14 palabras).** «Piloto de 90 días en la rutina del Banco: La Macarena y El Tablazo.»

**Visual por hacer, en dos piezas.**

- **Línea de tiempo.** Cuatro tramos, cada uno con su hito y su validación en pocas palabras, tomados de `docs/FICHA_CORTA.md`, componente 4.

| Días | Hito | Validación |
|---|---|---|
| 0 a 15 | Acuerdo y línea base, con carta del Banco y aval de la UGR | Carta firmada y línea base medida |
| 15 a 30 | Reconstrucción en frío de un mes | Real contra reconstruido |
| 30 a 60 | Un día normal planeado en sombra | Kilómetros y kilos vencidos frente a la forma actual |
| 60 a 90 | Simulacro con la UGR y A25 por tramo | Decisión escrita del Banco |

Debajo de la línea, la regla de cambio: «Si el Banco no reparte, el piloto pasa al flujo de la UGR y la Gobernación». Los responsables de cada tramo se toman del plan que escribe otro agente esta noche.

- **El corredor del territorio.** La opción rápida es un esquema: Banco Arquidiocesano, luego los tres CDI de La Macarena a entre 2,9 y 3,3 km, y luego Bajo Tablazo a 9,3 km por la vía a Chinchiná [M]. La opción con más tiempo es un mapa con `datos_publicos/puntos.csv`, `datos_publicos/acopios.csv` y la red vial. Las distancias salen de `docs/PILOTO_TERRITORIOS.md`, propuesta 1. Etiquetas: «Sismo: daños en El Carmen y Bajo Tablazo*» y «Java, 2025: unas 150 familias incomunicadas, según un líder local*».

**Pie de fuente.** «Calamidad pública de Manizales vigente hasta el 9 de agosto de 2027 (Alcaldía, 16 de octubre de 2026*). A25: IDEA, UNAL Sede Manizales. Daños: La Patria, 13 sep 2026 y 19 mar 2025*.»

**Nota del orador.** La recuperación del territorio, para este piloto, es que la capacidad de despachar quede en manos locales, con el Banco, las juntas y la UGR, y que se use entre desastres (`docs/FICHA_CORTA.md`, componente 4; lecciones del FOREC en la investigación 10, sección 5.4). Al Banco se le piden tres datos sin información personal: su catálogo de puntos, su inventario con vencimientos y un mes de despachos (`docs/PILOTO.md`, sección 6). Hay un criterio de parada. Si la reconstrucción en frío no ahorra kilómetros ni desperdicio, el piloto se rediseña antes de pedirle tiempo a nadie (`docs/PILOTO.md`, sección 5). El territorio lo decide el Banco, donde tenga más organizaciones inscritas.

**Criterio.** 4, hitos, entregables y validación; 5, aliados y riesgo, por la regla de cambio; 3, el A25.

**Evidencia que deja.** Un plan con hito y validación en cada tramo, y un territorio con nombre y con fuente.

---

## Diapositiva 8 · Cierre

**Texto en pantalla (12 palabras).** «DespachoX · Equipo 19 · Que la comida llegue aunque la vía se cierre.»

**Visual.** El nombre en grande. Debajo, en letra pequeña, el repositorio `github.com/cmorregof/despachoX` y los nombres del equipo: Samuel Rosso, Carlos Orrego, Nicolás Ramírez, Jacobo Vasco y José Manuel Aristizábal (`docs/ESTRATEGIA.md`). Si el equipo cambió de nombre en el encargo P3, va el nombre nuevo.

**Nota del orador.** La regla de cambio y la última frase del bloque 8.

**Criterio.** 2, porque deja el enlace al código que corre.

**Evidencia que deja.** El repositorio abierto, con las pruebas y el guion de la demo.

---

## Respaldo para preguntas

### A · Conocimiento UNAL y métodos

**Texto en pantalla (13 palabras).** «Conocimiento UNAL: A25 del IDEA, patente 37476 y dos tesis de la Sede.»

**Visual por hacer.** Una tabla de cuatro filas con la capacidad, qué es, dónde entra en DespachoX y su estado, tomada de `docs/FICHA_CORTA.md`, componente 3.

| Capacidad | Qué es | Dónde entra | Estado |
|---|---|---|---|
| A25 del IDEA, Sede Manizales | Lluvia acumulada de 25 días por estación. Alerta amarilla desde 200 mm, naranja desde 300 y roja desde 400* | Sube el costo de cada tramo según la alerta de la estación más cercana | Días 60 a 90 del piloto; hoy no está en el código. Se actualiza si entra antes de las 8:30 a. m. |
| Patente 37476, composición que captura etileno | Alarga la vida útil de un lote | Parámetro supuesto de 1,2, solo en fruta perecedera de un acopio con frío | En el código como supuesto. Único respaldo: cota inferior en gulupa a 8 °C* |
| Tesis de maestría, UNAL Manizales, 2019 | 22,6 km/h medidos con GPS en un bus de la ciudad* | Recalibra las velocidades de la simulación | Confirmar que la corrida nueva la usa [SIM] |
| Tesis de maestría, UNAL Manizales, 2017, dirigida por William Ariel Sarache Castro | Análisis de la red de ayuda humanitaria de Manizales* | Orienta el mapa de actores del piloto | Por verificar |

Debajo, métodos y datos: ruteo con capacidad y ventanas de tiempo en OR-Tools sobre la red de OpenStreetMap, 50 puntos de entrega reales con fuente (35 críticos), 178 registros de cierres viales y una simulación pareada con dos líneas base. Pedidos y lotes son sintéticos.

**Pie de fuente.** «IDEA, reporte A25 de 2020*. Solicitud de la patente 37476, folio 18*. Investigaciones 07 y 08 del equipo.»

**Nota del orador.** El 16 de febrero de 2026 Manizales declaró alerta amarilla con 200 mm en menos de 25 días, que es el umbral amarillo del A25. La nota de prensa no nombra al IDEA, así que la relación es un cotejo nuestro. El visto bueno de un profesor del IDEA está en gestión, y se actualiza el sábado. La arquitectura del modelo que lee, el código que calcula y la persona que decide viene de CARMEN, proyecto 56031 de Minciencias. La palabra «vigente» para la patente se dice solo si se confirma la anualidad 2026.

**Criterio.** 3, conocimiento utilizado.

**Evidencia que deja.** Cada capacidad con nombre, uso concreto y estado, y su fuente citada.

### B · Sin internet

**Texto en pantalla (11 palabras).** «Sin internet, el despachador sigue decidiendo y nada registrado se pierde.»

**Visual por hacer.** Una escalera de cuatro peldaños, de `docs/SIN_CONEXION.md`: (1) normal, con bot, nube, modelo y mapa en línea; (2) acopio aislado, con todo en un portátil y SMS por wifi local, leídos por reglas; (3) solo voz y radio, con una persona que digita y rutas impresas; (4) vuelve la señal y lo acumulado sube a la nube. Al lado, una página de la hoja de ruta impresa con QR, sacada de un PDF de `python -m despacho.hoja`.

**Pie de fuente.** «Medido con la red bloqueada, no con el wifi apagado: de la carga de datos a una entrega registrada en 23 s*.»

**Nota del orador.** El 11 de agosto en la mañana, el 28 % de las estaciones base de Caldas estaba sin servicio, y MinTIC recomendó usar SMS (Noticias RCN*). El lector de SMS acertó 20 de 20 mensajes sintéticos en una prueba que no es independiente. Falta probarlo todo con el wifi apagado y con un celular real, y el mapa del tablero todavía necesita internet.

**Criterio.** 5, factibilidad y riesgo de conectividad, y 2, funcionamiento.

**Evidencia que deja.** Una medición propia, con su salvedad escrita.

### C · La simulación en detalle

**Texto en pantalla (8 palabras).** «Simulación: [SIM] jornadas, dos líneas base, supuestos escritos.»

**Visual por hacer.** La tabla de la corrida nueva. Por nivel de carga, y para orden de llegada, despachador con oficio y DespachoX: críticos a tiempo, entregas a tiempo en todos los puntos, perecederos vencidos, kilómetros y espera del punto peor atendido, con diferencias pareadas e intervalos del 95 %. Datos: la sección nueva de `docs/SIMULACION.md` [SIM]. Debajo, los supuestos que cambiaron: velocidades acotadas a lo medido y vida útil de `datos_publicos/vida_util.csv` (aviso del canal de las 17:31).

**Pie de fuente.** «Simulación del equipo, 21 de noviembre de 2026 [SIM]. Lo que no prueba: `docs/SIMULACION.md`, sección 7.»

**Nota del orador.** Se reporta tal como salió. La primera corrida queda en revisión y no se cita.

**Criterio.** 2 y 6.

**Evidencia que deja.** Un número medido con su línea base, su número de jornadas y sus supuestos.

### D · Aliados

**Texto en pantalla (12 palabras).** «Qué le pedimos a cada aliado y en qué va cada conversación.»

**Visual.** La tabla de aliados de `docs/FICHA_CORTA.md`, componente 5 (Banco, UGR, Gobernación, Cruz Roja e IDEA con SIMAC), con la columna «Estado» actualizada el sábado a la 1:00 p. m. No lleva nombres ni teléfonos de personas que no hayan dado permiso.

**Pie de fuente.** «Estado al sábado 21 de noviembre, [hora]. El Banco recibe el informe con sus números y la herramienta con sus datos, que siguen siendo suyos.»

**Nota del orador.** Hasta el viernes en la noche ningún aliado había visto la propuesta. Lo que pasó en la llamada de las 8:00 a. m. se dice tal cual.

**Criterio.** 5, aliados y padrinos.

**Evidencia que deja.** Cada aliado con lo que se le pide y su estado real.

### E · Tres territorios

**Texto en pantalla (8 palabras).** «Tres territorios posibles. Al final decide el Banco.»

**Visual.** Tres columnas con las viñetas de `docs/PILOTO_TERRITORIOS.md`, sección «Para la diapositiva», sin cambiar ninguna cifra: La Macarena y El Tablazo; Ciudadela del Norte y El Manantial; Atardeceres y Kilómetro 41.

**Pie de fuente.** «Fuentes en `docs/PILOTO_TERRITORIOS.md`. Distancias por la red vial del equipo.»

**Nota del orador.** Ese documento recomienda la 1, porque el sismo dejó daño con fuente en sus dos partes y sus accesos se caen también sin sismo. Además, comuna y vereda quedan sobre una sola ruta. La 3 conviene si el IDEA respalda la prueba del A25.

**Criterio.** 4, y también 1 por el territorio.

**Evidencia que deja.** Evidencia del sismo por territorio, con fuente.

### F · Indicadores del piloto

**Texto en pantalla (10 palabras).** «Seis indicadores, todos contra la línea base del propio Banco.»

**Visual.** La tabla de indicadores de `docs/FICHA_CORTA.md`, componente 6, con indicador, línea base, meta y verificación. Las cifras de simulación de esa tabla son de la primera corrida y se cambian por [SIM].

**Pie de fuente.** «Indicadores del reto: entregas a tiempo en puntos críticos y desperdicio de perecederos por debajo del 5 %.»

**Nota del orador.** La espera del punto peor atendido no tiene meta y se vigila, porque priorizar lo crítico la aumenta. En la simulación nueva esa espera es [SIM].

**Criterio.** 6, impactos.

**Evidencia que deja.** Indicadores verificables, cada uno con su línea base y su medio de verificación.

### G · Lo que no sabemos

**Texto en pantalla (13 palabras).** «Lo que todavía no sabemos y a quién se lo vamos a preguntar.»

**Visual.** Cuatro preguntas de `docs/informe/informe_corto.tex`, sección 6, cada una con a quién se le hace: cómo despacha hoy el Banco y si reparte o las organizaciones recogen (Banco y ABACO); cuánta comida se dañó o se venció en agosto (UGR, Cruz Roja y Banco); si se activó SUMA (UGR); cuánto duraron los cierres después del 12 de agosto (UGR y Policía de Tránsito).

**Nota del orador.** Sirve para responder con honestidad «¿cómo saben que el Banco lo va a usar?».

**Criterio.** 1 y 5, riesgos.

**Evidencia que deja.** Los vacíos declarados, con a quién se les pregunta.

### H · Cómo funciona

**Texto en pantalla (9 palabras).** «El modelo lee. El optimizador calcula. El despachador decide.»

**Visual por hacer.** Un flujo de cinco cajas: pedido por chat o SMS; el modelo lo lee y pregunta el lugar; el optimizador reparte entre camión, campero y moto, primero lo que vence primero; el despachador aprueba; y el QR confirma la entrega. Una flecha de vuelta va desde «cierre reportado por un conductor» hasta el optimizador. Fuente: `docs/ESTRATEGIA.md`, sección 3, «Flujo».

**Nota del orador.** El modelo nunca decide una ruta ni despacha nada. Esta diapositiva reemplaza a la demo si fallan la demo y el video a la vez.

**Criterio.** 2 y 3, métodos.

**Evidencia que deja.** La arquitectura declarada, que se puede comprobar en el código.

La matriz de riesgos y el banco de preguntas los prepara otro agente en otra rama. Si llegan, entran aquí como diapositivas de respaldo.
