"""Figura (b): el cuello de botella fue despachar. Kilos en acopio, en tránsito y entregados tras el sismo.

Uso: python figuras_pitch/scripts/cuello_despacho.py [--fuente FAMILIA] [--salida CARPETA] [--ref-fuentes REF]
Lee  figuras_pitch/datos/cuello_despacho.csv (cifras y fuente) y el estado de la cifra en docs/FUENTES.md.
Escribe <salida>/png/b_cuello_despacho.png y <salida>/svg/b_cuello_despacho.svg.

Adaptada de docs/informe/figuras/scripts/barras_abaco.py, sin editar ese archivo.

Estado de verificación. El script busca la fila de «404.587» en docs/FUENTES.md de la carpeta de trabajo y, si no
la encuentra ahí, en la referencia de git --ref-fuentes (por defecto origin/fuentes-noche, leída con git show, sin
tocarla). El estado solo decide entre dos textos fijos. Si empieza por «Verificada por <nombre>», que es como el
equipo anota que una persona abrió la fuente, la figura no lleva sello. En cualquier otro caso lleva el sello
«Cifras por verificar». Así la figura no cambia cuando alguien reescribe la celda sin cambiar el estado, y el pie
nunca muestra una ruta de git. El estado leído y su origen salen solo en la consola.
"""
import csv
import re
import subprocess

import estilo as e

NOMBRE = "b_cuello_despacho"
DATOS = e.CARPETA / "datos" / "cuello_despacho.csv"
COLORES = {"En acopio": e.TINTA, "En tránsito": e.CENIZA, "Entregados": e.AMBAR}
VERIFICADA = re.compile(r"Verificada por (?!m[aá]quina|persona\b)\S")
PIE_FUENTE = ("Fuente: Portafolio, «Flypass paga peajes de 57 camiones para acelerar la entrega de ayudas tras el "
              "terremoto en Colombia», 16 de agosto de 2026.\n"
              "La nota atribuye las cifras a «los Bancos de Alimentos» y no dice hacia dónde iban los kilos en "
              "tránsito. «Seis días después» sale de su fecha.")
PIE_ESTADO = {
    True: "Una persona del equipo cotejó las cifras con la nota.",
    False: "Por verificar: falta que una persona del equipo abra la nota y coteje las cifras.",
}


def leer_fuentes(ref: str) -> list[tuple[str, str]]:
    """Textos de FUENTES.md que hay a mano: el de la carpeta de trabajo y el de la referencia `ref`."""
    textos = []
    local = e.RAIZ / "docs" / "FUENTES.md"
    if local.exists():
        textos.append(("docs/FUENTES.md", local.read_text(encoding="utf-8")))
    try:
        remoto = subprocess.run(["git", "-C", str(e.RAIZ), "show", f"{ref}:docs/FUENTES.md"],
                                capture_output=True, text=True, timeout=20)
        if remoto.returncode == 0:
            textos.append((f"{ref}:docs/FUENTES.md", remoto.stdout))
    except (OSError, subprocess.SubprocessError):
        pass
    return textos


def estado_de(clave: str, ref: str) -> tuple[bool, str, str]:
    """(verificada, texto del estado, dónde se leyó) para la primera fila de FUENTES.md que contiene `clave`."""
    for origen, texto in leer_fuentes(ref):
        for linea in texto.splitlines():
            if not linea.startswith("|") or clave not in linea:
                continue
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            estado = next((c for c in celdas if re.match(r"(Verificada|Revisada|Por verificar|No coincide)", c)), "")
            if not estado:
                continue
            return bool(VERIFICADA.match(estado)), estado, origen
    return False, "sin fila en FUENTES.md", "ninguno"


def main():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--ref-fuentes", default="origin/fuentes-noche",
                   help="referencia de git donde buscar docs/FUENTES.md si la carpeta de trabajo no trae la fila")
    args = p.parse_args()
    familia = e.configurar_fuente(args.fuente)
    with open(DATOS, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    verificada, estado, origen = estado_de(filas[0]["clave_fuentes"], args.ref_fuentes)
    print(f"fuente tipográfica: {familia}; estado de la cifra: {estado} ({origen}); "
          f"la figura dice: {'verificada' if verificada else 'por verificar'}")

    fig = e.lienzo()
    e.titulo(fig, "La donación llegó y el despacho se atascó",
             "Kilos de los bancos de alimentos el 16 de agosto, seis días después del sismo")
    if not verificada:
        e.sello(fig, "Cifras por verificar")

    ax = fig.add_axes([0.20, 0.30, 0.62, 0.46])
    y = list(range(len(filas)))[::-1]
    kilos = [int(f["kg"]) for f in filas]
    ax.barh(y, kilos, color=[COLORES[f["rotulo"]] for f in filas], height=0.62)
    tope = max(kilos)
    for yi, fila, kg in zip(y, filas, kilos):
        color = COLORES[fila["rotulo"]]
        ax.text(kg + tope * 0.015, yi, f"{e.miles(kg)} kg", va="center", ha="left",
                fontsize=e.pt(48), fontweight="bold", color=e.color_de_texto(color))
        ax.text(-tope * 0.025, yi, fila["rotulo"], va="center", ha="right", fontsize=e.pt(42), color=e.TEXTO)
    ax.set_xlim(0, tope * 1.32)
    ax.set_ylim(-0.6, len(filas) - 0.4)
    ax.axis("off")
    ax.axvline(0, color=e.CENIZA, linewidth=2)

    pie = e.pie(fig, PIE_FUENTE + "\n" + PIE_ESTADO[verificada])
    fig.canvas.draw()
    e.despejar(fig, ax, e.caja_px(fig, pie).y1)
    e.terminar(e.guardar(fig, NOMBRE, args.salida))


if __name__ == "__main__":
    main()
