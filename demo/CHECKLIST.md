# Lista de chequeo del sábado antes del pitch

**Aporta a:** criterio 2 (prototipo y demostración). Evidencia: la demo sale igual que `docs/GUION_DEMO.md`, verificada por `demo/correr.py`.
Pitch: sábado 2:00 p. m. Funciones congeladas desde las 8:30 a. m. Hora de Colombia.

Regla general: no se depura en vivo. Se intenta el respaldo una vez y, si no sale, se dice «tenemos el mismo recorrido grabado» y se pasa al video.

## Marcar en este orden (30 a 10 minutos antes)

| # | Revisar | Cómo | Si falla |
|---|---|---|---|
| 1 | Batería del computador y del teléfono del equipo | Al 100 % y los dos cargadores en la mesa. Modo «no molestar» y sin actualizaciones pendientes | Conectar ya. Sin enchufe cerca, bajar el brillo y cerrar todo lo que no sea la demo |
| 2 | Red de respaldo | Datos móviles del teléfono compartidos al computador (punto de acceso), probados con una página cualquiera. No usar el wifi del campus | Otro teléfono con datos. Si no hay red: ir al paso 11 (demo local sin red) |
| 3 | Railway arriba | Abrir la dirección del tablero en la nube. Debe cargar el mapa con dos acopios y quince puntos | Ver la tabla «Si falla» de abajo. Si no abre en dos minutos, demo local (paso 11) |
| 4 | Pulsar «Reiniciar datos de prueba» en el tablero de la nube | Deja la semilla limpia: 17 pedidos confirmados, 3 nuevos, sin planes ni cierres. La base de la nube conserva lotes viejos hasta que alguien lo haga | Si el botón no existe en el tablero: en Railway poner `DESPACHOX_REINICIAR=1`, esperar el redespliegue y **quitar la variable** (si no, cada reinicio borra todo). Ver `docs/DESPLIEGUE.md` |
| 5 | Plan 1 en la nube | «Calcular plan» y **no aprobar**. Esperado: 17 de 17 pedidos, 3 de 3 críticos a tiempo, tres vehículos con ruta (Camión 1, Camión 2, Campero 2) | No da 17 de 17: reiniciar datos otra vez (paso 4). Si persiste, video |
| 6 | Bot respondiendo | Desde el teléfono del equipo, `/start`. Responde con los dos ejemplos. Luego escribir el mensaje 1 **sin enviarlo** | No responde en diez segundos: ver «Bot» abajo. Sin bot: video del pedido y seguir con el tablero |
| 7 | Un solo bot con el token | Nadie corre el bot en local con el mismo token que Railway | Apagar el local. Telegram da error de conflicto si hay dos |
| 8 | Tarjeta del jurado | Impresa con: `derrumbe en la avenida del centro, no pasa camion, si pasa moto`. QR del bot a mano (`recursos/qr_bot.png`) | Sin tarjeta: quien maneja lo envía desde el teléfono del equipo |
| 9 | Video de respaldo a mano | Abierto en otra pestaña, en pausa en el segundo cero, con el volumen probado. Copia en el teléfono y en un USB | Si no existe o no abre: avisar a Carlos antes de las 12:00 |
| 10 | Demo por terminal lista | En el computador: `.venv/bin/python -m demo.correr --sin-pausas` termina con «33 de 33 bien» y «La demo sale igual que el guion» | Falla una verificación: leer cuál; si es del guion, se usa el video para ese paso |
| 11 | Demo local sin red (plan B) | `bash despliegue/local.sh` abre el tablero en `http://localhost:8501`. El bot no arranca sin red: el pedido y el cierre se envían con la terminal: `.venv/bin/python -m demo.correr` los muestra con el lector por reglas | Sin dependencias en el computador: `docs/SIN_CONEXION.md` y video |
| 12 | Quién habla y quién maneja | Quien habla no toca el computador. Acordado antes de subir | — |

Si los pasos 3 a 5 no dan lo esperado diez minutos antes, la demo en vivo se cambia por el video con la voz en directo. Mejor un video limpio que una demo rota.

## Si falla cada paso durante la demo

Es el cuadro de `docs/GUION_DEMO.md` resumido. Ahí está el detalle.

| Momento | Falla | Qué se hace |
|---|---|---|
| Pedido | El bot no responde en diez segundos | Repetir una vez. Si no, decir «el mismo mensaje, por el canal de respaldo» y mostrar el video de ese tramo |
| Pedido | El bot entiende mal (otro barrio, otra cantidad) | No corregir en vivo. Decir «por eso el despachador revisa antes de confirmar». Descartar y seguir con el video de ese tramo |
| Pedido | El bot ofrece varias opciones en vez de «Sí, es ahí» | Tocar San José. Es el comportamiento correcto: decirlo |
| Plan | Las rutas anteriores desaparecen y queda una sola | Se aprobó el plan 1 antes de tiempo. Terminal: `.venv/bin/python -m despacho.recalcular --segundos 3` |
| Plan | Plan vacío o «error interno» | Mostrar el motivo una vez. Repetir. Si vuelve a fallar, video |
| Cierre | El jurado escribe otra vía y el plan no cambia | «Esa vía no la usa ninguna ruta de hoy, así que el plan sigue igual». Quien maneja envía el mensaje de la avenida del Centro |
| Cierre | El jurado escribe un lugar desconocido | «Cuando no sabe, lo dice y pide un pin; no adivina». Luego el mensaje de la avenida del Centro |
| Cierre | El jurado tarda | A los quince segundos lo envía quien maneja |
| Recálculo | No aparece el aviso de recalcular | Terminal: `.venv/bin/python -m despacho.recalcular --segundos 3`. No usar «Calcular plan» con un plan aprobado |
| Recálculo | El plan nuevo no muestra el cambio esperado | Leer lo que sí muestra: pedidos atendidos y críticos a tiempo. No afirmar lo del campero si no está en pantalla |
| Cualquiera | Se cae internet | El mapa pierde el fondo y el bot deja de recibir. Video |
| Cualquiera | Se cae el tablero | Video. Si es una mentoría y no el pitch, `.venv/bin/python -m demo.correr` muestra todo por terminal |

## Si Railway no está bien

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| El tablero no abre | No hay dominio generado o el servicio cayó | Railway, ver logs del último despliegue. Redesplegar una vez. Si tarda, demo local (paso 11) |
| Los datos vuelven a cero o desaparecen | Falta el volumen en `/data` o `DESPACHOX_DB` apunta fuera de él | `DESPACHOX_DB=/data/despachox.db` o borrar la variable (`docs/DESPLIEGUE.md`) |
| El bot y el tablero no ven los mismos datos | Cada proceso usa su propia base | La misma ruta en `DESPACHOX_DB` para los dos |
| El bot da error de conflicto | Otro proceso usa el mismo token | Apagar el bot local |

## Ensayo en frío (la noche anterior o la mañana del sábado)

1. `.venv/bin/python -m demo.preparar` deja una base limpia y dice `[ok]` o `[FALLA]` en cada punto.
2. `.venv/bin/python -m demo.correr` recorre el guion con pausas, para ensayar en voz alta con el cronómetro. `--sin-pausas` lo corre de corrido.
3. Si el tablero local debe ver esa base: `export DESPACHOX_DB=<ruta que imprime preparar>` antes de arrancarlo.

Límites de este ensayo, para no prometer de más: el texto del barrio y el del cierre los lee el lector por reglas, no el modelo. No usa Telegram, ni clics del tablero, ni la nube. Prueba el despacho, la ubicación de lugares y la lógica de aprobar, no la red ni la interfaz.
