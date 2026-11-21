# Tres jurados Fable sobre el `main` del mediodía

**Documento interno. No se fusiona a `main` antes del pitch.** Como `revision/JURADO.md`, trae la nota que se pone el propio equipo en un repositorio público, así que se queda en la rama `n2-jurado`.

Tres jurados simulados con el modelo Fable calificaron `main` en `bdcea1c`, el commit de las 11:41 a. m., y un verificador independiente repitió sus pruebas y cotejó cada hecho y cada frase citada. Las notas de este archivo ya traen sus ajustes. Desde ese commit, `main` llegó a `f5d5bbc` y solo cambiaron `figuras_pitch/` (los mapas del piloto en P2) y `torre/CANAL.md` [M], así que las notas valen para el `main` de ahora. La síntesis la escribió el agente de Noche-2 desde las 12:15 p. m., y su hora de cierre es la del commit. Todo puntaje es estimado [E], y lo medido lleva [M].

## 1. Resumen

Sobre el `main` de las 11:41 a. m., los tres jurados Fable dan 71,25, 68,75 y 71,25 puntos después del cotejo, con un promedio de 70,4 [E]. Frente a la madrugada, cada uno sube 6,25 puntos sobre los 65, 62,5 y 65 de las 2:00 a. m., y el promedio queda cerca de los 70,8 que se proyectaban con todo fusionado y citado (75, 65 y 72,5), aunque repartido de otra forma. La subida común es el criterio 3, que pasa de parcial a sólido con los tres porque el A25 ya corre en el código de `main` y la simulación usa las velocidades de la tesis UNAL. El escenario de 87,5, 76,25 y 77,5 no llega, porque el repositorio no registra ninguna respuesta del Banco ni del IDEA, y por eso los aliados siguen en parcial con los tres. Las cinco correcciones de la sección 3 toman unos 45 minutos, y los jurados que las piden les calculan unos 5,5 puntos de promedio, que con la escala por niveles solo se cobran si algún criterio sube de nivel.

## 2. Tabla consolidada

La tabla da el nivel y los puntos de cada jurado después del cotejo. Entre paréntesis va lo que había puesto el jurado cuando no correspondía a la escala, que tiene cinco niveles (excelente 100 %, sólido 75 %, parcial 50 %, incipiente 25 % y no evidenciado 0 %). Por eso los 20, 21, 12, 9,4, 9 y 6 puntos de dos jurados no caben en ella, y el verificador los llevó al nivel que el propio jurado había escrito, sin cambiar ningún nivel. La última columna es la ronda de las 2:00 a. m., en el orden académico, directora y funcionaria.

| Criterio | Peso | Académico de la UNAL | Directora de un banco de alimentos | Funcionaria de gestión del riesgo | Promedio | 2:00 a. m., con Opus |
|---|---:|---|---|---|---:|---|
| 1. Problema y vertical | 20 | Sólido, 15 | Sólido, 15 | Sólido, 15 | 15,0 | 15 · 10 · 15 |
| 2. Prototipo | 25 | Sólido, 18,75 (puso 20) | Sólido, 18,75 (puso 21) | Sólido, 18,75 | 18,75 | 18,75 · 18,75 · 18,75 |
| 3. Conocimiento utilizado | 15 | Sólido, 11,25 | Sólido, 11,25 (puso 12) | Sólido, 11,25 | 11,25 | 7,5 · 7,5 · 7,5 |
| 4. Plan de 30 a 90 días | 15 | Sólido, 11,25 | Sólido, 11,25 | Sólido, 11,25 | 11,25 | 11,25 · 11,25 · 11,25 |
| 5. Viabilidad y aliados | 15 | Parcial, 7,5 (puso 9,4) | Parcial, 7,5 (puso 9) | Parcial, 7,5 | 7,5 | 7,5 · 7,5 · 7,5 |
| 6. Impactos | 10 | Sólido, 7,5 | Parcial, 5 (puso 6) | Sólido, 7,5 | 6,67 | 5 · 7,5 · 5 |
| **Total cotejado** | **100** | **71,25** | **68,75** | **71,25** | **70,4** | **65 · 62,5 · 65** |
| Total que dio el jurado | | 74,4 | 74,25 | 71,25 | 73,3 | |

**Qué subió desde la madrugada.** El criterio 3 pasa de parcial a sólido con los tres. A las 2:00 a. m. el A25 solo se nombraba en `main`. Hoy `despacho/a25.py` calcula el nivel de alerta por estación, `despacho/optimizar.py` (líneas 419 a 434) mete ese costo en el solver, y la sección 9 de `docs/SIMULACION.md` corre con las velocidades de la tesis UNAL de 2019. El académico y la funcionaria suben además el impacto, porque la sección 9 reemplazó la primera corrida y reporta también lo que empeora, ya que el punto peor atendido espera de 1,95 a 3,82 horas más que por orden de llegada. La directora sube el problema a sólido, porque ya ve un usuario con nombre y cifras con su fuente y su tipo. En cambio, baja el impacto a parcial, porque la magnitud del piloto sigue sin número, la ficha no usa el dato del propio Banco y el 0,0 % de vencidos sale de una regla de bodega que un despachador cuidadoso ya cumple.

**Frente a la proyección de las 4:40.** Con todo fusionado y citado, esa ronda esperaba 75, 65 y 72,5. El académico queda 3,75 puntos abajo, porque su plan de 30 a 90 días no llegó a excelente. La directora queda 3,75 arriba, porque sube el problema entero y le cuenta el A25, que la proyección no le daba, aunque baja el impacto. La funcionaria queda 1,25 abajo, porque sus aliados siguen en parcial, y en cambio sube el impacto.

**Qué no se movió.** El prototipo sigue en sólido con los tres, y corre de punta a punta. El académico repitió en una base temporal la demo por terminal de `docs/GUION_DEMO.md` (línea 156), y el recálculo tardó 4,3 s y pasó el pedido 21 del Camión 1 al Campero 1 [M]. Para el excelente le falta lo que se ve en la sala, porque el pitch nuevo cambió la demo en vivo por un video que el repositorio no muestra y, según `ENTREGA.md`, el tablero de la nube pide una clave que el jurado no recibe. El plan sigue en sólido porque descansa en un aliado que no ha dicho que sí, con recursos sin monto y dos responsables «por asignar» en la ficha corta. Los aliados siguen en parcial, porque no hay padrino ni patrocinador, la ficha dice «Ninguno ha visto todavía la propuesta» y el canal no registra qué pasó con la llamada de las 8:00 a. m.

**Lo que corrigió el verificador.** Ningún hecho falso cambió un nivel, aunque varios matices importan para las respuestas.

- **Pruebas.** Con `DESPACHOX_SIN_RED=1` pasan 555, fallan 13, se omite 1 y 24 son fallas esperadas [M]. Las 13 están en cinco archivos de `entrada/pruebas/` y salen de la variable, porque sin ella esos archivos pasan 67 de 67 [M]. La ficha corta (línea 26) y `README.md` (línea 17) todavía dicen 530.
- **Académico.** Contó 25 discrepancias en `docs/FUENTES.md`, y son 26, de D1 a D26. También escribió que el A25 solo está en la ficha, pero `pitch/DIAPOSITIVAS.md` lo trae en la diapositiva 7 y en la de respaldo A. Lo que sí es cierto es que el texto que se dice en voz no lo nombra.
- **Directora.** Propuso decir «la red nacional», y el verificador descartó esa corrección porque la nota de Portafolio no lo dice (D3). Además escribió que la ventaja sobre el despachador con oficio aparece solo con carga alta. Con las velocidades de la tesis también aparece con carga media (3,7 puntos) y holgada (1,5), y solo con carga alta se sostiene con las dos velocidades, que es la razón para decirla solo ahí.
- **Funcionaria.** Escribió que el ruteo está medido con 25 pedidos, y la simulación rutea 100, 125 y 149 por jornada. Lo que `main` no ha medido son miles. También escribió que el informe para el Consejo Municipal no tiene dueño. En `docs/PLAN_30_90.md` lo escribe José Manuel, y la ficha corta dice «por asignar», así que la ficha y el plan no coinciden.
- **Clave del tablero.** `README.md` y `ENTREGA.md` dicen que el tablero de la nube pide clave. El canal de las 9:36 a. m. dice que Fable lo abrió y no la pidió, porque `DESPACHOX_CLAVE_TABLERO` no estaba definida en Railway. Nadie lo ha comprobado después.

## 3. Las cinco correcciones que más puntos dan por minuto

Las correcciones salen de las catorce que el verificador dio por válidas. Varias tocaban la misma frase, así que las junté, y cada una trae los puntos que estimó cada jurado que la pidió. El orden sigue esos puntos sumados por minuto de trabajo, que es el mismo orden de su efecto en el promedio de los tres. Con la escala por niveles, un criterio sube 3,75 o 5 puntos de una vez, o no sube, así que estas cifras sirven para ordenar y no se suman a la nota.

Tres horas mandan sobre este trabajo. La ficha corta sale en PDF a las 12:40 (`ENTREGA.md`, línea 40), y por eso las correcciones 2 y 4 entran antes de esa hora o no entran. A la 1:00 p. m. sale del pitch toda cifra con asterisco cuya fuente nadie abrió (`pitch/PITCH_VENTA.md`, línea 14), y eso toca la corrección 5. Desde la 1:30 hasta las 3:30 p. m. no se empuja (canal, 11:40 a. m.). La ficha la ajusta Samuel con Carlos (`ENTREGA.md`, línea 39) y el pitch es de Fable. Además, la corrección 1 la decide Carlos, y la 2 solo la puede escribir quien sepa qué pasó con la llamada al Banco.

| # | Corrección | Archivo | Jurados que la piden [E] | Efecto en el promedio [E] | Minutos | Hora límite |
|---|---|---|---|---:|---:|---|
| 1 | La comparación con el despachador con oficio, en voz | `pitch/PITCH_VENTA.md`, línea 38 | Académico +1; directora +1,5 | +0,83 | 5 | Antes del ensayo; decide Carlos |
| 2 | Lo que pasó con la llamada al Banco | `docs/FICHA_CORTA.md`, líneas 85 y 89 | Académico +1,5; directora +1; funcionaria +2 | +1,5 | 10 | 12:40 |
| 3 | La UNAL y el A25 en voz, y la UGR como lo que se le pide | `pitch/PITCH_VENTA.md`, línea 42 | Académico +1,9; funcionaria +2 | +1,3 | 10 | Antes del ensayo |
| 4 | La magnitud con el dato del propio Banco | `docs/FICHA_CORTA.md`, línea 99 | Directora +1,5; funcionaria +1,5 | +1,0 | 10 | 12:40 |
| 5 | El bloque 1 ya aprobado y la nota de Portafolio abierta | `pitch/PITCH_VENTA.md`, línea 18 | Académico +1,5; funcionaria +1 | +0,83 | 10 | 1:00 p. m. |

Las tres del pitch (1, 3 y 5) le añaden entre 60 y 75 palabras a un texto de unas 400, según la versión del bloque 1. El primer corte que prevé el archivo (línea 84) es el párrafo de «Piensen en quien despacha», que tiene 37 palabras si sale entero. El resto lo decide un ensayo cronometrado, que el repositorio todavía no registra.

### 1 · La comparación con el despachador con oficio, en voz

El 40,5 % del bloque 4 compara contra el despacho por orden de llegada, que nadie con oficio usa, y por eso el académico y la directora lo preguntan primero. La frase que se añade es la de la fila C16 de `pitch/CIFRAS_PITCH.md` y de la nota de la pregunta 11, sin su comienzo («En simulación, con carga alta y 30 jornadas por política»), porque la primera frase del bloque ya lo dice. Decirla en voz cambia la decisión de Carlos de las 8:21 a. m., que la dejó para la diapositiva de respaldo C y las respuestas (`pitch/GUION.md`, línea 182), así que la decide él.

Frase actual:

> Si se despacha por orden de llegada, el 40,5 % de los pedidos críticos llega a tiempo. Con Convite llega el 98,4 %.

Frase propuesta:

> Si se despacha por orden de llegada, el 40,5 % de los pedidos críticos llega a tiempo. Con Convite llega el 98,4 %. Frente a un despachador con oficio, Convite entrega a tiempo entre 2,8 y 6,5 puntos más de pedidos críticos, según la velocidad que se suponga en las vías.

La directora pidió también los kilómetros. Con carga alta, Convite recorre 42,2 km menos por jornada con las velocidades de la tesis y 44,6 con las del modelo (`docs/SIMULACION.md`, 9.7, punto 6), y caben si el ensayo deja tiempo. La sección 9.7 no deja decir que Convite supera a un despachador humano, porque el despachador con oficio de la simulación es una regla que escribió el equipo, con toda la información a la vista. Esa es la respuesta si alguien pregunta quién es ese despachador.

### 2 · Lo que pasó con la llamada al Banco

A mediodía, la ficha todavía tiene como estado del Banco «Llamada el sábado a las 8:00 a. m.», y eso se lee como que nadie llamó. Los tres jurados lo marcan. El canal no registra la llamada ni su resultado, y la pregunta 23 de `pitch/PREGUNTAS_JURADO.md` da por hecho que José Manuel llamó, así que esta corrección no se puede escribir desde el repositorio. La escribe quien sepa qué pasó, y si nadie contestó, la ficha dice eso.

Frase actual, en la línea 85:

> **Aliados.** Ninguno ha visto todavía la propuesta.

Y en la tabla, línea 89:

`| Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | Llamada el sábado a las 8:00 a. m. |`

Frase propuesta para la línea 85:

> **Aliados.** Ninguno ha confirmado todavía. [Qué pasó con la llamada de las 8:00 a. m. al Banco, tal cual: quién llamó, con quién habló y con qué cargo, y qué respondió. Si nadie contestó, se escribe así.] En su informe de gestión 2025, el Banco pone como reto de 2026 fortalecer la logística para reducir el desperdicio, asegurar la trazabilidad y optimizar la distribución (por verificar).

Y para la tabla:

`| Banco Arquidiocesano de Alimentos | Un despachador, los tres datos y 30 días en paralelo | [Resultado de la llamada, con la hora] |`

El reto de 2026 lo propuso la funcionaria, porque es el propio Banco el que dice que su reto es la logística y la ficha no lo cita. Está en `aliados/DIRECTORIO.md`, línea 37, y necesita su fila en `docs/FUENTES.md` con el enlace del informe que trae la línea 34 del directorio. Con la misma respuesta se llenan las marcas [P5] de las preguntas 4 y 23. Si el Banco dijo que sí, la primera frase cambia por lo que dijo.

### 3 · La UNAL y el A25 en voz, y la UGR como lo que se le pide

En los tres minutos no se oye UNAL, IDEA ni A25, así que el criterio 3 depende de que el jurado lea la ficha o pida la diapositiva de respaldo A. La misma frase promete además que el piloto va «con la Unidad de Gestión del Riesgo», que la ficha corta tiene «Por contactar» (línea 90). La corrección junta las propuestas del académico y de la funcionaria sobre esa frase.

Frase actual:

> Esto se queda en Manizales. El piloto dura 90 días en la rutina del Banco Arquidiocesano de Alimentos, con la Unidad de Gestión del Riesgo.

Frase propuesta:

> Esto se queda en Manizales. Proponemos un piloto de 90 días en la rutina del Banco Arquidiocesano de Alimentos. A la Unidad de Gestión del Riesgo le pedimos el aval y un simulacro. La alerta de lluvia A25 del IDEA de la UNAL ya está en el código, por ahora con lluvia de prueba.

La última frase es la fila C19 de `pitch/CIFRAS_PITCH.md`, que ya estaba aprobada y no lleva asterisco porque no dice cifras. Tampoco dice que el IDEA avaló ese uso, porque no lo ha hecho. Lo que se le pide a la UGR sale de la ficha corta. El académico propuso añadir «y la simulación usa las velocidades de una tesis de la Sede», que entra si el ensayo deja tiempo.

### 4 · La magnitud con el dato del propio Banco

Para la directora y la funcionaria, el impacto queda sin magnitud local mientras la ficha diga que la medirá después, y el repositorio ya tiene un dato del Banco que la ficha no usa.

Frase actual:

> En los días 0 a 15 medimos cuántas personas atiende el Banco en el territorio del piloto.

Frase propuesta:

> En 2025 el Banco Arquidiocesano entregó 364 toneladas y atendió 156 organizaciones (informe de gestión 2025 del Banco; por verificar). En los días 0 a 15 medimos cuántas de esas organizaciones y cuántas personas están en el territorio del piloto.

Las cifras están en `aliados/DIRECTORIO.md`, línea 34, con el enlace al informe, y no tienen fila en `docs/FUENTES.md`. Por eso la corrección incluye esa fila y una línea en la tabla «Cifras usadas» de la ficha. No se dice «351 t rescatadas», porque el informe cuenta 48 t compradas dentro de las 351 recibidas (línea 35 del directorio). La directora propuso añadir que la fruta y la verdura fueron el 30 % de las salidas, un dato de la misma línea que le da contexto al indicador de perecederos.

### 5 · El bloque 1 ya aprobado, y la nota de Portafolio abierta antes de la 1:00 p. m.

La frase de apertura pega a «Manizales» una cifra de los bancos de alimentos que el propio guion no le atribuye a la ciudad, y deja fuera las 157 toneladas que iban en camino. La propuesta es el bloque 1 de `pitch/GUION.md` (línea 53), que ya estaba aprobado con las filas C01 y C02 de `pitch/CIFRAS_PITCH.md`.

Frase actual:

> Después del sismo, la comida llegó a Manizales. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y habían entregado 41*.

Frase propuesta:

> Después del sismo, Manizales fue uno de los principales puntos de acopio de la red de bancos de alimentos*. La comida llegó. Lo que se atascó fue despacharla. Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y 157 en camino. Habían entregado 41*.

Esta corrección tiene su propia hora límite. La línea 14 del pitch saca a la 1:00 p. m. toda cifra con asterisco cuya fuente nadie haya abierto, y la cifra de apertura es una de ellas. Por eso una persona abre la nota de Portafolio, cuyo enlace está en la fila C02, y anota «Verificada por <nombre>, <hora>» en `docs/FUENTES.md` y en esa fila. Si no alcanza a abrir también la nota de Noticias RCN de la fila C01, la primera frase queda «Después del sismo, la comida llegó a la región», como en la ficha corta (línea 10). La directora va más lejos, porque para ella 404 toneladas en acopio y 157 en camino al sexto día pueden ser una operación normal. Decir las 157 no responde esa objeción, pero deja la cifra completa y evita que se oiga como cifra de Manizales.

### Después de las cinco

Vienen tres más, con menos puntos por minuto. El académico pide decir en voz que la prueba de 15.000 mensajes fue en un portátil y con un lector simulado (+0,6, 3 minutos), y de paso cambiar las 530 pruebas de la ficha corta por las 555 de hoy. La directora pide que el bloque 5 diga que el Banco todavía no ha dicho que sí y qué pasa si no reparte (+1, 5 minutos), aunque esa frase depende de la misma llamada que la corrección 2. La funcionaria pide que una persona abra las cinco primeras cifras de `docs/VERIFICAR_SAMUEL.md` y las marque como verificadas (+2,5, 25 minutos). Es la que más puntos da sola, pero toma 25 minutos.

### Una más, que ningún jurado vio

El bot de `main` le dice a quien escribe /start «No guardo su nombre ni su teléfono: solo qué necesita y dónde» (`entrada/flujo.py`, línea 60). H6 contradice esa frase, y el canal de las 6:25 a. m. pidió que nadie la dijera mientras H6 siguiera abierto. La ficha corta invita al jurado a escribirle al bot (línea 34), así que si la nube corre `main`, el jurado la lee en la primera respuesta. La rama `samuel-bot` ya cambia ese texto y trae el plan A de H6 (`d53cc23` y `019dd03`, de las 9:57 y las 11:18 a. m.), y su canal de las 10:20 a. m. pide fusionarla y reiniciar el bot antes de que el jurado escriba. En una prueba con `git merge-tree`, su código entra a `main` sin choques y solo choca `torre/CANAL.md`, que se resuelve conservando las dos entradas [M]. Fusionarla después del congelamiento lo decide Carlos, y tendría que ser antes de la 1:30 p. m. Si entra, hay que repetir la demo, porque con el plan A el pin que fija un conductor tampoco se le ofrece al siguiente hasta que el despachador lo valide.

## 4. Las cinco preguntas más difíciles

Las nueve preguntas de los jurados se reducen a siete, porque dos pares se repiten. Estas cinco son las que más pueden costar, porque el repositorio no tiene la respuesta completa o porque la respuesta honesta obliga a admitir un hueco.

**1. «¿Ya hablaron con el Banco Arquidiocesano? ¿Reparte con vehículos o las organizaciones recogen en la bodega? Si recogen, no hay rutas que optimizar.»** (La directora y el académico.)

A medias. Las preguntas 4 y 23 de `pitch/PREGUNTAS_JURADO.md` dicen que el Banco no lo ha confirmado y dejan la marca [P5] para su respuesta, que nadie ha llenado. La 23 da por hecho que José Manuel llamó esta mañana, pero el canal no lo registra. Sobre quién transporta, `aliados/DIRECTORIO.md` (línea 36) cita el informe de gestión 2025, según el cual el Banco reparte con un cronograma fijo por medio de parroquias, comedores, fundaciones y organizaciones sociales. El informe no dice quién lleva la comida. Lo que sostiene la respuesta es la regla de cambio de la ficha corta (línea 64), según la cual, si el Banco confirma que las organizaciones recogen en la bodega, el piloto pasa al flujo de requerimientos de la UGR y la Gobernación.

**2. «Nadie despacha por orden de llegada. Frente a un despachador con oficio, ¿cuánto ganan, con qué intervalo, y por qué el producto planea con 40 km/h si la simulación usa las velocidades de la tesis?»** (El académico y la directora.)

Existe y está escrita, en la pregunta 11 con su nota y en `docs/SIMULACION.md`, secciones 9.3, 9.6 y 9.7. En simulación, con carga alta y 30 jornadas por política, Convite entrega a tiempo entre 2,8 [0,8; 4,7] y 6,5 [4,4; 8,7] puntos más de pedidos críticos que el despachador con oficio, según la velocidad que se suponga. Con carga media y holgada el pitch no lo afirma. Con las velocidades de la tesis, Convite recorre de 42,2 a 56,0 km menos por jornada. En el total de entregas a tiempo, con esas velocidades empata con carga holgada y media y gana 3,0 [0,7; 5,3] puntos con carga alta, mientras que con las velocidades del modelo queda 0,8, 2,6 y 2,7 puntos debajo (9.7, punto 7). El 0,0 % de vencidos lo logra también el despachador con oficio, que es una regla escrita por el equipo con toda la información a la vista. Sobre la velocidad, el producto sigue con las del modelo (`despacho/red.py`, líneas 36 a 44, con `primary` a 40 km/h), y la nota de la pregunta 11 dice que pasarle las de la tesis es trabajo del piloto.

**3. «Dicen que el A25 del IDEA es su capacidad UNAL principal. ¿Con qué lluvia corre hoy, de dónde salen los factores ×2 y ×4, quién del IDEA lo revisó y cuánto cambia un plan cuando lo encienden?»** (El académico.)

A medias. El A25 sí entra al costo del solver (`despacho/a25.py`; `despacho/optimizar.py`, líneas 419 a 434), y `despacho/tests/test_a25.py` reproduce los 36 valores publicados de la estación Chec-Uribe en el reporte de 2020 (`docs/FUENTES.md`, línea 134). Sin embargo, corre con lluvia sintética y apagado por defecto. Los factores ×2 y ×4 y la cobertura de 3 km son supuestos hasta calibrarlos con el IDEA (`docs/A25.md`, sección 7), y nadie del IDEA lo ha revisado, porque su estado sigue «En gestión» (ficha corta, línea 93; `docs/RIESGOS.md`, R12). Del efecto solo hay una demostración con lluvia sintética, en la que las rutas dejaron los 2,3 km de la avenida Kevin Ángel en alerta roja y tardaron 3,7 minutos más en total (`docs/A25.md`, sección 8). La salida del programa avisa que esa demostración muestra el mecanismo y no mide un impacto. Queda además una repregunta difícil, porque la estación más cercana a la salida a Letras, el ejemplo de la ficha de una vía que se cierra, está a 10,1 km, así que esa salida queda fuera de la red del A25 (`docs/A25.md`, línea 28).

**4. «El lunes, ¿qué me cuesta? ¿Cuántas horas de mi despachador, quién paga el servidor y los SMS, y quién me responde el día 91?»** (La directora.)

Parcial. Los datos que se le piden al Banco están claros (catálogo de puntos, inventario con vencimientos y un mes de despachos, sin datos personales; ficha corta, componente 5). El único gasto en efectivo estimado son los vehículos del simulacro, entre 718.800 y 3.112.353 COP a precios de 2019 y 2021 [E], y leer 10.000 mensajes costaría entre 1,75 y 4,50 USD [E] (pregunta 25). Para después del día 90, la pregunta 26 y el riesgo R9 proponen un portátil del acopio con software abierto, en manos del Banco y de la UGR, y nadie lo ha aceptado. No hay respuesta en el repositorio para las horas por semana del despachador ni para quién paga el servidor y los SMS, que siguen «por cotizar».

**5. «¿Con quién de la Unidad de Gestión del Riesgo hablaron? ¿Dónde encaja la mesa en la estrategia municipal de respuesta, y con qué autoridad un despachador del Banco confirma el cierre de una vía?»** (La funcionaria.)

Solo en parte. La UGR está «Por contactar» (ficha corta, línea 90), y se le pide aval, la fecha del próximo simulacro y reportes de cierres. `docs/FICHA.md` (línea 170) pide ese aval «dentro de la estrategia municipal de respuesta», y `docs/investigacion/10_problema_usuarios_alternativas.md` identifica la EMRE de Manizales (Decreto 416 de 2016, sin consultar su texto). No hay respuesta en el repositorio sobre dónde encaja la mesa en la EMRE ni sobre quién tiene autoridad para confirmar un cierre. Lo único escrito es que un cierre reportado no cambia el plan hasta que el despachador lo confirma. La funcionaria sugiere decir que esa confirmación es una decisión de ruteo del Banco y que en el piloto la fuente oficial de cierres sería la UGR. Esa frase no está en el repositorio, así que la aprueba Carlos antes de decirla.

Las otras dos preguntas tienen respuesta escrita y se pueden ensayar. Para la de sin internet, `docs/SIN_CONEXION.md` y la ficha corta dicen qué funciona y qué falta probar con el wifi apagado y un celular real. Para la de datos personales, `docs/PRIVACIDAD.md` (sección 1) trae una respuesta de 85 palabras, pero H6 obliga a admitir que el texto libre de un pin queda como un lugar que se les ofrece a otros, y el bot de `main` dice lo contrario en su primer mensaje.

## 5. Lo que preocupa del pitch de tres minutos

Los tres jurados ven el mismo problema de fondo. El pitch se reescribió a las 11:50 a. m. y el resto del material no lo siguió, así que, como dice la directora, el relato ganó claridad y perdió evidencia que califica.

La demostración es lo más delicado. El texto nuevo cambia la demo en vivo, que el académico repitió y funciona, por un video mudo de fondo, y el repositorio no muestra que ese video exista (`docs/FICHA.md`, línea 66, sigue en «[Pendiente: lo graba Jacobo…]»). Si a la hora del pitch no hay video, el criterio 2, de 25 puntos, se queda sin nada que se vea correr. La salida está escrita en dos versiones, la demo en vivo del bloque 5 de `pitch/GUION.md`, que sí está ensayada, y la demo por terminal de `docs/GUION_DEMO.md` (línea 156). El guion automático de 33 verificaciones, `demo/correr.py`, sigue en la rama `demo-noche`, sin fusionar.

El material visual quedó del guion anterior. `pitch/DIAPOSITIVAS.md` sigue con las ocho diapositivas de antes. El plan del video pide «la barra de la simulación, 40,5 % y 98,4 %», y la única figura de simulación en `figuras_pitch/png` es `e_simulacion_ejemplo.png`, que lleva la marca «NO CITAR» y cifras viejas (49,6 y 95,9), así que no puede salir en pantalla. Tampoco hay registro de un ensayo cronometrado de las 400 palabras.

Varias frases llegan sin la salvedad que un jurado pregunta. La apertura le atribuye a Manizales una cifra de los bancos de alimentos y omite lo que iba en camino (corrección 5). El 98,4 % se compara solo con el orden de llegada (corrección 1). Los 15.000 mensajes abren el día como hazaña, cuando se midieron en un portátil, con un lector simulado y solo para recibirlos, y el archivo guarda la respuesta completa para las preguntas (línea 58). El piloto va «con la Unidad de Gestión del Riesgo», que nadie ha contactado (corrección 3). Por último, la frase «La ayuda hace falta cuando llegan miles» promete un ruteo para miles que `main` no ha medido. La rama `escala`, sin fusionar, ya lo midió. Con 1.000 pedidos, el optimizador de hoy atiende 91, y desde 250 pedidos el techo son los 6.240 kg de la flota (canal de esa rama, 12:10 p. m.). Esa frase está en el párrafo que el archivo prevé cortar primero.

En tres minutos tampoco se oye a la UNAL ni un hecho de un aliado. Por eso los criterios 3 y 5, que suman 30 puntos, dependen de que el jurado lea la ficha o pida las diapositivas de respaldo A y D. La corrección 3 resuelve lo primero, y lo segundo depende de lo que haya dicho el Banco.

Quedan tres cabos sueltos de la entrega. La hora del pitch, 2:00 o 2:30 p. m., sigue sin confirmar en `ENTREGA.md` (línea 19). El repositorio se contradice sobre la clave del tablero, y si `DESPACHOX_CLAVE_TABLERO` no está definida en Railway, cualquiera con el enlace ve la mesa del despachador, de modo que «el despachador decide» queda sin respaldo, como anotó la ronda de las 4:40. Carlos sabe cuál de las dos versiones es cierta. Además, `ENTREGA.md` todavía nombra la carpeta del Drive «DespachoX · Equipo 19 · Vertical 04».

## 6. Quién calificó y con qué modelo

Los tres jurados corrieron con el modelo Fable, cada uno con su papel (el académico de la UNAL, la directora de operaciones de un banco de alimentos y la funcionaria de gestión del riesgo). Son los mismos papeles de las rondas de la madrugada. Fable nombra aquí el modelo, y los jurados fueron agentes aparte de la sesión Fable del proyecto en claude.ai, que escribe el pitch. Un verificador independiente repitió las pruebas en copias del repositorio y cotejó los hechos y las frases citadas de cada jurado. Esta síntesis, con la elección y la fusión de las correcciones, la escribió un agente de Noche-2 con Claude Opus 5.5. La ronda de las 2:00 a. m. se hizo con Opus, así que la diferencia con la madrugada mezcla dos cambios, el del repositorio y el del modelo que califica.

Esta calificación es una simulación hecha por el equipo. La nota real la ponen los jurados de la hackathon, que van a oír el pitch y ver la demo o el video, y ningún jurado simulado pudo hacer ninguna de las dos cosas. Todo puntaje de este archivo es estimado [E]. Lo medido [M] son las pruebas, la demo por terminal y los comandos del A25 que corrieron los jurados y el verificador, más la comparación de commits del comienzo y la prueba de fusión de `samuel-bot`.
