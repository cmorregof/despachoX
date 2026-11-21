"""Mapa base: OpenStreetMap estándar, sin proveedores que pidan clave, y tono claro solo en las teselas."""
import re
from pathlib import Path

from tablero import mapa_base

CARPETA = Path(__file__).resolve().parent.parent


def _html():
    return mapa_base.crear((5.07, -75.52)).get_root().render()


def test_teselas_de_openstreetmap_sin_carto():
    html = _html()
    urls = re.findall(r"https?://[^\s\"']*\{z\}[^\s\"']*", html)
    assert urls, "no se encontró la URL de las teselas"
    for url in urls:
        assert "cartocdn" not in url and "carto.com" not in url
        assert "tile.openstreetmap.org" in url
    assert "OpenStreetMap" in html                                   # atribución


def test_sin_proveedores_con_clave_en_el_tablero():
    for archivo in ("app.py", "mapa_base.py"):
        fuente = (CARPETA / archivo).read_text(encoding="utf-8").lower()
        for proveedor in ("cartocdn", "carto.com", "cartodb", "apikey", "api_key", "mapbox", "stadia", "thunderforest"):
            assert proveedor not in fuente, (archivo, proveedor)


def test_filtro_solo_en_la_capa_de_teselas():
    html = _html()
    assert ".leaflet-tile-pane { filter: grayscale(0.6) brightness(1.05) contrast(0.95); }" in html
    assert not re.search(r"\.leaflet-(marker|overlay)-pane\s*\{[^}]*filter", html)


def test_atribucion_en_pantalla():
    assert 'st.caption("© colaboradores de OpenStreetMap")' in (CARPETA / "app.py").read_text(encoding="utf-8")
