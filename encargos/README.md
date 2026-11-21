# Encargos para Claude Code

Cada archivo es un mensaje listo para pegar en Claude Code, abierto en la raíz del repositorio. `CLAUDE.md` se carga solo, así que el encargo no repite las reglas del equipo.

Modelo: Carlos usa Fable 5.2 (`claude --model claude-fable-5-2`). Samuel y Jacobo, con plan Pro, usan Opus 5.5:

```
git pull
pip install -r requirements.txt
claude --model claude-opus-5-5
```

Si el plan no deja usar ese modelo, escriban `/model` dentro de Claude Code y elijan el mejor disponible. Con plan Pro el cupo se acaba rápido: lancen agentes en paralelo solo cuando ahorren tiempo de verdad, y uno a la vez.

| Encargo | Quién | Cuándo |
|---|---|---|
| `0_MAESTRO.md` | Carlos | Una vez, al comienzo. Audita el plan, propone mejoras y afina los otros tres |
| `A_ENTRADA_SAMUEL.md` | Samuel | Ya |
| `B_DESPACHO_CARLOS.md` | Carlos | Ya |
| `C_TABLERO_JACOBO.md` | Jacobo | Ya |
| `S_SIMULACION.md` | Carlos, en una sesión aparte | Ya; trabaja en un árbol de trabajo separado |

Los tres encargos de rol se pueden empezar sin esperar al maestro. Si el maestro cambia algo, avisa en `docs/SUGERENCIAS.md` y cada uno hace `git pull`.
| `B2_RED_Y_LUGARES.md` | Carlos, sesión B-despacho | Segunda ronda: red completa, nomenclátor, datos reales |
| `S2_SIMULACION_CRITICOS.md` | Carlos, sesión simulacion | Segunda ronda: barrido del factor de puntos críticos |

Las sesiones se hablan entre sí y con Fable por `torre/CANAL.md` (reglas en `CLAUDE.md`).

## Vigentes desde las 4:00 p. m.

| Encargo | Quién | Rama |
|---|---|---|
| `A2_BOT_SAMUEL.md` | Samuel | `samuel-bot` |
| `C2_TABLERO_JACOBO.md` | Jacobo | `jacobo-tablero` |
| `RONDA_3.md`, parte B-despacho | Carlos | `carlos-despacho` |
| `B3_SIN_CONEXION_CARLOS.md` (después de la ronda 3) | Carlos | `carlos-despacho` |
| `A3_SMS_SAMUEL.md` (después de la etapa 1 de A2) | Samuel | `samuel-bot` |
| `T1_TERRITORIO.md` (vista por territorio, aprobada a las 5:10 p. m.) | Carlos, parte B; Jacobo, parte C | `carlos-despacho` y `jacobo-tablero` |
| `P1_PROBLEMA_SAMUEL_JACOBO.md` (encargo para personas, entrega a las 9:00 p. m.) | Samuel y Jacobo | `samuel-bot` |
| `P2_NOCHE_SAMUEL_JACOBO.md` (trabajo de la noche, antes del congelamiento) | Samuel y Jacobo | sus ramas |
| `P3_NOMBRE_IMAGEN_BANCO.md` (nombre, imagen, voz, video y visita al Banco) | Samuel y Jacobo | sus ramas |
| `P4_CARGA_START_TABLERO.md` (15.000 mensajes en local, /start y diseño del tablero) | Samuel y Jacobo | sus ramas |

Los demás son historia: ya se ejecutaron o fueron reemplazados.
