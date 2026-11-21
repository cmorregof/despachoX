"""Figura 2 del informe corto: kilos de la red de bancos de alimentos al sexto día.

Uso: /home/claude/venv-dx/bin/python docs/informe/figuras/scripts/barras_abaco.py
Escribe docs/informe/figuras/barras_abaco.pdf.

Cifras: Portafolio, 16 de agosto de 2026, citado en docs/investigacion/10_problema_usuarios_alternativas.md
(sección 4.1, marca [E]). Nadie del equipo ha abierto todavía la nota: por verificar.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

INFORME = Path(__file__).resolve().parents[2]
SALIDA = INFORME / "figuras" / "barras_abaco.pdf"
TINTA, AMBAR, CREMA, CENIZA = "#1F5C4A", "#D9982B", "#E4EADB", "#5C6A62"

for ttf in (INFORME / "fuentes").glob("AncizarSerif-*.ttf"):
    font_manager.fontManager.addfont(str(ttf))
plt.rcParams.update({"font.family": "Ancizar Serif", "font.size": 8.5, "pdf.fonttype": 42})

# (rótulo, kilos, color): de arriba abajo
datos = [("En acopio", 404_587, TINTA), ("En tránsito", 157_164, CENIZA), ("Entregados", 41_163, AMBAR)]


def miles(n):
    return f"{n:,}".replace(",", ".")


fig, ax = plt.subplots(figsize=(6.3, 1.32))
y = list(range(len(datos)))[::-1]
ax.barh(y, [d[1] for d in datos], color=[d[2] for d in datos], height=0.66)
for yi, (rotulo, kg, color) in zip(y, datos):
    ax.text(kg + 6_000, yi, f"{miles(kg)} kg", va="center", ha="left", fontsize=8.5, color=(TINTA if color == AMBAR else color))
ax.set_yticks(y)
ax.set_yticklabels([d[0] for d in datos], fontsize=8.5)
ax.set_xlim(0, 480_000)
ax.set_xticks([0, 100_000, 200_000, 300_000, 400_000])
ax.set_xticklabels(["0", "100.000", "200.000", "300.000", "400.000 kg"], fontsize=7.5, color=CENIZA)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
for lado in ("left", "bottom"):
    ax.spines[lado].set_color(CENIZA)
    ax.spines[lado].set_linewidth(0.6)
ax.tick_params(axis="both", colors=CENIZA, length=2)
for etiqueta in ax.get_yticklabels():
    etiqueta.set_color("#1C2A24")
fig.tight_layout(pad=0.3)
fig.savefig(SALIDA)
print(f"escrito {SALIDA}")
