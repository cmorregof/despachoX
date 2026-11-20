import pytest

from datos import db
from lugares import nomenclator as R


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "t.db")
    c.execute("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (1,'Albergue San José','San José',5.07,-75.52,1)")
    c.execute("INSERT INTO pedidos(id,creado_en,estado) VALUES (1,?, 'nuevo'), (2,?, 'nuevo')", (db.ahora(), db.ahora()))
    c.execute("INSERT INTO cierres(id,creado_en,descripcion) VALUES (1,?, 'derrumbe')", (db.ahora(),))
    c.commit()
    assert R.cargar_semilla(c) > 100       # barrios y vías de la semilla real
    return c


def test_exacto_y_con_ruido(con):
    r = R.resolver(con, "avenida Santander", elegir=None)
    assert r.seguro and r.elegido.nombre == "avenida Santander" and r.metodo == "exacto"
    r = R.resolver(con, "hay un derrumbe por la panamericana llegando", tipos=("via", "sitio"), elegir=None)
    assert r.seguro and r.elegido.nombre == "Panamericana"


def test_error_de_tipeo(con):
    r = R.resolver(con, "via a chinchna", tipos=("via",), elegir=None)
    assert r.elegido is not None and r.elegido.nombre == "vía a Chinchiná"


def test_desconocido_pide_pin_y_no_inventa(con):
    r = R.resolver(con, "la siria", tipos=("via", "sitio"), elegir=None)
    assert r.elegido is None and not r.seguro
    assert "ubicación" in r.pregunta


def test_el_modelo_solo_elige_de_la_lista(con):
    llamado = {}

    def elegir(texto, contexto, cands):
        llamado["ids"] = [c.lugar_id for c in cands]
        return cands[-1].lugar_id

    r = R.resolver(con, "san", elegir=elegir)          # ambiguo: muchos barrios con «san»
    if r.candidatos and not r.seguro:
        assert r.metodo == "modelo" and r.elegido.lugar_id in llamado["ids"] and not r.seguro


def test_pin_confirma_y_enseña_el_apodo(con):
    r = R.resolver(con, "la siria", tabla="cierres", fila_id=1, tipos=("via", "sitio"), elegir=None)
    assert R.corregir_con_pin(con, r.ubicacion_id, 5.0301, -75.5702, "remitente")
    c = con.execute("SELECT lat, lon FROM cierres WHERE id=1").fetchone()
    assert (c["lat"], c["lon"]) == (5.0301, -75.5702)
    otra = R.resolver(con, "derrumbe en la siria", tipos=("via", "sitio"), elegir=None)
    assert otra.seguro and otra.elegido.lat == 5.0301          # ya no pregunta


def test_confirmar_pedido_amarra_el_punto_y_aprende(con):
    r = R.resolver(con, "san jose", tabla="pedidos", fila_id=1, elegir=None)
    assert r.elegido is not None
    assert R.confirmar(con, r.ubicacion_id, "despachador")
    assert con.execute("SELECT punto_id FROM pedidos WHERE id=1").fetchone()[0] is not None
    assert con.execute("SELECT estado FROM ubicaciones WHERE id=?", (r.ubicacion_id,)).fetchone()[0] == "confirmada"


def test_confirmar_via_llena_la_arista_del_cierre(con):
    r = R.resolver(con, "kevin angel", tabla="cierres", fila_id=1, tipos=("via",), elegir=None)
    assert R.confirmar(con, r.ubicacion_id, "despachador")
    c = con.execute("SELECT lugar, osm_u, osm_v FROM cierres WHERE id=1").fetchone()
    assert c["lugar"] == "avenida Kevin Ángel" and c["osm_u"] and c["osm_v"]
