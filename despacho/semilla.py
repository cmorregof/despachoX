"""Datos de prueba en `datos/semilla/`. Todo es sintético y sale de una semilla fija.

Uso:
    python -m despacho.semilla                 # escribe los CSV sintéticos (barrios solo si falta)
    python -m despacho.semilla --cargar        # crea la base y la llena con los CSV que ya existen
    python -m despacho.semilla --cargar --reiniciar   # borra lo que haya en la base antes de llenar
    python -m despacho.semilla --cargar --reiniciar --origen datos_privados/   # datos reales
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


ARCHIVOS = ("puntos.csv", "acopios.csv", "vehiculos.csv", "lotes.csv", "pedidos.csv")
OBLIGATORIAS = {
    "puntos.csv": ("id", "nombre", "lat", "lon"),
    "acopios.csv": ("id", "nombre", "lat", "lon"),
    "vehiculos.csv": ("id", "tipo", "capacidad_kg", "acopio_id"),
    "lotes.csv": ("id", "acopio_id", "producto", "kg"),
    "pedidos.csv": ("id", "punto_id"),
}
TIPOS_VEHICULO = ("camion", "campero", "moto", "a_pie")
ESTADOS_VEHICULO = ("libre", "en_ruta", "fuera")
ESTADOS_PEDIDO = ("nuevo", "confirmado", "asignado", "entregado", "descartado")


class ArchivoMalo(Exception):
    """Un CSV no pasa la validación. El mensaje dice archivo, fila y razón."""


def _validar(archivo: str, filas: list[dict], ahora: datetime) -> list[dict]:
    """Devuelve las filas listas para insertar o lanza ArchivoMalo con todas las razones."""
    errores: list[str] = []
    oeste, sur, este, norte = red.AREA
    if not filas:
        raise ArchivoMalo(f"{archivo}: no tiene filas")
    faltan = [c for c in OBLIGATORIAS[archivo] if c not in filas[0]]
    if faltan:
        raise ArchivoMalo(f"{archivo}: faltan las columnas {', '.join(faltan)}")
    vistos, limpias = set(), []

    for n, crudo in enumerate(filas, start=2):          # la fila 1 es la cabecera
        r = {k: (v or "").strip() for k, v in crudo.items() if k}
        mal = lambda razon: errores.append(f"{archivo}, fila {n}: {razon}")

        def entero(campo, minimo=None, opcional=False, defecto=None):
            if not r.get(campo):
                if not opcional:
                    mal(f"falta `{campo}`")
                return defecto
            try:
                v = int(float(r[campo]))
            except ValueError:
                mal(f"`{campo}` no es un número entero: «{r[campo]}»")
                return defecto
            if minimo is not None and v < minimo:
                mal(f"`{campo}` debe ser al menos {minimo}: «{r[campo]}»")
            return v

        def real(campo, positivo=False, opcional=False):
            if not r.get(campo):
                if not opcional:
                    mal(f"falta `{campo}`")
                return None
            try:
                v = float(r[campo].replace(",", "."))
            except ValueError:
                mal(f"`{campo}` no es un número: «{r[campo]}»")
                return None
            if positivo and v <= 0:
                mal(f"`{campo}` debe ser mayor que cero: «{r[campo]}»")
            return v

        def coordenadas(opcional=False):
            lat, lon = real("lat", opcional=opcional), real("lon", opcional=opcional)
            if lat is not None and lon is not None and not (sur <= lat <= norte and oeste <= lon <= este):
                mal(f"coordenadas fuera del área de la red ({lat}, {lon}); lat entre {sur} y {norte}, "
                    f"lon entre {oeste} y {este}. ¿Están invertidas?")
            return lat, lon

        def fecha(absoluta, relativa, factor_h, opcional=True):
            """Acepta una fecha ISO 8601 en `absoluta` o un tiempo relativo a la carga en `relativa`."""
            if r.get(absoluta):
                try:
                    d = datetime.fromisoformat(r[absoluta])
                except ValueError:
                    mal(f"`{absoluta}` no es una fecha legible (use 2026-11-21T14:30): «{r[absoluta]}»")
                    return None
                return (d if d.tzinfo else d.replace(tzinfo=db.BOGOTA)).isoformat(timespec="seconds")
            if r.get(relativa):
                try:
                    return (ahora + timedelta(hours=float(r[relativa]) * factor_h)).isoformat(timespec="seconds")
                except ValueError:
                    mal(f"`{relativa}` no es un número: «{r[relativa]}»")
                    return None
            if not opcional:
                mal(f"falta `{absoluta}` (o `{relativa}`)")
            return None

        ident = entero("id", minimo=1)
        if ident in vistos:
            mal(f"`id` repetido: {ident}")
        vistos.add(ident)
        if archivo == "puntos.csv":
            lat, lon = coordenadas()
            if not r.get("nombre"):
                mal("falta `nombre`")
            limpias.append((ident, r.get("nombre"), r.get("barrio") or None, r.get("comuna") or None, lat, lon,
                            entero("critico", opcional=True, defecto=0)))
        elif archivo == "acopios.csv":
            lat, lon = coordenadas()
            if not r.get("nombre"):
                mal("falta `nombre`")
            limpias.append((ident, r.get("nombre"), lat, lon, entero("tiene_frio", opcional=True, defecto=0)))
        elif archivo == "vehiculos.csv":
            if r.get("tipo") not in TIPOS_VEHICULO:
                mal(f"`tipo` desconocido: «{r.get('tipo')}». Valen: {', '.join(TIPOS_VEHICULO)}")
            estado = r.get("estado") or "libre"
            if estado not in ESTADOS_VEHICULO:
                mal(f"`estado` desconocido: «{estado}». Valen: {', '.join(ESTADOS_VEHICULO)}")
            lat, lon = coordenadas(opcional=True)
            limpias.append([ident, r.get("nombre") or f"Vehículo {ident}", r.get("tipo"),
                            real("capacidad_kg", positivo=True), entero("acopio_id", minimo=1), lat, lon, estado])
        elif archivo == "lotes.csv":
            if not r.get("producto"):
                mal("falta `producto`")
            perecedero = entero("perecedero", opcional=True, defecto=0)
            vence = fecha("vence_en", "vence_en_horas", 1.0)
            if perecedero and vence is None and not any("vence" in e and f"fila {n}:" in e for e in errores):
                mal("un lote perecedero necesita `vence_en` o `vence_en_horas`")
            limpias.append((ident, entero("acopio_id", minimo=1), r.get("producto"), real("kg", positivo=True),
                            perecedero, vence, entero("empaque_activo", opcional=True, defecto=0)))
        elif archivo == "pedidos.csv":
            urgencia = entero("urgencia", opcional=True, defecto=2)
            if urgencia not in (1, 2, 3):
                mal(f"`urgencia` debe ser 1, 2 o 3: «{r.get('urgencia')}»")
            estado = r.get("estado") or "nuevo"
            if estado not in ESTADOS_PEDIDO:
                mal(f"`estado` desconocido: «{estado}». Valen: {', '.join(ESTADOS_PEDIDO)}")
            productos = r.get("productos") or None
            if productos:
                try:
                    lineas = json.loads(productos)
                    if not all(float(l["kg"]) > 0 and str(l["producto"]) for l in lineas):
                        raise ValueError
                except (ValueError, TypeError, KeyError):
                    mal('`productos` debe ser JSON como [{"producto": "arroz", "kg": 20}] con kilos positivos')
            kg = real("kg_estimado", positivo=True, opcional=True)
            familias = entero("familias", minimo=1, opcional=True)
            if not productos and kg is None and familias is None:
                mal("el pedido necesita `productos`, `kg_estimado` o `familias`")
            creado = fecha("creado_en", "creado_hace_min", -1 / 60) or ahora.isoformat(timespec="seconds")
            limpias.append((ident, creado, entero("punto_id", minimo=1), familias, kg, productos, urgencia,
                            fecha("limite_en", "limite_en_horas", 1.0), estado, r.get("texto_original") or None))
    if errores:
        raise ArchivoMalo("\n".join(errores))
    return limpias


def cargar(reiniciar: bool = False, con=None, origen: Path | str | None = None) -> dict:
    """Crea la base (si no existe) y la llena. Con `origen`, cada CSV se toma de esa carpeta si
    existe y de la semilla sintética si no. Un archivo malo detiene la carga sin tocar la base."""
    con = con or db.conectar()
    hay = sum(con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLAS)
    if hay and not reiniciar:
        raise SystemExit("La base ya tiene datos. Usa --reiniciar para borrarlos y cargar de nuevo.")
    ahora = datetime.now(db.BOGOTA).replace(microsecond=0)
    origen = Path(origen) if origen else None
    if origen is not None and not origen.is_dir():
        raise SystemExit(f"No existe la carpeta {origen}")
    datos, fuente, errores = {}, {}, []
    for archivo in ARCHIVOS:
        real = origen is not None and (origen / archivo).is_file()
        ruta = (origen if real else DIR) / archivo
        fuente[archivo] = "real" if real else "sintético"
        try:
            with open(ruta, encoding="utf-8-sig", newline="") as f:
                datos[archivo] = _validar(archivo, list(csv.DictReader(f)), ahora)
        except ArchivoMalo as e:
            errores.append(f"[{ruta}]\n{e}")
        except (OSError, UnicodeDecodeError, csv.Error) as e:
            errores.append(f"[{ruta}]\n{archivo}: no se pudo leer ({e}). Debe ser CSV en UTF-8.")
    if not errores:      # referencias entre archivos, que es donde falla una mezcla de real y sintético
        acopios = {a[0]: a for a in datos["acopios.csv"]}
        puntos = {p[0] for p in datos["puntos.csv"]}
        for v in datos["vehiculos.csv"]:
            if v[4] not in acopios:
                errores.append(f"vehiculos.csv ({fuente['vehiculos.csv']}), id {v[0]}: `acopio_id` {v[4]} no "
                               f"existe en acopios.csv ({fuente['acopios.csv']})")
            elif v[5] is None or v[6] is None:           # sin posición: está en su acopio
                v[5], v[6] = acopios[v[4]][2], acopios[v[4]][3]
        for l in datos["lotes.csv"]:
            if l[1] not in acopios:
                errores.append(f"lotes.csv ({fuente['lotes.csv']}), id {l[0]}: `acopio_id` {l[1]} no existe "
                               f"en acopios.csv ({fuente['acopios.csv']})")
        for p in datos["pedidos.csv"]:
            if p[2] not in puntos:
                errores.append(f"pedidos.csv ({fuente['pedidos.csv']}), id {p[0]}: `punto_id` {p[2]} no existe "
                               f"en puntos.csv ({fuente['puntos.csv']})")
    if errores:
        raise SystemExit("Carga rechazada; la base no se tocó.\n" + "\n".join(errores))
    with con:
        for t in ("ubicaciones", "lugares") + TABLAS:
            con.execute(f"DELETE FROM {t}")
        con.executemany("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                        datos["puntos.csv"])
        con.executemany("INSERT INTO acopios(id,nombre,lat,lon,tiene_frio) VALUES (?,?,?,?,?)", datos["acopios.csv"])
        con.executemany("INSERT INTO vehiculos(id,nombre,tipo,capacidad_kg,acopio_id,lat,lon,estado) "
                        "VALUES (?,?,?,?,?,?,?,?)", datos["vehiculos.csv"])
        con.executemany("INSERT INTO lotes(id,acopio_id,producto,kg,perecedero,vence_en,empaque_activo) "
                        "VALUES (?,?,?,?,?,?,?)", datos["lotes.csv"])
        con.executemany("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,"
                        "limite_en,estado,texto_original) VALUES (?,?,?,?,?,?,?,?,?,?)", datos["pedidos.csv"])
    reales = [a for a in ARCHIVOS if fuente[a] == "real"]
    db.anotar(con, "semilla", "cargar datos",
              f"reales: {', '.join(reales) or 'ninguno'}; sintéticos: "
              f"{', '.join(a for a in ARCHIVOS if fuente[a] != 'real') or 'ninguno'}")
    lugares_n = None
    try:                 # el nomenclátor depende de los puntos recién cargados
        import lugares
        lugares_n = lugares.cargar_semilla(con)
    except Exception as e:  # noqa: BLE001
        print(f"aviso: no se pudo recargar el nomenclátor ({type(e).__name__}: {e})", file=sys.stderr)
    return {"filas": {a[:-4]: len(datos[a]) for a in ARCHIVOS}, "origen": fuente, "lugares": lugares_n}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Genera la semilla sintética y carga la base, con datos "
                                             "sintéticos o con los CSV reales de otra carpeta.")
    ap.add_argument("--cargar", action="store_true", help="crea la base y la llena")
    ap.add_argument("--reiniciar", action="store_true", help="borra los datos que haya antes de cargar")
    ap.add_argument("--origen", metavar="CARPETA", help="carpeta con CSV reales (p. ej. datos_privados/); "
                    "lo que falte se completa con la semilla sintética")
    ap.add_argument("--generar", action="store_true", help="vuelve a escribir los CSV sintéticos")
    ap.add_argument("--barrios", action="store_true", help="vuelve a bajar barrios.csv de OpenStreetMap")
    args = ap.parse_args(argv)
    if args.barrios or not (DIR / "barrios.csv").exists():
        print(f"barrios.csv: {barrios()} barrios", file=sys.stderr)
    if args.generar or not args.cargar or not all((DIR / a).exists() for a in ARCHIVOS):
        generar()
        print(f"CSV sintéticos escritos en {DIR}", file=sys.stderr)
    if args.cargar:
        r = cargar(args.reiniciar, origen=args.origen)
        for archivo in ARCHIVOS:
            print(f"{archivo:14} {r['origen'][archivo]:10} {r['filas'][archivo[:-4]]:4} filas")
        if r["lugares"] is not None:
            print(f"nomenclátor    {r['lugares']} apodos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
