"""Corre variantes de la sensibilidad sobre un bloque de semillas, en tandas cortas.

    DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.correr --variantes referencia --desde 0 --semillas 30

Cada tarea es una variante, una semilla y una política, y llama a `despacho.sim.correr.una_corrida`
tal como está: carga media, red y optimizador por defecto (`auto`), 1 segundo de búsqueda. Lo que la
CLI de `despacho.sim.correr` no expone se cambia en memoria, sin editar `despacho/`:

- velocidad medida: `velocidad_medida.aplicar(multiplicador)` en cada proceso hijo;
- demanda: `pedidos_por_punto` = 2,5 (carga media de NIVELES_CARGA) × multiplicador, por `extra`;
- flota: `camperos_menos`, el mismo parámetro de `--camperos-menos`, por `extra`;
- factor crítico: la variable DESPACHOX_FACTOR_CRITICO, igual que `--factor-critico`.

Las variantes de una misma llamada deben compartir velocidad y factor, porque los dos se fijan por
proceso. La tanda deja de arrancar tareas nuevas a los `--tope` segundos; lo que falte se completa
con la misma orden, porque se saltan las tareas que ya están en `resultados/<variante>/*.csv`.
Cada llamada escribe `resultados/<variante>/tanda_<fecha>.csv` y añade una línea a `tandas.txt`.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RESULTADOS = AQUI / "resultados"
BASE = 20261150
CARGA = "media"
LIMITE_S = 1.0
FACTOR_REFERENCIA = 3

# Cada variante cambia un solo supuesto respecto de la referencia de la sensibilidad.
VARIANTES = {
    "referencia": {},
    "velocidad_x0.8": {"vel": 0.8},
    "velocidad_x1.2": {"vel": 1.2},
    "demanda_x0.75": {"demanda": 0.75},
    "demanda_x1.5": {"demanda": 1.5},
    "flota_menos_1": {"camperos_menos": 1},
    "flota_menos_2": {"camperos_menos": 2},
    "factor_1": {"factor": 1},
    "factor_5": {"factor": 5},
}
POLITICAS = ("despachox", "optimiza_una_vez", "experta", "ingenua")    # las largas primero


def parametros(variante: str) -> dict:
    p = {"vel": 1.0, "demanda": 1.0, "camperos_menos": 0, "factor": FACTOR_REFERENCIA}
    p.update(VARIANTES[variante])
    return p


def extra_de(p: dict) -> dict:
    from despacho.sim.escenario import NIVELES_CARGA
    extra = {}
    if p["demanda"] != 1.0:     # después de NIVELES_CARGA: en una_corrida, extra pisa al nivel de carga
        extra["pedidos_por_punto"] = NIVELES_CARGA[CARGA]["pedidos_por_punto"] * p["demanda"]
    if p["camperos_menos"]:
        extra["camperos_menos"] = p["camperos_menos"]
    return extra


def hechas(variante: str) -> set:
    """(semilla, política) que ya están en algún CSV de la variante."""
    out = set()
    for ruta in sorted((RESULTADOS / variante).glob("*.csv")):
        with open(ruta, newline="") as fh:     # una fila cortada por un timeout queda fuera
            out |= {(int(f["semilla"]), f["politica"]) for f in csv.DictReader(fh) if completa(f)}
    return out


def completa(f: dict) -> bool:
    return None not in f.values() and all(v != "" for k, v in f.items() if k in ("semilla", "politica", "segundos_tarea"))


def _preparar(vel: float) -> None:
    """Se ejecuta en cada proceso hijo antes de su primera tarea."""
    os.environ.setdefault("DESPACHOX_SIN_RED", "1")
    from . import velocidad_medida
    velocidad_medida.aplicar(vel)


def _tarea(args) -> list:
    variante, semilla, politica, extra = args
    from despacho import optimizar
    from despacho.sim.correr import una_corrida

    from . import velocidad_medida
    t0 = time.perf_counter()
    filas = una_corrida((CARGA, semilla, [politica], "auto", "auto", LIMITE_S, extra))
    segundos = time.perf_counter() - t0
    for f in filas:
        f.update(variante=variante, vel_medida_x=velocidad_medida.multiplicador_activo(),
                 factor_critico=optimizar.FACTOR_CRITICO, segundos_tarea=round(segundos, 1))
    return filas


def _commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                              cwd=AQUI).stdout.strip() or "sin git"
    except OSError:
        return "sin git"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variantes", required=True, help="separadas por coma: " + ", ".join(VARIANTES))
    ap.add_argument("--base", type=int, default=BASE)
    ap.add_argument("--desde", type=int, default=0, help="primera semilla = base + desde")
    ap.add_argument("--semillas", type=int, default=30)
    ap.add_argument("--politicas", default=",".join(POLITICAS))
    ap.add_argument("--procesos", type=int, default=7)
    ap.add_argument("--tope", type=float, default=330.0, help="segundos tras los que no arranca tareas nuevas")
    a = ap.parse_args(argv)

    variantes = a.variantes.split(",")
    ps = {v: parametros(v) for v in variantes}
    vel = {p["vel"] for p in ps.values()}
    factor = {p["factor"] for p in ps.values()}
    if len(vel) > 1 or len(factor) > 1:
        ap.error("las variantes de una llamada deben compartir velocidad y factor crítico")
    vel, factor = vel.pop(), factor.pop()
    os.environ["DESPACHOX_FACTOR_CRITICO"] = str(factor)        # los hijos la heredan al arrancar
    os.environ.setdefault("DESPACHOX_SIN_RED", "1")
    politicas = sorted(a.politicas.split(","), key=POLITICAS.index)
    semillas = [a.base + a.desde + i for i in range(a.semillas)]
    tareas = []
    for pol in politicas:
        for v in variantes:
            ya = hechas(v)
            tareas += [(v, s, pol, extra_de(ps[v])) for s in semillas if (s, pol) not in ya]
    # Primero las políticas que tardan un segundo; después `despachox`, con la demanda alta delante.
    # Así el tope corta, si corta, tareas largas que se completan en la tanda siguiente.
    tareas.sort(key=lambda t: (t[2] == "despachox", VARIANTES[t[0]].get("demanda", 1.0) <= 1.0))
    print(f"{len(tareas)} tareas pendientes de {len(politicas) * len(variantes) * len(semillas)}", flush=True)
    if not tareas:
        return 0

    inicio, t0 = dt.datetime.now(), time.perf_counter()
    filas, errores, canceladas = [], [], 0
    marca, escritores = f"{inicio:%Y%m%d_%H%M%S}", {}

    def guardar(f: dict) -> None:
        """Cada fila se escribe al terminar su tarea: si la tanda se corta, lo hecho queda en disco."""
        v = f["variante"]
        if v not in escritores:
            (RESULTADOS / v).mkdir(parents=True, exist_ok=True)
            ruta = RESULTADOS / v / f"tanda_{marca}.csv"
            fh = open(ruta, "w", newline="")
            w = csv.DictWriter(fh, fieldnames=["variante"] + [k for k in f if k != "variante"])
            w.writeheader()
            escritores[v] = (fh, w, ruta)
        fh, w, _ = escritores[v]
        w.writerow({k: (round(x, 4) if isinstance(x, float) else x) for k, x in f.items()})
        fh.flush()

    with ProcessPoolExecutor(a.procesos, initializer=_preparar, initargs=(vel,)) as ex:
        futuros = {ex.submit(_tarea, t): t for t in tareas}
        for fut in as_completed(futuros):
            v, s, pol, _ = futuros[fut]
            if fut.cancelled():
                continue
            try:
                nuevas = fut.result()
            except Exception as e:  # noqa: BLE001  (se anota y la tanda sigue)
                errores.append(f"{v} {s} {pol}: {type(e).__name__}: {e}")
                print(f"ERROR {v} {s} {pol}: {e}", file=sys.stderr, flush=True)
                continue
            filas += nuevas
            for f in nuevas:
                guardar(f)
            f = nuevas[0]
            print(f"{v:15s} {s} {pol:16s} {f['segundos_tarea']:6.1f} s  críticos {f['a_tiempo_criticos_pct']:5.1f}  "
                  f"vencido {f['perecedero_vencido_pct']:4.1f}  llamadas {f['recalculos']}", flush=True)
            if not canceladas and time.perf_counter() - t0 > a.tope:
                canceladas = sum(x.cancel() for x in futuros if not x.done()) or -1
    total = time.perf_counter() - t0
    canceladas = max(canceladas, 0)

    for fh, _, ruta in escritores.values():
        fh.close()
        print(f"Escrito {ruta}")
    c1, c5, c15 = os.getloadavg()
    linea = (f"{inicio:%Y-%m-%d %H:%M:%S} commit {_commit()} variantes {','.join(variantes)} "
             f"semillas {semillas[0]}-{semillas[-1]} políticas {','.join(politicas)} procesos {a.procesos} "
             f"tareas {len(tareas)} hechas {len(filas)} canceladas {canceladas} errores {len(errores)} "
             f"duración {total:.0f} s carga {c1:.1f}/{c5:.1f}/{c15:.1f}")
    for v in variantes:
        (RESULTADOS / v).mkdir(parents=True, exist_ok=True)
        with open(RESULTADOS / v / "tandas.txt", "a") as fh:
            fh.write(linea + "\n")
            for e in errores:
                fh.write(f"    {e}\n")
    print(linea)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
