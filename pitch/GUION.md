# Guion del pitch · Convite (antes DespachoX)

Versión 2, noche del viernes 20 al sábado 21 de noviembre, rama `pitch-noche`. Reemplaza el borrador 1 de las 11:00 a. m. Sigue lo que pidió la mentoría 1 (`docs/MENTORIA_1.md`) y el orden del pitch de la decisión 4 (`docs/DECISIONES_9PM.md`). Las diapositivas están en `pitch/DIAPOSITIVAS.md`, y cada cifra dicha en voz alta, en `pitch/CIFRAS_PITCH.md`.

**Duración.** Ningún documento del repositorio da la duración oficial. `docs/PLATAFORMA_INNOVO.md` solo trae la franja de la preselección, el sábado de 2:30 a 3:30 p. m., y `docs/ESTRATEGIA.md` la deja «sin definir todavía». **Supuesto: tres minutos.** Si los 22 equipos pasan por una sola sala en esa hora, a cada uno le tocan menos de tres minutos con los cambios de equipo (inferencia nuestra). Por eso hay un corte de dos minutos y una versión de un minuto. Lo primero que hay que preguntar en la mesa a las 8:30 a. m. es la duración.

**Hora y entrega.** iNNOVO pone la preselección a las 2:30 p. m., mientras que el sitio anterior y `CLAUDE.md` decían 2:00 p. m. La entrega en iNNOVO es un enlace de Drive y cierra a las 2:30 p. m. (`docs/PLATAFORMA_INNOVO.md`).

**Marcas.** Un asterisco (*) marca una cifra o un hecho por verificar, y su fila está en `pitch/CIFRAS_PITCH.md`. Las cifras de simulación salen de `docs/SIMULACION.md`, sección 9, y se dicen siempre con su línea base, su número de jornadas y la palabra «simulación». [DECIDE CARLOS] marca una decisión pendiente. Si a la 1:00 p. m. nadie ha abierto la fuente de una cifra con asterisco, esa cifra sale del pitch.

## Quién hace qué

| Papel | Rol | Qué hace |
|---|---|---|
| Voz 1 | D, ficha y pitch | Bloques 1 a 4, la narración de la demo y la última frase |
| Voz 2 | B, optimización y medición. Sugerido: el integrante de Ingeniería Industrial, porque lidera la visita al Banco [DECIDE CARLOS] | Bloques 6, 7 y la regla de cambio del 8 |
| Operador | C, tablero | Todos los clics. Cambia entre las diapositivas y el tablero. No habla |
| Teléfono | A, entrada | Le entrega al jurado el teléfono y la tarjeta impresa. Si a los 15 segundos no hay mensaje, lo envía desde el teléfono del equipo. No habla |

Quien habla no toca el computador.

## Lo que pidió la mentoría y dónde se responde

| Pedido de los mentores | Bloque |
|---|---|
| Recuperación del territorio, con personas y territorio además de tecnología | 3 y 7 |
| El porqué y el para qué | 1, 2 y 3 |
| A quién impacta y a quién le sirve | 3 |
| Si hay algo parecido y por qué no se usa en Manizales ni en la región | 4 |
| El prototipo funcional que mide el efecto | 5 y 6 |
| El piloto de 30 a 90 días para la recuperación del territorio | 7 |
| Enamorarse del problema aunque la solución cambie | 8, con la regla de cambio de la decisión 1 de `docs/DECISIONES_9PM.md` |

## Preparación

La demo de este guion no depende de nada nuevo. Es la de `docs/GUION_DEMO.md`, con la semilla ensayada.

1. Entre 30 y 10 minutos antes, los pasos 1 a 7 de la sección «Preparación» de `docs/GUION_DEMO.md`. La semilla se carga menos de 30 minutos antes y nunca más de 90. Si la demo corre en la nube, hay que reiniciar la base, porque conserva lotes viejos. Se usa el botón «Reiniciar datos de prueba» del tablero, en la pestaña «Bitácora». También sirve poner `DESPACHOX_REINICIAR=1` en Railway, esperar el redespliegue y quitar la variable, porque si se queda borra la base en cada despliegue (`despliegue/arranque.sh`).
2. Antes de entrar, los pasos «0:20 a 0:55» y «0:55 a 1:30» de ese mismo guion: enviar el pedido de San José, confirmarlo, calcular el plan y aprobarlo. Así el pitch arranca con el plan aprobado. Resultado esperado: 18 de 18 pedidos, 3 de 3 críticos a tiempo y San José en camión. Si no da eso, no hay demo en vivo y se usa el video.
3. Tarjeta impresa con el QR del bot y el mensaje del cierre, tal cual: «derrumbe en la avenida del centro, no pasa camion, si pasa moto». El QR lo genera rol A con el enlace real del bot.
4. Video de respaldo abierto en otra pestaña, en pausa en el segundo cero. Lo graba Jacobo (encargo P3), y hay que confirmar que existe.
5. Internet por datos móviles, no por el wifi del campus.
6. Diapositivas y tablero en dos ventanas. El operador cambia de una a otra con un atajo de teclado.

## Versión de tres minutos

Los tiempos suponen 2,5 palabras por segundo y suman 3:00 con la demo. El ensayo cronometrado manda. Si pasa de 3:00, se corta en el orden de la sección «Qué cortar».

### Bloque 1 · Por qué · 0:00 a 0:19 · criterio 1

**Habla:** Voz 1. **Pantalla:** diapositiva 1, las barras de los bancos de alimentos seis días después del sismo.

> Después del sismo, Manizales fue uno de los principales puntos de acopio de la red de bancos de alimentos*. La comida llegó. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y 157 en camino. Habían entregado 41*.

Las toneladas se dicen truncadas, y en pantalla van los kilos exactos, 404.587, 157.164 y 41.163. La nota de Portafolio atribuye las cifras a «los Bancos de Alimentos» y no dice «en todo el país» de forma explícita (discrepancia D3 de `docs/FUENTES.md` en la rama `fuentes-noche`). Por eso esas cifras no se le atribuyen a Manizales, y tampoco se dice «en todo el país». La misma nota da los 157.164 kg en tránsito, así que la frase los nombra y la comparación no los deja por fuera. «Seis días después» es cálculo nuestro con la fecha de la nota, el 16 de agosto, porque la nota no da fecha de corte. Lo que va en camino suma unos 3 segundos al bloque, y el ensayo cronometrado dice si hay que recortar con la sección «Qué cortar».

### Bloque 2 · Las vías se cierran sin sismo · 0:19 a 0:33 · criterio 1

**Habla:** Voz 1. **Pantalla:** diapositiva 2, el mapa de Manizales con la salida a Letras marcada.

> En Manizales las vías se cierran también sin sismo. La salida a Letras suma 87 registros de cierre por derrumbe o deslizamiento desde 2017*, y solo 4 son del sismo*.

Se dice «registros», porque un mismo derrumbe puede tener varios. Los 4 del sismo son las filas S04, S09, S10 y S11 de `datos_publicos/cierres_historicos.csv`; los otros 83 son de 2017 a enero de 2026.

### Bloque 3 · Para qué y para quién · 0:33 a 0:51 · criterios 1 y 6

**Habla:** Voz 1. **Pantalla:** diapositiva 3, quién despacha, quién pide, quién reporta las vías y quién avala.

> Convite existe para que la comida llegue a quien no puede ir a buscarla, aunque la vía esté cerrada. Es para quien despacha en el Banco Arquidiocesano de Alimentos y para quienes le piden: comedores, hogares infantiles y juntas de barrio y de vereda.

### Bloque 4 · Lo que existe y por qué no basta · 0:51 a 1:06 · criterio 1

**Habla:** Voz 1. **Pantalla:** diapositiva 4, las piezas sueltas y la que falta.

> ¿Hay algo parecido? Hay piezas sueltas, pensadas para la emergencia, y ninguna une el pedido, el vehículo, la vía y la entrega. Por ejemplo, el registro de damnificados cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas*.

Al terminar la frase, el operador pasa al tablero.

### Bloque 5 · Demo en vivo · 1:06 a 2:09 · criterio 2

**Habla:** Voz 1. **Opera:** rol C. **Teléfono:** rol A. **Pantalla:** el tablero a pantalla completa, con el plan aprobado, las rutas de colores y los tres puntos críticos resaltados.

| Tiempo | Qué pasa y qué se ve | Qué dice Voz 1 |
|---|---|---|
| 1:06 a 1:16 | Tablero con el plan aprobado | «Esta es la mesa de despacho. El plan aprobado ya incluye un pedido de prueba que llegó por chat desde San José. Ahora necesito a alguien del jurado.» |
| 1:16 a 1:33 | Rol A le entrega al jurado el teléfono con el chat abierto y la tarjeta. El jurado escribe el mensaje de la tarjeta. El bot responde «Ubiqué «avenida del centro» en: avenida del Centro (via). ¿Es correcto?», y el jurado toca **Sí, es ahí**. Si el mensaje lo lee el lector por reglas, la pregunta trae el artículo, «la avenida del centro», y es igual de correcta | Mientras escribe: «El 21 de octubre, un deslizamiento dejó la vía a Pereira a un carril, y solo pasaban livianos*. Quien lo sabe primero es el conductor.» |
| 1:33 a 1:41 | En el mapa aparece el cierre como reportado | «El sistema no cierra la vía por un mensaje. La deja reportada hasta que el despachador la confirme.» |
| 1:41 a 1:51 | El operador hace clic en **Confirmar** en el cierre. Aparece «Hay un cierre nuevo: recalcular». Clic en **Recalcular**. El plan nuevo sale en menos de diez segundos | «El despachador confirma y pide recalcular.» |
| 1:51 a 2:03 | Plan nuevo. En los avisos se lee `camion: punto:14 quedó aislado de la red`, y el pedido de San José pasa de un camión a un campero. También sale `camion: punto:3 quedó aislado de la red`, del comedor de Belén, y no se comenta | «Con la avenida cerrada, el camión ya no llega a San José. El sistema le pasa el pedido a un campero, que sí entra. Los tres puntos críticos siguen a tiempo*.» |
| 2:03 a 2:09 | Clic en **Aprobar**. Si hay bitácora, se muestra quién aprobó y a qué hora. El operador vuelve a las diapositivas | «El modelo leyó. El optimizador calculó. Decidió una persona, y quedó escrito quién y cuándo.» |

**Si algo falla.** No se depura en vivo. La tabla completa está en `docs/GUION_DEMO.md`, sección «Qué hacer si falla cada paso». Estos son los cuatro casos más probables.

- El jurado tarda o no quiere. A los 15 segundos, rol A envía el mensaje desde el teléfono del equipo.
- El jurado escribe otra vía, por ejemplo La Siria. Voz 1 dice «esa vía no la usa ninguna ruta de hoy, así que el plan sigue igual», y rol A envía el mensaje de la avenida del Centro.
- El plan nuevo no muestra el campero. Se lee lo que sí está en pantalla, pedidos atendidos y críticos a tiempo, y no se afirma lo del campero.
- Cualquier otra falla, o se cae internet. Voz 1 dice «tenemos el mismo recorrido grabado» y el operador pasa al video.

### Bloque 6 · Qué medimos y cómo · 2:09 a 2:30 · criterios 2 y 6

**Habla:** Voz 2. **Pantalla:** diapositiva 6, la tabla por comuna y vereda y la barra de la simulación.

> Cada paquete lleva un QR. La entrega queda registrada cuando ese código llega por chat o SMS. Con esos registros, el prototipo arma una tabla por comuna y vereda, y esa tabla mide el piloto. En simulación comparamos 30 jornadas por política, con carga media. Frente al despacho por orden de llegada, Convite sube los críticos a tiempo de 53,6 % a 98,3 %. Son 44,7 puntos. El intervalo del 95 % va de 37,7 a 51,6.

Las cifras son de `despacho/sim/resultados_velocidades/tablas.md`, críticos a tiempo, carga media. La comparación con un despachador con oficio va siempre en la diapositiva. Decirla en voz alta depende de la pregunta 2 de `docs/FICHA_MENTORIA.md`, que se les hace a los mentores en la mentoría 2 [DECIDE CARLOS]. Si se dice, la frase es «En simulación, frente a un despachador con oficio que ya atiende primero lo urgente, Convite recorre 56,0 km menos por jornada con carga media. Comparamos 30 jornadas por política. En el total de entregas a tiempo empatan, con −0,8 puntos y un intervalo de −3,1 a 1,4.» Frente al despachador con oficio solo se dicen en voz los kilómetros y el total de entregas a tiempo. La ventaja en críticos a tiempo no se dice en voz. Va en la diapositiva de respaldo C y en las respuestas, solo con carga alta y con la frase de `pitch/CIFRAS_PITCH.md`, fila C16 (`docs/SIMULACION.md`, sección 9.3).

### Bloque 7 · El piloto de 30 a 90 días · 2:30 a 2:52 · criterios 3, 4 y 5

**Habla:** Voz 2. **Pantalla:** diapositiva 7, la línea de tiempo del piloto y el mapa del territorio.

> El piloto es para la recuperación del territorio. Dura 90 días en la rutina del Banco, con la Unidad de Gestión del Riesgo. Empieza en Ciudadela del Norte y El Manantial, y cada 30 días suma una zona. Así la capacidad queda en Manizales y se usa entre desastres. La alerta de lluvia A25 del IDEA de la UNAL ya está en el código, por ahora con lluvia de prueba.

- **Territorio.** Ciudadela del Norte y El Manantial es la propuesta 2 de `docs/PILOTO_TERRITORIOS.md`, y Carlos la eligió el 21 de noviembre a las 6:10 a. m. Es la comuna más poblada, con 58.776 habitantes (ASIS 2023). Además, el PMA recorrió con la Alcaldía las veredas con más daño para identificar necesidades de seguridad alimentaria, y en esa nota hablan las juntas de Alto del Guamo y Alto Bonito (Alcaldía, 20 de agosto). A las 8:05 a. m. Carlos decidió que el piloto crece por zonas. El día 30 se suma La Macarena y El Tablazo, y el día 60, Atardeceres y Kilómetro 41, cada una solo si la anterior cumplió su criterio de validación y el Banco lo confirma (`docs/PLAN_30_90.md`, sección 4). En voz no se nombran las otras dos zonas. Con la frase del crecimiento, el bloque gana 8 palabras, y el ensayo cronometrado dice si cabe en sus 22 segundos.
- **A25.** Está en `main`, en `despacho/a25.py`, con lluvia sintética y apagado por defecto. Encendido, el optimizador encarece, sin cerrarlas, las vías con historial de deslizamientos que están en alerta naranja o roja (`docs/A25.md`, sección 2). Con la lluvia real del IDEA entra en los días 60 a 90 (`docs/FICHA_CORTA.md`, componente 3).
- **Visita al Banco.** Si hubo conversación el sábado y la persona dio permiso, esta frase reemplaza a «Así la capacidad queda...»: «Esta mañana se lo mostramos a [cargo] del Banco, que nos dijo: «[frase textual]».» Sin permiso o sin conversación, no se menciona.

### Bloque 8 · Regla de cambio y cierre · 2:52 a 3:00 · criterios 4 y 5

**Habla:** Voz 2 y luego Voz 1. **Pantalla:** la diapositiva 7 sigue mientras Voz 2 dice la regla de cambio, que está debajo de la línea de tiempo, y la 8 sale con la última frase.

> **Voz 2:** Si el Banco no reparte, el piloto pasa al flujo de requerimientos de la UGR y la Gobernación.
>
> **Voz 1:** Somos Convite. En el Eje Cafetero, el convite era la forma en que los vecinos se juntaban para abrir un camino.

Carlos confirmó el nombre «Convite», que Jacobo y Samuel propusieron en el canal a las 11:30 p. m. La explicación del nombre es la que dieron Jacobo y Samuel en el canal. Para que quepa, se corta la frase del 21 de octubre de la demo.

## Qué cortar

Se corta en este orden hasta que el ensayo dé 3:00, o el tiempo que fije la organización.

1. En la demo, la frase del 21 de octubre. Solo ahorra tiempo si el jurado escribe rápido o si rol A envía el mensaje.
2. En el bloque 7, la frase «Así la capacidad queda en Manizales y se usa entre desastres», unos 5 segundos. Se corta solo si no hubo visita al Banco, porque es la que explica la recuperación del territorio.
3. En el bloque 4, la frase del registro de damnificados, unos 7 segundos.
4. En el bloque 3, la lista de quienes piden. Queda «Es para quien despacha en el Banco Arquidiocesano de Alimentos y para quienes le piden».

### Corte de dos minutos

| Bloque | Qué queda | Tiempo |
|---|---|---|
| 1 y 2 | Sin cambios | 33 s |
| 3 | Solo la primera frase | 8 s |
| 4 | «Hay piezas sueltas, pensadas para la emergencia, y ninguna une el pedido, el vehículo, la vía y la entrega.» | 8 s |
| 5 | La demo sin la frase del 21 de octubre ni la de «El sistema no cierra la vía por un mensaje». Rol A envía el mensaje si el jurado tarda más de 10 segundos | 45 s |
| 6 | «Cada entrega confirmada entra a una tabla por comuna y vereda, y esa tabla mide el piloto.» La simulación queda en pantalla | 7 s |
| 7 | Primera, segunda, tercera y quinta frase. La tercera, la del crecimiento por zonas, todavía no está cronometrada | 18 s |
| 8 | No va | 0 s |

Suma 1:59 sin la frase del crecimiento por zonas, que el ensayo cronometrado debe medir.

## Si dan cinco minutos

Se añaden estos textos, en este orden. Sus cifras están en `pitch/CIFRAS_PITCH.md`, sección «Añadidos de cinco minutos».

1. **En el bloque 2, antes de la salida a Letras (6 s).** «Manizales está sobre una cuchilla y casi todas sus vías de acceso van por ladera.»
2. **Después del bloque 2 (10 s).** «El día del sismo, la Policía anunció al mediodía el cierre de Pereira–Chinchiná*. El registro oficial apareció 9 horas y 46 minutos después del sismo*.»
3. **Después del bloque 4 (12 s).** «En Manizales, la comida del sismo se repartió por listas. Para recibir un mercado había que llevar el formato azul de Bomberos*, y los kits se entregaron por turnos en la sede de la Cruz Roja Seccional Caldas*.»
4. **Después del añadido 3 (14 s).** «Según un estudio de la Javeriana de Cali, después del sismo de 1999 las gerencias del FOREC actuaron con autonomía frente a las autoridades locales. Eso debilitó la gobernanza del territorio*. Por eso el piloto queda en manos de Manizales.»
5. **En la demo (60 s más).** La demo completa de tres minutos de `docs/GUION_DEMO.md`, con el pedido de San José enviado en vivo.
6. **En el bloque 6 (15 s).** «En simulación, con carga media y 30 jornadas por política, Convite recorre 56,0 km menos por jornada que un despachador con oficio. En el total de entregas a tiempo empatan. Con los dos, los perecederos vencidos quedan en 0,0 %. Por orden de llegada se vence el 3,4 %. Priorizar tiene un costo, porque el punto peor atendido espera 3,07 horas más que por orden de llegada.» Son unas 62 palabras, más que los 15 s, y el ensayo cronometrado dice si se recorta.
7. **En el bloque 7 (20 s).** «Del día 0 al 15, acuerdo y línea base. Del 15 al 30, reconstruimos un mes de despachos del Banco. Del 30 al 60, el Banco reparte como siempre y Convite planea en sombra. Del 60 al 90, simulacro con la UGR y decisión escrita del Banco. El piloto cabe en la calamidad pública de Manizales, vigente hasta el 9 de agosto de 2027*.»
8. **Antes del bloque 8 (15 s).** «Al Banco le pedimos tres datos sin información personal: sus puntos de entrega, su inventario con vencimientos y un mes de despachos. Sin internet, el plan sale en un portátil y la ruta se imprime con un QR por paquete*. No guardamos el teléfono de quien escribe. Queda como un código.»

Las fases del añadido 7 salen de `docs/FICHA_CORTA.md`, componente 4, y coinciden con los hitos de los días 0, 15, 30, 60 y 90 de `docs/PLAN_30_90.md` (rama `defensa-noche`).

## Versión de un minuto

Sirve para un turno de un minuto, una presentación rápida en Conecta+ o un pasillo con un aliado. No lleva demo en vivo. **Habla:** Voz 1. **Pantalla:** diapositiva 1 hasta 0:20, el tablero con el plan recalculado hasta 0:56 y la diapositiva 8 al final. Sin proyector, se dice igual.

| Tiempo | Qué se dice |
|---|---|
| 0:00 a 0:16 | «Después del sismo, la comida llegó a la región. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y 157 en camino. Habían entregado 41*.» |
| 0:16 a 0:20 | «Y en Manizales las vías se cierran también sin sismo.» |
| 0:20 a 0:41 | «Convite es una mesa de despacho para el Banco Arquidiocesano de Alimentos. Comedores, hogares y juntas piden por chat o SMS, y los conductores reportan los derrumbes. El optimizador reparte entre camión, campero y moto. Saca primero lo que vence primero y recalcula si se cierra una vía. El despachador aprueba cada plan.» |
| 0:41 a 0:58 | «El piloto de 90 días entra a la rutina del Banco en Ciudadela del Norte y El Manantial, con la Unidad de Gestión del Riesgo y el A25 del IDEA de la UNAL. Cada 30 días suma una zona, y todo se mide contra la línea base del propio Banco.» |
| 0:58 a 1:00 | «Somos Convite.» |

## Decisiones para Carlos

1. **Duración.** Se asumió tres minutos. Hay que preguntar en la mesa a las 8:30 a. m.
2. **Voces.** Quién es Voz 1 y quién es Voz 2.
3. **Territorio.** Decidido el 21 de noviembre a las 6:10 a. m. El piloto empieza en Ciudadela del Norte y El Manantial, la propuesta 2 de `docs/PILOTO_TERRITORIOS.md`. A las 8:05 a. m. Carlos decidió que el día 30 se suma la propuesta 1 y el día 60 la 3.
4. **Despachador con oficio.** Si los kilómetros y el empate en el total se dicen en voz alta en el bloque 6 o quedan solo en pantalla. Depende de la mentoría 2. La ventaja en críticos no se dice en voz. Carlos decidió a las 8:21 a. m. que va en la diapositiva de respaldo y en las respuestas, solo con carga alta (corrida 9.3).
5. **A25.** Decidido. Está en `main`, y el bloque 7 dice que ya está en el código, por ahora con lluvia de prueba.
6. **Nombre.** Decidido. El producto se llama Convite, y el bloque 8 cierra con el nombre y su explicación.
7. **Frase del Banco.** Si hubo visita y permiso, entra en el bloque 7.

## Lo que falta para que este guion sea verdad

1. Abrir la fuente de cada cifra con asterisco. La lista por orden de prioridad está al final de `pitch/CIFRAS_PITCH.md`.
2. Hecho. La corrida 9.3 de `docs/SIMULACION.md` terminó a las 7:23 a. m. y separa el efecto de la red del de la velocidad. Por eso la ventaja en críticos frente al despachador con oficio se dice fuera de la voz y solo con carga alta.
3. La tabla por territorio en pantalla. Puede ser la pestaña «Territorio» del tablero o, si no llega antes de las 8:30 a. m., la figura hecha con `python -m despacho.territorio`.
4. El video de respaldo.
5. Dos ensayos cronometrados con la demo real, el segundo con datos móviles.
6. Una persona que repita el ensayo de la demo en la mañana. El último lo hizo el agente B-noche a las 11:15 p. m. y dio 18 de 18 pedidos, 3 de 3 críticos y el campero a San José (`torre/TORRE_CAPITAN.md`).

El plan detallado de 30 a 90 días, la matriz de riesgos y el banco de preguntas del jurado están en la rama `defensa-noche` (`docs/PLAN_30_90.md`, `docs/RIESGOS.md` y `pitch/PREGUNTAS_JURADO.md`). Fable los integra.
