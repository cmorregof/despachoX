"""Pestaña «Informe»: base vacía, base con la semilla (totales contra SQL directo) y perecederos resaltados."""
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from datos import db
from tablero import datos as T

CARPETA = Path(__file__).resolve().parent.parent


def test_base_vacia_no_se_rompe(tmp_path):
    con = db.conectar(tmp_path / "vacia.db")
    inf = T.informe(con)
    r = inf["resumen"]
    assert r["pedidos_atendidos"] == 0 and r["pedidos_pendientes"] == 0
    assert r["kg_despachados"] == 0 and r["kg_inventario_cargado"] == 0 and r["pct_criticos_a_tiempo"] is None
    for k in ("por_producto", "vehiculos", "por_territorio", "bodega", "lotes"):
        assert inf[k] == []
    assert "sin datos todavía" in T.informe_csv(inf).decode("utf-8-sig")


@pytest.fixture
def semilla(tmp_path):
    from despacho import semilla as S
    con = db.conectar(tmp_path / "semilla.db")
    S.cargar(reiniciar=True, con=con)
    # Paquetes de prueba sobre lotes reales: uno entregado, uno en ruta y uno en bodega (no cuenta).
    lotes = [r[0] for r in con.execute("SELECT id FROM lotes ORDER BY id LIMIT 3")]
    pedido = con.execute("SELECT id FROM pedidos ORDER BY id LIMIT 1").fetchone()[0]
    con.executemany("INSERT INTO paquetes(codigo,pedido_id,lote_id,kg,estado) VALUES (?,?,?,?,?)", [
        ("P1", pedido, lotes[0], 12.5, "entregado"), ("P2", pedido, lotes[1], 7.0, "en_ruta"),
        ("P3", pedido, lotes[2], 99.0, "en_bodega")])
    con.commit()
    return con


def test_totales_cuadran_con_sql(semilla):
    con = semilla
    r = T.informe(con)["resumen"]
    assert r["kg_inventario_cargado"] == round(con.execute("SELECT SUM(kg) FROM lotes").fetchone()[0], 1)
    assert r["kg_despachados"] == round(con.execute(
        "SELECT SUM(kg) FROM paquetes WHERE estado IN ('en_ruta','entregado')").fetchone()[0], 1) == 19.5
    assert r["kg_entregados"] == 12.5
    assert r["pedidos_pendientes"] == con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE estado IN ('nuevo','confirmado','asignado') AND duplicado_de IS NULL "
        "AND COALESCE(origen,'mensaje') != 'silencio'").fetchone()[0]
    inf = T.informe(con)
    assert sum(f["kg"] for f in inf["bodega"]) == pytest.approx(con.execute("SELECT SUM(kg) FROM lotes").fetchone()[0])
    assert sum(f["kg_despachado"] for f in inf["por_producto"]) == pytest.approx(19.5)
    assert len(inf["lotes"]) == con.execute("SELECT COUNT(*) FROM lotes").fetchone()[0]


def test_perecederos_resaltados_y_vencimientos(tmp_path):
    con = db.conectar(tmp_path / "p.db")
    ahora = datetime(2026, 11, 21, 8, 0, tzinfo=db.BOGOTA)
    iso = lambda h: (ahora + timedelta(hours=h)).isoformat(timespec="seconds")  # noqa: E731
    con.execute("INSERT INTO acopios(id,nombre,lat,lon) VALUES (1,'<b>Bodega</b>',5.0,-75.5)")
    con.executemany("INSERT INTO lotes(id,acopio_id,producto,kg,perecedero,vence_en) VALUES (?,?,?,?,?,?)", [
        (1, 1, "arroz", 500, 0, None), (2, 1, "leche", 20, 1, iso(6)), (3, 1, "fruta", 30, 1, iso(20)),
        (4, 1, "pan", 5, 1, iso(-1))])
    con.commit()
    inf = T.informe(con, ahora)
    pronto = {l["id"] for l in inf["lotes"] if l["vence_pronto"]}
    assert pronto == {2}                                   # vencido y a 20 h no se resaltan
    assert inf["resumen"]["kg_vencen_12h"] == 20 and inf["resumen"]["kg_vencen_24h"] == 50
    assert [l["id"] for l in inf["lotes"]] == [4, 2, 3, 1]   # por vencimiento; sin fecha al final


def test_pestana_informe_en_la_app():
    fuente = (CARPETA / "app.py").read_text(encoding="utf-8")
    assert '"Informe"' in fuente and '"Descargar informe (CSV)"' in fuente
    assert "Inventario cargado" in fuente and 'SIN_DATOS = "Sin datos todavía"' in fuente
    # Territorio e Informe están dentro del fragmento que se refresca cada 5 s.
    mesa = fuente[fuente.index("@st.fragment(run_every=SEGUNDOS_REFRESCO)"):]
    assert "detalle_territorio(con)" in mesa and "detalle_informe(con)" in mesa
    assert "SEGUNDOS_REFRESCO = 5" in fuente
