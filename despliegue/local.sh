#!/usr/bin/env bash
# Arranque en un portátil del centro de acopio, con o sin internet (docs/SIN_CONEXION.md, nivel 2).
# Corre lo mismo que Railway: base, optimizador, red vial y tablero, con la base en datos/.
#
# Uso, desde la raíz del repositorio:
#   bash despliegue/local.sh                      # sin red (por defecto): sin bot y sin modelo
#   DESPACHOX_SIN_RED=0 bash despliegue/local.sh  # con internet: también arranca el bot
#   DESPACHOX_REINICIAR=1 bash despliegue/local.sh   # borra la base y carga la semilla
#
# Antes de quedarse sin internet hay que haber instalado una vez las dependencias:
#   python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")/.."

export DESPACHOX_SIN_RED="${DESPACHOX_SIN_RED:-1}"
export DESPACHOX_DB="${DESPACHOX_DB:-$PWD/datos/despachox.db}"
export DESPACHOX_GRAFO="${DESPACHOX_GRAFO:-$PWD/despacho/cache/manizales_region.graphml}"
PY="${PYTHON:-.venv/bin/python}"
[ -x "$PY" ] || PY=python3
mkdir -p "$(dirname "$DESPACHOX_DB")" "$(dirname "$DESPACHOX_GRAFO")"

if ! "$PY" -c "import fpdf, ortools, osmnx, streamlit, segno" 2>/dev/null; then
  echo "[local] faltan dependencias en $PY. Con internet: $PY -m pip install -r requirements.txt" >&2
  exit 1
fi

# 1. Red vial: la del caché, o la copia que viene en el repositorio. Sin red nunca se descarga.
if [ ! -f "$DESPACHOX_GRAFO" ]; then
  if [ -f despliegue/grafo/manizales_region.graphml ]; then
    echo "[local] red vial: copia del repositorio"
    cp despliegue/grafo/manizales_region.graphml "$DESPACHOX_GRAFO"
  elif [ "$DESPACHOX_SIN_RED" = "1" ]; then
    echo "[local] no hay red vial en $DESPACHOX_GRAFO ni en despliegue/grafo/ y no hay internet" >&2
    exit 1
  else
    echo "[local] red vial: descargando de OpenStreetMap (puede tardar varios minutos)"
    "$PY" -m despacho.red
  fi
fi

# 2. Datos: la primera vez, o con DESPACHOX_REINICIAR=1, la semilla sintética.
if [ ! -f "$DESPACHOX_DB" ] || [ "${DESPACHOX_REINICIAR:-0}" = "1" ]; then
  echo "[local] cargando datos de prueba en $DESPACHOX_DB"
  "$PY" -m despacho.semilla --cargar --reiniciar
fi

# 3. Bot: solo con internet y con token.
if [ "$DESPACHOX_SIN_RED" = "1" ]; then
  echo "[local] DESPACHOX_SIN_RED=1: el bot no arranca y nada llama al modelo"
elif [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  ( while true; do "$PY" -m entrada.bot || true; echo "[local] el bot se detuvo; reintento en 5 s"; sleep 5; done ) &
else
  echo "[local] sin TELEGRAM_BOT_TOKEN: el bot no arranca"
fi

# 4. Tablero. Escucha en la red local para que otro equipo del acopio lo abra por wifi sin internet.
PUERTO="${PORT:-8501}"
IP="$(ipconfig getifaddr en0 2>/dev/null || hostname -I 2>/dev/null | awk '{print $1}' || true)"
echo "[local] tablero en http://localhost:$PUERTO${IP:+ y en la red local http://$IP:$PUERTO}"
echo "[local] hojas de ruta: $PY -m despacho.hoja  (quedan en $(dirname "$DESPACHOX_DB")/hojas/)"
exec "$PY" -m streamlit run tablero/app.py --server.port "$PUERTO" --server.address 0.0.0.0 \
  --server.headless true --browser.gatherUsageStats false
