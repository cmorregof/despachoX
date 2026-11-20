"""Políticas de despacho con una interfaz común: `planificar(estado) -> rutas`.

`rutas` es un diccionario vehículo -> lista de pedidos en orden de entrega. Un `None` dentro
de la lista obliga a volver al acopio a cargar antes de seguir. Los vehículos que no aparecen
conservan lo que tenían. Devolver `None` significa «no cambio nada».

Políticas:
- `ingenua`: orden de llegada, vehículo libre que llega más rápido, desvío solo al toparse el cierre.
- `experta`: la ingenua con dos reglas de un despachador con oficio: atiende primero lo más urgente
  y saca de bodega primero lo que vence primero. Es la línea base exigente.
- `optimiza_una_vez`: el optimizador planea una vez al inicio y no vuelve a calcular.
- `despachox`: el optimizador recalcula con cada cierre confirmado y cada tanda de pedidos.

El optimizador es intercambiable. `InsercionProvisional` es una heurística propia, marcada
como PROVISIONAL; `adaptador_b.OptimizadorB` llama al optimizador de `despacho/optimizar.py`.
"""
from __future__ import annotations

import time

import numpy as np

INF = float("inf")
# Tope de entregas por viaje en la regla ingenua. Se calibró a favor de la línea base con
# semillas distintas a las de la evaluación: sin tope fue lo que mejor le fue.
MAX_PARADAS = 99


# ------------------------------------------------------------------ línea base
def _asignar_fifo(estado, max_paradas: int, por_urgencia: bool = False) -> dict:
    """Regla del despachador con hoja de cálculo.

    Toma los pedidos sin asignar en orden de llegada. Al más antiguo le da el vehículo libre
    que llega más rápido y lo puede cargar. Ese vehículo se llena con los siguientes pedidos
    de la cola que quepan. El conductor ordena sus entregas por vecino más cercano.
    Con `por_urgencia`, la cola se ordena primero por urgencia y después por llegada.
    """
    en_cola = {p for v in estado.vehiculos for p in v.cola if p is not None}
    libres = [v for v in estado.vehiculos if v.estado == "libre" and not v.cola]
    clave = (lambda q: (-q.urgencia, q.creado, q.id)) if por_urgencia else (lambda q: (q.creado, q.id))
    espera = sorted((q for q in estado.pendientes if q.id not in en_cola), key=clave)
    rutas, tomados = {}, set()
    for q in espera:
        if not libres:
            break
        if q.id in tomados:
            continue
        aptos = [v for v in libres if v.cap >= q.kg and estado.con.tiempos(v.tipo)[0][q.punto_id] < INF]
        if not aptos:
            continue                      # espera a que vuelva un vehículo que sí pueda
        v = min(aptos, key=lambda v: (estado.con.tiempos(v.tipo)[0][q.punto_id], v.id))
        libres.remove(v)
        T = estado.con.tiempos(v.tipo)
        carga, kg = [q], q.kg
        for r in espera:
            if len(carga) >= max_paradas:
                break
            if r.id in tomados or r is q or kg + r.kg > v.cap or T[0][r.punto_id] == INF:
                continue
            carga.append(r)
            kg += r.kg
        orden, pos, resto = [], 0, carga[:]
        while resto:                      # vecino más cercano
            sig = min(resto, key=lambda r: (T[pos][r.punto_id], r.id))
            resto.remove(sig)
            orden.append(sig.id)
            pos = sig.punto_id
        tomados.update(orden)
        rutas[v.id] = orden
    return rutas or None


class Ingenua:
    disparadores = {"inicio", "pedido", "vehiculo_libre", "devuelto"}
    ultimo_fue_optimizador = False

    def __init__(self, max_paradas: int = MAX_PARADAS, regla_lotes: str = "fifo", nombre: str = "ingenua",
                 por_urgencia: bool = False):
        self.max_paradas, self.regla_lotes, self.nombre = max_paradas, regla_lotes, nombre
        self.por_urgencia = por_urgencia

    def planificar(self, estado):
        return _asignar_fifo(estado, self.max_paradas, self.por_urgencia)

    def demora_s(self, estado) -> float:
        return 0.0                        # decide al instante: ventaja para la línea base


# ------------------------------------------------------------------ optimizador provisional
class InsercionProvisional:
    """PROVISIONAL. Inserción más barata con mejora por reubicación.

    Minimiza el mismo sustituto que declara la receta del optimizador de B: retraso ponderado
    por urgencia, más una penalización por kilo perecedero que llegaría vencido, más un cargo
    pequeño por tiempo de llegada y por tiempo de viaje. Admite carga a bordo y varios viajes.
    """
    nombre = "heurística de inserción PROVISIONAL (varios viajes por vehículo)"
    un_viaje = False
    PESO = {1: 1.0, 2: 2.0, 3: 4.0}       # peso del retraso por urgencia
    PEN_KG_VENCIDO = 120.0                # segundos ponderados por kilo perecedero vencido
    PEN_LLEGADA = 0.05                    # cargo por segundo de espera del pedido
    PEN_VIAJE = 0.02

    def __init__(self, limite_s: float = 1.0):
        self.limite_s = limite_s

    def resolver(self, estado) -> dict:
        p = estado.esc.p
        self.t_carga, self.t_serv, self.t_fin = p.min_carga * 60, p.min_servicio * 60, estado.t_fin
        self.estado = estado
        self.vence = self._vencimientos(estado)
        veh = [v for v in estado.vehiculos if v.estado != "fuera"]
        self.T = {v.id: estado.con.tiempos(v.tipo) for v in veh}
        self.ini = {}
        for v in veh:
            nodo, t0 = v.ref(estado.t)
            fila = estado.con.tiempos_desde_nodo(v.tipo, nodo)
            self.ini[v.id] = (fila, t0, nodo == estado.esc.acopio_nodo and not v.a_bordo)
        # plan[v] = [entregas a bordo, viaje 1, viaje 2, ...]
        plan = {v.id: [self._ordenar_a_bordo(v)] for v in veh}
        costo = {v.id: self._costo(v, plan[v.id]) for v in veh}
        self.veh = {v.id: v for v in veh}
        pendientes = sorted(estado.pendientes, key=lambda q: (q.limite, -q.urgencia, q.id))
        fuera = []
        for q in pendientes:
            mejor = self._mejor_insercion(q, plan, costo)
            if mejor is None:
                fuera.append(q)
            else:
                self._insertar(q, mejor, plan, costo)
        self._reubicar(plan, costo, time.perf_counter() + self.limite_s)
        rutas = {}
        for vid, partes in plan.items():
            seq = list(partes[0])
            for viaje in partes[1:]:
                if viaje:
                    seq += [None] + viaje
            rutas[vid] = seq
        return rutas

    # --- piezas ---
    def _vencimientos(self, estado) -> dict:
        """Vencimiento estimado por pedido: reparto de lotes por vencimiento a los plazos más cortos."""
        vence = dict(estado.vence_a_bordo)
        lotes = sorted(([kg, v] for _, kg, v in estado.inventario), key=lambda l: l[1])
        i = 0
        for q in sorted(estado.pendientes, key=lambda q: (q.limite, q.id)):
            falta, primero = q.kg_perecedero, INF
            while falta > 1e-9 and i < len(lotes):
                usa = min(lotes[i][0], falta)
                primero = min(primero, lotes[i][1])
                lotes[i][0] -= usa
                falta -= usa
                if lotes[i][0] <= 1e-9:
                    i += 1
            vence[q.id] = primero
        return vence

    def _ordenar_a_bordo(self, v) -> list:
        return sorted(v.a_bordo, key=lambda pid: (self.estado.pedido(pid).limite, pid))

    def _costo_parada(self, q, t) -> float:
        c = self.PESO[q.urgencia] * (max(0.0, t - q.limite) + self.PEN_LLEGADA * (t - q.creado))
        if t >= self.vence.get(q.id, INF):
            c += self.PEN_KG_VENCIDO * q.kg_perecedero
        if t > self.t_fin:
            c += 1e6
        return c

    def _costo(self, v, partes) -> float:
        fila, t, en_acopio = self.ini[v.id]
        T, ped = self.T[v.id], self.estado.pedido
        costo, pos = 0.0, None
        for pid in partes[0]:
            q = ped(pid)
            d = fila[q.punto_id] if pos is None else T[pos][q.punto_id]
            t += d
            costo += self.PEN_VIAJE * d + self._costo_parada(q, t)
            t += self.t_serv
            pos = q.punto_id
        if pos is None:
            d = 0.0 if en_acopio else fila[0]
        else:
            d = T[pos][0]
        t += d
        costo += self.PEN_VIAJE * d
        for viaje in partes[1:]:
            if not viaje:
                continue
            t += self.t_carga
            pos = 0
            for pid in viaje:
                q = ped(pid)
                d = T[pos][q.punto_id]
                t += d
                costo += self.PEN_VIAJE * d + self._costo_parada(q, t)
                t += self.t_serv
                pos = q.punto_id
            d = T[pos][0]
            t += d
            costo += self.PEN_VIAJE * d
        return costo if costo < INF else 1e12

    def _mejor_insercion(self, q, plan, costo):
        mejor, mejor_delta = None, 1e9   # por encima de esto es preferible no asignarlo
        ped = self.estado.pedido
        for vid, partes in plan.items():
            v = self.veh[vid]
            if v.cap < q.kg or self.T[vid][0][q.punto_id] == INF:
                continue
            for k in range(1, len(partes) + 1):
                viaje = partes[k] if k < len(partes) else []
                if sum(ped(x).kg for x in viaje) + q.kg > v.cap + 1e-9:
                    continue
                for i in range(len(viaje) + 1):
                    prueba = partes[:k] + [viaje[:i] + [q.id] + viaje[i:]] + partes[k + 1:]
                    delta = self._costo(v, prueba) - costo[vid]
                    if delta < mejor_delta:
                        mejor, mejor_delta = (vid, k, i), delta
        return mejor

    def _insertar(self, q, lugar, plan, costo):
        vid, k, i = lugar
        if k == len(plan[vid]):
            plan[vid].append([])
        plan[vid][k].insert(i, q.id)
        costo[vid] = self._costo(self.veh[vid], plan[vid])

    def _reubicar(self, plan, costo, hasta):
        """Saca cada pedido y lo reinserta donde más baje el costo, hasta agotar mejoras o tiempo."""
        ped = self.estado.pedido
        mejora = True
        while mejora and time.perf_counter() < hasta:
            mejora = False
            for vid in list(plan):
                for k in range(1, len(plan[vid])):
                    for pid in list(plan[vid][k]):
                        if time.perf_counter() >= hasta:
                            return
                        antes = costo[vid]
                        i = plan[vid][k].index(pid)
                        plan[vid][k].pop(i)
                        sin = self._costo(self.veh[vid], plan[vid])
                        costo[vid] = sin
                        lugar = self._mejor_insercion(ped(pid), plan, costo)
                        if lugar is None:
                            plan[vid][k].insert(i, pid)
                            costo[vid] = antes
                            continue
                        w = lugar[0]
                        antes_w = costo[w] if w != vid else None
                        self._insertar(ped(pid), lugar, plan, costo)
                        total_antes = antes + (antes_w or 0.0)
                        total_despues = costo[vid] + (costo[w] if w != vid else 0.0)
                        if total_despues < total_antes - 1e-6:
                            mejora = True
                        elif lugar != (vid, k, i):     # no mejoró: se deshace
                            plan[w][lugar[1]].remove(pid)
                            costo[w] = self._costo(self.veh[w], plan[w])
                            plan[vid][k].insert(i, pid)
                            costo[vid] = antes


def optimizador_por_defecto(limite_s: float = 1.0, red: str = "auto"):
    """El optimizador de B si ya existe y la red es la real; si no, la heurística provisional."""
    if red != "malla":
        try:
            from .adaptador_b import OptimizadorB
            return OptimizadorB(limite_s=limite_s)
        except (ImportError, RuntimeError, FileNotFoundError):
            pass
    return InsercionProvisional(limite_s=limite_s)


# ------------------------------------------------------------------ políticas con optimizador
class OptimizaUnaVez:
    """Plan del optimizador al inicio. Después, lo que llegue se atiende con la regla ingenua."""
    disparadores = {"inicio", "pedido", "vehiculo_libre", "devuelto"}
    regla_lotes = "fefo"
    nombre = "optimiza_una_vez"

    def __init__(self, optimizador=None, max_paradas: int = MAX_PARADAS):
        self.opt = optimizador or optimizador_por_defecto()
        self.max_paradas = max_paradas
        self.ultimo_fue_optimizador = False

    def planificar(self, estado):
        self.ultimo_fue_optimizador = estado.motivo == "inicio"
        if self.ultimo_fue_optimizador:
            return self.opt.resolver(estado)
        return _asignar_fifo(estado, self.max_paradas)

    def demora_s(self, estado) -> float:
        return estado.esc.p.min_aprobacion * 60 if self.ultimo_fue_optimizador else 0.0


class DespachoX:
    """Optimiza al inicio y recalcula con cada cierre confirmado y cada tanda de pedidos."""
    disparadores = {"inicio", "tanda", "cierre"}
    regla_lotes = "fefo"
    nombre = "despachox"
    ultimo_fue_optimizador = True

    def __init__(self, optimizador=None):
        self.opt = optimizador or optimizador_por_defecto()
        self._vistos, self._version = set(), -1
        if getattr(self.opt, "un_viaje", False):
            # el optimizador de B planea un viaje por vehículo: hay que volver a llamarlo
            # cuando un vehículo regresa al acopio o devuelve carga
            self.disparadores = self.disparadores | {"vehiculo_libre", "devuelto"}

    def planificar(self, estado):
        if estado.motivo in ("vehiculo_libre", "devuelto") and not estado.pendientes:
            return None
        en_cola = {p for v in estado.vehiculos for p in v.cola if p is not None}
        nuevos = {q.id for q in estado.pendientes} - self._vistos
        sueltos = any(q.id not in en_cola for q in estado.pendientes)
        if estado.motivo == "tanda" and not nuevos and not sueltos and estado.con.version == self._version:
            return None                   # tanda sin novedades: no hay nada que recalcular
        self._vistos |= {q.id for q in estado.pendientes}
        self._version = estado.con.version
        return self.opt.resolver(estado)

    def demora_s(self, estado) -> float:
        return estado.esc.p.min_aprobacion * 60


def crear(nombre: str, optimizador=None, max_paradas: int = MAX_PARADAS):
    """Fábrica. Cada corrida necesita una política nueva, porque guardan memoria."""
    if nombre == "ingenua":
        return Ingenua(max_paradas)
    if nombre == "ingenua_fefo":
        return Ingenua(max_paradas, regla_lotes="fefo", nombre="ingenua_fefo")
    if nombre == "experta":       # la línea base más fuerte: prioriza urgencia y saca primero lo que vence
        return Ingenua(max_paradas, regla_lotes="fefo", nombre="experta", por_urgencia=True)
    if nombre == "optimiza_una_vez":
        return OptimizaUnaVez(optimizador, max_paradas)
    if nombre == "despachox":
        return DespachoX(optimizador)
    raise ValueError(nombre)


POLITICAS = ("ingenua", "experta", "optimiza_una_vez", "despachox")
