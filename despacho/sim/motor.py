"""Motor de eventos discretos.

Avanza el reloj, mueve los vehículos tramo a tramo por la red verdadera y registra entregas,
vencimientos y cierres descubiertos. La política solo ve el `Estado`: pedidos ya recibidos,
posición de la flota, inventario y la red conocida (sin los cierres que nadie ha reportado).

Reglas físicas que el motor impone a cualquier política:
- un vehículo nunca carga más que su capacidad, aunque el plan lo pida;
- un kilo perecedero que llega después del vencimiento de su lote no cuenta como entregado;
- un cierre solo se conoce cuando un vehículo intenta pasar por el tramo cerrado.
"""
from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field

from .escenario import Escenario
from .red_sim import FACTOR_EMERGENCIA, Conocimiento

# prioridad de los eventos que ocurren en el mismo instante
_PRIO = {"PEDIDO": 0, "INICIO": 1, "CONFIRMA": 2, "PLAN": 3, "FIN_TRAMO": 4, "SIGUE": 4, "TANDA": 5, "AVISO": 6}


@dataclass
class VehSim:
    id: int
    tipo: str
    cap: float
    nodo: int
    estado: str = "libre"          # libre | cargando | en_ruta | sirviendo | reportando | fuera
    t_ref: float = 0.0             # cuándo queda disponible en `nodo`
    a_bordo: list = field(default_factory=list)    # pedidos cargados, en orden de entrega
    carga: dict = field(default_factory=dict)      # pedido -> [(lote o None, kg)]
    devolver: list = field(default_factory=list)   # cargados que no se pudieron entregar
    cola: list = field(default_factory=list)       # pedidos por cargar; None fuerza volver a cargar
    tramo: dict | None = None
    version: int = 0
    km: float = 0.0
    max_carga: float = 0.0
    emergencias: int = 0           # veces que salió por vías no aptas para volver al acopio
    traza: list = field(default_factory=list)      # nodos recorridos, para pruebas

    def kg_a_bordo(self) -> float:
        return sum(kg for items in self.carga.values() for _, kg in items)

    def ref(self, t: float):
        """Nodo y hora desde los que este vehículo puede seguir un plan nuevo."""
        if self.estado == "en_ruta" and self.tramo:
            for nodo, tn in zip(self.tramo["nodos"], self.tramo["tiempos"]):
                if tn >= t:
                    return nodo, tn
            return self.tramo["nodos"][-1], self.tramo["tiempos"][-1]
        return self.nodo, max(t, self.t_ref)


@dataclass
class Estado:
    """Lo que la política puede ver en el instante `t`."""
    t: float
    motivo: str
    esc: Escenario                 # la política no debe leer esc.cierres ni pedidos futuros
    con: Conocimiento
    pendientes: list               # pedidos recibidos, sin entregar y sin cargar
    vehiculos: list                # VehSim (solo lectura)
    inventario: list               # (lote_id, kg disponibles, vence)
    vence_a_bordo: dict            # pedido cargado -> vencimiento más próximo de sus lotes
    inalcanzable: dict             # pedido -> tipos de vehículo que no pudieron llegar
    t_fin: float

    def sitio(self, pedido) -> int:
        return pedido.punto_id

    def pedido(self, pid: int):
        return self.esc.pedidos[pid - 1]


@dataclass
class Resultado:
    esc: Escenario
    politica: str
    entregas: dict                 # pedido -> dict(t, veh, kg_ok, kg_vencido)
    kg_valido_por_lote: dict
    vehiculos: list
    recalculos: list               # (t, motivo, segundos de cálculo)
    descubiertos: dict             # cierre -> hora en que se descubrió
    invalidas: int                 # asignaciones que el motor rechazó
    t_fin: float


class Motor:
    def __init__(self, esc: Escenario, politica):
        self.esc, self.pol, self.p = esc, politica, esc.p
        self.red = esc.red
        self.con = Conocimiento(esc.red, esc.sitios)
        self.cierre_de = {a: c for c in esc.cierres for a in c.aristas}
        self.ped = {q.id: q for q in esc.pedidos}
        self.estado_ped = {q.id: "futuro" for q in esc.pedidos}
        self.lote = {l.id: l for l in esc.lotes}
        self.inv = {l.id: l.kg for l in esc.lotes}
        self.veh = {v.id: VehSim(v.id, v.tipo, v.capacidad_kg, esc.acopio_nodo) for v in esc.vehiculos}
        self.entregas, self.kg_valido = {}, {l.id: 0.0 for l in esc.lotes}
        self.recalculos, self.descubiertos, self.invalidas = [], {}, 0
        self.inalcanzable = {}
        self.t_fin = self.p.horas_jornada * 3600.0
        self._cola, self._seq, self._en_aviso = [], 0, False
        self._plan_hasta, self._diferido = -1.0, None     # un plan a la vez espera aprobación

    # ---------- cola de eventos ----------
    def _push(self, t, tipo, *datos):
        self._seq += 1
        heapq.heappush(self._cola, (t, _PRIO[tipo], self._seq, tipo, datos))

    def correr(self) -> Resultado:
        for q in self.esc.pedidos:
            self._push(q.creado, "PEDIDO", q.id)
        self._push(0.0, "INICIO")
        k = 1
        while k * self.p.min_tanda * 60 < self.t_fin:
            self._push(k * self.p.min_tanda * 60, "TANDA")
            k += 1
        t_ant, repetidos = -1.0, 0
        while self._cola:
            t, _, _, tipo, datos = heapq.heappop(self._cola)
            if t > self.t_fin:
                break
            repetidos = repetidos + 1 if t == t_ant else 0
            t_ant = t
            if repetidos > 20000:
                raise RuntimeError(f"El reloj no avanza en t={t}: revisar la política {self.pol.nombre}")
            getattr(self, "_ev_" + tipo.lower())(t, *datos)
        return Resultado(self.esc, self.pol.nombre, self.entregas, self.kg_valido,
                         list(self.veh.values()), self.recalculos, self.descubiertos,
                         self.invalidas, self.t_fin)

    # ---------- eventos ----------
    def _ev_pedido(self, t, pid):
        self.estado_ped[pid] = "pendiente"
        if t > 0:
            self._avisar("pedido", t)

    def _ev_inicio(self, t):
        self._avisar("inicio", t)

    def _ev_tanda(self, t):
        self._avisar("tanda", t)

    def _ev_aviso(self, t, motivo):
        if motivo is None:
            motivo, self._diferido = self._diferido, None
        self._avisar(motivo, t)

    def _ev_confirma(self, t, cid):
        self._avisar("cierre", t)

    def _ev_plan(self, t, rutas):
        self._aplicar(rutas, t)

    def _ev_sigue(self, t, vid, version):
        v = self.veh[vid]
        if version == v.version:
            self._mover(v, t)

    def _ev_fin_tramo(self, t, vid, version):
        v = self.veh[vid]
        if version != v.version:
            return
        tramo = v.tramo
        self._cerrar_tramo(v, len(tramo["nodos"]) - 1)
        if tramo["tope"] is not None:
            nuevo = self._descubrir(tramo["tope"], t)
            v.estado = "reportando"
            v.t_ref = t + (self.p.min_reporte * 60 if nuevo else 0.0)
            v.version += 1
            self._push(v.t_ref, "SIGUE", v.id, v.version)
        elif tramo["destino"] == "acopio":
            self._en_acopio(v, t)
        else:
            self._entregar(v, t, tramo["destino"])

    # ---------- movimiento ----------
    def _cerrar_tramo(self, v, i):
        tramo = v.tramo
        v.km += tramo["km"][i] / 1000.0
        v.traza.extend(tramo["nodos"][1:i + 1])
        v.nodo = tramo["nodos"][i]
        v.t_ref = tramo["tiempos"][i]
        v.tramo = None

    def _cortar(self, v, t):
        """Interrumpe el tramo en el próximo nodo; allí el vehículo vuelve a decidir."""
        tiempos = v.tramo["tiempos"]
        i = next((k for k, tn in enumerate(tiempos) if tn >= t), len(tiempos) - 1)
        t_nodo = tiempos[i]
        self._cerrar_tramo(v, i)
        v.estado = "en_ruta"
        v.version += 1
        self._push(t_nodo, "SIGUE", v.id, v.version)

    def _mover(self, v, t):
        """Sale hacia la siguiente entrega a bordo o, si no hay, hacia el acopio."""
        seg = self.red.segundos[v.tipo]
        while True:
            destino = v.a_bordo[0] if v.a_bordo else "acopio"
            sitio = 0 if destino == "acopio" else self.ped[destino].punto_id
            camino = self.con.camino(v.tipo, v.nodo, self.con.nodo_sitio(v.tipo, sitio))
            if camino is not None:
                break
            if destino == "acopio":      # sin regreso por su red: sale por cualquier vía, más lento
                camino = self.con.camino_emergencia(v.tipo, v.nodo, self.esc.acopio_nodo)
                if camino is not None:
                    seg = self.red.segundos_emergencia[v.tipo]
                    v.emergencias += 1
                    break
                # de verdad aislado: sale de servicio y su carga se pierde
                v.estado, v.tramo = "fuera", None
                perdidos = v.devolver + v.a_bordo
                for pid in perdidos:     # los pedidos vuelven a la cola para otro vehículo
                    v.carga.pop(pid)
                    self.estado_ped[pid] = "pendiente"
                v.devolver, v.a_bordo, v.cola = [], [], []
                if perdidos:
                    self._avisar("devuelto", t)
                return
            v.a_bordo.pop(0)             # no hay paso conocido: la carga vuelve al acopio
            v.devolver.append(destino)
            self.inalcanzable.setdefault(destino, set()).add(v.tipo)
        nodos, tiempos, km, tope = [camino[0]], [t], [0.0], None
        for a, b in zip(camino, camino[1:]):
            e, lento = self.red.arista.get((a, b)), 1.0
            if e is None or seg[e] == float("inf") or e in self.con.cerradas[v.tipo]:
                # contravía por el otro sentido: solo ocurre en salida de emergencia
                e, lento = self.red.arista[(b, a)], FACTOR_EMERGENCIA
            c = self.cierre_de.get(e)
            if c is not None and c.t_ocurre <= tiempos[-1] and v.tipo in c.tipos:
                tope = c                 # se topa el cierre al llegar al nodo `a`
                break
            nodos.append(b)
            tiempos.append(tiempos[-1] + float(seg[e]) * lento)
            km.append(km[-1] + float(self.red.largo_m[e]))
        v.tramo = {"nodos": nodos, "tiempos": tiempos, "km": km, "destino": destino, "tope": tope}
        v.estado = "en_ruta"
        v.version += 1
        self._push(tiempos[-1], "FIN_TRAMO", v.id, v.version)

    def _descubrir(self, c, t) -> bool:
        if c.id in self.descubiertos:
            return False
        self.descubiertos[c.id] = t
        self.con.agregar_cierre(c.aristas, c.tipos)
        self._push(t + self.p.min_confirmacion * 60, "CONFIRMA", c.id)
        cerradas = set(c.aristas)
        for w in self.veh.values():      # el aviso por radio desvía a quien iba hacia ese tramo
            if w.estado != "en_ruta" or w.tramo is None or w.tipo not in c.tipos:
                continue
            nodos, tiempos = w.tramo["nodos"], w.tramo["tiempos"]
            i = next((k for k, tn in enumerate(tiempos) if tn >= t), len(tiempos) - 1)
            resto = list(zip(nodos[i:], nodos[i + 1:]))
            pasa = any(self.red.arista.get(ab, self.red.arista.get(ab[::-1])) in cerradas for ab in resto)
            if pasa or (w.tramo["tope"] is c):
                self._cortar(w, t)
        return True

    # ---------- acopio y entregas ----------
    def _entregar(self, v, t, pid):
        v.a_bordo.remove(pid)
        kg_ok = kg_venc = 0.0
        for lote, kg in v.carga.pop(pid):
            if lote is None or self.lote[lote].vence > t:
                kg_ok += kg
                if lote is not None:
                    self.kg_valido[lote] += kg
            else:
                kg_venc += kg
        self.entregas[pid] = {"t": t, "veh": v.id, "kg_ok": kg_ok, "kg_vencido": kg_venc}
        self.estado_ped[pid] = "entregado"
        v.estado = "sirviendo"
        v.t_ref = t + self.p.min_servicio * 60
        v.version += 1
        self._push(v.t_ref, "SIGUE", v.id, v.version)

    def _en_acopio(self, v, t):
        devueltos = v.devolver + v.a_bordo
        for pid in devueltos:
            for lote, kg in v.carga.pop(pid):
                if lote is not None:
                    self.inv[lote] += kg
            self.estado_ped[pid] = "pendiente"
        v.devolver, v.a_bordo = [], []
        v.estado, v.t_ref = "libre", t
        self._cargar(v, t)
        if devueltos:
            self._avisar("devuelto", t)

    def _lotes_en_orden(self, t):
        vivos = [l for l in self.esc.lotes if self.inv[l.id] > 1e-9 and l.vence > t]
        if self.pol.regla_lotes == "fefo":
            vivos.sort(key=lambda l: (l.vence, l.id))   # primero lo que vence primero
        return vivos                                    # fifo: orden de ingreso a bodega

    def _cargar(self, v, t):
        tiempos = self.con.tiempos(v.tipo)[0]
        toma, kg = [], 0.0
        while v.cola:
            pid = v.cola[0]
            if pid is None:
                v.cola.pop(0)
                if toma:
                    break
                continue
            q = self.ped[pid]
            if self.estado_ped[pid] != "pendiente":
                v.cola.pop(0)
            elif q.kg > v.cap + 1e-9:
                v.cola.pop(0)
                self.invalidas += 1
            elif tiempos[q.punto_id] == float("inf"):
                v.cola.pop(0)
                self.inalcanzable.setdefault(pid, set()).add(v.tipo)
            elif kg + q.kg > v.cap + 1e-9:
                break
            else:
                toma.append(v.cola.pop(0))
                kg += q.kg
        if not toma:
            v.estado, v.t_ref = "libre", t
            self._avisar("vehiculo_libre", t)
            return
        lotes = self._lotes_en_orden(t)
        for pid in toma:
            q = self.ped[pid]
            items, falta = [(None, q.kg - q.kg_perecedero)], q.kg_perecedero
            for l in lotes:
                if falta <= 1e-9:
                    break
                usa = min(self.inv[l.id], falta)
                if usa > 1e-9:
                    self.inv[l.id] -= usa
                    falta -= usa
                    items.append((l.id, usa))
            v.carga[pid] = items
            self.estado_ped[pid] = "a_bordo"
        v.a_bordo = toma
        v.max_carga = max(v.max_carga, v.kg_a_bordo())
        v.estado = "cargando"
        v.t_ref = t + self.p.min_carga * 60
        v.version += 1
        self._push(v.t_ref, "SIGUE", v.id, v.version)

    # ---------- política ----------
    def _estado(self, t, motivo) -> Estado:
        vence = {}
        for v in self.veh.values():
            for pid, items in v.carga.items():
                vs = [self.lote[l].vence for l, _ in items if l is not None]
                vence[pid] = min(vs) if vs else float("inf")
        return Estado(
            t=t, motivo=motivo, esc=self.esc, con=self.con,
            pendientes=[q for q in self.esc.pedidos if self.estado_ped[q.id] == "pendiente"],
            vehiculos=list(self.veh.values()),
            inventario=[(l.id, self.inv[l.id], l.vence) for l in self.esc.lotes
                        if self.inv[l.id] > 1e-9 and l.vence > t],
            vence_a_bordo=vence, inalcanzable=self.inalcanzable, t_fin=self.t_fin)

    def _avisar(self, motivo, t):
        if motivo not in self.pol.disparadores:
            return
        if t < self._plan_hasta:         # el despachador revisa un plan a la vez: se atiende al aprobarlo
            if self._diferido is None:
                self._push(self._plan_hasta, "AVISO", None)
            self._diferido = "cierre" if "cierre" in (motivo, self._diferido) else (self._diferido or motivo)
            return
        if self._en_aviso:               # ya se está planeando: se atiende después, en el mismo instante
            self._push(t, "AVISO", motivo)
            return
        self._en_aviso = True
        try:
            estado = self._estado(t, motivo)
            t0 = time.perf_counter()
            rutas = self.pol.planificar(estado)
            dt = time.perf_counter() - t0
        finally:
            self._en_aviso = False
        if rutas is None:
            return
        if self.pol.ultimo_fue_optimizador:
            self.recalculos.append((t, motivo, dt))
        demora = self.pol.demora_s(estado)
        if demora > 0:
            self._plan_hasta = t + demora
            self._push(t + demora, "PLAN", rutas)
        else:
            self._aplicar(rutas, t)

    def _aplicar(self, rutas, t):
        vistos, cambia = set(), {}
        for vid, seq in rutas.items():
            v = self.veh[vid]
            if v.estado == "fuera":
                continue
            ab = set(v.a_bordo)
            nuevo = [p for p in seq if p in ab]
            nuevo += [p for p in v.a_bordo if p not in nuevo]
            cola = []
            for p in seq:
                if p is None:
                    if cola and cola[-1] is not None:
                        cola.append(None)
                elif p not in ab and self.estado_ped.get(p) == "pendiente" and p not in vistos:
                    cola.append(p)
                    vistos.add(p)
            cambia[vid] = bool(v.a_bordo) and nuevo[0] != v.a_bordo[0]
            v.a_bordo, v.cola = nuevo, cola
        for w in self.veh.values():
            if w.id not in rutas:
                w.cola = [p for p in w.cola if p not in vistos]
        for vid in rutas:
            v = self.veh[vid]
            if v.estado == "libre" and v.cola:
                self._cargar(v, t)
            elif v.estado == "en_ruta" and cambia[vid] and v.tramo and v.tramo["destino"] != "acopio":
                self._cortar(v, t)


def simular(esc: Escenario, politica) -> Resultado:
    return Motor(esc, politica).correr()
