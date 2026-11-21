"""Tabla de la sensibilidad: medias y diferencias pareadas por variante.

    DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.tabla --semillas 60

Lee `resultados/<variante>/*.csv`, usa las semillas base .. base + semillas − 1 en todas las
variantes (las mismas semillas para todo) y escribe `resultados/resumen.md` y `resultados/tabla.csv`.
Los intervalos son los de `despacho.sim.correr.ic95`: t de Student al 95 % sobre la diferencia
pareada por semilla.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

from despacho.sim.correr import _num, ic95
from despacho.sim.metricas import METRICAS

from .correr import BASE, POLITICAS, RESULTADOS, VARIANTES, parametros

LINEAS_BASE = ("ingenua", "experta", "optimiza_una_vez")
INDICADORES = ("a_tiempo_criticos_pct", "perecedero_vencido_pct")
OTRAS = ("a_tiempo_todos_pct", "peor_punto_h", "km")
ETIQUETA = {
    "referencia": "Referencia de la sensibilidad (no es el resultado principal)",
    "velocidad_x0.8": "Velocidad medida × 0,8",
    "velocidad_x1.2": "Velocidad medida × 1,2",
    "demanda_x0.75": "Demanda × 0,75",
    "demanda_x1.5": "Demanda × 1,5",
    "flota_menos_1": "Flota con un campero menos",
    "flota_menos_2": "Flota con dos camperos menos",
    "factor_1": "Factor crítico 1",
    "factor_5": "Factor crítico 5",
}


def leer(variante: str) -> tuple:
    """{política: {semilla: fila}} y el número de filas repetidas que se descartaron."""
    datos, repetidas = {}, 0
    for ruta in sorted((RESULTADOS / variante).glob("*.csv")):
        with open(ruta, newline="") as fh:
            for f in csv.DictReader(fh):
                por = datos.setdefault(f["politica"], {})
                s = int(f["semilla"])
                if s in por:
                    repetidas += 1
                    continue
                por[s] = f
    return datos, repetidas


def x(filas, m) -> np.ndarray:
    return np.array([float(f[m]) for f in filas], float)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--semillas", type=int, default=60)
    ap.add_argument("--base", type=int, default=BASE)
    a = ap.parse_args(argv)
    semillas = list(range(a.base, a.base + a.semillas))

    L = ["# Sensibilidad: resultados por variante", "",
         "Estos números no son el resultado principal de la simulación. Miden si las conclusiones "
         "aguantan cuando cambia un supuesto, frente a una referencia propia de este análisis.", "",
         f"- Semillas: {semillas[0]} a {semillas[-1]} ({len(semillas)}), las mismas para todas las variantes y políticas.",
         "- Carga media, red y optimizador por defecto, 1 s de búsqueda por llamada, velocidad medida de "
         "`datos_publicos/velocidades.csv` salvo donde la variante la escala.",
         "- Intervalos: `ic95` de `despacho/sim/correr.py` sobre la diferencia pareada por semilla.", ""]
    tabla, referencia = [], None
    for v in VARIANTES:
        datos, repetidas = leer(v)
        faltan = {p: [s for s in semillas if s not in datos.get(p, {})] for p in POLITICAS}
        completas = [s for s in semillas if all(s in datos.get(p, {}) for p in ("despachox", "ingenua", "experta"))]
        if not completas:
            L += [f"## {ETIQUETA[v]}", "", "Sin datos todavía.", ""]
            continue
        por = {p: [datos[p][s] for s in completas] for p in POLITICAS if all(s in datos.get(p, {}) for s in completas)}
        d = por["despachox"]
        p = parametros(v)
        fallos = sum(int(float(f["fallos_optimizador"])) for pol in por for f in por[pol])
        llamadas = x(d, "recalculos")
        L += [f"## {ETIQUETA[v]}", "",
              f"Parámetros: velocidad medida × {_num(p['vel'], 2)}, demanda × {_num(p['demanda'], 2)}, "
              f"{p['camperos_menos']} camperos menos, factor crítico {p['factor']}. "
              f"Semillas completas: {len(completas)} de {len(semillas)}."
              + (f" Faltan: {', '.join(f'{pol} {len(s)}' for pol, s in faltan.items() if s)}." if any(faltan.values()) else "")
              + (f" Filas repetidas descartadas: {repetidas}." if repetidas else ""), "",
              f"Escenarios: {x(d, 'puntos').mean():.0f} puntos, {x(d, 'pedidos').mean():.0f} pedidos, "
              f"{_num(x(d, 'kg_pedidos').mean() / 1000)} t, {_num(x(d, 'vehiculos').mean())} vehículos y "
              f"{_num(x(d, 'cierres').mean())} cierres en promedio. `despachox` llamó {_num(llamadas.mean())} veces "
              f"al optimizador por jornada, {_num(x(d, 'recalculo_medio_s').mean(), 2)} s por llamada; la tarea de "
              f"`despachox` tardó {_num(x(d, 'segundos_tarea').mean())} s por semilla. Llamadas con error: {fallos}.", "",
              "| Métrica | " + " | ".join(f"`{pol}`" for pol in por) + " |", "|---|" + "---:|" * len(por)]
        for m in INDICADORES + OTRAS:
            dec = 2 if m.endswith("_h") else 1
            L.append(f"| {METRICAS[m][0]} | " + " | ".join(
                f"{_num(float(np.mean(x(por[pol], m))), dec)} ({_num(float(np.std(x(por[pol], m), ddof=1)), dec)})"
                for pol in por) + " |")
        L += ["", "| Comparación | Indicador | Diferencia media | IC 95 % | Semillas: mejor / igual / peor |",
              "|---|---|---:|---|---|"]
        fila = {"variante": v, "semillas": len(completas), "vehiculos": round(float(x(d, "vehiculos").mean()), 2),
                "pedidos": round(float(x(d, "pedidos").mean()), 1)}
        for pol in ("despachox",) + LINEAS_BASE:
            if pol in por:
                for m in INDICADORES + OTRAS:
                    fila[f"{pol}:{m}"] = round(float(np.mean(x(por[pol], m))), 3)
        for b in LINEAS_BASE:
            if b not in por:
                continue
            for m in INDICADORES + OTRAS:
                dif = x(d, m) - x(por[b], m)
                media, lo, hi, n = ic95(dif)
                signo = 1 if METRICAS[m][1] else -1
                mejor = int(np.sum(signo * dif > 1e-9))
                peor = int(np.sum(signo * dif < -1e-9))
                dec = 2 if m.endswith("_h") else 1
                L.append(f"| `despachox` − `{b}` | {METRICAS[m][0]} | {_num(media, dec)} | "
                         f"[{_num(lo, dec)}; {_num(hi, dec)}] | {mejor} / {n - mejor - peor} / {peor} |")
                fila.update({f"dx-{b}:{m}": round(media, 3), f"dx-{b}:{m}:lo": round(lo, 3),
                             f"dx-{b}:{m}:hi": round(hi, 3), f"dx-{b}:{m}:mejor": mejor, f"dx-{b}:{m}:peor": peor})
        L.append("")
        if v == "referencia":
            referencia = datos
        elif v.startswith("factor") and referencia is not None:
            # ingenua y experta no llaman al optimizador: deben salir iguales que en la referencia
            distintas = sum(1 for pol in ("ingenua", "experta") for s in completas
                            if s in referencia.get(pol, {}) and any(
                                abs(float(datos[pol][s][m]) - float(referencia[pol][s][m])) > 1e-9
                                for m in INDICADORES + OTRAS))
            L += [f"Control: filas de `ingenua` y `experta` distintas de las de la referencia: {distintas}.", ""]
            fila["control_lineas_base_distintas"] = distintas
        tabla.append(fila)
    (RESULTADOS / "resumen.md").write_text("\n".join(L) + "\n")
    if tabla:
        campos = list(dict.fromkeys(k for f in tabla for k in f))
        with open(RESULTADOS / "tabla.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            w.writerows(tabla)
    print("\n".join(L))


if __name__ == "__main__":
    main()
