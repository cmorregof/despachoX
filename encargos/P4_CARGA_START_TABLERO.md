# P4 · Prueba de 15.000 mensajes, el /start y el diseño del tablero

Lo pidió Carlos el viernes a las 10:33 p. m. y lo escribió Fable. P2 y P3 siguen vigentes; la prueba de carga puede quedar corriendo sola durante la noche mientras hacen lo demás.

## Samuel · 15.000 mensajes a la vez

Ya mediste 5.000 a la vez en `entrada/ESCALA.md` (914 por minuto, ninguno perdido). Ahora, 15.000, con el mismo arnés.

- **Nunca contra la nube ni contra servicios reales.** Ni el bot de Railway, ni Telegram, ni la API de Anthropic. Una prueba así contra producción tumba la demo de todo el equipo, puede hacer que Telegram limite al bot y gasta créditos. Se corre en local, con el extractor falso y una base temporal.
- **Qué medir:** mensajes por minuto, respuesta en mediana, en el percentil 95 y la máxima, mensajes perdidos (la meta es cero), mensajes guardados crudos, memoria máxima e integridad de la base al final. Agrega una fila a `entrada/ESCALA.md`.
- **El cuello de botella conocido** es `lugares/nomenclator.buscar`: el 97 % del tiempo por mensaje, con un techo de unos 900 por minuto. Si 15.000 no caben en un tiempo razonable, prueben un prefiltro de candidatos o un caché por texto, con pruebas de que el resultado no cambia. Es una mejora de rendimiento, no una función nueva.
- **Límite que no depende de nosotros:** Telegram limita cuántas respuestas por segundo puede mandar un bot. Su página de preguntas frecuentes para bots habla de unas 30 por segundo; verifíquenlo ahí. Contestar a 15.000 personas tomaría entonces varios minutos, aunque el servidor aguante. En el pitch se dice así: ninguno se pierde y todos quedan en cola con su orden.

## Samuel · el mejor /start posible

Quien escribe puede estar asustado, con poca batería y sin saber qué es un bot.

1. Un solo mensaje corto: quién somos, para qué sirve y qué hacer ahora.
2. Botones antes que texto: «Pedir comida», «Reportar una vía cerrada», «Confirmar una entrega», «¿Cómo va mi pedido?».
3. Un ejemplo que se copia con un toque, y la opción de mandar una nota de voz.
4. La privacidad en una línea: qué se guarda, para qué y cómo borrarlo (Ley 1581).
5. Antes de guardar, el bot repite lo que entendió y pide confirmar: «Entendí: 40 familias en San José, arroz y leche. ¿Está bien?».
6. Errores amables: si no entiende, ofrece los botones de nuevo y no culpa a nadie.
7. Prueba de uso con tres personas reales que no conozcan el proyecto: cuánto tardan en hacer su primer pedido y dónde se traban. Anótenlo en el canal.

## Jacobo · un tablero que no se vea de cajas

1. **Tarjetas en vez de rectángulos:** bordes redondeados (12 a 16 px), sombras suaves, más aire entre bloques y menos líneas de borde.
2. **Indicadores como fichas grandes**, con el número, su meta y una palabra de contexto. Por ejemplo: «92 % críticos a tiempo · meta 90 %».
3. **Tablas con estilo:** encabezados discretos, filas alternadas suaves, colores de estado (pendiente, en ruta, entregado, silencio) y nada de la cuadrícula por defecto.
4. **Tema de Streamlit** en `.streamlit/config.toml` con la paleta del informe (tinta #4F4086, ámbar #A36752, crema #EBD3A2, ceniza #6E6878) y una sola tipografía web legible.
5. **Mapa con fondo claro** y los mismos colores de estado.
6. **Ver los cambios en el celular**, porque es probable que el jurado vea capturas pequeñas.
7. **Si sobra tiempo:** pasar el módulo `triage/` con 15.000 solicitudes sintéticas y anotar cuánto tarda y cómo queda la cola. Es el mismo número que pidió Carlos, visto desde la mesa.
