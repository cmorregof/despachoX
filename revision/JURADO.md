# Revisión como jurado · DespachoX

Revisión del agente `n2-jurado` de Noche-2, el sábado 21 de noviembre de 2026, entre las 12:03 y las 12:40 a. m., hora de Colombia. Tres jurados que no vieron el trabajo lo califican con la rúbrica de `CLAUDE.md` y la escala de `docs/ESTRATEGIA.md` (excelente 100 %, sólido 75 %, parcial 50 %, incipiente 25 %, no evidenciado 0 %). Las calificaciones y los puntos que gana cada corrección son juicio de esta revisión, así que van como estimados [E]. Los conteos de pruebas, la demo por terminal y la cobertura del A25 los medí yo sobre copias de las ramas [M]. Nadie del equipo ha leído todavía este documento.

## Resumen

Si se entregara ahora, el trabajo sacaría entre 62,5 y 65 puntos de 100 con estos tres jurados [E]. El prototipo es lo más fuerte, porque corre de punta a punta y la simulación está bien diseñada. Lo más débil son los aliados, que nadie ha confirmado, y el A25, que la ficha llama capacidad principal y que en `main` solo se nombra. Las cifras del problema tienen fuente, pero ninguna la ha abierto una persona. Además, la regla del guion las saca del pitch a la 1:00 p. m. si siguen así.

Estas son las cinco correcciones que más puntos suben por hora de trabajo, en orden. El detalle, con la frase actual y la propuesta, está en la sección 7.

1. Anotar en la ficha y en el guion lo que respondió el Banco a las 8:00 a. m.
2. Subir al Drive el plan de 30 a 90 días y la matriz de riesgos, y enlazarlos en el README.
3. Abrir por persona las cifras que dice el pitch y marcarlas en `docs/FUENTES.md`.
4. Poner nombre al integrante de Ingeniería Industrial y dejar un solo reparto de responsables.
5. Fusionar la rama `a25` antes de las 8:30 a. m. y decir dónde está el A25 en el código, con su límite de cobertura.

Con las cinco y una respuesta del Banco que se pueda citar, el rango sube a entre 71,25 y 81,25 puntos [E]. Sin respuesta del Banco, queda entre 62,5 y 77,5, porque la directora del banco no se mueve con cambios de texto.

## Versiones revisadas

| Rama | Commit | Qué revisé |
|---|---|---|
| `main` | `7131261` en mi clon. `origin/main` está en `6121117`, que solo añade entradas a `torre/CANAL.md` y `torre/RELEVO_NOCHE2.md` | `docs/FICHA_CORTA.md`, `docs/FICHA.md`, `docs/informe/informe_corto.tex` y su PDF, `docs/FUENTES.md`, `docs/SIMULACION.md`, `docs/ESTRATEGIA.md`, `docs/DECISIONES_9PM.md`, `docs/MENTORIA_1.md`, `docs/PILOTO_TERRITORIOS.md`, `docs/GUION_DEMO.md`, `README.md` y el código |
| `pitch-noche` | `6782e4c` (primera lectura en `31a618b`) | `pitch/GUION.md`, `pitch/DIAPOSITIVAS.md` y `pitch/CIFRAS_PITCH.md` |
| `defensa-noche` | `9b85a37` | `docs/PLAN_30_90.md`, `docs/RIESGOS.md` y `pitch/PREGUNTAS_JURADO.md` |
| `fuentes-noche` | `2261013` (primera lectura en `f235cb2`) | `docs/FUENTES.md` (registro consolidado), `ENTREGA.md` y la sección «Para el jurado» de `README.md` |
| `a25` | `b96ff71` (primera lectura en `c5454ba`) | `despacho/a25.py`, sus pruebas, su línea de órdenes y `docs/A25.md` |
| `demo-noche` | `d24cd2d` | Solo `demo/correr.py`, para ensayar la demo por terminal |

Las ramas `pitch-noche` y `defensa-noche` ya existían a las 12:05 a. m., así que esta revisión las incluye. Tres ramas avanzaron mientras escribía, y a las 12:40 a. m. volví a cotejar con su última versión cada frase citada y cada medición. Las cuatro ramas de Fable que revisé (`a25`, `defensa-noche`, `pitch-noche` y `fuentes-noche`) se fusionan sin conflictos con `origin/main`, según `git merge-tree` [M].

## 1. Lo que comprobé, como lo haría un jurado escéptico

Esta sección reúne las comprobaciones que un jurado podría hacer por su cuenta. Cada una dice qué encontré, y la sección 11 dice cómo repetirla.

| Pregunta | Lo que encontré |
|---|---|
| ¿Corren las pruebas? | Con `DESPACHOX_SIN_RED=1`, `python -m pytest -q` da 334 pruebas en verde, 11 fallidas y 1 omitida, de 346, en 44,8 s [M]. Las 11 fallidas están en `entrada/pruebas/`, con 8 en `test_flujo.py`, 2 en `test_escala.py` y 1 en `test_enea.py`. Fallan porque, con esa variable, `Mesa.leer` usa el lector de SMS y salta el extractor falso que inyectan esas pruebas (`entrada/flujo.py`, línea 100). El equipo reporta 345 en verde a las 23:50 (`torre/CANAL.md`), y la cuenta cuadra con 346 menos la omitida. No corrí la suite sin la variable, porque la regla de esta noche lo prohíbe |
| ¿La demo sale como dice el guion? | Sí, con el lector por reglas. `demo/correr.py`, de `demo-noche`, pasa 33 de 33 verificaciones sobre el código de `main` [M]. Da 18 de 18 pedidos y 3 de 3 críticos a tiempo, y el pedido de San José pasa a un campero después del cierre. Los tres planes tardan 3,2, 3,1 y 3,1 s con 3 s de búsqueda. La lectura con el modelo no se probó, porque no hay clave en el entorno |
| ¿Funciona en la nube? | No lo comprobé, porque la regla de esta noche prohíbe llamar a Railway y a Telegram |
| ¿Las cifras tienen fuente? | En `main`, `docs/FUENTES.md` tiene 3 filas. En `fuentes-noche` hay un registro consolidado en 16 secciones. Ninguna cifra está verificada por una persona, y el registro anota 25 discrepancias entre nuestros textos y las fuentes, de D1 a D25 |
| ¿El A25 está en el código? | En `main`, no. Ningún archivo de código lo usa. En la rama `a25` sí, porque `despacho/a25.py` asigna a cada tramo la estación más cercana y, con `DESPACHOX_A25=1`, encarece sin cerrar los tramos en naranja (×2) o roja (×4). Con la rama fusionada sobre `main`, pasan 118 pruebas de `despacho/`, frente a 86 en `main` sola. La suite completa da 366 en verde, las mismas 11 fallidas de `entrada/` y 1 omitida, y la demo pasa 33 de 33 con el gancho apagado y encendido [M] |
| ¿Dónde no sirve el A25? | La línea de órdenes de la rama, con lluvia sintética, deja «fuera de la red» los tramos a más de 3 km de toda estación [M]. Ahí caen las vías con más cierres por ladera según el propio módulo. Son la salida a Letras (87 registros, La Nubia a 10,11 km), la vía a Medellín (35, CHEC-Uribe a 3,31 km), la autopista del Café (6), la vía a Neira (5) y La Siria (3). El límite viene de la distancia a las estaciones, así que no cambia con la lluvia real. `docs/A25.md`, en la rama, ya lo documenta y pide estaciones del SIMAC cerca de esas salidas, pero la ficha y las diapositivas no lo dicen |
| ¿Las otras capacidades UNAL están en el código? | La patente 37476 sí, como factor de 1,2 solo para fruta en un acopio con frío (`despacho/optimizar.py`, línea 54, y `despacho/semilla.py`). Los 22,6 km/h de la tesis de 2019 todavía no, porque `despacho/red.py` usa velocidades supuestas y la corrida nueva no ha llegado |
| ¿El plan tiene responsables y validación? | Sí. `docs/FICHA_CORTA.md` trae cuatro tramos con responsables y validación, con dos filas «por asignar». `docs/PLAN_30_90.md` (`defensa-noche`) trae cinco hitos con criterio para seguir, ajustar o parar. El integrante de Ingeniería Industrial aparece 20 veces en el plan, los riesgos y las preguntas, y nunca con su nombre |
| ¿Los documentos dicen lo mismo? | No del todo. El informe corto trae fases de 1 a 30, 31 a 60 y 61 a 90 días, y la ficha trae 0 a 15, 15 a 30, 30 a 60 y 60 a 90. La ficha pone a Samuel en el acuerdo con el Banco, y la decisión de las 23:01 se lo dio al integrante de Ingeniería Industrial |
| ¿Hay aliados? | No. La ficha dice «Ninguno ha visto todavía la propuesta» |
| ¿Los datos del escenario son los que dice la ficha? | Sí. `datos_publicos/puntos.csv` tiene 50 puntos, 35 de ellos críticos, y `datos_publicos/cierres_historicos.csv` tiene 178 registros [M] |
| ¿Se promete algo que no existe? | Tres cosas. La exportación a SUMA está en el informe corto, y no está en el código ni en el plan. El video de respaldo dice «por grabar». El comando de respaldo de `docs/GUION_DEMO.md`, `entrada.procesar`, no existe. Un cuarto caso, el botón «Reiniciar datos de prueba», ya lo corrigieron `pitch-noche` y `fuentes-noche` (`torre/CANAL.md`, 00:12) |

## 2. Qué califico

Esta revisión califica lo que el jurado tendría a mano si se entregara ahora con el plan de `ENTREGA.md` (rama `fuentes-noche`). Eso es la ficha corta, el anexo y el informe corto en PDF, el repositorio, el tablero, el pitch de `pitch-noche` y las respuestas de `defensa-noche`. `docs/PLAN_30_90.md` y `docs/RIESGOS.md` no están en la lista de lo que se sube, de modo que el jurado solo los oye en las respuestas. La rama `a25` tampoco entra en la nota de hoy, porque su fusión la decide Carlos. Las cifras de simulación son las de la ficha corta, porque la corrida nueva [SIM] no había llegado a las 12:40 a. m.

## 3. Jurado 1 · Profesor de la UNAL

**Quién es.** Es profesor de ingeniería en la Sede Manizales y ha dirigido tesis de ruteo y de logística. Conoce el IDEA y su indicador A25. Lee la ficha con lápiz, abre el repositorio y corre algo si puede. Le importan el método, el uso del conocimiento UNAL y el rigor de las cifras y de la simulación.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Sólido, 15 de 20 | El problema cabe en una frase y repite el entregable de la ficha 04 (`docs/FICHA_CORTA.md`, componente 1). Cada cifra nombra su fuente. El registro de `fuentes-noche` declara 25 discrepancias, y eso habla bien del método (`docs/FUENTES.md`, sección «Discrepancias») | Ninguna cifra la abrió una persona, y el resumen del informe corto lo admite. Seis frases del informe no coinciden con su fuente según la lectura de máquina (D8, D9, D10, D11, D21 y D24; sección 8, corrección 6) |
| 2. Prototipo | Sólido, 18,75 de 25 | El ensayo de la demo pasa 33 de 33 verificaciones sobre `main` (sección 1). El equipo reporta 345 pruebas en verde. La simulación compara cuatro políticas en 360 jornadas con diferencias pareadas (`docs/SIMULACION.md`, sección 5) | El extractor se midió con 15 mensajes escritos por el propio equipo, que dieron 62 de 64 campos. El lector de SMS se midió con 20 casos que no son independientes (`entrada/pruebas/reporte_campos.md` y `entrada/pruebas/reporte_sms.md`). Ningún mensaje viene de un usuario real |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | Los métodos están bien elegidos y declarados. El ruteo tiene capacidad y ventanas de tiempo en OR-Tools, la simulación es de eventos discretos con semillas comunes, y la regla para elegir el peso de los críticos se escribió antes de correr. El equipo reporta que ningún factor la cumplió (`docs/SIMULACION.md`, 8.1 a 8.3). La patente 37476 entra como parámetro (`despacho/optimizar.py`, línea 54) | El A25, que la ficha llama capacidad principal, no aparece en el código de `main`. El factor de 1,2 de la patente tiene un solo respaldo, en gulupa a 8 °C. La velocidad de la tesis de 2019 todavía no entra al código. Ningún profesor de la Sede ha revisado la formulación |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | Cuatro tramos con hito, entregables, responsables, recursos y validación, más una regla de cambio escrita (`docs/FICHA_CORTA.md`, componente 4) | Dos filas dicen «por asignar». El informe corto trae otras fases. El plan detallado de `defensa-noche`, que sí es excelente en estructura, no está en lo que se sube |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | Corre en un portátil con la red vial en disco (`docs/SIN_CONEXION.md`). El costo del simulacro sale de precios con fuente (`datos_publicos/costos.csv`) | Ningún aliado confirmado. El servidor y el plan de SMS están por cotizar, y el costo del modelo es una estimación sin medir (`entrada/ESCALA.md`) |
| 6. Impactos | Parcial, 5 de 10 | Seis indicadores con línea base, meta y forma de verificarlos (`docs/FICHA_CORTA.md`, componente 6) | La magnitud del piloto no tiene número. Las cifras de simulación de la ficha son de la primera corrida, hecha con factor crítico 1, y el código usa el 3 (`despacho/optimizar.py`, línea 50). El número nuevo [SIM] no ha llegado |
| **Total** | **65 de 100** | | |

**Lo que preguntaría.**

- «¿Qué tan lejos del óptimo queda OR-Tools con un segundo de búsqueda?» No hay cota inferior, y la respuesta 14 de `pitch/PREGUNTAS_JURADO.md` lo admite.
- «Si una regla de prioridad empata con el optimizador en críticos, ¿qué aporta el optimizador?» La respuesta está en `docs/SIMULACION.md`, sección 5. DespachoX recorre entre 46,7 y 75,1 km menos por jornada que el despachador con oficio, y recalcular sube los críticos frente a planear una sola vez.
- «Hasta la política ingenua queda bajo el 5 % de desperdicio. ¿Qué mide ese indicador en su simulación?» La sección 7 de `docs/SIMULACION.md` lo reconoce. Los lotes vencen entre 6 y 48 horas, y la rotación por vencimiento basta para dejarlo en 0,0 %.
- «¿Estos números salen del código que tienen hoy?» No del todo, porque la ficha cita la corrida con factor 1 (sección 8, corrección 8).
- «¿En qué línea está el A25?» En `main`, en ninguna.

## 4. Jurado 2 · Directora de operaciones de un banco de alimentos

**Quién es.** Dirige la operación de un banco de alimentos de la red ABACO en otra ciudad. Despacha todos los días a organizaciones inscritas y responde ante los donantes. Se pregunta si esto le sirve el lunes, cuánto le cuesta adoptarlo y qué datos le piden.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Parcial, 10 de 20 | Reconoce el cuello de botella del despacho en los 404.587 kg en acopio frente a 41.163 kg entregados. También reconoce la rutina de organizaciones inscritas que el equipo tomó del banco de Bogotá (`docs/MENTORIA_1.md`) | El equipo no ha hablado con ningún banco. No sabe si el Banco reparte o si las organizaciones recogen, y lo dice (`docs/DECISIONES_9PM.md`, decisión 1). Falta el usuario con nombre y cargo que `docs/ESTRATEGIA.md` pide para el criterio 1 |
| 2. Prototipo | Sólido, 18,75 de 25 | La hoja de ruta impresa trae un QR por paquete (`despacho/hoja.py`). La bodega saca primero lo que vence primero, y cada plan lo aprueba una persona con su nombre. Quien pide no instala nada, porque escribe por Telegram o por SMS | El inventario entra por la semilla o por un CSV que carga el equipo (`docs/PLAN_30_90.md`, día 15). No encontré en `tablero/` una forma de subirlo. WhatsApp queda «para el piloto» (`pitch/PREGUNTAS_JURADO.md`, pregunta 24), pero el plan no le pone hito |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | La vida útil por producto trae fuente, del ICBF, la FDA, el USDA y la FAO (`docs/FICHA.md`, componente 3). El factor del empaque solo cuenta en fruta de un acopio con frío | El A25 no le cambia nada un lunes sin lluvia. El empaque es un supuesto, y ella preguntará si su bodega tiene frío |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | Lo que se le pide está escrito. Son un despachador de contacto, tres datos sin información personal, dos semanas de bitácora y 30 días en paralelo (`docs/FICHA_CORTA.md`, componentes 4 y 5) | No dice cuántas horas por semana le cuesta la bitácora a su despachador, ni quién carga los datos cuando el equipo se vaya |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | El software es abierto y corre en un portátil. Sus datos siguen siendo suyos, y nadie le pide datos de beneficiarios | Falta quién lo sostiene después del día 90. Ese riesgo está en `docs/RIESGOS.md` (R9), que no llega al Drive. Tampoco hay cotización del servidor ni del SMS |
| 6. Impactos | Sólido, 7,5 de 10 | Los indicadores son los que ella ya reporta, como kilos vencidos, entregas confirmadas y kilómetros, y se miden contra su propia línea base. La confirmación de cada entrega le sirve para el reporte al donante | Falta cuántas organizaciones o personas atendería el piloto. La ficha lo deja para los días 0 a 15 |
| **Total** | **62,5 de 100** | | |

**Lo que preguntaría.**

- «¿Cuántas horas de mi despachador cuestan las dos semanas de bitácora?» No hay respuesta escrita.
- «¿Cómo subo mi inventario el lunes, y quién lo actualiza cada día?» Hoy lo carga el equipo desde un CSV.
- «¿Mis organizaciones tienen que aprender Telegram?» La respuesta 24 deja WhatsApp para el piloto, y el plan no le pone fecha.
- «¿Quién lo arregla un domingo?» El riesgo R9 lo reconoce, todavía sin dueño.

## 5. Jurado 3 · Funcionaria de gestión del riesgo

**Quién es.** Trabaja en la oficina de gestión del riesgo de un municipio o de un departamento. Conoce la estrategia de respuesta, el puesto de mando unificado, el RUD y SUMA. Mira si esto encaja con la operación de una emergencia, qué riesgos trae, quién lo avala y cómo sería el piloto.

| Criterio | Nivel y puntos | Evidencia que encuentra | Lo que le falta |
|---|---|---|---|
| 1. Problema y vertical | Sólido, 15 de 20 | El inventario de piezas con dueño, del RUD a SUMA y a la plataforma de ABACO, está en la figura 3 del informe corto. Las vías se cierran también sin sismo, con 87 registros en la salida a Letras, de los que 4 son del sismo (`pitch/GUION.md`, bloque 2) | El informe dice que SUMA «no recibe pedidos», y la página de la OPS dice que los sitios registran solicitudes (D8). Quien usa SUMA lo nota de inmediato |
| 2. Prototipo | Sólido, 18,75 de 25 | Un cierre queda reportado hasta que una persona lo confirma. Hay ruta impresa y SMS leídos por reglas, que responden a la caída del 28 % de las estaciones base de Caldas el 11 de agosto (`docs/FICHA.md`, componente 2; por verificar) | El informe promete exportar a SUMA, y no hay código ni hito para eso. El mapa del tablero todavía necesita internet |
| 3. Conocimiento utilizado | Parcial, 7,5 de 15 | El A25 es el indicador que usa la UGR, y la ficha cita sus umbrales y su origen (`docs/FICHA_CORTA.md`, componente 3) | En `main` el A25 solo se nombra. En la rama `a25` ya corre, pero las vías de acceso con más cierres quedan fuera de la red de estaciones (sección 1) |
| 4. Plan de 30 a 90 días | Sólido, 11,25 de 15 | El plan trae un simulacro con la UGR, un informe al Consejo Municipal de Gestión del Riesgo y un marco legal, la calamidad pública vigente hasta el 9 de agosto de 2027, que sigue por verificar (`docs/FICHA_CORTA.md`, componente 4) | La UGR está «por contactar», y el plan cuenta con horas suyas que nadie ha pedido |
| 5. Viabilidad y aliados | Parcial, 7,5 de 15 | La ficha trae riesgos con mitigación y cumple la Ley 1581 | Ningún padrino confirmado. La matriz de 16 riesgos con señal temprana y responsable existe en `defensa-noche`, pero no llega al Drive |
| 6. Impactos | Parcial, 5 de 10 | Indicadores con línea base y forma de verificarlos | El plan usa como línea base del recálculo los 9 h 46 min que tardó en aparecer el registro oficial de un cierre (`docs/PLAN_30_90.md`, sección 5). Ese número mide cuándo se publicó un registro, y el indicador mide una replanificación. Faltan los beneficiarios del territorio |
| **Total** | **65 de 100** | | |

**Lo que preguntaría.**

- «¿Esto entra a la estrategia municipal de respuesta o corre aparte?» El plan propone un informe al Consejo, sin respuesta de la UGR todavía.
- «¿Exporta a SUMA?» Hoy no.
- «¿Qué pasa si alguien reporta un cierre falso, o si nadie reporta uno real?» El despachador confirma cada cierre, y la simulación no modela cierres falsos ni tardíos (`docs/SIMULACION.md`, sección 7).
- «¿Quién responde si una ruta pasa por una ladera en alerta roja?» Con el A25 encendido el tramo se encarece sin cerrarse, y la ruta la aprueba el despachador.

## 6. Tabla consolidada

La tabla junta las tres notas. Las dos últimas filas estiman la nota con las cinco correcciones de la sección 7, con y sin una respuesta del Banco que se pueda citar [E].

| Criterio | Peso | Académico | Banco | Riesgo | Rango |
|---|---:|---:|---:|---:|---|
| 1. Problema y vertical | 20 | 15,0 | 10,0 | 15,0 | 10,0 a 15,0 |
| 2. Prototipo | 25 | 18,75 | 18,75 | 18,75 | 18,75 |
| 3. Conocimiento utilizado | 15 | 7,5 | 7,5 | 7,5 | 7,5 |
| 4. Plan de 30 a 90 días | 15 | 11,25 | 11,25 | 11,25 | 11,25 |
| 5. Viabilidad y aliados | 15 | 7,5 | 7,5 | 7,5 | 7,5 |
| 6. Impactos | 10 | 5,0 | 7,5 | 5,0 | 5,0 a 7,5 |
| **Total hoy** | **100** | **65,0** | **62,5** | **65,0** | **62,5 a 65,0** |
| Con las cinco y respuesta citable del Banco [E] | | 81,25 | 71,25 | 72,5 | 71,25 a 81,25 |
| Con las cinco y sin respuesta del Banco [E] | | 77,5 | 62,5 | 72,5 | 62,5 a 77,5 |

Los tres jurados coinciden en el prototipo, el conocimiento utilizado, el plan y los aliados. Difieren en el problema y en los impactos, porque la directora del banco pesa más la falta de una conversación con un banco real que la calidad de las fuentes. Por eso la corrección 1 es la única que la mueve. El académico es el que más sube, ya que las cinco correcciones tocan algo que él revisa.

## 7. Las cinco correcciones, por puntos por hora

Los puntos de cada corrección son una estimación de esta revisión [E], promediada entre los tres jurados. El tiempo cuenta solo el trabajo que falta, sin lo que ya está en la agenda, como la llamada de las 8:00 a. m. El orden sigue el punto medio de los puntos por hora.

| # | Corrección | Criterios | Puntos [E] | Tiempo | Puntos por hora, punto medio | Quién, propuesto |
|---|---|---|---|---|---:|---|
| 1 | Anotar lo que respondió el Banco | 5 y 1 | De 0 a 5,4, según la respuesta | 20 min | 8,1 | Integrante de Ingeniería Industrial y Fable |
| 2 | Subir el plan y la matriz de riesgos al Drive, y enlazarlos | 4 y 5 | De 1,25 a 3,75 | 20 min | 7,5 | Fable |
| 3 | Verificar por persona las cifras del pitch | 1 | De 5 a 6,7, contando que sin verificar salen del pitch a la 1:00 p. m. | 60 min | 5,8 | Samuel |
| 4 | Nombrar al integrante de Ingeniería Industrial y dejar un solo reparto | 4 | De 0 a 2,5 | 15 min | 5,0 | Carlos da el nombre y Fable edita |
| 5 | Fusionar `a25` y decir dónde está el A25, con su límite | 3 | 2,5 | 60 min | 2,5 | Carlos decide y Fable fusiona |

### Corrección 1 · Anotar lo que respondió el Banco a las 8:00 a. m.

**Por qué suma.** El criterio 5 pide padrinos, y `docs/ESTRATEGIA.md` pide para el criterio 1 un usuario con nombre y cargo. Hoy la ficha dice que ningún aliado ha visto la propuesta. Una respuesta del Banco, aunque sea un «muéstrenoslo el lunes», sube el criterio 5 de los tres jurados y el criterio 1 de la directora. Si el Banco dice que las organizaciones recogen y nadie reparte, se aplica la regla de cambio y se dice así, porque esa regla ya está escrita.

**Archivo.** `docs/FICHA_CORTA.md` (`main`, `7131261`), componente 5.

**Dice hoy.**

> **Aliados.** Ninguno ha visto todavía la propuesta.

**Propuesta, solo si hubo conversación.**

> **Aliados.** El Banco Arquidiocesano de Alimentos conoció la propuesta el sábado a las [hora], por [llamada o visita], con [cargo]. Los demás aliados todavía no la han visto.

**Dice hoy, en la tabla de aliados.**

> | Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | Llamada el sábado a las 8:00 a. m. |

**Propuesta.**

> | Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | [Cargo] respondió el sábado a las [hora]. [Reparte o recogen.] [Siguiente paso, con fecha] |

**Archivo.** `pitch/GUION.md` (`pitch-noche`, `31a618b`), bloque 7. La frase de reemplazo ya está escrita y solo entra con permiso de la persona.

> Esta mañana se lo mostramos a [cargo] del Banco, que nos dijo: «[frase textual]».»

**Dato que falta y dónde conseguirlo.** Lo trae el integrante de Ingeniería Industrial, con el encargo `encargos/P5_ALIADO_PILOTO.pdf`. Ese encargo fija la entrega a las 12:30 p. m., y `ENTREGA.md` saca el PDF de la ficha a las 12:40. Diez minutos no alcanzan, así que conviene un aviso corto en `torre/CANAL.md` apenas cuelgue, antes de la mentoría 2 de las 10:30 a. m.

### Corrección 2 · Subir el plan de 30 a 90 días y la matriz de riesgos al Drive

**Por qué suma.** Lo mejor del equipo para los criterios 4 y 5 está en `defensa-noche`. El plan tiene cinco hitos con criterio para seguir, ajustar o parar, y la matriz tiene 16 riesgos con señal temprana, mitigación y responsable. La lista de `ENTREGA.md` no los sube, y la sección «Para el jurado» del README no los enlaza. `ENTREGA.md` dice que el jurado califica lo que logra abrir. Primero hay que fusionar `defensa-noche`, que entra sin conflictos.

**Archivo.** `ENTREGA.md` (`fuentes-noche`, `f235cb2`), tabla «Qué se sube».

**Dice hoy.** La tabla termina en la fila 6, que empieza así.

> | 6 | Enlace al tablero y al bot |

**Propuesta.** Añadir una fila después de esa.

> | 7 | Plan de 30 a 90 días y matriz de riesgos, en PDF | `docs/PLAN_30_90.md` y `docs/RIESGOS.md` | Cambiar cada [SIM] por la cifra nueva y poner el nombre del integrante de Ingeniería Industrial | Samuel | Carlos |

**Dice hoy, en el horario.**

> | 12:40 | PDF de la ficha y del anexo, con los comandos de abajo. Se revisa que el anexo no traiga la nota interna | Samuel |

**Propuesta.**

> | 12:40 | PDF de la ficha, del anexo, del plan y de la matriz de riesgos, con los comandos de abajo. Se revisa que el anexo no traiga la nota interna | Samuel |

**Archivo.** `README.md` (`fuentes-noche`), tabla de la sección «Para el jurado». En la columna «Dónde» de estas dos filas, el primer enlace pasa a ser el documento nuevo.

> | 4. Plan de 30 a 90 días | Hitos, responsables, recursos y validación, y los territorios propuestos |

**Propuesta.** Poner `[docs/PLAN_30_90.md](docs/PLAN_30_90.md)` antes de `docs/FICHA.md` en la columna «Dónde».

> | 5. Viabilidad y aliados | Costos, riesgos, operación sin internet y lo que se le pide a cada aliado |

**Propuesta.** Poner `[docs/RIESGOS.md](docs/RIESGOS.md)` antes de `docs/FICHA.md` en la columna «Dónde».

**Archivo.** `docs/FICHA_CORTA.md`, línea 6.

> El anexo técnico, con todas las cifras, supuestos y riesgos, está en `docs/FICHA.md`.

**Propuesta.**

> El anexo técnico está en `docs/FICHA.md`. El plan detallado de 30 a 90 días está en `docs/PLAN_30_90.md`, y la matriz de 16 riesgos, en `docs/RIESGOS.md`.

### Corrección 3 · Abrir por persona las cifras que dice el pitch

**Por qué suma.** El guion trae su propia regla, y esa regla saca las cifras del pitch si nadie las abre.

> Si a la 1:00 p. m. nadie ha abierto la fuente de una cifra con asterisco, esa cifra sale del pitch.

Sin verificación, el pitch pierde a la 1:00 p. m. los 404.587 y 41.163 kg, los 87 registros de Letras y el cierre del RUD, y el criterio 1 cae a parcial. Con verificación, el académico puede darle excelente. `docs/VERIFICAR_SAMUEL.md` (`fuentes-noche`) ya trae las 15 cifras en orden, con enlace y casillas, y `pitch/CIFRAS_PITCH.md` (`pitch-noche`) les da un código. Bastan las cinco que dice la versión de tres minutos.

1. C01. Manizales fue «uno de los principales puntos de acopio» de la red (Noticias RCN, 10 de agosto).
2. C02. 404.587 kg en acopio y 41.163 kg entregados seis días después del sismo (Portafolio, 16 de agosto). El guion de `pitch-noche` ya quitó «en todo el país», que la nota no dice (discrepancia D3).
3. C04. 87 registros de cierre en la salida a Letras desde 2017, 4 de ellos del sismo (registro #767 de INVÍAS y `datos_publicos/cierres_historicos.csv`).
4. C08. El RUD cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas (Vanguardia, 5 de octubre). Según la fila del RUD en el registro de `fuentes-noche`, la nota habla de auxilios económicos y no de comida.
5. C10. El 21 de octubre un deslizamiento dejó a un carril la vía a Pereira y solo pasaban livianos (fila S22 de `datos_publicos/cierres_historicos.csv`, con su consulta al registro #767).

**Archivo.** `docs/FUENTES.md` (`fuentes-noche`), columna «Estado». Quien abra la fuente escribe «Verificada por [nombre], [hora]», como pide la sección «Cómo anotar una verificación».

**Archivo.** `docs/FICHA_CORTA.md`, línea 6.

> Las cifras de fuentes externas están por verificar.

**Propuesta, cuando se hayan abierto.**

> [Nombre] abrió el sábado las fuentes de las cifras que dice el pitch, y su estado está en `docs/FUENTES.md`. Las demás cifras de fuentes externas siguen por verificar.

**Archivo.** `docs/FICHA_CORTA.md`, componente 1. La ficha conserva el «en todo el país» que el guion ya quitó, así que conviene la misma corrección.

> Al sexto día tenía 404.587 kg en acopio y había entregado 41.163 kg en todo el país (Portafolio; por verificar).

**Propuesta.**

> Seis días después del sismo, los bancos de alimentos tenían 404.587 kg en acopio y habían entregado 41.163 kg (Portafolio; por verificar).

**Archivo.** `docs/informe/informe_corto.tex`, resumen. El cambio exige recompilar, y solo compila el computador de Carlos.

> Ninguna cifra de este informe ha sido verificada todavía por una persona del equipo.

**Propuesta.**

> Una persona del equipo verificó el 21 de noviembre las cifras que usa el pitch. Las demás siguen por verificar.

### Corrección 4 · Poner nombre al integrante de Ingeniería Industrial

**Por qué suma.** El criterio 4 pide responsables, y un rol sin nombre se lee como un hueco. `docs/PLAN_30_90.md` nombra el rol 10 veces, `docs/RIESGOS.md` 6 y `pitch/PREGUNTAS_JURADO.md` 4, siempre sin la persona. La ficha corta, además, pone a Samuel en el acuerdo con el Banco, y la decisión de Carlos de las 23:01 se lo dio al integrante de Ingeniería Industrial.

**Archivo.** `docs/PLAN_30_90.md` (`defensa-noche`, `9b85a37`), sección 6.

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

### Corrección 5 · Fusionar `a25` y decir dónde está el A25, con su límite

**Por qué suma.** El criterio 3 mira la identificación, la pertinencia y la aplicación del conocimiento (`docs/ESTRATEGIA.md`, rúbrica). La ficha llama al A25 «capacidad principal» y dice que no está en el código, y un profesor de la UNAL va a preguntar dónde está. La rama `a25` lo implementa, con estaciones y umbrales con fuente, lluvia sintética rotulada y el gancho apagado por defecto. En mi corrida con la última versión de la rama (`b96ff71`), `main` con `a25` fusiona limpio, pasan 366 pruebas y la demo da 33 de 33 con el gancho apagado y encendido [M]. Es código, así que tiene que entrar antes del congelamiento de las 8:30 a. m., y la decisión es de Carlos.

**El límite que hay que decir antes de que lo pregunten.** Las vías de acceso con más cierres por ladera quedan a más de 3 km de toda estación, y el módulo responde «fuera de la red» para ellas. La salida a Letras, con 87 registros, tiene la estación más cercana a 10,11 km. `docs/A25.md` lo dice en su sección 2, pero la ficha y las diapositivas no. Una funcionaria de gestión del riesgo lo va a notar, así que conviene que el equipo lo diga primero.

**Archivo.** `docs/FICHA_CORTA.md`, componente 3.

> Entra en el piloto, en los días 60 a 90, y hoy no está en el código.

**Propuesta, si se fusiona.**

> Ya corre en el código, en `despacho/a25.py`, con lluvia sintética que cada salida rotula como tal. El optimizador lo usa solo con `DESPACHOX_A25=1`, y entonces encarece sin cerrar los tramos en naranja o roja. En los días 60 a 90 del piloto se conecta a los datos diarios del IDEA. Las vías de acceso con más cierres, como la salida a Letras, quedan a más de 3 km de toda estación, así que para ellas el A25 no da alerta.

**Archivo.** `docs/FICHA.md`, componente 3.

> Entra en el piloto, en los días 60 a 90, y no está en el código hoy.

**Propuesta.** La misma de la ficha corta.

**Archivo.** `pitch/DIAPOSITIVAS.md` (`pitch-noche`, `6782e4c`), diapositiva de respaldo A, columna «Estado».

> Hecho en la rama `a25` con lluvia sintética y apagado por defecto; entra a `main` si Carlos lo fusiona. En el piloto, días 60 a 90, con lluvia real

**Propuesta, si se fusiona.**

> En el código con lluvia sintética y apagado por defecto. En el piloto, días 60 a 90, con lluvia real. No cubre cinco vías de acceso, entre ellas las salidas a Letras y a Medellín, que quedan a más de 3 km de toda estación

**Archivo.** `pitch/PREGUNTAS_JURADO.md` (`defensa-noche`), pregunta 13.

> Hoy no está en el código, porque entra en los días 60 a 90 con datos del IDEA, y estamos pidiendo el visto bueno de un profesor del instituto.

**Propuesta.**

> Ya está en el código con lluvia sintética, y en los días 60 a 90 se conecta a los datos diarios del IDEA. Estamos pidiendo el visto bueno de un profesor del instituto.

**Archivo.** `docs/RIESGOS.md` (`defensa-noche`), R12.

> El A25 es la capacidad UNAL principal y hoy no está en el código

**Propuesta.**

> El A25 es la capacidad UNAL principal y ya corre en el código con lluvia sintética

El bloque 7 de `pitch/GUION.md` ya trae la frase condicional para este caso, «La alerta de lluvia A25 del IDEA de la UNAL ya está en el código, por ahora con lluvia de prueba». Si Carlos no fusiona, las frases quedan como están, pero el límite de cobertura igual conviene en la nota del orador de la diapositiva A, porque el jurado puede preguntarlo de todos modos. Si el profesor del IDEA revisa el uso antes del pitch, su visto bueno se anota con su cargo y la hora, y el académico sube el criterio 3 otro nivel.

## 8. Otras correcciones, más pequeñas

Estas correcciones suman menos o dependen de algo que todavía no pasa. Van en el orden en que las haría.

**6. El informe corto contradice la ficha y a sus fuentes.** El informe que se sube al Drive se compiló el viernes a las 18:04, antes de las decisiones de las 9:00 p. m. Sus fases no son las de la ficha, y seis frases no coinciden con su fuente según la lectura de máquina de `fuentes-noche`. Hay dos salidas. Una es corregir estas frases en `docs/informe/informe_corto.tex` y recompilar en el computador de Carlos, en unos 40 minutos. La otra es no subir el informe. Antes de cambiar cada frase, una persona abre la fuente, porque la lectura de máquina puede equivocarse.

| Discrepancia | Dice hoy | Propuesta |
|---|---|---|
| Fases | `\item \textbf{Fases.} Días 1 a 30, el Banco usa la herramienta en paralelo y se mide la línea base. Días 31 a 60, entran las juntas y los reportes viales. Días 61 a 90, simulacro en temporada de lluvias, exportación a SUMA e informe de lecciones.` | `\item \textbf{Fases.} Días 0 a 15, acuerdo y línea base. Días 15 a 30, reconstrucción en frío de un mes de despachos. Días 30 a 60, uso en paralelo, con DespachoX planeando en sombra. Días 60 a 90, simulacro con la UGR, A25 por tramo y decisión escrita del Banco.` La exportación a SUMA queda o sale según decida Carlos (pregunta 4) |
| D11 | `Ese día el Coliseo Mayor seguía como albergue principal \cf{f:censo}.` | `Ese día el Coliseo Mayor seguía como uno de los principales albergues temporales \cf{f:censo}.` |
| D10 | `y desde el 11 de agosto el albergue del Coliseo Mayor dejó de recibir perecederos` | `y desde el 11 de agosto el punto oficial de donaciones, en el Coliseo Menor, dejó de recibir perecederos` |
| D21 | `Al 2 de septiembre llevaba 18.847 unidades entregadas` | `Al 2 de septiembre llevaba 18.847 unidades de ayuda entregadas, entre kits de alimentos, tejas, frazadas, colchonetas y baldes` |
| D24 | `había que llevar el formato azul que entregan los Bomberos después de revisar la vivienda.` | `había que llevar el formato azul que entregan los Bomberos.` El detalle de la vivienda sale de La Patria, que no está en las fuentes del informe |
| D9 | `El Programa Mundial de Alimentos (PMA) entregó efectivo en ciudades de Valle y Risaralda y raciones en especie en zonas remotas` | Según la lectura de máquina, Telesur dice que el PMA «prevé ampliar las transferencias de efectivo» en zonas urbanas de Valle y Risaralda. La frase se ajusta a lo que diga la nota cuando una persona la abra |
| D8 | `pero no recibe pedidos ni planea rutas` | `registra las solicitudes de artículos, pero no planea rutas ni asigna vehículos` |

**7. El conteo de pruebas está viejo en dos lugares.** La ficha corta dice 306 y el README de `fuentes-noche` dice 342 con 3 omitidas. El último conteo del equipo es 345 (23:50), y el conteo se repite después del congelamiento.

> y las 306 pruebas automáticas del repositorio pasan [M].

**Propuesta.** «y en la revisión de [hora] pasaron [N] pruebas automáticas con `python -m pytest -q` [M].»

> En la revisión del viernes a las 11:15 p. m. pasaron 342 y se omitieron 3

**Propuesta.** «En la revisión de [hora] pasaron [N] y se omitieron [K]», con el conteo final. Aparte, conviene que `entrada/pruebas/conftest.py` quite `DESPACHOX_SIN_RED` en las pruebas que inyectan un extractor falso, para que la suite no dependa de esa variable. Es código de `entrada/`, así que lo hace Samuel o quien Fable designe.

**8. La cifra de simulación de la ficha no es la del código de hoy.** La ficha cita la primera corrida, hecha con factor crítico 1 (`docs/SIMULACION.md`, sección 5, commit `d33dd27`), y el código usa el factor 3. Si la corrida nueva [SIM] no llega antes de las 8:30 a. m., la sección 8.3 sí corresponde al código de hoy, con 30 semillas nuevas por nivel de carga.

> En 360 jornadas sintéticas sobre la red real de Manizales, con 30 semillas por nivel de carga, DespachoX sube los críticos a tiempo en 12,0, 28,9 y 46,3 puntos frente al despacho por orden de llegada [M].

**Propuesta de respaldo.** «Con el factor crítico 3 que usa hoy el código, en 30 semillas nuevas por nivel de carga, DespachoX sube los críticos a tiempo en 10,1, 28,6 y 47,5 puntos frente al despacho por orden de llegada [M]. Frente a un despachador con oficio, la diferencia en críticos no es significativa, queda cerca de 2 puntos abajo en el total de entregas a tiempo en carga media y alta, y recorre entre 46,9 y 59,5 km menos por jornada.» Las cifras salen de la tabla de la sección 8.3 sin cambios.

**9. La línea base del recálculo compara cosas distintas.** Los 9 h 46 min miden cuándo apareció el registro oficial de un cierre, y el indicador mide cuánto tarda el despacho en aprobar un plan nuevo.

> Hoy se resuelve por teléfono, sin registro. El día del sismo, el registro oficial del cierre Pereira–Chinchiná apareció 9 h 46 min después [F, cálculo nuestro sobre el #767]

**Propuesta.** «Hoy se resuelve por teléfono, sin registro, así que la línea base se mide en el simulacro. Como contexto, el registro oficial del cierre Pereira–Chinchiná apareció 9 h 46 min después del sismo [F, cálculo nuestro sobre el #767].» La misma salvedad vale para el día 90 del plan y para la propuesta 1 de `docs/PILOTO_TERRITORIOS.md`.

**10. El plan B de la demo cita un comando que no existe.** `docs/GUION_DEMO.md` lo dice en la tabla de fallas.

> Ese comando todavía no existe: está pedido en el encargo A.

Si `demo-noche` se fusiona, `python -m demo.correr --sin-pausas --db <base de ensayo>` recorre el mismo flujo por terminal con el lector por reglas. El comando reinicia la base que se le pase, así que nunca se le debe dar la base que muestra el tablero durante el pitch.

**11. El nombre del equipo.** Jacobo y Samuel eligieron «Convite» a las 23:30 y le pidieron a Carlos confirmarlo, cosa que todavía no ha pasado (`torre/CANAL.md` en `origin/main`). El guion de `pitch-noche` ya trae la variante, mientras que la ficha y el informe dicen DespachoX. Un Drive con los dos nombres confunde al jurado, así que el nombre se cambia en todos los documentos a la vez o en ninguno.

**12. La hora del pitch.** `CLAUDE.md` dice 2:00 p. m. y iNNOVO dice 2:30 p. m. (discrepancia D17). `ENTREGA.md` cierra la entrega a la 1:45 p. m., así que sirve con cualquiera de las dos. La hora se confirma en la mesa a las 8:30 a. m.

**13. El tablero que recibe el jurado no pide clave.** La revisión de calidad lo encontró y propone una clave opcional (`docs/QA_NOCHE.md` en `qa-noche`, sección 2.1, según el aviso de las 00:20 en `torre/CANAL.md`). `ENTREGA.md` le da al jurado el enlace del tablero de la demo, y la base de la nube es una sola. Una funcionaria de gestión del riesgo preguntará quién puede aprobar un plan en ese tablero. Carlos decide en la mañana si define `DESPACHOX_CLAVE_TABLERO`, y si el jurado recibe el mismo enlace de la demo (`ENTREGA.md`, «Lo que decide Carlos», punto 3).

## 9. Preguntas para Carlos o Fable

1. ¿Cómo se llama el integrante de Ingeniería Industrial? Sin el nombre, la corrección 4 no se puede hacer.
2. ¿Se fusiona `a25` antes de las 8:30 a. m.? De eso dependen las frases de la corrección 5.
3. ¿El informe corto se corrige y se recompila, o se deja fuera del Drive? Solo compila el computador de Carlos.
4. ¿La exportación a SUMA entra al plan como entregable del día 90, o sale del informe corto?
5. ¿Convite o DespachoX en los documentos del Drive?
6. ¿Puede el integrante de Ingeniería Industrial avisar en el canal antes de las 10:30 a. m. lo que dijo el Banco, en vez de a las 12:30 p. m.?
7. ¿Quién arregla `entrada/pruebas/conftest.py` para que la variable sin red no tumbe 11 pruebas?

## 10. Lo que esta revisión no cubrió

- No probé el bot ni el tablero de la nube, ni el lector con el modelo. La regla de esta noche prohíbe llamar a Railway, a Telegram y a la API.
- No abrí ninguna fuente externa. Las discrepancias que cito son las de `fuentes-noche`, que vienen de una lectura de máquina.
- No revisé `qa-noche`, `samuel-bot`, `jacobo-silencio` ni `manuscrito`, que apareció en el remoto después de las 12:08 a. m. (`4aa2058`).
- La corrida nueva de la simulación [SIM] no había llegado. Cuando llegue, cambian las notas de los criterios 2 y 6, y conviene repetir esta revisión.
- De `pitch/CIFRAS_PITCH.md`, que llegó a `pitch-noche` mientras escribía, solo revisé las filas de las cinco cifras de la corrección 3.

## 11. Cómo repetir lo medido

Todo corre sin red y sin modelo, con el Python del proyecto (`.venv/bin/python`). Cada ruta entre «<» y «>» es una carpeta aparte, fuera del repositorio. La carpeta `despacho/cache/` se copia a mano, porque git no la lleva.

```
# Pruebas, en el clon de la rama n2-jurado (main 7131261)
export DESPACHOX_SIN_RED=1
python -m pytest -q -p no:cacheprovider

# Demo por terminal sobre main, con demo/ de demo-noche, en una copia aparte
git archive HEAD | tar -x -C <copia>
git archive origin/demo-noche demo | tar -x -C <copia>
cp despacho/cache/*.pkl despacho/cache/*.graphml <copia>/despacho/cache/
cd <copia> && DESPACHOX_SIN_RED=1 DESPACHOX_SAL=<sal de prueba> python -m demo.correr --sin-pausas --db <copia>/ensayo.db

# A25: módulo y cobertura, en una copia de la rama a25 (con despacho/cache/ copiada)
git archive origin/a25 | tar -x -C <copia_a25>
cd <copia_a25> && DESPACHOX_SIN_RED=1 python -m pytest -q -p no:cacheprovider despacho
DESPACHOX_SIN_RED=1 python -m despacho.a25 --fecha 2026-11-21

# main con a25, sin tocar ninguna rama: árbol fusionado en seco y copia aparte
arbol=$(git merge-tree --write-tree origin/main origin/a25 | head -1)
git archive $arbol | tar -x -C <copia_fusion>
git archive origin/demo-noche demo | tar -x -C <copia_fusion>
cd <copia_fusion> && DESPACHOX_SIN_RED=1 python -m pytest -q -p no:cacheprovider
DESPACHOX_SIN_RED=1 DESPACHOX_A25=1 DESPACHOX_SAL=<sal de prueba> python -m demo.correr --sin-pausas --db <copia_fusion>/ensayo.db
```
