"""Escribe en `pedidos` y `cierres`. Es lo único que entrada/ guarda por su cuenta; el lugar lo
lleva a la fila el módulo lugares/ cuando alguien lo confirma."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta

from datos import db
from entrada import raciones
from entrada.extraer import Cierre, Pedido

VENTANA_DUPLICADO_H = 2


def _hace(horas: float) -> str:
    return (datetime.now(db.BOGOTA) - timedelta(hours=horas)).isoformat(timespec="seconds")


def _hay_columna(con: sqlite3.Connection, tabla: str, columna: str) -> bool:
    return any(r[1] == columna for r in con.execute(f"PRAGMA table_info({tabla})"))


def _kg_total(lineas: list[dict]) -> float | None:
    kilos = [q.get("kg") for q in lineas]
    return round(sum(kilos), 1) if kilos and all(k for k in kilos) else None


def guardar_pedido(con: sqlite3.Connection, p: Pedido, texto: str, remitente: str,
                   lineas: list[dict] | None = None, dudas: list[str] | None = None) -> int:
    """Pedido en estado `nuevo`, sin punto. `lineas` son los productos ya completados por
    `raciones` (con la marca `supuesto` donde la mesa puso los kilos). `kg_estimado` solo se llena
    si todos los productos tienen kilos; si no, despacho/ los estima por familia. Las `dudas` se
    guardan si la base ya tiene la columna `pedidos.dudas` (pedida por el canal)."""
    lineas = lineas if lineas is not None else [q.model_dump() for q in p.productos]
    limite = _hace(-p.horas_limite) if p.horas_limite else None
    cur = con.execute(
        "INSERT INTO pedidos(creado_en, familias, kg_estimado, productos, urgencia, limite_en, estado, "
        "texto_original, remitente_hash) VALUES (?,?,?,?,?,?, 'nuevo', ?,?)",
        (db.ahora(), p.familias, _kg_total(lineas),
         json.dumps(lineas, ensure_ascii=False) if lineas else None,
         p.urgencia, limite, texto, remitente))
    if dudas and _hay_columna(con, "pedidos", "dudas"):
        con.execute("UPDATE pedidos SET dudas=? WHERE id=?", (json.dumps(dudas, ensure_ascii=False), cur.lastrowid))
    con.commit()
    return cur.lastrowid


def actualizar_familias(con: sqlite3.Connection, pedido_id: int, familias: int, nota: str) -> bool:
    """La persona respondió «¿para cuántas familias?». Recalcula los kilos que puso la mesa (los
    marcados `supuesto`) y deja la nota. Solo si el pedido aún no está en un plan."""
    f = con.execute("SELECT productos, estado FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if f is None or f["estado"] not in ("nuevo", "confirmado"):
        return False
    try:
        lineas = json.loads(f["productos"] or "[]")
    except ValueError:
        lineas = []
    notas = raciones.completar_kilos(lineas, familias)
    con.execute("UPDATE pedidos SET familias=?, productos=?, kg_estimado=? WHERE id=?",
                (familias, json.dumps(lineas, ensure_ascii=False) if lineas else None, _kg_total(lineas), pedido_id))
    if _hay_columna(con, "pedidos", "dudas"):
        previas = con.execute("SELECT dudas FROM pedidos WHERE id=?", (pedido_id,)).fetchone()["dudas"]
        dudas = [d for d in json.loads(previas or "[]") if not d.startswith(("Falta", "Familias", "Kilos"))]
        con.execute("UPDATE pedidos SET dudas=? WHERE id=?",
                    (json.dumps(dudas + [nota] + notas, ensure_ascii=False), pedido_id))
    con.commit()
    return True


def guardar_cierre(con: sqlite3.Connection, c: Cierre, texto: str) -> int:
    """Cierre en estado `reportado`, sin coordenadas. `lugar` guarda lo que dijo la persona hasta
    que se confirme."""
    cur = con.execute(
        "INSERT INTO cierres(creado_en, descripcion, lugar, tipos_bloqueados, estado, texto_original) "
        "VALUES (?,?,?,?, 'reportado', ?)",
        (db.ahora(), c.descripcion, c.lugar, json.dumps(c.tipos_bloqueados), texto))
    con.commit()
    return cur.lastrowid


def guardar_crudo(con: sqlite3.Connection, texto: str, remitente: str) -> int:
    """El mensaje no se pudo leer: queda como pedido `nuevo` sin datos para que el despachador lo vea."""
    cur = con.execute("INSERT INTO pedidos(creado_en, estado, texto_original, remitente_hash) "
                      "VALUES (?, 'nuevo', ?, ?)", (db.ahora(), texto, remitente))
    con.commit()
    return cur.lastrowid


def marcar_duplicado(con: sqlite3.Connection, pedido_id: int) -> int | None:
    """Si ya hay un pedido vivo del mismo punto en las últimas dos horas, enlaza este con aquel.
    Solo marca; descartarlo o sumarlo es decisión del despachador."""
    p = con.execute("SELECT punto_id FROM pedidos WHERE id=?", (pedido_id,)).fetchone()
    if p is None or p["punto_id"] is None:
        return None
    previo = con.execute(
        "SELECT id FROM pedidos WHERE punto_id=? AND id<>? AND creado_en>=? AND duplicado_de IS NULL "
        "AND origen='mensaje' AND estado IN ('nuevo','confirmado','asignado') ORDER BY id LIMIT 1",
        (p["punto_id"], pedido_id, _hace(VENTANA_DUPLICADO_H))).fetchone()
    if previo is None:
        return None
    con.execute("UPDATE pedidos SET duplicado_de=? WHERE id=?", (previo["id"], pedido_id))
    con.commit()
    return previo["id"]


def pedidos_de(con: sqlite3.Connection, remitente: str, limite: int = 5) -> list[sqlite3.Row]:
    """Los últimos pedidos de un remitente, con el nombre del punto si ya está ubicado."""
    return con.execute(
        "SELECT p.id, p.creado_en, p.estado, p.familias, p.duplicado_de, t.nombre AS punto, "
        "(SELECT pa.llegada_estimada FROM paradas pa JOIN planes pl ON pl.id = pa.plan_id "
        " WHERE pa.pedido_id = p.id AND pl.estado = 'aprobado' ORDER BY pl.id DESC LIMIT 1) AS llegada "
        "FROM pedidos p LEFT JOIN puntos t ON t.id = p.punto_id WHERE p.remitente_hash=? "
        "ORDER BY p.id DESC LIMIT ?", (remitente, limite)).fetchall()
