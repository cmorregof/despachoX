"""Indicador A25 de lluvia antecedente (IDEA, UNAL Manizales) aplicado a los tramos de vía.

Qué es. El A25 de una estación en el día D es la lluvia acumulada, en mm, de los 25 días que
terminan en D, incluido D. El IDEA lo adoptó a partir de la tesis de Terlien (1996), y la Unidad
de Gestión del Riesgo de Manizales le fijó tres niveles de alerta: amarilla desde 200 mm,
naranja desde 300 mm y roja desde 400 mm (IDEA, Boletín Ambiental 145, marzo de 2018, tabla 2).
El reporte del IDEA de 2020 llama a los niveles «amarilla o baja», «naranja o media» y «roja o
alta». Ninguno de los dos documentos dice en palabras si la suma incluye el día del reporte, y
por eso lo comprobamos con los números del reporte de 2020. Allí los 36 A25 de la estación
Chec-Uribe del 25 de enero al 29 de febrero de 2020 son la suma de ese día y los 24 anteriores
(prueba en `despacho/tests/test_a25.py`). Detalle y enlaces en `docs/A25.md`.

Cómo lo usa DespachoX. A cada tramo con nombre (`lugares` de tipo vía, o `datos/semilla/vias.csv`)
se le asigna la estación más cercana de `datos_publicos/estaciones_a25.csv`, igual que los
polígonos de Thiessen con que el IDEA promedia la lluvia de la ciudad. El tramo hereda el nivel
de esa estación. Aquí no interviene ningún modelo de lenguaje, como pide la regla de
arquitectura: la regla calcula y avisa, y el despachador decide. El gancho del optimizador
(`DESPACHOX_A25=1`, apagado por defecto) encarece las vías con historial de ladera que están en
naranja o roja, y nunca las cierra.

Datos. La lluvia por defecto es sintética (`datos/demo/lluvia_sintetica.csv`) y la salida lo dice.
Para la red real basta un CSV con el mismo formato en `DESPACHOX_LLUVIA` (ver `docs/A25.md`).

Uso:
    python -m despacho.a25 --fecha 2026-11-21               # alerta por tramo
    python -m despacho.a25 --fecha 2026-11-21 --csv         # lo mismo en CSV
    python -m despacho.a25 --fecha 2026-11-21 --estaciones  # A25 de cada estación
    python -m despacho.a25 --fecha 2026-11-21 --corredores  # km de cada vía en alerta (red vial)
    python -m despacho.a25 --fecha 2026-11-21 --comparar    # plan con el gancho apagado y encendido
    python -m despacho.a25 --desde 2026-10-01 --hasta 2026-11-21   # un renglón por día de la temporada
"""
from __future__ import annotations

import argparse
import csv
import io
import math
import os
import sqlite3
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Mapping

RAIZ = Path(__file__).resolve().parent.parent
RUTA_ESTACIONES = RAIZ / "datos_publicos" / "estaciones_a25.csv"
RUTA_LLUVIA_DEMO = RAIZ / "datos" / "demo" / "lluvia_sintetica.csv"
RUTA_VIAS = RAIZ / "datos" / "semilla" / "vias.csv"
RUTA_CIERRES = RAIZ / "datos_publicos" / "cierres_historicos.csv"
# Causas de `cierres_historicos.csv` que cuentan como remoción en masa (docs/datos/vias_y_riesgo.md).
CAUSAS_LADERA = ("desliz", "derrumb", "desla", "desprend", "caida de lodo", "rocas")

# ---- Tomado de la fuente (IDEA, Boletín Ambiental 145, tabla 2; reporte A25 de 2020) ----
VENTANA_DIAS = 25
UMBRALES_MM = {"amarilla": 200.0, "naranja": 300.0, "roja": 400.0}
FUENTE_UMBRALES = ("IDEA-UNAL, Boletín Ambiental 145 (marzo de 2018), tabla 2: niveles de alerta "
                   "según el A25 adoptados por la UGR de Manizales")
# Orden de gravedad, de menor a mayor. `fuera_de_red`: ninguna estación a menos de COBERTURA_KM.
NIVELES = ("fuera_de_red", "sin_dato", "sin_alerta", "amarilla", "naranja", "roja")
ETIQUETA = {"roja": "roja o alta", "naranja": "naranja o media", "amarilla": "amarilla o baja",
            "sin_alerta": "sin alerta", "sin_dato": "sin dato", "fuera_de_red": "fuera de la red"}

# ---- Supuestos nuestros, sin fuente. Se calibran en el piloto con el IDEA. ----
# Un tramo a más de 3 km de toda estación queda fuera de la red: su A25 no se extrapola.
# 3 km es del orden de la mayor distancia entre una estación y su vecina más cercana (2,8 km,
# La Palma y La Nubia; cálculo nuestro con estaciones_a25.csv).
COBERTURA_KM = 3.0
# Gancho del optimizador: el tiempo de cada arista del corredor de un tramo en alerta se
# multiplica por este factor solo en el costo que minimiza el solver. Los tiempos de llegada
# del plan no cambian. Encarece sin prohibir: si no hay otra ruta, el plan pasa igual y lo
# avisa. La amarilla solo avisa. Se cambia con DESPACHOX_A25_FACTOR, p. ej. «naranja=2,roja=4».
FACTOR_RIESGO = {"naranja": 2.0, "roja": 4.0}

AVISO_SINTETICO = ("LLUVIA SINTÉTICA: los valores de lluvia no son mediciones del IDEA ni de ninguna "
                   "estación; sirven solo para la demostración. Los umbrales y las estaciones sí "
                   "salen de fuentes del IDEA.")
COLUMNA_REAL, COLUMNA_SINTETICA = "lluvia_mm", "lluvia_mm_sintetica"


# ------------------------------------------------------------------ cálculo

@dataclass(frozen=True)
class Ventana:
    """A25 de una estación en un día, con los días que faltaron en la ventana de 25."""
    fecha: date
    valor: float                      # mm; NaN si ningún día de la ventana tiene dato
    dias_con_dato: int
    faltantes: tuple[date, ...]

    @property
    def completo(self) -> bool:
        return not self.faltantes


def _dias(fecha: date) -> list[date]:
    """Los 25 días de la ventana: `fecha` y los 24 anteriores (convención del IDEA)."""
    return [fecha - timedelta(days=k) for k in range(VENTANA_DIAS - 1, -1, -1)]


def _valor(x) -> float | None:
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) and v >= 0 else None


def ventana(serie_diaria: Mapping[date, float | None], fecha: date) -> Ventana:
    """A25 con detalle. Un día sin dato (ausente, vacío, negativo o no numérico) cuenta 0 y se
    lista en `faltantes`; así el valor es una cota inferior del A25 verdadero."""
    con, faltan = [], []
    for d in _dias(fecha):
        v = _valor(serie_diaria.get(d))
        if v is None:
            faltan.append(d)
        else:
            con.append(v)
    valor = round(math.fsum(con), 1) if con else float("nan")
    return Ventana(fecha, valor, len(con), tuple(faltan))


def a25(serie_diaria: Mapping[date, float | None], fecha: date) -> float:
    """Lluvia acumulada (mm) de los 25 días que terminan en `fecha`, incluida `fecha`.

    Así lo calcula el IDEA (36 valores de su reporte de 2020; ver el encabezado del módulo).
    Redondeado a 0,1 mm, la resolución de los reportes del IDEA. Los días sin dato cuentan 0,
    de modo que el resultado es una cota inferior; si ningún día tiene dato devuelve NaN.
    Use `ventana()` para saber cuántos días faltaron.
    """
    return ventana(serie_diaria, fecha).valor


def nivel(valor: float | None) -> str:
    """Nivel de alerta del A25 según los umbrales de la UGR de Manizales.

    amarilla: 200 <= A25 < 300 mm · naranja: 300 <= A25 < 400 mm · roja: A25 >= 400 mm.
    Por debajo de 200 mm, «sin_alerta». Sin valor (None o NaN), «sin_dato».
    """
    if valor is None or not math.isfinite(float(valor)):
        return "sin_dato"
    for n in ("roja", "naranja", "amarilla"):
        if valor >= UMBRALES_MM[n]:
            return n
    return "sin_alerta"


def gravedad(n: str) -> int:
    return NIVELES.index(n) if n in NIVELES else -1


# ------------------------------------------------------------------ datos

def normalizar(texto: str | None) -> str:
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return " ".join(t.replace("-", " ").replace("_", " ").split())


def metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia plana en metros, la misma aproximación de `despacho.red.metros`."""
    kx = 111_320 * math.cos(math.radians(lat1))
    return math.hypot((lon2 - lon1) * kx, (lat2 - lat1) * 110_540)


@dataclass(frozen=True)
class Estacion:
    id: str
    nombre: str
    lat: float
    lon: float
    alias: tuple[str, ...] = ()


def leer_estaciones(ruta: Path | str | None = None) -> list[Estacion]:
    """Estaciones de `datos_publicos/estaciones_a25.csv` (IDEA, Boletín 145, tabla 4)."""
    with open(ruta or RUTA_ESTACIONES, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    return [Estacion(r["id"], r["nombre"], float(r["lat"]), float(r["lon"]),
                     tuple(normalizar(a) for a in (r["id"], r["nombre"], r.get("nombre_reporte_2020")) if a))
            for r in filas]


@dataclass
class Lluvia:
    """Lluvia diaria por estación: series[id_estacion][fecha] = mm (None si el dato falta)."""
    series: dict[str, dict[date, float | None]]
    sintetica: bool
    origen: str
    avisos: list[str]


def ruta_lluvia() -> Path:
    return Path(os.environ.get("DESPACHOX_LLUVIA") or RUTA_LLUVIA_DEMO)


def leer_lluvia(ruta: Path | str | None = None, estaciones: list[Estacion] | None = None) -> Lluvia:
    """Lee un CSV largo `estacion,fecha,lluvia_mm` (o `lluvia_mm_sintetica`).

    Las líneas que empiezan por «#» son comentarios. La serie se marca sintética si la columna
    es `lluvia_mm_sintetica` o si un comentario dice «sintética». `estacion` puede ser el id, el
    nombre o el nombre del reporte de 2020; las desconocidas se descartan con un aviso.
    """
    ruta = Path(ruta or ruta_lluvia())
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    por_alias = {a: e.id for e in estaciones for a in e.alias}
    texto = ruta.read_text(encoding="utf-8")
    comentarios = [l for l in texto.splitlines() if l.lstrip().startswith("#")]
    lector = csv.DictReader(io.StringIO("\n".join(l for l in texto.splitlines()
                                                  if l.strip() and not l.lstrip().startswith("#"))))
    campos = lector.fieldnames or []
    columna = COLUMNA_SINTETICA if COLUMNA_SINTETICA in campos else COLUMNA_REAL
    if columna not in campos or "estacion" not in campos or "fecha" not in campos:
        raise ValueError(f"{ruta}: se esperan las columnas estacion, fecha y {COLUMNA_REAL} "
                         f"(o {COLUMNA_SINTETICA}); llegaron {campos}")
    sintetica = columna == COLUMNA_SINTETICA or any("sintetic" in normalizar(c) for c in comentarios)
    series: dict[str, dict[date, float | None]] = {}
    avisos, desconocidas = [], set()
    for k, r in enumerate(lector, start=1):
        eid = por_alias.get(normalizar(r["estacion"]))
        if eid is None:
            desconocidas.add(r["estacion"])
            continue
        try:
            d = date.fromisoformat((r["fecha"] or "").strip()[:10])
        except ValueError:
            avisos.append(f"registro {k}: fecha ilegible «{r['fecha']}»; se descarta")
            continue
        bruto = (r.get(columna) or "").strip()
        v = _valor(bruto) if bruto else None
        if bruto and v is None:
            avisos.append(f"registro {k}: lluvia inválida «{bruto}» en {eid} el {d}; cuenta como dato faltante")
        serie = series.setdefault(eid, {})
        if d in serie and serie[d] != v:
            avisos.append(f"registro {k}: {eid} el {d} aparece dos veces; vale el último ({v})")
        serie[d] = v
    if desconocidas:
        avisos.append("estaciones que no están en estaciones_a25.csv: " + ", ".join(sorted(desconocidas)))
    return Lluvia(series, sintetica, str(ruta), avisos)


def historial_ladera(ruta: Path | str | None = None) -> dict[str, int]:
    """Tramo -> filas de `cierres_historicos.csv` con causa de remoción en masa, con o sin fecha.

    Son registros y no eventos únicos (un derrumbe puede tener varios). El A25 dice cuándo
    llueve de más; este historial dice dónde se ha cerrado la vía por la ladera.
    """
    ruta = Path(ruta or RUTA_CIERRES)
    if not ruta.exists():
        return {}
    cuenta: dict[str, int] = {}
    with open(ruta, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("via_nombre") and any(c in normalizar(r.get("causa")) for c in CAUSAS_LADERA):
                cuenta[r["via_nombre"]] = cuenta.get(r["via_nombre"], 0) + 1
    return cuenta


def tramos(con: sqlite3.Connection | None = None) -> list[dict]:
    """Tramos con nombre y arista: los de tipo vía del nomenclátor o, si no hay, `vias.csv`."""
    salida, vistos = [], set()
    if con is not None:
        try:
            filas = con.execute("SELECT nombre, lat, lon, osm_u, osm_v FROM lugares WHERE tipo='via' "
                                "AND osm_u IS NOT NULL AND osm_v IS NOT NULL ORDER BY id").fetchall()
        except sqlite3.Error:
            filas = []
        for r in filas:
            if r["nombre"] not in vistos:
                vistos.add(r["nombre"])
                salida.append({"tramo": r["nombre"], "lat": float(r["lat"]), "lon": float(r["lon"]),
                               "osm_u": int(r["osm_u"]), "osm_v": int(r["osm_v"])})
    if salida or not RUTA_VIAS.exists():
        return salida
    with open(RUTA_VIAS, encoding="utf-8") as f:
        return [{"tramo": r["nombre"], "lat": float(r["lat"]), "lon": float(r["lon"]),
                 "osm_u": int(r["osm_u"]), "osm_v": int(r["osm_v"])}
                for r in csv.DictReader(f) if r.get("osm_u") and r.get("osm_v")]


# ------------------------------------------------------------------ alertas

def _fecha(f: date | datetime | str) -> date:
    if isinstance(f, datetime):
        return f.date()
    if isinstance(f, date):
        return f
    return date.fromisoformat(str(f)[:10])


def alertas_estaciones(fecha: date | str, lluvia: Lluvia | None = None,
                       estaciones: list[Estacion] | None = None) -> list[dict]:
    """A25 y nivel de cada estación en `fecha`."""
    fecha = _fecha(fecha)
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    lluvia = lluvia if lluvia is not None else leer_lluvia(estaciones=estaciones)
    salida = []
    for e in estaciones:
        w = ventana(lluvia.series.get(e.id, {}), fecha)
        salida.append({"estacion_id": e.id, "estacion": e.nombre, "lat": e.lat, "lon": e.lon,
                       "a25_mm": None if math.isnan(w.valor) else w.valor, "nivel": nivel(w.valor),
                       "dias_con_dato": w.dias_con_dato, "dias_faltantes": len(w.faltantes),
                       "completo": w.completo})
    return salida


def asignar(lat: float, lon: float, estaciones: list[Estacion], ventanas: Mapping[str, Ventana],
            cobertura_km: float = COBERTURA_KM) -> dict:
    """Estación que representa un lugar y su nivel: la más cercana, como en Thiessen.

    Si la más cercana tiene días sin dato y otra a menos de `cobertura_km` tiene la ventana
    completa, se usa la otra y se dice (el IDEA también completa la lluvia diaria con estaciones
    cercanas). Sin estación a menos de `cobertura_km`, el lugar queda `fuera_de_red`.
    """
    cerca = sorted(((metros(lat, lon, e.lat, e.lon) / 1000, e) for e in estaciones), key=lambda x: x[0])
    km0, e0 = cerca[0] if cerca else (float("inf"), None)
    base = {"estacion_mas_cercana": e0.nombre if e0 else None,
            "distancia_mas_cercana_km": round(km0, 2) if e0 else None}
    dentro = [(km, e) for km, e in cerca if km <= cobertura_km]
    if not dentro:
        return {**base, "estacion_id": None, "estacion": None, "distancia_km": None, "a25_mm": None,
                "nivel": "fuera_de_red", "dias_con_dato": 0, "dias_faltantes": None, "completo": False,
                "nota": f"ninguna estación a menos de {cobertura_km:g} km; la más cercana, "
                        f"{e0.nombre if e0 else '-'}, está a {km0:.1f} km"}
    completas = [(km, e) for km, e in dentro if ventanas[e.id].completo]
    km, e = completas[0] if completas else min(dentro, key=lambda x: (len(ventanas[x[1].id].faltantes), x[0]))
    w = ventanas[e.id]
    nota = None
    if e.id != dentro[0][1].id:
        nota = (f"{dentro[0][1].nombre} tiene {len(ventanas[dentro[0][1].id].faltantes)} días sin dato; "
                f"se usó {e.nombre}")
    elif not w.completo and w.dias_con_dato:
        nota = f"faltan {len(w.faltantes)} de {VENTANA_DIAS} días: el A25 es una cota inferior"
    return {**base, "estacion_id": e.id, "estacion": e.nombre, "distancia_km": round(km, 2),
            "a25_mm": None if math.isnan(w.valor) else w.valor, "nivel": nivel(w.valor),
            "dias_con_dato": w.dias_con_dato, "dias_faltantes": len(w.faltantes), "completo": w.completo,
            "nota": nota}


def alertas_tramos(con: sqlite3.Connection | None, fecha: date | str, lluvia: Lluvia | None = None,
                   estaciones: list[Estacion] | None = None, cobertura_km: float = COBERTURA_KM,
                   lista_tramos: list[dict] | None = None) -> list[dict]:
    """Nivel A25 de cada tramo en `fecha`, ordenado del más grave al menos grave.

    Cada tramo toma la estación más cercana a su punto de referencia (ver `asignar`). Los
    tramos salen del nomenclátor de la base (`con`) o, si no hay, de `datos/semilla/vias.csv`.
    """
    fecha = _fecha(fecha)
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    lluvia = lluvia if lluvia is not None else leer_lluvia(estaciones=estaciones)
    lista_tramos = lista_tramos if lista_tramos is not None else tramos(con)
    ventanas = {e.id: ventana(lluvia.series.get(e.id, {}), fecha) for e in estaciones}
    hist = historial_ladera()
    salida = [{**t, "fecha": fecha.isoformat(), "lluvia_sintetica": lluvia.sintetica,
               "cierres_por_ladera": hist.get(t["tramo"], 0),
               **asignar(t["lat"], t["lon"], estaciones, ventanas, cobertura_km)} for t in lista_tramos]
    salida.sort(key=lambda a: (-gravedad(a["nivel"]), -(a["a25_mm"] or 0), a["tramo"]))
    return salida


def resumen_a25(con: sqlite3.Connection | None, fecha: date | str, lluvia: Lluvia | None = None,
                estaciones: list[Estacion] | None = None, g=None) -> dict:
    """Todo lo que el tablero necesita para mostrar el A25 del día, listo para JSON.

    Con la red vial `g` agrega `corredores`: los km de cada vía con historial de ladera en
    alerta, arista por arista, que es lo que usa el gancho del optimizador.
    """
    fecha = _fecha(fecha)
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    lluvia = lluvia if lluvia is not None else leer_lluvia(estaciones=estaciones)
    por_tramo = alertas_tramos(con, fecha, lluvia, estaciones)
    corredores_alerta = (riesgo_corredores(g, fecha, lluvia, estaciones).detalle if g is not None else None)
    conteo = {n: 0 for n in reversed(NIVELES)}
    for a in por_tramo:
        conteo[a["nivel"]] += 1
    partes = [f"{conteo[n]} en {ETIQUETA[n]}" for n in ("roja", "naranja", "amarilla") if conteo[n]]
    frase = (f"{len(por_tramo)} tramos; " + (", ".join(partes) if partes else "ninguno en alerta")
             + (f"; {conteo['fuera_de_red']} fuera de la red de estaciones" if conteo["fuera_de_red"] else ""))
    return {
        "fecha": fecha.isoformat(),
        "lluvia": "sintética" if lluvia.sintetica else "real",
        "aviso": AVISO_SINTETICO if lluvia.sintetica else None,
        "origen_lluvia": lluvia.origen,
        "umbrales_mm": dict(UMBRALES_MM),
        "fuente_umbrales": FUENTE_UMBRALES,
        "cobertura_km": COBERTURA_KM,
        "factor_costo": factores(),
        "gancho_activo": gancho_activo(),
        "conteo": conteo,
        "frase": frase,
        "tramos": por_tramo,
        "estaciones": alertas_estaciones(fecha, lluvia, estaciones),
        "corredores": corredores_alerta,
        "avisos": list(lluvia.avisos),
    }


def _km_por_nivel(g, resultado: dict, riesgo: Riesgo) -> dict[str, float]:
    """Km que las rutas de un plan (paradas y regresos) recorren por aristas que `riesgo` encarece."""
    nodo_de = {(round(d["y"], 6), round(d["x"], 6)): n for n, d in g.nodes(data=True)}
    geos = [p["geometria"] for p in resultado["paradas"]]
    geos += [v["regreso"] for v in resultado["resumen"].get("vehiculos", [])]
    km = {n: 0.0 for n in ("roja", "naranja")}
    for geo in geos:
        nodos = [nodo_de[tuple(p)] for p in geo if tuple(p) in nodo_de]
        for u, v in zip(nodos[:-1], nodos[1:]):
            if (u, v) in riesgo.tramo and g.has_edge(u, v):
                n = riesgo.tramo[(u, v)][1]
                km[n] = km.get(n, 0.0) + min(float(d.get("length", 0.0)) for d in g[u][v].values()) / 1000
    return {n: round(x, 2) for n, x in km.items()}


def temporada(con: sqlite3.Connection | None, desde: date | str, hasta: date | str, lluvia: Lluvia | None = None,
              estaciones: list[Estacion] | None = None) -> list[dict]:
    """Un renglón por día: cuántos tramos hubo en cada nivel y qué vías de ladera estaban en naranja o roja.

    Con la lluvia real del IDEA, esta tabla da cuántos días de la temporada hubo vías con historial
    de cierres en alerta, que es un indicador verificable para el piloto.
    """
    desde, hasta = _fecha(desde), _fecha(hasta)
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    lluvia = lluvia if lluvia is not None else leer_lluvia(estaciones=estaciones)
    lista = tramos(con)
    salida = []
    for k in range((hasta - desde).days + 1):
        dia = desde + timedelta(days=k)
        al = alertas_tramos(con, dia, lluvia, estaciones, lista_tramos=lista)
        conteo = {n: sum(1 for a in al if a["nivel"] == n) for n in reversed(NIVELES)}
        ladera = [f"{a['tramo']} ({a['nivel']})" for a in al
                  if a["cierres_por_ladera"] and a["nivel"] in ("naranja", "roja")]
        salida.append({"fecha": dia.isoformat(), **conteo, "ladera_en_alerta": ladera,
                       "lluvia": "sintética" if lluvia.sintetica else "real"})
    return salida


def comparar(con: sqlite3.Connection, g, fecha: date | str, segundos: int = 8, ahora: datetime | None = None) -> dict:
    """El mismo plan con el gancho apagado y encendido, sin escribir nada en la base.

    Sirve para que el despachador vea, antes de decidir, cuánto se apartan las rutas de las vías
    en alerta y cuánto tiempo cuesta. Usa el modelo del optimizador (`optimizar._resolver`).
    """
    from datos import db
    from despacho import optimizar
    fecha = _fecha(fecha)
    ahora = ahora or datetime.now(db.BOGOTA)
    riesgo = riesgo_corredores(g, fecha)
    datos = optimizar._leer(con, incluir_asignados=False)
    salida = {"fecha": fecha.isoformat(), "lluvia": "sintética" if riesgo.sintetica else "real",
              "segundos_por_plan": segundos, "factor_costo": riesgo.factores,
              "vias_encarecidas": [d for d in riesgo.detalle if d["factor"] > 1]}
    for nombre, r in (("apagado", None), ("encendido", riesgo)):
        res = optimizar._resolver(datos, g, ahora, segundos, {}, riesgo=r)
        s = res["resumen"]
        salida[nombre] = {
            "pedidos_atendidos": s.get("pedidos_atendidos", 0), "pedidos_considerados": s.get("pedidos_considerados", 0),
            "criticos_a_tiempo": s.get("criticos", {}).get("a_tiempo", 0),
            "criticos": s.get("criticos", {}).get("paradas", 0),
            "duracion_rutas_min": round(sum(v["duracion_s"] for v in s.get("vehiculos", [])) / 60, 1),
            "retraso_total_min": round(s.get("retraso_total_s", 0) / 60, 1),
            "km_en_alerta": _km_por_nivel(g, res, riesgo)}
    return salida


# ------------------------------------------------------------------ gancho del optimizador

def gancho_activo() -> bool:
    """El gancho del optimizador se enciende con DESPACHOX_A25=1. Apagado por defecto."""
    return os.environ.get("DESPACHOX_A25", "").strip().lower() in ("1", "si", "sí", "true")


def factores() -> dict[str, float]:
    """FACTOR_RIESGO, o lo que diga DESPACHOX_A25_FACTOR («naranja=2,roja=4»). Nunca menor que 1."""
    texto = os.environ.get("DESPACHOX_A25_FACTOR", "").strip()
    if not texto:
        return dict(FACTOR_RIESGO)
    salida = {}
    for parte in texto.split(","):
        n, _, s = parte.partition("=")
        n = normalizar(n).replace(" ", "_")
        try:
            if n in UMBRALES_MM:
                salida[n] = max(1.0, float(s.replace(",", ".")))
        except ValueError:
            continue
    return salida


def corredores(g) -> dict[str, list[tuple[int, int, float, float, float]]]:
    """Tramo -> aristas (u, v, lat, lon, largo_m) de su corredor, elegidas como en `despacho/vias.py`.

    Un tramo con nombre en OSM es toda la vía que casa con su patrón; uno sin nombre, su arista
    fija. Así el gancho encarece la vía completa y no solo la arista que usa un cierre.
    """
    from despacho import vias       # importa osmnx: solo se carga si el gancho está encendido
    salida = {}
    for t in vias.TRAMOS:
        if "arista" in t:
            u, v = t["arista"]
            if g.has_edge(u, v):
                lat, lon = vias._punto_medio(g, u, v)
                largo = min(float(d.get("length", 0.0)) for d in g[u][v].values())
                salida[t["nombre"]] = [(u, v, lat, lon, largo)]
        else:
            salida[t["nombre"]] = [(int(u), int(v), lat, lon, float(largo))
                                   for u, v, lat, lon, largo in vias.candidatas(g, t)]
    return salida


@dataclass
class Riesgo:
    """Lo que el gancho le pasa al optimizador."""
    fecha: date
    factor: dict[tuple[int, int], float]          # arista dirigida -> factor de costo (> 1)
    tramo: dict[tuple[int, int], tuple[str, str]]  # arista dirigida -> (tramo, nivel)
    detalle: list[dict]                            # por tramo, estación y nivel: aristas y km
    sintetica: bool
    factores: dict[str, float]


def riesgo_corredores(g, fecha: date | str, lluvia: Lluvia | None = None,
                      estaciones: list[Estacion] | None = None, lista: dict | None = None,
                      factores_nivel: Mapping[str, float] | None = None,
                      cobertura_km: float = COBERTURA_KM, solo_con_historial: bool = True,
                      historial: Mapping[str, int] | None = None) -> Riesgo:
    """Factor de costo por arista para los corredores en naranja o roja en `fecha`.

    Cada arista del corredor toma la estación más cercana a su punto medio, de modo que una vía
    larga puede tener una parte en roja y otra sin alerta. Las aristas fuera de la red o con
    nivel sin factor no se tocan. Con `solo_con_historial` (por defecto) solo cuentan las vías
    con al menos un cierre por remoción en masa en `cierres_historicos.csv`: el A25 dice cuándo
    y el historial dice dónde. `lista` reemplaza a `corredores(g)` (para pruebas).
    """
    fecha = _fecha(fecha)
    estaciones = estaciones if estaciones is not None else leer_estaciones()
    lluvia = lluvia if lluvia is not None else leer_lluvia(estaciones=estaciones)
    fn = dict(factores() if factores_nivel is None else factores_nivel)
    hist = historial_ladera() if historial is None else dict(historial)
    ventanas = {e.id: ventana(lluvia.series.get(e.id, {}), fecha) for e in estaciones}
    factor: dict[tuple[int, int], float] = {}
    tramo: dict[tuple[int, int], tuple[str, str]] = {}
    grupos: dict[tuple[str, str, str], dict] = {}
    for nombre, aristas in (corredores(g) if lista is None else lista).items():
        if solo_con_historial and not hist.get(nombre):
            continue
        for u, v, lat, lon, largo in aristas:
            a = asignar(lat, lon, estaciones, ventanas, cobertura_km)
            f = float(fn.get(a["nivel"], 1.0))
            if a["nivel"] in ("amarilla", "naranja", "roja"):
                k = (nombre, a["estacion"], a["nivel"])
                grp = grupos.setdefault(k, {"tramo": nombre, "estacion": a["estacion"], "nivel": a["nivel"],
                                            "a25_mm": a["a25_mm"], "factor": f, "aristas": 0, "km": 0.0,
                                            "completo": a["completo"],
                                            "cierres_por_ladera": hist.get(nombre, 0)})
                grp["aristas"] += 1
                grp["km"] += largo / 1000
            if f <= 1.0:
                continue
            for par in ((int(u), int(v)), (int(v), int(u))):
                if f > factor.get(par, 1.0):
                    factor[par] = f
                    tramo[par] = (nombre, a["nivel"])
    detalle = sorted(({**d, "km": round(d["km"], 2)} for d in grupos.values()),
                     key=lambda d: (-gravedad(d["nivel"]), -d["km"], d["tramo"]))
    return Riesgo(fecha, factor, tramo, detalle, lluvia.sintetica, fn)


# ------------------------------------------------------------------ línea de órdenes

def _mm(x: float | None) -> str:
    return "-" if x is None else f"{x:.1f}".replace(".", ",")


def _km(x: float | None) -> str:
    return "-" if x is None else f"{x:.2f}".replace(".", ",") + " km"


def _imprimir_comparacion(fecha: date, segundos: int, lluvia: Lluvia) -> int:
    from datos import db
    from despacho import red
    if lluvia.sintetica:
        print(AVISO_SINTETICO, file=sys.stderr)
    con = db.conectar()
    try:
        r = comparar(con, red.cargar(), fecha, segundos)
    finally:
        con.close()
    a, e = r["apagado"], r["encendido"]
    print(f"Plan de la base con el gancho del A25 apagado y encendido · A25 del {r['fecha']} · "
          f"lluvia {r['lluvia']} · {segundos} s por plan · no se guarda nada")
    if lluvia.sintetica:
        print("LLUVIA SINTÉTICA · demuestra el mecanismo · no mide un impacto")
    filas = [("pedidos atendidos", f"{a['pedidos_atendidos']}/{a['pedidos_considerados']}",
              f"{e['pedidos_atendidos']}/{e['pedidos_considerados']}"),
             ("críticos a tiempo", f"{a['criticos_a_tiempo']}/{a['criticos']}", f"{e['criticos_a_tiempo']}/{e['criticos']}"),
             ("duración sumada de las rutas (min)", _mm(a["duracion_rutas_min"]), _mm(e["duracion_rutas_min"])),
             ("retraso total (min)", _mm(a["retraso_total_min"]), _mm(e["retraso_total_min"])),
             ("km por vías en alerta roja", _mm(a["km_en_alerta"]["roja"]), _mm(e["km_en_alerta"]["roja"])),
             ("km por vías en alerta naranja", _mm(a["km_en_alerta"]["naranja"]), _mm(e["km_en_alerta"]["naranja"]))]
    print(f"\n{'':36} {'apagado':>10} {'encendido':>10}")
    for nombre, x, y in filas:
        print(f"{nombre:36} {x:>10} {y:>10}")
    fx = ", ".join(f"{n} ×{f:g}" for n, f in r["factor_costo"].items())
    print(f"\nVías encarecidas ({fx} en el costo; supuesto sin fuente):")
    for d in r["vias_encarecidas"]:
        print(f"  {d['tramo']} · {d['estacion']} · {ETIQUETA[d['nivel']]} · {_mm(d['km'])} km")
    if not r["vias_encarecidas"]:
        print("  ninguna")
    return 0


def _imprimir_temporada(desde: date, hasta: date, lluvia: Lluvia, estaciones: list[Estacion],
                        en_csv: bool) -> int:
    from datos import db
    if lluvia.sintetica:
        print(AVISO_SINTETICO, file=sys.stderr)
    con = db.conectar() if db.RUTA_DB.exists() else None
    try:
        filas = temporada(con, desde, hasta, lluvia, estaciones)
    finally:
        if con is not None:
            con.close()
    if en_csv:
        w = csv.writer(sys.stdout)
        w.writerow(["fecha", "roja", "naranja", "amarilla", "sin_alerta", "sin_dato", "fuera_de_red",
                    "ladera_en_alerta", "lluvia"])
        for f in filas:
            w.writerow([f["fecha"], f["roja"], f["naranja"], f["amarilla"], f["sin_alerta"], f["sin_dato"],
                        f["fuera_de_red"], "; ".join(f["ladera_en_alerta"]), f["lluvia"]])
        return 0
    print(f"A25 por día, del {desde.isoformat()} al {hasta.isoformat()} · tramos por nivel")
    if lluvia.sintetica:
        print("LLUVIA SINTÉTICA · no es una medición del IDEA · solo para la demostración")
    print(f"\n{'fecha':10} {'roja':>5} {'naranja':>8} {'amarilla':>9} {'sin alerta':>11}  vías de ladera en naranja o roja")
    for f in filas:
        print(f"{f['fecha']:10} {f['roja']:>5} {f['naranja']:>8} {f['amarilla']:>9} {f['sin_alerta']:>11}  "
              f"{', '.join(f['ladera_en_alerta']) or '-'}")
    dias = sum(1 for f in filas if f["ladera_en_alerta"])
    print(f"\nDías con alguna vía de ladera en naranja o roja: {dias} de {len(filas)}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Alerta A25 (lluvia antecedente de 25 días) por tramo de vía.")
    ap.add_argument("--fecha", help="día del A25, AAAA-MM-DD (incluye ese día); por defecto, hoy")
    ap.add_argument("--csv", action="store_true", help="salida en CSV")
    ap.add_argument("--estaciones", action="store_true", help="A25 por estación en vez de por tramo")
    ap.add_argument("--corredores", action="store_true",
                    help="km de cada vía en alerta, arista por arista (carga la red vial)")
    ap.add_argument("--desde", help="con --hasta, un renglón por día de la temporada (AAAA-MM-DD)")
    ap.add_argument("--hasta", help="último día de la temporada (AAAA-MM-DD)")
    ap.add_argument("--comparar", action="store_true",
                    help="plan de la base con el gancho apagado y encendido, sin guardar nada")
    ap.add_argument("--segundos", type=int, default=8, help="límite del solver por plan en --comparar")
    ap.add_argument("--lluvia", help="CSV de lluvia (por defecto DESPACHOX_LLUVIA o la serie sintética)")
    args = ap.parse_args(argv)
    from datos import db
    if args.lluvia:
        os.environ["DESPACHOX_LLUVIA"] = str(args.lluvia)     # lo usan también el gancho y --comparar
    fecha = _fecha(args.fecha) if args.fecha else datetime.now(db.BOGOTA).date()
    estaciones = leer_estaciones()
    lluvia = leer_lluvia(args.lluvia, estaciones)
    if args.comparar:
        return _imprimir_comparacion(fecha, args.segundos, lluvia)
    if args.desde or args.hasta:
        return _imprimir_temporada(_fecha(args.desde or fecha), _fecha(args.hasta or fecha), lluvia,
                                   estaciones, args.csv)
    con = None
    if db.RUTA_DB.exists() and not (args.estaciones or args.corredores):
        con = db.conectar()
    try:
        if args.estaciones:
            filas = alertas_estaciones(fecha, lluvia, estaciones)
        elif args.corredores:
            from despacho import red
            filas = riesgo_corredores(red.cargar(), fecha, lluvia, estaciones).detalle
        else:
            filas = alertas_tramos(con, fecha, lluvia, estaciones)
    finally:
        if con is not None:
            con.close()
    origen = "sintética" if lluvia.sintetica else "real"
    if lluvia.sintetica:
        print(AVISO_SINTETICO, file=sys.stderr)
    for a in lluvia.avisos:
        print(f"aviso: {a}", file=sys.stderr)
    if args.csv:
        campos = (["fecha", "estacion_id", "estacion", "a25_mm", "nivel", "dias_con_dato", "dias_faltantes"]
                  if args.estaciones else
                  ["fecha", "tramo", "estacion", "nivel", "a25_mm", "km", "aristas", "factor",
                   "cierres_por_ladera"]
                  if args.corredores else
                  ["fecha", "tramo", "nivel", "a25_mm", "estacion", "distancia_km", "dias_con_dato",
                   "dias_faltantes", "cierres_por_ladera", "osm_u", "osm_v", "nota"])
        w = csv.writer(sys.stdout)
        w.writerow(campos + ["lluvia"])
        for f in filas:
            w.writerow([fecha.isoformat() if c == "fecha" else ("" if f.get(c) is None else f.get(c))
                        for c in campos] + [origen])
        return 0
    print(f"A25 · lluvia acumulada en los 25 días que terminan el {fecha.isoformat()} (IDEA, UNAL Manizales)")
    if lluvia.sintetica:
        print("LLUVIA SINTÉTICA · no es una medición del IDEA · solo para la demostración")
    print("Umbrales de la UGR de Manizales: amarilla 200 mm, naranja 300 mm, roja 400 mm "
          "(IDEA, Boletín Ambiental 145, tabla 2)\n")
    if args.estaciones:
        print(f"{'estación':30} {'nivel':16} {'A25 (mm)':>9}  días con dato")
        for f in filas:
            print(f"{f['estacion']:30} {ETIQUETA[f['nivel']]:16} {_mm(f['a25_mm']):>9}  "
                  f"{f['dias_con_dato']}/{VENTANA_DIAS}")
        return 0
    if args.corredores:
        print(f"{'vía':26} {'estación':28} {'nivel':16} {'A25 (mm)':>9} {'km':>6}  factor de costo")
        for f in filas:
            print(f"{f['tramo']:26} {f['estacion'][:28]:28} {ETIQUETA[f['nivel']]:16} {_mm(f['a25_mm']):>9} "
                  f"{_mm(f['km']):>6}  {f['factor']:g}")
        if not filas:
            print("Ninguna vía con nombre tiene aristas en alerta dentro de la red de estaciones.")
        print(f"\nCon DESPACHOX_A25=1 el optimizador multiplica por el factor el costo de esas aristas; "
              "los tiempos de llegada no cambian.")
        return 0
    print(f"{'tramo':26} {'nivel':16} {'A25 (mm)':>9}  {'estación':28} {'distancia':>9}  datos  "
          "cierres por ladera")
    for f in filas:
        datos_txt = f"{f['dias_con_dato']}/{VENTANA_DIAS}" if f["nivel"] != "fuera_de_red" else "-"
        estacion = f["estacion"] or f"(más cercana: {f['estacion_mas_cercana']})"
        distancia = f["distancia_km"] if f["distancia_km"] is not None else f["distancia_mas_cercana_km"]
        print(f"{f['tramo']:26} {ETIQUETA[f['nivel']]:16} {_mm(f['a25_mm']):>9}  {estacion[:28]:28} "
              f"{_km(distancia):>9}  {datos_txt:>5}  {f.get('cierres_por_ladera') or '-'}")
        if f.get("nota") and f["nivel"] != "fuera_de_red":
            print(f"{'':26} nota: {f['nota']}")
    r = {n: sum(1 for f in filas if f["nivel"] == n) for n in NIVELES}
    print(f"\nEn alerta: {r['roja']} en roja, {r['naranja']} en naranja, {r['amarilla']} en amarilla. "
          f"Fuera de la red de estaciones (más de {COBERTURA_KM:g} km): {r['fuera_de_red']}.")
    fx = ", ".join(f"{n} ×{f:g}" for n, f in factores().items())
    print("La alerta informa al despachador. El optimizador solo la usa con DESPACHOX_A25=1, y entonces "
          f"encarece sin prohibir las vías en alerta ({fx} en el costo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
