# Verificación de la velocidad medida

Generado por `python -m analisis.sensibilidad.verificar`. Velocidades en km/h, media por longitud (largo total entre segundos totales) de los tramos de cada tipo de vía del grafo `manizales_region.graphml`.

## 1. Velocidad media por tipo de vía: modelo, CSV y red parcheada (multiplicador 1)

| Tipo de vía | km del grafo | Vehículo | Modelo (travel_time × factor) | CSV | Simulación parcheada | Diferencia con el CSV |
|---|---:|---|---:|---:|---:|---:|
| unclassified | 2237,3 | camion | 20,2 | 21,9 | 21,9 | 0,00 |
| unclassified | 2237,3 | campero | 25,2 | 21,9 | 21,9 | 0,00 |
| unclassified | 2237,3 | moto | 28,0 | 24,4 | 24,4 | -0,00 |
| residential | 730,9 | camion | 16,0 | 21,9 | 20,9 | -1,01 |
| residential | 730,9 | campero | 20,0 | 21,9 | 21,9 | -0,00 |
| residential | 730,9 | moto | 22,2 | 24,4 | 24,4 | -0,00 |
| tertiary | 514,8 | camion | 24,0 | 17,1 | 17,1 | -0,00 |
| tertiary | 514,8 | campero | 30,0 | 17,1 | 17,1 | -0,00 |
| tertiary | 514,8 | moto | 33,3 | 19,0 | 19,0 | -0,00 |
| secondary | 387,9 | camion | 28,2 | 27,0 | 27,0 | 0,00 |
| secondary | 387,9 | campero | 35,3 | 27,0 | 27,0 | 0,00 |
| secondary | 387,9 | moto | 39,2 | 30,0 | 30,0 | 0,00 |
| trunk | 227,9 | camion | 38,2 | 26,5 | 26,5 | 0,00 |
| trunk | 227,9 | campero | 47,8 | 26,5 | 26,5 | 0,00 |
| trunk | 227,9 | moto | 53,1 | 29,4 | 29,4 | -0,00 |
| primary | 125,6 | camion | 30,6 | 23,3 | 23,3 | 0,00 |
| primary | 125,6 | campero | 38,2 | 23,3 | 23,3 | 0,00 |
| primary | 125,6 | moto | 42,5 | 25,9 | 25,9 | 0,00 |
| trunk_link | 10,5 | camion | 22,5 | 26,5 | 26,5 | 0,00 |
| trunk_link | 10,5 | campero | 28,1 | 26,5 | 26,5 | 0,00 |
| trunk_link | 10,5 | moto | 31,3 | 29,4 | 29,4 | 0,00 |
| primary_link | 5,5 | camion | 24,3 | 23,3 | 23,3 | 0,00 |
| primary_link | 5,5 | campero | 30,4 | 23,3 | 23,3 | 0,00 |
| primary_link | 5,5 | moto | 33,8 | 25,9 | 25,9 | 0,00 |
| secondary_link | 1,8 | camion | 20,2 | 25,0 | 25,0 | -0,00 |
| secondary_link | 1,8 | campero | 25,2 | 25,0 | 25,0 | -0,00 |
| secondary_link | 1,8 | moto | 28,0 | 27,8 | 27,8 | -0,00 |
| tertiary_link | 0,2 | camion | 20,0 | 17,1 | 17,1 | -0,00 |
| tertiary_link | 0,2 | campero | 25,0 | 17,1 | 17,1 | -0,00 |
| tertiary_link | 0,2 | moto | 27,8 | 19,0 | 19,0 | 0,00 |
| ladder | 0,1 | camion | 16,0 | 16,0 | 16,0 | 0,00 |
| ladder | 0,1 | campero | 20,0 | 20,0 | 20,0 | 0,00 |
| ladder | 0,1 | moto | 22,2 | 22,2 | 22,2 | 0,00 |

Mayor diferencia entre la red parcheada y el CSV: 1,006 km/h. El camión no tiene valor en las vías que no le son aptas (residential), porque no pasa por ellas.

## 2. Multiplicadores 0,8 y 1,2

| Multiplicador | Tipo de vía | Vehículo | CSV × multiplicador | Simulación parcheada |
|---:|---|---|---:|---:|
| 0,8 | primary | camion | 18,6 | 18,6 |
| 0,8 | primary | campero | 18,6 | 18,6 |
| 0,8 | primary | moto | 20,7 | 20,7 |
| 0,8 | secondary | camion | 21,6 | 21,6 |
| 0,8 | secondary | campero | 21,6 | 21,6 |
| 0,8 | secondary | moto | 24,0 | 24,0 |
| 0,8 | tertiary | camion | 13,7 | 13,7 |
| 0,8 | tertiary | campero | 13,7 | 13,7 |
| 0,8 | tertiary | moto | 15,2 | 15,2 |
| 0,8 | residential | camion | 17,5 | 16,7 |
| 0,8 | residential | campero | 17,5 | 17,5 |
| 0,8 | residential | moto | 19,5 | 19,5 |
| 1,2 | primary | camion | 28,0 | 28,0 |
| 1,2 | primary | campero | 28,0 | 28,0 |
| 1,2 | primary | moto | 31,1 | 31,1 |
| 1,2 | secondary | camion | 32,4 | 32,4 |
| 1,2 | secondary | campero | 32,4 | 32,4 |
| 1,2 | secondary | moto | 36,0 | 36,0 |
| 1,2 | tertiary | camion | 20,5 | 20,5 |
| 1,2 | tertiary | campero | 20,5 | 20,5 |
| 1,2 | tertiary | moto | 22,8 | 22,8 |
| 1,2 | residential | camion | 26,3 | 25,1 |
| 1,2 | residential | campero | 26,3 | 26,3 |
| 1,2 | residential | moto | 29,3 | 29,3 |

## 3. Simulación frente al optimizador, con el parche puesto

Misma comprobación que `test_misma_matriz_de_tiempos_que_el_optimizador`: segundos entre el acopio y los puntos de una semilla, calculados por `Conocimiento.tiempos` (simulación) y por `despacho.matriz.calcular` (optimizador). El optimizador redondea a segundos enteros.

| Multiplicador | Semilla | Vehículo | Mismos pares sin camino | Máxima diferencia (s) | Mediana del tiempo entre sitios (s) |
|---:|---|---|---|---:|---:|
| 1,0 | 20261150 | camion | sí | 0,50 | 767 |
| 1,0 | 20261150 | campero | sí | 0,50 | 695 |
| 1,0 | 20261150 | moto | sí | 0,50 | 625 |
| 1,0 | 20261151 | camion | sí | 0,50 | 758 |
| 1,0 | 20261151 | campero | sí | 0,50 | 681 |
| 1,0 | 20261151 | moto | sí | 0,50 | 612 |
| 1,0 | 20261152 | camion | sí | 0,50 | 777 |
| 1,0 | 20261152 | campero | sí | 0,50 | 751 |
| 1,0 | 20261152 | moto | sí | 0,50 | 676 |
| 0,8 | 20261150 | camion | sí | 0,50 | 958 |
| 0,8 | 20261150 | campero | sí | 0,50 | 869 |
| 0,8 | 20261150 | moto | sí | 0,50 | 782 |
| 0,8 | 20261151 | camion | sí | 0,50 | 948 |
| 0,8 | 20261151 | campero | sí | 0,50 | 851 |
| 0,8 | 20261151 | moto | sí | 0,50 | 766 |
| 0,8 | 20261152 | camion | sí | 0,50 | 971 |
| 0,8 | 20261152 | campero | sí | 0,50 | 939 |
| 0,8 | 20261152 | moto | sí | 0,50 | 845 |
| 1,2 | 20261150 | camion | sí | 0,50 | 639 |
| 1,2 | 20261150 | campero | sí | 0,50 | 579 |
| 1,2 | 20261150 | moto | sí | 0,50 | 521 |
| 1,2 | 20261151 | camion | sí | 0,50 | 632 |
| 1,2 | 20261151 | campero | sí | 0,50 | 567 |
| 1,2 | 20261151 | moto | sí | 0,50 | 510 |
| 1,2 | 20261152 | camion | sí | 0,50 | 647 |
| 1,2 | 20261152 | campero | sí | 0,50 | 626 |
| 1,2 | 20261152 | moto | sí | 0,50 | 563 |

Resultado: las dos matrices coinciden en todos los casos (tolerancia de 1 s).

## 4. Escenarios con cada multiplicador

Escalar todas las velocidades por el mismo número no cambia los caminos más cortos, así que los puntos, los críticos, los cierres, los pedidos y la flota de cada semilla deben quedar iguales. Comprobado en las semillas 20261150, 20261151, 20261152: iguales.

