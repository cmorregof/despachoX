"""De «por la siria, llegando a chinchiná» a un punto del mapa que una persona confirma.

Orden de la decisión (lo barato y seguro primero):
  1. coincidencia exacta con un apodo del nomenclátor            -> metodo 'exacto'
  2. coincidencia por parecido (errores de tipeo, palabras de más) -> metodo 'parecido'
  3. si hay duda, un modelo de lenguaje ELIGE entre los candidatos  -> metodo 'modelo'
  4. si nada sirve, se pide un pin de ubicación o lo ubica el despachador

El modelo nunca inventa coordenadas: solo puede devolver el id de un candidato o «ninguno».
Toda ubicación nace como 'propuesta' y la confirma quien reportó o el despachador. Cada
confirmación enseña un apodo nuevo, así la siguiente vez la respuesta es exacta y sin modelo.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
import unicodedata
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable

from datos import db

SEMILLA = Path(__file__).resolve().parent.parent / "datos" / "semilla"
UMBRAL_SEGURO = 0.90        # desde aquí se propone un solo lugar sin consultar al modelo
UMBRAL_CANDIDATO = 0.55     # por debajo no se ofrece como alternativa
MARGEN = 0.08               # si el segundo está así de cerca del primero, hay ambigüedad
MAX_CANDIDATOS = 5
MODELO = os.environ.get("DESPACHOX_MODELO_LUGARES") or "claude-haiku-5-5"   # vacío en .env cuenta como ausente

# Palabras que acompañan al lugar y no lo distinguen.
RELLENO = {"el", "la", "los", "las", "de", "del", "en", "por", "a", "al", "barrio", "sector", "via",
           "carretera", "llegando", "saliendo", "subiendo", "bajando", "cerca", "frente", "junto",
           "hacia", "para", "antes", "despues", "pasando", "entrada", "salida", "antigua", "vieja",
           "nueva", "avenida", "av", "avda", "y", "que", "va", "desde", "hasta", "ahi", "alla", "aqui", "zona", "parte"}


def normalizar(texto: str | None) -> str:
    """Minúsculas, sin tildes ni signos, espacios simples."""
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9ñ ]", " ", t).split())


def _nucleo(texto: str) -> str:
    """El texto normalizado sin palabras de relleno. Si queda vacío, devuelve el original."""
    palabras = [p for p in normalizar(texto).split() if p not in RELLENO]
    return " ".join(palabras) or normalizar(texto)


@dataclass
class Candidato:
    lugar_id: int
    nombre: str
    tipo: str
    lat: float
    lon: float
    puntaje: float
    osm_u: int | None = None
    osm_v: int | None = None
    punto_id: int | None = None


@dataclass
class Resultado:
    texto: str
    metodo: str                              # exacto, parecido, modelo, ninguno
    elegido: Candidato | None = None
    candidatos: list[Candidato] = field(default_factory=list)
    seguro: bool = False                     # True: basta un «¿es correcto?»; False: ofrecer opciones
    pregunta: str = ""                       # lo que el bot le dice a quien reportó
    ubicacion_id: int | None = None


def _parecido(consulta: str, alias: str) -> float:
    """Entre 0 y 1. Combina parecido de cadena y palabras compartidas; premia que el apodo
    completo aparezca dentro de lo que dijo la persona («derrumbe por la siria» contiene «siria»)."""
    if not consulta or not alias:
        return 0.0
    if consulta == alias:
        return 1.0
    pc, pa = set(consulta.split()), set(alias.split())
    if pa and pa <= pc:                       # todas las palabras del apodo están en la consulta
        return 0.93 if len(alias) >= 4 else 0.70
    if pc and pc <= pa and len(consulta) >= 5:   # la persona dijo solo parte del nombre
        return 0.90
    razon = SequenceMatcher(None, consulta, alias).ratio()
    # palabra a palabra, para tolerar un error de tipeo dentro de una frase larga
    por_palabra = [max((SequenceMatcher(None, a, c).ratio() for c in pc), default=0.0) for a in pa]
    cobertura = sum(por_palabra) / len(por_palabra) if por_palabra else 0.0
    return max(razon, 0.9 * cobertura if min(por_palabra, default=0) >= 0.75 else 0.0)


def _filas(con: sqlite3.Connection, tipos: tuple[str, ...] | None) -> list[sqlite3.Row]:
    if tipos:
        marcas = ",".join("?" * len(tipos))
        return con.execute(f"SELECT * FROM lugares WHERE tipo IN ({marcas})", tipos).fetchall()
    return con.execute("SELECT * FROM lugares").fetchall()


def buscar(con: sqlite3.Connection, texto: str, tipos: tuple[str, ...] | None = None) -> list[Candidato]:
    """Candidatos ordenados por puntaje, uno por lugar físico (el mejor de sus apodos)."""
    consulta, completa = _nucleo(texto), normalizar(texto)
    mejores: dict[tuple, Candidato] = {}
    for r in _filas(con, tipos):
        alias = r["alias"]
        p = max(_parecido(consulta, _nucleo(alias)), _parecido(completa, alias))
        if r["origen"] == "aprendido" and p >= 0.99:
            p = 1.0
        if p < UMBRAL_CANDIDATO:
            continue
        clave = (r["nombre"], r["tipo"], round(r["lat"], 5), round(r["lon"], 5))
        if clave not in mejores or p > mejores[clave].puntaje:
            mejores[clave] = Candidato(r["id"], r["nombre"], r["tipo"], r["lat"], r["lon"], round(p, 3),
                                       r["osm_u"], r["osm_v"], r["punto_id"])
    return sorted(mejores.values(), key=lambda c: (-c.puntaje, c.nombre))[:MAX_CANDIDATOS]


def elegir_con_modelo(texto: str, contexto: str, candidatos: list[Candidato]) -> int | None:
    """Pide al modelo que elija UNO de los candidatos o ninguno. Devuelve lugar_id o None.
    Sin clave, sin red o con respuesta rara devuelve None: el flujo sigue con las opciones.
    Con DESPACHOX_SIN_RED=1 ni lo intenta (acopio aislado, docs/SIN_CONEXION.md)."""
    if os.environ.get("DESPACHOX_SIN_RED", "").strip().lower() in ("1", "si", "sí", "true"):
        return None
    try:
        import anthropic
        cliente = anthropic.Anthropic()
        lista = "\n".join(f"{c.lugar_id}: {c.nombre} ({c.tipo})" for c in candidatos)
        r = cliente.messages.create(
            model=MODELO, max_tokens=20,
            system=("Eres un ayudante que ubica lugares de Manizales, Colombia. Te doy lo que dijo una "
                    "persona y una lista numerada de lugares conocidos. Responde SOLO con el número del "
                    "lugar al que se refiere, o con la palabra ninguno si no es claro o no está en la "
                    "lista. No expliques. No inventes lugares."),
            messages=[{"role": "user", "content":
                       f"Mensaje completo: {contexto or texto}\nLugar mencionado: {texto}\n\nLugares:\n{lista}"}])
        dicho = r.content[0].text.strip().lower()
        m = re.search(r"\d+", dicho)
        if m and int(m.group()) in {c.lugar_id for c in candidatos}:
            return int(m.group())
    except Exception:
        pass
    return None


def resolver(con: sqlite3.Connection, texto: str, *, tabla: str | None = None, fila_id: int | None = None,
             contexto: str = "", tipos: tuple[str, ...] | None = None,
             elegir: Callable[[str, str, list[Candidato]], int | None] | None = elegir_con_modelo) -> Resultado:
    """Propone dónde queda `texto`. Si se dan `tabla` y `fila_id`, deja la propuesta en `ubicaciones`.

    tipos: para un cierre vial conviene ('via', 'sitio'); para un pedido, ('barrio','punto','sitio','vereda').
    elegir: función que desempata con un modelo; pásale None para no usar modelo.
    """
    res = Resultado(texto=texto, metodo="ninguno")
    res.candidatos = buscar(con, texto, tipos)
    c = res.candidatos
    if c:
        claro = c[0].puntaje >= UMBRAL_SEGURO and (len(c) == 1 or c[0].puntaje - c[1].puntaje >= MARGEN)
        if claro:
            res.elegido, res.seguro = c[0], True
            res.metodo = "exacto" if c[0].puntaje >= 0.999 else "parecido"
        elif elegir is not None:
            lugar_id = elegir(texto, contexto, c)
            if lugar_id is not None:
                res.elegido = next(x for x in c if x.lugar_id == lugar_id)
                res.metodo = "modelo"                 # lo eligió un modelo: nunca se da por seguro
    res.pregunta = _pregunta(res)
    if tabla and fila_id is not None:
        e = res.elegido
        cur = con.execute(
            "INSERT INTO ubicaciones(creado_en, tabla, fila_id, texto, lugar_id, lat, lon, metodo, puntaje, "
            "candidatos) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (db.ahora(), tabla, fila_id, texto, e.lugar_id if e else None, e.lat if e else None,
             e.lon if e else None, res.metodo, e.puntaje if e else None,
             json.dumps([asdict(x) for x in c], ensure_ascii=False)))
        con.commit()
        res.ubicacion_id = cur.lastrowid
    return res


def _pregunta(res: Resultado) -> str:
    if res.elegido and res.seguro:
        return f"Ubiqué «{res.texto}» en: {res.elegido.nombre} ({res.elegido.tipo}). ¿Es correcto?"
    if res.elegido:
        otros = [c.nombre for c in res.candidatos if c.lugar_id != res.elegido.lugar_id][:3]
        cola = f" Otras opciones: {', '.join(otros)}." if otros else ""
        return f"Creo que «{res.texto}» es {res.elegido.nombre} ({res.elegido.tipo}). ¿Sí?{cola}"
    if res.candidatos:
        return (f"No estoy seguro de dónde queda «{res.texto}». ¿Es alguno de estos? "
                + "; ".join(f"{i}. {c.nombre}" for i, c in enumerate(res.candidatos, 1))
                + ". Si no, envíame la ubicación con el clip del chat.")
    return (f"No conozco «{res.texto}». Envíame la ubicación con el clip del chat, "
            "o dime un barrio o una vía cercana.")


def _aplicar(con: sqlite3.Connection, u: sqlite3.Row, lat: float, lon: float,
             lugar: sqlite3.Row | None) -> None:
    """Lleva la ubicación confirmada a la fila del pedido o del cierre."""
    if u["tabla"] == "cierres":
        con.execute("UPDATE cierres SET lat=?, lon=?, osm_u=?, osm_v=? WHERE id=?",
                    (lat, lon, lugar["osm_u"] if lugar else None, lugar["osm_v"] if lugar else None,
                     u["fila_id"]))
        if lugar is not None:
            con.execute("UPDATE cierres SET lugar=? WHERE id=?", (lugar["nombre"], u["fila_id"]))
    elif lugar is not None and lugar["punto_id"] is not None:
        con.execute("UPDATE pedidos SET punto_id=? WHERE id=?", (lugar["punto_id"], u["fila_id"]))
    else:   # pedido en un lugar que aún no es punto de entrega: se crea el punto
        nombre = lugar["nombre"] if lugar else u["texto"]
        cur = con.execute("INSERT INTO puntos(nombre, barrio, lat, lon, critico) VALUES (?,?,?,?,0)",
                          (f"Punto de entrega {nombre}", nombre, lat, lon))
        con.execute("UPDATE pedidos SET punto_id=? WHERE id=?", (cur.lastrowid, u["fila_id"]))
        if lugar is not None:
            con.execute("UPDATE lugares SET punto_id=? WHERE nombre=? AND tipo=?",
                        (cur.lastrowid, lugar["nombre"], lugar["tipo"]))


def aprender(con: sqlite3.Connection, texto: str, lugar: sqlite3.Row) -> None:
    """Guarda lo que dijo la persona como apodo del lugar confirmado."""
    alias = _nucleo(texto)
    if not alias or alias == lugar["alias"]:
        return
    con.execute("INSERT OR IGNORE INTO lugares(nombre, alias, tipo, lat, lon, osm_u, osm_v, punto_id, "
                "origen, creado_en) VALUES (?,?,?,?,?,?,?,?, 'aprendido', ?)",
                (lugar["nombre"], alias, lugar["tipo"], lugar["lat"], lugar["lon"], lugar["osm_u"],
                 lugar["osm_v"], lugar["punto_id"], db.ahora()))


def confirmar(con: sqlite3.Connection, ubicacion_id: int, quien: str, lugar_id: int | None = None) -> bool:
    """Quien reportó o el despachador dice «sí». Con `lugar_id` elige otra de las opciones."""
    u = con.execute("SELECT * FROM ubicaciones WHERE id=?", (ubicacion_id,)).fetchone()
    if u is None:
        return False
    lugar = con.execute("SELECT * FROM lugares WHERE id=?", (lugar_id or u["lugar_id"],)).fetchone()
    if lugar is None:
        return False
    _aplicar(con, u, lugar["lat"], lugar["lon"], lugar)
    aprender(con, u["texto"], lugar)
    con.execute("UPDATE ubicaciones SET estado='confirmada', lugar_id=?, lat=?, lon=?, confirmado_por=?, "
                "confirmado_en=? WHERE id=?", (lugar["id"], lugar["lat"], lugar["lon"], quien, db.ahora(),
                                              ubicacion_id))
    db.anotar(con, quien, "ubicacion_confirmada", f"{u['tabla']} {u['fila_id']}: «{u['texto']}» = {lugar['nombre']}")
    return True


def corregir_con_pin(con: sqlite3.Connection, ubicacion_id: int, lat: float, lon: float, quien: str,
                     nombre: str | None = None) -> bool:
    """La persona envió su ubicación o el despachador movió el pin en el mapa. Eso manda sobre
    cualquier texto, y deja aprendido el apodo con esas coordenadas."""
    u = con.execute("SELECT * FROM ubicaciones WHERE id=?", (ubicacion_id,)).fetchone()
    if u is None:
        return False
    tipo = "via" if u["tabla"] == "cierres" else "sitio"
    alias = _nucleo(u["texto"])
    con.execute("INSERT OR IGNORE INTO lugares(nombre, alias, tipo, lat, lon, origen, creado_en) "
                "VALUES (?,?,?,?,?, 'aprendido', ?)", (nombre or u["texto"].strip(), alias, tipo, lat, lon,
                                                      db.ahora()))
    lugar = con.execute("SELECT * FROM lugares WHERE alias=? AND tipo=? AND lat=? AND lon=?",
                        (alias, tipo, lat, lon)).fetchone()
    _aplicar(con, u, lat, lon, lugar if u["tabla"] == "pedidos" else None)
    if u["tabla"] == "cierres":   # sin arista: despacho/cierres.py la busca por cercanía al recalcular
        con.execute("UPDATE cierres SET osm_u=NULL, osm_v=NULL WHERE id=?", (u["fila_id"],))
    con.execute("UPDATE ubicaciones SET estado='confirmada', lugar_id=?, lat=?, lon=?, metodo=?, "
                "confirmado_por=?, confirmado_en=? WHERE id=?",
                (lugar["id"], lat, lon, "pin" if quien != "despachador" else "despachador", quien,
                 db.ahora(), ubicacion_id))
    db.anotar(con, quien, "ubicacion_por_pin", f"{u['tabla']} {u['fila_id']}: «{u['texto']}» = {lat:.5f},{lon:.5f}")
    return True


def cargar_semilla(con: sqlite3.Connection, carpeta: Path = SEMILLA) -> int:
    """Llena `lugares` desde barrios.csv, vias.csv, puntos de la base y lugares_extra.csv.
    Se puede correr varias veces: no duplica. Devuelve cuántas filas hay al final."""
    def meter(nombre, alias, tipo, lat, lon, u=None, v=None, punto=None, origen="semilla"):
        con.execute("INSERT OR IGNORE INTO lugares(nombre, alias, tipo, lat, lon, osm_u, osm_v, punto_id, "
                    "origen, creado_en) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (nombre, normalizar(alias), tipo, float(lat), float(lon), u, v, punto, origen, db.ahora()))

    def leer(archivo):
        ruta = carpeta / archivo
        if not ruta.exists():
            return []
        with open(ruta, encoding="utf-8") as f:
            return list(csv.DictReader(f))

    puntos = {normalizar(r["barrio"]): r["id"] for r in con.execute("SELECT id, barrio FROM puntos") if r["barrio"]}
    for r in leer("barrios.csv"):
        meter(r["nombre"], r["nombre"], "barrio", r["lat"], r["lon"], punto=puntos.get(normalizar(r["nombre"])))
    for r in leer("vias.csv"):
        meter(r["nombre"], r["nombre"], "via", r["lat"], r["lon"], int(r["osm_u"]), int(r["osm_v"]))
    for r in con.execute("SELECT * FROM puntos").fetchall():
        meter(r["nombre"], r["nombre"], "punto", r["lat"], r["lon"], punto=r["id"])
    # lugares_extra.csv: nombre,alias,tipo,lat,lon,osm_u,osm_v,origen  (alias separados por |)
    for r in leer("lugares_extra.csv"):
        for alias in [r["nombre"]] + [a for a in (r.get("alias") or "").split("|") if a.strip()]:
            meter(r["nombre"], alias, r["tipo"], r["lat"], r["lon"],
                  int(r["osm_u"]) if r.get("osm_u") else None, int(r["osm_v"]) if r.get("osm_v") else None,
                  origen=r.get("origen") or "geocodificado")
    con.commit()
    return con.execute("SELECT COUNT(*) FROM lugares").fetchone()[0]


if __name__ == "__main__":   # python -m lugares.nomenclator "por la panamericana"
    import sys
    con = db.conectar()
    print("lugares en el nomenclátor:", cargar_semilla(con))
    for t in sys.argv[1:]:
        r = resolver(con, t, elegir=None)
        print(f"\n«{t}» -> {r.metodo}, seguro={r.seguro}\n  {r.pregunta}")
        for c in r.candidatos:
            print(f"   {c.puntaje:.2f}  {c.nombre} ({c.tipo})")
