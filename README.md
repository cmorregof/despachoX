# DespachoX

Equipo 19 · Hackathon UNAL Manizales 2026 · Vertical 04, Logística y abastecimiento.
Samuel Rosso (líder) · Carlos Orrego · Jacobo Vasco · Nicolás Ramírez · José Manuel Aristizábal

> **Si acabas de llegar:** primero lee [`docs/PROBLEMA.md`](docs/PROBLEMA.md), que explica qué problema resolvemos. Luego esta página, que explica cómo lo resolvemos. Después abre tu archivo de tareas: [`SAMUEL.md`](SAMUEL.md), [`JACOBO.md`](JACOBO.md) o [`CARLOS.md`](CARLOS.md).

## Qué es, en un párrafo

Después del sismo, a Manizales llegó comida donada. Lo difícil fue decidir a dónde mandarla primero, por cuál vía y antes de que se dañara. DespachoX es una mesa de despacho para la persona que toma esa decisión en un centro de acopio. Los barrios piden por chat, los conductores avisan por chat cuando una vía está cerrada, el sistema propone rutas para los vehículos disponibles y las vuelve a calcular cuando algo cambia. La persona que despacha aprueba o rechaza cada plan.

La regla que no se negocia: **el modelo de lenguaje lee y ordena los mensajes; el optimizador y las reglas calculan; el despachador decide.**

## Cómo funciona

```mermaid
flowchart LR
    V["Vecino o conductor<br/>escribe por Telegram"] --> B["entrada/<br/>bot: lee el mensaje"]
    B --> L["lugares/<br/>¿dónde queda eso?<br/>pide confirmar"]
    L --> DB[("datos/<br/>base compartida")]
    DB --> D["despacho/<br/>optimizador de rutas"]
    D --> DB
    DB --> T["tablero/<br/>mapa del despachador"]
    T -->|"confirma, aprueba,<br/>rechaza"| DB
```

Un ejemplo de punta a punta:

1. Un líder de barrio escribe: «somos 40 familias en san jose no hay arroz ni leche».
2. El bot lo convierte en un pedido (lugar, familias, productos, urgencia) y contesta: «Ubiqué "san jose" en: San José (barrio). ¿Es correcto?».
3. La persona dice que sí. El pedido aparece en el mapa del despachador.
4. El despachador lo confirma y pulsa «Calcular plan». Aparecen las rutas de cada vehículo.
5. Un conductor escribe: «derrumbe en la avenida del centro, no pasa camión». El despachador confirma el cierre.
6. El sistema recalcula: el camión ya no entra a San José y el pedido pasa a un campero. La pantalla dice qué cambió.
7. El despachador aprueba con su nombre. Queda registrado.

## Qué hay en cada carpeta

| Carpeta | Qué hace | En palabras simples | Dueño |
|---|---|---|---|
| `entrada/` | Bot de Telegram | Recibe mensajes, usa un modelo de lenguaje para sacar los datos, borra teléfonos y nombres, y guarda el pedido o el cierre | Samuel |
| `tablero/` | Pantalla del despachador | Mapa con pedidos, cierres y rutas; botones para confirmar, calcular, aprobar y rechazar; bitácora de decisiones | Jacobo |
| `despacho/` | Optimizador | Reparte los pedidos entre camiones, camperos y motos sobre el mapa real de vías, saca primero lo que vence primero y recalcula cuando se cierra una vía | Carlos |
| `lugares/` | Ubicador de lugares | Convierte «por la siria» en un punto del mapa. Conoce 452 nombres y apodos de Manizales. Si no sabe, lo dice y pide la ubicación. Nada se ubica sin que una persona confirme | Carlos |
| `despacho/sim/` | Simulación | Prueba el sistema en 360 jornadas inventadas y lo compara contra otras formas de despachar | Carlos |
| `datos/` | Base de datos | `esquema.sql` define las tablas. `semilla/` trae datos de prueba inventados: 15 puntos, 2 acopios, 5 vehículos, 20 pedidos | Carlos |
| `despliegue/` | Nube | Lo necesario para correr todo en Railway | Carlos |
| `docs/`, `pitch/` | Documentos | Problema, estrategia, ficha, guiones, resultados (ver el mapa de documentos) | Samuel |
| `encargos/` | Instrucciones para Claude Code | Lo que se le pide a cada sesión de Claude Code, con objetivo, pasos y criterio de «hecho» | Cada dueño |
| `torre/` | Bitácoras | El estado de cada frente y `CANAL.md`, donde las sesiones dejan avisos, preguntas y resultados | Todos |

Los módulos no se llaman entre sí: solo se comunican por la base de datos. Por eso cada dueño puede avanzar en su parte sin esperar a los demás.

## Estado al viernes 4:00 p. m.

| Pieza | Estado |
|---|---|
| **En la nube** | **Funciona** desde las 3:45 p. m. Bot y tablero en Railway, con una sola base de datos |
| **De punta a punta** | **Funciona.** Un mensaje real («hay 6 bebés sin leche desde ayer en la enea») llegó por el bot, quien lo escribió confirmó el lugar desde el teléfono, el despachador lo confirmó y entró al plan: 19 de 19 pedidos en 3 vehículos, calculado en 8 s. Falta probar en la nube un cierre vial y la aprobación |
| Bot | Funciona. Leyó bien 62 de 64 datos en 15 mensajes de ejemplo escritos por el equipo. Falla conocido: no convierte «6 bebés» en familias ni pone cantidad a la leche. En corrección |
| Ubicador de lugares | Funciona. En 44 frases de prueba: 30 aciertos directos, 5 ofreciendo opciones, 9 «no sé» y ningún lugar equivocado propuesto con seguridad |
| Optimizador | Funciona. Planea unos 20 pedidos en 8 a 10 segundos y recalcula ante cierres |
| Tablero | Funciona. Fallo conocido: con un plan ya aprobado, «Calcular plan» borra las rutas anteriores. En corrección |
| Simulación | Primera ronda completa. Segunda en curso |
| Trazabilidad de paquetes | Pendiente |
| Ficha de los seis componentes | **Vacía** (`docs/FICHA.md`). Hay borrador de los componentes 4 a 6 |
| Cifras verificadas por una persona | **Ninguna** (`docs/FUENTES.md` vacío) |
| Aliado con nombre | Ninguno |

Las pruebas automáticas pasan completas: 101.

### Qué dice la simulación, sin adornos

- Contra despachar por orden de llegada, DespachoX sube las entregas a tiempo en puntos críticos entre 12 y 46 puntos porcentuales, según la carga.
- Contra un despachador experto que ya prioriza lo urgente, **empata** en puntos críticos, queda unos 2 puntos por debajo en el total de entregas a tiempo y ahorra entre 47 y 75 km por jornada. Darle más tiempo de cálculo al optimizador no cambia esto.
- El desperdicio de perecederos baja a cero por una regla de bodega (sacar primero lo que vence primero), no por el ruteo.

El argumento honesto: DespachoX pone al alcance de cualquier voluntario lo que hoy solo sabe hacer un despachador con experiencia, lo combina con los cierres que llegan por chat y deja registro. Detalle en `docs/SIMULACION.md`.

## En qué está cada uno ahora

| Quién | Frente | Qué está haciendo | Encargo para Claude Code | Rama |
|---|---|---|---|---|
| **Samuel** | Bot | Que entienda a un vecino («6 bebés sin leche»), que sea cómodo de usar (botones, notas de voz, aviso cuando el pedido sale) y que aguante miles de mensajes, medido. Después, **pedidos por SMS** para cuando no hay datos | `encargos/A2_BOT_SAMUEL.md`, luego `encargos/A3_SMS_SAMUEL.md` | `samuel-bot` |
| **Jacobo** | Tablero | Corregir lo que rompe la demo, un **resumen de la mesa hecho por un modelo** para cuando hay miles de pedidos, una pantalla con filtros para alguien con prisa, y un **mapa que funciona sin internet** | `encargos/C2_TABLERO_JACOBO.md` y la tarea 3 de `JACOBO.md` | `jacobo-tablero` |
| **Carlos** | Optimizador e integración | Trazabilidad, hoja de ruta impresa con QR para trabajar sin señal, la patente UNAL dentro del modelo, fusionar las ramas sin romper la nube, y las conversaciones con la organización, profesores y usuarios reales | `encargos/RONDA_3.md` (parte B), luego `encargos/B3_SIN_CONEXION_CARLOS.md` | `carlos-despacho` |

Las tareas con casillas de cada uno están en `SAMUEL.md`, `JACOBO.md` y `CARLOS.md`. Además, Samuel escribe la ficha y presenta; Jacobo opera la demo y graba el video de respaldo.

## Cómo trabajamos

**Cada quien es dueño de su parte.** La entiende, la mejora y la defiende ante el jurado. Mañana le van a preguntar a Samuel por el bot y a Jacobo por el tablero.

**Con Claude Code.** Cada dueño abre Claude Code en su copia del repositorio y le pide ejecutar su encargo:

```
Haz git pull --rebase, lee encargos/A2_BOT_SAMUEL.md y ejecútalo.
```

`CLAUDE.md` le da a Claude las reglas del equipo, y el encargo le dice qué hacer, qué no tocar y cuándo está hecho. Para entender tu módulo antes de mejorarlo, pídele: «explícame `entrada/` como si mañana me fueran a preguntar por él, y hazme cinco preguntas difíciles».

**En ramas, nunca directo a `main`.** Cada cambio en `main` reinicia el servidor de la nube y corta las pruebas de todos. Cada dueño sube a su rama y abre un pull request. Carlos fusiona a horas fijas, con las pruebas en verde: **6:30 p. m.**, **11:00 p. m.** y **8:00 a. m.**

**Avisos en `torre/CANAL.md`.** Si cambias algo que otro usa, necesitas una decisión o te bloqueas, escríbelo ahí. Si necesitas una columna nueva en la base, pídela ahí: `datos/esquema.sql` lo cambia Carlos.

**Una sola base en la nube.** Lo que confirmes o apruebes en el tablero lo ven los demás. Antes de un ensayo serio, se reinician los datos de prueba.

## Cómo probarlo

**En la nube (ya funciona):** le escribes al bot en Telegram y abres el tablero. Es la misma base de datos para todos: lo que confirmes o apruebes lo ven los demás. Si el mapa sale gris en Brave, desactiva los escudos de Brave para esa página.

- Bot: [t.me/despachox_bot](https://t.me/despachox_bot) (o escanea el código de abajo)
- Tablero: [despachox-production.up.railway.app](https://despachox-production.up.railway.app/)

<img src="recursos/qr_bot.png" alt="Código QR del bot de DespachoX en Telegram" width="220">

**En tu computador:** `docs/GUIA_SIGUIENTE.md`, «Paso 0». Ojo: solo un proceso puede leer el bot con el mismo token. Si el bot corre en la nube, no lo arranques en local.

**El guion de la demo**, con los mensajes y clics exactos: `docs/GUION_DEMO.md`.

## Qué nos califican

| # | Criterio | Puntos | Dónde lo trabajamos |
|---|---|---|---|
| 1 | Problema y vertical | 20 | `docs/FICHA.md`, `docs/FUENTES.md` |
| 2 | Prototipo de solución | 25 | El código, la demo y `docs/SIMULACION.md` |
| 3 | Conocimiento utilizado | 15 | `docs/investigacion/06_patentes_sipi.md` |
| 4 | Plan de 30 a 90 días | 15 | `docs/FICHA_4_5_6_BORRADOR.md` |
| 5 | Viabilidad y aliados | 15 | `docs/FICHA_4_5_6_BORRADOR.md` |
| 6 | Impactos esperados | 10 | `docs/FICHA_4_5_6_BORRADOR.md`, `docs/SIMULACION.md` |

El código cubre sobre todo el criterio 2. Los otros 75 puntos se ganan escribiendo, verificando y hablando con gente.

## Fechas

| Cuándo | Qué |
|---|---|
| Hoy, 5:00 o 7:00 p. m. | Mentoría 1: se muestran los componentes 1 a 3 |
| Sábado 8:30 a. m. | Se congelan las funciones: desde ahí solo se arregla |
| Sábado 10:30 a. m. | Mentoría 2: los seis componentes y la presentación |
| Sábado 1:00 a 2:30 p. m. | Entrega: un enlace de Google Drive registrado en iNNOVO |
| Sábado 2:30 p. m. | Pitch de preselección |
| Sábado 4:00 p. m. | Presentaciones finales |

## Mapa de documentos

| Si quieres saber… | Lee |
|---|---|
| Cuál es el problema que resolvemos | `docs/PROBLEMA.md` |
| Qué me toca ahora | `SAMUEL.md`, `JACOBO.md`, `CARLOS.md` |
| Qué le pido a Claude Code | `encargos/README.md` (encargos vigentes) |
| Por qué construimos esto y cómo ganar | `docs/ESTRATEGIA.md`, `docs/PLAN_EQUIPO.md` |
| Qué existe ya en el mundo y qué nos diferencia | `docs/ESTADO_DEL_ARTE.md` |
| Cómo se hace la demo | `docs/GUION_DEMO.md` |
| Qué decir en el pitch y qué van a preguntar | `pitch/GUION.md` |
| Dónde podemos perder | `docs/SUGERENCIAS.md` |
| Cómo se entrega y los horarios oficiales | `docs/PLATAFORMA_INNOVO.md` |
| Qué patente UNAL usamos | `docs/investigacion/06_patentes_sipi.md` |
| Cómo correr todo en la nube | `docs/DESPLIEGUE.md` |
| Cómo funciona sin internet | `docs/SIN_CONEXION.md` |
| El contexto regional, para mentores y jurado | `docs/informe/informe_contexto.pdf` |
| Lo que dijo la mentoría 1 y la idea que se discute | `docs/MENTORIA_1.md` |

## Reglas del equipo

- Ninguna clave en el repositorio. Van en `.env` o en las variables de Railway.
- Ningún dato personal real. Los datos de prueba son inventados.
- Toda cifra del pitch lleva su fuente en `docs/FUENTES.md`, y alguien del equipo abrió el enlace.
- Los números de la simulación se presentan como simulación.
- Trabaja en tu rama. Cuando termines una tarea, márcala en tu archivo, sube a tu rama y avisa en `torre/CANAL.md`.

Datos del mapa: © colaboradores de OpenStreetMap.
