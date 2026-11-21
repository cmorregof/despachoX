# Cuánto se equivoca el lector de pedidos

Medido por nosotros el 21 de noviembre de 2026 con `evaluacion/lector/evaluar.py`, sobre 330 mensajes sintéticos. Ninguna cifra de este documento viene de mensajes reales.

**Resumen.** El lector por reglas es el que usa el bot sin red y el que contesta los SMS. También es el respaldo cuando el modelo falla. Para saber cuánto se equivoca, lo probamos con pedidos que un generador escribe a partir de registros conocidos y con casos difíciles escritos a mano. Dejó listos sin ningún error 151 de los 300 pedidos generados y 11 de los 30 casos difíciles. Encontró el 97,0 % de los productos pedidos en los 300 generados. En ninguno de los 320 mensajes con pedido el resolvedor propuso con seguridad un lugar equivocado, aunque los lugares de los generados son nombres del nomenclátor. Sus errores se concentran en el lugar, que se lleva las palabras vecinas, en los números dichos en palabras y en los mensajes con dos pedidos. El conjunto lo escribimos nosotros, el mismo equipo que hizo el lector, así que la cifra probablemente es optimista frente a mensajes reales. El extractor con modelo no se midió, porque esta noche no había clave de Anthropic.

## Qué se midió

**El lector.** Con `DESPACHOX_SIN_RED=1`, `Mesa.leer` (`entrada/flujo.py`) limpia el texto con `entrada/privacidad.limpiar` y lo lee con `entrada/sms.leer_sms`, que funciona con reglas y sin modelo. El lugar leído pasa por `lugares.resolver` sin modelo (`elegir=None`), con los tipos que el bot usa para pedidos (barrio, punto, sitio y vereda), sobre una base temporal cargada con `datos/semilla/`. Se midió el código de `main` en el commit `7131261`, del que sale esta rama. A la 1:18 a. m. del 21, `origin/main` (`5b39e49`) daba las mismas 330 lecturas.

**El conjunto.** `conjunto.jsonl` guarda 330 mensajes congelados (sha256 `f3992b4fd8d054c4…`). Los primeros 300 los escribe `generar.py` con la semilla 20261121 a partir de registros conocidos: un lugar del nomenclátor, un conteo, productos del catálogo de `entrada/raciones.py` y una urgencia. El registro es la etiqueta de oro, y el texto se escribe después, como suponemos que lo escribe un comité. Los lugares salen de `lugares_base.csv`, una copia de la semilla del 21 de noviembre, para que un barrio nuevo no cambie el conjunto. Los otros 30 los escribimos a mano en `dificiles.jsonl` para cubrir lo que el generador no produce, por ejemplo negaciones, unidades raras, lugares ambiguos, reportes de vía, códigos de entrega, cancelaciones y correcciones. Ningún mensaje trae nombres, teléfonos ni direcciones de personas; donde hacía falta una firma usamos un cargo.

| Variante | Mensajes | Cómo se escribe |
|---|---|---|
| sms | 30 | El formato enseñado en `docs/SIN_CONEXION.md`, como `PEDIDO 40 SAN JOSE ARROZ LECHE` |
| limpio | 30 | Chat bien escrito, con tildes y puntuación |
| sin_tildes | 30 | Minúsculas, sin tildes y con poca puntuación |
| mayusculas | 30 | Mayúsculas sostenidas |
| abreviaturas | 45 | flias, fams, pers, xfa, porfa, q, x, pa, p, d, b/, brr, bns, grax |
| voz | 60 | Transcripción de una nota de voz: homófonos (arros, aseite, berdura, poyo), números en palabras en el 60 % y palabras partidas o pegadas en el 45 % |
| dos_pedidos | 30 | Dos pedidos de lugares distintos en un mensaje |
| faltan_datos | 45 | 15 sin lugar, 15 sin conteo y 15 sin productos |

En todas las variantes el conteo va en familias (50 %), personas (30 %), niños (7 %), adultos mayores (6 %) o bebés (7 %), y uno de cada cinco es aproximado («como 40»). El 20 % de los pedidos dice que es urgente y el 8 % que puede esperar; el 15 % trae kilos. Esas son probabilidades nominales. Lo que salió en cada mensaje está en sus `etiquetas`, y las proporciones son nuestra suposición de cómo escriben los comités.

**Cómo se califica.** Cada proporción lleva su intervalo de confianza del 95 % de Wilson.

- *Tipo*: pedido, cierre, entrega u otro. Una lectura fallida cuenta como otro, porque el bot la guarda cruda para el despachador. Una cancelación o una corrección de un pedido anterior también es otro, porque leerla como pedido nuevo duplica la demanda. La primera versión del conjunto (`54a5b70f…`) calificaba como pedido la corrección d22, y por eso daba 25 de 30 en el tipo de los difíciles.
- *Lugar extraído*: el texto del lugar sin artículos ni «barrio» o «vereda», igual al del oro.
- *Lugar resuelto*: la clase que da el resolvedor, con las categorías del banco de frases de `lugares/tests` (acierto seguro, por opciones, no sé, error seguro). Un lugar con el mismo punto de entrega que el del oro cuenta como el mismo.
- *Techo del nomenclátor*: lo que daría el resolvedor si el lector copiara el lugar tal como va en el mensaje. Separa lo que pierde el lector de lo que pierde el nomenclátor.
- *Conteo*: familias, personas y bebés, cada uno igual al oro. *Productos*: el conjunto de nombres de bodega, con precisión, exhaustividad y F1 sumadas sobre todos los mensajes. *Cantidades*: los kilos de cada producto que el oro trae con kilos.
- *Abstención*: si al oro le falta el lugar, el conteo o los productos, el lector debe dejar el campo vacío.
- *Dos pedidos*: la lectura se compara con el pedido de oro que mejor le empareja. El otro pedido no entra en los denominadores del lugar, del conteo ni de los productos. Cuenta en «dos pedidos detectados», en «mensaje sin ningún error» y en una fila aparte de exhaustividad, que suma sus productos como no encontrados. `Extraccion` tiene un solo pedido, así que con el esquema actual la detección no puede pasar de cero.
- *Mensaje sin ningún error*: todos los campos bien. El lugar debe quedar en acierto seguro, vacío si el mensaje no lo dice, o sin compromiso si es ambiguo o desconocido.

## Campo por campo

Celdas: aciertos/n (porcentaje; intervalo de Wilson al 95 %). Las tablas completas, con cada etiqueta, están en `tablas.md`.

| Campo | 300 generados | 30 difíciles |
|---|---|---|
| Tipo de mensaje | 299/300 (99,7 %; 98,1 a 99,9) | 24/30 (80,0 %; 62,7 a 90,5) |
| Lugar extraído | 174/285 (61,1 %; 55,3 a 66,5) | 7/20 (35,0 %; 18,1 a 56,7) |
| Lugar resuelto: acierto seguro | 211/285 (74,0 %; 68,6 a 78,8) | 10/16 (62,5 %; 38,6 a 81,5) |
| Lugar resuelto: seguro o entre las opciones | 254/285 (89,1 %; 85,0 a 92,2) | 11/16 (68,8 %; 44,4 a 85,8) |
| Techo del nomenclátor | 245/285 (86,0 %; 81,5 a 89,5) | 15/16 (93,8 %; 71,7 a 98,9) |
| Sin error seguro de lugar | 300/300 (100,0 %; 98,7 a 100,0) | 20/20 (100,0 %; 83,9 a 100,0) |
| Lugar ambiguo o desconocido: no se compromete | no aplica | 4/4 (100,0 %; 51,0 a 100,0) |
| Familias, cuando el oro las trae | 129/153 (84,3 %; 77,7 a 89,2) | 13/17 (76,5 %; 52,7 a 90,4) |
| Personas, cuando el oro las trae | 79/117 (67,5 %; 58,6 a 75,3) | 3/4 (75,0 %; 30,1 a 95,4) |
| Bebés, cuando el oro los trae | 13/15 (86,7 %; 62,1 a 96,3) | 1/1 (100,0 %; 20,7 a 100,0) |
| Conteo exacto (familias, personas y bebés) | 209/285 (73,3 %; 67,9 a 78,1) | 13/19 (68,4 %; 46,0 a 84,6) |
| Error: personas leídas como familias | 19/117 (16,2 %; 10,6 a 24,0) | 0/2 |
| Productos: precisión | 586/646 (90,7 %; 88,2 a 92,7) | 33/35 (94,3 %; 81,4 a 98,4) |
| Productos: exhaustividad | 586/604 (97,0 %; 95,3 a 98,1) | 33/38 (86,8 %; 72,7 a 94,2) |
| Productos: exhaustividad, con el pedido perdido | 586/669 (87,6 %; 84,9 a 89,9) | 33/38 (86,8 %; 72,7 a 94,2) |
| Productos: F1 | 93,8 % | 90,4 % |
| Productos: conjunto exacto | 238/285 (83,5 %; 78,8 a 87,4) | 15/19 (78,9 %; 56,7 a 91,5) |
| Cantidades en kilos | 27/31 (87,1 %; 71,1 a 94,9) | 1/3 (33,3 %; 6,1 a 79,2) |
| Urgencia | 281/300 (93,7 %; 90,3 a 95,9) | 19/20 (95,0 %; 76,4 a 99,1) |
| Dos pedidos detectados | 0/30 (0,0 %; 0,0 a 11,4) | no aplica |
| Abstención: lugar que falta | 8/15 (53,3 %; 30,1 a 75,2) | no aplica |
| Abstención: conteo que falta | 15/15 (100,0 %; 79,6 a 100,0) | 0/1 |
| Abstención: productos que faltan | 15/15 (100,0 %; 79,6 a 100,0) | 1/1 |
| Abstención: kilos que el mensaje no dice | 552/556 (99,3 %; 98,2 a 99,7) | 30/30 (100,0 %; 88,6 a 100,0) |
| Código de entrega | no aplica | 2/3 |
| Cierre detectado | no aplica | 2/3 |
| Mensaje sin ningún error | 151/300 (50,3 %; 44,7 a 56,0) | 11/30 (36,7 %; 21,9 a 54,5) |

**El lugar es el campo que más pierde.** El lector copió el lugar limpio en 174 de 285 pedidos generados. Aun así, el resolvedor ubicó con seguridad 211, porque tolera palabras de más. De los 74 que no quedaron en acierto seguro, 39 los pierde el lector: con el lugar bien copiado, el resolvedor los habría ubicado. Los otros 35 los pierde el nomenclátor, que tampoco los ubica con el texto exacto. En 19 de los 43 que quedaron por opciones, las dos primeras opciones eran el mismo punto de entrega con dos nombres, por ejemplo el barrio Velez y el Albergue temporal Velez. Por eso los albergues, comedores y salones comunales quedan en acierto seguro solo en 6 de 25 pedidos, aunque el lugar correcto está entre las opciones en 24.

**El conteo falla con números en palabras y con personas.** Ningún mensaje con el número en palabras salió con el conteo exacto (0 de 33). En cambio, con el número en cifras y una palabra conocida el conteo sale bien: 118 de 120 en las variantes sms, limpio, sin tildes y mayúsculas. Las palabras «pers» y «abuelitos» no están en el lector, así que 19 de 117 pedidos que daban personas quedaron con ese número como familias. Esto importa porque el bot va a preguntar por personas (`docs/DECISIONES_9PM.md`). Con la regla de `main`, 4 personas por familia, 49 personas leídas como 49 familias piden casi cuatro veces la comida que necesitan (g058).

**Los productos son lo más sólido.** El lector encuentra el 97,0 % de los productos pedidos, y el 90,7 % de los que lista fueron pedidos. Los 60 productos de más de los generados vienen todos de mensajes con dos pedidos, donde junta los de los dos lugares. Los 18 que faltan vienen todos de la voz, por homófonos que no reconoce. Esa exhaustividad se calcula sobre los pedidos emparejados. Si se cuentan también los 65 productos del pedido que se pierde en los mensajes con dos pedidos, quedan en el pedido que les corresponde 586 de 669 (87,6 %).

**Cuando falta un dato, no inventa conteos ni productos** (15 de 15 en cada caso). En cambio, cuando falta el lugar, llena el campo con otra cosa en 7 de 15 («quedamos atentos», «muchas», «mil»). El resolvedor no propuso ninguno con seguridad, pero sí ofreció opciones equivocadas, como Los Agustinos para «quedamos atentos» o Milán para «mil». Quien escribió tendría que rechazarlas y dar el lugar.

## Por variante

| Variante | n | Lugar resuelto | Conteo exacto | F1 productos | Sin ningún error (IC 95 %) |
|---|---|---|---|---|---|
| sms | 30 | 23/30 | 30/30 | 100,0 % | 23/30 (76,7 %; 59,1 a 88,2) |
| limpio | 30 | 18/30 | 30/30 | 100,0 % | 16/30 (53,3 %; 36,1 a 69,8) |
| sin_tildes | 30 | 24/30 | 29/30 | 100,0 % | 22/30 (73,3 %; 55,6 a 85,8) |
| mayusculas | 30 | 26/30 | 29/30 | 100,0 % | 24/30 (80,0 %; 62,7 a 90,5) |
| abreviaturas | 45 | 40/45 | 28/45 | 100,0 % | 24/45 (53,3 %; 39,1 a 67,1) |
| voz | 60 | 32/60 | 26/60 | 92,9 % | 13/60 (21,7 %; 13,1 a 33,6) |
| dos_pedidos | 30 | 26/30 | 9/30 | 68,4 % | 0/30 (0,0 %; 0,0 a 11,4) |
| faltan_datos | 45 | 22/30 | 28/30 | 100,0 % | 29/45 (64,4 %; 49,8 a 76,8) |

El formato enseñado por SMS sale bien en todo lo que depende del lector: tipo, lugar extraído, conteo y productos en 30 de 30. Los 7 que no quedan sin errores son lugares que el resolvedor deja por opciones, como Bajo Prado frente a El Prado o un albergue frente a su barrio. La voz es la variante más difícil, con 13 de 60 sin errores. Con 30 mensajes por variante los intervalos son anchos; por ejemplo, los de limpio y sin tildes se traslapan, así que esa diferencia no muestra que escribir bien empeore la lectura.

**Tiempo.** Leer un mensaje toma 1,03 ms de mediana (p95 2,21 ms) y resolver su lugar sin modelo 34,5 ms (p95 74,0 ms). Son las cifras de la corrida versionada (`resultados.json`), en un Mac arm64 (Darwin 25.5.0) con Python 3.12.13, sin red, sobre los 330 mensajes. El tiempo depende de la carga de la máquina. En otras corridas de esa noche en la misma máquina, que no quedaron guardadas, la mediana fue de 0,94 a 1,16 ms para leer y de 31,5 a 37,8 ms para el lugar.

## Errores típicos, con ejemplos del conjunto

1. **El lugar se lleva las palabras vecinas.** `_lugar` (`entrada/sms.py:108-119`) toma el tramo más largo de palabras que no clasificó. De los 111 lugares mal extraídos en los generados, 78 contienen el lugar con palabras de más y 32 son otro tramo del mensaje. Las que más se cuelan son «necesitan» y «Dios les pague» (13 veces cada una), «comité … pide» (12) y «quedamos atentos» (11). Por ejemplo, en g021 («Acá en barrio Villanueva somos unas 66 personas y nos falta panela, no hay afán, podemos esperar.») el lugar leído es «afan podemos». En g294 («…el comité de el barrio Portal de los Alcázares pide agua potable…») es «el comite de el barrio portal de los alcazares pide», que el resolvedor deja por opciones.
2. **Números en palabras.** En g030 («…para ciento siete personas en el barrio Fátima.») el conteo queda vacío y el lugar leído es «ciento siete».
3. **Personas leídas como familias.** «pers» aparece en 14 de los 19 casos y «abuelitos» en 5, porque no están en `PERSONAS` (`entrada/sms.py:40-41`). En g058 («en brr la macarena 49 pers…») salen 49 familias.
4. **Homófonos de la voz.** El parecido mínimo de 0,84 y el largo mínimo de 5 letras (`entrada/sms.py:101-104`) dejan por fuera «arros» (0,80), «aseite» (0,83) y «poyo» (4 letras), aunque «berdura» sí pasa. Cuando un producto no se reconoce, además, su palabra puede terminar en el lugar.
5. **Dos pedidos en uno.** En g036 («…barrio delicias hay 34 familias sin agua potable huevos y en malhabar somos 195 personas sin verdura…») sale un solo pedido con 34 familias, 195 personas y la verdura de Malhabar; el pedido de Malhabar se pierde.
6. **Negaciones.** En d01 («no necesitamos arroz, si leche y panela…») el arroz entra al pedido, y en d03 («no es urgente, pueden traerlo mañana…») la urgencia sale 3.
7. **Mensajes que no son pedidos.** Los cinco difíciles de este tipo se leyeron como un reporte. La pregunta de d15 («a que hora pasa el camion de la ayuda por la enea?») quedó como cierre. La cancelación de d21, la corrección de d22, la pregunta por un pedido anterior de d25 y el agradecimiento de d26 («gracias, ya recibimos los 30 mercados en aranjuez…») quedaron como pedidos nuevos. La corrección («perdon, me equivoque: eran 25 familias, no 40, en villa julia») crea un pedido de 25 familias que se suma al de 40, y el agradecimiento crea uno de 30.
8. **Números que no son familias.** En d09 («barrio 20 de julio, 15 familias sin agua») salen 20 familias, en d04 («2 bultos de arroz…») 2 familias y en d24 («50 kilos de arroz, 20 de frijol…») 20 familias. Los kilos dichos después del producto van al producto siguiente: en g204 («pedimos agua 5 kilos y huevos») los 5 kilos quedan en los huevos.
9. **Urgencia por personas vulnerables.** `VULNERABLES` incluye «enfermos» (`entrada/sms.py:46`), pero la línea 188 solo la revisa para palabras de `BEBES | PERSONAS`, así que nunca se activa. Tampoco reconoce «abuelitos». Con una mención de vulnerables sin número, la urgencia sale bien en 14 de 22 pedidos.
10. **Código de entrega dictado.** d17 («entregado de equis siete ka cu tres») no se lee y va crudo al despachador. Los códigos escritos (d16 y d18) salen bien.

## Lo que el lector hace bien

- El formato enseñado por SMS se lee completo en lo que le toca al lector, sin un solo error de tipo, conteo o productos en 30 mensajes.
- Encuentra casi todos los productos (586 de 604) y no inventa kilos (552 de 556 sin kilos quedaron sin kilos).
- No inventa conteos ni productos cuando faltan, y deja el código de entrega escrito tal como es.
- Con el resolvedor detrás, nunca propuso con seguridad un lugar equivocado en los 320 mensajes con pedido. Cuando duda, ofrece opciones o pide la ubicación, y el lugar lo confirma una persona. Los lugares de los generados son nombres del nomenclátor, así que esto no dice qué pasa con un nombre que el nomenclátor no tiene.
- Ni las tildes ni las mayúsculas lo afectan, y los emojis tampoco (d20 sale sin errores).
- Es rápido y no depende de la red, así que sirve en el acopio aislado.

## Arreglos que le proponemos a Samuel

No editamos `entrada/` ni `lugares/`. Cada arreglo se puede medir otra vez con `python -m evaluacion.lector.evaluar --salida "$(mktemp -d)"`; no adelantamos cifras.

1. `entrada/sms.py:108-119`. Elegir el tramo de lugar por su puntaje en el nomenclátor (`lugares.nomenclator.buscar`) en vez de por su largo, y sumar a `RELLENO` las fórmulas de cortesía y los verbos que más se cuelan (dios, les, pague, quedamos, atentos, mil, muchas, necesitan, pide, comite, afan, podemos).
2. `entrada/sms.py:168-185`. Leer números en palabras, de «uno» a «novecientos noventa y nueve», antes de clasificar.
3. `entrada/sms.py:40-41` y `46`. Añadir «pers», «abuelitos» y «embarazadas» a `PERSONAS`, y «abuelitos» a `VULNERABLES`. Revisar también la línea 188, que solo consulta `VULNERABLES` para las palabras de `BEBES | PERSONAS`; por eso «enfermos» nunca sube la urgencia. «Adultos mayores» ya funciona, porque el lector compara palabra por palabra y las dos palabras están en `PERSONAS`.
4. `entrada/sms.py:101-104` o `entrada/raciones.py`, `SINONIMOS`. Igualar s, z y c, b y v, y ll e y antes de comparar productos, o poner «arros», «aseite» y «poyo» como sinónimos.
5. `entrada/sms.py:170-173` y `222-223`. Si un producto ya trae kilos, leer «20 de frijol» como kilos y no como familias, y asignar los kilos dichos después de un producto a ese producto.
6. `entrada/sms.py:174-179`. No tomar como familias un número que es parte de un lugar conocido («20 de julio») ni uno seguido de bulto, arroba, libra o paca.
7. `entrada/sms.py:190-191` y `202-208`. Una regla mínima de negación: «no es urgente» no sube la urgencia, y un producto después de «no necesitamos» o «ya nos llegó» no se pide.
8. `entrada/sms.py:225-232`. Dejar como `otro`, para el despachador, los mensajes que cancelan («cancelen»), corrigen un pedido anterior («me equivoque»), agradecen una entrega («ya recibimos») o preguntan («cuando llega», «?»), en vez de crear un pedido nuevo.
9. `entrada/extraer.py:57-75`. `Extraccion` tiene un solo pedido. Mientras tanto, el lector puede anotar en `dudas` que parece haber dos pedidos, para que el despachador los separe.
10. **Probable error con el modelo activo.** `entrada/flujo.py:102-107`. `Mesa.leer` solo usa las reglas si el modelo falla, y `Lectura` (`entrada/extraer.py:57-65`) no tiene campo para el código de entrega. Probamos ese camino con un extractor falso que responde «otro», que es lo único que el esquema permite para un mensaje que no es pedido ni cierre. Con «ENTREGADO DX-4MQ7», el bot contestó «No entendí» y el paquete siguió en ruta; con las reglas quedó entregado. Falta ver qué devuelve el modelo real, porque no había clave. La propuesta es que `Mesa.leer` pruebe primero `leer_sms` y devuelva su lectura si trae `entregado`.
11. **Para fusionar `samuel-bot`.** Corrimos el mismo conjunto contra `origin/samuel-bot` (commit `aff5bcb`; desde `8bb5313` no cambió el código que lee), que amplía el catálogo con atún, azúcar, café, pasta, sal, chocolate y papa. El difícil d28 («atun, azucar y cafe») pasa a salir bien. En cambio, «café» rompe el barrio Villa Café: g101, g296 y g298 salían bien y ahora dan el lugar «villa» y un café que nadie pidió. Los generados sin errores bajan de 151 a 148 y los difíciles suben de 11 a 12. Conviene que una palabra que forma parte de un lugar conocido no se lea como producto.
12. **Para quien lleva `lugares/`.** En `buscar()` (`lugares/nomenclator.py:116-119`), fusionar los candidatos que comparten `punto_id`. Así el barrio y su albergue dejarían de competir entre sí, que es lo que pasa en 19 de los 43 pedidos por opciones.

## Otras ramas de la noche

Corrimos el mismo conjunto, sin cambiarlo, contra el código de dos ramas que tocan el lector. Ninguna se fusionó; el código se copió a una carpeta temporal. Las cifras son las del conjunto actual, con d22 calificado como otro.

| Rama (commit) | Generados sin errores | Difíciles sin errores | Mensajes con otra lectura |
|---|---|---|---|
| `main` (`7131261`, lo medido aquí; `5b39e49` da lo mismo) | 151/300 | 11/30 | |
| `samuel-bot` (`aff5bcb`) | 148/300 | 12/30 | 4: g101, g296 y g298 empeoran por «café» en Villa Café; d28 mejora |
| `qa-noche` (`ca195b4`) | 151/300 | 11/30 | ninguno |

Los cambios de `qa-noche` en `entrada/sms.py` y `entrada/privacidad.py` no cambian ninguna lectura de los 330. Los de `samuel-bot` están descritos en el arreglo 11.

## El extractor con modelo

No se midió. Esta noche no había `ANTHROPIC_API_KEY` y no se llamó a la API. `medir_modelo.py` queda listo: lee cada mensaje como el bot con red (modelo y, si falla, reglas), con un tope duro de 330 llamadas y sin reintentos, para que cada llamada sea una sola petición. Sin `--confirmo-gasto` solo dice qué haría. Recibe `--conjunto` y `--salida` igual que `evaluar.py`. Con los supuestos de `entrada/ESCALA.md`, el costo estimado de las 330 llamadas va de 0,06 a 0,15 USD. La única medición previa del modelo es la del equipo sobre sus 15 mensajes de ejemplo (62 de 64 campos, `entrada/pruebas/reporte_campos.md`), que no se puede comparar con esta porque los mensajes y los campos son otros.

## Salvedad

**La cifra probablemente es optimista.** El conjunto es sintético y lo hicimos nosotros, el mismo equipo que escribió el lector. Quien escribió el generador había leído antes el código del lector. Las plantillas, las abreviaturas y las proporciones de cada variante son nuestra suposición de cómo escriben los comités, y no tuvimos un solo mensaje real de referencia. Los mensajes reales traerán palabras, lugares y formas de contar que no imaginamos. Los lugares de los 300 generados son nombres del nomenclátor, escritos tal cual salvo tildes, mayúsculas y el ruido de la voz. Por eso el cero de errores seguros de lugar no dice qué pasa con los nombres que la gente usa y el nomenclátor no tiene. La voz, además, está simulada sobre texto, de modo que el conjunto no mide la transcripción. Algunas variantes difíciles pesan aquí más que en la realidad, como los dos pedidos en el 10 % de los mensajes, y el total mezcla situaciones distintas. Por eso reportamos cada variante por separado.

## Cómo medirlo con mensajes reales en el piloto

1. **Autorización.** Solo se miden los mensajes de quienes dijeron que sí. Cuando el pedido ya quedó registrado, el bot hace una pregunta aparte: si ese mensaje, sin datos personales, se puede usar para medir qué tan bien lo lee el sistema. La pregunta dice que la ayuda llega igual con cualquier respuesta y que el permiso se puede retirar después. Va separada del pedido porque quien pide comida después de un sismo no está en condiciones de negarse si cree que la ayuda depende de su respuesta. Solo cuenta un SÍ explícito, que se guarda con la fecha y la versión de la pregunta, y quien no contesta queda fuera. La Ley 1581 de 2012 (art. 9) pide autorización previa e informada, y el Decreto 1074 de 2015 (art. 2.2.2.25.2.4, que viene del art. 7 del Decreto 1377 de 2013) dice que «en ningún caso el silencio podrá asimilarse a una conducta inequívoca». Si además se corre `medir_modelo.py`, cada texto lo lee el modelo de Anthropic, un tercero, y la pregunta tiene que decirlo. Por SMS va la misma pregunta en la respuesta, para contestar SI o NO. El texto final se cruza con `docs/PRIVACIDAD.md` (rama `n2-privacidad`) y lo revisan el aliado y su abogado.
2. **Muestra.** En los primeros 30 días, 210 mensajes al azar entre los autorizados, 70 por canal (texto de chat, notas de voz transcritas y SMS). Con 210 mensajes, el intervalo de Wilson de una proporción cercana al 50 % mide unos 7 puntos hacia cada lado, y unos 11 con los 70 de un canal. Quien autoriza puede escribir distinto de quien no, así que se reporta también qué parte de los mensajes quedó autorizada.
3. **Anonimización.** `privacidad.limpiar` y una revisión a mano antes de etiquetar. Los textos se quedan en el equipo del aliado y no entran al repositorio; al repositorio solo llegan las cifras.
4. **Oro.** Dos personas del Banco o de la UGR etiquetan cada mensaje por separado, con los campos de `conjunto.jsonl` y sin ver la lectura del sistema. Una tercera resuelve los desacuerdos, y se reporta cuánto coincidieron las dos primeras.
5. **Corrida.** `python -m evaluacion.lector.evaluar --conjunto <archivo> --salida <carpeta>` para las reglas y `python -m evaluacion.lector.medir_modelo --conjunto <archivo> --salida <carpeta> --confirmo-gasto` para el modelo. Con un conjunto que no sea el congelado, los dos scripts exigen `--salida` y se niegan a escribir dentro del repositorio, porque `lecturas.jsonl` copia cada texto. Se reporta la misma tabla por canal, junto a esta cifra sintética.

## Cómo reproducir

```bash
export DESPACHOX_SIN_RED=1 PYTHONPATH=.                      # desde la raíz del repositorio
python evaluacion/lector/generar.py --verificar             # la parte generada sale igual, byte a byte
python -m evaluacion.lector.evaluar --salida "$(mktemp -d)"  # no toca la corrida versionada
python -m pytest evaluacion/lector/tests -q                 # 24 pruebas, un par de segundos
```

Sin `--salida`, `evaluar.py` rehace la corrida versionada (`resultados.json`, `lecturas.jsonl` y `tablas.md`), y al menos la fecha y los tiempos cambian. Se corre así solo cuando se quiere actualizar esa corrida. La base de lugares vive en una carpeta temporal que se borra al terminar.

Para medir otra rama sin fusionarla, como se hizo con `samuel-bot` y `qa-noche`:

```bash
T=$(mktemp -d)
git archive origin/samuel-bot entrada lugares datos despacho/__init__.py despacho/paquetes.py | tar -x -C "$T"
mkdir -p "$T/evaluacion/lector" && cp evaluacion/lector/*.py evaluacion/lector/conjunto.jsonl \
  evaluacion/lector/dificiles.jsonl evaluacion/lector/lugares_base.csv "$T/evaluacion/lector/"
(cd "$T" && DESPACHOX_SIN_RED=1 PYTHONPATH="$T" python -m evaluacion.lector.evaluar --salida "$T/salida")
```

| Archivo | Qué es |
|---|---|
| `generar.py` | Generador de los 300 pedidos, con la semilla y la mezcla de variantes en su cabecera |
| `lugares_base.csv` | Copia congelada de los 157 lugares de pedido de `datos/semilla/` que usa el generador |
| `dificiles.jsonl` | Los 30 casos escritos a mano, con su nota |
| `conjunto.jsonl` | Los 330 mensajes congelados con su oro, su origen y lo que les falta a propósito |
| `.gitattributes` | Fija el fin de línea LF en los `.jsonl` y `.csv` de esta carpeta, para que la comparación byte a byte también pase en un clon de Windows |
| `evaluar.py` | La medición campo por campo |
| `medir_modelo.py` | La medición del extractor con modelo, con tope de 330 llamadas; no se ha corrido |
| `resultados.json`, `lecturas.jsonl`, `tablas.md` | La corrida versionada del 21 de noviembre: métricas, lectura de cada mensaje y tablas |
| `tests/` | Pruebas del generador, de las métricas, de la carpeta de salida y del tope del modelo |

## Para el pitch (por aprobar)

Las frases usan el código de `main` y los 330 mensajes juntos, que están en `resultados.json` como grupo `todos`. Salieron sin ningún error 162 de 330 (49,1 %; IC 95 % de 43,7 a 54,5). Se encontraron 619 de 642 productos (96,4 %; 94,7 a 97,6), y no hubo ningún error seguro de lugar en los 320 mensajes con pedido. Si se cuentan como no encontrados los productos del pedido que se pierde en los mensajes con dos pedidos, la cifra de productos baja a 619 de 707 (87,6 %). Con `samuel-bot` fusionado quedan 160 de 330 sin errores y 622 de 642 productos (96,9 %), así que la primera frase diría «el 97 %». Al aprobarlas, se anotan en `docs/FUENTES.md` con tipo M, medido por nosotros; esta rama no toca ese archivo.

- «Probamos el lector sin internet con 330 mensajes de prueba que escribimos nosotros. Casi la mitad salió sin ningún error. Encontró el 96 % de los productos pedidos y no ubicó con seguridad ningún pedido en un lugar equivocado.» **Por aprobar.**
- «Donde más se equivoca es en el texto de las notas de voz, que simulamos, y en los mensajes con dos pedidos. Por diseño, el lugar lo confirma una persona y el despachador aprueba cada plan antes de despachar.» **Por aprobar.**
