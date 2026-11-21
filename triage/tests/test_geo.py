import math

import numpy as np

from triage import geo
from triage.geo import Zona
from triage.tests.conftest import LAT0, LON0, cuadrado_wkt, desplazar


def test_haversine_puntos_conocidos():
    # A lo largo de un meridiano la distancia exacta es R·Δφ.
    esperado = geo.R_TIERRA_M * math.radians(0.01)
    assert abs(geo.haversine_m(5.0, -75.5, 5.01, -75.5) - esperado) < 1.0
    # Un grado de ecuador.
    assert abs(geo.haversine_m(0, 0, 0, 1) - 111_194.93) < 1.0
    assert geo.haversine_m(5.0, -75.5, 5.0, -75.5) == 0.0
    d = geo.haversine_m(5.0, -75.5, np.array([5.01, 5.0]), np.array([-75.5, -75.5]))
    assert d.shape == (2,) and abs(d[0] - esperado) < 1.0


def test_proyeccion_local_coincide_con_haversine():
    x, y = geo.proyectar(np.array([5.07]), np.array([-75.49]), 5.06, -75.50)
    d = math.hypot(x[0], y[0])
    assert abs(d - geo.haversine_m(5.06, -75.50, 5.07, -75.49)) < 2.0


def _zonas_poligono():
    b = desplazar(LAT0, LON0, este_m=600)
    return [Zona(id=1, nombre="A", lat=LAT0, lon=LON0, geom_wkt=cuadrado_wkt(LAT0, LON0, 600)),
            Zona(id=2, nombre="B", lat=b[0], lon=b[1], geom_wkt=cuadrado_wkt(b[0], b[1], 600))]


def test_asignacion_dentro_de_poligono():
    p = desplazar(LAT0, LON0, norte_m=100, este_m=-100)
    assert geo.asignar_zona(p[0], p[1], _zonas_poligono(), 500) == (1, [])


def test_asignacion_en_el_limite_entre_dos_poligonos():
    # El borde compartido está a 300 m al este de A: lo contienen los dos y gana el centroide
    # más cercano (equidistante; se acepta cualquiera de los dos pero sin marca).
    zonas = _zonas_poligono()
    lat, lon = desplazar(LAT0, LON0, este_m=300)
    zid, marcas = geo.asignar_zona(lat, lon, zonas, 500)
    assert zid in (1, 2) and marcas == []
    # Borde exterior de A (al oeste): lo contiene solo A.
    lat, lon = desplazar(LAT0, LON0, este_m=-300)
    assert geo.asignar_zona(lat, lon, zonas, 500)[0] == 1


def test_asignacion_aproximada_y_fuera_de_rango():
    zonas = _zonas_poligono()
    cerca = desplazar(LAT0, LON0, norte_m=450)        # fuera del polígono, centroide a 450 m
    assert geo.asignar_zona(cerca[0], cerca[1], zonas, 500) == (1, ["asignacion_aproximada"])
    lejos = desplazar(LAT0, LON0, norte_m=2000)
    assert geo.asignar_zona(lejos[0], lejos[1], zonas, 500) == (None, ["sin_ubicar"])


def test_sin_poligonos_usa_1500_m_por_defecto():
    zonas = [Zona(id=7, nombre="Sin", lat=LAT0, lon=LON0)]
    a = desplazar(LAT0, LON0, norte_m=1400)
    b = desplazar(LAT0, LON0, norte_m=1600)
    assert geo.asignar_zona(a[0], a[1], zonas) == (7, ["asignacion_aproximada"])
    assert geo.asignar_zona(b[0], b[1], zonas) == (None, ["sin_ubicar"])


def test_coordenadas_invalidas():
    zonas = [Zona(id=7, nombre="Sin", lat=LAT0, lon=LON0)]
    for lat, lon in [(None, None), (0, 0), (float("nan"), -75.5), ("x", "y"),
                     (95, -75.5), (5.06, -74.0), (4.5, -75.5)]:
        assert geo.asignar_zona(lat, lon, zonas) == (None, ["sin_ubicar"])
    assert geo.asignar_zona(LAT0, LON0, []) == (None, ["sin_ubicar"])
    assert geo.asignar_zona("5,06", "-75,50", zonas)[0] == 7      # coma decimal


def test_wkt_malo_se_trata_como_sin_poligono():
    z = Zona(id=1, nombre="X", lat=LAT0, lon=LON0, geom_wkt="POLYGON((esto no es wkt")
    assert z.poligono is None
    assert geo.asignar_zona(LAT0, LON0, [z]) == (1, ["asignacion_aproximada"])


def test_distancia_a_zona():
    z = _zonas_poligono()[0]
    assert geo.distancia_a_zona_m(LAT0, LON0, z) == 0.0
    p = desplazar(LAT0, LON0, norte_m=800)                 # 500 m fuera del borde norte
    assert abs(geo.distancia_a_zona_m(p[0], p[1], z) - 500) < 5
    sin = Zona(id=2, nombre="S", lat=LAT0, lon=LON0)
    assert abs(geo.distancia_a_zona_m(p[0], p[1], sin) - 800) < 5
