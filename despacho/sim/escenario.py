"""Generador de escenarios con semilla.

Todo es sintético. Cada componente (puntos, pedidos, lotes, cierres) usa su propio flujo
aleatorio derivado de la semilla, de modo que cambiar un parámetro no altera los demás.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.sparse.csgraph import dijkstra

from .red_sim import CENTRO_MANIZALES, TIPOS, Red, cargar_red

H = 3600.0


@dataclass
class Parametros:
    """Supuestos de la simulación. Se copian tal cual a docs/SIMULACION.md."""
    # tamaño
    n_puntos_min: int = 30
    n_puntos_max: int = 80
    frac_criticos: float = 0.20
    separacion_min_m: float = 250.0
    radio_km: float = 6.0                  # los puntos quedan a esta distancia del centro, como mucho
    # demanda
    pedidos_por_punto: float = 3.0
    frac_pedidos_inicio: float = 0.40      # pedidos que ya están en cola al empezar
    horas_pedidos: float = 8.0             # los demás llegan uniformes en [0, 8 h]
    horas_jornada: float = 14.0            # corte de la simulación
    familias_min: int = 3
    familias_max: int = 50
    kg_por_familia: float = 12.0
    frac_perecedero_min: float = 0.20
    frac_perecedero_max: float = 0.50
    plazo_h: dict = field(default_factory=lambda: {3: 3.0, 2: 5.0, 1: 8.0})  # por urgencia
    # inventario
    oferta_perecedera: float = 1.0         # kg perecederos en bodega / kg perecederos pedidos
    lote_kg_min: float = 100.0
    lote_kg_max: float = 400.0
    vence_h_min: float = 6.0
    vence_h_max: float = 48.0
    # flota: capacidad en kg y un vehículo por cada tantos puntos
    capacidad_kg: dict = field(default_factory=lambda: {"camion": 3000.0, "campero": 700.0, "moto": 60.0})
    puntos_por_vehiculo: dict = field(default_factory=lambda: {"camion": 30, "campero": 15, "moto": 20})
    # cierres
    cierres_min: int = 3
    cierres_max: int = 8
    frac_cierres_inicio: float = 0.30      # cierres que existen desde la hora 0 (y nadie conoce)
    p_bloquea: dict = field(default_factory=lambda: {"camion": 1.0, "campero": 0.7, "moto": 0.3})
    radio_libre_acopio_m: float = 400.0    # no se cierran tramos pegados al acopio
    # operación
    min_carga: float = 10.0                # minutos para cargar en el acopio
    min_servicio: float = 8.0              # minutos por entrega
    min_reporte: float = 3.0               # lo que pierde el conductor al toparse un cierre
    min_confirmacion: float = 5.0          # del reporte a la confirmación humana del cierre
    min_aprobacion: float = 2.0            # lo que tarda el despachador en aprobar un plan
    min_tanda: float = 30.0                # cada cuánto se libera una tanda de pedidos


# Niveles de carga del sistema: cuántos pedidos hace cada punto en la jornada. Se eligieron con
# semillas de calibración (100 a 111): la política ingenua cumple cerca del 82 %, 63 % y 46 % de
# los pedidos críticos a tiempo en cada nivel.
NIVELES_CARGA = {
    "holgada": {"pedidos_por_punto": 2.5},
    "media": {"pedidos_por_punto": 3.0},
    "alta": {"pedidos_por_punto": 3.5},
}


@dataclass
class Punto:
    id: int            # 1..P; coincide con el índice de sitio (el acopio es el sitio 0)
    nodo: int
    critico: bool


@dataclass
class Pedido:
    id: int
    creado: float
    punto_id: int
    familias: int
    kg: float
    kg_perecedero: float
    urgencia: int
    limite: float


@dataclass
class Lote:
    id: int            # orden de ingreso a bodega
    kg: float
    vence: float


@dataclass
class Vehiculo:
    id: int
    tipo: str
    capacidad_kg: float


@dataclass
class Cierre:
    id: int
    aristas: tuple     # índices de arista (los dos sentidos)
    t_ocurre: float
    tipos: tuple       # tipos de vehículo que no pasan


@dataclass
class Escenario:
    semilla: int
    red: Red
    acopio_nodo: int
    puntos: list
    pedidos: list
    lotes: list
    vehiculos: list
    cierres: list
    p: Parametros

    @property
    def sitios(self):
        return [self.acopio_nodo] + [q.nodo for q in self.puntos]


def _puntos(red: Red, acopio: int, n: int, p: Parametros, rng) -> list:
    """Nodos alcanzables en campero de ida y vuelta desde el acopio, separados entre sí."""
    m = red.matriz("campero")
    ida = dijkstra(m, directed=True, indices=acopio)
    vuelta = dijkstra(m.T.tocsr(), directed=True, indices=acopio)
    al_centro = red.metros_a(*CENTRO_MANIZALES)
    elegidos = []
    for c in rng.permutation(red.n):
        if c == acopio or not np.isfinite(ida[c]) or not np.isfinite(vuelta[c]):
            continue
        if al_centro[c] > p.radio_km * 1000:
            continue
        d = red.metros_a(red.lat[c], red.lon[c])
        if d[acopio] < p.separacion_min_m or (elegidos and d[elegidos].min() < p.separacion_min_m):
            continue
        elegidos.append(int(c))
        if len(elegidos) == n:
            break
    n_crit = max(1, round(p.frac_criticos * len(elegidos)))
    criticos = set(rng.choice(len(elegidos), n_crit, replace=False).tolist())
    return [Punto(i + 1, nodo, i in criticos) for i, nodo in enumerate(elegidos)]


def _pedidos(puntos, p: Parametros, rng) -> list:
    n = max(len(puntos) // 2, int(rng.poisson(p.pedidos_por_punto * len(puntos))))
    filas = []
    for _ in range(n):
        q = puntos[int(rng.integers(len(puntos)))]
        creado = 0.0 if rng.random() < p.frac_pedidos_inicio else float(rng.uniform(0, p.horas_pedidos * H))
        familias = int(rng.integers(p.familias_min, p.familias_max + 1))
        kg = familias * p.kg_por_familia
        kg_per = round(kg * float(rng.uniform(p.frac_perecedero_min, p.frac_perecedero_max)), 1)
        if q.critico:
            urgencia = 3 if rng.random() < 0.8 else 2
        else:
            urgencia = int(rng.choice([1, 2, 3], p=[0.4, 0.5, 0.1]))
        filas.append((creado, q.id, familias, kg, kg_per, urgencia))
    filas.sort(key=lambda f: f[0])
    return [Pedido(i + 1, c, pid, fam, kg, kp, u, c + p.plazo_h[u] * H)
            for i, (c, pid, fam, kg, kp, u) in enumerate(filas)]


def _lotes(pedidos, p: Parametros, rng) -> list:
    falta = p.oferta_perecedera * sum(q.kg_perecedero for q in pedidos)
    lotes = []
    while falta > 1e-6:
        kg = min(falta, float(rng.uniform(p.lote_kg_min, p.lote_kg_max)))
        lotes.append(Lote(len(lotes) + 1, round(kg, 1), float(rng.uniform(p.vence_h_min, p.vence_h_max)) * H))
        falta -= kg
    return lotes


def _flota(n_puntos: int, p: Parametros) -> list:
    flota = []
    for tipo in TIPOS:
        for _ in range(max(1, round(n_puntos / p.puntos_por_vehiculo[tipo]))):
            flota.append(Vehiculo(len(flota) + 1, tipo, p.capacidad_kg[tipo]))
    return flota


def _cierres(red: Red, acopio: int, puntos, n: int, p: Parametros, rng) -> list:
    """Cierres sobre tramos que de verdad se usan: los de los caminos acopio-punto en campero.

    Se sortean con probabilidad proporcional al número de caminos que pasan por el tramo.
    Un cierre en una calle que nadie usa no pondría a prueba a ninguna política.
    """
    m = red.matriz("campero")
    destinos = [q.nodo for q in puntos]
    uso = {}
    for matriz, invertir in ((m, False), (m.T.tocsr(), True)):
        _, pred = dijkstra(matriz, directed=True, indices=acopio, return_predecessors=True)
        for d in destinos:
            v = d
            while v != acopio and pred[v] >= 0:
                u = int(pred[v])
                arista = red.arista.get((v, u) if invertir else (u, v))
                if arista is not None:
                    uso[arista] = uso.get(arista, 0) + 1
                v = u
    al_acopio = red.metros_a(red.lat[acopio], red.lon[acopio])
    lejos = lambda a: min(al_acopio[red.eu[a]], al_acopio[red.ev[a]]) > p.radio_libre_acopio_m
    candidatas = [a for a in uso if lejos(a)]
    if not candidatas:
        return []
    pesos = np.array([uso[a] for a in candidatas], float)
    elegidas = rng.choice(len(candidatas), min(n, len(candidatas)), replace=False, p=pesos / pesos.sum())
    cierres = []
    for i, k in enumerate(elegidas):
        a = candidatas[int(k)]
        par = red.arista.get((int(red.ev[a]), int(red.eu[a])))
        aristas = (a,) if par is None else (a, par)
        t = 0.0 if rng.random() < p.frac_cierres_inicio else float(rng.uniform(0, p.horas_pedidos * H))
        tipos = tuple(t_ for t_ in TIPOS if rng.random() < p.p_bloquea[t_])
        cierres.append(Cierre(i + 1, aristas, t, tipos))
    return cierres


def generar(semilla: int, red: Red | str = "auto", p: Parametros | None = None,
            n_puntos: int | None = None, n_cierres: int | None = None) -> Escenario:
    """Escenario reproducible. `red` puede ser una `Red`, 'auto', 'osm' o 'malla'."""
    p = p or Parametros()
    if isinstance(red, str):
        red = cargar_red(red)
    r_tam, r_pun, r_ped, r_lot, r_cie = [np.random.default_rng(s) for s in
                                         np.random.SeedSequence(semilla).spawn(5)]
    # el acopio queda sobre una vía apta para camión, lo más cerca posible del centro
    de_camion = red.nodos_del_tipo("camion")
    acopio = int(de_camion[red.metros_a(*CENTRO_MANIZALES)[de_camion].argmin()])
    if n_puntos is None:
        n_puntos = int(r_tam.integers(p.n_puntos_min, p.n_puntos_max + 1))
    if n_cierres is None:
        n_cierres = int(r_tam.integers(p.cierres_min, p.cierres_max + 1))
    puntos = _puntos(red, acopio, n_puntos, p, r_pun)
    pedidos = _pedidos(puntos, p, r_ped)
    return Escenario(semilla, red, acopio, puntos, pedidos, _lotes(pedidos, p, r_lot),
                     _flota(len(puntos), p), _cierres(red, acopio, puntos, n_cierres, p, r_cie), p)
