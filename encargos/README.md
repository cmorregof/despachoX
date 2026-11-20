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
