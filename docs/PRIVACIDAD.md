# Datos personales en DespachoX

**Borrador para revisión de un abogado.** Sábado 21 de noviembre de 2026. Lo escribió la sesión Noche-2 (agente `n2-privacidad`) entre las 12:02 y las 12:31 a. m., y otro agente lo corrigió entre la 1:00 y la 1:30 a. m. después de una revisión independiente. Sirve para que el equipo responda la pregunta del jurado sobre datos personales. No es un concepto jurídico y ningún abogado lo ha revisado todavía.

El documento separa lo que dice la norma de lo que hace el código y de lo que proponemos. Cada afirmación lleva una de estas marcas:

| Marca | Qué significa |
|---|---|
| **[N]** | Lo dice la norma. Va con el artículo y la fuente oficial de la sección 10. |
| **[C]** | Lo hace el código hoy. Va con archivo y línea. |
| **[P]** | Lo proponemos. No está programado y no es una obligación citada. |
| **[I]** | Inferencia nuestra sobre cómo se aplica la norma. La decide el abogado. |
| **[F]** | Tomado de la página oficial de un proveedor o de un documento del equipo, con su referencia. |
| **[M]** | Medido por nosotros esta noche. |
| **[pendiente]** | Falta el dato y no lo vamos a suponer. |

Las líneas de código citadas son del commit `7131261`, que es `main` del 20 de noviembre a las 11:50 p. m. A la 1:07 a. m. del 21, `origin/main` (`5b39e49`) tenía el mismo código en `entrada/`, `datos/`, `lugares/`, `despacho/`, `tablero/` y `despliegue/`, y el mismo `README.md`. Si se fusionan `qa-noche` o `samuel-bot`, algunas líneas de `entrada/` se corren unas pocas posiciones.

El producto puede pasar a llamarse Convite, un nombre que Carlos aún no confirma (`torre/CANAL.md`, 23:30). Por eso los textos para el usuario de la sección 7 escriben `{producto}`.

---

## 1. La respuesta para el jurado

La pregunta probable es «¿qué hacen con los datos de la gente que pide ayuda?». La respuesta tiene 85 palabras [M], y todo lo que afirma está en el código o marcado como propuesta:

> Pedimos solo qué falta, para cuántas familias y dónde. Antes del modelo y de la base, el sistema quita lo que parece teléfono, cédula o correo, y el nombre que sigue a «me llamo». Es una heurística y deja pasar direcciones y nombres sueltos. Cada chat queda como un código y no guardamos el audio. En el piloto, el Banco de Alimentos es el responsable y nosotros sus encargados. Antes de datos reales faltan el borrado a los 30 días y la clave del tablero.

Si el jurado sigue preguntando, estas son las respuestas cortas, con la sección donde está el detalle:

| Pregunta | Respuesta corta | Sección |
|---|---|---|
| ¿Y si el filtro falla? | Es una heurística y lo decimos. En once mensajes de prueba quitó dos celulares, una cédula, un correo y los nombres que seguían a «me llamo», «soy» y «llamen a». Dejó pasar dos direcciones con calle y número, nombres después de «doña», «la señora», «la familia» y «atte.», un nombre en minúscula después de «soy», un fijo de siete dígitos escrito con un espacio y un «abuelo diabético». Por eso proponemos borrar el texto a los 30 días y ponerle clave al tablero. | 3.1 y 4 |
| ¿Piden autorización? | Hoy el `/start` solo pide no escribir nombres, cédulas ni teléfonos (`entrada/flujo.py:49`). Proponemos que además informe quién trata los datos y para qué, y que el envío del pedido cuente como conducta inequívoca, una forma de autorización que el decreto acepta. Para los datos de salud, la ley pide autorización explícita, y esa pregunta va al abogado. También falta guardar la prueba de qué aviso vio cada chat. | 2.2, 6, 7 y 9 |
| ¿Los datos salen del país? | Sí. El texto limpio va a la API de Anthropic y el audio al servicio de transcripción, que sería Groq. Las dos son empresas con sede en Estados Unidos. Falta saber en qué país procesa cada una [pendiente]. De Groq sabemos que lo que retiene queda en Google Cloud, en Estados Unidos. La base de la nube vive en la región de Railway que se haya elegido, también [pendiente]. La norma permite enviarlos a un encargado con contrato, y la SIC incluye a Estados Unidos entre los países con nivel adecuado. | 5 |
| ¿Quién responde por los datos? | Hoy, en la demostración, el equipo. La base de la nube tiene la semilla sintética y los mensajes de quienes prueban el bot, y unos y otros se ven en el tablero público (`README.md:112-113`). En el piloto, el Banco como responsable y el equipo como encargado. Si el piloto pasa al flujo de la UGR y la UGR es una dependencia de la Alcaldía, el responsable sería el Municipio de Manizales, quizá junto con la Gobernación de Caldas [I]. | 5 y 9 |
| ¿Cómo borra alguien lo que envió? | Proponemos el comando `/borrar` en el chat y la palabra `BORRAR` por SMS. Hoy no existe, y lo único que hay es el reinicio de la base entera. | 4 y 7 |
| ¿Y los datos de niños o de salud? | No se piden. El bot cuenta bebés y niños para calcular raciones, sin identificar a nadie. Si alguien escribe datos de salud, quedan en el texto hasta que se borre. Por eso el `/start` propuesto pide no escribirlos, y le preguntamos al abogado qué exige la ley para los que llegan sin pedirlos. | 3.1, 6, 7 y 9 |
| ¿El modelo decide algo? | No. Lee y estructura. El lugar lo confirma la persona o el despachador, y el plan lo aprueba el despachador. | 3.1 |
| ¿Qué pasa con la voz? | El bot descarga la nota a su memoria, la envía al servicio de transcripción y no la escribe en disco ni en la base. Lo que se guarda es la transcripción limpia. El servicio puede guardar el audio hasta 30 días si no se activa la retención cero, y Telegram conserva la nota en el chat. | 3.2 |
| ¿Qué lleva el QR? | Solo un código de cuatro signos, como `DX-7KQ3`. La hoja de ruta lleva el punto de entrega, los productos y una línea para la firma de quien recibe. | 3.4 |

---

## 2. Qué dice la norma

El marco es la Ley Estatutaria 1581 de 2012 y su reglamento, el Decreto 1377 de 2013. Ese decreto está hoy compilado en el Capítulo 25 del Decreto 1074 de 2015, Decreto Único Reglamentario del Sector Comercio, Industria y Turismo. En el texto de la Función Pública, cada artículo del Capítulo 25 cierra con la nota del artículo del 1377 de donde viene. Aquí se cita el número del 1074 y, entre paréntesis, el del 1377. En esta sección, las frases entre comillas son copia textual de la norma.

### 2.1 Definiciones y principios

| Tema | Norma [N] | Qué dice | Qué implica para DespachoX |
|---|---|---|---|
| Dato personal | Ley 1581, art. 3 c) | Información «vinculada o que pueda asociarse a una o varias personas naturales determinadas o determinables» | El código del chat, el texto del pedido y una ubicación enviada desde una casa son datos personales mientras se puedan asociar a alguien [I] |
| Responsable | Ley 1581, art. 3 e) | Quien, «por sí misma o en asocio con otros», decide sobre la base de datos o el tratamiento | En el piloto, el Banco o la UGR (sección 5) |
| Encargado | Ley 1581, art. 3 d) | Quien realiza el tratamiento «por cuenta del Responsable» | El equipo y sus proveedores (sección 5) |
| Tratamiento | Ley 1581, art. 3 g) | Cualquier operación sobre datos personales, como recolección, almacenamiento, uso, circulación o supresión | Transcribir, leer con el modelo, guardar, mostrar en el tablero y borrar son tratamiento |
| Finalidad y libertad | Ley 1581, art. 4 b) y c) | La finalidad debe ser legítima e informada; el tratamiento requiere consentimiento previo, expreso e informado, salvo mandato legal | Base del aviso del `/start` (sección 7) |
| Circulación restringida | Ley 1581, art. 4 f) | Los datos no públicos no pueden estar en Internet, «salvo que el acceso sea técnicamente controlable» | El tablero de la nube no tiene clave. Con datos reales, eso choca con este principio [I] (sección 4) |
| Seguridad y confidencialidad | Ley 1581, art. 4 g) y h) | Medidas técnicas, humanas y administrativas contra adulteración, pérdida o acceso no autorizado; reserva aun después de terminar la labor | Sal fuera del repositorio, registros sin contenido, clave del tablero y cláusula de confidencialidad |
| Recolección mínima | Decreto 1074, art. 2.2.2.25.2.1 (1377, art. 4) | Solo los datos pertinentes y adecuados para la finalidad | Respalda no pedir nombres, cédulas ni teléfonos |
| Datos sensibles | Ley 1581, arts. 5 y 6; Decreto 1074, art. 2.2.2.25.2.3 (1377, art. 6) | Los datos de salud y los biométricos son sensibles y su tratamiento está prohibido salvo excepciones. La primera es que el titular haya dado su «autorización explícita» (art. 6 a). Hay que informar que no es obligatorio darlos, y «ninguna actividad podrá condicionarse» a que se den | No se piden. El texto libre puede traerlos («niños enfermos»), y la conducta inequívoca de la sección 6 no alcanza para ellos [I] (sección 9) |
| Niños, niñas y adolescentes | Ley 1581, art. 7; Corte Constitucional, C-748 de 2011; Decreto 1074, art. 2.2.2.25.2.9 (1377, art. 12) | El tratamiento está proscrito salvo datos públicos. La Corte lo declaró exequible si el tratamiento respeta el interés superior y no pone en riesgo la prevalencia de sus derechos | El bot cuenta bebés y niños como cifras para las raciones, sin identificarlos [I] |

### 2.2 Autorización, derechos y plazos

| Tema | Norma [N] | Qué dice | Qué implica para DespachoX |
|---|---|---|---|
| Autorización | Ley 1581, art. 9; Decreto 1074, arts. 2.2.2.25.2.2 y 2.2.2.25.2.4 (1377, arts. 5 y 7) | Previa e informada, a más tardar al recoger el dato. Vale por escrito, de forma oral o por conductas inequívocas. «En ningún caso el silencio podrá asimilarse a una conducta inequívoca» | El aviso va en el `/start`, antes del primer pedido (sección 6) |
| Prueba de la autorización | Ley 1581, art. 12, parágrafo; Decreto 1074, arts. 2.2.2.25.2.5 y 2.2.2.25.3.4 (1377, arts. 8 y 16) | El responsable conserva la prueba y el modelo del aviso que usó | Hoy no se registra qué aviso vio cada chat (sección 4) |
| Casos sin autorización | Ley 1581, art. 10 | Lista cerrada: información pedida por una entidad pública en ejercicio de sus funciones, datos públicos, urgencia médica o sanitaria, fines históricos, estadísticos o científicos, y registro civil | No proponemos apoyarnos en la urgencia (sección 6) |
| Deber de informar | Ley 1581, art. 12 | Informar el tratamiento y su finalidad, que es facultativo responder sobre datos sensibles o de niños, los derechos del titular y la identificación, dirección y teléfono del responsable | Contenido de `/privacidad` (sección 7.3) |
| Política y aviso de privacidad | Decreto 1074, arts. 2.2.2.25.3.1 a 2.2.2.25.3.3 (1377, arts. 13 a 15) | Política escrita en lenguaje claro, con contacto del responsable, finalidad, derechos y procedimiento. El aviso de privacidad tiene un contenido mínimo y debe decir cómo consultar la política | El Banco necesita su política; el bot, su aviso |
| Derechos del titular | Ley 1581, art. 8; Decreto 1074, art. 2.2.2.25.2.6 (1377, art. 9) | Conocer, actualizar, rectificar, pedir prueba de la autorización y pedir la supresión. Según el decreto, la supresión se puede pedir en todo momento, salvo un deber legal o contractual de permanecer en la base. Responsable y encargado deben ofrecer «mecanismos gratuitos y de fácil acceso» para pedirla | `/estado` cubre parte del derecho a conocer; falta `/borrar` |
| Consultas y reclamos | Ley 1581, arts. 14 y 15 | Consultas en 10 días hábiles, prorrogables 5. Reclamos en 15 días hábiles, prorrogables 8. Quien recibe un reclamo sin ser competente lo traslada en 2 días hábiles | Plazos del contrato (sección 8, cláusula 10) |
| Persona o área de datos | Decreto 1074, art. 2.2.2.25.4.4 (1377, art. 23) | Responsable y encargado designan una persona o área que tramite las solicitudes | El Banco designa la suya y el equipo un contacto del encargado [P] |
| Límite de tiempo | Decreto 1074, art. 2.2.2.25.2.8 (1377, art. 11) | Se tratan los datos solo «durante el tiempo que sea razonable y necesario». Cumplida la finalidad, se suprimen, y los procedimientos de conservación y supresión se documentan | Hoy no hay plazo ni borrado (sección 4) |

### 2.3 Deberes, transmisión y vigilancia

| Tema | Norma [N] | Qué dice | Qué implica para DespachoX |
|---|---|---|---|
| Deberes del responsable | Ley 1581, art. 17 | Entre otros, garantizar el hábeas data, conservar la autorización, guardar la información con seguridad, entregarle al encargado solo datos autorizados, exigirle seguridad, tramitar reclamos, tener un manual interno e informar a la SIC los incidentes | Lo asume el Banco o la UGR |
| Deberes del encargado | Ley 1581, art. 18 | Entre otros, seguridad, suprimir a tiempo, tramitar consultas y reclamos, dar acceso solo a quien puede tenerlo e informar a la SIC los incidentes. Si una persona es a la vez responsable y encargada, responde por los dos grupos de deberes | Lo asume el equipo |
| Transferencia y transmisión | Decreto 1074, art. 2.2.2.25.1.3, num. 4 y 5 (1377, art. 3) | Hay transferencia cuando el receptor es otro responsable. Hay transmisión cuando el receptor trata los datos como encargado, por cuenta del responsable | Anthropic, Groq y Railway reciben datos como encargados [I] |
| Transmisión internacional | Decreto 1074, arts. 2.2.2.25.5.1 y 2.2.2.25.5.2 (1377, arts. 24 y 25) | Las transmisiones internacionales entre responsable y encargado «no requerirán ser informadas al Titular ni contar con su consentimiento» si hay un contrato de transmisión. El contrato obliga al encargado, como mínimo, a tratar los datos según los principios, a cuidar su seguridad y a guardar confidencialidad | Contrato con el Banco y acuerdos con cada proveedor (secciones 5 y 8) |
| Transferencia a otro país | Ley 1581, art. 26 | Prohibida hacia países sin nivel adecuado de protección, salvo excepciones como la autorización expresa e inequívoca del titular | Aplica si algún receptor actuara como responsable |
| Países con nivel adecuado | SIC, Circular Única, Título V, num. 3.2 (versión de septiembre de 2017) | La lista incluye a Estados Unidos y a los Países Bajos. El parágrafo cuarto permite la transmisión a esos países con las reglas de la transferencia. El parágrafo tercero aclara que «el simple tránsito transfronterizo de datos no comporta una transferencia» | Singapur no está en esa versión. Hay que confirmar si hay una lista más reciente [pendiente] |
| Responsabilidad demostrada | Decreto 1074, art. 2.2.2.25.6.1 (1377, art. 26) | El responsable debe poder demostrarle a la SIC medidas apropiadas y efectivas, proporcionales a los datos y a sus riesgos | Este documento es el comienzo de esa evidencia |
| Registro Nacional de Bases de Datos | Decreto 1074, art. 2.2.2.26.1.2 (Decreto 886 de 2014, modificado por el Decreto 90 de 2018) | Inscriben sus bases las sociedades y entidades sin ánimo de lucro con activos totales superiores a 100.000 UVT y las «personas jurídicas de naturaleza pública» | Si la UGR es una dependencia de la Alcaldía, la persona jurídica que inscribe sería el Municipio de Manizales [I] (sección 9). El Banco depende de sus activos [pendiente] |
| Incidentes de seguridad | Ley 1581, arts. 17 n) y 18 k); SIC, Circular Única, Título V, capítulo segundo, reporte de novedades | Responsable y encargado informan a la SIC. El incidente se reporta al Registro dentro de los 15 días hábiles siguientes a su detección | Cláusula 11 del contrato |
| Inteligencia artificial | SIC, Circular Externa 002 del 21 de agosto de 2024 | La Ley 1581 se aplica a cualquier tecnología. Pide ponderar idoneidad, necesidad, razonabilidad y proporcionalidad, gestionar riesgos, hacer un «estudio de impacto de privacidad» cuando el riesgo sea alto y adoptar medidas de seguridad auditables | La sección 3 describe las operaciones; falta el estudio formal [pendiente] |
| Sanciones | Ley 1581, art. 23 | A responsables y encargados privados, multas de hasta 2.000 salarios mínimos mensuales y suspensión o cierre de operaciones. A una autoridad pública, la SIC la remite a la Procuraduría | Por eso el contrato reparte deberes por escrito |

**La emergencia no suspende la ley [I].** La única excepción que encontramos fue expresa y temporal. La Secretaría del Senado anota que, durante la emergencia sanitaria por el COVID-19, el Decreto Legislativo 538 de 2020 redujo lo que el principio de seguridad les exigía a los prestadores de salud. No vimos ninguna norma parecida para el sismo del 10 de agosto, aunque no la buscamos a fondo.

---

## 3. Qué pasa con los datos en cada canal

Hay dos bases con el mismo esquema, y ninguna se sube al repositorio (`datos/esquema.sql:1-6`) [C]. El chat y la voz escriben en la de la nube, que vive en el volumen de Railway, en `/data/despachox.db` (`despliegue/arranque.sh:6`; `docs/DESPLIEGUE.md`, tabla de fallos) [C, F]. El SMS escribe en la del portátil del acopio, porque la pasarela corre allí y no en Railway (`docs/SIN_CONEXION.md`, nivel 2; `docs/QA_NOCHE.md`, sección 2.6, rama `qa-noche`) [F].

### 3.1 Chat de Telegram: texto y ubicación

| Pregunta | Qué pasa hoy [C] |
|---|---|
| Qué entra | El texto, el id del chat y, si la persona la envía, su ubicación (`entrada/bot.py:59-63` y `87-91`). Telegram también le entrega a cada bot el nombre visible y el usuario de la cuenta (política de Telegram, sección 6.3) [F]. El bot no los lee ni los guarda (`entrada/bot.py:3-4`) |
| Qué se transforma antes | `limpiar` cambia por `[número]`, `[correo]` y `[nombre]` lo que tiene forma de teléfono, cédula, correo o nombre presentado (`entrada/privacidad.py:17-34` y `60-74`). Se aplica antes de llamar al modelo (`entrada/flujo.py:99-102`) y el texto que se guarda es ese mismo (`entrada/flujo.py:155` y `162`). El id del chat se convierte en un HMAC-SHA256 con sal, recortado a 32 caracteres (`entrada/privacidad.py:89-91`; `entrada/flujo.py:124`) |
| Para qué se usa | Para armar el pedido o el cierre (`entrada/extraer.py:31-65`), ubicarlo (`lugares/nomenclator.py:150-182`), responder `/estado` (`entrada/guardar.py:107-114`) y confirmar entregas (`entrada/flujo.py:292-299`). Con el modelo activo y sin un reporte pendiente, un saludo o un mensaje que no es pedido ni cierre no se guarda (`entrada/flujo.py:149-150`). Con el lector por reglas, que lee los SMS y los mensajes del chat sin red o cuando falla el modelo, ese mismo saludo se guarda como pedido crudo para el despachador (`entrada/flujo.py:146-148`) [M]. Si el chat tiene un reporte pendiente, el mensaje se toma primero como respuesta sobre el lugar (`entrada/flujo.py:131-145`). Termina en `ubicaciones.texto` (`entrada/flujo.py:143` y `189-201`) o, si no suena a lugar, guardado como crudo, como pasó esta noche con «vivo en la casa azul de doña Rosa» [M] |
| Quién lo ve | Anthropic recibe el texto limpio para leerlo (`entrada/extraer.py:147-151`) y, si hay que desempatar un lugar, el mensaje limpio como contexto (`lugares/nomenclator.py:139-140`). El tablero muestra el texto de pedidos y cierres (`tablero/app.py:373`, `395`, `402` y `417`), y el de la nube es público (sección 3.5). También lo ve quien tenga acceso al volumen de Railway |
| Cuánto se guarda | Sin plazo. Quedan `pedidos.texto_original` y `pedidos.remitente_hash` (`datos/esquema.sql:39-40`), lo que la persona dijo del lugar en `ubicaciones.texto` (`datos/esquema.sql:91`) y las coordenadas. Lo pendiente de cada chat vive en memoria hasta que el bot se reinicia (`entrada/flujo.py:85` y `88`) |
| Cómo se borra | Solo con el reinicio completo de la semilla, que vacía todas las tablas (`despacho/semilla.py:388-390`; `despliegue/arranque.sh:21-24`). No hay borrado por persona ni por plazo |

**Un mensaje que no se pudo leer también se guarda limpio [C].** El flujo lo guarda como pedido `nuevo` sin datos estructurados (`entrada/flujo.py:112-121` y `146-148`; `entrada/guardar.py:82-87`). El código le dice «crudo», y su texto también pasó por `limpiar`.

**La ubicación que alguien envía se guarda con toda su precisión [C, M].** Si el pedido no traía lugar, el bot crea una propuesta con el nombre «pin» y las coordenadas (`entrada/flujo.py:244-256`). `corregir_con_pin` añade esa ubicación al nomenclátor como lugar aprendido (`lugares/nomenclator.py:258-260`). Además crea un punto de entrega nuevo si el lugar no lo era (`lugares/nomenclator.py:211-215`) y anota las coordenadas con cinco decimales en la bitácora (`lugares/nomenclator.py:270`). Si el pedido traía el lugar en palabras, esas palabras pasan a ser el nombre del lugar aprendido y del punto. En una base de prueba, «casa azul de dona rosa» quedó como lugar y como punto, con las coordenadas del pin, y el bot contestó que el pedido «quedó ubicado en casa azul de dona rosa» [M]. Un punto colectivo, como un salón comunal, no identifica a nadie. Una ubicación enviada desde la casa de quien pide sí puede identificarlo [I]. `entrada/README.md:67-72` ya advierte que la ubicación se guarda. La revisión de calidad de la noche llegó al mismo hallazgo y propone redondear a tres decimales, unos 110 m, o llevar el pin al punto de entrega conocido más cercano (`docs/QA_NOCHE.md`, sección 2.7, rama `qa-noche`) [F].

**La limpieza es una heurística [M].** Esta noche la probamos con once mensajes sintéticos escritos por nosotros, que están en la sección 10. Quitó dos celulares, una cédula, un correo y los nombres que seguían a «me llamo», «soy» y «llamen a». En cambio, dejó pasar dos direcciones con calle o carrera y número, «la señora Rosa Inventada» después de «Escribe», «doña Rosa», «Doña Marta Ficticia», los apellidos que seguían a «la familia», un nombre después de «atte.» y un nombre en minúscula después de «soy». Tampoco quitó un fijo de siete dígitos escrito con un espacio ni los datos de salud «abuelo diabético» y «niños enfermos». Once casos no alcanzan para medir una tasa de acierto. Sirven para ver qué tipo de dato se escapa. Las 19 pruebas de `entrada/pruebas/test_privacidad.py` pasan [M].

### 3.2 Notas de voz

| Pregunta | Qué pasa hoy [C] |
|---|---|
| Qué entra | Una nota de voz o un audio de hasta 120 segundos; una más larga se rechaza (`entrada/bot.py:73-75`; `entrada/voz.py:22`) |
| Para qué se usa | Para convertir la nota en un pedido o un cierre, como si la persona lo hubiera escrito (`entrada/bot.py:65-67`) |
| Camino | El bot descarga el audio de Telegram a su memoria (`entrada/bot.py:76-77`) y lo envía al servicio de transcripción (`entrada/voz.py:36-39`). La transcripción pasa por `limpiar` y por el modelo (`entrada/bot.py:82`), y el bot le muestra a la persona lo que escuchó, ya limpio (`entrada/bot.py:83`). De ahí en adelante sigue el flujo del texto |
| Qué se guarda | La transcripción limpia, como cualquier texto. DespachoX no escribe el audio en disco ni en la base, porque el audio vive en una variable mientras dura la llamada (`entrada/bot.py:65-85`; `entrada/voz.py:10-11` y `29-45`) |
| Quién lo ve | El servicio de transcripción recibe el audio completo, con lo que la persona haya dicho, y sin la retención cero puede guardarlo hasta 30 días (abajo) [F]. `limpiar` solo puede actuar después de transcribir. Telegram conserva la nota en el chat [I] |
| Qué servicio | El código usa la dirección de OpenAI si no se configura otra (`entrada/voz.py:19-20`). Fable recomendó Groq a las 10:58 p. m. (`torre/CANAL.md`, 22:58). Cuál quedó configurado en Railway: [pendiente] |
| Cómo se borra | Del lado de DespachoX no hay audio que borrar. Del lado del servicio, ver abajo |

**Lo que dice Groq de sus datos [F].** Según su página «Your Data in GroqCloud», Groq no retiene por defecto los datos de las solicitudes de inferencia. Puede guardar entradas y salidas hasta por 30 días cuando investiga fallas de confiabilidad o sospechas de abuso. La tabla de esa página incluye el servicio de transcripción entre los que admiten retención cero (ZDR), que se activa en la configuración de datos de la organización. Lo que Groq retiene queda en buckets de Google Cloud en Estados Unidos. Esa página no dice dónde corre la transcripción, y su política de privacidad dice que Groq está en Estados Unidos y tiene operaciones de procesamiento en varias jurisdicciones. Dónde corre la transcripción: [pendiente]. Proponemos activar la retención cero antes del piloto [P]. Mientras no esté activada y confirmada, los textos para el usuario dicen «{producto} no guarda el audio» y no «el audio no se guarda».

### 3.3 SMS

| Pregunta | Qué pasa hoy [C] |
|---|---|
| Qué entra | El número de quien escribe y el texto, que un celular Android del acopio reenvía al portátil por el wifi local (`entrada/pasarela_sms.py:1-20` y `45-57`) |
| Para qué se usa | Para lo mismo que el chat, en un acopio sin internet: pedidos, cierres y confirmaciones de entrega (`entrada/sms.py:1-15`) |
| Qué se transforma | El número se convierte en el mismo hash del chat (`entrada/sms.py:314-318`; `entrada/flujo.py:124`). El texto pasa por `limpiar` y lo lee el lector por reglas, sin modelo (`entrada/flujo.py:99-101`). La pasarela crea su mesa sin modelo y sin desempate de lugares con modelo (`entrada/pasarela_sms.py:133-136`) |
| Quién lo ve | En la red del acopio, cualquiera que abra el tablero del portátil, que escucha en el wifi sin clave (abajo). Fuera de ella, el operador móvil que lleva el SMS. El número vuelve al celular en la respuesta HTTP (`entrada/pasarela_sms.py:122`) y en la orden de enviar la respuesta (`entrada/pasarela_sms.py:60-75`). El registro del proceso no escribe ni la ruta ni la IP (`entrada/pasarela_sms.py:81-82`), y del SMS solo anota cuántos caracteres tuvo la respuesta (`entrada/pasarela_sms.py:121`) |
| Cuánto se guarda | En la base del portátil, lo mismo que el chat y sin plazo. En el celular del acopio, cada SMS queda en la bandeja con el número, como en cualquier teléfono [I]. La documentación de SMS Gateway for Android menciona una función para leer el historial de mensajes, pero no dice dónde lo guarda [F, pendiente] |
| Riesgo | Sin `DESPACHOX_SMS_TOKEN`, cualquiera en el mismo wifi puede enviar SMS falsos al receptor (`entrada/pasarela_sms.py:104-107`) |
| Cómo se borra | En la base, igual que el chat. En el celular, a mano |

**La base del portátil [C, P].** La pasarela guarda en `DESPACHOX_DB` o, si falta, en `datos/despachox.db` (`entrada/pasarela_sms.py:130`; `datos/db.py:10`), la misma ruta que usa el arranque local (`despliegue/local.sh:16`). Esa base no pasa por la nube, así que sus riesgos son otros.

| Qué pasa hoy [C] | Qué proponemos [P] |
|---|---|
| El tablero del portátil escucha en todas las interfaces y sin clave (`despliegue/local.sh:56-62`). Cualquiera conectado al wifi del acopio puede abrirlo y leer los SMS | La misma clave que el tablero de la nube (sección 4, punto 3), o que escuche solo en el portátil (`--server.address 127.0.0.1`) si nadie más lo abre por wifi |
| `local.sh` no define `DESPACHOX_SAL` (`despliegue/local.sh:15-17`). Si el `.env` tampoco la trae, la sal queda en `datos/despachox.sal`, junto a la base (`entrada/privacidad.py:82-86`). Git no la sube, porque `.gitignore` excluye `datos/*.sal` | Definirla en el `.env`, fuera de `datos/`, para que quien copie la carpeta de la base no se lleve también la sal. Lo que de verdad la protege es el disco cifrado |
| El repositorio no dice si el disco está cifrado ni si el portátil se bloquea [pendiente] | Disco cifrado (FileVault o BitLocker), bloqueo con clave y una cuenta del sistema solo para la mesa |
| Nada borra esa base salvo el reinicio con `DESPACHOX_REINICIAR=1` (`despliegue/local.sh:42-45`) | La misma purga diaria de la sección 4. Al cerrar el piloto, borrar la base con sus archivos `-wal` y `-shm`, la sal y la carpeta `hojas/` |

### 3.4 QR, hoja de ruta y confirmación de entrega

| Pregunta | Qué pasa hoy [C] |
|---|---|
| Qué lleva el QR | Solo el código del paquete, como `DX-7KQ3` (`despacho/hoja.py:14-16` y `470`; `datos/esquema.sql:67`). El código son cuatro signos tomados al azar de un alfabeto de 25 (`despacho/paquetes.py:25` y `34-38`) |
| Para qué se usa | Para rastrear cada paquete desde que el despachador aprueba el plan hasta la entrega, y saber de qué lote salió por si hay que retirarlo (`despacho/paquetes.py:1-13` y `41-45`) |
| Quién lo ve | El conductor, quien recibe y quien escanee el código. El código no identifica a nadie. En la base se asocia a un pedido, a un lote y a unos kilos (`datos/esquema.sql:67-72`) |
| Cuánto se guarda | La tabla `paquetes` no tiene plazo. Como no lleva datos personales, la purga no necesita tocarla [I] |
| Qué lleva la hoja impresa | El punto y su barrio, la hora estimada, los productos, si el punto es crítico y una columna «Recibe: firma y hora» (`despacho/hoja.py:48-49`). El pie dice quién aprobó el plan (`despacho/hoja.py:533-535`) |
| Dónde queda el PDF | Junto a la base, en `hojas/plan_N/`, sin plazo (`despacho/hoja.py:577-579`) |
| Confirmación de entrega | «ENTREGADO DX-…» por chat o SMS marca el paquete y deja en la bitácora «remitente» seguido de los primeros 8 caracteres del hash (`entrada/flujo.py:292-299`; `despacho/paquetes.py:90-105`). En `samuel-bot`, sin fusionar, solo confirman el destino o el conductor asignado |
| Riesgo | La firma en papel es un dato personal en una base manual, y el Decreto 1074 también cubre las bases manuales (art. 2.2.2.26.2.6) [N]. Quién guarda las hojas firmadas y por cuánto tiempo: [pendiente con el Banco] |

Los puntos de entrega son sitios colectivos, como salones comunales, albergues o comedores (`datos/README.md:18`) [C]. La excepción son los puntos que nacen de una ubicación enviada (sección 3.1).

### 3.5 Lo que comparten los canales

**La base y la sal [C].** El hash usa la sal de la variable `DESPACHOX_SAL` o, si falta, un archivo `.sal` junto a la base con permisos 600 (`entrada/privacidad.py:77-86`). La guía de despliegue pide definirla como variable en Railway (`docs/DESPLIEGUE.md:24`), pero la misma guía dice que ese despliegue no se probó (`docs/DESPLIEGUE.md:50`). Falta confirmar en la cuenta que la variable existe [pendiente]. El caso del portátil está en la sección 3.3. Con la base y la sal juntas, alguien podría probar ids de chat o números de celular uno por uno y encontrar quién escribió [I]. Por eso la sal no debe vivir en el mismo volumen que la base. Si la sal se rota al cerrar el piloto y la vieja se destruye, los hashes viejos dejan de poder asociarse a nadie [I].

**El tablero [C, F].** Es una aplicación de Streamlit sin inicio de sesión, y `docs/DESPLIEGUE.md:36` advierte que «El tablero queda público». Además, su dirección está en el `README.md` de un repositorio público (`README.md:113`; `docs/QA_NOCHE.md`, sección 2.1). Muestra el texto de los mensajes, lo que la gente dijo de cada lugar (`tablero/app.py:188-192`) y la bitácora (`tablero/app.py:449-456`). El nombre del despachador se escribe en una casilla sin verificar (`tablero/app.py:80-81` y `494`). Ese nombre llega a `planes.aprobado_por` (`datos/esquema.sql:57`), a la bitácora y al pie de la hoja impresa. Hoy la base de la nube tiene la semilla sintética y los mensajes de quienes prueban el bot, que pueden ser jurados, mentores o cualquiera que lea el `README.md`. Lo que escriben es dato de personas reales y se ve en el tablero [I]. Con datos del piloto, un tablero abierto choca con el principio de circulación restringida (Ley 1581, art. 4 f) [I].

**La bitácora [C].** Guarda quién decidió qué (`datos/esquema.sql:73-75`; `datos/db.py:44-48`). Incluye lo que la persona dijo del lugar (`lugares/nomenclator.py:245`), las coordenadas de cada ubicación enviada (`lugares/nomenclator.py:270`) y, en cada entrega confirmada por chat o SMS, «remitente» con los 8 primeros caracteres del hash (`entrada/flujo.py:296`; `despacho/paquetes.py:104`).

**El repositorio [F].** La revisión de calidad de la noche buscó en los 152 commits de las 10 ramas. No encontró claves ni tokens, ni un `.env`, una base o una sal versionados. Tampoco encontró celulares, cédulas ni correos reales (`docs/QA_NOCHE.md`, tabla inicial, rama `qa-noche`).

**Los registros del proceso [C].** No llevan el texto de los mensajes. El bot no lo escribe (`entrada/bot.py:3-4`), el extractor y la voz solo anotan el tipo de error (`entrada/extraer.py:158-159`; `entrada/voz.py:43-44`) y el registro de `httpx` se sube a advertencia porque sus líneas llevan el token del bot (`entrada/bot.py:156`).

**El módulo `triage/` [C].** No está conectado a ningún canal. Ningún archivo de `entrada/`, `tablero/` o `despacho/` lo importa (búsqueda con `git grep`). Lee archivos CSV o JSON y guarda su texto sin pasar por `limpiar` (`triage/entrada_datos.py:261-262`). Antes de cargarle un archivo real hay que limpiarlo.

**Tres piezas pendientes que todavía no están en el esquema [C, F].** Carlos aprobó a las 10:48 p. m. la columna `pedidos.dudas` y la tabla `avisos` (`torre/CANAL.md`, 22:50). Ninguna de las dos está en `datos/esquema.sql`, ni en `main` ni en `samuel-bot`. `guardar.py` solo escribe las dudas si la columna existe (`entrada/guardar.py:43-44`), y son notas sobre lo que falta para despachar, sin datos de la persona. La tabla `avisos` sirve para el aviso de vuelta («tu pedido va en camino») y sí cambia el riesgo. Un hash no sirve para escribirle a nadie, así que la propuesta de Samuel guarda el id del chat cifrado con una clave aparte (`DESPACHOX_CLAVE_AVISOS`). Solo se guarda si la persona responde que sí, y se borra al entregar, al descartar o a las 48 horas (`torre/CANAL.md`, 17:15). Así cumple la regla de autorización expresa y la del límite de tiempo [I]. La tercera pieza es una pregunta de Samuel sin respuesta todavía, la columna `vehiculos.conductor_hash` (`torre/CANAL.md` de la rama `samuel-bot`, 23:30). Guardaría el hash del chat o del número de cada conductor, con la misma sal, para que el conductor asignado confirme la entrega. Con ella, los conductores también son titulares, así que entran al aviso y al contrato (sección 8, cláusula 4) [I].

---

## 4. Lo que el código no hace todavía

Ninguna propuesta de esta tabla está programada [P]. Como las funciones se congelan a las 8:30 a. m., la columna final dice si cabe antes o si va al plan de 30 días.

| # | Brecha [C] | Norma [N] | Propuesta [P] | ¿Antes de las 8:30? |
|---|---|---|---|---|
| 1 | No hay plazo de conservación ni borrado. Solo existe el reinicio completo (`despacho/semilla.py:388-390`) | Decreto 1074, art. 2.2.2.25.2.8 | Un `python -m datos.purgar` diario. A los 30 días quita el texto y el código de todo pedido que no vaya en ruta, el texto de las ubicaciones y de los cierres, y los textos, coordenadas y códigos de la bitácora. También redondea los pines a tres decimales, les quita el nombre a los puntos y lugares que nacieron de un pin y borra los PDF de los planes cerrados | No. Va al plan de 30 días |
| 2 | Nadie puede pedir el borrado desde el chat | Ley 1581, arts. 8 y 15; Decreto 1074, art. 2.2.2.25.2.6, que pide un mecanismo gratuito y de fácil acceso | `/borrar` en Telegram y `BORRAR` por SMS (sección 7.5) | Es función nueva. Lo deciden Samuel y Carlos |
| 3 | Ningún tablero tiene clave. El de la nube muestra el texto de los mensajes (`docs/DESPLIEGUE.md:36`) y su dirección está publicada (`README.md:113`). El del portátil escucha en el wifi del acopio (`despliegue/local.sh:61`) | Ley 1581, art. 4 f) y g) | Primero, la clave compartida por variable de entorno (`DESPACHOX_CLAVE_TABLERO`), que ya está diseñada (`docs/QA_NOCHE.md`, sección 2.1, rama `qa-noche`). Antes de cargar datos reales, inicio de sesión por persona, que no está diseñado, y el nombre del despachador tomado de su cuenta | La clave compartida es un arreglo pequeño y lo deciden Jacobo y Carlos. El inicio por persona es requisito para el día 30 a 45 del piloto (`docs/PILOTO.md`, sección 5) |
| 4 | La ubicación enviada se guarda con toda su precisión, crea un punto y entra al nomenclátor (`lugares/nomenclator.py:211-215`, `258-260` y `270`) | Decreto 1074, art. 2.2.2.25.2.1 | Pedir en el bot la ubicación del punto colectivo y no la de la casa. Redondear a tres decimales lo que va al nomenclátor y a la bitácora, como propone `docs/QA_NOCHE.md`. Que el despachador adopte o descarte el punto, y que la purga redondee y renombre lo no adoptado | El texto del bot, sí. El resto, después |
| 5 | El audio completo sale al servicio de transcripción (`entrada/voz.py:36-39`) | Decreto 1074, art. 2.2.2.25.5.2 | Retención cero en Groq, acuerdo de tratamiento y aviso en el `/start` | Sí, si el servicio configurado es Groq, porque la retención cero se activa en su configuración |
| 6 | El texto libre puede traer datos de salud de personas | Ley 1581, arts. 5 y 6; Decreto 1074, art. 2.2.2.25.2.3 | El `/start` pide no escribirlos y la purga borra el texto. Además, el tablero marca los pedidos con palabras de salud para que el despachador borre ese texto apenas despache, sin esperar los 30 días. El pedido solo necesita la urgencia | El texto del bot, sí. La marca en el tablero, después |
| 7 | No queda prueba de qué aviso vio cada chat | Ley 1581, art. 12, parágrafo; Decreto 1074, arts. 2.2.2.25.2.5 y 2.2.2.25.3.4 | Guardar, por hash, la versión del aviso y la fecha del primer mensaje, y archivar cada versión del texto del `/start` | No |
| 8 | Si falta `DESPACHOX_SAL`, la sal queda en un archivo junto a la base (`entrada/privacidad.py:82-86`) | Ley 1581, art. 4 g) | Exigir la variable en todo despliegue con datos reales y rotar la sal al cerrar el piloto | La guía de Railway la pide como variable (`docs/DESPLIEGUE.md:24`), y falta confirmarlo en la cuenta [pendiente]. En el portátil, va en el `.env` (sección 3.3) |
| 9 | El celular del acopio guarda cada SMS con el número [I] | Decreto 1074, art. 2.2.2.25.2.8 | Borrar los SMS del celular al cerrar cada jornada, con el aparato bloqueado con clave | Sí, porque es un procedimiento del acopio |
| 10 | `triage/` guarda el texto sin limpiar (`triage/entrada_datos.py:261-262`) | Ley 1581, art. 4 g) | Pasar `privacidad.limpiar` al importar | No toca la demostración |
| 11 | No hay política de tratamiento ni aviso completo | Decreto 1074, arts. 2.2.2.25.3.1 a 2.2.2.25.3.3 | `/privacidad` en el bot (sección 7.3) y la política del Banco | El texto del bot, sí |

La purga del punto 1 se puede escribir así, para que Samuel o Carlos la conviertan en código con su prueba. La tabla `pedidos` no guarda la hora de cierre, así que el plazo se cuenta desde la creación del pedido (`datos/esquema.sql:30-44`) [C]. Un pedido que sigue en «nuevo» o «confirmado» a los 30 días también pierde texto y código, porque si nadie lo atendió en un mes ya no sirve para repartir [P]. Solo espera el que va en ruta, en estado «asignado».

```sql
-- :limite = ahora menos 30 días, en ISO 8601 con hora de Colombia (datos/db.py:14-16)
-- 1. Pedidos que no van en ruta: sin texto ni código del remitente.
UPDATE pedidos SET texto_original = NULL, remitente_hash = NULL
 WHERE estado <> 'asignado' AND creado_en < :limite;
-- 2. Lo que la persona dijo del lugar, y el pin redondeado a tres decimales (unos 110 m).
UPDATE ubicaciones SET texto = '[borrado]'                -- la columna no admite NULL
 WHERE creado_en < :limite
   AND (tabla = 'cierres' OR fila_id IN (SELECT id FROM pedidos WHERE estado <> 'asignado'));
UPDATE ubicaciones SET lat = ROUND(lat, 3), lon = ROUND(lon, 3)
 WHERE metodo = 'pin' AND creado_en < :limite;
-- 3. Puntos y lugares que nacieron del pin de un remitente: sin su texto y con el pin redondeado.
--    Si el despachador adopta el punto como colectivo (punto 4 de la tabla), se excluye.
UPDATE puntos SET nombre = 'Punto de entrega por pin ' || id, barrio = NULL,
                  lat = ROUND(lat, 3), lon = ROUND(lon, 3)
 WHERE id IN (SELECT l.punto_id FROM lugares l JOIN ubicaciones u ON u.lugar_id = l.id
               WHERE u.metodo = 'pin' AND l.origen = 'aprendido' AND u.creado_en < :limite);
UPDATE lugares SET nombre = 'pin ' || id, alias = 'pin ' || id, lat = ROUND(lat, 3), lon = ROUND(lon, 3)
 WHERE origen = 'aprendido'
   AND id IN (SELECT lugar_id FROM ubicaciones WHERE metodo = 'pin' AND creado_en < :limite);
-- 4. Cierres: queda la descripción, no el mensaje.
UPDATE cierres SET texto_original = NULL WHERE creado_en < :limite;
-- 5. Bitácora: textos, coordenadas y los 8 caracteres del código del remitente.
UPDATE bitacora SET detalle = NULL
 WHERE accion IN ('ubicacion_confirmada', 'ubicacion_por_pin') AND cuando < :limite;
UPDATE bitacora SET quien = 'remitente' WHERE quien LIKE 'remitente %' AND cuando < :limite;
-- Falta: los PDF de hojas/plan_N de los planes cerrados (despacho/hoja.py:577-579).
```

Estas sentencias corrieron sin error esta noche [M]. La base temporal se llenó con el flujo real del bot y el lector por reglas, sin red: un saludo, un pedido sin lugar con un mensaje suelto y una ubicación enviada, un pedido ubicado en San José con «si», otro con el lugar en palabras y una ubicación enviada, un cierre y una entrega con «ENTREGADO». Todo quedó con 51 días de antigüedad, y un pedido más se escribió con la fecha de hoy. Después de la purga, los cinco pedidos viejos quedaron sin texto ni código, también los cuatro que seguían en «nuevo». Los pines quedaron redondeados a tres decimales en ubicaciones, lugares y puntos. Los dos puntos y los dos lugares que nacieron de los pines, unos con las coordenadas en el nombre y otros con «casa azul de dona rosa», quedaron con un nombre por número. La bitácora perdió los textos, las coordenadas y el código del remitente, y el pedido de hoy quedó intacto. Esa corrida prueba la lógica, no el script completo. El bloque de la sección 10 la repite.

Si la purga corre así, lo que queda es el registro de la operación: punto, productos, kilos, fechas y estado, con los pines redondeados a unos 110 m. Creemos que ese registro ya no se puede asociar a una persona y deja de ser dato personal [I]. Esa conclusión depende de dos condiciones. Un pin redondeado no debe apuntar a una sola casa, como puede pasar en una vereda. Y no debe quedar otra copia con el texto o las coordenadas exactas, como las hojas impresas, los PDF o los respaldos. La decide el abogado. Con ese registro se le rinde cuentas al donante.

---

## 5. Roles en el piloto y lo que sale del país

La ley define los roles por lo que cada uno hace. Responsable es quien decide para qué y cómo se tratan los datos (art. 3 e). Encargado es quien los trata por cuenta del responsable (art. 3 d). Con esas dos definiciones proponemos este reparto.

| Actor | Rol que proponemos | Por qué | Qué le exige la norma |
|---|---|---|---|
| Banco Arquidiocesano de Alimentos de Manizales | Responsable [P] | Decide a quién se reparte y para qué se reciben los pedidos | Política y aviso, autorización y su prueba, persona o área de datos, contrato con el encargado y reclamos (Ley 1581, art. 17; Decreto 1074, arts. 2.2.2.25.3.1 y 2.2.2.25.4.4). Inscribir la base si sus activos superan 100.000 UVT [pendiente] |
| Unidad de Gestión del Riesgo de Manizales | Responsable si el piloto pasa a su flujo, según la regla de cambio (`docs/DECISIONES_9PM.md:22`). Corresponsable si decide junto con el Banco [P] | La definición de responsable incluye a quien decide «en asocio con otros» | El Registro obliga a las «personas jurídicas de naturaleza pública» (Decreto 1074, art. 2.2.2.26.1.2 b) [N]. Si la UGR es una dependencia de la Alcaldía, esa persona jurídica sería el Municipio de Manizales [I] (sección 9, pregunta 12). Las faltas de una autoridad pública las investiga la Procuraduría (Ley 1581, art. 23, parágrafo) |
| Gobernación de Caldas | Posible corresponsable [P] | La regla de cambio lleva el piloto «al flujo de requerimientos de la UGR y la Gobernación» (`docs/DECISIONES_9PM.md:22`). Si decide con la UGR para qué y cómo se tratan los pedidos, decide «en asocio con otros» [I] | Lo mismo que la UGR. La persona jurídica pública sería el Departamento de Caldas [I] (sección 9, pregunta 12) |
| Equipo DespachoX | Encargado en el piloto [P]. Hoy, en la demostración, responsable del prototipo [I] | En el piloto opera el bot, la base y el tablero por cuenta del Banco. Hoy decide sobre la base de la demostración, que guarda la semilla sintética y los mensajes de quienes prueban el bot (`README.md:112-113`) | Deberes del art. 18 de la Ley 1581 y el contrato de la sección 8. Quién firma por el equipo: [pendiente] |
| Universidad Nacional, sede Manizales | Ninguno con datos personales, si el piloto se monta así [P]. Si aloja el sistema o firma, sería encargada o corresponsable [I] | Su aporte al proyecto es el indicador A25 del IDEA (`torre/CANAL.md`, 22:30), que trabaja con lluvia y no con personas | Pregunta para el abogado |
| Anthropic PBC (modelo de lenguaje) | Subencargado [I] | Lee el texto limpio por cuenta del responsable. Su política de privacidad excluye el contenido que trata para clientes empresariales y lo remite a los acuerdos con esos clientes [F] | Contrato de transmisión o acuerdo de tratamiento |
| Groq (transcripción) | Subencargado [I] | Transcribe el audio | Lo mismo |
| Railway (alojamiento) | Subencargado [I] | Guarda la base de la nube y corre el bot y el tablero | Lo mismo |
| Telegram | Servicio independiente que la persona eligió [I] | Su política dice que los bots son independientes de Telegram y que «should ask you for your permission before they access your data» (sección 6.4) [F]. Eso respalda el aviso del `/start`. Lo que el bot recibe es responsabilidad de quien lo opera [I] | No es encargado de DespachoX [I]. La persona puede borrar el chat (sección 10.2 de esa política) [F] |
| Operador móvil y SMS Gateway for Android | Canal | La aplicación corre en el celular del acopio y, en modo de servidor local, funciona sin internet [F] | Protocolo del celular (sección 4, punto 9) |

### 5.1 Lo que sale de Colombia

| Qué sale | A quién | Dónde | Qué pide la norma [N] | Qué proponemos [P] |
|---|---|---|---|---|
| Texto limpio del chat. El SMS no sale del portátil | Anthropic PBC | Empresa con sede en Estados Unidos, según su política de privacidad, que da su dirección registrada en San Francisco. Esa política dice que los datos van a servidores en Estados Unidos o en otros países, y no rige el contenido de los clientes comerciales [F]. La región donde la API procesa los datos depende de sus términos comerciales y de su lista de subencargados [pendiente] | Transmisión con contrato (Decreto 1074, arts. 2.2.2.25.5.1 y 2.2.2.25.5.2). Estados Unidos está en la lista de la SIC (Circular Única, Título V, num. 3.2). Si la API procesa en otro país, hay que revisarlo [pendiente] | Revisar sus términos comerciales con el abogado. Según su centro de privacidad, Anthropic borra entradas y salidas de la API dentro de los 30 días, con excepciones como el contenido marcado por sus políticas de uso, y por defecto no las usa para entrenar [F] |
| Audio de las notas de voz | Groq | Empresa con sede en Estados Unidos [F]. Lo que retiene queda en Google Cloud, en Estados Unidos [F]. Dónde corre la transcripción: [pendiente] | Lo mismo | Retención cero activada y acuerdo de tratamiento |
| La base de la nube | Railway | La región elegida, entre California, Virginia, Ámsterdam y Singapur [F]. La del proyecto no está en el repositorio: [pendiente] | Lo mismo. Singapur no figura en la versión de 2017 de la lista de la SIC | Elegir una región de Estados Unidos o de Europa y confirmarlo en la cuenta. Cambiar la región de un servicio con volumen obliga a migrar el volumen, y el servicio queda caído mientras tanto (página de regiones de Railway) [F]. Por eso el cambio va después del pitch o en el plan de 30 días |
| El chat | Telegram | Su política no dice dónde guarda los datos de quien se registró desde Colombia. Para el Reino Unido y el Espacio Económico Europeo dice Países Bajos (sección 4.1) [F] | No es una transmisión de DespachoX [I] | Decirlo en `/privacidad` |

Aunque la transmisión con contrato no exige informar al titular [N], proponemos decirlo en `/privacidad` [P], porque la circular de la SIC sobre inteligencia artificial insiste en que el titular pueda saber cómo se tratan sus datos.

---

## 6. Base legal que proponemos para el piloto

Esta sección es propuesta [P], salvo donde cita la norma. La decide el abogado.

1. **Autorización por conducta inequívoca después del aviso.** La persona recibe el aviso en el `/start` y después envía su pedido. Ese envío es la conducta inequívoca del art. 2.2.2.25.2.4 del Decreto 1074 [I]. Para que haya prueba, se guarda la versión del aviso y la fecha del primer mensaje (sección 4, punto 7). En Telegram, el primer contacto con un bot suele empezar con el botón que envía `/start` [I, por verificar]. Además, el bot responde el mismo texto a `/ayuda` y `/help` (`entrada/bot.py:141`) [C]. El SMS no tiene `/start`, así que el aviso va en un cartel del acopio y en la primera respuesta (sección 7.4). El decreto acepta un aviso verbal o escrito y cualquier medio que cumpla el deber de informar (arts. 2.2.2.25.1.3 y 2.2.2.25.3.5) [N].
2. **No apoyarse en la urgencia.** El art. 10 de la Ley 1581 exime de autorización los «casos de urgencia médica o sanitaria» [N]. Una emergencia alimentaria podría no caber ahí, así que no construimos el piloto sobre esa excepción.
3. **Datos sensibles.** No se piden. El aviso dice que no es obligatorio darlos y nada depende de darlos (Ley 1581, art. 12 b; Decreto 1074, art. 2.2.2.25.2.3) [N]. Cuando llegan sin pedirlos, como «abuelo diabético», la ley exige «autorización explícita» para tratarlos (Ley 1581, art. 6 a) [N], y la conducta inequívoca del punto 1 no la da [I]. Proponemos que el tablero marque los pedidos con palabras de salud para que el despachador borre ese texto apenas despache (sección 4, punto 6). La pregunta va al abogado (sección 9, pregunta 13).
4. **Niños.** El bot cuenta bebés y niños como cifras para calcular raciones y urgencia (`entrada/extraer.py:40-45`) [C]. No guarda datos de un niño identificable [I]. Queda abierta la pregunta de qué hacer si quien escribe es menor de edad (sección 9).
5. **Aviso de vuelta.** Lleva su propia autorización expresa (Sí o No), una finalidad aparte y un plazo de 48 horas, como lo propuso Samuel (`torre/CANAL.md`, 17:15) [F].
6. **Lo que el operador comparte para la línea base.** El Banco entrega catálogo de puntos, inventario y un mes de despachos sin datos de beneficiarios ni de conductores (`docs/PILOTO.md`, sección 6). La carta de intención dice que el equipo no pedirá datos personales de beneficiarios (`encargos/P5_ALIADO_PILOTO.pdf`, anexo A) [F]. Si esos tres archivos llegan sin datos personales, no requieren autorización de nadie [I].

---

## 7. Texto propuesto para el `/start`

El texto de hoy pide no escribir nombres, cédulas ni teléfonos (`entrada/flujo.py:49`), y solo nombra las notas de voz si la voz está disponible (`entrada/flujo.py:44`; `entrada/bot.py:54`) [C]. Le falta decir quién trata los datos y para qué, qué pasa con la voz y cómo pedir el borrado. El encargo de Samuel pide la privacidad «en una línea» (`encargos/P4_CARGA_START_TABLERO.md`, punto 4). Samuel decide el texto final y este documento no toca el bot. La advertencia sobre datos personales se queda en todas las versiones, porque es la única que tiene hoy el `/start`. En los textos, `{producto}` es DespachoX o Convite, según confirme Carlos.

### 7.1 Para el piloto

Estas líneas van al final del mensaje de bienvenida y reemplazan la última línea de hoy (`entrada/flujo.py:49`), que pasa a ser la línea 1 con dos datos más.

| Línea | Cuándo se muestra | Texto | Caracteres [M] |
|---|---|---|---|
| 1 | Siempre | No escribas nombres, cédulas, teléfonos, direcciones de casa ni datos de salud, porque no hacen falta. | 102 |
| 2 | Siempre | Lo que escribes lo usa el Banco de Alimentos de Manizales solo para repartir la ayuda. | 86 |
| 3 | Solo si `voz.disponible()` | Un servicio externo pasa a texto las notas de voz, y {producto} no guarda el audio. | 82 con DespachoX, 80 con Convite |
| 4 | Siempre | Para borrar tus mensajes, escribe /borrar. Más en /privacidad. | 62 |

Con voz suman 335 caracteres con DespachoX y 333 con Convite, y sin voz 252, contando los saltos de línea [M]. La línea 3 sigue la misma regla que hoy usa `ayuda(con_voz)`, así que no aparece cuando la voz está apagada.

**Versión de una línea.** Si Samuel prefiere una sola línea de privacidad, como pide el encargo, las líneas 2 y 4 se juntan en esta, de 96 caracteres [M]:

> Guardo lo que escribes para que el Banco de Alimentos reparta la ayuda, y lo borras con /borrar.

La línea 1 se queda, y la línea 3 se añade solo si la voz está disponible. Si el piloto pasa a la UGR, el nombre del responsable cambia en la línea 2 y en la versión de una línea.

### 7.2 Para la demostración de hoy

| Línea | Cuándo se muestra | Texto | Caracteres [M] |
|---|---|---|---|
| 1 | Siempre | Es un prototipo de la Hackathon UNAL 2026 y lo que escribes se ve en un tablero público. No escribas nombres, cédulas, teléfonos, direcciones de casa ni datos de salud. | 168 |
| 2 | Siempre | Lo que escribes lo usa el equipo {producto} solo para probar el reparto. | 71 con DespachoX, 69 con Convite |
| 3 | Solo si `voz.disponible()` | La línea 3 de la versión del piloto | 82 con DespachoX, 80 con Convite |
| 4 | Siempre | Para borrar tus mensajes, escribe /borrar. | 42 |

La línea 1 dice por qué no enviar datos reales. El tablero de la nube no pide clave (`docs/DESPLIEGUE.md:36`) y su dirección está en el `README.md` de un repositorio público (`README.md:113`; `docs/QA_NOCHE.md`, sección 2.1) [C, F]. Si el tablero recibe la clave antes del pitch, la primera frase cambia por «Es un prototipo de la Hackathon UNAL 2026, así que no envíes datos reales».

Si `/borrar` no alcanza a existir antes de las 8:30 a. m., la línea 4 cambia por «Para borrar tus mensajes, escríbenos a [contacto del equipo, pendiente]». Es más débil, porque el equipo no tiene cómo saber cuáles mensajes son de esa persona sin el id de su chat.

### 7.3 `/privacidad`: el aviso completo

Esta es la segunda capa, con el contenido mínimo del aviso de privacidad (Decreto 1074, art. 2.2.2.25.3.3) [N]. Los datos de contacto los pone el responsable.

> **Quién trata tus datos.** El Banco Arquidiocesano de Alimentos de Manizales, [dirección, correo y teléfono, pendiente]. El sistema lo opera el equipo {producto} por encargo del Banco.
>
> **Para qué.** Para recibir pedidos de comida y avisos de vías cerradas, ubicarlos, planear la entrega y confirmarla.
>
> **Qué guardamos.** Lo que escribes, después de que el sistema intenta quitarle nombres, cédulas y teléfonos. Un código en lugar de tu cuenta. La ubicación, si la envías. {producto} no guarda el audio de las notas de voz.
>
> **Quién más lo procesa.** Un programa de lenguaje lee el texto para ordenarlo, un servicio de transcripción pasa la voz a texto y un servicio de alojamiento guarda la base. Son empresas con sede en Estados Unidos, trabajan por encargo y tienen contrato. Procesan los datos en [países, pendiente]. El servicio de transcripción tampoco guarda el audio [solo si la retención cero está activada y confirmada]. Una persona de la mesa revisa cada pedido.
>
> **Cuánto tiempo.** Tu texto y tu código se guardan hasta 30 días después de que escribas, o hasta la entrega si tu pedido sigue en camino. Después queda el registro de lo entregado: punto, productos y kilos, sin tu texto ni tu código, y con la ubicación que enviaste redondeada a unos 110 metros.
>
> **Tus derechos.** Puedes conocer, corregir y borrar tus datos, y quejarte ante la Superintendencia de Industria y Comercio. Escribe /borrar o contacta al Banco. La política completa está en [enlace, pendiente].
>
> **Datos de salud y de niños.** No los pedimos. Darlos es voluntario y nada depende de que los des.

Este aviso solo puede publicarse cuando existan la purga y los contratos que menciona. Mientras falte la purga, la frase del tiempo diría «hasta que termine el piloto, cuando se borra la base», porque el borrado completo sí existe hoy (sección 3.1).

### 7.4 Por SMS, en 160 caracteres y sin tildes

> Banco de Alimentos y {producto} usan sus SMS solo para repartir ayuda. No envie nombres, cedulas, telefonos ni datos de salud. Para borrarlos, envie BORRAR.

Son 155 caracteres con DespachoX y 153 con Convite, todos del alfabeto GSM-7 [M]. Iría como respuesta al primer SMS de cada número. Requiere que el lector por reglas reconozca `BORRAR` (`entrada/sms.py:31-35`).

### 7.5 Lo mínimo que necesita `/borrar`

Es una especificación para Samuel [P], sin código.

1. Calcula el hash del chat o del número con `hash_remitente`, igual que el resto del flujo.
2. Pide confirmación con dos botones, porque es irreversible. Un pedido que siga abierto se cancela.
3. En los pedidos de ese hash pone `texto_original` y `remitente_hash` en nulo, y cambia por «[borrado]» el texto de sus ubicaciones. Los lugares y puntos que nacieron de sus pines pierden el nombre y quedan con el pin redondeado, como en la purga.
4. Borra lo que la bitácora guarda de esa persona. El texto y las coordenadas de sus ubicaciones se encuentran por el número de cada pedido suyo (`lugares/nomenclator.py:245` y `270`). El código de sus entregas se encuentra por los 8 primeros caracteres del hash (`entrada/flujo.py:296`).
5. Borra lo que el bot tiene en memoria para ese chat, que son sus reportes pendientes y la pregunta de familias abierta (`entrada/flujo.py:85` y `88`).
6. Deja en la bitácora «supresión pedida por el titular», con el número de filas y sin contenido. Eso sirve de prueba ante la SIC.
7. Responde cuántos mensajes borró y que el registro de lo entregado queda sin datos suyos.
8. Después, `/estado` ya no encuentra esos pedidos. Es el efecto esperado del borrado.

Los cierres no guardan quién los envió (`datos/esquema.sql:45-52`; `entrada/guardar.py:71-79`), así que `/borrar` no los encuentra [C]. Su texto se borra con la purga a los 30 días, y la respuesta del punto 7 debe decirlo.

---

## 8. Esquema del contrato de transmisión de datos personales

El Decreto 1074 llama así al contrato entre el responsable y el encargado (art. 2.2.2.25.5.2) [N]. Este es su esqueleto para el piloto con el Banco o con la UGR. El texto final lo redacta el abogado.

| # | Cláusula | Contenido mínimo | Origen |
|---|---|---|---|
| 1 | Partes | El responsable (el Banco, la UGR o los dos como corresponsables, con un acuerdo propio entre ellos) y el encargado (quien firme por el equipo DespachoX: [pendiente]) | [P] |
| 2 | Objeto | El encargado trata datos personales por cuenta del responsable para operar la mesa de despacho de ayuda alimentaria | Decreto 1074, art. 2.2.2.25.5.2 [N] |
| 3 | Finalidades | Recibir pedidos y cierres viales; ubicarlos; planear, ejecutar y confirmar entregas; informar a quien pidió sobre su pedido; reportes agregados sin datos personales. Quedan excluidos el perfilamiento, el mercadeo, la venta o cesión y el entrenamiento de modelos | [P]; el encargado trata los datos según la finalidad autorizada [N] |
| 4 | Datos tratados | Texto limpio de los mensajes, código del remitente, ubicación de los puntos, nombre del despachador en la bitácora y firma de quien recibe en la hoja impresa. Si se aprueba `vehiculos.conductor_hash`, también el código del chat o del número de cada conductor. Quedan excluidos cédulas, teléfonos en claro y nombres de beneficiarios. Los datos sensibles no se piden | [P]; carta de intención, anexo A [F] |
| 5 | Obligaciones del encargado | Tratar los datos según los principios, salvaguardar la seguridad de las bases y guardar confidencialidad. Aplicar la política del responsable. Cumplir los deberes del art. 18 de la Ley 1581 | Decreto 1074, art. 2.2.2.25.5.2, num. 1 a 3; Ley 1581, art. 18 [N] |
| 6 | Obligaciones del responsable | Política y aviso; autorización y su prueba; entregar al encargado solo datos autorizados; exigirle seguridad; atender consultas y reclamos | Ley 1581, art. 17 [N] |
| 7 | Seguridad | Tablero con inicio de sesión por persona; sal y claves fuera del repositorio y del volumen de la base; registros sin contenido; respaldos cifrados; acceso mínimo; borrado seguro al terminar | [P]; Ley 1581, art. 4 g) [N] |
| 8 | Subencargados | Lista anexa con Anthropic, Groq y Railway, su país y su función. Agregar o cambiar uno exige autorización previa y escrita del responsable. Cada uno queda obligado por escrito a lo mismo que el encargado | [P]; Decreto 1074, art. 2.2.2.25.5.1 [N] |
| 9 | Retención y borrado | Plazos de la sección 4. Al terminar el contrato, el encargado devuelve o suprime los datos, certifica por escrito que lo hizo y rota la sal | [P]; Decreto 1074, art. 2.2.2.25.2.8 [N] |
| 10 | Derechos de los titulares | El encargado remite al responsable toda consulta o reclamo en 2 días hábiles y lo apoya para responder en los plazos de ley: 10 días hábiles las consultas y 15 los reclamos | Ley 1581, arts. 14 y 15 [N]. Para un reclamo, los 2 días hábiles los fija la ley cuando quien lo recibe no es competente para resolverlo (art. 15, num. 1) [N]. Aplicar el mismo plazo a las consultas es propuesta [P] |
| 11 | Incidentes | El encargado avisa al responsable dentro de las 24 horas siguientes a detectar un incidente. Los dos informan a la SIC, y el incidente se reporta al Registro dentro de 15 días hábiles | Ley 1581, arts. 17 n) y 18 k), que obligan a responsable y encargado; Circular Única de la SIC, Título V [N]; las 24 horas son propuesta [P] |
| 12 | Auditoría y demostración | El responsable puede verificar el cumplimiento, y el encargado le entrega la evidencia que pida la SIC | Decreto 1074, art. 2.2.2.25.6.1 [N] |
| 13 | Confidencialidad | Obliga a todas las personas del equipo y sigue vigente después del contrato | Ley 1581, art. 4 h) [N] |
| 14 | Terminación | Causas, aviso previo y efectos: devolución o supresión y su certificación | [P] |
| 15 | Responsabilidad, ley aplicable y controversias | Para el abogado | [pendiente] |

---

## 9. Preguntas para el abogado

1. ¿Basta la conducta inequívoca después del `/start`, o hace falta un botón «Acepto» con su registro?
2. ¿Una emergencia alimentaria cabe en los «casos de urgencia médica o sanitaria» del art. 10 de la Ley 1581? No pensamos apoyarnos en eso, pero conviene saberlo.
3. Nuestra lectura es que el hash con sal sigue siendo dato personal mientras exista la sal. ¿Es correcta?
4. ¿La grabación de una nota de voz es dato biométrico aunque nadie la use para identificar a la persona?
5. ¿Los términos comerciales y acuerdos de tratamiento de Anthropic, Groq y Railway cumplen el art. 2.2.2.25.5.2 del Decreto 1074, o hace falta un anexo?
6. ¿Quién firma por el equipo DespachoX: la Universidad, una persona natural u otra entidad?
7. Si el Banco y la UGR deciden juntos, ¿son corresponsables y qué debe decir el acuerdo entre ellos?
8. ¿Qué hacer si quien escribe al bot es menor de edad?
9. ¿Cuánto tiempo debe conservar el Banco las hojas de ruta firmadas, por obligaciones contables o con sus donantes?
10. La Función Pública anota que el Decreto 1377 de 2013 fue derogado parcialmente por el Decreto 1081 de 2015. ¿Esa nota cambia algún artículo citado aquí?
11. ¿La lista de países con nivel adecuado de la SIC tiene una versión posterior a la de 2017 que consultamos?
12. ¿La UGR de Manizales es una dependencia de la Alcaldía? Si lo es, ¿el responsable, y quien inscribe la base en el Registro, es el Municipio de Manizales? Si el piloto pasa al flujo de requerimientos de la UGR y la Gobernación (`docs/DECISIONES_9PM.md:22`), ¿el Departamento de Caldas es corresponsable?
13. Los datos de salud que llegan sin pedirlos, como «abuelo diabético», son sensibles, y el art. 6 a) de la Ley 1581 exige «autorización explícita». ¿Basta con borrarlos pronto, o hay que pedir esa autorización o descartar el texto apenas llega?
14. ¿En qué países procesan los datos la API de Anthropic y la transcripción de Groq? Hay que leerlo en sus términos comerciales, su acuerdo de tratamiento y su lista de subencargados. Si alguno procesa fuera de los países de la lista de la SIC, ¿qué cambia en el contrato?

---

## 10. Fuentes

Todas se consultaron el 21 de noviembre de 2026.

**Norma y autoridad**

- Ley Estatutaria 1581 de 2012, texto vigente con notas de vigencia y jurisprudencia. Secretaría del Senado: <http://www.secretariasenado.gov.co/senado/basedoc/ley_1581_2012.html>. Las notas sobre la sentencia C-748 de 2011 y el Decreto Legislativo 538 de 2020 están en el archivo de notas de esa misma página.
- Ley 1581 de 2012. Función Pública, Gestor Normativo: <https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981>.
- Decreto 1377 de 2013. Función Pública, Gestor Normativo: <https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=53646>.
- Decreto 1074 de 2015, Capítulos 25 y 26 del Título 2 de la Parte 2 del Libro 2. Función Pública, Gestor Normativo: <https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=76608>.
- Superintendencia de Industria y Comercio, Circular Única, Título V, Protección de datos personales, versión publicada en septiembre de 2017: <https://sic.gov.co/sites/default/files/normatividad/092017/Titulo%20V%20Proteccion_Datos_Personales.pdf>.
- Superintendencia de Industria y Comercio, Circular Externa 002 del 21 de agosto de 2024, lineamientos sobre el tratamiento de datos personales en sistemas de inteligencia artificial: <https://sedeelectronica.sic.gov.co/transparencia/normativa/circular-externa-2-de-2024-de-la-superintendencia-de-industria-y-comercio-lineamientos-sobre-el-tratamiento-de-datos>.

**Proveedores**

- Anthropic, política de privacidad, vigente desde el 10 de septiembre de 2026, introducción y secciones 5 (transferencias) y 9 (contacto): <https://www.anthropic.com/legal/privacy>.
- Anthropic, centro de privacidad, «How long do you store my organization's data?», actualizado el 1 de julio de 2026: <https://privacy.claude.com/en/articles/7996866-how-long-do-you-store-my-organization-s-data>.
- Anthropic, centro de privacidad, «Is my data used for model training?», actualizado el 18 de agosto de 2026: <https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training>.
- Groq, «Your Data in GroqCloud»: <https://console.groq.com/docs/your-data>.
- Groq, política de privacidad, vigente desde el 12 de noviembre de 2025, sección para usuarios internacionales: <https://groq.com/privacy-policy>.
- Railway, regiones de despliegue y efecto de cambiar la región de un servicio con volumen: <https://docs.railway.com/reference/deployment-regions>.
- Telegram, política de privacidad, secciones 4.1, 6.3, 6.4 y 10.2: <https://telegram.org/privacy>.
- SMS Gateway for Android, modo de servidor local: <https://docs.sms-gate.app/getting-started/local-server/>.

**Documentos del equipo**

- `torre/CANAL.md`, entradas de las 17:15 (aviso de vuelta), 22:30 (capacidad UNAL), 22:50 (decisiones de Carlos), 22:58 (voz con Groq) y 23:30 (nombre Convite). En la rama `samuel-bot`, la entrada de las 23:30 sobre `vehiculos.conductor_hash`.
- `README.md` (líneas 112-113), `docs/DESPLIEGUE.md`, `docs/SIN_CONEXION.md`, `docs/PILOTO.md`, `docs/DECISIONES_9PM.md`, `despliegue/arranque.sh`, `despliegue/local.sh`, `entrada/README.md` y `encargos/P5_ALIADO_PILOTO.pdf`.
- `docs/QA_NOCHE.md` en la rama `qa-noche`, commit `ca195b4`, leído a las 12:30 a. m. y de nuevo a la 1:05 a. m., sin fusionar.

**Cómo repetir las pruebas de las secciones 3.1 y 4**

Se corren desde la raíz del repositorio, sin red. Los seis primeros mensajes siguen la descripción de la primera prueba, con números que no pueden existir. Los otros cinco son los casos de la revisión, con direcciones y números inventados.

```bash
export DESPACHOX_SIN_RED=1
python -m pytest entrada/pruebas/test_privacidad.py -q        # 19 pasan
python - <<'FIN'
from entrada.privacidad import limpiar
for m in ["Hola, me llamo Ana Inventada, somos 20 familias en San José, mi celular es 399 999 9999",
          "soy Pedro Ficticio del comité, necesitamos arroz",
          "Escribe la señora Rosa Inventada, mi cédula 9.999.999.999",
          "llamen a Luis Prueba al 3999999999 o al correo luis.prueba@example.com",
          "En la casa de doña Rosa hay un abuelo diabético, somos 3 familias",
          "Hay niños enfermos en La Enea, no hay leche",
          "soy maría, vivo en la calle 99 # 99-99 de San José",
          "aquí la familia Gómez Inventada, somos 4 en la carrera 99 # 99-99 de La Enea",
          "Necesitamos leche, pregunten en la casa de Doña Marta Ficticia",
          "atte. Marta Inventada",
          "el fijo es 999 9999"]:
    print(m, "\n  ->", limpiar(m))
FIN
```

<details>
<summary>Script de la purga: base temporal llenada por el flujo real y envejecida 51 días</summary>

Lee la purga del bloque SQL de la sección 4, así que prueba lo que está escrito en este documento.

```bash
python - <<'FIN'
import os, re, tempfile
os.environ.update(DESPACHOX_SIN_RED="1", DESPACHOX_SAL="sal-de-prueba",
                  DESPACHOX_DB=os.path.join(tempfile.mkdtemp(), "prueba.db"))
from datos import db
from entrada.flujo import Mesa
con = db.conectar(os.environ["DESPACHOX_DB"])
m = Mesa(con, elegir=None)                       # sin red, lee el lector por reglas
m.recibir_texto(111, "hola buenos dias")
m.recibir_texto(222, "PEDIDO 40 ARROZ LECHE")
m.recibir_texto(222, "vivo en la casa azul de doña Rosa")
m.recibir_ubicacion(222, 5.0685001, -75.5175001)
m.recibir_texto(333, "PEDIDO 10 SAN JOSE ARROZ"); m.recibir_texto(333, "si")
m.recibir_texto(444, "CIERRE AV DEL CENTRO CAMION")
m.recibir_texto(666, "PEDIDO 8 ARROZ CASA AZUL DE DONA ROSA")
m.recibir_ubicacion(666, 5.0686001, -75.5176001)
con.execute("INSERT INTO paquetes(codigo, pedido_id, kg, estado) VALUES ('DX-7KQ3', 2, 20, 'en_ruta')")
con.execute("UPDATE pedidos SET estado = 'asignado' WHERE id = 2"); con.commit()
m.recibir_texto(222, "ENTREGADO DX-7KQ3")
viejo = "2026-10-01T10:00:00-05:00"              # todo lo anterior queda con 51 días
for t, c in [("pedidos", "creado_en"), ("ubicaciones", "creado_en"), ("cierres", "creado_en"),
             ("lugares", "creado_en"), ("bitacora", "cuando")]:
    con.execute(f"UPDATE {t} SET {c} = ? WHERE {c} > ?", (viejo, viejo))
con.commit()
m.recibir_texto(555, "PEDIDO 5 LA ENEA LECHE")    # de hoy: la purga no lo toca
sql = re.search(r"```sql\n(.*?)```", open("docs/PRIVACIDAD.md", encoding="utf-8").read(), re.S).group(1)
with con:
    for s in filter(str.strip, sql.split(";")):
        con.execute(s, {"limite": "2026-10-22T00:00:00-05:00"})
for q in ["SELECT id, estado, texto_original, remitente_hash FROM pedidos",
          "SELECT tabla, fila_id, texto, lat, lon, metodo FROM ubicaciones",
          "SELECT nombre, lat, lon FROM lugares WHERE origen = 'aprendido'",
          "SELECT nombre, barrio, lat, lon FROM puntos",
          "SELECT id, estado, texto_original FROM cierres",
          "SELECT quien, accion, detalle FROM bitacora"]:
    print(q.split(" FROM ")[1].split()[0], [tuple(r) for r in con.execute(q)])
FIN
```

</details>
