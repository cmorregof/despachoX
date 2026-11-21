"""Hoja de ruta impresa: un PDF por vehículo del plan aprobado, con un QR por paquete.

Uso:
    python -m despacho.hoja                         # plan aprobado vigente
    python -m despacho.hoja --plan 12               # un plan aprobado concreto
    python -m despacho.hoja --plan 12 --salida hojas/

Para el tablero: `generar(con, plan_id) -> list[Path]`.

Es la respuesta al corte entre el acopio y el conductor (`docs/SIN_CONEXION.md`). Todo sale de la
base y de la red vial guardada en disco: no se descarga nada, ni teselas ni fuentes. El mapa y los
QR se dibujan como vectores, así que la hoja se imprime nítida en blanco y negro.

El QR contiene solo el código del paquete (por ejemplo `DX-7KQ3`), sin datos personales. Se lee con
cualquier cámara y la entrega se registra después por SMS (`ENTREGADO DX-7KQ3`), por el bot o en
el tablero (`despacho.paquetes.entregar`).

Solo se imprimen planes aprobados: los paquetes y sus códigos nacen cuando el despachador aprueba.
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import re
import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

import segno
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from datos import db

# Carta, en milímetros.
ANCHO, ALTO, MARGEN = 215.9, 279.4, 12.0
UTIL = ANCHO - 2 * MARGEN
MAPA_ALTO = 64.0
FILA_ALTO = 22.0            # QR de 16 mm más el código escrito debajo
QR_MM = 16.0
FIN_ALTO = 34.0             # tramos cerrados, reglas del conductor y pie
TIPOS = {"camion": "camión", "campero": "campero", "moto": "moto", "a_pie": "a pie"}
# Columnas de la tabla de paradas: (título, ancho en mm). La última toma lo que sobra.
COLUMNAS = [("#", 7), ("Paquete", 24), ("Punto y barrio", 48), ("Llega", 13), ("Qué se entrega", 50),
            ("Crítico", 15), ("Recibe: firma y hora", None)]
REGLA_ENTREGA = ("Al volver, registre las entregas con el código de cada paquete: por SMS "
                 "«ENTREGADO DX-XXXX», por el bot o en el tablero.")
REGLA_CIERRE = ("Si encuentra una vía cerrada: no intente pasar. Siga a la parada siguiente por otra vía "
                "y anote dónde estaba el cierre; si tiene señal, avise por SMS «CIERRE <lugar> <vehículo>». "
                "Si no hay otra vía, vuelva al acopio con lo que no pudo entregar.")
VIAS_PRINCIPALES = {"motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link",
                    "primary_link", "secondary_link"}


# ---------------------------------------------------------------- datos

def _plan_aprobado(con: sqlite3.Connection, plan_id: int | None) -> sqlite3.Row:
    if plan_id is None:
        r = con.execute("SELECT * FROM planes WHERE estado='aprobado' ORDER BY id DESC LIMIT 1").fetchone()
        if r is None:
            raise ValueError("no hay un plan aprobado: el despachador aprueba antes de imprimir")
        return r
    r = con.execute("SELECT * FROM planes WHERE id=?", (plan_id,)).fetchone()
    if r is None:
        raise ValueError(f"el plan {plan_id} no existe")
    if r["estado"] != "aprobado":
        raise ValueError(f"el plan {plan_id} está «{r['estado']}»: solo se imprimen planes aprobados, "
                         "porque los códigos de los paquetes nacen al aprobar")
    return r


def _paquete(con: sqlite3.Connection, pedido_id: int | None) -> sqlite3.Row | None:
    if pedido_id is None:
        return None
    return con.execute(
        "SELECT codigo, estado FROM paquetes WHERE pedido_id=? AND estado != 'perdido' ORDER BY "
        "CASE estado WHEN 'en_ruta' THEN 0 WHEN 'en_bodega' THEN 1 ELSE 2 END, rowid LIMIT 1",
        (pedido_id,)).fetchone()


def _entrega(surtido: list[dict], kg: float | None) -> str:
    """«arroz 20 kg, leche 12 kg»: los lotes del pedido sumados por producto."""
    por_producto: dict[str, float] = {}
    for linea in surtido or []:
        nombre = linea.get("producto") or "mercado"
        por_producto[nombre] = por_producto.get(nombre, 0.0) + float(linea.get("kg") or 0)
    if not por_producto:
        return f"mercado {_kg(kg)}"
    return ", ".join(f"{p} {_kg(k)}" for p, k in sorted(por_producto.items(), key=lambda x: -x[1]))


def _kg(kg: float | None) -> str:
    if kg is None:
        return "? kg"
    return f"{kg:,.1f}".rstrip("0").rstrip(".").replace(",", "X").replace(".", ",").replace("X", ".") + " kg"


def _hora(iso: str | None) -> str:
    if not iso:
        return "--:--"
    try:
        return datetime.fromisoformat(iso).strftime("%H:%M")
    except ValueError:
        return "--:--"


def _cierres(con: sqlite3.Connection, ids: list[int], tipo: str) -> list[sqlite3.Row]:
    """Cierres con los que se calculó el plan y que bloquean a este tipo de vehículo."""
    if not ids:
        return []
    filas = con.execute(f"SELECT * FROM cierres WHERE id IN ({','.join('?' * len(ids))}) ORDER BY id",
                        list(ids)).fetchall()
    fuera = []
    for c in filas:
        try:
            tipos = json.loads(c["tipos_bloqueados"] or "[]")
        except ValueError:
            tipos = []
        if not tipos or tipo in tipos:
            fuera.append(c)
    return fuera


def _leer(con: sqlite3.Connection, plan_id: int | None) -> dict:
    plan = _plan_aprobado(con, plan_id)
    try:
        resumen = json.loads(plan["resumen"] or "{}")
    except ValueError:
        resumen = {}
    surtido = resumen.get("surtido") or {}
    supuestas = resumen.get("cantidad_supuesta") or {}
    regresos = {v.get("vehiculo_id"): v for v in resumen.get("vehiculos") or []}
    vehiculos: dict[int, dict] = {}
    for pa in con.execute(
            "SELECT pa.*, pu.nombre AS punto, pu.barrio, pu.comuna, pu.critico, pu.lat, pu.lon, "
            "       v.nombre AS vehiculo, v.tipo, v.capacidad_kg, v.acopio_id, "
            "       a.nombre AS acopio, a.lat AS acopio_lat, a.lon AS acopio_lon "
            "FROM paradas pa LEFT JOIN puntos pu ON pu.id = pa.punto_id "
            "LEFT JOIN vehiculos v ON v.id = pa.vehiculo_id LEFT JOIN acopios a ON a.id = v.acopio_id "
            "WHERE pa.plan_id=? ORDER BY pa.vehiculo_id, pa.orden", (plan["id"],)):
        v = vehiculos.setdefault(pa["vehiculo_id"], {
            "id": pa["vehiculo_id"], "nombre": pa["vehiculo"] or f"Vehículo {pa['vehiculo_id']}",
            "tipo": pa["tipo"] or "", "capacidad_kg": pa["capacidad_kg"], "acopio": pa["acopio"] or "?",
            "acopio_lat": pa["acopio_lat"], "acopio_lon": pa["acopio_lon"], "paradas": [],
            "regreso": (regresos.get(pa["vehiculo_id"]) or {}).get("regreso") or [],
            "duracion_s": (regresos.get(pa["vehiculo_id"]) or {}).get("duracion_s")})
        paq = _paquete(con, pa["pedido_id"])
        try:
            geometria = json.loads(pa["geometria"] or "[]")
        except ValueError:
            geometria = []
        v["paradas"].append({
            "orden": pa["orden"], "punto": pa["punto"] or "?", "barrio": pa["barrio"] or "",
            "critico": bool(pa["critico"]), "lat": pa["lat"], "lon": pa["lon"],
            "llegada": _hora(pa["llegada_estimada"]), "kg": pa["kg"], "pedido_id": pa["pedido_id"],
            "entrega": _entrega(surtido.get(str(pa["pedido_id"])), pa["kg"]),
            "supuesta": supuestas.get(str(pa["pedido_id"])),
            "codigo": paq["codigo"] if paq else None, "estado": paq["estado"] if paq else None,
            "geometria": geometria})
    for v in vehiculos.values():
        v["cierres"] = _cierres(con, resumen.get("cierres_aplicados") or [], v["tipo"])
    return {"plan": plan, "resumen": resumen, "vehiculos": list(vehiculos.values())}


# ---------------------------------------------------------------- red vial del disco

def grafo_local():
    """La red vial guardada en disco, o None. Nunca descarga: sin archivo, el mapa sale sin calles."""
    from despacho import red
    if red.RUTA_GRAFO.exists():
        return red.cargar()
    if red.RUTA_PICKLE.exists():          # `red.cargar` descargaría si falta el graphml
        with open(red.RUTA_PICKLE, "rb") as f:
            return pickle.load(f)
    return None


def _calles(g, sur: float, oeste: float, norte: float, este: float) -> list[tuple[bool, list]]:
    """(es_principal, [(lon, lat), ...]) de las aristas con algún extremo dentro del recuadro."""
    if g is None:
        return []
    dentro = {n for n, d in g.nodes(data=True) if sur <= d["y"] <= norte and oeste <= d["x"] <= este}
    vistos, calles = set(), []
    for u, v, d in g.edges(data=True):
        if (u not in dentro and v not in dentro) or (v, u) in vistos or (u, v) in vistos:
            continue
        vistos.add((u, v))
        geom = d.get("geometry")
        pts = list(geom.coords) if geom is not None else [(g.nodes[u]["x"], g.nodes[u]["y"]),
                                                          (g.nodes[v]["x"], g.nodes[v]["y"])]
        h = d.get("highway", "")
        h = h[0] if isinstance(h, list) else str(h)
        calles.append((h in VIAS_PRINCIPALES, pts))
    return calles


def _punto_cierre(g, c: sqlite3.Row) -> tuple[float, float] | None:
    """(lat, lon) de un cierre: sus coordenadas o el centro de su arista."""
    if c["lat"] is not None and c["lon"] is not None:
        return c["lat"], c["lon"]
    if g is not None and c["osm_u"] in g and c["osm_v"] in g:
        a, b = g.nodes[c["osm_u"]], g.nodes[c["osm_v"]]
        return (a["y"] + b["y"]) / 2, (a["x"] + b["x"]) / 2
    return None


# ---------------------------------------------------------------- dibujo

def _texto(s) -> str:
    """Las fuentes base del PDF son latin-1: se cambian los signos que no caben."""
    s = str(s if s is not None else "")
    s = (s.replace("—", "-").replace("–", "-").replace("’", "'").replace("“", '"').replace("”", '"')
          .replace("…", "...").replace("≥", ">=").replace("≤", "<=").replace("→", "->"))
    return s.encode("latin-1", "replace").decode("latin-1")


def _slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "vehiculo"


class _Hoja(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="Letter")
        self.set_auto_page_break(False)
        self.set_margins(MARGEN, MARGEN, MARGEN)
        self.set_creator("DespachoX")
        self.set_draw_color(0)
        self.set_text_color(0)

    def t(self, x, y, texto, tam=9, estilo="", ancho=0, alinear="L", alto=None):
        self.set_font("Helvetica", estilo, tam)
        self.set_xy(x, y)
        self.cell(ancho, alto or tam * 0.45, _texto(texto), align=alinear,
                  new_x=XPos.RIGHT, new_y=YPos.TOP)

    def reponer_estado(self):
        """Al salir de un recorte el PDF vuelve a su estado anterior, pero fpdf2 cree que no y omite
        los cambios de color que le parecen repetidos. Se fuerza el estado conocido."""
        for poner in (self.set_fill_color, self.set_draw_color, self.set_text_color):
            poner(128)
            poner(0)
        self.set_line_width(0.3)
        self.set_line_width(0.25)
        self.set_dash_pattern(1, 1)
        self.set_dash_pattern()

    def qr(self, x, y, lado, codigo):
        """Dibuja el QR como cuadrados negros, con su zona en blanco de 4 módulos."""
        filas = list(segno.make(codigo, error="m", micro=False).matrix_iter(scale=1, border=4))
        m = lado / len(filas)
        self.set_fill_color(0)
        for i, fila in enumerate(filas):
            j = 0
            while j < len(fila):
                if fila[j]:
                    k = j
                    while k < len(fila) and fila[k]:
                        k += 1
                    self.rect(x + j * m, y + i * m, (k - j) * m, m, style="F")
                    j = k
                else:
                    j += 1


def _encabezado(pdf: _Hoja, datos: dict, v: dict, hoja: int, hojas: int) -> float:
    plan, resumen = datos["plan"], datos["resumen"]
    y = MARGEN
    pdf.t(MARGEN, y, "DespachoX", 15, "B")
    pdf.t(MARGEN + 31, y + 0.6, "Hoja de ruta", 12)
    pdf.t(MARGEN, y, f"Plan {plan['id']} · hoja {hoja} de {hojas}", 9, ancho=UTIL, alinear="R")
    y += 8
    pdf.t(MARGEN, y, v["nombre"], 20, "B")
    tipo = TIPOS.get(v["tipo"], v["tipo"])
    pdf.t(MARGEN + pdf.get_string_width(_texto(v["nombre"])) + 3, y + 2.2,
          f"{tipo} · capacidad {_kg(v['capacidad_kg'])}", 10)
    y += 10
    salida = resumen.get("calculado_para")
    regreso = "--:--"
    if salida and v.get("duracion_s") is not None:
        try:
            regreso = datetime.fromtimestamp(datetime.fromisoformat(salida).timestamp() + v["duracion_s"],
                                             datetime.fromisoformat(salida).tzinfo).strftime("%H:%M")
        except ValueError:
            pass
    kilos = sum(p["kg"] or 0 for p in v["paradas"])
    criticos = sum(p["critico"] for p in v["paradas"])
    celdas = [("Acopio de salida", v["acopio"]),
              ("Salida · regreso estimado", f"{_hora(salida)} · {regreso}"),
              ("Carga", f"{len(v['paradas'])} paradas · {_kg(kilos)}"
                        + (f" · {criticos} crítica{'s' if criticos != 1 else ''}" if criticos else "")),
              ("Conductor", "")]
    anchos = [56, 40, 50, UTIL - 146]
    x = MARGEN
    pdf.set_line_width(0.25)
    for (titulo, valor), w in zip(celdas, anchos):
        pdf.rect(x, y, w, 11)
        pdf.t(x + 1.5, y + 1.2, titulo, 6.5)
        pdf.t(x + 1.5, y + 5.2, valor, 9, "B", ancho=w - 3)
        x += w
    return y + 13


def _mapa(pdf: _Hoja, v: dict, g, x0: float, y0: float, w: float, h: float) -> None:
    pts = [(p["lat"], p["lon"]) for p in v["paradas"] if p["lat"] is not None]
    for p in v["paradas"]:
        pts += [tuple(q) for q in p["geometria"]]
    pts += [tuple(q) for q in v["regreso"]]
    if v["acopio_lat"] is not None:
        pts.append((v["acopio_lat"], v["acopio_lon"]))
    pdf.set_line_width(0.3)
    pdf.rect(x0, y0, w, h)
    if not pts:
        pdf.t(x0, y0 + h / 2 - 2, "sin geometría para dibujar", 9, ancho=w, alinear="C")
        return
    lats, lons = [p[0] for p in pts], [p[1] for p in pts]
    lat0 = (min(lats) + max(lats)) / 2
    kx = math.cos(math.radians(lat0))
    dx = max((max(lons) - min(lons)) * kx, 0.004) * 1.15
    dy = max(max(lats) - min(lats), 0.004) * 1.15
    escala = min(w / dx, h / dy)                       # mm por grado de latitud
    cx, cy = (max(lons) + min(lons)) / 2, lat0

    def xy(lat, lon):
        return x0 + w / 2 + (lon - cx) * kx * escala, y0 + h / 2 - (lat - cy) * escala

    medio_lon, medio_lat = w / 2 / (kx * escala), h / 2 / escala
    with pdf.rect_clip(x0, y0, w, h):
        for principal, linea in sorted(_calles(g, cy - medio_lat, cx - medio_lon, cy + medio_lat,
                                               cx + medio_lon), key=lambda c: c[0]):
            pdf.set_draw_color(120 if principal else 175)
            pdf.set_line_width(0.45 if principal else 0.15)
            pdf.polyline([xy(lat, lon) for lon, lat in linea])
        pdf.set_draw_color(0)
        if len(v["regreso"]) > 1:                      # regreso al acopio: discontinuo
            pdf.set_line_width(0.5)
            pdf.set_dash_pattern(1.6, 1.2)
            pdf.polyline([xy(*q) for q in v["regreso"]])
            pdf.set_dash_pattern()
        pdf.set_line_width(1.0)
        for p in v["paradas"]:
            if len(p["geometria"]) > 1:
                pdf.polyline([xy(*q) for q in p["geometria"]])
        for c in v["cierres"]:
            donde = _punto_cierre(g, c)
            if donde:
                cx_, cy_ = xy(*donde)
                pdf.set_line_width(0.9)
                pdf.line(cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2)
                pdf.line(cx_ - 2, cy_ + 2, cx_ + 2, cy_ - 2)
        if v["acopio_lat"] is not None:
            ax, ay = xy(v["acopio_lat"], v["acopio_lon"])
            pdf.set_fill_color(0)
            pdf.rect(ax - 2.4, ay - 2.4, 4.8, 4.8, style="F")
            pdf.set_text_color(255)
            pdf.t(ax - 2.4, ay - 1.6, "A", 8, "B", ancho=4.8, alinear="C", alto=3.2)
            pdf.set_text_color(0)
        juntas: dict[tuple, list[dict]] = {}          # dos pedidos en el mismo punto: un marcador
        for p in v["paradas"]:
            if p["lat"] is not None:
                juntas.setdefault((round(p["lat"], 5), round(p["lon"], 5)), []).append(p)
        for (lat, lon), grupo in juntas.items():
            px, py = xy(lat, lon)
            critico = any(p["critico"] for p in grupo)
            rotulo = "-".join(str(p["orden"]) for p in grupo)
            medio = max(2.7, len(rotulo) * 0.85 + 0.8)  # ancho a la mitad
            pdf.set_line_width(0.35)
            pdf.set_fill_color(255)
            if critico:
                pdf.rect(px - medio - 0.8, py - 3.5, 2 * medio + 1.6, 7, style="DF", round_corners=True,
                         corner_radius=3.5)
                pdf.set_fill_color(0)
                pdf.rect(px - medio, py - 2.7, 2 * medio, 5.4, style="F", round_corners=True,
                         corner_radius=2.7)
                pdf.set_text_color(255)
            else:
                pdf.rect(px - medio, py - 2.7, 2 * medio, 5.4, style="DF", round_corners=True,
                         corner_radius=2.7)
            pdf.t(px - medio, py - 1.5, rotulo, 7.5, "B", ancho=2 * medio, alinear="C", alto=3)
            pdf.set_text_color(0)
    pdf.reponer_estado()
    # Escala y norte, fuera del recorte para que no se tapen.
    metros_mm = 110_540 / escala
    paso = next((m for m in (100, 200, 250, 500, 1000, 2000, 5000) if m / metros_mm >= 12), 5000)
    largo = paso / metros_mm
    pdf.set_fill_color(255)
    pdf.rect(x0 + 2, y0 + h - 7, largo + 14, 5, style="F")
    pdf.set_line_width(0.6)
    pdf.line(x0 + 3, y0 + h - 3.5, x0 + 3 + largo, y0 + h - 3.5)
    pdf.t(x0 + 4 + largo, y0 + h - 5.2, f"{paso / 1000:g} km" if paso >= 1000 else f"{paso} m", 6.5)
    pdf.set_fill_color(0)
    pdf.polygon([(x0 + w - 5, y0 + 2.5), (x0 + w - 7, y0 + 7), (x0 + w - 3, y0 + 7)], style="F")
    pdf.t(x0 + w - 7, y0 + 7.4, "N", 7, "B", ancho=4, alinear="C")
    pdf.t(x0, y0 + h + 0.8, "Red vial: © colaboradores de OpenStreetMap, guardada en disco. Sin internet.",
          6, ancho=w)


def _leyenda(pdf: _Hoja, v: dict, x0: float, y0: float, w: float, h: float, calles: bool) -> None:
    pdf.set_line_width(0.25)
    pdf.rect(x0, y0, w, h)
    y = y0 + 2
    pdf.t(x0 + 2, y, "Cómo leer el mapa", 8.5, "B")
    y += 6
    pdf.set_draw_color(0)
    pdf.set_fill_color(0)
    pdf.rect(x0 + 3, y - 0.4, 4, 4, style="F")
    pdf.t(x0 + 9, y, "A  acopio de salida", 7.5)
    y += 6
    pdf.set_fill_color(255)
    pdf.set_line_width(0.35)
    pdf.circle(x0 + 5, y + 1.6, 2.2, style="DF")
    pdf.t(x0 + 9, y, "parada, en orden de visita", 7.5)
    y += 6
    pdf.circle(x0 + 5, y + 1.6, 2.9, style="DF")
    pdf.set_fill_color(0)
    pdf.circle(x0 + 5, y + 1.6, 2.2, style="F")
    pdf.t(x0 + 9, y, "punto crítico: va primero", 7.5)
    y += 6
    pdf.set_line_width(1.0)
    pdf.line(x0 + 2.5, y + 1.6, x0 + 7.5, y + 1.6)
    pdf.t(x0 + 9, y, "ruta de ida", 7.5)
    y += 5
    pdf.set_line_width(0.5)
    pdf.set_dash_pattern(1.6, 1.2)
    pdf.line(x0 + 2.5, y + 1.6, x0 + 7.5, y + 1.6)
    pdf.set_dash_pattern()
    pdf.t(x0 + 9, y, "regreso al acopio", 7.5)
    y += 5
    pdf.set_line_width(0.9)
    pdf.line(x0 + 3, y, x0 + 7, y + 3.2)
    pdf.line(x0 + 3, y + 3.2, x0 + 7, y)
    pdf.t(x0 + 9, y, "tramo cerrado que la ruta evita", 7.5)
    y += 7
    pdf.set_font("Helvetica", "", 7)
    pdf.set_xy(x0 + 2, y)
    nota = ("El plan lo calculó el optimizador y lo aprobó el despachador. Las horas son estimadas."
            if calles else
            "No hay red vial en disco: el mapa muestra solo la ruta. Las horas son estimadas.")
    pdf.multi_cell(w - 4, 3.2, _texto(nota), align="L")


def _tabla_titulos(pdf: _Hoja, y: float) -> float:
    x = MARGEN
    pdf.set_fill_color(0)
    pdf.rect(MARGEN, y, UTIL, 6, style="F")
    pdf.set_text_color(255)
    for titulo, w in COLUMNAS:
        w = w or UTIL - sum(c[1] for c in COLUMNAS if c[1])
        pdf.t(x + 1.2, y + 1.4, titulo, 7.5, "B", ancho=w - 2.4)
        x += w
    pdf.set_text_color(0)
    return y + 6


def _fila(pdf: _Hoja, p: dict, y: float) -> None:
    anchos = [w or UTIL - sum(c[1] for c in COLUMNAS if c[1]) for _, w in COLUMNAS]
    xs = [MARGEN + sum(anchos[:i]) for i in range(len(anchos))]
    pdf.set_line_width(0.25)
    pdf.set_draw_color(0)
    pdf.rect(MARGEN, y, UTIL, FILA_ALTO)
    for x in xs[1:]:
        pdf.line(x, y, x, y + FILA_ALTO)
    pdf.t(xs[0], y + 2, str(p["orden"]), 14, "B", ancho=anchos[0], alinear="C", alto=6)
    if p["codigo"]:
        pdf.qr(xs[1] + (anchos[1] - QR_MM) / 2, y + 0.6, QR_MM, p["codigo"])
        pdf.t(xs[1], y + QR_MM + 0.6, p["codigo"], 8.5, "B", ancho=anchos[1], alinear="C", alto=4)
    else:
        pdf.t(xs[1], y + 8, "sin código", 7.5, ancho=anchos[1], alinear="C")
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_xy(xs[2] + 1.2, y + 1.5)
    pdf.multi_cell(anchos[2] - 2.4, 3.7, _texto(p["punto"]), align="L")
    if p["barrio"] and p["barrio"] not in p["punto"]:
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_x(xs[2] + 1.2)
        pdf.multi_cell(anchos[2] - 2.4, 3.4, _texto(f"barrio {p['barrio']}"), align="L")
    pdf.t(xs[3], y + 2, p["llegada"], 10, "B", ancho=anchos[3], alinear="C", alto=5)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(xs[4] + 1.2, y + 1.5)
    pdf.multi_cell(anchos[4] - 2.4, 3.6, _texto(p["entrega"]), align="L")
    notas = []
    if p["supuesta"]:
        notas.append("cantidad supuesta: confirmar al entregar")
    if p["estado"] == "entregado":
        notas.append("ya registrado como entregado")
    if notas:
        pdf.set_font("Helvetica", "I", 7)
        pdf.set_x(xs[4] + 1.2)
        pdf.multi_cell(anchos[4] - 2.4, 3.2, _texto("; ".join(notas)), align="L")
    if p["critico"]:
        pdf.set_fill_color(0)
        pdf.rect(xs[5] + 1.2, y + 2, anchos[5] - 2.4, 5.5, style="F")
        pdf.set_text_color(255)
        pdf.t(xs[5] + 1.2, y + 2.6, "SÍ", 9, "B", ancho=anchos[5] - 2.4, alinear="C", alto=4.3)
        pdf.set_text_color(0)
    else:
        pdf.t(xs[5], y + 2.6, "no", 8, ancho=anchos[5], alinear="C", alto=4.3)
    pdf.set_line_width(0.2)
    for i, rotulo in enumerate(("firma", "hora")):
        ly = y + 9 + i * 8
        pdf.t(xs[6] + 1.2, ly - 3.2, rotulo, 6.5)
        pdf.line(xs[6] + 9, ly, xs[6] + anchos[6] - 2, ly)


def _final(pdf: _Hoja, datos: dict, v: dict, y: float) -> None:
    pdf.t(MARGEN, y, "Tramos cerrados que esta ruta evita", 9, "B")
    y += 5
    pdf.set_font("Helvetica", "", 8)
    pdf.set_xy(MARGEN, y)
    if v["cierres"]:
        lineas = []
        for c in v["cierres"]:
            donde = c["lugar"] or c["descripcion"] or "sin nombre"
            lineas.append(f"Cierre {c['id']}: {donde}")
        texto = "; ".join(lineas) + "."
    else:
        texto = "Ninguno confirmado cuando se calculó el plan."
    pdf.multi_cell(UTIL, 3.6, _texto(texto), align="L")
    y = pdf.get_y() + 2
    pdf.set_line_width(0.5)
    pdf.rect(MARGEN, y, UTIL, 17)
    pdf.set_xy(MARGEN + 2, y + 1.5)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.multi_cell(UTIL - 4, 3.8, _texto(REGLA_ENTREGA), align="L")
    pdf.set_x(MARGEN + 2)
    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(UTIL - 4, 3.6, _texto(REGLA_CIERRE), align="L")
    plan = datos["plan"]
    pie = (f"Plan {plan['id']} aprobado por {plan['aprobado_por'] or '?'} a las {_hora(plan['aprobado_en'])}. "
           f"Impresa el {datetime.now(db.BOGOTA).strftime('%d/%m/%Y %H:%M')}. "
           "El QR lleva solo el código del paquete, sin datos personales.")
    pdf.t(MARGEN, ALTO - MARGEN - 3, pie, 6.5, ancho=UTIL)


def _pdf_vehiculo(datos: dict, v: dict, g) -> _Hoja:
    pdf = _Hoja()
    paradas = v["paradas"]
    # Primera hoja: encabezado, mapa y las filas que quepan; si sobran, siguen en otras hojas.
    def caben(hoja: int, con_final: bool) -> int:
        y = MARGEN + 31 + (MAPA_ALTO + 5 if hoja == 1 else 0) + 6
        return int((ALTO - MARGEN - 4 - (FIN_ALTO if con_final else 0) - y) // FILA_ALTO)

    grupos: list[list[dict]] = []
    resto = paradas
    while True:                     # si lo que queda cabe con el bloque final, es la última hoja
        hoja = len(grupos) + 1
        if len(resto) <= caben(hoja, True):
            grupos.append(resto)
            break
        n = caben(hoja, False)
        grupos.append(resto[:n])
        resto = resto[n:]
    for i, grupo in enumerate(grupos, start=1):
        pdf.add_page()
        y = _encabezado(pdf, datos, v, i, len(grupos))
        if i == 1:
            ancho_mapa = UTIL - 52
            _mapa(pdf, v, g, MARGEN, y, ancho_mapa, MAPA_ALTO)
            _leyenda(pdf, v, MARGEN + ancho_mapa + 3, y, 49, MAPA_ALTO, g is not None)
            y += MAPA_ALTO + 5
        if grupo:
            y = _tabla_titulos(pdf, y)
            for p in grupo:
                _fila(pdf, p, y)
                y += FILA_ALTO
        if i == len(grupos):
            _final(pdf, datos, v, y + 3)
    return pdf


# ---------------------------------------------------------------- entrada

def carpeta_por_defecto(plan_id: int) -> Path:
    """Junto a la base (en la nube, el volumen persistente), en `hojas/plan_N/`."""
    return Path(db.RUTA_DB).resolve().parent / "hojas" / f"plan_{plan_id}"


def generar(con: sqlite3.Connection, plan_id: int | None = None, salida: Path | str | None = None,
            g=None, quien: str = "despachador") -> list[Path]:
    """Escribe un PDF por vehículo del plan aprobado y devuelve sus rutas, en orden de vehículo.

    plan_id: None toma el plan aprobado vigente. Lanza ValueError si el plan no está aprobado.
    g: red vial para el fondo del mapa; None la lee del disco si existe (nunca la descarga).
    """
    datos = _leer(con, plan_id)
    plan_id = datos["plan"]["id"]
    if g is None:
        g = grafo_local()
    carpeta = Path(salida) if salida else carpeta_por_defecto(plan_id)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for v in datos["vehiculos"]:
        ruta = carpeta / f"plan{plan_id}_{_slug(v['nombre'])}.pdf"
        _pdf_vehiculo(datos, v, g).output(str(ruta))
        rutas.append(ruta)
    db.anotar(con, quien, "imprimir hojas de ruta",
              f"plan {plan_id}: {len(rutas)} hojas, {sum(len(v['paradas']) for v in datos['vehiculos'])} paquetes")
    return rutas


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Hojas de ruta en PDF, una por vehículo, con un QR por paquete.")
    ap.add_argument("--plan", type=int, help="id del plan aprobado (por defecto, el vigente)")
    ap.add_argument("--salida", help="carpeta de salida (por defecto, hojas/plan_N junto a la base)")
    ap.add_argument("--quien", default="despachador")
    args = ap.parse_args(argv)
    con = db.conectar()
    try:
        rutas = generar(con, args.plan, args.salida, quien=args.quien)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1
    finally:
        con.close()
    if not rutas:
        print("el plan aprobado no tiene paradas")
    for r in rutas:
        print(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
