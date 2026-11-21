# Lector de SMS por reglas

20 de 20 SMS leídos bien (todos los campos). Medido por nosotros sobre veinte SMS sintéticos escritos por el equipo, con errores de tipeo, orden variable y relleno. No son mensajes reales.

**Salvedad.** Los veinte casos y las reglas los escribió la misma sesión, así que las reglas están ajustadas a estos casos: el resultado no es una medición independiente. Para tener una, otra persona del equipo escribe veinte SMS nuevos sin mirar `entrada/sms.py` y se corren con `python -m entrada.sms "..."`.

| # | SMS | Resultado |
|---|---|---|
| 1 | `PEDIDO 40 SAN JOSE ARROZ LECHE` | bien |
| 2 | `PEDIDO 6 BEBES LA ENEA LECHE URGENTE` | bien |
| 3 | `CIERRE AV DEL CENTRO CAMION` | bien |
| 4 | `ENTREGADO DX7K2Q` | bien |
| 5 | `pedido 25 familias villa hermosa agua y panela` | bien |
| 6 | `PEDDO 30 CHIPRE FRIJOL ACEITE` | bien |
| 7 | `PEDIDOS 12 personas en fatima arroz` | bien |
| 8 | `ciere via a chinchina no pasan camiones` | bien |
| 9 | `CIERRE panamericana solo pasan motos` | bien |
| 10 | `entregado dx-4mq7` | bien |
| 11 | `Buenas tardes, PEDIDO 15 flias barrio el carmen, lentejas, urjente` | bien |
| 12 | `pedido arroz leche 20 san jorge` | bien |
| 13 | `PEDIDO 50 BELEN 30 KILOS ARROZ` | bien |
| 14 | `pedido 10 la sultana pañales leche` | bien |
| 15 | `derrumbe en la via al magdalena nadie pasa` | bien |
| 16 | `somos 8 abuelos en el albergue de la francia sin comida` | bien |
| 17 | `CIERE AVENIDA SANTANDER ARBOL` | bien |
| 18 | `ENTRGADO DX9PRT` | bien |
| 19 | `hola como estan` | bien |
| 20 | `PEDIDO 5 BEBES 3 NINOS VILLAMARIA FORMULA` | bien |
