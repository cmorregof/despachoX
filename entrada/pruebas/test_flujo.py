"""El flujo completo con el Telegram simulado y el extractor falso, sobre una base temporal."""
import json

import pytest

from entrada import extraer as E, raciones
from entrada.flujo import Mesa
from entrada.privacidad import hash_remitente
from entrada.pruebas.conftest import extractor_falso
from entrada.pruebas.mensajes import MENSAJES
from entrada.pruebas.simulador import ClienteSimulado

TEXTO = {m["id"]: m["texto"] for m in MENSAJES}
ARROZ, LECHE = raciones.KG_POR_FAMILIA["arroz"], raciones.KG_POR_FAMILIA["leche"]


@pytest.fixture
def chat(mesa):
    return ClienteSimulado(mesa)


def una(con, sql, *args):
    return con.execute(sql, args).fetchone()


def test_los_quince_mensajes_dejan_la_fila_esperada(con, mesa):
    for m in MENSAJES:
        antes = (una(con, "SELECT COUNT(*) FROM pedidos")[0], una(con, "SELECT COUNT(*) FROM cierres")[0])
        enviados = ClienteSimulado(mesa, chat_id=5000 + m["id"]).escribir(m["texto"])
        e = m["esperado"]
        despues = (una(con, "SELECT COUNT(*) FROM pedidos")[0], una(con, "SELECT COUNT(*) FROM cierres")[0])
        assert despues == (antes[0] + bool(e.get("pedido")), antes[1] + bool(e.get("cierre"))), m["id"]
        assert len(enviados) == max(1, bool(e.get("pedido")) + bool(e.get("cierre"))), m["id"]
    assert una(con, "SELECT COUNT(*) FROM pedidos WHERE punto_id IS NOT NULL")[0] == 0     # nada sin confirmar
    assert una(con, "SELECT COUNT(*) FROM cierres WHERE lat IS NOT NULL")[0] == 0
    assert una(con, "SELECT COUNT(*) FROM pedidos WHERE estado<>'nuevo'")[0] == 0
    assert una(con, "SELECT COUNT(*) FROM cierres WHERE estado<>'reportado'")[0] == 0


def test_pedido_del_encargo_de_punta_a_punta(con, chat):
    r, = chat.escribir(TEXTO[1])
    assert "40 familias en san jose" in r.texto and f"arroz ({ARROZ * 40:g} kg aprox.) y leche ({LECHE * 40:g} kg aprox.)" in r.texto and "despachador" in r.texto
    assert "San José" in r.texto and r.botones[0][0] == "Sí, es ahí" and r.botones[-1][0] == "Enviar mi ubicación"
    assert any(t.startswith("San Jorge") for t, _ in r.botones)            # una alternativa por candidato
    p = una(con, "SELECT * FROM pedidos")
    assert (p["estado"], p["familias"], p["punto_id"], p["urgencia"]) == ("nuevo", 40, None, 2)
    assert json.loads(p["productos"]) == [
        {"producto": "arroz", "kg": round(ARROZ * 40, 1), "supuesto": f"{ARROZ:g} kg por familia"},
        {"producto": "leche", "kg": round(LECHE * 40, 1), "supuesto": f"{LECHE:g} kg por familia"}]
    assert p["remitente_hash"] == hash_remitente(1001) and "1001" not in p["remitente_hash"]
    u = una(con, "SELECT * FROM ubicaciones")
    assert (u["tabla"], u["fila_id"], u["estado"]) == ("pedidos", p["id"], "propuesta")

    fin, = chat.pulsar("Sí")
    assert "San José" in fin.texto and r.botones_quitados
    p = una(con, "SELECT * FROM pedidos")
    punto = una(con, "SELECT * FROM puntos WHERE id=?", p["punto_id"])
    assert punto["barrio"] == "San José"
    assert una(con, "SELECT estado, confirmado_por FROM ubicaciones")[:] == ("confirmada", "remitente")
    assert "resuelto" in chat.pulsar("Sí", de=r)[0].texto                   # pulsar dos veces no rompe nada


def test_elegir_una_alternativa(con, chat):
    r, = chat.escribir(TEXTO[1])
    chat.pulsar("San Jorge")
    p = una(con, "SELECT punto_id FROM pedidos")
    assert una(con, "SELECT barrio FROM puntos WHERE id=?", p["punto_id"])["barrio"] == "San Jorge"


def test_cierre_confirmado_lleva_coordenadas_y_arista(con, chat):
    r, = chat.escribir(TEXTO[8])
    assert "vía cerrada en via a chinchina" in r.texto and "no pasa camión" in r.texto
    c = una(con, "SELECT * FROM cierres")
    assert (c["estado"], c["lat"], json.loads(c["tipos_bloqueados"])) == ("reportado", None, ["camion"])
    chat.pulsar("Sí")
    c = una(con, "SELECT * FROM cierres")
    assert c["lugar"] == "vía a Chinchiná" and c["lat"] and c["osm_u"] and c["estado"] == "reportado"


DESCONOCIDO = "derrumbe por la quebrada el zancudo no hay paso"       # sitio inventado: no está en el nomenclátor
LEE_DESCONOCIDO = {DESCONOCIDO: {"tipo": "cierre", "cierre": {
    "lugar": "quebrada el zancudo", "descripcion": "derrumbe", "tipos_bloqueados": ["camion", "campero", "moto"]}}}


def test_lugar_desconocido_se_fija_con_la_ubicacion_del_chat(con, mesa):
    mesa.extraer = extractor_falso(LEE_DESCONOCIDO)
    chat = ClienteSimulado(mesa)
    r, = chat.escribir(DESCONOCIDO)
    assert "No conozco «quebrada el zancudo»" in r.texto and [t for t, _ in r.botones] == ["Enviar mi ubicación"]
    ayuda, = chat.pulsar("Enviar mi ubicación")
    assert ayuda.pide_ubicacion
    fin, = chat.enviar_ubicacion(5.0101, -75.5802)
    assert "cierre quedó ubicado" in fin.texto
    c = una(con, "SELECT lat, lon, osm_u FROM cierres")
    assert (round(c["lat"], 4), round(c["lon"], 4), c["osm_u"]) == (5.0101, -75.5802, None)
    assert una(con, "SELECT metodo, estado FROM ubicaciones")[:] == ("pin", "confirmada")
    # H6: lo aprendido con el pin de otra persona no se le ofrece a la siguiente...
    otro = ClienteSimulado(chat.m.mesa, chat_id=2002)
    r2, = otro.escribir(DESCONOCIDO)
    assert "Sí, es ahí" not in [t for t, _ in r2.botones] and "No conozco «quebrada el zancudo»" in r2.texto
    # ...hasta que el despachador lo valida (en el tablero, confirmar o mover el pin deja su nombre)
    con.execute("UPDATE ubicaciones SET confirmado_por='despachador' WHERE metodo='pin'")
    tercero = ClienteSimulado(chat.m.mesa, chat_id=2003)
    r3, = tercero.escribir(DESCONOCIDO)
    assert r3.botones[0][0] == "Sí, es ahí"


def test_respuesta_en_texto_libre_vuelve_a_resolver(con, mesa):
    mesa.extraer = extractor_falso({"somos 10 familias en el prado falta arroz": {
        "tipo": "pedido", "pedido": {"lugar": "el prado", "familias": 10, "personas": None, "bebes": None, "urgencia": 2, "horas_limite": None,
                                     "productos": [{"producto": "arroz", "kg": None}]}}})
    chat = ClienteSimulado(mesa)
    r, = chat.escribir("somos 10 familias en el prado falta arroz")
    assert "El Prado" in r.texto
    r2, = chat.escribir("no, es en bajo prado")
    # el resolvedor ve dos barrios «Prado» casi empatados y, sin modelo, ofrece las opciones
    assert "Bajo Prado" in r2.texto and [t for t, _ in r2.botones][:2] == ["Bajo Prado (barrio)", "El Prado (barrio)"]
    assert una(con, "SELECT COUNT(*) FROM pedidos")[0] == 1                 # no creó otro pedido
    estados = [f["estado"] for f in con.execute("SELECT estado FROM ubicaciones ORDER BY id")]
    assert estados == ["rechazada", "propuesta"]
    assert "¿Cuál es?" in chat.escribir("si")[0].texto                      # no hay una sola propuesta que aceptar
    r3, = chat.escribir("no, es más abajo, por la finca de don chucho")              # no está en el nomenclátor
    assert "No conozco" in r3.texto and [t for t, _ in r3.botones] == ["Enviar mi ubicación"]
    assert "sin lugar confirmado" in chat.escribir("gracias")[0].texto
    r4, = chat.escribir("queda en chipre")
    assert r4.botones[0][0] == "Sí, es ahí"
    fin, = chat.escribir("sí")                                              # «sí» escrito vale como el botón
    assert "Chipre" in fin.texto
    assert una(con, "SELECT punto_id FROM pedidos")["punto_id"] is not None
    assert una(con, "SELECT COUNT(*) FROM ubicaciones WHERE estado='propuesta'")[0] == 0
    assert "No alcancé a entender" in chat.escribir("gracias")[0].texto                # ya no hay nada pendiente


def test_pedido_sin_lugar_pregunta_y_acepta_texto_o_pin(con, mesa):
    a = ClienteSimulado(mesa, 1)
    r, = a.escribir(TEXTO[7])
    assert "15 familias" in r.texto and "No me dijiste dónde" in r.texto and "Me falta saber" in r.texto
    assert una(con, "SELECT COUNT(*) FROM ubicaciones")[0] == 0
    r2, = a.escribir("en chipre")
    assert "Chipre" in r2.texto
    a.pulsar("Sí")
    assert una(con, "SELECT punto_id FROM pedidos WHERE remitente_hash=?", hash_remitente(1))[0] is not None

    b = ClienteSimulado(mesa, 2)
    b.escribir(TEXTO[7])
    fin, = b.enviar_ubicacion(5.0626, -75.5181)
    assert "la ubicación que enviaste" in fin.texto
    p = una(con, "SELECT punto_id FROM pedidos WHERE remitente_hash=?", hash_remitente(2))
    assert round(una(con, "SELECT lat FROM puntos WHERE id=?", p["punto_id"])["lat"], 4) == 5.0626
    # el pin de una persona no se vuelve respuesta para otro mensaje sin lugar
    c = ClienteSimulado(mesa, 3)
    assert "No me dijiste dónde" in c.escribir(TEXTO[7])[0].texto


def test_mensaje_mixto_guarda_pedido_y_cierre_y_confirma_cada_uno(con, chat):
    pedido, cierre = chat.escribir(TEXTO[13])
    assert "35 familias" in pedido.texto and "vía cerrada" in cierre.texto
    fin, = chat.pulsar("Sí", de=cierre)
    assert "Falta ubicar tu otro reporte" in fin.texto
    assert una(con, "SELECT lugar FROM cierres")["lugar"] == "avenida Paralela"
    assert una(con, "SELECT punto_id FROM pedidos")["punto_id"] is None
    chat.pulsar("Sí", de=pedido)
    assert una(con, "SELECT punto_id FROM pedidos")["punto_id"] is not None


def test_lo_que_no_es_nada_no_guarda_fila(con, chat):
    r, = chat.escribir(TEXTO[14])
    assert "No alcancé a entender" in r.texto
    assert una(con, "SELECT COUNT(*) FROM pedidos")[0] + una(con, "SELECT COUNT(*) FROM cierres")[0] == 0


def test_sin_modelo_el_bot_lee_por_reglas_y_no_guarda_datos_personales(con):
    chat = ClienteSimulado(Mesa(con, extraer=E.crudo, elegir=None))
    r, = chat.escribir(TEXTO[15])
    assert "20 familias en fatima" in r.texto and "reglas" not in r.texto
    p = una(con, "SELECT * FROM pedidos")
    assert (p["estado"], p["punto_id"], p["familias"]) == ("nuevo", None, 20)
    assert "Pedro" not in p["texto_original"] and "3105551234" not in p["texto_original"]


def test_sin_modelo_lo_que_no_se_entiende_se_guarda_crudo(con):
    chat = ClienteSimulado(Mesa(con, extraer=E.crudo, elegir=None))
    r, = chat.escribir("hola buenas como hago para ser voluntario")
    assert "un despachador lo revisará" in r.texto
    p = una(con, "SELECT * FROM pedidos")
    assert p["estado"] == "nuevo" and p["familias"] is None and "voluntario" in p["texto_original"]


def test_no_se_guardan_nombre_telefono_ni_chat(con, chat):
    chat.escribir(TEXTO[15])
    chat.pulsar("Sí")
    volcado = "\n".join(con.iterdump())
    for prohibido in ("Pedro", "Gomez", "3105551234", "1001"):
        assert prohibido not in volcado


def test_duplicado_del_mismo_punto_en_dos_horas(con, mesa):
    a, b = ClienteSimulado(mesa, 1), ClienteSimulado(mesa, 2)
    a.escribir(TEXTO[1]); a.pulsar("Sí")
    b.escribir(TEXTO[1])
    fin, = b.pulsar("Sí")
    assert "Ya había un pedido reciente" in fin.texto
    primero, segundo = con.execute("SELECT id, duplicado_de FROM pedidos ORDER BY id").fetchall()
    assert primero["duplicado_de"] is None and segundo["duplicado_de"] == primero["id"]
    con.execute("UPDATE pedidos SET creado_en='2026-01-01T00:00:00-05:00'")     # fuera de la ventana
    c = ClienteSimulado(mesa, 3)
    c.escribir(TEXTO[1]); c.pulsar("Sí")
    assert con.execute("SELECT duplicado_de FROM pedidos ORDER BY id DESC").fetchone()[0] is None


def test_kilos_y_plazo(con, chat):
    chat.escribir(TEXTO[4])
    assert una(con, "SELECT kg_estimado FROM pedidos")[0] == 70
    ClienteSimulado(chat.m.mesa, 9).escribir(TEXTO[6])
    p = con.execute("SELECT * FROM pedidos ORDER BY id DESC").fetchone()
    assert p["kg_estimado"] == round(80 * (LECHE + raciones.KG_POR_FAMILIA["huevos"]), 1) and p["limite_en"] > p["creado_en"]


def test_estado_ayuda_y_mensajes_que_no_son_texto(con, chat):
    assert "No tengo pedidos" in chat.comando("estado")[0].texto
    chat.escribir(TEXTO[1]); chat.pulsar("Sí")
    e, = chat.comando("estado")
    assert "recibido. Una persona de la mesa lo está revisando" in e.texto and "San José" in e.texto
    assert "<code>Somos 40 familias en San José" in chat.comando("inicio")[1].texto
    assert "No alcancé a entender" in chat.enviar_foto()[0].texto
    assert "No tengo un reporte tuyo pendiente" in chat.enviar_ubicacion(5.0, -75.5)[0].texto


def test_botones_viejos_o_ajenos_no_rompen(con, mesa):
    assert "No alcancé a entender" in mesa.pulsar(1, "zzz").texto
    assert "No encontré" in mesa.pulsar(1, "s:999").texto
    ClienteSimulado(mesa, 1).escribir(TEXTO[1])
    assert "ya no está disponible" in mesa.pulsar(1, "c:1:99999").texto
