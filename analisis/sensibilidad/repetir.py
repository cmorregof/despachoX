"""Repite con el código versionado las tandas que corrieron antes de que el envoltorio entrara al repositorio.

    DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.repetir

Las tandas de las 00:11 a las 00:52 del 21 de noviembre corrieron con `correr.py` y
`velocidad_medida.py` todavía sin versionar. Por eso su línea de `tandas.txt` registra el commit
7131261, el de `main` del que sale la rama. El envoltorio entró al repositorio después, en 1e74acc.
Este script vuelve a correr esas tareas con el código versionado y compara cada fila con la original.

- `ingenua` y `experta` no llaman al optimizador ni dependen del reloj, así que deben salir idénticas.
- `optimiza_una_vez` y `despachox` cortan la búsqueda del optimizador por tiempo de reloj, así que
  pueden salir distintas aunque el código sea el mismo (`docs/SIMULACION.md`, sección 8.2).

Por defecto repite todas las filas de `ingenua`, `experta` y `optimiza_una_vez` de esas tandas, y
`despachox` en las 7 semillas de la medición de tiempo de la referencia. Escribe
`resultados/repeticion/filas.csv` y `resultados/repeticion.md`, sin tocar los CSV de las variantes.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from despacho.sim.correr import _num

from .correr import POLITICAS, RESULTADOS, VARIANTES, _commit, _preparar, _tarea, completa, extra_de, parametros

COMMIT_SIN_VERSIONAR = "7131261"
SALIDA = RESULTADOS / "repeticion"
# Se comparan todas las columnas salvo las que identifican la tarea y las que miden tiempo de reloj.
IDENTIFICAN = {"variante", "carga", "semilla", "politica"}
RELOJ = {"segundos_tarea", "recalculo_medio_s", "recalculo_max_s"}
NO_COMPARAR = IDENTIFICAN | RELOJ
RESUMEN = ("a_tiempo_criticos_pct", "a_tiempo_todos_pct", "perecedero_vencido_pct", "km")


def tandas_sin_versionar(variante: str) -> list:
    """Archivos CSV de la variante que salen de tandas con el commit 7131261, según su `tandas.txt`."""
    carpeta = RESULTADOS / variante
    registro = carpeta / "tandas.txt"
    if not registro.exists():
        return []
    rutas = []
    for linea in registro.read_text().splitlines():
        m = re.match(r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) commit (\w+) ", linea)
        if not m or m.group(2) != COMMIT_SIN_VERSIONAR:
            continue
        inicio = dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
        ruta = carpeta / f"tanda_{inicio:%Y%m%d_%H%M%S}.csv"
        if ruta.exists():
            rutas.append(ruta)
        elif " variante referencia " in linea:
            # La medición de tiempo de las 00:11 usó otro nombre de archivo.
            rutas += sorted(carpeta.glob("semillas_*.csv"))
        # Si no hay archivo, la tanda no tenía tareas pendientes en esta variante.
    return rutas


def originales(politicas: set, despachox: int) -> list:
    """(variante, semilla, política, fila original, archivo) de las tandas sin versionar."""
    out = []
    for v in VARIANTES:
        for ruta in tandas_sin_versionar(v):
            with open(ruta, newline="") as fh:
                for f in csv.DictReader(fh):
                    if completa(f) and f["politica"] in politicas:
                        out.append((v, int(f["semilla"]), f["politica"], f, ruta.name))
    medicion = sorted(RESULTADOS.glob("referencia/semillas_*.csv"))
    if despachox and medicion:
        with open(medicion[0], newline="") as fh:
            filas = [f for f in csv.DictReader(fh) if f["politica"] == "despachox" and completa(f)]
        for f in sorted(filas, key=lambda f: int(f["semilla"]))[:despachox]:
            out.append(("referencia", int(f["semilla"]), "despachox", f, medicion[0].name))
    return out


def iguales(nueva: dict, vieja: dict) -> tuple:
    """Si la fila nueva, redondeada como al escribirla, coincide con la original, y en qué columnas no."""
    distintas = []
    for k, x in nueva.items():
        if k in NO_COMPARAR or k not in vieja:
            continue
        a = float(round(x, 4) if isinstance(x, float) else x)
        b = float(vieja[k])
        if np.isnan(a) or np.isnan(b):
            if not (np.isnan(a) and np.isnan(b)):
                distintas.append(k)
        elif abs(a - b) > 1e-9:
            distintas.append(k)
    return not distintas, distintas


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--politicas", default="optimiza_una_vez,experta,ingenua",
                    help="políticas cuyas filas se repiten todas")
    ap.add_argument("--despachox", type=int, default=7, help="semillas de `despachox` de la medición de tiempo")
    ap.add_argument("--procesos", type=int, default=7)
    a = ap.parse_args(argv)

    lista = originales(set(a.politicas.split(",")), a.despachox)
    por_vel = {}
    for item in lista:
        p = parametros(item[0])
        assert p["factor"] == 3, "las tandas sin versionar son todas de factor 3"
        por_vel.setdefault(p["vel"], []).append(item)
    os.environ["DESPACHOX_FACTOR_CRITICO"] = "3"        # los hijos la heredan al arrancar
    os.environ.setdefault("DESPACHOX_SIN_RED", "1")
    print(f"{len(lista)} tareas para repetir", flush=True)
    if not lista:       # p. ej., si `resultados/` se apartó para repetir todo desde cero
        return 0

    inicio, t0 = dt.datetime.now(), time.perf_counter()
    resultados = []
    for vel, items in sorted(por_vel.items()):
        # `despachox` primero, para que las tareas largas no queden al final.
        items.sort(key=lambda t: t[2] != "despachox")
        with ProcessPoolExecutor(a.procesos, initializer=_preparar, initargs=(vel,)) as ex:
            tareas = [(v, s, pol, extra_de(parametros(v))) for v, s, pol, _, _ in items]
            for item, filas in zip(items, ex.map(_tarea, tareas)):
                nueva = filas[0]
                ok, distintas = iguales(nueva, item[3])
                resultados.append((item, nueva, ok, distintas))
                print(f"{item[0]:15s} {item[1]} {item[2]:16s} {'idéntica' if ok else 'distinta: ' + ','.join(distintas)}",
                      flush=True)
    total = time.perf_counter() - t0

    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / "filas.csv", "w", newline="") as fh:
        campos = ["archivo_original", "identica", "columnas_distintas"] + list(resultados[0][1])
        w = csv.DictWriter(fh, fieldnames=campos)
        w.writeheader()
        for (v, s, pol, vieja, archivo), nueva, ok, distintas in resultados:
            w.writerow({"archivo_original": archivo, "identica": int(ok), "columnas_distintas": ";".join(distintas),
                        **{k: (round(x, 4) if isinstance(x, float) else x) for k, x in nueva.items()}})

    L = ["# Repetición de las tandas sin versionar", "",
         f"Generado el {inicio:%Y-%m-%d a las %H:%M} con `python -m analisis.sensibilidad.repetir`, "
         f"commit `{_commit()}`, {a.procesos} procesos, {total:.0f} s.", "",
         f"Las tandas que registran el commit {COMMIT_SIN_VERSIONAR} corrieron antes de que el envoltorio "
         "entrara al repositorio en 1e74acc. Aquí se repiten con el código versionado y se compara cada "
         "fila con la original, columna por columna. Solo se dejan fuera las que miden tiempo de reloj "
         f"({', '.join(sorted(RELOJ))}).", "",
         "| Variante | Política | Filas repetidas | Idénticas | Semillas |", "|---|---|---:|---:|---|"]
    grupos = {}
    for r in resultados:
        grupos.setdefault((r[0][0], r[0][2]), []).append(r)
    orden = list(VARIANTES)
    for (v, pol), rs in sorted(grupos.items(), key=lambda g: (orden.index(g[0][0]), POLITICAS.index(g[0][1]))):
        semillas = sorted(r[0][1] for r in rs)
        L.append(f"| {v} | `{pol}` | {len(rs)} | {sum(r[2] for r in rs)} | {semillas[0]} a {semillas[-1]} |")
    L.append("")
    distintas = [r for r in resultados if not r[2]]
    if distintas:
        L += ["Filas distintas, original y repetición:", "",
              "| Variante | Semilla | Política | " + " | ".join(f"{m} (original → repetición)" for m in RESUMEN) + " |",
              "|---|---|---|" + "---|" * len(RESUMEN)]
        for (v, s, pol, vieja, _), nueva, _, _ in distintas:
            L.append(f"| {v} | {s} | `{pol}` | " + " | ".join(
                f"{_num(float(vieja[m]))} → {_num(float(nueva[m]))}" for m in RESUMEN) + " |")
        L.append("")
        for pol in ("optimiza_una_vez", "despachox"):
            rs = [r for r in resultados if r[0][2] == pol]
            if rs:
                dif = np.array([float(r[1]["a_tiempo_criticos_pct"]) - float(r[0][3]["a_tiempo_criticos_pct"]) for r in rs])
                L.append(f"`{pol}`: {sum(r[2] for r in rs)} de {len(rs)} filas idénticas; diferencia media en "
                         f"críticos a tiempo, repetición menos original, {_num(float(dif.mean()), 2)} puntos "
                         f"(de {_num(float(dif.min()), 1)} a {_num(float(dif.max()), 1)}).")
        L.append("")
    (RESULTADOS / "repeticion.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
