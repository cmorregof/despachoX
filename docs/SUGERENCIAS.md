# Sugerencias del maestro · auditoría del viernes 20 de noviembre, 2:45 p. m.

Sesión `maestro`. Revisé `main` hasta el commit `1730169`: estrategia, canal, simulación, `lugares/`, `despacho/`, esquema, semilla, el tablero y el bot recién subidos, guion del pitch, borrador de la ficha y los encargos A, C, B2 y S2. No escribí código del producto. Para no opinar de memoria, ensayé la demo completa en bases temporales con la semilla y el optimizador real, primero sobre la red urbana de las 11:20 a. m. y después sobre la red ampliada que B subió a las 2:22 p. m. Lo que aparece como **medido** sale de esos ensayos. Los puntos de rúbrica son **estimados míos**.

Faltan cuatro horas y media para la mentoría. `entrada/` entró a `main` a las 2:30 p. m., probado solo con Telegram simulado porque faltan las dos claves en `.env`. `tablero/` entró completo a las 2:32 p. m. y ya hace casi todo lo que pedía este documento para C. Mientras yo escribía, las sesiones A, B y C subieron cinco commits; repetí los ensayos sobre lo nuevo y dejé marcado lo que ya está resuelto. Desde las 2:20 p. m. los módulos A y C los construyen dos sesiones de Carlos; donde este documento dice Samuel o Jacobo para el código, léase la sesión `A-entrada` o `C-tablero`.

## Resumen

1. La demo que describe el pitch no muestra nada: cerrar la «vía a Chinchiná» no cambia ninguna ruta de la semilla. La que sí funciona es un pedido en San José y un cierre en la avenida del Centro. Está en `docs/GUION_DEMO.md`.
2. El contrato de datos alcanza para esa demo, pero tiene dos fallos que la tumban y varios huecos que hay que declarar. El más urgente: con un plan ya aprobado, pedir un plan con `despacho.optimizar` hace desaparecer las rutas anteriores, y es lo que hace hoy el botón «Calcular plan» del tablero.
3. El argumento del pitch resiste a medias. Resiste la comparación con el orden de llegada y el ahorro de kilómetros. No resiste la frase «empatamos en entregas a tiempo», porque en todos los puntos DespachoX queda por debajo en carga media y alta, ni la meta de equidad de la ficha, que la simulación contradice.
4. Las dos capacidades UNAL son hoy decorativas. Ninguna línea del código lee el indicador A25 ni la columna `empaque_activo`.

## Las diez sugerencias, por puntos ganados por hora

| # | Qué cambiar | Criterio y puntos (estimado) | Horas y quién | Qué se deja de hacer |
|---|---|---|---|---|
| 1 | Cambiar el cierre de la demo a la avenida del Centro y ensayar con `docs/GUION_DEMO.md` | 2 · protege entre 5 y 8 de 25 | 0,25 h · Fable edita `pitch/GUION.md`, Jacobo ensaya | Nada |
| 2 | Arreglar dos fallos de integración antes de unir bot y tablero | 2 · protege la demo completa | 0,5 h · B-despacho y C-tablero | Se aplaza la tarea 3 de B2 |
| 3 | Recortar bot y tablero al camino de la demo | 2 · de «incipiente» a «sólido», unos 12 de 25 | 0 h, es recorte · Samuel y Jacobo | `/estado`, duplicados, pin, indicadores, bitácora, QR, voz |
| 4 | Corregir en el pitch la frase del empate y preparar cuatro respuestas | 2 y 6 · entre 3 y 5 | 0,5 h · Fable y Carlos | Nada |
| 5 | Corregir la meta de equidad de la ficha y llenar los indicadores ya medidos | 6 · entre 2 y 3 de 10 | 0,3 h · Samuel | Nada |
| 6 | Sustentar el criterio 3 en lo que sí existe y conseguir 15 minutos de un profesor | 3 · de «parcial» a «sólido», 3,75 de 15 | 1 h · Carlos | Integrar el A25 esta noche |
| 7 | Conseguir hoy un aliado con nombre y una frase textual | 1, 4 y 5 · entre 4 y 6 | 1 h · Samuel o Carlos, en el evento | Una hora de código de quien vaya |
| 8 | Llenar `docs/FUENTES.md`, que está vacío | 1 · entre 3 y 5 de 20 | 0,5 h · Samuel con un agente | Nada |
| 9 | Trazabilidad mínima después de la mentoría | 1 y 2 · entre 2 y 3 | 1,5 h · quien se sume (Nicolás o José Manuel) | La parte 3 de S2 |
| 10 | Grabar el video de respaldo esta noche, apenas corra de punta a punta | 2 · seguro contra el cero | 0,5 h · Jacobo | Pulir el tablero antes de grabar |

### 1. La demo del pitch no cambia ninguna ruta

`pitch/GUION.md` le pide al jurado escribir «hay un derrumbe en la vía a Chinchiná». Lo ensayé: el cierre se ubica bien y el recálculo corre, pero ninguna ruta pasa por ese tramo, así que el plan nuevo es idéntico. En pantalla no pasa nada.

Probé cinco vías de `vias.csv` con el plan de la semilla (medido, búsqueda de 3 y de 8 segundos, red ampliada salvo donde se indica):

| Cierre | Qué cambia en el plan |
|---|---|
| vía a Chinchiná | Nada |
| La Siria | Nada. Ya está en la red y el bot la ubica, pero ninguna ruta de la semilla sale de la ciudad |
| Panamericana | Nada que se vea: mismas paradas en el mismo orden |
| avenida Bernardo Arango (red urbana) | El orden de paradas es el mismo. Dos vehículos tardan 25 y 20 segundos más |
| **avenida del Centro** | El camión ya no puede llegar a San José (`camion: punto:14 quedó aislado de la red`). El pedido nuevo de San José pasa del camión a un campero y los demás se reorganizan. Siguen 18 de 18 pedidos y 3 de 3 críticos a tiempo |

La avenida del Centro es la única que produce un cambio que se ve y se explica en una frase: «el camión ya no entra, el sistema manda el campero». Además muestra la flota mixta, que es la restricción de la ficha del reto.

Dos riesgos asociados. Primero, el resultado depende de la red y de la semilla: lo repetí con la red ampliada de B2 y se mantiene, pero hay que repetirlo cada vez que cambien `vias.csv`, `puntos.csv` o el grafo. Segundo, si el jurado escribe otra vía, el plan puede no cambiar. El guion de demo dice qué decir en ese caso.

### 2. Dos fallos de integración que tumban la demo (medidos)

Un tercero ya está resuelto: a las 2:13 p. m. `semilla --cargar --reiniciar` fallaba con `IntegrityError` cuando `lugares` tenía filas. B lo corrigió en `c2254a0` y lo verifiqué: el reinicio vacía `lugares` y `ubicaciones` y vuelve a llenar el nomenclátor. Eso también borra los apodos aprendidos, que es lo correcto para la demo.

- **Plan después de un plan aprobado.** Si ya hay un plan aprobado y el tablero llama `python -m despacho.optimizar`, sale un plan solo con el pedido nuevo. Al aprobarlo, el plan anterior queda `reemplazado` y sus 17 pedidos siguen `asignado` sin ruta vigente: las rutas desaparecen del mapa. Con un plan aprobado hay que llamar siempre `python -m despacho.recalcular`, que vuelve a planear todo. El tablero de las 2:32 p. m. llama `optimizar` en «Calcular plan» y solo ofrece «Recalcular» cuando hay un cierre pendiente, así que el fallo está vivo para el caso del pedido nuevo. El guion de demo lo esquiva sin tocar código: el plan inicial se deja propuesto y se aprueba después de sumar el pedido. A `recalcular` le falta `--motivo`: hoy un recálculo por pedido nuevo queda con el motivo «recálculo sin cierres confirmados».
- **Productos sin kilos.** El bot guarda los kilos solo si el mensaje los trae; es una decisión escrita en la torre de A. Con `[{"producto":"arroz"},{"producto":"leche"}]` sin kilos, `_demanda` descarta las líneas y surte un «mercado genérico» de no perecederos a 10 kg por familia. El barrio que pidió leche recibe 400 kg sin leche, y esos 400 kg dejan cortos de arroz, aceite y harina a otros tres pedidos (medido). La demo corre igual, pero el plan no entrega lo que se pidió. Hay que decidir quién aplica la tabla de raciones: el encargo A la deja en el bot mientras B responde.

### 3. Qué cortar para llegar a las 7:00 p. m. de punta a punta

El camino mínimo es: mensaje de texto, pregunta de ubicación con un botón «Sí», fila en la base, tablero con mapa y «Por revisar», recálculo y aprobación. Todo lo demás espera.

| Módulo | Queda para las 7:00 p. m. | Se corta hasta después de la mentoría |
|---|---|---|
| Bot (`A-entrada`) | Ya está el flujo completo. Faltan las dos claves, una corrida real desde un teléfono, los kilos por producto y una entrada por terminal como respaldo | Medir los quince mensajes con el modelo real puede esperar a después de la mentoría |
| Tablero (`C-tablero`) | Ya está casi todo. Faltan la regla de «Calcular plan» con plan aprobado, la búsqueda de 3 segundos y recorrer el guion completo | Formulario manual, marcar críticos y paquetes, que son funciones nuevas |
| Despacho (Carlos) | `--motivo` en `recalcular` y decidir quién pone los kilos por producto | Tareas 2 y 3 de B2 |
| Simulación | Parte 1 de S2 (factor de críticos) | Partes 2 y 3 de S2 |
| Nadie | | Voz, QR, WhatsApp, modo sin conexión |

El riesgo mayor del bot ya no es el código: son las claves. Sin `TELEGRAM_BOT_TOKEN` y `ANTHROPIC_API_KEY` nadie lo ha visto contestar. Si a las 6:00 p. m. el bot no está en Telegram, la demo de la mentoría se hace con la entrada por terminal que pide el encargo A. Si el tablero falla, se muestra el plan con `python -m despacho.optimizar` y las tablas. Los dos respaldos están en el guion de demo.

La red ampliada de B2 ya está en `main` y no rompió la demo. Desde ahora, cualquier cambio de la semilla o del grafo se fusiona solo después de repetir el ensayo de `docs/GUION_DEMO.md`.

### 4. ¿Resiste el argumento del pitch frente a la regla experta?

Resiste a medias. Esto es lo que se sostiene con `docs/SIMULACION.md` en la mano:

- Contra el orden de llegada, 12,0, 28,9 y 46,3 puntos porcentuales más de críticos a tiempo, con intervalos que no tocan el cero.
- Contra la regla experta, empate en críticos a tiempo y en perecederos, y entre 47 y 75 km menos por jornada.
- Recalcular frente a planear una vez: 6,7, 17,5 y 35,7 puntos, con la salvedad escrita de que la comparación mezcla dos efectos.

Esto es lo que no se sostiene y hay que corregir en `pitch/GUION.md`:

- La tabla de preguntas dice «contra un experto empatamos en entregas a tiempo». En entregas a tiempo de **todos** los puntos DespachoX queda 1,8 y 2,2 puntos por debajo en carga media y alta, y ese intervalo excluye el cero. El empate es solo en los dos indicadores del reto. Un jurado que abra el documento lo ve en la tabla.
- «DespachoX deja esa pericia escrita» invita a la réplica obvia: la pericia de `experta` son dos reglas y caben en un cartel. La respuesta honesta es que el optimizador, frente a esas dos reglas, aporta recorrido (del 5 % al 11 %) y factibilidad con flota mixta y cierres, y que el resto del valor está en la información: saber qué se pidió, dónde está cerrado y qué se entregó. Eso último la simulación no lo mide, y hay que decirlo así.

**Lo que preguntaría un jurado de ingeniería industrial y no sabemos responder hoy:**

| Pregunta | Estado |
|---|---|
| ¿El despacho real se parece a la política ingenua o a la experta? | No lo sabemos. Es la pregunta que responde la reconstrucción del día 30. Conviene decirlo antes de que lo pregunten |
| ¿Qué tan lejos del óptimo queda OR-Tools con 1 segundo de búsqueda? | No hay cota inferior ni corrida larga de referencia. La parte 2 de S2 lo mide de forma indirecta con 1, 3 y 8 segundos |
| ¿Por qué el inventario se asigna con una regla antes del ruteo y no dentro del modelo? | Es una simplificación declarada. No medimos cuánto se pierde |
| ¿Por qué un solo viaje por vehículo y plan? | En la simulación se compensa recalculando cuando el vehículo vuelve. En la demo no hay segundo viaje |
| Priorizar lo crítico hace esperar 2,3 y 4,3 horas más al punto peor atendido. ¿Qué hacen con eso? | No hay respuesta en el modelo. Ver sugerencia 5 |
| ¿Cuánto vale el ahorro de kilómetros en pesos o en horas de conductor? | No está calculado. No hay costo por kilómetro con fuente |
| Los niveles de carga los eligieron ustedes para que la línea base fallara. ¿Cuál es la carga real? | No lo sabemos. Está escrito en los límites del documento |
| ¿Cuánto del resultado depende del modelo de lenguaje? | Nada: la simulación supone extracción perfecta. La parte 2 de S2 lo aproxima |
| La demo tiene 18 pedidos y 5 vehículos, la simulación 111 a 166 pedidos. ¿El tablero aguanta esa escala? | No se ha probado |

La medición que puede convertir el empate en un argumento es la información imperfecta de S2, porque es lo único que distingue un sistema con confirmación de un despachador con cuaderno. Si el tiempo solo alcanza para una parte de S2 además del barrido del factor, que sea esa.

### 5. La ficha promete una meta de equidad que la simulación contradice

`docs/FICHA_4_5_6_BORRADOR.md` fija para «Equidad» la meta «menor que la línea base». La simulación midió lo contrario: el punto peor atendido espera 0,93, 2,27 y 4,25 horas **más** con DespachoX que con el orden de llegada. Hay dos salidas honestas: reportarlo como el costo medido de priorizar lo crítico, con un tope de espera como trabajo del piloto, o quitar el indicador. Recomiendo la primera, porque un jurado valora que el equipo muestre el costo.

En la misma tabla ya se pueden llenar tres celdas con datos medidos:

- Entregas a tiempo en puntos críticos: línea base 87,7 %, 69,1 % y 49,6 % con orden de llegada; DespachoX 99,7 %, 98,1 % y 95,9 % (carga holgada, media y alta).
- Desperdicio de perecederos: 0,5 %, 1,8 % y 3,5 % sin la regla de bodega y 0,0 % con ella. Conviene decir que incluso la línea base queda bajo el 5 % en estos escenarios, así que la meta del reto no discrimina.
- Tiempo de recálculo: 8,4 a 8,8 segundos con búsqueda de 8 segundos y 3,4 a 3,8 con búsqueda de 3, medido hoy con la semilla y la red ampliada, sin contar el arranque del proceso. B reporta 10,8 segundos para el comando completo con búsqueda de 8.

### 6. Las capacidades UNAL son hoy decorativas

- **Indicador A25 del IDEA.** No hay una sola línea que lo lea. No existe columna de riesgo por tramo ni fuente de datos. Integrado como penalización por tramo sí cambiaría una decisión, porque las rutas evitarían laderas en alerta. Pero hacerlo esta noche sin datos reales del IDEA sería inventar los umbrales y los tramos, que es peor que no tenerlo.
- **Patente del empaque captador de etileno.** La semilla escribe `lotes.empaque_activo` y ningún módulo lo lee. Además la ficha dice «ninguna patente entra al prototipo» mientras la torre del capitán la cuenta como segunda capacidad. Hay que elegir una versión.

Lo que sí existe y se puede señalar con el dedo: la arquitectura heredada de CARMEN (proyecto 56031), un profesor de la Sede en el equipo, la formulación del ruteo con sus supuestos escritos, la simulación con intervalos pareados y el nomenclátor con confirmación humana. Con eso y quince minutos de un profesor del Grupo de Logística o del IDEA que revise la formulación, el criterio 3 se defiende sin prometer nada falso. El A25 queda donde ya está en la ficha, en el hito de los días 60 a 75.

Esto cambia una decisión de la torre del capitán («esta noche: integrar el A25»), así que va como PREGUNTA en el canal y no lo apliqué.

### 7. Un aliado con nombre vale más que cualquier función

En la ficha, cinco de los siete aliados están «por contactar» y ninguno tiene nombre de persona. En el pitch faltan la frase de un usuario, el aliado y las dos cifras verificadas. Son tres criterios (1, 4 y 5, 50 puntos entre los tres) con el mismo hueco. Una conversación de diez minutos hoy en el evento con alguien del Banco de Alimentos, la Cruz Roja o la Defensa Civil llena los tres. Hay que salir de esa conversación con un nombre, un cargo, una frase textual autorizada y la respuesta a una pregunta: ¿hoy despachan por orden de llegada o por prioridad? Esa respuesta decide qué línea base es la justa.

### 8. `docs/FUENTES.md` está vacío

La regla del equipo exige cada cifra con su fuente. Hoy el archivo tiene solo la cabecera. Dos tandas: las cifras de la simulación, que son medidas y se copian de `docs/SIMULACION.md`, y dos o tres cifras del problema del informe 04, verificadas por una persona.

### 9. Trazabilidad: está en el entregable del reto y no tiene dueño

La ficha de la vertical pide «optimización de rutas y trazabilidad de paquetes». La tabla `paquetes` existe y nadie la escribe. Tampoco hay quién pase un pedido a `entregado`. La versión mínima es: al aprobar un plan se crea un paquete por parada con un código, el tablero lo muestra como QR con `segno` y un botón «Entregado» cierra el pedido. Es función nueva, así que debe quedar antes del sábado a las 8:30 a. m. Como cambia quién escribe qué tabla, va como PREGUNTA.

### 10. Video de respaldo esta noche

Los vencimientos y las horas límite de la semilla son relativos al momento de cargarla. Con la base recién cargada, la última parada urgente llega unas 2 horas después y el límite es de 4 horas. Una base cargada más de 90 minutos antes empieza a mostrar retrasos que no son del sistema. Por eso el video se graba con la base recién cargada, y antes de cada demo se recarga.

## ¿Alcanza el contrato de datos para integrar hoy?

Alcanza para el camino de la demo. Estos son los huecos, además de los dos fallos de la sugerencia 2.

| Hueco | Consecuencia | Qué hice o propongo |
|---|---|---|
| Un pedido `confirmado` con `punto_id` vacío no entra al plan ni aparece en `sin_atender` (medido) | El despachador cree que quedó planeado | Resuelto por C: el tablero no deja confirmar un pedido sin ubicar |
| Un cierre `confirmado` sin vía conocida ni coordenadas se ignora; solo deja un aviso en `resumen.avisos` (medido con la red urbana) | El plan pasa por la vía cerrada | Resuelto en parte por C: el tablero muestra los avisos del plan |
| `despacho/cierres.py` ubica un cierre por el texto de `cierres.lugar` aunque la ubicación de `lugares` siga en `propuesta` (medido: un cierre «la siria» sin confirmar entró al plan) | Dos localizadores con reglas distintas, y uno se salta la confirmación de la ubicación | Aviso a B. No rompe la demo |
| Nadie escribe `vehiculos.estado`, `lat` ni `lon` | Todo plan supone la flota libre y en el acopio. El recálculo «con vehículos en ruta» no se puede mostrar | Declararlo. No prometerlo en la demo |
| Nadie escribe `paquetes` ni el estado `entregado` | Sin trazabilidad | Sugerencia 9, PREGUNTA |
| Nadie puede marcar un punto como crítico. Un punto creado por `lugares` nace con `critico = 0` | El indicador del reto depende de una columna que solo llena la semilla | PREGUNTA: ¿la marca el despachador en el tablero? |
| `texto_original` guardaba lo que la persona escribió | Contradecía «no guardamos nombres ni teléfonos» | Resuelto por A en `entrada/privacidad.py`, que limpia antes de llamar al modelo y antes de guardar. Es una heurística: en la ficha conviene decir «quitamos lo que tiene forma de dato personal» |
| `cierres` no tiene `remitente_hash`, y la base no guarda a quién responder | El bot no puede avisar al remitente después de un reinicio | Se acepta para la demo |
| La regla de duplicados de `entrada/guardar.py` (cualquier pedido del mismo punto en dos horas) saca del plan pedidos legítimos, porque despacho ignora todo pedido con `duplicado_de`. La semilla tiene dos puntos con dos pedidos cada uno | Un pedido real desaparece. En los ensayos, el segundo envío del mensaje de San José no entra al plan | Encargo A: duplicado solo si coincide también el remitente. Antes de cada ensayo, reiniciar la base |
| `ROLES_VIERNES.md` dice que nadie llama funciones de otra carpeta | Ya no es cierto: bot y tablero llaman `lugares`, y el tablero debe llamar `optimizar.aprobar` | Encargos A y C actualizados |

## ¿La ficha y el pitch prometen algo que el código no hace?

| Promesa | Dónde | Realidad |
|---|---|---|
| «El mapa y el optimizador corren sin conexión» | Ficha 5, pitch | El optimizador y la red sí. El mapa de folium baja las teselas de internet. El bot necesita Telegram y el modelo |
| «El pedido se digita a mano» | Ficha 5, pitch, estrategia | El tablero no tiene formulario y C lo considera función nueva. Lo dejé en el encargo C como decisión de Carlos |
| «No guarda nombres ni teléfonos» | Ficha 5, pitch | El remitente es un hash con sal y el texto se limpia con una heurística, que no garantiza que no quede ninguno |
| Equidad «menor que la línea base» | Ficha 6 | La simulación midió lo contrario |
| Trazabilidad con QR | Ficha 6, pitch de cinco minutos, `CLAUDE.md` | No existe |
| «Empatamos en entregas a tiempo» con el experto | Pitch, preguntas | Solo en críticos. En todos los puntos, 1,8 y 2,2 puntos por debajo |
| Indicador de lluvia del IDEA | Pitch bloque 4, torre | No existe. El pitch lo marca como condicional, y así debe seguir |
| «Demo: escriba que hay un derrumbe en la vía a Chinchiná» | Pitch | Corre, pero no cambia ninguna ruta. La Siria tampoco |
| Texto «o voz» | `CLAUDE.md` | Cortado hoy. El pitch no lo promete, y está bien |

## Cambios hechos a los encargos

`encargos/A_ENTRADA_SAMUEL.md`

El módulo entró a `main` mientras yo revisaba, así que el encargo pasó de «construir» a «lo que falta».

1. Se elimina `entrada/lugares.py`: la ubicación la resuelve `lugares.resolver` con confirmación, y así lo hizo A.
2. La regla «solo escribo en `pedidos` y `cierres`» ahora admite `lugares`, `ubicaciones` y `puntos` a través del módulo `lugares`.
3. Pendiente nuevo: `entrada/procesar.py`, una entrada por línea de órdenes sobre `flujo.Mesa`. Es el respaldo de la demo.
4. Pendiente nuevo: los productos se guardan con kilos. Si el mensaje no los trae, una tabla de raciones los calcula y el bot lo dice.
5. Pendiente nuevo: duplicado solo si coinciden el punto y el remitente.
6. Primero las claves y una corrida real desde un teléfono.
7. «Hecho cuando» usa los dos mensajes de la demo.

`encargos/C_TABLERO_JACOBO.md`

El tablero entró completo a `main` mientras yo revisaba, y ya cumple la mayor parte de lo que iba a pedir: no deja confirmar pedidos sin ubicar, muestra los avisos del plan, lista «qué cambió» y aprueba con el comando de despacho. El encargo quedó en lo que falta.

1. Pendiente nuevo: «Calcular plan» debe recalcular cuando ya hay un plan aprobado.
2. Pendiente nuevo: búsqueda de 3 segundos para la demo.
3. Recorrer `docs/GUION_DEMO.md` completo y reportar diferencias.
4. El formulario manual, marcar críticos y los paquetes quedan como decisión de Carlos, porque escriben fuera de los estados.
5. Se quitan `datos_falsos.py` y los pasos ya hechos, y se añade la base compartida con `DESPACHOX_DB`.

No toqué `datos/esquema.sql`, `docs/ESTRATEGIA.md`, `pitch/GUION.md` ni la ficha. Lo que les toca está en el canal como AVISO o PREGUNTA.

## Cómo se midió

Base temporal fuera del repositorio, `despacho.semilla.cargar`, `lugares.cargar_semilla`, `optimizar.planificar`, `optimizar.aprobar` y `recalcular.recalcular`, con el Python del `.venv` y OR-Tools 9.15. Doce corridas con la red urbana a partir de las 2:13 p. m. y seis con la red ampliada después de las 2:22 p. m. El desempate de `lugares` con modelo estuvo apagado. El solver corta por tiempo, así que el orden exacto de las paradas puede variar entre máquinas. Lo que se repitió en todas las corridas está en `docs/GUION_DEMO.md` como resultado esperado.
