# P1 · Enamorarse del problema (Samuel y Jacobo)

Encargo para personas, no para Claude Code. Lo pidió Carlos el viernes a las 5:19 p. m. y lo escribió Fable. Entrega hoy a las 9:00 p. m., en `docs/PROPUESTA_P1.md` y en cinco minutos de conversación con Carlos.

## Por qué

En la mentoría 1 nos dijeron que la solución puede cambiar y que hay que enamorarse del problema (`docs/MENTORIA_1.md`). Carlos no está tranquilo con la solución, y hay algo que no sabemos: cómo trabaja el Banco de Alimentos de Manizales en un día normal.

Hay además una trampa que queremos evitar. Muchas herramientas de emergencia funcionan bien cuando llega la tragedia, pero nadie sabe usarlas, porque solo se diseñaron para la tragedia. DespachoX tiene que servir un martes cualquiera. Los derrumbes y los cierres de vías pueden ser ese uso de todos los días, porque en Manizales pasan sin terremoto; eso también hay que pensarlo.

Samuel presenta el pitch y Jacobo opera la demo. Los dos van a tener que responder por qué existe DespachoX y para quién.

## Las preguntas

1. ¿Cómo trabaja el Banco de Alimentos de Manizales un día normal? ¿Quién pide y cómo, quién reparte o quién recoge, qué comida se daña y por qué? Pregunten; no supongan.
2. Elijan tres personas reales del problema: una líder de junta de acción comunal, quien despacha en un centro de acopio y un conductor. Para cada una, describan un día normal y un día con una vía cerrada por un derrumbe. ¿Qué necesita cada una ese día, y qué hace hoy para conseguirlo?
3. ¿Qué parte de DespachoX le serviría a cada una un día normal? ¿Qué parte solo sirve en la tragedia?
4. Si pudieran cambiar la solución, ¿qué cambiarían? Máximo tres ideas. Cada una dice quién la usa, cuándo, y cómo la mediríamos en un piloto de 30 a 90 días.

## Cómo hacerlo

- Hablen con gente antes de escribir: una llamada o un mensaje al Banco de Alimentos, una líder de junta que conozcan, un conductor, alguien de su familia que haya recibido o repartido ayuda en agosto. El guion está en `docs/MENTORIA_1.md`. Si las oficinas ya cerraron, dejen el mensaje para mañana temprano y sigan con las otras personas.
- Lean `docs/PROBLEMA.md` y `docs/MENTORIA_1.md`. Hacia las 8:00 p. m. llegan dos investigaciones que ayudan, `docs/investigacion/10_problema_usuarios_alternativas.md` y `docs/investigacion/11_voz_publica_actores.md`, y el informe de contexto en `docs/informe/`.
- Pueden pedirle ayuda a Claude en el chat para ordenar ideas, pero las respuestas tienen que venir de personas o de fuentes. No gasten en esto el cupo de su Claude Code, que sigue con A2 y C2.
- Anoten nombre, cargo y hora de cada persona con la que hablen. Ningún dato personal de familias afectadas.

## Pistas para no partir de cero

Son hipótesis de Fable, no respuestas. Confírmenlas o descártenlas con lo que les digan.

- Las juntas podrían pedir por el mismo canal todos los días, no solo en una emergencia, y saber si su pedido llegó.
- El reporte de vías cerradas le sirve a cualquiera que reparta en Manizales en temporada de lluvias, no solo a la ayuda humanitaria.
- Un banco de alimentos recibe perecederos todos los días. Saber qué vence hoy y quién puede recibirlo hoy ataca el desperdicio sin esperar ninguna tragedia.
- La tabla por comuna y vereda (encargo T1) le diría a la Unidad de Gestión del Riesgo quién pidió, quién recibió y quién no ha pedido.

## Qué entregar

`docs/PROPUESTA_P1.md`, de una página: con quién hablaron y qué aprendieron; las tres personas y sus dos días; qué sirve un día normal y qué solo en la tragedia; y sus tres ideas. Súbanlo a la rama `samuel-bot` y avisen en `torre/CANAL.md`. A las 9:00 p. m., cinco minutos con Carlos y Fable para decidir qué cambia en la ficha y en el pitch antes de la fusión de las 11:00 p. m.

## Qué no hacer

- No programen nada nuevo por esto hoy. Las funciones nuevas se deciden a las 9:00 p. m. y se congelan mañana a las 8:30 a. m.
- No inventen cómo funciona el Banco de Alimentos. Si no lo saben, escriban «no sabemos» y a quién hay que preguntar.
