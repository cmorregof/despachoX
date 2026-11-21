# P2 · Trabajo de la noche (Samuel y Jacobo)

Lo escribió Fable el viernes a las 10:20 p. m., después de revisar todo lo que subieron. Va en orden de prioridad: si no alcanzan, lo de abajo queda para las 7:00 a. m. Las funciones se congelan el sábado a las 8:30 a. m.; después solo se arregla y se pule.

## Samuel

1. **Verificar las cifras del pitch.** Abre el enlace de las diez cifras candidatas de `docs/DECISIONES_9PM.md` y de las tres que añadiste a `docs/FUENTES.md`. Confirma número, fecha y redacción, y regístralas en `docs/FUENTES.md` como «verificada por Samuel, hora». Si una no coincide con la fuente, márcala y avisa en el canal. Es lo más valioso de la noche: sin esto, ninguna cifra puede ir al pitch (criterios 1 y 6).
2. **Raciones con fuente.** Respuesta a tu pregunta de las 6:00 p. m.: sí. Reemplaza las raciones de la semilla en `entrada/raciones.py` por las de `docs/datos/demanda.md` (555 g de ración seca por persona y día; 2,9 personas por hogar en Manizales), con la fuente en un comentario. Si tocas `despacho/semilla.py`, saca pollo y pan de `PERECEDEROS` o fallará con `KeyError`.
3. **La pasarela SMS con un celular real**, y un video de 30 a 60 segundos de un pedido por SMS que aparece en la mesa. Es el respaldo de la demo (criterio 2).
4. **`ENTREGADO` solo desde el punto de destino o el conductor**, como propusiste a las 9:00 p. m. Es un arreglo de seguridad, así que puede entrar aun después del congelamiento.

## Jacobo

1. **Pestaña «Territorio» (parte C de `encargos/T1_TERRITORIO.md`).** Si a las 11:30 p. m. todavía no existe `despacho/territorio.py`, escribe la misma función en `tablero/territorio.py`, con la misma firma, y la movemos después.
2. **Una sola definición de «silencio».** Hoy hay tres: `triage/debiles.py`, los pedidos con `origen='silencio'` de Samuel y la lista de T1. Acuerden con Samuel una función y un umbral, y anótenlo en el canal.
3. **Pintar en el tablero los pedidos con `origen='silencio'`**, con la etiqueta «Sin contacto: verificar» y las acciones «Mandar a verificar» y «Descartar», como pidió Samuel a las 7:00 p. m.
4. **Un escenario de triage para el pitch.** Elige uno, por ejemplo la ráfaga de pedidos coordinados, y escribe un párrafo con lo que muestra y con los parámetros que son supuestos. La ficha lo va a citar así.
5. **El video de respaldo de la demo**, con el guion de `docs/GUION_DEMO.md`.

## Para los dos

Cada etapa termina con pruebas en verde y una entrada LISTO en el canal. Nada de datos personales reales.
