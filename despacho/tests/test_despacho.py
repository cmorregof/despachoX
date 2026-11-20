"""Pruebas del módulo despacho/ sin red ni caché: grafo sintético y base temporal."""
import json
from datetime import timedelta

from despacho import matriz, optimizar, recalcular
from despacho.tests.conftest import AISLADO, PUENTE, coords, nodo

SEG = 1


def plan(con, plan_id):
    p = con.execute("SELECT * FROM planes WHERE id=?", (plan_id,)).fetchone()
    return p, json.loads(p["resumen"])


def paradas(con, plan_id):
    return [dict(r) for r in con.execute("SELECT * FROM paradas WHERE plan_id=? ORDER BY vehiculo_id, orden",
                                         (plan_id,))]


def aristas_de(geom, indice):
    """Pares de nodos (sin orden) recorridos por una geometría [[lat,lon],...]."""
    ids = [indice[(round(a, 6), round(b, 6))] for a, b in geom]
    return [frozenset(par) for par in zip(ids[:-1], ids[1:]) if par[0] != par[1]]


def indice_nodos(g):
    return {(round(d["y"], 6), round(d["x"], 6)): n for n, d in g.nodes(data=True)}


def test_plan_respeta_capacidades_y_deja_sin_atender(mundo, con, grafo, ahora):
    for i in range(1, 7):   # 6 x 40 kg = 240 kg frente a 150 kg de flota
        mundo.pedido(i, (i - 1) % 4 + 1, 40)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    p, r = plan(con, pid)
    assert p["estado"] == "propuesto"
    assert not r["vacio"]
    assert r["sin_atender"], "con demanda mayor que la flota algo debe quedar sin atender"
    cap = {v["id"]: v["capacidad_kg"] for v in con.execute("SELECT * FROM vehiculos")}
    por_veh = {}
    for s in paradas(con, pid):
        por_veh[s["vehiculo_id"]] = por_veh.get(s["vehiculo_id"], 0) + s["kg"]
    assert por_veh
    for v, kg in por_veh.items():
        assert kg <= cap[v] + 1e-9
    assert r["pedidos_atendidos"] + len(r["sin_atender"]) == 6


def test_cierre_en_arista_usada_cambia_la_ruta(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 40)
    mundo.pedido(2, 3, 30)
    mundo.listo()
    p1 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    ps = paradas(con, p1)
    assert ps
    idx = indice_nodos(grafo)
    usadas = [a for s in ps for a in aristas_de(json.loads(s["geometria"]), idx)]
    assert usadas
    u, v = sorted(usadas[0])
    mundo.cierre(u=u, v=v)
    con.commit()
    p2 = recalcular.recalcular(con, segundos=SEG, g=grafo, ahora=ahora)
    assert plan(con, p1)[0]["estado"] == "reemplazado"
    nuevo, r2 = plan(con, p2)
    assert nuevo["estado"] == "propuesto"
    assert paradas(con, p2), "debía existir desvío y el plan seguir atendiendo"
    assert r2["cierres_aplicados"]
    cerrada = frozenset((u, v))
    for s in paradas(con, p2):
        assert cerrada not in aristas_de(json.loads(s["geometria"]), idx)


def test_punto_aislado_no_rompe_nada(mundo, con, grafo, ahora):
    mundo.punto(9, AISLADO)
    mundo.pedido(1, 9, 20)
    mundo.pedido(2, 1, 20)
    mundo.pedido(3, 3, 20)
    mundo.cierre(u=PUENTE[0], v=PUENTE[1])
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert pid > 0
    _, r = plan(con, pid)
    assert [x["pedido_id"] for x in r["sin_atender"]] == [1]
    assert r["pedidos_atendidos"] == 2


def test_plan_nace_propuesto_y_aprobar_asigna(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert plan(con, pid)[0]["estado"] == "propuesto"
    assert con.execute("SELECT estado FROM pedidos WHERE id=1").fetchone()[0] == "confirmado"
    assert optimizar.aprobar(con, pid, "despachador de prueba")
    p, _ = plan(con, pid)
    assert p["estado"] == "aprobado" and p["aprobado_por"]
    assert con.execute("SELECT estado FROM pedidos WHERE id=1").fetchone()[0] == "asignado"


def test_sin_pedidos_confirmados_plan_vacio(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20, estado="nuevo")
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    p, r = plan(con, pid)
    assert p["estado"] == "propuesto"
    assert r["vacio"] and r["motivo_vacio"]
    assert paradas(con, pid) == []


def test_cierre_solo_para_camion_no_afecta_al_campero(mundo, grafo):
    a, b = coords(grafo, nodo(0, 0)), coords(grafo, nodo(0, 1))
    lugares = [matriz.Lugar("a", *a), matriz.Lugar("b", *b)]
    cierre = [{"estado": "confirmado", "osm_u": nodo(0, 0), "osm_v": nodo(0, 1),
               "tipos_bloqueados": '["camion"]'}]
    base = matriz.calcular(grafo, lugares, None, ("camion", "campero"))
    con_c = matriz.calcular(grafo, lugares, cierre, ("camion", "campero"))
    assert con_c["campero"].tiempo("a", "b") == base["campero"].tiempo("a", "b")
    assert con_c["camion"].tiempo("a", "b") > base["camion"].tiempo("a", "b")   # el camión da el rodeo
    assert con_c["camion"].tiempo("a", "b") < matriz.INALCANZABLE


def test_cierre_con_lat_lon_queda_ubicado_tras_recalcular(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20)
    lat, lon = coords(grafo, nodo(2, 2))
    cid = mundo.cierre(lat=lat + 0.0003, lon=lon + 0.0001)
    mundo.listo()
    recalcular.recalcular(con, cierre=cid, segundos=SEG, g=grafo, ahora=ahora)
    c = con.execute("SELECT * FROM cierres WHERE id=?", (cid,)).fetchone()
    assert c["osm_u"] is not None and c["osm_v"] is not None
    assert grafo.has_edge(c["osm_u"], c["osm_v"])


def test_perecedero_que_vence_antes_de_llegar_no_se_despacha(mundo, con, grafo, ahora):
    # Vence en 10 minutos: el margen de 30 min lo deja fuera de cualquier entrega.
    mundo.lote(2, producto="leche", kg=100, perecedero=1, vence=ahora + timedelta(minutes=10))
    mundo.pedido(1, 1, 20, producto="leche")
    mundo.pedido(2, 3, 20, producto="arroz")
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    _, r = plan(con, pid)
    surtido = r.get("surtido", {})
    lotes_usados = [l["lote_id"] for lineas in surtido.values() for l in lineas]
    assert 2 not in lotes_usados
    assert 1 in [x["pedido_id"] for x in r["sin_atender"]]
    assert r["pedidos_atendidos"] == 1


def test_producto_sin_kilos_no_se_vuelve_mercado_generico():
    p = {"productos": '[{"producto": "leche"}, {"producto": "arroz", "kg": 20}]', "kg_estimado": 50, "familias": 5}
    assert optimizar._demanda(p) == [{"producto": "arroz", "kg": 20.0}, {"producto": "leche", "kg": 30.0}]
    p = {"productos": '["leche", "pan"]', "kg_estimado": None, "familias": 4}
    assert optimizar._demanda(p) == [{"producto": "leche", "kg": 20.0}, {"producto": "pan", "kg": 20.0}]
    p = {"productos": None, "kg_estimado": None, "familias": 3}
    assert optimizar._demanda(p) == [{"producto": None, "kg": 30.0}]


def test_cierre_con_ubicacion_sin_confirmar_no_entra_al_plan(mundo, con, grafo, ahora):
    from datos import db
    from despacho import cierres
    con.execute("INSERT INTO cierres(id, creado_en, lugar, lat, lon, estado) VALUES (50, ?, 'un sitio', 5.062, -75.498, 'confirmado')",
                (db.ahora(),))
    con.execute("INSERT INTO ubicaciones(creado_en, tabla, fila_id, texto, estado) VALUES (?, 'cierres', 50, 'un sitio', 'propuesta')",
                (db.ahora(),))
    con.commit()
    avisos = cierres.ubicar(con, grafo)
    assert any("cierre 50" in a and "sin confirmar" in a for a in avisos)
    assert con.execute("SELECT osm_u FROM cierres WHERE id=50").fetchone()[0] is None
    con.execute("UPDATE ubicaciones SET estado='confirmada' WHERE fila_id=50")
    con.commit()
    cierres.ubicar(con, grafo)
    assert con.execute("SELECT osm_u FROM cierres WHERE id=50").fetchone()[0] is not None
