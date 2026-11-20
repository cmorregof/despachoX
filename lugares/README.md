# lugares/ · ubicar en el mapa lo que la gente dice

Problema: alguien escribe «derrumbe por la siria» y el sistema tiene que saber dónde es, o reconocer que no sabe. Un lugar mal ubicado manda un camión al sitio equivocado, así que **ninguna ubicación entra al plan sin que una persona la confirme**.

## Cómo decide

| Paso | Qué hace | Usa modelo |
|---|---|---|
| 1. Exacto | El texto coincide con un nombre o apodo del nomenclátor (`lugares`) | No |
| 2. Parecido | Tolera errores de tipeo y palabras de más («se cayó un barranco en la via a chinchna») | No |
| 3. Desempate | Si hay varios candidatos, un modelo elige uno de la lista o dice «ninguno». No puede inventar un lugar ni unas coordenadas | Sí |
| 4. Pin | Si nada sirve, el bot pide la ubicación del chat o un barrio cercano, o el despachador mueve el pin en el mapa | No |
| 5. Confirmación | Quien reportó o el despachador dice «sí». Solo entonces se actualiza el pedido o el cierre | No |
| 6. Aprendizaje | Lo que dijo la persona queda como apodo del lugar confirmado. La próxima vez es paso 1 | No |

## Uso

```python
from datos import db
import lugares

con = db.conectar()
lugares.cargar_semilla(con)                       # una vez, y cada vez que cambie la semilla

# Samuel (bot): al recibir un cierre
r = lugares.resolver(con, "por la via a chinchina", tabla="cierres", fila_id=7,
                     contexto=texto_completo, tipos=("via", "sitio"))
enviar(r.pregunta)                                # «Ubiqué … en: vía a Chinchiná (via). ¿Es correcto?»
# botones: Sí -> confirmar; cada candidato de r.candidatos -> confirmar con lugar_id; «Enviar ubicación»
lugares.confirmar(con, r.ubicacion_id, quien="remitente")
lugares.confirmar(con, r.ubicacion_id, quien="remitente", lugar_id=otro.lugar_id)
lugares.corregir_con_pin(con, r.ubicacion_id, lat, lon, quien="remitente")    # mensaje de ubicación de Telegram

# Para un pedido: tipos=("barrio", "punto", "sitio", "vereda")
```

`r.seguro` dice si basta un «¿es correcto?» (True) o si hay que mostrar las opciones (False). Lo que elige el modelo nunca se marca como seguro.

Jacobo (tablero): las filas de `ubicaciones` con estado `propuesta` van en «Por revisar», con el texto original, el lugar propuesto, las alternativas (`candidatos`, JSON) y un pin que el despachador puede mover; al soltarlo se llama `corregir_con_pin(..., quien="despachador")`.

Probar a mano: `python -m lugares.nomenclator "por la panamericana" "la siria"`

## Dónde vive el nomenclátor

- `datos/semilla/barrios.csv` y `vias.csv`: los genera `despacho/`.
- `datos/semilla/lugares_extra.csv` (cabecera `nombre,alias,tipo,lat,lon,osm_u,osm_v,origen`, apodos separados por `|`): sitios y apodos que no salen de OpenStreetMap. Lo llena el encargo `B2`.
- Tabla `lugares`, origen `aprendido`: lo que el uso va enseñando.

## Límites conocidos

- Si un sitio no está en el nomenclátor, el sistema lo dice y pide un pin. No adivina. Hoy faltan, entre otros, la Galería, el kilómetro 41, los peajes, los túneles y viaductos, y las estaciones del cable: Nominatim no los devolvió y no se pusieron de memoria.
- El acceso por tipo de vehículo no se decide aquí: lo calcula `despacho/matriz.py` cuando el punto ya tiene coordenadas.
- Los apodos de `lugares_extra.csv` los escribió el equipo; no se han validado con habitantes. El uso los corrige (paso 6).

## Medición (20 de noviembre de 2026)

Banco de 44 frases escritas como en un chat (`lugares/tests/frases.csv`), sin modelo de lenguaje, con `UMBRAL_SEGURO = 0.90` y `MARGEN = 0.08`:

| Resultado | Frases |
|---|---|
| Acierto seguro (propuso un solo lugar y era el correcto) | 30 |
| Acierto por opciones (el correcto estaba entre las alternativas) | 5 |
| «No sé» (9 de 9 eran lugares que no existen en el nomenclátor) | 9 |
| Error seguro (propuso con seguridad un lugar equivocado) | 0 |

Los umbrales no se cambiaron: ya daban cero errores seguros. El margen es el que protege: con `MARGEN = 0` aparece un error seguro («piedras en la carretera a villamaria» se iba al casco urbano de Villamaría y no a la vía). Repetir: `python -m lugares.tests.test_frases`.

Límite de la medición: las frases las escribió el equipo conociendo el nomenclátor. No es una muestra de mensajes reales; sirve para vigilar que un cambio no introduzca errores seguros, y hay que repetirla con mensajes de usuarios.
