"""Tabla del barrido de FACTOR_CRITICO y aplicación de la regla de elección.

    python -m despacho.sim.barrido despacho/sim/resultados_s2

Lee `factor_<n>/resultados.csv` y escribe `barrido_factor.md` en la misma carpeta. La regla
está en docs/SIMULACION.md, sección 8.1, y se escribió antes de correr el barrido.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from .correr import _num, ic95
from .metricas import METRICAS

REGLA = ["a_tiempo_criticos_pct", "a_tiempo_todos_pct"]          # deciden la elección
OTRAS = ["peor_punto_h", "km"]                                   # se reportan


def leer(ruta: Path) -> dict:
    """{(carga, politica): {semilla: fila}}"""
    datos = {}
    with open(ruta) as fh:
        for f in csv.DictReader(fh):
            datos.setdefault((f["carga"], f["politica"]), {})[int(f["semilla"])] = f
    return datos


def main(carpeta: str) -> None:
    base = Path(carpeta)
    factores = sorted(int(d.name.split("_")[1]) for d in base.glob("factor_*") if (d / "resultados.csv").exists())
    L = ["# Barrido de FACTOR_CRITICO", "",
         "Diferencia pareada `despachox` − `experta` por semilla, con IC del 95 %. "
         "Un factor cumple la regla si, en carga media y en carga alta, ninguna de las dos primeras "
         "métricas tiene el intervalo entero del lado desfavorable.", "",
         "| Factor | Carga | Métrica | `experta` | `despachox` | Diferencia | IC 95 % | ¿Peor? |",
         "|---:|---|---|---:|---:|---:|---|---|"]
    cumple = {}
    for factor in factores:
        datos = leer(base / f"factor_{factor}" / "resultados.csv")
        cumple[factor] = True
        for carga in dict.fromkeys(c for c, _ in datos):
            e, d = datos[(carga, "experta")], datos[(carga, "despachox")]
            semillas = sorted(set(e) & set(d))
            for m in REGLA + OTRAS:
                xe = [float(e[s][m]) for s in semillas]
                xd = [float(d[s][m]) for s in semillas]
                media, lo, hi, _ = ic95([a - b for a, b in zip(xd, xe)])
                desfavorable = hi < 0 if METRICAS[m][1] else lo > 0
                if m in REGLA and desfavorable:
                    cumple[factor] = False
                dec = 2 if m.endswith("_h") else 1
                L.append(f"| {factor} | {carga} | {METRICAS[m][0]} | {_num(sum(xe) / len(xe), dec)} | "
                         f"{_num(sum(xd) / len(xd), dec)} | {_num(media, dec)} | [{_num(lo, dec)}; {_num(hi, dec)}] | "
                         f"{'sí' if desfavorable else 'no'} |")
    elegidos = [f for f in factores if cumple[f]]
    L += ["", "Factores que cumplen la regla: " + (", ".join(map(str, elegidos)) or "ninguno") + ".",
          f"Factor elegido (el menor que cumple): {elegidos[0]}." if elegidos else "No se elige ningún factor."]
    (base / "barrido_factor.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "resultados_s2"))
