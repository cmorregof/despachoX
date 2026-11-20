# Encargo S2 · Subir el nivel de la simulación (sesión simulacion)

Haz `git pull --rebase`. Tu rama ya está fusionada en `main`: trabaja desde `main` en tu árbol de trabajo, solo en `despacho/sim/` y `docs/SIMULACION.md`.

Fable añadió a `despacho/optimizar.py` la constante `FACTOR_CRITICO`, que multiplica el peso del retraso y la penalización por no atender de los pedidos de puntos críticos. Se lee de la variable de entorno `DESPACHOX_FACTOR_CRITICO` y hoy vale 1, que reproduce tus resultados. Nadie la ha medido.

## 1. Barrido del factor

- Corre `despachox` y `experta` con factor 1, 3, 10 y 30, las mismas 30 semillas, en carga media y alta, con 1 s por llamada.
- Reporta por factor: críticos a tiempo, entregas a tiempo de todos los puntos, espera en el punto peor atendido y kilómetros, con la diferencia pareada frente a `experta`.
- Elige el valor con una regla escrita antes de mirar: el menor factor con el que `despachox` no es peor que `experta` en críticos a tiempo ni en entregas a tiempo de todos los puntos (intervalo que incluya el cero o sea favorable). Si ninguno lo logra, dilo.
- Para no elegir y evaluar sobre las mismas semillas, confirma el factor elegido en 30 semillas nuevas (20261150 a 20261179). Las cifras del pitch salen de esas.
- Propón por el canal el cambio del valor por defecto en `optimizar.py`. Lo aplica B o Carlos.

## 2. Lo que la primera versión no medía

Elige según el tiempo, en este orden de valor:

1. **Información imperfecta.** Hoy todas las políticas reciben pedidos y cierres perfectos. Añade un parámetro de error de ubicación: con probabilidad p, un cierre se registra tarde (hasta que alguien lo confirma) o un pedido llega con el punto equivocado y se corrige al confirmar. Corre con p de 0, 0,1 y 0,2. Esto mide de forma aproximada el valor de la confirmación.
2. **Tiempo de búsqueda.** Repite un nivel de carga con 1, 3 y 8 segundos por llamada, para saber si la demo (8 s) se comporta mejor que la simulación (1 s).
3. **Sensibilidad.** Número de cierres por jornada (0, 5, 10) y tamaño de la flota (menos dos vehículos).

## 3. Entrega

Actualiza `docs/SIMULACION.md` conservando la tabla original, añade las nuevas con su fecha y deja al día «Lo que esta simulación no prueba». Escribe en el canal un AVISO para Fable con las tres cifras que irían al pitch y su línea base. Reporta lo que salga, también si el factor no ayuda.

**Aporta a:** criterio 6 (indicadores medidos) y criterio 2 (evidencia).
