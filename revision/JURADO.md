# Revisión como jurado · DespachoX

**Documento interno. No se fusiona a `main` antes del pitch.** El repositorio es público (`docs/QA_NOCHE.md`, rama `qa-noche`, sección 2.1) y el jurado recibe su enlace (`ENTREGA.md`, rama `fuentes-noche`, fila 5). Este archivo trae la nota que se pone el propio equipo, así que se queda en la rama `n2-jurado`.

La escribió el agente `n2-jurado` de Noche-2 el sábado 21 de noviembre de 2026, hora de Colombia. La primera versión va de las 12:03 a las 12:37 a. m. (commit `c726bea`). Esta segunda versión, escrita entre la 1:01 y la 1:40 a. m., corrige lo que encontró una revisión independiente y vuelve a cotejar cada frase citada con las ramas de la 1:36 a. m. Tres jurados que no vieron el trabajo lo califican con la rúbrica de `CLAUDE.md` y la escala de `docs/ESTRATEGIA.md` (excelente 100 %, sólido 75 %, parcial 50 %, incipiente 25 %, no evidenciado 0 %). Las calificaciones y los puntos que gana cada corrección son juicio mío, así que van como estimados [E]. Los conteos de pruebas, la demo por terminal y la cobertura del A25 los medí sobre copias de las ramas [M].

## Resumen

Si se entregara ahora, el trabajo sacaría entre 62,5 y 65 puntos de 100 con estos tres jurados [E]. El prototipo es lo más fuerte, porque corre de punta a punta y la simulación está bien diseñada. Lo más débil son los aliados, que nadie ha confirmado, y el A25, que la ficha llama capacidad principal y que en `main` solo se nombra. Las cifras del problema tienen fuente, pero ninguna la ha abierto una persona. Si siguen así a la 1:00 p. m., la regla del guion las saca del pitch, y la nota baja a entre 57,5 y 60.

Por puntos ganados por hora de trabajo, conviene este orden.

1. Anotar en la ficha y en el guion lo que respondió el Banco a las 8:00 a. m.
2. Abrir por persona las siete cifras con asterisco de la versión de tres minutos y marcarlas en `docs/FUENTES.md`.
3. Fusionar la rama `a25` antes de las 8:30 a. m. y decir dónde está el A25 en el código, a qué vías toca y a cuáles no llega.
4. Poner nombre al integrante de Ingeniería Industrial y dejar un solo reparto de responsables.
5. Subir al Drive el plan de 30 a 90 días y la matriz de riesgos, y enlazarlos en el README.

Con las cinco y una respuesta del Banco que se pueda citar, el rango sube a entre 71,25 y 81,25 puntos [E]. Sin esa respuesta queda entre 62,5 y 72,5, porque la directora del banco no se mueve con cambios de texto. Las dos cuentas suponen que antes de registrar se corrigen las frases del informe corto y de la ficha que no coinciden con su fuente, como ya pide `ENTREGA.md`. El video de respaldo no está entre las cinco porque ya tiene lugar en la agenda. Aun así, si la demo en vivo falla y no hay video, el prototipo baja un nivel con los tres jurados (sección 7).

## Versiones revisadas

| Rama | Commit | Qué revisé |
|---|---|---|
| `main` | `7131261` en mi clon. `origin/main` está en `870d540`, que solo añade entradas a `torre/`, así que los archivos revisados son los mismos | `docs/FICHA_CORTA.md`, `docs/FICHA.md`, `docs/informe/informe_corto.tex` y su PDF, `docs/FUENTES.md`, `docs/SIMULACION.md`, `docs/ESTRATEGIA.md`, `docs/DECISIONES_9PM.md`, `docs/MENTORIA_1.md`, `docs/PILOTO_TERRITORIOS.md`, `docs/GUION_DEMO.md`, `README.md`, los encargos P2, P3 y P5, y el código |
| `pitch-noche` | `d337e06` (lecturas anteriores en `31a618b` y `6782e4c`) | `pitch/GUION.md`, `pitch/DIAPOSITIVAS.md` y `pitch/CIFRAS_PITCH.md` |
| `defensa-noche` | `5737e09` (lectura anterior en `9b85a37`) | `docs/PLAN_30_90.md`, `docs/RIESGOS.md` y `pitch/PREGUNTAS_JURADO.md` |
| `fuentes-noche` | `2261013` (lectura anterior en `f235cb2`) | `docs/FUENTES.md` (registro consolidado), `ENTREGA.md` y la sección «Para el jurado» de `README.md` |
| `a25` | `b96ff71` (lectura anterior en `c5454ba`) | `despacho/a25.py`, sus pruebas, su línea de órdenes y `docs/A25.md` |
| `demo-noche` | `d24cd2d` | `demo/correr.py`, para ensayar la demo por terminal, y `demo/CHECKLIST.md` |
| `erratas` | `4f5df00` | Solo `docs/GUION_DEMO.md` |
| `jacobo-tablero` | `65b3581` | Solo el botón «Reiniciar datos de prueba» de `tablero/app.py` |
| `simulacion` | `f52ea33` | Solo si llegó la corrida con las velocidades de la tesis de 2019. No revisé sus cifras |

Las ramas `pitch-noche` y `defensa-noche` ya existían a las 12:05 a. m., así que esta revisión las incluye desde su primera versión. Después de esa versión, Fable corrigió en ellas varias frases con discrepancia de `docs/FUENTES.md`. Por ejemplo, la pregunta 1 ya no dice «en todo el país» (D3), y el guion nombra los kilos en tránsito. Entre la 1:05 y la 1:36 a. m. volví a cotejar con las puntas de la tabla cada frase citada. Cada rama de la tabla se fusiona sin conflictos con `origin/main` (`870d540`), según `git merge-tree` [M].

## 1. Lo que comprobé, como lo haría un jurado escéptico

El prototipo corre y los datos son los que dice la ficha. Lo que falla está en los documentos. Prometen cosas que no existen, y todavía no tienen un aliado que citar. La sección 11 dice cómo repetir cada medición.

| Pregunta | Lo que encontré |
|---|---|
| ¿Corren las pruebas? | Sí, con una salvedad. Con `DESPACHOX_SIN_RED=1`, `python -m pytest -q` da 334 pruebas en verde, 11 fallidas y 1 omitida, de 346, en 44,8 s [M]. Las 11 fallidas están en `entrada/pruebas/`, con 8 en `test_flujo.py`, 2 en `test_escala.py` y 1 en `test_enea.py`. Fallan porque, con esa variable, `Mesa.leer` usa el lector de SMS y salta el extractor falso que inyectan esas pruebas (`entrada/flujo.py`, línea 100). El equipo reporta 345 en verde a las 23:50 (`torre/CANAL.md`), y la cuenta cuadra con 346 menos la omitida. No corrí la suite sin la variable, porque la regla de esta noche lo prohíbe |
| ¿La demo sale como dice el guion? | Sí, con el lector por reglas. `demo/correr.py`, de `demo-noche`, pasa 33 de 33 verificaciones sobre el código de `main`, a las 12:10 y a la 1:19 a. m. [M]. Da 18 de 18 pedidos y 3 de 3 críticos a tiempo, y el pedido de San José pasa a un campero después del cierre. Cada plan tarda entre 3,1 y 3,4 s con 3 s de búsqueda. La lectura con el modelo no se probó, porque no hay clave en el entorno |
| ¿Funciona en la nube? | No lo comprobé, porque la regla de esta noche prohíbe llamar a Railway y a Telegram |
| ¿Las cifras tienen fuente? | Tienen fuente, pero nadie la ha abierto. En `main`, `docs/FUENTES.md` tiene 3 filas. En `fuentes-noche` hay un registro consolidado de 17 secciones temáticas. Ninguna cifra está verificada por una persona. El registro anota 25 discrepancias entre nuestros textos y sus fuentes, de D1 a D25. Seis caen en la ficha corta y diez en el informe corto (`ENTREGA.md`, filas 1 y 3) |
| ¿El A25 está en el código? | En `main`, no, porque ningún archivo de código lo usa. En la rama `a25` sí. `despacho/a25.py` le asigna a cada tramo la estación más cercana. Con `DESPACHOX_A25=1`, el optimizador encarece, sin cerrarlas, las vías con historial de deslizamientos que están en naranja (×2) o roja (×4). Las demás vías en alerta solo avisan. Con la lluvia sintética, por ejemplo, la avenida Paralela queda en roja y no se encarece, porque no tiene cierres por ladera en el historial [M]. Con la rama fusionada sobre `main` pasan 118 pruebas de `despacho/`, frente a 86 en `main` sola. La suite completa da 366 en verde, las mismas 11 fallidas de `entrada/` y 1 omitida. La demo pasa 33 de 33 con el gancho apagado y encendido [M] |
| ¿Dónde no sirve el A25? | La línea de órdenes de la rama, con lluvia sintética, deja «fuera de la red» los tramos a más de 3 km de toda estación [M]. Ahí caen las vías con más cierres por ladera según el propio módulo. Son la salida a Letras (87 registros, La Nubia a 10,11 km), la vía a Medellín (35, CHEC-Uribe a 3,31 km), la autopista del Café (6), la vía a Neira (5) y La Siria (3). El límite viene de la distancia a las estaciones, así que no cambia con la lluvia real. `docs/A25.md`, en la rama, ya lo documenta y pide estaciones del SIMAC cerca de esas salidas. La ficha y las diapositivas no lo dicen |
| ¿Las otras capacidades UNAL están en el código? | La patente 37476 sí, como factor de 1,2 solo para fruta en un acopio con frío (`despacho/optimizar.py`, línea 54, y `despacho/semilla.py`). Los 22,6 km/h de la tesis de 2019 no entran al optimizador, porque `despacho/red.py` usa velocidades supuestas. La simulación de la rama `simulacion` ya puede usarlos (`despacho/sim/red_sim.py`), y su corrida llegó a esa rama a las 12:41 a. m. (`f52ea33`). Todavía no está en `docs/SIMULACION.md` ni en `main` |
| ¿El plan tiene responsables y validación? | Sí. `docs/FICHA_CORTA.md` trae cuatro tramos con responsables y validación, con dos filas «por asignar». `docs/PLAN_30_90.md` (`defensa-noche`) trae cinco hitos con criterio para seguir, ajustar o parar. El integrante de Ingeniería Industrial aparece 20 veces en el plan, los riesgos y las preguntas, y nunca con su nombre |
| ¿Los documentos dicen lo mismo? | No del todo. El informe corto trae fases de 1 a 30, 31 a 60 y 61 a 90 días, y la ficha trae 0 a 15, 15 a 30, 30 a 60 y 60 a 90. La ficha pone a Samuel en el acuerdo con el Banco, pero la decisión de las 23:01 se lo dio al integrante de Ingeniería Industrial (`encargos/P3_NOMBRE_IMAGEN_BANCO.md`) |
| ¿Hay aliados? | No. La ficha dice «Ninguno ha visto todavía la propuesta» |
| ¿Los datos del escenario son los que dice la ficha? | Sí. `datos_publicos/puntos.csv` tiene 50 puntos, 35 de ellos críticos, y `datos_publicos/cierres_historicos.csv` tiene 178 registros [M] |
| ¿Se promete algo que no existe? | Sí. El informe corto promete exportar a SUMA, y eso no está en el código ni en el plan. La ficha dice «[Video de respaldo: por grabar.]» (línea 34). `docs/GUION_DEMO.md` de `main` da como respaldo el comando `entrada.procesar`, que no existe. La rama `erratas` ya lo cambia por el comando `RESPALDO` (`4f5df00`, 12:57 a. m.). El botón «Reiniciar datos de prueba» es un cuarto caso. `pitch-noche`, `fuentes-noche` y `erratas` ya reinician la nube con `DESPACHOX_REINICIAR=1`, porque en `main` no hay botón, pero `demo/CHECKLIST.md`, de `demo-noche`, todavía lo pide en su paso 4. Desde las 12:57 a. m. el botón existe en `jacobo-tablero` (`65b3581`), pendiente de fusión |

## 2. Qué califico

Califico lo que el jurado tendría a mano si se entregara ahora con el plan de `ENTREGA.md` (rama `fuentes-noche`). Eso es la ficha corta, el anexo y el informe corto en PDF, el repositorio, el tablero, el pitch de `pitch-noche` y las respuestas de `defensa-noche`. `docs/PLAN_30_90.md` y `docs/RIESGOS.md` no están en la lista de lo que se sube, de modo que el jurado solo los oye en las respuestas. La rama `a25` tampoco entra en la nota de hoy, porque su fusión la decide Carlos. Las cifras de simulación son las de la ficha corta, porque la corrida nueva no está en `docs/SIMULACION.md`.

## 3. Jurado 1 · Profesor de la UNAL

**Quién es.** Es profesor de ingeniería en la Sede Manizales y ha dirigido tesis de ruteo y de logística. Conoce el IDEA y su indicador A25. Lee la ficha con lápiz, abre el repositorio y corre algo si puede. Le importan el método, el uso del conocimiento UNAL y el rigor de las cifras y de la simulación.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Sólido, 15 de 20 | El problema cabe en una frase y repite el entregable de la ficha 04 (`docs/FICHA_CORTA.md`, componente 1). Cada cifra nombra su fuente. El registro de `fuentes-noche` declara 25 discrepancias, y eso habla bien del método (`docs/FUENTES.md`, sección «Discrepancias») | Ninguna cifra la abrió una persona, y el resumen del informe corto lo admite. Diez discrepancias del registro caen en el informe corto y seis en la ficha corta (`ENTREGA.md`, filas 1 y 3; sección 8, punto 6). Para el excelente le falta, además, el usuario con nombre y cargo que pide `docs/ESTRATEGIA.md` |
| 2. Prototipo | Sólido, 18,75 de 25 | El ensayo de la demo pasa 33 de 33 verificaciones sobre `main` (sección 1). El equipo reporta 345 pruebas en verde. La simulación compara cuatro políticas en 360 jornadas con diferencias pareadas (`docs/SIMULACION.md`, sección 5) | Falta el video de respaldo de 60 a 90 segundos que `docs/ESTRATEGIA.md` pide para el excelente, junto con la demo en vivo y la tabla de la simulación. La ficha dice «por grabar». El extractor se midió con 15 mensajes escritos por el propio equipo, que dieron 62 de 64 campos. El lector de SMS se midió con 20 casos que no son independientes (`entrada/pruebas/reporte_campos.md` y `entrada/pruebas/reporte_sms.md`). Ningún mensaje viene de un usuario real |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | Los métodos están bien elegidos y declarados. El ruteo tiene capacidad y ventanas de tiempo en OR-Tools, y la simulación es de eventos discretos con semillas comunes. La regla para elegir el peso de los críticos se escribió antes de correr, y el equipo reporta que ningún factor la cumplió (`docs/SIMULACION.md`, 8.1 a 8.3). La patente 37476 entra como parámetro (`despacho/optimizar.py`, línea 54) | El A25, que la ficha llama capacidad principal, no aparece en el código de `main`. El factor de 1,2 de la patente tiene un solo respaldo, en gulupa a 8 °C. La velocidad de la tesis de 2019 todavía no entra al código de `main`. Ningún profesor de la Sede ha revisado la formulación |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | Cuatro tramos con hito, entregables, responsables, recursos y validación, más una regla de cambio escrita (`docs/FICHA_CORTA.md`, componente 4) | Dos filas dicen «por asignar». El informe corto trae otras fases. El plan detallado de `defensa-noche`, que sí es excelente en estructura, no está en lo que se sube |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | Corre en un portátil con la red vial en disco (`docs/SIN_CONEXION.md`). El costo del simulacro sale de precios con fuente (`datos_publicos/costos.csv`) | Ningún aliado confirmado. El servidor y el plan de SMS están por cotizar, y el costo del modelo es una estimación sin medir (`entrada/ESCALA.md`) |
| 6. Impactos | Parcial, 5 de 10 | Seis indicadores con línea base, meta y forma de verificarlos (`docs/FICHA_CORTA.md`, componente 6) | La magnitud del piloto no tiene número. Las cifras de simulación de la ficha son de la primera corrida, hecha con factor crítico 1, y el código usa el 3 (`despacho/optimizar.py`, línea 50). La corrida nueva no está en `docs/SIMULACION.md` |
| **Total** | **65 de 100** | | |

**Lo que preguntaría.**

- «¿Qué tan lejos del óptimo queda OR-Tools con un segundo de búsqueda?» No hay cota inferior, y la respuesta 14 de `pitch/PREGUNTAS_JURADO.md` lo admite.
- «Si una regla de prioridad empata con el optimizador en críticos, ¿qué aporta el optimizador?» La respuesta está en `docs/SIMULACION.md`, sección 5. DespachoX recorre entre 46,7 y 75,1 km menos por jornada que el despachador con oficio, y recalcular sube los críticos frente a planear una sola vez.
- «Hasta la política ingenua queda bajo el 5 % de desperdicio. ¿Qué mide ese indicador en su simulación?» La sección 7 de `docs/SIMULACION.md` lo reconoce. Los lotes vencen entre 6 y 48 horas, y la rotación por vencimiento basta para dejarlo en 0,0 %.
- «¿Estos números salen del código que tienen hoy?» No del todo, porque la ficha cita la corrida con factor 1 (sección 8, punto 8).
- «¿En qué línea está el A25?» En `main` no está en ninguna. En la rama `a25` está en `despacho/a25.py`.

## 4. Jurado 2 · Directora de operaciones de un banco de alimentos

**Quién es.** Dirige la operación de un banco de alimentos de la red ABACO en otra ciudad. Despacha todos los días a organizaciones inscritas y responde ante los donantes. Se pregunta si esto le sirve el lunes, cuánto le cuesta adoptarlo y qué datos le piden.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Parcial, 10 de 20 | Reconoce el cuello de botella del despacho en los 404.587 kg en acopio frente a 41.163 kg entregados. También reconoce la rutina de organizaciones inscritas que el equipo tomó del banco de Bogotá (`docs/MENTORIA_1.md`) | El equipo no ha hablado con ningún banco. No sabe si el Banco reparte o si las organizaciones recogen, y lo dice (`docs/DECISIONES_9PM.md`, decisión 1). Falta el usuario con nombre y cargo que `docs/ESTRATEGIA.md` pide para el criterio 1 |
| 2. Prototipo | Sólido, 18,75 de 25 | La hoja de ruta impresa trae un QR por paquete (`despacho/hoja.py`). La bodega saca primero lo que vence primero, y cada plan lo aprueba una persona con su nombre. Quien pide no instala nada, porque escribe por Telegram o por SMS | Falta el video de respaldo que `docs/ESTRATEGIA.md` pide para el excelente. El inventario entra por la semilla o por un CSV que carga el equipo (`docs/PLAN_30_90.md`, día 15), y no encontré en `tablero/` una forma de subirlo. WhatsApp queda «para el piloto» (`pitch/PREGUNTAS_JURADO.md`, pregunta 24), pero el plan no le pone hito |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | La vida útil por producto trae fuente, del ICBF, la FDA, el USDA y la FAO (`docs/FICHA.md`, componente 3). El factor del empaque solo cuenta en fruta de un acopio con frío | El A25 no le cambia nada un lunes sin lluvia. El empaque es un supuesto, y ella preguntará si su bodega tiene frío |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | Lo que se le pide está escrito. Son un despachador de contacto, tres datos sin información personal, dos semanas de bitácora y 30 días en paralelo (`docs/FICHA_CORTA.md`, componentes 4 y 5) | No dice cuántas horas por semana le cuesta la bitácora a su despachador, ni quién carga los datos cuando el equipo se vaya |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | El software es abierto y corre en un portátil. Sus datos siguen siendo suyos, y nadie le pide datos de beneficiarios | Falta quién lo sostiene después del día 90. Ese riesgo está en `docs/RIESGOS.md` (R9), que no llega al Drive. Tampoco hay cotización del servidor ni del SMS |
| 6. Impactos | Sólido, 7,5 de 10 | Los indicadores son los que ella ya reporta, como kilos vencidos, entregas confirmadas y kilómetros, y se miden contra su propia línea base. La confirmación de cada entrega le sirve para el reporte al donante | Falta cuántas organizaciones o personas atendería el piloto. La ficha lo deja para los días 0 a 15 |
| **Total** | **62,5 de 100** | | |

**Lo que preguntaría.**

- «¿Cuántas horas de mi despachador cuestan las dos semanas de bitácora?» No hay respuesta escrita.
- «¿Cómo subo mi inventario el lunes, y quién lo actualiza cada día?» Hoy lo carga el equipo desde un CSV.
- «¿Mis organizaciones tienen que aprender Telegram?» La respuesta 24 deja WhatsApp para el piloto, y el plan no le pone fecha.
- «¿Quién lo arregla un domingo?» R9 lo reconoce, con Carlos y Samuel como responsables, pero todavía no hay dueño institucional ni una persona del Banco que lo opere sola.

## 5. Jurado 3 · Funcionaria de gestión del riesgo

**Quién es.** Trabaja en la oficina de gestión del riesgo de un municipio o de un departamento. Conoce la estrategia de respuesta, el puesto de mando unificado, el RUD y SUMA. Mira si esto encaja con la operación de una emergencia, qué riesgos trae, quién lo avala y cómo sería el piloto.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Sólido, 15 de 20 | El inventario de piezas con dueño, del RUD a SUMA y a la plataforma de ABACO, está en la figura 3 del informe corto. Las vías se cierran también sin sismo, con 87 registros en la salida a Letras, de los que 4 son del sismo (`pitch/GUION.md`, bloque 2) | El informe dice que SUMA «no recibe pedidos», y la página de la OPS dice que los sitios registran solicitudes (D8). Quien usa SUMA lo nota de inmediato. Para el excelente le falta el usuario con nombre y cargo que pide `docs/ESTRATEGIA.md` |
| 2. Prototipo | Sólido, 18,75 de 25 | Un cierre queda reportado hasta que una persona lo confirma. Hay ruta impresa y SMS leídos por reglas, que responden a la caída del 28 % de las estaciones base de Caldas el 11 de agosto (`docs/FICHA.md`, componente 2; por verificar) | Falta el video de respaldo que `docs/ESTRATEGIA.md` pide para el excelente. El informe promete exportar a SUMA, y no hay código ni hito para eso. El mapa del tablero todavía necesita internet |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | El A25 es el indicador que usa la UGR, y la ficha cita sus umbrales y su origen (`docs/FICHA_CORTA.md`, componente 3) | En `main` el A25 solo se nombra. En la rama `a25` ya corre, pero las vías de acceso con más cierres quedan fuera de la red de estaciones (sección 1) |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | El plan trae un simulacro con la UGR, un informe al Consejo Municipal de Gestión del Riesgo y un marco legal, la calamidad pública vigente hasta el 9 de agosto de 2027, que sigue por verificar (`docs/FICHA_CORTA.md`, componente 4) | La UGR está «por contactar», y el plan cuenta con horas suyas que nadie ha pedido |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | La ficha trae riesgos con mitigación y cumple la Ley 1581 | Ningún padrino confirmado. La matriz de 16 riesgos con señal temprana y responsable existe en `defensa-noche`, pero no llega al Drive |
| 6. Impactos | Parcial, 5 de 10 | Indicadores con línea base y forma de verificarlos | El plan usa como línea base del recálculo los 9 h 46 min que tardó en aparecer el registro oficial de un cierre (`docs/PLAN_30_90.md`, sección 5). Ese número mide cuándo se publicó un registro, y el indicador mide una replanificación. Faltan los beneficiarios del territorio |
| **Total** | **65 de 100** | | |

**Lo que preguntaría.**

- «¿Esto entra a la estrategia municipal de respuesta o corre aparte?» El plan propone un informe al Consejo, y la UGR todavía no ha respondido.
- «¿Exporta a SUMA?» Hoy no.
- «¿Qué pasa si alguien reporta un cierre falso, o si nadie reporta uno real?» El despachador confirma cada cierre, y la simulación no modela cierres falsos ni tardíos (`docs/SIMULACION.md`, sección 7).
- «¿Quién responde si una ruta pasa por una ladera en alerta roja?» Con el A25 encendido, una vía con historial de deslizamientos se encarece sin cerrarse, y la ruta la aprueba el despachador. Una vía en roja sin historial no se encarece, como la avenida Paralela con la lluvia sintética.

## 6. Tabla consolidada

Los tres jurados ponen la misma nota en el prototipo, el conocimiento, el plan y los aliados, aunque por razones distintas. Difieren en el problema y en los impactos.

| Criterio | Peso | Académico | Banco | Riesgo | Rango |
|---|---:|---:|---:|---:|---|
| 1. Problema y vertical | 20 | 15,0 | 10,0 | 15,0 | 10,0 a 15,0 |
| 2. Prototipo | 25 | 18,75 | 18,75 | 18,75 | 18,75 |
| 3. Conocimiento utilizado | 15 | 7,5 | 7,5 | 7,5 | 7,5 |
| 4. Plan de 30 a 90 días | 15 | 11,25 | 11,25 | 11,25 | 11,25 |
| 5. Viabilidad y aliados | 15 | 7,5 | 7,5 | 7,5 | 7,5 |
| 6. Impactos | 10 | 5,0 | 7,5 | 5,0 | 5,0 a 7,5 |
| **Total hoy** | **100** | **65,0** | **62,5** | **65,0** | **62,5 a 65,0** |
| A la 1:00 p. m., si nadie abrió las fuentes [E] | | 60,0 | 57,5 | 60,0 | 57,5 a 60,0 |
| Con las cinco y sin respuesta del Banco [E] | | 72,5 | 62,5 | 72,5 | 62,5 a 72,5 |
| Con las cinco y respuesta citable del Banco [E] | | 81,25 | 71,25 | 77,5 | 71,25 a 81,25 |

**Cómo se cuentan las tres últimas filas.** La fila de la 1:00 p. m. aplica la regla del guion. Si nadie abrió las fuentes, las cifras con asterisco salen del pitch, y el criterio 1 baja un nivel con cada jurado. Las dos filas siguientes parten de ahí y suman las cinco correcciones de la sección 7. Además, suponen que antes de registrar se corrigen las frases con discrepancia y las fases del informe corto, como pide la lista final de `ENTREGA.md` (sección 8, punto 6). Si el informe sube como está, el académico no pasa de sólido en los criterios 1 y 4, y la funcionaria no pasa de sólido en el 1. En ese caso la última fila queda en 72,5, 71,25 y 72,5.

**Qué pesa distinto cuando la nota coincide.** En el prototipo, los tres ven la demo andar y a los tres les falta el video. Al académico le pesa además que el lector se midió con mensajes del propio equipo. A la directora le pesa que no puede subir su inventario, y a la funcionaria, que el informe promete exportar a SUMA y que el mapa necesita internet. En el conocimiento, el académico y la funcionaria quieren ver el A25 en el código. La directora no lo echa de menos un lunes sin lluvia, y le baja la nota al empaque, que es un supuesto. En el plan, el académico mira la estructura y los nombres. La directora pregunta cuántas horas le cuesta a su despachador, y la funcionaria, por las horas de la UGR que nadie ha pedido. En los aliados, el académico y la directora esperan al Banco. A la funcionaria la mueve la matriz de riesgos, porque su padrino natural es la UGR.

**Por qué cada jurado sube distinto.** La respuesta del Banco le da a la directora el usuario que le falta en el criterio 1 y el aliado del criterio 5. Aun así, ella se queda en sólido en el criterio 1, porque una llamada no le muestra cómo despacha el Banco, que es lo que ella mira. El académico y la funcionaria, en cambio, llegan a excelente en el criterio 1 cuando se juntan las cifras abiertas por una persona, el usuario con nombre y cargo y un informe sin discrepancias. Las dos primeras condiciones son la barra de `docs/ESTRATEGIA.md`, que aplico igual a los tres jurados. La tercera es el hueco que los dos anotaron.

## 7. Las cinco correcciones, por puntos por hora

Cada corrección se cuenta contra la fila de la 1:00 p. m. de la tabla consolidada, así que la corrección 2 cobra lo que evita perder. Cuando un nivel solo sube con dos correcciones, cada una se lleva la mitad. Los puntos son el promedio de los tres jurados [E]. El tiempo cuenta el trabajo que falta, sin lo que ya está en la agenda, como la llamada de las 8:00 a. m. El orden sigue el punto medio de los puntos por hora.

| # | Corrección | Qué mueve [E] | Puntos [E] | Tiempo | Puntos por hora, punto medio | Quién, propuesto |
|---|---|---|---|---|---:|---|
| 1 | Anotar lo que respondió el Banco | Criterio 5 del académico y de la directora, y criterio 1 de la directora, de parcial a sólido. Con la 2, la mitad del excelente en el criterio 1 del académico y de la funcionaria | De 0 a 5,8, según la respuesta | 20 min | 8,8 | Integrante de Ingeniería Industrial y Fable |
| 2 | Verificar por persona las siete cifras del pitch | Evita que el criterio 1 baje un nivel con los tres jurados a la 1:00 p. m. Con la 1, la otra mitad del excelente en el criterio 1 del académico y de la funcionaria | De 5,0 a 6,7, según la respuesta del Banco | 60 min | 5,8 | Samuel |
| 3 | Fusionar `a25` y decir dónde está el A25, a qué vías toca y a cuáles no llega | Criterio 3 del académico y de la funcionaria, de parcial a sólido | 2,5 | 60 min | 2,5 | Carlos decide y Fable fusiona |
| 4 | Nombrar al integrante de Ingeniería Industrial y dejar un solo reparto | Con la 5, la mitad del excelente en el criterio 4 del académico | 0,6 | 15 min | 2,5 | Carlos da el nombre y Fable edita |
| 5 | Subir el plan y la matriz de riesgos al Drive, y enlazarlos | Criterio 5 de la funcionaria, de parcial a sólido. Con la 4, la otra mitad del excelente en el criterio 4 del académico | 1,9 | 60 min | 1,9 | Fable y Samuel |

Contadas desde la fila de la 1:00 p. m., las cinco suman en promedio 17,5 puntos con respuesta del Banco y 10,0 sin ella. Esas sumas cuadran con la tabla consolidada. Las correcciones 3 y 4 empatan en 2,5 puntos por hora. Va primero la 3, porque es código y tiene que entrar antes del congelamiento de las 8:30 a. m. La 4 solo cobra sus puntos si se hace también la 5.

### Corrección 1 · Anotar lo que respondió el Banco a las 8:00 a. m.

**Por qué suma.** El criterio 5 pide padrinos, y `docs/ESTRATEGIA.md` pide para el excelente del criterio 1 un usuario con nombre y cargo. Hoy la ficha dice que ningún aliado ha visto la propuesta. Una respuesta del Banco que se pueda citar, aunque sea un «muéstrenoslo el lunes», sube a sólido el criterio 5 del académico y de la directora, y el criterio 1 de la directora. Con la corrección 2, además, abre el excelente del criterio 1 para el académico y la funcionaria. El criterio 5 de la funcionaria no se mueve, porque su padrino es la UGR. Si el Banco dice que las organizaciones recogen y nadie reparte, se aplica la regla de cambio y se dice así, porque esa regla ya está escrita.

**Archivo.** `docs/FICHA_CORTA.md` (`main`, `7131261`), componente 5.

**Dice hoy.**

> **Aliados.** Ninguno ha visto todavía la propuesta.

**Propuesta, solo si hubo conversación.**

> **Aliados.** El Banco Arquidiocesano de Alimentos conoció la propuesta el sábado a las [hora], por [llamada o visita], con [cargo]. Los demás aliados todavía no la han visto.

**Dice hoy, en la tabla de aliados.**

> | Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | Llamada el sábado a las 8:00 a. m. |

**Propuesta.**

> | Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | [Cargo] respondió el sábado a las [hora]. [Reparte o recogen.] [Siguiente paso, con fecha] |

**Archivo.** `pitch/GUION.md` (`pitch-noche`, `d337e06`), notas del bloque 7. La frase de reemplazo ya está escrita y solo entra con permiso de la persona.

> Esta mañana se lo mostramos a [cargo] del Banco, que nos dijo: «[frase textual]».»

**Dato que falta y dónde conseguirlo.** Lo trae el integrante de Ingeniería Industrial, con el encargo `encargos/P5_ALIADO_PILOTO.pdf`. Ese encargo fija la entrega a las 12:30 p. m., y `ENTREGA.md` saca el PDF de la ficha a las 12:40. Diez minutos no alcanzan, así que conviene un aviso corto en `torre/CANAL.md` apenas cuelgue, antes de la mentoría 2 de las 10:30 a. m.

### Corrección 2 · Abrir por persona las siete cifras con asterisco de la versión de tres minutos

**Por qué suma.** El guion trae su propia regla, y esa regla saca las cifras del pitch si nadie las abre.

> Si a la 1:00 p. m. nadie ha abierto la fuente de una cifra con asterisco, esa cifra sale del pitch.

**Supuesto de esta corrección [E].** Sin verificación, el pitch pierde a la 1:00 p. m. el acopio de Manizales, los kilos de Portafolio, los registros de Letras, el cierre del RUD y el carril de la vía a Pereira. Con eso, el criterio 1 baja un nivel con los tres jurados. Esa caída es la fila de la 1:00 p. m. de la tabla consolidada, y esta corrección la evita. Con la respuesta del Banco, además, el académico y la funcionaria pueden darle excelente al criterio 1.

`docs/VERIFICAR_SAMUEL.md` (`fuentes-noche`) ya trae las 15 cifras en orden, con enlace y casillas. `pitch/CIFRAS_PITCH.md` (`pitch-noche`, `d337e06`) les da un código y un orden para verificar. La versión de tres minutos tiene siete cifras con asterisco.

1. C01. Manizales fue «uno de los principales puntos de acopio» de la red (Noticias RCN, 10 de agosto).
2. C02. 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados (Portafolio, 16 de agosto). Desde las 12:46 a. m. el guion nombra también las 157 t en camino, que la comparación dejaba fuera, y ya no dice «en todo el país» (D3, commit `2e31c5f`).
3. C04. 87 registros de cierre en la salida a Letras desde 2017 (`datos_publicos/cierres_historicos.csv`, con el enlace de cada fila al registro #767 de INVÍAS o a la prensa).
4. C05. «y solo 4 son del sismo», que son las filas S04, S09, S10 y S11 del mismo CSV. Va en la misma frase que C04, pero es otra cifra y se verifica aparte.
5. C08. El RUD cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas (Vanguardia, 5 de octubre). Según la fila del RUD en el registro de `fuentes-noche`, la nota habla de auxilios económicos y no de comida.
6. C10. El 21 de octubre un deslizamiento dejó a un carril la vía a Pereira y solo pasaban livianos (fila S22 de `datos_publicos/cierres_historicos.csv`, con su consulta al registro #767).
7. C12. «y los tres puntos críticos siguen a tiempo», el resultado de la demo. Es una medida sobre la semilla sintética, así que se verifica viéndola en el ensayo de la mañana. Si nadie la ve, sale del pitch como las demás.

**Archivo.** `docs/FUENTES.md` (`fuentes-noche`), columna «Estado». Quien abra la fuente escribe «Verificada por [nombre], [hora]», como pide la sección «Cómo anotar una verificación».

**Archivo.** `docs/FICHA_CORTA.md`, línea 6.

> Las cifras de fuentes externas están por verificar.

**Propuesta, cuando se hayan abierto.**

> [Nombre] abrió el sábado las fuentes de las cifras que dice el pitch, y su estado está en `docs/FUENTES.md`. Las demás cifras de fuentes externas siguen por verificar.

**Archivo.** `docs/FICHA_CORTA.md`, componente 1, línea 12. La ficha conserva el «en todo el país» que el guion ya quitó. Conviene la misma corrección que Fable hizo en la pregunta 1 de `pitch/PREGUNTAS_JURADO.md` (`defensa-noche`, commit `b0f3415`).

> Al sexto día tenía 404.587 kg en acopio y había entregado 41.163 kg en todo el país (Portafolio; por verificar).

**Propuesta.**

> El 16 de agosto, los bancos de alimentos tenían 404.587 kg en acopio y 157.164 kg en tránsito, y habían entregado 41.163 kg (Portafolio; por verificar).

**Archivo.** `docs/informe/informe_corto.tex`, resumen. El cambio exige recompilar, y solo compila el computador de Carlos.

> Ninguna cifra de este informe ha sido verificada todavía por una persona del equipo.

**Propuesta.**

> Una persona del equipo verificó el 21 de noviembre las cifras que usa el pitch. Las demás siguen por verificar.

### Corrección 3 · Fusionar `a25` y decir dónde está el A25, a qué vías toca y a cuáles no llega

**Por qué suma.** El criterio 3 mira la identificación, la pertinencia y la aplicación del conocimiento (`docs/ESTRATEGIA.md`, rúbrica). La ficha llama al A25 «capacidad principal» y dice que no está en el código, y un profesor de la UNAL va a preguntar dónde está. La rama `a25` lo implementa con estaciones y umbrales con fuente, lluvia sintética rotulada y el gancho apagado por defecto. Corrí la última versión de la rama (`b96ff71`) fusionada en seco con `main`. La fusión no tiene conflictos y pasan 366 pruebas. La demo da 33 de 33 con el gancho apagado y encendido [M]. Es código, así que tiene que entrar antes del congelamiento de las 8:30 a. m., y la decisión es de Carlos.

**Lo que hay que decir antes de que lo pregunten.**

- **Cobertura.** Las vías de acceso con más cierres por ladera quedan a más de 3 km de toda estación, y el módulo responde «fuera de la red» para ellas. La salida a Letras, con 87 registros, tiene la estación más cercana a 10,11 km. `docs/A25.md` lo dice en su sección 2, pero la ficha y las diapositivas no.
- **Qué vías encarece.** El gancho solo toca las ocho vías con cierres por ladera en el historial (`despacho/a25.py`, función `riesgo_corredores`, con `solo_con_historial=True`). Una vía en roja sin historial no se encarece. Con la lluvia sintética del 21 de noviembre, la avenida Paralela queda en roja y su costo no cambia [M]. Hoy la ficha, el anexo, las diapositivas, el guion y la pregunta 13 dicen que el A25 sube el costo de «cada tramo» o encarece «los tramos en alerta».
- **Supuestos.** Los 3 km de cobertura y los factores ×2 y ×4 son supuestos nuestros hasta calibrarlos con el IDEA (`docs/A25.md`, sección 7).

El mensaje final de la línea de órdenes de la rama tampoco nombra el historial («encarece sin prohibir las vías en alerta»). Conviene que Fable lo ajuste en la rama `a25` antes de fusionar.

**Archivo.** `docs/FICHA_CORTA.md`, componente 3.

> En DespachoX, la alerta de la estación más cercana sube el costo de cada tramo, para que el optimizador evite las laderas en alerta. Entra en el piloto, en los días 60 a 90, y hoy no está en el código.

**Propuesta, si se fusiona.**

> En DespachoX, el A25 ya corre en el código, con lluvia sintética rotulada como tal. Cada tramo toma la alerta de la estación más cercana. Si se enciende, el optimizador encarece, sin cerrarlas, las vías con historial de deslizamientos que están en alerta naranja o roja. Viene apagado por defecto. En los días 60 a 90 del piloto se conecta a los datos diarios del IDEA. Las salidas con más cierres, como la de Letras, quedan a más de 3 km de toda estación y no reciben alerta. Esa cobertura y el recargo de cada nivel son supuestos nuestros hasta calibrarlos con el IDEA.

La propuesta suma unas 60 palabras. Fable dejó la ficha en 2.765 palabras, por debajo de 2.800 (commit `f5aaa7d`). Si el equipo quiere conservar ese límite, la última oración puede quedarse solo en el anexo.

**Archivo.** `docs/FICHA.md`, componente 3.

> En DespachoX, el A25 sube el costo de cada tramo según la alerta de la estación más cercana, para que el optimizador evite las laderas en alerta. Entra en el piloto, en los días 60 a 90, y no está en el código hoy.

**Propuesta.** La misma de la ficha corta. El anexo puede añadir los factores, ×2 en naranja y ×4 en roja, y la forma de encender el gancho, `DESPACHOX_A25=1`.

**Archivo.** `pitch/DIAPOSITIVAS.md` (`pitch-noche`, `d337e06`), diapositiva de respaldo A, columna «Uso».

> Sube el costo de cada tramo según la alerta de la estación más cercana, solo en naranja o roja, y nunca lo cierra

**Propuesta.**

> Sube el costo de las vías con historial de deslizamientos según la alerta de la estación más cercana, solo en naranja o roja, y nunca las cierra

**Misma diapositiva, columna «Estado».**

> Hecho en la rama `a25` con lluvia sintética y apagado por defecto; entra a `main` si Carlos lo fusiona. En el piloto, días 60 a 90, con lluvia real

**Propuesta, si se fusiona.**

> En el código con lluvia sintética y apagado por defecto. En el piloto, días 60 a 90, con lluvia real. No cubre cinco vías de acceso, entre ellas las salidas a Letras y a Medellín, que quedan a más de 3 km de toda estación

**Archivo.** `pitch/GUION.md` (`pitch-noche`, `d337e06`), notas del bloque 7.

> Encendido, encarece los tramos en alerta naranja o roja y nunca los cierra

**Propuesta.**

> Encendido, encarece las vías con historial de deslizamientos que están en alerta naranja o roja, y nunca las cierra

**Archivo.** `pitch/PREGUNTAS_JURADO.md` (`defensa-noche`, `5737e09`), pregunta 13.

> que en el piloto subirá el costo de cada tramo según la alerta de la estación más cercana [F]. Hoy no está en el código, porque entra en los días 60 a 90 con datos del IDEA, y estamos pidiendo el visto bueno de un profesor del instituto.

**Propuesta.**

> que DespachoX ya lee en el código con lluvia sintética [M]. Encendido, el optimizador encarece las vías con historial de deslizamientos que están en alerta naranja o roja, y nunca las cierra. En los días 60 a 90 se conecta a los datos diarios del IDEA, y estamos pidiendo el visto bueno de un profesor del instituto.

**Archivo.** `docs/RIESGOS.md` (`defensa-noche`, `5737e09`), justificación de R12. Las dos oraciones cambian juntas, porque con la rama fusionada la segunda contradice a la primera.

> El A25 es la capacidad UNAL principal y hoy no está en el código (`docs/FICHA.md`, componente 3). Integrarlo sin datos del IDEA obligaría a inventar umbrales y tramos (`docs/SUGERENCIAS.md`, sección 6).

**Propuesta.**

> El A25 es la capacidad UNAL principal y ya corre en el código con lluvia sintética (`docs/A25.md`). Sus umbrales y sus estaciones salen del IDEA, pero la cobertura de 3 km y el recargo de cada nivel son supuestos hasta calibrarlos con el instituto (`docs/A25.md`, sección 7).

El bloque 7 de `pitch/GUION.md` ya trae la frase condicional para este caso, «La alerta de lluvia A25 del IDEA de la UNAL ya está en el código, por ahora con lluvia de prueba». Si Carlos no fusiona, las frases quedan como están. Aun así, el límite de cobertura conviene en la nota del orador de la diapositiva A, porque el jurado puede preguntarlo de todos modos. Si el profesor del IDEA revisa el uso antes del pitch, su visto bueno se anota con su cargo y la hora, y el académico sube el criterio 3 otro nivel.

**Las fuentes del A25.** Según el aviso de Noche-2 de la 1:24 a. m. en `torre/CANAL.md`, los enlaces del reporte A25 de 2020 y del Boletín Ambiental 145 del IDEA daban error 404. No lo comprobé, porque esta revisión no abre fuentes externas. Si el académico abre esos enlaces y fallan, el criterio 3 pierde su respaldo con fuente, así que conviene cambiarlos antes de la entrega, como propone ese aviso.

### Corrección 4 · Poner nombre al integrante de Ingeniería Industrial

**Por qué suma.** El criterio 4 pide responsables, y un rol sin nombre se lee como un hueco. `docs/PLAN_30_90.md` nombra el rol 10 veces, `docs/RIESGOS.md` 6 y `pitch/PREGUNTAS_JURADO.md` 4, siempre sin la persona. La ficha corta, además, pone a Samuel en el acuerdo con el Banco, y la decisión de Carlos de las 23:01 se lo dio al integrante de Ingeniería Industrial. Con el nombre y con el plan en el Drive (corrección 5), el académico le da excelente al criterio 4.

**Archivo.** `docs/PLAN_30_90.md` (`defensa-noche`, `5737e09`), sección 6.

> El integrante de Ingeniería Industrial lleva la relación con el Banco y la medición.

**Propuesta.**

> [Nombre y apellido], de Ingeniería Industrial, lleva la relación con el Banco y la medición.

Lo mismo en las 20 apariciones de «integrante de Ingeniería Industrial» en los tres archivos.

**Archivo.** `docs/FICHA_CORTA.md`, tabla del componente 4.

> Samuel (acuerdo), Jacobo (bitácora), Carlos (datos)

**Propuesta.**

> [Nombre] (acuerdo y línea base), Samuel (aval de la UGR), Jacobo (bitácora), Carlos (datos)

> Carlos; por asignar la revisión externa

**Propuesta.**

> Carlos (reconstrucción); [Nombre] (revisión con un profesor de logística de la Sede)

> Todo el equipo; por asignar el informe

**Propuesta.**

> Todo el equipo; [Nombre] (informe)

**Dato que falta y dónde conseguirlo.** El nombre no está en el repositorio. Tampoco está en `encargos/P5_ALIADO_PILOTO.pdf`, que va dirigido «al integrante de Ingeniería Industrial». `docs/ESTRATEGIA.md` lista a Nicolás Ramírez y a José Manuel Aristizábal sin rol, así que no lo supuse. Lo sabe Carlos.

### Corrección 5 · Subir el plan de 30 a 90 días y la matriz de riesgos al Drive

**Por qué suma.** Lo mejor del equipo para los criterios 4 y 5 está en `defensa-noche`. El plan tiene cinco hitos con criterio para seguir, ajustar o parar, y la matriz tiene 16 riesgos con señal temprana, mitigación y responsable. La lista de `ENTREGA.md` no los sube, y la sección «Para el jurado» del README no los enlaza. `ENTREGA.md` dice que el jurado califica lo que logra abrir. Con la matriz en el Drive, la funcionaria sube a sólido el criterio 5. Con el nombre de la corrección 4, el académico le da excelente al criterio 4.

**Qué cabe en la hora.** Fusionar `defensa-noche`, que entra sin conflictos. Llenar los 10 [SIM] del plan y de la matriz, 6 y 4, con la corrida que Carlos dé por buena. Quitar del plan la sección 9, «Lo que falta para cerrar este plan», que es una lista de pendientes. Sacar los dos PDF y editar `ENTREGA.md`, `README.md` y `docs/FICHA_CORTA.md`. El nombre del integrante es la corrección 4.

**Archivo.** `ENTREGA.md` (`fuentes-noche`, `2261013`), tabla «Qué se sube».

**Dice hoy.** La tabla termina en la fila 6, que empieza así.

> | 6 | Enlace al tablero y al bot |

**Propuesta.** Añadir una fila después de esa.

> | 7 | Plan de 30 a 90 días y matriz de riesgos, en PDF | `docs/PLAN_30_90.md` y `docs/RIESGOS.md` | Cambiar cada [SIM] por la cifra nueva. Poner el nombre del integrante de Ingeniería Industrial. Quitar del plan la sección 9, «Lo que falta para cerrar este plan» | Samuel | Carlos |

**Dice hoy, en el horario.**

> | 12:40 | PDF de la ficha y del anexo, con los comandos de abajo. Se revisa que el anexo no traiga la nota interna | Samuel |

**Propuesta.**

> | 12:40 | PDF de la ficha, del anexo, del plan y de la matriz de riesgos, con los comandos de abajo. Se revisa que el anexo no traiga la nota interna | Samuel |

**Dice hoy, en la lista final.**

> - [ ] Los seis elementos abren sin sesión de Google, en incógnito y en un celular con datos móviles.

**Propuesta.**

> - [ ] Los siete elementos abren sin sesión de Google, en incógnito y en un celular con datos móviles.

**Archivo.** `README.md` (`fuentes-noche`), tabla de la sección «Para el jurado». En la columna «Dónde» de estas dos filas, el primer enlace pasa a ser el documento nuevo.

> | 4. Plan de 30 a 90 días | Hitos, responsables, recursos y validación, y los territorios propuestos |

**Propuesta.** Poner `[docs/PLAN_30_90.md](docs/PLAN_30_90.md)` antes de `docs/FICHA.md` en la columna «Dónde».

> | 5. Viabilidad y aliados | Costos, riesgos, operación sin internet y lo que se le pide a cada aliado |

**Propuesta.** Poner `[docs/RIESGOS.md](docs/RIESGOS.md)` antes de `docs/FICHA.md` en la columna «Dónde».

**Archivo.** `docs/FICHA_CORTA.md`, línea 6.

> El anexo técnico, con todas las cifras, supuestos y riesgos, está en `docs/FICHA.md`.

**Propuesta.**

> El anexo técnico está en `docs/FICHA.md`. El plan detallado de 30 a 90 días está en `docs/PLAN_30_90.md`, y la matriz de 16 riesgos, en `docs/RIESGOS.md`.

### El video de respaldo, fuera de las cinco

**Por qué no entra.** Ya tiene lugar en la agenda. `docs/ESTRATEGIA.md` lo pone el sábado de 8:30 a 10:30 a. m., los encargos P2 (punto 5) y P3 (punto 4) se lo dan a Jacobo, y `ENTREGA.md` lo sube en su fila 4. Por sí solo, además, no le da excelente en el criterio 2 a ningún jurado. `docs/ESTRATEGIA.md` lo pide para el excelente, junto con la demo en vivo y la tabla de la simulación, y aplico esa barra como condición necesaria, igual que en el criterio 1. Pero cada jurado tiene en el criterio 2 otro hueco que el video no tapa, como el lector medido con mensajes propios, el inventario que no se puede subir o el mapa que necesita internet (secciones 3 a 5).

**Lo que vale [E].** Es un seguro. Si la demo en vivo falla y no hay video, el criterio 2 baja a parcial con los tres jurados, 6,25 puntos con cada uno. En ese caso el video vale 6,25 puntos por hora, más que cualquiera de las cinco salvo la primera. Si la demo en vivo sale bien, suma poco. No sé estimar la probabilidad de que falle, porque esta noche nadie probó la nube ni Telegram. `demo/CHECKLIST.md` (`demo-noche`) ya manda pasar al video si los pasos 3 a 5 fallan diez minutos antes.

**Quién y cuánto [E].** Jacobo, en cerca de una hora, entre grabar con `docs/GUION_DEMO.md`, cortar, subir el archivo y abrirlo sin sesión.

**Lo que pide esta revisión.** Que el video dure entre 60 y 90 segundos, como pide `docs/ESTRATEGIA.md`, que abra sin sesión y que la ficha diga dónde está. Si a las 10:30 a. m. no existe, Jacobo avisa en el canal, porque entonces el único respaldo es la demo por terminal de `demo-noche`.

**Archivo.** `docs/FICHA_CORTA.md`, componente 2, línea 34.

> El jurado puede escribirle al bot con el QR. [Video de respaldo: por grabar.]

**Propuesta, cuando exista.**

> El jurado puede escribirle al bot con el QR. El mismo recorrido está grabado en un video de [N] segundos, en la carpeta del Drive.

Si a las 12:40 p. m. no existe, el corchete se borra, como ya pide la fila 1 de `ENTREGA.md`.

## 8. Otras correcciones, más pequeñas

Suman menos o dependen de algo que todavía no pasa. Van en el orden en que las haría.

**6. El informe corto y la ficha corta dicen cosas que sus fuentes no dicen.** El informe que se sube al Drive se compiló el viernes a las 18:04, antes de las decisiones de las 9:00 p. m. Sus fases no son las de la ficha, y diez discrepancias del registro de `fuentes-noche` caen en él, en trece pasajes (`ENTREGA.md`, fila 3). La lista final de `ENTREGA.md` ya pide corregir o quitar esas frases antes de registrar, y la tabla consolidada lo da por hecho. Sin esa corrección, las cinco de la sección 7 suman en promedio 4,6 puntos menos con respuesta del Banco y 1,25 menos sin ella.

Hay dos salidas. Una es corregir los pasajes en `docs/informe/informe_corto.tex` y recompilar en el computador de Carlos, en unos 80 minutos. Abrir las diez fuentes toma unos 50, y editar y recompilar, unos 30. La otra es no subir el informe. Antes de cambiar cada frase, una persona abre la fuente, porque la lectura de máquina puede equivocarse. Varias propuestas copian las correcciones que Fable ya hizo en el pitch y en las preguntas, para que todos los documentos digan lo mismo.

| Discrepancia | Línea | Dice hoy | Propuesta |
|---|---:|---|---|
| Fases | 204 | `\item \textbf{Fases.} Días 1 a 30, el Banco usa la herramienta en paralelo y se mide la línea base. Días 31 a 60, entran las juntas y los reportes viales. Días 61 a 90, simulacro en temporada de lluvias, exportación a SUMA e informe de lecciones.` | `\item \textbf{Fases.} Días 0 a 15, acuerdo y línea base. Días 15 a 30, reconstrucción en frío de un mes de despachos. Días 30 a 60, uso en paralelo, con DespachoX planeando en sombra. Días 60 a 90, simulacro con la UGR, A25 por tramo y decisión escrita del Banco.` La exportación a SUMA queda o sale según decida Carlos (pregunta 4) |
| D3 | 114 | `pero al sexto día tenía 404.587 kg en acopio y había entregado 41.163 kg en todo el país.` | Cerrar la oración en «puntos de acopio» y seguir con `El 16 de agosto, los bancos tenían 404.587 kg en acopio y 157.164 kg en tránsito, y habían entregado 41.163 kg.` La nota no dice «sexto día» ni «en todo el país», y trae los kilos en tránsito |
| D3 | 145 | `Al sexto día, sin embargo, la red tenía en acopio mucho más de lo que había entregado` | `El 16 de agosto, sin embargo, la red tenía en acopio mucho más de lo que había entregado` |
| D3 | 149 | `Kilos de la red de bancos de alimentos al sexto día después del sismo, en todo el país.` | `Kilos de la red de bancos de alimentos el 16 de agosto, seis días después del sismo.` La figura ya muestra las tres barras, con los 157.164 kg en tránsito |
| D7 | 114 | `con la Cruz Roja como operador logístico.` | `con entregas en la sede de la Cruz Roja.` La nota de la Alcaldía del 31 de agosto habla de «nuestro operador logístico» sin nombrarlo |
| D7 | 153 | `La Cruz Roja Seccional Caldas fue el operador logístico que entregó por turnos los kits de alimentos de la Alcaldía \cf{f:alcago}.` | `Los kits de alimentos de la Alcaldía se entregaron por turnos en la sede de la Cruz Roja Seccional Caldas \cf{f:alcago}.` Es la frase de `pitch/CIFRAS_PITCH.md`, A05, que la máquina tampoco encontró igual del todo |
| D8 | 160 | `pero no recibe pedidos ni planea rutas` | `registra las solicitudes de artículos, pero no planea rutas ni asigna vehículos` |
| D9 | 155 | `El Programa Mundial de Alimentos (PMA) entregó efectivo en ciudades de Valle y Risaralda y raciones en especie en zonas remotas` | Según la lectura de máquina, Telesur dice que el PMA «prevé ampliar las transferencias de efectivo» en zonas urbanas de Valle y Risaralda. La frase se ajusta a lo que diga la nota cuando una persona la abra |
| D10 | 153 | `y desde el 11 de agosto el albergue del Coliseo Mayor dejó de recibir perecederos` | `y desde el 11 de agosto el punto de donaciones del Coliseo Menor no recibía perecederos`. La lectura de máquina no dice «oficial». La pregunta 5 de `defensa-noche` (`88d0cda`) sí dice «punto oficial», así que conviene quitarlo también allí |
| D11 | 124 | `Ese día el Coliseo Mayor seguía como albergue principal \cf{f:censo}.` | `Ese día el Coliseo Mayor seguía como uno de los principales albergues temporales \cf{f:censo}.` |
| D14 | 145 | `El principal fue la llegada al territorio, y le siguieron el transporte, la articulación entre actores, el almacenamiento en los acopios y las vías de acceso hacia las zonas rurales \cf{f:retos}.` | `Entre ellos estaban el transporte, la articulación entre actores y la llegada al territorio, además del almacenamiento en los acopios y las vías de acceso hacia las zonas rurales \cf{f:retos}.` La nota los nombra juntos y no dice cuál es el principal. Quien habla es la gerente de Cooperación Internacional de la red |
| D18 | 126 | `la vía Manizales–Fresno en el Alto de Letras, entre los kilómetros 36 y 40 \cf{f:vias}` | `la vía Manizales–Fresno en Herveo, entre los kilómetros 36 y 40 \cf{f:vias}`. Semana dice Herveo y no nombra el Alto de Letras. Minuto30, del 10 de agosto, sí lo nombra |
| D21 | 153 | `Al 2 de septiembre llevaba 18.847 unidades entregadas` | `Al 2 de septiembre llevaba 18.847 unidades de ayuda entregadas, entre kits de alimentos, tejas, frazadas, colchonetas y baldes` |
| D24 | 153 | `había que llevar el formato azul que entregan los Bomberos después de revisar la vivienda.` | `había que llevar el formato azul que entregan los Bomberos.` El detalle de la vivienda sale de La Patria, que no está en las fuentes del informe |

La ficha corta tiene seis discrepancias (`ENTREGA.md`, fila 1). D3 está en la corrección 2, y D16, el conteo de pruebas, en el punto 7. Las otras cuatro también se corrigen antes de registrar.

| Discrepancia | Línea | Dice hoy | Propuesta |
|---|---:|---|---|
| D7 | 12 | `y la Cruz Roja Seccional Caldas entregó los kits por turnos (Alcaldía; por verificar)` | `y los kits se entregaron por turnos en la sede de la Cruz Roja Seccional Caldas (Alcaldía; por verificar)` |
| D12 | 44 | `Sus umbrales de alerta son 200, 300 y 400 mm, y el reporte de 2020 cubre 14 estaciones (IDEA; por verificar).` | `Sus umbrales de alerta son 200, 300 y 400 mm (IDEA; por verificar).` Las fuentes no coinciden en el número de estaciones, y la diapositiva A ya no lo dice (`pitch/CIFRAS_PITCH.md`, P14) |
| D15 | 14 | `La salida a Letras suma 87 registros de cierre por deslizamiento o derrumbe entre 2017 y 2026, aunque un mismo derrumbe puede tener varios registros (INVÍAS; por verificar).` | `La salida a Letras suma 87 registros de cierre por deslizamiento o derrumbe entre 2017 y 2026, y 4 de ellos son del sismo, así que sin el sismo quedan 83. Un mismo derrumbe puede tener varios registros (INVÍAS; por verificar).` Es la corrección que Fable ya hizo en la pregunta 2 (`01ad131`) |
| D18 | 14 | `y la salida a Fresno por el Alto de Letras (Semana; por verificar)` | `y la vía Manizales–Fresno en Herveo, entre los kilómetros 36 y 40 (Semana; por verificar)` |

Las líneas 109 y 119 de la ficha corta también dicen «al sexto día», que la nota de Portafolio no dice (D3). Basta con «el 16 de agosto». El anexo, `docs/FICHA.md`, tiene doce discrepancias (`ENTREGA.md`, fila 2). No las copio aquí, y si el anexo se sube, se corrigen con las mismas propuestas.

**7. El conteo de pruebas está viejo en dos lugares.** La ficha corta dice 306 y el README de `fuentes-noche` dice 342 con 3 omitidas. El último conteo del equipo es 345 (23:50), y el conteo se repite después del congelamiento.

> y las 306 pruebas automáticas del repositorio pasan [M].

**Propuesta.** «y en la revisión de [hora] pasaron [N] pruebas automáticas con `python -m pytest -q` [M].»

> En la revisión del viernes a las 11:15 p. m. pasaron 342 y se omitieron 3

**Propuesta.** «En la revisión de [hora] pasaron [N] y se omitieron [K]», con el conteo final. Aparte, conviene que `entrada/pruebas/conftest.py` quite `DESPACHOX_SIN_RED` en las pruebas que inyectan un extractor falso, para que la suite no dependa de esa variable. Es código de `entrada/`, así que lo hace Samuel o quien Fable designe.

**8. La cifra de simulación de la ficha no es la del código de hoy.** La ficha cita la primera corrida, hecha con factor crítico 1 (`docs/SIMULACION.md`, sección 5, commit `d33dd27`), y el código usa el factor 3. La corrida con las velocidades de la tesis de 2019, que el pitch espera para cada [SIM], llegó a la rama `simulacion` a las 12:41 a. m. (`despacho/sim/resultados_velocidades/tablas.md`, commit `f52ea33`). Todavía no está en `docs/SIMULACION.md`, y no revisé sus cifras. Cuando Carlos la dé por buena, la ficha y el pitch toman esa corrida.

Si no entra antes de las 8:30 a. m., la ficha tiene un respaldo en la sección 8.3, que sí usa el factor 3. Ese respaldo choca con una regla del pitch. `pitch/CIFRAS_PITCH.md` no dice ninguna cifra de la segunda ronda, «con el +28,6», y `docs/FUENTES.md` (`fuentes-noche`, sección 14) recuerda que el encargo de la noche pide no usar el +28,6 como definitivo. La razón es que la segunda ronda usó las mismas velocidades del modelo y la misma vida útil del huevo que la primera. Si la ficha usa el respaldo, hay que avisarle a Fable, porque la ficha y el pitch citarían corridas distintas. La decisión es de Carlos.

> En 360 jornadas sintéticas sobre la red real de Manizales, con 30 semillas por nivel de carga, DespachoX sube los críticos a tiempo en 12,0, 28,9 y 46,3 puntos frente al despacho por orden de llegada [M].

**Respaldo para el párrafo «Simulación» (línea 40), desde el comienzo hasta antes de «La corrida usó».**

> Con el factor crítico 3 que usa hoy el código, en 360 jornadas sintéticas sobre la red real de Manizales, con 30 semillas nuevas por nivel de carga, DespachoX sube los críticos a tiempo en 10,1, 28,6 y 47,5 puntos frente al despacho por orden de llegada [M]. Ningún intervalo del 95 % toca el cero. El factor 3 se eligió después de ver los datos, porque ningún factor cumplió la regla escrita antes de correr, y por eso se midió en semillas que no intervinieron en la elección. Estos escenarios son algo más chicos que los de la primera corrida, con 49 puntos y 7,5 vehículos en promedio. Frente a un despachador con oficio, la diferencia en críticos no es significativa. DespachoX queda cerca de 2 puntos abajo en el total de entregas a tiempo en carga media y alta, y recorre entre 46,9 y 59,5 km menos por jornada. Los perecederos vencidos quedan en 0,0 %, frente a 1,0 %, 1,8 % y 3,2 % por orden de ingreso, por una regla de bodega que el despachador con oficio también cumple. Priorizar hace esperar al punto peor atendido entre 1,41 y 3,81 horas más que por orden de llegada.

Las 360 jornadas se cuentan como en la primera corrida, con 90 escenarios y las cuatro políticas en cada uno. El resto del párrafo, desde «La corrida usó una media de 39,0 km/h», queda igual, porque la segunda ronda tiene las mismas dos salvedades.

**Respaldo para la tabla de indicadores.** En la fila de entregas a tiempo en puntos críticos dice esto.

> En simulación, 69,1 % por orden de llegada y 98,5 % con un despachador con oficio

Pasa a «En simulación, con carga media, 70,9 % por orden de llegada y 97,8 % con un despachador con oficio». Las dos medias salen de `despacho/sim/resultados_s2/confirmacion_factor_3/resumen.md`, carga media, porque la sección 8.3 solo trae diferencias. En la fila de la espera del punto peor atendido dice esto otro.

> En simulación, 0,93 a 4,25 horas más que por orden de llegada

Pasa a «En simulación, 1,41 a 3,81 horas más que por orden de llegada». Todas las cifras del respaldo salen sin cambios de la sección 8.3 y de ese resumen.

**9. La línea base del recálculo compara cosas distintas.** Los 9 h 46 min miden cuándo apareció el registro oficial de un cierre, y el indicador mide cuánto tarda el despacho en aprobar un plan nuevo.

> Hoy se resuelve por teléfono, sin registro. El día del sismo, el registro oficial del cierre Pereira–Chinchiná apareció 9 h 46 min después del sismo, y 4 h 20 min después de la hora de inicio que guarda el propio registro [F, cálculo nuestro sobre el #767]

**Propuesta.** «Hoy se resuelve por teléfono, sin registro, así que la línea base se mide en el simulacro. Como contexto, el registro oficial del cierre Pereira–Chinchiná apareció 9 h 46 min después del sismo, y 4 h 20 min después de la hora de inicio que guarda el propio registro [F, cálculo nuestro sobre el #767].» La misma salvedad vale para el día 90 del plan y para la propuesta 1 de `docs/PILOTO_TERRITORIOS.md`.

**10. La demo tiene dos instrucciones que no sirven en `main`.** `docs/GUION_DEMO.md` de `main` da como respaldo un comando que no existe.

> Ese comando todavía no existe: está pedido en el encargo A.

La rama `erratas` (`4f5df00`) ya lo reemplaza por el comando `RESPALDO` de la sección «Sin tablero». Si `demo-noche` se fusiona, `python -m demo.correr --sin-pausas --db <base de ensayo>` recorre además el mismo flujo por terminal con el lector por reglas. El comando reinicia la base que se le pase, así que nunca se le debe dar la base que muestra el tablero durante el pitch.

La otra instrucción está en `demo/CHECKLIST.md` (`demo-noche`, `d24cd2d`), paso 4.

> Pulsar «Reiniciar datos de prueba» en el tablero de la nube

Ese botón no está en `main`. Existe desde las 12:57 a. m. en `jacobo-tablero` (`65b3581`), dentro de la pestaña «Bitácora». Si `jacobo-tablero` se fusiona y se despliega antes de la demo, el paso 4 sirve como está. Si no, antes de fusionar `demo-noche` el paso 4 tiene que empezar por el reinicio con `DESPACHOX_REINICIAR=1` en Railway, que hoy figura solo como plan B en la columna «Si falla». Así lo dicen la fila 6 de `ENTREGA.md` y el aviso de Fable de las 12:12 a. m.

**11. El nombre del equipo.** Jacobo y Samuel eligieron «Convite» a las 23:30 y le pidieron a Carlos confirmarlo, y en `torre/CANAL.md` de `origin/main` todavía no hay respuesta. El tablero de `jacobo-tablero` ya dice Convite (canal, 00:48), y el guion de `pitch-noche` trae la variante. La ficha y el informe, en cambio, dicen DespachoX. Un Drive con los dos nombres confunde al jurado, así que el nombre se cambia en todos los documentos a la vez o en ninguno.

**12. La hora del pitch.** `CLAUDE.md` dice 2:00 p. m. y iNNOVO dice 2:30 p. m. (discrepancia D17). `ENTREGA.md` cierra la entrega a la 1:45 p. m., así que sirve con cualquiera de las dos. La hora se confirma en la mesa a las 8:30 a. m.

**13. El tablero que recibe el jurado no pide clave.** La revisión de calidad lo encontró y propone una clave opcional (`docs/QA_NOCHE.md` en `qa-noche`, sección 2.1). `ENTREGA.md` le da al jurado el enlace del tablero de la demo, y la base de la nube es una sola. Una funcionaria de gestión del riesgo preguntará quién puede aprobar un plan en ese tablero. Con `jacobo-tablero` el riesgo crece, porque su botón de reinicio tampoco pide clave. Cualquiera con el enlace podría borrar la base de la demo minutos antes del pitch, y la casilla de confirmación no lo impide. Carlos decide en la mañana si define `DESPACHOX_CLAVE_TABLERO`, y si el jurado recibe el mismo enlace de la demo (`ENTREGA.md`, «Lo que decide Carlos», punto 3).

## 9. Preguntas para Carlos o Fable

1. ¿Cómo se llama el integrante de Ingeniería Industrial? Sin el nombre, la corrección 4 no se puede hacer.
2. ¿Se fusiona `a25` antes de las 8:30 a. m.? De eso dependen las frases de la corrección 3.
3. ¿El informe corto se corrige y se recompila, o se deja fuera del Drive? Trae diez discrepancias en trece pasajes, más las fases, y solo compila el computador de Carlos.
4. ¿La exportación a SUMA entra al plan como entregable del día 90, o sale del informe corto?
5. ¿Convite o DespachoX en los documentos del Drive?
6. ¿Puede el integrante de Ingeniería Industrial avisar en el canal antes de las 10:30 a. m. lo que dijo el Banco, en vez de a las 12:30 p. m.?
7. ¿Quién arregla `entrada/pruebas/conftest.py` para que la variable sin red no tumbe 11 pruebas?
8. ¿La ficha toma la corrida de la rama `simulacion` o el respaldo de la sección 8.3? Si toma el respaldo, ¿cambia la regla del pitch sobre la segunda ronda?
9. ¿Se fusiona `jacobo-tablero` con el botón de reinicio? Si el jurado recibe el enlace del tablero de la demo, ¿se le pone clave antes?

## 10. Lo que esta revisión no cubrió

- No probé el bot ni el tablero de la nube, ni el lector con el modelo. La regla de esta noche prohíbe llamar a Railway, a Telegram y a la API.
- No abrí ninguna fuente externa. Las discrepancias que cito son las de `fuentes-noche`, que vienen de una lectura de máquina.
- No revisé `samuel-bot`, `jacobo-silencio` ni `manuscrito`. De `qa-noche` solo leí la sección 2.1, de `jacobo-tablero` solo el botón de reinicio y de `erratas` solo `docs/GUION_DEMO.md`.
- No revisé la corrida de la rama `simulacion`, ni sus cifras ni su método. Cuando entre a `docs/SIMULACION.md`, cambian las notas de los criterios 2 y 6, y conviene repetir esta revisión.
- De `pitch/CIFRAS_PITCH.md` revisé la versión de tres minutos, las cifras que no se dicen y el orden para verificar.

## 11. Cómo repetir lo medido

Todo corre sin red y sin modelo, con el Python del proyecto (`.venv/bin/python`). Cada bloque empieza en la raíz del clon. Cada ruta entre «<» y «>» es una carpeta aparte, fuera del repositorio. La carpeta `despacho/cache/` está en `.gitignore`, así que `git archive` no la crea. Por eso cada bloque la crea con `mkdir -p` antes de copiar la red vial.

```
# Pruebas, en el clon de la rama n2-jurado (main 7131261)
export DESPACHOX_SIN_RED=1
python -m pytest -q -p no:cacheprovider

# Demo por terminal sobre main, con demo/ de demo-noche, en una copia aparte
git archive HEAD | tar -x -C <copia>
git archive origin/demo-noche demo | tar -x -C <copia>
mkdir -p <copia>/despacho/cache
cp despacho/cache/*.pkl despacho/cache/*.graphml <copia>/despacho/cache/
cd <copia> && DESPACHOX_SIN_RED=1 DESPACHOX_SAL=<sal de prueba> python -m demo.correr --sin-pausas --db <copia>/ensayo.db

# A25: módulo y cobertura, en una copia de la rama a25
git archive origin/a25 | tar -x -C <copia_a25>
mkdir -p <copia_a25>/despacho/cache
cp despacho/cache/*.pkl despacho/cache/*.graphml <copia_a25>/despacho/cache/
cd <copia_a25> && DESPACHOX_SIN_RED=1 python -m pytest -q -p no:cacheprovider despacho
DESPACHOX_SIN_RED=1 python -m despacho.a25 --fecha 2026-11-21

# main con a25, sin tocar ninguna rama: árbol fusionado en seco y copia aparte
arbol=$(git merge-tree --write-tree origin/main origin/a25 | head -1)
git archive $arbol | tar -x -C <copia_fusion>
git archive origin/demo-noche demo | tar -x -C <copia_fusion>
mkdir -p <copia_fusion>/despacho/cache
cp despacho/cache/*.pkl despacho/cache/*.graphml <copia_fusion>/despacho/cache/
cd <copia_fusion> && DESPACHOX_SIN_RED=1 python -m pytest -q -p no:cacheprovider
DESPACHOX_SIN_RED=1 DESPACHOX_A25=1 DESPACHOX_SAL=<sal de prueba> python -m demo.correr --sin-pausas --db <copia_fusion>/ensayo.db
```

Probé los tres bloques entre la 1:19 y la 1:27 a. m. Sin el `mkdir -p`, la copia de la red vial falla. Con él, la demo sobre `main` da 33 de 33 [M]. La rama `a25` sola pasa 117 pruebas de `despacho/`. La fusión pasa 366 en total, 118 de ellas de `despacho/` [M].
