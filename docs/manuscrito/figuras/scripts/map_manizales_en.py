"""Figure 2 of the manuscript: road network of Manizales, delivery points and depots (English labels).

Usage (from any folder):
    nice -n 19 /home/claude/venv-dx/bin/python docs/manuscrito/figuras/scripts/map_manizales_en.py
Reads  despliegue/grafo/manizales_region.graphml, datos_publicos/puntos.csv, datos_publicos/acopios.csv.
Writes docs/manuscrito/figuras/map_manizales.pdf.

Adapted from docs/informe/figuras/scripts/mapa_manizales.py (Spanish version for the context report),
with default fonts so that it runs without the report's font files. The arrows on the border only show
the direction of the two corridors closed after the earthquake; the closures lie outside the map.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import osmnx as ox

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs" / "manuscrito" / "figuras" / "map_manizales.pdf"
INK, AMBER, GREY, NET = "#4F4086", "#A36752", "#6E6878", "#CFCCD3"
plt.rcParams.update({"font.size": 7.5, "pdf.fonttype": 42})


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


points = read_csv(ROOT / "datos_publicos" / "puntos.csv")
depots = read_csv(ROOT / "datos_publicos" / "acopios.csv")
critical = [p for p in points if p["critico"].strip() == "1"]
other = [p for p in points if p["critico"].strip() != "1"]
print(f"points: {len(points)} (critical {len(critical)}, other {len(other)}); depots: {len(depots)}")

lats = [float(p["lat"]) for p in points] + [float(a["lat"]) for a in depots]
lons = [float(p["lon"]) for p in points] + [float(a["lon"]) for a in depots]
pad = 0.012
lat0, lat1 = min(lats) - pad, max(lats) + pad
lon0, lon1 = min(lons) - pad, max(lons) + pad

G = ox.load_graphml(ROOT / "despliegue" / "grafo" / "manizales_region.graphml")
edges = ox.graph_to_gdfs(G, nodes=False, fill_edge_geometry=True)
edges = edges.cx[lon0:lon1, lat0:lat1]
print(f"edges inside the frame: {len(edges)}")

fig, ax = plt.subplots(figsize=(4.6, 4.7))
edges.plot(ax=ax, color=NET, linewidth=0.28, zorder=1, rasterized=True)
ax.scatter([float(p["lon"]) for p in other], [float(p["lat"]) for p in other], s=11,
           color=GREY, edgecolor="white", linewidth=0.5, zorder=3, label=f"Other delivery point ({len(other)})")
ax.scatter([float(p["lon"]) for p in critical], [float(p["lat"]) for p in critical], s=14,
           color=AMBER, edgecolor="white", linewidth=0.5, zorder=4, label=f"Critical point ({len(critical)})")
ax.scatter([float(a["lon"]) for a in depots], [float(a["lat"]) for a in depots], s=36, marker="s",
           color=INK, edgecolor="white", linewidth=0.7, zorder=5, label=f"Depot ({len(depots)})")

arrow = dict(arrowstyle="-|>", color=INK, linewidth=1.3, mutation_scale=9)
box = dict(boxstyle="square,pad=0.25", facecolor="white", edgecolor="none", alpha=0.85)
ax.annotate("", xy=(lon0 + 0.002, lat0 + 0.002), xytext=(lon0 + 0.020, lat0 + 0.020), arrowprops=arrow, zorder=6)
ax.text(lon0 + 0.022, lat0 + 0.010, "Towards Chinchiná and Pereira\n(closed at km 22 to 24 on 12 Aug)",
        color=INK, fontsize=7, va="bottom", ha="left", zorder=6, bbox=box)
y_let = lat0 + 0.42 * (lat1 - lat0)
ax.annotate("", xy=(lon1 - 0.001, y_let), xytext=(lon1 - 0.019, y_let), arrowprops=arrow, zorder=6)
ax.text(lon1 - 0.001, y_let - 0.004, "Towards Fresno\n(closed at km 36+800 to 40+300\non 12 Aug)",
        color=INK, fontsize=7, va="top", ha="right", zorder=6, bbox=box)

ax.set_xlim(lon0, lon1)
ax.set_ylim(lat0, lat1)
ax.set_aspect(1.0)
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
for side in ax.spines.values():
    side.set_color(GREY)
    side.set_linewidth(0.6)
legend = ax.legend(loc="upper left", frameon=True, fontsize=7, handletextpad=0.3, borderpad=0.5)
legend.get_frame().set_edgecolor("none")
legend.get_frame().set_alpha(0.9)
# OpenStreetMap attribution goes in the caption of the figure in main.tex.

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.tight_layout(pad=0.2)
fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0.03)
print(f"written {OUT}")
