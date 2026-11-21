# Pedidos por SMS en un acopio sin internet

Después de un sismo, los datos móviles suelen caerse antes que los SMS. Con esta guía, un acopio que solo tiene un portátil, electricidad y un celular Android recibe pedidos, cierres viales y confirmaciones de entrega por SMS, sin internet y sin modelo de lenguaje.

**Estado, 20 de noviembre de 2026, 9:30 p. m.** El lector por reglas y el receptor HTTP funcionan y tienen pruebas. El camino completo se probó con `curl`, que simula a la pasarela. **No se ha probado con un celular de verdad**: no hay video. Nada se compró ni se instaló.

## Cómo funciona

```
vecino --SMS--> celular Android del acopio --wifi local--> portátil: entrada.pasarela_sms
                (aplicación pasarela)                      -> sms.leer_sms (reglas, sin modelo)
                                                           -> el mismo flujo del bot -> base
vecino <--SMS-- celular <---------- respuesta de 160 caracteres o menos ----------
```

El formato que se le enseña a la gente está en `docs/SIN_CONEXION.md`:

```
PEDIDO 40 SAN JOSE ARROZ LECHE
PEDIDO 6 BEBES LA ENEA LECHE URGENTE
CIERRE AV DEL CENTRO CAMION
ENTREGADO DX7K2Q
```

El lector tolera minúsculas, la falta de tildes, el orden variable, las palabras de relleno y los errores de tipeo en la palabra clave (`PEDDO`, `CIERE`). La persona confirma el lugar respondiendo `SI` o el barrio correcto, y el número de familias respondiendo el número. Lo que no se entiende se guarda como pedido `nuevo` con el texto, para que lo vea el despachador.

**Respuestas sin tildes, a propósito.** Un SMS admite 160 caracteres con el alfabeto GSM-7. Una sola letra fuera de ese alfabeto, como la «á», cambia la codificación y el límite baja a 70.

**Medición.** 20 de 20 SMS sintéticos se leen bien (`entrada/pruebas/reporte_sms.md`). No es una medición independiente: los casos y las reglas los escribió la misma sesión. Hace falta que otra persona escriba veinte SMS sin mirar el código.

## Montaje en el acopio

1. **Portátil.** Con el repositorio y la base. Se arranca con `python -m entrada.pasarela_sms`, que imprime la dirección a configurar, por ejemplo `http://192.168.1.10:8081/sms`. Opcional: `DESPACHOX_SMS_TOKEN=<clave>` para que solo el celular del acopio pueda enviar.
2. **Celular Android** con una SIM que tenga plan de SMS, conectado al mismo wifi que el portátil. El wifi puede ser un enrutador sin internet o el punto de acceso del propio portátil.
3. **Aplicación pasarela** en el celular (opción A, abajo). En su modo de servidor local se registra el aviso `sms:received` hacia la dirección del paso 1.
4. **Respuesta al vecino.** Para que el celular envíe la respuesta, en el portátil se ponen `DESPACHOX_PASARELA_URL` (la API local del celular, por ejemplo `http://<ip-del-celular>:8080/message`), `DESPACHOX_PASARELA_USUARIO` y `DESPACHOX_PASARELA_CLAVE`, que la aplicación muestra en su pantalla. Sin eso, el SMS se guarda igual, pero no se contesta.
5. **Prueba.** Desde otro celular, enviar `PEDIDO 40 SAN JOSE ARROZ LECHE` al número de la SIM y ver el pedido en el tablero.

Para probar sin celular:

```bash
python -m entrada.pasarela_sms
curl -X POST http://localhost:8081/sms -H "Content-Type: application/json" \
     -d '{"de": "sms-prueba-1", "texto": "PEDIDO 6 BEBES LA ENEA LECHE URGENTE"}'
# {"respuesta": "Recibido: pedido 6 bebes leche URGENTE en La Enea. Responda SI o el barrio correcto.", ...}
```

## Opciones comparadas

| | A. Celular como pasarela, sin internet | B. Proveedor de SMS en la nube |
|---|---|---|
| Qué es | **SMS Gateway for Android** (capcom6), aplicación de código abierto con licencia Apache 2.0, para Android 5.0 o superior. Tiene modo de servidor local con autenticación básica, avisos (webhooks) para `sms:received` y una API HTTP para enviar | **Twilio**, como ejemplo verificado. Según su guía para Colombia, admite SMS de ida y vuelta |
| Necesita internet | No: celular y portátil en el mismo wifi | Sí, en el acopio |
| Número | La SIM del acopio, un número móvil normal | Un número local exige probar una dirección en Colombia. Con un número global, el remitente que ve el vecino se reemplaza por un código corto |
| Costo | El celular, la SIM y su plan de SMS: **[pendiente, no se cotizó]** | Por mensaje y por número, según la página de precios de Twilio: **[pendiente, no se consultó]** |
| Enlaces | [repositorio](https://github.com/capcom6/android-sms-gateway); [avisos (webhooks)](https://docs.sms-gate.app/features/webhooks/); [receptor de ejemplo en Flask](https://github.com/android-sms-gateway/example-webhooks-flask) | [guía de SMS de Twilio para Colombia](https://www.twilio.com/en-us/guidelines/co/sms); [requisitos regulatorios](https://www.twilio.com/guidelines/co/regulatory) |
| Para qué sirve | El caso de esta guía: el acopio aislado | El acopio con internet que quiere un número fijo y más volumen |

**Por qué A primero.** Es el único que funciona sin internet, que es justamente el escenario. B sirve para el plan de 30 días, si el operador quiere un número que no dependa de un celular.

## Qué falta

- **Probar con un celular real** y grabar el video. No había un Android disponible en esta sesión.
- **Verificar contra la versión instalada** el formato del envío de vuelta: `textMessage` y `phoneNumbers` hacia `/message`. Se tomó de resúmenes de búsqueda, no de la documentación oficial leída completa.
- **Verificar si la aplicación exige HTTPS** para enviar avisos a otra máquina de la red local. Si lo exige, hace falta un certificado local o un túnel.
- **Límites de la SIM.** Cuántos SMS al día permite el operador antes de bloquearla: [pendiente].
- **Seguridad de `ENTREGADO`.** Cualquiera que adivine un código puede marcarlo entregado. Para el piloto, solo debería contar si viene del punto de destino o del conductor.
- **Lista de productos.** Lo que no está en la tabla de `entrada/raciones.py` no se reconoce, por ejemplo «atún». Ampliarla con lo que reparta el banco.
