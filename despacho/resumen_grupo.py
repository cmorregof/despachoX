"""Resumen de un grupo de pedidos para el despachador, leído por el modelo.

Regla: el modelo lee y resume; no decide. Las familias, los kilos, la urgencia y la prioridad del grupo
los suma `despacho/agrupar.py` con código, y el resumen no los cambia. El despachador confirma cada grupo.

El texto se guarda en la tabla `resumenes_grupo` (datos/esquema.sql) y el tablero lo muestra con la
etiqueta «leído por el modelo». En las pruebas el extractor es falso: aquí no se llama a ninguna API.
"""
from __future__ import annotations

import json
import sqlite3
from typing import Callable, Iterable

from datos import db
from entrada.privacidad import limpiar

TOPE_TEXTOS = 60
TOPE_RESUMEN = 600

INSTRUCCION = (
    "Escriba para el despachador dos o tres líneas en español, tratándolo de usted: qué piden estos "
    "pedidos, qué casos especiales aparecen (bebés, adultos mayores, enfermos, alimentos que necesitan "
    "frío, agua) y qué no se entiende. Las familias y los kilos de arriba ya están sumados por el "
    "sistema: no los recalcule. Prohibido inventar cantidades o cambiar las dadas. No decida prioridad "
    "ni ruta.")


def texto_para_modelo(grupo, puntos: dict | None = None) -> str:
    """Arma la entrada del modelo: cabecera con los números del código y los textos limpios, numerados.

    `puntos` es opcional: {punto_id: nombre}. Sin él, la cabecera dice solo el id del punto.
    """
    nombre = (puntos or {}).get(grupo.punto_id)
    punto = f"punto {grupo.punto_id}" + (f" ({limpiar(nombre)})" if nombre else "")
    lineas = [
        f"Grupo de pedidos del {punto}.",
        f"Pedidos: {len(grupo.pedidos)}. Familias sumadas por el sistema: {grupo.familias}. "
        f"Kilos sumados por el sistema: {grupo.kg:g}.",
        "",
        "Textos de los pedidos:",
    ]
    for i, p in enumerate(grupo.pedidos[:TOPE_TEXTOS], start=1):
        texto = limpiar(p.get("texto_original")) if p.get("texto_original") else ""
        lineas.append(f"{i}. {texto or '(sin texto)'}")
    sobran = len(grupo.pedidos) - TOPE_TEXTOS
    if sobran > 0:
        lineas.append(f"y {sobran} textos más.")
    lineas += ["", INSTRUCCION]
    return "\n".join(lineas)


def resumir(grupo, extractor: Callable[[str], str], puntos: dict | None = None) -> str:
    """Pasa el texto del grupo al extractor (inyectado) y recorta la respuesta a 600 caracteres."""
    salida = extractor(texto_para_modelo(grupo, puntos)) or ""
    return str(salida).strip()[:TOPE_RESUMEN]


def extractor_modelo() -> Callable[[str], str]:
    """Devuelve un extractor que llama a Claude con `entrada.extraer.MODELO`.

    No se probó en esta sesión: no se llamó a la API. Importa `anthropic` solo al usarse.
    """
    try:
        from entrada.extraer import MODELO as modelo
    except Exception:  # noqa: BLE001 - sin el módulo de entrada se usa el mismo valor por defecto
        modelo = "claude-haiku-5-5"

    def extraer(texto: str) -> str:
        import anthropic
        r = anthropic.Anthropic().messages.create(
            model=modelo, max_tokens=400,
            messages=[{"role": "user", "content": texto}])
        return "".join(getattr(b, "text", "") for b in r.content)
    return extraer


# ---------- base ----------

def _ids(grupo) -> str:
    return json.dumps(sorted(int(i) for i in grupo.pedido_ids))


def guardar(con: sqlite3.Connection, grupo, resumen: str, modelo: str | None) -> None:
    """Guarda o reemplaza el resumen del grupo por su clave."""
    con.execute("INSERT OR REPLACE INTO resumenes_grupo(clave, punto_id, pedido_ids, resumen, modelo, creado_en) "
                "VALUES (?,?,?,?,?,?)",
                (grupo.clave, grupo.punto_id, _ids(grupo), resumen, modelo, db.ahora()))
    con.commit()


def leer(con: sqlite3.Connection, clave: str) -> dict | None:
    """El resumen guardado de un grupo, o None. `pedido_ids` vuelve como lista."""
    fila = con.execute("SELECT * FROM resumenes_grupo WHERE clave=?", (clave,)).fetchone()
    if fila is None:
        return None
    d = dict(fila)
    d["pedido_ids"] = json.loads(d["pedido_ids"] or "[]")
    return d


def resumir_y_guardar(con: sqlite3.Connection, grupos: Iterable, extractor: Callable[[str], str],
                      modelo: str = "falso", solo_faltantes: bool = True, puntos: dict | None = None) -> int:
    """Resume los grupos sin resumen guardado (o todos, si `solo_faltantes` es False). Devuelve cuántos."""
    n = 0
    for g in grupos:
        if solo_faltantes and leer(con, g.clave) is not None:
            continue
        guardar(con, g, resumir(g, extractor, puntos), modelo)
        n += 1
    return n
