# Encargo A · Entrada (Samuel)

Revisado por `maestro` el viernes a las 2:40 p. m. El módulo ya está en `main` (commit `45fb718`, sesión `A-entrada`): extracción con Haiku, limpieza de datos personales, escritura en `pedidos` y `cierres`, conversación con `lugares` y adaptador de Telegram, con 39 pruebas sin red. Este encargo ya no pide construirlo: pide lo que falta para la demo. Los cambios frente a la versión de la mañana están al final de `docs/SUGERENCIAS.md`.

Quien corra este encargo se llama `A-entrada` en el canal y sigue la torre `torre/TORRE_ENTRADA.md`. Samuel lleva además la ficha de los seis componentes.

Haz `git pull --rebase`. Lee `CLAUDE.md`, `torre/CANAL.md`, `torre/TORRE_ENTRADA.md`, `entrada/README.md`, `lugares/README.md`, `docs/GUION_DEMO.md` y la sugerencia 2 de `docs/SUGERENCIAS.md`.

## Objetivo

Un bot de Telegram al que cualquiera le escribe en lenguaje libre y que deja en la base un pedido de ayuda o un cierre vial bien estructurado, le contesta al remitente lo que entendió y le pregunta si el lugar es el correcto.

## Reglas de este módulo

- Trabajo solo dentro de `entrada/`. Escribo directamente en `pedidos` y `cierres`. Las tablas `ubicaciones`, `lugares` y `puntos` solo las toco a través de las funciones de `lugares`, con la excepción ya avisada en el canal: una propuesta anterior pasa a `rechazada` cuando la persona corrige el lugar por texto. De otras carpetas importo únicamente `datos.db` y `lugares`.
- El modelo solo extrae. No asigna prioridad final ni decide nada. Los kilos los calcula una tabla, no el modelo.
- No guardo nombres, teléfonos ni el id del chat en claro.
- Claves en `.env` (`TELEGRAM_BOT_TOKEN`, `ANTHROPIC_API_KEY`). La base es la de `DESPACHOX_DB`, la misma ruta absoluta que usan el despacho y el tablero.

## Lo que falta, en orden

1. **Las claves y una corrida real.** Es el bloqueo que A dejó en el canal a las 2:30 p. m. Con el token de BotFather y la clave de Anthropic en `.env`, arrancar `python -m entrada.bot` y enviar desde un teléfono los dos mensajes de la demo. Medir el tiempo de respuesta. Hasta que esto pase, nadie ha visto contestar al bot.
2. **Entrada por terminal.** `entrada/procesar.py`, una capa delgada sobre `flujo.Mesa`: `python -m entrada.procesar "texto"` imprime lo que contestaría el bot y deja las mismas filas; con `--si` confirma la ubicación propuesta. Es el respaldo de la demo cuando Telegram o la red fallan, y está citado en `docs/GUION_DEMO.md`.
3. **Kilos por producto.** Hoy los kilos se guardan solo si el mensaje los trae, y el optimizador descarta los productos sin kilos: surte un mercado genérico sin perecederos, así que quien pidió leche no la recibe y otros pedidos quedan cortos. Añadir `entrada/raciones.py` con la tabla de kilos por familia de `KG_POR_FAMILIA` en `despacho/semilla.py` (arroz 2, frijol 1, lenteja 1, aceite 1, panela 0,5, agua 3, harina de maíz 1, leche 2, pan 0,5, huevos 1, fruta 1,5, verdura 1,5, pollo 1). Si el mensaje no trae kilos y sí familias, cada producto se guarda con `familias × ración`, `kg_estimado` es la suma, y la respuesta lo dice como estimado. Un producto que no esté en la tabla se deja sin kilos. Es una regla, no una decisión del modelo. Antes de hacerlo, mira en el canal si B prefirió resolverlo en `despacho/`; se lo pregunté a las 2:40 p. m.
4. **Duplicados.** `guardar.marcar_duplicado` marca cualquier pedido del mismo punto en dos horas. El optimizador ignora todo pedido con `duplicado_de`, así que dos comités del mismo barrio se pisan. Añadir la condición de que coincida `remitente_hash`.
5. **Medir el extractor.** `python -m pytest entrada/pruebas/test_campos.py -s` con la clave, y pasar el número a la ficha con su fila en `docs/FUENTES.md`. Puede esperar a después de la mentoría.
6. Al terminar cada punto: LISTO en el canal con cómo probarlo, commit y push.

## Hecho cuando

Antes de las 7:00 p. m., con la semilla recién cargada (`python -m despacho.semilla --cargar --reiniciar`):

- Desde un teléfono escribo «somos 40 familias en san jose no hay arroz ni leche». En menos de diez segundos hay una fila en `pedidos` con 40 familias y arroz y leche a 80 kg cada uno, y el bot me pregunta «Ubiqué «san jose» en: San José (barrio). ¿Es correcto?». Toco **Sí, es ahí** y la fila queda con `punto_id` 14.
- Escribo «derrumbe en la avenida del centro, no pasa camion, si pasa moto». Hay una fila en `cierres` con estado `reportado`. Toco **Sí, es ahí** y queda con `lugar` «avenida del Centro» y la arista 582617778 → 323215241.
- Los dos mensajes dan el mismo resultado con `python -m entrada.procesar --si "..."`.

Son los mensajes de `docs/GUION_DEMO.md`. Solo se pueden usar lugares de `datos/semilla/barrios.csv` y las quince vías de `vias.csv`.

## En paralelo (Samuel)

Un agente Sonnet redacta en `docs/FICHA.md` los componentes 1, 2 y 3, usando `docs/ESTADO_DEL_ARTE.md`, `docs/investigacion/04_evidencia_del_problema.md` y `docs/SIMULACION.md`. Cada cifra con su enlace y su fila en `docs/FUENTES.md`, que hoy está vacío, y marcadas las que nadie del equipo ha verificado todavía. Samuel revisa el texto antes del commit. Las sugerencias 5, 7 y 8 de `docs/SUGERENCIAS.md` son suyas.

**Aporta a:** criterio 2 (demo en vivo con el teléfono de un jurado) y criterio 1 (ficha).
