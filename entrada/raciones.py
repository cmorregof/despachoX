"""Reglas escritas para completar un pedido que no trae familias o kilos. Las aplica el código, no el modelo.

FUENTES (detalle en docs/datos/demanda.md, secciones 2 y 7; consulta del 20 nov 2026). La ración seca por
persona y día sale de la columna ACNUR de la tabla de raciones del Logistics Cluster: cereal 450 g (valor
que la tabla pone junto a 2.100 kcal, el mínimo de Esfera según ACNUR), leguminosas 60 g, aceite 25 g,
azúcar 15 g y sal 5 g: 555 g en total. El cereal se reparte 6:2:2 entre arroz, harina de maíz y pasta, como
la Ración Familiar Para Preparar del ICBF (v2, 2026). Una familia son 2,9 personas (DANE, CNPV 2018,
Manizales). Un pedido cubre 7 días, el ejemplo de ración seca semanal de OPS/INCAP. Cada bebé sigue
contando como una familia aparte.
SUPUESTOS (marcados): frijol y lenteja a partes iguales; el agua de un pedido cubre 1 día; los frescos
usan la ración mensual del ICBF como referencia, sin tamaño de familia conocido. Pollo, pan, atún, azúcar,
café y chocolate no tienen ración con fuente: se reconocen como productos pero no se les ponen kilos.
Todo lo que sale de aquí queda marcado `supuesto` en el producto y en `dudas`, para que el despachador
sepa qué dijo la persona y qué completó la mesa.
"""
from __future__ import annotations

import math
import re
import unicodedata

# Gramos por persona y día de la ración seca.
# Fuente: https://log.logcluster.org/sites/default/files/pages/199/en/main-types-of-in-kind-commodities.pdf
# Reparto del cereal: https://www.icbf.gov.co/system/files/procesos/A26.G36.PP%20Anexo%20minuta%20patr%C3%B3n%20modalidad%20de%20atenci%C3%B3n%20y%20prevenci%C3%B3n%20de%20la%20desnutrici%C3%B3n%20-%20RFPP%20_v2.pdf
G_POR_PERSONA_DIA = {"arroz": 270, "harina de maíz": 90, "pasta": 90,   # cereal 450 g, reparto 6:2:2 (ICBF)
                     "frijol": 30, "lenteja": 30,                       # leguminosas 60 g, mitad y mitad (supuesto)
                     "aceite": 25, "panela": 15, "sal": 5}              # ACNUR; azúcar 15 a 20 g, se toma 15
# Agua para beber y cocinar: 2,5 a 3 L por persona y día (OPS, nota técnica 9, citando Esfera).
# https://paho.org/sites/default/files/2019-12/Nota-tecnica-sobre-agua-saneamiento-higiene-09.pdf
AGUA_L_POR_PERSONA_DIA = 3
# DANE, CNPV 2018, Manizales: 395.818 personas en 136.806 hogares, 2,9 por hogar.
# https://www.dane.gov.co/files/censo2018/informacion-tecnica/presentaciones-territorio/190801-CNPV-presentacion-Caldas-Manizales.pdf
PERSONAS_POR_FAMILIA = 2.9
# OPS/INCAP: ración seca por familia para un periodo fijo; el ejemplo es una semana (3 a 4 kg por persona).
# https://www.paho.org/es/emergencias-salud/seguridad-alimentaria-nutricional-situaciones-emergencia
DIAS_POR_PEDIDO = 7
DIAS_AGUA_POR_PEDIDO = 1          # supuesto: el agua se reparte a diario o por carrotanque

KG_POR_FAMILIA = {p: round(g * PERSONAS_POR_FAMILIA * DIAS_POR_PEDIDO / 1000, 2)
                  for p, g in G_POR_PERSONA_DIA.items()}
# -> arroz 5.48, harina de maíz 1.83, pasta 1.83, frijol 0.61, lenteja 0.61, aceite 0.51, panela 0.3, sal 0.1
KG_POR_FAMILIA["agua"] = round(AGUA_L_POR_PERSONA_DIA * PERSONAS_POR_FAMILIA * DIAS_AGUA_POR_PEDIDO, 1)  # 8.7
# Frescos: referencia, no estándar de emergencia. Ración mensual del ICBF (RFPP v2, 16/01/2026) llevada a
# 7 días: fruta 4 kg, verdura 3 kg, huevos 4 cubetas de 30 de 60 g (7,2 kg) y leche 12 L al mes.
KG_POR_FAMILIA |= {"fruta": round(4 * DIAS_POR_PEDIDO / 30, 2),       # 0.93
                   "verdura": round(3 * DIAS_POR_PEDIDO / 30, 2),     # 0.7
                   "huevos": round(7.2 * DIAS_POR_PEDIDO / 30, 2),    # 1.68
                   "leche": round(12 * DIAS_POR_PEDIDO / 30, 2)}      # 2.8 (1 L = 1 kg)
# Sin ración con fuente: se reconocen (bot y SMS) pero completar_kilos no les pone kilos.
SIN_RACION = {"pollo", "pan", "atún", "azúcar", "café", "chocolate", "papa"}
# Nombres como los escribe la gente -> nombre de la bodega
SINONIMOS = {"pastas": "pasta", "fideos": "pasta", "espagueti": "pasta", "azucar": "azúcar",
             "atun": "atún", "cafe": "café", "papas": "papa", "huevo": "huevos", "lentejas": "lenteja", "frijoles": "frijol", "frisol": "frijol",
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
        partes.append(f"{personas} persona{'s' if personas != 1 else ''} "
                      f"(1 familia cada {PERSONAS_POR_FAMILIA:g} personas)".replace(".", ","))
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
