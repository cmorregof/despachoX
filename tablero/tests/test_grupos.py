"""Vista de grupos en «Por revisar» (DESPACHOX_AGRUPAR). Base temporal, sin red y sin modelo.

Las pruebas con `agrupar_stub` corren siempre: sustituyen despacho/agrupar.py por un agrupador mínimo
que respeta su firma. Las marcadas `real` usan el módulo de verdad y se saltan si aún no existe.
"""
from __future__ import annotations

import types
from dataclasses import dataclass
from pathlib import Path

import pytest

from datos import db
from tablero import datos as T

RAIZ = Path(__file__).resolve().parents[2]
CREADO = "2026-11-21T09:00:00-05:00"
LIMITE = "2026-11-21T15:00:00-05:00"


@pytest.fixture
def ruta(tmp_path):
    r = tmp_path / "g.db"
    c = db.conectar(r)
    c.executemany("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (?,?,?,?,?,?)", [
        (1, "Albergue A", "A", 5.07, -75.52, 1), (2, "Comedor B", "B", 5.06, -75.51, 0),
        (3, "Salón C", "C", 5.05, -75.50, 0)])
    filas = []
    for i, punto in enumerate([1, 1, 1, 2, 2, 2], start=1):
        filas.append((i, CREADO, punto, 2 + (i == 2), LIMITE, "nuevo", f"pedido sintético {i}: arroz",
                      i, 10.0 * i))
    c.executemany("INSERT INTO pedidos(id,creado_en,punto_id,urgencia,limite_en,estado,texto_original,"
                  "familias,kg_estimado) VALUES (?,?,?,?,?,?,?,?,?)", filas)
    c.commit()
    c.close()
    return r


@pytest.fixture
def con(ruta):
    c = db.conectar(ruta)
    yield c
    c.close()


@dataclass
class Grupo:
    clave: str
    punto_id: int
    pedido_ids: list
    pedidos: list
    familias: int
    familias_declaradas: int
    tope_familias: int | None
    sobre_tope: bool
    kg: float
    kg_declarados: float
    productos: list
    urgencia: int
    limite_en: str | None
    creado_en: str
    zona: str | None
    critico: bool


def _stub():
    """Agrupador mínimo con la firma de despacho/agrupar.py: un grupo por punto, sin tope."""
    import os

    def activo():
        return (os.environ.get("DESPACHOX_AGRUPAR") or "").lower() in ("1", "si", "sí", "true")

    def grupos_nuevos(con, ahora=None):
        criticos = {r["id"]: bool(r["critico"]) for r in con.execute("SELECT id, critico FROM puntos")}
        por_punto: dict[int, list] = {}
        for r in con.execute("SELECT * FROM pedidos WHERE estado='nuevo' AND punto_id IS NOT NULL ORDER BY id"):
            por_punto.setdefault(r["punto_id"], []).append(dict(r))
        salida = []
        for punto, ps in por_punto.items():
            fam = sum(p["familias"] or 0 for p in ps)
            kg = sum(p["kg_estimado"] or 0 for p in ps)
            salida.append(Grupo(f"p{punto}", punto, [p["id"] for p in ps], ps, fam, fam, None, False, kg, kg, [],
                                max(p["urgencia"] for p in ps), min(p["limite_en"] for p in ps),
                                min(p["creado_en"] for p in ps), None, criticos[punto]))
        return salida
    return types.SimpleNamespace(activo=activo, grupos_nuevos=grupos_nuevos)


@pytest.fixture
def agrupar_stub(monkeypatch):
    monkeypatch.setattr(T, "_agrupar", _stub())


def _revisar_grupos(con):
    gs = sorted(T.grupos_por_revisar(con), key=lambda g: g["punto_id"])
    assert len(gs) == 2
    assert [g["pedido_ids"] for g in gs] == [[1, 2, 3], [4, 5, 6]]
    assert [g["familias"] for g in gs] == [6, 15]
    assert gs[0]["punto"] == "Albergue A" and gs[0]["critico"] and gs[0]["n_pedidos"] == 3
    assert {"id", "texto_original", "familias", "kg_estimado", "urgencia"} == set(gs[0]["pedidos"][0])
    return gs


def _confirmar(con, g):
    assert T.confirmar_grupo(con, g["pedido_ids"], "prueba", g["clave"]) == 3
    estados = [r[0] for r in con.execute("SELECT estado FROM pedidos WHERE id IN (1,2,3)")]
    assert estados == ["confirmado"] * 3
    bit = [r["accion"] for r in T.bitacora(con)]
    assert "confirmar grupo" in bit and bit.count("confirmar pedido") == 3


# ---------- con agrupador de prueba ----------

def test_apagada_no_hay_grupos(con, agrupar_stub, monkeypatch):
    monkeypatch.delenv("DESPACHOX_AGRUPAR", raising=False)
    assert T.grupos_por_revisar(con) == []


def test_grupos_y_confirmar(con, agrupar_stub, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    gs = _revisar_grupos(con)
    assert gs[0]["resumen"] is None
    _confirmar(con, gs[0])


def test_descartar_grupo(con, agrupar_stub, monkeypatch):
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    g = sorted(T.grupos_por_revisar(con), key=lambda g: g["punto_id"])[1]
    assert T.descartar_grupo(con, g["pedido_ids"], "prueba", g["clave"]) == 3
    assert "descartar grupo" in [r["accion"] for r in T.bitacora(con)]


def test_resumen_guardado_aparece(con, agrupar_stub, monkeypatch):
    from despacho import resumen_grupo as R
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    grupos = T._agrupar.grupos_nuevos(con)
    assert R.resumir_y_guardar(con, grupos, lambda t: "Piden arroz; hay bebés.") == 2
    g = T.grupos_por_revisar(con)[0]
    assert g["resumen"] == "Piden arroz; hay bebés." and g["resumen_modelo"] == "falso"


# ---------- con despacho/agrupar.py de verdad ----------

def test_real_grupos_y_confirmar(con, monkeypatch):
    agrupar = pytest.importorskip("despacho.agrupar")
    monkeypatch.setattr(T, "_agrupar", agrupar)
    monkeypatch.delenv("DESPACHOX_AGRUPAR", raising=False)
    assert T.grupos_por_revisar(con) == []
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    gs = _revisar_grupos(con)
    _confirmar(con, gs[0])


# ---------- la pantalla ----------

def _app(ruta, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("DESPACHOX_DB", str(ruta))
    monkeypatch.setattr(db, "RUTA_DB", ruta)
    monkeypatch.setattr(db.conectar, "__defaults__", (ruta,))   # el valor por defecto se fijó al importar
    monkeypatch.delenv("DESPACHOX_CLAVE_TABLERO", raising=False)
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    at = AppTest.from_file(str(RAIZ / "tablero" / "app.py"), default_timeout=120)
    at.run()
    return at


def _textos(at) -> list[str]:
    return [m.value for m in at.markdown]


def test_app_muestra_grupos(ruta, agrupar_stub, monkeypatch):
    at = _app(ruta, monkeypatch)
    assert not at.exception, at.exception
    textos = _textos(at)
    assert any("Grupo ·" in t for t in textos)
    # los pedidos agrupados no se repiten como sueltos
    assert not any(t.startswith("**Pedido 1**") for t in textos)


def test_app_apagada_sin_grupos(ruta, agrupar_stub, monkeypatch):
    at = _app(ruta, monkeypatch)
    monkeypatch.delenv("DESPACHOX_AGRUPAR")
    at.run()
    assert not at.exception, at.exception
    textos = _textos(at)
    assert not any("Grupo ·" in t for t in textos)
    assert any(t.startswith("**Pedido 1**") for t in textos)


def test_app_real_muestra_grupos(ruta, monkeypatch):
    agrupar = pytest.importorskip("despacho.agrupar")
    monkeypatch.setattr(T, "_agrupar", agrupar)
    at = _app(ruta, monkeypatch)
    assert not at.exception, at.exception
    assert sum("Grupo ·" in t for t in _textos(at)) == 2


def test_app_boton_confirmar_grupo(ruta, agrupar_stub, monkeypatch):
    at = _app(ruta, monkeypatch)
    at.button(key="gcp1").click().run()
    # AppTest repite la página entera, no el fragmento, así que refrescar() (st.rerun(scope="fragment"))
    # falla aquí después de guardar. Pasa igual con los botones que ya había; en el navegador no ocurre.
    assert all("scope=\"fragment\"" in e.value for e in at.exception), at.exception
    c = db.conectar(ruta)
    try:
        estados = [r[0] for r in c.execute("SELECT estado FROM pedidos ORDER BY id")]
    finally:
        c.close()
    assert estados == ["confirmado"] * 3 + ["nuevo"] * 3
