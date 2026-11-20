"""Tablero del despachador de DespachoX.

Uso:  streamlit run tablero/app.py        (detalle en tablero/README.md)

Esta pantalla solo dibuja y recoge decisiones. Todo lo que lee o cambia la base está en
tablero/datos.py. No calcula rutas: se las pide a despacho/ y el despachador las aprueba.
"""
from __future__ import annotations

import hashlib
import html
import json
import sys
from datetime import datetime
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

RAIZ = Path(__file__).resolve().parent.parent
# Streamlit pone la carpeta tablero/ al principio de la ruta de importación, y entonces `datos`
# sería tablero/datos.py y no el paquete datos/ de la raíz. Se deja solo la raíz.
sys.path[:] = [str(RAIZ)] + [p for p in sys.path if Path(p or ".").resolve() not in (RAIZ, RAIZ / "tablero")]

from datos import db  # noqa: E402
from tablero import datos as T  # noqa: E402

CENTRO = (5.07, -75.52)
SEGUNDOS_REFRESCO = 5
ALTERNATIVAS = 3          # cuántas alternativas de ubicación se ofrecen por propuesta
COLOR_PEDIDO = {"nuevo": "#f59e0b", "confirmado": "#2563eb", "asignado": "#7c3aed", "entregado": "#16a34a"}
COLORES_RUTA = ["#1f77b4", "#ff7f0e", "#2ca02c", "#9467bd", "#8c564b", "#e377c2", "#17becf", "#7f7f7f"]
ROJO = "#dc2626"
MORADO = "#a21caf"

ESTILO = """
<style>
.block-container {padding-top: 3.4rem; padding-bottom: 1rem; max-width: 100%;}
html, body, [data-testid="stMarkdownContainer"] p, .stButton button {font-size: 1.05rem;}
h1 {font-size: 1.7rem !important; padding: 0 !important;}
.tarjeta {border: 1px solid rgba(128,128,128,.35); border-radius: 12px; padding: .7rem 1rem; height: 100%;}
.tarjeta .rotulo {font-size: 1.05rem; opacity: .8; line-height: 1.2;}
.tarjeta .valor {font-size: 3rem; font-weight: 700; line-height: 1.1;}
.tarjeta .nota {font-size: 1.05rem; line-height: 1.25;}
.tarjeta.alerta {border-color: #dc2626; border-width: 2px;}
.tarjeta.alerta .valor {color: #dc2626;}
.ficha {display: inline-block; margin: .15rem .9rem .15rem 0; font-size: 1.05rem; white-space: nowrap;}
.ficha i {display: inline-block; width: 1.6rem; height: .5rem; border-radius: 3px; margin-right: .4rem;
          vertical-align: middle;}
.ficha b.punto {display: inline-block; width: .9rem; height: .9rem; border-radius: 50%; margin-right: .35rem;
                vertical-align: middle;}
.sin-ubicar {background: #dc2626; color: white; border-radius: 6px; padding: .1rem .5rem; font-weight: 700;}
.critico {color: #dc2626; font-weight: 700;}
.grande {font-size: 1.25rem; font-weight: 700;}
.cita {font-size: 1.1rem; font-style: italic;}
</style>
"""


# ---------- utilidades de pantalla ----------

def hora(texto: str | None) -> str:
    try:
        return datetime.fromisoformat(texto).strftime("%H:%M")
    except (TypeError, ValueError):
        return "?"


def limite(texto: str | None) -> str:
    """Hora del límite; con la fecha si no es hoy, para que «10:21» de mañana no parezca vencido."""
    try:
        f = datetime.fromisoformat(texto)
    except (TypeError, ValueError):
        return "?"
    hoy = datetime.now(db.BOGOTA).date()
    return f.strftime("%H:%M") if f.date() == hoy else f"{f.day}/{f.month} {f:%H:%M}"


def quien() -> str:
    return (st.session_state.get("quien") or "").strip() or "despachador"


def avisar(tipo: str, texto: str) -> None:
    st.session_state["aviso"] = (tipo, texto)


def refrescar() -> None:
    st.rerun(scope="fragment")


def color_de(rutas: list[dict]) -> dict[int, str]:
    """Un color fijo por vehículo, para que no cambie de un plan al siguiente."""
    return {r["vehiculo_id"]: COLORES_RUTA[(r["vehiculo_id"] - 1) % len(COLORES_RUTA)] for r in rutas}


def tarjeta(col, rotulo: str, valor: str, nota: str = "", alerta: bool = False) -> None:
    col.markdown(f'<div class="tarjeta{" alerta" if alerta else ""}"><div class="rotulo">{rotulo}</div>'
                 f'<div class="valor">{valor}</div><div class="nota">{nota or "&nbsp;"}</div></div>',
                 unsafe_allow_html=True)


# ---------- indicadores ----------

def indicadores(ind: dict, plan: dict | None) -> None:
    c1, c2, c3, c4 = st.columns(4)
    tarjeta(c1, "Pedidos pendientes", str(ind["pedidos_pendientes"]),
            f"{ind['pedidos_por_confirmar']} por confirmar")
    tarjeta(c2, "Perecederos que vencen en menos de 12 h", f"{ind['kg_vencen_pronto']:,.0f} kg".replace(",", "."),
            alerta=ind["kg_vencen_pronto"] > 0)
    tarjeta(c3, "Cierres activos", str(ind["cierres_activos"]),
            f"{ind['cierres_reportados']} por confirmar", alerta=ind["cierres_activos"] > 0)
    p = ind["puntualidad"]
    if p["pct"] is None:
        tarjeta(c4, "Pedidos del plan a tiempo", "–", "Sin plan" if not plan else "El plan no tiene paradas")
    else:
        crit = (f"Puntos críticos: <b>{p['pct_criticos']:.0f} %</b> ({p['criticos_a_tiempo']} de "
                f"{p['criticos_total']})" if p["pct_criticos"] is not None else "Sin puntos críticos en el plan")
        tarjeta(c4, f"Pedidos del plan a tiempo ({p['a_tiempo']} de {p['total']})", f"{p['pct']:.0f} %", crit,
                alerta=p["pct"] < 100)


# ---------- mapa ----------

def numero(n: int, color: str) -> folium.DivIcon:
    return folium.DivIcon(icon_size=(26, 26), icon_anchor=(13, 13), html=(
        f'<div style="background:{color};color:white;border:2px solid white;border-radius:50%;width:26px;'
        f'height:26px;line-height:22px;text-align:center;font-weight:700;font-size:14px;'
        f'box-shadow:0 0 3px rgba(0,0,0,.6)">{n}</div>'))


def capa(con, plan: dict | None, rutas: list[dict], revisar: dict, pin: dict | None) -> folium.FeatureGroup:
    """Todo lo que se dibuja sobre el mapa base. Se guarda mientras los datos no cambien, para que
    la actualización automática no redibuje ni mueva el mapa."""
    acopios = T.filas(con, "SELECT * FROM acopios")
    puntos = {p["id"]: p for p in T.filas(con, "SELECT * FROM puntos")}
    pedidos = T.filas(con, "SELECT id, punto_id, estado, urgencia, kg_estimado, familias FROM pedidos "
                           "WHERE estado IN ('nuevo','confirmado','asignado') AND duplicado_de IS NULL")
    cierres = T.filas(con, "SELECT * FROM cierres WHERE estado != 'levantado' AND lat IS NOT NULL")
    firma = hashlib.sha1(json.dumps(
        [acopios, puntos, pedidos, cierres, plan and plan["id"], plan and plan["estado"],
         revisar["ubicaciones"], pin], sort_keys=True, default=str).encode()).hexdigest()
    guardada = st.session_state.get("capa")
    if guardada and guardada[0] == firma:
        return guardada[1]

    fg = folium.FeatureGroup(name="despacho")
    colores = color_de(rutas)
    for r in rutas:
        c = colores[r["vehiculo_id"]]
        for s in r["paradas"]:
            if len(s["geometria"]) >= 2:
                folium.PolyLine(s["geometria"], color=c, weight=6, opacity=0.85,
                                tooltip=f"{r['nombre']} · parada {s['orden']}").add_to(fg)
        if len(r["regreso"]) >= 2:
            folium.PolyLine(r["regreso"], color=c, weight=3, opacity=0.6, dash_array="4 8",
                            tooltip=f"{r['nombre']} · regreso al acopio").add_to(fg)

    for p in puntos.values():
        folium.CircleMarker([p["lat"], p["lon"]], radius=13 if p["critico"] else 6,
                            color=ROJO if p["critico"] else "#374151", weight=4 if p["critico"] else 1.5,
                            fill=False, tooltip=p["nombre"] + (" · PUNTO CRÍTICO" if p["critico"] else "")
                            ).add_to(fg)
    for d in pedidos:
        p = puntos.get(d["punto_id"])
        if p:
            folium.CircleMarker([p["lat"], p["lon"]], radius=3 + 2.5 * (d["urgencia"] or 2), weight=1,
                                color="white", fill=True, fill_color=COLOR_PEDIDO[d["estado"]], fill_opacity=0.9,
                                tooltip=f"Pedido {d['id']} · {d['estado']} · urgencia {d['urgencia']} · "
                                        f"{d['kg_estimado'] or '?'} kg · {p['nombre']}").add_to(fg)
    for r in rutas:
        for s in r["paradas"]:
            if s["lat"] is not None:
                folium.Marker([s["lat"], s["lon"]], icon=numero(s["orden"], colores[r["vehiculo_id"]]),
                              tooltip=f"{r['nombre']} · parada {s['orden']} · {s['punto']} · "
                                      f"llega {hora(s['llegada_estimada'])}"
                                      + ("" if s["a_tiempo"] else " · TARDE")).add_to(fg)
    for a in acopios:
        folium.Marker([a["lat"], a["lon"]], tooltip=f"Acopio · {a['nombre']}",
                      icon=folium.Icon(color="darkgreen", icon="warehouse", prefix="fa")).add_to(fg)
    for c in cierres:
        reportado = c["estado"] == "reportado"
        folium.Circle([c["lat"], c["lon"]], radius=140, color=ROJO, weight=5,
                      dash_array="8 10" if reportado else None, fill=not reportado, fill_opacity=0.45,
                      tooltip=f"Cierre {c['id']} · {'por confirmar' if reportado else 'confirmado'} · "
                              f"{c['lugar'] or c['descripcion'] or ''}").add_to(fg)

    for u in revisar["ubicaciones"]:
        que = f"{'Pedido' if u['tabla'] == 'pedidos' else 'Cierre'} {u['fila_id']}"
        if u["lat"] is not None:
            folium.Marker([u["lat"], u["lon"]], icon=folium.Icon(color="purple", icon="question", prefix="fa"),
                          tooltip=f"Propuesta · {que} · «{u['texto']}» = {u['lugar'] or '?'}").add_to(fg)
        for c in u["alternativas"][:ALTERNATIVAS]:
            if c.get("lat") is not None:
                folium.CircleMarker([c["lat"], c["lon"]], radius=8, color=MORADO, weight=3, fill=True,
                                    fill_opacity=0.25, dash_array="3 5",
                                    tooltip=f"Alternativa · {que} · {c.get('nombre')}").add_to(fg)
    if pin and pin.get("punto"):
        folium.Marker(pin["punto"], icon=folium.Icon(color="red", icon="location-dot", prefix="fa"),
                      tooltip="Punto marcado: falta guardarlo").add_to(fg)

    st.session_state["capa"] = (firma, fg)
    return fg


def mapa(con, plan: dict | None, rutas: list[dict], revisar: dict) -> None:
    pin = st.session_state.get("pin")
    base = folium.Map(location=CENTRO, zoom_start=13, tiles="OpenStreetMap", control_scale=True)
    salida = st_folium(base, key="mapa", feature_group_to_add=capa(con, plan, rutas, revisar, pin),
                       height=640, use_container_width=True, returned_objects=["last_clicked"])
    clic = (salida or {}).get("last_clicked")
    clic = [round(clic["lat"], 6), round(clic["lng"], 6)] if clic else None
    if pin and clic and clic != pin.get("base") and clic != pin.get("punto"):
        pin["punto"] = clic
        refrescar()
    st.session_state["ultimo_clic"] = clic

    st.caption("© colaboradores de OpenStreetMap")
    colores = color_de(rutas)
    fichas = "".join(
        f'<span class="ficha"><i style="background:{colores[r["vehiculo_id"]]}"></i><b>{html.escape(r["nombre"])}</b>'
        f' · {len(r["paradas"])} paradas · {r["kg"]:.0f} kg</span>' for r in rutas)
    fichas += "".join(f'<span class="ficha"><b class="punto" style="background:{c}"></b>pedido {e}</span>'
                      for e, c in COLOR_PEDIDO.items() if e != "entregado")
    fichas += (f'<span class="ficha"><b class="punto" style="border:3px solid {ROJO}"></b>punto crítico</span>'
               f'<span class="ficha"><b class="punto" style="background:{ROJO}"></b>cierre</span>')
    st.markdown(fichas, unsafe_allow_html=True)


# ---------- bloque «Plan» ----------

def correr(texto: str, funcion, *args) -> T.Corrida:
    with st.spinner(texto):
        return funcion(*args)


def bloque_plan(con, plan: dict | None, rutas: list[dict]) -> None:
    st.subheader("Plan")
    pendientes = T.cierres_sin_aplicar(con, plan)
    if pendientes:
        st.error("**Hay un cierre nuevo: recalcular**")
        if st.button("Recalcular", type="primary", width="stretch", key="recalcular"):
            r = correr("Recalculando las rutas…", T.recalcular_plan)
            avisar("ok" if r.ok else "error", f"Plan {r.plan_id} recalculado. Falta aprobarlo." if r.ok
                   else f"No se pudo recalcular: {r.mensaje}")
            refrescar()

    if not plan:
        st.markdown("Todavía no hay plan.")
        calcular(principal=True)
        return

    res = plan["resumen"]
    estado = {"propuesto": "PROPUESTO · falta aprobar",
              "aprobado": f"APROBADO por {plan['aprobado_por'] or '?'} a las {hora(plan['aprobado_en'])}"
              }[plan["estado"]]
    st.markdown(f'<span class="grande">Plan {plan["id"]} · {estado}</span>', unsafe_allow_html=True)
    atendidos = sum(len(r["paradas"]) for r in rutas)
    st.markdown(f"{atendidos} pedidos en {len(rutas)} vehículos · calculado en "
                f"{plan['segundos_calculo'] or 0:.0f} s · motivo: {plan['motivo'] or '?'}")
    if res.get("vacio"):
        st.error(f"Plan vacío: {res.get('motivo_vacio') or 'sin motivo'}")

    cambios = T.cambios_del_recalculo(con, plan)
    if cambios:
        with st.container(border=True):
            st.markdown(f"**Qué cambió frente al plan {cambios['anterior']}**")
            if cambios["vehiculos"]:
                st.markdown("Cambian de ruta: " + ", ".join(
                    f"**{v['nombre']}** ({v['cambio']})" for v in cambios["vehiculos"]))
            else:
                st.markdown("Ningún vehículo cambia de ruta.")
            m = cambios["mayor"]
            if m and m["minutos"]:
                st.markdown(f"Llegada más afectada: **{m['punto']}** (pedido {m['pedido_id']}, {m['vehiculo']}), "
                            f"**{abs(m['minutos'])} min {'más tarde' if m['minutos'] > 0 else 'antes'}**.")
            elif m:
                st.markdown("Ninguna llegada se mueve.")
            if cambios["salen"]:
                st.markdown(f"Salen del plan los pedidos {', '.join(map(str, cambios['salen']))}.")

    fuera = T.sin_atender(con, plan)
    if fuera:
        st.error("**Sin atender ({})**\n\n".format(len(fuera)) + "\n".join(
            f"- Pedido {x['pedido_id']} · {x['punto']}{' · CRÍTICO' if x['critico'] else ''}: {x['motivo']}"
            for x in fuera))

    if plan["estado"] == "propuesto":
        c1, c2 = st.columns(2)
        if c1.button("Aprobar", type="primary", width="stretch", key="aprobar",
                     disabled=bool(res.get("vacio"))):
            r = correr("Aprobando…", T.aprobar_plan, plan["id"], quien())
            avisar("ok" if r.ok else "error", f"Plan {plan['id']} aprobado por {quien()}." if r.ok
                   else f"No se pudo aprobar: {r.mensaje}")
            refrescar()
        if c2.button("Rechazar", width="stretch", key="rechazar"):
            T.cambiar_estado(con, "planes", plan["id"], "rechazado", quien())
            avisar("ok", f"Plan {plan['id']} rechazado.")
            refrescar()
    calcular(principal=False)


def calcular(principal: bool) -> None:
    if st.button("Calcular plan", type="primary" if principal else "secondary", width="stretch",
                 key="calcular"):
        r = correr("Calculando las rutas (hasta 10 segundos)…", T.calcular_plan)
        avisar("ok" if r.ok else "error", f"Plan {r.plan_id} calculado. Falta aprobarlo." if r.ok
               else f"No se pudo calcular: {r.mensaje}")
        refrescar()


# ---------- columna «Por revisar» ----------

def tarjeta_ubicacion(con, u: dict) -> None:
    pin = st.session_state.get("pin")
    que = f"{'Pedido' if u['tabla'] == 'pedidos' else 'Cierre'} {u['fila_id']}"
    with st.container(border=True):
        st.markdown(f"**Ubicación · {que}**")
        st.markdown(f'<span class="cita">«{html.escape(u["texto"])}»</span>', unsafe_allow_html=True)
        if u["texto_completo"] and u["texto_completo"].strip() != u["texto"].strip():
            st.caption(u["texto_completo"])
        if u["lugar"]:
            st.markdown(f"Propuesta: **{u['lugar']}** ({u['lugar_tipo']}) · pin morado en el mapa")
        else:
            st.markdown('<span class="sin-ubicar">No se encontró el lugar</span>', unsafe_allow_html=True)

        if pin and pin["id"] == u["id"]:
            if pin.get("punto"):
                st.info(f"Punto marcado: {pin['punto'][0]:.5f}, {pin['punto'][1]:.5f}")
            else:
                st.info("Haz clic en el mapa donde queda.")
            c1, c2 = st.columns(2)
            if c1.button("Guardar punto", type="primary", key=f"ug{u['id']}", disabled=not pin.get("punto"),
                         width="stretch"):
                ok = T.corregir_ubicacion(con, u["id"], *pin["punto"])
                st.session_state.pop("pin", None)
                avisar("ok" if ok else "error", f"{que} ubicado con el punto del mapa." if ok
                       else "No se pudo guardar el punto.")
                refrescar()
            if c2.button("Cancelar", key=f"ux{u['id']}", width="stretch"):
                st.session_state.pop("pin", None)
                refrescar()
            return

        c1, c2 = st.columns(2)
        if c1.button("Confirmar", type="primary", key=f"uc{u['id']}", disabled=u["lugar_id"] is None,
                     width="stretch"):
            ok = T.confirmar_ubicacion(con, u["id"], quien())
            avisar("ok" if ok else "error", f"{que} ubicado en {u['lugar']}." if ok
                   else "No se pudo confirmar la ubicación.")
            refrescar()
        if c2.button("Corregir en el mapa", key=f"up{u['id']}", width="stretch"):
            st.session_state["pin"] = {"id": u["id"], "base": st.session_state.get("ultimo_clic"), "punto": None}
            refrescar()
        for c in u["alternativas"][:ALTERNATIVAS]:
            if st.button(f"Es {c.get('nombre')} ({c.get('tipo')})", key=f"ua{u['id']}_{c.get('lugar_id')}",
                         width="stretch"):
                ok = T.confirmar_ubicacion(con, u["id"], quien(), lugar_id=c.get("lugar_id"))
                avisar("ok" if ok else "error", f"{que} ubicado en {c.get('nombre')}." if ok
                       else "No se pudo confirmar la ubicación.")
                refrescar()


def por_revisar(con, revisar: dict) -> None:
    total = len(revisar["ubicaciones"]) + len(revisar["pedidos"]) + len(revisar["cierres"])
    st.subheader(f"Por revisar ({total})")
    if not total and not revisar["confirmados_sin_ubicar"]:
        st.markdown("Nada pendiente.")

    for c in revisar["cierres"]:
        with st.container(border=True):
            st.markdown(f"**Cierre {c['id']}** · {c['lugar'] or 'lugar sin confirmar'}")
            st.markdown(f'<span class="cita">«{html.escape(c["texto_original"] or c["descripcion"] or "sin texto")}»'
                        f'</span>', unsafe_allow_html=True)
            sin_ubicar = c["lat"] is None and not c["lugar"]
            if sin_ubicar:
                st.markdown('<span class="sin-ubicar">sin ubicar</span>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Confirmar", type="primary", key=f"cc{c['id']}", width="stretch",
                         disabled=sin_ubicar, help="Primero confirma dónde queda." if sin_ubicar else None):
                T.cambiar_estado(con, "cierres", c["id"], "confirmado", quien())
                refrescar()
            if c2.button("Levantar", key=f"cl{c['id']}", width="stretch"):
                T.cambiar_estado(con, "cierres", c["id"], "levantado", quien())
                refrescar()

    for u in revisar["ubicaciones"]:
        tarjeta_ubicacion(con, u)

    for d in revisar["pedidos"]:
        with st.container(border=True):
            donde = ('<span class="sin-ubicar">sin ubicar</span>' if d["sin_ubicar"] else
                     html.escape(d["punto"]) + (' <span class="critico">· CRÍTICO</span>' if d["critico"] else ""))
            st.markdown(f"**Pedido {d['id']}** · urgencia {d['urgencia']} · {donde}", unsafe_allow_html=True)
            st.markdown(f'<span class="cita">«{html.escape(d["texto_original"] or "sin texto")}»</span>',
                        unsafe_allow_html=True)
            st.caption(f"{d['familias'] or '?'} familias · {d['kg_estimado'] or '?'} kg · "
                       f"límite {limite(d['limite_en'])}")
            if d["duplicados"]:
                with st.expander(f"{len(d['duplicados'])} repetido(s) del mismo pedido"):
                    for x in d["duplicados"]:
                        st.caption(f"Pedido {x['id']}: {x['texto_original'] or ''}")
            c1, c2 = st.columns(2)
            if c1.button("Confirmar", type="primary", key=f"pc{d['id']}", disabled=d["sin_ubicar"],
                         width="stretch",
                         help="Primero confirma dónde queda." if d["sin_ubicar"] else None):
                T.cambiar_estado(con, "pedidos", d["id"], "confirmado", quien())
                refrescar()
            if c2.button("Descartar", key=f"pd{d['id']}", width="stretch"):
                T.cambiar_estado(con, "pedidos", d["id"], "descartado", quien())
                refrescar()

    for d in revisar["confirmados_sin_ubicar"]:
        with st.container(border=True):
            st.markdown(f'**Pedido {d["id"]}** · confirmado · <span class="sin-ubicar">sin ubicar</span> · '
                        f'no entra al plan', unsafe_allow_html=True)
            st.caption(d["texto_original"] or "")


# ---------- pestañas de detalle ----------

def detalle_plan(con, plan: dict | None, rutas: list[dict]) -> None:
    if not plan:
        st.markdown("Todavía no hay plan.")
        return
    st.markdown(f"**Plan {plan['id']}** · {plan['estado']} · creado a las {hora(plan['creado_en'])}")
    colores = color_de(rutas)
    for r in rutas:
        cap = f" de {r['capacidad_kg']:.0f}" if r["capacidad_kg"] else ""
        st.markdown(f'<span class="ficha"><i style="background:{colores[r["vehiculo_id"]]}"></i>'
                    f'<b>{html.escape(r["nombre"])}</b> · {r["kg"]:.0f}{cap} kg</span>', unsafe_allow_html=True)
        st.dataframe([{"Orden": s["orden"], "Punto": s["punto"], "Crítico": "sí" if s["critico"] else "",
                       "Pedido": s["pedido_id"], "Llega": hora(s["llegada_estimada"]),
                       "Límite": limite(s["limite_en"]), "A tiempo": "sí" if s["a_tiempo"] else "TARDE",
                       "kg": s["kg"]} for s in r["paradas"]], hide_index=True, width="stretch")
    fuera = T.sin_atender(con, plan)
    if fuera:
        st.markdown("**Sin atender**")
        st.dataframe([{"Pedido": x["pedido_id"], "Punto": x["punto"], "Crítico": "sí" if x["critico"] else "",
                       "Motivo": x["motivo"]} for x in fuera], hide_index=True, width="stretch")
    faltantes = plan["resumen"].get("faltantes") or []
    if faltantes:
        st.markdown("**Faltantes de inventario:** " + "; ".join(
            f"pedido {f.get('pedido_id')}, {f.get('producto')}, {f.get('kg')} kg" for f in faltantes))
    for a in plan["resumen"].get("avisos") or []:
        st.caption(f"Aviso del optimizador: {a}")


def detalle_bitacora(con) -> None:
    filas = T.bitacora(con, 60)
    if not filas:
        st.markdown("Todavía no hay decisiones registradas.")
        return
    st.dataframe([{"Hora": hora(f["cuando"]), "Quién": f["quien"], "Acción": f["accion"],
                   "Detalle": f["detalle"]} for f in filas], hide_index=True, width="stretch",
                 height=600)


# ---------- página ----------

@st.fragment(run_every=SEGUNDOS_REFRESCO)
def mesa() -> None:
    con = db.conectar()
    try:
        plan = T.plan_vigente(con)
        rutas = T.rutas(con, plan)
        revisar = T.por_revisar(con)
        indicadores(T.indicadores(con, plan), plan)
        st.write("")
        t_mesa, t_plan, t_bitacora = st.tabs(["Mesa", "Plan en detalle", "Bitácora"])
        with t_mesa:
            col_mapa, col_lado = st.columns([2.6, 1])
            with col_mapa:
                mapa(con, plan, rutas, revisar)
            with col_lado:
                aviso = st.session_state.get("aviso")
                if aviso:
                    (st.success if aviso[0] == "ok" else st.error)(aviso[1])
                bloque_plan(con, plan, rutas)
                por_revisar(con, revisar)
        with t_plan:
            detalle_plan(con, plan, rutas)
        with t_bitacora:
            detalle_bitacora(con)
    finally:
        con.close()


def main() -> None:
    st.set_page_config(page_title="DespachoX · Mesa de despacho", layout="wide")
    st.markdown(ESTILO, unsafe_allow_html=True)
    c1, c2 = st.columns([5, 1])
    c1.title("DespachoX · Mesa de despacho")
    c2.text_input("Despachador", key="quien", placeholder="Tu nombre", label_visibility="collapsed")
    mesa()


main()
