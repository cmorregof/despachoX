"""Mapa base del tablero: teselas de OpenStreetMap estándar (sin clave ni registro) en tono claro.

Las teselas de CARTO piden clave y salen como «API KEY REQUIRED»: no se usan. El tono claro sale de
un filtro CSS que se aplica solo a la capa de teselas; marcadores, rutas y cierres quedan con sus
colores. El filtro va dentro del HTML del mapa porque streamlit-folium lo dibuja en un iframe.
"""
from __future__ import annotations

import folium

TESELAS = "OpenStreetMap"     # https://tile.openstreetmap.org, atribución «© colaboradores de OpenStreetMap»
FILTRO_TESELAS = ".leaflet-tile-pane { filter: grayscale(0.6) brightness(1.05) contrast(0.95); }"


def crear(centro: tuple[float, float], zoom: int = 13) -> folium.Map:
    m = folium.Map(location=centro, zoom_start=zoom, tiles=TESELAS, control_scale=True)
    m.get_root().header.add_child(folium.Element(f"<style>{FILTRO_TESELAS}</style>"))
    return m
