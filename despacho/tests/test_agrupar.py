"""Pruebas de despacho/agrupar.py: la regla que junta pedidos por punto y ventana de tiempo."""
import json
import random
from datetime import datetime, timedelta

import numpy as np
import pytest

from datos import db
from despacho import agrupar as ag
from triage import censo, cluster, config
from triage.geo import Zona

AHORA = datetime(2026, 11, 20, 10, 0, 0, tzinfo=db.BOGOTA)
LAT, LON = 5.06, -75.50


def iso(dt):
    return dt.isoformat(timespec="seconds")


def pedido(id, punto_id=1, horas=1.0, familias=5, kg=50.0, productos=None, urgencia=2,
           limite_h=10, origen="mensaje"):
    return {
        "id": id, "creado_en": iso(AHORA - timedelta(hours=horas)), "punto_id": punto_id,
        "familias": familias, "kg_estimado": kg,
        "productos": json.dumps(productos if productos is not None else [{"producto": "arroz", "kg": kg}]),
        "urgencia": urgencia, "limite_en": iso(AHORA + timedelta(hours=limite_h)) if limite_h else None,
        "estado": "confirmado", "origen": origen, "texto_original": "sintético",
        "remitente_hash": None, "duplicado_de": None,
    }


def puntos(*coords):
    return {i: {"id": i, "nombre": f"Punto {i}", "lat": la, "lon": lo, "critico": 0}
            for i, (la, lo) in enumerate(coords, start=1)}


def test_mismo_punto_misma_hora_un_grupo():
    ps = [pedido(7, horas=0.5, familias=4, kg=40, urgencia=1, limite_h=12),
          pedido(3, horas=1.0, familias=6, kg=None, urgencia=3, limite_h=5,
                 productos=[{"producto": "Fríjol", "kg": 0}])]
    grupos = ag.agrupar(ps, puntos((LAT, LON)), ahora=AHORA, zonas=[])
    assert len(grupos) == 1
    g = grupos[0]
    assert g.pedido_ids == [3, 7]
    assert g.familias == g.familias_declaradas == 10
    assert g.tope_familias is None and not g.sobre_tope
    assert g.kg == pytest.approx(40 + 6 * ag.KG_POR_FAMILIA)
    assert g.urgencia == 3
    assert g.limite_en == iso(AHORA + timedelta(hours=5))
    assert g.creado_en == iso(AHORA - timedelta(hours=1))
    fila = g.como_pedido()
    assert fila["id"] == 3                       # la madre: el más antiguo
    assert fila["miembros"] == [3, 7] and fila["grupo"] == g.clave
    assert fila["estado"] == "confirmado" and fila["duplicado_de"] is None
    assert {l["producto"] for l in json.loads(fila["productos"])} == {"arroz", "Fríjol"}


def test_mismo_punto_20_horas_dos_grupos():
    ps = [pedido(1, horas=1), pedido(2, horas=21)]
    grupos = ag.agrupar(ps, puntos((LAT, LON)), ahora=AHORA, zonas=[])
    assert sorted(g.pedido_ids for g in grupos) == [[1], [2]]


def test_puntos_a_5_km_grupos_distintos():
    ps = [pedido(1, punto_id=1), pedido(2, punto_id=2)]
    grupos = ag.agrupar(ps, puntos((LAT, LON), (LAT + 0.045, LON)), ahora=AHORA, zonas=[])
    assert sorted(g.pedido_ids for g in grupos) == [[1], [2]]


def test_puntos_vecinos_se_parten_por_punto():
    ps = [pedido(1, punto_id=1), pedido(2, punto_id=2), pedido(3, punto_id=1, horas=2)]
    grupos = ag.agrupar(ps, puntos((LAT, LON), (LAT + 0.0005, LON)), ahora=AHORA, zonas=[])
    assert sorted(g.pedido_ids for g in grupos) == [[1, 3], [2]]


def test_tope_por_zona():
    p = config.completar(None)
    zona = Zona(id=1, nombre="Zona chica", lat=LAT, lon=LON, personas=30, tamano_hogar=3,
                afectacion=1.0)
    tope = censo.tope_familias(zona, p)
    ps = [pedido(i, horas=0.1 * i, familias=20, kg=200.0,
                 productos=[{"producto": "arroz", "kg": 150}, {"producto": "aceite", "kg": 50}])
          for i in range(1, 11)]
    g, = ag.agrupar(ps, puntos((LAT, LON)), ahora=AHORA, zonas=[zona], params=p)
    assert g.familias_declaradas == 200 and tope < 200
    assert g.tope_familias == tope and g.familias == tope and g.sobre_tope
    assert g.zona == "Zona chica"
    factor = tope / 200
    assert g.kg_declarados == pytest.approx(2000)
    assert g.kg == pytest.approx(2000 * factor)
    kilos = {l["producto"]: l["kg"] for l in g.productos}
    assert kilos["arroz"] == pytest.approx(1500 * factor, abs=1e-3)
    assert kilos["aceite"] == pytest.approx(500 * factor, abs=1e-3)
    assert g.como_pedido()["familias"] == tope


def test_determinista_con_entrada_barajada():
    pts = puntos((LAT, LON), (LAT + 0.01, LON), (LAT + 0.02, LON + 0.01))
    rng = random.Random(4)
    ps = [pedido(i, punto_id=rng.randint(1, 3), horas=rng.uniform(0, 40),
                 urgencia=rng.randint(1, 3), limite_h=rng.choice([None, 4, 8, 20]))
          for i in range(1, 80)]
    base = ag.agrupar(ps, pts, ahora=AHORA)
    for semilla in range(3):
        otra = ps[:]
        random.Random(semilla).shuffle(otra)
        r = ag.agrupar(otra, pts, ahora=AHORA)
        assert [g.clave for g in r] == [g.clave for g in base]
        assert [g.pedido_ids for g in r] == [g.pedido_ids for g in base]
    # Orden: urgencia descendente, luego límite ascendente con None al final.
    llaves = [(-g.urgencia, g.limite_en is None, g.limite_en or "") for g in base]
    assert llaves == sorted(llaves)


def test_activo(monkeypatch):
    monkeypatch.delenv(ag.VARIABLE, raising=False)
    assert ag.activo() is False
    assert ag.activo(True) is True
    monkeypatch.setenv(ag.VARIABLE, "1")
    assert ag.activo() is True
    monkeypatch.setenv(ag.VARIABLE, "sí")
    assert ag.activo() is True
    monkeypatch.setenv(ag.VARIABLE, "0")
    assert ag.activo() is False


def test_silencio_y_sin_punto_quedan_fuera():
    ps = [pedido(1), pedido(2, origen="silencio"), pedido(3, punto_id=99), pedido(4, punto_id=None)]
    pts = puntos((LAT, LON))
    grupos = ag.agrupar(ps, pts, ahora=AHORA, zonas=[])
    assert [g.pedido_ids for g in grupos] == [[1]]
    assert sorted(q["id"] for q in ag.sin_agrupar(ps, pts)) == [2, 3, 4]


def _particion(etiquetas):
    grupos = {}
    for i, e in enumerate(etiquetas):
        grupos.setdefault(("r", i) if e == cluster.RUIDO else e, []).append(i)
    return sorted(tuple(v) for v in grupos.values())


@pytest.mark.parametrize("semilla", range(5))
def test_misma_particion_que_st_dbscan(semilla):
    rng = np.random.default_rng(semilla)
    lugares = np.c_[LAT + rng.uniform(0, 0.01, 12), LON + rng.uniform(0, 0.01, 12)]
    k = rng.integers(0, 12, 300)
    lat, lon = lugares[k, 0], lugares[k, 1]
    t = -rng.uniform(0, 96, 300)
    t[5] = np.nan
    esperado = cluster.st_dbscan(lat, lon, t, ag.EPS_S_M, ag.EPS_T_H, min_samples=2)
    obtenido = ag.st_dbscan_min2(lat, lon, t, ag.EPS_S_M, ag.EPS_T_H)
    assert _particion(obtenido) == _particion(esperado)


def test_desde_base(con):
    con.execute("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (1,'P1','B',?,?,1)",
                (LAT, LON))
    for i, estado in [(1, "confirmado"), (2, "confirmado"), (3, "nuevo")]:
        q = pedido(i, horas=i * 0.2)
        con.execute("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,"
                    "urgencia,limite_en,estado) VALUES (?,?,?,?,?,?,?,?,?)",
                    (q["id"], q["creado_en"], 1, q["familias"], q["kg_estimado"], q["productos"],
                     q["urgencia"], q["limite_en"], estado))
    con.commit()
    g, = ag.agrupar_desde_base(con, ahora=AHORA)
    assert g.pedido_ids == [1, 2] and g.critico
    n, = ag.grupos_nuevos(con, ahora=AHORA)
    assert n.pedido_ids == [3]
