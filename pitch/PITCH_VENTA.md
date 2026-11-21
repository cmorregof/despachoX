# Pitch de tres minutos · versión para vender

Sábado 21 de noviembre, 11:50 a. m. Responde a la mentoría 2: «el modelo corre bien, pero no saben venderlo». Reemplaza la versión de tres minutos de `pitch/GUION.md` para la semifinal. Las cifras son las mismas de `pitch/CIFRAS_PITCH.md`, `entrada/ESCALA.md` y `docs/SIMULACION.md`, sección 9. No hay ninguna nueva.

## Qué cambia

- El pitch cuenta un día en la mesa de despacho. Antes era una lista de bloques con cifras.
- Los tres puntos que propuso Jacobo (los 15.000 mensajes, el silencio y los cierres sin confirmar) son los tres momentos de ese día.
- La demo en vivo se cambia por un video sin audio, de fondo. El tablero de la nube queda abierto en otra pestaña por si el jurado quiere verlo en las preguntas.
- Quedan cinco cifras en voz. Las demás van en las diapositivas de respaldo.

## El texto

Unas 400 palabras, tres minutos a ritmo tranquilo. El asterisco marca una cifra que sale del pitch si a la 1:00 p. m. nadie ha abierto su fuente.

### 1 · El problema · 0:00 a 0:30

> Después del sismo, la comida llegó a Manizales. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y habían entregado 41*.
>
> Piensen en quien despacha ese día. Tiene un teléfono que no para de sonar y unas vías que se cierran sin avisar. Repartir veinte pedidos lo hace cualquiera con oficio. La ayuda hace falta cuando llegan miles.

### 2 · Qué es Convite · 0:30 a 0:45

> Convite es la mesa de despacho para ese día. Los barrios y las veredas piden por chat o por SMS, con sus palabras. El sistema lee cada mensaje y calcula las rutas. La decisión la toma una persona.

### 3 · Un día en la mesa · 0:45 a 2:05

> Les contamos tres momentos de ese día.
>
> El primero es la avalancha. En una prueba de carga le mandamos 15.000 mensajes a la vez. No se perdió ninguno, y todos quedaron en cola, en su orden.
>
> El segundo es el barrio que no escribe. Después de un desastre, puede ser el que se quedó sin señal. Si un punto crítico lleva seis horas sin pedir, Convite le avisa al despachador para que mande a alguien a verificar. Así el que no puede escribir tampoco se queda por fuera.
>
> El tercero es la vía. Un conductor escribe que hay un derrumbe. Convite no cierra la vía por un mensaje, porque puede ser un error o un rumor. La deja reportada hasta que el despachador la confirma. Cuando la confirma, el plan se recalcula en menos de diez segundos, y el pedido que iba en camión pasa a un campero, que sí entra.

### 4 · La evidencia · 2:05 a 2:30

> ¿Y sirve? Lo medimos en simulación, con 30 jornadas por política y carga alta. Si se despacha por orden de llegada, el 40,5 % de los pedidos críticos llega a tiempo. Con Convite llega el 98,4 %.

### 5 · El piloto y lo que pedimos · 2:30 a 3:00

> Esto se queda en Manizales. El piloto dura 90 días en la rutina del Banco Arquidiocesano de Alimentos, con la Unidad de Gestión del Riesgo. Empieza en Ciudadela del Norte y El Manantial, y cada 30 días suma una zona si la anterior cumplió.
>
> Para empezar necesitamos un despachador del Banco y 30 días trabajando a su lado.
>
> Somos Convite. En el Eje Cafetero, el convite era la forma en que los vecinos se juntaban para abrir un camino.

## De dónde sale cada cifra

| Lo que se dice | Fuente | Tipo |
|---|---|---|
| 404 toneladas en acopio y 41 entregadas, seis días después | `pitch/CIFRAS_PITCH.md`, nota de Portafolio. Son cifras de «los Bancos de Alimentos», no de Manizales | Tomado de una fuente, por verificar |
| 15.000 mensajes a la vez, ninguno perdido | `entrada/ESCALA.md`. En local, con extractor falso de 1,8 s, sin Telegram ni Railway. Repetida el 21 de noviembre a las 11:40 a. m.: 0 perdidos, 0 errores | Medido por nosotros |
| Seis horas de silencio en un punto crítico | `entrada/silencio.py`, `UMBRAL_H = 6` | Regla del producto |
| Recalcula en menos de diez segundos | `docs/GUION_DEMO.md` | Medido por nosotros en la demo |
| 40,5 % y 98,4 % de críticos a tiempo | `despacho/sim/resultados_velocidades/tablas.md`, carga alta, 30 jornadas por política, frente a orden de llegada. Diferencia de 57,9 puntos, intervalo del 95 % de 52,7 a 63,1 | Simulación |

Si preguntan por los 15.000, la respuesta completa es esta: se probó que el sistema los recibe y los guarda. Leerlos con el modelo real toma minutos y planear rutas para miles exige agrupar los pedidos por punto de entrega. Eso está en curso (`encargos/S3_MUCHOS_PEDIDOS.md`) y, si no alcanza hoy, es el primer hito del piloto.

Frente a un despachador con oficio, la comparación va en la diapositiva de respaldo C y se dice solo si la piden, con la frase de `pitch/CIFRAS_PITCH.md`, fila C16.

## El video de fondo

Sin audio, tres minutos, sin loop, en el mismo orden del texto. Si Jacobo prefiere el loop de 30 segundos, que tenga estas mismas escenas en este orden.

| Tramo | Mientras se dice | Qué se ve |
|---|---|---|
| 0:00 a 0:30 | El problema | Portada con la ilustración y el logo, quieta |
| 0:30 a 0:45 | Qué es | El chat: llega un pedido por Telegram y el bot pregunta por el lugar |
| 0:45 a 1:10 | La avalancha | La terminal de la prueba de carga con «Mensajes perdidos: 0», y la cola del tablero |
| 1:10 a 1:35 | El silencio | El tablero con una alerta «Sin contacto: verificar» y el botón «Mandar a verificar» |
| 1:35 a 2:05 | La vía | El chat con el derrumbe, el cierre reportado, «Confirmar», «Recalcular» y el plan nuevo con el campero |
| 2:05 a 2:30 | La evidencia | La barra de la simulación, 40,5 % y 98,4 % |
| 2:30 a 3:00 | El piloto | El mapa de Ciudadela del Norte y El Manantial, y al final el logo |

Antes de grabar: reiniciar la base, entrar al tablero para que la clave no salga, teléfono en «no molestar», dictar «solo pasa moto» y no abrir la pestaña Informe.

## Cómo decirlo

- Una sola voz para todo el relato. Dos voces partían el hilo. La segunda persona contesta las preguntas técnicas.
- De memoria, mirando al jurado. La pantalla acompaña; quien habla no la mira.
- Las dos primeras frases y la última se dicen igual siempre. Lo demás puede variar.
- Pausa de un segundo después de «41» y después de «98,4 %».
- Si el tiempo aprieta, sale primero la frase de «Piensen en quien despacha». Después, la del campero.
