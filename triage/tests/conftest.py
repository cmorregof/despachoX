"""Fixtures sin red: base temporal, zonas sintéticas y hora fija."""
from datetime import datetime, timedelta

import pytest

from datos import db as datos_db
from triage import config
from triage import db as tdb

AHORA = datetime(2026, 11, 20, 10, 0, 0, tzinfo=datos_db.BOGOTA)
LAT0, LON0 = 5.0600, -75.5000
GRADO_LAT_M = 111_320.0     # metros por grado de latitud (aprox.)


def desplazar(lat, lon, norte_m=0.0, este_m=0.0):
    """Mueve un punto unos metros al norte y al este (aproximación local)."""
    import math
    return (lat + norte_m / GRADO_LAT_M,
            lon + este_m / (GRADO_LAT_M * math.cos(math.radians(lat))))


def h(etiqueta: str) -> str:
    """Hash sintético de remitente (64 hex)."""
    import hashlib
    return hashlib.sha256(f"prueba:{etiqueta}".encode()).hexdigest()


def cuadrado_wkt(lat, lon, lado_m):
    """Polígono cuadrado centrado en (lat, lon) en WKT (lon lat)."""
    s_lat, s_lon = desplazar(lat, lon, -lado_m / 2, -lado_m / 2)
    n_lat, n_lon = desplazar(lat, lon, lado_m / 2, lado_m / 2)
    return (f"POLYGON(({s_lon} {s_lat}, {n_lon} {s_lat}, {n_lon} {n_lat}, "
            f"{s_lon} {n_lat}, {s_lon} {s_lat}))")


@pytest.fixture
def ahora():
    return AHORA


@pytest.fixture
def params():
    return config.completar(None)


@pytest.fixture
def con(tmp_path):
    c = tdb.conectar(tmp_path / "triage_prueba.db")
    yield c
    c.close()


def zonas_basicas():
    """Tres barrios separados 2 km, un albergue y una vereda (todos sintéticos)."""
    a = (LAT0, LON0)
    b = desplazar(LAT0, LON0, este_m=2000)
    c = desplazar(LAT0, LON0, norte_m=2000)
    v = desplazar(LAT0, LON0, norte_m=-8000, este_m=-6000)
    al = desplazar(LAT0, LON0, norte_m=-2000)
    return [
        {"nombre": "Barrio A", "comuna": "Uno", "lat": a[0], "lon": a[1], "personas": 6000,
         "afectacion": 0.2, "fuente": "sintetico", "fecha_corte": "2026-11-20"},
        {"nombre": "Barrio B", "comuna": "Uno", "lat": b[0], "lon": b[1], "personas": 3000,
         "afectacion": 0.2, "fuente": "sintetico", "fecha_corte": "2026-11-20"},
        {"nombre": "Barrio C", "comuna": "Dos", "lat": c[0], "lon": c[1], "personas": 9000,
         "afectacion": 0.1, "fuente": "sintetico", "fecha_corte": "2026-11-20"},
        {"nombre": "Albergue Coliseo", "tipo": "albergue", "comuna": "Dos", "lat": al[0],
         "lon": al[1], "ocupacion": 300, "personas": 300, "afectacion": 1.0},
        {"nombre": "Vereda Sintetica", "tipo": "vereda", "lat": v[0], "lon": v[1], "personas": 400},
    ]


@pytest.fixture
def zonas_sinteticas(con, params):
    """Carga las zonas básicas en la base temporal y devuelve sus objetos Zona."""
    from triage import censo
    filas, _ = censo.normalizar_zonas(zonas_basicas(), params)
    censo.cargar_zonas(con, filas)
    return censo.zonas_de_base(con)


@pytest.fixture
def hora():
    def _h(horas=0.0, minutos=0.0):
        return AHORA + timedelta(hours=horas, minutes=minutos)
    return _h
