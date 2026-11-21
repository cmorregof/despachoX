"""Figura (b): el cuello de botella fue despachar. Kilos en acopio, en tránsito y entregados al sexto día.

Uso: python figuras_pitch/scripts/cuello_despacho.py [--fuente FAMILIA] [--salida CARPETA]
Lee  figuras_pitch/datos/cuello_despacho.csv (cifras y fuente) y el estado de la cifra en docs/FUENTES.md.
Escribe <salida>/png/b_cuello_despacho.png y <salida>/svg/b_cuello_despacho.svg.

Adaptada de docs/informe/figuras/scripts/barras_abaco.py, sin editar ese archivo.

Estado de verificación. El script busca la fila de «404.587» en docs/FUENTES.md de la carpeta de trabajo y, si no
la encuentra ahí, en la rama origin/fuentes-noche (con git show, solo lectura). La figura dice «Cifras por
verificar» salvo que el estado de esa fila empiece por «Verificada por <nombre>», que es como el equipo anota que
una persona abrió la fuente. «Revisada por máquina» no cuenta como verificada.
"""
import csv
import re
import subprocess

import estilo as e

NOMBRE = "b_cuello_despacho"
DATOS = e.CARPETA / "datos" / "cuello_despacho.csv"
COLORES = {"En acopio": e.TINTA, "En tránsito": e.CENIZA, "Entregados": e.AMBAR}


def leer_fuentes() -> list[tuple[str, str]]:
    """Textos de FUENTES.md que hay a mano: el de la carpeta de trabajo y el de origin/fuentes-noche."""
    textos = []
    local = e.RAIZ / "docs" / "FUENTES.md"
    if local.exists():
        textos.append(("docs/FUENTES.md", local.read_text(encoding="utf-8")))
    try:
        remoto = subprocess.run(["git", "-C", str(e.RAIZ), "show", "origin/fuentes-noche:docs/FUENTES.md"],
                                capture_output=True, text=True, timeout=20)
        if remoto.returncode == 0:
            textos.append(("origin/fuentes-noche:docs/FUENTES.md", remoto.stdout))
    except (OSError, subprocess.SubprocessError):
        pass
    return textos


def estado_de(clave: str) -> tuple[bool, str, str]:
    """(verificada, texto del estado, dónde se leyó) para la primera fila de FUENTES.md que contiene `clave`."""
    for origen, texto in leer_fuentes():
        for linea in texto.splitlines():
            if not linea.startswith("|") or clave not in linea:
                continue
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            estado = next((c for c in celdas if re.match(r"(Verificada|Revisada|Por verificar|No coincide)", c)), "")
            if not estado:
                continue
            verificada = bool(re.match(r"Verificada por (?!m[aá]quina|persona\b)", estado))
            return verificada, estado, origen
    return False, "sin fila en FUENTES.md", "ninguno"


def main():
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    with open(DATOS, encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    verificada, estado, origen = estado_de(filas[0]["clave_fuentes"])
    print(f"fuente tipográfica: {familia}; estado de la cifra: {estado} ({origen})")

    fig = e.lienzo()
    e.titulo(fig, "La donación llegó y el despacho se atascó",
             "Kilos de la red de bancos de alimentos el 16 de agosto, sexto día después del sismo")
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
                fontsize=e.pt(48), fontweight="bold", color=color)
        ax.text(-tope * 0.025, yi, fila["rotulo"], va="center", ha="right", fontsize=e.pt(42), color=e.TEXTO)
    ax.set_xlim(0, tope * 1.32)
    ax.set_ylim(-0.6, len(filas) - 0.4)
    ax.axis("off")
    ax.axvline(0, color=e.CENIZA, linewidth=2)

    f0 = filas[0]
    lineas = [
        f"Fuente: {f0['fuente']}, 16 de agosto de 2026.",
        "La nota atribuye las cifras a «los Bancos de Alimentos». «Sexto día» sale de la fecha de publicación.",
    ]
    if verificada:
        lineas.append(f"Estado en {origen}: {estado}.")
    else:
        lineas.append(f"Por verificar: nadie ha anotado que abrió la nota. Estado en {origen}: "
                      f"{estado.split(':')[0].lower()}.")
    e.pie(fig, "\n".join(lineas))
    e.guardar(fig, NOMBRE, args.salida)


if __name__ == "__main__":
    main()
