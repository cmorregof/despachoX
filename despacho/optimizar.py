"""Optimizador de despacho: lee la base, resuelve el ruteo con OR-Tools y escribe un plan `propuesto`.

Uso:
    python -m despacho.optimizar                  # imprime el id del plan
    python -m despacho.optimizar --segundos 5 --motivo "pedido nuevo"

Regla del módulo: el plan siempre nace `propuesto`; solo el despachador lo aprueba. Si no hay
solución se escribe un plan vacío con el motivo. Nunca se lanza una excepción hacia afuera.
Una alerta por silencio (`pedidos.origen='silencio'`) nunca sale con comida, aunque esté
confirmada: no se surte ni se rutea, y queda listada en `resumen.verificar`.

Modelo (sustituto declarado de «tiempo de llegada y privación»):
  minimizar  tiempo de viaje
           + retraso frente a `limite_en`, ponderado por urgencia
           + penalización alta por pedido sin atender (mayor si es urgente o lleva perecederos)
  sujeto a   capacidad por vehículo (gramos), una red vial por tipo de vehículo,
             llegada antes del vencimiento del perecedero menos un margen (ventana dura),
             inventario del acopio que surte (regla: primero lo que vence primero).
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from datos import db
from despacho import cierres as mod_cierres
from despacho import matriz as mod_matriz
from despacho.cierres import normalizar

# ---- Supuestos del modelo. Son nuestros y quedan escritos en el resumen de cada plan. ----
LIMITE_BUSQUEDA_S = 8            # tope de búsqueda por defecto; nunca más de 10
HORIZONTE_S = 24 * 3600          # un plan cubre como máximo las próximas 24 horas
SERVICIO_S = 600                 # 10 minutos de descarga por parada
MARGEN_VENCIMIENTO_S = 1800      # el perecedero debe llegar 30 minutos antes de vencer
KG_POR_FAMILIA = 10.0            # si el pedido no trae kilos
LIMITE_POR_URGENCIA_H = {3: 4, 2: 12, 1: 24}      # si el pedido no trae `limite_en`
PESO_RETRASO = {1: 1, 2: 3, 3: 10}                # costo por segundo de retraso
# Los pedidos de puntos críticos (albergues, comedores) pesan más en el retraso y en quedar
# sin atender: es lo que mide el indicador del reto. 1 = sin trato especial. El 3 por defecto
# lo propuso la simulación (barrido de 1, 3, 10 y 30 en docs/SIMULACION.md, sección 8; canal,
# 16:57) y lo aprobó Carlos el viernes 20: mejora en promedio los críticos a tiempo y no
# empeora nada medido. Se barre con la variable de entorno DESPACHOX_FACTOR_CRITICO.
FACTOR_CRITICO = max(1, int(os.environ.get("DESPACHOX_FACTOR_CRITICO") or 3))
MOTIVO_SILENCIO = "alerta por silencio: visita de verificación, no sale con comida"
PENAL_SIN_ATENDER = 20_000_000                    # por nivel de urgencia
PENAL_KG_PERECEDERO = 20_000                      # extra por kilo perecedero que se quedaría
# Empaque captador de etileno (patente UNAL, certificado 37476). Un lote de fruta perecedera con
# `empaque_activo=1`, guardado en un acopio con frío (`tiene_frio=1`), dura más: el tiempo que le
# queda hasta `vence_en` se multiplica por este factor. A todo lo demás se le aplica 1,0.
# La solicitud de la patente solo lo probó en gulupa a 8 °C: sin empaque el pico de etileno llega
# en la semana 5 y con el empaque no hay pico hasta la semana 6 (figuras 1 y 2, folio 18;
# docs/investigacion/07_patentes_a_fondo.md). 6/5 = 1,2 es una cota inferior, no una vida útil
# medida. Se barre con DESPACHOX_FACTOR_EMPAQUE.
FACTOR_EMPAQUE_ACTIVO = max(1.0, float(os.environ.get("DESPACHOX_FACTOR_EMPAQUE") or 1.2))
NOTA_EMPAQUE = ("cota inferior medida en gulupa a 8 °C en la solicitud de la patente UNAL 37476; "
                "pendiente de datos del ICTA para otros productos")
EMPAQUE_APLICA_A = "lotes de fruta perecedera con empaque activo en acopios con frío; 1,0 en lo demás"
# Frutas frescas, ya normalizadas (sin tildes, minúsculas). El plátano no está: el SIPSA del DANE
# lo cuenta con los tubérculos, no con las frutas.
FRUTAS = ("fruta", "frutas", "gulupa", "maracuya", "granadilla", "curuba", "uchuva", "mora", "fresa",
          "lulo", "guayaba", "feijoa", "tomate de arbol", "banano", "naranja", "mandarina", "limon",
          "mango", "papaya", "pina", "manzana", "pera", "uva", "durazno", "melon", "patilla",
          "guanabana", "pitahaya", "aguacate")


@dataclass
class Surtido:
    """Qué lotes cubren un pedido. Lo calculan reglas, no el solver."""
    acopio_id: int | None = None
    lineas: list[dict] = field(default_factory=list)       # {lote_id, producto, kg, perecedero}
    faltantes: list[dict] = field(default_factory=list)    # {producto, kg}
    vence: datetime | None = None

    @property
    def kg(self) -> float:
        return sum(l["kg"] for l in self.lineas)

    @property
    def kg_perecedero(self) -> float:
        return sum(l["kg"] for l in self.lineas if l["perecedero"])


def _fecha(texto: str | None) -> datetime | None:
    if not texto:
        return None
    try:
        d = datetime.fromisoformat(texto)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=db.BOGOTA)


def _demanda(p: dict, notas: list[str] | None = None) -> list[dict]:
    """Líneas pedidas: [{producto, kg}]. Sin detalle, un mercado genérico por kilos.

    Un producto que llega sin kilos no se descarta: se reparte entre ellos lo que falte para
    completar `kg_estimado` (o familias × KG_POR_FAMILIA). Así quien pidió leche recibe leche.
    Si `notas` es una lista, se le añade por qué la cantidad es supuesta (vacía si no lo es).
    """
    lineas = _demanda_lineas(p)
    if notas is not None:
        notas.extend(_por_que_supuesta(p, lineas))
    return lineas


def _por_que_supuesta(p: dict, lineas: list[dict]) -> list[str]:
    """Qué completó la red de seguridad de `_demanda`. Vacía si todo lo dijo quien pidió."""
    declarados = [l for l in _productos(p) if l["kg"] > 0]
    if lineas and len(declarados) == len(lineas):
        return []                          # cada producto trae sus kilos
    notas = []
    if not p["kg_estimado"]:
        if p["familias"]:
            notas.append(f"kilos estimados con {KG_POR_FAMILIA:g} kg por familia")
        else:
            notas.append(f"sin kilos ni familias: se supuso 1 familia, {KG_POR_FAMILIA:g} kg")
    if any(l["producto"] for l in lineas) and len(declarados) < len(lineas):
        notas.append("kilos repartidos entre productos que no los traían")
    return notas


def _productos(p: dict) -> list[dict]:
    """Productos del pedido como [{producto, kg}] con kg=0 si no los trae. Tolera JSON malo."""
    salida = []
    try:
        for l in json.loads(p["productos"] or "[]"):
            l = {"producto": l} if isinstance(l, str) else l
            nombre = str(l.get("producto") or "").strip()
            if not nombre:
                continue
            try:
                kg = float(l.get("kg") or 0)
            except (TypeError, ValueError):
                kg = 0.0
            salida.append({"producto": nombre, "kg": max(0.0, kg)})
    except (TypeError, ValueError, AttributeError):
        return []
    return salida


def _demanda_lineas(p: dict) -> list[dict]:
    total = float(p["kg_estimado"] or (p["familias"] or 1) * KG_POR_FAMILIA)
    con_kg, sin_kg = [], []
    for l in _productos(p):
        (con_kg if l["kg"] > 0 else sin_kg).append(l)
    if sin_kg:
        resto = total - sum(l["kg"] for l in con_kg)
        if resto <= 0:                       # los kilos declarados ya cubren el total
            resto = KG_POR_FAMILIA * (p["familias"] or 1) * len(sin_kg) / (len(con_kg) + len(sin_kg))
        for l in sin_kg:
            l["kg"] = round(resto / len(sin_kg), 3)
    if con_kg or sin_kg:
        return con_kg + sin_kg
    return [{"producto": None, "kg": total}]


def _sirve(lote: dict, producto: str | None) -> bool:
    if producto is None:                       # mercado genérico: solo no perecederos
        return not lote["perecedero"]
    a, b = normalizar(lote["producto"]), normalizar(producto)
    return a == b or a in b or b in a


def es_fruta(producto: str | None) -> bool:
    """«fruta», «frutas», «gulupa», «mora de castilla»…; no «verdura» ni «tomate»."""
    n = normalizar(producto)
    return any(n == f or n.startswith(f + " ") for f in FRUTAS)


def factor_empaque(lote: dict, frio: bool) -> float:
    """FACTOR_EMPAQUE_ACTIVO para fruta perecedera con empaque activo en un acopio con frío; si no, 1,0."""
    if frio and lote.get("perecedero") and lote.get("empaque_activo") and es_fruta(lote.get("producto")):
        return FACTOR_EMPAQUE_ACTIVO
    return 1.0


def vence_efectivo(lote: dict, ahora: datetime, frio: bool = False) -> datetime | None:
    """Vencimiento que usa el modelo. `frio`: el acopio del lote tiene frío.

    Solo a la fruta perecedera con empaque activo en frío se le alarga el tiempo restante.
    """
    vence = _fecha(lote.get("vence_en"))
    factor = factor_empaque(lote, frio)
    if vence is None or factor == 1.0 or vence <= ahora:
        return vence
    return ahora + (vence - ahora) * factor


def surtir(pedidos: list[dict], lotes: list[dict], ahora: datetime, acopios_de: dict,
           segundos_a: dict, existencias: dict[int, float] | None = None,
           frios: frozenset[int] | set[int] = frozenset()) -> dict[int, Surtido]:
    """Asigna lotes a pedidos: primero el pedido más urgente, primero el lote que vence primero.

    acopios_de[pedido_id]  -> acopios desde los que algún vehículo puede llegar al punto
    segundos_a[(acopio_id, pedido_id)] -> tiempo de viaje del vehículo más rápido
    frios -> ids de los acopios con frío (solo ahí cuenta el empaque activo)
    Un lote que vencería antes de poder llegar no se asigna a ese pedido.
    """
    queda = existencias if existencias is not None else {l["id"]: float(l["kg"]) for l in lotes}
    lejos = datetime.max.replace(tzinfo=db.BOGOTA)
    vence_de = {l["id"]: vence_efectivo(l, ahora, l["acopio_id"] in frios) for l in lotes}
    orden_lotes = sorted(lotes, key=lambda l: (vence_de[l["id"]] or lejos, l["id"]))
    resultado: dict[int, Surtido] = {}

    def intento(p: dict, acopio_id: int, comprometer: bool) -> Surtido:
        s = Surtido(acopio_id=acopio_id)
        local = queda if comprometer else dict(queda)
        llegada = ahora + timedelta(seconds=segundos_a.get((acopio_id, p["id"]), 0) + MARGEN_VENCIMIENTO_S)
        for linea in _demanda(p):
            falta = linea["kg"]
            for l in orden_lotes:
                if falta <= 1e-9:
                    break
                if l["acopio_id"] != acopio_id or local.get(l["id"], 0) <= 1e-9 or not _sirve(l, linea["producto"]):
                    continue
                vence = vence_de[l["id"]]
                if l["perecedero"] and vence is not None and vence <= llegada:
                    continue
                toma = min(falta, local[l["id"]])
                local[l["id"]] -= toma
                falta -= toma
                s.lineas.append({"lote_id": l["id"], "producto": l["producto"], "kg": round(toma, 3),
                                 "perecedero": bool(l["perecedero"])})
                if l["perecedero"] and vence is not None and (s.vence is None or vence < s.vence):
                    s.vence = vence
            if falta > 1e-9:
                s.faltantes.append({"producto": linea["producto"] or "mercado", "kg": round(falta, 3)})
        return s

    for p in sorted(pedidos, key=lambda p: (-(p["urgencia"] or 2), p["limite_en"] or "9", p["id"])):
        candidatos = acopios_de.get(p["id"], [])
        if not candidatos:
            resultado[p["id"]] = Surtido()
            continue
        mejor = max(candidatos, key=lambda a: (round(intento(p, a, False).kg, 3),
                                               -segundos_a.get((a, p["id"]), 0)))
        resultado[p["id"]] = intento(p, mejor, True)
    return resultado


def _leer(con: sqlite3.Connection, incluir_asignados: bool) -> dict:
    filas = lambda sql, *a: [dict(r) for r in con.execute(sql, a).fetchall()]
    estados = ("confirmado", "asignado") if incluir_asignados else ("confirmado",)
    marcas = ",".join("?" * len(estados))
    return {
        "pedidos": filas(f"SELECT * FROM pedidos WHERE estado IN ({marcas}) AND duplicado_de IS NULL "
                         "AND punto_id IS NOT NULL ORDER BY id", *estados),
        "ya_asignados": [] if incluir_asignados else filas(
            "SELECT * FROM pedidos WHERE estado='asignado' AND punto_id IS NOT NULL ORDER BY id"),
        "puntos": {r["id"]: r for r in filas("SELECT * FROM puntos")},
        "acopios": {r["id"]: r for r in filas("SELECT * FROM acopios")},
        "lotes": filas("SELECT * FROM lotes ORDER BY id"),
        "vehiculos": filas("SELECT * FROM vehiculos WHERE estado != 'fuera' ORDER BY id"),
        "cierres": filas("SELECT * FROM cierres WHERE estado='confirmado' ORDER BY id"),
    }


def _plan_vigente(con: sqlite3.Connection) -> int | None:
    r = con.execute("SELECT id FROM planes WHERE estado IN ('aprobado','propuesto') "
                    "ORDER BY (estado='aprobado') DESC, id DESC LIMIT 1").fetchone()
    return r["id"] if r else None


def sincronizar_aprobados(con: sqlite3.Connection) -> None:
    """Los pedidos de un plan aprobado pasan a `asignado` (por si el tablero solo cambió el plan)."""
    con.execute("UPDATE pedidos SET estado='asignado' WHERE estado='confirmado' AND id IN "
                "(SELECT pa.pedido_id FROM paradas pa JOIN planes pl ON pl.id = pa.plan_id "
                " WHERE pl.estado='aprobado' AND pa.pedido_id IS NOT NULL)")
    con.commit()


def _resolver(datos: dict, g, ahora: datetime, segundos: int, bloqueos: dict[int, int]) -> dict:
    """Arma y resuelve el modelo. Devuelve {'paradas': [...], 'resumen': {...}} sin tocar la base.

    bloqueos: pedido_id -> vehiculo_id, para la carga que ya va a bordo de un vehículo en ruta.
    """
    from ortools.constraint_solver import pywrapcp, routing_enums_pb2

    avisos: list[str] = []
    sin_atender: list[dict] = []
    puntos, acopios = datos["puntos"], datos["acopios"]

    # --- Flota utilizable ---
    flota = []
    for v in datos["vehiculos"]:
        if v["tipo"] not in mod_matriz.TIPOS:
            avisos.append(f"vehículo {v['id']} ({v['tipo']}): tipo no modelado, queda fuera del plan")
        elif v["acopio_id"] not in acopios:
            avisos.append(f"vehículo {v['id']}: sin acopio asignado, queda fuera del plan")
        else:
            flota.append(v)
    # Una alerta por silencio (`origen='silencio'`, entrada/silencio.py) es una visita de
    # verificación, no un pedido: nunca sale con comida. Se aparta antes del surtido para que no
    # reserve inventario, no entra al ruteo ni a los indicadores y queda en `resumen.verificar`.
    pedidos, verificar = [], []
    for p in datos["pedidos"]:
        if p["punto_id"] not in puntos:
            continue
        if p.get("origen") == "silencio":
            verificar.append({"pedido_id": p["id"], "punto_id": p["punto_id"], "motivo": MOTIVO_SILENCIO})
            avisos.append(f"pedido {p['id']} ({puntos[p['punto_id']]['nombre']}): {MOTIVO_SILENCIO}. "
                          "Descártelo o reemplácelo por un pedido real.")
        else:
            pedidos.append(p)

    def vacio(motivo: str) -> dict:
        return {"paradas": [], "resumen": {
            "vacio": True, "motivo_vacio": motivo, "pedidos_considerados": len(pedidos),
            "pedidos_atendidos": 0, "sin_atender": sin_atender, "verificar": verificar, "avisos": avisos}}

    if not pedidos:
        return vacio("no hay pedidos confirmados por despachar"
                     + (f"; {len(verificar)} alerta(s) por silencio se verifican en persona, sin comida"
                        if verificar else ""))
    if not flota:
        return vacio("no hay vehículos disponibles")

    # --- Matrices por tipo de vehículo ---
    lugares = [mod_matriz.Lugar(f"acopio:{a}", acopios[a]["lat"], acopios[a]["lon"]) for a in acopios]
    lugares += [mod_matriz.Lugar(f"punto:{i}", puntos[i]["lat"], puntos[i]["lon"])
                for i in sorted({p["punto_id"] for p in pedidos})]
    inicio_de = {}
    for v in flota:
        if v["estado"] == "en_ruta" and v["lat"] is not None and v["lon"] is not None:
            lugares.append(mod_matriz.Lugar(f"veh:{v['id']}", v["lat"], v["lon"]))
            inicio_de[v["id"]] = f"veh:{v['id']}"
        else:
            inicio_de[v["id"]] = f"acopio:{v['acopio_id']}"
    tipos = tuple(sorted({v["tipo"] for v in flota}))
    matrices = mod_matriz.calcular(g, lugares, datos["cierres"], tipos)
    for m in matrices.values():
        avisos.extend(m.avisos)

    def llega(v: dict, p: dict) -> bool:
        m, pt = matrices[v["tipo"]], f"punto:{p['punto_id']}"
        return m.alcanzable(inicio_de[v["id"]], pt) and m.alcanzable(pt, f"acopio:{v['acopio_id']}")

    # --- Surtido por reglas (inventario y vencimientos) ---
    libres = [v for v in flota if v["estado"] != "en_ruta"]
    acopios_de, segundos_a = {}, {}
    for p in pedidos:
        if p["id"] in bloqueos:
            cand = [v for v in flota if v["id"] == bloqueos[p["id"]]]
        else:
            cand = [v for v in libres if llega(v, p)]
        acopios_de[p["id"]] = sorted({v["acopio_id"] for v in cand})
        for v in cand:
            t = matrices[v["tipo"]].tiempo(inicio_de[v["id"]], f"punto:{p['punto_id']}")
            clave = (v["acopio_id"], p["id"])
            segundos_a[clave] = min(segundos_a.get(clave, t), t)
    existencias = {l["id"]: float(l["kg"]) for l in datos["lotes"]}
    frios = frozenset(a for a, r in acopios.items() if r.get("tiene_frio"))
    todos_acopios = {p["id"]: list(acopios) for p in datos["ya_asignados"]}
    surtir(datos["ya_asignados"], datos["lotes"], ahora, todos_acopios, {}, existencias, frios)  # ya comprometido
    surtido = surtir(pedidos, datos["lotes"], ahora, acopios_de, segundos_a, existencias, frios)

    # --- Qué pedidos entran al modelo ---
    nodos_pedido: list[dict] = []
    for p in pedidos:
        s = surtido[p["id"]]
        base = {"pedido_id": p["id"], "punto_id": p["punto_id"]}
        if not acopios_de[p["id"]]:
            sin_atender.append({**base, "motivo": "punto aislado: ningún vehículo disponible llega"})
            continue
        if s.kg <= 0:
            sin_atender.append({**base, "motivo": "sin inventario para este pedido"})
            continue
        permitidos = [k for k, v in enumerate(flota)
                      if v["acopio_id"] == s.acopio_id and s.kg <= v["capacidad_kg"]
                      and (bloqueos.get(p["id"]) == v["id"] if p["id"] in bloqueos
                           else v["estado"] != "en_ruta" and llega(v, p))]
        if not permitidos:
            sin_atender.append({**base, "motivo": "no cabe en ningún vehículo que llegue al punto"})
            continue
        urg = p["urgencia"] or 2
        limite = _fecha(p["limite_en"]) or (
            (_fecha(p["creado_en"]) or ahora) + timedelta(hours=LIMITE_POR_URGENCIA_H[urg]))
        duro = None
        if s.vence is not None:
            duro = int((s.vence - ahora).total_seconds()) - MARGEN_VENCIMIENTO_S
        notas: list[str] = []
        _demanda(p, notas)
        nodos_pedido.append({"p": p, "s": s, "permitidos": permitidos, "urg": urg, "limite": limite,
                             "supuesta": "; ".join(notas) or None,
                             "factor": FACTOR_CRITICO if puntos[p["punto_id"]]["critico"] else 1,
                             "blando": max(0, int((limite - ahora).total_seconds())), "duro": duro})
    if not nodos_pedido:
        return vacio("ningún pedido se puede despachar: " +
                     "; ".join(sorted({x["motivo"] for x in sin_atender})))

    # --- Modelo de ruteo ---
    n_v = len(flota)
    claves = ([inicio_de[v["id"]] for v in flota] + [f"acopio:{v['acopio_id']}" for v in flota]
              + [f"punto:{x['p']['punto_id']}" for x in nodos_pedido])
    servicio = [0] * (2 * n_v) + [SERVICIO_S] * len(nodos_pedido)
    gramos = [0] * (2 * n_v) + [int(round(x["s"].kg * 1000)) for x in nodos_pedido]
    tabla = {}
    for t in tipos:
        m = matrices[t]
        idx = [m.claves.index(c) for c in claves]
        tabla[t] = [[int(m.segundos[i, j]) + servicio[a] for j in idx] for a, i in enumerate(idx)]

    manager = pywrapcp.RoutingIndexManager(len(claves), n_v, list(range(n_v)), list(range(n_v, 2 * n_v)))
    routing = pywrapcp.RoutingModel(manager)
    transitos = []
    for k, v in enumerate(flota):
        T = tabla[v["tipo"]]
        cb = routing.RegisterTransitCallback(
            lambda i, j, T=T: T[manager.IndexToNode(i)][manager.IndexToNode(j)])
        routing.SetArcCostEvaluatorOfVehicle(cb, k)
        transitos.append(cb)
    routing.AddDimensionWithVehicleTransits(transitos, 0, HORIZONTE_S, True, "tiempo")
    dim_t = routing.GetDimensionOrDie("tiempo")
    carga = routing.RegisterUnaryTransitCallback(lambda i: gramos[manager.IndexToNode(i)])
    routing.AddDimensionWithVehicleCapacity(
        carga, 0, [int(v["capacidad_kg"] * 1000) for v in flota], True, "carga")

    for n, x in enumerate(nodos_pedido, start=2 * n_v):
        i = manager.NodeToIndex(n)
        penal = (PENAL_SIN_ATENDER * x["urg"] * x["factor"]
                 + int(PENAL_KG_PERECEDERO * x["s"].kg_perecedero))
        routing.AddDisjunction([i], penal)
        if len(x["permitidos"]) < n_v:
            routing.VehicleVar(i).SetValues([-1] + x["permitidos"])   # -1 = sin atender
        if x["duro"] is not None:
            dim_t.CumulVar(i).SetMax(max(0, min(HORIZONTE_S, x["duro"])))
        dim_t.SetCumulVarSoftUpperBound(i, min(HORIZONTE_S, x["blando"]),
                                        PESO_RETRASO[x["urg"]] * x["factor"])

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(max(1, min(10, int(segundos))))
    sol = routing.SolveWithParameters(params)
    if sol is None:
        return vacio(f"el solver no encontró solución en {segundos} s (estado {routing.status()})")

    # --- Lectura de la solución ---
    paradas, por_vehiculo, atendidos = [], [], set()
    retraso_total, criticos_total, criticos_a_tiempo = 0, 0, 0
    for k, v in enumerate(flota):
        m = matrices[v["tipo"]]
        i = routing.Start(k)
        previo, orden, kg_v = claves[manager.IndexToNode(i)], 0, 0.0
        while True:
            i = sol.Value(routing.NextVar(i))
            n = manager.IndexToNode(i)
            if routing.IsEnd(i):
                break
            x = nodos_pedido[n - 2 * n_v]
            llegada_s = sol.Min(dim_t.CumulVar(i))
            orden += 1
            kg_v += x["s"].kg
            atendidos.add(x["p"]["id"])
            retraso = max(0, llegada_s - x["blando"])
            retraso_total += retraso
            if puntos[x["p"]["punto_id"]]["critico"]:
                criticos_total += 1
                criticos_a_tiempo += retraso == 0
            paradas.append({
                "vehiculo_id": v["id"], "orden": orden, "punto_id": x["p"]["punto_id"],
                "pedido_id": x["p"]["id"], "kg": round(x["s"].kg, 3),
                "llegada_estimada": (ahora + timedelta(seconds=llegada_s)).isoformat(timespec="seconds"),
                "geometria": m.geometria(g, previo, claves[n]), "retraso_s": retraso,
                "cantidad_supuesta": x["supuesta"]})
            previo = claves[n]
        if orden:
            por_vehiculo.append({
                "vehiculo_id": v["id"], "nombre": v["nombre"], "tipo": v["tipo"], "paradas": orden,
                "kg": round(kg_v, 1), "capacidad_kg": v["capacidad_kg"],
                "duracion_s": sol.Min(dim_t.CumulVar(i)),
                "regreso": m.geometria(g, previo, f"acopio:{v['acopio_id']}")})

    for n, x in enumerate(nodos_pedido, start=2 * n_v):
        if x["p"]["id"] in atendidos:
            continue
        directo = min(tabla[flota[k]["tipo"]][k][n] for k in x["permitidos"])
        if x["duro"] is not None and directo > x["duro"]:
            motivo = "no se alcanza a llegar antes de que venza el perecedero"
        else:
            motivo = "no cabe en la flota disponible (capacidad o tiempo)"
        sin_atender.append({"pedido_id": x["p"]["id"], "punto_id": x["p"]["punto_id"], "motivo": motivo})

    hechos = [x for x in nodos_pedido if x["p"]["id"] in atendidos]
    supuestas = {str(x["p"]["id"]): x["supuesta"] for x in hechos if x["supuesta"]}
    for x in hechos:
        if x["supuesta"]:
            avisos.append(f"pedido {x['p']['id']} ({puntos[x['p']['punto_id']]['nombre']}): cantidad supuesta, "
                          f"{round(x['s'].kg, 1):g} kg; {x['supuesta']}. Confirmar con quien pidió.")
    resumen = {
        "vacio": not paradas,
        "calculado_para": ahora.isoformat(timespec="seconds"),
        "pedidos_considerados": len(pedidos),
        "pedidos_atendidos": len(atendidos),
        "kg_planeados": round(sum(x["s"].kg for x in hechos), 1),
        "kg_perecederos_planeados": round(sum(x["s"].kg_perecedero for x in hechos), 1),
        "paradas_con_retraso": sum(1 for p in paradas if p["retraso_s"] > 0),
        "retraso_total_s": retraso_total,
        "criticos": {"paradas": criticos_total, "a_tiempo": criticos_a_tiempo},
        "sin_atender": sin_atender,
        "verificar": verificar,
        "cantidad_supuesta": supuestas,
        "faltantes": [{"pedido_id": x["p"]["id"], **f} for x in hechos for f in x["s"].faltantes],
        "surtido": {str(x["p"]["id"]): [{k: l[k] for k in ("lote_id", "producto", "kg")}
                                        for l in x["s"].lineas] for x in hechos},
        "vehiculos": por_vehiculo,
        "cierres_aplicados": [c["id"] for c in datos["cierres"] if c["osm_u"] is not None],
        "avisos": avisos,
        "solver": {"estado": routing.status(), "objetivo": sol.ObjectiveValue(),
                   "limite_s": max(1, min(10, int(segundos))),
                   "estrategia": "PATH_CHEAPEST_ARC + GUIDED_LOCAL_SEARCH"},
        "supuestos": {"servicio_s": SERVICIO_S, "margen_vencimiento_s": MARGEN_VENCIMIENTO_S,
                      "horizonte_s": HORIZONTE_S, "kg_por_familia": KG_POR_FAMILIA,
                      "limite_por_urgencia_h": LIMITE_POR_URGENCIA_H, "peso_retraso": PESO_RETRASO,
                      "factor_critico": FACTOR_CRITICO,
                      "factor_empaque_activo": FACTOR_EMPAQUE_ACTIVO,
                      "factor_empaque_activo_nota": NOTA_EMPAQUE,
                      "factor_empaque_activo_aplica_a": EMPAQUE_APLICA_A,
                      "factor_tiempo": mod_matriz.FACTOR_TIEMPO, "un_viaje_por_vehiculo": True},
    }
    if not paradas:
        resumen["motivo_vacio"] = "ningún pedido cupo en el plan"
    return {"paradas": paradas, "resumen": resumen}


def _escribir(con: sqlite3.Connection, motivo: str, resultado: dict, segundos_calculo: float,
              reemplazar: list[int]) -> int:
    """Guarda el plan como `propuesto` y marca como `reemplazado` lo que deja de valer."""
    with con:
        for pid in reemplazar:
            con.execute("UPDATE planes SET estado='reemplazado' WHERE id=?", (pid,))
        cur = con.execute(
            "INSERT INTO planes(creado_en, motivo, estado, segundos_calculo, resumen) "
            "VALUES (?,?, 'propuesto', ?, ?)",
            (db.ahora(), motivo, round(segundos_calculo, 2),
             json.dumps(resultado["resumen"], ensure_ascii=False)))
        plan_id = cur.lastrowid
        con.executemany(
            "INSERT INTO paradas(plan_id, vehiculo_id, orden, punto_id, pedido_id, llegada_estimada, "
            "kg, geometria) VALUES (?,?,?,?,?,?,?,?)",
            [(plan_id, p["vehiculo_id"], p["orden"], p["punto_id"], p["pedido_id"],
              p["llegada_estimada"], p["kg"], json.dumps(p["geometria"])) for p in resultado["paradas"]])
    return plan_id


def planificar(con: sqlite3.Connection | None = None, motivo: str = "inicial",
               segundos: int = LIMITE_BUSQUEDA_S, recalculo: bool = False, g=None,
               ahora: datetime | None = None) -> int:
    """Calcula y escribe un plan `propuesto`. Devuelve su id. No lanza excepciones.

    recalculo=False: planea los pedidos `confirmado` con los vehículos libres.
    recalculo=True:  vuelve a planear también los pedidos `asignado`; lo que va a bordo de un
                     vehículo en ruta se queda en él.
    En los dos casos las propuestas anteriores pasan a `reemplazado`. El plan aprobado sigue
    vigente hasta que el despachador apruebe el nuevo (`aprobar`); si rechaza la propuesta, el
    aprobado no se pierde. `resumen.reemplaza_a` nombra igual el aprobado que se quiere sustituir.
    """
    inicio = time.perf_counter()
    propia = con is None
    con = con or db.conectar()
    reemplazar: list[int] = []      # propuestas que dejan de valer ya
    sustituye: list[int] = []       # lo que el plan nuevo reemplazaría si se aprueba
    try:
        sincronizar_aprobados(con)
        vigente = _plan_vigente(con)
        reemplazar = [r["id"] for r in con.execute("SELECT id FROM planes WHERE estado='propuesto' ORDER BY id DESC")]
        sustituye = ([vigente] if recalculo and vigente is not None and vigente not in reemplazar else []) + reemplazar
        if g is None:
            from despacho import red
            g = red.cargar()
        avisos_cierres = mod_cierres.ubicar(con, g)
        datos = _leer(con, incluir_asignados=recalculo)
        bloqueos: dict[int, int] = {}
        if recalculo and vigente is not None:
            en_ruta = {v["id"] for v in datos["vehiculos"] if v["estado"] == "en_ruta"}
            asignados = {p["id"] for p in datos["pedidos"] if p["estado"] == "asignado"}
            for r in con.execute("SELECT pedido_id, vehiculo_id FROM paradas WHERE plan_id=?", (vigente,)):
                if r["vehiculo_id"] in en_ruta and r["pedido_id"] in asignados:
                    bloqueos[r["pedido_id"]] = r["vehiculo_id"]
        resultado = _resolver(datos, g, ahora or datetime.now(db.BOGOTA), segundos, bloqueos)
        resultado["resumen"]["avisos"] = avisos_cierres + resultado["resumen"].get("avisos", [])
    except Exception as e:  # noqa: BLE001  (regla del módulo: plan vacío con motivo, nunca excepción)
        traceback.print_exc(file=sys.stderr)
        resultado = {"paradas": [], "resumen": {
            "vacio": True, "motivo_vacio": f"error interno: {type(e).__name__}: {e}",
            "pedidos_atendidos": 0, "sin_atender": [], "avisos": []}}
    resultado["resumen"]["motivo"] = motivo
    resultado["resumen"]["reemplaza_a"] = sustituye
    try:
        plan_id = _escribir(con, motivo, resultado, time.perf_counter() - inicio, reemplazar)
    except sqlite3.Error:
        traceback.print_exc(file=sys.stderr)
        plan_id = -1
    finally:
        if propia:
            con.close()
    return plan_id


def aprobar(con: sqlite3.Connection, plan_id: int, quien: str = "despachador") -> bool:
    """Para el tablero o la línea de órdenes: un humano aprueba el plan y sus pedidos pasan a `asignado`.

    Solo aquí el aprobado anterior pasa a `reemplazado`, y solo aquí nacen los paquetes (`en_ruta`).
    """
    from despacho import paquetes

    r = con.execute("SELECT estado FROM planes WHERE id=?", (plan_id,)).fetchone()
    if r is None or r["estado"] != "propuesto":
        return False
    previo = con.execute("SELECT id FROM planes WHERE estado='aprobado' ORDER BY id DESC LIMIT 1").fetchone()
    with con:
        con.execute("UPDATE planes SET estado='reemplazado' WHERE estado='aprobado'")
        con.execute("UPDATE planes SET estado='aprobado', aprobado_por=?, aprobado_en=? WHERE id=?",
                    (quien, db.ahora(), plan_id))
    sincronizar_aprobados(con)
    codigos = paquetes.crear_para_plan(con, plan_id, previo["id"] if previo else None)
    db.anotar(con, quien, "aprobar plan",
              f"plan {plan_id}" + (f", reemplaza al plan {previo['id']}" if previo else "")
              + f"; {len(codigos)} paquetes en ruta")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Calcula un plan de despacho y lo deja propuesto.")
    ap.add_argument("--segundos", type=int, default=LIMITE_BUSQUEDA_S, help="límite de búsqueda (máx. 10)")
    ap.add_argument("--motivo", default="inicial")
    ap.add_argument("--aprobar", type=int, metavar="PLAN", help="aprueba un plan propuesto (lo hace un humano)")
    ap.add_argument("--quien", default="despachador")
    args = ap.parse_args(argv)
    if args.aprobar is not None:
        con = db.conectar()
        ok = aprobar(con, args.aprobar, args.quien)
        print(args.aprobar if ok else f"el plan {args.aprobar} no está propuesto", file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 1
    print(planificar(motivo=args.motivo, segundos=args.segundos))
    return 0


if __name__ == "__main__":
    sys.exit(main())
