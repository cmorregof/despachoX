"""Figura (e): plantilla que dibuja los resultados de la simulación desde resultados.csv.

Uso:
    python figuras_pitch/scripts/sim_resultados.py --entrada despacho/sim/<carpeta>/resultados.csv \\
        --salida figuras_pitch --titulo "<lo que muestran los resultados>"
    python figuras_pitch/scripts/sim_resultados.py --entrada analisis/sensibilidad/resultados --salida <carpeta>
    python figuras_pitch/scripts/sim_resultados.py --entrada <csv> --panel criticos --filtro carga=alta \\
        --etiqueta "Simulación: {jornadas} jornadas sintéticas sobre la red vial de Manizales"

Entrada. Un CSV con una fila por carga, semilla y política, como el que escribe `python -m despacho.sim.correr`,
o una carpeta: entonces se leen todos los `resultados*.csv` que haya debajo y cada archivo queda como una variante
con el nombre de su carpeta. Columnas que hacen falta: `politica`, `a_tiempo_criticos_pct` y
`perecedero_vencido_pct`. `semilla` y `carga` son opcionales.

Salida. <salida>/png/<nombre>.png (1920 × 1080), <salida>/svg/<nombre>.svg y <salida>/datos/<nombre>_resumen.csv,
con la media, la desviación, el intervalo del 95 % y la diferencia pareada por semilla contra la línea base.

La figura no interpreta nada. Dibuja la media por grupo y política con su intervalo del 95 % (t de Student entre
semillas) y la meta del reto de perecederos (menos del 5 %). El título lo pone quien la use, con --titulo.

Cifras. Llevan un decimal, como despacho/sim/resultados/resumen.md. Una media que no es 100 nunca se escribe 100,
ni una que no es 0 se escribe 0. Si el redondeo la lleva ahí, se agregan decimales: una media de 99,96 se escribe
con dos, 99,96.

Corridas que no se citan. La marca «Ejemplo con resultados anteriores, no citar» la decide el contenido del CSV,
así que da igual cómo se escriba la ruta. Si la huella SHA-256 de algún archivo de la entrada está en
CORRIDAS_ANTERIORES, la figura lleva la marca, también si se pide --marca "". Hoy la lista tiene solo la corrida
d33dd27 del 20 de noviembre a las 11:52 (despacho/sim/resultados/resultados.csv).
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
MARCA_ANTERIOR = "Ejemplo con resultados anteriores, no citar"
# Huella SHA-256 de cada resultados.csv que no se cita, con los fines de línea \r\n cambiados por \n, y qué
# corrida es. La de d33dd27 es la del archivo que entró en el commit ac731d2 (despacho/sim/resultados/).
CORRIDAS_ANTERIORES = {
    "b0025b37e392b191d80f22eeec8fbad55c41755c75925a022f946c35f5a2ef24":
        "la corrida d33dd27 del 20 de noviembre de 2026 a las 11:52, que no se cita",
}
PX_VALOR, PX_GRUPO = 26, 28


def argumentos():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--entrada", required=True, help="resultados.csv o carpeta con varios resultados*.csv")
    p.add_argument("--nombre", default="e_simulacion", help="nombre de los archivos de salida")
    p.add_argument("--marca", default="", help="advertencia visible, por ejemplo «Ejemplo con resultados "
                                                "anteriores, no citar». Las corridas de CORRIDAS_ANTERIORES la "
                                                "llevan siempre")
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


def archivos_de(entrada: Path) -> list[Path]:
    return sorted(entrada.rglob("resultados*.csv")) if entrada.is_dir() else [entrada]


def huella(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def corrida_anterior(entrada: str | Path) -> str | None:
    """Si algún archivo de la entrada es una corrida que no se cita, dice cuál. Decide por el contenido."""
    for a in archivos_de(Path(entrada)):
        if a.is_file() and huella(a) in CORRIDAS_ANTERIORES:
            return f"{nombre_corto(a)} es {CORRIDAS_ANTERIORES[huella(a)]}"
    return None


def nombre_corto(ruta: Path) -> str:
    """La ruta desde la raíz del repositorio si queda dentro de él, para que el pie no muestre rutas largas."""
    try:
        return str(ruta.resolve().relative_to(e.RAIZ))
    except ValueError:
        return str(ruta)


def leer(entrada: Path) -> tuple[pd.DataFrame, str]:
    if entrada.is_dir():
        archivos = archivos_de(entrada)
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
        descripcion = f"{nombre_corto(entrada)} ({len(archivos)} archivos)"
    elif entrada.is_file():
        datos = pd.read_csv(entrada)
        datos["archivo"] = str(entrada)
        descripcion = nombre_corto(entrada)
    else:
        sys.exit(f"no existe {entrada}")
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


def panel(fig, rect, resumen, met, grupos, politicas, estilos, etiqueta, tope, meta=None):
    """Barras por grupo y política. Devuelve los ejes y los números puestos sobre las barras."""
    ax = fig.add_axes(rect)
    numeros = []
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
            ax.bar(x, m, width=ancho * 0.9, color=relleno, edgecolor=borde, linewidth=2.5)
            if hi > lo:
                ax.plot([x, x], [lo, hi], color=e.TEXTO, linewidth=2.5, solid_capstyle="butt")
            if rotacion is not None:
                numeros.append(ax.text(x, max(m, hi) + tope * 0.015, cifra(m), ha="center", va="bottom",
                                       rotation=rotacion, fontsize=e.pt(PX_VALOR), color=e.TEXTO))
    if meta is not None:
        ax.axhline(meta, color=e.AMBAR, linewidth=3, linestyle=(0, (6, 4)))
        ax.text(1.0, meta + tope * 0.02, f"meta del reto: menos de {cifra(meta, 0)} %",
                transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=e.pt(26), color=e.AMBAR,
                fontweight="bold")
    ax.set_xlim(-0.5, len(grupos) - 0.5)
    ax.set_ylim(0, tope)
    ax.set_xticks(range(len(grupos)))
    rotulos, giro = rotulos_de_grupo(fig, grupos, ancho_px / len(grupos) - 16)
    ax.set_xticklabels(rotulos, fontsize=e.pt(PX_GRUPO), rotation=giro, linespacing=1.05)
    ax.tick_params(axis="x", length=0, pad=10)
    ax.tick_params(axis="y", labelsize=e.pt(24), colors=e.CENIZA, length=0)
    ax.yaxis.set_major_formatter(lambda v, _: f"{v:.0f} %")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.grid(axis="y", color="#E6E3EA", linewidth=1.2)
    ax.set_axisbelow(True)
    fig.text(rect[0], rect[1] + rect[3] + 0.04, etiqueta, fontsize=e.pt(32), fontweight="bold", color=e.TEXTO)
    return ax, numeros


def subir_tope(fig, ax, numeros, aire_px: float = 6):
    """Sube el tope del eje y hasta que los números de las barras queden dentro de los ejes.

    Las marcas del eje no pasan de 100 %, aunque el tope quede más arriba para dar sitio a los números.
    """
    for _ in range(6):
        fig.canvas.draw()
        caja = ax.get_window_extent()
        exceso = max((e.caja_px(fig, t).y1 for t in numeros), default=0) + aire_px - caja.y1
        if exceso <= 0:
            break
        y0, y1 = ax.get_ylim()
        ax.set_ylim(y0, y1 + (exceso / caja.height) * (y1 - y0) * 1.1)
    marcas = ax.get_yticks()
    ax.set_yticks([v for v in marcas if 0 <= v <= min(ax.get_ylim()[1], 100) + 1e-9])


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
    datos, descripcion = leer(entrada)
    marca = args.marca
    anterior = corrida_anterior(entrada)
    if anterior:
        marca = marca or MARCA_ANTERIOR
        print(f"aviso: {anterior}; la figura lleva la marca «{marca}»", file=sys.stderr)
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
        if sub is not None:      # la etiqueta no puede pasar debajo del sello
            fig.canvas.draw()
            e.encajar(fig, sub, e.caja_px(fig, s).x0 - 0.04 * e.ANCHO_PX - 30)
        fig.text(0.5, 0.5, "NO CITAR", fontsize=e.pt(230), color=e.AMBAR, alpha=0.10, rotation=18,
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
    for clave, rect in rects.items():
        met, texto, tope, meta = paneles[clave]
        ax, numeros = panel(fig, rect, resumen, met, grupos, politicas, estilos, texto, tope, meta=meta)
        e.despejar(fig, ax, tope_leyenda)
        subir_tope(fig, ax, numeros)
    e.terminar(e.guardar(fig, args.nombre, args.salida, ignorar=(marca, "NO CITAR")))


if __name__ == "__main__":
    main()
