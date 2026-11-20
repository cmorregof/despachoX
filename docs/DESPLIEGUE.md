# Despliegue en la nube (Railway)

Objetivo: que el bot y el tablero funcionen sin depender del computador de nadie. Cualquiera del equipo le escribe al bot desde su teléfono y abre el tablero desde una dirección pública.

## Por qué todo va en Railway y nada en Vercel

El tablero está hecho en Streamlit, que es un servidor de Python que mantiene una conexión abierta con el navegador. Vercel sirve páginas estáticas y funciones de corta duración, y no puede alojar eso. Además el bot, el tablero y el optimizador comparten un archivo SQLite, y un volumen de Railway se monta en un solo servicio. Por eso va **un solo servicio con las tres cosas adentro**: lo arma `Dockerfile` y lo arranca `despliegue/arranque.sh`.

## Pasos

1. **Antes de desplegar, sube la red vial al repositorio.** Así el arranque no depende de que el servidor de OpenStreetMap responda desde Railway. En tu computador:
   ```bash
   mkdir -p despliegue/grafo
   cp despacho/cache/manizales_region.graphml despliegue/grafo/
   git add -f despliegue/grafo/manizales_region.graphml
   git commit -m "[capitán] Red vial para el despliegue" && git push
   ```
   Si no lo haces, el arranque intenta descargarla y puede tardar o fallar.
2. En Railway: **New Project → Deploy from GitHub repo →** `cmorregof/despachoX`. Detecta el `Dockerfile` solo.
3. Al servicio, añade un **volumen** con ruta de montaje `/data`. Ahí viven la base y la red vial.
4. **Variables** del servicio:
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `DESPACHOX_SAL`: cualquier cadena larga al azar. Fija el hash de los remitentes entre reinicios.
   - `PORT=8080`, para que el tablero escuche en el mismo puerto que se le indica al dominio.
   - No hace falta definir `DESPACHOX_DB` ni `DESPACHOX_GRAFO`: por defecto apuntan a `/data`.
5. **Settings → Networking → Generate Domain.** Pide el puerto: `8080`, el mismo de la variable `PORT`. Esa dirección es el tablero.
6. Mira los registros. Deben aparecer, en orden: red vial, datos de prueba, «Bot en marcha» y la dirección de Streamlit.
7. Prueba: escríbele al bot desde el teléfono y mira el pedido aparecer en el tablero.

## Cosas que hay que saber

- **Un solo bot a la vez.** Telegram solo admite un proceso leyendo con el mismo token. Si el bot corre en Railway, **nadie lo corre en local** con ese token, o los dos fallan con un error de conflicto. Para desarrollo local, crea un segundo bot en BotFather.
- **Una sola réplica.** No escales el servicio: dos copias serían dos bots y dos bases.
- **Reiniciar los datos de prueba** antes de un ensayo: pon la variable `DESPACHOX_REINICIAR=1`, deja que redespliegue, y luego quítala. Si no la quitas, cada reinicio borra los datos. (La sesión del tablero tiene pendiente un botón para esto.)
- **El tablero queda público.** Cualquiera con la dirección puede aprobar un plan. Para la demo sirve; no pongas datos reales ahí. No compartas la dirección fuera del equipo y del jurado.
- **Cada `git push` a `main` redespliega** y corta el bot unos segundos. Antes del pitch, desactiva el despliegue automático o no subas nada.
- **Plan B obligatorio.** El wifi del campus o Railway pueden fallar durante el pitch. La versión local (`docs/GUIA_SIGUIENTE.md`, paso 0) debe seguir funcionando en un computador, con un segundo token, y el video de respaldo debe existir.

## Si algo falla

| Síntoma en los registros | Causa probable | Qué hacer |
|---|---|---|
| Se queda en «descargando de OpenStreetMap» o falla ahí | No se subió la red vial al repositorio | Paso 1 |
| `Conflict: terminated by other getUpdates request` | Otro proceso usa el mismo token | Apagar el bot local |
| El tablero abre y «Calcular plan» falla | Falta la red vial en `/data/cache` o el volumen no está montado | Revisar el volumen y redesplegar |
| El tablero no abre | El servicio no tomó el puerto | Confirmar que se generó el dominio; Railway define `PORT` solo |
| Los datos desaparecen al redesplegar | No hay volumen en `/data`, o `DESPACHOX_DB` apunta fuera de él (pasó el 20 de noviembre: valía `samcarjac`, una ruta relativa dentro del contenedor) | Paso 3, y `DESPACHOX_DB=/data/despachox.db` o borrar la variable |

Este despliegue no se ha probado: lo escribió Fable sin acceso a Railway. La primera vez puede necesitar un ajuste; pega el error en el canal.
