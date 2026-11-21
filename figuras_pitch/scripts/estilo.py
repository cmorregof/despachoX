"""Estilo común de las figuras del pitch: paleta del informe, fuente, tamaño de proyección y revisión de textos.

Cada figura se guarda en 1920 × 1080 px (PNG) y en SVG con los textos convertidos en trazos, así que el SVG se ve
igual en cualquier computador aunque no tenga la fuente.

Fuente. La del informe es Ancízar Serif, que no está en el repositorio. Por defecto se usa PT Serif (licencia OFL),
que viene con macOS, y si no está, DejaVu Serif, que trae matplotlib. Con --fuente se elige otra familia instalada
(por ejemplo --fuente "Ancizar Serif") o un archivo .ttf, .otf o .ttc que esté en el disco. Ningún archivo de
fuente se copia al repositorio.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]          # raíz del repositorio
CARPETA = RAIZ / "figuras_pitch"

# Paleta del informe (docs/informe/figuras/scripts/).
TINTA, AMBAR, CREMA, CENIZA = "#4F4086", "#A36752", "#EBD3A2", "#6E6878"
TEXTO = "#2E2550"          # tinta oscura para el texto corrido, la misma de barras_abaco.py
FONDO = "#FFFFFF"
GRIS_RED = "#D9D6DD"       # red vial de fondo, como GRIS_RED de mapa_manizales.py pero más claro

ANCHO_PX, ALTO_PX, DPI = 1920, 1080, 100
MIN_PX = 24                 # ningún texto por debajo de esto al proyectar
FUENTES_POR_DEFECTO = ("PT Serif", "DejaVu Serif")
RUTA_PT_SERIF = "/System/Library/Fonts/Supplemental/PTSerif.ttc"


def pt(px: float) -> float:
    """Tamaño en puntos de matplotlib para que el texto mida `px` píxeles en el PNG de 1920 × 1080."""
    return px * 72.0 / DPI


# Tamaños en píxeles del PNG final.
PX_TITULO = 60
PX_SUBTITULO = 36
PX_TEXTO = 32
PX_ROTULO = 30
PX_PIE = 26


def _familias_instaladas() -> set[str]:
    return {f.name for f in font_manager.fontManager.ttflist}


def configurar_fuente(pedida: str | None = None) -> str:
    """Fija la familia de todas las figuras y devuelve el nombre que quedó en uso."""
    if os.path.exists(RUTA_PT_SERIF) and "PT Serif" not in _familias_instaladas():
        try:
            font_manager.fontManager.addfont(RUTA_PT_SERIF)
        except Exception:  # noqa: BLE001  (si no carga, se sigue con DejaVu Serif)
            pass
    familia = None
    if pedida:
        if os.path.isfile(pedida):
            font_manager.fontManager.addfont(pedida)
            familia = font_manager.FontProperties(fname=pedida).get_name()
        elif pedida in _familias_instaladas():
            familia = pedida
        else:
            print(f"aviso: la fuente «{pedida}» no está instalada; uso la de siempre", file=sys.stderr)
    if familia is None:
        familia = next((f for f in FUENTES_POR_DEFECTO if f in _familias_instaladas()), "DejaVu Serif")
    plt.rcParams.update({
        "font.family": familia,
        "font.size": pt(PX_TEXTO),
        "svg.fonttype": "path",
        "svg.hashsalt": "despachox-figuras-pitch",
        "axes.edgecolor": CENIZA,
        "axes.labelcolor": TEXTO,
        "xtick.color": TEXTO,
        "ytick.color": TEXTO,
        "text.color": TEXTO,
        "figure.facecolor": FONDO,
        "axes.facecolor": FONDO,
        "savefig.facecolor": FONDO,
    })
    return familia


def argumentos(descripcion: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=descripcion)
    p.add_argument("--fuente", default=None,
                   help="familia instalada o archivo de fuente (por defecto PT Serif, si no DejaVu Serif)")
    p.add_argument("--salida", default=str(CARPETA),
                   help="carpeta base; las figuras quedan en <salida>/png y <salida>/svg (por defecto figuras_pitch/)")
    return p


def lienzo():
    """Figura vacía de 1920 × 1080 px."""
    return plt.figure(figsize=(ANCHO_PX / DPI, ALTO_PX / DPI), dpi=DPI)


def titulo(fig, texto: str, subtitulo: str | None = None, x: float = 0.04, y: float = 0.93):
    fig.text(x, y, texto, fontsize=pt(PX_TITULO), fontweight="bold", color=TEXTO, va="baseline", ha="left")
    if subtitulo:
        fig.text(x, y - 0.065, subtitulo, fontsize=pt(PX_SUBTITULO), color=CENIZA, va="baseline", ha="left")


def pie(fig, texto: str, x: float = 0.04, y: float = 0.03):
    """Fuente de la figura, abajo a la izquierda. Admite varias líneas con \\n."""
    fig.text(x, y, texto, fontsize=pt(PX_PIE), color=CENIZA, va="bottom", ha="left", linespacing=1.25)


def sello(fig, texto: str, x: float = 0.96, y: float = 0.93, color: str = AMBAR):
    """Recuadro de advertencia, arriba a la derecha (por ejemplo «Cifras por verificar»)."""
    fig.text(x, y, texto, fontsize=pt(PX_ROTULO), color=color, fontweight="bold", ha="right", va="baseline",
             bbox=dict(boxstyle="round,pad=0.45", facecolor=FONDO, edgecolor=color, linewidth=3))


def miles(n: float, decimales: int = 0) -> str:
    """Número con punto de miles y coma decimal, como en los documentos del equipo."""
    texto = f"{n:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def revisar_textos(fig, nombre: str, ignorar: tuple[str, ...] = ()) -> list[str]:
    """Busca textos por debajo de MIN_PX, cortados por el borde o encimados. Devuelve los avisos."""
    fig.canvas.draw()
    render = fig.canvas.get_renderer()
    textos = []
    for t in fig.findobj(matplotlib.text.Text):
        if not t.get_visible() or not t.get_text().strip() or t.get_text() in ignorar:
            continue
        caja = t.get_window_extent(render)
        if caja.width == 0 or caja.height == 0:
            continue
        textos.append((t, caja))
    avisos = []
    for t, caja in textos:
        px = t.get_fontsize() * DPI / 72.0
        etiqueta = t.get_text().replace("\n", " ")[:40]
        if px < MIN_PX - 0.01:
            avisos.append(f"{nombre}: «{etiqueta}» mide {px:.0f} px")
        if caja.x0 < -1 or caja.y0 < -1 or caja.x1 > ANCHO_PX + 1 or caja.y1 > ALTO_PX + 1:
            avisos.append(f"{nombre}: «{etiqueta}» se sale del lienzo")
    for (t1, c1), (t2, c2) in itertools.combinations(textos, 2):
        if c1.overlaps(c2):
            a = t1.get_text().replace("\n", " ")[:30]
            b = t2.get_text().replace("\n", " ")[:30]
            avisos.append(f"{nombre}: «{a}» se encima con «{b}»")
    return avisos


def guardar(fig, nombre: str, salida: str | Path, ignorar: tuple[str, ...] = ()) -> list[Path]:
    """Guarda <salida>/png/<nombre>.png (1920 × 1080) y <salida>/svg/<nombre>.svg, y revisa los textos."""
    salida = Path(salida)
    (salida / "png").mkdir(parents=True, exist_ok=True)
    (salida / "svg").mkdir(parents=True, exist_ok=True)
    for aviso in revisar_textos(fig, nombre, ignorar):
        warnings.warn(aviso, stacklevel=2)
        print("AVISO", aviso, file=sys.stderr)
    rutas = [salida / "png" / f"{nombre}.png", salida / "svg" / f"{nombre}.svg"]
    fig.savefig(rutas[0], dpi=DPI, metadata={"Software": None})
    fig.savefig(rutas[1], metadata={"Date": None, "Creator": None})
    plt.close(fig)
    for r in rutas:
        print(f"escrito {r}")
    return rutas
