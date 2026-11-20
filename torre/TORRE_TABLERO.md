# Torre de control · C-tablero · rol C (tablero)
Última actualización: 2026-11-20 14:30 (hora de Colombia)

Sesión de Claude Code que lanzó Carlos para adelantar el módulo de Jacobo. Parte de `tablero/app.py` de Jacobo (commit e9e15fc) y lo reemplaza.

## Estado en una frase
El tablero está completo y probado de punta a punta en pantalla con la semilla real: confirmar, calcular, aprobar, cierre, recalcular, ubicar con pin y bitácora.

## Hecho (con el commit o archivo que lo prueba)
- `tablero/datos.py`: lecturas, indicadores, puntualidad con críticos aparte, comparación de planes, aviso de cierre sin aplicar, cambios de estado con bitácora y llamada a `despacho/` por proceso aparte.
- `tablero/tests/test_datos.py`: 17 pruebas con base temporal (`python -m pytest tablero -q`).
- `tablero/app.py`: cuatro indicadores, mapa con rutas numeradas por vehículo, bloque Plan, Por revisar (cierres, ubicaciones, pedidos), pestañas Plan en detalle y Bitácora, actualización cada 5 s.
- `tablero/README.md`: comando de arranque y qué hace cada parte.
- Verificado en el navegador con una base temporal cargada con la semilla (`despacho.semilla --cargar --reiniciar`): «Calcular plan» dejó el plan 1 con 17 de 17 pedidos en 3 vehículos en 8 s; «Aprobar» lo aprobó con el nombre escrito; al confirmar un cierre salió el aviso; tras «Recalcular» con un cierre puesto sobre la ruta del Camión 2 se leyó «Cambian de ruta: Camión 2, Campero 2» y la llegada más afectada. El zoom se conservó tras 8 s de actualizaciones.
- Sobre la base compartida solo se comprobó que la pantalla carga sin excepciones. No se pulsó nada ahí.

## En curso (qué, hasta dónde llegó, qué falta)
Nada en curso.

## Siguiente paso exacto (el comando o el archivo por donde seguir)
Jacobo: `streamlit run tablero/app.py` con `DESPACHOX_DB` apuntando a la base compartida, recorrer el guion de la demo y anotar qué sobra y qué falta.

## Decisiones y por qué
- El plan que se muestra es la última propuesta y, si no hay, el aprobado. El despachador tiene que ver lo que espera su decisión.
- Un pedido sin atender cuenta como no entregado a tiempo en el indicador. El denominador son todos los pedidos que el plan consideró.
- La puntualidad se calcula en el tablero con `llegada_estimada` contra `limite_en`; si el pedido no trae límite, se usa el plazo por urgencia que el plan declara en `resumen.supuestos`.
- Las llegadas de dos planes se comparan en minutos desde la hora de cálculo de cada uno, para no contar como cambio el tiempo entre cálculos.
- Un pedido sin punto no se puede confirmar: ninguna ubicación entra al plan sin que una persona la confirme (regla de `lugares/`).
- Un cierre que un recálculo ya vio y no pudo amarrar a la red no vuelve a pedir recálculo; si no, el aviso quedaría fijo.
- `app.py` quita `tablero/` de la ruta de importación: Streamlit la pone primero y `datos` resolvía a `tablero/datos.py` en vez del paquete `datos/`.
- Colores de ruta fijos por `vehiculo_id`, para que un vehículo no cambie de color entre planes.

## Bloqueos y preguntas para el capitán
- El cierre de la demo debe caer sobre una ruta del plan. Con la semilla, «vía a Chinchiná» se aplicó y no cambió ninguna ruta («Ningún vehículo cambia de ruta»). Hay que elegir un tramo que sí toque una ruta o ajustar la semilla. Es de B-despacho y del guion.
- El tablero no puede completar un pedido que el modelo no leyó (familias, productos) ni ubicar un pedido sin propuesta de ubicación. Las reglas del módulo solo permiten cambiar estados.
- Si se rechaza el plan de un recálculo, no queda plan vigente: `despacho/` ya marcó el anterior como reemplazado.

## Observaciones de mentores (textuales, con hora)

## Cómo correr lo mío (comandos, variables de entorno sin sus valores)
- `export DESPACHOX_DB=<ruta absoluta a datos/despachox.db de la carpeta principal>`
- `streamlit run tablero/app.py`
- `python -m pytest tablero -q`
- El tablero no usa claves de `.env`.

## Aporte a la rúbrica (criterio → evidencia)
- Criterio 2 (prototipo): la pantalla de la demo corre de punta a punta con la semilla; 17 pruebas automáticas.
- Criterio 5 (viabilidad): cada plan lo aprueba una persona con su nombre y queda en la bitácora; ninguna ubicación entra al plan sin confirmación.
- Criterio 6 (impactos): los dos indicadores del reto están arriba, con los puntos críticos aparte.
