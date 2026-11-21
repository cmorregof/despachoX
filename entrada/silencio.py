"""Alerta por silencio: un punto crítico que no escribe sube en la lista en vez de desaparecer de ella.

Hoy, un barrio que no escribe no existe para quien despacha: el que no pudo pedir, no recibe. Este
módulo vigila los puntos con `critico = 1` y, si uno lleva demasiado tiempo sin un pedido, deja una
fila en `pedidos` con `origen='silencio'` para que el despachador decida si manda a verificar o la
descarta. No despacha nada, no inventa familias ni kilos y nunca usa urgencia 3: una verificación no
puede desplazar a un pedido real.

SUPUESTOS DECLARADOS (del equipo, sin fuente; ajustables por variable de entorno):
- UMBRAL_H = 6 horas sin un pedido con lugar confirmado (`DESPACHOX_SILENCIO_HORAS`).
- La jornada empieza a las 06:00, hora de Colombia (`DESPACHOX_JORNADA_INICIO`). Un punto que nunca
  ha escrito cuenta su silencio desde esa hora.
- Cuenta como contacto solo un pedido de origen `mensaje` con lugar confirmado en ese punto, en
  cualquier estado. Un mensaje cuyo lugar nadie confirmó no se sabe de qué punto es.

    python -m entrada.silencio                       # una revisión sobre DESPACHOX_DB
    python -m entrada.silencio --ahora 2026-11-21T14:00:00-05:00 --umbral 6
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, time as hora_del_dia, timedelta

from datos import db

UMBRAL_H = float(os.environ.get("DESPACHOX_SILENCIO_HORAS") or 6)
JORNADA_INICIO = os.environ.get("DESPACHOX_JORNADA_INICIO") or "06:00"
CADA_MIN = float(os.environ.get("DESPACHOX_SILENCIO_MIN") or 10)     # cada cuánto revisa el bot
QUIEN = "silencio"


def _inicio_jornada(ahora: datetime) -> datetime:
    """La última vez que dieron las 06:00 (o la hora configurada): hoy, o ayer si aún no es la hora."""
    h, m = (int(x) for x in JORNADA_INICIO.split(":"))
    inicio = datetime.combine(ahora.date(), hora_del_dia(h, m), tzinfo=db.BOGOTA)
    return inicio if inicio <= ahora else inicio - timedelta(days=1)


def _con_zona(t: datetime) -> datetime:
    return t if t.tzinfo else t.replace(tzinfo=db.BOGOTA)


def _texto(horas: float) -> str:
    return f"Sin contacto hace {int(horas)} h. Visita de verificación."


def revisar(con: sqlite3.Connection, ahora: datetime | None = None, umbral_h: float | None = None) -> dict:
    """Una pasada por los puntos críticos. Crea, actualiza o descarta alertas y devuelve qué hizo."""
    ahora = _con_zona(ahora or datetime.now(db.BOGOTA))
    umbral_h = UMBRAL_H if umbral_h is None else umbral_h
    inicio = _inicio_jornada(ahora)
    hecho = {"creadas": [], "actualizadas": [], "descartadas": [], "revisados": 0}
    for punto in con.execute("SELECT id, nombre FROM puntos WHERE critico = 1 ORDER BY id").fetchall():
        hecho["revisados"] += 1
        ultimo = con.execute("SELECT MAX(creado_en) FROM pedidos WHERE punto_id=? AND origen='mensaje'",
                             (punto["id"],)).fetchone()[0]
        viva = con.execute("SELECT id, creado_en FROM pedidos WHERE punto_id=? AND origen='silencio' "
                           "AND estado='nuevo' ORDER BY id LIMIT 1", (punto["id"],)).fetchone()
        alerta_en = _con_zona(datetime.fromisoformat(viva["creado_en"])) if viva else None
        if ultimo:
            desde = _con_zona(datetime.fromisoformat(ultimo))
        else:                                       # nunca ha escrito: desde el inicio de la jornada, o
            desde = inicio                          # desde antes, si ya había una alerta de otra jornada
            if alerta_en is not None:
                desde = min(desde, alerta_en - timedelta(hours=umbral_h))
        if viva is not None and ultimo and desde >= alerta_en:     # escribió después de la alerta
            _descartar(con, viva["id"], "el punto volvió a escribir")
            hecho["descartadas"].append(punto["id"])
            viva = None
        horas = max(0.0, (ahora - desde).total_seconds() / 3600)
        if horas < umbral_h:
            continue
        if viva is not None:
            con.execute("UPDATE pedidos SET texto_original=? WHERE id=?", (_texto(horas), viva["id"]))
            hecho["actualizadas"].append(punto["id"])
        else:
            cur = con.execute(
                "INSERT INTO pedidos(creado_en, punto_id, familias, kg_estimado, productos, urgencia, estado, "
                "texto_original, remitente_hash, origen) VALUES (?,?,NULL,NULL,NULL,2,'nuevo',?,NULL,'silencio')",
                (ahora.isoformat(timespec="seconds"), punto["id"], _texto(horas)))
            con.execute("INSERT INTO bitacora(cuando, quien, accion, detalle) VALUES (?,?,?,?)",
                        (db.ahora(), QUIEN, "alerta por silencio",
                         f"pedido {cur.lastrowid}, punto {punto['id']} ({punto['nombre']}), {int(horas)} h"))
            hecho["creadas"].append(punto["id"])
    con.commit()
    return hecho


def _descartar(con: sqlite3.Connection, pedido_id: int, motivo: str) -> None:
    con.execute("UPDATE pedidos SET estado='descartado' WHERE id=? AND origen='silencio' AND estado='nuevo'",
                (pedido_id,))
    con.execute("INSERT INTO bitacora(cuando, quien, accion, detalle) VALUES (?,?,?,?)",
                (db.ahora(), QUIEN, "alerta descartada", f"pedido {pedido_id}: {motivo}"))


def apagar(con: sqlite3.Connection, punto_id: int | None) -> int | None:
    """Llegó un pedido real de ese punto: la alerta viva queda descartada. Devuelve su id."""
    if punto_id is None:
        return None
    viva = con.execute("SELECT id FROM pedidos WHERE punto_id=? AND origen='silencio' AND estado='nuevo' "
                       "ORDER BY id LIMIT 1", (punto_id,)).fetchone()
    if viva is None:
        return None
    _descartar(con, viva["id"], "llegó un mensaje real del punto")
    con.commit()
    return viva["id"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Una revisión de silencio sobre la base compartida.")
    ap.add_argument("--ahora", help="hora ISO para simular, por ejemplo 2026-11-21T14:00:00-05:00")
    ap.add_argument("--umbral", type=float, help=f"horas sin contacto (por defecto {UMBRAL_H:g})")
    a = ap.parse_args(argv)
    from dotenv import load_dotenv
    load_dotenv(db.RAIZ.parent / ".env")
    con = db.conectar(os.environ.get("DESPACHOX_DB") or db.RUTA_DB)
    ahora = datetime.fromisoformat(a.ahora) if a.ahora else None
    h = revisar(con, ahora, a.umbral)
    print(f"Puntos críticos revisados: {h['revisados']}")
    print(f"Alertas nuevas: {len(h['creadas'])} {h['creadas'] or ''}")
    print(f"Alertas actualizadas: {len(h['actualizadas'])} · descartadas: {len(h['descartadas'])}")
    for f in con.execute("SELECT p.id, t.nombre, p.texto_original FROM pedidos p JOIN puntos t ON t.id=p.punto_id "
                         "WHERE p.origen='silencio' AND p.estado='nuevo' ORDER BY p.id"):
        print(f"  #{f['id']} · {f['nombre']} · {f['texto_original']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
