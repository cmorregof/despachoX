"""Estilo común de las figuras del pitch: paleta del informe, fuente, tamaño de proyección y revisión de textos.

Cada figura se guarda en 1920 × 1080 px (PNG) y en SVG con los textos convertidos en trazos, así que el SVG se ve
igual en cualquier computador aunque no tenga la fuente.

Fuente. La del informe es Ancízar Serif, que no está en el repositorio. Si está instalada en el computador, las
figuras la usan. Si no, usan PT Serif (licencia OFL), que viene con macOS, y si tampoco está, DejaVu Serif, que trae
matplotlib. Con --fuente se elige otra familia instalada, un archivo .ttf, .otf o .ttc del disco o una carpeta con
los archivos de una familia. Con un archivo se registran también los demás pesos de su familia que estén en la misma
carpeta, para que la negrita no salga en peso normal. La familia se busca también en las carpetas de fuentes del
sistema, porque la caché de matplotlib puede ser anterior a la instalación. Ningún archivo de fuente se copia al
repositorio.

Revisión. `guardar` busca textos por debajo de 24 px, cortados por el borde o encimados entre sí o con los
obstáculos que le pase cada figura (barras y líneas), imprime una línea AVISO por cada uno y los devuelve. `terminar`
sale con código 1 si hubo alguno, para que nadie proyecte una figura dañada sin enterarse.
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
import textwrap
import unicodedata
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
FUENTES_POR_DEFECTO = ("Ancizar Serif", "PT Serif", "DejaVu Serif")
RUTA_PT_SERIF = "/System/Library/Fonts/Supplemental/PTSerif.ttc"
CARPETAS_FUENTES = [*font_manager.OSXFontDirectories, *font_manager.X11FontDirectories,
                    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")]


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


def _clave(texto: str) -> str:
    """Minúsculas, sin tildes ni espacios: «Ancízar Serif» y «AncizarSerif-Bold» comparten «ancizarserif»."""
    plano = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in plano if c.isalnum() and not unicodedata.combining(c))


def _instalada(familia: str) -> str | None:
    """Nombre exacto de la familia instalada que coincide con `familia`, sin mirar tildes ni mayúsculas."""
    clave = _clave(familia)
    return next((f for f in sorted(_familias_instaladas()) if _clave(f) == clave), None)


def _nombre_de_familia(archivo: str) -> str | None:
    try:
        return font_manager.FontProperties(fname=archivo).get_name()
    except Exception:  # noqa: BLE001  (archivo que FreeType no abre)
        return None


def _archivos_de_familia(familia: str, carpetas: list[str], a_fondo: bool = False) -> list[str]:
    """Archivos de `familia` en `carpetas`: todos sus pesos y estilos.

    Primero mira los archivos cuyo nombre contiene el de la familia. Con `a_fondo`, si no halla ninguno, abre cada
    archivo y lee su nombre de familia, que es más lento.
    """
    archivos = font_manager.findSystemFonts(fontpaths=carpetas)
    clave = _clave(familia)
    candidatos = [a for a in archivos if clave in _clave(Path(a).stem)]
    if not candidatos and a_fondo:
        candidatos = [a for a in archivos if _clave(_nombre_de_familia(a) or "") == clave]
    return candidatos


def _agregar(archivos: list[str]) -> None:
    for a in archivos:
        try:
            font_manager.fontManager.addfont(a)
        except Exception:  # noqa: BLE001
            continue


def _registrar_familia(familia: str, a_fondo: bool = False) -> str | None:
    """Registra en matplotlib los archivos de `familia` que haya en las carpetas de fuentes del sistema.

    Devuelve el nombre de la familia ya disponible, o None.
    """
    if _instalada(familia):
        return _instalada(familia)
    _agregar(_archivos_de_familia(familia, [c for c in CARPETAS_FUENTES if os.path.isdir(c)], a_fondo))
    return _instalada(familia)


def _registrar_archivo_o_carpeta(pedida: str) -> str | None:
    """Registra un archivo de fuente con los demás pesos de su familia que estén en su carpeta, o una carpeta.

    Con un solo archivo, matplotlib no tendría la negrita y pondría los títulos en peso normal. Por eso se
    registran también los archivos hermanos de la misma familia. Con una carpeta se registran todos sus archivos, y
    la familia es la que más archivos tiene.
    """
    if os.path.isdir(pedida):
        archivos = font_manager.findSystemFonts(fontpaths=[pedida])
        _agregar(archivos)
        nombres = [n for n in map(_nombre_de_familia, archivos) if n]
        return max(sorted(set(nombres)), key=nombres.count) if nombres else None   # empate: orden alfabético
    familia = _nombre_de_familia(pedida)
    if familia is None:
        return None
    carpeta = os.path.dirname(os.path.abspath(pedida))
    _agregar([pedida] + _archivos_de_familia(familia, [carpeta], a_fondo=True))
    return familia


def configurar_fuente(pedida: str | None = None) -> str:
    """Fija la familia de todas las figuras y devuelve el nombre que quedó en uso."""
    if os.path.exists(RUTA_PT_SERIF) and "PT Serif" not in _familias_instaladas():
        try:
            font_manager.fontManager.addfont(RUTA_PT_SERIF)
        except Exception:  # noqa: BLE001  (si no carga, se sigue con DejaVu Serif)
            pass
    familia = None
    if pedida:
        if os.path.exists(pedida):
            familia = _registrar_archivo_o_carpeta(pedida)
        else:
            familia = _registrar_familia(pedida, a_fondo=True)
    if familia is None:
        familia = next((f for f in map(_registrar_familia, FUENTES_POR_DEFECTO) if f), "DejaVu Serif")
        if pedida:
            print(f"aviso: la fuente «{pedida}» no está instalada; uso {familia}", file=sys.stderr)
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
                   help="familia instalada, archivo de fuente o carpeta con los archivos de una familia (por defecto "
                        "Ancizar Serif si está instalada, si no PT Serif, y si no DejaVu Serif)")
    p.add_argument("--salida", default=str(CARPETA),
                   help="carpeta base; las figuras quedan en <salida>/png y <salida>/svg (por defecto figuras_pitch/)")
    return p


def lienzo():
    """Figura vacía de 1920 × 1080 px."""
    return plt.figure(figsize=(ANCHO_PX / DPI, ALTO_PX / DPI), dpi=DPI)


def ancho_px(fig, t) -> float:
    """Ancho en píxeles de un texto ya puesto en la figura."""
    return t.get_window_extent(fig.canvas.get_renderer()).width


def encajar(fig, t, maximo_px: float):
    """Achica el texto hasta que quepa en `maximo_px`, sin bajar de MIN_PX. Sirve si --fuente es más ancha."""
    while ancho_px(fig, t) > maximo_px and t.get_fontsize() * DPI / 72.0 > MIN_PX + 0.5:
        t.set_fontsize(max(t.get_fontsize() * 0.97, pt(MIN_PX)))
    return t


def titulo(fig, texto: str, subtitulo: str | None = None, x: float = 0.04, y: float = 0.93):
    """Título y subtítulo arriba a la izquierda. Si una familia ancha no cabe, se achican sin bajar de 24 px."""
    disponible = ANCHO_PX * (1 - 2 * x)
    t1 = encajar(fig, fig.text(x, y, texto, fontsize=pt(PX_TITULO), fontweight="bold", color=TEXTO,
                               va="baseline", ha="left"), disponible)
    t2 = None
    if subtitulo:
        t2 = encajar(fig, fig.text(x, y - 0.065, subtitulo, fontsize=pt(PX_SUBTITULO), color=CENIZA,
                                   va="baseline", ha="left"), disponible)
    return t1, t2


def pie(fig, texto: str, x: float = 0.04, y: float = 0.03, ancho: int = 150, derecha_px: float = 40):
    """Fuente de la figura, abajo a la izquierda. Respeta los \\n y parte las líneas para que no pasen el borde."""
    disponible = ANCHO_PX * (1 - x) - derecha_px
    t = fig.text(x, y, "", fontsize=pt(PX_PIE), color=CENIZA, va="bottom", ha="left", linespacing=1.25)
    while True:
        lineas = [r for parte in texto.split("\n") for r in (textwrap.wrap(parte, ancho) or [""])]
        t.set_text("\n".join(lineas))
        if ancho_px(fig, t) <= disponible or ancho < 30:
            return t
        ancho = int(ancho * 0.95)


def caja_px(fig, artista):
    """Caja en píxeles del PNG (origen abajo a la izquierda) de un texto, unos ejes u otro artista."""
    render = fig.canvas.get_renderer()
    if hasattr(artista, "get_tightbbox") and not isinstance(artista, matplotlib.text.Text):
        return artista.get_tightbbox(render)
    return artista.get_window_extent(render)


def despejar(fig, ax, piso_px: float, aire_px: float = 18):
    """Sube el borde inferior de `ax`, con sus rótulos, hasta `piso_px` + `aire_px`. El borde superior no se mueve.

    Así un pie de varias líneas, que crece con una familia más ancha, nunca tapa los rótulos del eje.
    """
    fig.canvas.draw()
    falta = piso_px + aire_px - caja_px(fig, ax).y0
    if falta > 0:
        x0, y0, w, h = ax.get_position().bounds
        d = falta / ALTO_PX
        ax.set_position([x0, y0 + d, w, h - d])
    return ax


def sello(fig, texto: str, x: float = 0.96, y: float = 0.93, color: str = AMBAR):
    """Recuadro de advertencia, arriba a la derecha (por ejemplo «Cifras por verificar»)."""
    return fig.text(x, y, texto, fontsize=pt(PX_ROTULO), color=color, fontweight="bold", ha="right",
                    va="baseline", bbox=dict(boxstyle="round,pad=0.45", facecolor=FONDO, edgecolor=color,
                                             linewidth=3))


def miles(n: float, decimales: int = 0) -> str:
    """Número con punto de miles y coma decimal, como en los documentos del equipo."""
    texto = f"{n:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def revisar_textos(fig, nombre: str, ignorar: tuple[str, ...] = (), obstaculos=()) -> list[str]:
    """Busca textos por debajo de MIN_PX, cortados por el borde, encimados o encima de un obstáculo.

    `obstaculos` es una lista de pares (artista, qué es), por ejemplo (barra, "una barra"). La caja de una línea
    se ensancha con la mitad de su grosor. Devuelve los avisos.
    """
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
    for artista, que in obstaculos:
        caja = artista.get_window_extent(render)
        if isinstance(artista, matplotlib.lines.Line2D):
            caja = caja.padded(artista.get_linewidth() * DPI / 72.0 / 2)
        for t, c in textos:
            if c.overlaps(caja):
                avisos.append(f"{nombre}: «{t.get_text().replace(chr(10), ' ')[:30]}» tapa {que}")
    return avisos


def guardar(fig, nombre: str, salida: str | Path, ignorar: tuple[str, ...] = (), obstaculos=(),
            avisos_extra=()) -> list[str]:
    """Guarda <salida>/png/<nombre>.png (1920 × 1080) y <salida>/svg/<nombre>.svg. Devuelve los avisos.

    Los archivos se escriben aunque haya avisos, para poder mirarlos, pero cada aviso sale en una línea AVISO.
    `avisos_extra` son avisos de la figura que no son de texto, como una cifra por confirmar.
    """
    salida = Path(salida)
    (salida / "png").mkdir(parents=True, exist_ok=True)
    (salida / "svg").mkdir(parents=True, exist_ok=True)
    avisos = revisar_textos(fig, nombre, ignorar, obstaculos) + list(avisos_extra)
    for aviso in avisos:
        print("AVISO", aviso, file=sys.stderr)
    rutas = [salida / "png" / f"{nombre}.png", salida / "svg" / f"{nombre}.svg"]
    fig.savefig(rutas[0], dpi=DPI, metadata={"Software": None})
    fig.savefig(rutas[1], metadata={"Date": None, "Creator": None})
    plt.close(fig)
    for r in rutas:
        print(f"escrito {r}")
    return avisos


def terminar(avisos: list[str]) -> None:
    """Sale con código 1 si hubo avisos. Las figuras quedan escritas, pero no están listas para proyectar."""
    if avisos:
        print(f"{len(avisos)} AVISO: textos pequeños, cortados o encimados, o una cifra por confirmar. Revise la "
              "figura antes de proyectarla.", file=sys.stderr)
        sys.exit(1)
