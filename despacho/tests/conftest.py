"""Fixtures sin red: grafo sintético con la forma del de osmnx y una base temporal."""
import json
from datetime import datetime, timedelta

import networkx as nx
import pytest

from datos import db
from despacho import red

AHORA = datetime(2026, 11, 20, 10, 0, 0, tzinfo=db.BOGOTA)
LAT0, LON0, PASO = 5.06, -75.50, 0.002
AISLADO = 100          # nodo unido a la malla solo por el puente (4, AISLADO)
PUENTE = (4, AISLADO)


def nodo(r, c):
    return r * 5 + c


def _arista(g, u, v, highway="tertiary"):
    largo = float(red.metros(g.nodes[u]["y"], g.nodes[u]["x"], g.nodes[v]["y"], g.nodes[v]["x"]))
    for a, b in ((u, v), (v, u)):
        g.add_edge(a, b, length=largo, travel_time=largo / (30 / 3.6), highway=highway, oneway=False)


@pytest.fixture
def grafo():
    """Malla 5x5 (nodo = fila*5 + col) más un nodo aislado unido por un puente al nodo 4."""
    g = nx.MultiDiGraph()
    g.graph["crs"] = "epsg:4326"
    for r in range(5):
        for c in range(5):
            g.add_node(nodo(r, c), y=LAT0 + r * PASO, x=LON0 + c * PASO)
    g.add_node(AISLADO, y=LAT0, x=LON0 + 4 * PASO + 0.012)   # a ~1,3 km del nodo 4
    for r in range(5):
        for c in range(5):
            if c < 4:
                _arista(g, nodo(r, c), nodo(r, c + 1))
            if r < 4:
                _arista(g, nodo(r, c), nodo(r + 1, c))
    _arista(g, *PUENTE, highway="secondary")
    return g


def iso(dt):
    return dt.isoformat(timespec="seconds")


def coords(g, n):
    return g.nodes[n]["y"], g.nodes[n]["x"]


class Mundo:
    """Ayudante para cargar datos sintéticos en la base temporal."""

    def __init__(self, con, g):
        self.con, self.g = con, g

    def acopio(self, id, n, frio=0):
        lat, lon = coords(self.g, n)
        self.con.execute("INSERT INTO acopios(id,nombre,lat,lon,tiene_frio) VALUES (?,?,?,?,?)",
                         (id, f"Acopio {id}", lat, lon, frio))

    def punto(self, id, n, critico=0):
        lat, lon = coords(self.g, n)
        self.con.execute("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (?,?,?,?,?,?)",
                         (id, f"Punto {id}", "Barrio X", lat, lon, critico))

    def vehiculo(self, id, tipo, cap, acopio_id=1):
        self.con.execute("INSERT INTO vehiculos(id,nombre,tipo,capacidad_kg,acopio_id,estado) "
                         "VALUES (?,?,?,?,?,'libre')", (id, f"Veh {id}", tipo, cap, acopio_id))

    def lote(self, id, producto="arroz", kg=1000, acopio_id=1, perecedero=0, vence=None, empaque=0):
        self.con.execute("INSERT INTO lotes(id,acopio_id,producto,kg,perecedero,vence_en,empaque_activo) "
                         "VALUES (?,?,?,?,?,?,?)",
                         (id, acopio_id, producto, kg, perecedero, iso(vence) if vence else None, empaque))

    def pedido(self, id, punto_id, kg, producto="arroz", urgencia=2, estado="confirmado"):
        self.con.execute(
            "INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,limite_en,estado) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (id, iso(AHORA - timedelta(hours=1)), punto_id, 5, kg,
             json.dumps([{"producto": producto, "kg": kg}]), urgencia,
             iso(AHORA + timedelta(hours=10)), estado))

    def cierre(self, estado="confirmado", u=None, v=None, lat=None, lon=None, tipos=None):
        cur = self.con.execute(
            "INSERT INTO cierres(creado_en,descripcion,lat,lon,osm_u,osm_v,tipos_bloqueados,estado) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (iso(AHORA), "cierre de prueba", lat, lon, u, v,
             tipos or '["camion","campero","moto"]', estado))
        return cur.lastrowid

    def listo(self):
        self.con.commit()
        return self


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "prueba.db")
    yield c
    c.close()


@pytest.fixture
def mundo(con, grafo):
    """Acopio en la esquina (nodo 0), un camión y un campero, arroz de sobra y cuatro puntos."""
    m = Mundo(con, grafo)
    m.acopio(1, nodo(0, 0))
    m.vehiculo(1, "camion", 100)
    m.vehiculo(2, "campero", 50)
    m.lote(1, kg=5000)
    for i, n in enumerate([nodo(4, 4), nodo(4, 0), nodo(2, 3), nodo(3, 1)], start=1):
        m.punto(i, n)
    return m


@pytest.fixture
def ahora():
    return AHORA
