"""Métricas de una corrida. Las dos primeras son los indicadores de la ficha del reto."""
from __future__ import annotations

import numpy as np

from .motor import Resultado

H = 3600.0

# nombre -> (descripción, True si más alto es mejor)
METRICAS = {
    "a_tiempo_criticos_pct": ("Pedidos de puntos críticos entregados antes de su hora límite (%)", True),
    "perecedero_vencido_pct": ("Kilos perecederos que vencieron sin entregarse (%)", False),
    "a_tiempo_todos_pct": ("Pedidos entregados antes de su hora límite, todos los puntos (%)", True),
    "entregados_pct": ("Pedidos entregados dentro de la jornada (%)", True),
    "demanda_no_atendida_pct": ("Kilos pedidos que no llegaron en buen estado (%)", False),
    "llegada_media_h": ("Tiempo medio del pedido a la entrega (h)", False),
    "llegada_max_h": ("Tiempo máximo del pedido a la entrega (h)", False),
    "peor_punto_h": ("Tiempo medio de espera en el punto peor atendido (h)", False),
    "km": ("Kilómetros recorridos por la flota", False),
    "recalculos": ("Llamadas al optimizador", False),
    "recalculo_medio_s": ("Segundos de cálculo por llamada, media", False),
    "recalculo_max_s": ("Segundos de cálculo por llamada, máximo", False),
}


def calcular(r: Resultado) -> dict:
    esc = r.esc
    critico = {q.id: q.critico for q in esc.puntos}
    ped = esc.pedidos
    ent = r.entregas
    a_tiempo = lambda q: q.id in ent and ent[q.id]["t"] <= q.limite
    crit = [q for q in ped if critico[q.punto_id]]
    pct = lambda num, den: 100.0 * num / den if den else float("nan")

    # perecederos: vence dentro de la jornada todo kilo de un lote con vencimiento antes del
    # corte que no se haya entregado a tiempo (en bodega, a bordo o entregado ya vencido)
    kg_per = sum(l.kg for l in esc.lotes)
    kg_venc = sum(l.kg - r.kg_valido_por_lote[l.id] for l in esc.lotes if l.vence <= r.t_fin)

    esperas = [ent[q.id]["t"] - q.creado for q in ped if q.id in ent]
    # punto peor atendido: espera media por punto; lo no entregado cuenta hasta el corte
    por_punto = {}
    for q in ped:
        espera = (ent[q.id]["t"] if q.id in ent else r.t_fin) - q.creado
        por_punto.setdefault(q.punto_id, []).append(espera)
    seg = [s for _, _, s in r.recalculos]
    return {
        "a_tiempo_criticos_pct": pct(sum(a_tiempo(q) for q in crit), len(crit)),
        "perecedero_vencido_pct": pct(max(0.0, kg_venc), kg_per),
        "a_tiempo_todos_pct": pct(sum(a_tiempo(q) for q in ped), len(ped)),
        "entregados_pct": pct(len(ent), len(ped)),
        "demanda_no_atendida_pct": pct(sum(q.kg for q in ped) - sum(e["kg_ok"] for e in ent.values()),
                                       sum(q.kg for q in ped)),
        "llegada_media_h": float(np.mean(esperas)) / H if esperas else float("nan"),
        "llegada_max_h": float(np.max(esperas)) / H if esperas else float("nan"),
        "peor_punto_h": max(float(np.mean(v)) for v in por_punto.values()) / H,
        "km": sum(v.km for v in r.vehiculos),
        "recalculos": len(seg),
        "recalculo_medio_s": float(np.mean(seg)) if seg else 0.0,
        "recalculo_max_s": float(np.max(seg)) if seg else 0.0,
    }


def descripcion_escenario(r: Resultado) -> dict:
    esc = r.esc
    return {
        "puntos": len(esc.puntos),
        "criticos": sum(q.critico for q in esc.puntos),
        "pedidos": len(esc.pedidos),
        "kg_pedidos": round(sum(q.kg for q in esc.pedidos)),
        "vehiculos": len(esc.vehiculos),
        "cierres": len(esc.cierres),
        "cierres_descubiertos": len(r.descubiertos),
    }
