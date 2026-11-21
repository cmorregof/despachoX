"""Lecturas y cambios de estado del tablero, separados de la interfaz para poder probarlos.

Reglas del módulo:
- El tablero lee todas las tablas y solo cambia estados (pedidos, cierres, planes). Cada cambio
  queda en la bitácora.
- No calcula rutas: pide el plan a `despacho/` con `ejecutar_despacho` (un proceso aparte).
- Las ubicaciones se confirman o corrigen con las funciones de `lugares/`.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import lugares
from datos import db

try:            # parte B de encargos/T1_TERRITORIO.md; si no ha llegado, la pestaña lo dice
    from despacho import territorio as _territorio
except Exception:  # noqa: BLE001 - cualquier fallo de importación deja la pestaña en «pendiente»
    _territorio = None

try:            # parte 3 de encargos/S3_MUCHOS_PEDIDOS.md; sin estos módulos no hay vista de grupos
    from despacho import agrupar as _agrupar
    from despacho import resumen_grupo as _resumen_grupo
except Exception:  # noqa: BLE001 - cualquier fallo de importación deja la vista de grupos vacía
    _agrupar = _resumen_grupo = None

RAIZ = Path(__file__).resolve().parent.parent
HORAS_VENCE_PRONTO = 12
# Meta de críticos a tiempo: la misma de la ficha de puntualidad, que se marca en alerta por debajo
# del 100 %. No hay otra meta numérica en el código ni en CLAUDE.md.
META_CRITICOS_PCT = 100
ORIGEN_SILENCIO = "silencio"
# decisión sobre una alerta por silencio -> (estado nuevo del pedido, acción en la bitácora)
ACCIONES_SILENCIO = {"verificar": ("confirmado", "mandar a verificar"),
                     "descartar": ("descartado", "descartar alerta por silencio")}
# Solo se usa si el plan no trae sus supuestos; es el mismo valor de despacho/optimizar.py.
LIMITE_POR_URGENCIA_H = {3: 4, 2: 12, 1: 24}

# Cambios de estado que el tablero puede hacer: tabla -> {estado nuevo: estados de partida}.
TRANSICIONES = {
    "pedidos": {"confirmado": {"nuevo"}, "descartado": {"nuevo", "confirmado"}},
    "cierres": {"confirmado": {"reportado"}, "levantado": {"reportado", "confirmado"}},
    "planes": {"rechazado": {"propuesto"}},
}


# ---------- utilidades ----------

def filas(con: sqlite3.Connection, sql: str, args: tuple = ()) -> list[dict]:
    return [dict(r) for r in con.execute(sql, args).fetchall()]


def _json(texto: str | None, por_defecto):
    try:
        valor = json.loads(texto) if texto else por_defecto
    except (json.JSONDecodeError, TypeError):
        return por_defecto
    return valor if isinstance(valor, type(por_defecto)) else por_defecto


def _fecha(texto: str | None) -> datetime | None:
    if not texto:
        return None
    try:
        f = datetime.fromisoformat(texto)
    except ValueError:
        return None
    return f if f.tzinfo else f.replace(tzinfo=db.BOGOTA)


def _ahora(ahora: datetime | None) -> datetime:
    return ahora or datetime.now(db.BOGOTA)


# ---------- plan ----------

def _plan(fila: sqlite3.Row | None) -> dict | None:
    if fila is None:
        return None
    p = dict(fila)
    p["resumen"] = _json(p.get("resumen"), {})
    return p


def plan(con: sqlite3.Connection, plan_id: int) -> dict | None:
    return _plan(con.execute("SELECT * FROM planes WHERE id=?", (plan_id,)).fetchone())


def plan_vigente(con: sqlite3.Connection) -> dict | None:
    """El plan que el despachador tiene que mirar: la última propuesta y, si no hay, el aprobado."""
    return _plan(con.execute(
        "SELECT * FROM planes WHERE estado IN ('propuesto','aprobado') "
        "ORDER BY (estado='propuesto') DESC, id DESC LIMIT 1").fetchone())


def plan_aprobado(con: sqlite3.Connection) -> dict | None:
    return _plan(con.execute(
        "SELECT * FROM planes WHERE estado='aprobado' ORDER BY id DESC LIMIT 1").fetchone())


def paradas(con: sqlite3.Connection, p: dict | None) -> list[dict]:
    """Paradas del plan con el punto, el vehículo y si llegan antes del límite del pedido."""
    if not p:
        return []
    horas = {int(k): v for k, v in
             (p["resumen"].get("supuestos", {}).get("limite_por_urgencia_h") or LIMITE_POR_URGENCIA_H).items()}
    calculado = _fecha(p["resumen"].get("calculado_para")) or _fecha(p["creado_en"])
    salida = filas(con, """
        SELECT pa.id, pa.vehiculo_id, pa.orden, pa.punto_id, pa.pedido_id, pa.llegada_estimada, pa.kg,
               pa.geometria, pu.nombre AS punto, pu.lat, pu.lon, COALESCE(pu.critico, 0) AS critico,
               v.nombre AS vehiculo, v.tipo AS tipo_vehiculo,
               pe.limite_en, pe.creado_en AS pedido_creado_en, pe.urgencia
        FROM paradas pa
        LEFT JOIN puntos pu ON pu.id = pa.punto_id
        LEFT JOIN vehiculos v ON v.id = pa.vehiculo_id
        LEFT JOIN pedidos pe ON pe.id = pa.pedido_id
        WHERE pa.plan_id = ? ORDER BY pa.vehiculo_id, pa.orden""", (p["id"],))
    for s in salida:
        s["geometria"] = _json(s["geometria"], [])
        llegada = _fecha(s["llegada_estimada"])
        limite = _fecha(s["limite_en"])
        if limite is None:
            base = _fecha(s["pedido_creado_en"]) or calculado
            limite = base + timedelta(hours=horas.get(s["urgencia"] or 2, 12)) if base else None
        s["a_tiempo"] = bool(llegada and limite and llegada <= limite)
        s["minutos_desde_salida"] = (
            (llegada - calculado).total_seconds() / 60 if llegada and calculado else None)
    return salida


def sin_atender(con: sqlite3.Connection, p: dict | None) -> list[dict]:
    """Pedidos que el plan dejó por fuera, con el motivo que dio el optimizador."""
    if not p:
        return []
    puntos = {r["id"]: r for r in filas(con, "SELECT id, nombre, critico FROM puntos")}
    salida = []
    for x in p["resumen"].get("sin_atender") or []:
        if not isinstance(x, dict):
            continue
        pu = puntos.get(x.get("punto_id"), {})
        salida.append({"pedido_id": x.get("pedido_id"), "punto_id": x.get("punto_id"),
                       "punto": pu.get("nombre") or "sin punto", "critico": int(pu.get("critico") or 0),
                       "motivo": x.get("motivo") or "sin motivo"})
    return salida


def puntualidad(con: sqlite3.Connection, p: dict | None) -> dict:
    """Porcentaje de pedidos del plan que llegan a tiempo; los puntos críticos aparte.

    Un pedido sin atender cuenta como no entregado a tiempo: el denominador son todos los
    pedidos que el plan consideró.
    """
    ps, fuera = paradas(con, p), sin_atender(con, p)
    total = len(ps) + len(fuera)
    a_tiempo = sum(s["a_tiempo"] for s in ps)
    crit = [s for s in ps if s["critico"]]
    crit_total = len(crit) + sum(1 for x in fuera if x["critico"])
    crit_a_tiempo = sum(s["a_tiempo"] for s in crit)

    def pct(n: int, d: int) -> float | None:
        return round(100 * n / d, 1) if d else None

    return {"total": total, "a_tiempo": a_tiempo, "pct": pct(a_tiempo, total),
            "criticos_total": crit_total, "criticos_a_tiempo": crit_a_tiempo,
            "pct_criticos": pct(crit_a_tiempo, crit_total)}


def rutas(con: sqlite3.Connection, p: dict | None) -> list[dict]:
    """Una entrada por vehículo del plan: tramos hasta cada parada y el regreso al acopio."""
    por_vehiculo: dict[int, dict] = {}
    for s in paradas(con, p):
        r = por_vehiculo.setdefault(s["vehiculo_id"], {
            "vehiculo_id": s["vehiculo_id"], "nombre": s["vehiculo"] or f"Vehículo {s['vehiculo_id']}",
            "tipo": s["tipo_vehiculo"], "paradas": [], "regreso": [], "kg": 0.0, "capacidad_kg": None})
        r["paradas"].append(s)
        r["kg"] += s["kg"] or 0
    for v in (p or {}).get("resumen", {}).get("vehiculos") or []:
        if not isinstance(v, dict):
            continue
        r = por_vehiculo.get(v.get("vehiculo_id", v.get("id")))
        if r:
            r["regreso"] = v.get("regreso") or []
            r["capacidad_kg"] = v.get("capacidad_kg")
            r["nombre"] = v.get("nombre") or r["nombre"]
    return [por_vehiculo[k] for k in sorted(por_vehiculo)]


# ---------- cierres y recálculo ----------

def cierres_sin_aplicar(con: sqlite3.Connection, p: dict | None) -> list[dict]:
    """Cierres confirmados que el plan vigente no tuvo en cuenta. Si hay alguno, toca recalcular."""
    if not p:
        return []
    aplicados = set(p["resumen"].get("cierres_aplicados") or [])
    # Un recálculo lleva el motivo «cierre N»: ya vio los cierres hasta N. Si alguno de esos no
    # quedó aplicado es porque no se pudo amarrar a la red, y recalcular otra vez no lo arregla.
    motivo = str(p.get("motivo") or "")
    visto_hasta = int(motivo.split()[1]) if motivo.startswith("cierre ") and motivo.split()[1].isdigit() else 0
    pendientes = []
    for c in filas(con, "SELECT * FROM cierres WHERE estado='confirmado' ORDER BY id"):
        if c["id"] in aplicados:
            continue
        if c["id"] <= visto_hasta and not _confirmado_despues(con, c["id"], p["creado_en"]):
            continue
        pendientes.append(c)
    return pendientes


def _confirmado_despues(con: sqlite3.Connection, cierre_id: int, momento: str) -> bool:
    """True si la bitácora registra una confirmación de ese cierre posterior a `momento`."""
    r = con.execute("SELECT MAX(cuando) AS c FROM bitacora WHERE accion='confirmar cierre' AND detalle LIKE ?",
                    (f"cierres {cierre_id} %",)).fetchone()
    return bool(r and r["c"] and r["c"] >= momento)


def comparar_planes(con: sqlite3.Connection, nuevo: dict | None, anterior: dict | None) -> dict | None:
    """Qué cambió entre dos planes: vehículos con otra ruta y la llegada que más se movió.

    Las llegadas se comparan en minutos desde la hora de cálculo de cada plan, para no contar
    como cambio el tiempo que pasó entre un cálculo y el otro.
    """
    if not nuevo or not anterior:
        return None
    rn = {r["vehiculo_id"]: r for r in rutas(con, nuevo)}
    ra = {r["vehiculo_id"]: r for r in rutas(con, anterior)}
    cambiados = []
    for vid in sorted(set(rn) | set(ra)):
        a, n = ra.get(vid), rn.get(vid)
        orden_a = [s["pedido_id"] for s in a["paradas"]] if a else []
        orden_n = [s["pedido_id"] for s in n["paradas"]] if n else []
        if orden_a != orden_n:
            tipo = "paradas distintas" if set(orden_a) != set(orden_n) else "otro orden"
        elif [s["geometria"] for s in a["paradas"]] != [s["geometria"] for s in n["paradas"]] \
                or a["regreso"] != n["regreso"]:
            tipo = "desvío"
        else:
            continue
        cambiados.append({"vehiculo_id": vid, "nombre": (n or a)["nombre"], "cambio": tipo})

    antes = {s["pedido_id"]: s for r in ra.values() for s in r["paradas"]}
    mayor = None
    for r in rn.values():
        for s in r["paradas"]:
            a = antes.get(s["pedido_id"])
            if not a or s["minutos_desde_salida"] is None or a["minutos_desde_salida"] is None:
                continue
            delta = s["minutos_desde_salida"] - a["minutos_desde_salida"]
            if mayor is None or abs(delta) > abs(mayor["minutos"]):
                mayor = {"pedido_id": s["pedido_id"], "punto": s["punto"], "vehiculo": r["nombre"],
                         "minutos": round(delta)}
    ids_n = {s["pedido_id"] for r in rn.values() for s in r["paradas"]}
    return {"plan": nuevo["id"], "anterior": anterior["id"], "vehiculos": cambiados, "mayor": mayor,
            "salen": sorted(set(antes) - ids_n), "entran": sorted(ids_n - set(antes))}


def cambios_del_recalculo(con: sqlite3.Connection, p: dict | None) -> dict | None:
    """Si el plan vigente salió de un recálculo, lo compara con el plan que reemplazó."""
    if not p or not str(p.get("motivo") or "").startswith(("cierre", "recálculo")):
        return None
    for anterior_id in p["resumen"].get("reemplaza_a") or []:
        anterior = plan(con, anterior_id)
        if anterior and con.execute("SELECT 1 FROM paradas WHERE plan_id=? LIMIT 1", (anterior_id,)).fetchone():
            return comparar_planes(con, p, anterior)
    return None


# ---------- indicadores ----------

def indicadores(con: sqlite3.Connection, p: dict | None = None, ahora: datetime | None = None) -> dict:
    ahora = _ahora(ahora)
    tope = ahora + timedelta(hours=HORAS_VENCE_PRONTO)
    # Las alertas por silencio no son pedidos de comida: se cuentan aparte, como «sin contacto».
    pendientes = con.execute("SELECT COUNT(*) FROM pedidos WHERE estado IN ('nuevo','confirmado') "
                             "AND duplicado_de IS NULL AND COALESCE(origen, 'mensaje') != ?",
                             (ORIGEN_SILENCIO,)).fetchone()[0]
    por_confirmar = con.execute("SELECT COUNT(*) FROM pedidos WHERE estado='nuevo' "
                                "AND duplicado_de IS NULL AND COALESCE(origen, 'mensaje') != ?",
                                (ORIGEN_SILENCIO,)).fetchone()[0]
    sin_contacto = con.execute("SELECT COUNT(*) FROM pedidos WHERE estado IN ('nuevo','confirmado') "
                               "AND origen = ?", (ORIGEN_SILENCIO,)).fetchone()[0]
    kg = 0.0
    for lote in filas(con, "SELECT kg, vence_en FROM lotes WHERE perecedero=1 AND vence_en IS NOT NULL"):
        vence = _fecha(lote["vence_en"])
        if vence and ahora <= vence <= tope:
            kg += lote["kg"] or 0
    activos = con.execute("SELECT COUNT(*) FROM cierres WHERE estado='confirmado'").fetchone()[0]
    reportados = con.execute("SELECT COUNT(*) FROM cierres WHERE estado='reportado'").fetchone()[0]
    return {"pedidos_pendientes": pendientes, "pedidos_por_confirmar": por_confirmar,
            "sin_contacto": sin_contacto,
            "kg_vencen_pronto": round(kg, 1), "cierres_activos": activos,
            "cierres_reportados": reportados, "puntualidad": puntualidad(con, p)}


# ---------- por revisar ----------

def por_revisar(con: sqlite3.Connection) -> dict:
    """Lo que espera una decisión del despachador: pedidos nuevos, cierres reportados y ubicaciones."""
    puntos = {r["id"]: r for r in filas(con, "SELECT * FROM puntos")}
    todos = filas(con, "SELECT * FROM pedidos WHERE estado='nuevo' AND duplicado_de IS NULL "
                       "ORDER BY urgencia DESC, id")
    # Las alertas por silencio (entrada/silencio.py) no son pedidos de comida: van aparte.
    silencio = [d for d in todos if d.get("origen") == ORIGEN_SILENCIO]
    pedidos = [d for d in todos if d.get("origen") != ORIGEN_SILENCIO]
    for d in silencio:
        pu = puntos.get(d["punto_id"])
        d["punto"] = pu["nombre"] if pu else None
        d["critico"] = int(pu["critico"] or 0) if pu else 0
    # Los repetidos de todos los pedidos nuevos en una sola consulta: con miles de pedidos, una
    # consulta por pedido tardaba 5,6 s (docs/ESCALA_DESPACHO.md).
    repetidos: dict[int, list[dict]] = {}
    for r in filas(con, "SELECT d.id, d.texto_original, d.duplicado_de FROM pedidos d "
                        "JOIN pedidos m ON m.id = d.duplicado_de "
                        "WHERE m.estado='nuevo' AND m.duplicado_de IS NULL AND d.estado != 'descartado' "
                        "ORDER BY d.id"):
        repetidos.setdefault(r.pop("duplicado_de"), []).append(r)
    for d in pedidos:
        pu = puntos.get(d["punto_id"])
        d["punto"] = pu["nombre"] if pu else None
        d["critico"] = int(pu["critico"] or 0) if pu else 0
        d["sin_ubicar"] = pu is None
        d["duplicados"] = repetidos.get(d["id"], [])
    # Un pedido confirmado sin punto no entra al plan: también hay que mostrarlo.
    sin_ubicar = filas(con, "SELECT * FROM pedidos WHERE estado='confirmado' AND punto_id IS NULL ORDER BY id")
    cierres = filas(con, "SELECT * FROM cierres WHERE estado='reportado' ORDER BY id")
    ubicaciones = filas(con, """
        SELECT u.*, l.nombre AS lugar, l.tipo AS lugar_tipo FROM ubicaciones u
        LEFT JOIN lugares l ON l.id = u.lugar_id WHERE u.estado='propuesta' ORDER BY u.id""")
    for u in ubicaciones:
        u["candidatos"] = [c for c in _json(u["candidatos"], []) if isinstance(c, dict)]
        u["alternativas"] = [c for c in u["candidatos"] if c.get("lugar_id") != u["lugar_id"]]
        origen = con.execute(f"SELECT texto_original FROM {u['tabla']} WHERE id=?",  # tabla validada por el esquema
                             (u["fila_id"],)).fetchone() if u["tabla"] in ("pedidos", "cierres") else None
        u["texto_completo"] = origen["texto_original"] if origen else None
    return {"pedidos": pedidos, "confirmados_sin_ubicar": sin_ubicar, "cierres": cierres,
            "ubicaciones": ubicaciones, "silencio": silencio}


def grupos_por_revisar(con: sqlite3.Connection, ahora: datetime | None = None) -> list[dict]:
    """Grupos de pedidos nuevos por punto, detrás de DESPACHOX_AGRUPAR. Apagada, lista vacía.

    Las sumas las hace despacho/agrupar.py con código; el resumen es lo que leyó el modelo y no cambia
    ningún número. El despachador confirma o descarta el grupo entero.
    """
    if _agrupar is None or not _agrupar.activo():
        return []
    puntos = {r["id"]: r["nombre"] for r in con.execute("SELECT id, nombre FROM puntos")}
    salida = []
    for g in _agrupar.grupos_nuevos(con, ahora=ahora):
        r = _resumen_grupo.leer(con, g.clave) if _resumen_grupo is not None else None
        salida.append({
            "clave": g.clave, "punto_id": g.punto_id, "punto": puntos.get(g.punto_id),
            "critico": bool(g.critico), "n_pedidos": len(g.pedido_ids), "pedido_ids": list(g.pedido_ids),
            "familias": g.familias, "familias_declaradas": g.familias_declaradas, "sobre_tope": g.sobre_tope,
            "tope_familias": g.tope_familias, "kg": g.kg, "urgencia": g.urgencia, "limite_en": g.limite_en,
            "resumen": r["resumen"] if r else None, "resumen_modelo": r["modelo"] if r else None,
            "pedidos": [{k: p.get(k) for k in ("id", "texto_original", "familias", "kg_estimado", "urgencia")}
                        for p in g.pedidos]})
    return salida


def resumen_mesa(con: sqlite3.Connection, ahora: datetime | None = None) -> dict | None:
    """El resumen de toda la mesa que leyó el modelo para los grupos vigentes, o None si no hay o la
    variable está apagada. Cambia de clave cuando cambian los grupos, así no se muestra uno viejo."""
    if _agrupar is None or _resumen_grupo is None or not _agrupar.activo():
        return None
    grupos = _agrupar.grupos_nuevos(con, ahora=ahora)
    r = _resumen_grupo.leer_mesa(con, grupos)
    if not r:
        return None
    return {"resumen": r["resumen"], "modelo": r["modelo"], "creado_en": r["creado_en"], "grupos": len(grupos)}


RESUMIR = ("despacho.resumen_grupo", "--resumir")
ESPERA_RESUMIR_S = 600


def resumir_grupos(correr=subprocess.run, espera_s: int = ESPERA_RESUMIR_S, falso: bool = False) -> Corrida:
    """Ejecuta `python -m despacho.resumen_grupo --resumir` (hereda DESPACHOX_DB y la clave del modelo)."""
    args = [sys.executable, "-m", *RESUMIR] + (["--falso"] if falso else [])
    try:
        r = correr(args, cwd=RAIZ, capture_output=True, text=True, timeout=espera_s)
    except subprocess.TimeoutExpired:
        return Corrida(False, None, f"el resumen no terminó en {espera_s} s")
    except OSError as e:
        return Corrida(False, None, f"no se pudo ejecutar despacho.resumen_grupo: {e}")
    ultima = ((r.stdout or "").strip().splitlines() or [""])[-1]
    error = ((r.stderr or "").strip().splitlines() or [""])[-1]
    try:
        cifras = json.loads(ultima)
    except ValueError:
        return Corrida(False, None, error or "el resumen no devolvió cifras")
    if r.returncode != 0:
        return Corrida(False, None, f"{cifras.get('sin_resumen', cifras.get('fallos', '?'))} grupos quedaron sin "
                                    f"resumen ({cifras.get('fallos', '?')} llamadas fallaron); {error}")
    modelos = cifras.get("modelo", "?")
    if cifras.get("modelo_mesa") and cifras["modelo_mesa"] != modelos:
        modelos += f" y {cifras['modelo_mesa']} para la mesa"
    return Corrida(True, None, f"{cifras.get('resumidos', 0)} grupos resumidos de {cifras.get('grupos', 0)}"
                   + (", y la mesa" if cifras.get("mesa") else "") + f" con {modelos}"
                   + (f"; {cifras.get('tokens_entrada', 0):,} tokens de entrada, "
                      f"{cifras.get('costo_usd', 0):.4f} USD estimados" if cifras.get("modelo") != "falso" else ""))


def _decidir_grupo(con: sqlite3.Connection, pedido_ids: list[int], estado: str, quien: str,
                   clave: str | None) -> int:
    n = sum(cambiar_estado(con, "pedidos", int(i), estado, quien) for i in pedido_ids)
    accion = {"confirmado": "confirmar grupo", "descartado": "descartar grupo"}[estado]
    db.anotar(con, quien or "despachador", accion,
              f"grupo {clave or '?'} pedidos {json.dumps([int(i) for i in pedido_ids])} -> {estado} ({n})")
    return n


def confirmar_grupo(con: sqlite3.Connection, pedido_ids: list[int], quien: str, clave: str | None = None) -> int:
    """Confirma cada pedido del grupo (cada uno queda en la bitácora) y anota el grupo. Devuelve cuántos."""
    return _decidir_grupo(con, pedido_ids, "confirmado", quien, clave)


def descartar_grupo(con: sqlite3.Connection, pedido_ids: list[int], quien: str, clave: str | None = None) -> int:
    """Descarta cada pedido del grupo y anota el grupo. Devuelve cuántos cambiaron."""
    return _decidir_grupo(con, pedido_ids, "descartado", quien, clave)


# ---------- cambios de estado ----------

def cambiar_estado(con: sqlite3.Connection, tabla: str, fila_id: int, estado: str, quien: str) -> bool:
    """Cambia el estado de un pedido, un cierre o un plan y lo anota. False si el cambio no aplica."""
    permitidos = TRANSICIONES.get(tabla, {}).get(estado)
    if not permitidos:
        return False
    actual = con.execute(f"SELECT * FROM {tabla} WHERE id=?", (fila_id,)).fetchone()
    if actual is None or actual["estado"] not in permitidos:
        return False
    if tabla == "pedidos" and estado == "confirmado" and actual["punto_id"] is None:
        return False            # sin ubicar: primero se confirma la ubicación
    con.execute(f"UPDATE {tabla} SET estado=? WHERE id=?", (estado, fila_id))
    con.commit()
    verbo = {"confirmado": "confirmar", "descartado": "descartar", "levantado": "levantar",
             "rechazado": "rechazar"}[estado]
    db.anotar(con, quien, f"{verbo} {tabla[:-1] if tabla != 'planes' else 'plan'}",
              f"{tabla} {fila_id} -> {estado}")
    return True


def decidir_silencio(con: sqlite3.Connection, pedido_id: int, decision: str, quien: str) -> bool:
    """El despachador decide sobre una alerta por silencio. False si no aplica.

    «verificar»: el pedido pasa a 'confirmado'; despacho/optimizar.py lo lista en `resumen.verificar`
    como visita sin comida. «descartar»: pasa a 'descartado'. No toca familias ni kilos.
    """
    if decision not in ACCIONES_SILENCIO:
        return False
    actual = con.execute("SELECT estado, origen, punto_id FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if actual is None or actual["origen"] != ORIGEN_SILENCIO or actual["estado"] != "nuevo":
        return False
    estado, accion = ACCIONES_SILENCIO[decision]
    if estado == "confirmado" and actual["punto_id"] is None:
        return False
    con.execute("UPDATE pedidos SET estado=? WHERE id=? AND origen=?", (estado, pedido_id, ORIGEN_SILENCIO))
    con.commit()
    db.anotar(con, quien or "despachador", accion, f"pedidos {pedido_id} -> {estado}")
    return True


def confirmar_ubicacion(con: sqlite3.Connection, ubicacion_id: int, quien: str = "despachador",
                        lugar_id: int | None = None) -> bool:
    ok = lugares.confirmar(con, ubicacion_id, quien=quien, lugar_id=lugar_id)
    con.commit()
    return ok


def corregir_ubicacion(con: sqlite3.Connection, ubicacion_id: int, lat: float, lon: float) -> bool:
    """El despachador marcó el punto en el mapa. En `lugares` queda con quien='despachador'."""
    ok = lugares.corregir_con_pin(con, ubicacion_id, lat, lon, quien="despachador")
    con.commit()
    return ok


# ---------- territorio (encargos/T1_TERRITORIO.md, parte C) ----------

def _orden_territorio(f: dict) -> tuple:
    """Peor atendidos arriba: menor % de críticos a tiempo; sin críticos evaluados, al final."""
    pct = f.get("pct_criticos_a_tiempo")
    general = f.get("pct_a_tiempo")
    return (pct is None, pct if pct is not None else 0.0,
            general is None, general if general is not None else 0.0,
            -(f.get("pendiente_mas_viejo_h") or 0.0), str(f.get("territorio") or ""))


def territorio(con: sqlite3.Connection, ahora: datetime | None = None, modulo=None) -> dict:
    """Resumen por comuna y lugares sin pedidos registrados, leídos de despacho.territorio.

    Devuelve {"disponible": False} si la parte B no está. Nunca trae texto_original ni remitente_hash:
    solo pasan las columnas declaradas por despacho.territorio.
    """
    m = _territorio if modulo is None else modulo
    if m is None:
        return {"disponible": False, "tabla": [], "sin_pedidos": [], "columnas": ()}
    columnas = tuple(m.COLUMNAS)
    tabla = [{c: f.get(c) for c in columnas} for f in m.resumen(con, ahora=_ahora(ahora))]
    for f in tabla:
        pct = f.get("pct_criticos_a_tiempo")
        f["bajo_meta"] = pct is not None and pct < META_CRITICOS_PCT
    tabla.sort(key=_orden_territorio)
    cols_sil = tuple(getattr(m, "COLUMNAS_SILENCIO", ("nombre", "tipo", "comuna", "estado")))
    sin_pedidos = [{c: s.get(c) for c in cols_sil} for s in m.silencio(con)]
    return {"disponible": True, "tabla": tabla, "sin_pedidos": sin_pedidos, "columnas": columnas,
            "columnas_sin_pedidos": cols_sil, "meta": META_CRITICOS_PCT}


def territorio_csv(datos_territorio: dict) -> bytes:
    """La tabla por territorio en CSV (UTF-8 con BOM para que Excel lea las tildes)."""
    import csv
    import io
    columnas = datos_territorio.get("columnas") or ()
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(columnas), extrasaction="ignore")
    w.writeheader()
    w.writerows(datos_territorio.get("tabla") or [])
    return ("﻿" + buf.getvalue()).encode("utf-8")


# ---------- informe (solo lectura) ----------
# lotes.kg no se descuenta al despachar en ningún módulo: es «inventario cargado», no existencia real.
ESTADOS_DESPACHADOS = ("en_ruta", "entregado")


def informe(con: sqlite3.Connection, ahora: datetime | None = None) -> dict:
    """Cifras de lo mandado y de la bodega, tal como las registra la base. Nada se estima."""
    ahora = _ahora(ahora)
    abiertos = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE estado IN ('nuevo','confirmado','asignado') AND duplicado_de IS NULL "
        "AND COALESCE(origen,'mensaje') != ?", (ORIGEN_SILENCIO,)).fetchone()[0]
    atendidos = con.execute("SELECT COUNT(*) FROM pedidos WHERE estado='entregado' AND duplicado_de IS NULL "
                            "AND COALESCE(origen,'mensaje') != ?", (ORIGEN_SILENCIO,)).fetchone()[0]
    kg = {e: con.execute("SELECT COALESCE(SUM(kg),0) FROM paquetes WHERE estado IN (%s)" % ",".join("?" * len(e)),
                         e).fetchone()[0] for e in (ESTADOS_DESPACHADOS, ("entregado",))}
    lotes = filas(con, "SELECT l.id, l.producto, l.kg, l.perecedero, l.vence_en, a.nombre AS acopio "
                       "FROM lotes l LEFT JOIN acopios a ON a.id = l.acopio_id")
    vence = {12: 0.0, 24: 0.0}
    for l in lotes:
        f = _fecha(l["vence_en"])
        horas = (f - ahora).total_seconds() / 3600 if f else None
        l["horas_para_vencer"] = round(horas, 1) if horas is not None else None
        l["vence_pronto"] = bool(l["perecedero"] and horas is not None and 0 <= horas <= HORAS_VENCE_PRONTO)
        for h in vence:
            if l["perecedero"] and horas is not None and 0 <= horas <= h:
                vence[h] += l["kg"] or 0
    lotes.sort(key=lambda l: (l["vence_en"] is None, l["vence_en"] or "", l["id"]))
    por_producto = filas(con, """
        SELECT COALESCE(l.producto, 'sin lote') AS producto,
               SUM(CASE WHEN pa.estado IN ('en_ruta','entregado') THEN pa.kg ELSE 0 END) AS kg_despachado,
               SUM(CASE WHEN pa.estado = 'entregado' THEN pa.kg ELSE 0 END) AS kg_entregado
        FROM paquetes pa LEFT JOIN lotes l ON l.id = pa.lote_id
        WHERE pa.estado IN ('en_ruta','entregado') GROUP BY 1 ORDER BY 2 DESC""")
    vehiculos = filas(con, """
        SELECT v.nombre AS vehiculo, v.tipo, v.estado, COUNT(pa.id) AS paradas, COALESCE(SUM(pa.kg),0) AS kg
        FROM paradas pa JOIN planes p ON p.id = pa.plan_id AND p.estado = 'aprobado'
        LEFT JOIN vehiculos v ON v.id = pa.vehiculo_id GROUP BY pa.vehiculo_id ORDER BY v.nombre""")
    bodega = filas(con, "SELECT l.producto, COALESCE(a.nombre,'sin acopio') AS acopio, SUM(l.kg) AS kg "
                        "FROM lotes l LEFT JOIN acopios a ON a.id = l.acopio_id GROUP BY 1, 2 ORDER BY 1, 2")
    terr = territorio(con, ahora)
    por_territorio = [{"territorio": f["territorio"], "kg_pedidos": f.get("kg_pedidos"),
                       "kg_entregados": f.get("kg_entregados")} for f in terr["tabla"]
                      if f.get("kg_pedidos") or f.get("kg_entregados")]
    crit_ok = sum(f.get("criticos_a_tiempo") or 0 for f in terr["tabla"])
    crit_ev = sum(f.get("criticos_evaluados") or 0 for f in terr["tabla"])
    return {"resumen": {"pedidos_atendidos": atendidos, "pedidos_pendientes": abiertos,
                        "kg_despachados": round(kg[ESTADOS_DESPACHADOS], 1), "kg_entregados": round(kg[("entregado",)], 1),
                        "kg_inventario_cargado": round(sum(l["kg"] or 0 for l in lotes), 1),
                        "kg_vencen_12h": round(vence[12], 1), "kg_vencen_24h": round(vence[24], 1),
                        "criticos_a_tiempo": crit_ok, "criticos_evaluados": crit_ev,
                        "pct_criticos_a_tiempo": round(100 * crit_ok / crit_ev, 1) if crit_ev else None},
            "por_producto": por_producto, "vehiculos": vehiculos, "por_territorio": por_territorio,
            "bodega": bodega, "lotes": lotes}


def informe_csv(inf: dict) -> bytes:
    """Todas las tablas del informe en un CSV, con una columna `seccion`."""
    import csv
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["resumen"])
    w.writerow(["indicador", "valor"])
    for k, v in inf["resumen"].items():
        w.writerow([k, v])
    for nombre in ("por_producto", "vehiculos", "por_territorio", "bodega", "lotes"):
        w.writerow([])
        w.writerow([nombre])
        if not inf[nombre]:
            w.writerow(["sin datos todavía"])
            continue
        columnas = list(inf[nombre][0].keys())
        w.writerow(columnas)
        for fila in inf[nombre]:
            w.writerow([fila.get(c) for c in columnas])
    return ("﻿" + buf.getvalue()).encode("utf-8")


# ---------- bitácora ----------

def bitacora(con: sqlite3.Connection, n: int = 50) -> list[dict]:
    return filas(con, "SELECT cuando, quien, accion, detalle FROM bitacora ORDER BY id DESC LIMIT ?", (n,))


# ---------- pedir el plan a despacho/ ----------

@dataclass
class Corrida:
    ok: bool
    plan_id: int | None
    mensaje: str = ""


def ejecutar_despacho(modulo: str, *args: str, correr=subprocess.run, espera_s: int = 120) -> Corrida:
    """Ejecuta `python -m despacho.<modulo>` y lee el id del plan que imprime."""
    if modulo not in ("optimizar", "recalcular"):
        return Corrida(False, None, f"módulo desconocido: {modulo}")
    try:
        r = correr([sys.executable, "-m", f"despacho.{modulo}", *args], cwd=RAIZ,
                   capture_output=True, text=True, timeout=espera_s)
    except subprocess.TimeoutExpired:
        return Corrida(False, None, f"despacho.{modulo} no respondió en {espera_s} s")
    except OSError as e:
        return Corrida(False, None, f"no se pudo ejecutar despacho.{modulo}: {e}")
    lineas = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
    error = ((r.stderr or "").strip().splitlines() or [""])[-1]
    try:
        plan_id = int(lineas[-1])
    except (IndexError, ValueError):
        return Corrida(False, None, error or "despacho no devolvió el id del plan")
    if r.returncode != 0 or plan_id < 0:
        return Corrida(False, None, error or "despacho terminó con error")
    return Corrida(True, plan_id)


SEMILLA = ("despacho.semilla", "--cargar", "--reiniciar")
ESPERA_SEMILLA_S = 300


def reiniciar_datos_prueba(con: sqlite3.Connection, quien: str, correr=subprocess.run,
                           espera_s: int = ESPERA_SEMILLA_S) -> Corrida:
    """Borra los datos de la base y carga la semilla (`python -m despacho.semilla --cargar --reiniciar`).

    El proceso hereda DESPACHOX_DB, así que reinicia la misma base que mira el tablero. La entrada de
    la bitácora se escribe después, para que el reinicio no la borre.
    """
    try:
        r = correr([sys.executable, "-m", *SEMILLA], cwd=RAIZ, capture_output=True, text=True,
                   timeout=espera_s)
    except subprocess.TimeoutExpired:
        return Corrida(False, None, f"despacho.semilla no respondió en {espera_s} s")
    except OSError as e:
        return Corrida(False, None, f"no se pudo ejecutar despacho.semilla: {e}")
    if r.returncode != 0:
        error = ((r.stderr or "").strip().splitlines() or ["despacho.semilla terminó con error"])[-1]
        return Corrida(False, None, error)
    db.anotar(con, (quien or "").strip() or "despachador", "reiniciar datos de prueba",
              "despacho.semilla --cargar --reiniciar")
    return Corrida(True, None)


def calcular_plan() -> Corrida:
    return ejecutar_despacho("optimizar")


def recalcular_plan() -> Corrida:
    return ejecutar_despacho("recalcular")


def aprobar_plan(plan_id: int, quien: str) -> Corrida:
    return ejecutar_despacho("optimizar", "--aprobar", str(plan_id), "--quien", quien or "despachador")
