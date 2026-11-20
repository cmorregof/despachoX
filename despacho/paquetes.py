"""Trazabilidad mínima: un paquete por parada del plan aprobado, con un código corto (el del QR).

Uso:
    python -m despacho.paquetes                      # paquetes del plan aprobado
    python -m despacho.paquetes --entregar DX-7KQ3   # marca entregado el paquete y su pedido
    python -m despacho.paquetes --entregar DX-7KQ3 --quien "conductor Camión 1"

Reglas:
- Los paquetes los crea `optimizar.aprobar`, nunca el modelo: nacen `en_ruta` cuando un humano
  aprueba el plan.
- Un pedido tiene un solo paquete vivo. Si un recálculo lo cambia de vehículo, el paquete conserva
  su código y se actualizan kilos y lote. Si el plan nuevo lo deja por fuera, vuelve a `en_bodega`.
- `entregar` pasa el paquete y su pedido a `entregado` y lo anota en la bitácora.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sqlite3
import sys

from datos import db

ALFABETO = "ACDEFGHJKMNPQRTUVWXY34679"     # sin 0/O, 1/I/L, 2/Z, 5/S, 8/B: se dictan sin confusión
VIVOS = ("en_bodega", "en_ruta")


def normalizar_codigo(codigo: str) -> str:
    c = "".join(ch for ch in str(codigo).upper() if ch.isalnum())
    return f"DX-{c[2:]}" if c.startswith("DX") else f"DX-{c}"


def _codigo_nuevo(con: sqlite3.Connection) -> str:
    while True:
        codigo = "DX-" + "".join(secrets.choice(ALFABETO) for _ in range(4))
        if con.execute("SELECT 1 FROM paquetes WHERE codigo=?", (codigo,)).fetchone() is None:
            return codigo


def _lote_principal(surtido: list[dict]) -> int | None:
    """El lote que aporta más kilos al pedido (el que se rastrea si hay que retirar un lote)."""
    if not surtido:
        return None
    return max(surtido, key=lambda l: (l.get("kg") or 0, -(l.get("lote_id") or 0))).get("lote_id")


def crear_para_plan(con: sqlite3.Connection, plan_id: int, anterior: int | None = None) -> list[str]:
    """Crea o pone al día un paquete `en_ruta` por cada parada del plan. Devuelve los códigos.

    anterior: el plan aprobado que este reemplaza. Sus pedidos que no siguen en el plan nuevo
    (y no van a bordo de un vehículo en ruta) vuelven a `confirmado` y su paquete a `en_bodega`.
    """
    fila = con.execute("SELECT resumen FROM planes WHERE id=?", (plan_id,)).fetchone()
    try:
        surtido = (json.loads(fila["resumen"] or "{}") if fila else {}).get("surtido") or {}
    except (TypeError, ValueError, AttributeError):
        surtido = {}
    paradas = con.execute("SELECT pedido_id, kg FROM paradas WHERE plan_id=? AND pedido_id IS NOT NULL "
                          "ORDER BY vehiculo_id, orden", (plan_id,)).fetchall()
    codigos = []
    with con:
        for p in paradas:
            lote = _lote_principal(surtido.get(str(p["pedido_id"])) or [])
            vivo = con.execute(
                f"SELECT codigo FROM paquetes WHERE pedido_id=? AND estado IN ({','.join('?' * len(VIVOS))}) "
                "ORDER BY rowid LIMIT 1", (p["pedido_id"], *VIVOS)).fetchone()
            if vivo:
                con.execute("UPDATE paquetes SET lote_id=?, kg=?, estado='en_ruta' WHERE codigo=?",
                            (lote, p["kg"], vivo["codigo"]))
                codigos.append(vivo["codigo"])
            elif con.execute("SELECT 1 FROM paquetes WHERE pedido_id=? AND estado='entregado'",
                             (p["pedido_id"],)).fetchone() is None:
                codigo = _codigo_nuevo(con)
                con.execute("INSERT INTO paquetes(codigo, pedido_id, lote_id, kg, estado) "
                            "VALUES (?,?,?,?, 'en_ruta')", (codigo, p["pedido_id"], lote, p["kg"]))
                codigos.append(codigo)
        if anterior is not None:
            fuera = [r["pedido_id"] for r in con.execute(
                "SELECT pa.pedido_id FROM paradas pa LEFT JOIN vehiculos v ON v.id = pa.vehiculo_id "
                "WHERE pa.plan_id=? AND pa.pedido_id IS NOT NULL AND COALESCE(v.estado,'') != 'en_ruta' "
                "AND pa.pedido_id NOT IN (SELECT pedido_id FROM paradas WHERE plan_id=? AND pedido_id IS NOT NULL)",
                (anterior, plan_id))]
            for pid in fuera:
                con.execute("UPDATE pedidos SET estado='confirmado' WHERE id=? AND estado='asignado'", (pid,))
                con.execute("UPDATE paquetes SET estado='en_bodega' WHERE pedido_id=? AND estado='en_ruta'", (pid,))
    return codigos


def entregar(con: sqlite3.Connection, codigo: str, quien: str = "despachador") -> bool:
    """Marca entregado el paquete y su pedido, y lo anota en la bitácora. False si no aplica."""
    codigo = normalizar_codigo(codigo)
    r = con.execute("SELECT * FROM paquetes WHERE codigo=?", (codigo,)).fetchone()
    if r is None or r["estado"] not in VIVOS:
        return False
    cuando = db.ahora()
    with con:
        con.execute("UPDATE paquetes SET estado='entregado', entregado_en=? WHERE codigo=?", (cuando, codigo))
        pendientes = con.execute(
            "SELECT COUNT(*) FROM paquetes WHERE pedido_id=? AND estado IN ('en_bodega','en_ruta')",
            (r["pedido_id"],)).fetchone()[0]
        if r["pedido_id"] is not None and pendientes == 0:
            con.execute("UPDATE pedidos SET estado='entregado' WHERE id=?", (r["pedido_id"],))
    db.anotar(con, quien, "entregar paquete", f"{codigo} · pedido {r['pedido_id']} · {r['kg']} kg")
    return True


def listar(con: sqlite3.Connection, plan_id: int | None = None) -> list[dict]:
    """Paquetes de las paradas de un plan (por defecto el aprobado), en orden de ruta."""
    if plan_id is None:
        r = con.execute("SELECT id FROM planes WHERE estado='aprobado' ORDER BY id DESC LIMIT 1").fetchone()
        if r is None:
            return []
        plan_id = r["id"]
    return [dict(x) for x in con.execute(
        "SELECT pq.codigo, pq.estado, pq.kg, pq.lote_id, pq.entregado_en, pa.pedido_id, pa.vehiculo_id, "
        "       v.nombre AS vehiculo, pa.orden, pu.nombre AS punto, lo.producto AS producto_lote "
        "FROM paradas pa JOIN paquetes pq ON pq.pedido_id = pa.pedido_id "
        "LEFT JOIN vehiculos v ON v.id = pa.vehiculo_id LEFT JOIN puntos pu ON pu.id = pa.punto_id "
        "LEFT JOIN lotes lo ON lo.id = pq.lote_id "
        "WHERE pa.plan_id=? AND pq.estado != 'perdido' ORDER BY pa.vehiculo_id, pa.orden", (plan_id,))]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Paquetes del plan aprobado y confirmación de entrega.")
    ap.add_argument("--entregar", metavar="CODIGO", help="marca entregado el paquete y su pedido")
    ap.add_argument("--quien", default="despachador")
    args = ap.parse_args(argv)
    con = db.conectar()
    try:
        if args.entregar:
            if entregar(con, args.entregar, args.quien):
                print(f"{normalizar_codigo(args.entregar)} entregado")
                return 0
            print(f"{normalizar_codigo(args.entregar)}: no existe o ya no está en ruta", file=sys.stderr)
            return 1
        filas = listar(con)
        if not filas:
            print("no hay plan aprobado o no tiene paquetes")
        for f in filas:
            print(f"{f['codigo']}  {f['estado']:<10} {f['vehiculo'] or '?'} #{f['orden']}  "
                  f"pedido {f['pedido_id']}  {f['punto'] or '?'}  {f['kg']} kg  lote {f['lote_id']}")
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    sys.exit(main())
