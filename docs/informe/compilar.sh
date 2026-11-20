#!/usr/bin/env bash
# Compila el informe de contexto con lualatex (vía latexmk) y borra los archivos auxiliares.
# Uso: ./compilar.sh   (desde cualquier carpeta)
set -euo pipefail
cd "$(dirname "$0")"
export TZ=America/Bogota

latexmk -lualatex -interaction=nonstopmode -halt-on-error informe_contexto.tex

# Avisa si quedó algún desborde antes de borrar el registro.
if grep -q "Overfull \\\\hbox" informe_contexto.log; then
  echo "AVISO: hay líneas desbordadas. Revísalas:"
  grep -n "Overfull \\\\hbox" informe_contexto.log
fi

latexmk -c informe_contexto.tex
rm -f informe_contexto.run.xml informe_contexto.bbl informe_contexto.synctex.gz

echo "PDF listo: $(pwd)/informe_contexto.pdf"
