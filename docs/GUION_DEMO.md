# Guion de la demo de tres minutos

Sesión `maestro`, viernes 20 de noviembre, 2:45 p. m. Ensayado en bases temporales con la semilla de `main` (commit `1730169`), el optimizador real y las dos redes: la urbana de las 11:20 a. m. y la ampliada de las 2:22 p. m. El resultado es el mismo en ambas. El bot entró a `main` a las 2:30 p. m. y nadie lo ha corrido con Telegram real, porque faltan las claves. El tablero entró completo a las 2:32 p. m. Ensayé el despacho y la ubicación de lugares, no los clics: los textos del bot salen de `entrada/flujo.py` y de `lugares/`, y los botones, de `tablero/README.md`. Hay que recorrerlo una vez con todo junto y corregir aquí lo que no coincida.

**Actualización del sábado 21, 1:00 a. m. (rama `erratas`).** Esta versión corrige lo que había quedado viejo. El nomenclátor carga hoy 450 apodos, y el bot ya calcula los kilos con la tabla de raciones. «avenida del centro» sin filtro ya no sale «exacto», y por eso el paso 2 usa el filtro de cierres, como `demo/preparar.py` de la rama `demo-noche`. El lector por reglas pregunta con artículo, «la avenida del centro». El plan 3 avisa también `camion: punto:3 quedó aislado de la red`. El comando `entrada.procesar` no existe, así que el respaldo por terminal es otro. La base de la nube se reinicia con `DESPACHOX_REINICIAR=1` en Railway, porque el tablero de `main` no tiene botón para eso. El bot y el tablero corren en la nube desde el viernes a las 3:45 p. m. Las salidas del nomenclátor y del lector por reglas se repitieron el sábado a la 1:00 a. m. sobre una base temporal con la semilla; el optimizador no se volvió a correr esta noche.

**Aporta a:** criterio 2 (funcionamiento y demostración). Muestra las cuatro cosas que pide el entregable del reto: pedido, cierre vial, recálculo y decisión humana, y de paso la flota mixta.

Una persona habla y otra maneja. Quien habla no toca el computador.

## La historia en una frase

Un barrio pide comida por chat, el despachador la suma al plan, un conductor reporta un derrumbe que le impide al camión llegar a ese barrio, y el sistema propone mandar un campero. El despachador aprueba.

## Datos fijos que hacen que salga bien

Todo está en `datos/semilla/`. Nada de esto se improvisa en vivo.

| Dato | Valor | Por qué importa |
|---|---|---|
| Barrio del pedido | San José, que ya es el punto 14 «Salón comunal San José» | Está en `barrios.csv`. `lugares` lo resuelve como exacto y seguro, sin modelo |
| Vía del cierre | avenida del Centro, arista 582617778 → 323215241 | Está en `vias.csv`. Es la única de las cinco vías ensayadas cuyo cierre cambia las rutas. Deja al camión sin acceso al punto 14 |
| Flota | Camión 1 (3.000 kg) y Campero 1 (600 kg) en el Acopio Oriente; Camión 2 (2.000 kg), Campero 2 (600 kg) y Moto 1 (40 kg) en el Acopio Occidente | El campero es quien resuelve el cierre |
| Pedidos de la semilla | 17 `confirmado` y 3 `nuevo` (los 18, 19 y 20) | Los tres `nuevo` se dejan sin tocar. No ensayé qué pasa si se confirman |
| Puntos críticos | Arrayanes, Campohermoso y San Jorge | Deben seguir «3 de 3 a tiempo» en los tres planes |
| Pedidos previos en San José | Los 14 y 17, creados 139 y 150 minutos antes de la carga | Quedan fuera de la ventana de dos horas de la regla de duplicados |
| Un solo envío del mensaje de San José por cada carga de la base | Reiniciar la base antes de cada ensayo | Un segundo pedido del mismo punto en dos horas queda como duplicado y el plan lo ignora |
| Hora de carga de la semilla | Menos de 30 minutos antes de la demo; nunca más de 90 | Las horas límite y los vencimientos son relativos a la carga. Los urgentes tienen 4 horas y la última parada urgente llega cerca de 2 horas después |
| Búsqueda del optimizador | `--segundos 3` | Medido: el plan sale en 3,4 a 3,8 segundos y da el mismo resultado esencial que con 8 |
| Base compartida | La misma ruta absoluta en `DESPACHOX_DB` para el bot, el despacho y el tablero | Sin eso, cada copia del repositorio usa su propia base y no se ven |

Vías que **no** se usan en la demo: vía a Chinchiná, La Siria y Panamericana (el plan no cambia a la vista) y avenida Bernardo Arango (el orden de paradas no cambia, solo unos segundos de recorrido). Las rutas de la semilla no salen de la ciudad, así que cerrar un acceso no las toca. Las otras diez vías de `vias.csv` no están ensayadas.

## Preparación

Entre 30 y 10 minutos antes. Todo desde la raíz del repositorio, con el `.venv`.

1. Reiniciar la base: `.venv/bin/python -m despacho.semilla --cargar --reiniciar`. Debe informar 15 puntos, 2 acopios, 5 vehículos, 34 lotes, 20 pedidos y un nomenclátor de 450 apodos. El reinicio borra también los apodos aprendidos en ensayos anteriores. Si la demo corre en la nube, se usa el botón «Reiniciar datos de prueba» del tablero, en la pestaña «Bitácora». También sirve poner en Railway la variable `DESPACHOX_REINICIAR=1`, esperar el redespliegue y quitar la variable, porque si se queda borra la base en cada despliegue (`despliegue/arranque.sh`; `docs/DESPLIEGUE.md`). Entre el reinicio y la demo nadie le escribe al bot de la nube, para que el pedido nuevo siga siendo el 21.
2. Comprobar el nomenclátor con los mismos filtros que usa el bot, uno para pedidos y otro para cierres (`TIPOS` en `entrada/flujo.py`):

   ```
   .venv/bin/python -c "from datos import db; from lugares import nomenclator as n; con = db.conectar(); r1 = n.resolver(con, 'san jose', tipos=('barrio', 'punto', 'sitio', 'vereda'), elegir=None); r2 = n.resolver(con, 'avenida del centro', tipos=('via', 'sitio'), elegir=None); print(r1.metodo, r1.seguro, r1.pregunta); print(r2.metodo, r2.seguro, r2.pregunta)"
   ```

   Debe decir `exacto True` para los dos, con «Ubiqué «san jose» en: San José (barrio)» y «Ubiqué «avenida del centro» en: avenida del Centro (via)». No sirve `python -m lugares.nomenclator "avenida del centro"`, porque busca sin filtro. Así empata el barrio Centro con la vía y responde con una lista de opciones, aunque el bot sí la ubica. Si `demo/` ya está en `main`, `.venv/bin/python -m demo.preparar` hace los pasos 1 y 2 de una vez y marca `[ok]` o `[FALLA]` en cada punto.
3. Arrancar el bot y el tablero. Proyectar el tablero a pantalla completa.
4. En el tablero, «Calcular plan» y **no aprobar todavía**. Resultado esperado: **17 de 17 pedidos, 3 de 3 críticos a tiempo, tres vehículos con ruta** (Camión 1, Camión 2 y Campero 2). Este es el plan 1 y se queda propuesto. Si se aprueba ahora, el botón «Calcular plan» del paso 0:55 planea solo el pedido nuevo y borra las demás rutas, hasta que C lo corrija.
5. Dejar el teléfono del equipo con el chat del bot abierto y el mensaje 1 ya escrito sin enviar. Tener a mano el QR del bot para el jurado.
6. Internet por datos móviles, no por el wifi del campus. El mapa necesita internet para las teselas.
7. Tener abierto el video de respaldo en otra pestaña, en pausa en el segundo cero.

Si el paso 4 no da 17 de 17, no se hace la demo en vivo: se usa el video.

## Paso a paso

Los tiempos suman tres minutos. Lo que dice quien habla va en cursiva.

### 0:00 a 0:20 · Dónde estamos

Pantalla: mapa con dos acopios, quince puntos, tres críticos resaltados y tres rutas de colores. El plan dice «PROPUESTO · falta aprobar».

*«Esta es la mesa de despacho. Hay diecisiete pedidos confirmados y un plan propuesto para tres vehículos, que el despachador está por aprobar. En ese momento entra un pedido nuevo.»*

### 0:20 a 0:55 · Un barrio pide por chat

Desde el teléfono del equipo se envía, tal cual:

> somos 40 familias en san jose no hay arroz ni leche

El bot responde lo que entendió y pregunta la ubicación. El texto de la pregunta lo da `lugares`:

> Ubiqué «san jose» en: San José (barrio). ¿Es correcto?

Se toca el botón **Sí, es ahí**.

*«El modelo solo leyó el mensaje. No decide nada: le devuelve al remitente lo que entendió y le pregunta si el lugar es ese.»*

En la base queda el pedido 21, con `punto_id` 14, 40 familias y estado `nuevo`. El bot ya aplica la tabla de raciones (`entrada/raciones.py`), así que guarda 80 kg de arroz y 80 de leche, 160 kg en total, con el supuesto de 2 kg por familia. Así salió con el lector por reglas el sábado a la 1:00 a. m., en una base temporal. El viernes se ensayaron las dos variantes, con y sin kilos, y la demo salió en ambas.

### 0:55 a 1:30 · El despachador lo suma al plan

En el tablero, columna «Por revisar»:

1. Clic en **Confirmar** en el pedido de San José.
2. Clic en **Calcular plan**. El plan propuesto anterior queda reemplazado.
3. En menos de diez segundos aparecen las rutas nuevas (unos cuatro cuando el tablero use la búsqueda de 3 segundos). Resultado esperado: **18 de 18 pedidos, 3 de 3 críticos a tiempo. A San José lo atiende un camión.**
4. Clic en **Aprobar**.

*«El despachador confirma el pedido y pide un plan. El optimizador reparte dieciocho pedidos entre la flota y saca primero lo que vence primero. El plan es una propuesta hasta que alguien lo aprueba.»*

### 1:30 a 2:05 · Un jurado reporta un derrumbe

*«Ahora necesito a alguien del jurado.»* Se le pasa el teléfono o escanea el QR. Se le pide escribir esto, que está impreso en una tarjeta:

> derrumbe en la avenida del centro, no pasa camion, si pasa moto

El bot responde:

> Ubiqué «avenida del centro» en: avenida del Centro (via). ¿Es correcto?

Si el mensaje lo lee el lector por reglas (SMS, o el bot sin modelo), la pregunta trae el artículo: «Ubiqué «la avenida del centro» en: avenida del Centro (via). ¿Es correcto?». Es igual de correcta, y `demo/correr.py` acepta las dos. El lector por reglas, además, lee «si pasa moto» como si la moto tampoco pasara, y el bot responde «no pasa camión y moto». El resultado de la demo no cambia, porque la moto no lleva los 160 kg de San José, pero quien habla no dice que la moto sí pasa.

El jurado toca **Sí, es ahí**. En el mapa aparece el cierre como reportado.

*«Cualquier conductor o socorrista puede avisar. El sistema no cierra la vía por un mensaje: lo deja reportado hasta que el despachador lo confirme.»*

### 2:05 a 2:35 · El plan cambia

En el tablero:

1. Clic en **Confirmar** en el cierre. Aparece el aviso «Hay un cierre nuevo: recalcular».
2. Clic en **Recalcular**. En menos de diez segundos aparece el plan nuevo, con la lista de vehículos que cambiaron de ruta.

Resultado esperado, repetido en todos los ensayos:

- En los avisos del plan: `camion: punto:14 quedó aislado de la red`. También sale `camion: punto:3 quedó aislado de la red`, del Comedor comunitario Belén, y no se comenta.
- El pedido nuevo de San José (21) pasa de un camión a un campero.
- Ninguno de los tres pedidos de San José (14, 17 y 21) va en camión.
- Siguen 18 de 18 pedidos, 3 de 3 críticos a tiempo y ninguna parada con retraso.

*«Con la avenida cerrada, el camión ya no puede llegar a San José. El sistema no cancela el pedido: lo pasa a un campero, que sí entra, y reorganiza a los demás. Nadie se queda sin atender y los tres albergues críticos siguen a tiempo.»*

### 2:35 a 3:00 · Decide una persona

Clic en **Aprobar**. Si la bitácora ya existe, se muestra: ubicación confirmada por el remitente, plan aprobado por el despachador.

*«El modelo leyó. El optimizador calculó. Quien decidió fue una persona, y quedó escrito quién y cuándo.»*

## Versión de 75 segundos para el pitch

El pitch reserva 75 segundos para la demo. El guion nuevo del pitch, en la rama `pitch-noche`, le da 63 segundos, de 1:06 a 2:09, y el que manda es el ensayo cronometrado. Se parte de la pantalla posterior al paso 0:55 a 1:30, con el pedido de San José ya aprobado, y se hacen solo el derrumbe y el recálculo (1:30 a 3:00, apretados). El pedido por chat se menciona en una frase mientras el jurado escribe.

## Qué hacer si falla cada paso

Regla general: no se depura en vivo. Se intenta un respaldo una sola vez y, si no sale, se dice «tenemos el mismo recorrido grabado» y se pasa al video.

| Paso | Falla | Qué se hace |
|---|---|---|
| Preparación | El bot escribe y el tablero no lo ve | Cada proceso está usando su propia base. Poner la misma ruta en `DESPACHOX_DB` y reiniciar los dos |
| Preparación | El plan 1 no da 17 de 17 | La base se cargó hace mucho o cambió la semilla. Recargar. Si persiste, video |
| Pedido | El bot no responde en diez segundos | En una terminal ya abierta, el comando `RESPALDO` de la sección «Sin tablero» con el mensaje de San José. Lo lee el lector por reglas, sin modelo, y lo deja en la base local. Se dice «el mismo mensaje, por el canal de respaldo». Con la demo en la nube este respaldo no sirve, porque la terminal no escribe en la base de Railway: video. `entrada.procesar` no existe |
| Pedido | El bot entiende mal (otro barrio, otra cantidad) | No se corrige en vivo. Se dice «por eso el despachador revisa antes de confirmar», se descarta en el tablero y se usa el respaldo de la fila anterior |
| Pedido | El bot pregunta por varias opciones en vez de un «Sí, es ahí» | Se elige San José en los botones. Es el comportamiento correcto y se dice |
| Confirmar pedido | El pedido no aparece en «Por revisar» | Botón de actualizar del tablero. Si no hay, recargar la página |
| Plan | Las rutas anteriores desaparecen y queda una sola | Se aprobó el plan 1 antes de tiempo y «Calcular plan» planeó solo el pedido nuevo. En la terminal: `.venv/bin/python -m despacho.recalcular --segundos 3`, y esperar a que el tablero se actualice |
| Plan | El plan sale vacío o con «error interno» | Mostrar el motivo en pantalla una vez. Repetir el cálculo. Si vuelve a fallar, video |
| Cierre | El jurado escribe otra vía de la lista y el plan no cambia | Se dice: «esa vía no la usa ninguna ruta de hoy, así que el plan sigue igual». Quien maneja envía enseguida el mensaje de la avenida del Centro |
| Cierre | El jurado escribe «La Siria» | El bot la ubica y el cierre se puede confirmar, pero el plan no cambia. Misma frase de la fila anterior, y luego el mensaje de la avenida del Centro |
| Cierre | El jurado escribe un lugar que no está en el nomenclátor | El bot contesta «No conozco «…». Envíame la ubicación…». Se dice: «cuando no sabe, lo dice y pide un pin; no adivina». Luego, el mensaje de la avenida del Centro |
| Cierre | El jurado tarda o no quiere | A los quince segundos lo envía quien maneja, desde el teléfono del equipo |
| Recálculo | No aparece el aviso de recalcular | En la terminal: `.venv/bin/python -m despacho.recalcular --segundos 3`. No usar «Calcular plan» con un plan aprobado |
| Recálculo | El plan nuevo no muestra el cambio esperado | Leer lo que sí muestra: pedidos atendidos y críticos a tiempo. No afirmar lo del campero si no está en pantalla |
| Cualquiera | Se cae internet | El mapa pierde el fondo y el bot deja de recibir. Video |
| Cualquiera | Se cae el tablero | Video. Si es la mentoría y no el pitch, se muestra por terminal con los comandos de abajo |

## Sin tablero: la misma demo por terminal

Sirve para la mentoría si el tablero falla, y para ensayar el despacho solo. El mensaje de respaldo lo lee el lector por reglas (`entrada/sms.py`), con la misma mesa del bot, y toca «Sí, es ahí» por quien escribe. Se probó el sábado a la 1:00 a. m. sobre una base temporal con la semilla. Si `demo/` ya está en `main` (rama `demo-noche`), `.venv/bin/python -m demo.correr` hace todo este recorrido y verifica cada resultado.

```
RESPALDO='from datos import db; from entrada.flujo import Mesa; from entrada.sms import leer_sms; import sys; m = Mesa(db.conectar(), extraer=leer_sms, elegir=None); r = m.recibir_texto("chat-respaldo", sys.argv[1]); print(r[0].texto); s = [d for _, d in r[0].botones if d.startswith("s:")]; print(m.pulsar("chat-respaldo", s[0]).texto if s else "sin botón Sí: revisar el tablero")'
.venv/bin/python -m despacho.optimizar --segundos 3          # imprime 1; se deja propuesto
# llega el pedido 21 por el bot, o con el respaldo:
.venv/bin/python -c "$RESPALDO" "somos 40 familias en san jose no hay arroz ni leche"
sqlite3 datos/despachox.db "UPDATE pedidos SET estado='confirmado' WHERE id=21"
.venv/bin/python -m despacho.optimizar --segundos 3          # imprime 2
.venv/bin/python -m despacho.optimizar --aprobar 2 --quien carlos
# llega el cierre 1 por el bot, o con el respaldo:
.venv/bin/python -c "$RESPALDO" "derrumbe en la avenida del centro, no pasa camion, si pasa moto"
sqlite3 datos/despachox.db "UPDATE cierres SET estado='confirmado' WHERE id=1"
.venv/bin/python -m despacho.recalcular --segundos 3         # imprime 3
sqlite3 datos/despachox.db "SELECT v.nombre, pa.orden, pu.barrio, pa.pedido_id FROM paradas pa JOIN vehiculos v ON v.id=pa.vehiculo_id JOIN puntos pu ON pu.id=pa.punto_id WHERE plan_id=3 ORDER BY 1,2"
```

Los identificadores 21, 1, 2 y 3 valen para una base recién cargada.

## Lo que este guion supone y todavía no existe

1. `entrada/`: el ensayo completo desde un teléfono contra el bot de la nube, que corre desde el viernes a las 3:45 p. m. La entrada por terminal es el comando `RESPALDO`, porque `entrada.procesar` no existe. Los kilos por producto ya salen de la tabla de raciones.
2. `tablero/`: un recorrido completo de estos clics con el bot real. El tablero existe, pero nadie ha hecho la secuencia entera.
3. Que nadie cambie la arista de la avenida del Centro, el punto 14 ni la flota. Cada vez que cambien `vias.csv`, `puntos.csv`, `vehiculos.csv` o el grafo, hay que repetir este ensayo antes de usar el guion.
4. El video de respaldo, que se graba con este mismo guion apenas corra de punta a punta.
