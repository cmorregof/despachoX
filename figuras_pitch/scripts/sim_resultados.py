"""Figura (e): plantilla que dibuja los resultados de la simulación desde resultados.csv.

Uso:
    python figuras_pitch/scripts/sim_resultados.py --entrada despacho/sim/resultados/resultados.csv \\
        --salida figuras_pitch --marca "Ejemplo con resultados anteriores, no citar"
    python figuras_pitch/scripts/sim_resultados.py --entrada analisis/sensibilidad/resultados --salida <carpeta>

Entrada. Un CSV con una fila por carga, semilla y política, como el que escribe `python -m despacho.sim.correr`,
o una carpeta: entonces se leen todos los `resultados*.csv` que haya debajo y cada archivo queda como una variante
con el nombre de su carpeta. Columnas que hacen falta: `politica`, `a_tiempo_criticos_pct` y
`perecedero_vencido_pct`. `semilla` y `carga` son opcionales.

Salida. <salida>/png/<nombre>.png (1920 × 1080), <salida>/svg/<nombre>.svg y <salida>/datos/<nombre>_resumen.csv,
con la media, la desviación, el intervalo del 95 % y la diferencia pareada por semilla contra la línea base.

La figura no interpreta nada. Dibuja la media por grupo y política con su intervalo del 95 % (t de Student entre
semillas) y la meta del reto de perecederos (menos del 5 %). El título lo pone quien la use, con --titulo.
"""
from __future__ import annotations

import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

import estilo as e

COLUMNAS = ("politica", "a_tiempo_criticos_pct", "perecedero_vencido_pct")
# Nombre en la figura y estilo de cada política conocida; las demás toman los estilos que sobran.
POLITICAS = {
    "ingenua": ("Orden de llegada", e.CENIZA, e.CENIZA),
    "experta": ("Despachador con oficio", e.AMBAR, e.AMBAR),
    "optimiza_una_vez": ("Optimiza una vez", e.CREMA, e.TINTA),
    "despachox": ("DespachoX", e.TINTA, e.TINTA),
}
ESTILOS_EXTRA = [("#FFFFFF", e.AMBAR), ("#FFFFFF", e.CENIZA), ("#FFFFFF", e.TINTA)]
ORDEN_CARGAS = ["holgada", "media", "alta"]
META_PERECEDEROS = 5.0     # indicador del reto: desperdicio de perecederos por debajo del 5 %


def argumentos():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--entrada", required=True, help="resultados.csv o carpeta con varios resultados*.csv")
    p.add_argument("--nombre", default="e_simulacion", help="nombre de los archivos de salida")
    p.add_argument("--marca", default="", help="advertencia visible, por ejemplo «Ejemplo con resultados "
                                                "anteriores, no citar»")
    p.add_argument("--titulo", default="Resultados de la simulación por política de despacho")
    p.add_argument("--agrupar", default=None, help="columna del eje x (por defecto `carga`, o `variante` si la "
                                                   "entrada es una carpeta con varios archivos)")
    p.add_argument("--grupos", default=None, help="valores del eje x a dibujar, separados por comas")
    p.add_argument("--politicas", default=None, help="políticas a dibujar y su orden, separadas por comas")
    p.add_argument("--base", default="ingenua", help="línea base de las diferencias pareadas del resumen")
    p.add_argument("--filtro", action="append", default=[], metavar="COLUMNA=VALOR",
                   help="deja solo las filas con ese valor; se puede repetir (por ejemplo --filtro carga=alta)")
    return p.parse_args()


def leer(entrada: Path) -> tuple[pd.DataFrame, str]:
    if entrada.is_dir():
        archivos = sorted(entrada.rglob("resultados*.csv"))
        if not archivos:
            sys.exit(f"no hay resultados*.csv debajo de {entrada}")
        partes = []
        for a in archivos:
            df = pd.read_csv(a)
            rel = a.parent.relative_to(entrada)
            df["variante"] = str(rel) if str(rel) != "." else a.stem
            df["archivo"] = str(a)
            partes.append(df)
        datos = pd.concat(partes, ignore_index=True)
        descripcion = f"{entrada} ({len(archivos)} archivos)"
    else:
        datos = pd.read_csv(entrada)
        datos["archivo"] = str(entrada)
        descripcion = str(entrada)
    faltan = [c for c in COLUMNAS if c not in datos.columns]
    if faltan:
        sys.exit(f"faltan columnas en {descripcion}: {', '.join(faltan)}")
    return datos, descripcion


def media_ic(valores: np.ndarray) -> tuple[float, float, float, float]:
    """Media, desviación, y límites del intervalo del 95 % de la media (t de Student)."""
    v = valores[~np.isnan(valores)]
    n = len(v)
    if n == 0:
        return math.nan, math.nan, math.nan, math.nan
    m = float(v.mean())
    if n == 1:
        return m, 0.0, m, m
    sd = float(v.std(ddof=1))
    try:
        from scipy.stats import t
        q = float(t.ppf(0.975, n - 1))
    except Exception:  # noqa: BLE001  (sin scipy se usa la normal)
        q = 1.96
    mitad = q * sd / math.sqrt(n)
    return m, sd, m - mitad, m + mitad


def redondear(x: float, decimales: int) -> str:
    if x == 0:
        return "0"
    q = Decimal(1).scaleb(-decimales)
    texto = str(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))
    return texto.replace(".", ",")


def resumir(datos, grupo, grupos, politicas, base) -> pd.DataFrame:
    filas = []
    for g in grupos:
        sub = datos[datos[grupo] == g] if grupo else datos
        for pol in politicas:
            d = sub[sub["politica"] == pol]
            fila = {"grupo": g, "politica": pol, "n": len(d)}
            for met in COLUMNAS[1:]:
                m, sd, lo, hi = media_ic(d[met].to_numpy(dtype=float))
                fila.update({f"{met}_media": m, f"{met}_sd": sd, f"{met}_ic_bajo": lo, f"{met}_ic_alto": hi})
            # Diferencia pareada por semilla contra la línea base, si hay semillas y base.
            if "semilla" in sub.columns and base in politicas and pol != base:
                llaves = ["semilla"] + [c for c in ("carga", "variante") if c in sub.columns and c != grupo]
                pares = d.merge(sub[sub["politica"] == base], on=llaves, suffixes=("", "_base"))
                for met in COLUMNAS[1:]:
                    dif = (pares[met] - pares[f"{met}_base"]).to_numpy(dtype=float)
                    m, _, lo, hi = media_ic(dif)
                    fila.update({f"{met}_dif_vs_{base}": m, f"{met}_dif_ic_bajo": lo, f"{met}_dif_ic_alto": hi,
                                 f"{met}_semillas_mejor": int((dif > 0).sum()) if met.startswith("a_tiempo")
                                 else int((dif < 0).sum()),
                                 f"{met}_semillas_igual": int((dif == 0).sum())})
            filas.append(fila)
    return pd.DataFrame(filas)


def panel(fig, rect, resumen, met, grupos, politicas, estilos, etiqueta, decimales, tope, meta=None):
    ax = fig.add_axes(rect)
    k = len(politicas)
    ancho = 0.8 / k
    for j, pol in enumerate(politicas):
        relleno, borde = estilos[pol]
        for i, g in enumerate(grupos):
            fila = resumen[(resumen["grupo"] == g) & (resumen["politica"] == pol)]
            if fila.empty or math.isnan(fila[f"{met}_media"].iloc[0]):
                continue
            m = fila[f"{met}_media"].iloc[0]
            lo, hi = fila[f"{met}_ic_bajo"].iloc[0], fila[f"{met}_ic_alto"].iloc[0]
            x = i - 0.4 + ancho * (j + 0.5)
            ax.bar(x, m, width=ancho * 0.9, color=relleno, edgecolor=borde, linewidth=2.5)
            if hi > lo:
                ax.plot([x, x], [max(lo, 0), hi], color=e.TEXTO, linewidth=2.5, solid_capstyle="butt")
            ax.text(x, max(m, hi) + tope * 0.015, redondear(m, decimales), ha="center", va="bottom",
                    fontsize=e.pt(26), color=e.TEXTO)
    if meta is not None:
        ax.axhline(meta, color=e.AMBAR, linewidth=3, linestyle=(0, (6, 4)))
        ax.text(1.0, meta + tope * 0.02, f"meta del reto: menos de {redondear(meta, 0)} %",
                transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=e.pt(26), color=e.AMBAR,
                fontweight="bold")
    ax.set_xlim(-0.5, len(grupos) - 0.5)
    ax.set_ylim(0, tope)
    ax.set_xticks(range(len(grupos)))
    ax.set_xticklabels([f"Carga {g}" if g in ORDEN_CARGAS else str(g) for g in grupos], fontsize=e.pt(28))
    ax.tick_params(axis="x", length=0, pad=10)
    ax.tick_params(axis="y", labelsize=e.pt(24), colors=e.CENIZA, length=0)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f} %")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color="#E6E3EA", linewidth=1.2)
    ax.set_axisbelow(True)
    fig.text(rect[0], rect[1] + rect[3] + 0.04, etiqueta, fontsize=e.pt(32), fontweight="bold", color=e.TEXTO)
    return ax


def main():
    args = argumentos()
    familia = e.configurar_fuente(args.fuente)
    entrada = Path(args.entrada)
    datos, descripcion = leer(entrada)
    for f in args.filtro:
        col, _, val = f.partition("=")
        if col not in datos.columns:
            sys.exit(f"--filtro: la columna «{col}» no está en {descripcion}")
        datos = datos[datos[col].astype(str) == val]
        descripcion += f", {col} = {val}"
    if datos.empty:
        sys.exit("no quedan filas después de los filtros")
    varias = "variante" in datos.columns and datos["variante"].nunique() > 1
    grupo = args.agrupar or ("variante" if varias else "carga" if "carga" in datos.columns else None)
    if grupo == "variante" and "carga" in datos.columns and datos["carga"].nunique() > 1:
        print(f"aviso: cada variante mezcla {datos['carga'].nunique()} cargas; use --filtro carga=<valor> "
              "para dibujar una sola", file=sys.stderr)
    if grupo and grupo not in datos.columns:
        sys.exit(f"la columna «{grupo}» no está en {descripcion}")
    if grupo:
        presentes = list(dict.fromkeys(datos[grupo].astype(str)))
        datos[grupo] = datos[grupo].astype(str)
        grupos = [g for g in ORDEN_CARGAS if g in presentes] + [g for g in presentes if g not in ORDEN_CARGAS]
    else:
        grupos = ["todas"]
    if args.grupos:
        grupos = [g.strip() for g in args.grupos.split(",") if g.strip() in grupos]
    if grupo:
        datos = datos[datos[grupo].isin(grupos)]
    presentes = list(dict.fromkeys(datos["politica"]))
    politicas = [p for p in POLITICAS if p in presentes] + [p for p in presentes if p not in POLITICAS]
    if args.politicas:
        politicas = [p.strip() for p in args.politicas.split(",") if p.strip() in presentes]
    estilos, extra = {}, iter(ESTILOS_EXTRA * 3)
    for p in politicas:
        estilos[p] = POLITICAS[p][1:] if p in POLITICAS else next(extra)

    resumen = resumir(datos, grupo, grupos, politicas, args.base)
    carpeta_datos = Path(args.salida) / "datos"
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(carpeta_datos / f"{args.nombre}_resumen.csv", index=False, float_format="%.4f")
    print(f"fuente tipográfica: {familia}; entrada: {descripcion}; grupos: {grupos}; políticas: {politicas}")

    fig = e.lienzo()
    e.titulo(fig, args.titulo)
    if args.marca:
        e.sello(fig, args.marca, y=0.865)
        fig.text(0.5, 0.5, "NO CITAR", fontsize=e.pt(230), color=e.AMBAR, alpha=0.10, rotation=18,
                 ha="center", va="center", fontweight="bold", zorder=0)
    tope_crit = 109
    panel(fig, [0.06, 0.25, 0.50, 0.50], resumen, "a_tiempo_criticos_pct", grupos, politicas, estilos,
          "Pedidos críticos entregados a tiempo (%)", 0, tope_crit)
    maximo = max(resumen["perecedero_vencido_pct_ic_alto"].max(), META_PERECEDEROS)
    tope_per = math.ceil(maximo * 1.25)
    panel(fig, [0.64, 0.25, 0.33, 0.50], resumen, "perecedero_vencido_pct", grupos, politicas, estilos,
          "Kilos perecederos vencidos (%)", 1, tope_per, meta=META_PERECEDEROS)

    # Leyenda de políticas, en una fila.
    x = 0.06
    for p in politicas:
        nombre = POLITICAS[p][0] if p in POLITICAS else p
        relleno, borde = estilos[p]
        fig.patches.append(Rectangle((x, 0.148), 0.016, 0.028, transform=fig.transFigure, facecolor=relleno,
                                     edgecolor=borde, linewidth=2.5))
        t = fig.text(x + 0.022, 0.150, nombre, fontsize=e.pt(28), color=e.TEXTO)
        fig.canvas.draw()
        x = t.get_window_extent().x1 / e.ANCHO_PX + 0.03

    # Pie: datos, escenarios, línea base y supuestos.
    cuentas = sorted({int(c) for c in resumen["n"] if c > 0})
    escenarios = (f"{cuentas[0]} escenarios por grupo y política" if len(cuentas) == 1 else
                  f"De {cuentas[0]} a {cuentas[-1]} escenarios por grupo y política")
    semillas = ""
    if "semilla" in datos.columns:
        s = datos["semilla"]
        claves = [grupo] if grupo else []
        iguales = all(len({frozenset(d["semilla"]) for _, d in sub.groupby("politica")}) == 1
                      for _, sub in (datos.groupby(claves) if claves else [(None, datos)]))
        semillas = f", semillas {s.min()} a {s.max()}" + (", las mismas para todas" if iguales else "")
    if args.base in politicas:
        base = "Línea base: " + (POLITICAS[args.base][0].lower() if args.base in POLITICAS else args.base) + ". "
    else:
        base = f"Estos datos no traen la línea base «{args.base}». "
    e.pie(fig, f"Datos: {descripcion}, {len(datos)} filas. {escenarios}{semillas}.\n"
               f"Barra: media. Línea: intervalo del 95 % de la media entre escenarios. {base}"
               f"Supuestos: docs/SIMULACION.md.", y=0.025)
    e.guardar(fig, args.nombre, args.salida, ignorar=(args.marca, "NO CITAR"))


if __name__ == "__main__":
    main()
