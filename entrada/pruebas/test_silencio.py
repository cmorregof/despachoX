"""Alerta por silencio: el punto crítico que no escribe sube en la lista. Sin red; horas fijas."""
import asyncio
import sqlite3
from datetime import datetime, timedelta

import pytest

from datos import db
from entrada import silencio
from entrada.bot import vigilar_silencio
from entrada.pruebas.simulador import ClienteSimulado

AHORA = datetime(2026, 11, 21, 14, 0, tzinfo=db.BOGOTA)          # 8 h después del inicio de la jornada


def _criticos(con):
    return [r[0] for r in con.execute("SELECT id FROM puntos WHERE critico=1 ORDER BY id")]


def _pedido_real(con, punto_id, hace_h):
    con.execute("INSERT INTO pedidos(creado_en, punto_id, familias, estado, origen) VALUES (?,?,10,'nuevo','mensaje')",
                ((AHORA - timedelta(hours=hace_h)).isoformat(timespec="seconds"), punto_id))
    con.commit()


def _alertas(con, punto_id=None, estado="nuevo"):
    sql = "SELECT * FROM pedidos WHERE origen='silencio' AND estado=?" + (" AND punto_id=?" if punto_id else "")
    return con.execute(sql, (estado, punto_id) if punto_id else (estado,)).fetchall()


@pytest.fixture
def puntos(con):
    c = _criticos(con)
    assert len(c) >= 2, "la semilla debe traer al menos dos puntos críticos"
    return c


def test_callado_7_horas_genera_alerta_y_el_que_escribio_hace_2_no(con, puntos):
    callado, activo = puntos[0], puntos[1]
    _pedido_real(con, callado, 7)
    _pedido_real(con, activo, 2)
    h = silencio.revisar(con, AHORA)
    assert callado in h["creadas"] and activo not in h["creadas"]
    a, = _alertas(con, callado)
    assert a["texto_original"] == "Sin contacto hace 7 h. Visita de verificación."
    assert (a["urgencia"], a["familias"], a["kg_estimado"], a["productos"], a["remitente_hash"]) == (2, None, None, None, None)
    assert not _alertas(con, activo)
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='alerta por silencio'").fetchone()[0] == len(h["creadas"])


def test_punto_que_nunca_escribio_cuenta_desde_el_inicio_de_la_jornada(con, puntos):
    silencio.revisar(con, AHORA.replace(hour=11))                   # 5 h desde las 06:00: aún no
    assert not _alertas(con)
    silencio.revisar(con, AHORA)                                    # 8 h
    assert len(_alertas(con)) == len(puntos)
    assert all(a["texto_original"].startswith("Sin contacto hace 8 h") for a in _alertas(con))


def test_el_mismo_punto_no_genera_dos_y_las_horas_se_actualizan(con, puntos):
    p = puntos[0]
    _pedido_real(con, p, 7)
    silencio.revisar(con, AHORA)
    h = silencio.revisar(con, AHORA + timedelta(hours=3))
    a, = _alertas(con, p)
    assert p in h["actualizadas"] and p not in h["creadas"]
    assert a["texto_original"] == "Sin contacto hace 10 h. Visita de verificación."


def test_la_alerta_de_ayer_no_se_borra_sola_al_empezar_la_jornada(con, puntos):
    silencio.revisar(con, AHORA)                                    # nadie escribió: todos alertan
    h = silencio.revisar(con, AHORA + timedelta(days=1) - timedelta(hours=7))   # 07:00 del día siguiente
    assert not h["descartadas"] and len(_alertas(con)) == len(puntos)


def test_un_mensaje_real_descarta_la_alerta_viva(con, mesa):
    chat = ClienteSimulado(mesa)
    chat.escribir("somos 40 familias en san jose no hay arroz ni leche")
    chat.pulsar("Sí")
    punto = con.execute("SELECT punto_id FROM pedidos").fetchone()[0]
    con.execute("INSERT INTO pedidos(creado_en, punto_id, urgencia, estado, texto_original, origen) "
                "VALUES (?,?,2,'nuevo','Sin contacto hace 7 h. Visita de verificación.','silencio')",
                (db.ahora(), punto))
    con.commit()
    otro = ClienteSimulado(mesa, chat_id=2002)
    otro.escribir("somos 40 familias en san jose no hay arroz ni leche")
    fin, = otro.pulsar("Sí")
    assert not _alertas(con, punto) and len(_alertas(con, punto, "descartado")) == 1
    assert "Ya había un pedido reciente de ese punto (#1)" in fin.texto       # el duplicado es el real, no la alerta
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='alerta descartada'").fetchone()[0] == 1


def test_si_el_punto_escribe_la_revision_tambien_la_descarta(con, puntos):
    p = puntos[0]
    _pedido_real(con, p, 7)
    silencio.revisar(con, AHORA)
    _pedido_real(con, p, -1)                                        # escribió una hora después
    h = silencio.revisar(con, AHORA + timedelta(hours=1, minutes=5))
    assert p in h["descartadas"] and not _alertas(con, p)


def test_el_reloj_del_bot_revisa(con, mesa, monkeypatch):
    llamadas = []
    monkeypatch.setattr(silencio, "revisar", lambda c, *a, **k: llamadas.append(c) or
                        {"creadas": [], "actualizadas": [], "descartadas": [], "revisados": 0})
    asyncio.run(vigilar_silencio(mesa, cada_s=0, vueltas=3))
    assert llamadas == [con, con, con]


def test_la_migracion_corre_sobre_una_base_vieja(tmp_path):
    vieja = tmp_path / "vieja.db"
    esquema = (db.RAIZ / "esquema.sql").read_text(encoding="utf-8")
    # Una base creada con el esquema anterior: pedidos sin la columna origen.
    c = sqlite3.connect(vieja)
    c.executescript(esquema.replace(
        "  remitente_hash TEXT,                     -- hash del chat, nunca el id en claro\n"
        "  origen TEXT NOT NULL DEFAULT 'mensaje' CHECK(origen IN ('mensaje','silencio'))",
        "  remitente_hash TEXT"))
    assert "origen" not in {r[1] for r in c.execute("PRAGMA table_info(pedidos)")}
    c.execute("INSERT INTO pedidos(creado_en, estado, texto_original) VALUES ('2026-11-20T10:00:00-05:00','nuevo','viejo')")
    c.commit()
    c.close()

    con = db.conectar(vieja)
    assert "origen" in {r[1] for r in con.execute("PRAGMA table_info(pedidos)")}
    assert con.execute("SELECT origen FROM pedidos").fetchone()[0] == "mensaje"     # lo viejo era mensaje
    con.close()
    db.conectar(vieja).close()                                       # dos veces no rompe nada
    with pytest.raises(sqlite3.IntegrityError):
        c = db.conectar(vieja)
        c.execute("INSERT INTO pedidos(creado_en, origen) VALUES ('x','otra')")
