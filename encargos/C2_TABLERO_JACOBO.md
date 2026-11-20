# Encargo C2 · La mejor mesa de despacho posible (Jacobo)

Pégalo en Claude Code abierto en la carpeta del repositorio, con el modelo que tengas (Opus 5.5 si tu plan lo permite). Tienes plan Pro: no leas archivos que no hagan falta y no lances agentes en paralelo salvo que ahorren tiempo de verdad.

---

Soy Jacobo, dueño de `tablero/` (la pantalla del despachador). Te llamas `C-tablero` en `torre/CANAL.md`; mi torre es `torre/TORRE_TABLERO.md`. Desde ahora soy yo quien dirige este módulo.

Lee, en este orden y nada más: `docs/PROBLEMA.md`, `tablero/README.md`, `torre/TORRE_TABLERO.md`, las entradas de `torre/CANAL.md` desde las 14:30, la parte de C en `encargos/RONDA_3.md` y `tablero/datos.py`.

**Rama de trabajo.** No trabajes en `main`: cada push a `main` redespliega el servidor y corta las pruebas de todos. Haz `git pull --rebase`, crea la rama `jacobo-tablero` y sube ahí. Cuando una etapa esté probada, abre un pull request a `main` y avísale a Carlos por el canal: él fusiona a horas fijas.

## Etapa 1 · Lo que hoy rompe la demo (antes de las 6:30 p. m.)

1. **Fallo conocido:** con un plan aprobado, «Calcular plan» ejecuta `despacho.optimizar` y las rutas de los pedidos ya asignados desaparecen. Con plan aprobado debe ejecutar `despacho.recalcular --motivo "pedido nuevo"`. Pasa `--segundos 3` en ambos.
2. Botón **«Reiniciar datos de prueba»**, escondido en un menú y con confirmación, que ejecute `python -m despacho.semilla --cargar --reiniciar`. Hace falta para ensayar en la nube.
3. Un pedido con familias o kilos vacíos se puede completar en el tablero antes de confirmarlo (familias y productos). Es lo que pasó con «6 bebés sin leche en La Enea».

**Hecho cuando:** el guion de `docs/GUION_DEMO.md` funciona completo con el plan inicial aprobado, y las pruebas de `tablero/` pasan.

## Etapa 2 · Un resumen hecho por un modelo, para cuando los pedidos son miles

Quien despacha no puede leer mil mensajes en un día. Un panel «Resumen de la mesa» le dice en diez líneas qué está pasando.

Diseño obligatorio, para que sea barato, rápido y honesto:

1. **Las cuentas las hace SQL, no el modelo.** `tablero/resumen.py` arma primero un resumen numérico desde la base: pedidos por estado, por urgencia y por comuna; productos más pedidos y faltantes de inventario; pedidos sin ubicar o con datos incompletos; posibles duplicados; cierres activos; el pedido más antiguo sin atender por urgencia; puntos críticos sin plan.
2. **El modelo solo redacta.** Recibe ese resumen en JSON más, como máximo, los 30 textos más urgentes sin atender. Nunca la lista completa. Usa `claude-opus-5-5` (configurable con `DESPACHOX_MODELO_RESUMEN`). Devuelve hasta seis viñetas: qué está pasando, qué zona acumula urgencias, qué falta en bodega, qué conviene revisar primero. **Cada viñeta cita los números de pedido** en que se apoya, y el tablero los vuelve enlaces o los resalta.
3. **No decide.** El texto propone qué revisar; no aprueba, no descarta, no reprioriza. Lo dice en una línea debajo del panel.
4. **Se genera con un botón** («Resumir la mesa») y se guarda con su hora. No en cada actualización de cinco segundos: eso costaría cientos de llamadas por hora.
5. Si no hay clave o el modelo falla, el panel muestra solo el resumen numérico.
6. Pruebas con el modelo falso: el resumen numérico cuadra con la base y el texto nunca cita un pedido que no existe (si lo hace, se descarta esa viñeta).
7. Mide el costo de una llamada con 1.000 pedidos sintéticos y anótalo en tu torre.

## Etapa 3 · La pantalla para alguien con prisa y para miles de pedidos

1. «Por revisar» deja de ser una lista larga: filtros por urgencia y por comuna, agrupado por punto, y los críticos primero. Muestra 20 y un «ver más».
2. Confirmar varios pedidos de una vez.
3. Pedidos del mismo punto en poco tiempo, agrupados bajo uno con «se repitió 3 veces».
4. Que se lea proyectado: textos grandes, pocos colores con significado fijo (rojo = urgente o cierre), nada que dependa solo del color.
5. Prueba con 1.000 pedidos sintéticos que la pantalla siga cargando en menos de tres segundos. Si no, pagina las consultas.

## Reglas

- El tablero solo cambia estados y completa datos que un humano escribe; las rutas las calcula `despacho/`.
- No toques `despacho/`, `entrada/`, `lugares/` ni `datos/esquema.sql`. Si necesitas una columna, pídela por el canal.
- Al cerrar cada etapa: torre al día, entrada LISTO en el canal, push a `jacobo-tablero` y aviso a Carlos.
