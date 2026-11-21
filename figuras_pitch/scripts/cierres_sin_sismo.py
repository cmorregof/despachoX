"""Figura (d): las vías de Manizales y sus accesos se cierran también sin sismo. Registros por corredor.

Uso: python figuras_pitch/scripts/cierres_sin_sismo.py [--fuente FAMILIA] [--salida CARPETA]
Lee  datos_publicos/cierres_historicos.csv.
Escribe <salida>/png/d_cierres_sin_sismo.png, <salida>/svg/d_cierres_sin_sismo.svg y el conteo en
<salida>/datos/d_cierres_sin_sismo.csv.

La figura no compara años. Según docs/datos/vias_y_riesgo.md (sección 3), la cobertura del #767 cambia de un año a
otro, así que los conteos son mínimos y no sirven para comparar años. Por eso a la derecha solo dice en cuántos
años la salida a Letras tiene algún registro. El conteo por año queda en el CSV de salida, sin dibujarlo.

Regla del conteo (es nuestra y se puede discutir):
- Cuenta filas. Cada fila es un registro, y un mismo derrumbe puede tener varios. Por ejemplo, A154 es la
  demolición preventiva de rocas que siguió al deslave de A153, en la Panamericana, y las dos cuentan.
- Entra la fila si su causa es remoción en masa: deslizamiento, derrumbe, deslave, desprendimiento o caída de
  lodo o de rocas. No entran las dos filas cuya causa dice «no es derrumbe» (A019 y A078).
- Sale toda fila cuya causa menciona el sismo. Las demás filas de 2026 se quedan, por ejemplo el deslizamiento
  del 21 de octubre en el tramo Puente La Libertad-Tres Puertas (S22), que no lo causó el sismo.
- Queda fuera la fila sin fecha_inicio (A007, vía a Chinchiná, no verificada), aunque su tramo dice «noviembre de
  2017». vias_y_riesgo.md tampoco la cuenta.
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
LETRAS = "salida a Letras"
ANIOS = range(2017, 2027)


def contar() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Filas que entran al conteo, y filas de remoción sin sismo que quedan fuera por no tener fecha."""
    df = pd.read_csv(ENTRADA, dtype=str)
    causa = df["causa"].fillna("")
    filtro = causa.str.contains(REMOCION) & ~causa.str.contains("no es derrumbe") & ~causa.str.contains("sismo")
    sel = df[filtro].copy()
    sel["anio"] = pd.to_numeric(sel["fecha_inicio"].str[:4], errors="coerce")
    fuera = sel[sel["anio"].isna()]
    sel = sel[sel["anio"].between(ANIOS[0], ANIOS[-1])]
    sel["corredor"] = sel["via_nombre"].fillna(OTROS)
    return sel, fuera


def main():
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    sel, fuera = contar()
    tabla = pd.crosstab(sel["corredor"], sel["anio"].astype(int)).reindex(columns=list(ANIOS), fill_value=0)
    tabla["total"] = tabla.sum(axis=1)
    tabla = tabla.sort_values("total", ascending=False)
    datos = Path(args.salida) / "datos"
    datos.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(datos / f"{NOMBRE}.csv")
    total = int(tabla["total"].sum())
    anios_letras = [a for a in ANIOS if tabla.loc[LETRAS, a] > 0]
    print(f"fuente tipográfica: {familia}; registros sin sismo: {total}; salida a Letras: "
          f"{int(tabla.loc[LETRAS, 'total'])}, con registros en {len(anios_letras)} de {len(ANIOS)} años")
    print(f"fuera por no tener fecha: {', '.join(fuera['id'])}")
    print("columna verificado de las filas contadas: " +
          ", ".join(f"{k} {v}" for k, v in sel["verificado"].value_counts().items()))
    print(tabla.to_string())

    fig = e.lienzo()
    e.titulo(fig, "Las vías de Manizales y sus accesos se cierran también sin sismo",
             f"{total} registros de derrumbe o deslizamiento de 2017 a 2026, sin contar los del sismo")
    pie = e.pie(fig, "Conteo nuestro sobre datos_publicos/cierres_historicos.csv, que reúne el registro #767 de "
                     "INVÍAS y notas de prensa (consulta del 20 nov 2026).\n"
                     "El #767 no registra todos los eventos y su cobertura cambia de un año a otro, así que estos "
                     "conteos son mínimos y no sirven para comparar años.\n"
                     "Cada fila es un registro, y un mismo derrumbe puede tener varios, como los 2 de la "
                     "Panamericana. Queda fuera una fila sin fecha.\n"
                     "Las filas las revisó un agente, y todavía no las ha revisado ninguna persona.")
    fig.canvas.draw()
    tope_pie = e.caja_px(fig, pie).y1

    # Izquierda: registros por corredor. «Otras vías de la región» va al final aunque sume más que alguno.
    orden = [c for c in tabla.index if c != OTROS] + ([OTROS] if OTROS in tabla.index else [])
    ax = fig.add_axes([0.265, 0.20, 0.33, 0.53])
    y = list(range(len(orden)))[::-1]
    valores = [int(tabla.loc[c, "total"]) for c in orden]
    colores = [e.TINTA if c == LETRAS else e.CENIZA for c in orden]
    ax.barh(y, valores, color=colores, height=0.68)
    for yi, c, v, col in zip(y, orden, valores, colores):
        ax.text(v + max(valores) * 0.03, yi, str(v), va="center", ha="left", fontsize=e.pt(34),
                fontweight="bold", color=col)
        ax.text(-max(valores) * 0.04, yi, c, va="center", ha="right", fontsize=e.pt(30), color=e.TEXTO)
    ax.set_xlim(0, max(valores) * 1.2)
    ax.set_ylim(-0.6, len(orden) - 0.4)
    ax.axis("off")
    e.despejar(fig, ax, tope_pie)
    fig.text(0.04, 0.775, "Dónde", fontsize=e.pt(38), fontweight="bold", color=e.TEXTO)

    # Derecha: en cuántos años hay algún registro en la salida a Letras. No hay magnitudes por año.
    x0 = 0.665
    fig.text(x0, 0.775, "Cuándo", fontsize=e.pt(38), fontweight="bold", color=e.TEXTO)
    grande = fig.text(x0, 0.57, f"{len(anios_letras)} de {len(ANIOS)} años", fontsize=e.pt(104),
                      fontweight="bold", color=e.TINTA, va="baseline")
    e.encajar(fig, grande, e.ANCHO_PX * (0.97 - x0))
    fig.text(x0, 0.535, f"con registros en la salida a Letras,\nde {ANIOS[0]} a {ANIOS[-1]}", fontsize=e.pt(34),
             color=e.TEXTO, va="top", linespacing=1.2)
    lado, hueco = 40, 12
    y_cuadro = 0.355
    for i, a in enumerate(ANIOS):
        x_px = x0 * e.ANCHO_PX + i * (lado + hueco)
        lleno = a in anios_letras
        fig.patches.append(Rectangle((x_px / e.ANCHO_PX, y_cuadro), lado / e.ANCHO_PX, lado / e.ALTO_PX,
                                     transform=fig.transFigure, facecolor=e.TINTA if lleno else e.FONDO,
                                     edgecolor=e.TINTA, linewidth=2))
        if i in (0, len(ANIOS) - 1):
            fig.text((x_px + lado / 2) / e.ANCHO_PX, y_cuadro - 0.012, str(a), ha="center", va="top",
                     fontsize=e.pt(28), color=e.CENIZA)
    e.terminar(e.guardar(fig, NOMBRE, args.salida))


if __name__ == "__main__":
    main()
