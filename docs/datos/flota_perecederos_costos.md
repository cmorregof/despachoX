# Flota, vida útil de los alimentos, velocidades y costos

Este documento reúne datos públicos que pueden reemplazar cuatro supuestos del modelo: la flota, la vida útil de cada producto, la velocidad por tipo de vía y el costo de mover la ayuda. Todo se consultó el 20 de noviembre de 2026. Los datos están en cinco archivos de `datos_publicos/`: `vehiculos.csv`, `vehiculos_fuentes.csv`, `velocidades.csv`, `vida_util.csv` y `costos.csv`.

Cada cifra lleva una marca:

- **F**: la dice una fuente, con enlace al final.
- **C**: la calculamos a partir de cifras de una fuente.
- **M**: la medimos nosotros en archivos del repositorio.
- **S**: es un supuesto nuestro.

## 1. Lo que cambiaría en el modelo

Esta sección resume los cuatro hallazgos con efecto sobre el modelo. El detalle de cada uno está en las secciones 2 a 5.

1. **El modelo supone vías más rápidas que las medidas en Manizales.** Un bus diésel medido con GPS en Manizales promedió 22,6 km/h (F). En vías principales fue de 21,8 a 24,2 km/h, y en colectoras de 16,2 a 17,5 km/h (F). En cambio, el grafo del modelo le da al campero 39,0 km/h de media en vías `primary` y 54,7 km/h en `trunk` (M). Fuera de la ciudad, el SICE-TAC del Ministerio de Transporte supone 15 km/h para un camión de dos ejes en terreno montañoso (F). Así que los tiempos de viaje del modelo salen cortos, y el porcentaje de entregas a tiempo de la simulación puede estar inflado. Hay que volver a correr la simulación con `velocidades.csv` para saber cuánto.
2. **Solo cuatro casos vencen en horas.** El pollo crudo aguanta 2 h sin frío (F, FDA), y suponemos lo mismo para la leche pasteurizada (S). La leche de fórmula preparada, 2 h (F, CDC). El pan del día, 24 h (F, ICBF). En cambio, el huevo dura de 15 a 30 días según la temperatura (F, ICBF), el tomate maduro de 4 a 7 días (F, USDA) y la leche UHT al menos 90 días (F, ICBF). La semilla le da al huevo entre 26 y 42 h y a la fruta entre 8 y 47 h, y la simulación usa entre 6 y 48 h para todo perecedero (M). Así que el desperdicio simulado de huevos y fruta viene de esos supuestos y no de la evidencia.
3. **La fruta tropical no va al cuarto frío.** El banano se daña por debajo de 11,5 a 13 °C, y la papaya por debajo de 7 °C (F, FAO). La semilla solo manda al acopio con frío el pollo y la leche (M, `CON_FRIO` en `despacho/semilla.py`), y eso coincide con la evidencia.
4. **La flota de referencia tiene tres camiones, como los que reportó la prensa en Manizales.** Portafolio contó 3 camiones de los Bancos de Alimentos en Manizales tras el sismo (F). La flota propuesta suma 3 camiones, 4 vehículos livianos y 2 motos. Sus capacidades salen de fichas de fabricante y de pliegos públicos. No es la flota real de Manizales, porque ninguna fuente la describe.

## 2. Flota de referencia

Esta sección explica qué vehículos documentados usan las organizaciones de la ficha y cómo se armó `vehiculos.csv`.

### 2.1 Lo que dicen las fuentes por organización

- **Bancos de alimentos (ABACO).** El 16 de agosto de 2026 había 57 camiones vinculados a los Bancos de Alimentos, y Flypass pagó sus peajes (F, Portafolio). En Manizales había 3; en Medellín 26 y en Cali 13 (F). La nota no da modelo ni capacidad. ABACO usó a Manizales y a Buenaventura como centros de recepción (F, Portafolio, 21 sep 2026).
- **Banco de Alimentos.** En 2020 Dafiti le movía 3,5 t diarias de donaciones con repartidores en moto y un vehículo de 800 kg por viaje (F, La República). La nota no precisa la sede.
- **ICBF.** Su pliego de transporte de alimentos de 2015 exige camiones tipo furgón de 2,0 t o más, modelo 2007 o posterior, y el servicio se paga por kilo transportado (F).
- **UNGRD.** En diciembre de 2025 anunció equipos para 12 departamentos, entre ellos camionetas 4x4 y camiones cisterna (F, RTVC). Caldas está en la lista, pero la nota no dice qué recibe ni qué modelos son.
- **Cruz Roja Colombiana.** En 2020 Ford le prestó cinco vehículos, entre ellos una Ford Ranger XLT. Entre otras tareas, debían repartir alimentos a personas mayores aisladas (F). Tras el sismo, la Alcaldía de Bogotá, con la Cruz Roja de Bogotá y Cundinamarca, envió 172 vehículos de carga con 2.141 t hasta el 18 de agosto de 2026 (F). Eso da 12,4 t por vehículo en promedio (C): son viajes de larga distancia, no de reparto en barrios.
- **Defensa Civil.** No encontramos fuente sobre sus vehículos. La nota de El Heraldo sobre la dotación de 2024 en Atlántico no menciona vehículos (F).
- **Banco Arquidiocesano de Alimentos de Manizales.** Una monografía de 2020 lo nombra como uno de los dos bancos de alimentos del Eje Cafetero (F, Universidad Católica de Pereira). No encontramos fuente sobre su flota propia.

Las fuentes tampoco dicen qué vehículos hicieron la última milla dentro de Manizales. Una tractomula con ayudas de Bogotá llegó a la ciudad (F, Alcaldía de Bogotá, 15 ago 2026), y un camión de 8 t salió con donaciones hacia el Chocó (F, La República, 18 ago 2026).

### 2.2 Capacidades por tipo de vehículo

| Tipo en el modelo | Vehículo de referencia | Capacidad | Marca |
|---|---|---|---|
| camion | Chevrolet NPR Euro VI | 5.115 kg de carga; peso bruto 7.800 kg | F |
| camion | Furgón de 2,0 t o más (pliego del ICBF); ejemplo Chevrolet NHR Euro VI | 2.000 kg (mínimo ICBF); la ficha del NHR declara 2.457 kg y la prensa, 2,2 t | F |
| campero | Pick-up 4x4 doble cabina; ejemplo Toyota Hilux 2024 | 845 a 905 kg según versión; se toma 845 | F |
| campero | Vehículo de reparto de Dafiti | 800 kg por viaje | F |
| moto | Moto de reparto; ejemplo Bajaj Boxer CT100 (peso en seco 109 kg) | 40 kg | S |

Los ejemplos no son arbitrarios. El NHR era el primero en ventas de su segmento en 2019, con 1.118 unidades en el primer semestre (F, El Carro Colombiano). La Boxer CT100 es, según la misma revista, la moto más popular del país (F).

Hay tres salvedades:

- La capacidad de carga de un chasis incluye la carrocería. Por eso la carga neta de un NHR o un NPR con furgón es menor que la de la ficha, y no verificamos cuánto (S).
- La tabla de pesos de la ficha de la Hilux llega desordenada. Los seis juegos de valores cuadran entre sí, pero no se pueden asignar a cada versión con certeza (F con reserva).
- Ninguna fuente dio la carga de una moto de reparto. Los 40 kg son el supuesto que ya traía la semilla (S).

### 2.3 La flota propuesta

`vehiculos.csv` tiene 9 vehículos: 3 camiones (5.115, 2.000 y 2.000 kg), 3 pick-up de 845 kg, una furgoneta de 800 kg y 2 motos de 40 kg. Suman 12.530 kg (C). La semilla actual suma 6.240 kg con 5 vehículos (M). El acopio 1 recibe el camión mediano, un furgón, dos pick-up y una moto, porque es el principal y el único con frío en la semilla (S). La furgoneta se clasificó como `campero` porque el esquema no tiene otro tipo liviano (S).

La simulación arma su propia flota con 3.000 kg por camión, 700 por campero y 60 por moto (M, `despacho/sim/escenario.py`). Con esta evidencia serían de 2.000 a 5.115 kg por camión, de 800 a 845 por campero y 40 por moto (S). Si el equipo adopta esta flota en la demo, la capacidad total casi se duplica frente a la semilla. Una mejora en entregas a tiempo que venga de ese cambio no se puede atribuir al optimizador.

## 3. Velocidades

Esta sección compara las velocidades del modelo con las medidas en Manizales y explica cómo se armó `velocidades.csv`.

### 3.1 Mediciones en Manizales

**Tesis de maestría de la UNAL Manizales (2019).** Midió con un registrador GPS dos buses: uno eléctrico y uno a combustión con chasis FRR (F). Las mediciones del bus a combustión van de marzo a mayo de 2019 (F). Los recorridos se hacían al inicio de la jornada, al almuerzo y a la salida de los trabajadores (F). Clasificó las vías principales, secundarias y colectoras según el POT 2017-2031, y las locales y nacionales según el Plan de Movilidad de 2011 (F). También clasificó la pendiente media en cuatro intervalos (F). El bus a combustión promedió 22,6 km/h (F). Su tabla 14 da estas velocidades en km/h (F):

| Pendiente media | Principal | Secundaria | Colectora | Nacional | Local |
|---|---|---|---|---|---|
| 3 % o menos | 23,8 | 21,6 | 17,3 | sin dato | 18,1 |
| más de 3 % y menos de 6 % | 21,8 | 28,8 | 17,5 | sin dato | 23,2 |
| de 6 % a menos de 8 % | 23,4 | 28,8 | 16,2 | sin dato | 23,2 |
| 8 % o más | 24,2 | 28,8 | 17,3 | 26,5 | 23,2 |

En estos datos la velocidad del bus no baja con la pendiente (F). Una lectura posible es que en la ciudad pesan más la congestión y el tipo de vía que la pendiente (S). Los recorridos caen en horas de entrada, almuerzo y salida, que suelen tener más tráfico (S). Si además el bus paraba a recoger pasajeros, su velocidad subestima la de un camión (S).

**Diagnóstico del POT de Manizales.** En arterias principales la velocidad promedio era de 20,3 km/h de recorrido y de 27,9 km/h de marcha (F). En el corredor central era de 13,0 y 20 km/h (F). El extracto no distingue modos ni da el año; sus datos llegan hasta cerca del año 2000 (F).

Las dos fuentes coinciden en 20 a 24 km/h para las vías principales de la ciudad (C).

**Parámetros del SICE-TAC para carretera.** El sistema de costos eficientes del Ministerio de Transporte usa velocidades promedio por tipo de camión y de terreno. Una tesis de la UNAL Medellín de 2021 las transcribe (F, tabla 18):

| Camión | Plano | Ondulado | Montañoso |
|---|---|---|---|
| C2 (dos ejes, como el NHR o el NPR) | 53,0 | 30,0 | 15,0 |
| C3 (tres ejes) | 56,6 | 32,5 | 18,7 |
| C3S2 (tractomula) | 56,3 | 33,1 | 23,6 |

Estas velocidades son para viajes entre ciudades, no para calles urbanas. Sirven para los accesos de Manizales, como la vía a Chinchiná o la subida a Letras, si se clasifican como terreno montañoso (S).

### 3.2 Lo que usa el modelo hoy

`despacho/red.py` asigna velocidades por tipo de vía solo a los tramos sin `maxspeed` en OpenStreetMap. Donde el tramo trae `maxspeed`, osmnx usa ese límite legal como velocidad. Después, `despacho/matriz.py` multiplica el tiempo por 1,25 para el camión y por 0,9 para la moto. Medimos el grafo `despliegue/grafo/manizales_region.graphml` con un script corto que suma kilómetros y velocidades por tipo de vía. El script quedó fuera del repositorio, en `trabajo/agente-4/velocidades_grafo.py`.

| highway | km en el grafo | km con maxspeed | Media del modelo, campero | Medido o propuesto | Modelo / medido |
|---|---|---|---|---|---|
| trunk | 227,9 | 60 % (80 km/h en el 32 %) | 54,7 | 26,5 | 2,1 |
| primary | 125,6 | 24 % | 39,0 | 23,3 | 1,7 |
| secondary | 387,9 | 14 % | 35,5 | 27,0 | 1,3 |
| tertiary | 514,8 | 4 % | 30,0 | 17,1 | 1,8 |
| unclassified | 2.251,1 | 9 % | 25,4 | 21,9 | 1,2 |
| residential | 736,2 | 1 % | 20,1 | 21,9 | 0,9 |

Las tres primeras columnas numéricas son **M**. La columna «medido o propuesto» es la media simple de las cuatro pendientes de la tesis (C). Asignar `tertiary` a colectora y `unclassified` y `residential` a local es un supuesto (S). La última columna es **C**.

Para el camión, el modelo usa 43,8 km/h en `trunk`, 31,2 en `primary`, 28,4 en `secondary` y 24,0 en `tertiary` (C, media del grafo dividida por 1,25). Eso es entre 5 % y 65 % más que el bus medido (C).

### 3.3 Cómo se armó `velocidades.csv`

- Donde hay medición, el camión toma la velocidad del bus diésel (C).
- El campero toma la misma velocidad que el camión (S). El POT da 20,3 km/h de recorrido en arterias sin distinguir modo, menos que el bus. Así que no encontramos evidencia de que un campero vaya 25 % más rápido que un vehículo pesado dentro de la ciudad.
- La moto va 11 % más rápido que el campero, que es el factor 0,9 de `matriz.py` (S).
- Los enlaces (`_link`) toman el menor valor entre la vía madre medida y el supuesto actual del modelo (S).
- Donde no hay medición (`motorway`, `living_street`, `service`, `motorway_link`), se conservan el supuesto de `red.py` y los factores de `matriz.py` (S). Ninguno de esos tipos aparece en el grafo (M).

### 3.4 Qué cambiar en el código

1. Reemplazar el diccionario `VELOCIDADES` por los valores de `velocidades.csv`.
2. Topar la velocidad de los tramos con `maxspeed` dentro del casco urbano, o ignorar `maxspeed`. Sin esto el cambio no alcanza a `trunk`, donde el 60 % de los kilómetros usa el límite legal (M).
3. Revisar el factor 1,25 del camión: la medición urbana no lo respalda (S). Fuera de la ciudad sí hay razón para un camión más lento: el SICE-TAC le da 15 km/h a un C2 en terreno montañoso (F). Una opción es usar ese valor en los tramos `trunk` fuera del casco urbano (S).
4. Volver a correr la simulación y reportar el cambio en entregas a tiempo frente a la corrida del 20 de noviembre.

`despacho/sim/red_sim.py` repite el mismo diccionario y los mismos factores, así que el cambio va en los dos archivos.

## 4. Vida útil de la canasta

Esta sección resume `vida_util.csv`, que tiene 26 filas para los 16 productos de la tabla de raciones del bot. Las horas salen de convertir días y meses a horas (C): un mes son 730 h.

### 4.1 Por plazo

| Plazo | Producto y condición | Vida útil | Fuente |
|---|---|---|---|
| Horas | Pollo crudo o leche pasteurizada sin frío | 2 h; 1 h si el aire pasa de 32 °C | FDA (para la leche, inferencia nuestra) |
| Horas | Leche de fórmula preparada | 2 h; 24 h refrigerada | CDC |
| Horas | Pan del día | 24 h | ICBF |
| Días | Pollo crudo refrigerado a 4,4 °C o menos | 1 a 2 días | FSIS |
| Días | Leche pasteurizada cerrada a 4 °C | 3 a 4 días; 15 si es de alta pasteurización | OCU de España vía Semana (fuente secundaria) |
| Días | Tomate maduro firme a 12,8 a 21,1 °C | 4 a 7 días | USDA vía U. de Maine |
| Días | Tomate verde maduro, mismo rango | 1 a 3 semanas | USDA vía U. de Maine |
| Días | Huevo fresco bajo 22 °C | 20 a 30 días | ICBF |
| Días | Huevo fresco entre 22 y 32 °C | 15 a 20 días | ICBF |
| Días | Pan empacado | 15 días o más al entregar | ICBF |
| Meses | Leche UHT entera | 90 días o más desde el envase | ICBF |
| Meses | Arroz, harina de maíz precocida | 10 meses o más al entregar | ICBF |
| Meses | Frijol, lenteja, aceite, leche en polvo, fórmula en polvo, compota | 12 meses desde la producción | ICBF |
| Sin cifra | Panela | El ICBF escribe «no aplica» | ICBF |
| Sin cifra | Agua envasada, pañales | La define el productor o no se fija | Colombia Compra |
| Sin cifra | Fruta tropical | Solo la temperatura mínima segura | FAO |

Las fichas del ICBF son las que usa el Estado colombiano para comprar alimentos de sus programas. Varias dan la vida útil mínima que debe quedar al entregar y no la vida total. En esos casos el CSV usa el mínimo, que es la cifra conservadora.

Hay dos salvedades sobre la regla de las 2 horas:

- La FDA la da para perecederos en general. Aplicarla a la leche pasteurizada es inferencia nuestra (S), porque Colombia Compra exige guardar esa leche entre 0 y 4 °C (F).
- La FDA también pide refrigerar el huevo en 2 h (F). La ficha del ICBF, en cambio, admite guardarlo a temperatura ambiente con plazos según la temperatura (F). El CSV usa la ficha del ICBF porque es la norma de compra en Colombia (S).

### 4.2 Comparación con la semilla

La semilla de lotes usa estos vencimientos (M, `datos/semilla/lotes.csv`):

| Producto | Semilla | Evidencia |
|---|---|---|
| leche | 12 a 21 h | pasteurizada: 2 h sin frío y 3 a 4 días en frío; UHT: 90 días |
| pan | 7 a 25 h | 24 h si es del día; 15 días o más si es empacado |
| huevos | 26 a 42 h | 15 a 30 días según temperatura |
| fruta | 8 a 47 h | sin cifra en horas; el tomate dura de 4 a 7 días |
| verdura | 13 a 44 h | tomate de 4 a 7 días; lechuga de 2 a 3 semanas en frío |
| pollo | 9 a 28 h (en el acopio con frío) | 24 a 48 h refrigerado; 2 h sin frío |

La simulación usa entre 6 y 48 h para todo perecedero (M, `despacho/sim/escenario.py`).

### 4.3 Qué cambiar en el modelo

1. Generar `vence_en_horas` por producto a partir de `vida_util.csv`, y no con un rango común.
2. Distinguir la variedad de leche: la UHT no es perecedera a escala de un día de despacho.
3. Usar la condición de frío del acopio: en un acopio sin frío, pollo y leche pasteurizada vencen en 2 h.
4. No mandar fruta tropical al cuarto frío a 4 °C.

Con estos cambios el desperdicio simulado se concentraría en pollo, leche pasteurizada y pan del día (S). La leche UHT, en cambio, no necesita frío (F, ICBF). En el sismo, la leche que Alpina llevó a Quibdó fue UHT: 30.000 litros (F, La República).

## 5. Costos

Esta sección lista los costos que encontramos. Son pocos, y ninguno es el costo por kilómetro de un camión de reparto.

| Concepto | Valor | Año | Marca |
|---|---|---|---|
| Cobro logístico del Banco de Alimentos de Bogotá por kilo de fruta y verdura | 270 COP/kg | 2025 | F |
| Camioneta 4x4 con conductor, a todo costo | 426.000 COP/día | 2016 | F |
| Camioneta station wagon 4x2 con conductor, Bogotá | 415.909 COP/día | 2016 | F |
| Campero 4x2 con conductor, urbano (Acuerdo Marco, ICBF) | 1.037.451 COP/día | 2021 | F con reserva |
| Bus diésel con conductor en Manizales, precio del contrato por recorrido | 89.850 COP/recorrido | 2019 | F |
| El mismo contrato, por día (4 recorridos) | 359.400 COP/día | 2019 | F |
| El mismo bus, costo por kilómetro | 6.395 COP/km aprox. | 2019 | C |
| ACPM usado en la tesis para Manizales | 8.909 COP/galón | 2019 | F |
| Moto Bajaj Boxer CT100, precio de compra | 6.199.000 COP | 2026 | F |

Hay cinco salvedades:

- El cobro de 270 COP/kg no es un flete. Según la misma fuente, en Bogotá el transporte directo lo paga 60 % la institución que recibe y 40 % el banco (F).
- La orden del ICBF muestra precios distintos para el mismo tipo de vehículo y no aclara qué incluye. Hay que verificarla antes de usarla.
- El bus de la tesis transporta trabajadores y no es un camión de reparto. Sirve como orden de magnitud de un vehículo diésel mediano con conductor en ladera.
- El costo por kilómetro divide el precio por recorrido entre 14,05 km por recorrido, que salen de 2.402,7 km en 171 recorridos (C). Falta verificar en la tesis que ambos datos son del mismo bus. Además, la tabla 31 reparte el precio diario en proporciones fijas (50 % combustible, 25 % mantenimiento, 20 % conductor, 5 % parqueadero, C), así que esos componentes no son consumos medidos.
- Los precios de 2016, 2019 y 2021 no están actualizados a 2026.

Hoy el optimizador no usa costos en pesos: el costo de cada arco es el tiempo de viaje más el de servicio, y el retraso se penaliza según la urgencia (M, `despacho/optimizar.py`). Estos datos sirven para el criterio de viabilidad del pitch, no para el ruteo.

## 6. Qué faltó

Esta sección lista lo que no se pudo cubrir y por qué.

- **Búsquedas.** El cupo de búsquedas web compartido entre los agentes se agotó hacia las 5:10 p. m. Por eso no se buscaron los costos del SICE-TAC del Ministerio de Transporte (sus velocidades sí aparecen en una tesis), los precios del combustible de 2026, el costo por kilómetro de una moto, la velocidad de camiones en pendiente del manual del INVIAS ni una fuente colombiana primaria sobre la vida útil de la leche pasteurizada refrigerada. La cifra de 3 a 4 días viene de una organización de consumidores española citada por la prensa.
- **Sitios que no respondieron.** Los datos de FoodKeeper del USDA (acceso denegado desde la terminal y error del sitio con WebFetch). La página del FSIS sobre temperaturas (error del sitio). El Decreto 616 de 2006 en Función Pública (no se pudo leer su robots.txt). El archivo del MIT CTL (robots.txt lo prohíbe). La nota de gestión del riesgo de Cundinamarca sobre ayudas del sismo (error del sitio).
- **Pista para `empaque_activo`.** Un estudio colombiano probó permanganato de potasio, un captador de etileno, en banano bocadillo a 18 °C durante 16 días (F, García y otros, 2012). No extrajimos el efecto medido.

## 7. Lo que solo una persona puede conseguir

Esta sección lista a quién llamar y qué preguntarle. Cada respuesta, con nombre de la institución y cargo, reemplaza un supuesto de los CSV.

- **Banco Arquidiocesano de Alimentos de Manizales, coordinación logística.** ¿Cuántos vehículos propios o prestados tuvo tras el sismo, de qué tipo y con cuántos kilos útiles? ¿Alguno era refrigerado? ¿Cuánto costó un viaje dentro de la ciudad? ¿Recibieron pollo o leche pasteurizada durante los cortes de energía, y qué pasó con ellos?
- **ABACO, área de logística.** ¿Qué modelo y capacidad tenían los 3 camiones de Manizales? ¿Cuánto costó mover un kilo por el corredor del Eje Cafetero?
- **Cruz Roja Colombiana, Seccional Caldas, y Defensa Civil, Seccional Caldas.** ¿Qué vehículos hicieron la última milla en Manizales y con qué carga útil? ¿Usaron motos?
- **Unidad de Gestión del Riesgo de Manizales.** ¿Qué vehículos de la ciudad se asignaron a ayuda alimentaria y cuántos viajes hicieron por día?
- **Secretaría de Movilidad de Manizales, o el director de la tesis de 2019 en la UNAL Manizales.** ¿Hay velocidades medidas más recientes por tipo de vía, en hora pico y valle, o datos GPS de vehículos pesados?

## Fuentes

Todas consultadas el 20 de noviembre de 2026.

**Flota**

- Portafolio (16 ago 2026). Flypass paga peajes de 57 camiones. https://www.portafolio.co/economia/regiones/flypass-paga-peajes-de-57-camiones-para-acelerar-la-entrega-de-ayudas-tras-el-terremoto-en-colombia-500521
- Portafolio (21 sep 2026). ABACO: 2.000 toneladas de ayuda movilizadas. https://www.portafolio.co/historias-portafolio/abaco-2-000-toneladas-de-ayuda-movilizadas-502977
- Alcaldía de Bogotá (18 ago 2026). 172 vehículos de carga con ayudas. https://bogota.gov.co/mi-ciudad/gobierno/2141-toneladas-de-ayudas-de-bogota-zonas-afectadas-por-terremoto
- Alcaldía de Bogotá (15 ago 2026). Ayudas en Quibdó y Manizales. https://bogota.gov.co/mi-ciudad/gobierno/ayudas-de-bogota-ya-estan-en-quibdo-y-manizales-atencion-por-terremoto
- La República (18 ago 2026). La ayuda del sector privado se mide en toneladas, litros y kits. https://www.larepublica.co/empresas/la-ayuda-del-sector-privado-se-mide-en-toneladas-litros-y-kits-4460543
- La República (6 abr 2020). Dafiti transporta 3,5 toneladas diarias del Banco de Alimentos. https://www.larepublica.co/empresas/dafiti-esta-transportando-3-5-toneladas-diarias-de-donaciones-del-banco-de-alimentos-2988735
- ICBF (2015). Ficha técnica de transporte de mercancía. https://www.icbf.gov.co/sites/default/files/transporte_de_mercancia_-150821_-_fct.pdf
- RTVC Noticias (14 dic 2025). UNGRD destina más de 31 mil millones para equipos de emergencia. https://www.rtvcnoticias.com/colombia/ungrd-equipos-emergencia-departamentos
- El Carro Colombiano (7 abr 2020). Ford entregó vehículos a la Cruz Roja Colombiana. https://www.elcarrocolombiano.com/noticias/ford-entrego-vehiculos-a-la-cruz-roja-colombiana-para-enfrentar-el-covid-19/
- El Heraldo (1 ago 2024). Gobierno entrega dotación a la Defensa Civil del Atlántico. https://www.elheraldo.co/judicial/gobierno-nacional-entrega-dotacion-la-defensa-civil-del-atlantico-1114836
- Saavedra Guerra, M. y Pérez Henao, J. W. (2020). Un ahorro que alimenta. Monografía, Universidad Católica de Pereira. https://kujane.minciencias.gov.co/Record/RepoRIBUC2_0dbbb2e6246c9a7b1a9485c51fa5537b/Details
- Chevrolet Buses y Camiones. Ficha técnica NHR Euro VI. https://www.busesycamioneschevrolet.com.co/wp-content/uploads/2023/07/Ficha-Tecnica-NHR-EuroVI.pdf
- Chevrolet Buses y Camiones. Ficha técnica NPR Euro VI. https://busesycamioneschevrolet.com.co/wp-content/uploads/2023/09/Ficha-Tecnica-NPR-EVI.pdf
- Toyota de Colombia. Ficha técnica Hilux 2024. https://www.toyota.com.co/wp-content/uploads/2024/04/FT-HILUX-2024.pdf
- Bajaj Colombia. Boxer CT 100 ES. https://colombia.globalbajaj.com/en/BRANDS/Boxer/BOXER-CT-100-ES
- El Carro Colombiano (12 ago 2019). El camión Chevrolet NHR cumple 20 años y se mantiene como líder. https://www.elcarrocolombiano.com/resenas/el-camion-chevrolet-nhr-cumple-20-anos-y-se-mantiene-como-lider-en-colombia/
- El Carro Colombiano (4 ene 2021). Bajaj Boxer CT 100, la moto más popular. https://www.elcarrocolombiano.com/dos-ruedas/bajaj-boxer-ct-100-la-moto-mas-popular-sigue-vigente-en-colombia/

**Velocidades**

- Ocampo González, D. (2019). Determinación de los costos de operación de vehículos eléctricos en el transporte como estrategia de movilidad sostenible. Caso de estudio Manizales. Tesis de maestría, Universidad Nacional de Colombia, Manizales. Tablas 14 (p. 48), 17, 31 (p. 80) y 33 (p. 85). https://bffrepositorio.unal.edu.co/server/api/core/bitstreams/46d4a283-1bb5-4027-9a7d-6b0831aec2d8/content
- Alcaldía de Manizales. POT, Diagnóstico integral del territorio, área urbana, capítulo 3, Vías y transporte, p. 176. https://www.manizales.gov.co/RecursosAlcaldia/201505201528445252.pdf
- Quintero Giraldo, R. (2021). Análisis de emisiones del transporte interurbano de carga en camiones. Tesis de maestría, Universidad Nacional de Colombia, Medellín. Tabla 18 (p. 70), a partir del SICE-TAC. https://bffrepositorio.unal.edu.co/server/api/core/bitstreams/7637bcb8-a0fd-4614-a2af-6594543373c4/content

**Vida útil**

- ICBF. Fichas técnicas, grupo cereales, raíces, tubérculos y plátanos, v3 (2020). https://www.icbf.gov.co/system/files/procesos/a25.g6.pp_fichas_tecnicas_grupo_cereales_raices_tuberculos_y_platanos_v3.pdf
- ICBF. Fichas técnicas, grupo leche y productos lácteos, v3 (2021). https://www.icbf.gov.co/system/files/procesos/a27.g6.pp_fichas_tecnicas_grupo_leche_y_productos_lacteos_v3.pdf
- ICBF. Fichas técnicas, grupo carnes, huevos y leguminosas secas, v4 (2023). https://www.icbf.gov.co/system/files/procesos/a28.g6.pp_fichas_tecnicas_grupo_carnes_huevos_leguminosas_secas_frutos_secos_y_semillas_v4.pdf
- ICBF. Fichas técnicas, grupo grasas, v1 (2016). https://www.icbf.gov.co/sites/default/files/procesos/a29.g6.pp_fichas_tecnicas_grupo_grasas_v1.pdf
- ICBF. Fichas técnicas, grupo azúcares, v3 (2021). https://www.icbf.gov.co/system/files/procesos/a30.g6.pp_fichas_tecnicas_grupo_azucares_v3.pdf
- ICBF. Anexo 2, fichas técnicas de alimentos, recuperación nutricional (2015). https://www.icbf.gov.co/sites/default/files/anexo_2._fichas_tecnicas_de_alimentos.pdf
- ICBF. Ficha FT-02, leche entera UHT, convenio MADR. https://www.icbf.gov.co/sites/default/files/leche_entera_convenio_madr_-150326_-_ft-02.pdf
- Colombia Compra Eficiente. Anexo técnico, fichas de alimentos y elementos de aseo, v01 (2022). https://www.colombiacompra.gov.co/wp-content/uploads/2025/04/004._anexo_tecnico_iad_alimentos_y_elementos_de_aseo.pdf
- FDA. Termómetros para refrigeradores (vigente al 17 feb 2022). https://www.fda.gov/food/buy-store-serve-safe-food/termometros-para-refrigeradores-informacion-acerca-de-la-seguridad-de-los-alimentos
- USDA FSIS. Pollo de la granja a la mesa. https://www.fsis.usda.gov/es/node/6218
- Semana (13 dic 2023). Cuánto tiempo se puede conservar la leche en la nevera, con datos de la OCU de España. https://www.semana.com/vida-moderna/articulo/cuanto-tiempo-se-puede-conservar-la-leche-en-la-nevera-despues-de-abierta/202317/
- CDC. Infant formula preparation and storage (revisada el 14 may 2026). https://www.cdc.gov/nutrition/InfantandToddlerNutrition/formula-feeding/infant-formula-preparation-and-storage.html
- University of Maine Extension. Bulletin 4135, Storage conditions: fruits and vegetables (tabla de USDA Agriculture Handbook 66, 1986). https://extension.umaine.edu/publications/4135e/
- Kitinoja, L. y Kader, A. A. Small-scale postharvest handling practices, capítulo 6. FAO. https://www.fao.org/3/ae075e/ae075e14.htm
- García, J. C., Balaguera-López, H. E. y Herrera, A. O. (2012). Conservación del fruto de banano bocadillo con permanganato de potasio. Revista Colombiana de Ciencias Hortícolas 6(2). https://revistas.uptc.edu.co/index.php/ciencias_horticolas/article/download/1974/1969/2324

**Costos**

- Global FoodBanking Network (2025). Colombia case study. https://www.foodbanking.org/wp-content/uploads/2025/08/2025-GFN-Columbia-Case-Study.pdf
- Law Insider. Negociación de transporte del Fondo para la Reparación de las Víctimas (2016). https://lawinsider.com/es/contracts/hoZTvSCA8to
- Colombia Compra Eficiente. Orden de compra 83411 del ICBF, Acuerdo Marco CCE-285-AMP-2020 (2021). https://operaciones.colombiacompra.gov.co/sites/cce_public/files/documentos_adicionales_oc/orde_de_compra_r_11.pdf
- Galgo. Bajaj Boxer CT 100 ES, precio. https://www.galgo.com/co/motos/CO1033-bajaj-boxer-ct-100-es
