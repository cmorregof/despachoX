"""Caché por texto para la búsqueda de lugares. Mejora de rendimiento, no función nueva.

`lugares.nomenclator.buscar` compara el texto contra todos los nombres y apodos con difflib: es el
97 % del tiempo de cada mensaje en el hilo del bot (`entrada/ESCALA.md`). Como la gente repite los
mismos barrios, guardar el resultado por texto evita repetir la cuenta.

No cambia el resultado. La clave lleva el texto, los tipos y una «versión» del nomenclátor: número de
filas, id máximo y suma de puntos asignados. Si se aprende un apodo (`aprender` inserta una fila) o se
asigna un punto, la versión cambia y la búsqueda se vuelve a calcular. Lo prueba
`entrada/pruebas/test_cache_lugares.py`. Este archivo no toca `lugares/`: envuelve su función en
tiempo de ejecución, y `quitar()` la deja como estaba.
"""
from __future__ import annotations

import copy
import sqlite3
from collections import OrderedDict

from lugares import nomenclator

MAXIMO = 4096
_original = None
_guardado: OrderedDict = OrderedDict()
aciertos = {"si": 0, "no": 0}


def _version(con: sqlite3.Connection) -> tuple:
    archivo = con.execute("PRAGMA database_list").fetchone()["file"] if con.row_factory else ""
    return (archivo,) + tuple(con.execute("SELECT COUNT(*), MAX(id), TOTAL(punto_id) FROM lugares").fetchone())


def _buscar_con_cache(con: sqlite3.Connection, texto: str, tipos: tuple[str, ...] | None = None):
    clave = (texto, tuple(tipos) if tipos else None, _version(con))
    if clave in _guardado:
        _guardado.move_to_end(clave)
        aciertos["si"] += 1
        return [copy.copy(c) for c in _guardado[clave]]        # copias: quien la use puede modificarla
    aciertos["no"] += 1
    resultado = _original(con, texto, tipos)
    _guardado[clave] = [copy.copy(c) for c in resultado]
    if len(_guardado) > MAXIMO:
        _guardado.popitem(last=False)
    return resultado


def instalar() -> None:
    """Pone el caché delante de `nomenclator.buscar`. Llamarla dos veces no hace nada."""
    global _original
    if _original is None:
        _original = nomenclator.buscar
        nomenclator.buscar = _buscar_con_cache


def quitar() -> None:
    global _original
    if _original is not None:
        nomenclator.buscar = _original
        _original = None
    _guardado.clear()
    aciertos.update(si=0, no=0)
