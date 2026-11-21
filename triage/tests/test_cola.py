import json

import pytest

from triage import cola
from triage.entrada_datos import a_iso
from triage.tests.conftest import h


def _sol(con, i, zona_id, t, familias, tipo_punto=None, estado="en_cola", marcas=()):
    con.execute("INSERT INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, zona_id, "
                "familias_declaradas, familias_efectivas, tipo_punto, estado, marcas) "
                "VALUES (?,?,?,?,?,?,?,?,?)",
                (a_iso(t), f"h{i}", h(str(i)), zona_id, familias, familias, tipo_punto, estado,
                 json.dumps(list(marcas))))


def test_orden_por_prioridad(con, params, zonas_sinteticas, hora):
    z = {x.nombre: x for x in zonas_sinteticas}
    _sol(con, 1, z["Barrio A"].id, hora(), 5)
    _sol(con, 2, z["Albergue Coliseo"].id, hora(), 5)               # u = 3
    _sol(con, 3, z["Barrio B"].id, hora(), 5, tipo_punto="critico")   # u = 3
    _sol(con, 4, z["Barrio C"].id, hora(), 20)
    _sol(con, 5, z["Barrio C"].id, hora(), 99, estado="confirmada_regla")
    orden = cola.cola_ordenada(con, hora(), params)
    assert [d["id"] for d in orden] == [4, 2, 3, 1]
    assert orden[0]["prioridad"] == pytest.approx(20)
    assert orden[1]["prioridad"] == pytest.approx(15)


def test_aumenta_con_la_espera(con, params, zonas_sinteticas, hora):
    _sol(con, 1, zonas_sinteticas[0].id, hora(), 4)
    p0 = cola.cola_ordenada(con, hora(0), params)[0]["prioridad"]
    p2 = cola.cola_ordenada(con, hora(2), params)[0]["prioridad"]
    assert p2 - p0 == pytest.approx(2 * params["gamma"])


def test_aislada_duplica(con, params, zonas_sinteticas, hora):
    zid = zonas_sinteticas[0].id
    _sol(con, 1, zid, hora(), 4)
    con.execute("UPDATE zonas SET aislada=1 WHERE id=?", (zid,))
    assert cola.cola_ordenada(con, hora(), params)[0]["prioridad"] == pytest.approx(8)


def test_lotes_con_conteos_exactos(con, params, zonas_sinteticas, hora):
    z = {x.nombre: x for x in zonas_sinteticas}
    for i in range(5):
        _sol(con, i, z["Barrio A"].id, hora(), 3, marcas=["sobre_tope"] if i < 2 else [])
    _sol(con, 10, z["Barrio B"].id, hora(), 7, marcas=["sin_texto"])
    _sol(con, 11, None, hora(), 2, marcas=["sin_ubicar"])
    _sol(con, 12, z["Barrio B"].id, hora(), 50, estado="cuarentena")
    l = cola.lotes(con, hora(), params)
    assert [x["zona"] for x in l] == ["Barrio A", "Barrio B", "sin zona"]
    a = l[0]
    assert a["solicitudes"] == 5 and a["familias"] == 15 and a["marcas"] == {"sobre_tope": 2}
    assert len(a["muestra"]) == 3 and set(a["muestra"]) <= set(range(1, 6))
    assert a["muestra"] == cola.lotes(con, hora(), params)[0]["muestra"]     # semilla fija
    assert l[1]["solicitudes"] == 1 and l[1]["muestra"] == [6]
    assert cola.lotes(con, hora(), params)[2]["marcas"] == {"sin_ubicar": 1}


def test_cola_vacia(con, params, hora):
    assert cola.lotes(con, hora(), params) == []
