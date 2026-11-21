"""Zonas con datos censales: lectura, respaldo sin censo y topes T_z y S_z (B.2 y B.3)."""
from __future__ import annotations

import csv
import math
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

from triage import config, entrada_datos, geo
from triage.geo import Zona, numero

RAIZ = Path(__file__).resolve().parent.parent
SEMILLA_BARRIOS = RAIZ / "datos" / "semilla" / "barrios.csv"
TIPOS = ("barrio", "vereda", "albergue")
ESTADOS_CONFIRMADOS = ("confirmada_regla", "confirmada")
# Población sintética de la semilla: rango de personas por barrio (SUPUESTO, solo para pruebas).
PERSONAS_SINTETICAS = (1500, 12000)


def _entero(v) -> int | None:
    x = numero(v)
    return None if x is None or x < 0 else int(round(x))


def normalizar_zonas(filas: list[dict], params: dict | None = None) -> tuple[list[dict], list[dict]]:
    """Aplica B.2.1 y B.2.3. Devuelve (zonas válidas como dict, errores)."""
    p = config.completar(params) if params is None or "a_prior" not in params else params
    zonas, errores = [], []
    for i, crudo in enumerate(filas, start=1):
        if not isinstance(crudo, dict):
            errores.append({"fila": i, "campo": "fila", "motivo": "no_es_objeto", "rechazada": True})
            continue
        d = {entrada_datos.clave(k): v for k, v in crudo.items()}
        nombre = str(d.get("nombre") or "").strip()
        lat, lon = numero(d.get("lat") or d.get("latitud")), numero(d.get("lon") or d.get("longitud"))
        if not nombre or lat is None or lon is None:
            errores.append({"fila": i, "campo": "nombre/lat/lon", "motivo": "zona_invalida",
                            "rechazada": True})
            continue
        tipo = str(d.get("tipo") or "barrio").strip().lower()
        if tipo not in TIPOS:
            errores.append({"fila": i, "campo": "tipo", "motivo": f"tipo_desconocido: {tipo[:20]}",
                            "rechazada": False})
            tipo = "barrio"
        estimado = False
        th = numero(d.get("tamano_hogar"))
        if th is None or th <= 0:
            th = p["tamano_hogar_defecto"]
        poligono = geo.poligono_desde_wkt(d.get("geom_wkt"))
        area = numero(d.get("area_km2"))
        if (area is None or area <= 0) and poligono is not None:
            area = geo.area_km2(poligono)
        afect = numero(d.get("afectacion"))
        if afect is not None:
            afect = min(1.0, max(0.0, afect))
        critico = entrada_datos.parsear_bool(d.get("critico"))
        fuente = (str(d.get("fuente")).strip() or None) if d.get("fuente") is not None else None
        fecha = (str(d.get("fecha_corte")).strip() or None) if d.get("fecha_corte") is not None else None
        if not fuente or not fecha:
            estimado = True
        zonas.append({
            "nombre": nombre, "tipo": tipo, "comuna": (str(d.get("comuna")).strip() or None)
            if d.get("comuna") not in (None, "") else None,
            "lat": lat, "lon": lon, "geom_wkt": d.get("geom_wkt") if poligono is not None else None,
            "area_km2": area, "personas": _entero(d.get("personas")),
            "hogares": _entero(d.get("hogares")), "tamano_hogar": th, "afectacion": afect,
            "ocupacion": _entero(d.get("ocupacion")) if tipo == "albergue" else None,
            "critico": 1 if critico else 0, "fuente": fuente, "fecha_corte": fecha,
            "_estimado": estimado,
        })
    _respaldo_sin_censo(zonas, p)
    return zonas, errores


def _respaldo_sin_censo(zonas: list[dict], p: dict) -> None:
    """B.2.3: personas por mediana de la comuna (o de todas) y hogares por tamaño de hogar."""
    con_dato = [z for z in zonas if z["personas"] is not None]
    por_comuna: dict = {}
    for z in con_dato:
        por_comuna.setdefault(z["comuna"], []).append(z["personas"])
    todas = [z["personas"] for z in con_dato]
    afect_comuna: dict = {}
    for z in zonas:
        if z["afectacion"] is not None and z["comuna"]:
            afect_comuna.setdefault(z["comuna"], []).append(z["afectacion"])
    for z in zonas:
        if z["personas"] is None:
            z["_estimado"] = True
            if z["comuna"] in por_comuna and z["comuna"]:
                z["personas"] = int(statistics.median(por_comuna[z["comuna"]]))
            elif todas:
                z["personas"] = int(statistics.median(todas))
        if z["hogares"] is None:
            z["_estimado"] = True
            if z["personas"] is not None:
                z["hogares"] = int(round(z["personas"] / z["tamano_hogar"]))
        if z["afectacion"] is None:
            vals = afect_comuna.get(z["comuna"]) if z["comuna"] else None
            z["afectacion"] = float(np.mean(vals)) if vals else p["a_prior"]
        z["calidad_dato"] = "estimado" if z.pop("_estimado") else "fuente"


def leer_zonas(ruta, params: dict | None = None) -> tuple[list[dict], list[dict]]:
    filas, errores = entrada_datos.leer_tabla(ruta)
    zonas, errs = normalizar_zonas([f for f in filas if f is not None], params)
    return zonas, errores + errs


def zonas_desde_semilla(params: dict | None = None, ruta=SEMILLA_BARRIOS) -> list[dict]:
    """Zonas de datos/semilla/barrios.csv con población sintética (semilla 2026, 'estimado')."""
    p = config.completar(params) if params is None or "semilla" not in params else params
    rng = np.random.default_rng(p["semilla"])
    filas = []
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for d in csv.DictReader(f):
            filas.append({"nombre": d.get("nombre"), "comuna": d.get("comuna"),
                          "lat": d.get("lat"), "lon": d.get("lon"),
                          "personas": int(rng.integers(PERSONAS_SINTETICAS[0],
                                                       PERSONAS_SINTETICAS[1] + 1)),
                          "fuente": "sintetico (semilla 2026)"})
    zonas, _ = normalizar_zonas(filas, p)
    for z in zonas:
        z["calidad_dato"] = "estimado"
    return zonas


COLUMNAS = ("nombre", "tipo", "comuna", "lat", "lon", "geom_wkt", "area_km2", "personas", "hogares",
            "tamano_hogar", "afectacion", "ocupacion", "critico", "calidad_dato", "fuente",
            "fecha_corte")


def cargar_zonas(con: sqlite3.Connection, zonas: list[dict], commit: bool = True) -> list[int]:
    """Inserta o actualiza (por nombre y tipo) las zonas. No toca el estado dinámico."""
    ids = []
    for z in zonas:
        valores = [z.get(c) for c in COLUMNAS]
        fila = con.execute("SELECT id FROM zonas WHERE nombre=? AND tipo=?",
                           (z["nombre"], z.get("tipo", "barrio"))).fetchone()
        if fila:
            asignacion = ", ".join(f"{c}=?" for c in COLUMNAS)
            con.execute(f"UPDATE zonas SET {asignacion} WHERE id=?", valores + [fila["id"]])
            ids.append(fila["id"])
        else:
            cur = con.execute(f"INSERT INTO zonas({', '.join(COLUMNAS)}) "
                              f"VALUES ({', '.join('?' * len(COLUMNAS))})", valores)
            ids.append(cur.lastrowid)
    if commit:
        con.commit()
    return ids


def zonas_de_base(con: sqlite3.Connection) -> list[Zona]:
    return [Zona.desde_fila(f) for f in con.execute("SELECT * FROM zonas ORDER BY id")]


def zona_por_id(con: sqlite3.Connection, zona_id) -> Zona | None:
    if zona_id is None:
        return None
    f = con.execute("SELECT * FROM zonas WHERE id=?", (zona_id,)).fetchone()
    return Zona.desde_fila(f) if f else None


def _tamano_hogar(z: Zona, p: dict) -> float:
    th = numero(z.tamano_hogar)
    return th if th and th > 0 else p["tamano_hogar_defecto"]


def hogares_afectados(z: Zona, params: dict | None = None) -> float:
    """H_af,z = hogares_z × a_z (0 si no hay datos)."""
    p = params or config.PARAMETROS_DEFECTO
    hogares = numero(z.hogares)
    if hogares is None:
        personas = numero(z.personas)
        hogares = personas / _tamano_hogar(z, p) if personas is not None else 0.0
    a = numero(z.afectacion)
    a = p["a_prior"] if a is None else min(1.0, max(0.0, a))
    return max(0.0, hogares * a)


def densidad(z: Zona) -> float | None:
    """rho_z = personas / km² (None sin área)."""
    personas, area = numero(z.personas), numero(z.area_km2)
    if personas is None or not area or area <= 0:
        return None
    return personas / area


def tope_familias(z: Zona, params: dict | None = None) -> int:
    """T_z (B.3.3)."""
    p = params or config.PARAMETROS_DEFECTO
    ocup = numero(z.ocupacion)
    if z.tipo == "albergue" and ocup is not None:
        t = math.ceil(ocup / _tamano_hogar(z, p) * (1 + p["delta"]))
    else:
        t = math.ceil(hogares_afectados(z, p) * (1 + p["delta"]))
    return int(max(t, p["T_min"]))


def tope_solicitudes(z: Zona, params: dict | None = None) -> int:
    """S_z (B.3.5)."""
    p = params or config.PARAMETROS_DEFECTO
    f_bar = p["f_bar"] if p["f_bar"] > 0 else 1
    return int(max(p["S_min"], math.ceil(p["m"] * tope_familias(z, p) / f_bar)))


def cupo_consumido(con: sqlite3.Connection, zona_id, ahora: datetime, params: dict | None = None,
                   excluir_id=None) -> int:
    """C_z: familias efectivas confirmadas de la zona en el ciclo vigente (B.3.4)."""
    p = params or config.PARAMETROS_DEFECTO
    desde = entrada_datos.a_iso(ahora - timedelta(hours=p["ciclo_h"]))
    hasta = entrada_datos.a_iso(ahora)
    fila = con.execute(
        "SELECT COALESCE(SUM(familias_efectivas), 0) FROM solicitudes WHERE zona_id=? "
        "AND estado IN (?, ?) AND recibida_en > ? AND recibida_en <= ? AND id IS NOT ?",
        (zona_id, *ESTADOS_CONFIRMADOS, desde, hasta, excluir_id)).fetchone()
    return int(fila[0] or 0)
