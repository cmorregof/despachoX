"""Revisión QA de la noche (rama qa-noche).

1. Una alerta por silencio, tal como la crea `entrada.silencio.revisar`, nunca se rutea ni se surte:
   sin decisión del despachador el plan ni la ve; confirmada en el tablero queda en `verificar`; al
   aprobar no recibe paquete, no pasa a `asignado` y la hoja impresa no la lleva.
2. El código del paquete: 25 signos, 4 posiciones, generado con `secrets`, único y de un solo uso.
Detalle en docs/QA_NOCHE.md.
"""
import json
import math
import re

from despacho.tests.conftest import nodo


def _resumen(con, plan_id):
    return json.loads(con.execute("SELECT resumen FROM planes WHERE id=?", (plan_id,)).fetchone()[0])


def _paradas(con, plan_id):
    return [r[0] for r in con.execute("SELECT pedido_id FROM paradas WHERE plan_id=? ORDER BY id", (plan_id,))]


def test_alerta_de_silencio_de_punta_a_punta_nunca_sale_con_comida(mundo, con, grafo, ahora):
    from despacho import hoja, optimizar, territorio
    from entrada import silencio
    from tablero import datos as T

    mundo.punto(5, nodo(1, 2), critico=1)            # albergue que no ha escrito en toda la jornada
    mundo.pedido(2, 3, 20)                            # un pedido real, confirmado
    mundo.listo()
    hecho = silencio.revisar(con, ahora=ahora, umbral_h=2)     # 10:00; la jornada empezó a las 06:00
    assert hecho["creadas"] == [5]
    alerta = dict(con.execute("SELECT * FROM pedidos WHERE origen='silencio'").fetchone())
    assert alerta["estado"] == "nuevo" and alerta["urgencia"] < 3
    assert alerta["familias"] is None and alerta["kg_estimado"] is None and alerta["productos"] is None

    # Sin decisión del despachador, el optimizador ni la ve.
    p1 = optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora)
    r1 = _resumen(con, p1)
    assert _paradas(con, p1) == [2] and r1["verificar"] == [] and str(alerta["id"]) not in r1["surtido"]

    # El despachador la confirma en el tablero: sigue sin ruta ni comida, y queda para verificar.
    assert T.cambiar_estado(con, "pedidos", alerta["id"], "confirmado", "despachador de prueba")
    p2 = optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora)
    r2 = _resumen(con, p2)
    assert _paradas(con, p2) == [2]
    assert [v["pedido_id"] for v in r2["verificar"]] == [alerta["id"]]
    assert str(alerta["id"]) not in r2["surtido"] and r2["faltantes"] == []

    # Aprobar no le crea paquete ni la asigna, y la hoja de ruta impresa no la lleva.
    assert optimizar.aprobar(con, p2, "despachador de prueba")
    assert con.execute("SELECT COUNT(*) FROM paquetes WHERE pedido_id=?", (alerta["id"],)).fetchone()[0] == 0
    assert con.execute("SELECT estado FROM pedidos WHERE id=?", (alerta["id"],)).fetchone()[0] == "confirmado"
    impresas = [pa["pedido_id"] for v in hoja._leer(con, p2)["vehiculos"] for pa in v["paradas"]]
    assert impresas == [2]

    # Y no cuenta como pedido en la vista por territorio.
    assert sum(f["pedidos"] for f in territorio.resumen(con, ahora=ahora)) == 1


def test_codigo_de_paquete_entropia_unicidad_y_un_solo_uso(mundo, con, grafo, ahora):
    from despacho import optimizar, paquetes

    assert len(set(paquetes.ALFABETO)) == len(paquetes.ALFABETO) == 25
    assert round(4 * math.log2(len(paquetes.ALFABETO)), 2) == 18.58       # 390.625 códigos posibles
    for i, punto in enumerate((1, 2, 3, 4), start=1):
        mundo.pedido(i, punto, 10)
    mundo.listo()
    plan = optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora)
    assert optimizar.aprobar(con, plan)
    codigos = [r[0] for r in con.execute("SELECT codigo FROM paquetes")]
    assert codigos and len(set(codigos)) == len(codigos)
    assert all(re.fullmatch(f"DX-[{paquetes.ALFABETO}]{{4}}", c) for c in codigos)
    assert paquetes.entregar(con, codigos[0], "conductor de prueba")
    assert not paquetes.entregar(con, codigos[0], "conductor de prueba")     # no se reutiliza
    assert not paquetes.entregar(con, "DX-0000", "conductor de prueba")      # 0 no está en el alfabeto
