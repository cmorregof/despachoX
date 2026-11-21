"""H6 (evaluacion/inyeccion/HALLAZGOS.md), plan A: el lugar que una persona describió con sus palabras
y fijó con su ubicación no se le ofrece a otra hasta que el despachador lo valide. Datos sintéticos."""
from entrada.flujo import AVISO_DATOS, SEPARADOR, Mesa, lugares_ajenos
from entrada.pruebas.conftest import extractor_falso
from entrada.pruebas.mensajes import _p
from entrada.pruebas.simulador import ClienteSimulado
from entrada.sms import atender_sms

VICTIMA = "Necesitamos agua, estamos en la casa de doña Ficticia Prueba frente a la tienda El Ensayo"
EXTRANO = "Necesitamos agua frente a la tienda El Ensayo"
LECTURAS = {VICTIMA: {"tipo": "pedido", "pedido": _p("casa de doña Ficticia Prueba frente a la tienda El Ensayo",
                                                      3, ["agua"])},
            EXTRANO: {"tipo": "pedido", "pedido": _p("frente a la tienda El Ensayo", 2, ["agua"])}}
PIN = (5.06000, -75.50000)


def _mesa(con):
    return Mesa(con, extraer=extractor_falso(LECTURAS), elegir=None)


def _victima_fija_su_casa(mesa):
    v = ClienteSimulado(mesa, chat_id=700002)
    v.escribir(VICTIMA)
    v.enviar_ubicacion(*PIN)
    return v


def _ofrecido(respuestas) -> str:
    return " ".join(r.texto + " " + " ".join(t for t, _ in r.botones) for r in respuestas).lower()


def test_el_texto_de_la_victima_no_se_le_ofrece_a_un_extrano(con):
    mesa = _mesa(con)
    _victima_fija_su_casa(mesa)
    aprendido = con.execute("SELECT id FROM lugares WHERE origen='aprendido' AND nombre LIKE '%Ficticia%'").fetchone()
    assert aprendido is not None, "la prueba necesita el lugar aprendido que crea el pin"
    r = ClienteSimulado(mesa, chat_id=900408).escribir(EXTRANO)
    assert "ficticia" not in _ofrecido(r)
    assert not any(d.startswith("s:") for x in r for _, d in x.botones)    # nada que confirmar con un «sí»


def test_tampoco_el_punto_que_nace_del_pin_tras_reiniciar(con):
    """Al reiniciar, la semilla vuelve «Punto de entrega <texto>» un lugar tipo punto. Hereda el dueño."""
    _victima_fija_su_casa(_mesa(con))
    mesa = _mesa(con)                                 # Mesa nueva: vuelve a cargar la semilla
    punto = con.execute("SELECT id FROM lugares WHERE tipo='punto' AND nombre LIKE '%Ficticia%'").fetchone()
    assert punto is not None
    r = ClienteSimulado(mesa, chat_id=900408).escribir(EXTRANO)
    assert "ficticia" not in _ofrecido(r)
    assert lugares_ajenos(con, "otro-hash", [punto["id"]]) == {punto["id"]}


def test_ni_por_sms(con, monkeypatch):
    mesa = _mesa(con)
    _victima_fija_su_casa(mesa)
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")      # el SMS lo lee el lector por reglas, no el extractor falso
    respuesta = atender_sms(mesa, "sms-extrano", "PEDIDO AGUA FRENTE A LA TIENDA EL ENSAYO").lower()
    assert "recibido" in respuesta and "ficticia" not in respuesta, respuesta


def test_un_boton_forjado_con_el_lugar_ajeno_no_ubica_el_pedido(con):
    mesa = _mesa(con)
    _victima_fija_su_casa(mesa)
    ajeno = con.execute("SELECT id FROM lugares WHERE origen='aprendido' AND nombre LIKE '%Ficticia%'").fetchone()["id"]
    ClienteSimulado(mesa, chat_id=900408).escribir(EXTRANO)
    u = con.execute("SELECT id, candidatos FROM ubicaciones ORDER BY id DESC LIMIT 1").fetchone()
    assert str(ajeno) in u["candidatos"]              # el despachador sí ve la lista completa
    r = mesa.pulsar(900408, f"c:{u['id']}:{ajeno}")
    assert "ya no está disponible" in r.texto
    assert con.execute("SELECT estado FROM ubicaciones WHERE id=?", (u["id"],)).fetchone()[0] == "propuesta"


def test_quien_lo_fijo_y_el_despachador_si_lo_ven(con):
    mesa = _mesa(con)
    v = _victima_fija_su_casa(mesa)
    r = v.escribir(VICTIMA)                           # la misma persona vuelve a pedir
    assert "ficticia" in _ofrecido(r)
    con.execute("UPDATE ubicaciones SET confirmado_por='despachador' WHERE metodo='pin'")   # validado
    r = ClienteSimulado(mesa, chat_id=900409).escribir(EXTRANO)
    assert "ficticia" in _ofrecido(r)


def test_la_semilla_se_sigue_ofreciendo_a_todos(con):
    mesa = _mesa(con)
    _victima_fija_su_casa(mesa)
    semilla = [r["id"] for r in con.execute("SELECT id FROM lugares WHERE origen!='aprendido' LIMIT 500")]
    assert lugares_ajenos(con, "cualquiera", semilla) == set()


# ---------- aviso de tratamiento de datos ----------

def test_el_start_termina_con_el_aviso_y_no_dice_que_no_guarda_el_nombre(mesa):
    bienvenida, _ = ClienteSimulado(mesa).comando("inicio")
    assert bienvenida.texto.endswith(f"{SEPARADOR}\n{AVISO_DATOS}")
    assert "no guardo" not in bienvenida.texto.lower()
    assert "/borrar" in AVISO_DATOS and "1581" in AVISO_DATOS


def test_el_aviso_va_solo_en_la_primera_respuesta_de_un_remitente_nuevo(mesa):
    chat = ClienteSimulado(mesa, chat_id=4242)
    primera = chat.escribir("somos 40 familias en san jose no hay arroz ni leche")
    assert primera[-1].texto.endswith(AVISO_DATOS)
    segunda = chat.escribir("somos 40 familias en san jose no hay arroz ni leche")
    assert not any(AVISO_DATOS in r.texto for r in segunda)


def test_quien_ya_vio_el_start_no_lo_recibe_otra_vez(mesa):
    chat = ClienteSimulado(mesa, chat_id=4343)
    chat.comando("inicio")
    r = chat.escribir("somos 40 familias en san jose no hay arroz ni leche")
    assert not any(AVISO_DATOS in x.texto for x in r)


def test_el_sms_no_lleva_el_aviso_porque_no_cabe(mesa):
    respuesta = atender_sms(mesa, "sms-nuevo", "PEDIDO 40 SAN JOSE ARROZ")
    assert "CONVITE" not in respuesta and len(respuesta) <= 160
