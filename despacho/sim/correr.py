"""Corre el experimento: las mismas semillas para todas las políticas y diferencia pareada.

    python -m despacho.sim.correr                       # 30 semillas, carga media
    python -m despacho.sim.correr --carga todas         # holgada, media y alta
    python -m despacho.sim.correr --semillas 5 --red malla --salida /tmp/prueba
    python -m despacho.sim.correr --velocidades medidas  # velocidades de datos_publicos/velocidades.csv

Escribe `resultados.csv` (una fila por carga, semilla y política) y `resumen.md`.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy import stats

from .escenario import NIVELES_CARGA, Parametros, generar
from .metricas import METRICAS, calcular, descripcion_escenario
from .motor import simular
from .politicas import POLITICAS, InsercionProvisional, crear, optimizador_por_defecto
from .red_sim import MODOS_VELOCIDAD, VARIABLE_VELOCIDADES, cargar_red, modo_velocidades

SEMILLA_BASE = 20261120          # semillas de evaluación: base, base+1, ...
PARES = [("despachox", "ingenua"), ("despachox", "experta"),
         ("despachox", "optimiza_una_vez"), ("optimiza_una_vez", "ingenua"),
         ("despachox", "despachox_sin_confirmar"), ("despachox_sin_confirmar", "experta")]
PRINCIPALES = ["a_tiempo_criticos_pct", "perecedero_vencido_pct"]


def _optimizador(nombre: str, limite_s: float, red: str = "auto"):
    if nombre == "provisional":
        return InsercionProvisional(limite_s)
    if nombre == "b":
        from .adaptador_b import OptimizadorB
        return OptimizadorB(limite_s=limite_s)
    return optimizador_por_defecto(limite_s, red)


def una_corrida(args) -> list:
    carga, semilla, politicas, red, optimizador, limite_s, extra = args
    esc = generar(semilla, red, Parametros(**{**NIVELES_CARGA[carga], **extra}))
    filas = []
    for nombre in politicas:
        opt = _optimizador(optimizador, limite_s, red)
        r = simular(esc, crear(nombre, opt))
        usa_opt = nombre in ("optimiza_una_vez", "despachox")
        filas.append({"carga": carga, "semilla": semilla, "politica": nombre,
                      **descripcion_escenario(r), **calcular(r),
                      "fallos_optimizador": getattr(opt, "fallos", 0) if usa_opt else 0})
    return filas


def ic95(x) -> tuple:
    """Media e intervalo de confianza del 95 % (t de Student) de una muestra."""
    x = np.asarray([v for v in x if not math.isnan(v)], float)
    n = len(x)
    if n < 2:
        return (float(x.mean()) if n else float("nan"), float("nan"), float("nan"), n)
    medio = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / math.sqrt(n)
    return float(x.mean()), float(x.mean() - medio), float(x.mean() + medio), n


def _num(x, dec=1):
    if math.isnan(x):
        return "s. d."
    texto = f"{x:.{dec}f}"
    if float(texto) == 0:
        texto = texto.lstrip("-")
    return texto.replace(".", ",").replace("-", "−")


def resumen_md(filas, politicas, meta) -> str:
    L = ["# Resultados de la simulación", "",
         f"Generado el {meta['fecha']} con `python -m despacho.sim.correr`. Commit `{meta['commit']}`.", "",
         f"- Red: {meta['red']}.",
         f"- Optimizador de `optimiza_una_vez` y `despachox`: {meta['optimizador']}.",
         f"- Semillas: {meta['n']} por nivel de carga, de {meta['base']} a {meta['base'] + meta['n'] - 1}, "
         "las mismas para todas las políticas.",
         "- Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.",
         f"- Llamadas al optimizador que terminaron en error: {sum(f['fallos_optimizador'] for f in filas)}."]
    if meta.get("variante"):
        L.append(f"- Variante: {meta['variante']}.")
    L.append("")
    for carga in dict.fromkeys(f["carga"] for f in filas):
        sub = [f for f in filas if f["carga"] == carga]
        por = {p: sorted((f for f in sub if f["politica"] == p), key=lambda f: f["semilla"]) for p in politicas}
        uno = por[politicas[0]]
        L += [f"## Carga {carga}", "",
              f"Escenarios: {np.mean([f['puntos'] for f in uno]):.0f} puntos, "
              f"{np.mean([f['pedidos'] for f in uno]):.0f} pedidos, "
              f"{_num(np.mean([f['kg_pedidos'] for f in uno]) / 1000)} t, "
              f"{_num(np.mean([f['vehiculos'] for f in uno]))} vehículos y "
              f"{_num(np.mean([f['cierres'] for f in uno]))} cierres en promedio.", "",
              "### Media por política (desviación estándar entre semillas)", "",
              "| Métrica | " + " | ".join(f"`{p}`" for p in politicas) + " |",
              "|---|" + "---:|" * len(politicas)]
        for m, (desc, _) in METRICAS.items():
            celdas = []
            for p in politicas:
                x = np.array([f[m] for f in por[p]], float)
                dec = 2 if m.endswith("_s") or m.endswith("_h") else 1
                celdas.append(f"{_num(float(np.nanmean(x)), dec)} ({_num(float(np.nanstd(x, ddof=1)), dec)})")
            L.append(f"| {desc} | " + " | ".join(celdas) + " |")
        L += ["", "### Diferencias pareadas (los dos primeros indicadores son los del reto)", "",
              "| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |",
              "|---|---|---:|---|---|"]
        for a, b in PARES:
            if a not in por or b not in por:
                continue
            for m in PRINCIPALES + ["a_tiempo_todos_pct", "demanda_no_atendida_pct", "llegada_media_h",
                      "peor_punto_h", "km"]:
                d = [fa[m] - fb[m] for fa, fb in zip(por[a], por[b])]
                media, lo, hi, n = ic95(d)
                signo = 1 if METRICAS[m][1] else -1
                validos = [v for v in d if not math.isnan(v)]
                mejor = sum(signo * v > 1e-9 for v in validos)
                peor = sum(signo * v < -1e-9 for v in validos)
                dec = 2 if m.endswith("_h") else 1
                L.append(f"| `{a}` − `{b}` | {METRICAS[m][0]} | {_num(media, dec)} | "
                         f"[{_num(lo, dec)}; {_num(hi, dec)}] | {mejor} / {n - mejor - peor} / {peor} |")
        L.append("")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semillas", type=int, default=30)
    ap.add_argument("--base", type=int, default=SEMILLA_BASE)
    ap.add_argument("--carga", default="media", help="holgada, media, alta o todas")
    ap.add_argument("--red", default="auto", help="auto, osm o malla")
    ap.add_argument("--optimizador", default="auto", help="auto, b o provisional")
    ap.add_argument("--limite", type=float, default=1.0, help="segundos de búsqueda por llamada al optimizador")
    ap.add_argument("--politicas", default=",".join(POLITICAS))
    ap.add_argument("--salida", default=str(Path(__file__).parent / "resultados"))
    ap.add_argument("--procesos", type=int, default=6)
    ap.add_argument("--factor-critico", type=int, help="FACTOR_CRITICO de despacho/optimizar.py")
    ap.add_argument("--p-error", type=float, help="probabilidad de que un pedido se registre en otro punto")
    ap.add_argument("--cierres", type=int, help="número fijo de cierres por jornada")
    ap.add_argument("--camperos-menos", type=int, help="camperos que se le quitan a la flota")
    ap.add_argument("--velocidades", choices=MODOS_VELOCIDAD,
                    help="modelo (las de despacho/red.py, por defecto) o medidas (datos_publicos/velocidades.csv)")
    ap.add_argument("--vida-util", choices=("rango", "csv"),
                    help="rango (6 a 48 h, por defecto) o csv (por producto, datos_publicos/vida_util.csv)")
    a = ap.parse_args(argv)

    extra, variante = {}, []
    if a.velocidades is not None:         # los procesos hijos heredan la variable al arrancar
        os.environ[VARIABLE_VELOCIDADES] = a.velocidades
    if modo_velocidades() == "medidas":
        variante.append("velocidades medidas de datos_publicos/velocidades.csv, también en el optimizador")
    if a.factor_critico is not None:      # los procesos hijos heredan la variable al arrancar
        os.environ["DESPACHOX_FACTOR_CRITICO"] = str(a.factor_critico)
        variante.append(f"FACTOR_CRITICO = {a.factor_critico}")
    if a.p_error is not None:
        extra["p_error"] = a.p_error
        variante.append(f"error de ubicación de pedidos p = {a.p_error}")
    if a.cierres is not None:
        extra["cierres_min"] = extra["cierres_max"] = a.cierres
        variante.append(f"{a.cierres} cierres por jornada")
    if a.camperos_menos is not None:
        extra["camperos_menos"] = a.camperos_menos
        variante.append(f"flota con {a.camperos_menos} camperos menos")
    if a.vida_util is not None and a.vida_util != "rango":
        extra["vida_util"] = a.vida_util
        variante.append("vida útil por producto de datos_publicos/vida_util.csv")

    cargas = list(NIVELES_CARGA) if a.carga == "todas" else a.carga.split(",")
    politicas = a.politicas.split(",")
    tareas = [(c, a.base + i, politicas, a.red, a.optimizador, a.limite, extra)
              for c in cargas for i in range(a.semillas)]
    if a.procesos > 1:
        with ProcessPoolExecutor(a.procesos) as ex:
            filas = [f for fs in ex.map(una_corrida, tareas) for f in fs]
    else:
        filas = [f for t in tareas for f in una_corrida(t)]

    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with open(salida / "resultados.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        for f in filas:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in f.items()})
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                                cwd=Path(__file__).parent).stdout.strip() or "sin git"
    except OSError:
        commit = "sin git"
    meta = {"fecha": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "commit": commit,
            "red": cargar_red(a.red).origen, "optimizador": _optimizador(a.optimizador, a.limite, a.red).nombre,
            "n": a.semillas, "base": a.base, "variante": "; ".join(variante)}
    texto = resumen_md(filas, politicas, meta)
    (salida / "resumen.md").write_text(texto + "\n")
    print(texto)
    print(f"\nEscrito en {salida}/resultados.csv y {salida}/resumen.md")


if __name__ == "__main__":
    main()
