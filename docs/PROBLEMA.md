# El problema que DespachoX quiere resolver

Lectura obligatoria para todo el equipo antes de cualquier otra tarea. Toma unos diez minutos. Al final hay cinco preguntas: si puedes responderlas sin volver al texto, ya entiendes el proyecto.

**Sobre las cifras.** Las reunieron agentes de investigación a partir de prensa y documentos oficiales, y nadie del equipo ha abierto todavía los enlaces. Sirven para entender el problema. Ninguna va al pitch hasta que una persona la verifique y la anote en `docs/FUENTES.md`. Las fuentes de cada una están en `docs/investigacion/04_evidencia_del_problema.md` y `02_referentes_latinoamerica.md`.

## 1. Qué pasó

El 10 de agosto de 2026, a las 7:34 de la mañana, un sismo de magnitud 7,4 con epicentro en el Chocó sacudió el occidente de Colombia. El Gobierno declaró la emergencia en quince departamentos, Caldas entre ellos. Nueve días después, la Unidad Nacional para la Gestión del Riesgo contaba más de 262.000 damnificados, 314 personas fallecidas y 449 vías afectadas en el país. En Manizales, un censo del 24 de agosto registró 8.240 damnificados y 3.080 predios evacuados, y el Coliseo Mayor seguía funcionando como albergue.

La comida sí llegó. La red de bancos de alimentos del país montó un corredor humanitario y usó a Manizales como su principal punto de acopio para el Eje Cafetero. En la primera semana movió más de 2.000 toneladas para más de 9.000 familias. En Bogotá, un solo centro de acopio reunió 933 toneladas en seis días.

El problema apareció después de la donación. El mismo centro de Bogotá, con las bodegas llenas, tuvo que pedir camiones, montacargas y voluntarios para poder despachar. El gerente de la red de bancos de alimentos dijo que su mayor reto era el transporte y la llegada a las zonas rurales. Los cortes de energía dañaron la cadena de frío, y por eso se dio prioridad a los enlatados sobre los alimentos frescos. Dos días después del sismo, dos de las salidas de Manizales seguían cerradas: la vía hacia Chinchiná y la que sube a Letras.

## 2. El problema que nos asignaron

La hackathon nos puso en la vertical 04, Logística y abastecimiento. Su ficha describe el problema así: los derrumbes en las vías de acceso a Manizales generan embotellamientos y desabastecimiento de alimentos de primera necesidad. Los usuarios que nombra son la Cruz Roja, la Defensa Civil, el Banco de Alimentos, los transportadores y los comités barriales. Pide una plataforma o un protocolo de despacho en tiempo real, con optimización de rutas y trazabilidad de los paquetes de ayuda. Mide el resultado con dos indicadores: el porcentaje de entregas a tiempo en puntos críticos y el desperdicio de alimentos perecederos, que debe quedar por debajo del 5 %.

La ficha dice que el desabastecimiento llega «en cuestión de 48 horas». No encontramos una fuente que respalde esa cifra para este sismo, así que no la repetimos como un hecho. Lo que sí está documentado es lo que cuenta la sección anterior, y es suficiente.

## 3. El problema, dicho con precisión

No faltó comida y no faltó voluntad. Faltó una forma de decidir. Cada mañana, alguien en un centro de acopio tiene que responder la misma pregunta: con lo que hay en bodega y los vehículos que tengo, ¿qué le mando a quién, en qué orden y por dónde? Esa pregunta es difícil por tres razones que se juntan.

**La demanda llega desordenada.** Un líder de barrio escribe por WhatsApp que son cuarenta familias sin arroz. Otro vecino del mismo barrio escribe lo mismo una hora después. Un tercero llama. Nadie sabe si son tres necesidades o una sola contada tres veces. Los lugares se nombran como los nombra la gente, «por la Siria», «abajo de la Terminal», y hay que saber dónde queda eso. Mientras tanto, lo que no se pidió por el canal correcto no existe para quien despacha.

**El mapa cambia durante el día.** Manizales está construida sobre una cuchilla. Tiene pocas vías de acceso, casi todas por ladera, y los derrumbes las cierran con frecuencia aun sin terremoto: hubo cierres por deslizamientos en 2017, 2021 y 2023. Después de un sismo, una vía que estaba abierta a las ocho puede estar cerrada a las diez. Quien lo sabe primero es el conductor que se la encuentra, y hoy esa información viaja por teléfono, tarde y sin registro. Además no todos los vehículos pasan por los mismos sitios: donde no entra un camión puede entrar un campero o una moto.

**La comida se vence.** Una parte de lo donado es perecedera. Si la leche o la verdura se quedan en bodega mientras salen primero los enlatados, se pierden. Y si salen hacia un punto al que el camión no puede llegar, se pierden en el camino.

Cada una de estas dificultades tiene solución conocida por separado. Juntas, y bajo presión, superan lo que una persona puede sostener en la cabeza con un cuaderno y un teléfono. El resultado no es que nadie reciba nada. Es que los puntos más urgentes, como un albergue o un comedor comunitario, reciben tarde, que algunos barrios reciben dos veces y otros ninguna, y que una parte de la comida se daña.

## 4. Quién lo vive

- **La persona que despacha.** Es nuestro usuario principal. Puede ser una funcionaria del Banco de Alimentos con años de experiencia o un voluntario que llegó ayer. Decide con información incompleta y responde por lo que salga mal.
- **El líder de barrio.** Pide en nombre de sus vecinos. Necesita saber que lo oyeron y que su pedido quedó bien entendido.
- **El conductor.** Conoce el estado real de las vías mejor que cualquier mapa. Hoy nadie le pregunta de forma ordenada.
- **Las familias.** No van a usar nada de lo que construyamos. Solo van a notar si la comida llegó, si llegó a tiempo y si llegó buena.
- **Quien donó.** Quiere saber si lo que dio llegó a alguien. En Colombia hay antecedentes de ayudas que se perdieron o se desviaron, y por eso la trazabilidad no es un lujo.

## 5. Qué existe y qué falta

Existen herramientas que calculan rutas, incluso con vías bloqueadas. Existen sistemas que registran entregas, como los que usan el Programa Mundial de Alimentos o la Cruz Roja. Existen plataformas que recogen reportes ciudadanos. Tras este sismo aparecieron además sitios para informar y para recaudar donaciones. Lo que no encontramos es una herramienta abierta que una todo el recorrido: del mensaje de un vecino a la ruta de un vehículo, con el cierre vial que reportó un conductor y con el vencimiento de lo que va en la carga. Tampoco encontramos, entre las plataformas de 2026, alguna que despache.

Ese es el hueco. Por eso nuestro aporte está en la integración y no en un algoritmo nuevo.

## 6. Qué significa resolverlo

Resolver este problema no es entregar más comida, porque no producimos comida. Es que, con la misma comida y los mismos vehículos, más pedidos urgentes lleguen a tiempo y menos alimentos se dañen. Los dos indicadores de la ficha miden exactamente eso.

Hay algo que aprendimos al simularlo y que conviene tener claro. Un despachador con experiencia, que atiende primero lo urgente y saca primero lo que vence, ya consigue casi el mismo resultado que nuestro sistema en esos dos indicadores. El desperdicio, en particular, se resuelve con una regla de bodega y no con rutas. Eso no invalida el proyecto. Lo precisa: el valor está en que esa pericia quede disponible para cualquier voluntario, a cualquier hora, y en que se combine con información que hoy llega tarde o no llega, como los pedidos del chat, los cierres de vía y la confirmación de cada entrega.

También hay límites que debemos decir en voz alta. No decidimos por nadie: el sistema propone y una persona aprueba. No sabemos todavía cómo despacha de verdad el Banco de Alimentos de Manizales, porque no hemos hablado con ellos. Y priorizar los puntos críticos tiene un costo medido: el punto peor atendido espera más.

## 7. Lo que todavía no sabemos

- Cuánto duraron los cierres de las vías de Manizales y cuáles fueron, más allá de los dos primeros días.
- Si hubo alimentos donados que se vencieron en Manizales, y cuántos.
- Cuántas familias recibieron ayuda alimentaria en la ciudad y desde qué centros.
- Cómo decide hoy, paso a paso, quien despacha en el Banco de Alimentos.

Cualquiera de estas respuestas, dicha por una persona que estuvo ahí y citada con nombre y cargo, vale más que todas las cifras de prensa de este documento. Conseguirla es tarea de todos.

## 8. Cinco preguntas para saber si lo entendiste

1. Si la comida llegó, ¿cuál es el problema?
2. ¿Por qué es más difícil despachar en Manizales que en una ciudad plana?
3. ¿Qué tres cosas tiene que saber quien despacha, y de dónde le llega hoy cada una?
4. ¿Qué miden los dos indicadores del reto, y cuál de los dos casi no depende de las rutas?
5. Si un jurado dice «un buen despachador ya hace esto», ¿qué le respondes?
