# Guion del pitch · DespachoX

Borrador 1, viernes 11:00 a. m. La organización aún no dice cuánto dura el pitch: aquí va la versión de **tres minutos**, y al final qué se añade si dan cinco. El pitch debe cubrir los seis componentes de la rúbrica; cada bloque dice a cuál responde. Lo marcado **[ ]** falta por conseguir.

Una sola persona habla y otra maneja la demo. Quien habla no toca el computador.

## Versión de tres minutos

### 1. El problema (30 s) · criterio 1

> El 10 de agosto, Manizales se volvió el punto de acopio de alimentos para el Eje Cafetero. La comida llegó. Lo que faltó fue saber a dónde mandarla primero, por cuál vía y antes de que se dañara.

- Un dato de volumen con fuente: **[toneladas movidas por la red de bancos de alimentos, verificado]**.
- Un dato de vías: **[dos salidas de Manizales cerradas dos días después, verificado]**.
- La voz del usuario: **[frase textual de un despachador o coordinador, con nombre y cargo]**.

No decir «desabastecimiento en 48 horas»: no tenemos fuente.

### 2. Para quién (15 s) · criterio 1

> Nuestro usuario es la persona que despacha en el centro de acopio. Hoy decide con un teléfono, un cuaderno y lo que le cuentan los conductores.

### 3. Demo en vivo (75 s) · criterio 2

Con el tablero proyectado y el plan aprobado ya en pantalla:

1. «Un líder de barrio pide ayuda por chat.» Se envía el mensaje preparado. Aparece el pedido en el mapa. (15 s)
2. «El despachador lo confirma y pide un plan.» Clic, rutas dibujadas. (15 s)
3. **«Ahora necesito a alguien del jurado.»** Se le pasa un teléfono o se muestra un código QR del bot: «Escriba que hay un derrumbe en La Siria.» (20 s)
4. El cierre aparece en rojo. El despachador lo confirma. Las rutas cambian. «Ningún camión pasa ya por ahí, y lo que vence primero sigue saliendo primero.» (20 s)
5. «El sistema propuso. Quien aprobó fue una persona.» (5 s)

Si algo falla: se dice «tenemos el mismo recorrido grabado» y se reproduce el video. No se depura en vivo.

### 4. Qué hay detrás (25 s) · criterio 3

> Tres piezas. Un modelo de lenguaje que solo lee y ordena el mensaje. Un optimizador de rutas para flota mixta que prioriza por vencimiento. Y una regla: decide el despachador.

- Capacidad UNAL: **[indicador de lluvia acumulada del IDEA, que penaliza los tramos de ladera en alerta, si queda integrado]**.
- Asesoría: **[profesor de la Sede que revisó la formulación, si se consigue]**.

### 5. Qué medimos (20 s) · criterios 2 y 6

> Lo probamos en **[N]** escenarios simulados sobre la red vial real de Manizales, contra un despacho por orden de llegada.

- Entregas a tiempo en puntos críticos: **[línea base]** contra **[DespachoX]**.
- Perecederos vencidos: **[línea base]** contra **[DespachoX]**; la meta del reto es menos del 5 %.

> Es una simulación, con sus supuestos escritos. El dato real sale del piloto.

### 6. Plan y aliados (25 s) · criterios 4 y 5

> En 30 días reconstruimos los despachos de agosto con **[aliado]** y comparamos. En 60, un simulacro con un comité barrial y vehículos reales. En 90, operación junto al despachador y decisión de adopción.

- Corre en un portátil, sin conexión si hace falta. Leer un mensaje cuesta fracciones de centavo.
- No guarda nombres ni teléfonos.

### 7. Cierre (10 s)

> La reconstrucción ya tiene fondo y las donaciones ya tienen plataformas. A la última milla de la comida le faltaba una mesa de despacho. Somos DespachoX.

## Si dan cinco minutos

- Tras el bloque 1: un antecedente de cierre vial por derrumbe anterior a 2026, para mostrar que el problema vuelve cada invierno.
- En la demo: la trazabilidad con QR y la bitácora de decisiones.
- En el bloque 5: la política intermedia (optimizar sin recalcular), que muestra cuánto aporta el recálculo.
- En el bloque 6: riesgos y cómo se mitigan, y qué se le pide a cada padrino.

## Preguntas que van a hacer

| Pregunta | Respuesta corta |
|---|---|
| ¿Qué pasa si la IA entiende mal? | Le responde al remitente lo que entendió y un humano confirma antes de despachar. Medimos el acierto con mensajes mal escritos: **[número]** |
| ¿Por qué no usar Google Maps o Waze? | Dan una ruta para un carro. No reparten veinte pedidos entre cinco vehículos distintos ni saben qué se vence |
| ¿Y sin internet? | El mapa y el optimizador corren sin conexión. El pedido se digita a mano |
| ¿La línea base es justa? | Es lo que hace un despachador con prisa: orden de llegada y vehículo más cercano. Además comparamos contra optimizar una sola vez |
| ¿Qué de la UNAL hay aquí? | **[respuesta honesta según lo que quede integrado]** |
| ¿Quién lo va a usar? | **[aliado con nombre]** |
| ¿Qué tiene de nuevo? | La integración. Existen herramientas de ruteo, de registro y de reportes; no encontramos una abierta que una el pedido por chat con el despacho y el recálculo |
| ¿Datos personales? | No guardamos nombres ni teléfonos; el remitente queda como un código |

## Lo que falta para que este guion sea verdad

1. Una frase real de un usuario.
2. Dos cifras verificadas por un humano.
3. Los números de la simulación.
4. Un aliado con nombre.
5. La capacidad UNAL integrada, o una frase honesta sobre el plan de integrarla.
6. El video de respaldo.
