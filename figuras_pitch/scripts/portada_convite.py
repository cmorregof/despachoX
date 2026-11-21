"""Portada de la presentación: el hero de Convite abajo, a todo el ancho, y el logo y la frase arriba a la izquierda.

El hero (recursos/marca/hero_convite.png, 2048 × 768) se generó con IA. Su lado izquierdo está vacío, y ahí van el
logo y la frase. El fondo de la figura toma el color de la esquina del hero, para que no se vea la costura.

Regenerar: python figuras_pitch/scripts/portada_convite.py
"""
from __future__ import annotations

import matplotlib.image as mpimg

import estilo as e

MARCA = e.RAIZ / "recursos" / "marca"
FRASE = "Que la comida llegue\naunque la vía se cierre"


def main() -> None:
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    print(f"fuente tipográfica: {familia}")
    hero = mpimg.imread(MARCA / "hero_convite.png")[..., :3]
    logo = mpimg.imread(MARCA / "convite_logo_transparente.png")
    fondo = tuple(float(c) for c in hero[5:40, 5:40].reshape(-1, 3).mean(axis=0))

    fig = e.lienzo()
    fig.set_facecolor(fondo)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, e.ANCHO_PX)
    ax.set_ylim(e.ALTO_PX, 0)
    ax.axis("off")
    ax.set_facecolor(fondo)

    alto_hero = e.ANCHO_PX * hero.shape[0] / hero.shape[1]          # 720 px
    ax.imshow(hero, extent=(0, e.ANCHO_PX, e.ALTO_PX, e.ALTO_PX - alto_hero), interpolation="lanczos", zorder=1)
    # Borde superior del hero difuminado hacia el fondo, para que no se vea el corte.
    import numpy as np
    alfa = np.linspace(1.0, 0.0, 80)[:, None, None]
    velo = np.concatenate([np.broadcast_to(np.array(fondo), (80, 2, 3)), np.broadcast_to(alfa, (80, 2, 1))], axis=2)
    y_hero = e.ALTO_PX - alto_hero
    ax.imshow(velo, extent=(0, e.ANCHO_PX, y_hero + 80, y_hero - 1), aspect="auto", interpolation="bilinear", zorder=1.5)
    ax.set_xlim(0, e.ANCHO_PX)
    ax.set_ylim(e.ALTO_PX, 0)
    ancho_logo = 760
    alto_logo = ancho_logo * logo.shape[0] / logo.shape[1]
    ax.imshow(logo, extent=(70, 70 + ancho_logo, 60 + alto_logo, 60), interpolation="lanczos", zorder=2)

    serif = e.SERIF_TITULOS if e._instalada(e.SERIF_TITULOS) else familia
    ax.text(118, 360, FRASE, fontsize=e.pt(54), fontfamily=serif, fontweight="bold", color=e.TINTA,
            va="top", ha="left", linespacing=1.15, zorder=3)
    ax.text(122, 560, "Mesa de despacho de ayuda alimentaria\nEquipo 19 · Hackathon UNAL Manizales 2026",
            fontsize=e.pt(30), color=e.CENIZA, va="top", ha="left", linespacing=1.3, zorder=3)
    ax.text(122, 1045, "Ilustración generada con IA", fontsize=e.pt(24), color=e.CENIZA, va="baseline", ha="left",
            zorder=3)
    e.plt.rcParams["savefig.facecolor"] = fondo
    avisos = e.guardar(fig, "portada_convite", args.salida)
    e.terminar(avisos)


if __name__ == "__main__":
    main()
