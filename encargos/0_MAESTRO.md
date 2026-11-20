# Encargo 0 · Maestro (lo corre Carlos, con Fable 5.2)

Soy Carlos, capitán de DespachoX. Estamos a viernes 20 de noviembre y la mentoría 1 es a las 7:00 p. m. Hoy trabajamos tres personas: Samuel (A, entrada, y la ficha), yo (B, despacho) y Jacobo (C, tablero).

Lee, en este orden: `CLAUDE.md`, `docs/ESTRATEGIA.md`, `docs/ESTADO_DEL_ARTE.md`, `docs/ROLES_VIERNES.md`, `datos/esquema.sql`, `datos/db.py`, los tres encargos de `encargos/` y `torre/TORRE_CAPITAN.md`. Los informes de `docs/investigacion/` solo si necesitas un detalle.

No escribas código del producto en este encargo. Haz tres cosas.

## 1. Auditoría crítica del plan → `docs/SUGERENCIAS.md`

Quiero que busques dónde podemos perder, no que confirmes el plan. Entrega como máximo diez sugerencias, ordenadas por puntos de rúbrica ganados por hora de trabajo. Para cada una:

- qué cambiar, en una frase;
- a qué criterio de la rúbrica le suma y cuánto (estimado, dilo como estimado);
- cuánto cuesta en horas y quién la haría;
- qué dejamos de hacer para caber.

Revisa en particular:
- si el alcance cabe en tres personas hasta las 7:00 p. m. y qué cortarías primero;
- si el contrato de datos tiene huecos (campos que A no puede llenar, que B necesita o que C no puede mostrar);
- cómo se ubica en el mapa un lugar dicho en lenguaje libre («derrumbe en La Siria»), que es el punto más frágil de la demo;
- si la simulación con tres políticas y 30 semillas es defendible ante un jurado de ingeniería industrial;
- si las capacidades UNAL elegidas (indicador A25 del IDEA, patente del empaque captador de etileno) cambian de verdad una decisión del sistema o son decorativas;
- qué preguntaría un jurado escéptico y qué no sabríamos responder hoy.

Cierra con una sección «Guion de demo de tres minutos»: la secuencia exacta de mensajes y clics, con datos fijos, que muestra pedido, cierre vial, recálculo y aprobación.

## 2. Coherencia de los tres encargos

Verifica que `A_ENTRADA_SAMUEL.md`, `B_DESPACHO_CARLOS.md` y `C_TABLERO_JACOBO.md` usan los mismos nombres de tablas, columnas y estados que `datos/esquema.sql`, y que ninguno depende de algo que otro no produce. Corrige los encargos si encuentras un desajuste y lista los cambios al final de `docs/SUGERENCIAS.md`. Si hace falta cambiar el esquema, propón el cambio y espera mi visto bueno antes de tocarlo.

## 3. Trabajo en paralelo

Si la auditoría y la revisión de coherencia se pueden repartir, lanza un agente Opus para la auditoría del optimizador y la simulación, y uno Sonnet para cruzar encargos contra esquema. Revisa lo que devuelvan antes de escribirlo.

## Al terminar

Actualiza `torre/TORRE_CAPITAN.md`, y propón el commit `[capitán] sugerencias y ajuste de encargos`. No cambies `docs/ESTRATEGIA.md` sin preguntarme.

**Aporta a:** todos los criterios; sobre todo protege el 2 (que la demo funcione) y el 1 (que el problema se cuente con evidencia).
