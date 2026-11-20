#!/usr/bin/env bash
# Arranque en la nube. Un solo servicio, porque el bot, el tablero y el optimizador comparten
# un archivo SQLite y un volumen solo se monta en un servicio.
set -euo pipefail

export DESPACHOX_DB="${DESPACHOX_DB:-/data/despachox.db}"
export DESPACHOX_GRAFO="${DESPACHOX_GRAFO:-/data/cache/manizales_region.graphml}"
mkdir -p "$(dirname "$DESPACHOX_DB")" "$(dirname "$DESPACHOX_GRAFO")"

# 1. Red vial: se usa la copia del repositorio si existe; si no, se baja de OpenStreetMap.
if [ ! -f "$DESPACHOX_GRAFO" ]; then
  if [ -f despliegue/grafo/manizales_region.graphml ]; then
    echo "[arranque] red vial: copia del repositorio"
    cp despliegue/grafo/manizales_region.graphml "$DESPACHOX_GRAFO"
  else
    echo "[arranque] red vial: descargando de OpenStreetMap (puede tardar varios minutos)"
    python -m despacho.red
  fi
fi

# 2. Datos: la primera vez, o cuando se pide con DESPACHOX_REINICIAR=1, se carga la semilla sintética.
if [ ! -f "$DESPACHOX_DB" ] || [ "${DESPACHOX_REINICIAR:-0}" = "1" ]; then
  echo "[arranque] cargando datos de prueba"
  python -m despacho.semilla --cargar --reiniciar
fi

# 3. Bot en segundo plano. Si se cae, vuelve a arrancar. Sin token no arranca y el tablero sigue.
if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
  ( while true; do python -m entrada.bot || true; echo "[arranque] el bot se detuvo; reintento en 5 s"; sleep 5; done ) &
else
  echo "[arranque] sin TELEGRAM_BOT_TOKEN: el bot no arranca"
fi

# 4. Tablero en primer plano, en el puerto que asigna la plataforma.
exec streamlit run tablero/app.py --server.port "${PORT:-8501}" --server.address 0.0.0.0 \
  --server.headless true --browser.gatherUsageStats false
