"""Tablero del despachador de DespachoX.

Uso:  streamlit run tablero/app.py

Lee la base con datos.db.conectar(). Solo cambia estados (pedidos, cierres, planes)
y anota cada cambio en la bitácora. No calcula rutas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from datos import db  # noqa: E402

QUIEN = "despachador"
CENTRO = (5.07, -75.52)
COLOR_PEDIDO = {"nuevo": "orange", "confirmado": "blue", "asignado": "purple",
                "entregado": "green", "descartado": "gray"}
COLORES_RUTA = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4",
                "#46f0f0", "#f032e6", "#bcf60c"]


# ---------- lectura ----------

def filas(con, sql: str, args: tuple = ()) -> list[dict]:
    return [dict(r) for r in con.execute(sql, args).fetchall()]


def plan_vigente(con) -> dict | None:
    """El último plan aprobado; si no hay, el último propuesto."""
    for estado in ("aprobado", "propuesto"):
        p = con.execute("SELECT * FROM planes WHERE estado=? ORDER BY id DESC LIMIT 1",
                        (estado,)).fetchone()
        if p:
            return dict(p)
    return None


# ---------- cambios de estado (siempre con bitácora) ----------

def cambiar(tabla: str, fila_id: int, estado: str, accion: str) -> None:
    con = db.conectar()
    con.execute(f"UPDATE {tabla} SET estado=? WHERE id=?", (estado, fila_id))
    con.commit()
    db.anotar(con, QUIEN, accion, f"{tabla} {fila_id} -> {estado}")
    con.close()


# ---------- mapa ----------

def dibujar_mapa(con, plan: dict | None) -> folium.Map:
    m = folium.Map(location=CENTRO, zoom_start=13, tiles="OpenStreetMap")

    for a in filas(con, "SELECT * FROM acopios"):
        folium.Marker([a["lat"], a["lon"]], tooltip=a["nombre"],
                      icon=folium.Icon(color="darkgreen", icon="home")).add_to(m)

    puntos = {p["id"]: p for p in filas(con, "SELECT * FROM puntos")}
    for p in puntos.values():
        folium.CircleMarker([p["lat"], p["lon"]], radius=9 if p["critico"] else 5,
                            color="red" if p["critico"] else "black", weight=3 if p["critico"] else 1,
                            fill=False, tooltip=f"{p['nombre']}{' · CRÍTICO' if p['critico'] else ''}"
                            ).add_to(m)

    for d in filas(con, "SELECT * FROM pedidos WHERE estado != 'descartado' AND duplicado_de IS NULL"):
        p = puntos.get(d["punto_id"])
        if not p:
            continue
        folium.CircleMarker([p["lat"], p["lon"]], radius=4 + 3 * (d["urgencia"] or 2),
                            color=COLOR_PEDIDO.get(d["estado"], "gray"), fill=True, fill_opacity=0.6,
                            tooltip=f"Pedido {d['id']} · {d['estado']} · urgencia {d['urgencia']} · "
                                    f"{d['kg_estimado'] or '?'} kg").add_to(m)

    for c in filas(con, "SELECT * FROM cierres WHERE estado != 'levantado' AND lat IS NOT NULL"):
        punteado = c["estado"] == "reportado"
        folium.Circle([c["lat"], c["lon"]], radius=120, color="red", weight=4,
                      dash_array="8 8" if punteado else None, fill=not punteado, fill_opacity=0.3,
                      tooltip=f"Cierre {c['id']} · {c['estado']} · {c['lugar'] or ''}").add_to(m)

    if plan:
        paradas = filas(con, "SELECT * FROM paradas WHERE plan_id=? ORDER BY vehiculo_id, orden",
                        (plan["id"],))
        vehiculos = sorted({s["vehiculo_id"] for s in paradas})
        color_de = {v: COLORES_RUTA[i % len(COLORES_RUTA)] for i, v in enumerate(vehiculos)}
        for s in paradas:
            try:
                geo = json.loads(s["geometria"] or "[]")
            except json.JSONDecodeError:
                geo = []
            if len(geo) >= 2:
                folium.PolyLine(geo, color=color_de[s["vehiculo_id"]], weight=5, opacity=0.8,
                                tooltip=f"Vehículo {s['vehiculo_id']} · parada {s['orden']}").add_to(m)
        try:
            resumen = json.loads(plan["resumen"] or "{}")
        except json.JSONDecodeError:
            resumen = {}
        for v in resumen.get("vehiculos", []) if isinstance(resumen, dict) else []:
            geo = v.get("regreso") or []
            vid = v.get("id") or v.get("vehiculo_id")
            if len(geo) >= 2:
                folium.PolyLine(geo, color=color_de.get(vid, "gray"), weight=3, opacity=0.5,
                                dash_array="4 6", tooltip=f"Regreso vehículo {vid}").add_to(m)
    return m


# ---------- columna «Por revisar» ----------

def por_revisar(con) -> None:
    st.subheader("Por revisar")

    nuevos = filas(con, "SELECT * FROM pedidos WHERE estado='nuevo' ORDER BY urgencia DESC, id")
    originales = [d for d in nuevos if d["duplicado_de"] is None]
    duplicados: dict[int, list[dict]] = {}
    for d in filas(con, "SELECT * FROM pedidos WHERE duplicado_de IS NOT NULL AND estado != 'descartado'"):
        duplicados.setdefault(d["duplicado_de"], []).append(d)

    st.markdown(f"**Pedidos nuevos ({len(originales)})**")
    if not originales:
        st.caption("Nada pendiente.")
    for d in originales:
        with st.container(border=True):
            st.markdown(f"**#{d['id']}** · urgencia {d['urgencia']} · {d['familias'] or '?'} familias")
            st.caption(d["texto_original"] or "(sin texto)")
            dups = duplicados.get(d["id"], [])
            if dups:
                with st.expander(f"{len(dups)} duplicado(s)"):
                    for x in dups:
                        st.caption(f"#{x['id']}: {x['texto_original'] or ''}")
            c1, c2 = st.columns(2)
            if c1.button("Confirmar", key=f"pc{d['id']}"):
                cambiar("pedidos", d["id"], "confirmado", "confirmar pedido")
                st.rerun()
            if c2.button("Descartar", key=f"pd{d['id']}"):
                cambiar("pedidos", d["id"], "descartado", "descartar pedido")
                st.rerun()

    reportados = filas(con, "SELECT * FROM cierres WHERE estado='reportado' ORDER BY id")
    st.markdown(f"**Cierres reportados ({len(reportados)})**")
    if not reportados:
        st.caption("Nada pendiente.")
    for c in reportados:
        with st.container(border=True):
            st.markdown(f"**#{c['id']}** · {c['lugar'] or 'sin lugar'}")
            st.caption(c["texto_original"] or c["descripcion"] or "(sin texto)")
            c1, c2 = st.columns(2)
            if c1.button("Confirmar", key=f"cc{c['id']}"):
                cambiar("cierres", c["id"], "confirmado", "confirmar cierre")
                st.rerun()
            if c2.button("Levantar", key=f"cl{c['id']}"):
                cambiar("cierres", c["id"], "levantado", "levantar cierre")
                st.rerun()


# ---------- página ----------

def main() -> None:
    st.set_page_config(page_title="DespachoX · Tablero", layout="wide")
    st.title("DespachoX · Mesa de despacho")

    con = db.conectar()
    plan = plan_vigente(con)

    col_mapa, col_lado = st.columns([3, 1])
    with col_mapa:
        st_folium(dibujar_mapa(con, plan), height=600, use_container_width=True,
                  returned_objects=[])
        st.caption("© colaboradores de OpenStreetMap")
    with col_lado:
        por_revisar(con)
    con.close()


main()
