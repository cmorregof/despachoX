"""Reglas escritas para completar un pedido que no trae familias o kilos. Las aplica el código, no el modelo.

SUPUESTO (estimado por el equipo, sin fuente todavía): las raciones por familia son las mismas que usa
la semilla de `despacho/semilla.py` (KG_POR_FAMILIA) para que la bodega y el bot hablen igual. Una
familia son 4 personas y cada bebé cuenta como una familia aparte, porque es raro que una familia
tenga varios bebés. Todo lo que sale de aquí queda marcado `supuesto` en el producto y en `dudas`,
para que el despachador sepa qué dijo la persona y qué completó la mesa.
"""
from __future__ import annotations

import math
import re
import unicodedata

PERSONAS_POR_FAMILIA = 4
KG_POR_FAMILIA = {"arroz": 2, "frijol": 1, "lenteja": 1, "aceite": 1, "panela": 0.5, "agua": 3,
                  "harina de maíz": 1, "leche": 2, "pan": 0.5, "huevos": 1, "fruta": 1.5,
                  "verdura": 1.5, "pollo": 1}
# Nombres como los escribe la gente -> nombre de la bodega
SINONIMOS = {"huevo": "huevos", "lentejas": "lenteja", "frijoles": "frijol", "frisol": "frijol",
             "frisoles": "frijol", "verduras": "verdura", "frutas": "fruta", "harina": "harina de maíz",
             "harina de maiz": "harina de maíz", "arepa": "harina de maíz", "agua potable": "agua",
             "leche en polvo": "leche", "leche entera": "leche", "panes": "pan", "pañal": "pañales",
             "formula": "leche de fórmula", "fórmula": "leche de fórmula", "leche de formula": "leche de fórmula",
             "formula infantil": "leche de fórmula", "fórmula infantil": "leche de fórmula", "compotas": "compota"}
# Productos para bebés: se conservan siempre, aunque el modelo los omita o no estén en la tabla
PARA_BEBES = {"leche": r"leche", "pañales": r"pa[ñn]al(es)?", "leche de fórmula": r"f[oó]rmula",
              "compota": r"compotas?"}
# Respuestas con botón a «¿Para cuántas familias?»: (etiqueta, valor que se guarda)
RANGOS = [("1 a 5", 3), ("6 a 10", 8), ("11 a 20", 15), ("Más de 20", 25)]


def _plano(t: str) -> str:
    """Minúsculas sin tildes; la ñ se conserva."""
    return unicodedata.normalize("NFC", (t or "").lower()).translate(str.maketrans("áéíóúü", "aeiouu"))


def canonico(nombre: str) -> str:
    n = (nombre or "").strip().lower()
    return SINONIMOS.get(n, n)


def familias_desde(personas: int | None, bebes: int | None) -> tuple[int | None, str | None]:
    """Familias aproximadas desde personas o bebés, y la nota que lo explica. (None, None) si no hay con qué."""
    personas = personas if personas and personas > 0 else 0
    bebes = bebes if bebes and bebes > 0 else 0
    if not personas and not bebes:
        return None, None
    fam = max(bebes, math.ceil(personas / PERSONAS_POR_FAMILIA), 1)
    partes = []
    if bebes:
        partes.append(f"{bebes} bebé{'s' if bebes != 1 else ''} (1 familia por bebé)")
    if personas:
        partes.append(f"{personas} persona{'s' if personas != 1 else ''} (1 familia cada {PERSONAS_POR_FAMILIA})")
    return fam, f"Familias estimadas: {fam}, a partir de " + " y ".join(partes) + "."


_BEBES = re.compile(r"\b(\d{1,4})\s+(?:bebes?|bebitos?|lactantes?|recien nacidos?)\b")
_PERSONAS = re.compile(r"\b(\d{1,4})\s+(?:personas?|niños?|niñas?|ninos?|adultos?(?: mayores)?|abuelos?|"
                       r"ancianos?|menores|habitantes|vecinos)\b")


def contar_en_texto(texto: str) -> tuple[int | None, int | None]:
    """Respaldo si el modelo no contó: (personas, bebés) escritos con cifra en el texto."""
    plano = _plano(texto)
    personas = sum(int(n) for n in _PERSONAS.findall(plano)) or None
    bebes = sum(int(n) for n in _BEBES.findall(plano)) or None
    return personas, bebes


def faltantes_para_bebes(texto: str, productos: list[str]) -> list[str]:
    """Productos para bebés que el texto nombra y la lectura dejó por fuera."""
    plano = _plano(texto)
    tiene = {canonico(p) for p in productos}
    return [p for p, patron in PARA_BEBES.items()
            if p not in tiene and re.search(rf"\b{patron}\b", plano)]


def completar_kilos(productos: list[dict], familias: int | None) -> list[str]:
    """Pone kilos por ración a los productos de la tabla que no los traen. Modifica la lista y
    devuelve las notas. Recalcula los que ya estaban marcados `supuesto` (cambió el número de familias)."""
    if not familias:
        return []
    notas = []
    for q in productos:
        racion = KG_POR_FAMILIA.get(q["producto"])
        if racion is None or (q.get("kg") and not q.get("supuesto")):
            continue
        q["kg"] = round(racion * familias, 1)
        q["supuesto"] = f"{racion:g} kg por familia"
        notas.append(f"Kilos de {q['producto']} estimados: {q['kg']:g} ({racion:g} kg por familia × {familias}).")
    return notas
