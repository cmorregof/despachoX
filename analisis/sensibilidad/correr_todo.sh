#!/bin/sh
# Corre todas las tandas de la sensibilidad y arma la tabla. Se puede cortar y volver a lanzar:
# cada tanda salta las tareas que ya están en analisis/sensibilidad/resultados/<variante>/*.csv.
#
#   PY=/ruta/al/python N=60 sh analisis/sensibilidad/correr_todo.sh
#
# Cada tanda deja de arrancar tareas a los 300 s y no pasa de 570 s (timeout).
set -u
cd "$(dirname "$0")/../.." || exit 1
PY=${PY:-python}
N=${N:-60}
export DESPACHOX_SIN_RED=1
GRUPO_A=referencia,demanda_x0.75,demanda_x1.5,flota_menos_1,flota_menos_2   # velocidad x1 y factor 3

hasta=5
while [ "$hasta" -le "$N" ]; do        # el grupo A, de a cinco semillas
  timeout 570 "$PY" -m analisis.sensibilidad.correr --variantes "$GRUPO_A" --desde 0 --semillas "$hasta" --tope 300
  hasta=$((hasta + 5))
done
for v in velocidad_x0.8 velocidad_x1.2 factor_1 factor_5; do   # cada una fija su velocidad o su factor
  for intento in 1 2 3; do
    timeout 570 "$PY" -m analisis.sensibilidad.correr --variantes "$v" --desde 0 --semillas "$N" --tope 300
  done
done
"$PY" -m analisis.sensibilidad.tabla --semillas "$N"
