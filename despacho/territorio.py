"""Vista por territorio: cómo va la atención por comuna y qué barrios no han pedido nada.

Uso:
    python -m despacho.territorio
    python -m despacho.territorio --desde 2026-11-21T00:00 --csv salida.csv

Solo lee la base. No toca el esquema ni el optimizador, y no saca datos personales
(`texto_original` y `remitente_hash` nunca se leen).

Definiciones (encargos/T1_TERRITORIO.md):
- Un pedido cuenta si se creó en el periodo, no está `descartado`, no es duplicado y no es una
  alerta por silencio (esas las crea el sistema, no las pide nadie).
- La hora de entrega es el `entregado_en` más tardío de sus paquetes.
- `pct_a_tiempo` = entregados a tiempo / entregados con `limite_en` y hora de entrega conocida.
- Los pedidos que aún no tienen punto de entrega salen en una fila «sin ubicar».
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from datos import db
from despacho import optimizar
from despacho.cierres import normalizar

SIN_COMUNA = "sin comuna"
SIN_UBICAR = "sin ubicar"
ABIERTOS = ("nuevo", "confirmado", "asignado")
BARRIOS_CSV = Path(__file__).resolve().parent.parent / "datos" / "semilla" / "barrios.csv"
COLUMNAS = ["territorio", "puntos", "puntos_criticos", "pedidos", "familias", "kg_pedidos",
            "entregados", "kg_entregados", "a_tiempo", "pct_a_tiempo", "criticos_a_tiempo",
            "pct_criticos_a_tiempo", "espera_mediana_h", "pendiente_mas_viejo_h"]


def _fecha(valor) -> datetime | None:
    if valor is None or isinstance(valor, datetime):
        return valor if valor is None or valor.tzinfo else valor.replace(tzinfo=db.BOGOTA)
    return optimizar._fecha(str(valor))


def _horas(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 3600


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 1) if d else None


def _tiene_origen(con: sqlite3.Connection) -> bool:
    return any(r["name"] == "origen" for r in con.execute("PRAGMA table_info(pedidos)"))


def _pedidos(con: sqlite3.Connection, desde, hasta) -> list[dict]:
    """Pedidos que cuentan en el periodo, con su punto, su comuna y su hora de entrega."""
    filtro_origen = "AND COALESCE(pe.origen, 'mensaje') != 'silencio'" if _tiene_origen(con) else ""
    filas = con.execute(
        "SELECT pe.id, pe.creado_en, pe.punto_id, pe.familias, pe.kg_estimado, pe.productos, pe.urgencia, "
        "       pe.limite_en, pe.estado, pu.comuna, pu.barrio, COALESCE(pu.critico, 0) AS critico, "
        "       (SELECT MAX(entregado_en) FROM paquetes pq WHERE pq.pedido_id = pe.id "
        "          AND pq.estado = 'entregado') AS entregado_en, "
        "       (SELECT SUM(kg) FROM paquetes pq WHERE pq.pedido_id = pe.id "
        "          AND pq.estado = 'entregado') AS kg_paquetes "
        "FROM pedidos pe LEFT JOIN puntos pu ON pu.id = pe.punto_id "
        f"WHERE pe.estado != 'descartado' AND pe.duplicado_de IS NULL {filtro_origen} ORDER BY pe.id").fetchall()
    desde, hasta = _fecha(desde), _fecha(hasta)
    salida = []
    for r in filas:
        p = dict(r)
        creado = _fecha(p["creado_en"])
        if creado is None or (desde and creado < desde) or (hasta and creado > hasta):
            continue
        p["creado"] = creado
        p["kg"] = round(sum(l["kg"] for l in optimizar._demanda(p)), 3)
        if p["punto_id"] is None:
            p["territorio"] = SIN_UBICAR
        else:
            p["territorio"] = (p["comuna"] or "").strip() or SIN_COMUNA
        salida.append(p)
    return salida


def resumen(con: sqlite3.Connection, desde=None, hasta=None, ahora=None) -> list[dict]:
    """Una fila por comuna con puntos de entrega (con o sin pedidos), más «sin comuna» y «sin ubicar»."""
    ahora = _fecha(ahora) or datetime.now(db.BOGOTA)
    pedidos = _pedidos(con, desde, hasta)
    territorios = {(r["comuna"] or "").strip() or SIN_COMUNA
                   for r in con.execute("SELECT comuna FROM puntos")}
    territorios |= {p["territorio"] for p in pedidos}
    filas = []
    for t in sorted(territorios, key=lambda t: (t in (SIN_COMUNA, SIN_UBICAR), t == SIN_UBICAR, t)):
        ps = [p for p in pedidos if p["territorio"] == t]
        if not ps and t in (SIN_COMUNA, SIN_UBICAR):
            continue
        entregados = [p for p in ps if p["estado"] == "entregado"]
        medibles = [p for p in entregados if p["limite_en"] and p["entregado_en"]]
        a_tiempo = [p for p in medibles if _fecha(p["entregado_en"]) <= _fecha(p["limite_en"])]
        crit_medibles = [p for p in medibles if p["critico"]]
        crit_a_tiempo = [p for p in a_tiempo if p["critico"]]
        esperas = [_horas(p["creado"], _fecha(p["entregado_en"])) for p in entregados if p["entregado_en"]]
        abiertos = [p for p in ps if p["estado"] in ABIERTOS]
        puntos = {p["punto_id"] for p in ps if p["punto_id"] is not None}
        filas.append({
            "territorio": t,
            "puntos": len(puntos),
            "puntos_criticos": len({p["punto_id"] for p in ps if p["punto_id"] is not None and p["critico"]}),
            "pedidos": len(ps),
            "familias": sum(p["familias"] or 0 for p in ps),
            "kg_pedidos": round(sum(p["kg"] for p in ps), 1),
            "entregados": len(entregados),
            "kg_entregados": round(sum(p["kg_paquetes"] if p["kg_paquetes"] is not None else p["kg"]
                                       for p in entregados), 1),
            "a_tiempo": len(a_tiempo),
            "pct_a_tiempo": _pct(len(a_tiempo), len(medibles)),
            "criticos_a_tiempo": len(crit_a_tiempo),
            "pct_criticos_a_tiempo": _pct(len(crit_a_tiempo), len(crit_medibles)),
            "espera_mediana_h": round(statistics.median(esperas), 1) if esperas else None,
            "pendiente_mas_viejo_h": (round(max(_horas(p["creado"], ahora) for p in abiertos), 1)
                                      if abiertos else None),
        })
    return filas


def _comunas_de_barrios(con: sqlite3.Connection) -> dict[str, str]:
    """Comuna de cada barrio: primero la de los puntos de entrega, luego la de barrios.csv."""
    comunas: dict[str, str] = {}
    if BARRIOS_CSV.exists():
        with BARRIOS_CSV.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("nombre") and r.get("comuna"):
                    comunas[normalizar(r["nombre"])] = r["comuna"].strip()
    for r in con.execute("SELECT barrio, comuna FROM puntos WHERE barrio IS NOT NULL AND comuna IS NOT NULL"):
        comunas[normalizar(r["barrio"])] = r["comuna"].strip()
    return comunas


def silencio(con: sqlite3.Connection, desde=None, hasta=None) -> list[dict]:
    """Barrios y veredas del nomenclátor sin ningún pedido en el periodo: «sin pedidos registrados».

    Un barrio tiene pedidos si algún pedido que cuenta cae en un punto de ese barrio, o si su
    ubicación confirmada es ese lugar. Que no haya pedidos no dice que no haya necesidad.
    """
    pedidos = _pedidos(con, desde, hasta)
    ids = [p["id"] for p in pedidos]
    con_pedidos = {normalizar(p["barrio"]) for p in pedidos if p["barrio"]}
    if ids:
        marcas = ",".join("?" * len(ids))
        con_pedidos |= {normalizar(r["nombre"]) for r in con.execute(
            "SELECT l.nombre FROM ubicaciones u JOIN lugares l ON l.id = u.lugar_id "
            f"WHERE u.tabla='pedidos' AND u.estado='confirmada' AND u.fila_id IN ({marcas})", ids)}
    comunas = _comunas_de_barrios(con)
    vistos, salida = set(), []
    for r in con.execute("SELECT DISTINCT nombre, tipo FROM lugares WHERE tipo IN ('barrio','vereda')"):
        clave = normalizar(r["nombre"])
        if clave in con_pedidos or (clave, r["tipo"]) in vistos:
            continue
        vistos.add((clave, r["tipo"]))
        salida.append({"nombre": r["nombre"], "tipo": r["tipo"], "comuna": comunas.get(clave)})
    return sorted(salida, key=lambda x: (x["comuna"] is None, x["comuna"] or "", x["tipo"], x["nombre"]))


def _texto(v) -> str:
    return "–" if v is None else (f"{v:g}" if isinstance(v, float) else str(v))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Atención por comuna y barrios sin pedidos registrados.")
    ap.add_argument("--desde", help="ISO 8601, por ejemplo 2026-11-21T00:00")
    ap.add_argument("--hasta", help="ISO 8601")
    ap.add_argument("--csv", type=Path, help="exporta la tabla; la lista de barrios va a <nombre>_sin_pedidos.csv")
    args = ap.parse_args(argv)
    con = db.conectar()
    try:
        filas = resumen(con, args.desde, args.hasta)
        callados = silencio(con, args.desde, args.hasta)
    finally:
        con.close()
    cortas = ["territorio", "pedidos", "entregados", "pct_a_tiempo", "pct_criticos_a_tiempo",
              "espera_mediana_h", "pendiente_mas_viejo_h"]
    ancho = max([len(f["territorio"]) for f in filas] + [10])
    print(f"{'territorio':<{ancho}}  " + "  ".join(c for c in cortas[1:]))
    for f in filas:
        print(f"{f['territorio']:<{ancho}}  " + "  ".join(f"{_texto(f[c]):>{len(c)}}" for c in cortas[1:]))
    print(f"\nBarrios y veredas sin pedidos registrados: {len(callados)}")
    for c in callados:
        print(f"  {c['nombre']} ({c['tipo']}, {c['comuna'] or 'comuna sin dato'})")
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNAS)
            w.writeheader()
            w.writerows(filas)
        otro = args.csv.with_name(args.csv.stem + "_sin_pedidos.csv")
        with otro.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["nombre", "tipo", "comuna"])
            w.writeheader()
            w.writerows(callados)
        print(f"\nCSV: {args.csv} y {otro}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
