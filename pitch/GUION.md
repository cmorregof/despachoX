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
3. **«Ahora necesito a alguien del jurado.»** Se le pasa un teléfono o se muestra un código QR del bot: «Escriba que hay un derrumbe en la avenida del Centro.» (Es el tramo que sí cambia rutas con la semilla; ver `docs/GUION_DEMO.md`. La Siria ya se reconoce y sirve para las preguntas.) (20 s)
4. El cierre aparece en rojo. El despachador lo confirma. Las rutas cambian. «El camión ya no entra a San José, así que el sistema manda el campero.» (20 s)
5. «El sistema propuso. Quien aprobó fue una persona.» (5 s)

Si algo falla: se dice «tenemos el mismo recorrido grabado» y se reproduce el video. No se depura en vivo.

### 4. Qué hay detrás (25 s) · criterio 3

> Tres piezas. Un modelo de lenguaje que solo lee y ordena el mensaje. Un optimizador de rutas para flota mixta que prioriza por vencimiento. Y una regla: decide el despachador.

- Capacidad UNAL: la patente colombiana 37476 de la Universidad Nacional, un empaque que captura etileno y retarda la maduración. El modelo trata distinto el vencimiento de un lote con ese empaque, como supuesto declarado, y el piloto propone medirlo con la UNAL. **[decir «vigente» solo si Fernando Bernal confirma la anualidad 2026]**
- Asesoría: **[profesor de la Sede que revisó la formulación, si se consigue]**.

### 5. Qué medimos (20 s) · criterios 2 y 6

> Lo probamos en 360 jornadas simuladas sobre la red vial real de Manizales, con 30 semillas por nivel de carga.

- Contra un despacho por orden de llegada, las entregas a tiempo en puntos críticos suben 12, 29 y 46 puntos porcentuales con carga holgada, media y alta.
- Los perecederos vencidos bajan de entre 0,5 % y 3,5 % a 0 %. Eso lo logra la regla de bodega «primero lo que vence primero», no el ruteo.
- Contra un despachador experto que ya prioriza lo urgente, empatamos en puntos críticos y recorremos entre 47 y 75 km menos por jornada. En entregas a tiempo de todos los puntos quedamos 1,8 y 2,2 puntos por debajo con carga media y alta: se dice si preguntan.

> Es una simulación, con sus supuestos escritos. No todos los centros de acopio tienen a ese experto un domingo a las tres de la mañana: DespachoX deja esa pericia escrita y disponible para cualquier voluntario. El dato real sale del piloto.

Fuente: `docs/SIMULACION.md`. Estas cifras son de la primera corrida; el encargo S2 las puede cambiar. Decir siempre contra qué línea base es cada cifra.

### 6. Plan y aliados (25 s) · criterios 4 y 5

> En 30 días reconstruimos los despachos de agosto con **[aliado]** y comparamos. En 60, un simulacro con un comité barrial y vehículos reales. En 90, operación junto al despachador y decisión de adopción.

- Corre en un portátil. El optimizador no necesita internet; el fondo del mapa sí. Leer un mensaje cuesta fracciones de centavo.
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
| ¿Y sin internet? | El optimizador y la red vial corren sin conexión. El fondo del mapa y el chat necesitan red; sin ella, el pedido se digita en el tablero |
| ¿La línea base es justa? | Usamos tres. Contra el orden de llegada ganamos por mucho. Contra un experto que prioriza lo urgente empatamos en puntos críticos, quedamos unos 2 puntos por debajo en el total y ahorramos kilómetros. Lo decimos así porque así salió |
| Entonces, ¿para qué el optimizador si una regla simple empata? | Porque esa regla vive en la cabeza de una persona con experiencia. El sistema la aplica siempre, la combina con cierres viales que llegan por chat, ahorra recorrido y deja registro. Y la simulación no mide el valor de la entrada por chat ni de la trazabilidad |
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
