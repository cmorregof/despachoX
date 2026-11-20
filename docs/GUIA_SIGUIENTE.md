# Guía de trabajo · viernes 3:15 p. m.

> Las tareas vigentes de cada persona están en `SAMUEL.md`, `JACOBO.md` y `CARLOS.md`, en la raíz. Esta guía conserva el «Paso 0» para correr todo en un solo computador, que ahora es el plan B del despliegue en la nube.

Qué hace cada uno a continuación. La escribe el capitán después de revisar el repositorio y el canal.

## Estado en cinco líneas

- **Bot:** corre con las claves reales. El extractor acertó 62 de 64 campos en quince mensajes de ejemplo. **Nadie le ha escrito todavía desde un teléfono.**
- **Tablero:** completo y probado en pantalla con los datos de prueba. Tiene un fallo conocido: con un plan aprobado, «Calcular plan» borra las rutas anteriores. Mientras se corrige, no se aprueba el plan hasta sumar el pedido nuevo.
- **Despacho:** optimizador, recálculo, red ampliada (ya reconoce La Siria) y carga de datos reales. 100 lugares con apodos.
- **Simulación:** primera corrida completa. Con 8 segundos de búsqueda el resultado no cambia: frente al despachador experto empatamos en puntos críticos, quedamos 1,8 puntos por debajo en el total y ahorramos 61 km por jornada. El barrido del peso de puntos críticos está en curso.
- **Sin hacer:** la ficha, las fuentes verificadas, el aliado, la trazabilidad y la carpeta de Drive.

## Paso 0 · Los tres juntos, ya (20 minutos)

En el computador de Carlos, con tres terminales en la carpeta principal y el `.venv` activo. En las tres:

```bash
export DESPACHOX_DB=/Users/cmorregof/Personal/despachoX/datos/despachox.db
```

```bash
# Terminal 1: datos limpios
git pull && python -m despacho.semilla --cargar --reiniciar

# Terminal 2: bot
python -m entrada.bot

# Terminal 3: tablero
streamlit run tablero/app.py
```

Sigan `docs/GUION_DEMO.md` desde «Paso a paso». Samuel escribe desde su teléfono, Jacobo opera el tablero, Carlos anota en `torre/CANAL.md` todo lo que falle. No se arregla nada en el momento. El cierre de la demo es **«avenida del Centro»**.

Hecho cuando: un mensaje del teléfono de Samuel aparece en el mapa, entra a un plan, y un cierre reportado por chat cambia una ruta.

---

## Samuel · el bot, la ficha y el pitch

**Ahora (hasta las 5:00 p. m.)**

1. Después del paso 0, mándale al bot diez mensajes como los escribiría un vecino: con errores, sin tildes, con lugares dichos a medias. Anota en `torre/CANAL.md` los que entendió mal. Esa lista vale más que la cifra de 62 de 64, porque son mensajes de una persona y no del equipo.
2. `docs/FICHA.md`, componentes 1, 2 y 3. Material:
   - Problema: `docs/investigacion/04_evidencia_del_problema.md`, sección «Las 8 cifras más fuertes». **Abre cada enlace** antes de usar la cifra y pásala a `docs/FUENTES.md` con la fecha de corte.
   - Prototipo: lo que viste funcionar en el paso 0, más la tabla de `docs/SIMULACION.md`.
   - Conocimiento: `docs/investigacion/06_patentes_sipi.md` y la regla «el modelo lee, el optimizador calcula, el despachador decide».
3. Crea la carpeta del equipo en Drive, compártela con «cualquier persona con el enlace puede ver» y pega el enlace en el canal. La entrega de mañana es un enlace de Drive registrado en iNNOVO.
4. En iNNOVO: marca las tareas del tablero del equipo que ya están hechas.

**Mentoría:** tú presentas. Tres minutos: problema, demo, qué hay detrás. Usa `pitch/GUION.md`.

**Noche:** componentes 4, 5 y 6 a partir de `docs/FICHA_4_5_6_BORRADOR.md`, con lo que digan los mentores. Un ensayo cronometrado del pitch. Luego duermes: mañana presentas.

**La pregunta que debes poder responder:** «¿Qué pasa si la IA entiende mal un mensaje?» Respuesta corta: le contesta a la persona lo que entendió, le pide confirmar el lugar con botones, y nada entra al plan sin que el despachador lo confirme. Pídele a Claude que te explique `entrada/flujo.py` y que te haga cinco preguntas difíciles.

---

## Jacobo · el tablero y la demo

**Ahora (hasta las 5:00 p. m.)**

1. Después del paso 0, recorre el guion dos veces más tú solo, como un despachador con prisa. Anota en `torre/TORRE_JACOBO.md`: qué botón buscaste y no encontraste, qué texto sobra, qué no se lee desde lejos. Proyecta o aleja la pantalla para probarlo.
2. A las 4:00 p. m. ve a la charla que más sirva (prototipo o pitch) y trae tres ideas.
3. Escríbeles a Nicolás y a José Manuel: que entren a https://innovo-hub.netlify.app con su correo UNAL para quedar vinculados al equipo. Tú también.
4. Cuando la sesión del tablero suba la tercera ronda (botón de punto crítico, pestaña «Entregas», corrección de «Calcular plan»), vuelve a probar y confirma en el canal que funciona.

**Mentoría:** tú operas el tablero mientras Samuel habla. Ensaya los clics hasta no tener que mirar.

**Noche:** el video de respaldo. Graba la pantalla siguiendo la «Versión de 75 segundos» de `docs/GUION_DEMO.md`, con la base recién reiniciada. Súbelo a la carpeta de Drive. Si la demo falla mañana, se reproduce ese video.

**La pregunta que debes poder responder:** «¿Quién decide?» Respuesta corta: el sistema propone un plan y muestra qué cambió; el despachador lo aprueba o lo rechaza con su nombre, y queda en la bitácora. Pídele a Claude que te explique `tablero/app.py` y la tabla `planes`.

---

## Carlos · integración, sesiones y personas

**Ahora**

1. Dirigir el paso 0.
2. Lanzar la tercera ronda. El mismo mensaje en las sesiones de despacho, tablero y simulación:
   ```
   Haz git pull --rebase, lee las entradas nuevas de torre/CANAL.md y ejecuta tu parte de encargos/RONDA_3.md.
   ```
   Orden de urgencia: tablero (el fallo de «Calcular plan»), despacho (trazabilidad y el campo de empaque), simulación (barrido).
3. La mesa de organización, que sigue pendiente:
   - que compartan las carpetas del kit, sobre todo el **formato de prototipo MVP** y la **plantilla de presentación**;
   - en qué franja de mentoría va DespachoX (5:00 o 7:00 p. m.);
   - si el pitch de preselección escoge por vertical o por puntaje global, y cuánto dura;
   - con Fernando Bernal: la anualidad 2026 de la patente 37476 y qué se necesita para usarla en un piloto.
4. Un profesor de logística de la Sede: quince minutos para revisar la formulación.
5. El contacto del Banco de Alimentos de Manizales o de cualquier organismo de socorro presente. Tres preguntas: cómo decidieron a dónde mandar primero, qué se dañó o se quedó, qué no supieron a tiempo.

**Mentoría:** anotas cada observación, textual y con hora, en `torre/CANAL.md`.

**Noche:** revisar lo que suban las tres sesiones, decidir el peso de puntos críticos con el resultado del barrido y actualizar las cifras del guion.

**La pregunta que debes poder responder:** «¿Por qué no basta una regla simple, si empata?» Respuesta en `pitch/GUION.md`, tabla de preguntas.

---

## Reglas para las próximas horas

- La base compartida se reinicia antes de cada ensayo (`python -m despacho.semilla --cargar --reiniciar`). Un segundo pedido del mismo barrio en dos horas queda como duplicado y el plan lo ignora.
- Las claves no salen del `.env` de Carlos. Si el token se filtra, `/revoke` en BotFather.
- Sábado 8:30 a. m.: se congelan las funciones.
- Sábado 1:00 a 2:30 p. m.: entrega en iNNOVO. Sábado 2:30 p. m.: pitch de preselección.
