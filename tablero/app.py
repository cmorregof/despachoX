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
from tablero import mapa_base  # noqa: E402
from tablero.clave import clave_ok  # noqa: E402
from tablero.mapa_base import seguro as S  # noqa: E402  - todo texto de la base que va al mapa

NOMBRE = "Convite"          # nombre visible (canal, 20/11 23:30); módulos y archivos no cambian
CENTRO = (5.07, -75.52)
SEGUNDOS_REFRESCO = 5
ALTERNATIVAS = 3          # cuántas alternativas de ubicación se ofrecen por propuesta
# Paleta Convite «Camino abierto» (recursos/marca/README.md): verde monte, maíz, niebla y piedra. La tierra roja
# es solo para el cierre, que además va punteado para no depender del color.
TINTA, AMBAR, CREMA, CENIZA = "#1F5C4A", "#D9982B", "#E4EADB", "#5C6A62"
VERDE = "#4E7D5B"
# Colores de estado: pendiente (nuevo y confirmado), en ruta (asignado), entregado y silencio.
COLOR_PEDIDO = {"nuevo": AMBAR, "confirmado": "#EBC77A", "asignado": TINTA, "entregado": VERDE}
COLOR_SILENCIO = CENIZA
FONDO_ESTADO = {"pendiente": "#F7EAD0", "en ruta": "#E4EADB", "entregado": "#D3E6DC", "silencio": "#E9ECEA"}
COLORES_RUTA = [TINTA, CENIZA, "#2F7F86", "#8A5A9E", "#5F7A3B", "#B4566E", "#3E6FA3", "#1C2A24"]
ROJO = "#C73A1E"
MORADO = "#8A5A9E"
FILA_ALTERNA = "#EEF2E8"

ESTILO = """
<style>
.block-container {padding-top: 3.2rem; padding-bottom: 1.5rem; max-width: 100%;}
html, body, [data-testid="stMarkdownContainer"] p, .stButton button {font-size: 1.05rem;}
h1 {font-size: 1.75rem !important; padding: 0 !important; color: #1F5C4A; letter-spacing: .01em;}
h3 {color: #1F5C4A;}
[data-testid="stVerticalBlock"] {gap: 1.05rem;}
/* Tarjetas: bordes redondeados, sombra suave y aire; el borde por defecto casi desaparece. */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
  border-radius: 14px; border-color: rgba(92,106,98,.22) !important; background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(28,42,36,.05), 0 6px 18px rgba(28,42,36,.07); padding: .35rem .25rem;}
.tarjeta {border-radius: 16px; padding: 1rem 1.2rem 1.05rem; height: 100%; background: #E4EADB;
          box-shadow: 0 1px 2px rgba(28,42,36,.05), 0 8px 22px rgba(28,42,36,.08);
          border-top: 5px solid #1F5C4A;}
.tarjeta .rotulo {font-size: 1rem; color: #5C6A62; line-height: 1.25; font-weight: 600;}
.tarjeta .valor {font-size: 3.1rem; font-weight: 750; line-height: 1.05; color: #1C2A24; margin: .35rem 0 .2rem;}
.tarjeta .meta {font-size: .95rem; color: #5C6A62; font-weight: 600;}
.tarjeta .nota {font-size: 1rem; line-height: 1.3; color: #1C2A24;}
.tarjeta .contexto {display: inline-block; font-size: .85rem; font-weight: 700; letter-spacing: .04em;
                    text-transform: uppercase; border-radius: 999px; padding: .12rem .6rem; margin-bottom: .2rem;
                    background: #FFFFFF; color: #1F5C4A;}
.tarjeta.alerta {border-top-color: #D9982B;}
.tarjeta.alerta .valor {color: #1C2A24;}
.tarjeta.alerta .contexto {background: #D9982B; color: #1C2A24;}
.ficha {display: inline-block; margin: .2rem .9rem .2rem 0; font-size: 1rem; white-space: nowrap; color: #1C2A24;}
.ficha i {display: inline-block; width: 1.6rem; height: .5rem; border-radius: 3px; margin-right: .4rem;
          vertical-align: middle;}
.ficha b.punto {display: inline-block; width: .9rem; height: .9rem; border-radius: 50%; margin-right: .35rem;
                vertical-align: middle;}
.sin-ubicar {background: #D9982B; color: #1C2A24; border-radius: 8px; padding: .1rem .55rem; font-weight: 700;}
.critico {color: #1F5C4A; font-weight: 700;}
.silencio {background: #5C6A62; color: white; border-radius: 8px; padding: .1rem .55rem; font-weight: 700;}
.grande {font-size: 1.25rem; font-weight: 700; color: #1F5C4A;}
.cita {font-size: 1.1rem; font-style: italic; color: #5C6A62;}
[data-testid="stTabs"] button[role="tab"] p {font-size: 1.05rem; font-weight: 600;}
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


def tarjeta(col, rotulo: str, valor: str, nota: str = "", alerta: bool = False, contexto: str = "",
            meta: str = "") -> None:
    """Ficha grande: palabra de contexto, rótulo, número, meta (si existe) y una nota."""
    col.markdown(f'<div class="tarjeta{" alerta" if alerta else ""}">'
                 f'<span class="contexto">{contexto or ("atención" if alerta else "al día")}</span>'
                 f'<div class="rotulo">{rotulo}</div><div class="valor">{valor}</div>'
                 f'<div class="meta">{meta or "&nbsp;"}</div><div class="nota">{nota or "&nbsp;"}</div></div>',
                 unsafe_allow_html=True)


def tabla(filas: list[dict], columna_estado: str | None = None, estado_de=None, fondo_fila=None):
    """Tabla con filas alternadas suaves y, si se da, el color de estado de cada fila."""
    import pandas as pd
    df = pd.DataFrame(filas)
    if df.empty:
        return df

    def pintar(fila):
        fondo = fondo_fila(fila.name) if fondo_fila else None
        if not fondo and columna_estado and estado_de:
            fondo = FONDO_ESTADO.get(estado_de(fila[columna_estado]))
        if not fondo and fila.name % 2:
            fondo = FILA_ALTERNA
        return [f"background-color: {fondo}" if fondo else ""] * len(fila)
    return df.style.apply(pintar, axis=1)


# ---------- indicadores ----------

def indicadores(ind: dict, plan: dict | None) -> None:
    c1, c2, c3, c4 = st.columns(4)
    tarjeta(c1, "Pedidos pendientes", str(ind["pedidos_pendientes"]),
            f"{ind['pedidos_por_confirmar']} por confirmar"
            + (f' · <span class="silencio">{ind["sin_contacto"]} sin contacto</span>' if ind["sin_contacto"] else ""),
            contexto="en espera")
    tarjeta(c2, "Perecederos que vencen en menos de 12 h", f"{ind['kg_vencen_pronto']:,.0f} kg".replace(",", "."),
            alerta=ind["kg_vencen_pronto"] > 0,
            contexto="vencen pronto" if ind["kg_vencen_pronto"] > 0 else "sin riesgo")
    tarjeta(c3, "Cierres activos", str(ind["cierres_activos"]),
            f"{ind['cierres_reportados']} por confirmar", alerta=ind["cierres_activos"] > 0,
            contexto="vías cerradas" if ind["cierres_activos"] > 0 else "vías abiertas")
    p = ind["puntualidad"]
    if p["pct"] is None:
        tarjeta(c4, "Pedidos del plan a tiempo", "–", "Sin plan" if not plan else "El plan no tiene paradas",
                contexto="sin plan", meta=f"meta {T.META_CRITICOS_PCT} %")
    else:
        crit = (f"Puntos críticos: <b>{p['pct_criticos']:.0f} %</b> ({p['criticos_a_tiempo']} de "
                f"{p['criticos_total']})" if p["pct_criticos"] is not None else "Sin puntos críticos en el plan")
        tarjeta(c4, f"Pedidos del plan a tiempo ({p['a_tiempo']} de {p['total']})", f"{p['pct']:.0f} %", crit,
                alerta=p["pct"] < T.META_CRITICOS_PCT, contexto="a tiempo",
                meta=f"meta {T.META_CRITICOS_PCT} %")


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
    pedidos = T.filas(con, "SELECT id, punto_id, estado, urgencia, kg_estimado, familias, origen FROM pedidos "
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
                                tooltip=S(f"{r['nombre']} · parada {s['orden']}")).add_to(fg)
        if len(r["regreso"]) >= 2:
            folium.PolyLine(r["regreso"], color=c, weight=3, opacity=0.6, dash_array="4 8",
                            tooltip=S(f"{r['nombre']} · regreso al acopio")).add_to(fg)

    for p in puntos.values():
        folium.CircleMarker([p["lat"], p["lon"]], radius=13 if p["critico"] else 6,
                            color="#1C2A24" if p["critico"] else "#5C6A62", weight=4 if p["critico"] else 1.5,
                            fill=False, tooltip=S(p["nombre"] + (" · PUNTO CRÍTICO" if p["critico"] else ""))
                            ).add_to(fg)
    for d in pedidos:
        p = puntos.get(d["punto_id"])
        if p:
            folium.CircleMarker([p["lat"], p["lon"]], radius=3 + 2.5 * (d["urgencia"] or 2), weight=1,
                                color="white", fill=True, fill_opacity=0.9,
                                fill_color=COLOR_SILENCIO if d.get("origen") == T.ORIGEN_SILENCIO
                                else COLOR_PEDIDO[d["estado"]],
                                tooltip=S(f"Pedido {d['id']} · {d['estado']} · urgencia {d['urgencia']} · "
                                          f"{d['kg_estimado'] or '?'} kg · {p['nombre']}")).add_to(fg)
    for r in rutas:
        for s in r["paradas"]:
            if s["lat"] is not None:
                folium.Marker([s["lat"], s["lon"]], icon=numero(s["orden"], colores[r["vehiculo_id"]]),
                              tooltip=S(f"{r['nombre']} · parada {s['orden']} · {s['punto']} · "
                                        f"llega {hora(s['llegada_estimada'])}"
                                        + ("" if s["a_tiempo"] else " · TARDE"))).add_to(fg)
    for a in acopios:
        folium.Marker([a["lat"], a["lon"]], tooltip=S(f"Acopio · {a['nombre']}"),
                      icon=folium.Icon(color="darkgreen", icon="warehouse", prefix="fa")).add_to(fg)
    for c in cierres:
        reportado = c["estado"] == "reportado"
        folium.Circle([c["lat"], c["lon"]], radius=140, color=ROJO, weight=5,
                      dash_array="8 10" if reportado else "16 8", fill=not reportado, fill_opacity=0.45,
                      tooltip=S(f"Cierre {c['id']} · {'por confirmar' if reportado else 'confirmado'} · "
                                f"{c['lugar'] or c['descripcion'] or ''}")).add_to(fg)

    for u in revisar["ubicaciones"]:
        que = f"{'Pedido' if u['tabla'] == 'pedidos' else 'Cierre'} {u['fila_id']}"
        if u["lat"] is not None:
            folium.Marker([u["lat"], u["lon"]], icon=folium.Icon(color="purple", icon="question", prefix="fa"),
                          tooltip=S(f"Propuesta · {que} · «{u['texto']}» = {u['lugar'] or '?'}")).add_to(fg)
        for c in u["alternativas"][:ALTERNATIVAS]:
            if c.get("lat") is not None:
                folium.CircleMarker([c["lat"], c["lon"]], radius=8, color=MORADO, weight=3, fill=True,
                                    fill_opacity=0.25, dash_array="3 5",
                                    tooltip=S(f"Alternativa · {que} · {c.get('nombre')}")).add_to(fg)
    if pin and pin.get("punto"):
        folium.Marker(pin["punto"], icon=folium.Icon(color="red", icon="location-dot", prefix="fa"),
                      tooltip=S("Punto marcado: falta guardarlo")).add_to(fg)

    st.session_state["capa"] = (firma, fg)
    return fg


def mapa(con, plan: dict | None, rutas: list[dict], revisar: dict) -> None:
    pin = st.session_state.get("pin")
    base = mapa_base.crear(CENTRO, 13)
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
    fichas += f'<span class="ficha"><b class="punto" style="background:{COLOR_SILENCIO}"></b>sin contacto</span>'
    fichas += (f'<span class="ficha"><b class="punto" style="border:3px solid #1C2A24"></b>punto crítico</span>'
               f'<span class="ficha"><b class="punto" style="border:3px dashed {ROJO}"></b>cierre (punteado)</span>')
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
              "aprobado": f"APROBADO por {html.escape(plan['aprobado_por'] or '?')} a las {hora(plan['aprobado_en'])}"
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


def tarjeta_silencio(con, d: dict) -> None:
    """Alerta por silencio: no trae familias ni kilos, y no se inventan."""
    with st.container(border=True):
        donde = html.escape(d["punto"] or "sin punto") + (' <span class="critico">· CRÍTICO</span>'
                                                          if d["critico"] else "")
        st.markdown(f'<span class="silencio">Sin contacto: verificar</span> **Pedido {d["id"]}** · {donde}',
                    unsafe_allow_html=True)
        if d["texto_original"]:
            st.caption(d["texto_original"])
        c1, c2 = st.columns(2)
        if c1.button("Mandar a verificar", type="primary", key=f"sv{d['id']}", width="stretch",
                     disabled=d["punto_id"] is None):
            ok = T.decidir_silencio(con, d["id"], "verificar", quien())
            avisar("ok" if ok else "error", f"Pedido {d['id']}: visita de verificación mandada por {quien()}."
                   if ok else "No se pudo mandar a verificar.")
            refrescar()
        if c2.button("Descartar", key=f"sd{d['id']}", width="stretch"):
            ok = T.decidir_silencio(con, d["id"], "descartar", quien())
            avisar("ok" if ok else "error", f"Alerta {d['id']} descartada por {quien()}." if ok
                   else "No se pudo descartar.")
            refrescar()


def por_revisar(con, revisar: dict) -> None:
    total = (len(revisar["ubicaciones"]) + len(revisar["pedidos"]) + len(revisar["cierres"])
             + len(revisar["silencio"]))
    st.subheader(f"Por revisar ({total})")
    if not total and not revisar["confirmados_sin_ubicar"]:
        st.markdown("Nada pendiente.")

    for d in revisar["silencio"]:
        tarjeta_silencio(con, d)

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
        st.dataframe(tabla([{"Orden": s["orden"], "Punto": s["punto"], "Crítico": "sí" if s["critico"] else "",
                             "Pedido": s["pedido_id"], "Llega": hora(s["llegada_estimada"]),
                             "Límite": limite(s["limite_en"]), "A tiempo": "sí" if s["a_tiempo"] else "TARDE",
                             "kg": s["kg"]} for s in r["paradas"]],
                           columna_estado="A tiempo",
                           estado_de=lambda v: "pendiente" if v == "TARDE" else None),
                     hide_index=True, width="stretch")
    fuera = T.sin_atender(con, plan)
    if fuera:
        st.markdown("**Sin atender**")
        st.dataframe(tabla([{"Pedido": x["pedido_id"], "Punto": x["punto"], "Crítico": "sí" if x["critico"] else "",
                             "Motivo": x["motivo"]} for x in fuera]), hide_index=True, width="stretch")
    faltantes = plan["resumen"].get("faltantes") or []
    if faltantes:
        st.markdown("**Faltantes de inventario:** " + "; ".join(
            f"pedido {f.get('pedido_id')}, {f.get('producto')}, {f.get('kg')} kg" for f in faltantes))
    for a in plan["resumen"].get("avisos") or []:
        st.caption(f"Aviso del optimizador: {a}")


TITULOS_TERRITORIO = {
    "territorio": "Territorio", "puntos": "Puntos", "puntos_criticos": "Críticos", "pedidos": "Pedidos",
    "familias": "Familias", "kg_pedidos": "kg pedidos", "entregados": "Entregados",
    "kg_entregados": "kg entregados", "a_tiempo": "A tiempo", "evaluados": "Evaluados",
    "pct_a_tiempo": "% a tiempo", "criticos_a_tiempo": "Críticos a tiempo",
    "criticos_evaluados": "Críticos evaluados", "pct_criticos_a_tiempo": "% críticos a tiempo",
    "espera_mediana_h": "Espera mediana (h)", "pendiente_mas_viejo_h": "Pendiente más viejo (h)"}
TITULOS_SIN_PEDIDOS = {"nombre": "Lugar", "tipo": "Tipo", "comuna": "Comuna", "estado": "Estado"}
FONDO_BAJO_META = "#F7EAD0"       # maíz muy suave: por debajo de la meta


def detalle_territorio(con) -> None:
    d = T.territorio(con)
    if not d["disponible"]:
        st.info("Pendiente: despacho.territorio")
        return
    st.markdown(f"**Atención por territorio** · los peor atendidos arriba · en color, los que están por "
                f"debajo de la meta de {d['meta']} % de críticos a tiempo")
    bajo = [f["bajo_meta"] for f in d["tabla"]]
    if d["tabla"]:
        st.dataframe(tabla([{TITULOS_TERRITORIO.get(c, c): f.get(c) for c in d["columnas"]} for f in d["tabla"]],
                           fondo_fila=lambda i: FONDO_BAJO_META if bajo[i] else None),
                     hide_index=True, width="stretch")
    else:
        st.markdown("Todavía no hay territorios con datos.")
    st.download_button("Descargar CSV", T.territorio_csv(d), file_name="territorio.csv", mime="text/csv",
                       key="territorio_csv")
    st.caption("A tiempo: entregado a más tardar en su hora límite. Evaluados: pedidos con hora límite ya "
               "entregados o con la hora vencida.")
    st.markdown(f"**Barrios y veredas sin pedidos registrados ({len(d['sin_pedidos'])})**")
    st.caption("Que un lugar no haya pedido no quiere decir que esté bien: puede no tener señal ni líder.")
    if d["sin_pedidos"]:
        st.dataframe(tabla([{TITULOS_SIN_PEDIDOS.get(c, c): s.get(c) or "" for c in d["columnas_sin_pedidos"]}
                            for s in d["sin_pedidos"]], columna_estado="Estado", estado_de=lambda v: "silencio"),
                     hide_index=True, width="stretch", height=360)
    else:
        st.markdown("Todos los barrios y veredas del nomenclátor tienen pedidos registrados.")


def estado_de_accion(accion: str | None) -> str | None:
    """Color de estado de una fila de la bitácora según la acción registrada."""
    a = (accion or "").lower()
    if "silencio" in a or "verificar" in a:
        return "silencio"
    if "entreg" in a:
        return "entregado"
    if "aprob" in a or "asign" in a:
        return "en ruta"
    if "confirm" in a:
        return "pendiente"
    return None


def reinicio_datos(con) -> None:
    """Botón para volver a la semilla antes de una demo. Pide confirmación con una casilla aparte."""
    with st.expander("Reiniciar datos de prueba"):
        st.caption("Borra pedidos, cierres, planes, inventario y ubicaciones de esta base y carga la semilla "
                   "sintética (`python -m despacho.semilla --cargar --reiniciar`). Solo para pruebas y demos.")
        seguro = st.checkbox("Sí, borrar los datos y cargar la semilla", key="confirmar_reinicio")
        if st.button("Reiniciar datos de prueba", type="primary", disabled=not seguro, key="reiniciar_datos"):
            r = correr("Cargando la semilla…", T.reiniciar_datos_prueba, con, quien())
            st.session_state.pop("confirmar_reinicio", None)
            st.session_state.pop("capa", None)
            avisar("ok" if r.ok else "error", f"Datos de prueba reiniciados por {quien()}." if r.ok
                   else f"No se pudo reiniciar: {r.mensaje}")
            refrescar()


SIN_DATOS = "Sin datos todavía"
FONDO_VENCE = "#F7EAD0"            # maíz muy suave (antes #F6E9E2, paleta vieja): perecedero que vence en menos de 12 h


def _kg(v) -> str:
    return f"{v or 0:,.0f} kg".replace(",", ".")


def _barras(filas: list[dict], categoria: str, series: dict[str, str], titulo_y: str = "kg"):
    """Barras agrupadas con altair (viene con Streamlit). series: columna -> rótulo."""
    import altair as alt
    import pandas as pd
    df = pd.DataFrame([{categoria: html.escape(str(f.get(categoria) or "?")), "serie": rotulo,
                        "kg": float(f.get(col) or 0)} for f in filas for col, rotulo in series.items()])
    colores = [TINTA, AMBAR, CENIZA, CREMA][:len(series)]
    return (alt.Chart(df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(x=alt.X(f"{categoria}:N", sort="-y", title=None),
                    y=alt.Y("kg:Q", title=titulo_y), xOffset="serie:N",
                    color=alt.Color("serie:N", title=None,
                                    scale=alt.Scale(domain=list(series.values()), range=colores)),
                    tooltip=[f"{categoria}:N", "serie:N", alt.Tooltip("kg:Q", format=",.0f")])
            .properties(height=280))


def detalle_informe(con) -> None:
    """Solo lectura: lo mandado y lo que hay en bodega, tal como lo registra la base."""
    inf = T.informe(con)
    r = inf["resumen"]
    c1, c2, c3, c4 = st.columns(4)
    tarjeta(c1, "Pedidos atendidos (entregados)", str(r["pedidos_atendidos"]),
            f"{r['pedidos_pendientes']} pendientes (nuevos, confirmados y asignados)", contexto="pedidos")
    tarjeta(c2, "Despachado (paquetes en ruta o entregados)", _kg(r["kg_despachados"]),
            f"Entregado: <b>{_kg(r['kg_entregados'])}</b>", contexto="mandado")
    tarjeta(c3, "Inventario cargado en bodega", _kg(r["kg_inventario_cargado"]),
            "Suma de lotes.kg: no se descuenta al despachar", contexto="bodega")
    crit = ("–" if r["pct_criticos_a_tiempo"] is None else f"{r['pct_criticos_a_tiempo']:.0f} %")
    tarjeta(c4, "Críticos entregados a tiempo", crit,
            f"{r['criticos_a_tiempo']} de {r['criticos_evaluados']} evaluados", contexto="críticos",
            alerta=r["pct_criticos_a_tiempo"] is not None and r["pct_criticos_a_tiempo"] < T.META_CRITICOS_PCT,
            meta=f"meta {T.META_CRITICOS_PCT} %")
    c5, c6, _, _ = st.columns(4)
    tarjeta(c5, "Perecederos que vencen en menos de 12 h", _kg(r["kg_vencen_12h"]),
            alerta=r["kg_vencen_12h"] > 0, contexto="vencen pronto" if r["kg_vencen_12h"] > 0 else "sin riesgo")
    tarjeta(c6, "Perecederos que vencen en menos de 24 h", _kg(r["kg_vencen_24h"]),
            alerta=r["kg_vencen_24h"] > 0, contexto="próximas 24 h")

    st.subheader("Lo que se ha mandado")
    st.markdown("**kg por producto** · despachado y entregado (de los paquetes)")
    if inf["por_producto"]:
        st.altair_chart(_barras(inf["por_producto"], "producto",
                                {"kg_despachado": "despachado", "kg_entregado": "entregado"}), use_container_width=True)
    else:
        st.markdown(SIN_DATOS)
    a, b = st.columns(2)
    with a:
        st.markdown("**Por vehículo** · planes aprobados")
        if inf["vehiculos"]:
            st.dataframe(tabla([{"Vehículo": v["vehiculo"], "Tipo": v["tipo"], "Paradas": v["paradas"],
                                 "kg": round(v["kg"] or 0, 1), "Estado": v["estado"]} for v in inf["vehiculos"]]),
                         hide_index=True, width="stretch")
        else:
            st.markdown(SIN_DATOS)
    with b:
        st.markdown("**kg por territorio** · pedidos y entregados")
        if inf["por_territorio"]:
            st.altair_chart(_barras(inf["por_territorio"], "territorio",
                                    {"kg_pedidos": "pedido", "kg_entregados": "entregado"}),
                            use_container_width=True)
        else:
            st.markdown(SIN_DATOS)

    st.subheader("Lo que hay en bodega")
    st.caption("Inventario cargado: los lotes registrados. La base no descuenta los kilos despachados, así que "
               "no es la existencia real.")
    if inf["bodega"]:
        st.altair_chart(_barras([{"producto": f["producto"], f["acopio"]: f["kg"]} for f in inf["bodega"]],
                                "producto", {ac: ac for ac in sorted({f["acopio"] for f in inf["bodega"]})},
                                "kg cargados"), use_container_width=True)
        vence = [l["vence_pronto"] for l in inf["lotes"]]
        st.markdown("**Lotes por vencimiento** · en ámbar, perecederos que vencen en menos de 12 h")
        st.dataframe(tabla([{"Lote": l["id"], "Producto": l["producto"], "Acopio": l["acopio"],
                             "kg": l["kg"], "Perecedero": "sí" if l["perecedero"] else "",
                             "Vence": limite(l["vence_en"]) if l["vence_en"] else "",
                             "Horas para vencer": l["horas_para_vencer"]} for l in inf["lotes"]],
                           fondo_fila=lambda i: FONDO_VENCE if vence[i] else None),
                     hide_index=True, width="stretch")
    else:
        st.markdown(SIN_DATOS)
    st.download_button("Descargar informe (CSV)", T.informe_csv(inf), file_name="informe.csv", mime="text/csv",
                       key="informe_csv")


def detalle_bitacora(con) -> None:
    filas = T.bitacora(con, 60)
    if not filas:
        st.markdown("Todavía no hay decisiones registradas.")
        return
    st.dataframe(tabla([{"Hora": hora(f["cuando"]), "Quién": f["quien"], "Acción": f["accion"],
                         "Detalle": f["detalle"]} for f in filas],
                       columna_estado="Acción", estado_de=estado_de_accion),
                 hide_index=True, width="stretch", height=600)


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
        t_mesa, t_plan, t_territorio, t_informe, t_bitacora = st.tabs(
            ["Mesa", "Plan en detalle", "Territorio", "Informe", "Bitácora"])
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
        with t_territorio:
            detalle_territorio(con)
        with t_informe:
            detalle_informe(con)
        with t_bitacora:
            detalle_bitacora(con)
            reinicio_datos(con)
    finally:
        con.close()


def main() -> None:
    st.set_page_config(page_title=f"{NOMBRE} · Mesa de despacho", layout="wide")
    st.markdown(ESTILO, unsafe_allow_html=True)
    st.logo(str(RAIZ / "recursos" / "marca" / "convite_logo_transparente.png"), size="large")
    if not clave_ok():
        st.stop()
    c1, c2 = st.columns([5, 1])
    c1.title(f"{NOMBRE} · Mesa de despacho")
    c2.text_input("Despachador", key="quien", placeholder="Tu nombre", label_visibility="collapsed")
    mesa()


main()
