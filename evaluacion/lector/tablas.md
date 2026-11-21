# Tablas de la corrida (generadas por evaluar.py)

Lector: entrada.sms.leer_sms tras entrada.privacidad.limpiar (Mesa.leer con DESPACHOX_SIN_RED=1); lugar con lugares.resolver, elegir=None. Conjunto: 330 mensajes, sha256 `54a5b70f792b82bc…`. Corrida: 2026-11-21T00:24:02-05:00. Celdas: aciertos/n (porcentaje; intervalo de Wilson al 95 %).

## Campo por campo

| Campo | 300 generados | 30 difíciles |
|---|---|---|
| Tipo de mensaje | 299/300 (99,7 %; 98,1 a 99,9) | 25/30 (83,3 %; 66,4 a 92,7) |
| Lugar extraído (núcleo igual) | 174/285 (61,1 %; 55,3 a 66,5) | 7/21 (33,3 %; 17,2 a 54,6) |
| Lugar resuelto: acierto seguro | 211/285 (74,0 %; 68,6 a 78,8) | 10/17 (58,8 %; 36,0 a 78,4) |
| Lugar resuelto: seguro o entre las opciones | 254/285 (89,1 %; 85,0 a 92,2) | 11/17 (64,7 %; 41,3 a 82,7) |
| Sin error seguro de lugar | 300/300 (100,0 %; 98,7 a 100,0) | 21/21 (100,0 %; 84,5 a 100,0) |
| Lugar ambiguo o desconocido: no se compromete | no aplica | 4/4 (100,0 %; 51,0 a 100,0) |
| Techo: el lugar del oro, resuelto tal como se escribió | 245/285 (86,0 %; 81,5 a 89,5) | 16/17 (94,1 %; 73,0 a 99,0) |
| Familias (cuando el oro las trae) | 129/153 (84,3 %; 77,7 a 89,2) | 14/18 (77,8 %; 54,8 a 91,0) |
| Personas (cuando el oro las trae) | 79/117 (67,5 %; 58,6 a 75,3) | 3/4 (75,0 %; 30,1 a 95,4) |
| Bebés (cuando el oro los trae) | 13/15 (86,7 %; 62,1 a 96,3) | 1/1 (100,0 %; 20,7 a 100,0) |
| Conteo exacto (familias, personas y bebés) | 209/285 (73,3 %; 67,9 a 78,1) | 14/20 (70,0 %; 48,1 a 85,5) |
| Error: personas leídas como familias | 19/117 (16,2 %; 10,6 a 24,0) | 0/2 (0,0 %; 0,0 a 65,8) |
| Productos: conjunto exacto | 238/285 (83,5 %; 78,8 a 87,4) | 15/19 (78,9 %; 56,7 a 91,5) |
| Cantidades en kilos | 27/31 (87,1 %; 71,1 a 94,9) | 1/3 (33,3 %; 6,1 a 79,2) |
| Urgencia | 281/300 (93,7 %; 90,3 a 95,9) | 20/21 (95,2 %; 77,3 a 99,2) |
| Dos pedidos detectados | 0/30 (0,0 %; 0,0 a 11,4) | no aplica |
| Abstención: lugar que falta | 8/15 (53,3 %; 30,1 a 75,2) | no aplica |
| Abstención: conteo que falta | 15/15 (100,0 %; 79,6 a 100,0) | 0/1 (0,0 %; 0,0 a 79,3) |
| Abstención: productos que faltan | 15/15 (100,0 %; 79,6 a 100,0) | 2/2 (100,0 %; 34,2 a 100,0) |
| Abstención: kilos que el mensaje no dice | 552/556 (99,3 %; 98,2 a 99,7) | 30/30 (100,0 %; 88,6 a 100,0) |
| Código de entrega | no aplica | 2/3 (66,7 %; 20,8 a 93,9) |
| Cierre detectado | no aplica | 2/3 (66,7 %; 20,8 a 93,9) |
| Cierre: lugar extraído | no aplica | 1/2 (50,0 %; 9,5 a 90,5) |
| Cierre: lugar resuelto | no aplica | 2/2 (100,0 %; 34,2 a 100,0) |
| Cierre: vehículos bloqueados | no aplica | 1/1 (100,0 %; 20,7 a 100,0) |
| Mensaje sin ningún error | 151/300 (50,3 %; 44,7 a 56,0) | 11/30 (36,7 %; 21,9 a 54,5) |
| Productos: precisión | 586/646 (90,7 %; 88,2 a 92,7) | 33/35 (94,3 %; 81,4 a 98,4) |
| Productos: exhaustividad | 586/604 (97,0 %; 95,3 a 98,1) | 33/38 (86,8 %; 72,7 a 94,2) |
| Productos: F1 | 93,8 % | 90,4 % |

## Lugar: de lo leído a lo resuelto

| Clase | Generados | Difíciles |
|---|---|---|
| acierto seguro | 211 | 10 |
| por opciones | 43 | 2 |
| no sé | 30 | 9 |
| error seguro | 0 | 0 |
| sin lugar | 1 | 0 |
| se abstiene | 8 | 0 |
| inventa sin compromiso | 7 | 0 |
| inventa con seguridad | 0 | 0 |

Techo del nomenclátor: si el lector copiara el lugar tal como va en el mensaje, el resolvedor daría acierto seguro en 245/285 (86,0 %; 81,5 a 89,5) de los mismos pedidos generados. La diferencia con el acierto seguro del lector es lo que pierde el lector; el resto lo pierde el nomenclátor.

## Por variante (generados)

| Variante | n | Tipo | Lugar extraído | Lugar resuelto | Conteo exacto | Productos exactos | F1 productos | Kilos | Urgencia | Sin errores |
|---|---|---|---|---|---|---|---|---|---|---|
| sms | 30 | 30/30 (100,0 %) | 30/30 (100,0 %) | 23/30 (76,7 %) | 30/30 (100,0 %) | 30/30 (100,0 %) | 100,0 % | 3/3 (100,0 %) | 30/30 (100,0 %) | 23/30 (76,7 %) |
| limpio | 30 | 30/30 (100,0 %) | 22/30 (73,3 %) | 18/30 (60,0 %) | 30/30 (100,0 %) | 30/30 (100,0 %) | 100,0 % | 3/4 (75,0 %) | 27/30 (90,0 %) | 16/30 (53,3 %) |
| sin_tildes | 30 | 30/30 (100,0 %) | 27/30 (90,0 %) | 24/30 (80,0 %) | 29/30 (96,7 %) | 30/30 (100,0 %) | 100,0 % | 5/5 (100,0 %) | 28/30 (93,3 %) | 22/30 (73,3 %) |
| mayusculas | 30 | 30/30 (100,0 %) | 20/30 (66,7 %) | 26/30 (86,7 %) | 29/30 (96,7 %) | 30/30 (100,0 %) | 100,0 % | 3/3 (100,0 %) | 27/30 (90,0 %) | 24/30 (80,0 %) |
| abreviaturas | 45 | 45/45 (100,0 %) | 29/45 (64,4 %) | 40/45 (88,9 %) | 28/45 (62,2 %) | 45/45 (100,0 %) | 100,0 % | 5/5 (100,0 %) | 42/45 (93,3 %) | 24/45 (53,3 %) |
| voz | 60 | 59/60 (98,3 %) | 20/60 (33,3 %) | 32/60 (53,3 %) | 26/60 (43,3 %) | 42/60 (70,0 %) | 92,9 % | 7/9 (77,8 %) | 59/60 (98,3 %) | 13/60 (21,7 %) |
| dos_pedidos | 30 | 30/30 (100,0 %) | 7/30 (23,3 %) | 26/30 (86,7 %) | 9/30 (30,0 %) | 1/30 (3,3 %) | 68,4 % | 1/2 (50,0 %) | 25/30 (83,3 %) | 0/30 (0,0 %) |
| faltan_datos | 45 | 45/45 (100,0 %) | 19/30 (63,3 %) | 22/30 (73,3 %) | 28/30 (93,3 %) | 30/30 (100,0 %) | 100,0 % | no aplica | 43/45 (95,6 %) | 29/45 (64,4 %) |

## Por etiqueta (generados; un mensaje puede tener varias)

| Variante | n | Tipo | Lugar extraído | Lugar resuelto | Conteo exacto | Productos exactos | F1 productos | Kilos | Urgencia | Sin errores |
|---|---|---|---|---|---|---|---|---|---|---|
| conteo_aproximado | 61 | 61/61 (100,0 %) | 23/58 (39,7 %) | 45/58 (77,6 %) | 37/61 (60,7 %) | 43/58 (74,1 %) | 90,8 % | 4/5 (80,0 %) | 54/61 (88,5 %) | 22/61 (36,1 %) |
| conteo_ausente | 15 | 15/15 (100,0 %) | 11/15 (73,3 %) | 11/15 (73,3 %) | no aplica | 15/15 (100,0 %) | 100,0 % | no aplica | 14/15 (93,3 %) | 11/15 (73,3 %) |
| conteo_bebes | 18 | 18/18 (100,0 %) | 6/16 (37,5 %) | 12/16 (75,0 %) | 12/18 (66,7 %) | 11/16 (68,8 %) | 84,2 % | 1/1 (100,0 %) | 16/18 (88,9 %) | 10/18 (55,6 %) |
| conteo_familias | 161 | 160/161 (99,4 %) | 98/153 (64,1 %) | 116/153 (75,8 %) | 129/161 (80,1 %) | 127/153 (83,0 %) | 93,1 % | 14/14 (100,0 %) | 155/161 (96,3 %) | 88/161 (54,7 %) |
| conteo_mayores | 13 | 13/13 (100,0 %) | 4/11 (36,4 %) | 10/11 (90,9 %) | 5/13 (38,5 %) | 8/12 (66,7 %) | 86,2 % | no aplica | 6/13 (46,2 %) | 3/13 (23,1 %) |
| conteo_ninos | 11 | 11/11 (100,0 %) | 5/11 (45,5 %) | 10/11 (90,9 %) | 7/11 (63,6 %) | 5/9 (55,6 %) | 82,6 % | 1/2 (50,0 %) | 10/11 (90,9 %) | 5/11 (45,5 %) |
| conteo_personas | 103 | 103/103 (100,0 %) | 54/100 (54,0 %) | 72/100 (72,0 %) | 62/103 (60,2 %) | 73/101 (72,3 %) | 90,0 % | 12/15 (80,0 %) | 96/103 (93,2 %) | 34/103 (33,0 %) |
| espera | 21 | 21/21 (100,0 %) | 8/20 (40,0 %) | 13/20 (65,0 %) | 14/21 (66,7 %) | 17/21 (81,0 %) | 93,2 % | 2/2 (100,0 %) | 21/21 (100,0 %) | 7/21 (33,3 %) |
| familias_implicitas | 12 | 12/12 (100,0 %) | 12/12 (100,0 %) | 12/12 (100,0 %) | 12/12 (100,0 %) | 12/12 (100,0 %) | 100,0 % | no aplica | 12/12 (100,0 %) | 12/12 (100,0 %) |
| homofonos | 36 | 35/36 (97,2 %) | 11/36 (30,6 %) | 17/36 (47,2 %) | 16/36 (44,4 %) | 18/36 (50,0 %) | 88,2 % | 3/5 (60,0 %) | 35/36 (97,2 %) | 4/36 (11,1 %) |
| kilos | 33 | 33/33 (100,0 %) | 16/33 (48,5 %) | 20/33 (60,6 %) | 22/33 (66,7 %) | 26/33 (78,8 %) | 93,7 % | 27/31 (87,1 %) | 31/33 (93,9 %) | 12/33 (36,4 %) |
| lugar_ausente | 15 | 15/15 (100,0 %) | no aplica | no aplica | 14/15 (93,3 %) | 15/15 (100,0 %) | 100,0 % | no aplica | 14/15 (93,3 %) | 8/15 (53,3 %) |
| lugar_barrio | 237 | 236/237 (99,6 %) | 137/237 (57,8 %) | 184/237 (77,6 %) | 157/223 (70,4 %) | 182/223 (81,6 %) | 92,9 % | 22/24 (91,7 %) | 221/237 (93,2 %) | 124/237 (52,3 %) |
| lugar_punto | 25 | 25/25 (100,0 %) | 18/25 (72,0 %) | 6/25 (24,0 %) | 15/24 (62,5 %) | 19/25 (76,0 %) | 92,3 % | 2/4 (50,0 %) | 25/25 (100,0 %) | 0/25 (0,0 %) |
| lugar_vereda | 35 | 35/35 (100,0 %) | 21/35 (60,0 %) | 31/35 (88,6 %) | 26/35 (74,3 %) | 22/34 (64,7 %) | 86,3 % | 3/3 (100,0 %) | 31/35 (88,6 %) | 19/35 (54,3 %) |
| mencion_vulnerable | 22 | 22/22 (100,0 %) | 11/21 (52,4 %) | 14/21 (66,7 %) | 12/18 (66,7 %) | 21/21 (100,0 %) | 100,0 % | 1/1 (100,0 %) | 14/22 (63,6 %) | 5/22 (22,7 %) |
| numeros_en_palabras | 33 | 32/33 (97,0 %) | 3/33 (9,1 %) | 14/33 (42,4 %) | 0/33 (0,0 %) | 26/33 (78,8 %) | 95,2 % | 5/7 (71,4 %) | 32/33 (97,0 %) | 0/33 (0,0 %) |
| palabras_partidas | 13 | 13/13 (100,0 %) | 4/13 (30,8 %) | 4/13 (30,8 %) | 5/13 (38,5 %) | 11/13 (84,6 %) | 96,0 % | 4/4 (100,0 %) | 13/13 (100,0 %) | 3/13 (23,1 %) |
| palabras_pegadas | 10 | 10/10 (100,0 %) | 3/10 (30,0 %) | 4/10 (40,0 %) | 5/10 (50,0 %) | 6/10 (60,0 %) | 89,5 % | 1/1 (100,0 %) | 10/10 (100,0 %) | 1/10 (10,0 %) |
| sin_conteo | 15 | 15/15 (100,0 %) | 11/15 (73,3 %) | 11/15 (73,3 %) | no aplica | 15/15 (100,0 %) | 100,0 % | no aplica | 14/15 (93,3 %) | 11/15 (73,3 %) |
| sin_lugar | 15 | 15/15 (100,0 %) | no aplica | no aplica | 14/15 (93,3 %) | 15/15 (100,0 %) | 100,0 % | no aplica | 14/15 (93,3 %) | 8/15 (53,3 %) |
| sin_productos | 15 | 15/15 (100,0 %) | 8/15 (53,3 %) | 11/15 (73,3 %) | 14/15 (93,3 %) | no aplica | no aplica | no aplica | 15/15 (100,0 %) | 10/15 (66,7 %) |
| urgente | 53 | 53/53 (100,0 %) | 26/51 (51,0 %) | 36/51 (70,6 %) | 32/50 (64,0 %) | 35/48 (72,9 %) | 90,2 % | 5/6 (83,3 %) | 53/53 (100,0 %) | 22/53 (41,5 %) |

## Abstención en los que les falta un dato (generados)

| Variante | n | Abst. lugar | Abst. conteo | Abst. productos |
|---|---|---|---|---|
| sin_lugar | 15 | 8/15 (53,3 %) | no aplica | no aplica |
| sin_conteo | 15 | no aplica | 15/15 (100,0 %) | no aplica |
| sin_productos | 15 | no aplica | no aplica | 15/15 (100,0 %) |

## Difíciles por tipo de caso

| Variante | n | Tipo | Lugar extraído | Conteo | Productos | Urgencia | Sin errores |
|---|---|---|---|---|---|---|---|
| bebes | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |
| cancelacion | 1 | 0/1 (0,0 %) | no aplica | no aplica | no aplica | no aplica | 0/1 (0,0 %) |
| correccion | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | no aplica | 1/1 (100,0 %) | 0/1 (0,0 %) |
| emojis | 1 | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) |
| entrega | 3 | 2/3 (66,7 %) | no aplica | no aplica | no aplica | no aplica | 2/3 (66,7 %) |
| fuera_de_catalogo | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |
| kilos_en_serie | 1 | 1/1 (100,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |
| largo | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) |
| lugar_ambiguo | 2 | 2/2 (100,0 %) | 1/2 (50,0 %) | 2/2 (100,0 %) | 1/1 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) |
| lugar_desconocido | 2 | 2/2 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) |
| negacion | 3 | 3/3 (100,0 %) | 0/3 (0,0 %) | 3/3 (100,0 %) | 1/3 (33,3 %) | 2/3 (66,7 %) | 0/3 (0,0 %) |
| no_pedido | 3 | 0/3 (0,0 %) | no aplica | no aplica | no aplica | no aplica | 0/3 (0,0 %) |
| numero_en_lugar | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |
| pedido_y_cierre | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |
| personas_y_familias | 3 | 3/3 (100,0 %) | 1/3 (33,3 %) | 1/3 (33,3 %) | 3/3 (100,0 %) | 3/3 (100,0 %) | 1/3 (33,3 %) |
| reporte_via | 2 | 2/2 (100,0 %) | no aplica | no aplica | no aplica | no aplica | 2/2 (100,0 %) |
| unidades_raras | 2 | 2/2 (100,0 %) | 1/2 (50,0 %) | 1/1 (100,0 %) | 2/2 (100,0 %) | 2/2 (100,0 %) | 0/2 (0,0 %) |
| voz_extrema | 1 | 1/1 (100,0 %) | 0/1 (0,0 %) | 0/1 (0,0 %) | 0/1 (0,0 %) | 1/1 (100,0 %) | 0/1 (0,0 %) |

## Tiempo por mensaje

Medido en Darwin 25.5.0 arm64, Python 3.12.13, sin red. Lectura (limpiar y leer_sms), 330 mensajes: mediana 0,947 ms, p95 1,991 ms y máximo 5,724 ms. Resolver el lugar sin modelo, 318 lugares: mediana 30,88 ms, p95 68,14 ms y máximo 157,99 ms.
