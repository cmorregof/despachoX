"""Datos de prueba en `datos/semilla/`. Todo es sintético y sale de una semilla fija.

Uso:
    python -m despacho.semilla                 # escribe los CSV (barrios solo si falta)
    python -m despacho.semilla --cargar        # además crea la base y la llena
    python -m despacho.semilla --cargar --reiniciar   # borra lo que haya en la base antes de llenar
    python -m despacho.semilla --barrios       # vuelve a bajar los barrios de OpenStreetMap

Los barrios y sus comunas vienen de OpenStreetMap. Los puntos, acopios, vehículos, lotes y
pedidos son inventados: ninguno corresponde a una bodega, una organización o una persona real.
`vias.csv` lo genera `despacho/vias.py`.

En los CSV los tiempos son relativos (horas desde la carga) para que la semilla no envejezca;
al cargar se convierten en fechas ISO 8601.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from datos import db
from despacho import matriz, red

SEMILLA = 2026
DIR = Path(__file__).resolve().parent.parent / "datos" / "semilla"
TABLAS = ("paquetes", "paradas", "planes", "pedidos", "cierres", "lotes", "vehiculos", "acopios",
          "puntos", "bitacora")

# Ubicaciones inventadas de los dos acopios; se ajustan a la vía apta para camión más cercana.
ACOPIOS = [("Acopio Oriente (sintético)", 5.0370, -75.4400, 1),
           ("Acopio Occidente (sintético)", 5.0790, -75.5210, 0)]
VEHICULOS = [("Camión 1", "camion", 3000, 1), ("Camión 2", "camion", 2000, 2),
             ("Campero 1", "campero", 600, 1), ("Campero 2", "campero", 600, 2),
             ("Moto 1", "moto", 40, 2)]
NO_PERECEDEROS = ["arroz", "frijol", "lenteja", "aceite", "panela", "agua", "harina de maíz"]
PERECEDEROS = ["leche", "pan", "huevos", "fruta", "verdura", "pollo"]
CON_FRIO = {"pollo", "leche"}            # solo salen del acopio que tiene frío
KG_POR_FAMILIA = {"arroz": 2, "frijol": 1, "lenteja": 1, "aceite": 1, "panela": 0.5, "agua": 3,
                  "harina de maíz": 1, "leche": 2, "pan": 0.5, "huevos": 1, "fruta": 1.5,
                  "verdura": 1.5, "pollo": 1}
TIPOS_PUNTO = ["Salón comunal", "Albergue temporal", "Comedor comunitario", "Punto de entrega"]


def _escribir(nombre: str, campos: list[str], filas: list[dict]) -> None:
    DIR.mkdir(parents=True, exist_ok=True)
    with open(DIR / nombre, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


def _leer(nombre: str) -> list[dict]:
    with open(DIR / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def barrios() -> int:
    """barrios.csv (nombre, comuna, lat, lon) desde los lugares y las comunas de OpenStreetMap."""
    import geopandas as gpd
    import osmnx as ox

    ox.settings.use_cache = True
    ox.settings.cache_folder = str(red.CACHE / "http")
    ox.settings.requests_timeout = 120

    def insistir(f):
        for intento in range(1, red.INTENTOS + 1):
            try:
                red._evitar_ip_caida()
                return f()
            except Exception as e:  # noqa: BLE001
                print(f"intento {intento} falló: {type(e).__name__}", file=sys.stderr, flush=True)
                if intento == red.INTENTOS:
                    raise
                time.sleep(8)

    lugar = red.LUGARES[0]
    b = insistir(lambda: ox.features_from_place(lugar, {"place": ["suburb", "neighbourhood", "quarter"]}))
    a = insistir(lambda: ox.features_from_place(lugar, {"boundary": "administrative"}))
    b = b[b["name"].notna()].copy()
    b["geometry"] = b.geometry.representative_point()
    a = a[a.geometry.geom_type.isin(["Polygon", "MultiPolygon"]) & (a["admin_level"] == "8")
          & a["name"].fillna("").str.startswith("Comuna")][["name", "geometry"]]
    a = a.rename(columns={"name": "comuna"})
    j = gpd.sjoin(b[["name", "geometry"]], a, how="left", predicate="within")
    filas, vistos = [], set()
    for _, r in j.sort_values("name").iterrows():
        if r["name"] in vistos:
            continue
        vistos.add(r["name"])
        comuna = r["comuna"].replace("Comuna ", "") if isinstance(r["comuna"], str) else ""
        filas.append({"nombre": r["name"], "comuna": comuna,
                      "lat": round(r.geometry.y, 6), "lon": round(r.geometry.x, 6)})
    _escribir("barrios.csv", ["nombre", "comuna", "lat", "lon"], filas)
    return len(filas)


def generar() -> None:
    """puntos, acopios, vehiculos, lotes y pedidos, con semilla fija."""
    rng = random.Random(SEMILLA)
    g = red.cargar()
    _, _, _, red_camion = matriz._red_del_tipo(g, "camion", set())

    # --- Puntos: 15 barrios urbanos pegados a la red vial, repartidos por comunas; tres críticos ---
    candidatos = []
    for b in _leer("barrios.csv"):
        if not b["comuna"]:
            continue
        _, d = red.nodo_cercano(g, float(b["lat"]), float(b["lon"]))
        if d <= 150:
            candidatos.append(b)
    rng.shuffle(candidatos)
    elegidos, por_comuna = [], {}
    for b in candidatos:                       # como máximo dos por comuna
        if por_comuna.get(b["comuna"], 0) < 2 and len(elegidos) < 15:
            elegidos.append(b)
            por_comuna[b["comuna"]] = por_comuna.get(b["comuna"], 0) + 1
    elegidos.sort(key=lambda b: b["nombre"])
    criticos = set(rng.sample(range(len(elegidos)), 3))
    puntos = []
    for i, b in enumerate(elegidos):
        tipo = "Albergue temporal" if i in criticos else rng.choice(TIPOS_PUNTO)
        puntos.append({"id": i + 1, "nombre": f"{tipo} {b['nombre']}", "barrio": b["nombre"],
                       "comuna": b["comuna"], "lat": b["lat"], "lon": b["lon"],
                       "critico": int(i in criticos)})
    _escribir("puntos.csv", ["id", "nombre", "barrio", "comuna", "lat", "lon", "critico"], puntos)

    # --- Acopios y vehículos ---
    acopios = []
    for i, (nombre, lat, lon, frio) in enumerate(ACOPIOS, start=1):
        n, _ = red.nodo_cercano(g, lat, lon, red_camion)
        acopios.append({"id": i, "nombre": nombre, "lat": round(g.nodes[n]["y"], 6),
                        "lon": round(g.nodes[n]["x"], 6), "tiene_frio": frio})
    _escribir("acopios.csv", ["id", "nombre", "lat", "lon", "tiene_frio"], acopios)
    vehiculos = [{"id": i, "nombre": n, "tipo": t, "capacidad_kg": c, "acopio_id": a,
                  "lat": acopios[a - 1]["lat"], "lon": acopios[a - 1]["lon"], "estado": "libre"}
                 for i, (n, t, c, a) in enumerate(VEHICULOS, start=1)]
    _escribir("vehiculos.csv", ["id", "nombre", "tipo", "capacidad_kg", "acopio_id", "lat", "lon", "estado"],
              vehiculos)

    # --- Pedidos: 20; los puntos críticos piden con urgencia 3 ---
    pedidos = []
    orden_puntos = [p["id"] for p in puntos] + rng.sample([p["id"] for p in puntos], 5)
    for i, punto_id in enumerate(orden_puntos, start=1):
        p = puntos[punto_id - 1]
        familias = rng.choice([4, 6]) if i in (7, 14) else rng.randint(10, 45)   # dos pedidos caben en la moto
        productos = rng.sample(NO_PERECEDEROS, 1 if familias < 8 else rng.randint(2, 3))
        if rng.random() < 0.6:
            productos += rng.sample(PERECEDEROS, 1 if familias < 8 else rng.randint(1, 2))
        lineas = [{"producto": x, "kg": round(familias * KG_POR_FAMILIA[x], 1)} for x in productos]
        urgencia = 3 if p["critico"] else rng.choice([1, 2, 2, 3])
        pedidos.append({
            "id": i, "creado_hace_min": rng.randint(5, 180), "punto_id": punto_id, "familias": familias,
            "kg_estimado": round(sum(l["kg"] for l in lineas), 1),
            "productos": json.dumps(lineas, ensure_ascii=False), "urgencia": urgencia,
            "limite_en_horas": {3: 4, 2: 10, 1: 20}[urgencia],
            "estado": "nuevo" if i in (18, 19, 20) else "confirmado",
            "texto_original": f"Somos {familias} familias en {p['barrio']}, necesitamos "
                              + ", ".join(productos) + "."})
    _escribir("pedidos.csv", ["id", "creado_hace_min", "punto_id", "familias", "kg_estimado", "productos",
                              "urgencia", "limite_en_horas", "estado", "texto_original"], pedidos)

    # --- Lotes: alcanzan para casi todo; el pollo queda corto a propósito ---
    pedido_kg: dict[str, float] = {}
    for p in pedidos:
        for l in json.loads(p["productos"]):
            pedido_kg[l["producto"]] = pedido_kg.get(l["producto"], 0) + l["kg"]
    lotes = []
    for producto in NO_PERECEDEROS + PERECEDEROS:
        perecedero = producto in PERECEDEROS
        total = max(60.0, pedido_kg.get(producto, 0)) * (0.6 if producto == "pollo" else 1.3)
        for acopio_id in (1, 2):
            if producto in CON_FRIO and not acopios[acopio_id - 1]["tiene_frio"]:
                continue
            partes = 2 if perecedero else 1          # dos lotes con vencimientos distintos
            comparte = 1 if producto in CON_FRIO else 2
            for _ in range(partes):
                lotes.append({
                    "id": len(lotes) + 1, "acopio_id": acopio_id, "producto": producto,
                    "kg": round(total / comparte / partes, 1), "perecedero": int(perecedero),
                    "vence_en_horas": rng.randint(6, 48) if perecedero else "",
                    "empaque_activo": int(producto in ("fruta", "verdura") and rng.random() < 0.5)})
    _escribir("lotes.csv", ["id", "acopio_id", "producto", "kg", "perecedero", "vence_en_horas",
                            "empaque_activo"], lotes)


def cargar(reiniciar: bool = False, con=None) -> dict[str, int]:
    """Crea la base (si no existe) y la llena con la semilla. Devuelve filas por tabla."""
    con = con or db.conectar()
    hay = sum(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLAS)
    if hay and not reiniciar:
        raise SystemExit("La base ya tiene datos. Usa --reiniciar para borrarlos y cargar la semilla.")
    ahora = datetime.now(db.BOGOTA).replace(microsecond=0)
    iso = lambda horas: (ahora + timedelta(hours=float(horas))).isoformat(timespec="seconds")
    with con:
        for t in TABLAS:
            con.execute(f"DELETE FROM {t}")
        con.executemany("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                        [(r["id"], r["nombre"], r["barrio"], r["comuna"], r["lat"], r["lon"], r["critico"])
                         for r in _leer("puntos.csv")])
        con.executemany("INSERT INTO acopios(id,nombre,lat,lon,tiene_frio) VALUES (?,?,?,?,?)",
                        [(r["id"], r["nombre"], r["lat"], r["lon"], r["tiene_frio"]) for r in _leer("acopios.csv")])
        con.executemany("INSERT INTO vehiculos(id,nombre,tipo,capacidad_kg,acopio_id,lat,lon,estado) "
                        "VALUES (?,?,?,?,?,?,?,?)",
                        [(r["id"], r["nombre"], r["tipo"], r["capacidad_kg"], r["acopio_id"], r["lat"],
                          r["lon"], r["estado"]) for r in _leer("vehiculos.csv")])
        con.executemany("INSERT INTO lotes(id,acopio_id,producto,kg,perecedero,vence_en,empaque_activo) "
                        "VALUES (?,?,?,?,?,?,?)",
                        [(r["id"], r["acopio_id"], r["producto"], r["kg"], r["perecedero"],
                          iso(r["vence_en_horas"]) if r["vence_en_horas"] else None, r["empaque_activo"])
                         for r in _leer("lotes.csv")])
        con.executemany("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,"
                        "limite_en,estado,texto_original) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [(r["id"], iso(-float(r["creado_hace_min"]) / 60), r["punto_id"], r["familias"],
                          r["kg_estimado"], r["productos"], r["urgencia"], iso(r["limite_en_horas"]),
                          r["estado"], r["texto_original"]) for r in _leer("pedidos.csv")])
    db.anotar(con, "semilla", "cargar semilla", f"semilla {SEMILLA}")
    return {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in ("puntos", "acopios", "vehiculos", "lotes", "pedidos")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Genera la semilla sintética y, si se pide, la carga en la base.")
    ap.add_argument("--cargar", action="store_true", help="crea la base y la llena")
    ap.add_argument("--reiniciar", action="store_true", help="borra los datos que haya antes de cargar")
    ap.add_argument("--barrios", action="store_true", help="vuelve a bajar barrios.csv de OpenStreetMap")
    args = ap.parse_args(argv)
    if args.barrios or not (DIR / "barrios.csv").exists():
        print(f"barrios.csv: {barrios()} barrios", file=sys.stderr)
    generar()
    print(f"CSV escritos en {DIR}", file=sys.stderr)
    if args.cargar:
        print(cargar(args.reiniciar))
    return 0


if __name__ == "__main__":
    sys.exit(main())
