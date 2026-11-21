# DespachoX sin internet

Después de un sismo, los datos móviles son lo primero que colapsa. Este documento explica cómo DespachoX sigue funcionando cuando eso pasa. Sirve para el diseño, para el componente 5 de la ficha (viabilidad y riesgos) y para una diapositiva del pitch.

## Tres cortes distintos

| Corte | Qué se pierde | Respuesta |
|---|---|---|
| Del vecino al sistema | El líder de barrio no tiene datos y Telegram no funciona | SMS, que suele aguantar más que los datos porque pide muy poco ancho de banda. Si tampoco hay SMS: radio o una persona que digita |
| Del centro de acopio a la nube | El despachador pierde el tablero en línea | Todo corre en un portátil en el acopio: base, optimizador, red vial y mapa guardados en disco |
| Del acopio al conductor | El conductor no recibe la ruta ni puede reportar | Hoja de ruta impresa con un QR por paquete. La confirmación de entrega se registra al volver |

## La escalera de degradación

DespachoX no promete funcionar igual sin internet. Promete que, cuando la red cae, el despachador sigue decidiendo con la mejor información disponible y nada de lo registrado se pierde.

| Nivel | Qué hay | Cómo funciona |
|---|---|---|
| 1. Normal | Internet y datos | Bot de Telegram, nube, modelo de lenguaje, mapa en línea |
| 2. Acopio aislado | Portátil y electricidad, sin internet | Todo en el portátil. Mensajes por SMS a un celular conectado por wifi local. Sin modelo, el SMS sigue un formato corto y lo lee un programa de reglas; lo que no entiende, lo digita el despachador |
| 3. Solo voz y radio | Ni datos ni SMS | Una persona recibe por radio o teléfono y digita en el tablero. El optimizador sigue funcionando. Las rutas salen impresas |
| 4. Vuelve la señal | Conexión intermitente | Lo acumulado sube a la nube: pedidos, cierres vistos y entregas confirmadas |

Lo que ya funciona sin internet desde el principio: el optimizador, la red vial guardada en disco y el ubicador de lugares (el modelo solo desempata).

## Formato de SMS

Corto, sin tildes obligatorias, tolerante con el orden:

```
PEDIDO 40 SAN JOSE ARROZ LECHE
PEDIDO 6 BEBES LA ENEA LECHE URGENTE
CIERRE AV DEL CENTRO CAMION
ENTREGADO DX7K2Q
```

La primera palabra dice el tipo. El número son familias (o personas, si dice «personas», «bebés» o «niños»). El lugar se resuelve con el nomenclátor. Lo que el programa no entiende queda como texto para el despachador, nunca se descarta.

## Qué entra antes del congelamiento y qué queda para el piloto

| Pieza | Cuándo | Responsable |
|---|---|---|
| Hoja de ruta impresa con QR por paquete | Hecha | Carlos (`encargos/B3_SIN_CONEXION_CARLOS.md`) |
| Arranque completo en un portátil sin internet | Hecho; falta probarlo con el wifi apagado | Carlos |
| Mapa de fondo dibujado desde la red vial, sin teselas en línea | Antes del congelamiento | Jacobo |
| Lector de SMS por reglas y entrada por SMS | Lector antes del congelamiento; pasarela si alcanza | Samuel (`encargos/A3_SMS_SAMUEL.md`) |
| Resincronización con la nube | Plan de 30 días | |
| Red de radio o malla | Plan de 30 a 90 días, con un equipo de la vertical de energía y conectividad | |

## Estado (viernes 20, 4:50 p. m.)

**Hecho, rama `carlos-despacho`:**

- Hoja de ruta impresa. `python -m despacho.hoja` escribe un PDF carta por vehículo del plan aprobado: encabezado, mapa dibujado con la red vial del disco, una fila por parada con su QR, hora estimada, qué se entrega, si es crítica y espacio para firma y hora; al final, los tramos cerrados que la ruta evita y las reglas del conductor. Se imprime en blanco y negro. Solo imprime planes aprobados, porque los códigos nacen al aprobar.
- `despliegue/local.sh` arranca base, optimizador, red vial y tablero en un portátil. Por defecto trae `DESPACHOX_SIN_RED=1`: el bot no arranca, el ubicador no usa el modelo para desempatar y la red vial nunca intenta descargarse.

**Medido con la red bloqueada** (macOS `sandbox-exec`, sin conexiones de salida salvo a localhost; no es el wifi apagado): semilla, confirmar un pedido, ubicar tres frases sin modelo, calcular (12 s), aprobar, imprimir tres hojas y registrar una entrega, 23 s en total. El tablero arrancó y respondió en localhost.

**Lo que falla sin internet:**

- El mapa del tablero no se dibuja. Folium carga Leaflet, jQuery y Bootstrap desde `cdn.jsdelivr.net`, `cdnjs.cloudflare.com` y `code.jquery.com`, además de las teselas. Sin internet se pierde el mapa entero, no solo el fondo. Indicadores, tablas y botones sí funcionan porque Streamlit los sirve desde el portátil. Lo arregla `DESPACHOX_MAPA=local` (Jacobo) si además sirve esas librerías desde el disco.
- La lectura de mensajes sigue llamando al modelo. Sin red la llamada falla y el texto queda crudo para el despachador, que es el comportamiento seguro, pero el lector por reglas de Samuel todavía no existe.

**Falta:** la prueba de verdad con el wifi apagado en el portátil de la demo.

## Lo que decimos con honestidad

Si un vecino no tiene ni datos, ni SMS, ni radio, la única interfaz es una persona que camina hasta el albergue. DespachoX no reemplaza eso: hace que lo que esa persona trae no se pierda y que el despachador lo use bien.
