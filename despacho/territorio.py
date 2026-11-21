"""Vista por territorio: cómo se atendió cada comuna y qué barrios y veredas no han pedido nada.

Uso:
    python -m despacho.territorio                                  # todo lo que hay en la base
    python -m despacho.territorio --desde 2026-11-21T00:00 --hasta 2026-11-22T00:00
    python -m despacho.territorio --csv salida.csv                 # tabla para el informe del piloto

Responde a la mentoría 1 (encargos/T1_TERRITORIO.md, parte B): un prototipo que mide por territorio.
Solo lee la base; no cambia el esquema ni el optimizador. No saca `texto_original` ni `remitente_hash`.

Reglas (las mismas en la tabla, el CSV y el tablero):
- El periodo es `desde <= pedidos.creado_en < hasta`; sin fechas, todo.
- Cuentan los pedidos con punto de entrega, sin los `descartado`, sin los que tienen `duplicado_de` y
  sin las alertas por silencio (`origen='silencio'`), que son visitas de verificación, no pedidos.
- El territorio es la comuna del punto. Si el punto no la tiene (los que crea el bot al confirmar un
  lugar), se toma la de su barrio en `datos/semilla/barrios.csv`; si tampoco, «sin comuna».
- La hora de entrega es el `entregado_en` más tardío de los paquetes del pedido.
- A tiempo: entregado a más tardar en `limite_en`. El denominador (`evaluados`) son los pedidos con
  `limite_en` que ya se pueden juzgar: entregados con hora conocida, o abiertos con el límite vencido
  a la hora `ahora`. Los que no tienen `limite_en` y los abiertos que aún están en plazo no cuentan.
- Los kilos son los declarados en el pedido (`kg_estimado` o la suma de `productos`), sin imputar;
  los entregados, los de sus paquetes entregados.
"""
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import statistics
import sys
from datetime import datetime
from pathlib import Path

from datos import db
from despacho.cierres import normalizar

SIN_COMUNA = "sin comuna"
RUTA_BARRIOS = Path(__file__).resolve().parent.parent / "datos" / "semilla" / "barrios.csv"
ABIERTOS = ("nuevo", "confirmado", "asignado")
COLUMNAS = ("territorio", "puntos", "puntos_criticos", "pedidos", "familias", "kg_pedidos", "entregados",
            "kg_entregados", "a_tiempo", "evaluados", "pct_a_tiempo", "criticos_a_tiempo",
            "criticos_evaluados", "pct_criticos_a_tiempo", "espera_mediana_h", "pendiente_mas_viejo_h")
COLUMNAS_SILENCIO = ("nombre", "tipo", "comuna", "estado")
SIN_PEDIDOS = "sin pedidos registrados"     # nunca «sin necesidad»: callar no es estar bien


def _fecha(valor) -> datetime | None:
    if valor is None or valor == "":
        return None
    if isinstance(valor, datetime):
        d = valor
    else:
        try:
            d = datetime.fromisoformat(str(valor))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=db.BOGOTA)


def _en_periodo(creado: datetime | None, desde: datetime | None, hasta: datetime | None) -> bool:
    if creado is None:
        return desde is None and hasta is None
    return (desde is None or creado >= desde) and (hasta is None or creado < hasta)


def _comuna_de_barrio() -> dict[str, str]:
    """barrio normalizado -> comuna, del nomenclátor de OpenStreetMap."""
    if not RUTA_BARRIOS.exists():
        return {}
    with open(RUTA_BARRIOS, encoding="utf-8") as f:
        return {normalizar(r["nombre"]): r["comuna"].strip() for r in csv.DictReader(f)
                if r.get("nombre") and (r.get("comuna") or "").strip()}


def _territorios(con: sqlite3.Connection) -> tuple[dict[int, str], set[str]]:
    """Comuna de cada punto y todas las comunas conocidas (también las que no tienen puntos)."""
    por_barrio = _comuna_de_barrio()
    de_punto = {}
    for p in con.execute("SELECT id, barrio, comuna FROM puntos"):
        comuna = (p["comuna"] or "").strip() or por_barrio.get(normalizar(p["barrio"])) or SIN_COMUNA
        de_punto[p["id"]] = comuna
    return de_punto, (set(de_punto.values()) | set(por_barrio.values()))


def _kg_declarados(p: sqlite3.Row) -> float:
    if p["kg_estimado"] is not None:
        return float(p["kg_estimado"])
    try:
        lineas = json.loads(p["productos"] or "[]")
        return float(sum(float(l.get("kg") or 0) for l in lineas if isinstance(l, dict)))
    except (TypeError, ValueError, AttributeError):
        return 0.0


def _pedidos(con: sqlite3.Connection, desde: datetime | None, hasta: datetime | None) -> list[sqlite3.Row]:
    filas = con.execute(
        "SELECT pe.id, pe.creado_en, pe.punto_id, pe.familias, pe.kg_estimado, pe.productos, pe.limite_en, "
        "       pe.estado, pu.critico, "
        "       (SELECT MAX(pa.entregado_en) FROM paquetes pa WHERE pa.pedido_id = pe.id "
        "          AND pa.estado = 'entregado') AS entregado_en, "
        "       (SELECT COALESCE(SUM(pa.kg), 0) FROM paquetes pa WHERE pa.pedido_id = pe.id "
        "          AND pa.estado = 'entregado') AS kg_entregado "
        "FROM pedidos pe JOIN puntos pu ON pu.id = pe.punto_id "
        "WHERE pe.estado != 'descartado' AND pe.duplicado_de IS NULL "
        "  AND COALESCE(pe.origen, 'mensaje') != 'silencio' ORDER BY pe.id").fetchall()
    return [p for p in filas if _en_periodo(_fecha(p["creado_en"]), desde, hasta)]


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def resumen(con: sqlite3.Connection, desde=None, hasta=None, ahora=None) -> list[dict]:
    """Una fila por comuna (también las que no tienen pedidos) y «sin comuna» si hace falta.

    `desde`, `hasta` y `ahora` aceptan datetime o texto ISO 8601; sin zona se toma la de Colombia.
    Las columnas están en COLUMNAS y su definición, en el docstring del módulo.
    """
    desde, hasta = _fecha(desde), _fecha(hasta)
    ahora = _fecha(ahora) or datetime.now(db.BOGOTA)
    de_punto, comunas = _territorios(con)
    filas = {t: {"territorio": t, "_puntos": set(), "_criticos": set(), "pedidos": 0, "familias": 0,
                 "kg_pedidos": 0.0, "entregados": 0, "kg_entregados": 0.0, "a_tiempo": 0, "evaluados": 0,
                 "criticos_a_tiempo": 0, "criticos_evaluados": 0, "_esperas": [], "_abierto_desde": None}
             for t in comunas}
    for p in _pedidos(con, desde, hasta):
        f = filas[de_punto[p["punto_id"]]]
        creado, limite, entrega = _fecha(p["creado_en"]), _fecha(p["limite_en"]), _fecha(p["entregado_en"])
        f["_puntos"].add(p["punto_id"])
        if p["critico"]:
            f["_criticos"].add(p["punto_id"])
        f["pedidos"] += 1
        f["familias"] += p["familias"] or 0
        f["kg_pedidos"] += _kg_declarados(p)
        entregado = p["estado"] == "entregado"
        if entregado:
            f["entregados"] += 1
            f["kg_entregados"] += float(p["kg_entregado"] or 0)
            if entrega is not None and creado is not None:
                f["_esperas"].append((entrega - creado).total_seconds() / 3600)
        elif p["estado"] in ABIERTOS and creado is not None:
            if f["_abierto_desde"] is None or creado < f["_abierto_desde"]:
                f["_abierto_desde"] = creado
        if limite is None:
            continue
        if entregado and entrega is not None:
            a_tiempo = entrega <= limite
        elif not entregado and limite < ahora:
            a_tiempo = False                  # sigue abierto y ya se le pasó la hora
        else:
            continue                          # en plazo, o entregado sin hora conocida
        f["evaluados"] += 1
        f["a_tiempo"] += a_tiempo
        if p["critico"]:
            f["criticos_evaluados"] += 1
            f["criticos_a_tiempo"] += a_tiempo

    salida = []
    for t in sorted(filas, key=lambda t: (t == SIN_COMUNA, normalizar(t))):
        f = filas[t]
        abierto = f.pop("_abierto_desde")
        esperas = f.pop("_esperas")
        f["puntos"], f["puntos_criticos"] = len(f.pop("_puntos")), len(f.pop("_criticos"))
        f["kg_pedidos"], f["kg_entregados"] = round(f["kg_pedidos"], 1), round(f["kg_entregados"], 1)
        f["pct_a_tiempo"] = _pct(f["a_tiempo"], f["evaluados"])
        f["pct_criticos_a_tiempo"] = _pct(f["criticos_a_tiempo"], f["criticos_evaluados"])
        f["espera_mediana_h"] = round(statistics.median(esperas), 1) if esperas else None
        f["pendiente_mas_viejo_h"] = (round(max(0.0, (ahora - abierto).total_seconds() / 3600), 1)
                                      if abierto is not None else None)
        salida.append({c: f[c] for c in COLUMNAS})
    return salida


def silencio(con: sqlite3.Connection, desde=None, hasta=None) -> list[dict]:
    """Barrios y veredas del nomenclátor sin ningún pedido en el periodo, con su comuna si se conoce.

    Un lugar tiene pedidos si algún pedido del periodo (las mismas reglas de `resumen`) cae en un punto
    enlazado a ese lugar o en un punto cuyo barrio se llama igual; una vereda, también si el nombre del
    punto la menciona («Salón JAC vereda La Aurora»). En pantalla se dice «sin pedidos registrados»,
    nunca «sin necesidad».
    """
    desde, hasta = _fecha(desde), _fecha(hasta)
    con_pedidos = {p["punto_id"] for p in _pedidos(con, desde, hasta)}
    puntos = [dict(r) for r in con.execute("SELECT id, nombre, barrio FROM puntos") if r["id"] in con_pedidos]
    barrios_con = {normalizar(p["barrio"]) for p in puntos if p["barrio"]}
    nombres_con = [f" {normalizar(p['nombre'])} " for p in puntos]
    de_punto, _ = _territorios(con)
    por_barrio = _comuna_de_barrio()
    for r in con.execute("SELECT id, barrio FROM puntos WHERE barrio IS NOT NULL"):
        if de_punto[r["id"]] != SIN_COMUNA:
            por_barrio.setdefault(normalizar(r["barrio"]), de_punto[r["id"]])
    lugares: dict[tuple[str, str], dict] = {}
    for r in con.execute("SELECT nombre, tipo, punto_id FROM lugares WHERE tipo IN ('barrio','vereda') "
                         "ORDER BY nombre, tipo"):
        l = lugares.setdefault((r["nombre"], r["tipo"]), {"nombre": r["nombre"], "tipo": r["tipo"], "puntos": set()})
        if r["punto_id"] is not None:
            l["puntos"].add(r["punto_id"])
    salida = []
    for (nombre, tipo), l in lugares.items():
        n = normalizar(nombre)
        if l["puntos"] & con_pedidos or n in barrios_con or (
                tipo == "vereda" and any(f" {n} " in x for x in nombres_con)):
            continue
        comuna = por_barrio.get(n) if tipo == "barrio" else None
        enlazadas = sorted({de_punto[i] for i in l["puntos"] if de_punto.get(i, SIN_COMUNA) != SIN_COMUNA})
        salida.append({"nombre": nombre, "tipo": tipo, "comuna": comuna or (enlazadas[0] if enlazadas else None),
                       "estado": SIN_PEDIDOS})
    return sorted(salida, key=lambda s: (s["comuna"] is None, normalizar(s["comuna"]), s["tipo"], normalizar(s["nombre"])))


def _texto(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v)


def _escribir_csv(ruta: Path, columnas: tuple[str, ...], filas: list[dict]) -> None:
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas)
        w.writeheader()
        w.writerows(filas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Resumen por comuna y barrios o veredas sin pedidos registrados.")
    ap.add_argument("--desde", help="inicio del periodo, ISO 8601 (p. ej. 2026-11-21T00:00); incluido")
    ap.add_argument("--hasta", help="fin del periodo, ISO 8601; excluido")
    ap.add_argument("--ahora", help="hora de corte para lo pendiente (por defecto, ahora)")
    ap.add_argument("--csv", metavar="SALIDA", help="exporta la tabla; la lista sin pedidos va a SALIDA_sin_pedidos.csv")
    a = ap.parse_args(argv)
    for nombre in ("desde", "hasta", "ahora"):
        if getattr(a, nombre) and _fecha(getattr(a, nombre)) is None:
            ap.error(f"--{nombre}: fecha ilegible «{getattr(a, nombre)}»; use 2026-11-21T00:00")
    con = db.conectar()
    try:
        tabla = resumen(con, a.desde, a.hasta, a.ahora)
        callados = silencio(con, a.desde, a.hasta)
    finally:
        con.close()
    titulos = ("Territorio", "Puntos", "Críticos", "Pedidos", "Familias", "kg pedidos", "Entregados",
               "kg entregados", "A tiempo", "Evaluados", "% a tiempo", "Críticos a tiempo", "Críticos evaluados",
               "% críticos a tiempo", "Espera mediana (h)", "Pendiente más viejo (h)")
    celdas = [[_texto(f[c]) for c in COLUMNAS] for f in tabla]
    anchos = [max(len(t), *(len(c[i]) for c in celdas)) if celdas else len(t) for i, t in enumerate(titulos)]
    periodo = f"desde {a.desde or 'el inicio'} hasta {a.hasta or 'hoy'}"
    print(f"Resumen por territorio ({periodo}). Datos de la base; las cifras son medidas sobre ella.\n")
    print("  ".join(t.ljust(anchos[i]) if i == 0 else t.rjust(anchos[i]) for i, t in enumerate(titulos)))
    for c in celdas:
        print("  ".join(x.ljust(anchos[i]) if i == 0 else x.rjust(anchos[i]) for i, x in enumerate(c)))
    print("\nA tiempo: entregado a más tardar en su hora límite. Evaluados: pedidos con hora límite ya "
          "entregados o con la hora vencida.")
    print(f"\nBarrios y veredas {SIN_PEDIDOS} ({len(callados)}). No quiere decir que no necesiten nada:")
    for s in callados:
        print(f"  {s['nombre']} ({s['tipo']}{', ' + s['comuna'] if s['comuna'] else ''})")
    if a.csv:
        ruta = Path(a.csv)
        _escribir_csv(ruta, COLUMNAS, tabla)
        otra = ruta.with_name(ruta.stem + "_sin_pedidos" + (ruta.suffix or ".csv"))
        _escribir_csv(otra, COLUMNAS_SILENCIO, callados)
        print(f"\nCSV: {ruta} y {otra}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
