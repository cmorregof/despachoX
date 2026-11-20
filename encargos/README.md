# Encargos para Claude Code

Cada archivo es un mensaje listo para pegar en Claude Code, abierto en la raíz del repositorio. `CLAUDE.md` se carga solo, así que el encargo no repite las reglas del equipo.

Modelo: Fable 5.2.

```
git pull
pip install -r requirements.txt
claude --model claude-fable-5-2
```

| Encargo | Quién | Cuándo |
|---|---|---|
| `0_MAESTRO.md` | Carlos | Una vez, al comienzo. Audita el plan, propone mejoras y afina los otros tres |
| `A_ENTRADA_SAMUEL.md` | Samuel | Ya |
| `B_DESPACHO_CARLOS.md` | Carlos | Ya |
| `C_TABLERO_JACOBO.md` | Jacobo | Ya |

Los tres encargos de rol se pueden empezar sin esperar al maestro. Si el maestro cambia algo, avisa en `docs/SUGERENCIAS.md` y cada uno hace `git pull`.
