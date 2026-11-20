# Encargo B2 · Red vial completa, nomenclátor y datos reales (Carlos, sesión B-despacho)

Haz `git pull --rebase` y lee las entradas nuevas de `torre/CANAL.md`, `lugares/README.md` y los cambios de `datos/esquema.sql` (tablas `lugares` y `ubicaciones`) y de `despacho/optimizar.py` (`FACTOR_CRITICO`).

Fable añadió el módulo `lugares/`, que ubica un lugar dicho en lenguaje coloquial y exige confirmación humana. Funciona con los barrios y las vías de la semilla, pero el nomenclátor es corto y la red no cubre varios sitios que la gente va a nombrar. Tres tareas, en este orden.

## 1. Que la red cubra lo que la gente nombra

La demo y los usuarios van a decir «La Siria», «la vía a Neira», «el alto de Letras», «La Manuela», «Tres Puertas», «el kilómetro 41», «La Cabaña». Hoy `vias.csv` no tiene La Siria ni la vía a Neira porque el grafo no llega.

- Amplía el área de `despacho/red.py` hasta donde haga falta para incluir los accesos reales a Manizales: vía antigua a Chinchiná por La Siria, autopista del Café, vía a Neira, vía a Villamaría, salida a Letras y al Magdalena. Mide cuánto crece el grafo y cuánto tarda la matriz; si se vuelve lenta, conserva fuera del casco urbano solo las vías principales.
- Regenera `vias.csv` y verifica cada tramo contra el grafo. Di con claridad cuáles no encontraste y por qué.
- Vuelve a correr las pruebas de `despacho/` y `python -m despacho.optimizar` con la semilla.

## 2. Nomenclátor: `datos/semilla/lugares_extra.csv`

Cabecera: `nombre,alias,tipo,lat,lon,osm_u,osm_v,origen`. Los apodos van separados por `|`. Tipos: `via`, `sitio`, `vereda`, `barrio`.

Lanza un agente Sonnet con este encargo: reunir entre 60 y 100 lugares que un habitante de Manizales usaría para ubicarse y que no están en `barrios.csv` ni en `vias.csv`. Sectores y sitios (La Siria, Maltería, La Enea, El Cable, Milán, la Galería, la Terminal, Los Cámbulos, hospitales, coliseos, universidades, glorietas, puentes y viaductos con nombre), veredas y corregimientos cercanos, y apodos de vías («la Pana», «la Kevin», «la Paralela», «la 23»). Para cada uno, coordenadas tomadas de OpenStreetMap (por nombre en el grafo o con Nominatim, respetando su límite de una consulta por segundo), nunca de memoria. Lo que no se pueda ubicar con una fuente queda fuera y se lista aparte.

Tú revisas el resultado antes de aceptarlo:
- cada fila cae dentro del área de la red y a menos de 500 m de una arista;
- las de tipo `via` llevan `osm_u` y `osm_v` de una arista que existe;
- no hay dos lugares distintos con el mismo apodo sin que sea deliberado.

Luego `python -m lugares.nomenclator "la siria" "la pana" "por la terminal"` y pega la salida en tu torre.

## 3. Medir el resolvedor

Escribe `lugares/tests/frases.csv` con 40 frases como las escribiría alguien por chat (con errores, sin tildes, con referencias vagas), cada una con el lugar correcto o `ninguno`. Añade una prueba que reporte: aciertos seguros, aciertos que pasaron por opciones, errores seguros (el caso grave: propuso con seguridad un lugar equivocado) y «no sé». Ajusta `UMBRAL_SEGURO` y `MARGEN` para que los errores seguros sean cero aunque suban los «no sé». Ese número va a la ficha.

## 4. Lista para datos reales

Cuando la organización o un aliado nos pase datos (centros de acopio, vehículos, puntos, inventario), deben entrar sin tocar código:

- `python -m despacho.semilla --cargar --origen datos_privados/` lee los mismos CSV de `datos/semilla/` desde otra carpeta. `datos_privados/` ya está en `.gitignore`.
- Lo que falte en esa carpeta se completa con la semilla sintética, y el programa dice qué archivos fueron reales y cuáles sintéticos.
- Valida al cargar: coordenadas dentro del área, tipos de vehículo conocidos, fechas legibles, kilos positivos. Un archivo malo se rechaza con un mensaje que diga la fila y la razón.
- Escribe `datos/README.md` con la cabecera exacta de cada CSV y un ejemplo de fila, para poder mandárselo a quien nos dé los datos.

## Reglas

- No cambies la firma de `planificar` ni de `_resolver` sin avisar a `simulacion` por el canal.
- Cada etapa: LISTO en el canal con cómo probarlo, commit y push.

**Aporta a:** criterio 2 (la demo no se cae por un nombre de lugar), criterio 3 (método con medición) y criterio 5 (lista para datos de un aliado).
