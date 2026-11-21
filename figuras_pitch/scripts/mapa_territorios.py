"""Figura (a): las tres propuestas de territorio para el piloto, con puntos críticos, acopios y rutas por la red.

Uso: python figuras_pitch/scripts/mapa_territorios.py [--fuente FAMILIA] [--salida CARPETA]
Lee  despacho/cache/manizales_region.graphml (o despliegue/grafo/manizales_region.graphml si no está),
     figuras_pitch/datos/limites_osm.geojson (sale de despacho/cache/admin_osm.pkl con extraer_limites.py),
     datos_publicos/puntos.csv, datos_publicos/acopios.csv y datos/semilla/lugares_extra.csv (Bajo Tablazo).
Escribe <salida>/png/a_territorios_piloto.png, <salida>/svg/a_territorios_piloto.svg y las distancias en
<salida>/datos/a_territorios_rutas.csv.

Adaptada de docs/informe/figuras/scripts/mapa_manizales.py, sin editar ese archivo. Sin teselas de internet: el
fondo es la red vial del equipo y los límites de OpenStreetMap.

Las propuestas, sus territorios y sus razones vienen de docs/PILOTO_TERRITORIOS.md. Las rutas son el camino más
corto por longitud en el grafo dirigido, desde el nodo del Banco hasta el nodo más cercano a cada lugar rural.
El Kilómetro 41 no tiene coordenada con fuente en el repositorio (lugares/README.md), así que va como flecha.
"""
import csv
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import networkx as nx
import numpy as np
import osmnx as ox
from matplotlib.lines import Line2D
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

import estilo as e

NOMBRE = "a_territorios_piloto"
GRAFOS = [e.RAIZ / "despacho" / "cache" / "manizales_region.graphml",
          e.RAIZ / "despliegue" / "grafo" / "manizales_region.graphml"]
LIMITES = e.CARPETA / "datos" / "limites_osm.geojson"
# Recuadro del mapa (oeste, sur, este, norte), cuadrado en grados.
RECUADRO = (-75.586, 4.996, -75.456, 5.126)
GRIS_PUNTO = "#B9B4C0"
# Posición a mano de algunos números, si la automática no sirve (vacío: todas son automáticas).
AJUSTE_INSIGNIA = {}
RADIO_INSIGNIA = 0.0037   # grados; el círculo del número mide unos 60 px

PROPUESTAS = [
    {"n": 1, "color": e.TINTA, "comuna": "La Macarena", "corregimiento": "El Tablazo (Corredor Agroturístico)",
     "titulo": "La Macarena y El Tablazo", "nota": "Recomendada. Tres CDI y la vereda\nsobre un mismo corredor.",
     "rural": "Bajo Tablazo"},
    {"n": 2, "color": e.AMBAR, "comuna": "Ciudadela del Norte", "corregimiento": "El Manantial",
     "titulo": "Ciudadela del Norte y El Manantial",
     "nota": "La comuna más poblada. La ruta a\nAlto Bonito sale por la comuna San José.", "rural": "Alto Bonito"},
    {"n": 3, "color": e.CENIZA, "comuna": "Atardeceres", "corregimiento": None,
     "titulo": "Atardeceres y Kilómetro 41", "nota": "Probaría el A25 de la UNAL. El km 41\nqueda a 36,4 km, por La Aurora.",
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


def halo(ancho=6):
    return [pe.withStroke(linewidth=ancho, foreground="white")]


def main():
    args = e.argumentos(__doc__.splitlines()[0]).parse_args()
    familia = e.configurar_fuente(args.fuente)
    ruta_grafo = next((g for g in GRAFOS if g.exists()), None)
    if ruta_grafo is None:
        raise SystemExit("no hay grafo: copie despliegue/grafo/manizales_region.graphml a despacho/cache/")
    G = ox.load_graphml(ruta_grafo)
    ids = np.array(list(G.nodes))
    lat = np.array([G.nodes[n]["y"] for n in ids])
    lon = np.array([G.nodes[n]["x"] for n in ids])
    aristas = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
    o, s, este, n = RECUADRO
    aristas = aristas.cx[o - 0.01:este + 0.01, s - 0.01:n + 0.01]
    limites = gpd.read_file(LIMITES)
    puntos = leer_csv(e.RAIZ / "datos_publicos" / "puntos.csv")
    acopios = leer_csv(e.RAIZ / "datos_publicos" / "acopios.csv")
    rurales = lugares_rurales()
    print(f"fuente tipográfica: {familia}; grafo: {ruta_grafo.relative_to(e.RAIZ)} "
          f"({G.number_of_nodes()} nodos); aristas en el recuadro: {len(aristas)}")

    # Rutas desde el Banco (acopio 1).
    banco = next(a for a in acopios if a["id"] == "1")
    nodo_banco, _ = nodo_cercano(G, ids, lat, lon, float(banco["lat"]), float(banco["lon"]))
    rutas, filas = {}, []
    for nombre, (la, lo, origen) in rurales.items():
        nodo, d_nodo = nodo_cercano(G, ids, lat, lon, la, lo)
        camino = nx.shortest_path(G, nodo_banco, nodo, weight="length")
        km = nx.path_weight(G, camino, weight="length") / 1000
        rutas[nombre] = (camino, km, d_nodo)
        filas.append({"lugar": nombre, "lat": la, "lon": lo, "origen_coordenada": origen,
                      "km_por_la_red": round(km, 2), "metros_al_nodo_mas_cercano": round(d_nodo)})
        print(f"ruta Banco -> {nombre}: {km:.2f} km; nodo a {d_nodo:.0f} m del lugar")
    carpeta_datos = Path(args.salida) / "datos"
    carpeta_datos.mkdir(parents=True, exist_ok=True)
    with open(carpeta_datos / "a_territorios_rutas.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    fig = e.lienzo()
    lado = 1040
    ax = fig.add_axes([20 / e.ANCHO_PX, 20 / e.ALTO_PX, lado / e.ANCHO_PX, lado / e.ALTO_PX])
    aristas.plot(ax=ax, color=e.GRIS_RED, linewidth=0.55, zorder=1, rasterized=True)  # SVG liviano
    comunas = limites[limites["clase"] == "comuna"]
    comunas.boundary.plot(ax=ax, color=e.CENIZA, linewidth=0.8, alpha=0.6, zorder=2)
    limites[limites["clase"] == "corregimiento"].boundary.plot(ax=ax, color=e.CENIZA, linewidth=1.0,
                                                               linestyle=(0, (4, 3)), alpha=0.6, zorder=2)
    color_comuna = {}
    for p in PROPUESTAS:
        color_comuna[p["comuna"]] = p["color"]
        for nombre in (p["comuna"], p["corregimiento"]):
            if not nombre:
                continue
            poli = limites[limites["nombre"] == nombre]
            poli.plot(ax=ax, color=p["color"], alpha=0.16, zorder=2)
            poli.boundary.plot(ax=ax, color=p["color"], linewidth=3.5, zorder=3)

    # Rutas por la red, del color de su propuesta, con la geometría de cada arista. Se dibujan de la 3 a la 1
    # para que la propuesta recomendada quede encima donde las rutas comparten calles.
    lineas_ruta = []
    for p in reversed(PROPUESTAS):
        camino, km, d_nodo = rutas[p["rural"]]
        linea = linea_de_ruta(G, camino)
        lineas_ruta.append(linea)
        xs, ys = linea.xy
        ax.plot(xs, ys, color=p["color"], linewidth=5.5, zorder=5, solid_capstyle="round",
                solid_joinstyle="round", path_effects=halo(10))
        la, lo, _ = rurales[p["rural"]]
        if d_nodo > 100:      # el grafo no llega: tramo final punteado hasta el lugar
            fin_x, fin_y = G.nodes[camino[-1]]["x"], G.nodes[camino[-1]]["y"]
            ax.plot([fin_x, lo], [fin_y, la], color=p["color"], linewidth=4, linestyle=(0, (1.5, 1.5)), zorder=5)
        ax.scatter([lo], [la], s=440, marker="D", color=p["color"], edgecolor="white", linewidth=2.5, zorder=7)

    # Puntos críticos y acopios.
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
    convenciones = [
        Line2D([], [], marker="o", linestyle="none", markersize=13, color=e.TINTA, markeredgecolor="white",
               label="Punto crítico"),
        Line2D([], [], marker="s", linestyle="none", markersize=16, color=e.TEXTO, markeredgecolor="white",
               label="Acopio"),
        Line2D([], [], color=e.TEXTO, linewidth=5, label="Ruta más corta por la red"),
    ]
    ley = ax.legend(handles=convenciones, loc="lower right", fontsize=e.pt(26), frameon=True, borderpad=0.6,
                    handletextpad=0.5, labelspacing=0.4)
    ley.get_frame().set_edgecolor(e.CENIZA)
    ley.get_frame().set_alpha(0.95)
    ley.set_zorder(12)

    # Panel derecho: título, propuestas y fuentes. Posiciones en píxeles desde arriba.
    x0 = 1110 / e.ANCHO_PX

    def arriba(px):
        return 1 - px / e.ALTO_PX

    fig.text(x0, arriba(55), "Tres territorios\npara el piloto", fontsize=e.pt(58), fontweight="bold",
             color=e.TEXTO, va="top", linespacing=1.05)
    fig.text(x0, arriba(215), "Cada uno une una comuna y un corregimiento.\nElige el Banco, según dónde tenga "
             "más organizaciones.", fontsize=e.pt(28), color=e.CENIZA, va="top", linespacing=1.25)
    y = 330
    for p in PROPUESTAS:
        fig.text(x0 + 0.013, arriba(y + 22), str(p["n"]), fontsize=e.pt(30), fontweight="bold", color="white",
                 ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.25", facecolor=p["color"],
                                                     edgecolor="none"))
        fig.text(x0 + 0.036, arriba(y), p["titulo"], fontsize=e.pt(32), fontweight="bold", color=p["color"],
                 va="top")
        fig.text(x0 + 0.036, arriba(y + 52), p["nota"], fontsize=e.pt(28), color=e.TEXTO, va="top",
                 linespacing=1.2)
        y += 165
    e.pie(fig, "Fuente: docs/PILOTO_TERRITORIOS.md (20 nov 2026), con razones por verificar. Rutas y distancias: "
               "cálculo nuestro sobre la red vial del equipo. El km 41 no tiene coordenada con fuente; su distancia "
               "es la del documento. Mapa base © colaboradores de OpenStreetMap (ODbL).", x=x0, y=0.02, ancho=60)
    e.guardar(fig, NOMBRE, args.salida)


if __name__ == "__main__":
    main()
