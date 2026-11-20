# Encargo C · Tablero (Jacobo)

Soy Jacobo. Mi rol hoy es C (tablero). Crea mi torre `torre/TORRE_JACOBO.md` desde la plantilla y mantenla al día.

Lee `CLAUDE.md`, `docs/ROLES_VIERNES.md`, `datos/esquema.sql` y `datos/db.py`.

## Objetivo

La pantalla del despachador: un mapa de Manizales donde ve pedidos, cierres y rutas, y desde donde confirma, pide un plan y lo aprueba. Es lo que el jurado va a mirar durante la demo.

## Reglas de este módulo

- Trabajo solo dentro de `tablero/`. Leo todas las tablas con `datos.db.conectar()`. Solo cambio estados: `pedidos.estado`, `cierres.estado`, `planes.estado`, `planes.aprobado_por` y `planes.aprobado_en`. Cada cambio se anota con `datos.db.anotar()`.
- No calculo rutas. Para pedir un plan ejecuto `python -m despacho.optimizar` o `python -m despacho.recalcular` con `subprocess` y muestro el resultado.
- Mientras no exista la semilla de Carlos, uso `tablero/datos_falsos.py` para llenar una base local con cinco puntos, tres pedidos y una ruta inventada. Debe poder borrarse sin tocar nada más.

## Pasos

1. `tablero/app.py` con Streamlit y streamlit-folium, ancho completo. Mapa centrado en Manizales (5.07, -75.52) con:
   - acopios (icono de bodega), puntos de entrega (los críticos resaltados);
   - pedidos por color según estado y tamaño según urgencia;
   - cierres en rojo, punteados si están `reportado` y sólidos si `confirmado`;
   - rutas del plan vigente, un color por vehículo, dibujadas desde `paradas.geometria`.
2. Columna lateral «Por revisar»: pedidos `nuevo` con su texto original y botones Confirmar y Descartar; cierres `reportado` con botones Confirmar y Levantar. Los duplicados se muestran agrupados bajo el pedido original.
3. Bloque «Plan»: botón «Calcular plan», tabla por vehículo (orden, punto, hora estimada, kilos), tiempo de cálculo, y botones Aprobar y Rechazar. Si se confirma un cierre con un plan aprobado, aparece el aviso «Hay un cierre nuevo: recalcular».
4. Fila de indicadores arriba: pedidos pendientes, kilos de perecederos que vencen en menos de 12 horas, cierres activos, porcentaje de pedidos del plan que llegan a tiempo.
5. Actualización automática cada cinco segundos, para que un mensaje enviado al bot aparezca solo.
6. Pestaña «Bitácora» con las últimas decisiones.
7. Abajo del mapa, la atribución «© colaboradores de OpenStreetMap».

## Hecho cuando

Con la base cargada, abro `streamlit run tablero/app.py`, veo pedidos y cierres en el mapa, confirmo un pedido, pulso «Calcular plan», veo las rutas dibujadas y apruebo el plan. Todo sin tocar la terminal.

## En paralelo

Lanza un agente Sonnet para `datos_falsos.py` mientras armas el mapa. Cuando todo funcione, pide a un agente Opus que revise la pantalla como si fuera un despachador con prisa y te diga qué sobra.

**Aporta a:** criterio 2 (es la cara de la demo) y criterio 5 (se ve que un humano decide).
