"""Mide el lector de pedidos por texto, campo por campo, sobre el conjunto congelado (conjunto.jsonl).

    DESPACHOX_SIN_RED=1 PYTHONPATH=. python -m evaluacion.lector.evaluar

Qué lector se mide: el camino del bot sin red. Con DESPACHOX_SIN_RED=1, entrada/flujo.py (Mesa.leer)
limpia el texto con entrada/privacidad.limpiar y lo lee con entrada/sms.leer_sms, las reglas sin modelo.
El lugar que sale se pasa por lugares.resolver sin modelo (elegir=None) con los tipos que usa el bot
para pedidos (barrio, punto, sitio, vereda) o para cierres (vía, sitio), sobre una base temporal con
la semilla de datos/semilla/. Nada llama al modelo ni a la red.

Escribe, junto a este archivo:
    resultados.json   todas las métricas, con n, aciertos e intervalo de Wilson al 95 %
    lecturas.jsonl    la lectura de cada mensaje, su calificación y sus errores
    tablas.md         las tablas que copia RESULTADOS.md

Reglas de calificación (las mismas para el lector con modelo, ver medir_modelo.py):
- tipo: pedido, cierre, entrega (código ENTREGADO) u otro. Una lectura fallida (fallo=True) es «otro»,
  porque el bot la guarda cruda para el despachador.
- Dos pedidos en un mensaje: el esquema de Extraccion tiene un solo pedido, así que la detección se
  mide pero no puede pasar de cero. Los campos se califican contra el pedido de oro que mejor
  empareja con la lectura; el otro pedido queda perdido.
- lugar extraído: el núcleo del texto (sin artículos ni «barrio», «vereda») igual al del oro.
- lugar resuelto: clases del banco de frases de lugares/tests: acierto seguro, por opciones, no sé y
  error seguro. Un lugar con el mismo punto de entrega que el del oro cuenta como el mismo lugar.
- conteo: familias, personas y bebés, cada uno igual al oro; el conteo exacto exige los tres.
- productos: conjunto de nombres de bodega; precisión, exhaustividad y F1 sumando todos los mensajes.
- cantidades: kilos de cada producto que el oro trae con kilos.
- abstención: si al oro le falta el lugar, el conteo o los productos, el lector debe dejarlo vacío.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import statistics
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import lugares  # noqa: E402
from datos import db  # noqa: E402
from entrada import raciones  # noqa: E402
from entrada.flujo import TIPOS  # noqa: E402
from entrada.privacidad import limpiar  # noqa: E402
from entrada.sms import leer_sms  # noqa: E402
from lugares import normalizar  # noqa: E402

CONJUNTO = AQUI / "conjunto.jsonl"
Z95 = 1.959963984540054
# Palabras que acompañan al nombre y no lo distinguen («el barrio la enea» = «la enea»).
RELLENO_LUGAR = {"el", "la", "los", "las", "de", "del", "en", "barrio", "b", "bo", "brr", "sector", "vereda",
                 "comuna"}
CLASES_LUGAR = ["acierto seguro", "por opciones", "no sé", "error seguro", "sin lugar"]


# ---------- utilidades ----------

def wilson(k: int, n: int, z: float = Z95) -> tuple[float | None, float | None]:
    """Intervalo de confianza de Wilson para una proporción k/n."""
    if n == 0:
        return None, None
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0.0, centro - margen), min(1.0, centro + margen)


def nucleo(texto: str | None) -> str:
    return " ".join(p for p in normalizar(texto).split() if p not in RELLENO_LUGAR)


def clave_producto(nombre: str) -> str:
    """Nombre de bodega comparable: sinónimos de raciones, sin tildes y sin plural."""
    p = normalizar(raciones.canonico(normalizar(nombre)))
    p = normalizar(raciones.canonico(p))
    return p[:-1] if p.endswith("s") and len(p) > 4 else p


def cargar_conjunto(ruta: Path = CONJUNTO) -> list[dict]:
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]


def base_de_lugares(carpeta: Path | None = None):
    """Base temporal con los puntos de la semilla y el nomenclátor cargado, como en entrada/pruebas."""
    carpeta = Path(carpeta or tempfile.mkdtemp(prefix="eval-lector-"))
    con = db.conectar(carpeta / "eval.db")
    with open(db.RAIZ / "semilla" / "puntos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            con.execute("INSERT OR IGNORE INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                        (r["id"], r["nombre"], r["barrio"], r["comuna"], r["lat"], r["lon"], r["critico"]))
    con.commit()
    lugares.cargar_semilla(con)
    return con


class Lugares:
    """Resuelve con lugares.resolver sin modelo y responde si dos nombres son el mismo punto de entrega."""

    def __init__(self, con):
        self.con = con
        self.puntos: dict[str, set[int]] = defaultdict(set)
        for r in con.execute("SELECT nombre, punto_id FROM lugares WHERE punto_id IS NOT NULL"):
            self.puntos[r["nombre"]].add(r["punto_id"])
        self._cache: dict[tuple, object] = {}

    def resolver(self, texto: str, tabla: str = "pedidos"):
        k = (texto, tabla)
        if k not in self._cache:
            self._cache[k] = lugares.resolver(self.con, texto, tipos=TIPOS[tabla], elegir=None)
        return self._cache[k]

    def mismo(self, candidato, nombre: str) -> bool:
        if candidato.nombre == nombre:
            return True
        return candidato.punto_id is not None and candidato.punto_id in self.puntos.get(nombre, set())

    def clase(self, dicho: str | None, oro: dict, tabla: str = "pedidos") -> str:
        """Clase del lugar leído frente al oro de un pedido o de un cierre."""
        if oro.get("lugar_texto") is None:                     # al oro le falta el lugar a propósito
            if not dicho:
                return "se abstiene"
            return "inventa con seguridad" if self.resolver(dicho, tabla).seguro else "inventa sin compromiso"
        if not dicho:
            return "sin lugar"
        r = self.resolver(dicho, tabla)
        nombre = oro.get("lugar_nombre")
        if nombre is None:                                      # ambiguo o fuera del nomenclátor
            if r.seguro:
                return "error seguro"
            ambiguo = oro.get("lugar_ambiguo") or []
            return "por opciones" if any(c.nombre in ambiguo for c in r.candidatos) else "no sé"
        if r.seguro:
            return "acierto seguro" if self.mismo(r.elegido, nombre) else "error seguro"
        if any(self.mismo(c, nombre) for c in r.candidatos):
            return "por opciones"
        return "no sé"


# ---------- lectura ----------

def lectura_reglas(texto: str):
    """Lo que hace Mesa.leer con DESPACHOX_SIN_RED=1."""
    return leer_sms(limpiar(texto))


def a_dict(x) -> dict:
    """La Extraccion como datos simples, con el tipo de cuatro valores que se califica."""
    tipo = "entrega" if x.entregado else ("otro" if x.fallo else x.tipo)
    return {"tipo": tipo, "fallo": bool(x.fallo), "entregado": x.entregado,
            "pedido": x.pedido.model_dump() if x.pedido is not None else None,
            "cierre": x.cierre.model_dump() if x.cierre is not None else None}


# ---------- calificación de un mensaje ----------

VACIO = {"lugar": None, "familias": None, "personas": None, "bebes": None, "productos": [], "urgencia": None}


def _conteo(p: dict) -> tuple:
    return p.get("familias"), p.get("personas"), p.get("bebes")


def _emparejar(lect_ped: dict, oros: list[dict], L: Lugares) -> int:
    """Índice del pedido de oro que mejor empareja con el pedido leído (el primero si empatan)."""
    def puntaje(o):
        s = 0.0
        if o.get("lugar_texto") is not None and lect_ped.get("lugar"):
            s += 2 * (L.clase(lect_ped["lugar"], o) in ("acierto seguro", "por opciones"))
            s += nucleo(lect_ped["lugar"]) == nucleo(o["lugar_texto"])
        s += any(v is not None and v == w for v, w in zip(_conteo(lect_ped), _conteo(o)))
        dichos = {clave_producto(q["producto"]) for q in lect_ped.get("productos") or []}
        s += 0.1 * len(dichos & {clave_producto(q["producto"]) for q in o["productos"]})
        return s
    puntajes = [puntaje(o) for o in oros]
    return puntajes.index(max(puntajes))


def calificar(reg: dict, lect: dict, L: Lugares) -> dict:
    """Calificación de un mensaje: {campo: True/False} solo para los campos que aplican, más
    los conteos de productos y la lista de errores legibles."""
    oro = reg["oro"]
    c: dict = {}
    errores: list[str] = []
    prod = {"vp": 0, "fp": 0, "fn": 0}
    c["tipo"] = lect["tipo"] == oro["tipo"]
    if not c["tipo"]:
        errores.append(f"tipo: {lect['tipo']}{' (fallo)' if lect['fallo'] else ''} en vez de {oro['tipo']}")
    if oro["tipo"] in ("otro", "entrega", "cierre") and lect["tipo"] in ("pedido", "cierre") and not c["tipo"]:
        c["falso_reporte"] = True               # crea un pedido o un cierre que nadie hizo
    if oro["tipo"] == "entrega":
        c["codigo_entrega"] = lect["entregado"] == oro["entregado"]
        if not c["codigo_entrega"]:
            errores.append(f"código: {lect['entregado']} en vez de {oro['entregado']}")
    if oro.get("cierre"):
        oc, lc = oro["cierre"], lect.get("cierre")
        c["cierre_detectado"] = lc is not None
        if lc is None:
            errores.append("cierre: no lo vio")
        else:
            c["cierre_lugar_extraido"] = nucleo(lc.get("lugar")) == nucleo(oc["lugar_texto"])
            if oc.get("lugar_nombre"):
                clase = L.clase(lc.get("lugar"), oc, "cierres")
                c["cierre_lugar_resuelto"] = clase == "acierto seguro"
                if not c["cierre_lugar_resuelto"]:
                    errores.append(f"lugar del cierre: {lc.get('lugar')!r} ({clase})")
            elif not c["cierre_lugar_extraido"]:
                errores.append(f"lugar del cierre: {lc.get('lugar')!r} en vez de {oc['lugar_texto']!r}")
            if oc.get("tipos_bloqueados") is not None:
                c["cierre_bloqueados"] = sorted(lc["tipos_bloqueados"]) == sorted(oc["tipos_bloqueados"])
                if not c["cierre_bloqueados"]:
                    errores.append(f"bloqueados: {lc['tipos_bloqueados']} en vez de {oc['tipos_bloqueados']}")
    clase_lugar = None
    if oro["pedidos"]:
        p = dict(VACIO, **(lect["pedido"] or {})) if lect["pedido"] else dict(VACIO)
        i = _emparejar(p, oro["pedidos"], L) if len(oro["pedidos"]) > 1 else 0
        o = oro["pedidos"][i]
        if len(oro["pedidos"]) > 1:
            c["dos_pedidos_detectados"] = False          # Extraccion trae un solo pedido
            errores.append(f"dos pedidos: se leyó uno (el {i + 1}) y el otro se perdió")
        # lugar
        clase_lugar = L.clase(p["lugar"], o)
        if o["lugar_texto"] is not None:
            c["lugar_extraido"] = bool(p["lugar"]) and nucleo(p["lugar"]) == nucleo(o["lugar_texto"])
            if o.get("lugar_nombre"):
                c["lugar_acierto_seguro"] = clase_lugar == "acierto seguro"
                c["lugar_correcto_o_en_opciones"] = clase_lugar in ("acierto seguro", "por opciones")
            else:
                c["lugar_dudoso_sin_compromiso"] = clase_lugar != "error seguro"
            if o.get("lugar_nombre"):
                c["techo_lugar"] = L.clase(o["lugar_texto"], o) == "acierto seguro"
            if not c["lugar_extraido"]:
                errores.append(f"lugar: {p['lugar']!r} en vez de {o['lugar_texto']!r} ({clase_lugar})")
            elif o.get("lugar_nombre") and clase_lugar != "acierto seguro" or clase_lugar == "error seguro":
                errores.append(f"lugar resuelto: {clase_lugar} para {p['lugar']!r}")
        else:
            c["abstencion_lugar"] = not p["lugar"]
            if p["lugar"]:
                errores.append(f"lugar inventado: {p['lugar']!r} ({clase_lugar})")
        c["sin_error_seguro_de_lugar"] = clase_lugar not in ("error seguro", "inventa con seguridad")
        # conteo
        for campo in ("familias", "personas", "bebes"):
            if o[campo] is not None:
                c[campo] = p[campo] == o[campo]
        if any(v is not None for v in _conteo(o)):
            c["conteo_exacto"] = _conteo(p) == _conteo(o)
            if o["personas"] is not None and o["familias"] is None:
                c["personas_como_familias"] = p["familias"] == o["personas"]      # un error: se cuenta cuántas veces pasa
        else:
            c["abstencion_conteo"] = all(v is None for v in _conteo(p))
        if _conteo(p) != _conteo(o):
            errores.append(f"conteo (familias, personas, bebés): {_conteo(p)} en vez de {_conteo(o)}")
        # urgencia
        c["urgencia"] = p["urgencia"] == o["urgencia"]
        if not c["urgencia"]:
            errores.append(f"urgencia: {p['urgencia']} en vez de {o['urgencia']}")
        # productos
        dichos = {clave_producto(q["producto"]): q.get("kg") for q in p["productos"]}
        oros = {clave_producto(q["producto"]): q.get("kg") for q in o["productos"]}
        prod = {"vp": len(dichos.keys() & oros.keys()), "fp": len(dichos.keys() - oros.keys()),
                "fn": len(oros.keys() - dichos.keys())}
        if oros:
            c["productos_exactos"] = dichos.keys() == oros.keys()
        else:
            c["abstencion_productos"] = not dichos
        if dichos.keys() != oros.keys():
            errores.append(f"productos: sobran {sorted(dichos.keys() - oros.keys())}, "
                           f"faltan {sorted(oros.keys() - dichos.keys())}")
        kilos_bien = []
        for k, kg in oros.items():
            if kg is not None:
                bien = k in dichos and dichos[k] is not None and abs(dichos[k] - kg) < 0.01
                kilos_bien.append(bien)
                if not bien:
                    errores.append(f"kilos de {k}: {dichos.get(k)} en vez de {kg}")
            elif k in dichos:
                c.setdefault("_kg_abst", []).append(dichos[k] is None)
                if dichos[k] is not None:
                    errores.append(f"kilos de {k} inventados: {dichos[k]}")
        if kilos_bien:
            c["_kg"] = kilos_bien
        # el mensaje entero, sin corrección humana
        lugar_ok = (clase_lugar == "acierto seguro" if o.get("lugar_nombre")
                    else clase_lugar in ("se abstiene",) if o["lugar_texto"] is None
                    else clase_lugar != "error seguro")
        c["mensaje_sin_errores"] = bool(
            c["tipo"] and lugar_ok and _conteo(p) == _conteo(o) and dichos.keys() == oros.keys()
            and all(kilos_bien) and all(c.get("_kg_abst", [])) and c["urgencia"] and len(oro["pedidos"]) == 1
            and (not oro.get("cierre") or c.get("cierre_detectado")))
    elif oro["tipo"] in ("otro", "entrega", "cierre"):
        lugar_cierre_ok = c.get("cierre_lugar_resuelto", c.get("cierre_lugar_extraido", True))
        c["mensaje_sin_errores"] = bool(c["tipo"] and c.get("codigo_entrega", True) and lugar_cierre_ok
                                        and c.get("cierre_bloqueados", True))
    return {"campos": c, "productos": prod, "clase_lugar": clase_lugar, "errores": errores}


# ---------- agregación ----------

ORDEN = [  # (campo, nombre en la tabla)
    ("tipo", "Tipo de mensaje"),
    ("lugar_extraido", "Lugar extraído (núcleo igual)"),
    ("lugar_acierto_seguro", "Lugar resuelto: acierto seguro"),
    ("lugar_correcto_o_en_opciones", "Lugar resuelto: seguro o entre las opciones"),
    ("sin_error_seguro_de_lugar", "Sin error seguro de lugar"),
    ("lugar_dudoso_sin_compromiso", "Lugar ambiguo o desconocido: no se compromete"),
    ("techo_lugar", "Techo: el lugar del oro, resuelto tal como se escribió"),
    ("familias", "Familias (cuando el oro las trae)"),
    ("personas", "Personas (cuando el oro las trae)"),
    ("bebes", "Bebés (cuando el oro los trae)"),
    ("conteo_exacto", "Conteo exacto (familias, personas y bebés)"),
    ("personas_como_familias", "Error: personas leídas como familias"),
    ("productos_exactos", "Productos: conjunto exacto"),
    ("kg", "Cantidades en kilos"),
    ("urgencia", "Urgencia"),
    ("dos_pedidos_detectados", "Dos pedidos detectados"),
    ("abstencion_lugar", "Abstención: lugar que falta"),
    ("abstencion_conteo", "Abstención: conteo que falta"),
    ("abstencion_productos", "Abstención: productos que faltan"),
    ("kg_abstencion", "Abstención: kilos que el mensaje no dice"),
    ("codigo_entrega", "Código de entrega"),
    ("cierre_detectado", "Cierre detectado"),
    ("cierre_lugar_extraido", "Cierre: lugar extraído"),
    ("cierre_lugar_resuelto", "Cierre: lugar resuelto"),
    ("cierre_bloqueados", "Cierre: vehículos bloqueados"),
    ("mensaje_sin_errores", "Mensaje sin ningún error"),
]


def agregar(calificaciones: list[dict]) -> dict:
    """{campo: {n, aciertos, proporcion, ic95}} más productos (precisión, exhaustividad, F1)."""
    cuenta: dict[str, list[bool]] = defaultdict(list)
    vp = fp = fn = 0
    clases = Counter()
    falsos = 0
    for cal in calificaciones:
        for k, v in cal["campos"].items():
            if k == "_kg":
                cuenta["kg"] += v
            elif k == "_kg_abst":
                cuenta["kg_abstencion"] += v
            elif k == "falso_reporte":
                falsos += 1
            else:
                cuenta[k].append(bool(v))
        vp, fp, fn = vp + cal["productos"]["vp"], fp + cal["productos"]["fp"], fn + cal["productos"]["fn"]
        if cal["clase_lugar"]:
            clases[cal["clase_lugar"]] += 1
    salida = {}
    for k, vals in cuenta.items():
        n, a = len(vals), sum(vals)
        lo, hi = wilson(a, n)
        salida[k] = {"n": n, "aciertos": a, "proporcion": a / n if n else None, "ic95": [lo, hi]}
    prec = vp / (vp + fp) if vp + fp else None
    exh = vp / (vp + fn) if vp + fn else None
    f1 = 2 * prec * exh / (prec + exh) if prec and exh else (0.0 if prec is not None and exh is not None else None)
    salida["productos"] = {"vp": vp, "fp": fp, "fn": fn, "precision": prec, "precision_ic95": list(wilson(vp, vp + fp)),
                           "exhaustividad": exh, "exhaustividad_ic95": list(wilson(vp, vp + fn)), "f1": f1}
    salida["clases_lugar"] = dict(clases)
    salida["falsos_reportes"] = falsos
    salida["mensajes"] = len(calificaciones)
    return salida


def grupos(conjunto: list[dict]) -> dict[str, list[int]]:
    """Subconjuntos que se reportan: generados, difíciles, cada variante y cada etiqueta de los generados."""
    g: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(conjunto):
        g["todos"].append(i)
        g["generados" if r["origen"] == "generado" else "dificiles"].append(i)
        if r["origen"] == "generado":
            g[f"variante:{r['variante']}"].append(i)
            for e in r["etiquetas"]:
                if e != r["variante"]:
                    g[f"etiqueta:{e}"].append(i)
        else:
            g[f"dificil:{r['variante']}"].append(i)
    return dict(g)


# ---------- tablas ----------

def _pct(x: float | None) -> str:
    return "" if x is None else f"{100 * x:.1f}".replace(".", ",")


def _celda(m: dict | None) -> str:
    if not m or not m["n"]:
        return "no aplica"
    lo, hi = m["ic95"]
    return f"{m['aciertos']}/{m['n']} ({_pct(m['proporcion'])} %; {_pct(lo)} a {_pct(hi)})"


def tabla_campos(metricas: dict[str, dict], columnas: list[str], titulos: list[str]) -> str:
    filas = ["| Campo | " + " | ".join(titulos) + " |", "|---|" + "---|" * len(columnas)]
    for campo, nombre in ORDEN:
        celdas = [_celda(metricas[c].get(campo)) for c in columnas]
        if all(x == "no aplica" for x in celdas):
            continue
        filas.append(f"| {nombre} | " + " | ".join(celdas) + " |")
    for c_prod, nombre in (("precision", "Productos: precisión"), ("exhaustividad", "Productos: exhaustividad")):
        celdas = []
        for c in columnas:
            p = metricas[c]["productos"]
            k = p["vp"]
            n = p["vp"] + (p["fp"] if c_prod == "precision" else p["fn"])
            lo, hi = p[f"{c_prod}_ic95"]
            celdas.append(f"{k}/{n} ({_pct(p[c_prod])} %; {_pct(lo)} a {_pct(hi)})" if n else "no aplica")
        filas.append(f"| {nombre} | " + " | ".join(celdas) + " |")
    filas.append("| Productos: F1 | " + " | ".join(
        (_pct(metricas[c]["productos"]["f1"]) + " %") if metricas[c]["productos"]["f1"] is not None else "no aplica"
        for c in columnas) + " |")
    return "\n".join(filas)


def tabla_variantes(metricas: dict[str, dict], claves: list[str], campos: list[tuple[str, str]]) -> str:
    filas = ["| Variante | n | " + " | ".join(t for _, t in campos) + " |", "|---|---|" + "---|" * len(campos)]
    for k in claves:
        m = metricas[k]
        celdas = []
        for campo, _ in campos:
            if campo == "f1":
                f1 = m["productos"]["f1"]
                celdas.append(_pct(f1) + " %" if f1 is not None else "no aplica")
            else:
                x = m.get(campo)
                celdas.append(f"{x['aciertos']}/{x['n']} ({_pct(x['proporcion'])} %)" if x and x["n"] else "no aplica")
        filas.append(f"| {k.split(':', 1)[1]} | {m['mensajes']} | " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def tablas_md(res: dict) -> str:
    m = res["metricas"]
    partes = [f"Lector: {res['lector']}. Conjunto: {res['conjunto']['n']} mensajes, sha256 "
              f"`{res['conjunto']['sha256'][:16]}…`. Corrida: {res['fecha']}. Celdas: aciertos/n "
              "(porcentaje; intervalo de Wilson al 95 %).",
              "## Campo por campo"]
    cols = [c for c in ("generados", "dificiles") if c in m]
    titulos = [f"{m[c]['mensajes']} {'generados' if c == 'generados' else 'difíciles'}" for c in cols]
    partes.append(tabla_campos(m, cols, titulos))
    cl = ["acierto seguro", "por opciones", "no sé", "error seguro", "sin lugar", "se abstiene",
          "inventa sin compromiso", "inventa con seguridad"]
    partes.append("## Lugar: de lo leído a lo resuelto\n\n| Clase | " + " | ".join(titulos) + " |\n|---|"
                  + "---|" * len(cols) + "\n" + "\n".join(
                      f"| {c} | " + " | ".join(str(m[k]['clases_lugar'].get(c, 0)) for k in cols) + " |" for c in cl))
    t = m.get("generados", {}).get("techo_lugar")
    if t:
        partes.append(f"Techo del nomenclátor: si el lector copiara el lugar tal como va en el mensaje, el "
                      f"resolvedor daría acierto seguro en {_celda(t)} de los mismos pedidos generados. La diferencia "
                      f"con el acierto seguro del lector es lo que pierde el lector; el resto lo pierde el nomenclátor.")
    campos = [("tipo", "Tipo"), ("lugar_extraido", "Lugar extraído"), ("lugar_acierto_seguro", "Lugar resuelto"),
              ("conteo_exacto", "Conteo exacto"), ("productos_exactos", "Productos exactos"), ("f1", "F1 productos"),
              ("kg", "Kilos"), ("urgencia", "Urgencia"), ("mensaje_sin_errores", "Sin errores")]
    variantes = [k for k in m if k.startswith("variante:")]
    orden_v = ["sms", "limpio", "sin_tildes", "mayusculas", "abreviaturas", "voz", "dos_pedidos", "faltan_datos"]
    variantes.sort(key=lambda k: orden_v.index(k.split(":")[1]) if k.split(":")[1] in orden_v else 99)
    partes.append("## Por variante (generados)\n\n" + tabla_variantes(m, variantes, campos))
    etiquetas = sorted(k for k in m if k.startswith("etiqueta:"))
    partes.append("## Por etiqueta (generados; un mensaje puede tener varias)\n\n" + tabla_variantes(m, etiquetas, campos))
    abst = [("abstencion_lugar", "Abst. lugar"), ("abstencion_conteo", "Abst. conteo"),
            ("abstencion_productos", "Abst. productos")]
    partes.append("## Abstención en los que les falta un dato (generados)\n\n" + tabla_variantes(
        m, [k for k in ("etiqueta:sin_lugar", "etiqueta:sin_conteo", "etiqueta:sin_productos") if k in m], abst))
    dif = sorted(k for k in m if k.startswith("dificil:"))
    partes.append("## Difíciles por tipo de caso\n\n" + tabla_variantes(
        m, dif, [("tipo", "Tipo"), ("lugar_extraido", "Lugar extraído"), ("conteo_exacto", "Conteo"),
                 ("productos_exactos", "Productos"), ("urgencia", "Urgencia"), ("mensaje_sin_errores", "Sin errores")]))
    tp = res["tiempos_ms"]

    def ms(x, d=2):
        return f"{x:.{d}f}".replace(".", ",")
    lec, lug = tp["lectura"], tp["lugar"]
    partes.append(f"## Tiempo por mensaje\n\nMedido en {res['maquina']}, sin red. Lectura (limpiar y leer_sms), "
                  f"{lec['n']} mensajes: mediana {ms(lec['mediana'], 3)} ms, p95 {ms(lec['p95'], 3)} ms y máximo "
                  f"{ms(lec['max'], 3)} ms. Resolver el lugar sin modelo, {lug['n']} lugares: mediana {ms(lug['mediana'])} ms, "
                  f"p95 {ms(lug['p95'])} ms y máximo {ms(lug['max'])} ms.")
    return "\n\n".join(partes) + "\n"


# ---------- corrida ----------

def _resumen_tiempos(xs: list[float]) -> dict:
    xs = sorted(xs)
    return {"n": len(xs), "mediana": statistics.median(xs), "p95": xs[min(len(xs) - 1, math.ceil(0.95 * len(xs)) - 1)],
            "max": xs[-1], "total": sum(xs)}


def evaluar(conjunto: list[dict], leer=lectura_reglas, con=None, medir_tiempo: bool = True,
            calentar: bool = True) -> dict:
    """Lee y califica cada mensaje. `leer` recibe el texto y devuelve una Extraccion. Ninguna llamada
    de aquí usa la red: el lector por reglas no la usa y el lugar se resuelve con elegir=None."""
    con = con or base_de_lugares()
    L = Lugares(con)
    if calentar:
        leer("PEDIDO 1 SAN JOSE ARROZ")                # calienta importaciones antes de medir
    lecturas, cals, t_lectura, t_lugar = [], [], [], []
    for reg in conjunto:
        t0 = time.perf_counter()
        x = leer(reg["texto"])
        t1 = time.perf_counter()
        lect = a_dict(x)
        dicho = (lect["pedido"] or {}).get("lugar") or (lect["cierre"] or {}).get("lugar")
        t2 = time.perf_counter()
        if dicho:                                       # sin caché, para medir lo que tarda de verdad
            lugares.resolver(con, dicho, tipos=TIPOS["pedidos" if lect["pedido"] else "cierres"], elegir=None)
        t3 = time.perf_counter()
        cal = calificar(reg, lect, L)
        t_lectura.append(1000 * (t1 - t0))
        if dicho:
            t_lugar.append(1000 * (t3 - t2))
        lecturas.append(lect)
        cals.append(cal)
    g = grupos(conjunto)
    metricas = {k: agregar([cals[i] for i in idx]) for k, idx in g.items()}
    res = {"metricas": metricas, "lecturas": lecturas, "calificaciones": cals}
    if medir_tiempo:
        res["tiempos_ms"] = {"lectura": _resumen_tiempos(t_lectura), "lugar": _resumen_tiempos(t_lugar or [0.0])}
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mide el lector por reglas sobre conjunto.jsonl")
    ap.add_argument("--conjunto", type=Path, default=CONJUNTO)
    ap.add_argument("--salida", type=Path, default=AQUI, help="carpeta para resultados.json, lecturas.jsonl y tablas.md")
    a = ap.parse_args(argv)
    os.environ["DESPACHOX_SIN_RED"] = "1"        # garantía para la corrida: nada de lugares/ llama al modelo
    conjunto = cargar_conjunto(a.conjunto)
    res = evaluar(conjunto)
    bruto = a.conjunto.read_bytes()
    res.update({
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "lector": "entrada.sms.leer_sms tras entrada.privacidad.limpiar (Mesa.leer con DESPACHOX_SIN_RED=1); "
                  "lugar con lugares.resolver, elegir=None",
        "maquina": f"{platform.system()} {platform.release()} {platform.machine()}, Python {platform.python_version()}",
        "conjunto": {"ruta": str(a.conjunto.relative_to(RAIZ)) if a.conjunto.is_relative_to(RAIZ) else str(a.conjunto),
                     "n": len(conjunto), "sha256": hashlib.sha256(bruto).hexdigest()},
    })
    a.salida.mkdir(parents=True, exist_ok=True)
    with open(a.salida / "lecturas.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for reg, lect, cal in zip(conjunto, res["lecturas"], res["calificaciones"]):
            f.write(json.dumps({"id": reg["id"], "origen": reg["origen"], "variante": reg["variante"],
                                "texto": reg["texto"], "lectura": lect,
                                "campos": {k: v for k, v in cal["campos"].items()},
                                "clase_lugar": cal["clase_lugar"], "errores": cal["errores"]},
                               ensure_ascii=False) + "\n")
    guardar = {k: v for k, v in res.items() if k not in ("lecturas", "calificaciones")}
    (a.salida / "resultados.json").write_text(json.dumps(guardar, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (a.salida / "tablas.md").write_text("# Tablas de la corrida (generadas por evaluar.py)\n\n" + tablas_md(res),
                                        encoding="utf-8")
    gen, dif = res["metricas"]["generados"], res["metricas"]["dificiles"]
    print(f"generados: sin errores {gen['mensaje_sin_errores']['aciertos']}/{gen['mensaje_sin_errores']['n']}, "
          f"lugar seguro {gen['lugar_acierto_seguro']['aciertos']}/{gen['lugar_acierto_seguro']['n']}, "
          f"F1 productos {gen['productos']['f1']:.3f}")
    print(f"difíciles: sin errores {dif['mensaje_sin_errores']['aciertos']}/{dif['mensaje_sin_errores']['n']}")
    print(f"escrito en {a.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
