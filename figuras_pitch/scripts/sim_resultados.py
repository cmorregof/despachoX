"""Figura (e): plantilla que dibuja los resultados de la simulación desde resultados.csv.

Uso:
    python figuras_pitch/scripts/sim_resultados.py --entrada despacho/sim/<carpeta>/resultados.csv \\
        --salida figuras_pitch --titulo "<lo que muestran los resultados>"
    python figuras_pitch/scripts/sim_resultados.py --entrada analisis/sensibilidad/resultados --salida <carpeta>
    python figuras_pitch/scripts/sim_resultados.py --entrada <csv> --panel criticos --filtro carga=alta \\
        --etiqueta "Simulación: {jornadas} jornadas sintéticas sobre la red vial de Manizales"

Entrada. Un CSV con una fila por carga, semilla y política, como el que escribe `python -m despacho.sim.correr`,
o una carpeta. Con una carpeta se leen todos los CSV que haya debajo (--patron, por defecto `*.csv`) y se saltan,
con un aviso, los que no traen las columnas mínimas, como una tabla de resumen. Así entran los `resultados.csv` de
despacho/sim y los `tanda_*.csv` de analisis/sensibilidad/resultados. La variante de cada fila es su columna
`variante`, si el CSV la trae, y si no, el nombre de la carpeta del archivo. Las filas repetidas por variante,
carga, semilla y política se descartan, y queda la primera en el orden de los archivos, como en
analisis/sensibilidad/tabla.py. Columnas que hacen falta: `politica`, `a_tiempo_criticos_pct` y
`perecedero_vencido_pct`. `semilla` y `carga` son opcionales.

Salida. <salida>/png/<nombre>.png (1920 × 1080), <salida>/svg/<nombre>.svg y <salida>/datos/<nombre>_resumen.csv,
con la media, la desviación, el intervalo del 95 % y la diferencia pareada por semilla contra la línea base.

La figura no interpreta nada. Dibuja la media por grupo y política con su intervalo del 95 % (t de Student entre
semillas) y la meta del reto de perecederos (menos del 5 %). El rótulo de la meta va bajo el título del panel,
fuera de los ejes, para que ninguna barra lo cruce, y un número que caiga sobre la línea de la meta sube por encima
de ella. La revisión de textos compara también cada texto con las barras, los intervalos y la línea de la meta. El
título lo pone quien la use, con --titulo.

Cifras. Llevan un decimal, como despacho/sim/resultados/resumen.md. Una media que no es 100 nunca se escribe 100,
ni una que no es 0 se escribe 0. Si el redondeo la lleva ahí, se agregan decimales: una media de 99,96 se escribe
con dos, 99,96.

Corridas que no se citan. La marca «Ejemplo con resultados anteriores, no citar» la decide el contenido del CSV,
así que da igual cómo se escriba la ruta. Si la huella SHA-256 de algún archivo de la entrada está en
CORRIDAS_ANTERIORES, la figura lleva esa marca y la marca de agua «NO CITAR», también si se pide --marca "". Hoy la
lista tiene solo la corrida d33dd27 del 20 de noviembre a las 11:52 (despacho/sim/resultados/resultados.csv).
Con --marca, cualquier otra corrida lleva solo el recuadro con el texto pedido, por ejemplo «Preliminar». La marca
de agua «NO CITAR» se pide aparte, con --marca-de-agua.
"""
from __future__ import annotations

import hashlib
import math
import sys
import textwrap
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

import estilo as e

COLUMNAS = ("politica", "a_tiempo_criticos_pct", "perecedero_vencido_pct")
LLAVES = ("variante", "carga", "semilla", "politica")    # una fila por cada combinación
PATRON = "*.csv"
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
MARCA_ANTERIOR = "Ejemplo con resultados anteriores, no citar"
MARCA_DE_AGUA = "NO CITAR"
ALTO_ROTULO_META = 0.035   # fracción del alto que se quita a los ejes para el rótulo de la meta (unos 38 px)
# Huella SHA-256 de cada resultados.csv que no se cita, con los fines de línea \r\n cambiados por \n, y qué
# corrida es. La de d33dd27 es la del archivo que entró en el commit ac731d2 (despacho/sim/resultados/).
CORRIDAS_ANTERIORES = {
    "b0025b37e392b191d80f22eeec8fbad55c41755c75925a022f946c35f5a2ef24":
        "la corrida d33dd27 del 20 de noviembre de 2026 a las 11:52, que no se cita",
}
PX_VALOR, PX_GRUPO = 26, 28


def argumentos():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--entrada", required=True, help="CSV de resultados o carpeta con varios")
    p.add_argument("--patron", default=PATRON, help="archivos que se leen de una carpeta (por defecto *.csv)")
    p.add_argument("--nombre", default="e_simulacion", help="nombre de los archivos de salida")
    p.add_argument("--marca", default="", help="advertencia visible en un recuadro, por ejemplo «Preliminar». Las "
                                                "corridas de CORRIDAS_ANTERIORES llevan siempre «Ejemplo con "
                                                "resultados anteriores, no citar» y la marca de agua «NO CITAR»")
    p.add_argument("--marca-de-agua", action="store_true",
                   help="agrega la marca de agua «NO CITAR», que las corridas de CORRIDAS_ANTERIORES llevan siempre")
    p.add_argument("--titulo", default="Resultados de la simulación por política de despacho")
    p.add_argument("--etiqueta", default="", help="línea bajo el título. {jornadas} se cambia por el número de "
                                                  "filas dibujadas y {semillas} por el de semillas distintas")
    p.add_argument("--panel", default="ambos", choices=["ambos", "criticos", "perecederos"],
                   help="dibujar los dos paneles o solo uno")
    p.add_argument("--agrupar", default=None, help="columna del eje x (por defecto `carga`, o `variante` si la "
                                                   "entrada es una carpeta con varios archivos)")
    p.add_argument("--grupos", default=None, help="valores del eje x a dibujar, separados por comas")
    p.add_argument("--politicas", default=None, help="políticas a dibujar y su orden, separadas por comas")
    p.add_argument("--base", default="ingenua", help="línea base de las diferencias pareadas del resumen")
    p.add_argument("--filtro", action="append", default=[], metavar="COLUMNA=VALOR",
                   help="deja solo las filas con ese valor; se puede repetir (por ejemplo --filtro carga=alta)")
    return p.parse_args()


def archivos_de(entrada: Path, patron: str = PATRON) -> list[Path]:
    return sorted(entrada.rglob(patron)) if entrada.is_dir() else [entrada]


def huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def corrida_anterior(entrada: str | Path, patron: str = PATRON) -> str | None:
    """Si algún archivo de la entrada es una corrida que no se cita, dice cuál. Decide por el contenido."""
    for a in archivos_de(Path(entrada), patron):
        if a.is_file() and huella(a) in CORRIDAS_ANTERIORES:
            return f"{nombre_corto(a)} es {CORRIDAS_ANTERIORES[huella(a)]}"
    return None


def nombre_corto(ruta: Path) -> str:
    """La ruta desde la raíz del repositorio si queda dentro de él, para que el pie no muestre rutas largas."""
    try:
        return str(ruta.resolve().relative_to(e.RAIZ))
    except ValueError:
        return str(ruta)


def leer(entrada: Path, patron: str = PATRON) -> tuple[pd.DataFrame, str]:
    if entrada.is_dir():
        partes = []
        for a in archivos_de(entrada, patron):
            try:
                df = pd.read_csv(a)
            except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as error:
                print(f"aviso: salto {nombre_corto(a)}, que no se lee como CSV ({error})", file=sys.stderr)
                continue
            faltan = [c for c in COLUMNAS if c not in df.columns]
            if faltan:
                print(f"aviso: salto {nombre_corto(a)}, porque le falta {', '.join(faltan)}", file=sys.stderr)
                continue
            if "variante" not in df.columns:
                rel = str(a.parent.relative_to(entrada))
                df["variante"] = rel if rel != "." else entrada.resolve().name
            df["variante"] = df["variante"].astype(str)
            df["archivo"] = str(a)
            partes.append(df)
        if not partes:
            sys.exit(f"no hay CSV de resultados ({patron}, con las columnas {', '.join(COLUMNAS)}) debajo de "
                     f"{entrada}")
        datos = pd.concat(partes, ignore_index=True)
        descripcion = f"{nombre_corto(entrada)} ({len(partes)} archivos)"
    elif entrada.is_file():
        datos = pd.read_csv(entrada)
        datos["archivo"] = str(entrada)
        descripcion = nombre_corto(entrada)
    else:
        sys.exit(f"no existe {entrada}")
    faltan = [c for c in COLUMNAS if c not in datos.columns]
    if faltan:
        sys.exit(f"faltan columnas en {descripcion}: {', '.join(faltan)}")
    return sin_repetidas(datos, descripcion), descripcion


def sin_repetidas(datos: pd.DataFrame, descripcion: str) -> pd.DataFrame:
    """Descarta las filas repetidas por variante, carga, semilla y política, y deja la primera.

    Las tandas de una sensibilidad pueden repetir semillas. Sin semilla no hay cómo saber qué es una repetición, así
    que no se descarta nada.
    """
    if "semilla" not in datos.columns:
        return datos
    llaves = [c for c in LLAVES if c in datos.columns]
    repetidas = datos.duplicated(llaves, keep="first")
    if repetidas.any():
        grupos = datos[datos.duplicated(llaves, keep=False)].groupby(llaves)[list(COLUMNAS[1:])].nunique()
        distintas = int((grupos > 1).any(axis=1).sum())
        print(f"aviso: {int(repetidas.sum())} filas repetidas por {', '.join(llaves)} en {descripcion}; queda la "
              "primera, en el orden de los archivos" + (f". En {distintas} casos las cifras no coinciden"
                                                         if distintas else ""), file=sys.stderr)
    return datos[~repetidas].reset_index(drop=True)


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


def cifra(x: float, decimales: int = 1) -> str:
    """Porcentaje con `decimales`, sin escribir 100 ni 0 cuando el valor no lo es: entonces agrega decimales."""
    if x == 100:
        return "100"
    for d in range(decimales, decimales + 4):
        texto = redondear(x, d)
        valor = float(texto.replace(",", "."))
        if not ((valor >= 100 and x < 100) or (valor == 0 and x > 0)):
            return texto
    return texto


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


def medir(fig, texto: str, px: float, rotacion: float = 0) -> tuple[float, float]:
    """Ancho y alto en píxeles de un texto, sin dejarlo en la figura."""
    t = fig.text(0, 0, texto, fontsize=e.pt(px), rotation=rotacion)
    caja = e.caja_px(fig, t)
    t.remove()
    return caja.width, caja.height


def rotulos_de_grupo(fig, grupos, hueco_px) -> tuple[list[str], float]:
    """Rótulos del eje x partidos en líneas para que quepan en su hueco. Si ni así caben, van verticales (90°)."""
    crudos = [f"Carga {g}" if g in ORDEN_CARGAS else str(g).replace("_", " ") for g in grupos]
    partidos = []
    for r in crudos:
        elegido = None
        for ancho in range(len(r), 3, -1):
            prueba = textwrap.fill(r, ancho, break_long_words=False)
            if prueba.count("\n") > 2:
                break
            if medir(fig, prueba, PX_GRUPO)[0] <= hueco_px:
                elegido = prueba
                break
        if elegido is None:
            return crudos, 90
        partidos.append(elegido)
    return partidos, 0


def marca_del_eje(v: float) -> str:
    """Rótulo de una marca del eje y: entero si lo es, y si no, con un decimal y coma («2,5 %»)."""
    return f"{v:.0f} %" if abs(v - round(v)) < 1e-9 else f"{v:.1f} %".replace(".", ",")


def localizador():
    """Marcas enteras del eje y, en pasos de 1, 2, 5 o 10 (nunca 2,5)."""
    return MaxNLocator(nbins="auto", integer=True, steps=[1, 2, 5, 10])


def rotulo_meta(fig, x0: float, y_base: float, meta: float):
    """Rótulo de la meta del reto fuera de los ejes, con una muestra de la línea punteada a su izquierda."""
    fig.add_artist(Line2D([x0, x0 + 68 / e.ANCHO_PX], [y_base + 8 / e.ALTO_PX] * 2, transform=fig.transFigure,
                          color=e.AMBAR, linewidth=3, linestyle=(0, (6, 4))))   # dos trazos de la línea
    return fig.text(x0 + 80 / e.ANCHO_PX, y_base, f"meta del reto: menos de {cifra(meta, 0)} %", fontsize=e.pt(26),
                    color=e.AMBAR, fontweight="bold", va="baseline")


def panel(fig, rect, resumen, met, grupos, politicas, estilos, etiqueta, tope, y_etiqueta, meta=None):
    """Barras por grupo y política.

    Devuelve los ejes, los números puestos sobre las barras, la línea de la meta (o None) y los obstáculos que
    ningún texto debe tapar: barras, intervalos y línea de la meta.
    """
    ax = fig.add_axes(rect)
    numeros, obstaculos = [], []
    k = len(politicas)
    ancho = 0.8 / k
    ancho_px = rect[2] * e.ANCHO_PX
    # ¿Caben los números sobre las barras? Horizontales, verticales o ninguno.
    hueco_barra = ancho_px / (len(grupos) * k)
    valores = [cifra(v) for v in resumen[f"{met}_media"].dropna()]
    mas_ancho = max((medir(fig, v, PX_VALOR)[0] for v in valores), default=0)
    alto_letra = medir(fig, "0", PX_VALOR)[1]
    if mas_ancho + 8 <= hueco_barra:
        rotacion = 0
    elif alto_letra + 6 <= hueco_barra:
        rotacion = 90
    else:
        rotacion = None
        print(f"aviso: en «{etiqueta}» no caben los números sobre las barras; están en el resumen CSV",
              file=sys.stderr)
    for j, pol in enumerate(politicas):
        relleno, borde = estilos[pol]
        for i, g in enumerate(grupos):
            fila = resumen[(resumen["grupo"] == g) & (resumen["politica"] == pol)]
            if fila.empty or math.isnan(fila[f"{met}_media"].iloc[0]):
                continue
            m = fila[f"{met}_media"].iloc[0]
            # El intervalo se dibuja dentro de 0 y 100 %, porque un porcentaje no sale de ahí.
            lo = min(max(fila[f"{met}_ic_bajo"].iloc[0], 0.0), 100.0)
            hi = min(max(fila[f"{met}_ic_alto"].iloc[0], 0.0), 100.0)
            x = i - 0.4 + ancho * (j + 0.5)
            barras = ax.bar(x, m, width=ancho * 0.9, color=relleno, edgecolor=borde, linewidth=2.5)
            obstaculos.append((barras.patches[0], "una barra"))
            if hi > lo:
                intervalo, = ax.plot([x, x], [lo, hi], color=e.TEXTO, linewidth=2.5, solid_capstyle="butt")
                obstaculos.append((intervalo, "un intervalo"))
            if rotacion is not None:
                numeros.append(ax.text(x, max(m, hi) + tope * 0.015, cifra(m), ha="center", va="bottom",
                                       rotation=rotacion, fontsize=e.pt(PX_VALOR), color=e.TEXTO))
    linea_meta = None
    if meta is not None:
        linea_meta = ax.axhline(meta, color=e.AMBAR, linewidth=3, linestyle=(0, (6, 4)))
        obstaculos.append((linea_meta, "la línea de la meta"))
        rotulo_meta(fig, rect[0], rect[1] + rect[3] + 0.013, meta)
    ax.set_xlim(-0.5, len(grupos) - 0.5)
    ax.set_ylim(0, tope)
    ax.set_xticks(range(len(grupos)))
    rotulos, giro = rotulos_de_grupo(fig, grupos, ancho_px / len(grupos) - 16)
    ax.set_xticklabels(rotulos, fontsize=e.pt(PX_GRUPO), rotation=giro, linespacing=1.05)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.tick_params(axis="y", labelsize=e.pt(24), colors=e.CENIZA, length=0)
    ax.yaxis.set_major_locator(localizador())
    ax.yaxis.set_major_formatter(lambda v, _: marca_del_eje(v))
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color="#E6E3EA", linewidth=1.2)
    ax.set_axisbelow(True)
    fig.text(rect[0], y_etiqueta, etiqueta, fontsize=e.pt(32), fontweight="bold", color=e.TEXTO)
    return ax, numeros, linea_meta, obstaculos


def subir_tope(fig, ax, numeros, aire_px: float = 6):
    """Sube el tope del eje y hasta que los números de las barras queden dentro de los ejes.

    Las marcas del eje son enteras y no pasan de 100 %, aunque el tope quede más arriba para dar sitio a los
    números.
    """
    for _ in range(6):
        fig.canvas.draw()
        caja = ax.get_window_extent()
        exceso = max((e.caja_px(fig, t).y1 for t in numeros), default=0) + aire_px - caja.y1
        if exceso <= 0:
            break
        y0, y1 = ax.get_ylim()
        ax.set_ylim(y0, y1 + (exceso / caja.height) * (y1 - y0) * 1.1)
    ax.yaxis.set_major_locator(localizador())
    marcas = ax.get_yticks()
    ax.set_yticks([v for v in marcas if 0 <= v <= min(ax.get_ylim()[1], 100) + 1e-9])


def despegar_de_meta(fig, ax, numeros, linea_meta, aire_px: float = 6) -> int:
    """Sube por encima de la línea de la meta los números de las barras que caen sobre ella. Devuelve cuántos."""
    if linea_meta is None:
        return 0
    fig.canvas.draw()
    render = fig.canvas.get_renderer()
    linea = linea_meta.get_window_extent(render).padded(linea_meta.get_linewidth() * e.DPI / 72.0 / 2)
    subidos = 0
    for t in numeros:
        caja = t.get_window_extent(render)
        if caja.y0 <= linea.y1 and caja.y1 >= linea.y0:
            t.set_y(ax.transData.inverted().transform((0, linea.y1 + aire_px))[1])
            subidos += 1
    return subidos


def leyenda(fig, politicas, estilos, base_px: float, x0: float = 0.06) -> float:
    """Leyenda de políticas sobre `base_px`, en una o más filas. Devuelve su borde superior en píxeles."""
    items = []
    for p in politicas:
        t = fig.text(0, 0, POLITICAS[p][0] if p in POLITICAS else p, fontsize=e.pt(28), color=e.TEXTO,
                     va="bottom")
        items.append((p, t, e.caja_px(fig, t).width))
    filas, usado = [[]], 0.0
    for item in items:
        ocupa = 42 + item[2] + 56
        if filas[-1] and x0 * e.ANCHO_PX + usado + ocupa - 56 > 0.96 * e.ANCHO_PX:
            filas.append([])
            usado = 0.0
        filas[-1].append(item)
        usado += ocupa
    alto_fila = 48
    for i, fila in enumerate(filas):
        y_px = base_px + (len(filas) - 1 - i) * alto_fila
        x_px = x0 * e.ANCHO_PX
        for p, t, w in fila:
            relleno, borde = estilos[p]
            fig.patches.append(Rectangle((x_px / e.ANCHO_PX, (y_px + 4) / e.ALTO_PX), 30 / e.ANCHO_PX,
                                         30 / e.ALTO_PX, transform=fig.transFigure, facecolor=relleno,
                                         edgecolor=borde, linewidth=2.5))
            t.set_position(((x_px + 42) / e.ANCHO_PX, y_px / e.ALTO_PX))
            x_px += 42 + w + 56
    return base_px + len(filas) * alto_fila


def main():
    args = argumentos()
    familia = e.configurar_fuente(args.fuente)
    entrada = Path(args.entrada)
    datos, descripcion = leer(entrada, args.patron)
    marca = args.marca
    anterior = corrida_anterior(entrada, args.patron)
    if anterior:
        marca = marca or MARCA_ANTERIOR
        print(f"aviso: {anterior}; la figura lleva la marca «{marca}» y la marca de agua «NO CITAR»",
              file=sys.stderr)
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
        datos[grupo] = datos[grupo].astype(str)
        presentes = list(dict.fromkeys(datos[grupo]))
        grupos = [g for g in ORDEN_CARGAS if g in presentes] + [g for g in presentes if g not in ORDEN_CARGAS]
    else:
        grupos = ["todas"]
    if args.grupos:
        pedidos = [g.strip() for g in args.grupos.split(",") if g.strip()]
        grupos = [g for g in pedidos if g in grupos]
        if not grupos:
            sys.exit(f"--grupos: ninguno de {pedidos} está en la columna «{grupo}». Hay: {', '.join(presentes)}")
    if grupo:
        datos = datos[datos[grupo].isin(grupos)]
    presentes_pol = list(dict.fromkeys(datos["politica"]))
    politicas = [p for p in POLITICAS if p in presentes_pol] + [p for p in presentes_pol if p not in POLITICAS]
    if args.politicas:
        pedidas = [p.strip() for p in args.politicas.split(",") if p.strip()]
        politicas = [p for p in pedidas if p in presentes_pol]
        if not politicas:
            sys.exit(f"--politicas: ninguna de {pedidas} está en los datos. Hay: {', '.join(presentes_pol)}")
        datos = datos[datos["politica"].isin(politicas)]
    estilos, extra = {}, iter(ESTILOS_EXTRA * 3)
    for p in politicas:
        estilos[p] = POLITICAS[p][1:] if p in POLITICAS else next(extra)

    resumen = resumir(datos, grupo, grupos, politicas, args.base)
    carpeta_datos = Path(args.salida) / "datos"
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(carpeta_datos / f"{args.nombre}_resumen.csv", index=False, float_format="%.4f")
    print(f"fuente tipográfica: {familia}; entrada: {descripcion}; grupos: {grupos}; políticas: {politicas}")

    fig = e.lienzo()
    semillas_distintas = datos["semilla"].nunique() if "semilla" in datos.columns else 0
    etiqueta = args.etiqueta.replace("{jornadas}", e.miles(len(datos))).replace("{semillas}",
                                                                                 str(semillas_distintas))
    _, sub = e.titulo(fig, args.titulo, etiqueta or None)
    if marca:
        s = e.sello(fig, marca, y=0.865)
        if sub is not None:      # la etiqueta se achica para no pasar debajo del sello; si ni así cabe, hay AVISO
            fig.canvas.draw()
            e.encajar(fig, sub, e.caja_px(fig, s).x0 - 0.04 * e.ANCHO_PX - 30)
    if anterior or args.marca_de_agua:
        fig.text(0.5, 0.5, MARCA_DE_AGUA, fontsize=e.pt(230), color=e.AMBAR, alpha=0.10, rotation=18,
                 ha="center", va="center", fontweight="bold", zorder=0)

    # De abajo arriba: pie, leyenda y paneles, para que un pie más alto nunca tape la leyenda ni los ejes.
    cuentas = sorted({int(c) for c in resumen["n"] if c > 0})
    if not cuentas:
        sys.exit("ningún grupo tiene filas de las políticas pedidas")
    escenarios = (f"{cuentas[0]} escenarios por grupo y política" if len(cuentas) == 1 else
                  f"De {cuentas[0]} a {cuentas[-1]} escenarios por grupo y política")
    semillas = ""
    if "semilla" in datos.columns:
        s = datos["semilla"]
        claves = [grupo] if grupo else []
        iguales = all(len({frozenset(d["semilla"]) for _, d in sub_.groupby("politica")}) == 1
                      for _, sub_ in (datos.groupby(claves) if claves else [(None, datos)]))
        semillas = f", semillas {s.min()} a {s.max()}" + (", las mismas para todas" if iguales else "")
    if args.base in politicas:
        base = "Línea base: " + (POLITICAS[args.base][0].lower() if args.base in POLITICAS else args.base) + ". "
    else:
        base = f"Estos datos no traen la línea base «{args.base}». "
    pie = e.pie(fig, f"Datos: {descripcion}, {len(datos)} filas. {escenarios}{semillas}.\n"
                     f"Barra: media. Línea: intervalo del 95 % de la media entre escenarios, sin pasar de 0 ni de "
                     f"100 %. {base}Supuestos: docs/SIMULACION.md.", y=0.025)
    fig.canvas.draw()
    tope_leyenda = leyenda(fig, politicas, estilos, e.caja_px(fig, pie).y1 + 26)

    tope_crit = 109
    maximo = max(resumen["perecedero_vencido_pct_ic_alto"].max(), META_PERECEDEROS)
    tope_per = math.ceil(min(maximo, 100) * 1.25)
    paneles = {
        "criticos": ("a_tiempo_criticos_pct", "Pedidos críticos entregados a tiempo (%)", tope_crit, None),
        "perecederos": ("perecedero_vencido_pct", "Kilos perecederos vencidos (%)", tope_per, META_PERECEDEROS),
    }
    if args.panel == "ambos":
        rects = {"criticos": [0.06, 0.25, 0.50, 0.50], "perecederos": [0.64, 0.25, 0.33, 0.50]}
    else:
        rects = {args.panel: [0.06, 0.25, 0.90, 0.50]}
    y_etiqueta = 0.25 + 0.50 + 0.04
    if "perecederos" in rects:     # el rótulo de la meta va entre el título del panel y los ejes
        for rect in rects.values():
            rect[3] -= ALTO_ROTULO_META
    obstaculos = []
    for clave, rect in rects.items():
        met, texto, tope, meta = paneles[clave]
        ax, numeros, linea_meta, obst = panel(fig, rect, resumen, met, grupos, politicas, estilos, texto, tope,
                                              y_etiqueta, meta=meta)
        e.despejar(fig, ax, tope_leyenda)
        for _ in range(5):          # subir un número sobre la meta puede pedir más tope, y más tope mueve la meta
            subir_tope(fig, ax, numeros)
            if not despegar_de_meta(fig, ax, numeros, linea_meta):
                break
        obstaculos += obst
    e.terminar(e.guardar(fig, args.nombre, args.salida, ignorar=(MARCA_DE_AGUA,), obstaculos=obstaculos))


if __name__ == "__main__":
    main()
