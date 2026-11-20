# Tareas de Carlos

Capitán. Dueño del **optimizador** (`despacho/`), la **simulación**, la **integración** y la nube.

Marca con `[x]` lo que termines.

## Hecho

- [x] Todo en la nube: bot y tablero en Railway desde las 3:45 p. m. Primer pedido real de punta a punta.

## Tarea 1 · Integrar sin romper la nube

Samuel y Jacobo trabajan en ramas. Tú eres el único que fusiona a `main`.

- [ ] Desactiva el despliegue automático en Railway o acepta que cada fusión reinicia el bot unos segundos.
- [ ] Fusiona a horas fijas: **6:30 p. m.** (antes de la mentoría de las 7:00), **11:00 p. m.** y **8:00 a. m.** (antes del congelamiento). Antes de fusionar: pruebas completas en verde.
- [ ] Detén tus sesiones de Claude Code `A-entrada` y `C-tablero`: ahora esos módulos los dirigen Samuel y Jacobo, y dos sesiones en el mismo módulo se pisan.
- [ ] Después de cada fusión, recorre el guion de demo en la nube.

## Tarea 2 · Tu parte técnica

En tu sesión `B-despacho`:

```
Haz git pull --rebase, lee las entradas nuevas de torre/CANAL.md y ejecuta la parte de B-despacho de encargos/RONDA_3.md. Trabaja en la rama carlos-despacho.
```

- [ ] El optimizador lee `empaque_activo` (patente UNAL 37476 como supuesto declarado).
- [ ] Trazabilidad mínima: paquetes con código al aprobar un plan.
- [ ] El plan anterior pasa a `reemplazado` al aprobar el nuevo.
- [ ] Un pedido urgente con cantidad supuesta sale marcado en el plan.
- [ ] Prueba en la nube el paso que falta: un cierre en la avenida del Centro por el bot, recalcular y aprobar.

## Tarea 3 · Despacho sin conexión

Cuando tu sesión termine la ronda 3:

```
Haz git pull --rebase, lee las entradas nuevas de torre/CANAL.md y ejecuta encargos/B3_SIN_CONEXION_CARLOS.md. Sigue en la rama carlos-despacho.
```

- [x] Hoja de ruta impresa por vehículo, con un QR por paquete.
- [ ] Arranque completo en un portátil con el wifi apagado. (`despliegue/local.sh` listo y probado con la red bloqueada; falta apagar el wifi de verdad.)
- [ ] Diapositiva de la escalera de degradación (`docs/SIN_CONEXION.md`) para el pitch.
- [ ] Caminar hasta un equipo de la vertical de energía y conectividad y proponer «su red, nuestra mesa de despacho» para el plan de 30 a 90 días.

## Tarea 4 · Lo que solo tú puedes hacer

Los criterios 3 y 5 (30 puntos) siguen en cero, y dependen de personas.

- [ ] **Mesa de organización:** carpetas del kit (formato de prototipo MVP y plantilla), franja de mentoría (5:00 o 7:00 p. m.), cómo se escoge en la preselección y cuánto dura el pitch.
- [ ] **Fernando Bernal:** anualidad 2026 de la patente 37476 y qué se necesita para usarla en un piloto.
- [ ] **Un profesor de logística de la Sede:** quince minutos. Nombre: ______
- [ ] **Un usuario real** (Banco de Alimentos, Cruz Roja, Defensa Civil o gestión del riesgo). Nombre y cargo: ______
- [ ] Mostrarle el bot y el tablero en vivo a ese usuario. Una frase suya vale más que cualquier función.

## Notas y bloqueos
