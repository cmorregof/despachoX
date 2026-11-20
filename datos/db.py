"""Acceso compartido a la base. Es lo único que los tres módulos importan en común."""
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
# Varias sesiones trabajan en copias distintas del repositorio. Para que bot, despacho y tablero
# compartan una sola base, apunta DESPACHOX_DB a la misma ruta en todas.
RUTA_DB = Path(os.environ.get("DESPACHOX_DB") or RAIZ / "despachox.db")
BOGOTA = timezone(timedelta(hours=-5))


def ahora() -> str:
    """Hora de Colombia en ISO 8601, el formato de todas las columnas de tiempo."""
    return datetime.now(BOGOTA).isoformat(timespec="seconds")


def conectar(ruta: Path = RUTA_DB) -> sqlite3.Connection:
    """Abre la base (la crea con el esquema si no existe). Filas accesibles por nombre."""
    con = sqlite3.connect(ruta, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")   # bot, optimizador y tablero escriben a la vez
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript((RAIZ / "esquema.sql").read_text(encoding="utf-8"))
    return con


def anotar(con: sqlite3.Connection, quien: str, accion: str, detalle: str = "") -> None:
    """Deja rastro en la bitácora de quién decidió qué."""
    con.execute("INSERT INTO bitacora(cuando, quien, accion, detalle) VALUES (?,?,?,?)",
                (ahora(), quien, accion, detalle))
    con.commit()
