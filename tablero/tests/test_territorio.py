"""Pestaña «Territorio» (encargos/T1_TERRITORIO.md, parte C). Base temporal, sin red."""
import csv
import io
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

from datos import db
from tablero import datos as T

AHORA = datetime(2026, 11, 21, 12, 0, 0, tzinfo=db.BOGOTA)
CARPETA = Path(__file__).resolve().parent.parent


def iso(horas: float) -> str:
    return (AHORA + timedelta(hours=horas)).isoformat(timespec="seconds")


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "t.db")
    c.executemany("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)", [
        (1, "Albergue Norte", "Norte", "Comuna Norte", 5.07, -75.52, 1),
        (2, "Comedor Sur", "Sur", "Comuna Sur", 5.05, -75.50, 1)])
    # Norte: crítico entregado tarde. Sur: crítico entregado a tiempo.
    c.executemany("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,limite_en,estado,"
                  "texto_original,remitente_hash) VALUES (?,?,?,?,?,?,?,?,?)", [
                      (1, iso(-6), 1, 10, 100, iso(-3), "entregado", "texto privado uno", "hashsecreto1"),
                      (2, iso(-6), 2, 5, 50, iso(-3), "entregado", "texto privado dos", "hashsecreto2")])
    c.executemany("INSERT INTO paquetes(codigo,pedido_id,kg,estado,entregado_en) VALUES (?,?,?,?,?)", [
        ("A1", 1, 100, "entregado", iso(-1)), ("B1", 2, 50, "entregado", iso(-4))])
    c.executemany("INSERT INTO lugares(nombre,alias,tipo,lat,lon) VALUES (?,?,?,?,?)", [
        ("Norte", "norte", "barrio", 5.07, -75.52), ("La Aurora", "la aurora", "vereda", 5.0, -75.6),
        ("Callado", "callado", "barrio", 5.08, -75.53)])
    c.commit()
    return c


def test_pendiente_si_no_hay_modulo(con, monkeypatch):
    monkeypatch.setattr(T, "_territorio", None)
    d = T.territorio(con, AHORA)
    assert d["disponible"] is False and d["tabla"] == [] and d["sin_pedidos"] == []
    assert T.territorio_csv(d).decode("utf-8-sig").strip() == ""


def test_tabla_real_peor_atendido_arriba_y_bajo_meta(con):
    d = T.territorio(con, AHORA)
    assert d["disponible"] is True
    con_datos = [f for f in d["tabla"] if f["pct_criticos_a_tiempo"] is not None]
    assert [f["territorio"] for f in con_datos] == ["Comuna Norte", "Comuna Sur"]
    assert con_datos[0]["pct_criticos_a_tiempo"] == 0.0 and con_datos[0]["bajo_meta"] is True
    assert con_datos[1]["pct_criticos_a_tiempo"] == 100.0 and con_datos[1]["bajo_meta"] is False
    # Los territorios sin críticos evaluados van al final, sin color.
    resto = d["tabla"][len(con_datos):]
    assert all(f["pct_criticos_a_tiempo"] is None and not f["bajo_meta"] for f in resto)


def test_orden_con_empates_y_vacios():
    filas = [
        {"territorio": "C", "pct_criticos_a_tiempo": None, "pct_a_tiempo": 10.0, "pendiente_mas_viejo_h": 1},
        {"territorio": "B", "pct_criticos_a_tiempo": 50.0, "pct_a_tiempo": 80.0, "pendiente_mas_viejo_h": 1},
        {"territorio": "A", "pct_criticos_a_tiempo": 50.0, "pct_a_tiempo": 60.0, "pendiente_mas_viejo_h": 1},
        {"territorio": "D", "pct_criticos_a_tiempo": 100.0, "pct_a_tiempo": 100.0, "pendiente_mas_viejo_h": 9}]
    falso = SimpleNamespace(COLUMNAS=("territorio", "pct_criticos_a_tiempo", "pct_a_tiempo",
                                      "pendiente_mas_viejo_h"),
                            resumen=lambda con, ahora=None: filas, silencio=lambda con: [])
    d = T.territorio(None, AHORA, modulo=falso)
    assert [f["territorio"] for f in d["tabla"]] == ["A", "B", "D", "C"]
    assert [f["bajo_meta"] for f in d["tabla"]] == [True, True, False, False]


def test_sin_pedidos_registrados(con):
    d = T.territorio(con, AHORA)
    nombres = {s["nombre"] for s in d["sin_pedidos"]}
    assert {"La Aurora", "Callado"} <= nombres and "Norte" not in nombres
    assert all(s["estado"] == "sin pedidos registrados" for s in d["sin_pedidos"])


def test_sin_datos_personales_ni_texto(con):
    d = T.territorio(con, AHORA)
    for f in d["tabla"] + d["sin_pedidos"]:
        assert "texto_original" not in f and "remitente_hash" not in f
    texto = T.territorio_csv(d).decode("utf-8-sig")
    assert "privado" not in texto and "hashsecreto" not in texto
    filas = list(csv.DictReader(io.StringIO(texto)))
    assert list(filas[0].keys()) == list(d["columnas"]) and len(filas) == len(d["tabla"])


def test_nunca_dice_sin_necesidad():
    for archivo in ("app.py", "datos.py"):
        assert "sin necesidad" not in (CARPETA / archivo).read_text(encoding="utf-8").lower()


def test_pestana_territorio_en_la_app():
    fuente = (CARPETA / "app.py").read_text(encoding="utf-8")
    assert '"Territorio"' in fuente and "Pendiente: despacho.territorio" in fuente
    assert "Barrios y veredas sin pedidos registrados" in fuente and '"Descargar CSV"' in fuente
