"""Construye el nomenclátor complementario: sitios, veredas y apodos de vías de Manizales.

Uso (desde la raíz del repo):  .venv/bin/python -m lugares.construir_extra

Escribe:
  datos/semilla/lugares_extra.csv          nombre,alias,tipo,lat,lon,osm_u,osm_v,origen
  datos/semilla/lugares_extra_fuentes.csv  nombre,fuente,consulta,osm_tipo,osm_id,display_name,metros_a_la_red

Ninguna coordenada se escribe a mano. Cada una sale de una de tres fuentes:
  - `vias.csv`: apodos de una vía que ya existe (misma arista y mismo punto).
  - `grafo`: una arista del grafo vial local, elegida por nombre exacto (vías nuevas).
  - `nominatim`: respuesta de Nominatim (OSM) con viewbox y bounded=1, guardada en
    despacho/cache/nominatim/. Con el caché lleno el script corre sin red.

Lo que no se ubica con una fuente, o no pasa las validaciones, queda fuera del CSV y se imprime al final.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path

import numpy as np
import requests

from despacho import red

RAIZ = Path(__file__).resolve().parent.parent
SEMILLA = RAIZ / "datos" / "semilla"
CACHE = RAIZ / "despacho" / "cache" / "nominatim"
SALIDA = SEMILLA / "lugares_extra.csv"
SALIDA_FUENTES = SEMILLA / "lugares_extra_fuentes.csv"

LON_MIN, LON_MAX, LAT_MIN, LAT_MAX = -75.74, -75.30, 4.93, 5.20
MAX_METROS = 500.0
UA = "nomenclator-hackathon/0.1"

# (nombre, alias, tipo, consulta, tokens que debe llevar el nombre del resultado)
# Los tokens se comparan sin tildes ni mayúsculas contra el primer segmento de display_name.
SITIOS = [
    # Transporte y accesos
    ("Terminal de Transportes", "la terminal|el terminal|terminal de manizales|terminal de transporte", "sitio",
     "Terminal de Transportes Manizales", ("terminal",)),
    ("Los Cámbulos", "cambulos|estacion cambulos|estacion los cambulos", "sitio", "Los Cámbulos Manizales", ("cambulos",)),
    ("Aeropuerto La Nubia", "aeropuerto|el aeropuerto|aeropuerto de manizales", "sitio",
     "Aeropuerto La Nubia Manizales", ("aeropuerto",)),
    ("La Manuela", "manuela|sector la manuela", "sitio", "La Manuela Manizales", ("manuela",)),
    ("Tres Puertas", "sector tres puertas|las tres puertas", "sitio", "Tres Puertas Manizales", ("tres puertas",)),
    ("La Cabaña", "sector la cabana|cabana", "sitio", "La Cabaña Manizales", ("cabana",)),
    ("La Rochela", "rochela|parque la rochela", "sitio", "La Rochela Manizales", ("rochela",)),
    ("Glorieta San Rafael", "glorieta de san rafael|san rafael glorieta", "sitio", "Glorieta San Rafael Manizales",
     ("glorieta", "san rafael")),
    ("Glorieta El Caribe", "glorieta del caribe|glorieta caribe", "sitio", "Glorieta El Caribe Manizales", ("glorieta", "caribe")),
    ("Glorieta Peralonso", "glorieta de peralonso", "sitio", "Glorieta Peralonso Manizales", ("glorieta", "peralonso")),
    ("Glorieta San Cayetano", "glorieta de san cayetano", "sitio", "Glorieta San Cayetano Manizales",
     ("glorieta", "san cayetano")),
    ("Puente de Cristal", "puente de vidrio", "sitio", "Puente de Cristal Manizales", ("puente", "cristal")),
    ("Hospital de Caldas", "hospital caldas|el hospital de caldas", "sitio", "Hospital de Caldas Manizales",
     ("hospital de caldas",)),
    ("Hospital Santa Sofía", "santa sofia|hospital santa sofia|hospital departamental|hospital de santa sofia", "sitio",
     "Hospital Santa Sofía Manizales", ("santa sofia",)),
    ("Clínica de La Presentación", "clinica la presentacion|la presentacion", "sitio",
     "Clínica de La Presentación Manizales", ("presentacion",)),
    ("Clínica San Juan de Dios", "clinica psiquiatrica san juan de dios|san juan de dios", "sitio",
     "Clínica Psiquiátrica San Juan de Dios Manizales", ("san juan de dios",)),
    ("Clínica Esimed", "esimed", "sitio", "Clínica Esimed Manizales", ("esimed",)),
    ("Clínica Versalles", "clinica de versalles", "sitio", "Clínica Versalles Manizales", ("versalles",)),
    ("Clínica Avidanti", "avidanti", "sitio", "Clínica Avidanti Manizales", ("avidanti",)),
    ("Clínica Santa Ana", "santa ana clinica", "sitio", "Clínica Santa Ana Manizales", ("santa ana",)),
    ("Clínica de la Policía", "clinica de la policia|sanidad de la policia", "sitio", "Clínica de la Policía Manizales",
     ("policia",)),
    ("Defensa Civil", "la defensa civil", "sitio", "Defensa Civil Manizales", ("defensa civil",)),
    ("Bomberos Fundadores", "estacion de bomberos fundadores|bomberos del centro", "sitio",
     "Estación de Bomberos Fundadores Manizales", ("bomberos", "fundadores")),
    ("Bomberos Palogrande", "estacion de bomberos palogrande", "sitio", "Estación de Bomberos Palogrande Manizales",
     ("bomberos", "palogrande")),
    ("Bomberos Oriental", "bomberos juanchito|estacion de bomberos oriental", "sitio",
     "Estación de Bomberos Oriental Manizales", ("bomberos", "oriental")),
    ("Policía Metropolitana de Manizales", "policia metropolitana|comando de policia", "sitio",
     "Policía Metropolitana de Manizales", ("policia metropolitana",)),
    ("Estación de Policía Maltería", "policia malteria|estacion de policia de malteria", "sitio",
     "Estación de Policía Maltería", ("malteria",)),
    ("Batallón Ayacucho", "el batallon|batallon de infanteria 22|batallon ayacucho", "sitio",
     "Batallón Ayacucho Manizales", ("ayacucho",)),
    # Deporte
    ("Estadio Palogrande", "estadio de palogrande|el estadio|estadio de manizales", "sitio",
     "Estadio Palogrande Manizales", ("estadio palogrande",)),
    ("Coliseo Mayor", "coliseo mayor de manizales", "sitio", "Coliseo Mayor Manizales", ("coliseo mayor",)),
    ("Coliseo Menor", "coliseo menor de manizales", "sitio", "Coliseo Menor Manizales", ("coliseo menor",)),
    ("Plaza de Toros", "la plaza de toros|plaza de toros de manizales", "sitio", "Plaza de toros de Manizales",
     ("plaza de toros",)),
    ("Expoferias", "centro de ferias|las ferias|expoferias manizales", "sitio", "Expoferias Manizales", ("expoferias",)),
    ("Universidad Nacional Palogrande", "nacional palogrande|unal palogrande|la nacional de palogrande", "sitio",
     "Universidad Nacional Campus Palogrande Manizales", ("palogrande",)),
    ("Universidad Nacional El Cable", "nacional el cable|unal el cable|la nacional del cable", "sitio",
     "Universidad Nacional Campus El Cable Manizales", ("el cable",)),
    ("Universidad Nacional La Nubia", "nacional la nubia|unal la nubia|campus la nubia", "sitio",
     "Universidad Nacional Campus La Nubia Manizales", ("la nubia",)),
    ("Universidad de Caldas", "u de caldas|ucaldas|la universidad de caldas", "sitio",
     "Universidad de Caldas Manizales", ("universidad de caldas",)),
    ("Universidad Autónoma de Manizales", "la autonoma|autonoma|uam", "sitio",
     "Universidad Autónoma de Manizales", ("autonoma",)),
    ("Universidad Católica de Manizales", "la catolica|catolica|ucm", "sitio",
     "Universidad Católica de Manizales", ("catolica",)),
    ("Universidad de Manizales", "umanizales|la u de manizales", "sitio", "Universidad de Manizales",
     ("universidad de manizales",)),
    ("Universidad Luis Amigó", "luis amigo|funlam", "sitio", "Universidad Luis Amigó Manizales", ("amigo",)),
    ("SENA Manizales", "el sena|sena|sena juanchito", "sitio", "SENA Manizales", ("sena",)),
    # Centros históricos, parques y comercio
    ("Catedral de Manizales", "la catedral|catedral basilica|catedral de nuestra senora del rosario", "sitio",
     "Catedral Basílica de Manizales", ("catedral",)),
    ("Plaza de Bolívar", "plaza bolivar|plaza principal|plaza de simon bolivar", "sitio",
     "Plaza de Bolívar Manizales", ("plaza de bolivar",)),
    ("Parque Caldas", "parque de caldas|el parque caldas", "sitio", "Parque Caldas Manizales", ("parque caldas",)),
    ("Monumento a los Colonizadores", "los colonizadores|colonizadores|monumento de chipre", "sitio",
     "Monumento a los Colonizadores Manizales", ("colonizadores",)),
    ("Torre al Cielo", "torre del cielo|mirador torre al cielo", "sitio", "Torre al Cielo Manizales", ("torre al cielo",)),
    ("Parque Antonio Nariño", "parque narino|parque antonio narino|el parque narino", "sitio",
     "Parque Antonio Nariño Manizales", ("narino",)),
    ("Ecoparque Los Yarumos", "los yarumos|yarumos|parque los yarumos", "sitio", "Ecoparque Los Yarumos Manizales",
     ("yarumos",)),
    ("Parque del Agua", "parque del agua manizales", "sitio", "Parque del Agua Manizales", ("parque del agua",)),
    ("Cable Plaza", "centro comercial cable plaza|c c cable plaza", "sitio", "Cable Plaza Manizales", ("cable plaza",)),
    ("Centro Comercial Sancancio", "c c sancancio|centro comercial de sancancio", "sitio",
     "Centro Comercial Sancancio Manizales", ("sancancio",)),
    ("Galería de Manizales", "la galeria|galeria|plaza de mercado|plaza de mercado de manizales|mercado de la galeria",
     "sitio", "Plaza de Mercado Galería Manizales", ("galeria",)),
    ("Hacienda Venecia", "finca venecia", "sitio", "Hacienda Venecia Manizales", ("venecia",)),
    ("Cementerio San Esteban", "san esteban|cementerio de san esteban", "sitio", "Cementerio San Esteban Manizales",
     ("san esteban",)),
    ("Cementerio Universal", "cementerio universal de manizales", "sitio", "Cementerio Universal Manizales",
     ("cementerio universal",)),
    ("Cementerio Municipal de Villamaría", "cementerio de villamaria", "sitio", "Cementerio Villamaría",
     ("cementerio",)),
    ("Cable Aéreo Línea 1", "cable linea 1|linea 1 del cable", "sitio", "Línea 1 Cable Aéreo Manizales",
     ("linea 1",)),
    ("Cable Aéreo Línea 2", "cable linea 2|linea 2 del cable", "sitio", "Línea 2 Cable Aéreo Manizales",
     ("linea 2",)),
    ("Cable Aéreo Línea 3", "cable linea 3|linea 3 del cable", "sitio", "Línea 3 Cable Aéreo Manizales",
     ("linea 3",)),
    # Municipios y poblados cercanos
    ("Villamaría", "villa maria|casco urbano de villamaria|parque de villamaria", "sitio", "Villamaría Caldas",
     ("villamaria",)),
    ("Santágueda", "santagueda|termales de santagueda", "vereda", "Santágueda Palestina Caldas", ("santagueda",)),
    ("Arauca", "arauca caldas|la arauca", "vereda", "Arauca Palestina Caldas", ("arauca",)),
    # Veredas y corregimientos de Manizales y Villamaría
    ("San Peregrino", "vereda san peregrino", "vereda", "San Peregrino Manizales", ("san peregrino",)),
    ("Río Claro", "rio claro|vereda rio claro", "vereda", "Río Claro Manizales", ("rio claro",)),
    ("La Trinidad", "vereda la trinidad|trinidad", "vereda", "La Trinidad Manizales", ("trinidad",)),
    ("El Arenillo", "arenillo|vereda el arenillo", "vereda", "El Arenillo Manizales", ("arenillo",)),
    ("Corinto", "vereda corinto", "vereda", "Corinto Manizales", ("corinto",)),
    ("Alto Tablazo", "vereda alto tablazo", "vereda", "Alto Tablazo Manizales", ("tablazo",)),
    ("Bajo Tablazo", "vereda bajo tablazo", "vereda", "Bajo Tablazo Manizales", ("tablazo",)),
    ("La Cristalina", "vereda la cristalina|cristalina", "vereda", "La Cristalina Manizales", ("cristalina",)),
    ("Llanitos", "vereda llanitos", "vereda", "Llanitos Manizales", ("llanitos",)),
    ("El Águila", "vereda el aguila|aguila", "vereda", "El Águila Manizales", ("aguila",)),
    ("La Aurora", "vereda la aurora|aurora", "vereda", "La Aurora Manizales", ("aurora",)),
    ("Alto del Naranjo", "naranjo|vereda alto del naranjo", "vereda", "Alto del Naranjo Villamaría",
     ("naranjo",)),
    ("La Violeta", "vereda la violeta|violeta", "vereda", "La Violeta Villamaría", ("violeta",)),
    ("Cuchilla del Salado", "cuchilla|salado|vereda cuchilla del salado", "vereda", "Cuchilla del Salado Manizales",
     ("salado",)),
    ("Río Blanco", "rio blanco|reserva rio blanco", "vereda", "Río Blanco Manizales", ("rio blanco",)),
    ("Corredor Agroturístico", "corredor agroturistico", "vereda", "Corredor Agroturístico Villamaría", ("agroturistico",)),
]

# Apodos de vías que ya están en vias.csv: nombre canónico exacto -> apodos.
APODOS_VIAS = {
    "Panamericana": "la pana|pana|la panamericana|carretera panamericana",
    "avenida Kevin Ángel": "la kevin|kevin angel|la kevin angel|avenida kevin",
    "avenida Paralela": "la paralela|paralela",
    "avenida Santander": "la santander|santander",
    "autopista del Café": "la autopista|autopista|la autopista del cafe",
    "vía a Medellín": "carretera a medellin|via medellin|salida a medellin|la via a medellin",
    "vía a Chinchiná": "la via a chinchina|via chinchina|carretera a chinchina|salida a chinchina",
    "vía a Villamaría": "la via a villamaria|carretera a villamaria|via villamaria|salida a villamaria",
    "vía a Neira": "la via a neira|carretera a neira|salida a neira|via neira",
    "salida a Letras": "alto de letras|letras|via a letras|via al nevado del ruiz|via a bogota|salida a bogota",
    "avenida del Centro": "avenida gilberto alzate|la avenida del centro|la gilberto alzate|gilberto alzate avendano",
    "avenida 12 de Octubre": "la 12 de octubre|12 de octubre|doce de octubre",
    "avenida Alberto Mendoza": "alberto mendoza|la alberto mendoza|avenida mendoza",
    "avenida Bernardo Arango": "bernardo arango|la bernardo arango",
}

# Vías nuevas, por nombre exacto de arista en el grafo: (nombre, alias, regex sobre `name`)
VIAS_NUEVAS = [
    ("carrera 19", "la 19|cra 19|la carrera 19", r"^Carrera 19$"),
    ("carrera 20", "la 20|cra 20|la carrera 20", r"^Carrera 20$"),
    ("carrera 21", "la 21|cra 21|la carrera 21", r"^Carrera 21$"),
    ("carrera 22", "la 22|cra 22|la carrera 22", r"^Carrera 22$"),
    ("carrera 23", "la 23|cra 23|la carrera 23", r"^Carrera 23$"),
    ("carrera 24", "la 24|cra 24|la carrera 24", r"^Carrera 24$"),
    ("carrera 27", "la 27|cra 27|la carrera 27", r"^Carrera 27$"),
    ("carrera 28", "la 28|cra 28|la carrera 28", r"^Carrera 28$"),
    ("calle 23", "la calle 23|cll 23", r"^Calle 23$"),
    ("calle 48", "la calle 48|cll 48", r"^Calle 48$"),
    ("calle 50", "la calle 50|cll 50", r"^Calle 50$"),
    ("avenida Marcelino Palacio", "marcelino palacio|la marcelino palacio", r"^Avenida Marcelino Palacio$"),
    ("avenida Centenario", "la centenario|centenario avenida", r"^Avenida Centenario$"),
    ("avenida El Guamo", "la avenida el guamo|avenida guamo", r"^Avenida El Guamo$"),
    ("avenida La Sultana", "la sultana avenida|avenida sultana", r"^Avenida La Sultana$"),
    ("avenida José Restrepo", "jose restrepo|avenida restrepo", r"^Avenida José Restrepo$"),
    ("avenida Las Araucarias", "las araucarias|avenida araucarias", r"^Avenida Las Araucarias$"),
    ("avenida Lindsay", "la lindsay|lindsay", r"^Avenida Lindsay$"),
    ("Troncal del Eje Cafetero", "la troncal|troncal|troncal del eje", r"^Troncal del Eje Cafetero$"),
]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s).strip()


def sin_articulo(s: str) -> str:
    return re.sub(r"^(el|la|los|las) ", "", norm(s))


# ---------- Nominatim con caché ----------
_ultima = [0.0]


def nominatim(consulta: str) -> list | None:
    """Respuesta de Nominatim (lista) o None si no hay caché y falla la red."""
    CACHE.mkdir(parents=True, exist_ok=True)
    ruta = CACHE / (hashlib.sha1(consulta.encode()).hexdigest() + ".json")
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))
    params = dict(format="jsonv2", q=consulta, countrycodes="co", viewbox="-75.74,5.20,-75.30,4.93",
                  bounded=1, limit=5)
    for intento in range(3):
        espera = 1.1 - (time.time() - _ultima[0])
        if espera > 0:
            time.sleep(espera)
        _ultima[0] = time.time()
        try:
            r = requests.get("https://nominatim.openstreetmap.org/search", params=params,
                             headers={"User-Agent": UA}, timeout=30)
            if r.status_code == 200:
                datos = r.json()
                ruta.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
                return datos
        except requests.RequestException:
            pass
        time.sleep(5 * (intento + 1))
    return None


def elegir_resultado(res: list, tokens: tuple):
    for x in res:
        lat, lon = float(x["lat"]), float(x["lon"])
        if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
            continue
        primero = norm(x["display_name"].split(",")[0])
        if all(norm(t) in primero for t in tokens):
            return x
    return None


# ---------- Vías en el grafo ----------
def lista(x):
    return x if isinstance(x, list) else [x]


def arista_media(g, patron: str):
    rx = re.compile(patron, re.I)
    cands = []
    for u, v, d in g.edges(data=True):
        if not any(rx.search(str(s)) for s in lista(d.get("name", "")) if s):
            continue
        geom = red.geometria_arista(g, u, v)
        p = geom.interpolate(0.5, normalized=True)
        cands.append((u, v, p.y, p.x, d.get("length", 0.0)))
    if not cands:
        return None
    xy = np.array([[c[3], c[2]] for c in cands])
    xy = xy - xy.mean(axis=0)
    eje = np.linalg.svd(xy, full_matrices=False)[2][0]
    proy = xy @ eje
    orden = np.argsort(np.abs(proy - np.median(proy)))
    for i in orden:
        if cands[i][4] >= 40:
            return cands[i]
    return cands[orden[0]]


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    g = red.cargar()
    barrios = leer_csv(SEMILLA / "barrios.csv")
    vias = {r["nombre"]: r for r in leer_csv(SEMILLA / "vias.csv")}
    nombres_barrio = {norm(b["nombre"]) for b in barrios} | {sin_articulo(b["nombre"]) for b in barrios}

    filas, fuentes, fuera = [], [], []

    def anotar_fuera(nombre, motivo):
        fuera.append((nombre, motivo))

    # 1. Apodos de vías existentes
    for nombre, alias in APODOS_VIAS.items():
        v = vias.get(nombre)
        if v is None:
            anotar_fuera(nombre, "no está en vias.csv")
            continue
        filas.append(dict(nombre=nombre, alias=alias, tipo="via", lat=v["lat"], lon=v["lon"],
                          osm_u=v["osm_u"], osm_v=v["osm_v"], origen="geocodificado"))
        fuentes.append(dict(nombre=nombre, fuente="vias.csv", consulta="(fila existente de vias.csv)",
                            osm_tipo="edge", osm_id=f"{v['osm_u']}-{v['osm_v']}", display_name=nombre, metros_a_la_red=""))

    # 2. Vías nuevas desde el grafo
    for nombre, alias, patron in VIAS_NUEVAS:
        r = arista_media(g, patron)
        if r is None:
            anotar_fuera(nombre, f"ninguna arista del grafo con name ~ {patron}")
            continue
        u, v, lat, lon, _ = r
        filas.append(dict(nombre=nombre, alias=alias, tipo="via", lat=f"{lat:.6f}", lon=f"{lon:.6f}",
                          osm_u=u, osm_v=v, origen="geocodificado"))
        fuentes.append(dict(nombre=nombre, fuente="grafo", consulta=patron, osm_tipo="edge", osm_id=f"{u}-{v}",
                            display_name=nombre, metros_a_la_red=""))

    # 3. Sitios y veredas desde Nominatim
    for nombre, alias, tipo, consulta, tokens in SITIOS:
        res = nominatim(consulta)
        if res is None:
            anotar_fuera(nombre, f"sin respuesta de Nominatim para «{consulta}» y sin caché")
            continue
        x = elegir_resultado(res, tokens)
        if x is None:
            motivo = "Nominatim no devolvió un resultado que lleve " + "/".join(tokens)
            if res:
                motivo += f" (devolvió: {res[0]['display_name'].split(',')[0]})"
            else:
                motivo += " (respuesta vacía)"
            anotar_fuera(nombre, motivo)
            continue
        filas.append(dict(nombre=nombre, alias=alias, tipo=tipo, lat=f"{float(x['lat']):.6f}",
                          lon=f"{float(x['lon']):.6f}", osm_u="", osm_v="", origen="geocodificado"))
        fuentes.append(dict(nombre=nombre, fuente="nominatim", consulta=consulta, osm_tipo=x["osm_type"],
                            osm_id=x["osm_id"], display_name=x["display_name"], metros_a_la_red=""))

    # 4. Validaciones
    ok, ok_fuentes = [], []
    reservados = {norm(n): n for n in vias} | {sin_articulo(n): n for n in vias}
    vistos = {}      # apodo normalizado -> nombre del lugar
    log = []
    for fila, fu in zip(filas, fuentes):
        nombre = fila["nombre"]
        lat, lon = float(fila["lat"]), float(fila["lon"])
        if not (LON_MIN <= lon <= LON_MAX and LAT_MIN <= lat <= LAT_MAX):
            anotar_fuera(nombre, f"fuera del área ({lat}, {lon})")
            continue
        _, _, m = red.arista_cercana(g, lat, lon)
        fu["metros_a_la_red"] = f"{m:.1f}"
        if m > MAX_METROS:
            anotar_fuera(nombre, f"a {m:.0f} m de la red vial (máximo {MAX_METROS:.0f})")
            continue
        if fila["tipo"] == "via" and not g.has_edge(int(fila["osm_u"]), int(fila["osm_v"])):
            anotar_fuera(nombre, "la arista (osm_u, osm_v) no existe en el grafo")
            continue
        if fila["tipo"] != "via":
            n = norm(nombre)
            if n in nombres_barrio or sin_articulo(nombre) in nombres_barrio or n in reservados or sin_articulo(nombre) in reservados:
                anotar_fuera(nombre, "el nombre coincide con un barrio o una vía existente")
                continue
        claves = []
        for a in [a for a in fila["alias"].split("|") if a]:
            claves.append(a)
        podados = []
        for a in claves:
            k, k2 = norm(a), sin_articulo(a)
            propio = {norm(nombre), sin_articulo(nombre)}
            if k in propio or k2 in propio:
                continue                       # repite el nombre canónico: se omite sin más
            choque = None
            for kk in {k, k2}:
                if kk in nombres_barrio:
                    choque = "barrio"
                elif kk in reservados and reservados[kk] != nombre:
                    choque = f"vía «{reservados[kk]}»"
                elif kk in vistos and vistos[kk] != nombre:
                    choque = f"lugar «{vistos[kk]}»"
            if choque:
                log.append(f"apodo «{a}» de «{nombre}» choca con {choque}: se quita")
                continue
            podados.append(a)
        for a in podados:
            vistos[norm(a)] = nombre
            vistos[sin_articulo(a)] = nombre
        vistos.setdefault(norm(nombre), nombre)
        vistos.setdefault(sin_articulo(nombre), nombre)
        fila["alias"] = "|".join(podados)
        if "," in fila["alias"] or "," in nombre:
            anotar_fuera(nombre, "coma en nombre o apodo")
            continue
        ok.append(fila)
        ok_fuentes.append(fu)

    # Duplicados por objeto OSM (dos lugares con el mismo osm_id)
    por_id = {}
    for fila, fu in zip(ok, ok_fuentes):
        if fu["fuente"] == "nominatim":
            por_id.setdefault((fu["osm_tipo"], fu["osm_id"]), []).append(fila["nombre"])
    dup = {k: v for k, v in por_id.items() if len(v) > 1}

    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "alias", "tipo", "lat", "lon", "osm_u", "osm_v", "origen"])
        w.writeheader()
        w.writerows(ok)
    with open(SALIDA_FUENTES, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nombre", "fuente", "consulta", "osm_tipo", "osm_id", "display_name",
                                          "metros_a_la_red"])
        w.writeheader()
        w.writerows(ok_fuentes)

    por_tipo = {}
    for fila in ok:
        por_tipo[fila["tipo"]] = por_tipo.get(fila["tipo"], 0) + 1
    print(f"{len(ok)} filas -> {SALIDA}  {por_tipo}")
    print(f"fuentes -> {SALIDA_FUENTES}")
    print("\nAvisos de apodos:")
    for l in log:
        print("  -", l)
    print("\nMismo objeto OSM en dos lugares:", dup or "ninguno")
    print(f"\nNo ubicados o descartados ({len(fuera)}):")
    for n, m in fuera:
        print(f"  - {n}: {m}")
    d = [float(fu["metros_a_la_red"]) for fu in ok_fuentes]
    print(f"\nDistancia a la red: máx {max(d):.0f} m, mediana {np.median(d):.0f} m")


if __name__ == "__main__":
    main()
