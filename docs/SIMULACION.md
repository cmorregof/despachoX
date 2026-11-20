# Simulación: cuánto mejora DespachoX frente a un despacho sin optimizador

Estado: **BORRADOR**. El diseño y los supuestos están completos. La sección 5 no tiene todavía resultados citables.

Código en `despacho/sim/`. Se reproduce con `python -m despacho.sim.correr --carga todas`.

## 1. Qué pregunta responde

La ficha del reto fija dos indicadores: el porcentaje de entregas a tiempo en puntos críticos y el desperdicio de perecederos, que debe quedar por debajo del 5 %. La simulación mide esos dos indicadores para cuatro formas de despachar la misma jornada, con los mismos pedidos, la misma flota y los mismos cierres viales. La diferencia entre ellas es lo que se le puede atribuir a DespachoX.

## 2. Diseño

**Red.** El grafo de conducción de Manizales y Villamaría de OpenStreetMap, el mismo archivo que usa el optimizador (`despacho/cache/manizales.graphml`). La simulación aplica las velocidades y las reglas de acceso de `despacho/red.py` y `despacho/matriz.py`, de modo que el plan y la jornada simulada describen la misma ciudad. Una prueba compara las dos matrices de tiempos y falla si difieren en más de un segundo.

**Escenario.** Cada semilla genera una jornada completa:

- Entre 30 y 80 puntos de entrega sobre nodos de la red, a 6 km del centro como máximo y separados al menos 250 m. El 20 % son críticos.
- Un acopio, sobre la vía apta para camión más cercana a la plaza de Bolívar.
- Pedidos: el 40 % ya está en cola al empezar y el resto llega en momentos uniformes durante las primeras 8 horas. Cada pedido atiende entre 3 y 50 familias, a 12 kg por familia, y entre el 20 % y el 50 % de su peso es perecedero.
- Urgencia y plazo: los puntos críticos piden con urgencia 3 el 80 % de las veces. El plazo de entrega es de 3 horas para urgencia 3, 5 horas para urgencia 2 y 8 horas para urgencia 1.
- Inventario perecedero: tantos kilos como piden los pedidos, en lotes de 100 a 400 kg que vencen entre 6 y 48 horas después del inicio.
- Flota mixta: un camión de 3.000 kg por cada 30 puntos, un campero de 700 kg por cada 15 y una moto de 60 kg por cada 20.
- Cierres: entre 3 y 8 tramos cerrados por jornada, en los dos sentidos. El 30 % existe desde la hora cero y los demás ocurren durante las primeras 8 horas. Cada cierre bloquea siempre al camión, al campero con probabilidad 0,7 y a la moto con probabilidad 0,3. No se levantan durante la jornada.

**Cómo se conoce un cierre.** Nadie lo sabe hasta que un vehículo intenta pasar. El conductor pierde 3 minutos, reporta y se desvía. El reporte desvía también a los vehículos que iban hacia ese tramo, en todas las políticas. El despacho confirma el cierre 5 minutos después del reporte.

**Motor.** Simulador de eventos discretos. Los vehículos avanzan tramo a tramo por la red verdadera, mientras que los caminos se calculan con la red conocida, que no incluye los cierres sin reportar. El motor impone tres reglas a cualquier política: ningún vehículo carga más que su capacidad, un kilo perecedero que llega después del vencimiento de su lote no cuenta como entregado, y un cierre desconocido no cambia ninguna ruta. Las tres están cubiertas por pruebas en `despacho/sim/tests/`.

**Jornada.** La simulación se corta a las 14 horas. Lo que no se entregó para entonces cuenta como no entregado.

## 3. Políticas comparadas

| Política | Qué hace |
|---|---|
| `ingenua` | Atiende por orden de llegada. Al pedido más antiguo le asigna el vehículo libre que llega más rápido y lo llena con los siguientes pedidos de la cola. El conductor ordena sus entregas por vecino más cercano. Saca los lotes de bodega por orden de ingreso. Se desvía solo al toparse un cierre. |
| `experta` | La ingenua con dos reglas de un despachador con oficio: atiende primero lo más urgente y saca de bodega primero lo que vence primero. |
| `optimiza_una_vez` | El optimizador planea al inicio con los pedidos que hay y no vuelve a calcular. Lo demás se atiende con la regla ingenua. |
| `despachox` | El optimizador planea al inicio y recalcula con cada cierre confirmado, con cada tanda de pedidos (cada 30 minutos) y cada vez que un vehículo vuelve al acopio. |

La política `experta` no estaba en el encargo. Se añadió porque un despachador real no ignora la urgencia, y porque la literatura muestra que una política intuitiva puede quedar cerca del óptimo (Cook y Lodree, 2017). La comparación de `optimiza_una_vez` con `despachox` aísla lo que aporta recalcular.

**El optimizador** es el de `despacho/optimizar.py`: OR-Tools con capacidad, una red por tipo de vehículo, ventana dura hasta el vencimiento del perecedero, retraso ponderado por urgencia y penalización por pedido sin atender. La simulación llama a su modelo con un límite de búsqueda de 1 segundo por llamada. El modelo planea un viaje por vehículo y solo asigna pedidos nuevos a los vehículos que están en el acopio, por eso `despachox` lo vuelve a llamar cuando un vehículo regresa.

**Ventajas que se le dieron a la línea base.** Decide al instante, mientras que cada plan del optimizador espera 2 minutos la aprobación del despachador y solo se revisa un plan a la vez. Ve cada pedido apenas llega, mientras que `despachox` lo ve en la siguiente tanda o cuando regresa un vehículo. Sus conductores reciben el aviso de cada cierre igual que los de DespachoX. Su tope de paradas por viaje se eligió con semillas de calibración, distintas de las de evaluación, y se dejó en el valor que mejor le fue, que es no tener tope.

## 4. Métricas y estadística

- **Entregas a tiempo en puntos críticos:** pedidos de puntos críticos entregados antes de su hora límite, sobre el total de pedidos de puntos críticos. Un pedido sin entregar cuenta como tarde.
- **Perecederos vencidos:** kilos de lotes que vencen dentro de la jornada y no se entregaron antes de vencer, sobre el total de kilos perecederos en bodega. Incluye lo que venció en bodega, a bordo o al llegar tarde.
- Además: entregas a tiempo en todos los puntos, pedidos entregados, kilos que no llegaron en buen estado, tiempo medio y máximo del pedido a la entrega, espera media en el punto peor atendido, kilómetros de la flota y segundos de cada llamada al optimizador.

Cada nivel de carga se corre con 30 semillas (20261120 a 20261149), las mismas para todas las políticas. Se reporta la diferencia pareada por semilla con su intervalo de confianza del 95 % (t de Student, 29 grados de libertad) y el número de semillas en que cada política gana, empata o pierde.

**Niveles de carga.** La demanda se fija en 2, 2,5 o 3 pedidos por punto en la jornada (carga holgada, media y alta). Los niveles se eligieron con las semillas de calibración 100 a 111, mirando solo a la política ingenua: cumple cerca del 86 %, el 74 % y el 52 % de los pedidos críticos a tiempo. Con una demanda menor todas las políticas entregan casi todo a tiempo y la comparación no mide nada.

## 5. Resultados

Pendiente. La tabla se copiará tal como salga de `despacho/sim/resultados/resumen.md`.

## 6. Supuestos

Todos son supuestos nuestros, no datos medidos, salvo el trazado de la red vial.

| Supuesto | Valor |
|---|---|
| Velocidad por tipo de vía | La de `despacho/red.py`: 40 km/h en vía primaria, 35 en secundaria, 30 en terciaria, 20 en residencial, o el `maxspeed` de OpenStreetMap si existe |
| Factor por vehículo | Camión 1,25 veces el tiempo base, campero 1,0, moto 0,9 |
| Acceso del camión | No entra a vías residenciales ni de servicio. Atiende un punto si hay una vía apta a 300 m o menos |
| Vehículo sin regreso por su red | Sale por cualquier vía de conducción, también en contravía, al doble del tiempo |
| Vehículo sin ningún regreso | Sale de servicio, su carga se pierde y sus pedidos vuelven a la cola |
| Tiempo de carga en el acopio | 10 minutos por viaje |
| Tiempo por entrega | 10 minutos, igual que en el optimizador |
| Tiempo perdido al toparse un cierre | 3 minutos |
| Confirmación humana de un cierre | 5 minutos |
| Aprobación humana de un plan | 2 minutos, un plan a la vez |
| Tanda de pedidos | cada 30 minutos |
| Extracción de pedidos y cierres por el modelo de lenguaje | sin errores |
| Pedidos | no se parten entre vehículos |
| Inventario no perecedero | ilimitado |
| Acopios | uno solo |
| Demanda, flota, inventario y cierres | sintéticos |

Los cierres se sortean entre los tramos que usan los caminos más cortos del acopio a los puntos, con probabilidad proporcional al número de caminos que pasan por cada uno. Se hizo así porque un cierre en una calle que ningún vehículo usa no pone a prueba a ninguna política. La consecuencia es que los cierres de la simulación estorban más que cierres sorteados al azar sobre toda la red.

## 7. Lo que esta simulación no prueba

Pendiente de redactar con los resultados a la vista.
