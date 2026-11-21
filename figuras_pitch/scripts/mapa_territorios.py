"""Figura (a): las tres propuestas de territorio para el piloto, con puntos críticos, acopios y rutas por la red.

Uso: python figuras_pitch/scripts/mapa_territorios.py [--fuente FAMILIA] [--salida CARPETA] [--solo 1]
Lee  despacho/cache/manizales_region.graphml (o despliegue/grafo/manizales_region.graphml si no está),
     figuras_pitch/datos/limites_osm.geojson (sale de despacho/cache/admin_osm.pkl con extraer_limites.py),
     datos_publicos/puntos.csv, datos_publicos/acopios.csv y datos/semilla/lugares_extra.csv (Bajo Tablazo).
Escribe <salida>/png/a_territorios_piloto.png, <salida>/svg/a_territorios_piloto.svg y las distancias en
<salida>/datos/a_territorios_rutas.csv.

Con --solo 1 dibuja solo la propuesta 1, la recomendada, para la diapositiva del piloto: el corredor del Banco a los
tres CDI de La Macarena y a Bajo Tablazo. Escribe a_territorio_propuesta1 (PNG y SVG) y sus distancias en
<salida>/datos/a_territorio_propuesta1_rutas.csv.

Adaptada de docs/informe/figuras/scripts/mapa_manizales.py, sin editar ese archivo. Sin teselas de internet: el
fondo es la red vial del equipo y los límites de OpenStreetMap.

Las propuestas, sus territorios y sus razones vienen de docs/PILOTO_TERRITORIOS.md. Las rutas son el camino más
corto por longitud en el grafo dirigido, desde el nodo del Banco hasta el nodo más cercano a cada lugar.
El Kilómetro 41 no tiene coordenada con fuente en el repositorio (lugares/README.md), así que va como flecha.
"""
import csv
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import networkx as nx
import numpy as np
import osmnx as ox
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import estilo as e

NOMBRE = "a_territorios_piloto"
NOMBRE_SOLO = "a_territorio_propuesta1"
GRAFOS = [e.RAIZ / "despacho" / "cache" / "manizales_region.graphml",
          e.RAIZ / "despliegue" / "grafo" / "manizales_region.graphml"]
LIMITES = e.CARPETA / "datos" / "limites_osm.geojson"
# Recuadro del mapa (oeste, sur, este, norte), cuadrado en grados.
RECUADRO = (-75.586, 4.996, -75.456, 5.126)
RECUADRO_SOLO = (-75.552, 5.0145, -75.485, 5.0815)
GRIS_PUNTO = "#B9B4C0"
# Posición a mano de algunos números, si la automática no sirve (vacío: todas son automáticas).
AJUSTE_INSIGNIA = {}
RADIO_INSIGNIA = 0.0037   # grados; el círculo del número mide unos 60 px
ANCHO_RUTA, ANCHO_LIMITE = 7.5, 2.2

PROPUESTAS = [
    {"n": 1, "color": e.TINTA, "comuna": "La Macarena", "corregimiento": "El Tablazo (Corredor Agroturístico)",
     "titulo": "La Macarena y El Tablazo", "nota": "Recomendada. Tres CDI y la vereda en un corredor.",
     "rural": "Bajo Tablazo"},
    {"n": 2, "color": e.AMBAR, "comuna": "Ciudadela del Norte", "corregimiento": "El Manantial",
     "titulo": "Ciudadela del Norte y El Manantial", "nota": "La comuna más poblada.", "rural": "Alto Bonito"},
    {"n": 3, "color": e.CENIZA, "comuna": "Atardeceres", "corregimiento": None,
     "titulo": "Atardeceres y Kilómetro 41", "nota": "Probaría las alertas de lluvia A25 del IDEA (UNAL).",
     "rural": "La Aurora"},
]


def leer_csv(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def lugares_rurales():
    puntos = {p["nombre"]: p for p in leer_csv(e.RAIZ / "datos_publicos" / "puntos.csv")}
    extra = {p["nombre"]: p for p in leer_csv(e.RAIZ / "datos" / "semilla" / "lugares_extra.csv")}
    return {
        "Bajo Tablazo": (float(extra["Bajo Tablazo"]["lat"]), float(extra["Bajo Tablazo"]["lon"]),
                         "datos/semilla/lugares_extra.csv (Nominatim)"),
        "Alto Bonito": (float(puntos["Casa de la Cultura Alto Bonito"]["lat"]),
                        float(puntos["Casa de la Cultura Alto Bonito"]["lon"]), "datos_publicos/puntos.csv, id 46"),
        "La Aurora": (float(puntos["Salón JAC vereda La Aurora"]["lat"]),
                      float(puntos["Salón JAC vereda La Aurora"]["lon"]), "datos_publicos/puntos.csv, id 44"),
    }


def nodo_cercano(G, ids, lat, lon, la, lo):
    """Nodo más cercano por distancia sobre la esfera, y su distancia en metros (sin scikit-learn)."""
    p1, p2 = np.radians(la), np.radians(lat)
    d = 2 * 6371000.0 * np.arcsin(np.sqrt(np.sin((p2 - p1) / 2) ** 2 +
                                          np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon - lo) / 2) ** 2))
    i = int(d.argmin())
    return ids[i], float(d[i])


def linea_de_ruta(G, camino) -> LineString:
    """Une la geometría de las aristas del camino en una sola línea, en el sentido del recorrido."""
    puntos = []
    for u, v in zip(camino[:-1], camino[1:]):
        datos = min(G[u][v].values(), key=lambda d: d.get("length", 0))
        if "geometry" in datos:
            coords = list(datos["geometry"].coords)
            xu, yu = G.nodes[u]["x"], G.nodes[u]["y"]
            if (coords[0][0] - xu) ** 2 + (coords[0][1] - yu) ** 2 > (coords[-1][0] - xu) ** 2 + (coords[-1][1] - yu) ** 2:
                coords = coords[::-1]
        else:
            coords = [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
        puntos.extend(coords if not puntos else coords[1:])
    return LineString(puntos)


def sitio_libre(forma, obstaculos, paso=0.0008):
    """Punto de `forma` más lejos a la vez de su borde y de los obstáculos (rutas, puntos y rótulos)."""
    x0, y0, x1, y1 = forma.bounds
    mejor, puntaje = forma.representative_point(), -1.0
    for x in np.arange(x0, x1, paso):
        for y in np.arange(y0, y1, paso):
            q = Point(x, y)
            if not forma.contains(q):
                continue
            d = min(forma.boundary.distance(q), obstaculos.distance(q))
            if d > puntaje:
                mejor, puntaje = q, d
    return mejor.x, mejor.y, puntaje


def sitio_para_rotulo(forma, obstaculos, ancho, alto, paso=0.0004):
    """Centro de un rótulo de `ancho` × `alto` grados dentro de `forma`, sin tocar los obstáculos.

    Prefiere la caja entera dentro de la forma y, entre esas, la más lejana de los obstáculos. Si ninguna caja
    libre cabe, devuelve None.
    """
    x0, y0, x1, y1 = forma.bounds
    mejor, puntaje = None, (-1.0, -1.0)
    for x in np.arange(x0, x1, paso):
        for y in np.arange(y0, y1, paso):
            caja = box(x - ancho / 2, y - alto / 2, x + ancho / 2, y + alto / 2)
            if caja.intersects(obstaculos):
                continue
            dentro = caja.intersection(forma).area / caja.area
            p = (round(dentro, 2), obstaculos.distance(caja))
            if p > puntaje:
                mejor, puntaje = (x, y), p
    return mejor


def halo(ancho=6):
    return [pe.withStroke(linewidth=ancho, foreground="white")]


class Red:
    """Grafo vial, sus nodos en arreglos y las rutas más cortas desde el Banco."""

    def __init__(self, ruta_grafo, banco):
        self.G = ox.load_graphml(ruta_grafo)
        self.ids = np.array(list(self.G.nodes))
        self.lat = np.array([self.G.nodes[n]["y"] for n in self.ids])
        self.lon = np.array([self.G.nodes[n]["x"] for n in self.ids])
        self.origen, _ = self.cercano(float(banco["lat"]), float(banco["lon"]))

    def cercano(self, la, lo):
        return nodo_cercano(self.G, self.ids, self.lat, self.lon, la, lo)

    def ruta(self, la, lo):
        """(camino, km por la red, metros del lugar a su nodo más cercano)."""
        nodo, d_nodo = self.cercano(la, lo)
        camino = nx.shortest_path(self.G, self.origen, nodo, weight="length")
        return camino, nx.path_weight(self.G, camino, weight="length") / 1000, d_nodo


def escribir_rutas(ruta_csv, filas):
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def base_del_mapa(fig, aristas, limites, recuadro):
    """Ejes cuadrados de 1040 px a la izquierda, con la red vial y los límites de comunas y corregimientos."""
    lado = 1040
    ax = fig.add_axes([20 / e.ANCHO_PX, 20 / e.ALTO_PX, lado / e.ANCHO_PX, lado / e.ALTO_PX])
    o, s, este, n = recuadro
    aristas.cx[o - 0.01:este + 0.01, s - 0.01:n + 0.01].plot(ax=ax, color=e.GRIS_RED, linewidth=0.55, zorder=1,
                                                              rasterized=True)  # SVG liviano
    limites[limites["clase"] == "comuna"].boundary.plot(ax=ax, color=e.CENIZA, linewidth=0.8, alpha=0.6, zorder=2)
    limites[limites["clase"] == "corregimiento"].boundary.plot(ax=ax, color=e.CENIZA, linewidth=1.0,
                                                               linestyle=(0, (4, 3)), alpha=0.6, zorder=2)
    return ax


def territorio(ax, limites, nombre, color):
    """Relleno suave y borde punteado y delgado, para que no se confunda con las rutas, que van gruesas."""
    poli = limites[limites["nombre"] == nombre]
    poli.plot(ax=ax, color=color, alpha=0.16, zorder=2)
    poli.boundary.plot(ax=ax, color=color, linewidth=ANCHO_LIMITE, linestyle=(0, (5, 3)), zorder=3)


def ruta_en_mapa(ax, red, camino, d_nodo, la, lo, color, rombo=True):
    linea = linea_de_ruta(red.G, camino)
    xs, ys = linea.xy
    ax.plot(xs, ys, color=color, linewidth=ANCHO_RUTA, zorder=5, solid_capstyle="round", solid_joinstyle="round",
            path_effects=halo(13))
    if d_nodo > 100:      # el grafo no llega: tramo final punteado hasta el lugar
        fin_x, fin_y = red.G.nodes[camino[-1]]["x"], red.G.nodes[camino[-1]]["y"]
        ax.plot([fin_x, lo], [fin_y, la], color=color, linewidth=4.5, linestyle=(0, (1.5, 1.5)), zorder=5)
    if rombo:
        ax.scatter([lo], [la], s=440, marker="D", color=color, edgecolor="white", linewidth=2.5, zorder=7)
    return linea


def cerrar_mapa(ax, recuadro, convenciones):
    o, s, este, n = recuadro
    ax.set_xlim(o, este)
    ax.set_ylim(s, n)
    ax.set_aspect(1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.set_ylabel("")
    for borde in ax.spines.values():
        borde.set_color(e.CENIZA)
        borde.set_linewidth(1.5)
    ley = ax.legend(handles=[c for c, _ in convenciones], labels=[t for _, t in convenciones], loc="lower right",
                    fontsize=e.pt(26), frameon=True, borderpad=0.6, handletextpad=0.5, labelspacing=0.4,
                    handler_map={tuple: HandlerTuple(ndivide=None, pad=0.3)})
    ley.get_frame().set_edgecolor(e.CENIZA)
    ley.get_frame().set_alpha(0.95)
    ley.set_zorder(12)


def punto(color, tam=13):
    return Line2D([], [], marker="o", linestyle="none", markersize=tam, color=color, markeredgecolor="white")


ACOPIO = Line2D([], [], marker="s", linestyle="none", markersize=16, color=e.TEXTO, markeredgecolor="white")


def arriba(px):
    """Posición vertical de la figura a `px` píxeles del borde superior."""
    return 1 - px / e.ALTO_PX


def mapa_tres(fig, args, red, aristas, limites, puntos, acopios, banco, rurales):
    """Las tres propuestas, con la ruta del Banco al lugar rural de cada una."""
    rutas, filas = {}, []
    for nombre, (la, lo, origen) in rurales.items():
        camino, km, d_nodo = red.ruta(la, lo)
        rutas[nombre] = (camino, km, d_nodo)
        filas.append({"lugar": nombre, "lat": la, "lon": lo, "origen_coordenada": origen,
                      "km_por_la_red": round(km, 2), "metros_al_nodo_mas_cercano": round(d_nodo)})
        print(f"ruta Banco -> {nombre}: {km:.2f} km; nodo a {d_nodo:.0f} m del lugar")
    escribir_rutas(Path(args.salida) / "datos" / "a_territorios_rutas.csv", filas)

    ax = base_del_mapa(fig, aristas, limites, RECUADRO)
    o, s, este, n = RECUADRO
    color_comuna = {}
    for p in PROPUESTAS:
        color_comuna[p["comuna"]] = p["color"]
        for nombre in (p["comuna"], p["corregimiento"]):
            if nombre:
                territorio(ax, limites, nombre, p["color"])

    # Rutas de la 3 a la 1, para que la recomendada quede encima donde comparten calles.
    lineas_ruta = []
    for p in reversed(PROPUESTAS):
        camino, km, d_nodo = rutas[p["rural"]]
        la, lo, _ = rurales[p["rural"]]
        lineas_ruta.append(ruta_en_mapa(ax, red, camino, d_nodo, la, lo, p["color"]))

    criticos = [q for q in puntos if q["critico"].strip() == "1"]
    for q in criticos:
        color = color_comuna.get(q["comuna"], GRIS_PUNTO)
        ax.scatter(float(q["lon"]), float(q["lat"]), s=170 if color != GRIS_PUNTO else 80, color=color,
                   edgecolor="white", linewidth=1.5, zorder=6 if color != GRIS_PUNTO else 4)
    for a in acopios:
        ax.scatter(float(a["lon"]), float(a["lat"]), s=560 if a["id"] == "1" else 280, marker="s", color=e.TEXTO,
                   edgecolor="white", linewidth=2.5, zorder=8)
    bx, by = float(banco["lon"]), float(banco["lat"])
    ax.text(bx - 0.0025, by - 0.0050, "Banco", fontsize=e.pt(32), fontweight="bold", color=e.TEXTO, zorder=9,
            ha="right", path_effects=halo(8))

    # Rótulos de los lugares rurales, con la distancia medida por nosotros.
    desplazamientos = {"Bajo Tablazo": (0.0045, -0.0005, "left", "center"),
                       "Alto Bonito": (0.0045, 0.0, "left", "center"),
                       "La Aurora": (0.0, 0.0050, "center", "bottom")}
    for p in PROPUESTAS:
        camino, km, _ = rutas[p["rural"]]
        la, lo, _ = rurales[p["rural"]]
        dx, dy, ha, va = desplazamientos[p["rural"]]
        ax.text(lo + dx, la + dy, f"{p['rural']}\n{e.miles(km, 1)} km", fontsize=e.pt(28), color=p["color"],
                fontweight="bold", ha=ha, va=va, zorder=9, linespacing=1.05, path_effects=halo(8))

    # Flecha hacia el Kilómetro 41: en el grafo, la rama de La Aurora sigue solo hacia el occidente.
    la, lo, _ = rurales["La Aurora"]
    ax.annotate("", xy=(o + 0.0015, la), xytext=(lo - 0.0045, la), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color=e.CENIZA, linewidth=4.5, mutation_scale=36))
    ax.text(o + 0.0025, la - 0.0035, "Al km 41,\n36,4 km", fontsize=e.pt(28), color=e.CENIZA, fontweight="bold",
            ha="left", va="top", zorder=9, linespacing=1.05, path_effects=halo(8))

    # Números de cada propuesta sobre su comuna y su corregimiento (parte visible del polígono).
    marco = box(o, s, este, n).buffer(-0.006)
    solo_puntos = unary_union([Point(float(q["lon"]), float(q["lat"])) for q in criticos] +
                              [Point(lo, la) for la, lo, _ in rurales.values()] + [Point(bx, by)])
    obstaculos = unary_union(lineas_ruta + [solo_puntos])
    for p in PROPUESTAS:
        for nombre in (p["comuna"], p["corregimiento"]):
            if not nombre:
                continue
            forma = limites[limites["nombre"] == nombre].geometry.iloc[0].intersection(marco)
            x, y, holgura = sitio_libre(forma, obstaculos)
            if holgura < RADIO_INSIGNIA:          # sin sitio libre: se permite tapar la ruta, no los puntos
                x, y, holgura = sitio_libre(forma, solo_puntos)
            x, y = AJUSTE_INSIGNIA.get(nombre, (x, y))
            ax.text(x, y, str(p["n"]), fontsize=e.pt(34), fontweight="bold", color="white", ha="center",
                    va="center", zorder=11,
                    bbox=dict(boxstyle="circle,pad=0.28", facecolor=p["color"], edgecolor="white", linewidth=3))

    cerrar_mapa(ax, RECUADRO, [
        ((punto(e.TINTA), punto(e.AMBAR), punto(e.CENIZA)), "Punto crítico de una propuesta"),
        (punto(GRIS_PUNTO, 10), "Otro punto crítico"),
        (ACOPIO, "Acopio"),
        (Line2D([], [], color=e.TEXTO, linewidth=ANCHO_RUTA), "Ruta más corta por la red"),
    ])

    # Panel derecho: título, propuestas y fuentes. Posiciones en píxeles desde arriba.
    x0 = 1110 / e.ANCHO_PX
    fig.text(x0, arriba(55), "Tres territorios\npara el piloto", fontsize=e.pt(58), fontweight="bold",
             color=e.TEXTO, va="top", linespacing=1.05)
    fig.text(x0, arriba(215), "Cada uno une una comuna y un corregimiento.\nDecide el Banco.", fontsize=e.pt(28),
             color=e.CENIZA, va="top", linespacing=1.25)
    y = 330
    ancho_nota = e.ANCHO_PX - 40 - (x0 + 0.036) * e.ANCHO_PX
    for p in PROPUESTAS:
        fig.text(x0 + 0.013, arriba(y + 22), str(p["n"]), fontsize=e.pt(30), fontweight="bold", color="white",
                 ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.25", facecolor=p["color"],
                                                     edgecolor="none"))
        e.encajar(fig, fig.text(x0 + 0.036, arriba(y), p["titulo"], fontsize=e.pt(32), fontweight="bold",
                                color=p["color"], va="top"), ancho_nota)
        e.encajar(fig, fig.text(x0 + 0.036, arriba(y + 52), p["nota"], fontsize=e.pt(28), color=e.TEXTO, va="top"),
                  ancho_nota)
        y += 140
    e.pie(fig, "Fuente: docs/PILOTO_TERRITORIOS.md (20 nov 2026), con razones por verificar. Rutas y distancias: "
               "cálculo nuestro sobre la red vial del equipo. El km 41 no tiene coordenada con fuente; su distancia "
               "es la del documento. Mapa base © colaboradores de OpenStreetMap (ODbL).", x=x0, y=0.02, ancho=60)
    return e.guardar(fig, NOMBRE, args.salida)


def mapa_propuesta1(fig, args, red, aristas, limites, puntos, acopios, banco, rurales):
    """Solo la propuesta 1: el Banco, los tres CDI de La Macarena y Bajo Tablazo sobre un mismo corredor."""
    p = PROPUESTAS[0]
    cdi = [q for q in puntos if q["comuna"] == p["comuna"] and q["critico"].strip() == "1"]
    filas, km_cdi, lineas = [], [], []
    ax = base_del_mapa(fig, aristas, limites, RECUADRO_SOLO)
    o, s, este, n = RECUADRO_SOLO
    for nombre in (p["comuna"], p["corregimiento"]):
        territorio(ax, limites, nombre, p["color"])
    for q in cdi:
        la, lo = float(q["lat"]), float(q["lon"])
        camino, km, d_nodo = red.ruta(la, lo)
        km_cdi.append(km)
        lineas.append(ruta_en_mapa(ax, red, camino, d_nodo, la, lo, p["color"], rombo=False))
        filas.append({"lugar": q["nombre"], "lat": la, "lon": lo, "origen_coordenada": f"datos_publicos/puntos.csv, "
                      f"id {q['id']}", "km_por_la_red": round(km, 2), "metros_al_nodo_mas_cercano": round(d_nodo)})
        print(f"ruta Banco -> {q['nombre']}: {km:.2f} km; nodo a {d_nodo:.0f} m del lugar")
    la, lo, origen = rurales[p["rural"]]
    camino, km_rural, d_nodo = red.ruta(la, lo)
    lineas.append(ruta_en_mapa(ax, red, camino, d_nodo, la, lo, p["color"]))
    filas.append({"lugar": p["rural"], "lat": la, "lon": lo, "origen_coordenada": origen,
                  "km_por_la_red": round(km_rural, 2), "metros_al_nodo_mas_cercano": round(d_nodo)})
    print(f"ruta Banco -> {p['rural']}: {km_rural:.2f} km; nodo a {d_nodo:.0f} m del lugar")
    escribir_rutas(Path(args.salida) / "datos" / f"{NOMBRE_SOLO}_rutas.csv", filas)

    otros = [q for q in puntos if q["critico"].strip() == "1" and q not in cdi]
    for q in otros:
        ax.scatter(float(q["lon"]), float(q["lat"]), s=110, color=GRIS_PUNTO, edgecolor="white", linewidth=1.5,
                   zorder=4)
    for q in cdi:
        ax.scatter(float(q["lon"]), float(q["lat"]), s=260, color=p["color"], edgecolor="white", linewidth=2,
                   zorder=7)
    for a in acopios:
        ax.scatter(float(a["lon"]), float(a["lat"]), s=620 if a["id"] == "1" else 300, marker="s", color=e.TEXTO,
                   edgecolor="white", linewidth=2.5, zorder=8)
    bx, by = float(banco["lon"]), float(banco["lat"])
    ax.text(bx, by + 0.0028, "Banco", fontsize=e.pt(34), fontweight="bold", color=e.TEXTO, zorder=9, ha="center",
            va="bottom", path_effects=halo(8))
    rango = f"{e.miles(min(km_cdi), 1)} a {e.miles(max(km_cdi), 1)} km"
    cx = np.mean([float(q["lon"]) for q in cdi])
    cy = max(float(q["lat"]) for q in cdi)
    ax.text(cx, cy + 0.0028, f"{len(cdi)} CDI\n{rango}", fontsize=e.pt(30), fontweight="bold", color=p["color"],
            ha="center", va="bottom", zorder=9, linespacing=1.05, path_effects=halo(8))
    ax.text(lo + 0.0030, la, f"{p['rural']}\n{e.miles(km_rural, 1)} km", fontsize=e.pt(30), fontweight="bold",
            color=p["color"], ha="left", va="center", zorder=9, linespacing=1.05, path_effects=halo(8))

    # Nombre de la comuna y del corregimiento, en una caja libre de rutas, puntos y otros rótulos.
    marco = box(o, s, este, n).buffer(-0.002)
    grado_px = (este - o) / 1040                     # grados por píxel del mapa
    fig.canvas.draw()
    ocupado = []
    for t in ax.texts:
        c = t.get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted())
        ocupado.append(box(c.x0, c.y0, c.x1, c.y1))
    obstaculos = unary_union([l.buffer(14 * grado_px) for l in lineas] +
                             [Point(float(q["lon"]), float(q["lat"])).buffer(14 * grado_px) for q in cdi + otros] +
                             [Point(lo, la).buffer(20 * grado_px), Point(bx, by).buffer(24 * grado_px)] + ocupado)
    for nombre, rotulo in ((p["comuna"], "comuna\nLa Macarena"), (p["corregimiento"], "corregimiento\nEl Tablazo")):
        forma = limites[limites["nombre"] == nombre].geometry.iloc[0].intersection(marco)
        t = ax.text(0, 0, rotulo, fontsize=e.pt(28), color=p["color"], ha="center", va="center", zorder=9,
                    linespacing=1.05, path_effects=halo(8))
        caja = e.caja_px(fig, t)
        sitio = sitio_para_rotulo(forma, obstaculos, (caja.width + 12) * grado_px, (caja.height + 12) * grado_px)
        if sitio is None:
            print(f"aviso: no hay sitio libre para el rótulo «{rotulo.replace(chr(10), ' ')}»; va sin él",
                  file=sys.stderr)
            t.remove()
            continue
        t.set_position(sitio)
        obstaculos = obstaculos.union(box(sitio[0] - caja.width * grado_px / 2, sitio[1] - caja.height * grado_px / 2,
                                          sitio[0] + caja.width * grado_px / 2, sitio[1] + caja.height * grado_px / 2))

    cerrar_mapa(ax, RECUADRO_SOLO, [
        (punto(p["color"]), "CDI de La Macarena"),
        (punto(GRIS_PUNTO, 11), "Otro punto crítico"),
        (ACOPIO, "Acopio"),
        (Line2D([], [], color=p["color"], linewidth=ANCHO_RUTA), "Ruta más corta por la red"),
    ])

    x0 = 1110 / e.ANCHO_PX
    fig.text(x0, arriba(55), "La Macarena\ny El Tablazo", fontsize=e.pt(58), fontweight="bold", color=e.TEXTO,
             va="top", linespacing=1.05)
    fig.text(x0, arriba(215), "La propuesta 1 para el piloto.\nDecide el Banco.", fontsize=e.pt(28),
             color=e.CENIZA, va="top", linespacing=1.25)
    for y, cifra, texto in ((340, rango, f"del Banco a los {len(cdi)} CDI de la comuna"),
                            (500, f"{e.miles(km_rural, 1)} km", f"del Banco a {p['rural']},\npor el mismo corredor")):
        fig.text(x0, arriba(y), cifra, fontsize=e.pt(56), fontweight="bold", color=p["color"], va="top")
        fig.text(x0, arriba(y + 78), texto, fontsize=e.pt(30), color=e.TEXTO, va="top", linespacing=1.2)
    e.pie(fig, "Fuente: docs/PILOTO_TERRITORIOS.md, propuesta 1 (20 nov 2026). Rutas y distancias: cálculo "
               f"nuestro sobre la red vial del equipo. El grafo no llega a {p['rural']}, y el último tramo, de "
               f"{e.miles(d_nodo)} m, va punteado. Mapa base © colaboradores de OpenStreetMap (ODbL).",
          x=x0, y=0.02, ancho=60)
    return e.guardar(fig, NOMBRE_SOLO, args.salida)


def main():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--solo", type=int, choices=[1], default=None,
                   help="dibujar solo la propuesta 1, la recomendada (a_territorio_propuesta1)")
    args = p.parse_args()
    familia = e.configurar_fuente(args.fuente)
    ruta_grafo = next((g for g in GRAFOS if g.exists()), None)
    if ruta_grafo is None:
        raise SystemExit("no hay grafo: copie despliegue/grafo/manizales_region.graphml a despacho/cache/")
    acopios = leer_csv(e.RAIZ / "datos_publicos" / "acopios.csv")
    banco = next(a for a in acopios if a["id"] == "1")
    red = Red(ruta_grafo, banco)
    aristas = ox.graph_to_gdfs(red.G, nodes=False, fill_edge_geometry=True)
    limites = gpd.read_file(LIMITES)
    puntos = leer_csv(e.RAIZ / "datos_publicos" / "puntos.csv")
    print(f"fuente tipográfica: {familia}; grafo: {ruta_grafo.relative_to(e.RAIZ)} ({red.G.number_of_nodes()} nodos)")
    dibujar = mapa_propuesta1 if args.solo == 1 else mapa_tres
    e.terminar(dibujar(e.lienzo(), args, red, aristas, limites, puntos, acopios, banco, lugares_rurales()))


if __name__ == "__main__":
    main()
