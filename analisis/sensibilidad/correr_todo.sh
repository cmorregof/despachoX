#!/bin/sh
# Corre todas las tandas de la sensibilidad y arma la tabla. Se puede cortar y volver a lanzar:
# cada tanda salta las tareas que ya están en analisis/sensibilidad/resultados/<variante>/*.csv.
# Para repetir desde cero, primero hay que apartar esa carpeta (por ejemplo, renombrarla); si no,
# todas las tandas dicen «0 tareas pendientes» y solo se rehace la tabla.
#
#   PY=/ruta/al/python N=60 sh analisis/sensibilidad/correr_todo.sh
#
# Necesita `timeout`, de GNU coreutils (en macOS: brew install coreutils). Cada tanda deja de arrancar
# tareas a los 300 s y `timeout` la corta a los 480 s, los 8 minutos que puede durar una tanda. Si la
# corta, las filas terminadas ya están en disco y la tanda siguiente completa el resto, pero la tanda
# cortada no deja su línea en tandas.txt. Con 7 procesos, las 60 semillas de las nueve variantes
# sumaron unas 2,2 horas de tandas.
set -u
command -v timeout >/dev/null || { echo 'falta timeout: brew install coreutils'; exit 1; }
cd "$(dirname "$0")/../.." || exit 1
PY=${PY:-python}
N=${N:-60}
export DESPACHOX_SIN_RED=1
GRUPO_A=referencia,demanda_x0.75,demanda_x1.5,flota_menos_1,flota_menos_2   # velocidad x1 y factor 3

hasta=5
while [ "$hasta" -le "$N" ]; do        # el grupo A, de a cinco semillas
  timeout 480 "$PY" -m analisis.sensibilidad.correr --variantes "$GRUPO_A" --desde 0 --semillas "$hasta" --tope 300
  hasta=$((hasta + 5))
done
for intento in 1 2; do                 # lo que el tope o el timeout dejaron pendiente en el grupo A
  timeout 480 "$PY" -m analisis.sensibilidad.correr --variantes "$GRUPO_A" --desde 0 --semillas "$N" --tope 300
done
for v in velocidad_x0.8 velocidad_x1.2 factor_1 factor_5; do   # cada una fija su velocidad o su factor
  for intento in 1 2 3; do
    timeout 480 "$PY" -m analisis.sensibilidad.correr --variantes "$v" --desde 0 --semillas "$N" --tope 300
  done
done
"$PY" -m analisis.sensibilidad.tabla --semillas "$N"
