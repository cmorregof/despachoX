# Relevo · Noche-2

Sábado 21 de noviembre, 00:05. Versión inicial: la final llega antes de las 6:15 a. m. Si esta sesión se corta, quien siga empieza aquí.

## Estado en una frase

Siete agentes Opus trabajan desde la medianoche, cada uno en su clon y en su rama `n2-*`, y ninguno escribe en `main`. Cada rama pasa por cuatro pasos antes de darse por terminada: el trabajo, una revisión independiente, el arreglo de lo que encuentre la revisión y un cierre que verifica el push.

## Ramas

| Rama | Entrega | Criterios | Plazo interno |
|---|---|---|---|
| `n2-eval-lector` | `evaluacion/lector/`: generador, 330 mensajes, evaluación campo por campo y `RESULTADOS.md` | 2 y 3 | 3:45 |
| `n2-eval-inyeccion` | `evaluacion/inyeccion/`: 40 mensajes maliciosos, pruebas y `HALLAZGOS.md` | 2 y 5 | 3:45 |
| `n2-sensibilidad` | `analisis/sensibilidad/` y `docs/SENSIBILIDAD.md` | 2, 3 y 6 | corridas 4:30, documento 5:00 |
| `n2-figuras` | `figuras_pitch/`: cinco figuras en PNG y SVG a 1920 × 1080, con README | 1 y 6 | 3:45 |
| `n2-privacidad` | `docs/PRIVACIDAD.md`, borrador para revisión de un abogado | 5 | 3:30 |
| `n2-aliados` | `aliados/DIRECTORIO.md` para la llamada de las 8:00 a. m. | 5 | 3:30 |
| `n2-jurado` | `revision/JURADO.md` con tres jurados y cinco correcciones | todos | 2:30 |

Los plazos internos dejan una hora para revisar y arreglar antes de las 6:10, cuando Fable empieza a revisar. Noche-2 no fusiona nada.

## Decisiones tomadas

1. No hay `ANTHROPIC_API_KEY` en el entorno. Por eso el lector y la inyección se miden solo por reglas, y los scripts quedan listos para medir el extractor con los topes de 330 y 60 llamadas.
2. La inyección prueba además un «modelo comprometido»: reemplaza la extracción por la peor salida que permite el esquema y verifica que ningún plan, despacho o entrega cambia sin el despachador. Así se prueba la regla de arquitectura sin gastar llamadas.
3. La sensibilidad corre una fila de referencia (velocidad medida, demanda y flota completas, factor 3) con las mismas semillas que las variantes. Sin ella no hay comparación pareada, y va rotulada como «no es el resultado principal».
4. La CLI de la simulación no expone velocidades medidas ni multiplicadores. El agente los aplica desde un envoltorio en `analisis/sensibilidad/`, leyendo `datos_publicos/velocidades.csv`, sin editar `despacho/`. Su versión de las velocidades medidas puede no coincidir con la de la simulación principal, y el documento lo dirá.
5. Las figuras usan PT Serif (licencia OFL), como pediste. Ancízar Serif sí está instalada en este Mac (`~/Library/Fonts`), y los scripts aceptan `--fuente` para usarla; ningún archivo de fuente entra al repositorio.
6. El Python del proyecto no trae matplotlib. Las figuras usan un entorno aparte en la carpeta temporal de esta sesión, así que el `.venv` del equipo no cambió.
7. Las notas de avance de cada agente viven fuera del repositorio, en la carpeta temporal de esta sesión, para no ensuciar las ramas.
8. La vigilancia de `pitch-noche` y `defensa-noche` cada 20 minutos la hace Noche-2. Cuando aparezcan, relanza la revisión del jurado sobre ellas, y a las 4:40 corre una última ronda.
9. El Mac de Carlos queda despierto hasta las 6:45 con `caffeinate`, además del permiso de la app, que se suelta si la sesión queda quieta cinco minutos.

## Si Noche-2 se corta

- Lo empujado está en GitHub: `git ls-remote --heads origin 'n2-*'` y `git log origin/main..origin/<rama>`.
- En el Mac de Carlos, los clones están en la carpeta temporal de la sesión (`.../scratchpad/clones/<rama>`), con las notas de cada agente en `.../scratchpad/estado/<rama>.md` y los borradores de LISTO en `.../scratchpad/listo/`.
- Una rama sin entrada LISTO en el canal no pasó todavía por la revisión: Fable debe revisarla antes de fusionar.
