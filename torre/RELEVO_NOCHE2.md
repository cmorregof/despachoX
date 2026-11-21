# Relevo · Noche-2

Sábado 21 de noviembre, versión final de las 5:21 a. m. Reemplaza las de las 00:05 y las 2:40. Noche-2 termina aquí. Las ramas quedan para que Fable las revise desde las 6:10, y Carlos decide lo suyo a las 6:30.

## Estado en una frase

Las siete ramas `n2-*` están cerradas y empujadas. Cada una pasó por una revisión independiente, el arreglo de lo que encontró y un cierre que verificó el push, y tiene su LISTO en `torre/CANAL.md`. A las 4:40 el jurado hizo una ronda final que ordena las fusiones por puntos esperados. Noche-2 no fusionó nada.

## Ramas

| Rama | Entrega | Criterios | Último commit | Probar |
|---|---|---|---|---|
| `n2-aliados` | `aliados/DIRECTORIO.md`: ocho fichas para las llamadas de las 8:00 a. m., con canales institucionales, URL y fecha | 5 | `1bc08ac` | `git show origin/n2-aliados:aliados/DIRECTORIO.md` |
| `n2-privacidad` | `docs/PRIVACIDAD.md`: borrador para revisión de un abogado, con respuesta de 85 palabras para el jurado | 5 | `9a87606` | `python -m pytest entrada/pruebas/test_privacidad.py` |
| `n2-eval-lector` | `evaluacion/lector/`: 330 mensajes, evaluación campo por campo, 24 pruebas y `RESULTADOS.md` | 2 y 3 | `473444d` | `DESPACHOX_SIN_RED=1 PYTHONPATH=. python -m evaluacion.lector.evaluar` |
| `n2-eval-inyeccion` | `evaluacion/inyeccion/`: 40 mensajes maliciosos, 69 pruebas, 26 xfail estrictos y `HALLAZGOS.md` | 2 y 5 | `193a68a` | `DESPACHOX_SIN_RED=1 python -m pytest evaluacion/inyeccion -q` |
| `n2-figuras` | `figuras_pitch/`: seis figuras de 1920 × 1080 en PNG y SVG, con scripts, datos y README | 1 y 2 | `ff8cf7b` | `figuras_pitch/scripts/todas.py` con un Python que tenga matplotlib |
| `n2-sensibilidad` | `docs/SENSIBILIDAD.md` y `analisis/sensibilidad/`: nueve variantes con 60 semillas y cuatro políticas | 2, 3 y 6 | `30fab28` | `DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.tabla --semillas 60` |
| `n2-jurado` | `revision/JURADO.md`: tres jurados, cinco correcciones y la ronda de las 4:40 con los puntos de cada rama | todos | `aed8bf4` | leer el archivo |

## Orden sugerido para las fusiones

La ronda de las 4:40 de `n2-jurado` estimó cuántos puntos suma cada rama de la noche si se fusiona y se cita. Por puntos esperados por hora de trabajo, el orden es `n2-aliados`, `a25`, `n2-eval-lector`, `n2-sensibilidad`, `simulacion`, `n2-privacidad`, `n2-eval-inyeccion`, `n2-figuras` y `erratas`. Los puestos 3 a 5 casi empatan, y `simulacion` va primero de ellos porque es la corrección 6 del jurado. `a25` debe entrar después de `fuentes-noche`, porque las dos chocan en `docs/FUENTES.md`. `erratas` solo cambia `docs/GUION_DEMO.md` y se puede fusionar sin más. Las condiciones de cada rama están al principio de `revision/JURADO.md`.

Según la misma ronda, todavía no conviene citar lo siguiente:

- la ventaja sobre el despachador con oficio en críticos, porque mezcla el efecto de la red y el de las velocidades;
- la referencia de la sensibilidad como si fuera el resultado principal;
- «No guardamos teléfono ni nombre», que H6 contradice;
- «Solo el despachador aprueba», sin decir que el tablero no pide clave;
- la confirmación de entrega por chat mostrada en vivo, mientras no entre el arreglo de `qa-noche`;
- «351 t rescatadas» por el Banco, porque 48 t fueron compradas;
- los enlaces del IDEA que dan 404 y cualquier distancia a Bajo Tablazo.

## Lo que Carlos tiene que decidir

1. **La clave del tablero.** El tablero que recibe el jurado no pide clave, y el botón de reinicio de `jacobo-tablero` tampoco. Con el enlace, cualquiera podría aprobar un plan o reiniciar la base durante la demo. La pregunta es si se define `DESPACHOX_CLAVE_TABLERO` en Railway antes del pitch.
2. **El arreglo de H6 antes de las 8:30.** Cuando alguien describe su sitio con sus palabras y manda su ubicación, el bot le ofrece ese texto, con las coordenadas exactas, a cualquier desconocido (`lugares/nomenclator.py:258-259`). El arreglo propuesto está en `evaluacion/inyeccion/HALLAZGOS.md` y le toca a Samuel. Mientras no se arregle, nadie debe decirle al jurado «No guardamos teléfono ni nombre».
3. **La fusión de `a25` antes de las 8:30.** Es la capacidad UNAL del proyecto. Según `n2-jurado`, `main` con `a25` fusiona limpio, pasan las pruebas y la demo da 33 de 33 con el gancho apagado y encendido.
4. **El commit `7a290fe` de `qa-noche`.** Arregla el ENTREGADO por chat con el modelo activo. Según `n2-jurado`, se aplica sin choque sobre la fusión de las doce ramas, pero nadie lo probó con el modelo activo, porque eso exige la API.
5. **El nombre del integrante de Ingeniería Industrial**, que pide la corrección 4 del jurado.
6. **El informe corto.** Trae diez discrepancias con sus fuentes en catorce pasajes y otras fases que la ficha. Se corrige y se recompila en tu computador, o se deja fuera del Drive.
7. **`/borrar` y `BORRAR` por SMS.** Son funciones nuevas, así que después de las 8:30 ya no entran. Si no entran, hay que decir en el `/start` de la demo a quién se le pide el borrado.
8. **Datos de la nube.** En qué región corre Railway y qué servicio de voz quedó configurado, Groq u OpenAI (`entrada/voz.py:19`).
9. **La medición del extractor con modelo.** `evaluacion/lector/medir_modelo.py` necesita la clave de Anthropic y cuesta entre 0,06 y 0,15 USD según el agente. Sin ella, el pitch solo puede citar el lector por reglas.

## Lo que Fable tiene que resolver

1. Los enlaces del reporte A25 de 2020 y del Boletín Ambiental 145 del IDEA dan 404, y los citan la ficha corta, el informe, `docs/PILOTO.md` y cuatro ramas.
2. Bajo Tablazo queda a 8,4 km del Banco por la red del equipo, y `docs/PILOTO_TERRITORIOS.md`, la fila P10 de las cifras y la diapositiva 7 dicen 9,3 km. El mismo método cambia los críticos de Atardeceres a entre 4,2 y 6,9 km.
3. H4 y H6 de la inyección contradicen las secciones 2.4 y 2.7 de `docs/QA_NOCHE.md`.
4. Las frases para el pitch del lector, la inyección y la sensibilidad están «por aprobar». Si se aprueban, cada una necesita su fila de tipo M en `docs/FUENTES.md`.
5. La sección 7 de `docs/SIMULACION.md` dice que la experta le gana a DespachoX en entregas a tiempo de todos los puntos. La sensibilidad muestra que eso ya no aguanta en general, así que conviene retirarla o condicionarla.
6. Choques de fusión probados a la 1:45: `qa-noche` con `samuel-bot` en `entrada/pasarela_sms.py`, y `a25` con `samuel-bot` en `docs/FUENTES.md`.
7. `samuel-bot` reconoce atún, azúcar y café, pero lee «café» dentro de «Villa Café» y empeora 3 de 300 mensajes del lector.
8. El directorio de aliados usa un fijo del Banco que publica ABACO y no el Banco, marcado así en la tabla. Falta decidir si vale como canal.
9. Las cifras del directorio y de las figuras pueden pasar a `docs/FUENTES.md` después de que una persona abra cada enlace.
10. La corrección 6 del jurado: escribir la sección 9 de `docs/SIMULACION.md` con la corrida de `simulacion` (`f52ea33`) y llenar los [SIM] del guion con su línea base, el número de jornadas y la palabra «simulación».

## Cifras nuevas de la noche

| Cifra | Tipo | Dónde |
|---|---|---|
| En la sensibilidad, DespachoX entrega a tiempo más pedidos críticos que el orden de llegada en las nueve variantes, por 15,5 a 69,4 puntos; en la referencia, 99,3 % contra 54,7 %. Frente a la experta gana 3,2 puntos [2,1; 4,4] en la referencia y empata con factor crítico 1. No es el resultado principal | Medido por nosotros en 2.160 jornadas sintéticas | `docs/SENSIBILIDAD.md` |
| El perecedero vencido queda en 0,0 % en las 540 jornadas de DespachoX y de la experta, y la ingenua pierde entre 1,0 % y 8,2 % | Medido por nosotros en la simulación | `docs/SENSIBILIDAD.md` |
| El lector por reglas dejó sin ningún error 162 de 330 mensajes (49,1 %), encontró 619 de 642 productos (96,4 %) y no propuso con seguridad ningún lugar equivocado en 320 pedidos. El conjunto es sintético y nuestro, así que probablemente es optimista | Medido por nosotros | `evaluacion/lector/RESULTADOS.md` |
| Ninguno de 40 mensajes maliciosos aprobó un plan ni puso un paquete en ruta. Con un lector falso que devuelve la peor lectura posible, aguantaron 134 de 165 comprobaciones | Medido por nosotros | `evaluacion/inyeccion/HALLAZGOS.md` |
| En 11 mensajes sintéticos, `privacidad.limpiar` quitó celulares, cédula, correo y el nombre tras «me llamo», pero dejó pasar direcciones y nombres tras «doña» | Medido por nosotros | `docs/PRIVACIDAD.md` |
| En 2025 el Banco recibió 351 t, entregó 364 t y atendió 156 organizaciones | Tomado de una fuente: su informe de gestión 2025 | `aliados/DIRECTORIO.md` |
| De lo recibido, 48 t fueron compradas, así que lo rescatado ronda las 303 t | Estimado: cálculo nuestro sobre esa tabla | `aliados/DIRECTORIO.md` |
| 152 registros de derrumbe o deslizamiento sin sismo entre 2017 y 2026, con 83 en la salida a Letras (87 con los 4 del sismo) | Medido por nosotros sobre `datos_publicos/cierres_historicos.csv` | `figuras_pitch/README.md` |
| La demo de `demo-noche` sobre `main` dio 33 de 33 verificaciones, con planes de 3,2 a 3,4 s | Medido por nosotros a la 1:19 a. m. | `revision/JURADO.md` |
| La fusión de doce ramas sobre `main` (`5571ab2`) da 465 pruebas en verde, las mismas 11 fallidas de `entrada/` por `DESPACHOX_SIN_RED`, 1 omitida y 26 xfail, en 61,9 s. Sobre esa fusión, la demo pasa 33 de 33 con el A25 apagado y encendido | Medido por nosotros en la ronda de las 4:40 | `revision/JURADO.md` |
| Con las cinco correcciones y todo fusionado y citado, la nota de los tres jurados queda en 75, 65 y 72,5 puntos, frente a 65, 62,5 y 65 hoy. Sube a 87,5, 76,25 y 77,5 si responden el Banco y el IDEA | Estimado | `revision/JURADO.md` |

## Decisiones tomadas

1. No hay `ANTHROPIC_API_KEY` en el entorno. Por eso el lector y la inyección se midieron solo por reglas, y los scripts quedaron listos para medir el extractor con los topes de 330 y 60 llamadas.
2. La inyección probó además un lector falso que devuelve la peor salida que permite el esquema. Así se prueba la regla de arquitectura sin gastar llamadas.
3. La sensibilidad corrió una fila de referencia con las mismas semillas que las variantes, rotulada como «no es el resultado principal». Usa 60 semillas desde 20261150 en la red ampliada, con cierres de 3 a 8, a diferencia de la corrida «sin cierres» de la otra sesión.
4. La simulación no deja variar velocidad ni demanda desde la línea de comandos. El agente aplicó la velocidad medida desde `datos_publicos/velocidades.csv` y los multiplicadores desde un envoltorio en su carpeta, sin editar `despacho/`. La flota pierde camperos y conserva al menos uno.
5. Las figuras usan PT Serif, que es libre. Ancízar Serif sí está instalada en este Mac (`~/Library/Fonts`), y `--fuente` la usa; ningún archivo de fuente entró al repositorio.
6. El Python del proyecto no trae matplotlib. Las figuras se hicieron con un entorno aparte, así que el `.venv` del equipo no cambió.
7. El jurado corrió la suite con `DESPACHOX_SIN_RED=1`, y con esa variable fallan 11 pruebas de `entrada/pruebas` porque el flujo lee por reglas en vez del extractor falso. Sin la variable pasan. El encargo lo pidió así, y `JURADO.md` y `HALLAZGOS.md` lo explican.
8. La segunda revisión dejó dos problemas mayores sin arreglar, y Noche-2 los arregló a las 3:30: la frase del pitch de la inyección ahora dice que las entregas sí se registran al instante con el código del paquete (H1 y H2), y la tabla del jurado suma el pasaje de la línea 185 del informe corto.
9. El Mac de Carlos queda despierto hasta las 6:45 con `caffeinate`, además del permiso de la app.

## Notas de la revisión

- Mientras buscaba canales, el agente de aliados descargó un directorio interno de la Alcaldía en la carpeta temporal de la sesión. El agente que corrigió la rama lo borró a la 1:11 a. m., y nunca entró al repositorio.
- En el AVISO de las 3:32 escribí que corregí la frase de la sensibilidad para que no compare con la experta. No es así: su agente ya la había escrito de ese modo. Lo que corregí fue la de la inyección.
- Ningún agente cayó por cupo. Trabajaron 38 agentes sin errores: 34 en las siete ramas y 4 en la ronda final del jurado.

## Qué queda en este Mac

Los clones de los agentes están en la carpeta temporal de la sesión (`.../scratchpad/clones/<rama>`), con las notas de cada agente en `.../scratchpad/estado/<rama>.md` y los borradores de LISTO en `.../scratchpad/listo/`. Todo lo que importa está empujado a GitHub, así que esa carpeta se puede perder sin daño.
