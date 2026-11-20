# DespachoX

Equipo 19 · Hackathon UNAL Manizales 2026 · Vertical 04, Logística y abastecimiento.

Mesa de despacho de ayuda alimentaria después del sismo: los barrios piden por chat, los conductores reportan vías bloqueadas, un optimizador calcula rutas para una flota mixta y prioriza lo que vence primero, y un despachador humano aprueba cada plan.

**El modelo lee y estructura. El optimizador y las reglas calculan. El despachador decide.**

## Equipo

Samuel Rosso (líder) · Carlos Orrego · Nicolás Ramírez · Jacobo Vasco · José Manuel Aristizábal

## Por dónde empezar

**Hoy, antes de las 2:30 p. m.: `docs/TAREA_0.md`.**

1. Lee `docs/ESTRATEGIA.md`: qué pide la hackathon, la rúbrica, qué construimos y el horario.
2. Abre Claude en esta carpeta. `CLAUDE.md` ya trae las instrucciones del equipo. Si usas el chat web, copia `docs/PROMPT_EQUIPO.md` en las instrucciones de tu proyecto.
3. Copia `torre/PLANTILLA_TORRE.md` a `torre/TORRE_<tu-nombre>.md` y mantenla al día.
4. Haz commit y push al cerrar cada etapa: `[rol] qué cambió`.

## Mapa

| Carpeta | Qué hay | Rol |
|---|---|---|
| `docs/` | Estrategia, ficha de los seis componentes, fuentes, estado del arte | D y capitán |
| `torre/` | Torres de control: una del capitán y una por integrante | todos |
| `entrada/` | Bot de chat, voz, extracción de pedidos y cierres viales | A |
| `despacho/` | Optimizador de rutas, simulación, datos de prueba | B |
| `tablero/` | Mapa, cola de pedidos, trazabilidad | C |
| `pitch/` | Diapositivas, guion, video | D |

## Reglas

- Ninguna clave en el repositorio: van en `.env` (ver `.env.example`).
- Ningún dato personal real. Los pedidos de prueba son sintéticos.
- Toda cifra lleva su fuente en `docs/FUENTES.md`.
- El sábado a las 8:30 a. m. se congelan las funciones.
