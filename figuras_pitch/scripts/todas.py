"""Regenera todas las figuras del pitch con un solo comando.

Uso (desde cualquier carpeta, con un Python que tenga matplotlib, osmnx y geopandas):
    DESPACHOX_SIN_RED=1 python figuras_pitch/scripts/todas.py [--fuente FAMILIA] [--salida CARPETA]
        [--sim CSV_O_CARPETA] [--titulo-sim TEXTO] [--marca-sim TEXTO]

Figura (e). Sin --sim se dibuja con despacho/sim/resultados/resultados.csv. Si el contenido de ese archivo, o del que
se pase con --sim, es una corrida que no se cita (CORRIDAS_ANTERIORES en sim_resultados.py), la figura se llama
e_simulacion_ejemplo y lleva la marca «Ejemplo con resultados anteriores, no citar». Con cualquier otro contenido se
llama e_simulacion y no lleva marca, salvo que se pida una con --marca-sim. La decisión mira el contenido del CSV y
no su ruta, así que no importa cómo se escriba la ruta ni si una corrida nueva sobrescribe la carpeta vieja.

Al final imprime un resumen por figura y sale con código 1 si algún script falló o dejó líneas AVISO.
"""
import argparse
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SIM_POR_DEFECTO = RAIZ / "despacho" / "sim" / "resultados" / "resultados.csv"
sys.path.insert(0, str(AQUI))
from sim_resultados import corrida_anterior  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--fuente", default=None, help="familia instalada o archivo de fuente")
    p.add_argument("--salida", default=str(RAIZ / "figuras_pitch"))
    p.add_argument("--sim", default=None, help="resultados.csv o carpeta de la simulación para la figura (e)")
    p.add_argument("--marca-sim", default=None, help="advertencia visible en la figura (e); las corridas que no se "
                                                     "citan la llevan siempre")
    p.add_argument("--titulo-sim", default=None, help="título de la figura (e), con lo que muestran los resultados")
    args = p.parse_args()
    sim = Path(args.sim).resolve() if args.sim else SIM_POR_DEFECTO
    anterior = corrida_anterior(sim)
    nombre_sim = "e_simulacion_ejemplo" if anterior else "e_simulacion"
    print(f"figura (e): {sim} -> {nombre_sim}" + (f" ({anterior})" if anterior else ""))
    comunes = ["--salida", str(Path(args.salida).resolve())] + (["--fuente", args.fuente] if args.fuente else [])
    pasos = [
        ["mapa_territorios.py"],
        ["mapa_territorios.py", "--solo", "1"],
        ["cuello_despacho.py"],
        ["regla_arquitectura.py"],
        ["cierres_sin_sismo.py"],
        ["sim_resultados.py", "--entrada", str(sim), "--nombre", nombre_sim]
        + (["--marca", args.marca_sim] if args.marca_sim is not None else [])
        + (["--titulo", args.titulo_sim] if args.titulo_sim else []),
    ]
    resumen = []
    for paso in pasos:
        orden = [sys.executable, str(AQUI / paso[0])] + paso[1:] + comunes
        etiqueta = " ".join(paso[:3]) if paso[1:2] == ["--solo"] else paso[0]
        print(f"\n== {etiqueta}", flush=True)
        r = subprocess.run(orden, cwd=RAIZ, stderr=subprocess.PIPE, text=True)
        sys.stderr.write(r.stderr)
        sys.stderr.flush()
        avisos = sum(1 for linea in r.stderr.splitlines() if linea.startswith("AVISO "))
        estado = (f"{avisos} AVISO" if avisos else f"falló con código {r.returncode}" if r.returncode else "bien")
        resumen.append((etiqueta, estado))
    print("\nResumen:")
    for nombre, estado in resumen:
        print(f"  {nombre}: {estado}")
    malos = [n for n, est in resumen if est != "bien"]
    if malos:
        print(f"Hay que revisar {len(malos)} figura(s) antes de proyectarlas: {', '.join(malos)}", file=sys.stderr)
    sys.exit(1 if malos else 0)


if __name__ == "__main__":
    main()
