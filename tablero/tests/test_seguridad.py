"""Textos de la base escapados en el mapa y botón «Reiniciar datos de prueba». Sin red."""
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import folium
import pytest

from datos import db
from tablero import datos as T
from tablero import mapa_base

CARPETA = Path(__file__).resolve().parent.parent
MALO = "<script>alert(1)</script>"


def test_seguro_escapa():
    assert mapa_base.seguro(MALO) == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert mapa_base.seguro(None) == "" and mapa_base.seguro(12) == "12"


def test_tooltip_con_script_sale_escapado_en_el_mapa():
    m = mapa_base.crear((5.07, -75.52))
    fg = folium.FeatureGroup()
    folium.CircleMarker([5.07, -75.52], radius=6, tooltip=mapa_base.seguro(f"Cierre 1 · {MALO}")).add_to(fg)
    folium.Marker([5.07, -75.52], tooltip=mapa_base.seguro(f"Acopio · {MALO}")).add_to(fg)
    fg.add_to(m)
    html = m.get_root().render()
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_todos_los_tooltips_del_tablero_pasan_por_seguro():
    fuente = (CARPETA / "app.py").read_text(encoding="utf-8")
    tooltips = re.findall(r"tooltip=([^\s,)]{1,3})", fuente)
    assert tooltips and all(t.startswith("S(") for t in tooltips), tooltips
    assert "popup=" not in fuente
    assert "html.escape(plan['aprobado_por']" in fuente          # nombre de quien aprobó


@pytest.fixture
def con(tmp_path):
    return db.conectar(tmp_path / "t.db")


def test_reiniciar_ejecuta_la_semilla_y_anota(con):
    llamadas = []

    def correr(cmd, **kw):
        llamadas.append((cmd, kw))
        return SimpleNamespace(returncode=0, stdout="puntos.csv  sintético 15 filas\n", stderr="")
    r = T.reiniciar_datos_prueba(con, "Ana", correr=correr)
    assert r.ok
    cmd, kw = llamadas[0]
    assert cmd == [sys.executable, "-m", "despacho.semilla", "--cargar", "--reiniciar"]
    assert kw["cwd"] == T.RAIZ and kw["timeout"] == T.ESPERA_SEMILLA_S
    b = con.execute("SELECT quien, accion FROM bitacora ORDER BY id DESC LIMIT 1").fetchone()
    assert (b["quien"], b["accion"]) == ("Ana", "reiniciar datos de prueba")


def test_reiniciar_con_error_no_anota(con):
    def falla(cmd, **kw):
        return SimpleNamespace(returncode=1, stdout="", stderr="Traceback\nSystemExit: Carga rechazada")
    r = T.reiniciar_datos_prueba(con, "Ana", correr=falla)
    assert not r.ok and "Carga rechazada" in r.mensaje

    def lento(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, 1)
    assert "no respondió" in T.reiniciar_datos_prueba(con, "Ana", correr=lento).mensaje
    assert con.execute("SELECT COUNT(*) FROM bitacora").fetchone()[0] == 0


def test_reiniciar_sin_nombre_firma_despachador(con):
    T.reiniciar_datos_prueba(con, "  ", correr=lambda cmd, **kw: SimpleNamespace(returncode=0, stdout="", stderr=""))
    assert con.execute("SELECT quien FROM bitacora").fetchone()[0] == "despachador"


def test_boton_pide_confirmacion():
    fuente = (CARPETA / "app.py").read_text(encoding="utf-8")
    assert 'st.checkbox("Sí, borrar los datos y cargar la semilla"' in fuente
    assert 'st.button("Reiniciar datos de prueba", type="primary", disabled=not seguro' in fuente
