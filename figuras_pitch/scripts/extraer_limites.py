"""Pasa los límites de OpenStreetMap de despacho/cache/admin_osm.pkl a un GeoJSON pequeño para el mapa del pitch.

Uso (con un Python que tenga geopandas y pyarrow, por ejemplo el del proyecto):
    python figuras_pitch/scripts/extraer_limites.py

Lee  despacho/cache/admin_osm.pkl (ignorado por git; lo baja el código de despacho/).
Escribe figuras_pitch/datos/limites_osm.geojson, con el perímetro urbano, las 12 comunas y los 5 corregimientos que
trae el archivo, simplificados a unos 15 m. El pickle guarda texto con pyarrow, y el Python de las figuras no lo
trae; por eso el GeoJSON se guarda en el repositorio y el mapa lo lee de ahí.

Datos © colaboradores de OpenStreetMap, licencia ODbL (https://www.openstreetmap.org/copyright).
"""
import json
import pickle
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENTRADA = RAIZ / "despacho" / "cache" / "admin_osm.pkl"
SALIDA = RAIZ / "figuras_pitch" / "datos" / "limites_osm.geojson"
TOLERANCIA = 0.00015  # grados, unos 15 m en Manizales

# OSM llama «Corredor Agroturístico» al corregimiento que los documentos del equipo llaman El Tablazo.
NOMBRE_EQUIPO = {"Corredor Agroturístico": "El Tablazo (Corredor Agroturístico)"}


def main():
    with open(ENTRADA, "rb") as f:
        gdf = pickle.load(f)
    gdf = gdf.reset_index()
    rasgos = []
    for _, fila in gdf.iterrows():
        nombre = str(fila["name"])
        nivel = str(fila["admin_level"])
        if nombre.startswith("Comuna "):
            clase, corto = "comuna", nombre.removeprefix("Comuna ")
        elif nivel == "7" and nombre not in ("Perímetro Urbano Manizales", "Cabecera Municipal Villamaría", "170001"):
            clase, corto = "corregimiento", NOMBRE_EQUIPO.get(nombre, nombre)
        elif nombre == "Perímetro Urbano Manizales":
            clase, corto = "perimetro", "Perímetro urbano de Manizales"
        else:
            continue
        geom = fila.geometry.simplify(TOLERANCIA, preserve_topology=True)
        rasgos.append({
            "type": "Feature",
            "properties": {"clase": clase, "nombre": corto, "nombre_osm": nombre,
                           "osm": f"{fila['element']}/{fila['id']}"},
            "geometry": json.loads(json.dumps(geom.__geo_interface__)),
        })
    datos = {
        "type": "FeatureCollection",
        "atribucion": "© colaboradores de OpenStreetMap, ODbL. Extraído de despacho/cache/admin_osm.pkl.",
        "features": sorted(rasgos, key=lambda r: (r["properties"]["clase"], r["properties"]["nombre"])),
    }
    texto = json.dumps(datos, ensure_ascii=False)
    # Redondea coordenadas a 6 decimales para que el archivo pese poco.
    import re
    texto = re.sub(r"(-?\d+\.\d{6})\d+", r"\1", texto)
    SALIDA.write_text(texto, encoding="utf-8")
    print(f"escrito {SALIDA} ({len(rasgos)} polígonos, {SALIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
