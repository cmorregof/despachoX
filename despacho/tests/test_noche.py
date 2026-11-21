"""Pendientes de la noche del viernes: factor crítico 3, kilos por ración y alertas por silencio."""
import json
import os
from datetime import timedelta

from despacho import optimizar, paquetes
from despacho.tests.conftest import AHORA, iso

SEG = 1


def plan(con, plan_id):
    p = con.execute("SELECT * FROM planes WHERE id=?", (plan_id,)).fetchone()
    return p, json.loads(p["resumen"])


def test_factor_critico_por_defecto_es_3():
    esperado = int(os.environ.get("DESPACHOX_FACTOR_CRITICO") or 3)
    assert optimizar.FACTOR_CRITICO == esperado


def test_kilos_por_racion_cuentan_como_cantidad_supuesta():
    # Lo que deja el bot para «6 bebés sin leche»: kilos puestos por la mesa con la clave `supuesto`.
    p = {"productos": json.dumps([{"producto": "leche", "kg": 12, "supuesto": "2 kg por familia"}]),
         "kg_estimado": 12, "familias": 6}
    notas = []
    assert optimizar._demanda(p, notas) == [{"producto": "leche", "kg": 12.0}]
    assert notas == ["kilos por ración (leche: 2 kg por familia)"]
    # Mezcla: arroz dicho por quien pidió, leche por ración, pan sin kilos.
    p = {"productos": json.dumps([{"producto": "arroz", "kg": 20}, {"producto": "leche", "kg": 12,
                                  "supuesto": "2 kg por familia"}, {"producto": "pan"}]),
         "kg_estimado": 40, "familias": 6}
    notas = []
    optimizar._demanda(p, notas)
    assert notas[0].startswith("kilos por ración") and "kilos repartidos" in notas[-1]
    # Todo dicho por quien pidió: nada supuesto.
    notas = []
    optimizar._demanda({"productos": '[{"producto": "arroz", "kg": 20}]', "kg_estimado": 20,
                        "familias": 2}, notas)
    assert notas == []


def _alerta(con, id, punto_id):
    con.execute("INSERT INTO pedidos(id,creado_en,punto_id,urgencia,estado,origen,texto_original) "
                "VALUES (?,?,?,3,'confirmado','silencio','sin contacto en 6 horas')",
                (id, iso(AHORA - timedelta(hours=1)), punto_id))


def test_alerta_por_silencio_confirmada_es_visita_sin_carga(mundo, con, grafo, ahora):
    con.execute("UPDATE lotes SET kg=40 WHERE id=1")
    con.execute("UPDATE puntos SET critico=1 WHERE id=2")
    _alerta(con, 1, 2)
    mundo.pedido(2, 3, 30)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    _, r = plan(con, pid)
    paradas = {x["pedido_id"]: dict(x) for x in con.execute("SELECT * FROM paradas WHERE plan_id=?", (pid,))}
    assert set(paradas) == {1, 2}
    assert paradas[1]["kg"] == 0                        # no sale comida a una verificación
    assert r["surtido"]["1"] == [] and r["visitas"] == [1]
    assert r["kg_planeados"] == 30                      # el arroz no se gastó en la visita
    assert "1" not in r["cantidad_supuesta"]
    assert any("pedido 1" in a and "verificación" in a for a in r["avisos"])
    assert r["criticos"]["paradas"] == 0                # una visita no cuenta como entrega a un crítico
    assert optimizar.aprobar(con, pid)
    assert [f["pedido_id"] for f in paquetes.listar(con)] == [2]   # la visita no lleva paquete


def test_sin_origen_el_pedido_es_normal():
    assert not optimizar.es_visita({"id": 1})
    assert not optimizar.es_visita({"id": 1, "origen": "mensaje"})
    assert optimizar.es_visita({"id": 1, "origen": "silencio"})
