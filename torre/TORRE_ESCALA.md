# Torre de control · Carlos · sesión de Claude Code para el encargo S3 (rama `escala`, PR #11)
Última actualización: sábado 21 de noviembre de 2026, 13:20

Torre aparte de `TORRE_CAPITAN.md` para no chocar con las otras sesiones de Carlos. Este archivo es el resumen para revisar el PR [cmorregof/despachoX#11](https://github.com/cmorregof/despachoX/pull/11): qué se hizo, qué decidió Carlos en el camino, qué revisar y qué falta.

## Estado en una frase
Las tres partes del encargo S3 están hechas y medidas en `escala`; además, por decisión de Carlos, el modelo resume cada grupo y la mesa entera, el bot lee con Sonnet 5.5 y el resumen usa Sonnet 5.5 por grupo y Opus 5.5 para la mesa. 607 pruebas pasan (antes 568), `main` fusionado sin conflictos de código, PR abierto para que Carlos haga el merge.

## Qué entra, por archivo

| Archivo | Qué es | Pruebas |
|---|---|---|
| `despacho/escala.py` (nuevo) | Arnés de medición: base temporal con la semilla, un punto por barrio (138), N pedidos sintéticos con frases de casos especiales; mide consultas del tablero, AppTest y `planificar`; `--agrupar` | sin pruebas propias; es un arnés |
| `docs/ESCALA_DESPACHO.md` (nuevo) | Todas las cifras medidas, máquina, condiciones, lo que no se midió, capturas | — |
| `despacho/agrupar.py` (nuevo) | Regla determinista: ST-DBSCAN del triage (250 m, 6 h, min 2) sobre punto y hora, partido por punto de entrega; familias y kilos sumados con tope T_z de `triage/censo.py`; `Grupo.como_pedido()`; `DESPACHOX_AGRUPAR` | `test_agrupar.py` (14), incluye equivalencia con `cluster.st_dbscan` |
| `despacho/optimizar.py` (editado) | Gancho `_agrupar_pedidos`: con la variable, un pedido por grupo (id = pedido más antiguo); `resumen.grupos`; `sincronizar_aprobados` marca a los miembros; `--agrupar` | `test_agrupar_plan.py` (5): apagado = igual que hoy |
| `despacho/resumen_grupo.py` (nuevo) | El modelo lee: `texto_para_modelo` (todos los textos del grupo, limpios), `resumir`, `texto_mesa` y `resumir_mesa` (una llamada sobre los resúmenes), comando `--resumir [--falso] [--todos]`, reintentos, cifras en bitácora | `test_resumen_grupo.py` (9), extractor falso |
| `datos/esquema.sql` (editado) | Tabla nueva `resumenes_grupo`; no cambia ninguna tabla existente | — |
| `tablero/datos.py`, `tablero/app.py` (editados) | `grupos_por_revisar`, `resumen_mesa`, `confirmar_grupo`, `descartar_grupo`, `resumir_grupos`; tarjetas de grupo y «La mesa en pocas líneas» con el botón «Resumir con el modelo», detrás de la variable; `por_revisar` con una sola consulta de repetidos | `test_grupos.py` (10), con AppTest |
| `entrada/extraer.py`, `entrada/carga.py`, `evaluacion/lector/medir_modelo.py`, `.env.example` | Sonnet 5.5 por defecto; `PRECIOS_MTOK` por modelo; costo solo si hay precio | las de `entrada/` siguen pasando |
| `datos/db.py` (editado) | `ruta_env()`: el `.env` de la carpeta principal cuando se trabaja en una copia de git | — |
| `docs/capturas/` (nuevo) | Cuatro imágenes del tablero con 15.000 pedidos | — |

## Cifras que se pueden citar (todas medidas aquí, Apple M5, 21 nov)

- Tablero con 15.000 pedidos (7.584 nuevos): página completa 13,2 s → 6,5 s tras arreglar `por_revisar` (5,6 → 0,02 s); con grupos 4,4 s; 278 botones en vez de 15.170.
- `planificar` sin agrupar, 8 s de solver: termina siempre entre 8,3 y 9,0 s; atiende 48/50, 89/100, 106/250, 100/500, 91/1.000; desde 250 el techo es la flota (6.240 kg).
- Agrupar 15.000 pedidos: 0,13 s, 138 grupos (uno por punto); familias 321.506 → 35.518 con tope; plan en 8,9 s, 8 grupos atendidos, 4 de 5 críticos a tiempo.
- Resumen real (Carlos, 12:31, Opus 5.5 con los topes viejos): 131 de 138 grupos y la mesa en 11 s. Tokens y costo no registrados en esa corrida (ya se guardan en la bitácora).

## Decisiones de Carlos durante la sesión
1. 12:20 · Arreglar `por_revisar` aunque sea posterior al congelamiento.
2. 12:35 · Que el modelo resuma los 138 grupos y la mesa entera para el despachador (lectura, no decisión).
3. 12:40 · Sonnet para el bot de Telegram, Opus para el tablero; se eligieron las 5.5 por precio.
4. 12:55 · Sin topes (todos los textos, resumen sin cortar); Sonnet 5.5 por grupo y Opus 5.5 solo para la mesa.
5. 13:05 · Push y PR a `main`; Carlos hace el merge.

## Decisiones mías, para revisar
- Un grupo = un punto de entrega dentro de un clúster espacio-temporal. ST-DBSCAN encadena en el tiempo, así que con pedidos continuos sale un grupo por punto. Una ventana en bloques sería otra regla.
- El pedido más antiguo representa al grupo en `paradas.pedido_id`: la tabla `paradas` no cambia; `resumen.grupos` guarda los miembros y `aprobar` los pasa a `asignado`.
- `st_dbscan_min2` (del agente): misma partición que `cluster.st_dbscan` con `min_samples=2` en O(n log n), con prueba de equivalencia, porque con miles de pedidos en un punto el original tardaba 4,6 s.
- Pedidos sintéticos de las últimas 3 h, no 6, para que ningún crítico nazca vencido; la primera corrida daba 4 de 7 por ese artefacto.
- El resumen de la mesa se guarda con clave `mesa:<hash de las claves de los grupos>`: si cambian los grupos, el resumen viejo deja de mostrarse.
- La instrucción al modelo le prohíbe cambiar cantidades y ordenar grupos; la tarjeta dice «No decide el orden: eso es suyo».

## Qué revisar con más cuidado
- `despacho/optimizar.py`: que con `DESPACHOX_AGRUPAR` apagada no cambie nada (la prueba `test_apagado_una_parada_por_pedido` y las 568 pruebas previas lo cubren; la demo por terminal no se volvió a ensayar a mano).
- El cambio de modelo del bot a Sonnet 5.5 toca producción en Railway en cuanto se fusione: unas 20 veces el costo por token de Haiku y respuesta algo más lenta. La ficha dice 1,75 a 4,50 USD por 10.000 mensajes con Haiku; con Sonnet serían 35 a 90, sin medir.
- La tabla nueva `resumenes_grupo` se crea sola con `CREATE TABLE IF NOT EXISTS` al conectar.
- Documentos del jurado: no se tocaron.

## Lo que no está
- Un grupo que no cabe en el vehículo que llega al punto queda sin atender: el modelo planea un viaje por vehículo.
- El mapa dibuja un círculo por pedido (unos 4 s de los 4,4 con 15.000).
- `planificar` con 15.000 pedidos sueltos no se intentó (tablas de unos 20 GB).
- La corrida real con la configuración final (Sonnet por grupo, sin topes) no se ha hecho; el comando con `--todos` está en el canal.

## Cómo correr lo mío
```bash
.venv/bin/python -m pytest -q -p no:cacheprovider
.venv/bin/python -m despacho.escala --tablero --pedidos 15000 --agrupar
.venv/bin/python -m despacho.escala --planificar 50 100 250 500 1000 15000 --agrupar
DESPACHOX_AGRUPAR=1 .venv/bin/python -m despacho.resumen_grupo --resumir --falso
DESPACHOX_AGRUPAR=1 .venv/bin/python -m despacho.resumen_grupo --resumir --todos   # con la clave del .env
```

## Aporte a la rúbrica
- Criterio 2 → tablas medidas en `docs/ESCALA_DESPACHO.md`, 39 pruebas nuevas, capturas reales.
- Criterio 5 → el cuello de botella queda nombrado con cifras: la flota, no el software; y el costo del modelo por mensaje cambia con Sonnet.
