# Relevo · coordinación del proyecto (Fable, segundo chat)

Viernes 20 de noviembre, 18:08. Reemplaza al relevo de las 4:50 p. m., cuya tarea (lanzar e integrar los agentes de datos, patentes y capacidades) quedó hecha. Si este chat se corta, el siguiente empieza aquí.

## Estado en una frase

Terminaron los once agentes. Datos públicos e investigaciones 07 a 11 están en `main` (fusión del PR 4) y los cierres viales históricos en la rama `datos`. El informe de contexto está en `main` en versión larga y corta. Lo que se decide a las 9:00 p. m. está en `docs/DECISIONES_9PM.md`.

## Leer primero

`docs/MENTORIA_1.md`, `docs/DECISIONES_9PM.md`, `torre/CANAL.md` desde las 17:18, `docs/informe/informe_corto.pdf`, `docs/investigacion/10_problema_usuarios_alternativas.md` y `11_voz_publica_actores.md`.

## Actualización de las 22:16

- Samuel subió A2 (etapas 1 a 3), A3 (lector de SMS por reglas y pasarela local), alertas de silencio y `docs/PILOTO.md`. Jacobo subió el módulo `triage/`. Carlos fusionó todo en `main`: 306 pruebas en verde.
- La ficha la escribe un agente de Fable y llega a la rama `ficha` antes de las 12:30 a. m. Hay que revisarla antes de la mentoría 2 (sábado, 10:30 a. m.).
- Encargo de la noche para Samuel y Jacobo: `encargos/P2_NOCHE_SAMUEL_JACOBO.md`.

## Pendiente

1. 9:00 p. m.: reunión de Carlos, Samuel y Jacobo con la propuesta del encargo P1 (`docs/PROPUESTA_P1.md`). Se decide el usuario del piloto, los cambios antes del congelamiento y el orden del pitch.
2. Ficha: la rama `ficha` del agente de las 4:25 p. m. no llegó. Si no aparece, Fable escribe `docs/FICHA.md` con las decisiones, para la fusión de las 11:00 p. m. Corregir las cifras dudosas: el cierre es Pereira–Chinchiná, km 22 a 24; Manizales fue «uno de los principales» acopios de ABACO; no usar «ABACO registra vencimientos»; el +28,6 es con factor 3 y está en revisión por las velocidades.
3. `pitch/GUION.md`: reordenar según la decisión 4.
4. `docs/FUENTES.md`: las diez cifras candidatas de `DECISIONES_9PM.md`, abiertas por una persona.
5. Informe de contexto: escribir la sección del piloto cuando se decida.
6. Simulación: esperar la corrida con velocidades medidas (aviso de las 17:31).
7. B-despacho: factor 3 aprobado; empaque 1,2 solo para fruta en frío, propuesto; parte B de T1.
8. Jacobo: parte C de T1 y la regla numérica del resumen hecho con Opus.

## Cómo se trabaja

- Fable sube a `main` solo documentos de coordinación; los datos van a la rama `datos`; Carlos fusiona.
- Las fuentes Ancízar del informe corto no se suben al repositorio público (`docs/informe/fuentes/` está ignorado). Están en la carpeta Proyecto Godel de Carlos.
- Toda cifra del pitch, con fuente abierta por una persona.
