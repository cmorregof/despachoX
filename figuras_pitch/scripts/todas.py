"""Regenera las cinco figuras del pitch con un solo comando.

Uso (desde la raíz del repositorio, con un Python que tenga matplotlib, osmnx y geopandas):
    DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py [--fuente FAMILIA] [--salida CARPETA]
                                                              [--sim CSV_O_CARPETA] [--marca-sim TEXTO]

Sin --sim, la figura (e) se dibuja con despacho/sim/resultados/resultados.csv y la marca «Ejemplo con resultados
anteriores, no citar». Cuando lleguen los resultados nuevos, pase --sim con su ruta y --marca-sim "" para quitar la
marca (y --titulo-sim con el mensaje que la figura deba decir).
"""
import argparse
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SIM_EJEMPLO = "despacho/sim/resultados/resultados.csv"
MARCA_EJEMPLO = "Ejemplo con resultados anteriores, no citar"


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--fuente", default=None)
    p.add_argument("--salida", default=str(RAIZ / "figuras_pitch"))
    p.add_argument("--sim", default=SIM_EJEMPLO)
    p.add_argument("--marca-sim", default=None)
    p.add_argument("--titulo-sim", default=None)
    args = p.parse_args()
    comunes = ["--salida", args.salida] + (["--fuente", args.fuente] if args.fuente else [])
    marca = args.marca_sim if args.marca_sim is not None else (MARCA_EJEMPLO if args.sim == SIM_EJEMPLO else "")
    nombre_sim = "e_simulacion_ejemplo" if args.sim == SIM_EJEMPLO else "e_simulacion"
    pasos = [
        ["mapa_territorios.py"],
        ["cuello_despacho.py"],
        ["regla_arquitectura.py"],
        ["cierres_sin_sismo.py"],
        ["sim_resultados.py", "--entrada", args.sim, "--nombre", nombre_sim, "--marca", marca]
        + (["--titulo", args.titulo_sim] if args.titulo_sim else []),
    ]
    fallos = 0
    for paso in pasos:
        orden = [sys.executable, str(AQUI / paso[0])] + paso[1:] + comunes
        print(f"\n== {paso[0]}", flush=True)
        r = subprocess.run(orden, cwd=RAIZ)
        fallos += r.returncode != 0
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
