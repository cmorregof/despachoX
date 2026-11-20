# Tarea 0 · Verificar las referencias

**Cuándo:** viernes, antes de las 2:30 p. m. (el almuerzo de 12:00 a 2:00 es el mejor rato). **Tope:** 40 minutos por persona.

**Por qué:** los cinco informes de `docs/investigacion/` los escribieron agentes de IA. Traen enlaces, pero ningún humano los ha abierto. Una cifra falsa en el pitch nos cuesta más puntos que no tener cifra. Además, quien verifica un informe queda como el experto del equipo en ese tema cuando pregunte el jurado.

## Reparto

Un informe por persona. Carlos confirma los nombres.

| Informe | Quién | Por qué esa persona |
|---|---|---|
| `01_estado_del_arte_tecnico.md` | El ingeniero industrial | Es quien va a formular el ruteo y la simulación (rol B) |
| `02_referentes_latinoamerica.md` | Samuel | Como líder necesita el relato y los referentes para el pitch |
| `03_capacidades_y_patentes_unal.md` | Carlos | Conoce a los profesores y va a la mesa a preguntar por patentes y datos |
| `04_evidencia_del_problema.md` | Quien tome el rol D | Son las cifras de la ficha y de la primera diapositiva |
| `05_datos_abiertos_y_aliados.md` | Quien tome el rol A o C | Son los datos y las librerías que va a usar esta tarde |

## Qué hace cada uno

1. Lee primero `docs/ESTADO_DEL_ARTE.md` (cinco minutos) y luego su informe completo.
2. Abre los enlaces de las afirmaciones que podríamos usar en el pitch o en el diseño. No hace falta abrirlos todos: primero los de la sección de cifras fuertes o de recomendaciones.
3. Crea `docs/investigacion/verificacion_0X.md` (con el número de su informe) y llena esta tabla:

```
| Afirmación | Enlace | Resultado | Nota |
|---|---|---|---|
| ... | ... | ✔ confirma / ✘ no dice eso / ⚠ dice otra cosa / ☠ enlace caído | qué dice de verdad, con fecha de corte |
```

4. Al final del archivo escribe tres cosas:
   - **Las 3 cosas que sí usaría** en el pitch o en el diseño.
   - **Lo que encontró falso o dudoso.**
   - **Una pregunta** que haría hoy a un mentor, asesor u organizador.
5. Hace commit y push: `[tarea 0] verificación informe 0X`.

## Reglas para no pisarnos

- Cada uno toca solo su archivo `verificacion_0X.md`. Nadie edita los informes originales ni `FUENTES.md` en esta tarea.
- Quien tenga el rol D pasa después las afirmaciones con ✔ a `docs/FUENTES.md`.
- Se puede usar Claude para leer más rápido, pero el enlace lo abre una persona. La IA ya lo «verificó» una vez; el punto es el segundo par de ojos.
- Si algo clave sale ✘ o ⚠, avisar de una vez al capitán por el grupo. No esperar al cierre.

## Cierre (2:15 p. m., diez minutos, de pie)

Cada uno dice sus tres cosas y su pregunta. El capitán ajusta `docs/ESTRATEGIA.md` y la torre con lo que cambió, y arranca el trabajo de las 2:30.

**Aporta a:** criterio 1 (evidencia verificada), criterio 3 (capacidades UNAL reales) y criterio 5 (aliados y datos que existen).
