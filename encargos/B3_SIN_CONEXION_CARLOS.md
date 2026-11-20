# Encargo B3 · Despacho sin conexión (Carlos, sesión B-despacho)

Empieza cuando termines tu parte de `encargos/RONDA_3.md`. Sigue en la rama `carlos-despacho`.

Haz `git pull --rebase` y lee: `docs/SIN_CONEXION.md`, las entradas nuevas de `torre/CANAL.md`, y lo que ya existe de trazabilidad en `despacho/` (la tabla `paquetes`).

Contexto: después del sismo los datos móviles colapsan. DespachoX tiene que poder seguir despachando desde un portátil en el centro de acopio, y los conductores tienen que poder trabajar sin señal. El optimizador y la red vial ya funcionan sin internet; faltan las dos piezas de abajo.

## 1. Hoja de ruta impresa con QR (lo principal)

`python -m despacho.hoja --plan ID [--salida carpeta]` genera un PDF por vehículo del plan aprobado.

Cada hoja, en una página carta legible impresa en blanco y negro:
- encabezado: DespachoX, vehículo, conductor (espacio en blanco), plan, hora de salida, acopio;
- un mapa pequeño de la ruta dibujado desde la geometría de las paradas y la red vial del caché (matplotlib o similar). **Sin teselas de internet**;
- tabla de paradas en orden: punto, barrio, llegada estimada, qué se entrega (producto y kilos), si es crítico, y un QR por paquete con su código;
- al final: tramos cerrados que la ruta evita, y un espacio para firma y hora de entrega por parada;
- pie: «Al volver, registre las entregas con el código de cada paquete» y la regla de qué hacer si encuentra una vía cerrada.

El QR contiene solo el código del paquete (por ejemplo `DX7K2Q`), sin datos personales. Así se puede leer con cualquier cámara y registrar después por SMS (`ENTREGADO DX7K2Q`), por el bot o en el tablero.

Añade `reportlab` o `fpdf2` a `requirements.txt` (el que sea más liviano) y confirma que el `Dockerfile` sigue construyendo.

Función en Python para el tablero: `despacho.hoja.generar(con, plan_id) -> list[Path]`, para que Jacobo ponga un botón «Imprimir hojas de ruta». Avísale por el canal cuando exista.

Pruebas: el PDF se genera con la semilla y un plan aprobado; cada parada tiene su QR; el QR decodifica al código guardado en `paquetes`; la generación no hace ninguna llamada de red (prueba que falle si se intenta).

## 2. Arranque en un portátil sin internet

`despliegue/local.sh`: arranca en un portátil todo lo que hoy corre en Railway, con la base en `datos/`.

- Variable `DESPACHOX_SIN_RED=1`: el bot de Telegram no arranca; la lectura de mensajes no llama al modelo y usa el lector por reglas de `entrada/` si ya existe (lo está haciendo Samuel; si no existe, guarda el texto crudo para el despachador); el ubicador no usa el modelo para desempatar.
- El tablero usa el mapa de fondo sin conexión cuando Jacobo lo tenga (`DESPACHOX_MAPA=local`); mientras tanto, documenta que el fondo saldrá vacío pero rutas y puntos se ven.
- Prueba de verdad: con el wifi apagado, cargar la semilla, confirmar un pedido, calcular, aprobar e imprimir hojas. Anota en tu torre qué falló.

En `docs/SIN_CONEXION.md` marca qué quedó hecho.

## Reglas

- No toques `entrada/` ni `tablero/`: pide por el canal.
- Pruebas completas en verde antes de abrir el pull request.
- LISTO en el canal al cerrar cada parte, con cómo probarlo.

**Aporta a:** criterio 2 (demo con un papel en la mano), criterio 5 (riesgo de conectividad con respuesta concreta) y el entregable del reto (trazabilidad).
