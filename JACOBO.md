# Tareas de Jacobo

Dueño del **tablero** (`tablero/`) y operador de la **demo**.

Marca con `[x]` lo que termines. Luego `git pull --rebase && git push`. Trabaja en tu rama `jacobo-tablero`: cada push a `main` reinicia el servidor de todos.

## Tarea 0 · Entender el problema (antes que nada)

- [ ] Lee `docs/PROBLEMA.md` completo y responde en voz alta las cinco preguntas del final.
- [ ] Lee el `README.md`.

## Tarea 1 · Usar el tablero como un despachador con prisa (30 minutos)

- [ ] Abre el [tablero](https://conviteman.up.railway.app/) y recorre `docs/GUION_DEMO.md` desde «Paso a paso», dos veces. Si el mapa sale gris en Brave, desactiva los escudos para esa página.
- [ ] Anota en la tabla qué botón buscaste y no encontraste, qué sobra, qué no se lee a dos metros.

| Qué vi | Dónde | Qué propongo |
|---|---|---|
| | | |

Esa tabla es la entrada de tu tarea 2.

## Tarea 2 · Dirigir a Claude Code para mejorar el tablero

- [ ] Abre Claude Code en tu copia del repositorio y escribe: «Haz git pull --rebase, lee `encargos/C2_TABLERO_JACOBO.md` y ejecútalo». No hace falta pegar el archivo. Dale tu tabla de la tarea 1.
- [ ] Etapa 1 (el fallo de «Calcular plan», reiniciar datos, completar pedidos incompletos) antes de las 6:30 p. m.
- [ ] Etapa 2: el **resumen de la mesa** hecho por un modelo, para cuando hay miles de pedidos.
- [ ] Etapa 3: filtros, agrupación y prueba con 1.000 pedidos.
- [ ] Revisa lo que haga antes de pedir que lo fusionen. Si no lo entiendes, pídele que te lo explique.

**La pregunta que debes poder responder:** «¿Quién decide, el sistema o la persona?» y «¿cómo lee el despachador mil pedidos?».

## Tarea 3 · El tablero sin internet

Diseño completo en `docs/SIN_CONEXION.md`. Pídeselo a tu sesión de Claude Code cuando termine la etapa 1 de C2:

- [ ] **Mapa de fondo sin conexión** con `DESPACHOX_MAPA=local`: dibujar como fondo las vías de la red guardada en disco (`despacho/cache/`), en gris claro, en vez de las teselas de OpenStreetMap. **No descargar teselas en bloque**: la política de uso de los servidores de OpenStreetMap lo prohíbe. La red vial ya la tenemos, así que el fondo sale de ahí.
- [ ] Botón **«Imprimir hojas de ruta»** con el plan aprobado, que llama `despacho.hoja.generar` y ofrece los PDF para descargar. Carlos avisa por el canal cuando la función exista.
- [ ] Registrar entregas por código de paquete (lo que el conductor trae anotado en la hoja).

## Tarea 4 · La demo y su respaldo

- [ ] Entra a https://innovo-hub.netlify.app con tu correo UNAL y pídeles a Nicolás y a José Manuel que hagan lo mismo.
- [ ] Ensaya la «Versión de 75 segundos» de `docs/GUION_DEMO.md` hasta hacer los clics sin mirar.
- [ ] Esta noche, con los datos recién reiniciados, graba la pantalla haciendo esa versión. Súbela a la carpeta de Drive. Enlace: ______

## Tarea 5 · Pestaña «Territorio» (mentoría 1)

- [ ] Pídele a tu Claude Code la parte C de `encargos/T1_TERRITORIO.md`: una pestaña con la tabla por comuna y vereda y la lista de barrios sin pedidos. Puede empezar antes de que exista `despacho/territorio.py`; mientras tanto, la pestaña dice «Pendiente».
- [ ] Va después de la etapa 1 de C2 (lo que rompe la demo) y antes del mapa sin internet.

## Tarea 6 · Enamorarse del problema, con Samuel (encargo P1)

- [ ] Lee `encargos/P1_PROBLEMA_SAMUEL_JACOBO.md`. Es un encargo para ustedes, no para Claude Code.
- [ ] Habla esta noche con personas reales (Banco de Alimentos, una líder de junta, un conductor) usando el guion de `docs/MENTORIA_1.md`.
- [ ] Entrega `docs/PROPUESTA_P1.md` y conversa cinco minutos con Carlos y Fable a las 9:00 p. m.

## Notas y bloqueos
