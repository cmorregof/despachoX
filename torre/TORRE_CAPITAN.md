# Torre de control · Carlos · capitán
Última actualización: viernes 20 de noviembre de 2026, 8:20 a. m.

## Estado en una frase
Repositorio montado con estrategia, prompt del equipo, torre de control y revisión del estado del arte; todavía no hay código.

## Hecho
- Lectura completa del sitio de la hackathon: bases, rúbrica, fichas de las ocho verticales, patentes, banco de capacidades, equipos. Resumen en `docs/ESTRATEGIA.md`.
- Propuesta de producto para la vertical 04 y horario de las dos jornadas.
- Prompt del equipo en `CLAUDE.md` y `docs/PROMPT_EQUIPO.md`.
- Revisión del estado del arte con cinco agentes: síntesis en `docs/ESTADO_DEL_ARTE.md`, informes en `docs/investigacion/`.

## En curso
- Nada. Falta que el equipo abra las fuentes y pase las cifras a `docs/FUENTES.md`.

## Siguiente paso exacto
0. **Tarea 0 (antes de las 2:30 p. m.):** cada integrante verifica un informe de `docs/investigacion/`. Instrucciones y reparto en `docs/TAREA_0.md`. Cierre de diez minutos a las 2:15 p. m.
1. Confirmar con Samuel que la vertical inscrita es la 04.
2. Preguntar en la mesa: duración del pitch, forma de entrega, jurados, acceso real al software de ruteo UNAL y a los datos de la ficha.
3. Asignar roles A, B, C y D con nombre.
4. A las 2:30 p. m.: esqueleto de punta a punta (pedido por chat → ruta en el mapa).

## Decisiones y por qué
- Usuario principal: ABACO y el Banco de Alimentos. Es quien ya opera desde Manizales y ya dijo en prensa que su reto es el transporte.
- No repetir «desabastecimiento en 48 horas» como hecho: no tiene fuente para este sismo.
- Capacidad UNAL principal: indicador A25 del IDEA como riesgo de tramo. Segunda: patente del empaque captador de etileno, como supuesto de vida útil.
- Pila: python-telegram-bot, Claude Haiku, SQLite, osmnx, OR-Tools, Streamlit. Simulación con tres políticas y 30 semillas.
- Vertical 04: es la que Samuel inscribió (por confirmar) y su entregable coincide con el nombre del equipo.
- Telegram para la demo: se despliega en una hora. WhatsApp queda para el piloto.
- OR-Tools sobre OpenStreetMap como motor mientras no haya acceso confirmado al software de ruteo UNAL.
- La decisión de despacho es humana siempre.

## Bloqueos y preguntas
- ¿Existen de verdad el software de ruteo UNAL, ERIS-UNAL y los datos de la ficha 04? Varias entradas del sitio parecen de plantilla.
- Duración del pitch y mecanismo de entrega.
- Ruta piloto: la noticia de la Sede dice 20 a 30 días y el sitio, 30 a 90.

## Observaciones de mentores
(vacío hasta la mentoría 1, viernes 7:00 p. m.)

## Roles
| Rol | Quién |
|---|---|
| A · Entrada | por asignar |
| B · Optimización y medición | por asignar (ingeniero industrial + Carlos) |
| C · Tablero | por asignar |
| D · Ficha y pitch | por asignar |
| Capitán | Carlos |

## Aporte a la rúbrica
| Criterio | Evidencia hoy | Falta |
|---|---|---|
| 1 Problema (20) | Ficha 04 | Cifras con fuente, cita de un usuario real |
| 2 Prototipo (25) | Nada | Todo |
| 3 Conocimiento (15) | Candidatas listadas | Confirmar una capacidad UNAL y usarla |
| 4 Plan (15) | Borrador 30/60/90 | Responsables, recursos |
| 5 Viabilidad y aliados (15) | Lista de padrinos | Contacto real, costos, riesgos |
| 6 Impactos (10) | Indicadores de la ficha | Línea base y meta medidas |
