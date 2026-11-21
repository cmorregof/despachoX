"""El gancho DESPACHOX_AGRUPAR en `planificar`: apagado, todo como hoy; encendido, un pedido por grupo."""
import json

from despacho import optimizar
from despacho.tests.conftest import nodo


def _dos_del_mismo_punto(mundo):
    mundo.pedido(1, 1, 30)
    mundo.pedido(2, 1, 25, urgencia=3)
    mundo.pedido(3, 2, 20)
    mundo.listo()


def _plan(con, plan_id):
    fila = con.execute("SELECT resumen FROM planes WHERE id=?", (plan_id,)).fetchone()
    paradas = [dict(r) for r in con.execute("SELECT * FROM paradas WHERE plan_id=? ORDER BY vehiculo_id, orden",
                                             (plan_id,))]
    return json.loads(fila["resumen"]), paradas


def test_apagado_una_parada_por_pedido(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.delenv("DESPACHOX_AGRUPAR", raising=False)
    _dos_del_mismo_punto(mundo)
    resumen, paradas = _plan(con, optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora))
    assert sorted(p["pedido_id"] for p in paradas) == [1, 2, 3]
    assert resumen["grupos"] == {} and resumen["supuestos"]["agrupar"] is False
    assert not any("grupos:" in a for a in resumen["avisos"])


def test_encendido_un_pedido_por_grupo(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    _dos_del_mismo_punto(mundo)
    resumen, paradas = _plan(con, optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora))
    assert sorted(p["pedido_id"] for p in paradas) == [1, 3]           # 1 es la madre del grupo {1, 2}
    grupo = next(p for p in paradas if p["pedido_id"] == 1)
    assert grupo["kg"] == 55.0                                          # 30 + 25, sumados por código
    assert resumen["grupos"] == {"1": [1, 2], "3": [3]}             # un pedido solo también es un grupo
    assert resumen["pedidos_considerados"] == 2 and resumen["pedidos_atendidos"] == 2
    assert resumen["supuestos"]["agrupar"] is True
    assert any("agrupados en 2 grupo(s)" in a for a in resumen["avisos"])
    assert len(resumen["grupos_detalle"]) == 2


def test_aprobar_asigna_a_todos_los_miembros(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    _dos_del_mismo_punto(mundo)
    plan_id = optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora)
    assert optimizar.aprobar(con, plan_id)
    estados = {r["id"]: r["estado"] for r in con.execute("SELECT id, estado FROM pedidos")}
    assert estados == {1: "asignado", 2: "asignado", 3: "asignado"}


def test_argumento_manda_sobre_la_variable(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    _dos_del_mismo_punto(mundo)
    _, paradas = _plan(con, optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora, agrupar=False))
    assert sorted(p["pedido_id"] for p in paradas) == [1, 2, 3]


def test_silencio_no_se_agrupa(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    _dos_del_mismo_punto(mundo)
    con.execute("INSERT INTO pedidos(id,creado_en,punto_id,urgencia,estado,origen) VALUES (9,?,1,3,'confirmado','silencio')",
                (ahora.isoformat(timespec='seconds'),))
    con.commit()
    resumen, paradas = _plan(con, optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora))
    assert [v["pedido_id"] for v in resumen["verificar"]] == [9]
    assert 9 not in {x for ids in resumen["grupos"].values() for x in ids}
    assert sorted(p["pedido_id"] for p in paradas) == [1, 3]
