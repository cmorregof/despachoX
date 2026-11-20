# Encargo C · Tablero (Jacobo)

Revisado por `maestro` el viernes a las 2:45 p. m. El tablero ya está en `main` (commit `1730169`, sesión `C-tablero`): indicadores, mapa, plan, aprobación, aviso de cierre, «qué cambió», ubicaciones con pin, bitácora y 17 pruebas. Este encargo ya no pide construirlo: pide lo que falta para la demo. Los cambios frente a la versión de la mañana están al final de `docs/SUGERENCIAS.md`.

Quien corra este encargo se llama `C-tablero` en el canal y sigue la torre `torre/TORRE_TABLERO.md`. Jacobo prueba el tablero como despachador y anota en `torre/TORRE_JACOBO.md` qué sobra y qué falta.

Haz `git pull --rebase`. Lee `CLAUDE.md`, `torre/CANAL.md`, `tablero/README.md`, `lugares/README.md`, `docs/GUION_DEMO.md`, que es la secuencia exacta de clics que el tablero debe soportar, y la sugerencia 2 de `docs/SUGERENCIAS.md`.

## Objetivo

La pantalla del despachador: un mapa de Manizales donde ve pedidos, cierres y rutas, y desde donde confirma, pide un plan y lo aprueba. Es lo que el jurado va a mirar durante la demo.

## Reglas de este módulo

- Trabajo solo dentro de `tablero/`. Leo todas las tablas con `datos.db.conectar()`. Solo cambio estados, y cada cambio queda en la bitácora.
- Para las ubicaciones llamo `lugares.confirmar` y `lugares.corregir_con_pin`. Para aprobar, `python -m despacho.optimizar --aprobar ID --quien NOMBRE`, que además pasa los pedidos a `asignado`.
- No calculo rutas. Los planes los pido a `despacho/` con `subprocess`.
- El bot, el despacho y el tablero comparten la base: la misma ruta absoluta en `DESPACHOX_DB`.

## Lo que falta, en orden

1. **«Calcular plan» con un plan ya aprobado.** Hoy ese botón llama siempre `despacho.optimizar`. Si ya hay un plan `aprobado` y entra un pedido nuevo, `optimizar` planea solo ese pedido; al aprobar ese plan, el anterior queda `reemplazado` y las rutas de los otros 17 pedidos desaparecen del mapa, aunque siguen `asignado` (medido). Regla: si existe un plan `aprobado`, el botón ejecuta `python -m despacho.recalcular`, que vuelve a planear todo; `optimizar` solo cuando no hay plan aprobado. Ojo con `cierres_sin_aplicar`, que lee el motivo «cierre N»: un recálculo por pedido nuevo hoy queda con el motivo «recálculo sin cierres confirmados», y B puede añadir `--motivo`.
2. **Búsqueda de 3 segundos.** Pasar `--segundos 3` a `optimizar` y a `recalcular`. Con la semilla da el mismo resultado esencial que con 8 (medido) y cada plan baja de unos 9 a unos 4 segundos, que en una demo de 75 segundos con dos planes es la diferencia.
3. **Recorrer el guion.** Con la base recién cargada, los pasos de `docs/GUION_DEMO.md` de principio a fin, primero con las filas insertadas por terminal y después con el bot real. Anotar en la torre cualquier texto de pantalla que no coincida con el guion y avisarle a `maestro` o a Carlos para corregir el guion, no el tablero.
4. Después de la mentoría, y solo si Carlos lo decide antes de la congelación del sábado a las 8:30 a. m., porque son funciones nuevas que escriben fuera de los estados:
   - formulario «Digitar pedido» para cuando no hay internet ni modelo. La ficha y el pitch lo prometen;
   - marcar un punto como crítico;
   - paquetes con código y botón «Entregado» (sugerencia 9).
5. Al terminar cada punto: LISTO en el canal con cómo probarlo, commit y push.

## Hecho cuando

Antes de las 7:00 p. m., con la base recién cargada (`python -m despacho.semilla --cargar --reiniciar`), abro `streamlit run tablero/app.py` y hago sin tocar la terminal:

1. «Calcular plan»: veo tres rutas, 17 de 17 pedidos y 3 de 3 críticos a tiempo.
2. Llega por el bot el pedido de San José. Lo confirmo, pido el plan y veo 18 de 18. Apruebo.
3. Con el plan aprobado, llega el cierre de la avenida del Centro. Lo confirmo, pulso «Recalcular» y veo el aviso `camion: punto:14 quedó aislado de la red` y el pedido nuevo de San José en un campero. Apruebo.
4. Repito el paso 2 con el plan del paso 1 ya aprobado: las rutas de los 17 pedidos anteriores siguen en el mapa.

## En paralelo (Jacobo)

Abrir el tablero, recorrer el guion como despachador con prisa y anotar qué sobra. La sugerencia 10 de `docs/SUGERENCIAS.md` es suya: grabar el video de respaldo esta noche, con la base recién cargada.

**Aporta a:** criterio 2 (es la cara de la demo) y criterio 5 (se ve que un humano decide).
