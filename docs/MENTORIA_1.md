# Mentoría 1 · viernes 20 de noviembre de 2026

Lo anotó Fable, el coordinador, a partir de lo que contó Carlos al salir de la mentoría (5:02 y 5:04 p. m.). Los mentores son de Bogotá y no conocen la región, así que el contexto regional lo tenemos que poner nosotros.

## Lo que dijeron

- La palabra clave es **recuperación del territorio**. La solución no puede ser solo tecnología: también son personas y territorio. La idea es que nos recuperemos como territorio.
- Hay que vender el piloto de 30 a 90 días como un piloto para la recuperación del territorio.
- Enfocarse en el porqué y en para qué sirve.
- Decir a qué personas impacta y a quién le sirve.
- ¿Hay algo parecido? Si lo hay, ¿por qué no se usa en Manizales o en la región? ¿Por qué fallan las otras soluciones en la ciudad y en la región?
- ¿Cuál es el prototipo funcional que va a poder medir el efecto de la solución para la región?
- No importa que la solución cambie. Hay que enamorarse del problema para que la solución le sirva a todos y a la región.

## Lo que pide la hackathon para el piloto

La página oficial describe el entregable como «Prueba real en territorio» y anuncia pilotos de campo «con entidades aliadas y comunidades del Eje Cafetero». La pregunta central del evento es cómo acelerar la recuperación de Manizales y del Eje Cafetero después del sismo. El piloto, entonces, ocurre en la fase de recuperación.

## Lo que se decidió (Carlos, 5:10 p. m.)

1. Dos agentes de investigación más, con entrega hacia las 8:00 p. m. Uno trabaja alternativas, por qué no se usan aquí, quién usaría la solución y el marco oficial de la recuperación (`docs/investigacion/10_problema_usuarios_alternativas.md`). El otro reúne lo que dijeron en público los actores de Manizales en redes, prensa e informes de gestión (`docs/investigacion/11_voz_publica_actores.md`).
2. Un informe de contexto regional en LaTeX que crece durante la noche: `docs/informe/`. La versión 0.1 llega hacia las 6:30 p. m.
3. Una vista por territorio en el prototipo, antes del congelamiento del sábado a las 8:30 a. m.: `encargos/T1_TERRITORIO.md`.

## Lo que decidió Carlos a las 5:19 p. m.

1. `FACTOR_CRITICO` pasa de 1 a 3, como propuso la simulación.
2. Principio de diseño: DespachoX tiene que servir un día normal. Muchas herramientas de emergencia funcionan bien cuando llega la tragedia, pero nadie sabe usarlas, porque solo se diseñaron para la tragedia. Los derrumbes y cierres viales, que en Manizales pasan sin terremoto, pueden ser el uso cotidiano; se estudia.
3. Samuel y Jacobo piensan qué cambiar en la solución, hablando con personas reales: `encargos/P1_PROBLEMA_SAMUEL_JACOBO.md`, con entrega a las 9:00 p. m.

## La idea, en una página (17:57)

Es una propuesta de Fable para discutir a las 9:00 p. m. con lo que traigan Samuel y Jacobo de sus conversaciones. El contexto completo está en `docs/informe/informe_contexto.pdf`, y la evidencia en `docs/investigacion/08` y `10`.

**Lo que encontramos.**

- La comida llegó, pero no salió. Según Portafolio (16 de agosto), al sexto día la red de bancos de alimentos tenía 404.587 kg en acopio y había entregado 41.163 kg. Falta que una persona lo verifique.
- Lo que ya existe no despacha. La Cruz Roja registra hogares con KoboCollect y AccessRC; SUMA, de la OPS, lleva inventario y entregas; el RUD lista damnificados; ABACO recauda y le rinde cuentas al donante. Ninguna pieza une el pedido, el vehículo, la vía y la entrega.
- En el casco urbano, la agenda pública de hoy es vivienda, y en ciudades con comercio abierto el PMA y la Cruz Roja prefieren dar efectivo. La comida en especie sigue importando donde el efectivo no sirve: albergues, comedores, hogares infantiles y veredas que quedan aisladas cuando se cae una vía.
- El Banco de Alimentos de Manizales fue nodo regional hacia municipios y veredas de Caldas. Los bancos de alimentos trabajan todos los días con organizaciones inscritas que les hacen pedidos: el de Bogotá atendió así a 993 organizaciones en 2022 ([El Tiempo](https://www.eltiempo.com/bogota/banco-de-alimentos-de-bogota-director-hace-balance-de-los-22-anos-de-la-fundacion-769904)).
- Las vías de Manizales se cierran por derrumbes sin necesidad de un sismo, y la ciudad ya tiene una alerta por lluvia: el indicador A25 del IDEA de la UNAL.

**La idea.** Que DespachoX sea la mesa de despacho de todos los días del Banco de Alimentos, hacia comedores, hogares, albergues y veredas. En temporada de lluvias, la misma mesa recibe las alertas y los cierres y reorganiza las rutas. Así, cuando llegue la próxima emergencia, el Banco, las juntas y los conductores ya la conocen. Las juntas piden y confirman cada entrega con QR, y lo entregado se exporta a SUMA, para sumarse a lo que ya existe en vez de competir con ello.

**El piloto de 30 a 90 días.** Sobre la rutina real del Banco, en un territorio con nombre, medido de las cuatro formas de la sección siguiente.

**Lo que tienen que averiguar Samuel y Jacobo.** Si el Banco reparte o las organizaciones recogen; si sigue despachando ayuda del sismo; qué sistema usa; y si aceptaría 30 días de prueba en paralelo.

## En discusión: el piloto

Carlos preguntó cómo funciona el piloto, y cómo se mide su efecto, si la calamidad fue en agosto. La propuesta del coordinador es llevar DespachoX a la operación diaria de un aliado, por ejemplo el Banco de Alimentos, en un territorio con nombre. El efecto se mediría con cuatro instrumentos:

1. La operación diaria contra su propia línea base: dos semanas registrando cómo se despacha hoy, después el sistema en sombra y luego asistiendo.
2. Un simulacro con la Unidad de Gestión del Riesgo, con un cierre planeado y vehículos reales.
3. Los cierres reales de la temporada de lluvias, si ocurren dentro de los 90 días.
4. La reconstrucción de los despachos de agosto, si el aliado entrega los registros, más la simulación calibrada con datos públicos.

Falta un dato que cambia el diseño: si el Banco de Alimentos reparte en vehículos en un día normal o si las organizaciones recogen en su bodega.

## Lo que hay que poder responder el sábado

| Pregunta | Dónde se trabaja |
|---|---|
| ¿Por qué hacemos esto y para qué sirve? | Ficha, componente 1; informe de contexto, secciones 2 y 3 |
| ¿A quién le sirve y a quién impacta? | Ficha, componentes 1 y 6; investigaciones 10 y 11 |
| ¿Hay algo parecido y por qué no se usa aquí? | `docs/ESTADO_DEL_ARTE.md`; investigación 10 |
| ¿Qué prototipo mide el efecto en la región? | Tablero, encargo T1 y `docs/SIMULACION.md` |
| ¿Cómo es el piloto para la recuperación del territorio? | Ficha, componente 4 |

## Guion de cinco minutos para hablar con un usuario real

1. En agosto, ¿cómo decidían qué ayuda salía, a qué barrio o vereda y en qué vehículo? ¿Quién decidía y con qué: cuaderno, Excel, WhatsApp o algún programa?
2. ¿Cómo les llegaban los pedidos? ¿Qué se perdía: pedidos repetidos, barrios o veredas que nunca pidieron?
3. ¿Cómo se enteraban de una vía cerrada, y cuánto tardaban?
4. ¿Se dañó o se venció comida? ¿Más o menos cuánta, y por qué?
5. ¿Usaron alguna plataforma (de ABACO, la Alcaldía, la UNGRD u otra)? ¿Por qué sí o por qué no?
6. Si mañana hay otro derrumbe grande, ¿qué les haría más falta?
7. ¿Quién de su equipo usaría algo así, y en qué momento del día?
8. ¿Podemos citarlo mañana con nombre y cargo? ¿Nos recibirían para un piloto de 30 a 90 días?

Anoten nombre, cargo, entidad y hora. Con un líder de junta de acción comunal, cambien la 1 y la 7: cómo pidieron, si les llegó la ayuda y cómo se enteraron. Al Banco de Alimentos háganle una pregunta más: en un día normal, ¿reparten ustedes o las organizaciones recogen en la bodega?
