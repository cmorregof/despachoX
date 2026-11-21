# Torre de control · Carlos · sesión de Claude Code para el encargo S3 (rama `escala`)
Última actualización: sábado 21 de noviembre de 2026, 12:10

Torre aparte de `TORRE_CAPITAN.md` para no chocar con las otras sesiones de Carlos. Fable revisa y fusiona la rama.

## Estado en una frase
Las tres partes del encargo S3 están hechas en la rama `escala` y medidas: 15.000 pedidos se agrupan en 138 grupos en 0,13 s y el plan sale en 8,9 s; el tablero tarda 13 s en pintar 7.584 pedidos nuevos.

## Hecho
- `despacho/escala.py`: arnés de medición (base temporal, un punto por barrio, pedidos sintéticos; mide consultas, AppTest y `planificar`).
- `docs/ESCALA_DESPACHO.md`: todas las cifras, máquina, condiciones y lo que no se midió.
- `despacho/agrupar.py` + `despacho/tests/test_agrupar.py` (agente Opus): regla determinista con el ST-DBSCAN del triage y topes T_z.
- `despacho/optimizar.py`: gancho `DESPACHOX_AGRUPAR` / `--agrupar`; `resumen.grupos`; `sincronizar_aprobados` marca a los miembros. Prueba: `despacho/tests/test_agrupar_plan.py`.
- `despacho/resumen_grupo.py` + pruebas y tabla `resumenes_grupo` en `datos/esquema.sql` (agente Opus). Extractor inyectado; sin llamada real al modelo.
- Vista de grupos en `tablero/app.py` y `tablero/datos.py`, detrás de la variable; pruebas en `tablero/tests/test_grupos.py`.

## Decisiones y por qué
- Un grupo = un punto de entrega dentro de un clúster espacio-temporal. ST-DBSCAN encadena en el tiempo, así que con pedidos continuos sale un grupo por punto. Dejado así; ventana en bloques es otra regla.
- El pedido más antiguo del grupo representa al grupo en `paradas.pedido_id` (la tabla no cambia); `resumen.grupos` guarda los miembros.
- El agente reemplazó `cluster.st_dbscan` por `st_dbscan_min2`, que da la misma partición en O(n log n) (prueba de equivalencia incluida), porque con miles de pedidos en el mismo punto el original tardaba 4,6 s.
- Pedidos sintéticos de las últimas 3 h (no 6) para que ningún crítico nazca vencido: la primera corrida daba 4 de 7 críticos a tiempo por ese artefacto.
- Tabla nueva `resumenes_grupo`: avisado en el canal.

## Lo que no se hizo o no se midió
- `planificar` con 15.000 pedidos sueltos (tabla de tiempos de unos 20 GB).
- Tablero con la vista de grupos encendida.
- El modelo real resumiendo grupos.
- Un grupo que no cabe en el vehículo que llega al punto queda sin atender; hoy el modelo es un viaje por vehículo.

## Cómo correr lo mío
```bash
.venv/bin/python -m despacho.escala --tablero --pedidos 15000
.venv/bin/python -m despacho.escala --planificar 50 100 250 500 1000 15000 --agrupar
DESPACHOX_AGRUPAR=1 .venv/bin/python -m despacho.optimizar
.venv/bin/python -m pytest -q -p no:cacheprovider
```

## Aporte a la rúbrica
- Criterio 2 → tablas medidas en `docs/ESCALA_DESPACHO.md`; pruebas nuevas (33) que pasan.
- Criterio 5 → el cuello de botella queda nombrado con cifras: la flota, no el software.
