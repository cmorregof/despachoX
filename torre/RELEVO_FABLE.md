# Relevo · coordinación del proyecto (Fable)

Sábado 21 de noviembre, 6:25 a. m. Reemplaza al relevo de las 23:38. Si este chat se corta, el siguiente empieza aquí.

## Estado en una frase

`main` (c4ce320) tiene el tablero Convite de Jacobo, la clave del tablero y los documentos y evaluaciones de la noche, y pasan 467 pruebas. A las 6:10 Carlos decidió: de las ramas de código solo entra `jacobo-tablero`; el tablero lleva clave; Samuel arregla H6 antes de las 8:30; el piloto va en el territorio P2 (Ciudadela del Norte y El Manantial).

## Traspaso de las 6:30

Carlos abre un chat nuevo de Claude Code con el modelo Fable como orquestador principal, desde las 6:30 hasta el pitch. Desde ese momento, las fusiones a `main` y la coordinación son de ese chat. Esta sesión (Opus) sigue viva solo para terminar sus dos agentes y empujar sus ramas, `simulacion` y `territorio-p2`, con un aviso en el canal. No fusiona nada más.

## Corriendo

- Simulación. A la 1 a. m. se detuvo el servidor de la sesión. La corrida principal ya había terminado (factor 3, velocidades de la tesis, 30 semillas por carga, rama `simulacion`). A las 6:03 se relanzó la corrida con velocidades del modelo en la misma red, que termina hacia las 7:25 (`/tmp/simnoche/cadena.log`). Su agente escribe la §9 de `docs/SIMULACION.md` en la rama `simulacion`.
- Territorio. Un agente pasa a P2 el guion, las diapositivas, las cifras, el plan, los riesgos, las preguntas y el mapa, en la rama `territorio-p2`, antes de las 7:30.

## Siguiente

1. Revisar y fusionar `simulacion` y `territorio-p2`.
2. Llenar los [SIM] del guion, las diapositivas, `pitch/CIFRAS_PITCH.md` y la defensa (plan §5 y §7, R6, R14, preguntas 11, 15, 29 y 30) con `despacho/sim/resultados_velocidades/tablas.md`. Para las velocidades: «derivadas de mediciones GPS de un bus en Manizales y asignadas por tipo de vía y pendiente (tesis UNAL de 2019, tabla 14, pp. 46 a 48)».
3. Armar la presentación para la mentoría de las 10:30 con `pitch/DIAPOSITIVAS.md` y `figuras_pitch/`.
4. Erratas: Carlos aprueba `docs/ERRATAS.md` fila por fila. El informe corto se recompila en su computador, porque la fuente Ancízar no está en el repositorio.
5. Antes de la demo de las 2:00 p. m.: Carlos define `DESPACHOX_CLAVE_TABLERO` en Railway; la base se reinicia con el botón del tablero después de las 10:13, cuando vencen los límites de la semilla.

## Decisiones pendientes de Carlos

- La duración y la hora del pitch (la página dice 2:00 y la plataforma 2:30).
- Quién habla, y el nombre del integrante de Ingeniería Industrial.
- El nombre Convite.
- El tamaño de familia: 1,8, 2,9 o 4.
- Si reconsidera `a25`, `qa-noche` o `demo-noche` antes de las 8:30. Sin `qa-noche`, ENTREGADO por Telegram con el modelo activo no se registra.
- El manuscrito sigue en su rama (`manuscrito`), sin fusionar, porque el repositorio es público.

## Dónde está el detalle

- Revisión de cada rama de la noche: `torre/REVISION_NOCHE.md`.
- Noche-2: `torre/RELEVO_NOCHE2.md`.
- Directorio de aliados en PDF: se le envió a Carlos para la llamada de las 8:00 (`aliados/DIRECTORIO.md`).

## Cómo se trabaja

- Fable sube a `main` solo documentos de coordinación; el código se fusiona con el sí de Carlos.
- Las fuentes Ancízar no se suben al repositorio público.
- Toda cifra del pitch, con fuente abierta por una persona.
- Congelamiento: 8:30 a. m. Mentoría 2: 10:30 a. m. Entrega en iNNOVO: 1:00 a 2:30 p. m. Pitch: 2:00 p. m.
