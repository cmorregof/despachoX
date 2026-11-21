# Relevo · Noche-2

Sábado 21 de noviembre, 2:40 a. m. Esta versión reemplaza la de las 00:05, y la final llega antes de las 6:15 a. m. Si esta sesión se corta, quien siga empieza aquí.

## Estado en una frase

Seis de las siete ramas `n2-*` cerraron con revisión independiente, arreglo y LISTO en el canal. La sensibilidad terminó sus corridas de 60 semillas y escribe su documento, y a las 4:40 corre la última ronda del jurado. Noche-2 no fusiona nada: Fable decide desde las 6:10.

## Ramas

| Rama | Entrega | Criterios | Estado |
|---|---|---|---|
| `n2-aliados` | `aliados/DIRECTORIO.md`: ocho fichas para las llamadas de las 8:00 a. m. | 5 | Cerrada, LISTO 1:24 |
| `n2-privacidad` | `docs/PRIVACIDAD.md`, borrador para revisión de un abogado | 5 | Cerrada, LISTO 1:41 |
| `n2-eval-lector` | `evaluacion/lector/`: 330 mensajes, evaluación campo por campo y 24 pruebas | 2 y 3 | Cerrada, LISTO 1:54 |
| `n2-jurado` | `revision/JURADO.md`: tres jurados y cinco correcciones | todos | Cerrada, LISTO 2:08; última ronda a las 4:40 |
| `n2-figuras` | `figuras_pitch/`: seis figuras de 1920 × 1080 en PNG y SVG | 1 y 2 | Cerrada, LISTO 2:15 |
| `n2-eval-inyeccion` | `evaluacion/inyeccion/`: 40 mensajes maliciosos, 69 pruebas y 26 xfail estrictos | 2 y 5 | Cerrada, LISTO 2:26 |
| `n2-sensibilidad` | `analisis/sensibilidad/` y `docs/SENSIBILIDAD.md` | 2, 3 y 6 | Corridas listas; falta el documento y su revisión |

## Lo que Carlos tiene que decidir

1. **La clave del tablero.** El tablero que recibe el jurado no pide clave, y el botón de reinicio de `jacobo-tablero` tampoco. Lo encontraron `n2-jurado` y la revisión de calidad de Fable. La pregunta es si se define `DESPACHOX_CLAVE_TABLERO` en Railway antes del pitch.
2. **El arreglo de H6 antes de las 8:30.** Cuando alguien describe su sitio con sus palabras y manda su ubicación, el bot le ofrece ese texto, con las coordenadas exactas, a cualquier desconocido (`lugares/nomenclator.py:258-259`). El arreglo propuesto está en `evaluacion/inyeccion/HALLAZGOS.md` y le toca a Samuel. Mientras no se arregle, nadie debe decirle al jurado «No guardamos teléfono ni nombre».

## Lo que Fable tiene que resolver

1. Los enlaces del reporte A25 de 2020 y del Boletín Ambiental 145 del IDEA dan 404, y los citan la ficha corta, el informe, `docs/PILOTO.md` y cuatro ramas.
2. Bajo Tablazo queda a 8,4 km del Banco por la red del equipo, y `docs/PILOTO_TERRITORIOS.md`, la fila P10 de las cifras y la diapositiva 7 dicen 9,3 km.
3. H4 y H6 de la inyección contradicen las secciones 2.4 y 2.7 de `docs/QA_NOCHE.md`.
4. Las frases para el pitch del lector, la inyección y la sensibilidad están marcadas «por aprobar».

## Cifras nuevas de la noche

| Cifra | Tipo | Dónde |
|---|---|---|
| El lector por reglas dejó sin ningún error 162 de 330 mensajes (49,1 %), encontró 619 de 642 productos (96,4 %) y no propuso con seguridad ningún lugar equivocado en 320 pedidos. El conjunto es sintético y nuestro, así que probablemente es optimista | Medido por nosotros | `evaluacion/lector/RESULTADOS.md` |
| Ninguno de 40 mensajes maliciosos aprobó un plan ni puso un paquete en ruta. Con un lector falso que devuelve la peor lectura posible, aguantaron 134 de 165 comprobaciones | Medido por nosotros | `evaluacion/inyeccion/HALLAZGOS.md` |
| En 11 mensajes sintéticos, `privacidad.limpiar` quitó celulares, cédula, correo y el nombre tras «me llamo», pero dejó pasar direcciones y nombres tras «doña» | Medido por nosotros | `docs/PRIVACIDAD.md` |
| En 2025 el Banco recibió 351 t, entregó 364 t y atendió 156 organizaciones | Tomado de una fuente (su informe de gestión 2025) | `aliados/DIRECTORIO.md` |
| De lo recibido, 48 t fueron compradas, así que lo rescatado ronda las 303 t | Estimado (cálculo nuestro sobre esa tabla) | `aliados/DIRECTORIO.md` |
| 152 registros de derrumbe o deslizamiento sin sismo entre 2017 y 2026, con 83 en la salida a Letras (87 con los 4 del sismo) | Medido por nosotros sobre `datos_publicos/cierres_historicos.csv` | `figuras_pitch/README.md` |
| La demo de `demo-noche` sobre `main` dio 33 de 33 verificaciones, con planes de 3,2 a 3,4 s | Medido por nosotros a la 1:19 a. m. | `revision/JURADO.md` |
| Calificación de los tres jurados: 65, 62,5 y 65 puntos hoy; 81,25, 71,25 y 77,5 con las cinco correcciones | Estimado | `revision/JURADO.md` |

## Decisiones tomadas

1. No hay `ANTHROPIC_API_KEY` en el entorno. Por eso el lector y la inyección se midieron solo por reglas, y los scripts quedaron listos para medir el extractor con los topes de 330 y 60 llamadas.
2. La inyección probó además un lector falso que devuelve la peor salida que permite el esquema. Así se prueba la regla de arquitectura sin gastar llamadas.
3. La sensibilidad corre una fila de referencia con las mismas semillas que las variantes, rotulada como «no es el resultado principal». Usa 60 semillas desde 20261150, con cierres de 3 a 8, a diferencia de la corrida «sin cierres» de la otra sesión.
4. La simulación no deja variar velocidad ni demanda desde la línea de comandos. El agente aplica la velocidad medida desde `datos_publicos/velocidades.csv` y los multiplicadores desde un envoltorio en su carpeta, sin editar `despacho/`. La flota pierde camperos y conserva al menos uno.
5. Las figuras usan PT Serif, que es libre. Ancízar Serif sí está instalada en este Mac (`~/Library/Fonts`), y `--fuente` la usa; ningún archivo de fuente entró al repositorio.
6. El Python del proyecto no trae matplotlib. Las figuras se hicieron con un entorno aparte, así que el `.venv` del equipo no cambió.
7. El directorio de aliados usa un fijo del Banco que publica ABACO y no el Banco, y lo dice en la tabla. Es la única excepción a la regla de canales publicados por la propia entidad.
8. El jurado corrió la suite con `DESPACHOX_SIN_RED=1`, y con esa variable fallan 11 pruebas de `entrada/pruebas`, porque el flujo lee por reglas en vez del extractor falso. Sin la variable pasan. El encargo lo pidió así, y tanto `JURADO.md` como `HALLAZGOS.md` lo explican.
9. El Mac de Carlos queda despierto hasta las 6:45 con `caffeinate`, además del permiso de la app.

## Si Noche-2 se corta

- Lo empujado está en GitHub: `git ls-remote --heads origin 'n2-*'` y `git log origin/main..origin/<rama>`.
- En el Mac de Carlos, los clones están en la carpeta temporal de la sesión (`.../scratchpad/clones/<rama>`), con las notas de cada agente en `.../scratchpad/estado/<rama>.md` y los borradores de LISTO en `.../scratchpad/listo/`.
- Una rama sin entrada LISTO en el canal no pasó todavía por la revisión, y Fable debe revisarla antes de fusionar. A las 2:40 esa rama es `n2-sensibilidad`.
