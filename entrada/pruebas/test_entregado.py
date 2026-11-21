"""ENTREGADO solo desde el destino o el conductor asignado. Remitentes sintéticos, sin red."""
import pytest

from datos import db
from entrada import guardar
from entrada.flujo import SEPARADOR, Mesa
from entrada.privacidad import hash_remitente
from entrada.pruebas.simulador import ClienteSimulado

PUNTO = 1


@pytest.fixture
def paquete(con):
    """Un pedido de «comite-a» en el punto 1, con su paquete en ruta en el camión del plan aprobado."""
    con.execute("INSERT INTO vehiculos(id, nombre, tipo, capacidad_kg) VALUES (1, 'Camión 1', 'camion', 3000)")
    con.execute("INSERT INTO pedidos(id, creado_en, punto_id, estado, remitente_hash) VALUES (50, ?, ?, 'asignado', ?)",
                (db.ahora(), PUNTO, hash_remitente("comite-a")))
    con.execute("INSERT INTO planes(id, creado_en, estado) VALUES (1, ?, 'aprobado')", (db.ahora(),))
    con.execute("INSERT INTO paradas(plan_id, vehiculo_id, orden, punto_id, pedido_id) VALUES (1, 1, 1, ?, 50)", (PUNTO,))
    con.execute("INSERT INTO paquetes(codigo, pedido_id, kg, estado) VALUES ('DX-7K2Q', 50, 30, 'en_ruta')")
    con.commit()
    return "DX-7K2Q"


def _escribir(mesa, remitente, texto):
    r, = ClienteSimulado(mesa, chat_id=remitente).escribir(texto)
    return r.texto


@pytest.fixture
def mesa_reglas(con):
    from entrada.sms import leer_sms
    return Mesa(con, extraer=leer_sms, elegir=None)


def _estado(con):
    return con.execute("SELECT estado FROM paquetes WHERE codigo='DX-7K2Q'").fetchone()[0]


def test_quien_pidio_confirma(con, mesa_reglas, paquete):
    assert "quedó entregado" in _escribir(mesa_reglas, "comite-a", "ENTREGADO DX7K2Q")
    assert _estado(con) == "entregado"
    quien = con.execute("SELECT quien FROM bitacora WHERE accion='entregar paquete'").fetchone()[0]
    assert quien.endswith("(destino)") and "comite-a" not in quien


def test_un_extrano_no_puede_y_recibe_lo_mismo_que_con_un_codigo_inexistente(con, mesa_reglas, paquete):
    r = _escribir(mesa_reglas, "extrano", "ENTREGADO DX7K2Q")
    inexistente = _escribir(mesa_reglas, "extrano", "ENTREGADO DX9999")
    assert "No pude confirmar el paquete DX-7K2Q" in r
    r = r.split("\n\n" + SEPARADOR)[0]           # el primer mensaje de un remitente nuevo trae el aviso de datos
    assert r.replace("DX-7K2Q", "X") == inexistente.replace("DX-9999", "X")     # no delata si el código existe
    assert _estado(con) == "en_ruta"
    rechazos = con.execute("SELECT detalle FROM bitacora WHERE accion='entrega rechazada'").fetchall()
    assert len(rechazos) == 2 and "extrano" not in str([dict(x) for x in rechazos])


def test_otro_miembro_del_comite_del_mismo_punto_puede(con, mesa_reglas, paquete):
    con.execute("INSERT INTO pedidos(creado_en, punto_id, estado, remitente_hash, origen) VALUES (?,?, 'nuevo', ?, 'mensaje')",
                (db.ahora(), PUNTO, hash_remitente("comite-b")))
    con.commit()
    assert "quedó entregado" in _escribir(mesa_reglas, "comite-b", "ENTREGADO DX7K2Q")


def test_una_alerta_por_silencio_no_da_permiso(con, mesa_reglas, paquete):
    con.execute("INSERT INTO pedidos(creado_en, punto_id, estado, remitente_hash, origen) VALUES (?,?, 'nuevo', ?, 'silencio')",
                (db.ahora(), PUNTO, hash_remitente("alguien")))
    con.commit()
    assert "No pude confirmar" in _escribir(mesa_reglas, "alguien", "ENTREGADO DX7K2Q")


def test_el_conductor_asignado_puede_si_existe_la_columna(con, mesa_reglas, paquete):
    assert guardar.quien_confirma(con, paquete, hash_remitente("conductor-1")) is None      # hoy no existe
    con.execute("ALTER TABLE vehiculos ADD COLUMN conductor_hash TEXT")
    con.execute("UPDATE vehiculos SET conductor_hash=? WHERE id=1", (hash_remitente("conductor-1"),))
    con.commit()
    assert guardar.quien_confirma(con, paquete, hash_remitente("conductor-2")) is None
    assert "quedó entregado" in _escribir(mesa_reglas, "conductor-1", "ENTREGADO DX7K2Q")
    quien = con.execute("SELECT quien FROM bitacora WHERE accion='entregar paquete'").fetchone()[0]
    assert quien.endswith("(conductor)")


def test_confirmar_dos_veces_no_aplica(con, mesa_reglas, paquete):
    _escribir(mesa_reglas, "comite-a", "ENTREGADO DX7K2Q")
    assert "No pude confirmar" in _escribir(mesa_reglas, "comite-a", "ENTREGADO DX7K2Q")
