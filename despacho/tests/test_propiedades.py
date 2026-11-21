"""Propiedades del optimizador, con escenarios aleatorios de semilla fija (sin dependencias nuevas).

Cada prueba recorre varias semillas sobre el grafo sintético de conftest.py. Si una semilla
falla, el mensaje dice cuál, para repetir el escenario con `random.Random(semilla)`.

  1. La capacidad de un vehículo nunca se excede.
  2. Un tramo cerrado nunca se usa después de recalcular.
  3. Los puntos críticos se atienden cuando es factible.
  4. Lo que vence primero sale primero (regla `surtir`, primero el lote que vence primero).

Aporta a: criterio 2 (funcionamiento) con evidencia que corre.
"""
import json
import random
from datetime import timedelta

import pytest

from despacho import optimizar, recalcular
from despacho.tests.conftest import AHORA, Mundo, nodo
from despacho.tests.test_despacho import aristas_de, indice_nodos, paradas, plan

SEG = 1


@pytest.fixture
def mundo_vacio(con, grafo):
    """Base vacía (sin acopio, flota ni puntos): cada escenario aleatorio arma lo suyo."""
    return Mundo(con, grafo), con, grafo


SEMILLAS = range(6)
NODOS_PUNTO = [nodo(4, 4), nodo(4, 0), nodo(2, 3), nodo(3, 1), nodo(1, 4), nodo(2, 2), nodo(0, 3), nodo(4, 2)]


def escenario(m: Mundo, rng: random.Random, n_pedidos: int, kg=(5, 70), criticos=()):
    """Acopio, flota aleatoria, puntos (los de `criticos` son críticos) y pedidos de arroz."""
    m.acopio(1, nodo(0, 0))
    for i, (tipo, cap) in enumerate([("camion", rng.choice([100, 150, 300])), ("campero", rng.choice([40, 60, 80])),
                                     ("moto", 20)][: rng.randint(2, 3)], start=1):
        m.vehiculo(i, tipo, cap)
    m.lote(1, kg=50_000)
    for i, n in enumerate(NODOS_PUNTO, start=1):
        m.punto(i, n, critico=int(i in criticos))
    for k in range(1, n_pedidos + 1):
        punto = rng.randint(1, len(NODOS_PUNTO))
        m.pedido(k, punto, rng.randint(*kg), urgencia=3 if punto in criticos else rng.choice([1, 2, 2, 3]))
    m.listo()


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_la_capacidad_de_un_vehiculo_nunca_se_excede(semilla, mundo_vacio):
    m, con, g = mundo_vacio
    rng = random.Random(100 + semilla)
    escenario(m, rng, n_pedidos=rng.randint(4, 12))
    cap = {v["id"]: v["capacidad_kg"] for v in con.execute("SELECT * FROM vehiculos")}
    p1 = optimizar.planificar(con, segundos=SEG, g=g, ahora=AHORA)
    # también después de un recálculo con un cierre
    idx = indice_nodos(g)
    usadas = [a for s in paradas(con, p1) for a in aristas_de(json.loads(s["geometria"]), idx)]
    p2 = None
    if usadas:
        u, v = sorted(usadas[0])
        m.cierre(u=u, v=v)
        con.commit()
        p2 = recalcular.recalcular(con, segundos=SEG, g=g, ahora=AHORA)
    for pid in filter(None, (p1, p2)):
        por_veh: dict[int, float] = {}
        for s in paradas(con, pid):
            por_veh[s["vehiculo_id"]] = por_veh.get(s["vehiculo_id"], 0) + s["kg"]
        for v, kg in por_veh.items():
            assert kg <= cap[v] + 1e-6, f"semilla {semilla}, plan {pid}: vehículo {v} lleva {kg} kg y cabe {cap[v]}"
        for r in plan(con, pid)[1].get("vehiculos", []):
            assert r["kg"] <= r["capacidad_kg"] + 1e-6, f"semilla {semilla}, plan {pid}: resumen excede la capacidad"


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_un_tramo_cerrado_nunca_se_usa_tras_recalcular(semilla, mundo_vacio):
    m, con, g = mundo_vacio
    rng = random.Random(200 + semilla)
    escenario(m, rng, n_pedidos=rng.randint(3, 8), kg=(5, 25))
    p1 = optimizar.planificar(con, segundos=SEG, g=g, ahora=AHORA)
    idx = indice_nodos(g)
    usadas = sorted({a for s in paradas(con, p1) for a in aristas_de(json.loads(s["geometria"]), idx)},
                    key=sorted)
    assert usadas, f"semilla {semilla}: el plan 1 debía usar alguna arista"
    cerradas = [frozenset(a) for a in rng.sample(usadas, min(2, len(usadas)))]      # hasta dos tramos a la vez
    for a in cerradas:
        u, v = sorted(a)
        m.cierre(u=u, v=v)
    con.commit()
    p2 = recalcular.recalcular(con, segundos=SEG, g=g, ahora=AHORA)
    r2 = plan(con, p2)[1]
    # Que no haya desvío posible es un resultado válido; lo que no vale es usar el tramo cerrado.
    for s in paradas(con, p2):
        usadas2 = set(aristas_de(json.loads(s["geometria"]), idx))
        for a in cerradas:
            assert a not in usadas2, f"semilla {semilla}: la parada {s['id']} cruza el tramo cerrado {sorted(a)}"
    for veh in r2.get("vehiculos", []):                                               # y el regreso al acopio
        for a in cerradas:
            assert a not in set(aristas_de(veh["regreso"], idx)), \
                f"semilla {semilla}: el regreso de {veh['nombre']} cruza el tramo cerrado {sorted(a)}"


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_los_criticos_se_atienden_cuando_es_factible(semilla, mundo_vacio):
    """Factible: cada pedido cabe en algún vehículo, la demanda total es menos de la mitad de la flota,
    hay inventario y todo es alcanzable. Entonces cada pedido crítico debe tener parada y llegar a tiempo."""
    m, con, g = mundo_vacio
    rng = random.Random(300 + semilla)
    escenario(m, rng, n_pedidos=rng.randint(4, 9), kg=(5, 20), criticos={1, 3, 5})
    flota = sum(v["capacidad_kg"] for v in con.execute("SELECT * FROM vehiculos"))
    demanda = con.execute("SELECT SUM(kg_estimado) FROM pedidos").fetchone()[0]
    assert demanda <= flota / 2, "el escenario debía ser factible"
    pid = optimizar.planificar(con, segundos=SEG, g=g, ahora=AHORA)
    _, r = plan(con, pid)
    con_parada = {s["pedido_id"] for s in paradas(con, pid)}
    criticos = {r_["id"] for r_ in con.execute(
        "SELECT pe.id FROM pedidos pe JOIN puntos pu ON pu.id = pe.punto_id WHERE pu.critico=1")}
    assert criticos, "el escenario debía tener pedidos críticos"
    assert criticos <= con_parada, f"semilla {semilla}: críticos sin atender {sorted(criticos - con_parada)}"
    assert r["criticos"]["a_tiempo"] == r["criticos"]["paradas"] == len(criticos), \
        f"semilla {semilla}: críticos a tiempo {r['criticos']}"


@pytest.mark.parametrize("semilla", SEMILLAS)
def test_lo_que_vence_primero_sale_primero(semilla):
    """`surtir`: si un lote que vence después ya dio producto, los lotes del mismo producto y acopio que
    vencen antes están agotados. Lotes perecederos con vencimientos lejanos, para que ninguno se descarte."""
    rng = random.Random(400 + semilla)
    lotes = []
    for i in range(1, rng.randint(4, 7) + 1):
        lotes.append({"id": i, "acopio_id": 1, "producto": "leche", "kg": float(rng.randint(10, 60)),
                      "perecedero": 1, "empaque_activo": 0, "vence_en": (AHORA + timedelta(hours=rng.randint(30, 90))).isoformat()})
    pedidos = [{"id": k, "punto_id": 1, "familias": 5, "kg_estimado": float(rng.randint(5, 40)), "urgencia": rng.choice([1, 2, 3]),
                "limite_en": (AHORA + timedelta(hours=10)).isoformat(),
                "productos": json.dumps([{"producto": "leche", "kg": float(rng.randint(5, 40))}])}
               for k in range(1, rng.randint(2, 5) + 1)]
    for p in pedidos:
        p["kg_estimado"] = json.loads(p["productos"])[0]["kg"]
    res = optimizar.surtir(pedidos, lotes, AHORA, {p["id"]: [1] for p in pedidos}, {})
    tomado = {l["id"]: 0.0 for l in lotes}
    for s in res.values():
        for linea in s.lineas:
            tomado[linea["lote_id"]] += linea["kg"]
    por_vence = sorted(lotes, key=lambda l: l["vence_en"])
    for i, tarde in enumerate(por_vence):
        if tomado[tarde["id"]] > 1e-9:
            for antes in por_vence[:i]:
                assert tomado[antes["id"]] >= antes["kg"] - 1e-6, (
                    f"semilla {semilla}: salió del lote {tarde['id']} (vence {tarde['vence_en']}) "
                    f"con el lote {antes['id']} (vence {antes['vence_en']}) sin agotar: {tomado[antes['id']]} de {antes['kg']} kg")


def test_fefo_en_el_plan_completo(mundo, con, grafo, ahora):
    """Mismo criterio de punta a punta: el pedido pequeño toma del lote que vence antes."""
    mundo.lote(2, "leche", kg=100, perecedero=1, vence=ahora + timedelta(hours=40))
    mundo.lote(3, "leche", kg=100, perecedero=1, vence=ahora + timedelta(hours=20))
    mundo.pedido(1, 1, 30, producto="leche")
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    surtido = plan(con, pid)[1]["surtido"]["1"]
    assert {l["lote_id"] for l in surtido} == {3}, f"debía salir del lote que vence primero (3): {surtido}"
