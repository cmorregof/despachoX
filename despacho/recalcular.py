"""Recalcula el plan cuando hay cierres viales confirmados.

Uso:
    python -m despacho.recalcular              # motivo «cierre N», con N el cierre confirmado más reciente
    python -m despacho.recalcular --cierre 3   # nombra otro cierre en el motivo
    python -m despacho.recalcular --motivo "pedido nuevo"   # recálculo que no nace de un cierre

Ubica en el grafo cada cierre vigente (por `vias.csv` o por la arista más cercana), marca el
plan vigente como `reemplazado` y resuelve de nuevo sin las aristas cerradas. El plan nuevo
nace `propuesto`: el despachador lo aprueba. Imprime el id del plan.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys

from datos import db
from despacho import optimizar


def recalcular(con: sqlite3.Connection | None = None, cierre: int | None = None,
               segundos: int = optimizar.LIMITE_BUSQUEDA_S, g=None, ahora=None,
               motivo: str | None = None) -> int:
    propia = con is None
    con = con or db.conectar()
    try:
        if cierre is None:
            r = con.execute("SELECT MAX(id) AS n FROM cierres WHERE estado='confirmado'").fetchone()
            cierre = r["n"] if r else None
        if motivo is None:
            motivo = f"cierre {cierre}" if cierre is not None else "recálculo sin cierres confirmados"
        return optimizar.planificar(con, motivo=motivo, segundos=segundos, recalculo=True, g=g, ahora=ahora)
    finally:
        if propia:
            con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Recalcula el plan con los cierres confirmados.")
    ap.add_argument("--cierre", type=int, help="id del cierre que motiva el recálculo")
    ap.add_argument("--segundos", type=int, default=optimizar.LIMITE_BUSQUEDA_S, help="límite de búsqueda (máx. 10)")
    ap.add_argument("--motivo", help='texto del motivo, p. ej. "pedido nuevo"; por defecto «cierre N»')
    args = ap.parse_args(argv)
    print(recalcular(cierre=args.cierre, segundos=args.segundos, motivo=args.motivo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
