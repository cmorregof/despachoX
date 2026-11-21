"""Generador de los 300 pedidos sintéticos con los que se mide el lector de pedidos por texto.

    python evaluacion/lector/generar.py               # reescribe conjunto.jsonl (300 generados + 30 a mano)
    python evaluacion/lector/generar.py --verificar   # comprueba que la parte generada sale igual, byte a byte

Cada mensaje sale de un registro conocido: un lugar del nomenclátor (barrios.csv, veredas de
lugares_extra.csv y puntos.csv de datos/semilla/), un conteo de familias, personas, niños, adultos
mayores o bebés, productos del catálogo de entrada/raciones.py (con kilos a veces) y una urgencia.
El registro es la etiqueta de oro; el texto se escribe después, como escriben los comités.

Semilla fija: SEMILLA = 20261121. Con la misma semilla, los mismos CSV de la semilla y Python 3.12,
la parte generada se reproduce byte a byte. El generador no importa código de entrada/ ni de
lugares/: lee los CSV directamente, para que la etiqueta no dependa del lector que se mide.

Mezcla de variantes (variante principal, disjunta; suma 300):

    sms           30   el formato enseñado en docs/SIN_CONEXION.md: PEDIDO 40 SAN JOSE ARROZ LECHE
    limpio        30   chat bien escrito: tildes, mayúsculas iniciales y puntuación
    sin_tildes    30   minúsculas, sin tildes, poca puntuación
    mayusculas    30   mayúsculas sostenidas
    abreviaturas  45   flias, xfa, porfa, q, x, pa, d, b/, pers, tb, grax
    voz           60   transcripción de una nota de voz: homófonos (s por z, s por c, b por v, y por ll,
                       h muda), números en palabras (60 %), palabras partidas o pegadas (45 %)
    dos_pedidos   30   dos pedidos de lugares distintos en un mensaje, sin tildes
    faltan_datos  45   15 sin lugar, 15 sin conteo y 15 sin productos, sin tildes

Atributos que se cruzan con todas las variantes (probabilidad por pedido):
    conteo        familias 50 %, personas 30 %, niños 7 %, adultos mayores 6 %, bebés 7 %;
                  aproximado («como», «unas», «más o menos») 20 %
    urgencia      urgente 20 %, puede esperar 8 % (nunca junto a niños, mayores o bebés), normal el resto;
                  mención de vulnerables sin número («hay niños») 10 %
    productos     1 (30 %), 2 (40 %), 3 (20 %) o 4 (10 %) del catálogo, con pesos; kilos explícitos 15 %
    lugar         barrio 80 %, vereda 10 %, albergue, comedor o salón comunal 10 %
    cortesía      saludo 75 %, despedida 50 % («gracias», «Dios les pague», «quedamos atentos»)

Regla de urgencia del oro, la misma que escribe entrada/extraer.py: 3 si dice urgente o hay niños,
enfermos o adultos mayores; 1 si dice que puede esperar; 2 en los demás casos.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
SEMILLA_DATOS = RAIZ / "datos" / "semilla"
CONJUNTO = AQUI / "conjunto.jsonl"
DIFICILES = AQUI / "dificiles.jsonl"
SEMILLA = 20261121
N = 300

PLAN = [("sms", 30), ("limpio", 30), ("sin_tildes", 30), ("mayusculas", 30), ("abreviaturas", 45),
        ("voz", 60), ("dos_pedidos", 30), ("faltan_datos", 45)]

# ---------- catálogo: los nombres de bodega de entrada/raciones.py (KG_POR_FAMILIA y PARA_BEBES) ----------
# (nombre de bodega, peso al sortear, formas en que lo escribe la gente)
CATALOGO = [
    ("arroz", 10, ["arroz"]),
    ("frijol", 6, ["frijol", "fríjol", "frijoles", "frisoles"]),
    ("lenteja", 5, ["lenteja", "lentejas"]),
    ("aceite", 6, ["aceite"]),
    ("panela", 6, ["panela"]),
    ("agua", 9, ["agua", "agua potable"]),
    ("harina de maíz", 3, ["harina de maíz", "harina"]),
    ("leche", 7, ["leche", "leche en polvo"]),
    ("pan", 3, ["pan"]),
    ("huevos", 4, ["huevos"]),
    ("fruta", 3, ["fruta", "frutas"]),
    ("verdura", 3, ["verdura", "verduras"]),
    ("pollo", 2, ["pollo"]),
    ("pañales", 2, ["pañales"]),
    ("leche de fórmula", 1, ["leche de fórmula", "fórmula"]),
    ("compota", 1, ["compotas", "compota"]),
]
PARA_BEBES = ["pañales", "leche de fórmula", "compota"]
SIN_KILOS = {"pañales", "compota"}
KILOS = [5, 10, 20, 25, 30, 40, 50, 100]

# ---------- conteos ----------
UNIDADES = {   # unidad: (campo del oro, género, rango, palabras, abreviaturas)
    "familias": ("familias", "f", (3, 60), ["familias"], ["flias", "flias", "fams"]),
    "personas": ("personas", "f", (8, 200), ["personas"], ["pers", "personas"]),
    "ninos": ("personas", "m", (4, 40), ["niños"], ["niños"]),
    "abuelos": ("personas", "m", (3, 25), ["adultos mayores", "abuelitos", "abuelos"], ["abuelitos"]),
    "bebes": ("bebes", "m", (1, 12), ["bebés"], ["bebes"]),
}
VULNERABLES = {"ninos", "abuelos", "bebes"}

SALUDOS = ["hola, ", "buenas, ", "buenos días, ", "buenas tardes, ", "buenas noches, ", "hola buenas, "]
DESPEDIDAS = [" gracias", " muchas gracias", " mil gracias", " Dios les pague", " quedamos atentos"]
URGENTE = ["urgente", "es urgente", "por favor urgente", "urge", "con urgencia"]
ESPERA = ["puede esperar hasta mañana", "no hay afán, podemos esperar", "podemos esperar unos días"]
MENCION_VULNERABLE = ["hay niños", "hay niños pequeños", "hay adultos mayores", "hay abuelitos", "tenemos enfermos"]

# Plantillas: {lugar} {conteo} {prods} son los datos; lo demás es texto del comité.
COMPLETAS = [
    "{saludo}somos {conteo} en {lugar} y no hay {prods}{extra}{despedida}",
    "{saludo}en {lugar} hay {conteo} sin {prods}{extra}{despedida}",
    "{saludo}necesitamos {prods} para {conteo} en {lugar}{extra}{despedida}",
    "{lugar}: {conteo}, necesitamos {prods}{extra}{despedida}",
    "{saludo}desde {lugar} pedimos {prods} para {conteo}{extra}{despedida}",
    "{saludo}acá en {lugar} somos {conteo} y nos falta {prods}{extra}{despedida}",
    "{saludo}por favor {prods} para {lugar}, somos {conteo}{extra}{despedida}",
    "{saludo}el comité de {lugar} pide {prods} para {conteo}{extra}{despedida}",
    "{saludo}en {lugar} {conteo} necesitan {prods}{extra}{despedida}",
]
CON_KILOS = {2, 3, 4, 6, 7, 8}          # plantillas donde «50 kilos de arroz» se lee natural
SIN_LUGAR = [
    "{saludo}somos {conteo} y no hay {prods}{extra}{despedida}",
    "{saludo}necesitamos {prods} para {conteo}{extra}{despedida}",
    "{saludo}por favor {prods}, somos {conteo}{extra}{despedida}",
    "{saludo}hay {conteo} sin {prods}{extra}{despedida}",
]
SIN_CONTEO = [
    "{saludo}en {lugar} no hay {prods}{extra}{despedida}",
    "{saludo}necesitamos {prods} en {lugar}{extra}{despedida}",
    "{saludo}somos varias familias en {lugar} y nos falta {prods}{extra}{despedida}",
    "{saludo}desde {lugar} pedimos {prods}{extra}{despedida}",
]
SIN_PRODUCTOS = [
    "{saludo}somos {conteo} en {lugar} y no tenemos comida{extra}{despedida}",
    "{saludo}necesitamos mercados para {conteo} en {lugar}{extra}{despedida}",
    "{saludo}en {lugar} hay {conteo} que necesitan ayuda{extra}{despedida}",
    "{saludo}desde {lugar} pedimos ayuda para {conteo}{extra}{despedida}",
]
PEDIDO_CORTO = [
    "{conteo} en {lugar} necesitan {prods}",
    "en {lugar} somos {conteo} sin {prods}",
    "en {lugar} hay {conteo} sin {prods}",
]
SEPARADORES = [" y ", ". También ", "; además "]

ABREVIATURAS = [   # (palabra, formas abreviadas); solo se aplican al texto del comité, nunca al lugar
    ("por favor", ["xfa", "porfa", "x fa"]), ("familias", ["flias", "fams"]), ("personas", ["pers"]),
    ("que", ["q"]), ("para", ["pa", "p"]), ("por", ["x"]), ("de", ["d"]), ("barrio", ["b/", "bº", "brr"]),
    ("también", ["tb", "tmb"]), ("gracias", ["grax", "gracias"]), ("buenas", ["bns", "buenas"]),
    ("necesitamos", ["necesitamos", "nesecitamos"]),
]

# ---------- números en palabras (1 a 999) ----------
_UNI = ["", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve"]
_ESP = {10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce", 15: "quince", 16: "dieciséis",
        17: "diecisiete", 18: "dieciocho", 19: "diecinueve", 20: "veinte", 21: "veintiún", 22: "veintidós",
        23: "veintitrés", 24: "veinticuatro", 25: "veinticinco", 26: "veintiséis", 27: "veintisiete",
        28: "veintiocho", 29: "veintinueve"}
_DEC = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_CEN = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos",
        6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}


def en_palabras(n: int, genero: str = "m") -> str:
    """40 -> «cuarenta»; 21 familias -> «veintiuna»; 200 personas -> «doscientas»."""
    if not 0 < n < 1000:
        raise ValueError(n)
    if n == 100:
        return "cien"
    c, r = divmod(n, 100)
    partes = [_CEN[c]] if c else []
    if r:
        if r < 10:
            partes.append(_UNI[r])
        elif r < 30:
            partes.append(_ESP[r])
        else:
            d, u = divmod(r, 10)
            partes.append(_DEC[d] + (f" y {_UNI[u]}" if u else ""))
    texto = " ".join(partes)
    if genero == "f":
        texto = texto.replace("ientos", "ientas")
        texto = re.sub(r"\bun$", "una", texto).replace("veintiún", "veintiuna")
    return texto


# ---------- texto ----------

def sin_tildes(t: str) -> str:
    """Quita tildes y diéresis; la ñ se queda, como en un teclado de celular."""
    return t.translate(str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU"))


def plano(t: str) -> str:
    """Minúsculas, sin tildes ni signos: la forma con que se compara el lugar escrito."""
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split())


def _cap(t: str) -> str:
    return t[:1].upper() + t[1:]


# ---------- registros ----------

def lugares() -> list[dict]:
    """Lugares de pedido del nomenclátor, en un orden fijo."""
    def leer(nombre):
        with open(SEMILLA_DATOS / nombre, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    barrios = [{"nombre": r["nombre"], "tipo": "barrio", "nucleo": r["nombre"]} for r in leer("barrios.csv")]
    veredas = [{"nombre": r["nombre"], "tipo": "vereda", "nucleo": r["nombre"]}
               for r in leer("lugares_extra.csv") if r["tipo"] == "vereda"]
    puntos = []
    for r in leer("puntos.csv"):
        clase = r["nombre"].split()[0].lower()       # albergue, comedor, salón, punto
        if clase in ("albergue", "comedor", "salón"):
            puntos.append({"nombre": r["nombre"], "tipo": "punto", "nucleo": r["barrio"], "clase": clase})
    return sorted(barrios, key=lambda x: x["nombre"]), veredas, puntos


class Generador:
    def __init__(self, semilla: int = SEMILLA):
        self.rng = random.Random(semilla)
        self.barrios, self.veredas, self.puntos = lugares()

    # --- el registro (la verdad) ---

    def lugar(self) -> dict:
        r = self.rng.random()
        if r < 0.80:
            base = self.rng.choice(self.barrios)
        elif r < 0.90:
            base = self.rng.choice(self.veredas)
        else:
            base = self.rng.choice(self.puntos)
        return dict(base)

    def conteo(self, permitir_vulnerables: bool = True) -> dict:
        r = self.rng.random()
        unidad = ("familias" if r < 0.50 else "personas" if r < 0.80 else "ninos" if r < 0.87
                  else "abuelos" if r < 0.93 else "bebes")
        if not permitir_vulnerables and unidad in VULNERABLES:
            unidad = "familias"
        lo, hi = UNIDADES[unidad][2]
        return {"unidad": unidad, "n": self.rng.randint(lo, hi), "aprox": self.rng.random() < 0.20}

    def productos(self, bebes: bool) -> list[dict]:
        k = self.rng.choices([1, 2, 3, 4], weights=[30, 40, 20, 10])[0]
        nombres = [c[0] for c in CATALOGO]
        pesos = [c[1] for c in CATALOGO]
        elegidos: list[str] = []
        if bebes and self.rng.random() < 0.6:
            elegidos.append(self.rng.choice(PARA_BEBES))
        while len(elegidos) < k:
            p = self.rng.choices(nombres, weights=pesos)[0]
            if p not in elegidos:
                elegidos.append(p)
        return [{"producto": p, "kg": None} for p in elegidos]

    def registro(self, permitir_kilos: bool = True) -> dict:
        urg = self.rng.random()
        urgencia = "urgente" if urg < 0.20 else "espera" if urg < 0.28 else "normal"
        conteo = self.conteo(permitir_vulnerables=urgencia != "espera")
        prods = self.productos(conteo["unidad"] == "bebes")
        if permitir_kilos and self.rng.random() < 0.15:
            candidatos = [q for q in prods if q["producto"] not in SIN_KILOS]
            if candidatos:
                self.rng.choice(candidatos)["kg"] = self.rng.choice(KILOS)
        mencion = urgencia != "espera" and self.rng.random() < 0.10
        return {"lugar": self.lugar(), "conteo": conteo, "productos": prods, "urgencia": urgencia,
                "mencion": self.rng.choice(MENCION_VULNERABLE) if mencion else None}

    # --- el texto, por pedazos marcados ---
    # Un pedazo es (clase, texto, índice del pedido). Clases: t (texto del comité), pre (barrio, vereda),
    # lugar, num, unidad, prod, kg. Las variantes transforman cada clase a su manera.

    def _lugar_pedazos(self, lugar: dict, i: int, estilo: str) -> list[tuple]:
        r = self.rng
        if lugar["tipo"] == "barrio":
            pre = r.choice(["", "", "el barrio ", "barrio "])
            return ([("pre", pre, i)] if pre else []) + [("lugar", lugar["nombre"], i)]
        if lugar["tipo"] == "vereda":
            pre = r.choice(["la vereda ", "vereda ", ""])
            return ([("pre", pre, i)] if pre else []) + [("lugar", lugar["nombre"], i)]
        clase, barrio = lugar["clase"], lugar["nucleo"]
        forma = {"albergue": ["albergue de {b}", "el albergue de {b}", "albergue temporal {b}"],
                 "comedor": ["comedor de {b}", "comedor comunitario de {b}"],
                 "salón": ["salón comunal de {b}", "salón comunal {b}"]}[clase]
        return [("lugar", r.choice(forma).format(b=barrio), i)]

    def _conteo_pedazos(self, conteo: dict, i: int, estilo: str) -> list[tuple]:
        unidad = conteo["unidad"]
        genero = UNIDADES[unidad][1]
        palabras = UNIDADES[unidad][4] if estilo == "abreviaturas" else UNIDADES[unidad][3]
        pedazos = []
        if conteo["aprox"]:
            pedazos.append(("t", self.rng.choice(["como ", "más o menos ",
                                                  "unas " if genero == "f" else "unos "]), i))
        pedazos += [("num", str(conteo["n"]), i), ("t", " ", i), ("unidad", self.rng.choice(palabras), i)]
        return pedazos

    def _productos_pedazos(self, prods: list[dict], i: int, estilo: str) -> list[tuple]:
        piezas = []
        for q in prods:
            forma = self.rng.choice(next(c[2] for c in CATALOGO if c[0] == q["producto"]))
            if q["kg"]:
                u = self.rng.choice(["kilos", "kg", "kilos"])
                if self.rng.random() < 0.7:
                    piezas.append([("kg", str(q["kg"]), i), ("t", f" {u} de ", i), ("prod", forma, i)])
                else:
                    piezas.append([("prod", forma, i), ("t", " ", i), ("kg", str(q["kg"]), i), ("t", f" {u}", i)])
            else:
                piezas.append([("prod", forma, i)])
        unir = self.rng.choice(["coma", "espacio"]) if estilo not in ("limpio", "voz") else "coma"
        pedazos = []
        for j, pieza in enumerate(piezas):
            if j:
                ultimo = j == len(piezas) - 1
                sep = (" y " if ultimo else ", ") if unir == "coma" else (" y " if ultimo and self.rng.random() < 0.5 else " ")
                pedazos.append(("t", sep, i))
            pedazos += pieza
        return pedazos

    def _extra(self, reg: dict, i: int, plantilla: str) -> list[tuple]:
        partes = []
        if reg["mencion"]:
            partes.append(reg["mencion"])
        if reg["urgencia"] == "urgente" and not plantilla.startswith("{urg_ini}"):
            partes.append(self.rng.choice(URGENTE))
        elif reg["urgencia"] == "espera":
            partes.append(self.rng.choice(ESPERA))
        return [("t", ", " + ", ".join(partes), i)] if partes else []

    def _llenar(self, plantilla: str, reg: dict, i: int, estilo: str, cortesia: bool = True) -> list[tuple]:
        pedazos = []
        for literal, campo in re.findall(r"([^{]*)(?:\{(\w+)\})?", plantilla):
            if literal:
                pedazos.append(("t", literal, i))
            if not campo:
                continue
            if campo == "saludo":
                if cortesia and self.rng.random() < 0.75:
                    pedazos.append(("t", self.rng.choice(SALUDOS), i))
            elif campo == "despedida":
                if cortesia and self.rng.random() < 0.50:
                    pedazos.append(("t", self.rng.choice(DESPEDIDAS), i))
            elif campo == "lugar":
                pedazos += self._lugar_pedazos(reg["lugar"], i, estilo)
            elif campo == "conteo":
                pedazos += self._conteo_pedazos(reg["conteo"], i, estilo)
            elif campo == "prods":
                pedazos += self._productos_pedazos(reg["productos"], i, estilo)
            elif campo == "extra":
                pedazos += self._extra(reg, i, plantilla)
        return pedazos

    # --- variantes ---

    def _sms(self, reg: dict) -> tuple[list[tuple], list[str]]:
        r, c = self.rng, reg["conteo"]
        etiquetas = []
        if c["unidad"] in ("ninos", "abuelos"):          # en el formato enseñado solo hay familias, personas y bebés
            c["unidad"] = "personas"
        unidad = {"familias": r.choice(["", "", "FAMILIAS"]), "personas": "PERSONAS", "bebes": "BEBES"}[c["unidad"]]
        if c["unidad"] == "familias" and not unidad:
            etiquetas.append("familias_implicitas")
        c["aprox"] = False
        pedazos = [("t", "PEDIDO ", 0), ("num", str(c["n"]), 0)]
        if unidad:
            pedazos += [("t", " ", 0), ("unidad", unidad, 0)]
        pedazos.append(("t", " ", 0))
        if reg["lugar"]["tipo"] == "vereda":
            pedazos.append(("pre", "VEREDA ", 0))
        pedazos.append(("lugar", reg["lugar"]["nombre"], 0))
        for q in reg["productos"]:
            if q["kg"]:
                pedazos += [("t", " ", 0), ("kg", str(q["kg"]), 0), ("t", " KILOS ", 0),
                            ("prod", q["producto"], 0)]
            else:
                pedazos += [("t", " ", 0), ("prod", q["producto"], 0)]
        reg["mencion"] = None
        if reg["urgencia"] == "urgente":
            pedazos.append(("t", " URGENTE", 0))
        elif reg["urgencia"] == "espera":
            reg["urgencia"] = "normal"                    # el formato enseñado no tiene «puede esperar»
        return pedazos, etiquetas

    def _homofono(self, palabra: str) -> str:
        """Un error de transcripción por sonido en una palabra, si la palabra lo admite."""
        reglas = []
        low = palabra.lower()
        if "z" in low:
            reglas.append(lambda s: s.replace("z", "s").replace("Z", "S"))
        if re.search(r"c[eiéí]", low):
            reglas.append(lambda s: re.sub(r"([cC])([eiéí])", lambda m: ("s" if m.group(1) == "c" else "S") + m.group(2), s, count=1))
        if "v" in low:
            reglas.append(lambda s: s.replace("v", "b", 1).replace("V", "B", 1))
        if "ll" in low:
            reglas.append(lambda s: s.replace("ll", "y", 1).replace("Ll", "Y", 1))
        if low.startswith("h") and len(low) > 3:
            reglas.append(lambda s: s[1:2].upper() + s[2:] if s[0].isupper() else s[1:])
        return self.rng.choice(reglas)(palabra) if reglas else palabra

    def _voz(self, pedazos: list[tuple], generos: dict[int, str]) -> tuple[list[tuple], list[str]]:
        r = self.rng
        etiquetas = set()
        salida = []
        for clase, texto, i in pedazos:
            if clase in ("num", "kg") and r.random() < 0.60:
                genero = generos.get(i, "m") if clase == "num" else "m"
                texto = en_palabras(int(texto), genero)
                etiquetas.add("numeros_en_palabras")
            elif clase in ("prod", "lugar"):
                palabras = texto.split(" ")
                for k, w in enumerate(palabras):
                    if len(w) > 3 and r.random() < (0.5 if clase == "prod" else 0.4):
                        nuevo = self._homofono(w)
                        if nuevo != w:
                            palabras[k] = nuevo
                            etiquetas.add("homofonos")
                texto = " ".join(palabras)
                if clase == "lugar" and r.random() < 0.45:
                    partes = texto.split(" ")
                    largas = [k for k, w in enumerate(partes) if len(w) >= 7]
                    if len(partes) >= 2 and (not largas or r.random() < 0.5):
                        k = r.randrange(len(partes) - 1)
                        partes[k:k + 2] = [partes[k] + partes[k + 1].lower()]
                        etiquetas.add("palabras_pegadas")
                    elif largas:
                        k = r.choice(largas)
                        w = partes[k]
                        corte = r.randint(3, len(w) - 3)
                        partes[k] = w[:corte] + " " + w[corte:]
                        etiquetas.add("palabras_partidas")
                    texto = " ".join(partes)
            elif clase == "t" and "necesitamos" in texto and r.random() < 0.5:
                texto = texto.replace("necesitamos", "nesesitamos")
                etiquetas.add("homofonos")
            salida.append((clase, texto, i))
        return salida, sorted(etiquetas)

    def _abreviar(self, pedazos: list[tuple]) -> tuple[list[tuple], list[str]]:
        salida, usadas = [], False
        for clase, texto, i in pedazos:
            if clase in ("t", "pre", "unidad"):
                for palabra, formas in ABREVIATURAS:
                    patron = rf"\b{re.escape(palabra)}\b"
                    if re.search(patron, texto) and self.rng.random() < 0.7:
                        texto = re.sub(patron, self.rng.choice(formas), texto)
                        usadas = True
            salida.append((clase, texto, i))
        return salida, ["abreviaturas"] if usadas else []

    def _render(self, pedazos: list[tuple], estilo: str) -> str:
        """Une los pedazos con el estilo de escritura; el lugar conserva su forma propia en limpio y voz."""
        partes = []
        for clase, texto, _ in pedazos:
            if estilo in ("limpio", "voz"):
                partes.append(texto)
            elif estilo == "mayusculas":
                partes.append(texto.upper())
            elif estilo == "sms":
                partes.append(sin_tildes(texto).upper() if self._sms_mayus else sin_tildes(texto).lower())
            else:
                partes.append(sin_tildes(texto).lower())
        texto = "".join(partes)
        texto = re.sub(r"\s+", " ", texto).strip()
        texto = re.sub(r"\s+([,.;:])", r"\1", texto)
        if estilo in ("limpio", "voz"):
            texto = _cap(texto)
            if not texto.endswith((".", "!", "?")):
                texto += "."
        if estilo == "mayusculas" and self._mayus_sin_tildes:
            texto = sin_tildes(texto)
        if estilo in ("sin_tildes", "abreviaturas") and self.rng.random() < 0.5:
            texto = texto.replace(",", "")
        return texto

    # --- oro ---

    @staticmethod
    def _oro_pedido(reg: dict, pedazos: list[tuple], i: int, con_lugar=True, con_conteo=True, con_prods=True) -> dict:
        lugar_texto = " ".join(texto for clase, texto, j in pedazos if clase == "lugar" and j == i)
        c = reg["conteo"]
        campo = UNIDADES[c["unidad"]][0]
        vulnerable = (con_conteo and c["unidad"] in VULNERABLES) or bool(reg["mencion"])
        urgencia = 3 if reg["urgencia"] == "urgente" or vulnerable else 1 if reg["urgencia"] == "espera" else 2
        return {
            "lugar_texto": plano(lugar_texto) if con_lugar else None,
            "lugar_nombre": reg["lugar"]["nombre"] if con_lugar else None,
            "lugar_tipo": reg["lugar"]["tipo"] if con_lugar else None,
            "lugar_ambiguo": None,
            "familias": c["n"] if con_conteo and campo == "familias" else None,
            "personas": c["n"] if con_conteo and campo == "personas" else None,
            "bebes": c["n"] if con_conteo and campo == "bebes" else None,
            "productos": [dict(q) for q in reg["productos"]] if con_prods else [],
            "urgencia": urgencia,
        }

    def mensaje(self, k: int, variante: str, sub: str | None = None) -> dict:
        r = self.rng
        estilo = {"dos_pedidos": "sin_tildes", "faltan_datos": "sin_tildes"}.get(variante, variante)
        self._sms_mayus = r.random() < 0.7
        self._mayus_sin_tildes = r.random() < 0.6
        etiquetas = {variante}
        faltan: list[str] = []
        regs = [self.registro(permitir_kilos=variante != "faltan_datos")]
        if variante == "sms":
            pedazos, extra = self._sms(regs[0])
            etiquetas |= set(extra)
        elif variante == "dos_pedidos":
            regs.append(self.registro(permitir_kilos=False))
            while regs[1]["lugar"]["nombre"] == regs[0]["lugar"]["nombre"]:
                regs[1]["lugar"] = self.lugar()
            regs[1]["urgencia"] = regs[0]["urgencia"]
            regs[0]["mencion"] = regs[1]["mencion"] = None    # una mención suelta no diría a cuál de los dos
            if regs[0]["urgencia"] == "espera":
                for reg in regs:
                    if reg["conteo"]["unidad"] in VULNERABLES:
                        reg["conteo"]["unidad"] = "familias"
            p1 = self._llenar(r.choice(PEDIDO_CORTO), regs[0], 0, estilo)
            p2 = self._llenar(r.choice(PEDIDO_CORTO), regs[1], 1, estilo)
            saludo = [("t", r.choice(SALUDOS), 0)] if r.random() < 0.6 else []
            pedazos = saludo + p1 + [("t", r.choice(SEPARADORES), 0)] + p2 + self._extra(regs[0], 0, "")
            if r.random() < 0.4:
                pedazos.append(("t", r.choice(DESPEDIDAS), 0))
        else:
            if variante == "faltan_datos":
                plantillas = {"lugar": SIN_LUGAR, "conteo": SIN_CONTEO, "productos": SIN_PRODUCTOS}[sub]
                faltan = [sub]
                etiquetas.add(f"sin_{sub}")
                if sub == "conteo" and regs[0]["conteo"]["unidad"] in VULNERABLES:
                    regs[0]["conteo"]["unidad"] = "familias"
            else:
                plantillas = COMPLETAS
            idx = r.randrange(len(plantillas))
            plantilla = plantillas[idx]
            if variante != "faltan_datos" and idx not in CON_KILOS:
                for q in regs[0]["productos"]:
                    q["kg"] = None
            if regs[0]["urgencia"] == "urgente" and variante != "faltan_datos" and r.random() < 0.3:
                plantilla = "{urg_ini}" + plantilla.replace("{saludo}", "")
            pedazos = self._llenar(plantilla, regs[0], 0, estilo)
            if plantilla.startswith("{urg_ini}"):
                pedazos.insert(0, ("t", r.choice(["URGENTE ", "urgente: ", "Urgente, "]), 0))
        if estilo == "voz":
            generos = {i: UNIDADES[reg["conteo"]["unidad"]][1] for i, reg in enumerate(regs)}
            pedazos, extra = self._voz(pedazos, generos)
            etiquetas |= set(extra)
        elif estilo == "abreviaturas":
            pedazos, extra = self._abreviar(pedazos)
            etiquetas |= set(extra)
        texto = self._render(pedazos, estilo)
        con = {"con_lugar": "lugar" not in faltan, "con_conteo": "conteo" not in faltan,
               "con_prods": "productos" not in faltan}
        oro_pedidos = [self._oro_pedido(reg, pedazos, i, **con) for i, reg in enumerate(regs)]
        for i, reg in enumerate(regs):
            etiquetas.add({"familias": "conteo_familias", "personas": "conteo_personas", "ninos": "conteo_ninos",
                           "abuelos": "conteo_mayores", "bebes": "conteo_bebes"}[reg["conteo"]["unidad"]]
                          if con["con_conteo"] else "conteo_ausente")
            if any(q["kg"] for q in reg["productos"]) and con["con_prods"]:
                etiquetas.add("kilos")
            if reg["urgencia"] == "urgente":
                etiquetas.add("urgente")
            if reg["urgencia"] == "espera":
                etiquetas.add("espera")
            if reg["mencion"]:
                etiquetas.add("mencion_vulnerable")
            if reg["conteo"]["aprox"] and con["con_conteo"] and variante != "sms":
                etiquetas.add("conteo_aproximado")
            etiquetas.add(f"lugar_{reg['lugar']['tipo']}" if con["con_lugar"] else "lugar_ausente")
        return {"id": f"g{k:03d}", "origen": "generado", "variante": variante, "etiquetas": sorted(etiquetas),
                "texto": texto,
                "oro": {"tipo": "pedido", "pedidos": oro_pedidos, "cierre": None, "entregado": None},
                "faltan": faltan}

    def todos(self) -> list[dict]:
        tareas = []
        for variante, n in PLAN:
            if variante == "faltan_datos":
                tareas += [(variante, sub) for sub in ("lugar", "conteo", "productos") for _ in range(n // 3)]
            else:
                tareas += [(variante, None)] * n
        assert len(tareas) == N, len(tareas)
        self.rng.shuffle(tareas)
        return [self.mensaje(k, v, s) for k, (v, s) in enumerate(tareas, 1)]


def linea(registro: dict) -> str:
    """Una línea JSON con orden de claves fijo: la forma congelada del conjunto."""
    return json.dumps(registro, ensure_ascii=False) + "\n"


def generar(semilla: int = SEMILLA) -> list[dict]:
    return Generador(semilla).todos()


def leer_dificiles(ruta: Path = DIFICILES) -> list[dict]:
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def texto_generado(semilla: int = SEMILLA) -> str:
    return "".join(linea(r) for r in generar(semilla))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    ap.add_argument("--verificar", action="store_true", help="compara la parte generada con conjunto.jsonl")
    a = ap.parse_args(argv)
    generado = texto_generado(a.semilla)
    if a.verificar:
        congelado = CONJUNTO.read_text(encoding="utf-8")
        parte = "".join(congelado.splitlines(keepends=True)[:N])
        igual = parte.encode("utf-8") == generado.encode("utf-8")
        print("la parte generada coincide byte a byte" if igual else "NO coincide con conjunto.jsonl")
        return 0 if igual else 1
    dificiles = leer_dificiles()
    with open(CONJUNTO, "w", encoding="utf-8", newline="\n") as f:
        f.write(generado)
        for d in dificiles:
            f.write(linea({**d, "origen": "a_mano"}))
    print(f"{CONJUNTO.relative_to(RAIZ)}: {N} generados (semilla {a.semilla}) y {len(dificiles)} a mano")
    return 0


if __name__ == "__main__":
    sys.exit(main())
