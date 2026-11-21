"""Genera `datos/demo/lluvia_sintetica.csv`: lluvia diaria SINTÉTICA para demostrar el A25.

Ningún valor es una medición del IDEA ni de ninguna estación. Las estaciones (nombre y
coordenadas) sí son las del IDEA, Boletín Ambiental 145, tabla 4 (`datos_publicos/estaciones_a25.csv`).

Cómo se fabrica, con semilla fija para que siempre salga igual:
1. Cada estación sigue una cadena de días secos y lluviosos con montos al azar. Desde octubre
   llueve más seguido y más fuerte, para imitar una temporada de lluvias. Las probabilidades y
   los montos son inventados.
2. Para el día de la demostración se fija el A25 de cada estación con un aguacero inventado
   centrado cerca del Hospital de Caldas, que decae con la distancia. Los 25 días de esa ventana
   se escalan para que el A25 dé ese valor. Así la demostración muestra los cuatro niveles y una
   alerta roja sobre la avenida Kevin Ángel, que tiene derrumbes registrados en 2017 y 2019
   (`datos_publicos/cierres_historicos.csv`, filas A002 y A066).

Uso:  python datos/demo/generar_lluvia.py
"""
from __future__ import annotations

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
ESTACIONES = RAIZ / "datos_publicos" / "estaciones_a25.csv"
SALIDA = Path(__file__).resolve().parent / "lluvia_sintetica.csv"

SEMILLA = 2026
DESDE, HASTA = date(2026, 8, 1), date(2026, 11, 30)
DIA_DEMO = date(2026, 11, 21)                 # sábado del pitch
# Aguacero inventado del día de la demostración: A25 = BASE + AMPLITUD · exp(-d² / 2σ²).
CENTRO = (5.0640, -75.4985)                   # cerca del Hospital de Caldas
BASE_MM, AMPLITUD_MM, SIGMA_KM = 150.0, 280.0, 1.8

ENCABEZADO = ("# LLUVIA SINTÉTICA. No es una medición del IDEA ni de ninguna estación. "
              "La generó datos/demo/generar_lluvia.py (semilla 2026) para demostrar el A25 en DespachoX. "
              "Estaciones: IDEA, Boletín Ambiental 145, tabla 4.")


def _km(lat1, lon1, lat2, lon2):
    kx = 111.320 * math.cos(math.radians(lat1))
    return math.hypot((lon2 - lon1) * kx, (lat2 - lat1) * 110.540)


def _dia_base(rng: random.Random, d: date, ayer_llovio: bool) -> tuple[float, bool]:
    temporada = d >= date(2026, 10, 1)
    p = (0.70 if ayer_llovio else 0.45) if temporada else (0.55 if ayer_llovio else 0.30)
    if rng.random() >= p:
        return 0.0, False
    media = 11.0 if temporada else 6.0
    return round(rng.expovariate(1 / media), 1), True


def _escalar(valores: list[float], objetivo: float) -> list[float]:
    """Escala la ventana para que sume `objetivo` con un decimal exacto."""
    total = sum(valores)
    if total <= 0:
        valores = [1.0] * len(valores)
        total = float(len(valores))
    nuevos = [round(v * objetivo / total, 1) for v in valores]
    resto = round(objetivo - sum(nuevos), 1)
    k = max(range(len(nuevos)), key=lambda i: nuevos[i])
    nuevos[k] = round(nuevos[k] + resto, 1)
    return nuevos


def generar() -> list[tuple[str, date, float]]:
    rng = random.Random(SEMILLA)
    with open(ESTACIONES, encoding="utf-8") as f:
        estaciones = list(csv.DictReader(f))
    dias = [DESDE + timedelta(days=k) for k in range((HASTA - DESDE).days + 1)]
    inicio_ventana = DIA_DEMO - timedelta(days=24)
    filas = []
    for e in estaciones:
        serie, llovio = [], False
        for d in dias:
            v, llovio = _dia_base(rng, d, llovio)
            serie.append(v)
        d_km = _km(float(e["lat"]), float(e["lon"]), *CENTRO)
        objetivo = round(BASE_MM + AMPLITUD_MM * math.exp(-d_km ** 2 / (2 * SIGMA_KM ** 2)), 1)
        i0, i1 = dias.index(inicio_ventana), dias.index(DIA_DEMO) + 1
        serie[i0:i1] = _escalar(serie[i0:i1], objetivo)
        filas += [(e["id"], d, v) for d, v in zip(dias, serie)]
    return filas


def main() -> None:
    filas = generar()
    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        f.write(ENCABEZADO + "\n")
        w = csv.writer(f)
        w.writerow(["estacion", "fecha", "lluvia_mm_sintetica"])
        for eid, d, v in filas:
            w.writerow([eid, d.isoformat(), f"{v:.1f}"])
    print(f"{len(filas)} filas sintéticas -> {SALIDA}")


if __name__ == "__main__":
    main()
