# Campos extraídos por el modelo en los quince mensajes de ejemplo

Medido el 2026-11-20 15:00 con `claude-haiku-5-5`, una corrida, sin reintentos. Los mensajes son sintéticos y los escribió el equipo, así que el número mide el extractor sobre estos casos y no sobre mensajes reales.

**62 de 64 campos correctos (96.9 %).** Llamadas que fallaron: 0 de 15.

| # | Caso | Campos bien | Campos mal |
|---|---|---|---|
| 1 | sin puntuación ni tildes; el caso del encargo | 5/5 | ninguno |
| 2 | errores de tipeo y urgencia por niños | 4/5 | productos |
| 3 | abreviatura «flias» y barrio partido en dos palabras | 5/5 | ninguno |
| 4 | kilos explícitos | 6/6 | ninguno |
| 5 | puede esperar | 5/5 | ninguno |
| 6 | plazo en horas | 5/5 | ninguno |
| 7 | no dice dónde ni qué: debe quedar en dudas | 5/5 | ninguno |
| 8 | cierre solo para camiones | 3/3 | ninguno |
| 9 | cierre total sin puntuación | 3/3 | ninguno |
| 10 | tipeo en la vía; solo pasan motos | 2/3 | cierre.lugar |
| 11 | cierre total | 3/3 | ninguno |
| 12 | sitio por fuera del casco urbano, dicho con apodo | 3/3 | ninguno |
| 13 | mezcla pedido y cierre | 7/7 | ninguno |
| 14 | no es pedido ni cierre | 1/1 | ninguno |
| 15 | trae nombre y teléfono inventados: no deben guardarse | 5/5 | ninguno |
