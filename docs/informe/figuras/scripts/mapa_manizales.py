"""Figura 1 del informe corto: red vial de Manizales, puntos de entrega y acopios.

Uso: /home/claude/venv-dx/bin/python docs/informe/figuras/scripts/mapa_manizales.py
Lee  despliegue/grafo/manizales_region.graphml, datos_publicos/puntos.csv y datos_publicos/acopios.csv.
Escribe docs/informe/figuras/mapa_manizales.pdf.

Las flechas del borde solo indican la dirección de los dos corredores cerrados tras el sismo.
No marcan el sitio del cierre, que queda fuera del mapa.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import osmnx as ox

RAIZ = Path(__file__).resolve().parents[4]          # .../despachoX
INFORME = RAIZ / "docs" / "informe"
FUENTES = INFORME / "fuentes"
SALIDA = INFORME / "figuras" / "mapa_manizales.pdf"

TINTA, AMBAR, CREMA, CENIZA = "#1F5C4A", "#D9982B", "#E4EADB", "#5C6A62"
GRIS_RED = "#D3D8D0"

for ttf in FUENTES.glob("AncizarSerif-*.ttf"):
    font_manager.fontManager.addfont(str(ttf))
plt.rcParams.update({"font.family": "Ancizar Serif", "font.size": 7.5, "pdf.fonttype": 42})


def leer_csv(ruta):
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


puntos = leer_csv(RAIZ / "datos_publicos" / "puntos.csv")
acopios = leer_csv(RAIZ / "datos_publicos" / "acopios.csv")
criticos = [p for p in puntos if p["critico"].strip() == "1"]
otros = [p for p in puntos if p["critico"].strip() != "1"]
print(f"puntos: {len(puntos)} (críticos {len(criticos)}, otros {len(otros)}); acopios: {len(acopios)}")

lats = [float(p["lat"]) for p in puntos] + [float(a["lat"]) for a in acopios]
lons = [float(p["lon"]) for p in puntos] + [float(a["lon"]) for a in acopios]
margen = 0.012
lat0, lat1 = min(lats) - margen, max(lats) + margen
lon0, lon1 = min(lons) - margen, max(lons) + margen

G = ox.load_graphml(RAIZ / "despliegue" / "grafo" / "manizales_region.graphml")
aristas = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
aristas = aristas.cx[lon0:lon1, lat0:lat1]
print(f"aristas dentro del recuadro: {len(aristas)}")

fig, ax = plt.subplots(figsize=(3.75, 3.9))
aristas.plot(ax=ax, color=GRIS_RED, linewidth=0.28, zorder=1, rasterized=True)

ax.scatter([float(p["lon"]) for p in otros], [float(p["lat"]) for p in otros], s=10,
           color=CENIZA, edgecolor="white", linewidth=0.5, zorder=3,
           label=f"Otro punto de entrega ({len(otros)})")
ax.scatter([float(p["lon"]) for p in criticos], [float(p["lat"]) for p in criticos], s=13,
           color=AMBAR, edgecolor="white", linewidth=0.5, zorder=4,
           label=f"Punto crítico ({len(criticos)})")
ax.scatter([float(a["lon"]) for a in acopios], [float(a["lat"]) for a in acopios], s=34, marker="s",
           color=TINTA, edgecolor="white", linewidth=0.7, zorder=5, label=f"Acopio ({len(acopios)})")

# Flechas en el borde: solo dirección, sin ubicar el cierre.
flecha = dict(arrowstyle="-|>", color=TINTA, linewidth=1.3, mutation_scale=9)
ax.annotate("", xy=(lon0 + 0.002, lat0 + 0.002), xytext=(lon0 + 0.020, lat0 + 0.020),
            arrowprops=flecha, zorder=6)
ax.text(lon0 + 0.022, lat0 + 0.010, "Hacia Chinchiná y Pereira\n(cierre en km 22 a 24)",
        color=TINTA, fontsize=7, va="bottom", ha="left", zorder=6,
        bbox=dict(boxstyle="square,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85))
ylet = lat0 + 0.42 * (lat1 - lat0)
ax.annotate("", xy=(lon1 - 0.001, ylet), xytext=(lon1 - 0.019, ylet), arrowprops=flecha, zorder=6)
ax.text(lon1 - 0.001, ylet - 0.004, "Hacia Letras y Fresno\n(cierre en km 36 a 40)",
        color=TINTA, fontsize=7, va="top", ha="right", zorder=6,
        bbox=dict(boxstyle="square,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85))

ax.set_xlim(lon0, lon1)
ax.set_ylim(lat0, lat1)
ax.set_aspect(1.0)
ax.set_xticks([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_yticks([])
for borde in ax.spines.values():
    borde.set_color(CENIZA)
    borde.set_linewidth(0.6)
leyenda = ax.legend(loc="upper left", frameon=True, fontsize=7, handletextpad=0.3, borderpad=0.5)
leyenda.get_frame().set_edgecolor("none")
leyenda.get_frame().set_alpha(0.9)
# La atribución de OpenStreetMap va en el pie de la figura, en informe_corto.tex.

fig.tight_layout(pad=0.2)
fig.savefig(SALIDA, dpi=300, bbox_inches="tight", pad_inches=0.03)
print(f"escrito {SALIDA}")
