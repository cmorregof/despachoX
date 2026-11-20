# Escenario público: Manizales después del sismo

Este escenario corre la mesa con lugares y parámetros reales. Son 50 puntos, 2 acopios, 9 vehículos, 28 pedidos y 28 lotes. Solo los pedidos y los lotes son sintéticos, porque no existen datos públicos de ninguno de los dos. Generado el 20 de noviembre de 2026 con `/home/claude/trabajo/agente-11/generar.py` (semilla fija).

## Qué es real

Con la fuente de cada informe:
- **Puntos y acopios** (`puntos.csv`, `acopios.csv`): lugares con fuente y coordenada de OpenStreetMap. Ver `puntos_y_acopios.md`.
- **Flota** (`vehiculos.csv`): referencia de 9 vehículos. Ver `flota_perecederos_costos.md`.
- **Ración** (`raciones.csv`): 555 g de ración seca por persona y día, 2,9 personas por hogar (DANE, censo 2018). Ver `demanda.md`.
- **Vida útil** (`vida_util.csv`): horas sin frío y con frío por producto. Ver `flota_perecederos_costos.md`.
- **Ocupación de albergues**: 90 personas en el Coliseo Mayor (Defensoría, 25 de agosto) y 245 en el albergue junto al Coliseo Menor (Noticias RCN, 12 de agosto; la nota dice entre 114 y 245, se toma el máximo).

## Qué es sintético

- **Pedidos** (`pedidos.csv`): 28 pedidos de 26 puntos, repartidos en las 12 comunas más una zona rural. 24 son de puntos críticos y 2 son segundos pedidos de albergue. Cantidades y horas inventadas; textos escritos como los escribiría un líder comunitario, sin nombres ni teléfonos.
- **Lotes** (`lotes.csv`): 28 lotes, uno por producto y acopio. Las cantidades son inventadas.

## Supuestos

- **Personas atendidas.** Solo los dos albergues tienen ocupación reportada. El dataset no trae cupos del ICBF. Para el resto se supuso: hogares infantiles de 80 a 120, CDI de 60 a 100, hospitales de 70 a 100, centro día 60, geriátrico 60, centros de salud 40, salones comunales 60 y 70. Familias = personas / 2,9.
- **Kilos.** Ración seca por persona y día por los días del pedido: 3 días para albergues, hospitales, geriátrico y salones; 2 días para el resto. CDI y hogares infantiles piden además leche, y los hogares piden huevos y fruta, con la ración mensual del ICBF dividida por 30 (referencia, no norma de emergencia). Compota (0,1 kg por niño y día) y leche de fórmula (0,1 kg por lactante y día, en dos hogares) no tienen fuente: son supuestos. Cada albergue tiene un segundo pedido de frescos (fruta, verdura, huevos).
- **Urgencia y hora límite**, como en `semilla.py`: críticos con urgencia 3 y 4 horas; el resto con urgencia 1 o 2 y 20 o 10 horas. Tres pedidos están en `nuevo` (ids 3, 16 y 20) y el optimizador no los toma hasta que alguien los confirme.
- **Inventario.** Cubre entre 1,16 y 1,23 veces la demanda de cada producto (1,18 en total), con el 65 % en el acopio 1 y el 35 % en el 2. Incluye los secos de la ración, porque sin ellos los pedidos no tendrían con qué surtirse.
- **Frío.** Los dos acopios tienen `tiene_frio` vacío (no se sabe), así que todas las vidas útiles son sin frío. Ningún lote lleva `empaque_activo=1`, porque ningún acopio tiene frío confirmado. Con esa regla, la leche pasteurizada (2 horas sin frío) y el pollo (2 horas) no se pueden despachar. Por eso la leche del escenario es UHT, que `vida_util.csv` marca como no perecedera, y el pollo y el pan se dejaron fuera: ninguna ración los incluye.
- **Vencimientos.** Verdura 96 horas (tomate maduro), huevos 360 horas (bodega entre 22 y 32 °C) y fruta 72 horas. Este último es un supuesto nuestro: la fuente de fruta no trae horas sin frío.

## Cómo cargarlo

```
DESPACHOX_DB=/tmp/escenario.db DESPACHOX_GRAFO=despliegue/grafo/manizales_region.graphml \
  python -m despacho.semilla --cargar --reiniciar --origen datos_publicos/
DESPACHOX_DB=/tmp/escenario.db DESPACHOX_GRAFO=despliegue/grafo/manizales_region.graphml \
  python -m despacho.optimizar --segundos 3
```

La carga dice «real» en los cinco archivos.

## Resultado del plan

Con 3 segundos de búsqueda (3,5 s de cálculo):
- 25 de 25 pedidos confirmados atendidos, sin faltantes (3.064 kg, de ellos 301 kg perecederos).
- 23 de 23 paradas críticas a tiempo, sin retrasos.
- 5 de 9 vehículos: el camión mediano, tres camperos y la furgoneta.
- El optimizador no imprime kilómetros.

Un aviso: el Hospital Geriátrico San Isidro (punto 6) queda aislado para camión en la red, y lo atiende un campero.

Ninguna cifra de este escenario va al pitch sin revisión humana de las fuentes, por la regla de `docs/PROBLEMA.md`.
