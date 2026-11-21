import math
from datetime import datetime, timedelta

import networkx as nx
import pytest

from datos import db as datos_db
from entrada import silencio as entrada_silencio
from triage import censo, config, debiles
from triage.entrada_datos import a_iso
from triage.tests.conftest import h

BOG = datos_db.BOGOTA
EV = datetime(2026, 11, 20, 6, 0, tzinfo=BOG)     # evento a las 06:00 = inicio de la jornada


def hh(horas):
    return EV + timedelta(hours=horas)


def _p(params, evento=EV, **extra):
    return dict(params, hora_evento=a_iso(evento), **extra)


def _sol(con, i, zona_id, t, estado="en_cola", canal="chat", lugar=1):
    con.execute("INSERT INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, zona_id, canal, "
                "lugar_confirmado, estado) VALUES (?,?,?,?,?,?,?)",
                (a_iso(t), f"s{i}", h(f"r{i}"), zona_id, canal, lugar, estado))


def _solo(con, zonas, nombre):
    """Deja con afectación solo la zona `nombre` para aislar cada prueba."""
    for z in zonas:
        con.execute("UPDATE zonas SET afectacion=? WHERE id=?", (z.afectacion if z.nombre == nombre
                                                                 else 0.0, z.id))
    return next(z for z in zonas if z.nombre == nombre)


def test_umbral_y_jornada_son_los_de_entrada():
    assert config.PARAMETROS_DEFECTO["silencio_h"] == entrada_silencio.UMBRAL_H
    assert config.PARAMETROS_DEFECTO["jornada_inicio"] == entrada_silencio.JORNADA_INICIO
    assert "alpha_sil" in config.PARAMETROS_DEFECTO     # obsoleto, se conserva


def test_inicio_de_jornada():
    assert debiles.inicio_jornada(hh(3), "06:00") == EV
    assert debiles.inicio_jornada(EV - timedelta(hours=1), "06:00") == EV - timedelta(days=1)


def test_silencio_a_las_6_horas_y_escala(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Albergue Coliseo")
    p = _p(params)
    assert debiles.detectar(con, hh(5.99), p) == []
    assert debiles.detectar(con, hh(6), p) == [zona.id]
    tarea = con.execute("SELECT * FROM tareas_campo").fetchone()
    assert tarea["estado"] == "abierta" and tarea["zona_id"] == zona.id
    assert censo.zona_por_id(con, zona.id).es_debil == 1
    assert debiles.detectar(con, hh(7), p) == []                    # no duplica
    assert debiles.escalar(con, hh(11), p) == []                    # 5 h después de creada
    assert debiles.escalar(con, hh(12), p) == [tarea["id"]]         # 6 h después
    assert con.execute("SELECT estado FROM tareas_campo").fetchone()[0] == "escalada"


def test_contacto_confirmado_reinicia_el_conteo(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Barrio A")
    _sol(con, 1, zona.id, hh(2))
    p = _p(params)
    assert debiles.detectar(con, hh(7.9), p) == []                  # 5.9 h desde el contacto
    assert debiles.detectar(con, hh(8), p) == [zona.id]


def test_a_solo_cuarentena_sigue_en_silencio(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Barrio A")
    for i in range(20):                                               # ataque de bots
        _sol(con, i, zona.id, hh(5 + i / 60), estado="cuarentena")
    _sol(con, 99, zona.id, hh(5.5), estado="descartada")
    assert debiles.detectar(con, hh(6), _p(params)) == [zona.id]


def test_b_lugar_sin_confirmar_no_es_contacto(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Barrio A")
    _sol(con, 1, zona.id, hh(5), lugar=0)
    assert debiles.detectar(con, hh(6), _p(params)) == [zona.id]


def test_c_validacion_de_agente_es_contacto(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Barrio A")
    _sol(con, 1, zona.id, hh(5), canal="agente", lugar=0, estado="confirmada_regla")
    assert debiles.detectar(con, hh(6), _p(params)) == []
    assert debiles.detectar(con, hh(11), _p(params)) == [zona.id]


def test_d_orden_por_h_af_y_mu(con, params, zonas_sinteticas):
    z = {x.nombre: x for x in zonas_sinteticas}
    for x in zonas_sinteticas:
        con.execute("UPDATE zonas SET afectacion=0 WHERE id=?", (x.id,))
    # Barrio C: más hogares afectados y más silencio (sin contacto desde las 06:00).
    con.execute("UPDATE zonas SET afectacion=0.3 WHERE id=?", (z["Barrio C"].id,))
    con.execute("UPDATE zonas SET afectacion=0.1 WHERE id=?", (z["Barrio B"].id,))
    _sol(con, 1, z["Barrio B"].id, hh(1))                             # B habló a la 1 h
    p = _p(params)
    assert set(debiles.detectar(con, hh(7), p)) == {z["Barrio B"].id, z["Barrio C"].id}
    orden = debiles.tareas_ordenadas(con)
    assert [t["zona_id"] for t in orden] == [z["Barrio C"].id, z["Barrio B"].id]
    zc = censo.zona_por_id(con, z["Barrio C"].id)
    assert orden[0]["prioridad"] == pytest.approx(debiles.prioridad_tarea(zc, 7, p))


def test_e_desde_el_evento_si_es_posterior_a_las_6(con, params, zonas_sinteticas):
    zona = _solo(con, zonas_sinteticas, "Barrio A")
    p = _p(params, evento=hh(4))                                      # sismo a las 10:00
    assert debiles.detectar(con, hh(9.9), p) == []                    # 5.9 h desde el evento
    assert debiles.detectar(con, hh(10), p) == [zona.id]
    # Un evento anterior a las 06:00 cuenta desde las 06:00.
    zb = _solo(con, zonas_sinteticas, "Barrio B")
    p2 = _p(params, evento=EV - timedelta(hours=4))
    assert debiles.detectar(con, hh(5.9), p2) == []
    assert debiles.detectar(con, hh(6), p2) == [zb.id]


def test_sin_hora_de_evento_no_hace_nada(con, params, zonas_sinteticas):
    assert debiles.detectar(con, hh(20), params) == []


def test_prioridad_de_tarea(params):
    from triage.geo import Zona
    z = Zona(id=1, nombre="Z", lat=5.06, lon=-75.5, hogares=1000, afectacion=0.2)
    lam = 200 * params["q"] / 24
    assert debiles.prioridad_tarea(z, 6, params) == pytest.approx(200 * (1 - math.exp(-lam * 6)))
    assert debiles.prioridad_tarea(z, 0, params) == 0
    z.aislada = 1
    assert debiles.prioridad_tarea(z, 6, params) == pytest.approx(400 * (1 - math.exp(-lam * 6)))


def _grafo():
    g = nx.MultiDiGraph()
    for u, v in [(0, 1), (1, 2), (2, 3), (3, 4), (1, 5)]:
        g.add_edge(u, v)
        g.add_edge(v, u)
    return g


def test_grafo_aislado_y_no_aislado():
    g = _grafo()
    assert not debiles.aislada(g, 4, [0], [])
    assert debiles.aislada(g, 4, [0], [(2, 3)])
    assert not debiles.aislada(g, 5, [0], [(2, 3)])
    assert not debiles.aislada(g, 4, [0, 3], [(2, 3)])   # otro acopio sí llega
    assert g.number_of_edges() == 10                     # no modifica el grafo original
    assert not debiles.aislada(None, 4, [0], [])          # sin grafo: False y no falla
    assert not debiles.aislada(g, 99, [0], [])
    assert not debiles.aislada(nx.Graph([(0, 1)]), 1, [0], [(7, 8)])


def test_reabrir_exige_humano_o_agente(con, params, zonas_sinteticas):
    zid = zonas_sinteticas[0].id
    con.execute("UPDATE zonas SET es_debil=1 WHERE id=?", (zid,))
    debiles.crear_tarea(con, zonas_sinteticas[0], hh(6), "prueba", params)
    with pytest.raises(PermissionError):
        debiles.reabrir(con, zid, "regla:v1")
    debiles.reabrir(con, zid, "agente:abc")
    assert censo.zona_por_id(con, zid).es_debil == 0
    assert con.execute("SELECT estado FROM tareas_campo").fetchone()[0] == "cerrada"


def test_aislamiento_duplica_la_prioridad(con, params, zonas_sinteticas):
    zid = zonas_sinteticas[0].id
    assert debiles.actualizar_aislamiento(con, _grafo(), {zid: 4}, [0], [(3, 4)]) == [zid]
    zona = censo.zona_por_id(con, zid)
    tid = debiles.crear_tarea(con, zona, hh(6), "prueba", params, horas=6)
    pr = con.execute("SELECT prioridad FROM tareas_campo WHERE id=?", (tid,)).fetchone()[0]
    con.execute("UPDATE zonas SET aislada=0 WHERE id=?", (zid,))
    assert pr == pytest.approx(2 * debiles.prioridad_tarea(censo.zona_por_id(con, zid), 6, params))
    assert debiles.actualizar_aislamiento(con, None, {zid: 4}, [0], []) == []
