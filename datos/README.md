# datos/

`esquema.sql` es el contrato entre los módulos. La base de trabajo es `datos/despachox.db` (no se sube al repositorio); la variable `DESPACHOX_DB` permite apuntar a otra ruta.

## Cargar la base

```
python -m despacho.semilla --cargar --reiniciar                           # todo sintético
python -m despacho.semilla --cargar --reiniciar --origen datos_privados/   # con datos reales
```

Con `--origen`, cada archivo se toma de esa carpeta si existe y de la semilla sintética (`datos/semilla/`) si no. El programa dice cuáles fueron reales y cuáles sintéticos. Si un archivo tiene un error, la carga se rechaza completa, se indica la fila y la razón, y la base queda como estaba. `datos_privados/` está en `.gitignore`: lo que se ponga ahí no se sube.

## Formato de los archivos

CSV en UTF-8, separado por comas, con la primera fila de cabecera. Excel lo guarda con «CSV UTF-8 (delimitado por comas)». Las columnas marcadas con * son obligatorias; las demás pueden faltar o ir vacías. Las coordenadas van en grados decimales con punto (latitud cerca de 5.06, longitud cerca de -75.50). Las fechas van como `2026-11-21T14:30` (hora de Colombia).

**No incluya datos personales**: ni nombres de personas, ni teléfonos, ni cédulas, ni direcciones de viviendas. Un punto de entrega es un sitio colectivo (salón comunal, albergue, comedor).

### `acopios.csv` · bodegas o centros de acopio

| Columna | Qué es |
|---|---|
| `id` * | Número entero, único |
| `nombre` * | Nombre de la bodega |
| `lat` *, `lon` * | Ubicación |
| `tiene_frio` | 1 si tiene cuarto frío, 0 si no |

```
id,nombre,lat,lon,tiene_frio
1,Bodega principal,5.037138,-75.439679,1
```

### `vehiculos.csv` · flota disponible

| Columna | Qué es |
|---|---|
| `id` * | Número entero, único |
| `nombre` | Cómo lo llaman («Camión 1»). Sin nombre del conductor |
| `tipo` * | `camion`, `campero`, `moto` o `a_pie` |
| `capacidad_kg` * | Carga máxima en kilos |
| `acopio_id` * | `id` del acopio del que sale y al que regresa |
| `lat`, `lon` | Posición actual. Vacío = está en su acopio |
| `estado` | `libre` (por defecto), `en_ruta` o `fuera` |

```
id,nombre,tipo,capacidad_kg,acopio_id,lat,lon,estado
1,Camión 1,camion,3000,1,,,libre
```

### `puntos.csv` · puntos de entrega

| Columna | Qué es |
|---|---|
| `id` * | Número entero, único |
| `nombre` * | Nombre del sitio |
| `lat` *, `lon` * | Ubicación |
| `barrio`, `comuna` | Para ubicarlo por nombre |
| `critico` | 1 si es punto crítico (albergue, comedor, centro de salud), 0 si no |

```
id,nombre,barrio,comuna,lat,lon,critico
1,Albergue temporal San Jorge,San Jorge,La Estación,5.065826,-75.499456,1
```

### `lotes.csv` · inventario

| Columna | Qué es |
|---|---|
| `id` * | Número entero, único |
| `acopio_id` * | `id` del acopio donde está |
| `producto` * | Nombre del producto («arroz», «leche») |
| `kg` * | Kilos disponibles |
| `perecedero` | 1 si vence pronto, 0 si no |
| `vence_en` | Fecha y hora de vencimiento. Obligatoria si es perecedero |
| `vence_en_horas` | Alternativa a `vence_en`: horas que faltan desde el momento de la carga |
| `empaque_activo` | 1 si usa empaque que alarga la vida útil, 0 si no |

```
id,acopio_id,producto,kg,perecedero,vence_en,empaque_activo
1,1,arroz,800,0,,0
2,1,leche,120,1,2026-11-21T18:00,0
```

### `pedidos.csv` · pedidos ya recibidos (opcional; normalmente llegan por el chat)

| Columna | Qué es |
|---|---|
| `id` * | Número entero, único |
| `punto_id` * | `id` del punto de entrega |
| `familias` | Número de familias |
| `kg_estimado` | Kilos totales |
| `productos` | Detalle en JSON: `[{"producto": "arroz", "kg": 20}]` |
| `urgencia` | 1, 2 o 3 (3 es lo más urgente). Por defecto 2 |
| `creado_en` | Cuándo se pidió. Alternativa: `creado_hace_min` |
| `limite_en` | Hora tope de entrega. Alternativa: `limite_en_horas` |
| `estado` | `nuevo` (por defecto) o `confirmado` |
| `texto_original` | El mensaje, sin nombres ni teléfonos |

Cada pedido necesita al menos una de `productos`, `kg_estimado` o `familias`.

```
id,punto_id,familias,kg_estimado,urgencia,limite_en,estado
1,1,30,240,3,2026-11-21T12:00,confirmado
```

## Otros archivos de `datos/semilla/`

No hace falta que los entregue un aliado; los genera el equipo.

- `barrios.csv` (`nombre,comuna,lat,lon`): barrios y comunas de OpenStreetMap. `python -m despacho.semilla --barrios`.
- `vias.csv` (`nombre,lat,lon,osm_u,osm_v`): tramos viales con nombre coloquial, amarrados a la red. `python -m despacho.vias`.
- `lugares_extra.csv` (`nombre,alias,tipo,lat,lon,osm_u,osm_v,origen`): sitios y apodos para ubicar lo que la gente dice. Ver `lugares/README.md`.
