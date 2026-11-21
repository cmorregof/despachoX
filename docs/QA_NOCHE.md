# Revisión QA de la noche

Rama `qa-noche`, sobre `main` en 917b42b. La hizo un agente de Fable entre las 11:30 p. m. del viernes 20 y las 12:30 a. m. del sábado 21, en una copia aparte y con `nice -n 19`, sin tocar la simulación. No se llamó a Telegram, Railway, Anthropic ni Groq. Suma al criterio 2 (funcionamiento) y al 5 (riesgos).

## En cinco líneas

- Railway corre lo mismo que se probó aquí: la suite pasa completa con Python 3.12 y las versiones de hoy, y el arranque no falla sin las variables opcionales.
- Arreglé seis fallas, cada una con su prueba; la del HTML, solo del lado de la entrada. La más visible: con el modelo activo, «ENTREGADO DX-XXXX» por Telegram no registraba la entrega.
- Quedan cuatro riesgos que un jurado técnico puede encontrar y que no se arreglan esta noche: el tablero público sin clave, los códigos de entrega adivinables, el HTML sin escapar en el mapa y los apodos que se aprenden del pin de cualquier chat.
- Antes de cada presentación hay que reiniciar los datos de la nube y luego reiniciar el servicio. En `main` no existe el botón «Reiniciar datos de prueba».
- Carlos decide seis cosas, listadas al final.

## Qué se probó

| Prueba | Resultado |
|---|---|
| Suite en un venv propio con Python 3.12.3 (el Dockerfile usa `python:3.12-slim`) y las versiones de PyPI de las 11:31 p. m. | `main` 917b42b: 342 pasan y 3 se omiten, en 1 min 25 s. Rama `qa-noche`: 378 pasan y 3 se omiten, entre 1 min 20 s y 1 min 36 s |
| Fusión de prueba de `qa-noche` con el `main` de las 12:15 a. m. (2073997, 12 commits más) | Sin conflictos. 379 pasan y 3 se omiten |
| Las 3 que se omiten | Dos de la simulación piden `despacho/cache/manizales.graphml`, que no está en el repositorio. Una mide el extractor real y pide `ANTHROPIC_API_KEY`. Ninguna corre en Railway |
| Dependencias de sistema de zxing-cpp y pypdfium2, con `ldd` | Solo piden `libstdc++.so.6`, `libgcc_s.so.1` y la libc, que ya vienen en `python:3.12-slim` porque `apt` depende de ellas. El Dockerfile no necesita `apt-get`. Aquí no hay Docker para construir la imagen |
| `despliegue/arranque.sh` con base y red vial en una carpeta temporal, sin `TELEGRAM_BOT_TOKEN`, sin `ANTHROPIC_API_KEY` y sin opcionales | Copia la red vial, carga la semilla (15 puntos, 20 pedidos, 450 apodos), avisa que el bot no arranca, y el tablero responde `ok` en `/_stcore/health` a los 3 s |
| `despliegue/local.sh`, el plan B sin red | También responde `ok` a los 5 s, sin bot y sin modelo |
| Tablero con Streamlit 1.67, con AppTest y sin editar `tablero/` | La primera carga no da excepciones (0,6 s). «Calcular plan» deja el plan propuesto en 10 s. En AppTest el clic reejecuta toda la página, y entonces el `st.rerun(scope="fragment")` del tablero da error. En el navegador el clic reejecuta solo el fragmento, así que lo que sigue al clic se verifica allí, como hizo Jacobo |
| Alerta de silencio de punta a punta (`despacho/tests/test_qa_noche.py`) | Pasa. Se crea con `entrada.silencio.revisar`. Sin decisión del despachador, el plan no la ve. Confirmada en el tablero, queda en `resumen.verificar`. Al aprobar no recibe paquete ni pasa a `asignado`. La hoja impresa no la lleva y la vista por territorio no la cuenta |
| Secretos en los 152 commits de las 10 ramas | Ninguno. No hay claves de Anthropic, Groq u OpenAI, ni tokens de Telegram o GitHub. Nunca se versionó un `.env`, `.db` o `.sal` |
| Datos personales en el repositorio | Ningún celular, cédula ni correo real. Los de las pruebas son inventados (`310 555 1234`, `alguien@correo.com`). Las únicas direcciones exactas son de instituciones y vienen de fuentes públicas (Banco de Alimentos, Casa de la Cultura, ICBF) |
| Consultas SQL | Todas usan `?`. Las que arman texto solo ponen nombres de tabla fijos del código o listas de `?` |
| Registros y privacidad del bot | El remitente es un HMAC-SHA256 con sal. El audio no se guarda. Los registros de errores solo escriben el tipo de excepción. El QR lleva solo el código del paquete |

## 1. Bloquea la demo o la puede romper

### 1.1 ENTREGADO por Telegram no se registraba con el modelo activo. Arreglado

En la nube el bot lee con el modelo. Pero el esquema que devuelve el modelo (`Lectura`, en `entrada/extraer.py`) no tiene campo para un código de paquete. Por eso «ENTREGADO DX-7K2Q» salía como `otro`: el bot contestaba «No entendí…» y el paquete seguía `en_ruta`. Solo funcionaba por SMS, sin red o cuando el modelo fallaba. Y la hoja impresa le dice al conductor que registre la entrega «por el bot», mientras el guion del pitch trae la trazabilidad con QR como bloque opcional.

Arreglo en `Mesa.leer` (`entrada/flujo.py`). Un mensaje que trae un código DX, o que empieza por «entreg», lo lee primero la regla. Si la regla ve una entrega, no se llama al modelo; si no, el mensaje sigue al modelo como antes. Pruebas: `test_entregado_por_telegram_queda_registrado_sin_pasar_por_el_modelo`, con cuatro formas de escribirlo, y `test_un_pedido_normal_sigue_yendo_al_modelo`.

### 1.2 Un pin de cualquier chat cambia la respuesta clave de la demo

`lugares.corregir_con_pin` aprende el apodo con las coordenadas que manda cualquier remitente (`lugares/nomenclator.py:249` y `:258`). Lo medí con la semilla. Un chat escribe «derrumbe en la avenida del centro» y manda una ubicación en Bogotá. Desde ese momento, el mensaje del jurado ya no recibe «Ubiqué «avenida del centro» en: avenida del Centro (via). ¿Es correcto?» con el botón «Sí, es ahí». Recibe «No estoy seguro de dónde queda… ¿Es alguno de estos?», con dos opciones casi iguales, y una de ellas está en Bogotá. Además, pasa sin mala fe: basta con que en un ensayo alguien toque «Enviar mi ubicación» en vez de «Sí».

Para mañana: reiniciar los datos justo antes de la demo, porque eso vacía `lugares` y `ubicaciones` y recarga el nomenclátor. Y en los ensayos, tocar siempre «Sí, es ahí». Arreglo propuesto para Carlos: que solo el pin del despachador enseñe apodos, o que el apodo aprendido de un remitente no compita con uno de la semilla. No lo hice porque cambia el diseño de `lugares/`. Se repite con `python docs/qa_noche/envenenar.py`.

### 1.3 Las alertas de silencio salen solas pocas horas después de reiniciar

El bot revisa el silencio cada 10 minutos. Con la semilla, los tres albergues críticos reciben su alerta así, contando desde la carga: Arrayanes a las 3 h 4 min, San Jorge a las 3 h 56 min y Campohermoso a las 5 h 41 min. Si se reinicia a las 8:00 a. m., en el pitch ya estarán las tres en «Por revisar» y en el contador de pendientes. No rompen el plan, porque no se rutean ni se surten. Pero aparecen sin que nadie las espere. Decide Carlos: reiniciar menos de 3 horas antes de cada presentación, subir `DESPACHOX_SILENCIO_HORAS` en Railway o mostrar una alerta a propósito.

### 1.4 No existe el botón «Reiniciar datos de prueba»

No está en `tablero/app.py` de `main` ni en ninguna de las 10 ramas remotas; Fable lo corrigió en el canal a las 12:12 a. m. Si el rediseño de Jacobo no lo trae, hay dos vías. La del canal: poner `DESPACHOX_REINICIAR=1` en Railway, esperar el redespliegue y quitar la variable. La del viernes a las 4:55 p. m.: `railway ssh -- 'python -m despacho.semilla --cargar --reiniciar'`, que no redespliega.

Con la segunda vía hay que reiniciar después el servicio en Railway. El bot guarda en memoria las conversaciones a medias, y como los ids vuelven a empezar tras el borrado, una conversación vieja puede confirmar la ubicación del reporte nuevo de otra persona. La primera vía ya reinicia el bot. En las dos, el guion cuenta con que el pedido nuevo sea el 21: nadie debe escribirle al bot entre el reinicio y la demo.

### 1.5 Railway instalaba la última versión de cada paquete. Arreglado en un commit aparte; decide Carlos

`requirements.txt` no fija versiones, y cada push a `main` reconstruye la imagen. Así, un paquete publicado el sábado (Streamlit, OR-Tools o python-telegram-bot) cambiaría lo que corre en la demo sin que nadie lo pruebe. El commit 341aa81 añade `despliegue/restricciones.txt`, con los 73 paquetes del venv donde pasaron las pruebas, y el Dockerfile instala con `-c restricciones.txt`. Prueba: un venv limpio se instaló con esas restricciones en 21 s, `pip check` no dio errores, quedaron las mismas versiones y pasaron las 378 pruebas. Si una rama de la mañana trae una dependencia que choque, el build falla y sigue el despliegue anterior. Para no tomarlo: `git revert 341aa81`.

## 2. Riesgo ante el jurado

### 2.1 El tablero es público, no pide clave y su dirección está en un repositorio público

GitHub reporta el repositorio como público, y `README.md:113` publica la dirección del tablero. Con ella, cualquiera puede aprobar o rechazar planes, confirmar cierres, descartar pedidos y escribir cualquier nombre en «Despachador». `docs/DESPLIEGUE.md` ya lo advierte. Arreglo propuesto para Jacobo, después de su fusión, porque es un arreglo y no una función: una clave por variable de entorno al comienzo de `main()` en `tablero/app.py`.

```python
import hmac, os

def clave_ok() -> bool:
    clave = os.environ.get("DESPACHOX_CLAVE_TABLERO")
    if not clave or st.session_state.get("clave_ok"):
        return True
    dada = st.text_input("Clave del tablero", type="password")
    if dada and hmac.compare_digest(dada.encode(), clave.encode()):
        st.session_state["clave_ok"] = True
        st.rerun()
    return False
# en main(), antes de mesa():   if not clave_ok(): st.stop()
```

Sin la variable, el tablero sigue como hoy. Mientras tanto, la respuesta para el jurado: «En el piloto, el tablero va detrás de una clave y en la red del acopio. Hoy es una demostración con datos inventados».

### 2.2 ENTREGADO: cualquiera con el código lo marca, y el código se puede adivinar

- El código es «DX-» más 4 signos de un alfabeto de 25 (`despacho/paquetes.py:25` y `:36`). Eso da 390.625 códigos, es decir 18,58 bits. Se genera con `secrets`, se comprueba único contra todos los paquetes de la base y sirve una sola vez. Además, «no existe» y «ya se entregó» reciben la misma respuesta.
- Lo puede marcar cualquier chat de Telegram, cualquier SMS que entre por la pasarela y la línea de órdenes. El tablero no tiene botón de entrega. La bitácora guarda «remitente» y 8 caracteres del hash.
- No hay límite de intentos. Medí la pasarela sin token, con un solo cliente, `nice -n 19` y la simulación usando los dos núcleos: entre 1.401 y 2.058 intentos por segundo en dos corridas. Recorrer todos los códigos toma entre 3,2 y 4,6 minutos. Con 20 paquetes en ruta, el primer acierto llega en unos 10 a 15 segundos; en una corrida de 10 segundos acertó 2. Por Telegram no lo medí. Con 20 paquetes en ruta, el primer acierto pide unos 19.500 intentos en promedio.
- Una entrega marcada no se puede deshacer, y el pedido sale del plan: quien pidió deja de aparecer como pendiente.
- El lector de SMS, además, marcaba como entrega un reclamo como «no ha llegado el paquete DX-7K2Q». Eso ya está arreglado (punto 2.5).

Arreglo propuesto para el piloto, que Samuel tiene en el encargo P2: ENTREGADO solo cuenta si viene del chat que hizo el pedido o de un conductor registrado, y lo demás queda «por confirmar» para el despachador. A eso se suman un tope de intentos fallidos por remitente, códigos de 6 signos (244 millones) y un «deshacer entrega» en el tablero. Para mañana: si se muestra la pasarela de SMS, definir `DESPACHOX_SMS_TOKEN` antes de `--registrar`. Se repite con `python docs/qa_noche/fuerza_bruta.py`.

### 2.3 El mapa del tablero pinta el HTML que llega por chat. Mitigado en la entrada

folium 1.0 no escapa el texto de los tooltips. Lo comprobé: `tooltip="<img src=x onerror=alert(1)>"` queda tal cual en la página. Y varios tooltips llevan texto del remitente o del modelo. Son el lugar de un cierre ubicado con pin (`tablero/app.py:185`), el texto de la propuesta de ubicación (`:192`) y los nombres de puntos y alternativas que se aprenden de ese texto (`:162`, `:175` y `:197`). El mapa corre en un iframe del mismo origen, así que un script ahí puede operar el tablero.

Mitigación hecha: `privacidad.limpiar` quita «<» y «>» de todo lo que llega por chat, voz o SMS, y `extraer._normalizar` los quita del lugar y la descripción que devuelve el modelo. Con eso, tampoco se puede cerrar la etiqueta `<mensaje>` del prompt. Son 3 pruebas, y las tres fallan con el código anterior. Falta el arreglo de fondo, para Jacobo: `html.escape(...)` en esos tooltips. Pasa algo parecido, aunque menor, con el Markdown. `st.caption` y `st.markdown` muestran los enlaces y las imágenes que escriba un remitente (`tablero/app.py:321`, `:323`, `:372`, `:402` y `:417`). Se resuelve mostrando ese texto con `st.text` o entre comillas invertidas.

### 2.4 Botones forjados. Arreglado el que cambia cantidades

Un cliente de Telegram modificado puede mandar cualquier dato de botón. Con `f:<pedido>:<n>`, cualquier chat fijaba las familias de cualquier pedido nuevo o confirmado, con cualquier número. Medido: 99.999 familias con 199.998 kg, o −3 familias. Arreglo en `Mesa.pulsar`: el botón solo vale para el chat que hizo el pedido, y con 0 < n ≤ 2.000, el mismo tope que ya tenía un número escrito. Son 5 pruebas, y 4 fallan con el código anterior.

Queda el mismo problema, con menos efecto, en `s:` y `c:`: otro chat puede confirmar la ubicación propuesta de un reporte ajeno. Solo puede elegir entre los candidatos que ofreció el sistema, y el despachador igual confirma el pedido. Para los pedidos se arregla comparando `remitente_hash`; los cierres no guardan remitente.

### 2.5 El lector de SMS perdía pedidos y marcaba reclamos como entregas. Arreglado

Un código sin «DX» se aceptaba en cualquier mensaje que empezara por «entrega», y palabras como «enea» o «para» caben en el alfabeto de los códigos. Medido: «entrega de mercado en la enea» se leía como ENTREGADO DX-ENEA, el bot contestaba «No encontré un paquete…» y el pedido no se guardaba. Además, un código DX en cualquier mensaje contaba como entrega, así que «no ha llegado el paquete DX-7K2Q» y «todavía no nos han entregado…» cerraban el paquete.

Arreglo en `entrada/sms.py`. Un código sin «DX» solo vale en un mensaje de hasta 3 palabras. Sin palabra clave, solo cuenta el código solo, como queda al pegar el QR. Y una negación antes de «entregado» manda el mensaje al despachador. Son 13 pruebas, y 7 fallan con el código anterior. Los 20 SMS de la tabla de Samuel se siguen leyendo bien. Esto también importa en la nube, porque cuando el modelo falla el bot cae al lector de SMS.

### 2.6 La pasarela de SMS se colgaba con entradas malformadas. Arreglado

El receptor atiende con un solo hilo y no tenía tiempo de espera. Por eso un `Content-Length: -1`, o un cliente que anuncia un cuerpo y no lo manda, lo dejaba colgado para todos los demás SMS. Un JSON que no es objeto cortaba la conexión sin respuesta. Y `--registrar` no ponía el token en la dirección del celular, así que quien definiera `DESPACHOX_SMS_TOKEN` recibía 401 en cada SMS.

Arreglos: 400 para un JSON que no es objeto y para un `Content-Length` inválido, 15 s de espera por conexión, el token comparado con `hmac.compare_digest` y añadido al registrar, y un aviso al arrancar sin token. Son 8 pruebas: con el código anterior fallan 7 y una se cuelga. La pasarela no corre en Railway, solo en el portátil del acopio.

### 2.7 Ley 1581: la ubicación que manda un remitente se guarda con precisión de un metro

El pin de Telegram puede ser la casa de quien pide. Se guarda en `ubicaciones`; en `lugares`, donde otros lo ven como alternativa; en la bitácora con 5 decimales, y como punto en el mapa público. No lleva nombre ni teléfono al lado, solo el hash del chat. Propuesta para el piloto: redondear a 3 decimales (unos 110 m) lo que se guarda en `lugares` y en la bitácora, o llevarlo al punto de entrega conocido más cercano. Para el jurado: «El pin solo sirve para ubicar el punto de entrega. No guardamos teléfono ni nombre».

## 3. Deuda

- **Silencio: la definición única del canal todavía no coincide con el código.** Hay tres lugares que lo calculan.
  - (a) `entrada/silencio.py` es la alerta operativa: un punto crítico sin un pedido de origen `mensaje` en 6 h, contadas desde las 06:00 si nunca escribió. Es la única que escribe, una fila en `pedidos`.
  - (b) `silencio()` en `despacho/territorio.py:175` es una lista de cobertura: barrios y veredas del nomenclátor sin pedidos en el periodo. Solo lee.
  - (c) `triage/debiles.py`, en el prototipo de triage, que no está conectado al bot ni al tablero. En `main` usa una prueba de Poisson (`:19`); en la rama `jacobo-silencio`, sin fusionar, ya usa las 6 h y la de Poisson solo ordena.

  A las 11:30 p. m. el canal acordó una sola definición, con (a) como fuente: 6 h sin un pedido de origen `mensaje` con lugar confirmado, desde la más tardía entre las 06:00 y la hora del evento. Debe mandar (a), porque es la única que crea alertas, la que aparta el optimizador (`despacho/optimizar.py:306`) y la que se prueba de punta a punta. Pero quedan tres diferencias. Primera: ¿cuenta como contacto un mensaje descartado? (a) dice que sí, porque cuenta cualquier estado (`entrada/silencio.py:58`). (b) dice que no, y tampoco cuenta duplicados (`despacho/territorio.py:105`). (c) en `jacobo-silencio` dice que no, aunque su docstring dice «igual que entrada/silencio.py». Efecto: si el despachador descarta el único mensaje de un albergue, la alerta se apaga 6 horas y el albergue sigue «sin pedidos registrados». Segunda: (a) cuenta desde las 06:00 y no mira la hora del evento. Tercera: (b) no usa el umbral de 6 h, sino el periodo que se le pide. Propuesta: que Carlos decida si un descarte cuenta como contacto y que (a) lo siga; es una condición en la consulta de `entrada/silencio.py:58`, más su prueba. Y que (b) se presente como «sin pedidos registrados en el periodo», que es lo que mide.
- El tablero cuenta las alertas de silencio en «Pedidos pendientes» (`tablero/datos.py:260`). Una vez confirmadas, solo aparecen como aviso en «Plan en detalle»: falta mostrar `resumen.verificar`, como pidió el canal a las 11:15 p. m.
- Mensajes internos a la vista. Si el optimizador falla, el plan vacío dice «error interno: Tipo: mensaje» (`despacho/optimizar.py:592`) y el tablero lo muestra (`tablero/app.py:262`). También muestra la última línea de error del subproceso (`tablero/datos.py:368`). No llevan datos personales, pero pueden mostrar rutas del servidor.
- La hoja impresa dice que las entregas se registran también «en el tablero» (`despacho/hoja.py:50`), y el tablero no tiene cómo. Hay que agregar el botón o quitar la frase.
- El bot no limita los mensajes por chat, y cada mensaje que no es una entrega llama al modelo. El costo por mensaje es bajo, pero es una vía de gasto.
- El lector de SMS toma solo el primer código de un mensaje que trae varios.
- `railway.toml` reintenta 5 veces. Después de 5 caídas seguidas, el servicio queda abajo hasta que alguien lo reinicie.
- `entrada/pruebas/test_sms.py` reescribe `entrada/pruebas/reporte_sms.md` en cada corrida: si cambia un resultado, la suite deja un archivo modificado.
- Los teléfonos de prueba (`310 555 1234`) tienen forma de celular real. Son inventados y el filtro los quita, pero conviene un patrón que no pueda existir.
- El mensaje del commit 516154b dice que con el código anterior fallan 6 pruebas de la pasarela. Son 7 y una se cuelga, como dice este informe.

## 4. Pasos para la mañana

1. **8:00 a. m., fusión.** Incluir `qa-noche` y decidir si entra el commit 341aa81 (versiones fijas). Correr `python -m pytest -q`: con la rama, 378 pasan y 3 se omiten. Samuel revisa los cambios en sus archivos de `entrada/` (sección 6).
2. **Registros de Railway después del despliegue.** Deben verse la red vial, los datos, «Bot en marcha» y la dirección de Streamlit, y no debe aparecer `Conflict: terminated by other getUpdates`. Nadie corre el bot local con el token de producción.
3. **Después de la última fusión,** desactivar el despliegue automático (`docs/DESPLIEGUE.md`).
4. **Antes de cada presentación, pulsar «Reiniciar datos de prueba».** Si el tablero de Jacobo no trae ese botón, poner `DESPACHOX_REINICIAR=1` en Railway, esperar el redespliegue y quitar la variable. Si se reinicia por `railway ssh`, hacer después «Restart» del servicio, para que el bot olvide las conversaciones viejas (punto 1.4). Hacerlo menos de 3 horas antes de la presentación, o ajustar `DESPACHOX_SILENCIO_HORAS` (punto 1.3).
5. **Entre el reinicio y la demo, nadie le escribe al bot de la nube.** El guion cuenta con que el pedido nuevo sea el 21 y con que nadie haya enseñado apodos.
6. **En los ensayos, tocar «Sí, es ahí»** para el cierre de la avenida del Centro, nunca «Enviar mi ubicación». Si se ensaya en la nube, reiniciar otra vez antes del pitch.
7. **Si se muestra la trazabilidad con QR:** con `qa-noche` fusionada, «ENTREGADO DX-XXXX» por Telegram registra la entrega. Probarlo una vez con un código de la hoja impresa.
8. **Si se muestra la pasarela de SMS:** definir `DESPACHOX_SMS_TOKEN` antes de `python -m entrada.pasarela_sms --registrar`.
9. **La dirección del tablero no se comparte** fuera del equipo y del jurado. Si Jacobo agrega la clave, definir `DESPACHOX_CLAVE_TABLERO` en Railway.

## 5. Decisiones para Carlos

1. ¿Entra el commit 341aa81, que fija las versiones que instala Railway?
2. ¿A qué hora se reinician los datos? ¿O se sube `DESPACHOX_SILENCIO_HORAS`, o se muestra una alerta de silencio a propósito?
3. ¿Se le pone clave al tablero mañana (Jacobo, unas 10 líneas), o se acepta el riesgo y se responde con el plan del piloto?
4. Para el piloto: ¿ENTREGADO solo desde el destino o desde un conductor registrado, con tope de intentos y códigos de 6 signos?
5. Para el piloto: ¿los pines de los remitentes enseñan apodos? ¿Se redondean a unos 100 m?
6. ¿Un mensaje descartado cuenta como contacto para la alerta de silencio? Hoy `entrada/silencio.py` dice que sí, y territorio y triage dicen que no (sección 3).

## 6. Archivos de esta rama

| Archivo | Qué cambió |
|---|---|
| `entrada/flujo.py` | ENTREGADO lo lee la regla antes que el modelo; el botón `f:` solo vale para quien hizo el pedido y con tope |
| `entrada/sms.py` | Código sin «DX» solo en mensajes cortos; sin palabra clave, solo el código solo; una negación antes de «entregado» va al despachador |
| `entrada/pasarela_sms.py` | 400 para un JSON que no es objeto y para un `Content-Length` inválido; 15 s de espera; token con `compare_digest` y en el registro; aviso sin token |
| `entrada/privacidad.py` y `entrada/extraer.py` | Sin «<» ni «>» en lo que entra ni en lo que devuelve el modelo |
| `entrada/pruebas/test_qa_noche.py` | 34 pruebas de lo anterior |
| `despacho/tests/test_qa_noche.py` | El silencio de punta a punta y las propiedades del código del paquete (2 pruebas) |
| `Dockerfile` y `despliegue/restricciones.txt` | Versiones fijas para Railway, en el commit aparte 341aa81 |
| `docs/qa_noche/fuerza_bruta.py` y `docs/qa_noche/envenenar.py` | Las dos mediciones de este informe, para repetirlas |
| `.gitignore` | `*.pkl`: si `DESPACHOX_GRAFO` apunta a la copia del repositorio, como hace `demo/preparar.py` en `demo-noche`, `despacho/red.py` deja al lado un caché de 6,5 MB que `git add -A` subiría |

Ningún cambio toca `tablero/`, `despacho/sim/`, `docs/SIMULACION.md`, el optimizador, el `/start` ni los textos del bot. Los arreglos de `entrada/` están en archivos de Samuel, así que conviene que los vea antes de su próxima fusión.
