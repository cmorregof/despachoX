"""Geometría: distancias, proyección local y asignación de un punto a una zona (B.2.4)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import shapely
from shapely import wkt as shapely_wkt
from shapely.geometry import MultiPolygon, Point, Polygon

from triage import config

R_TIERRA_M = 6_371_000.0


def numero(v) -> float | None:
    """Convierte a float finito o devuelve None. Acepta coma decimal."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, str):
        v = v.strip().replace(",", ".")
        if not v:
            return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def coordenada_valida(lat, lon) -> bool:
    """Lat/lon numéricas, en rango y dentro del recuadro de Manizales."""
    la, lo = numero(lat), numero(lon)
    if la is None or lo is None:
        return False
    r = config.RECUADRO_MANIZALES
    return r["lat_min"] <= la <= r["lat_max"] and r["lon_min"] <= lo <= r["lon_max"]


def haversine_m(lat1, lon1, lat2, lon2):
    """Distancia de gran círculo en metros. Acepta escalares o arreglos de numpy."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(np.asarray(lon2, dtype=float) - np.asarray(lon1, dtype=float))
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    d = 2 * R_TIERRA_M * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))
    return float(d) if np.ndim(d) == 0 else d


def proyectar(lat, lon, lat0: float, lon0: float):
    """Proyección equirectangular local en metros centrada en (lat0, lon0)."""
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    x = R_TIERRA_M * np.radians(lon - lon0) * math.cos(math.radians(lat0))
    y = R_TIERRA_M * np.radians(lat - lat0)
    return x, y


def poligono_desde_wkt(texto):
    """Polígono shapely o None si el WKT falta o no es un polígono válido."""
    if not texto or not isinstance(texto, str):
        return None
    try:
        g = shapely_wkt.loads(texto)
    except Exception:  # WKT malformado: se trata como zona sin polígono
        return None
    if not isinstance(g, (Polygon, MultiPolygon)) or g.is_empty:
        return None
    if not g.is_valid:
        g = g.buffer(0)
    return g if not g.is_empty else None


def _geom_en_metros(g, lat0: float, lon0: float):
    def f(coords):
        px, py = proyectar(coords[:, 1], coords[:, 0], lat0, lon0)
        return np.c_[px, py]
    return shapely.transform(g, f)


def area_km2(g) -> float | None:
    if g is None:
        return None
    c = g.centroid
    return float(_geom_en_metros(g, c.y, c.x).area / 1e6)


@dataclass
class Zona:
    id: int | None
    nombre: str
    lat: float
    lon: float
    tipo: str = "barrio"
    comuna: str | None = None
    geom_wkt: str | None = None
    area_km2: float | None = None
    personas: int | None = None
    hogares: int | None = None
    tamano_hogar: float | None = None
    afectacion: float | None = None
    ocupacion: int | None = None
    critico: int = 0
    calidad_dato: str = "fuente"
    fuente: str | None = None
    fecha_corte: str | None = None
    es_debil: int = 0
    aislada: int = 0
    lambda_h: float | None = None
    rafaga_hasta: str | None = None
    _poligono: object = field(default=None, repr=False, compare=False)
    _poligono_leido: bool = field(default=False, repr=False, compare=False)

    @property
    def poligono(self):
        if not self._poligono_leido:
            self._poligono = poligono_desde_wkt(self.geom_wkt)
            self._poligono_leido = True
        return self._poligono

    @classmethod
    def desde_fila(cls, fila) -> "Zona":
        d = dict(fila)
        campos = {k: d.get(k) for k in cls.__dataclass_fields__ if not k.startswith("_") and k in d}
        return cls(**campos)


def distancia_a_zona_m(lat: float, lon: float, zona: Zona) -> float:
    """Distancia al polígono (0 si está dentro) o, sin polígono, al centroide."""
    if zona.poligono is not None:
        g = _geom_en_metros(zona.poligono, lat, lon)
        return float(g.distance(Point(0.0, 0.0)))
    return haversine_m(lat, lon, zona.lat, zona.lon)


def asignar_zona(lat, lon, zonas: list[Zona], r_max_m: float | None = None,
                 params: dict | None = None) -> tuple[int | None, list[str]]:
    """Zona de un punto: polígono que lo contiene o centroide más cercano dentro de r_max_m."""
    if not coordenada_valida(lat, lon) or not zonas:
        return None, ["sin_ubicar"]
    la, lo = numero(lat), numero(lon)
    p = params or config.PARAMETROS_DEFECTO
    pt = Point(lo, la)
    con_poligono = [z for z in zonas if z.poligono is not None]
    contienen = [z for z in con_poligono if z.poligono.covers(pt)]
    if contienen:
        mejor = min(contienen, key=lambda z: haversine_m(la, lo, z.lat, z.lon))
        return mejor.id, []
    if r_max_m is None:
        r_max_m = p["r_max_poligono_m"] if con_poligono else p["r_max_centroide_m"]
    d = haversine_m(la, lo, np.array([z.lat for z in zonas], dtype=float),
                    np.array([z.lon for z in zonas], dtype=float))
    d = np.atleast_1d(d)
    i = int(np.argmin(d))
    if d[i] < r_max_m:
        return zonas[i].id, ["asignacion_aproximada"]
    return None, ["sin_ubicar"]
