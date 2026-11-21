"""Figura (c): la regla de arquitectura como diagrama, para leerse en cinco segundos desde el fondo del auditorio.

Uso: python figuras_pitch/scripts/regla_arquitectura.py [--fuente FAMILIA] [--salida CARPETA]
Escribe <salida>/png/c_regla_arquitectura.png y <salida>/svg/c_regla_arquitectura.svg.

No lee datos. El texto sigue la regla de docs/ESTRATEGIA.md («El modelo lee y estructura. El optimizador y las
reglas calculan. El despachador decide.») y docs/FICHA.md, que dice que los SMS los lee un programa de reglas sin
modelo y que ese lector toma el lugar del modelo si este falla.
"""
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import estilo as e

NOMBRE = "c_regla_arquitectura"


def caja(ax, x, y, w, h, color, borde=None, radio=18):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radio}",
                                facecolor=color, edgecolor=borde or color, linewidth=3, zorder=2))


def flecha(ax, x0, y0, x1, y1, color=e.TEXTO, grosor=5):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=42,
                                 color=color, linewidth=grosor, zorder=3, shrinkA=0, shrinkB=0))


def main():
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    print(f"fuente tipográfica: {familia}")

    fig = e.lienzo()
    e.titulo(fig, "La regla que no se negocia", "El modelo nunca decide una ruta ni despacha nada.")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, e.ANCHO_PX)
    ax.set_ylim(0, e.ALTO_PX)
    ax.axis("off")

    yc = 505                        # centro vertical de la fila principal
    margen, sep = 50, 52
    w_can, w_sal = 170, 230
    w = (e.ANCHO_PX - 2 * margen - w_can - w_sal - 4 * sep) / 3   # ancho de cada bloque de la regla
    h = 340

    # Canales de entrada.
    x_can, h_pil = margen, 88
    ax.text(x_can + w_can / 2, yc + 240, "Canales", ha="center", va="center", fontsize=e.pt(32), color=e.CENIZA)
    for i, canal in enumerate(("Chat", "Voz", "SMS")):
        y = yc + 120 - i * 120
        caja(ax, x_can, y - h_pil / 2, w_can, h_pil, e.CREMA, radio=30)
        e.encajar(fig, ax.text(x_can + w_can / 2, y, canal, ha="center", va="center", fontsize=e.pt(40),
                               color=e.TEXTO, zorder=4), w_can - 24)

    # Los tres bloques de la regla.
    x0 = x_can + w_can + sep
    bloques = [
        (e.CENIZA, ["El modelo", "de lenguaje"], "lee y estructura", "o un lector por reglas"),
        (e.AMBAR, ["El optimizador", "y las reglas"], "calculan", None),
        (e.TINTA, ["El despachador"], "decide", None),
    ]
    xs = []
    for i, (color, quien, verbo, nota) in enumerate(bloques):
        x = x0 + i * (w + sep)
        xs.append(x)
        caja(ax, x, yc - h / 2, w, h, color)
        y_quien = yc + 72 if len(quien) == 2 else yc + 48
        e.encajar(fig, ax.text(x + w / 2, y_quien, "\n".join(quien), ha="center", va="center",
                               fontsize=e.pt(38), color="white", zorder=4, linespacing=1.15), w - 36)
        e.encajar(fig, ax.text(x + w / 2, yc - 78, verbo, ha="center", va="center", fontsize=e.pt(50),
                               fontweight="bold", color="white", zorder=4), w - 36)
        if nota:
            ax.text(x + w / 2, yc - h / 2 - 40, nota, ha="center", va="center", fontsize=e.pt(30),
                    color=e.CENIZA, zorder=4)
        if i < len(bloques) - 1:
            flecha(ax, x + w + 6, yc, x + w + sep - 6, yc)
    flecha(ax, x_can + w_can + 6, yc, x0 - 6, yc)

    # Lo que pasa después de la decisión: una columna a la derecha.
    x_sal = xs[-1] + w + sep
    h_sal = 104
    salidas = ("Despacho", "QR en\ncada paquete", "Entrega\nconfirmada")
    ys = [yc + 165, yc, yc - 165]
    flecha(ax, xs[-1] + w + 6, ys[0], x_sal - 6, ys[0])
    for i, (texto, y) in enumerate(zip(salidas, ys)):
        caja(ax, x_sal, y - h_sal / 2, w_sal, h_sal, e.FONDO, borde=e.TINTA, radio=24)
        e.encajar(fig, ax.text(x_sal + w_sal / 2, y, texto, ha="center", va="center", fontsize=e.pt(32),
                               color=e.TEXTO, fontweight="bold" if i == 2 else "normal", zorder=4,
                               linespacing=1.1), w_sal - 24)
        if i < len(salidas) - 1:
            flecha(ax, x_sal + w_sal / 2, y - h_sal / 2 - 3, x_sal + w_sal / 2, ys[i + 1] + h_sal / 2 + 3,
                   color=e.TINTA, grosor=4)

    e.pie(fig, "Regla de arquitectura de docs/ESTRATEGIA.md. Según docs/FICHA.md, los SMS los lee un programa de "
               "reglas, sin modelo ni red.\nEse lector toma el lugar del modelo si este falla. El despachador aprueba "
               "cada plan con su nombre.")
    e.terminar(e.guardar(fig, NOMBRE, args.salida))


if __name__ == "__main__":
    main()
