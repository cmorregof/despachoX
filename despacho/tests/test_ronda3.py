"""Ronda 3 de B-despacho: empaque activo, trazabilidad, cantidad supuesta y plan vigente."""
import json
from datetime import timedelta

import pytest

from despacho import optimizar, paquetes, recalcular
from despacho.tests.conftest import AHORA, iso

SEG = 1


def plan(con, plan_id):
    p = con.execute("SELECT * FROM planes WHERE id=?", (plan_id,)).fetchone()
    return p, json.loads(p["resumen"])


def estado_pedido(con, pid):
    return con.execute("SELECT estado FROM pedidos WHERE id=?", (pid,)).fetchone()[0]


def pedido_sin_cantidad(con, id, punto_id, urgencia=3):
    """Como «6 bebés sin leche en La Enea»: sin familias, sin kilos y sin productos."""
    con.execute("INSERT INTO pedidos(id,creado_en,punto_id,urgencia,estado,texto_original) "
                "VALUES (?,?,?,?, 'confirmado', 'hay bebes sin leche')",
                (id, iso(AHORA - timedelta(minutes=30)), punto_id, urgencia))


# ---------- 1. empaque activo ----------
# Desde la noche del viernes el factor (1,2) solo cuenta en fruta perecedera de un acopio con frío.

def _pedido(producto="fruta", id=1):
    return {"id": id, "urgencia": 2, "limite_en": None, "kg_estimado": 20, "familias": 2,
            "productos": json.dumps([{"producto": producto, "kg": 20}])}


@pytest.mark.parametrize("empaque, surtido", [(0, False), (1, True)])
def test_empaque_activo_cambia_que_se_puede_surtir(monkeypatch, empaque, surtido):
    monkeypatch.setattr(optimizar, "FACTOR_EMPAQUE_ACTIVO", 1.2)
    # Vence en 55 min; llegar toma 30 min y el margen es 30 min. Sin empaque no alcanza (60 > 55);
    # con empaque le quedan 55 × 1,2 = 66 min y sí alcanza.
    lote = {"id": 7, "acopio_id": 1, "producto": "fruta", "kg": 100, "perecedero": 1,
            "vence_en": iso(AHORA + timedelta(minutes=55)), "empaque_activo": empaque}
    r = optimizar.surtir([_pedido()], [lote], AHORA, {1: [1]}, {(1, 1): 1800}, frios={1})
    assert (r[1].kg == 20) is surtido
    if surtido:
        assert r[1].vence == AHORA + timedelta(minutes=66)


def test_empaque_no_toca_lotes_no_perecederos_ni_vencidos(monkeypatch):
    monkeypatch.setattr(optimizar, "FACTOR_EMPAQUE_ACTIVO", 1.2)
    base = {"producto": "fruta", "perecedero": 1, "empaque_activo": 1}
    vencido = AHORA - timedelta(hours=1)
    assert optimizar.vence_efectivo({**base, "vence_en": iso(vencido)}, AHORA, frio=True) == vencido
    seco = {"producto": "fruta", "perecedero": 0, "empaque_activo": 1, "vence_en": iso(AHORA + timedelta(hours=2))}
    assert optimizar.vence_efectivo(seco, AHORA, frio=True) == AHORA + timedelta(hours=2)
    assert optimizar.vence_efectivo({"vence_en": None, **base}, AHORA, frio=True) is None


def test_empaque_activo_en_el_plan_y_en_supuestos(mundo, con, grafo, ahora, monkeypatch):
    monkeypatch.setattr(optimizar, "FACTOR_EMPAQUE_ACTIVO", 1.2)
    con.execute("UPDATE acopios SET tiene_frio=1 WHERE id=1")
    # Vence en 31 min: sin empaque nada llega con 30 min de margen; con empaque (37,2 min) sí.
    mundo.lote(2, producto="fruta", kg=50, perecedero=1, vence=ahora + timedelta(minutes=31))
    mundo.lote(3, producto="fruta", kg=50, perecedero=1, vence=ahora + timedelta(minutes=31), acopio_id=1,
               empaque=1)
    mundo.pedido(1, 3, 20, producto="fruta")
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    _, r = plan(con, pid)
    assert r["pedidos_atendidos"] == 1
    assert [l["lote_id"] for l in r["surtido"]["1"]] == [3]
    assert r["supuestos"]["factor_empaque_activo"] == optimizar.FACTOR_EMPAQUE_ACTIVO
    assert "ICTA" in r["supuestos"]["factor_empaque_activo_nota"]
    assert "37476" in r["supuestos"]["factor_empaque_activo_nota"]
    assert "fruta" in r["supuestos"]["factor_empaque_activo_aplica_a"]


# ---------- 3. cantidad supuesta ----------

def test_cantidad_supuesta_por_que():
    notas = []
    optimizar._demanda({"productos": None, "kg_estimado": None, "familias": None}, notas)
    assert notas and "1 familia" in notas[0]
    notas = []
    optimizar._demanda({"productos": None, "kg_estimado": None, "familias": 4}, notas)
    assert notas == ["kilos estimados con 10 kg por familia"]
    notas = []
    optimizar._demanda({"productos": '["leche"]', "kg_estimado": 30, "familias": 3}, notas)
    assert notas == ["kilos repartidos entre productos que no los traían"]
    for p in ({"productos": '[{"producto": "arroz", "kg": 20}]', "kg_estimado": None, "familias": None},
              {"productos": None, "kg_estimado": 25, "familias": None}):
        notas = []
        optimizar._demanda(p, notas)
        assert notas == [], p


def test_pedido_sin_cantidad_sale_marcado(mundo, con, grafo, ahora):
    pedido_sin_cantidad(con, 1, 1)
    mundo.pedido(2, 3, 20)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    _, r = plan(con, pid)
    assert r["pedidos_atendidos"] == 2
    assert list(r["cantidad_supuesta"]) == ["1"]
    assert any("pedido 1" in a and "cantidad supuesta" in a for a in r["avisos"])
    resultado = optimizar._resolver(optimizar._leer(con, False), grafo, ahora, SEG, {})
    marca = {p["pedido_id"]: p["cantidad_supuesta"] for p in resultado["paradas"]}
    assert marca[1] and marca[2] is None


# ---------- 2. trazabilidad ----------

def test_aprobar_crea_paquetes_y_entregar_los_cierra(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20)
    mundo.pedido(2, 3, 30)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert con.execute("SELECT COUNT(*) FROM paquetes").fetchone()[0] == 0   # proponer no crea nada
    assert optimizar.aprobar(con, pid, "despachador de prueba")
    filas = paquetes.listar(con)
    assert len(filas) == 2 and len({f["codigo"] for f in filas}) == 2
    assert all(f["estado"] == "en_ruta" and f["lote_id"] == 1 for f in filas)
    assert {f["pedido_id"]: f["kg"] for f in filas} == {1: 20, 2: 30}

    codigo = next(f["codigo"] for f in filas if f["pedido_id"] == 1)
    assert paquetes.entregar(con, codigo.lower().replace("-", ""), "conductor de prueba")
    assert estado_pedido(con, 1) == "entregado" and estado_pedido(con, 2) == "asignado"
    pq = con.execute("SELECT * FROM paquetes WHERE codigo=?", (codigo,)).fetchone()
    assert pq["estado"] == "entregado" and pq["entregado_en"]
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='entregar paquete' AND detalle LIKE ?",
                       (f"{codigo}%",)).fetchone()[0] == 1
    assert not paquetes.entregar(con, codigo)          # ya entregado
    assert not paquetes.entregar(con, "DX-0000")       # no existe


def test_linea_de_ordenes_entregar(mundo, con, grafo, ahora, monkeypatch, capsys):
    mundo.pedido(1, 1, 20)
    mundo.listo()
    assert optimizar.aprobar(con, optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora))
    codigo = paquetes.listar(con)[0]["codigo"]
    ruta = con.execute("PRAGMA database_list").fetchone()["file"]
    from datos import db
    monkeypatch.setattr(db, "RUTA_DB", ruta)
    monkeypatch.setattr(db.conectar, "__defaults__", (ruta,))
    assert paquetes.main(["--entregar", codigo]) == 0
    assert estado_pedido(con, 1) == "entregado"
    assert paquetes.main(["--entregar", codigo]) == 1


# ---------- 4. plan vigente ----------

def test_rechazar_un_recalculo_deja_vigente_el_aprobado(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20)
    mundo.pedido(2, 3, 20)
    mundo.listo()
    p1 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert optimizar.aprobar(con, p1)
    codigos = {f["pedido_id"]: f["codigo"] for f in paquetes.listar(con)}
    mundo.pedido(3, 4, 20)
    mundo.listo()
    p2 = recalcular.recalcular(con, segundos=SEG, g=grafo, ahora=ahora, motivo="pedido nuevo")
    assert plan(con, p1)[0]["estado"] == "aprobado"            # proponer ya no lo reemplaza
    nuevo, r2 = plan(con, p2)
    assert nuevo["estado"] == "propuesto" and r2["reemplaza_a"] == [p1]
    con.execute("UPDATE planes SET estado='rechazado' WHERE id=?", (p2,))   # como lo hace el tablero
    con.commit()
    assert plan(con, p1)[0]["estado"] == "aprobado"

    p3 = recalcular.recalcular(con, segundos=SEG, g=grafo, ahora=ahora, motivo="pedido nuevo")
    assert plan(con, p1)[0]["estado"] == "aprobado"
    assert optimizar.aprobar(con, p3)
    assert plan(con, p1)[0]["estado"] == "reemplazado"
    assert plan(con, p3)[0]["estado"] == "aprobado"
    nuevos = {f["pedido_id"]: f["codigo"] for f in paquetes.listar(con)}
    assert set(nuevos) == {1, 2, 3}
    assert all(nuevos[k] == codigos[k] for k in codigos)      # el paquete conserva su código
    assert con.execute("SELECT COUNT(*) FROM paquetes").fetchone()[0] == 3


def test_pedido_que_sale_del_plan_aprobado_vuelve_a_bodega(mundo, con, grafo, ahora):
    mundo.pedido(1, 1, 20)
    mundo.listo()
    p1 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert optimizar.aprobar(con, p1)
    mundo.pedido(2, 3, 20)
    mundo.listo()
    p2 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)   # sin recálculo: solo el pedido 2
    assert optimizar.aprobar(con, p2)
    assert estado_pedido(con, 1) == "confirmado"
    assert con.execute("SELECT estado FROM paquetes WHERE pedido_id=1").fetchone()[0] == "en_bodega"
    assert estado_pedido(con, 2) == "asignado"
