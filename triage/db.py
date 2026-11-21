"""Conexión del triage: la base compartida más las tablas de triage/esquema_triage.sql."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from datos import db as datos_db
from triage import config

ESQUEMA = Path(__file__).resolve().with_name("esquema_triage.sql")
# Orden de borrado: primero las que tienen llaves foráneas hacia las otras.
TABLAS_TRIAGE = ("solicitudes", "tareas_campo", "remitentes", "zonas", "parametros")


def conectar(ruta) -> sqlite3.Connection:
    """Abre (o crea) la base en `ruta` con el esquema común y el de triage."""
    con = datos_db.conectar(Path(ruta))
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    config.sembrar(con)
    return con


def anotar_regla(con: sqlite3.Connection, quien: str, accion: str, detalle: dict, cuando) -> None:
    """Bitácora de una decisión de regla, sin commit (va dentro de la transacción del lote).

    `cuando` es la hora simulada del lote (inyectable), no la del reloj.
    """
    texto = json.dumps(detalle, ensure_ascii=False, sort_keys=True, default=str)
    momento = cuando.isoformat(timespec="seconds") if hasattr(cuando, "isoformat") else str(cuando)
    con.execute("INSERT INTO bitacora(cuando, quien, accion, detalle) VALUES (?,?,?,?)",
                (momento, quien, accion, texto))


def reiniciar(con: sqlite3.Connection) -> None:
    """Borra solo las tablas de triage (y lo que las reglas de triage anotaron) y las recrea."""
    if con.in_transaction:
        con.commit()
    for tabla in TABLAS_TRIAGE:
        con.execute(f"DROP TABLE IF EXISTS {tabla}")   # nombres fijos de este módulo, no datos
    marcas = ",".join("?" * len(config.ACCIONES_REGLA))
    con.execute(f"DELETE FROM bitacora WHERE quien LIKE 'regla:%' AND accion IN ({marcas})",
                config.ACCIONES_REGLA)
    con.commit()
    con.executescript(ESQUEMA.read_text(encoding="utf-8"))
    config.sembrar(con)
