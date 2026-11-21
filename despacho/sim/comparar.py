"""Tablas de la sección 9 de docs/SIMULACION.md (velocidades de la tesis UNAL de 2019, tabla 14).

    python -m despacho.sim.comparar despacho/sim/resultados_velocidades

Lee las corridas de esa carpeta y la confirmación de la sección 8.3
(`resultados_s2/confirmacion_factor_3`), y escribe `tablas.md` en la misma carpeta.
Todas las corridas usan las semillas 20261150 a 20261179 y FACTOR_CRITICO = 3.

- `confirmacion_factor_3`: velocidades de `datos_publicos/velocidades.csv` (tesis UNAL de 2019,
  tabla 14; que se midieran con GPS está por confirmar), red ampliada (sección 9).
- `modelo_misma_red`: velocidades del modelo, misma red y semillas. Sirve para aislar el
  efecto de las velocidades, porque la sección 8.3 usó la red urbana.
- `sin_cierres`: velocidades de la tesis, 0 cierres por jornada.
- `vida_util`: velocidades de la tesis, vida útil por producto de datos_publicos/vida_util.csv.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

from .correr import _num, ic95
from .metricas import METRICAS

CARGAS = ("holgada", "media", "alta")
POLITICAS = ("ingenua", "experta", "optimiza_una_vez", "despachox")
INDICADORES = {
    "a_tiempo_criticos_pct": "Críticos a tiempo (%)",
    "a_tiempo_todos_pct": "A tiempo, todos los puntos (%)",
    "perecedero_vencido_pct": "Perecederos vencidos (%)",
    "km": "Kilómetros de la flota",
    "peor_punto_h": "Espera en el punto peor atendido (h)",
}
S83 = Path(__file__).parent / "resultados_s2" / "confirmacion_factor_3"


def leer(carpeta: Path) -> dict | None:
    """{(carga, politica): {semilla: fila}} o None si la corrida no existe."""
    ruta = carpeta / "resultados.csv"
    if not ruta.exists():
        return None
    datos = {}
    with open(ruta) as fh:
        for f in csv.DictReader(fh):
            datos.setdefault((f["carga"], f["politica"]), {})[int(f["semilla"])] = f
    return datos


def _dec(m):
    return 2 if m.endswith("_h") else 1


def media(datos, carga, pol, m) -> float:
    return float(np.mean([float(f[m]) for f in datos[(carga, pol)].values()]))


def pareada(da, pa, db, pb, carga, m) -> tuple:
    """Diferencia pareada por semilla (da, pa) − (db, pb): media, IC 95 %, n, ganadas, perdidas."""
    a, b = da[(carga, pa)], db[(carga, pb)]
    semillas = sorted(set(a) & set(b))
    d = [float(a[s][m]) - float(b[s][m]) for s in semillas]
    med, lo, hi, n = ic95(d)
    signo = 1 if METRICAS[m][1] else -1
    gana = sum(signo * x > 1e-9 for x in d)
    pierde = sum(signo * x < -1e-9 for x in d)
    return med, lo, hi, n, gana, pierde


def celda(t, dec=1) -> str:
    med, lo, hi = t[:3]
    return f"{_num(med, dec)} [{_num(lo, dec)}; {_num(hi, dec)}]"


def doble(da, db, carga, m) -> tuple:
    """Cambio de la brecha despachox − experta de la corrida a frente a la b, pareado por semilla."""
    sa = da[(carga, "despachox")]
    sb = db[(carga, "despachox")]
    semillas = sorted(set(sa) & set(sb) & set(da[(carga, "experta")]) & set(db[(carga, "experta")]))
    d = [(float(da[(carga, "despachox")][s][m]) - float(da[(carga, "experta")][s][m]))
         - (float(db[(carga, "despachox")][s][m]) - float(db[(carga, "experta")][s][m])) for s in semillas]
    return ic95(d)


def tabla_indicador(L, m, A, C, S) -> None:
    dec = _dec(m)
    L += [f"### {INDICADORES[m]}", "",
          "| Carga | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` | `despachox` − `experta` "
          "| Semillas mejor / igual / peor frente a `experta` | Misma diferencia, velocidades del modelo, misma red "
          "| Misma diferencia en la sección 8.3 |",
          "|---|---:|---:|---:|---|---|---|---|---|"]
    for c in CARGAS:
        pe = pareada(A, "despachox", A, "experta", c, m)
        fila = [c.capitalize()] + [_num(media(A, c, p, m), dec) for p in ("ingenua", "experta", "despachox")]
        fila += [celda(pareada(A, "despachox", A, "ingenua", c, m), dec), celda(pe, dec),
                 f"{pe[4]} / {pe[3] - pe[4] - pe[5]} / {pe[5]}",
                 celda(pareada(C, "despachox", C, "experta", c, m), dec) if C else "s. d.",
                 celda(pareada(S, "despachox", S, "experta", c, m), dec) if S else "s. d."]
        L.append("| " + " | ".join(fila) + " |")
    L.append("")


def main(carpeta: str) -> None:
    base = Path(carpeta)
    A = leer(base / "confirmacion_factor_3")
    C = leer(base / "modelo_misma_red")
    B = leer(base / "sin_cierres")
    D = leer(base / "vida_util")
    S = leer(S83)
    if A is None:
        raise SystemExit(f"falta {base / 'confirmacion_factor_3' / 'resultados.csv'}")
    n = len(A[("media", "despachox")])
    L = ["# Tablas de la sección 9 (velocidades de la tesis UNAL de 2019, tabla 14)", "",
         f"Generadas con `python -m despacho.sim.comparar {carpeta}`. {n} semillas por carga "
         "(20261150 en adelante), las mismas en todas las corridas y políticas. FACTOR_CRITICO = 3. "
         "Intervalos: t de Student al 95 % sobre la diferencia pareada por semilla.", ""]
    for nombre, d in (("velocidades de la tesis", A), ("velocidades del modelo, misma red", C),
                      ("sin cierres", B), ("vida útil por producto", D), ("sección 8.3", S)):
        if d:
            fallos = sum(int(f["fallos_optimizador"]) for filas in d.values() for f in filas.values())
            jornadas = sum(len(v) for v in d.values())
            L.append(f"- {nombre}: {jornadas} jornadas, {fallos} llamadas al optimizador con error.")
    L.append("")
    uno = A[("media", "ingenua")]
    for c in CARGAS:
        f = list(A[(c, "ingenua")].values())
        L.append(f"- Carga {c}: {np.mean([int(x['puntos']) for x in f]):.0f} puntos, "
                 f"{np.mean([int(x['pedidos']) for x in f]):.0f} pedidos, "
                 f"{_num(np.mean([float(x['vehiculos']) for x in f]))} vehículos, "
                 f"{_num(np.mean([float(x['cierres']) for x in f]))} cierres en promedio.")
    del uno
    L += ["", "## Velocidades de la tesis: medias y diferencias pareadas", ""]
    for m in INDICADORES:
        tabla_indicador(L, m, A, C, S)

    if C:
        L += ["## Efecto de las velocidades de la tesis en la misma red", "",
              "Diferencia pareada por semilla, velocidades de la tesis menos velocidades del modelo. "
              "Mismos puntos, pedidos, lotes y flota; los cierres se sortean con la misma regla sobre "
              "los caminos de cada red de velocidades, así que pueden caer en otros tramos.", "",
              "| Carga | Indicador | `ingenua` | `experta` | `despachox` | Cambio de la brecha `despachox` − `experta` |",
              "|---|---|---|---|---|---|"]
        for c in CARGAS:
            for m in INDICADORES:
                dec = _dec(m)
                L.append(f"| {c.capitalize()} | {INDICADORES[m]} | "
                         + " | ".join(celda(pareada(A, p, C, p, c, m), dec) for p in ("ingenua", "experta", "despachox"))
                         + f" | {celda(doble(A, C, c, m), dec)} |")
        L += ["", "Medias con velocidades del modelo en la misma red:", "",
              "| Carga | Indicador | `ingenua` | `experta` | `despachox` |", "|---|---|---:|---:|---:|"]
        for c in CARGAS:
            for m in INDICADORES:
                dec = _dec(m)
                L.append(f"| {c.capitalize()} | {INDICADORES[m]} | "
                         + " | ".join(_num(media(C, c, p, m), dec) for p in ("ingenua", "experta", "despachox")) + " |")
        L.append("")

    if S:
        L += ["## Medias de la sección 8.3 (red urbana, velocidades del modelo)", "",
              "| Carga | Indicador | `ingenua` | `experta` | `despachox` |", "|---|---|---:|---:|---:|"]
        for c in CARGAS:
            for m in INDICADORES:
                dec = _dec(m)
                L.append(f"| {c.capitalize()} | {INDICADORES[m]} | "
                         + " | ".join(_num(media(S, c, p, m), dec) for p in ("ingenua", "experta", "despachox")) + " |")
        L.append("")

    for titulo, d, ref in (("Sin cierres (0 por jornada), velocidades de la tesis", B, A),
                           ("Vida útil por producto, velocidades de la tesis", D, A)):
        if not d:
            continue
        L += [f"## {titulo}", "",
              "| Carga | Indicador | `ingenua` | `experta` | `despachox` | `despachox` − `ingenua` "
              "| `despachox` − `experta` | Semillas mejor / igual / peor frente a `experta` "
              "| `despachox` − `experta` en la corrida principal (9.2) |",
              "|---|---|---:|---:|---:|---|---|---|---|"]
        cargas = [c for c in CARGAS if (c, "despachox") in d]
        for c in cargas:
            for m in INDICADORES:
                dec = _dec(m)
                pe = pareada(d, "despachox", d, "experta", c, m)
                L.append(f"| {c.capitalize()} | {INDICADORES[m]} | "
                         + " | ".join(_num(media(d, c, p, m), dec) for p in ("ingenua", "experta", "despachox"))
                         + f" | {celda(pareada(d, 'despachox', d, 'ingenua', c, m), dec)} | {celda(pe, dec)} | "
                         f"{pe[4]} / {pe[3] - pe[4] - pe[5]} / {pe[5]} | "
                         f"{celda(pareada(ref, 'despachox', ref, 'experta', c, m), dec)} |")
        L.append("")
        L += ["Cambio frente a la corrida principal (9.2), pareado por semilla:", "",
              "| Carga | Indicador | `ingenua` | `experta` | `despachox` |", "|---|---|---|---|---|"]
        for c in cargas:
            for m in INDICADORES:
                dec = _dec(m)
                L.append(f"| {c.capitalize()} | {INDICADORES[m]} | "
                         + " | ".join(celda(pareada(d, p, ref, p, c, m), dec) for p in ("ingenua", "experta", "despachox"))
                         + " |")
        L.append("")
    (base / "tablas.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "resultados_velocidades"))
