"""Figura (a): las tres propuestas de territorio para el piloto, con puntos críticos, acopios y rutas por la red.

Uso: python figuras_pitch/scripts/mapa_territorios.py [--fuente FAMILIA] [--salida CARPETA] [--solo 1|2]
Lee  despacho/cache/manizales_region.graphml (o despliegue/grafo/manizales_region.graphml si no está),
     figuras_pitch/datos/limites_osm.geojson (sale de despacho/cache/admin_osm.pkl con extraer_limites.py),
     datos_publicos/puntos.csv, datos_publicos/acopios.csv y datos/semilla/lugares_extra.csv (Bajo Tablazo).
Escribe <salida>/png/a_territorios_piloto.png, <salida>/svg/a_territorios_piloto.svg y las distancias en
<salida>/datos/a_territorios_rutas.csv.

Con --solo 1 dibuja solo la propuesta 1: el corredor del Banco a los tres CDI de La Macarena y a Bajo Tablazo.
Escribe a_territorio_propuesta1 (PNG y SVG) y sus distancias en <salida>/datos/a_territorio_propuesta1_rutas.csv.

Con --solo 2 dibuja solo la propuesta 2, la que eligió Carlos el 21 de noviembre para el piloto: las rutas del Banco
a los cuatro puntos del catálogo en Ciudadela del Norte (dos CDI, un centro de salud y un CISCO) y a Alto Bonito, en
El Manantial. Escribe a_territorio_propuesta2 (PNG y SVG) y sus distancias en
<salida>/datos/a_territorio_propuesta2_rutas.csv.

Adaptada de docs/informe/figuras/scripts/mapa_manizales.py, sin editar ese archivo. Sin teselas de internet: el
fondo es la red vial del equipo y los límites de OpenStreetMap.

Las propuestas, sus territorios y sus razones vienen de docs/PILOTO_TERRITORIOS.md. Las rutas son el camino más
corto por longitud en el grafo dirigido, desde el nodo del Banco hasta el punto de la vía más cercano a cada lugar.
Cada lugar se proyecta sobre la arista más cercana, y la ruta suma el camino hasta el nodo de entrada de esa arista
más el tramo parcial. Si la vía más cercana pasa a más de 100 m, el último tramo, del punto de la vía al lugar, va
punteado. El Kilómetro 41 no tiene coordenada con fuente en el repositorio (lugares/README.md), así que va como
flecha.

Si una distancia redondeada a un decimal no es la que escribe docs/PILOTO_TERRITORIOS.md para ese lugar, la figura
lleva el sello «Distancia a <lugar> por confirmar» y el script imprime un AVISO y sale con código 1. El sello se va
solo cuando el documento y el cálculo coinciden.
"""
import csv
import math
import re
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import networkx as nx
import numpy as np
import osmnx as ox
import shapely
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from shapely.geometry import LineString, Point, box
from shapely.ops import substring, unary_union

import estilo as e

NOMBRE = "a_territorios_piloto"
NOMBRE_SOLO = {1: "a_territorio_propuesta1", 2: "a_territorio_propuesta2"}
GRAFOS = [e.RAIZ / "despacho" / "cache" / "manizales_region.graphml",
          e.RAIZ / "despliegue" / "grafo" / "manizales_region.graphml"]
LIMITES = e.CARPETA / "datos" / "limites_osm.geojson"
# Recuadro del mapa (oeste, sur, este, norte), cuadrado en grados.
RECUADRO = (-75.586, 4.996, -75.456, 5.126)
GRIS_PUNTO = "#B3BDB6"
# Posición a mano de algunos números, si la automática no sirve (vacío: todas son automáticas).
AJUSTE_INSIGNIA = {}
RADIO_INSIGNIA = 0.0037   # grados; el círculo del número mide unos 60 px
# Distancia mínima del centro de un número a un punto, un rombo o un acopio: el círculo del número (unos 32 px de
# radio con su borde blanco) más el radio de un punto (unos 10 px), en grados.
DISTANCIA_A_PUNTOS = 0.0055
ANCHO_RUTA, ANCHO_LIMITE = 7.5, 2.2
METROS_SIN_VIA = 100      # si la vía más cercana pasa más lejos, el tramo final hasta el lugar va punteado
LAT_REF, RADIO_TIERRA = 5.05, 6371000.0   # plano local en metros para proyectar los lugares sobre las vías
DOC_PILOTO = e.RAIZ / "docs" / "PILOTO_TERRITORIOS.md"

PROPUESTAS = [
    {"n": 1, "color": e.AMBAR, "comuna": "La Macarena", "corregimiento": "El Tablazo (Corredor Agroturístico)",
     "titulo": "La Macarena y El Tablazo", "nota": "Días 30 a 60. Tres CDI y la vereda en un corredor.", "orden": 1,
     "rural": "Bajo Tablazo"},
    {"n": 2, "color": e.TINTA, "comuna": "Ciudadela del Norte", "corregimiento": "El Manantial",
     "titulo": "Ciudadela del Norte y El Manantial", "nota": "Días 0 a 30. La comuna más poblada.", "orden": 0,
     "rural": "Alto Bonito"},
    {"n": 3, "color": e.CENIZA, "comuna": "Atardeceres", "corregimiento": None,
     "titulo": "Atardeceres y Kilómetro 41", "nota": "Días 60 a 90. Alertas de lluvia A25 del IDEA (UNAL).", "orden": 2,
     "rural": "La Aurora"},
]

# Figuras de una sola propuesta (--solo). La 1 conserva el recuadro, los rótulos y las posiciones con que se hizo.
# «criticos»: si se dibujan solo los puntos críticos de la comuna (la 1) o todos los del catálogo (la 2, porque
# docs/PILOTO_TERRITORIOS.md cuenta el CISCO, que no es crítico). Los desplazamientos van en grados.
SOLO = {
    1: {"recuadro": (-75.552, 5.0145, -75.485, 5.0815), "criticos": True, "grupo": "CDI",
        "leyenda": "CDI de La Macarena", "titulo": "La Macarena\ny El Tablazo",
        "rotulos": ("comuna\nLa Macarena", "corregimiento\nEl Tablazo"),
        "via_rural": "por el mismo corredor", "banco": (0.0, 0.0028, "center", "bottom"),
        "grupo_arriba": True, "rural": (0.0030, 0.0, "left", "center"), "leyenda_loc": "lower right",
        "y_subtitulo": 215, "subtitulo": "Segunda zona del piloto,\ndel día 30 al 60."},
    2: {"recuadro": (-75.540, 5.050, -75.466, 5.124), "criticos": False, "grupo": "puntos",
        "leyenda": "CDI, centro de salud y CISCO", "titulo": "Ciudadela del Norte\ny El Manantial",
        "rotulos": ("comuna\nCiudadela del Norte", "corregimiento\nEl Manantial"),
        "via_rural": "por la comuna San José", "banco": (0.0, -0.0028, "center", "top"),
        "grupo_arriba": True, "rural": (-0.0030, 0.0, "right", "center"), "leyenda_loc": "upper right",
        "y_subtitulo": 228, "subtitulo": "Primera zona del piloto,\ndel día 0 al 30.", "leyenda_primero": True},
}


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


def a_metros(coords):
    """(lon, lat) en grados a un plano local en metros, equirrectangular alrededor de LAT_REF."""
    k = RADIO_TIERRA * math.cos(math.radians(LAT_REF))
    return [(math.radians(x) * k, math.radians(y) * RADIO_TIERRA) for x, y in coords]


def a_grados(coords):
    k = RADIO_TIERRA * math.cos(math.radians(LAT_REF))
    return [(math.degrees(x / k), math.degrees(y / RADIO_TIERRA)) for x, y in coords]


def coords_arista(G, u, v, datos) -> list:
    """Coordenadas (lon, lat) de una arista, desde u hasta v."""
    if "geometry" not in datos:
        return [(G.nodes[u]["x"], G.nodes[u]["y"]), (G.nodes[v]["x"], G.nodes[v]["y"])]
    coords = list(datos["geometry"].coords)
    xu, yu = G.nodes[u]["x"], G.nodes[u]["y"]
    if (coords[0][0] - xu) ** 2 + (coords[0][1] - yu) ** 2 > (coords[-1][0] - xu) ** 2 + (coords[-1][1] - yu) ** 2:
        coords = coords[::-1]
    return coords


def coords_de_camino(G, camino) -> list:
    """Une la geometría de las aristas del camino en una sola lista de puntos, en el sentido del recorrido."""
    if len(camino) == 1:
        return [(G.nodes[camino[0]]["x"], G.nodes[camino[0]]["y"])]
    puntos = []
    for u, v in zip(camino[:-1], camino[1:]):
        coords = coords_arista(G, u, v, min(G[u][v].values(), key=lambda d: d.get("length", 0)))
        puntos.extend(coords if not puntos else coords[1:])
    return puntos


def sitio_libre(forma, obstaculos, paso=0.0008, intocables=None, radio=0.0):
    """Punto de `forma` más lejos a la vez de su borde y de los obstáculos (rutas, puntos y rótulos).

    Con `intocables`, descarta los puntos que queden a menos de `radio` de ellos.
    """
    x0, y0, x1, y1 = forma.bounds
    mejor, puntaje = forma.representative_point(), -1.0
    for x in np.arange(x0, x1, paso):
        for y in np.arange(y0, y1, paso):
            q = Point(x, y)
            if not forma.contains(q) or (intocables is not None and intocables.distance(q) < radio):
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
    """Grafo vial, las rutas más cortas desde el Banco y el ajuste de cada lugar a la vía más cercana."""

    def __init__(self, ruta_grafo, banco):
        self.G = ox.load_graphml(ruta_grafo)
        self.ids = np.array(list(self.G.nodes))
        self.lat = np.array([self.G.nodes[n]["y"] for n in self.ids])
        self.lon = np.array([self.G.nodes[n]["x"] for n in self.ids])
        self.origen, self.banco_m = self.cercano(float(banco["lat"]), float(banco["lon"]))
        self.dist, self.caminos = nx.single_source_dijkstra(self.G, self.origen, weight="length")
        self.aristas = [(u, v, d["length"], coords_arista(self.G, u, v, d))
                        for u, v, d in self.G.edges(data=True)]
        self.lineas_m = np.array([LineString(a_metros(c)) for *_, c in self.aristas], dtype=object)

    def cercano(self, la, lo):
        return nodo_cercano(self.G, self.ids, self.lat, self.lon, la, lo)

    def ruta(self, la, lo) -> dict:
        """Ruta más corta del Banco al punto de la vía más cercano al lugar.

        El lugar se proyecta sobre la arista más cercana. Se prueban esa arista y su gemela en sentido contrario, y
        la ruta es el camino hasta el nodo de entrada más el tramo parcial hasta la proyección. Devuelve la línea
        de la ruta en grados, los km por la red y los metros del lugar a la vía. Para comparar, también los metros
        al nodo más cercano y los km hasta ese nodo, que era el método anterior.
        """
        p = Point(a_metros([(lo, la)])[0])
        lejos = shapely.distance(self.lineas_m, p)
        nodo, d_nodo = self.cercano(la, lo)
        resultado = {"m_nodo": d_nodo, "km_nodo": self.dist.get(nodo, math.inf) / 1000}
        mejor = None
        for i in np.flatnonzero(lejos <= lejos.min() + 1.0):
            u, _, largo, _ = self.aristas[i]
            if u not in self.dist:
                continue
            fraccion = self.lineas_m[i].project(p, normalized=True)
            total = self.dist[u] + fraccion * largo
            if mejor is None or total < mejor[0]:
                mejor = (total, i, fraccion)
        if mejor is None:        # ninguna de las aristas más cercanas se alcanza desde el Banco: nodo más cercano
            coords = coords_de_camino(self.G, self.caminos[nodo])
            return {**resultado, "linea": LineString(coords * (2 if len(coords) == 1 else 1)),
                    "km": resultado["km_nodo"], "m_via": d_nodo}
        total, i, fraccion = mejor
        coords = coords_de_camino(self.G, self.caminos[self.aristas[i][0]])
        tramo = substring(self.lineas_m[i], 0, fraccion, normalized=True)
        if fraccion > 0 and tramo.length > 0:
            coords += a_grados(list(tramo.coords))[1:]
        if len(coords) == 1:
            coords = coords * 2
        return {**resultado, "linea": LineString(coords), "km": total / 1000, "m_via": float(lejos.min())}


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


def ruta_en_mapa(ax, ruta, la, lo, color, rombo=True):
    linea = ruta["linea"]
    xs, ys = linea.xy
    ax.plot(xs, ys, color=color, linewidth=ANCHO_RUTA, zorder=5, solid_capstyle="round", solid_joinstyle="round",
            path_effects=halo(13))
    if ruta["m_via"] > METROS_SIN_VIA:      # la vía no llega: tramo final punteado hasta el lugar
        fin_x, fin_y = linea.coords[-1]
        ax.plot([fin_x, lo], [fin_y, la], color=color, linewidth=4.5, linestyle=(0, (1.5, 1.5)), zorder=5)
    if rombo:
        ax.scatter([lo], [la], s=440, marker="D", color=color, edgecolor="white", linewidth=2.5, zorder=7)
    return linea


def fila_de_ruta(lugar, la, lo, origen, ruta) -> dict:
    """Fila del CSV de distancias. Las dos últimas columnas son del método anterior, para comparar."""
    return {"lugar": lugar, "lat": la, "lon": lo, "origen_coordenada": origen, "km_por_la_red": round(ruta["km"], 3),
            "metros_a_la_via": round(ruta["m_via"]), "metros_al_nodo_mas_cercano": round(ruta["m_nodo"]),
            "km_hasta_el_nodo_mas_cercano": round(ruta["km_nodo"], 3)}


def frase_sin_via(rutas: dict) -> str:
    """Frase del pie para los lugares a los que la vía no llega, con su tramo punteado. Vacía si no hay."""
    lejos = [(lugar, r["m_via"]) for lugar, r in rutas.items() if r["m_via"] > METROS_SIN_VIA]
    if not lejos:
        return ""
    if len(lejos) == 1:
        lugar, m = lejos[0]
        return f" La vía no llega a {lugar}, y el último tramo, de {e.miles(m)} m, va punteado."
    nombres = ", ".join(lugar for lugar, _ in lejos[:-1]) + f" ni a {lejos[-1][0]}"
    return f" La vía no llega a {nombres}, y el último tramo de esas rutas va punteado."


def informar(lugar, ruta):
    print(f"ruta Banco -> {lugar}: {ruta['km']:.2f} km; vía a {ruta['m_via']:.0f} m del lugar "
          f"(hasta el nodo más cercano, a {ruta['m_nodo']:.0f} m: {ruta['km_nodo']:.2f} km)")


def cifras_del_documento(propuesta: int) -> set[str] | None:
    """Cifras en km de la sección de una propuesta en docs/PILOTO_TERRITORIOS.md.

    «9,3 km» da «9,3», y «entre 2,9 y 3,3 km» da «2,9» y «3,3». Devuelve None si el documento no está.
    """
    try:
        texto = DOC_PILOTO.read_text(encoding="utf-8")
    except OSError:
        return None
    seccion = re.search(rf"^## {propuesta}\..*?(?=^## |\Z)", texto, flags=re.S | re.M)
    pares = re.findall(r"(?<![\d.,])(\d+(?:,\d+)?)(?: (?:y|a) (\d+(?:,\d+)?))? km\b",
                       seccion.group(0) if seccion else texto)
    return {c for par in pares for c in par if c}


def por_confirmar(cifras) -> list:
    """De las cifras que muestra la figura, como (propuesta, a qué, km con un decimal), las que el documento no
    tiene en la sección de esa propuesta."""
    faltan = []
    for n, que, km in cifras:
        doc = cifras_del_documento(n)
        if doc is None:
            print(f"aviso: no encontré {DOC_PILOTO}; no comparo las distancias", file=sys.stderr)
            return []
        if km not in doc:
            faltan.append((n, que, km, ", ".join(sorted(doc)) or "ninguna"))
    return faltan


def sello_y_avisos(fig, nombre, faltan, x0, y_px):
    """Sello «Distancia a <lugar> por confirmar» en el panel derecho y los AVISO que lo explican."""
    if not faltan:
        return [], None
    lugares = list(dict.fromkeys(que for _, que, _, _ in faltan))
    texto = f"Distancia a {lugares[0]} por confirmar" if len(lugares) == 1 else "Distancias por confirmar"
    s = fig.text(x0 + 0.004, arriba(y_px), texto, fontsize=e.pt(30), fontweight="bold", color=e.TEXTO, ha="left",
                 va="top", bbox=dict(boxstyle="round,pad=0.45", facecolor=e.FONDO, edgecolor=e.AMBAR, linewidth=3))
    avisos = [f"{nombre}: la figura da {km} km a {que}, y la propuesta {n} de docs/PILOTO_TERRITORIOS.md no tiene "
              f"esa cifra (tiene {doc} km). Lleva el sello «{texto}» hasta que el documento la tenga"
              for n, que, km, doc in faltan]
    return avisos, s


def cerrar_mapa(ax, recuadro, convenciones, loc="lower right"):
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
    ley = ax.legend(handles=[c for c, _ in convenciones], labels=[t for _, t in convenciones], loc=loc,
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
        rutas[nombre] = red.ruta(la, lo)
        filas.append(fila_de_ruta(nombre, la, lo, origen, rutas[nombre]))
        informar(nombre, rutas[nombre])
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
        la, lo, _ = rurales[p["rural"]]
        lineas_ruta.append(ruta_en_mapa(ax, rutas[p["rural"]], la, lo, p["color"]))

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
        km = rutas[p["rural"]]["km"]
        la, lo, _ = rurales[p["rural"]]
        dx, dy, ha, va = desplazamientos[p["rural"]]
        ax.text(lo + dx, la + dy, f"{p['rural']}\n{e.miles(km, 1)} km", fontsize=e.pt(28), color=e.color_de_texto(p["color"]),
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
                              [Point(lo, la) for la, lo, _ in rurales.values()] +
                              [Point(float(a["lon"]), float(a["lat"])) for a in acopios])
    obstaculos = unary_union(lineas_ruta + [solo_puntos])
    for p in PROPUESTAS:
        for nombre in (p["comuna"], p["corregimiento"]):
            if not nombre:
                continue
            forma = limites[limites["nombre"] == nombre].geometry.iloc[0].intersection(marco)
            x, y, holgura = sitio_libre(forma, obstaculos, intocables=solo_puntos, radio=DISTANCIA_A_PUNTOS)
            if holgura < RADIO_INSIGNIA:          # sin sitio libre: se permite tapar la ruta, nunca un punto
                x, y, holgura = sitio_libre(forma, solo_puntos, intocables=solo_puntos, radio=DISTANCIA_A_PUNTOS)
                if holgura < 0:                   # ni así cabe: el sitio más libre de puntos que haya
                    x, y, holgura = sitio_libre(forma, solo_puntos)
                    print(f"aviso: el número de {nombre} queda a menos de su radio de un punto", file=sys.stderr)
            x, y = AJUSTE_INSIGNIA.get(nombre, (x, y))
            ax.text(x, y, str(p["n"]), fontsize=e.pt(34), fontweight="bold", color=e.blanco_o_texto(p["color"]), ha="center",
                    va="center", zorder=11,
                    bbox=dict(boxstyle="circle,pad=0.28", facecolor=p["color"], edgecolor="white", linewidth=3))

    cerrar_mapa(ax, RECUADRO, [
        (tuple(punto(p["color"]) for p in PROPUESTAS), "Punto crítico de una propuesta"),
        (punto(GRIS_PUNTO, 10), "Otro punto crítico"),
        (ACOPIO, "Acopio"),
        (Line2D([], [], color=e.TEXTO, linewidth=ANCHO_RUTA), "Ruta más corta por la red"),
    ])

    # Panel derecho: título, propuestas y fuentes. Posiciones en píxeles desde arriba.
    x0 = 1110 / e.ANCHO_PX
    fig.text(x0, arriba(55), "El piloto crece\npor zonas", fontsize=e.pt(58), fontweight="bold",
             color=e.TEXTO, va="top", linespacing=1.05)
    fig.text(x0, arriba(215), "Una zona nueva cada 30 días,\nsi la anterior cumplió y el Banco acepta.", fontsize=e.pt(28),
             color=e.CENIZA, va="top", linespacing=1.25)
    y = 330
    ancho_nota = e.ANCHO_PX - 40 - (x0 + 0.036) * e.ANCHO_PX
    for p in sorted(PROPUESTAS, key=lambda p: p["orden"]):
        fig.text(x0 + 0.013, arriba(y + 22), str(p["n"]), fontsize=e.pt(30), fontweight="bold", color=e.blanco_o_texto(p["color"]),
                 ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.25", facecolor=p["color"],
                                                     edgecolor="none"))
        e.encajar(fig, fig.text(x0 + 0.036, arriba(y), p["titulo"], fontsize=e.pt(32), fontweight="bold",
                                color=e.color_de_texto(p["color"]), va="top"), ancho_nota)
        e.encajar(fig, fig.text(x0 + 0.036, arriba(y + 52), p["nota"], fontsize=e.pt(28), color=e.TEXTO, va="top",
                                fontweight="bold" if p["orden"] == 0 else "normal"),
                  ancho_nota)
        y += 140
    cifras = [(p["n"], p["rural"], e.miles(rutas[p["rural"]]["km"], 1)) for p in PROPUESTAS]
    avisos, _ = sello_y_avisos(fig, NOMBRE, por_confirmar(cifras), x0, 745)
    e.pie(fig, "Fuente: docs/PILOTO_TERRITORIOS.md (21 nov 2026), con razones por verificar. Rutas y distancias: "
               f"cálculo nuestro sobre la red vial del equipo.{frase_sin_via(rutas)} El km 41 no tiene coordenada "
               "con fuente; su distancia es la del documento. Mapa base © colaboradores de OpenStreetMap (ODbL).",
          x=x0, y=0.02, ancho=60)
    return e.guardar(fig, NOMBRE, args.salida, avisos_extra=avisos)


def mapa_propuesta(fig, args, red, aristas, limites, puntos, acopios, banco, rurales, numero):
    """Una sola propuesta: el Banco, los puntos de su comuna y su lugar rural, con las rutas por la red.

    La 1 dibuja los tres CDI de La Macarena y Bajo Tablazo sobre un mismo corredor. La 2 dibuja los cuatro puntos del
    catálogo en Ciudadela del Norte y Alto Bonito, cuya ruta sale por la comuna San José.
    """
    p, cfg, nombre_fig = PROPUESTAS[numero - 1], SOLO[numero], NOMBRE_SOLO[numero]
    cdi = [q for q in puntos if q["comuna"] == p["comuna"] and (q["critico"].strip() == "1" or not cfg["criticos"])]
    filas, km_cdi, lineas = [], [], []
    ax = base_del_mapa(fig, aristas, limites, cfg["recuadro"])
    o, s, este, n = cfg["recuadro"]
    for nombre in (p["comuna"], p["corregimiento"]):
        territorio(ax, limites, nombre, p["color"])
    for q in cdi:
        la, lo = float(q["lat"]), float(q["lon"])
        ruta = red.ruta(la, lo)
        km_cdi.append(ruta["km"])
        lineas.append(ruta_en_mapa(ax, ruta, la, lo, p["color"], rombo=False))
        filas.append(fila_de_ruta(q["nombre"], la, lo, f"datos_publicos/puntos.csv, id {q['id']}", ruta))
        informar(q["nombre"], ruta)
    la, lo, origen = rurales[p["rural"]]
    ruta = red.ruta(la, lo)
    km_rural = ruta["km"]
    lineas.append(ruta_en_mapa(ax, ruta, la, lo, p["color"]))
    filas.append(fila_de_ruta(p["rural"], la, lo, origen, ruta))
    informar(p["rural"], ruta)
    escribir_rutas(Path(args.salida) / "datos" / f"{nombre_fig}_rutas.csv", filas)

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
    dx, dy, ha, va = cfg["banco"]
    ax.text(bx + dx, by + dy, "Banco", fontsize=e.pt(34), fontweight="bold", color=e.TEXTO, zorder=9, ha=ha,
            va=va, path_effects=halo(8))
    rango = f"{e.miles(min(km_cdi), 1)} a {e.miles(max(km_cdi), 1)} km"
    cx = np.mean([float(q["lon"]) for q in cdi])
    if cfg["grupo_arriba"]:
        cy, va = max(float(q["lat"]) for q in cdi) + 0.0028, "bottom"
    else:
        cy, va = min(float(q["lat"]) for q in cdi) - 0.0028, "top"
    ax.text(cx, cy, f"{len(cdi)} {cfg['grupo']}\n{rango}", fontsize=e.pt(30), fontweight="bold", color=e.color_de_texto(p["color"]),
            ha="center", va=va, zorder=9, linespacing=1.05, path_effects=halo(8))
    dx, dy, ha, va = cfg["rural"]
    ax.text(lo + dx, la + dy, f"{p['rural']}\n{e.miles(km_rural, 1)} km", fontsize=e.pt(30), fontweight="bold",
            color=e.color_de_texto(p["color"]), ha=ha, va=va, zorder=9, linespacing=1.05, path_effects=halo(8))

    convenciones = [
        (punto(p["color"]), cfg["leyenda"]),
        (punto(GRIS_PUNTO, 11), "Otro punto crítico"),
        (ACOPIO, "Acopio"),
        (Line2D([], [], color=p["color"], linewidth=ANCHO_RUTA), "Ruta más corta por la red"),
    ]
    # Con «leyenda_primero», la leyenda se dibuja antes que los nombres de la comuna y del corregimiento, para que
    # ninguno quede debajo de ella con una letra más ancha. La 1 conserva el orden con que se hizo.
    if cfg.get("leyenda_primero"):
        cerrar_mapa(ax, cfg["recuadro"], convenciones, loc=cfg["leyenda_loc"])

    # Nombre de la comuna y del corregimiento, en una caja libre de rutas, puntos y otros rótulos.
    marco = box(o, s, este, n).buffer(-0.002)
    grado_px = (este - o) / 1040                     # grados por píxel del mapa
    fig.canvas.draw()
    ocupado = []
    for t in ax.texts:
        c = t.get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted())
        ocupado.append(box(c.x0, c.y0, c.x1, c.y1))
    if cfg.get("leyenda_primero"):
        c = ax.get_legend().get_window_extent(fig.canvas.get_renderer()).transformed(ax.transData.inverted())
        ocupado.append(box(c.x0, c.y0, c.x1, c.y1))
    obstaculos = unary_union([l.buffer(14 * grado_px) for l in lineas] +
                             [Point(float(q["lon"]), float(q["lat"])).buffer(14 * grado_px) for q in cdi + otros] +
                             [Point(lo, la).buffer(20 * grado_px), Point(bx, by).buffer(24 * grado_px)] + ocupado)
    for nombre, rotulo in zip((p["comuna"], p["corregimiento"]), cfg["rotulos"]):
        forma = limites[limites["nombre"] == nombre].geometry.iloc[0].intersection(marco)
        t = ax.text(0, 0, rotulo, fontsize=e.pt(28), color=e.color_de_texto(p["color"]), ha="center", va="center", zorder=9,
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

    if not cfg.get("leyenda_primero"):
        cerrar_mapa(ax, cfg["recuadro"], convenciones, loc=cfg["leyenda_loc"])

    x0 = 1110 / e.ANCHO_PX
    fig.text(x0, arriba(55), cfg["titulo"], fontsize=e.pt(58), fontweight="bold", color=e.TEXTO,
             va="top", linespacing=1.05)
    fig.text(x0, arriba(cfg["y_subtitulo"]), cfg["subtitulo"],
             fontsize=e.pt(28), color=e.CENIZA, va="top", linespacing=1.25)
    for y, cifra, texto in ((340, rango, f"del Banco a los {len(cdi)} {cfg['grupo']} de la comuna"),
                            (500, f"{e.miles(km_rural, 1)} km", f"del Banco a {p['rural']},\n{cfg['via_rural']}")):
        fig.text(x0, arriba(y), cifra, fontsize=e.pt(56), fontweight="bold", color=e.color_de_texto(p["color"]), va="top")
        fig.text(x0, arriba(y + 78), texto, fontsize=e.pt(30), color=e.TEXTO, va="top", linespacing=1.2)
    que = f"los {cfg['grupo']}"
    cifras = [(p["n"], que, e.miles(min(km_cdi), 1)), (p["n"], que, e.miles(max(km_cdi), 1)),
              (p["n"], p["rural"], e.miles(km_rural, 1))]
    avisos, _ = sello_y_avisos(fig, nombre_fig, por_confirmar(cifras), x0, 700)
    e.pie(fig, f"Fuente: docs/PILOTO_TERRITORIOS.md, propuesta {numero} (21 nov 2026). Rutas y distancias: cálculo "
               "nuestro sobre la red vial del equipo, hasta el punto de la vía más cercano a cada lugar."
               f"{frase_sin_via({p['rural']: ruta})} Mapa base © colaboradores de OpenStreetMap (ODbL).",
          x=x0, y=0.02, ancho=60)
    return e.guardar(fig, nombre_fig, args.salida, avisos_extra=avisos)


def main():
    p = e.argumentos(__doc__.splitlines()[0])
    p.add_argument("--solo", type=int, choices=sorted(SOLO), default=None,
                   help="dibujar solo una propuesta: 1 (a_territorio_propuesta1) o 2, la elegida para el piloto "
                        "(a_territorio_propuesta2)")
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
    datos = (e.lienzo(), args, red, aristas, limites, puntos, acopios, banco, lugares_rurales())
    e.terminar(mapa_propuesta(*datos, args.solo) if args.solo else mapa_tres(*datos))


if __name__ == "__main__":
    main()
