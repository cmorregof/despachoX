# Tareas de Carlos

Capitán. Dueño del **optimizador**, la **simulación**, la **integración** y las sesiones de Claude Code.

Marca con `[x]` lo que termines. Luego `git pull --rebase && git push`.

## Tarea 0 · Entender el problema (antes que nada)

- [ ] Lee `docs/PROBLEMA.md` completo. Son diez minutos.
- [ ] Responde en voz alta las cinco preguntas del final. Si alguna no te sale, vuelve al texto o pregunta en el grupo.
- [ ] Lee el `README.md` para ver cómo responde a ese problema lo que hay construido.

**Hecho cuando:** puedes explicarle el problema a alguien de fuera en un minuto, sin mencionar la tecnología.

## Tarea 1 · Todo en la nube

**Para qué:** que Samuel y Jacobo prueben desde sus equipos sin depender de un computador, y que la demo tenga una dirección pública.

- [ ] Sigue `docs/DESPLIEGUE.md`. Va todo en un solo servicio de Railway (bot, tablero y optimizador). Vercel no sirve aquí: el tablero es Streamlit, un servidor de Python con conexión abierta, y además los tres comparten un archivo SQLite.
- [ ] Antes de desplegar, sube la red vial al repositorio (paso 1 de esa guía). Evita que el arranque dependa de OpenStreetMap.
- [ ] Volumen en `/data`, variables `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN` y `DESPACHOX_SAL`, y dominio público.
- [ ] Apaga el bot local: Telegram solo admite un proceso por token.
- [ ] Pega en el README, sección «Cómo probarlo», el nombre del bot y la dirección del tablero. Avisa a Samuel y a Jacobo.

**Hecho cuando:** un mensaje enviado desde el teléfono de Samuel aparece en el tablero abierto en el computador de Jacobo.

## Tarea 2 · Tercera ronda de las sesiones

**Para qué:** corregir el fallo del tablero y cerrar lo que la rúbrica pide y todavía no existe.

El mismo mensaje en las sesiones de tablero, despacho y simulación, en ese orden:

```
Haz git pull --rebase, lee las entradas nuevas de torre/CANAL.md y ejecuta tu parte de encargos/RONDA_3.md.
```

- [ ] Tablero: «Calcular plan» recalcula cuando ya hay un plan aprobado; botón de punto crítico; pestaña «Entregas»; **botón para reiniciar los datos de prueba** (añádelo al pedir la ronda: hace falta para ensayar en la nube).
- [ ] Despacho: el optimizador lee `empaque_activo`; se crean paquetes al aprobar; el plan anterior se reemplaza al aprobar el nuevo.
- [ ] Simulación: barrido del peso de puntos críticos y confirmación en semillas nuevas.
- [ ] Revisar lo que suban antes de darlo por bueno. Tras cada cambio en `main`, Railway redespliega.

**Hecho cuando:** las pruebas pasan, la demo del guion funciona en la nube con el plan ya aprobado, y `docs/SIMULACION.md` tiene el resultado del barrido.

## Tarea 3 · Las conversaciones que nadie más puede tener

**Para qué:** son los puntos de los criterios 3 y 5, y siguen en cero desde la mañana.

- [ ] **Mesa de organización:**
  - que compartan las carpetas del kit (formato de prototipo MVP y plantilla de presentación);
  - franja de mentoría de DespachoX: 5:00 o 7:00 p. m.;
  - si la preselección escoge por vertical o por puntaje global, y cuánto dura el pitch.
- [ ] **Fernando Bernal:** la anualidad 2026 de la patente 37476 no figura pagada en la SIC. ¿La pagan dentro del plazo de gracia? ¿Qué se necesita para usarla en un piloto?
- [ ] **Un profesor de logística de la Sede:** quince minutos para revisar la formulación. Nombre y fecha: ______
- [ ] **Un usuario real** (Banco de Alimentos, Cruz Roja, Defensa Civil o gestión del riesgo): cómo decidieron a dónde mandar primero, qué se dañó, qué no supieron a tiempo. Permiso para citarlo. Nombre y cargo: ______

**Hecho cuando:** hay al menos un nombre real en la tabla de aliados de `docs/FICHA_4_5_6_BORRADOR.md` y sabemos la duración del pitch.

## Notas y bloqueos
