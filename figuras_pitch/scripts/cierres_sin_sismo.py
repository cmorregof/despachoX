"""Figura (d): las vías de Manizales se cierran sin sismo. Registros de derrumbe o deslizamiento por corredor y año.

Uso: python figuras_pitch/scripts/cierres_sin_sismo.py [--fuente FAMILIA] [--salida CARPETA]
Lee  datos_publicos/cierres_historicos.csv.
Escribe <salida>/png/d_cierres_sin_sismo.png, <salida>/svg/d_cierres_sin_sismo.svg y el conteo en
<salida>/datos/d_cierres_sin_sismo.csv.

Regla del conteo (es nuestra y se puede discutir):
- Cuenta filas, no eventos. Un derrumbe puede tener varios registros, y el #767 de INVÍAS no registra todo.
- Entra la fila si su causa es remoción en masa: deslizamiento, derrumbe, deslave, desprendimiento o caída de
  lodo o de rocas. No entran las dos filas cuya causa dice «no es derrumbe» (A019 y A078).
- Sale toda fila cuya causa menciona el sismo. Las demás filas de 2026 se quedan, por ejemplo el deslizamiento
  del 21 de octubre en la autopista del Café (S22), que no lo causó el sismo.
- Las filas sin corredor en `via_nombre` van como «otras vías de la región»: el corredor norte hacia Neira,
  Aranzazu y Salamina, tramos entre Estación Uribe, Tres Puertas y Puente La Libertad, y una variante de Pereira.
"""
import re
from pathlib import Path

import pandas as pd
from matplotlib.patches import Rectangle

import estilo as e

NOMBRE = "d_cierres_sin_sismo"
ENTRADA = e.RAIZ / "datos_publicos" / "cierres_historicos.csv"
REMOCION = re.compile(r"deslizamiento|derrumbe|deslave|desprendimiento|caída de lodo|caída de rocas", re.I)
OTROS = "otras vías de la región"


def contar() -> pd.DataFrame:
    df = pd.read_csv(ENTRADA, dtype=str)
    causa = df["causa"].fillna("")
    filtro = causa.str.contains(REMOCION) & ~causa.str.contains("no es derrumbe") & ~causa.str.contains("sismo")
    sel = df[filtro].copy()
    sel["anio"] = pd.to_numeric(sel["fecha_inicio"].str[:4], errors="coerce")
    sel = sel[sel["anio"].between(2017, 2026)]
    sel["corredor"] = sel["via_nombre"].fillna(OTROS)
    return sel


def main():
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    sel = contar()
    tabla = pd.crosstab(sel["corredor"], sel["anio"].astype(int))
    tabla["total"] = tabla.sum(axis=1)
    tabla = tabla.sort_values("total", ascending=False)
    datos = Path(args.salida) / "datos"
    datos.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(datos / f"{NOMBRE}.csv")
    total = int(tabla["total"].sum())
    letras = int(tabla.loc["salida a Letras", "total"])
    anios = [c for c in tabla.columns if c != "total"]
    print(f"fuente tipográfica: {familia}; registros sin sismo: {total}; salida a Letras: {letras}")
    print(tabla.to_string())

    fig = e.lienzo()
    e.titulo(fig, "Las vías de Manizales se cierran también sin sismo",
             f"{total} registros de derrumbe o deslizamiento de 2017 a 2026, sin contar los del sismo")

    # Izquierda: por corredor. «Otros corredores» va al final aunque sume más que alguno.
    orden = [c for c in tabla.index if c != OTROS] + ([OTROS] if OTROS in tabla.index else [])
    ax = fig.add_axes([0.235, 0.17, 0.30, 0.58])
    y = list(range(len(orden)))[::-1]
    valores = [int(tabla.loc[c, "total"]) for c in orden]
    colores = [e.TINTA if c == "salida a Letras" else e.CENIZA for c in orden]
    ax.barh(y, valores, color=colores, height=0.68)
    for yi, c, v, col in zip(y, orden, valores, colores):
        ax.text(v + max(valores) * 0.03, yi, str(v), va="center", ha="left", fontsize=e.pt(34),
                fontweight="bold", color=col)
        ax.text(-max(valores) * 0.04, yi, c, va="center", ha="right", fontsize=e.pt(30), color=e.TEXTO)
    ax.set_xlim(0, max(valores) * 1.2)
    ax.set_ylim(-0.6, len(orden) - 0.4)
    ax.axis("off")
    fig.text(0.04, 0.80, "Dónde", fontsize=e.pt(38), fontweight="bold", color=e.TEXTO)

    # Derecha: por año, la salida a Letras en tinta y el resto en ceniza.
    ax2 = fig.add_axes([0.60, 0.17, 0.37, 0.53])
    x = list(range(len(anios)))
    serie_letras = [int(tabla.loc["salida a Letras", a]) for a in anios]
    serie_resto = [int(tabla[a].sum()) - l for a, l in zip(anios, serie_letras)]
    ax2.bar(x, serie_letras, color=e.TINTA, width=0.72, label="salida a Letras")
    ax2.bar(x, serie_resto, bottom=serie_letras, color=e.CENIZA, width=0.72, label="otros corredores")
    for xi, l, r in zip(x, serie_letras, serie_resto):
        ax2.text(xi, l + r + 0.8, str(l + r), ha="center", va="bottom", fontsize=e.pt(28), color=e.TEXTO)
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(a) for a in anios], fontsize=e.pt(26))
    hueco = ax2.get_window_extent().width / len(anios) - 8      # ancho de cada año, con aire entre rótulos
    for rotulo in ax2.get_xticklabels():
        e.encajar(fig, rotulo, hueco)
    ax2.set_yticks([])
    for lado in ("top", "right", "left"):
        ax2.spines[lado].set_visible(False)
    ax2.spines["bottom"].set_color(e.CENIZA)
    ax2.tick_params(axis="x", length=0, pad=8)
    ax2.set_ylim(0, max(l + r for l, r in zip(serie_letras, serie_resto)) * 1.18)
    fig.text(0.60, 0.80, "Cuándo", fontsize=e.pt(38), fontweight="bold", color=e.TEXTO)
    for x_ley, texto, color in ((0.715, "salida a Letras", e.TINTA), (0.862, "el resto", e.CENIZA)):
        fig.patches.append(Rectangle((x_ley, 0.803), 0.012, 0.022, transform=fig.transFigure,
                                     facecolor=color, edgecolor="none"))
        fig.text(x_ley + 0.018, 0.80, texto, fontsize=e.pt(28), color=color)

    e.pie(fig, "Conteo nuestro sobre datos_publicos/cierres_historicos.csv, que reúne el registro #767 de INVÍAS y "
               "notas de prensa (consulta del 20 nov 2026).\nSon registros, no eventos, y el #767 no registra "
               "todo. 2026 va hasta el 20 de noviembre. Las filas las revisó un agente, no una persona.")
    e.guardar(fig, NOMBRE, args.salida)


if __name__ == "__main__":
    main()
