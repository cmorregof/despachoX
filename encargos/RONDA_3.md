# Ronda 3 · tres encargos cortos (sesiones de Carlos)

Cada sesión: `git pull --rebase`, leer las entradas del canal desde las 14:20 y `docs/PLAN_EQUIPO.md` (sección «Decisiones del capitán»). Cada etapa termina con pruebas, commit, push y LISTO en el canal.

## B-despacho

1. **`empaque_activo` deja de ser decorativo.** En el surtido, un lote perecedero con `empaque_activo=1` vence más tarde: multiplica el tiempo restante hasta `vence_en` por `FACTOR_EMPAQUE_ACTIVO`, constante declarada como supuesto (valor inicial 1,5; se lee de `DESPACHOX_FACTOR_EMPAQUE`). Va al `resumen.supuestos` de cada plan con la nota «supuesto, pendiente de datos del ICTA; patente UNAL 37476». Prueba: el mismo lote con y sin empaque activo cambia qué pedidos se pueden surtir.
2. **Trazabilidad mínima.** Al aprobar un plan, crear una fila en `paquetes` por parada: código corto único, `pedido_id`, `lote_id` principal, kilos, estado `en_ruta`. Función `entregar(con, codigo, quien)` que pasa el paquete y su pedido a `entregado` y lo anota en la bitácora. Línea de órdenes: `python -m despacho.paquetes --entregar CODIGO`.
3. **Plan vigente.** El plan anterior pasa a `reemplazado` cuando se aprueba el nuevo, no cuando se propone. Avisa a `C-tablero` y a `simulacion` antes de subirlo y verifica que sus pruebas siguen pasando.

## C-tablero

1. **Urgente:** con un plan aprobado, «Calcular plan» ejecuta `despacho.recalcular --motivo "pedido nuevo"`, no `despacho.optimizar`. Pasa `--segundos 3`.
2. Botón para marcar o desmarcar un punto como crítico, con anotación en la bitácora.
3. Pestaña «Entregas»: paquetes del plan aprobado con su código y estado, y botón «Entregado» que llama `despacho.paquetes.entregar`. Si `segno` está instalado, muestra el QR del código.
4. Un pedido que el modelo no pudo leer se puede completar en el tablero: familias, productos y lugar. Es el «se digita a mano» que promete la ficha.

## simulacion

Ejecuta `encargos/S2_SIMULACION_CRITICOS.md` sobre el grafo urbano original (`DESPACHOX_GRAFO=despacho/cache/manizales.graphml`), para que las cifras sean comparables con la primera corrida. Añade una corrida corta con y sin `empaque_activo` en la mitad de los lotes perecederos, solo si B ya subió ese cambio, y repórtala como sensibilidad a un supuesto.
