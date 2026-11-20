# Plan del equipo · viernes 3:00 p. m. en adelante

**Los pasos concretos de cada persona están en `docs/GUIA_SIGUIENTE.md`.** Este documento explica el porqué y las decisiones.

Reemplaza a `ROLES_VIERNES.md`. Lo escribe el capitán después de revisar todo el repositorio.

## Dónde estamos

| Pieza | Estado | Probado |
|---|---|---|
| Despacho (optimizador, recálculo, red ampliada, datos reales) | Hecho | Sí, con pruebas |
| Ubicador de lugares (452 apodos) | Hecho | 44 frases, 0 errores seguros |
| Bot de Telegram | Corre con claves reales | Extractor: 62 de 64 campos en 15 mensajes de ejemplo. Falta la prueba desde un teléfono |
| Tablero | Hecho | En pantalla con la semilla |
| Simulación | Primera corrida hecha | 360 jornadas |
| **Todo junto, con un teléfono real** | **Nunca se ha corrido** | No |
| Ficha de los seis componentes | Vacía, con borrador de 4 a 6 | |
| Fuentes verificadas por una persona | Ninguna | |
| Aliado con nombre | Ninguno | |

Las pruebas automáticas pasan completas (96). El riesgo ya no está en el código: está en que nunca se ha visto funcionar de punta a punta y en que la mitad de la rúbrica no es código.

## Quién hace qué

El código lo escribieron sesiones de Claude de Carlos. A partir de ahora cada persona es **dueña** de una parte: la corre, la entiende y la defiende ante el jurado.

| | Samuel (líder) | Jacobo | Carlos (capitán) |
|---|---|---|---|
| Es dueño de | El bot y la ficha. Presenta el pitch | El tablero. Lo opera en la demo | El optimizador, la simulación y la integración |
| Pregunta del jurado que debe poder responder | «¿Qué pasa si la IA entiende mal?» | «¿Quién decide?» | «¿Por qué no basta una regla simple?» |

### Ahora mismo (3:00 a 4:00 p. m.)

**Los tres juntos, en el computador de Carlos: la primera corrida de punta a punta.** Es el hito del día.

1. Samuel crea el bot en BotFather (pasos en `entrada/README.md`) y le pasa el token a Carlos por privado.
2. Carlos pone las dos claves en `.env`, hace `git pull`, carga la semilla y arranca el bot y el tablero.
3. Se sigue `docs/GUION_DEMO.md` paso a paso con el teléfono de Samuel. El cierre de la demo es **«avenida del Centro»**.
4. Jacobo maneja el tablero. Todo lo que falle se anota en `torre/CANAL.md`; no se arregla en el momento.

### 4:00 p. m. · Charlas
Va una persona (Jacobo) y trae lo que sirva. Los otros dos siguen.

### 4:00 a 6:00 p. m.

- **Samuel:** componentes 1, 2 y 3 de `docs/FICHA.md`. Abre los enlaces de `docs/investigacion/04_evidencia_del_problema.md`, elige tres cifras, las verifica y las pasa a `docs/FUENTES.md`. Crea la carpeta del equipo en Drive y marca las tareas del tablero de iNNOVO.
- **Jacobo:** recorre el tablero como despachador con prisa y anota en su torre qué sobra y qué falta. Pide a Nicolás y a José Manuel que entren a iNNOVO con su correo para quedar vinculados.
- **Carlos:** la mesa (formato de prototipo, plantilla, franja de mentoría, anualidad de la patente), un profesor de logística y el contacto del Banco de Alimentos. Lanza la tercera ronda de encargos (`encargos/RONDA_3.md`).

### Mentorías (5:00 p. m. o 7:00 p. m., según la franja)

Se muestra la demo en vivo y la ficha 1 a 3. Samuel habla, Jacobo opera, Carlos anota cada observación en el canal. Después, cada uno llena en iNNOVO el formulario de «Mentorías y asesorías recibidas».

### Noche

| Quién | Qué |
|---|---|
| Samuel | Ficha 4 a 6 a partir de `FICHA_4_5_6_BORRADOR.md`, con los ajustes de la mentoría. Primer ensayo del pitch |
| Jacobo | Video de respaldo de la demo, 60 a 90 segundos, grabando la pantalla |
| Carlos | Trazabilidad mínima, segunda corrida de la simulación, revisar lo que salga de la ronda 3 |

Quien presenta el sábado duerme.

### Sábado

8:30 a. m. se congelan las funciones. 10:30 mentoría 2 con la presentación real. 1:00 p. m. entrega en iNNOVO (enlace de Drive). 2:30 p. m. pitch de preselección.

## Cómo trabajar con Claude sin gastar el cupo

- Samuel y Jacobo usan su cupo para **entender y escribir**, no para programar: pedirle a Claude que les explique su módulo, redactar la ficha, preparar respuestas al jurado.
- Los cambios de código los piden por `torre/CANAL.md` y los ejecutan las sesiones de Carlos.
- Diez minutos que valen la pena: cada uno abre Claude en el repositorio y le pide «explícame `entrada/` (o `tablero/`) como si mañana me fueran a preguntar por él, y hazme cinco preguntas difíciles».

## Decisiones del capitán (responden a la auditoría)

1. **Demo:** el cierre es la avenida del Centro, que sí cambia rutas. La Siria ya se reconoce y queda para las preguntas.
2. **Capacidad UNAL:** una sola patente, el empaque captador de etileno (certificado 37476, vigente), como parámetro del modelo con supuesto declarado. Para que no sea decorativa, el optimizador debe leer `lotes.empaque_activo`. El indicador de lluvia del IDEA sale del prototipo y queda en el plan, salvo que el IDEA entregue datos hoy. El criterio 3 se apoya además en la formulación, la simulación y la revisión de un profesor.
3. **Trazabilidad:** entra una versión mínima antes del congelamiento: al aprobar un plan se crean los paquetes con su código, y el tablero permite marcar «entregado». El QR impreso es opcional.
4. **Puntos críticos:** los marca el despachador en el tablero.
5. **Plan rechazado tras un recálculo:** se corrige esta noche (el plan anterior solo pasa a `reemplazado` cuando se aprueba el nuevo).
6. **Lo que no se dice:** que el mapa funciona sin conexión (el fondo necesita red), que hay formulario para digitar pedidos (no lo hay), ni una meta de equidad (la simulación muestra que priorizar lo crítico hace esperar más al punto peor atendido; se dice como costo conocido).
