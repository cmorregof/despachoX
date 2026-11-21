# 09 · Canales para pedir ayuda sin internet

Hackathon UNAL Manizales 2026 · Equipo 19 DespachoX · Vertical 04 «Logística y abastecimiento». Fuentes consultadas el 20 de noviembre de 2026. Agente 7, para revisión del coordinador.

**Marcas.** Cada dato lleva una. **[F]**: lo dice una fuente o una medición publicada, enlazada. **[C]**: cálculo nuestro a partir de datos [F]. **[S]**: supuesto o propuesta nuestra, sin medir. **[NV]**: no verificado. Los pesos son cálculos con la TRM del 20 de noviembre de 2026, 3.415,10 COP por dólar ([datos.gov.co](https://www.datos.gov.co/resource/32sa-8pi3.json)) [F]. Ningún precio incluye envío, arancel ni IVA de importación [NV].

## Resumen

- **SMS** es el primer respaldo realista. En agosto la red de Caldas quedó dañada pero viva, y MinTIC recomendó mensajes de texto cuando la voz se congestiona.
- **Meshtastic** es viable para un piloto acotado: nodos fijos en albergues, comedores y juntas, cada uno con un responsable entrenado. No sirve como canal para el público general.
- **Malla por Bluetooth** no sirve como canal de DespachoX: unos 100 m de alcance, instalación previa obligatoria y ninguna forma documentada de llevar el mensaje al sistema sin redigitarlo.
- **Radio VHF** ya la operan los organismos de socorro y los radioaficionados. DespachoX solo necesita un formulario con el formato del SMS y una casilla de digitación que use el mismo lector.
- **Emisoras** sirven de salida: un boletín por barrio sacado del plan aprobado.
- Todo canal de entrada termina en el mismo lector de `entrada/`. Proponemos una sola puerta que reciba canal, remitente y texto.

## 1. Qué pasó con la red en agosto

El estado de la red después del sismo decide qué canal va primero, porque el SMS solo sirve donde queda una antena.

- La mañana del 11 de agosto, MinTIC reportó 3.403 de 7.379 estaciones base sin servicio en siete departamentos, un 46,1 %. En Caldas, el 28 % ([Noticias RCN, 11-ago-2026](https://www.noticiasrcn.com/colombia/senal-movil-en-colombia-46-esta-afectada-1049064)) [F].
- Las causas fueron tres: congestión de voz, cortes de energía que agotaron baterías y plantas, y daño físico en estaciones ([Noticias RCN, 11-ago-2026](https://www.noticiasrcn.com/tendencias/temblor-colombia-senal-caida-por-que-1049139)) [F].
- La CRC recordó que, ante congestión de voz, los operadores deben priorizar SMS y mensajería instantánea ([Noticias RCN, 11-ago-2026](https://www.noticiasrcn.com/colombia/senal-movil-en-colombia-46-esta-afectada-1049064)) [F].
- MinTIC recomendó «usar mensajes de texto o servicios de mensajería instantánea». También pidió apoyo a radioaficionados y a la banda ciudadana, en coordinación con la UNGRD, y dijo que todas las emisoras de Radio Nacional seguían al aire ([MinTIC, actualizado 13-ago-2026](https://www.mintic.gov.co/portal/715/w3-article-440280.html)) [F].
- El 13 de agosto, Claro tenía cerca del 80 % de sus estaciones base funcionando ([Infobae, 13-ago-2026](https://www.infobae.com/tecno/2026/08/13/avanza-un-80-la-reparacion-de-infraestructura-de-telecomunicaciones-en-zonas-afectadas-por-el-terremoto-en-colombia-claro-y-tigo-afectadas/)) [F].

Si el 28 % de las estaciones de Caldas estaba caído, el 72 % seguía en pie [C]. Así que la red celular de Caldas siguió viva aunque congestionada, y los dos primeros canales de DespachoX (Telegram y SMS) son los mismos que recomendó MinTIC.

## 2. Tabla comparativa

La primera tabla compara lo que cuesta y lo que alcanza cada canal. La segunda, lo que se pierde y cómo entra el mensaje a DespachoX. El detalle y las fuentes están en las secciones 3 a 7.

| Canal | Costo (fecha y moneda) | Alcance | Hardware | Quién lo opera |
|---|---|---|---|---|
| SMS con pasarela Android | Prepago Claro de 7 días con SMS nacionales ilimitados: 10.000 COP, oferta del 29-oct al 30-nov-2026 [F]. App de pasarela gratuita y abierta [F]. El celular, el que haya [S] | Lo que quede de cobertura celular. Nada más | Un Android 5.0 o superior con SIM, cargador y wifi local compartido con el portátil [F] [S] | El despachador en el acopio. Quien pide usa cualquier celular |
| LoRa con Meshtastic | Desde 17,90 USD por nodo Heltec V3, unos 61.130 COP (20-nov-2026) [F] [C]. Con GPS: 39,90 USD, unos 136.262 COP [F] [C] | Medido en ciudad: hasta 1,2 km con 92 % de entrega [F]. En Manizales, sin medición [NV] | Un nodo por punto, uno en el acopio por USB y repetidores en puntos altos con energía propia | Responsables de punto entrenados, el despachador y el equipo de conectividad para los repetidores [S] |
| Malla por Bluetooth | App gratuita. Bridgefy vende extras de 0,99 a 29,99 USD [F] | Unos 100 m [F] | Celulares con la app instalada antes del desastre [F] | Cada vecino |
| Radio VHF de socorro | Equipos de los organismos y de los radioaficionados [NV]. Para DespachoX, una persona en el acopio [S] | Depende de las repetidoras. La Liga Radio Manizales tiene una en el Cerro El Recreo [F] | Radios y repetidoras existentes | Defensa Civil, Cruz Roja, bomberos y radioaficionados [F parcial] [NV] |
| Emisora (salida) | Sin dato [NV] | Toda la ciudad con radios de pilas [S] | Los radios de los hogares | La emisora. El despachador aprueba el texto [S] |

| Canal | Qué se pierde | Cómo entra a DespachoX |
|---|---|---|
| SMS | La ubicación precisa (solo llega el nombre del lugar), los botones, la entrega a tiempo, y espacio: 160 caracteres, 70 si lleva á, í, ó o ú [F] | El portátil consulta los SMS recibidos del celular por la red local, los pasa al lector por reglas y responde por el mismo celular [S] |
| Meshtastic | Los botones, los mensajes de más de 200 bytes, la confirmación en mensajes a todo el canal y la ubicación si el nodo no tiene GPS [F] | Un receptor en el portátil escucha el nodo por USB y entrega el texto al mismo lector. Responde con un mensaje directo con acuse [F] [S] |
| Malla por Bluetooth | Todo vínculo con DespachoX. En Bridgefy, además, la autenticidad del remitente [F] | Solo si alguien lee el pedido y lo reenvía por SMS o lo digita [S] |
| Radio VHF | El registro automático, la ubicación salvo lo que se diga, y se suman errores de transcripción | Un operador transcribe con el formato del SMS y lo digita en el tablero, que usa el mismo lector [S] |
| Emisora | La confirmación de que alguien oyó | No entra: sale. Boletín por barrio desde el plan aprobado [S] |

## 3. SMS con pasarela Android

El SMS es el respaldo con más gente ya equipada, porque cualquier celular lo envía sin datos. Lo que hay que resolver es cómo llega del celular del acopio al portátil sin internet.

### Aplicaciones de pasarela

- **SMS Gateway for Android** (capcom6). Licencia Apache-2.0, Android 5.0 o superior, unas 5,9 mil estrellas en GitHub ([GitHub](https://github.com/capcom6/android-sms-gateway)) [F]. Su modo de servidor local funciona en el mismo wifi sin acceso a internet, con autenticación básica ([documentación](https://docs.sms-gate.app/getting-started/local-server/)) [F]. En ese modo se envía con `POST /message` y se leen los recibidos con `GET /inbox`, que solo existe en modo local ([lectura de mensajes](https://docs.sms-gate.app/features/reading-messages/)) [F].
- **Sus webhooks exigen HTTPS.** La única excepción es `http://127.0.0.1`. Una IP privada como 192.168.x.x necesita un certificado de confianza ([FAQ de webhooks](https://docs.sms-gate.app/faq/webhooks/)) [F]. Existe una versión «insecure» que acepta HTTP, pensada solo para redes de confianza [F]. Para operar aislado hay que apagar «Require Internet connection» en los ajustes de webhooks [F]. Si el receptor no contesta, reintenta 14 veces con espera creciente, unos dos días ([webhooks](https://docs.sms-gate.app/features/webhooks/)) [F].
- **Se instala desde el APK de GitHub.** En Android 15 o superior, Play Protect puede bloquearlo, y la documentación indica apagar su escaneo durante la instalación ([instalación](https://docs.sms-gate.app/installation/)) [F]. Así que el celular de la pasarela se prepara antes de la emergencia [S].
- **android_income_sms_gateway_webhook** (bogkonstantin; licencia MIT, en F-Droid). Reenvía cada SMS recibido como JSON por HTTP y tiene un modo de red local sin internet ([GitHub](https://github.com/bogkonstantin/android_income_sms_gateway_webhook)) [F]. No menciona enviar respuestas [F], así que sola no basta.

**Propuesta.** El portátil consulta `GET /inbox` del celular cada 5 a 10 segundos y responde con `POST /message` [S]. Así no hace falta certificado, porque es el portátil quien llama al celular por HTTP en la red local; los ejemplos de la documentación usan `http://<ip-del-celular>:8080` [F]. El wifi puede ser el punto de acceso del propio celular o un enrutador con batería [S]. Falta probarlo con un celular real [NV]. Esto complementa el encargo A3, que pide el receptor y su `SMS.md`.

### Costo del plan en Colombia

- Claro prepago «Todo Incluido» trae SMS nacionales ilimitados a cualquier operador móvil del país: 3.000 COP por 1 día, 10.000 COP por 7 días con 2 GB y 100.000 COP por 30 días con 80 GB. La oferta va del 29 de octubre al 30 de noviembre de 2026 ([condiciones de Claro](https://www.claro.com.co/portal/co/recursos_contenido/pdf/Terminos-condiciones-paquetes-prepago-todo-incluido.pdf)) [F]. El plan de 7 días equivale a unos 2,93 USD [C].
- Las mismas condiciones dicen que el paquete «NO puede ser utilizado para envío de mensajes de texto SMS originados de manera masiva» desde servidores o sistemas, ni con fines comerciales. El spam puede terminar el contrato [F].
- Una pasarela que contesta cada pedido no es publicidad, pero sus respuestas salen de un sistema. Por eso conviene acordar el uso con el operador antes del piloto [S].
- En pospago, el plan más barato de cada operador traía voz y SMS ilimitados en marzo de 2025: WOM 35.990 COP al mes, Claro 44.900, Tigo 45.900 y Movistar 56.990 ([Enter.co, 21-mar-2025](https://www.enter.co/colombia/planes-moviles-pospago-mas-economicos-por-operador-en-colombia-cual-es-el-mejor-relacion-costo-beneficio)) [F]. Son precios de hace 20 meses; los de hoy de Tigo, Movistar y WOM no los verifiqué [NV].

### Límites de envío

- Android advierte al usuario cuando una app intenta enviar 30 o más SMS en un minuto, según un cambio de 2012 en el código de Android ([AOSP](https://android.googlesource.com/platform/frameworks/opt/telephony/+/e7fd4f7%5E%21/)) [F]. Si cada fabricante conserva ese valor: no verificado.
- Así que un celular pasarela contesta como mucho unos 30 pedidos por minuto sin que alguien toque la pantalla [C]. La app permite restringir los envíos por periodo y desaconseja los envíos por lotes por las restricciones de los operadores ([GitHub](https://github.com/capcom6/android-sms-gateway)) [F]. Conviene fijar un límite menor [S].
- Un SMS lleva 160 caracteres en el alfabeto GSM de 7 bits. Ese alfabeto incluye é, ñ y ü, pero no á, í, ó ni ú. Una sola de esas letras pasa el mensaje a UCS-2 y el límite baja a 70 caracteres ([GSM 03.38, Wikipedia](https://en.wikipedia.org/wiki/GSM_03.38)) [F]. Existe una tabla de extensión para español que agrega esas letras [F], pero no sé si los celulares y operadores de Colombia la usan [NV]. Por eso las respuestas de DespachoX deben evitar á, í, ó y ú: «Recibido: 40 fam San José» se queda en 160, en cambio una palabra como «ubicación» baja el límite a 70 [C].

### Red saturada pero viva

- Un informe de 2005 patrocinado por la GSMA concluyó que los SMS tienen más probabilidad de pasar en una emergencia, porque usan menos capacidad y pueden quedar en cola hasta que haya espacio ([Enlightenment Economics para la GSMA, 2005](https://www.itu.int/en/ITU-D/Emergency-Telecommunications/Documents/ET-OnlineToolkit/bp/The%20Role%20of%20Mobiles%20in%20Disasters%20and%20Emergencies%20%E2%80%93%20%E2%80%9805.pdf)) [F]. El informe no trae cifras de demora [F].
- En agosto de 2026, la CRC y MinTIC pidieron priorizar SMS y mensajería instantánea (sección 1) [F].
- Como el SMS puede quedar en cola, un pedido puede llegar tarde o después de uno posterior [C]. El tablero debe mostrar la hora de recepción y el lector no debe suponer orden [S].
- MinTIC informó que la ANE definía una banda para un servicio satelital temporal directo al celular ([MinTIC](https://www.mintic.gov.co/portal/715/w3-article-440280.html)) [F]. Si llega a funcionar, esos SMS caen en la misma pasarela y DespachoX no cambia [S].

### Qué se pierde y cómo entra

- Se pierde la ubicación precisa: el SMS no trae pin, así que el lugar sale del nomenclátor [S]. Se pierden los botones: la respuesta pide «SI» o el barrio correcto, como ya prevé el encargo A3. El número del remitente se guarda como hash, igual que el chat de Telegram (A3) [F, repositorio].
- Ruta: celular pasarela, portátil (consulta `GET /inbox`), `leer_sms` por reglas (encargo A3), `Mesa.atender`, texto de respuesta y `POST /message` [S].

## 4. LoRa con Meshtastic

Meshtastic es un firmware abierto que convierte radios LoRa baratos en una malla de mensajes de texto, sin operador y en una banda de uso libre. Su ventaja es el precio y la banda; su incógnita, el alcance en una ciudad de montaña.

### Precio de un nodo

- **Heltec WiFi LoRa 32 V3**: de 17,90 a 19,90 USD en la [tienda oficial](https://heltec.org/project/wifi-lora-32-v3/) [F], unos 61.130 a 67.960 COP [C]. En [Rokland](https://store.rokland.com/collections/heltec-products/products/heltec-wifi-lora-32v3), distribuidor en EE. UU.: 26,97 USD sin carcasa y 29,97 USD con carcasa, con antena y sin batería [F].
- **SenseCAP T1000-E** (Seeed): 39,90 USD, con GPS, batería de 700 mAh, IP65, un botón y sin pantalla ([Seeed](https://www.seeedstudio.com/SenseCAP-Card-Tracker-T1000-E-for-Meshtastic-p-5913.html)) [F]. Unos 136.262 COP [C].
- **LILYGO T-Deck Plus**: 77,16 USD, con teclado, GPS y batería de 2.000 mAh. La versión de 915 MHz aparecía agotada ([LILYGO](https://lilygo.cc/products/t-deck-plus-meshtastic)) [F]. Unos 263.509 COP [C].
- **Precio en tiendas colombianas: no verificado.** MercadoLibre Colombia y Vistrónica no permitieron la consulta automática, y la categoría LoRa de Electronilab no mostró productos.

### Banda y región en Colombia

- La documentación de Meshtastic asigna Colombia a la región ANZ ([región por país](https://meshtastic.org/docs/configuration/region-by-country/)), que va de 915 a 928 MHz; la región US va de 902 a 928 MHz ([configuración LoRa](https://meshtastic.org/docs/configuration/radio/lora/)) [F].
- La Resolución 28 de 2026 de la ANE planeó de 896 a 915 MHz para servicios móviles y fijos. En sus considerandos menciona «dispositivos de uso libre en el segmento superior (915-928 MHz)» ([normograma MinTIC](https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_ane_0028_2026.htm)) [F].
- Así que cada nodo debe quedar en ANZ y no en US [C]. El uso libre no requiere permiso, pero no puede interferir con servicios licenciados (Resolución 105 de 2020, artículos 4.1.2 y 4.1.4, [normograma MinTIC](https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_ane_0105_2020.htm)) [F].
- Una propuesta de la ANE de diciembre de 2022 confirma que los dispositivos de uso libre en 915 a 928 MHz se rigen por el Anexo 1 de la Resolución 105 de 2020. Dice también que sus límites de potencia reducen el alcance a cerca de un tercio del que tendría un sistema licenciado ([ANE, propuesta para la banda de 900 MHz](https://www.ane.gov.co/Sliders/archivos/gesti%C3%B3n%20t%C3%A9cnica/Estudios%20de%20gesti%C3%B3n%20y%20planeaci%C3%B3n/900%20MHz/Documentos/PropuestaUsoBanda900MHz.pdf)) [F]. Las potencias exactas del Anexo 1 no las pude abrir [NV].
- La misma propuesta planteaba restringir la importación de dispositivos de uso libre que operen en 902 a 915 MHz [F]. Si eso se adoptó: no verificado. Por eso conviene comprar nodos que declaren 915 a 928 MHz o un rango amplio (el Heltec V3 cubre de 863 a 928 MHz) [F] [S].

### Alcance medido

- **Ciudad.** En Zúrich, una red Meshtastic a 868 MHz con el perfil LongFast alcanzó hasta 1,2 km con 92 % de paquetes entregados ([Khamaisi et al., arXiv 2025](https://arxiv.org/abs/2509.22568)) [F].
- **Ciudad y periferia.** En Castelldefels (España), LoRa perdió la conexión más allá de 1,5 a 2 km. Era LoRaWAN, no Meshtastic ([Sanchez-Vital et al., Sensors 2025](https://www.mdpi.com/1424-8220/25/23/7209)) [F].
- **Ecuador.** Una tesis de la Universidad de Cuenca (2023), sobre un sitio de monitoreo en Saraguro, midió más de 97 % de paquetes recibidos a cerca de 1 km con SF9 y SF10, a 433 MHz ([Gonzales Zapata y González Armijos](https://dspace-test.ucuenca.edu.ec/bitstream/123456789/41515/1/Trabajo-de-Titulaci%c3%b3n.pdf)) [F]. El entorno exacto de esa prueba no lo pude leer [NV]. Su revisión cita un ensayo a 915 MHz en cultivos andinos a 2.910 m de altitud que llegó a 875 m; esa fuente original no la consulté [NV].
- **Montaña con árboles.** Cerca de Trento, con la configuración más rápida, el alcance cayó de 450 a 550 m con línea de vista a 50 a 90 m entre árboles en ladera ([Iova et al., EWSN 2017](https://openpub.fmach.it/bitstream/10449/42132/1/madcom17.pdf)) [F]. Esa configuración es más débil que LongFast, así que el dato es un piso y no una predicción [S].
- **Récords.** 254 km con LongFast a 915 MHz y 331 km con un perfil más lento ([Meshtastic](https://meshtastic.org/docs/overview/range-tests/)) [F]. El enlace del récord de 331 km lleva «mountain_to_mountain» en su dirección [F]. Son enlaces entre cumbres y no sirven para planear una ciudad [S].
- **Banco de pruebas en la banda de 915 MHz de Colombia.** Los perfiles rápidos fallan con 110 a 120 dB de atenuación y el más lento resiste hasta 180 dB ([Hernández Ortiz et al., arXiv 2026](https://arxiv.org/abs/2605.17063)) [F]. Es una medición en enlace guiado, aislada de la propagación, no en campo [F].
- **Manizales: sin mediciones publicadas que yo encontrara** [NV]. Supuesto de diseño, por confirmar con una prueba de campo: 1 km entre nodos en zona construida, y repetidores en puntos altos con línea de vista a los barrios [S].

### Largo del mensaje y capacidad

- La app de Android limita el mensaje a 200 bytes. El límite del paquete en la malla es 233 bytes ([guía de la app](https://meshtastic.github.io/Meshtastic-Android/en/user/messages-and-channels)) [F]. La librería de Python 2.7.11 rechaza más de 233 bytes con el error «Data payload too big» (código de `mesh_interface.py`) [F].
- El límite es en bytes UTF-8, así que cada á o ñ cuenta doble [C]. `PEDIDO 40 SAN JOSE ARROZ LECHE` ocupa 30 bytes [C].
- LongFast transmite a 1,07 kbps ([perfiles de radio](https://meshtastic.org/docs/overview/radio-settings/)) [F]. Un mensaje de 200 bytes ocupa el aire unos 1,5 s y uno de 60 bytes unos 0,45 s, sin contar preámbulo ni retransmisiones [C]. Cada salto retransmite el mensaje al menos una vez, así que un pedido ocupa el canal varias veces [C]. Por eso un canal aguanta los pedidos de decenas de puntos fijos, no los de una ciudad entera [S].

### ¿Quién pide necesita un teléfono con la aplicación?

- En la mayoría de los nodos, sí. El T1000-E se maneja desde la app en un teléfono emparejado [F]. El teléfono habla con el nodo por Bluetooth ([Khamaisi et al.](https://arxiv.org/abs/2509.22568)) [F], así que no necesita señal celular para enviar por la malla [S].
- Hay dos excepciones. El T-Deck Plus trae teclado, pantalla y GPS ([Meshtastic](https://meshtastic.org/docs/hardware/devices/lilygo/tdeck); [LILYGO](https://lilygo.cc/products/t-deck-plus-meshtastic)) [F], y una reseña en la tienda lo describe como un equipo que funciona solo [F, reseña de usuario]. Y el módulo de mensajes predefinidos envía sin teléfono si se conecta una perilla, botones o un teclado I2C; la lista completa cabe en 200 bytes ([mensajes predefinidos](https://meshtastic.org/docs/configuration/module/canned-message/)) [F].
- Propuesta: registrar cada nodo con su punto (junta, albergue, comedor). Así un mensaje predefinido como «PEDIDO URGENTE» ya trae el lugar, porque DespachoX sabe de qué nodo vino [S].

### Confirmación, ubicación y mensajes perdidos

- Los mensajes directos tienen acuse de recibo: la app muestra «Delivered to recipient» y, desde el firmware 2.8.1, una prueba que solo el destinatario puede producir. Los mensajes a un canal solo indican que llegaron a la malla ([guía de la app](https://meshtastic.github.io/Meshtastic-Android/en/user/messages-and-channels)) [F]. Por eso el pedido debe ir como mensaje directo al nodo del acopio, y la respuesta también [S].
- Los nodos con GPS (T1000-E, T-Deck Plus) reportan posición, y la librería la publica en `meshtastic.receive.position` [F].
- Store & Forward guarda unos 11.000 mensajes y los reenvía a quien estuvo fuera de alcance. Solo lo hacen nodos ESP32 con PSRAM, como el T-Beam, y no funciona en el canal público por defecto ([Store & Forward](https://meshtastic.org/docs/configuration/module/store-and-forward-module/)) [F].

### Seguridad y roles

- Las claves de los canales por defecto vienen en el código fuente, así que cualquiera puede leer esos mensajes. Para comunicación privada, la documentación indica una clave aleatoria de 256 bits ([canales](https://meshtastic.org/docs/configuration/radio/channels/)) [F]. DespachoX debe usar un canal privado propio [S].
- El rol ROUTER retransmite siempre, y la documentación aconseja ponerlo en sitios estratégicos. REPEATER quedó obsoleto desde el firmware 2.7.11 ([roles](https://meshtastic.org/docs/configuration/radio/device/)) [F].
- Saltos: 3 por defecto y 7 como máximo ([configuración LoRa](https://meshtastic.org/docs/configuration/radio/lora/)) [F].

### Leer los mensajes desde un portátil con la librería de Python

- Librería `meshtastic` 2.7.11, del 17 de julio de 2026, licencia GPL-3.0, Python 3.9 a 3.14 ([PyPI](https://pypi.org/project/meshtastic/)) [F].
- Conexión por USB: `meshtastic.serial_interface.SerialInterface(devPath)`. Sin ruta, busca el dispositivo solo ([documentación de la API](https://python.meshtastic.org/)) [F].
- **El evento es el tema de PyPubSub `meshtastic.receive.text`.** El manejador recibe `packet`, un diccionario, e `interface` [F]. Otros temas útiles: `meshtastic.receive.position`, `meshtastic.connection.established` y `meshtastic.connection.lost` [F].
- **El texto queda en `packet["decoded"]["text"]`.** La documentación de la librería dice `decoded.data.text`, pero el código de la versión 2.7.11 lo guarda en `decoded.text` [F]. Lo comprobamos pasando un paquete simulado por la librería instalada [C].
- Para responder: `interface.sendText(texto, destinationId=..., wantAck=True, channelIndex=...)` [F].
- Con el mismo paquete simulado comprobamos otros cuatro detalles [C]. `fromId` llega vacío (`None`) si el nodo aún no está en la base de nodos, así que el remitente debe salir del número `from`. La clave `channel` no aparece cuando el canal es 0. `toId` vale `^all` en mensajes a todo el canal. El paquete trae `rxTime`, `rxSnr`, `rxRssi`, `hopStart` y `hopLimit`.
- La librería llama a los manejadores desde un hilo propio llamado «publishing» y, si el manejador falla, solo registra el error ([`meshtastic/util.py`](https://pypi.org/project/meshtastic/), clase `DeferredExecution`) [F]. En cambio, la base de DespachoX se abre con `sqlite3.connect` sin permitir otros hilos (`datos/db.py`) [F]. Así que el manejador solo debe encolar el paquete [C].

## 5. Malla por Bluetooth

Las aplicaciones de malla por Bluetooth conectan celulares cercanos sin red, pero exigen tener la app instalada antes y no dejan el mensaje en ningún sistema.

- **Bridgefy.** Versión 5.1.9 del 26 de septiembre; la App Store no muestra el año. Alcance de hasta 100 m, según su propia ficha. Pide internet la primera vez para iniciar sesión. Vende extras de 0,99 a 29,99 USD. Tiene 2,6 de 5 con 66 opiniones en la tienda de EE. UU. ([App Store](https://apps.apple.com/us/app/id975776347)) [F]. En 2022, Albrecht, Eikenberg y Paterson mostraron que seguía siendo atacable después de adoptar libsignal: lectura de mensajes privados, suplantación en el canal de difusión y una denegación de servicio limitada ([USENIX Security 2022](https://www.usenix.org/conference/usenixsecurity22/presentation/albrecht)) [F].
- **Briar.** Versión 1.5.24 en F-Droid, del 4 de noviembre de 2026, Android 5.0 o superior ([F-Droid](https://f-droid.org/en/packages/org.briarproject.briar.android/)) [F]. Sincroniza por Bluetooth o wifi si cae internet. Los contactos se agregan con QR en persona o con un enlace ([manual](https://briarproject.org/manual/)) [F]. La documentación no describe reenvío por desconocidos [F]. Así que no es una malla abierta: el pedido solo llega a contactos agregados antes [S].
- **bitchat.** Llegó a la App Store en julio de 2025. Alcance típico de unos 100 m. En ese momento no tenía revisión externa de seguridad y un investigador mostró que era fácil suplantar usuarios ([TechCrunch, 29-jul-2025](https://techcrunch.com/2025/07/29/jack-dorseys-bluetooth-messaging-app-bitchat-now-on-app-store)) [F]. En GitHub, la versión 1.7.0 (8 de julio) agregó guardar y reenviar mensajes directos a pares fuera de alcance, y la 1.5.4 corrigió hallazgos de una auditoría, 3 críticos y 7 altos ([versiones](https://github.com/permissionlesstech/bitchat/releases)) [F]. Las entradas no muestran el año; el pie de la página dice 2026 [F]. Las notas mencionan un cliente Android [F].
- Una evaluación académica resume el límite: las apps de celular a celular alcanzan menos de 100 m ([Khamaisi et al.](https://arxiv.org/abs/2509.22568)) [F].
- **Cómo entra:** no encontré una forma documentada de leer los mensajes de estas apps desde otro programa [NV]. Así que entra solo si una persona en el albergue lee el pedido y lo reenvía por SMS o lo digita [S].
- **Veredicto:** no lo recomendamos como canal de DespachoX. Puede servir entre vecinos que ya lo tengan instalado [S].

## 6. Radio VHF de los organismos de socorro

La radio VHF ya existe y la operan otros. DespachoX solo tiene que definir cómo se transcribe un pedido para que entre por el mismo lector.

### Quién la opera

- En Manizales, Bomberos, Defensa Civil y Cruz Roja trabajaron con la Alcaldía en el censo de damnificados ([Blu Radio, 13-ago-2026](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10)) [F]. Qué redes de radio usaron y en qué frecuencias: no verificado.
- MinTIC pidió apoyo a radioaficionados y a la banda ciudadana, en coordinación con la UNGRD, y dijo que revisaba alternativas en HF, VHF y UHF con repetidoras ([MinTIC](https://www.mintic.gov.co/portal/715/w3-article-440280.html)) [F].
- La Liga Colombiana de Radioaficionados presenta las comunicaciones de emergencia como un compromiso de sus miembros. Reporta un simulacro nacional en octubre de 2024 con 335 radioaficionados y una red Packet/APRS/Winlink de respaldo. También informa que la Liga Radio Manizales instaló una antena nueva en su repetidora FM/C4FM del Cerro El Recreo, en el PNN Los Nevados, para mejorar la cobertura en Manizales ([LCRA, portada](https://www.lcra.org.co/)) [F]. Las notas completas no abrieron [NV].
- La Defensa Civil tiene una «Emisora Virtual», pero es solo transmisión por internet ([Defensa Civil](https://www.defensacivil.gov.co/sala-prensa/programacion)) [F], así que no sirve sin red [C].

### Cómo un operador transcribe un pedido [S]

1. **El mismo formato del SMS, dicho en voz:** tipo, número, lugar, productos y urgencia. Así el lector por reglas sirve sin cambios.
2. **Formulario de papel «Pedido por radio»** con casillas en ese orden, número de mensaje, hora y estación que transmite. La estación se identifica por organismo o indicativo, nunca por el nombre de una persona.
3. **Colación:** el operador del acopio lee el pedido de vuelta y la otra estación responde «correcto». Esa es la confirmación del canal.
4. **Digitación:** el operador escribe la línea en una casilla de entrada manual del tablero, por ejemplo `PEDIDO 40 SAN JOSE ARROZ LECHE`. La casilla llama al mismo lector con remitente `radio:<estación>`.
5. **Cierre:** el tablero muestra lo entendido, el operador lo lee por radio y anota el número de pedido en el formulario, que se archiva para la trazabilidad.
6. **Volumen:** si llegan muchos pedidos, un segundo voluntario digita mientras el primero escucha.

Hoy el tablero no tiene esa casilla de entrada manual (revisé `tablero/` el 20 de noviembre). Hay que pedirla a Jacobo, dueño de `tablero/`, y a Samuel, dueño de `entrada/`.

Winlink es correo por radio. Si los radioaficionados lo usan, el texto podría llegar a un cliente en el portátil y pasar al lector sin digitar. Es un supuesto sin verificar [S].

**Qué se pierde:** el registro automático y la ubicación, salvo lo que se diga. Se suman errores de transcripción, que la colación reduce [S].

## 7. Radio comunitaria y emisoras de Manizales (salida)

La emisora no sirve para pedir, pero sí para avisar a los barrios cuándo y dónde llega la ayuda.

- MinTIC informó que todas las emisoras de Radio Nacional seguían activas para informar desde las regiones ([MinTIC](https://www.mintic.gov.co/portal/715/w3-article-440280.html)) [F].
- La portada de Radio Nacional anuncia que pone sus 74 frecuencias a disposición de la ciudadanía ([Radio Nacional](https://www.radionacional.co/)) [F]. No pude abrir la nota ni confirmar la frecuencia de Manizales [NV].
- El artículo 8 de la Ley 1341 de 2009 obliga a los proveedores de redes y servicios de telecomunicaciones a poner sus redes a disposición de las autoridades, gratis, en una emergencia ([normograma MinTIC](https://normograma.mintic.gov.co/mintic/compilacion/docs/ley_1341_2009.htm)) [F]. Ese artículo no menciona la radiodifusión sonora [F]. Si las emisoras tienen una obligación equivalente: no verificado.
- Emisoras comerciales y comunitarias de Manizales: no las pude consultar [NV].

### Boletín por barrio [S]

- **Contenido:** punto de entrega, franja horaria, qué llega y cómo reportar (el número SMS del acopio o el punto físico). Sin datos personales ni cantidades por familia.
- **Largo:** unos 500 caracteres, cerca de 85 palabras. Con un ritmo supuesto de 150 palabras por minuto, se leen en unos 35 segundos [C].
- **Aprobación:** el despachador aprueba el texto, porque anunciar un punto y una hora puede atraer más gente de la que la entrega atiende.
- **Llegada a la emisora:** por correo o mensajería si hay datos; impreso y llevado en moto si no; o leído por VHF a la estación.
- **Qué se pierde:** la confirmación de que alguien oyó. Se compensa preguntando al responsable del punto por SMS o por la malla.

## 8. Veredicto sobre Meshtastic

**Sí es viable para un piloto acotado.** Sirve para unir el acopio con puntos fijos (albergues, comedores, juntas de acción comunal) donde la red celular cae. No sirve como canal para el público general, porque cada persona necesitaría un nodo y, en la mayoría de los modelos, un teléfono con la app [F] [S].

**Por qué sí:**

- **Costo:** desde 17,90 USD por nodo Heltec V3 en la tienda oficial (20-nov-2026), unos 61.130 COP [F] [C]. Un piloto de mesa con tres Heltec (acopio, repetidor y un barrio) cuesta de 53,70 a 59,70 USD, unos 183.000 a 204.000 COP [C]. Un piloto de barrio con dos Heltec y cuatro T1000-E con GPS para responsables de punto cuesta 199,40 USD, unos 681.000 COP [C]. Ninguna cifra incluye baterías, carcasas, paneles, envío ni impuestos [NV].
- **Banda:** 915 a 928 MHz de uso libre, región ANZ [F].
- **Lectura desde Python comprobada:** evento `meshtastic.receive.text` y texto en `decoded.text` [F] [C].
- **Confirmación:** los mensajes directos tienen acuse de recibo [F].
- **Formato:** el formato corto de DespachoX cabe en 200 bytes [C].

**Condiciones del piloto [S]:**

1. Los nodos se reparten antes de la emergencia a puntos fijos, con un responsable entrenado.
2. Al menos un repetidor en un punto alto, con energía propia.
3. Canal privado con clave propia y región ANZ en todos los nodos.
4. Los pedidos van como mensaje directo al nodo del acopio.
5. Una prueba de alcance en Manizales antes de prometer cobertura.

## 9. Diseño del receptor y su simulador

El receptor lee un nodo conectado al portátil y entrega el texto al mismo lector de `entrada/` que usan Telegram y el SMS. Todo lo de esta sección es propuesta [S], salvo los datos marcados [F] o [C] en la sección 4. No incluye código.

### Una sola puerta en `entrada/`

Proponemos a Samuel una puerta común: una función que recibe canal, remitente, texto y, opcionalmente, una ubicación, y devuelve los textos de respuesta ya planos y cortos. La misma función se expone como la ruta HTTP local del encargo A3. La pasarela SMS, el receptor de malla y la digitación de radio la llaman igual.

El remitente lleva el canal adelante: `sms:<número>`, `malla:!a1b2c3d4` o `radio:<estación>`. La puerta usa `leer_sms` (reglas, sin modelo) cuando `DESPACHOX_SIN_RED=1`, o el extractor con modelo si hay red. Las dos rutas terminan en `Mesa.atender`, que guarda el remitente como hash con `hash_remitente`, igual que el chat de Telegram. Los botones de `Respuesta` se convierten en texto: «Responda SI o escriba el barrio», como ya prevé A3.

### El receptor de malla

Un módulo `entrada/malla.py`, que corre con un puerto USB o con un guion simulado.

1. **Arranque.** Abre `SerialInterface` con el puerto indicado o lo busca solo. Se suscribe a `meshtastic.receive.text`, `meshtastic.receive.position`, `meshtastic.connection.established` y `meshtastic.connection.lost`. Anota el número del nodo propio para ignorar lo que él mismo envía.
2. **Manejador.** Solo encola el paquete. La librería lo llama desde otro hilo y la base SQLite no admite ese hilo. Además, si el manejador falla, el mensaje se pierde y solo queda el error en el registro.
3. **Filtro.** El bucle principal toma un paquete de la cola. Acepta solo texto, solo del canal privado de DespachoX o dirigido al nodo del acopio. Descarta duplicados por número de nodo e identificador de paquete en los últimos 10 minutos, por precaución.
4. **Remitente.** Arma `malla:!` más el número `from` en hexadecimal de 8 dígitos, porque `fromId` puede llegar vacío. El número crudo vive solo en memoria para responder; en la base queda el hash.
5. **Texto.** Toma `decoded.text`. Si falta, porque el UTF-8 venía dañado, guarda el mensaje como crudo para el despachador. Nunca descarta.
6. **Entrega.** Llama la puerta común con canal «malla».
7. **Respuesta.** Recorta a 200 bytes UTF-8, no a 200 caracteres. Si no cabe, la parte en dos con «1/2» y «2/2». La envía con `sendText` como mensaje directo, con `wantAck=True` y en el mismo canal. Registra el acuse en el registro del proceso, sin el texto del mensaje, como ya hace el bot.
8. **Ubicación.** Si el nodo reportó posición hace poco, la respuesta ofrece «Responda UBICACION para usar la posición de su equipo». Solo con esa respuesta se llama `Mesa.recibir_ubicacion`. Así la posición automática del equipo no se guarda sin que la persona lo pida, igual que el pin de Telegram.
9. **Desconexión.** Con `connection.lost`, el tablero muestra «radio desconectado» y el receptor reintenta cada 10 segundos. Lo que llegue al nodo mientras el portátil está desconectado puede perderse [NV]. Por eso el nodo del acopio debería ser servidor Store & Forward (un T-Beam con PSRAM) o tener cable fijo y energía de respaldo.
10. **Licencia.** La librería es GPL-3.0 [F]. Correr el receptor como proceso aparte, que habla con DespachoX por la ruta HTTP local, separa ese código del resto. Hay que confirmarlo con quien lleve la licencia del proyecto.

### El simulador, para cuando no hay hardware

- **Misma cara que el nodo real.** Un `NodoSimulado` ofrece al receptor lo mismo que la interfaz de la librería: suscripción a eventos, `sendText`, la base de nodos y `close`.
- **Paquetes con la forma real.** El simulador no arma el diccionario a mano. Construye un `MeshPacket` de protobuf y lo pasa por el mismo método interno que procesa lo que llega del radio, `_handlePacketFromRadio`, sobre una `MeshInterface(noProto=True)`. Así el paquete simulado trae las mismas rarezas que el real. Lo probamos: funciona si la base de nodos (`nodesByNum` y `nodes`) se inicia vacía [C]. Como ese método es interno, conviene fijar `meshtastic==2.7.11` en `requirements.txt` y tener una prueba que avise si la forma del paquete cambia.
- **Entradas.** Un guion de texto con segundo, nodo, canal y mensaje (por ejemplo, los veinte SMS de prueba del encargo A3), o la consola para una demo en vivo.
- **Fallas que inyecta.** Duplicados, mensajes de más de 200 bytes, UTF-8 dañado, nodo desconocido (`fromId` vacío), canal 0 frente a canal privado, posición del nodo, desconexión y reconexión, y acuse negativo.
- **Captura de respuestas.** Recoge lo que el receptor contesta, como `ClienteSimulado` en `entrada/pruebas/simulador.py`, para que las pruebas lo comparen.
- **Pruebas.** Los veinte mensajes dan la misma extracción por malla que por SMS. Ninguna respuesta pasa de 200 bytes. En la base no queda el número del nodo, solo el hash. No hay llamadas de red. Un duplicado no crea dos pedidos.
- **Demo.** En modo simulado, los pedidos aparecen en el tablero sin hardware. Con dos nodos reales, el mismo guion se envía desde la app y el resultado debe ser idéntico.

## 10. Propuesta de alianza con la vertical 03, «Energía y conectividad»

A un equipo de la vertical 03 ([verticales de la hackathon](https://8wf9bsh8.insforge.site/#seleccionados)) le propondríamos un piloto conjunto de 30 a 90 días con una frontera simple: ellos llevan la señal y la energía, y nosotros decidimos qué se hace con ella. Ellos montan dos o tres repetidores Meshtastic con panel solar en puntos altos de Manizales, el wifi local del acopio y la carga de celulares y nodos. Nosotros ponemos el receptor, el lector, el despacho y el boletín de salida. Entre los dos solo pasa un texto corto, como `PEDIDO 40 SAN JOSE ARROZ LECHE`, por una ruta HTTP local en el portátil. Así, cualquier red que ellos construyan, sea LoRa, wifi comunitario o un enlace satelital, queda conectada a DespachoX sin cambiar el tablero. Mediríamos juntos cuatro cosas: el alcance real de cada enlace en la ciudad, la fracción de pedidos que llega con acuse, los minutos entre el envío y la ruta aprobada, y la fracción de pedidos que el lector entiende sin digitación. Para la demo de mañana bastan dos nodos, uno en su mesa y otro en la nuestra, y un pedido que cruce el salón y aparezca en el tablero [S].

## 11. Lo que no pude verificar y a quién preguntar

La búsqueda web de esta sesión se agotó a mitad del trabajo (límite compartido entre agentes). Desde ese momento solo abrí páginas que ya habían aparecido. Por eso faltan los precios actuales de Tigo y Movistar, las emisoras locales y las redes de radio de cada organismo.

| Falta | A quién preguntar | Qué preguntar |
|---|---|---|
| Nodos LoRa disponibles hoy y prueba de alcance | Equipos de la vertical 03 en el Bloque X | Si tienen nodos de 915 MHz y si prueban dos nodos con nosotros hoy |
| Radio en el acopio y en los barrios | Defensa Civil seccional Caldas, Cruz Roja Caldas, Bomberos Manizales | Quién opera la radio en el acopio, si en agosto recibieron pedidos de comida por radio y si aceptan el formulario |
| Repetidoras y voluntarios | Liga Radio Manizales y coordinación de emergencias de la LCRA | Si transmitirían pedidos con el formato corto y si usan Winlink en la región |
| Uso de una SIM como pasarela | Claro, Tigo o Movistar | Si responder cada SMS desde una app viola la cláusula de envío masivo, y si hay código corto para emergencias |
| Emisoras de Manizales | Radio Nacional y emisoras comunitarias y comerciales locales | Si leerían un boletín diario de entregas y por qué canal lo reciben |
| Precio de nodos en Colombia | Tiendas de electrónica de Manizales o Bogotá | Precio y disponibilidad de Heltec V3 o T-Beam en 915 MHz |
| Prueba real de la pasarela | Samuel, con un Android de sobra | Si `GET /inbox` funciona sin internet y cuánto tarda un SMS en aparecer |
| Potencias de uso libre en 915 a 928 MHz | Texto del Anexo 1 de la Resolución ANE 105 de 2020 | Potencia máxima y condiciones |

## 12. Fuentes

Todas consultadas el 20 de noviembre de 2026.

| Fuente | Qué respalda | Publicación |
|---|---|---|
| [Noticias RCN, señal móvil](https://www.noticiasrcn.com/colombia/senal-movil-en-colombia-46-esta-afectada-1049064) | 46,1 % de estaciones base sin servicio, Caldas 28 %, prioridad a SMS | 11-ago-2026 |
| [Noticias RCN, por qué se cae la señal](https://www.noticiasrcn.com/tendencias/temblor-colombia-senal-caida-por-que-1049139) | Congestión, energía y daño físico | 11-ago-2026 |
| [MinTIC, artículo 440280](https://www.mintic.gov.co/portal/715/w3-article-440280.html) | Recomendación de SMS, radioaficionados, Radio Nacional, satélite directo al celular | Actualizado 13-ago-2026 |
| [Infobae](https://www.infobae.com/tecno/2026/08/13/avanza-un-80-la-reparacion-de-infraestructura-de-telecomunicaciones-en-zonas-afectadas-por-el-terremoto-en-colombia-claro-y-tigo-afectadas/) | Claro con cerca del 80 % de estaciones base | 13-ago-2026 |
| [Blu Radio](https://www.bluradio.com/nacion/manizales-censa-a-mas-de-2-000-damnificados-y-anuncia-subsidios-de-arriendo-desde-la-proxima-semana-rg10) | Bomberos, Defensa Civil y Cruz Roja con la Alcaldía | 13-ago-2026 |
| [SMS Gateway for Android, GitHub](https://github.com/capcom6/android-sms-gateway) | Licencia, Android 5.0, límite por periodo | Sin fecha |
| [Modo local](https://docs.sms-gate.app/getting-started/local-server/), [webhooks](https://docs.sms-gate.app/features/webhooks/), [FAQ](https://docs.sms-gate.app/faq/webhooks/), [lectura](https://docs.sms-gate.app/features/reading-messages/), [instalación](https://docs.sms-gate.app/installation/) | Funcionamiento sin internet, HTTPS, `/inbox`, APK | Sin fecha |
| [Incoming SMS to URL Forwarder](https://github.com/bogkonstantin/android_income_sms_gateway_webhook) | Reenvío por HTTP, modo de red local | Sin fecha |
| [Claro, condiciones Todo Incluido](https://www.claro.com.co/portal/co/recursos_contenido/pdf/Terminos-condiciones-paquetes-prepago-todo-incluido.pdf) | Precios, SMS ilimitados, prohibición de envío masivo | Oferta 29-oct a 30-nov-2026 |
| [Enter.co, pospago más económico por operador](https://www.enter.co/colombia/planes-moviles-pospago-mas-economicos-por-operador-en-colombia-cual-es-el-mejor-relacion-costo-beneficio) | Pospago con SMS ilimitados de Claro, Movistar, Tigo y WOM | 21-mar-2025 |
| [AOSP, SmsUsageMonitor](https://android.googlesource.com/platform/frameworks/opt/telephony/+/e7fd4f7%5E%21/) | Aviso con 30 SMS en un minuto | 29-nov-2012 |
| [GSM 03.38, Wikipedia](https://en.wikipedia.org/wiki/GSM_03.38) | 160 y 70 caracteres, letras con tilde | Sin fecha |
| [Enlightenment Economics para la GSMA](https://www.itu.int/en/ITU-D/Emergency-Telecommunications/Documents/ET-OnlineToolkit/bp/The%20Role%20of%20Mobiles%20in%20Disasters%20and%20Emergencies%20%E2%80%93%20%E2%80%9805.pdf) | SMS en emergencias y colas | Dic-2005 |
| [TRM, datos.gov.co](https://www.datos.gov.co/resource/32sa-8pi3.json) | 3.415,10 COP por dólar | 20-nov-2026 |
| [Heltec](https://heltec.org/project/wifi-lora-32-v3/), [Rokland](https://store.rokland.com/collections/heltec-products/products/heltec-wifi-lora-32v3), [Seeed](https://www.seeedstudio.com/SenseCAP-Card-Tracker-T1000-E-for-Meshtastic-p-5913.html), [LILYGO](https://lilygo.cc/products/t-deck-plus-meshtastic) | Precios y características de nodos | Consulta del 20-nov-2026 |
| [Meshtastic: región por país](https://meshtastic.org/docs/configuration/region-by-country/), [LoRa](https://meshtastic.org/docs/configuration/radio/lora/), [perfiles](https://meshtastic.org/docs/overview/radio-settings/), [récords](https://meshtastic.org/docs/overview/range-tests/), [canales](https://meshtastic.org/docs/configuration/radio/channels/), [roles](https://meshtastic.org/docs/configuration/radio/device/), [mensajes predefinidos](https://meshtastic.org/docs/configuration/module/canned-message/), [Store & Forward](https://meshtastic.org/docs/configuration/module/store-and-forward-module/), [T-Deck](https://meshtastic.org/docs/hardware/devices/lilygo/tdeck) | Banda, saltos, perfiles, seguridad, envío sin teléfono | Documentación vigente |
| [Guía de la app de Android](https://meshtastic.github.io/Meshtastic-Android/en/user/messages-and-channels) | 200 bytes, 233 bytes, acuses | Documentación vigente |
| [Librería meshtastic en PyPI](https://pypi.org/project/meshtastic/) y [documentación de la API](https://python.meshtastic.org/) | Versión 2.7.11, GPL-3.0, eventos, `sendText` | 17-jul-2026 |
| Código de `meshtastic` 2.7.11 instalado (`mesh_interface.py`, `__init__.py`, `util.py`) y prueba propia con un paquete simulado | `decoded.text`, `fromId`, `channel`, hilo de publicación, 233 bytes | Prueba del 20-nov-2026 |
| [ANE, Resolución 28 de 2026](https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_ane_0028_2026.htm) | Banda de 900 MHz y uso libre en 915 a 928 MHz | 26-ene-2026 |
| [ANE, Resolución 105 de 2020](https://normograma.mintic.gov.co/mintic/compilacion/docs/resolucion_ane_0105_2020.htm) | Uso libre sin permiso y sin interferencia | 2020, compilada |
| [ANE, propuesta para la banda de 900 MHz](https://www.ane.gov.co/Sliders/archivos/gesti%C3%B3n%20t%C3%A9cnica/Estudios%20de%20gesti%C3%B3n%20y%20planeaci%C3%B3n/900%20MHz/Documentos/PropuestaUsoBanda900MHz.pdf) | Uso libre en 915 a 928 MHz por el Anexo 1, alcance reducido por potencia, propuesta de restringir importación en 902 a 915 MHz | Dic-2022 |
| [Gonzales Zapata y González Armijos, Universidad de Cuenca](https://dspace-test.ucuenca.edu.ec/bitstream/123456789/41515/1/Trabajo-de-Titulaci%c3%b3n.pdf) | Más de 97 % de paquetes a cerca de 1 km, a 433 MHz; entorno de la prueba no verificado | 2023 |
| [Khamaisi et al., arXiv 2509.22568](https://arxiv.org/abs/2509.22568) | 1,2 km y 92 % en Zúrich; Bluetooth a menos de 100 m | 26-sep-2025 |
| [Sanchez-Vital et al., Sensors 25(23):7209](https://www.mdpi.com/1424-8220/25/23/7209) | LoRa hasta 1,5 a 2 km en zona urbana | 26-nov-2025 |
| [Iova et al., EWSN 2017](https://openpub.fmach.it/bitstream/10449/42132/1/madcom17.pdf) | Alcance en montaña con vegetación | Feb-2017 |
| [Hernández Ortiz et al., arXiv 2605.17063](https://arxiv.org/abs/2605.17063) | Perfiles de Meshtastic a 915 MHz en banco de pruebas | 16-may-2026 |
| [Bridgefy, App Store](https://apps.apple.com/us/app/id975776347) | Versión, alcance, inicio de sesión, precios | Versión del 26-sep |
| [Albrecht et al., USENIX Security 2022](https://www.usenix.org/conference/usenixsecurity22/presentation/albrecht) | Ataques a Bridgefy después de libsignal | 2022 |
| [Briar, F-Droid](https://f-droid.org/en/packages/org.briarproject.briar.android/) y [manual](https://briarproject.org/manual/) | Versión, sincronización, contactos | 4-nov-2026 |
| [TechCrunch](https://techcrunch.com/2025/07/29/jack-dorseys-bluetooth-messaging-app-bitchat-now-on-app-store) y [bitchat en GitHub](https://github.com/permissionlesstech/bitchat/releases) | Lanzamiento, alcance, seguridad, versiones | 29-jul-2025; versiones de julio |
| [LCRA](https://www.lcra.org.co/) | Simulacro, red Winlink, repetidora del Cerro El Recreo | Portada vigente |
| [Defensa Civil, Emisora Virtual](https://www.defensacivil.gov.co/sala-prensa/programacion) | Emisora solo por internet | Sin fecha |
| [Radio Nacional](https://www.radionacional.co/) | 74 frecuencias a disposición | Portada vigente |
| [Ley 1341 de 2009, normograma](https://normograma.mintic.gov.co/mintic/compilacion/docs/ley_1341_2009.htm) | Artículo 8, redes para autoridades | 2009, compilada |
| [Hackathon, verticales](https://8wf9bsh8.insforge.site/#seleccionados) | Vertical 03, Energía y conectividad | Consulta del 20-nov-2026 |

No se pudieron abrir: MercadoLibre Colombia y Vistrónica (bloquean la consulta automática), las notas internas de la LCRA, la nota de Radio Nacional sobre sus frecuencias, el Anexo 1 de la Resolución ANE 105 de 2020 y la guía FCC-FEMA sobre comunicación en emergencias.
