# Encargo · Samuel · sábado 21 de noviembre

De Carlos, redactado con Fable. El pitch es a las 2:00 p. m. y la mentoría a las 10:30.

## Tu zona para el pitch: El Manantial y la vía a Neira

Eres quien responde por el corregimiento. Estudia la sección 2b del dossier: sus veredas, cómo se llega, qué pasó en Pueblo Hondo y el historial de derrumbes de la vía a Neira. Tienes que poder contar, sin leer, cómo llega un camión del Banco a Alto Bonito (8,8 km por nuestra red, saliendo por la comuna San José) y qué pasa si la vía se cierra en Maracas.

Preguntas del dossier que te tocan: 3, 4, 6 y 7.

## Lo tuyo en el producto

1. **H6, antes de cualquier otra cosa.** Un lugar aprendido por el pin de una persona se le ofrece a otra (`lugares/nomenclator.py`, líneas 257 a 259 y 211 a 218). El arreglo está descrito en `evaluacion/inyeccion/HALLAZGOS.md`: el lugar aprendido solo se le ofrece a quien lo envió hasta que el despachador lo valide. Al arreglarlo, quita el xfail estricto de su prueba, o la suite falla. Trabaja sobre el `main` de hoy, porque `entrada/flujo.py` y `entrada/sms.py` cambiaron esta mañana. Es un arreglo, así que cabe después del congelamiento de las 8:30. Una función nueva no cabe.
2. **Prueba con tu teléfono, apenas esté el despliegue.** Manda un pedido, confirma el lugar, reporta un cierre y manda `ENTREGADO DX-…` con el código de un paquete en ruta. Esta mañana entró el arreglo para que esa entrega quede registrada con el modelo activo, y nadie lo ha probado con el modelo real. Escribe en el canal qué pasó en cada paso.
3. **«Sí pasa moto».** El lector por reglas lo lee como si la moto quedara bloqueada (`entrada/sms.py`, líneas 194 a 196). No lo arregles hoy. En la demo, el reporte de cierre se dicta con «solo pasa moto».

## Lo que defiendes en las preguntas

El prototipo por dentro: cómo lee el bot, qué pasa sin internet, datos personales y seguridad. En `pitch/PREGUNTAS_JURADO.md` son las preguntas del bot, del SMS, de la Ley 1581 y de la inyección. Dos cosas que no se dicen: «no guardamos nombres ni teléfonos», hasta que H6 esté arreglado, y que el lector se midió con mensajes reales, porque los 330 son sintéticos y los escribimos nosotros.

## Horas

- 9:30 · H6 empujado y avisado en el canal.
- 10:00 · prueba con el teléfono hecha y escrita en el canal.
- 10:30 · mentoría.
- 12:30 · ensayo de preguntas con Jacobo y José Manuel. Cada uno le hace a los otros las preguntas que no escribió.
## Lo que los tres tienen que saber de memoria

Lean primero `docs/DOSSIER_ZONA.md`, secciones 1, 4 y 5. Son veinte minutos. Después, esto.

**El piloto.** Empieza en la comuna Ciudadela del Norte y el corregimiento El Manantial. Cada 30 días suma una zona, si la anterior cumplió y el Banco lo confirma. A los 30 días entra La Macarena y El Tablazo. A los 60, Atardeceres y Kilómetro 41.

**Cinco hechos de la zona.** Todos tienen fuente en el dossier, y ninguno lo ha abierto todavía una persona.
1. Ciudadela del Norte es la comuna más poblada de Manizales, con 58.776 habitantes (ASIS 2023, tabla 30).
2. El 20 de agosto, la Alcaldía y el Programa Mundial de Alimentos recorrieron las veredas con más daño para mirar seguridad alimentaria. En esa nota hablan las juntas de Alto del Guamo y de Alto Bonito.
3. En Pueblo Hondo, vereda de El Manantial, cuatro viviendas tuvieron pérdida total (Alcaldía, 27 de agosto).
4. La vía a Neira, que pasa por Alto Bonito y Maracas, tiene cinco derrumbes en el registro de INVÍAS entre 2017 y 2023. En Maracas no hay ruta alterna.
5. El 21 de octubre, con las lluvias, los Bomberos revisaron laderas y drenajes en la comuna.

**Lo que se dice con honestidad.** El daño urbano del sismo se concentró en el centro, Milán, Chipre y Galán. Ciudadela del Norte queda fuera de esa lista. La elegimos por su tamaño, por sus laderas y porque el PMA ya buscó necesidades de comida en sus veredas vecinas. Eso es lectura nuestra, y así se dice.

**Lo que no sabemos.** Cuánta gente vive en El Manantial. Si el Banco ya atiende organizaciones en la zona. Qué encontró el PMA. Ante una pregunta sobre esto, la respuesta es «no lo sabemos todavía, y es lo primero que le preguntamos al Banco».

**Cómo se dice bien.** Ciudadela del Norte es comuna, urbana. El Manantial es corregimiento, rural, y Alto Bonito, Alto del Guamo y Pueblo Hondo son veredas suyas. Solferino, Comuneros y Villa Hermosa hoy son de la comuna Nuevo Horizonte, no de Ciudadela del Norte. La vía es la vía a Neira. El banco es el Banco Arquidiocesano de Alimentos. La UGR es de Manizales; la UNGRD es nacional. Quien visitó fue el PMA.

**Tres reglas para hablar ante el jurado.**
- Ninguna cifra sin su fuente y sin decir si es medida, tomada de una fuente o simulada.
- Lo de la simulación se dice con la palabra «simulación», la línea base y las 30 jornadas por política.
- Si no saben algo, lo dicen. El jurado perdona un «no lo sabemos» y no perdona un dato inventado.

**Antes de editar cualquier documento:** `git pull --rebase`. Esta mañana cambiaron casi todos. Y avisen en `torre/CANAL.md` lo que terminan.
