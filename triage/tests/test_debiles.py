import math
from datetime import timedelta

import networkx as nx
import pytest

from triage import censo, debiles
from triage.entrada_datos import a_iso


def test_exp_mu_contra_alpha():
    assert debiles.es_silenciosa(5.0, 0.01)             # exp(-5) = 0.0067
    assert not debiles.es_silenciosa(4.0, 0.01)         # exp(-4) = 0.018
    assert debiles.es_silenciosa(-math.log(0.01) + 1e-6, 0.01)
    assert not debiles.es_silenciosa(float("nan"), 0.01)
    assert not debiles.es_silenciosa(None, 0.01)


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


def _params_evento(params, hora_evento, **extra):
    return dict(params, hora_evento=a_iso(hora_evento), **extra)


def test_detecta_zona_silenciosa_y_escala(con, params, zonas_sinteticas, hora):
    z = {x.nombre: x for x in zonas_sinteticas}
    # Albergue: H_af = 100 → lambda = 0.21/h. Lo subimos a 2/h con lambda_h para la prueba.
    con.execute("UPDATE zonas SET lambda_h=2.0 WHERE id=?", (z["Albergue Coliseo"].id,))
    con.execute("INSERT INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, zona_id) "
                "VALUES (?,?,?,?)", (a_iso(hora(1)), "x", "r", z["Barrio A"].id))
    p = _params_evento(params, hora(0))
    assert debiles.detectar(con, hora(2), p) == []                # menos de 3 h
    nuevas = debiles.detectar(con, hora(3), p)
    assert nuevas == [z["Albergue Coliseo"].id]                   # 2/h × 3 h = 6 → exp(-6) < 0.01
    tarea = con.execute("SELECT * FROM tareas_campo").fetchone()
    assert tarea["estado"] == "abierta" and tarea["zona_id"] == z["Albergue Coliseo"].id
    zona = censo.zona_por_id(con, z["Albergue Coliseo"].id)
    assert zona.es_debil == 1
    assert tarea["prioridad"] == pytest.approx(censo.hogares_afectados(zona, p))
    assert debiles.detectar(con, hora(4), p) == []                # no duplica
    assert debiles.escalar(con, hora(8), p) == []                 # 5 h
    assert debiles.escalar(con, hora(9.1), p) == [tarea["id"]]    # más de 6 h
    assert con.execute("SELECT estado FROM tareas_campo").fetchone()[0] == "escalada"
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='escalar_tarea'").fetchone()[0] == 1


def test_sin_hora_de_evento_no_hace_nada(con, params, zonas_sinteticas, hora):
    assert debiles.detectar(con, hora(10), params) == []


def test_reabrir_exige_humano_o_agente(con, params, zonas_sinteticas, hora):
    zid = zonas_sinteticas[0].id
    con.execute("UPDATE zonas SET es_debil=1 WHERE id=?", (zid,))
    debiles.crear_tarea(con, zonas_sinteticas[0], hora(), "prueba", params)
    with pytest.raises(PermissionError):
        debiles.reabrir(con, zid, "regla:v1")
    debiles.reabrir(con, zid, "agente:abc")
    assert censo.zona_por_id(con, zid).es_debil == 0
    assert con.execute("SELECT estado FROM tareas_campo").fetchone()[0] == "cerrada"


def test_prioridad_de_tarea_con_aislamiento(con, params, zonas_sinteticas, hora):
    g = _grafo()
    zid = zonas_sinteticas[0].id
    assert debiles.actualizar_aislamiento(con, g, {zid: 4}, [0], [(3, 4)]) == [zid]
    zona = censo.zona_por_id(con, zid)
    tid = debiles.crear_tarea(con, zona, hora(), "prueba", params)
    pr = con.execute("SELECT prioridad FROM tareas_campo WHERE id=?", (tid,)).fetchone()[0]
    assert pr == pytest.approx(2 * censo.hogares_afectados(zona, params))
    assert debiles.actualizar_aislamiento(con, None, {zid: 4}, [0], []) == []
