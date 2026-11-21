"""Alertas por silencio (origen='silencio') en «Por revisar»: verificar o descartar. Base temporal."""
from pathlib import Path

import pytest

from datos import db
from tablero import datos as T

CARPETA = Path(__file__).resolve().parent.parent


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "t.db")
    c.executemany("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (?,?,?,?,?,?)", [
        (1, "Albergue A", "A", 5.07, -75.52, 1), (2, "Salón B", "B", 5.06, -75.51, 0)])
    c.executemany(
        "INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,urgencia,estado,texto_original,origen) "
        "VALUES (?,?,?,?,?,?,?,?,?)", [
            (1, "2026-11-21T08:00:00-05:00", 1, None, None, 2, "nuevo",
             "Sin contacto hace 7 h. Visita de verificación.", "silencio"),
            (2, "2026-11-21T08:00:00-05:00", 2, 4, 40, 2, "nuevo", "necesitamos arroz", "mensaje"),
            (3, "2026-11-21T08:00:00-05:00", 2, None, None, 2, "descartado", "Sin contacto hace 9 h.",
             "silencio")])
    c.commit()
    return c


def _bitacora(con):
    return [dict(r) for r in con.execute("SELECT quien, accion, detalle FROM bitacora ORDER BY id")]


def test_las_alertas_van_aparte_de_los_pedidos(con):
    r = T.por_revisar(con)
    assert [d["id"] for d in r["silencio"]] == [1]
    assert [d["id"] for d in r["pedidos"]] == [2]
    assert r["silencio"][0]["punto"] == "Albergue A" and r["silencio"][0]["critico"] == 1


def test_mandar_a_verificar(con):
    assert T.decidir_silencio(con, 1, "verificar", "Ana") is True
    f = con.execute("SELECT estado, familias, kg_estimado FROM pedidos WHERE id=1").fetchone()
    assert f["estado"] == "confirmado"
    assert f["familias"] is None and f["kg_estimado"] is None          # no se inventan
    assert _bitacora(con)[-1] == {"quien": "Ana", "accion": "mandar a verificar",
                                  "detalle": "pedidos 1 -> confirmado"}
    assert T.por_revisar(con)["silencio"] == []
    assert T.decidir_silencio(con, 1, "verificar", "Ana") is False      # ya no está nuevo


def test_descartar(con):
    assert T.decidir_silencio(con, 1, "descartar", "Luis") is True
    assert con.execute("SELECT estado FROM pedidos WHERE id=1").fetchone()[0] == "descartado"
    assert _bitacora(con)[-1]["quien"] == "Luis"
    assert _bitacora(con)[-1]["accion"] == "descartar alerta por silencio"


def test_no_aplica_a_otros_pedidos_ni_decisiones(con):
    assert T.decidir_silencio(con, 2, "verificar", "Ana") is False      # pedido de comida
    assert T.decidir_silencio(con, 3, "descartar", "Ana") is False      # ya descartada
    assert T.decidir_silencio(con, 99, "verificar", "Ana") is False
    assert T.decidir_silencio(con, 1, "despachar", "Ana") is False
    assert _bitacora(con) == []
    assert con.execute("SELECT estado FROM pedidos WHERE id=2").fetchone()[0] == "nuevo"


def test_sin_nombre_firma_despachador(con):
    assert T.decidir_silencio(con, 1, "descartar", "") is True
    assert _bitacora(con)[-1]["quien"] == "despachador"


def test_textos_de_la_tarjeta():
    fuente = (CARPETA / "app.py").read_text(encoding="utf-8")
    for texto in ("Sin contacto: verificar", '"Mandar a verificar"', 'T.decidir_silencio'):
        assert texto in fuente


def test_pendientes_no_cuentan_alertas_de_silencio(con):
    i = T.indicadores(con, None)
    assert i["pedidos_pendientes"] == 1 and i["pedidos_por_confirmar"] == 1     # solo el pedido 2
    assert i["sin_contacto"] == 1                                               # la alerta 1 (la 3 está descartada)
    T.decidir_silencio(con, 1, "verificar", "Ana")                              # en verificación sigue abierta
    i = T.indicadores(con, None)
    assert i["pedidos_pendientes"] == 1 and i["sin_contacto"] == 1
    T.decidir_silencio(con, 1, "descartar", "Ana")                              # ya confirmada: no aplica
    con.execute("UPDATE pedidos SET estado='descartado' WHERE id=1")
    assert T.indicadores(con, None)["sin_contacto"] == 0


def test_ficha_muestra_sin_contacto():
    assert "sin contacto</span>" in (CARPETA / "app.py").read_text(encoding="utf-8")
