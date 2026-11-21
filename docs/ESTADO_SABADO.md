# Estado del sábado · revisión general de las 7:00 a. m.

Sábado 21 de noviembre de 2026. Lo escribió Fable, el orquestador, entre las 6:26 y las 7:10 a. m., sobre `main` en `a3db326`. Cuatro agentes revisaron el producto, las ramas de código, las ramas de documentos y la coherencia de lo que lee el jurado. Fable comprobó en el código y en las tablas los hallazgos que aquí se citan. Lo medido lleva [M] y lo leído en el código lleva [I]. Los informes completos de los agentes no están en el repositorio.

Congelamiento de funciones: 8:30 a. m. Mentoría 2: 10:30 a. m. Entrega: de 1:00 a 2:30 p. m. Pitch: 2:00 p. m. Entre la 1:30 y las 3:30 p. m. no se empuja nada a `main`.

## 1. Estado por criterio de la rúbrica

| # | Criterio | Qué va | Qué no va | Evidencia | Qué falta | Quién | Para cuándo |
|---|---|---|---|---|---|---|---|
| 1 | Problema y vertical (20) | El problema cabe en una frase y repite el entregable de la ficha 04. El guion ya dice 404 t en acopio, 157 en tránsito y 41 entregadas. `docs/FUENTES.md` tiene el registro consolidado con 25 discrepancias declaradas | Ninguna cifra externa la ha abierto una persona. Las fichas y el informe corto conservan frases que su fuente no dice (D3, D7, D8, D15, D18). No hay usuario con nombre y cargo | `docs/FUENTES.md`, `docs/ERRATAS.md`, `docs/VERIFICAR_SAMUEL.md` | Abrir por persona las siete cifras con asterisco del guion. Marcar las erratas. Anotar lo que diga el Banco | Samuel abre fuentes. Carlos marca erratas. El integrante de Ingeniería Industrial llama al Banco | Llamada a las 8:00. Fuentes antes de la 1:00 p. m. |
| 2 | Prototipo (25) | La suite da 469 pruebas en verde, 1 omitida y 26 fallas esperadas [M]. La demo por terminal pasa 33 de 33 verificaciones, con planes de 3,5 a 3,6 s [M]. El tablero carga, la clave funciona y los tooltips escapan HTML [M]. El tablero de Railway responde en su ruta de salud [M] | Con el modelo activo, un ENTREGADO por Telegram no se registra (`entrada/flujo.py:97-105`) [M]. El lector por reglas lee «sí pasa moto» como bloqueo de la moto (`entrada/sms.py:194-196`) [M]. H6 sigue abierto (`lugares/nomenclator.py:257-259`) [M]. No hay video de respaldo | Suite y demo corridas a las 6:35 a. m. en Python 3.12 | Traer el commit `7a290fe` o decir «por SMS». Arreglo de H6. Video de 60 a 90 segundos. Pulsar «Confirmar» y «Reiniciar» una vez en el tablero real | Carlos decide `7a290fe`. Samuel, H6. Jacobo, video | Antes de las 8:30 el código. Video antes de las 10:30 |
| 3 | Conocimiento utilizado (15) | Ruteo con capacidad y ventanas en OR-Tools. Simulación de eventos con semillas pareadas. La corrida nueva usa las velocidades de la tesis UNAL de 2019 y todas sus cifras cuadran con los CSV [M]. Ancízar, la tipografía de la UNAL, entra al tablero | El A25, que la ficha llama capacidad principal, no está en el código de `main`. Ningún profesor de la Sede ha revisado la formulación. Los enlaces del IDEA dan 404 | Rama `simulacion` (`513b88a`), sección 9. Rama `a25` (`b96ff71`): 501 pruebas en verde sobre `main` [M] | Fusionar `simulacion`. Decidir `a25`. Cambiar los enlaces del IDEA por las capturas del Internet Archive, abiertas por una persona. Visto bueno de un profesor del IDEA | Fable fusiona. Carlos decide `a25` y busca al profesor | Antes de las 8:30 el código |
| 4 | Plan de 30 a 90 días (15) | `docs/PLAN_30_90.md` tiene cinco hitos con criterio para seguir, ajustar o parar, y una regla de cambio | El plan nombra todavía La Macarena y El Tablazo. El integrante de Ingeniería Industrial no tiene nombre. La ficha corta y el plan reparten distinto los responsables. El informe corto trae otras fases | `docs/PLAN_30_90.md`, `docs/FICHA_CORTA.md`, componente 4 | Fusionar `territorio-p2`. Poner el nombre. Un solo reparto de responsables. Subir el plan al Drive | Fable edita. Carlos da el nombre | Antes de la mentoría |
| 5 | Viabilidad y aliados (15) | Matriz de 16 riesgos. Borrador de privacidad. Directorio de ocho aliados. Corre en un portátil sin red | Ningún aliado ha visto la propuesta. La ficha corta dice «no se guardan nombres ni teléfonos» (`:84`) y H6 lo contradice. Ningún documento dice que el tablero pide clave | `docs/RIESGOS.md`, `docs/PRIVACIDAD.md`, `aliados/DIRECTORIO.md` | Respuesta del Banco. Definir la clave en Railway. Cambiar la frase de la ficha | Integrante de Ingeniería Industrial. Carlos | 8:00 la llamada. Clave antes de la demo |
| 6 | Impactos (10) | En simulación, con carga media y 30 jornadas por política, DespachoX sube los críticos a tiempo de 53,6 % a 98,3 % frente al orden de llegada: 44,7 puntos, con intervalo del 95 % de 37,7 a 51,6 [M] | La ficha corta, el anexo y el README citaban la primera corrida. La magnitud del piloto no tiene número. La ventaja sobre el despachador con oficio en críticos no se puede afirmar hasta ver la corrida 9.3 | `despacho/sim/resultados_velocidades/tablas.md` en la rama `simulacion` | Llenar los [SIM] del pitch después de `territorio-p2`. Beneficiarios del territorio P2 | Fable | Antes de la mentoría |

## 2. Ramas sin fusionar

| Rama | Qué trae | Choca con `main` | Pruebas sobre `main` [M] | Recomendación |
|---|---|---|---|---|
| `simulacion` (`513b88a`) | Sección 9, resultados y 6 pruebas | No | 475 / 1 / 26 | Fusionar. Aprobado por Carlos a las 6:40, con tres arreglos de texto |
| `territorio-p2` | Guion, diapositivas, cifras, plan, riesgos, preguntas y mapa en P2 | Por ver | Por ver | Revisar y fusionar cuando llegue |
| `qa-noche` (`ca195b4`) | Arreglos de calidad en `entrada/` y 36 pruebas | No | 505 / 1 / 26 | Traer solo `7a290fe` (492 / 1 / 26). El resto espera, porque choca con `samuel-bot` |
| `a25` (`b96ff71`) | Alertas A25 con lluvia sintética, apagadas por defecto | Solo en `docs/FUENTES.md` | 501 / 1 / 26 | Fusionar, si Carlos lo aprueba. Diez minutos |
| `demo-noche` (`d24cd2d`) | Demo por terminal, lista de chequeo y pruebas de propiedades | No | 494 / 1 / 26 | Esperar. La carpeta `demo/` se copia en el portátil como respaldo |
| `samuel-bot` (`aff5bcb`) | Productos nuevos y arreglos H2 y H3. No trae H6 | En `docs/FUENTES.md` y `torre/CANAL.md` | 481 / 1 / 24 | Esperar. Cambia los kilos por familia y lee «café» en «Villa Café» |
| `jacobo-silencio` (`5792fc8`) | Definición única de silencio en el triage | No | 477 / 1 / 26 | Esperar. Contradice `entrada/silencio.py:58` sobre los mensajes descartados |
| `manuscrito` (`4aa2058`) | El artículo, solo en `docs/manuscrito/` | No | Sin código | Esperar |
| `ficha`, `datos`, `carlos-despacho`, `jacobo-triage` | Nada pendiente | — | — | Ya están enteras en `main` |
| `ancizar` (local, `2c4c072`) | Ancízar Sans en el tablero, con licencia SIL OFL 1.1 | No | 48 de `tablero/` | Fusionar. Pedido por Carlos a las 6:39 |

Con `main`, `a25` y `7a290fe` juntos pasan 524 pruebas, y la demo por terminal da 33 de 33 con el A25 apagado y encendido [M].

## 3. Lo que los documentos del jurado no dicen igual

1. **Territorio.** La Macarena y El Tablazo siguen en el guion (`:111`, `:178`), las diapositivas (`:149`, `:165`), el plan, los riesgos y las preguntas 18 y 28. Lo resuelve `territorio-p2`.
2. **La cifra de apertura.** El guion dice una cosa y las dos fichas otra (D3 y D15).
3. **La entrega por chat.** El guion (`:103`), la ficha corta (`:32`) y el plan (`:60`) la afirman sin salvedad.
4. **La simulación.** Primera corrida en la ficha corta, la ficha de mentoría y el README. En corrección.
5. **Datos personales.** `docs/FICHA_CORTA.md:84` contra H6.
6. **El nombre.** El tablero dice Convite y el guion cierra con DespachoX.
7. **El reinicio.** `pitch/GUION.md:38` dice que no hay botón, y sí lo hay (`tablero/app.py:591`).
8. **El A25.** La diapositiva A y el guion tienen variantes abiertas.
9. **Las velocidades.** Quedan 9 lugares con «medido con GPS» y 13 con «velocidades medidas».
10. **Los responsables.** Dos repartos distintos y un integrante sin nombre.

Ninguna errata de `docs/ERRATAS.md` está aplicada en las fichas ni en el informe corto.

## 4. Decisiones de Carlos, con la recomendación de Fable

| # | Decisión | Recomendación | Por qué |
|---|---|---|---|
| 1 | ¿Entra `7a290fe` antes de las 8:30? | Sí | Doce líneas, sin choque, 23 pruebas más. Sin él hay que quitar del guion y de la ficha la entrega por chat |
| 2 | ¿Entra `a25` antes de las 8:30? | Sí | Es la capacidad UNAL y hoy solo se nombra. Viene apagada y una prueba confirma que así el plan no cambia |
| 3 | Convite o DespachoX | Convite | El tablero ya lo lleva y responde a la mentoría. DespachoX queda como nombre técnico |
| 4 | Identidad visual | Opción 1, tinta y cobre, con bermellón de alerta | Ya está aplicada. Las otras cuestan entre 75 minutos y 3 horas |
| 5 | Erratas de la sección 1 de `docs/ERRATAS.md` | Aprobar las cinco | Son las que tocan la apertura del pitch |
| 6 | La palabra «GPS» | La frase ya aprobada, en todos los lugares | Coincide con las páginas 46 a 48 de la tesis |
| 7 | Bajo Tablazo, 8,4 o 9,3 km | Pierde peso con P2. Verificar las distancias de P2 con el mismo método | El método viejo mide hasta el nodo del grafo |
| 8 | ¿El jurado recibe la clave del tablero? | No. Recibe el video y el enlace al bot | La base de la nube es una sola, y con la clave podría reiniciarla |
| 9 | Informe corto | Dejarlo fuera del Drive, salvo que haya 80 minutos para corregir y recompilar | Trae diez discrepancias y otras fases |
| 10 | Nombre del integrante de Ingeniería Industrial | Darlo hoy | Aparece 20 veces como rol sin persona |
| 11 | Hora y duración del pitch, quién habla | Preguntar en la mesa a las 8:30 | La página dice 2:00 y la plataforma 2:30 |
| 12 | Tamaño de familia: 1,8, 2,9 o 4 | 2,9, que es el del escenario público, con su fuente | `raciones.py` usa 4 sin fuente |
| 13 | `revision/JURADO.md` en un repositorio público | Sacarlo de `main` | Es un documento interno, y lo dice su primera línea |
| 14 | `jacobo-silencio`: ¿un mensaje descartado cuenta como contacto? | Decidir después del pitch | No afecta la demo |

## 5. Lo que sigue, en orden

1. Hasta las 8:30: push agrupado con `simulacion` y sus arreglos, las fichas, Ancízar y lo que Carlos apruebe de los puntos 1 y 2. Arreglo de H6 de Samuel.
2. Al llegar `territorio-p2`: revisar, fusionar y llenar los [SIM] del guion, las diapositivas, las cifras, el plan y los riesgos.
3. De 8:30 a 10:30: presentación para la mentoría, video de respaldo, erratas aprobadas y lo que diga el Banco (marcas [P5]).
4. De 11:00 a 12:00: reinicio de la base de la nube con el botón del tablero y ensayo.
5. A la 1:00 p. m.: entrega según `ENTREGA.md`. A la 1:30 se cierra `main`.

## 6. Lo que esta revisión no comprobó

- El modelo real, Telegram y `despliegue/arranque.sh`, porque no hay claves en el entorno de revisión.
- El contenido del tablero de Railway. Solo se comprobó que el servicio responde.
- Ninguna fuente externa. Las discrepancias son lecturas de máquina de anoche.
- La corrida 9.3 de la simulación, que no había llegado.
