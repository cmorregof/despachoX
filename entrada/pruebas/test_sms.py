"""Lector de SMS por reglas: veinte SMS sintéticos con errores y la conversación completa por SMS.

Ningún número de teléfono es real: el remitente de las pruebas es un texto como «sms-prueba-1».
`python -m pytest entrada/pruebas/test_sms.py -s` imprime cuántos se leen bien y deja el detalle en
`entrada/pruebas/reporte_sms.md`.
"""
from pathlib import Path

import pytest

from datos import db
from entrada import sms
from entrada.flujo import Mesa, SIN_LEER
from entrada.sms import LIMITE_SMS, leer_sms

T = ["camion", "campero", "moto"]

# (SMS, lo que debe salir). Pedido: lugar, familias, personas, bebes, productos, urgencia.
CASOS = [
    ("PEDIDO 40 SAN JOSE ARROZ LECHE", {"tipo": "pedido", "lugar": "san jose", "familias": 40, "productos": {"arroz", "leche"}, "urgencia": 2}),
    ("PEDIDO 6 BEBES LA ENEA LECHE URGENTE", {"tipo": "pedido", "lugar": "la enea", "bebes": 6, "productos": {"leche"}, "urgencia": 3}),
    ("CIERRE AV DEL CENTRO CAMION", {"tipo": "cierre", "lugar": "avenida del centro", "bloqueados": ["camion"]}),
    ("ENTREGADO DX7K2Q", {"tipo": "entregado", "codigo": "DX-7K2Q"}),
    ("pedido 25 familias villa hermosa agua y panela", {"tipo": "pedido", "lugar": "villa hermosa", "familias": 25, "productos": {"agua", "panela"}}),
    ("PEDDO 30 CHIPRE FRIJOL ACEITE", {"tipo": "pedido", "lugar": "chipre", "familias": 30, "productos": {"frijol", "aceite"}}),
    ("PEDIDOS 12 personas en fatima arroz", {"tipo": "pedido", "lugar": "fatima", "personas": 12, "productos": {"arroz"}}),
    ("ciere via a chinchina no pasan camiones", {"tipo": "cierre", "lugar": "via a chinchina", "bloqueados": ["camion"]}),
    ("CIERRE panamericana solo pasan motos", {"tipo": "cierre", "lugar": "panamericana", "bloqueados": ["camion", "campero"]}),
    ("entregado dx-4mq7", {"tipo": "entregado", "codigo": "DX-4MQ7"}),
    ("Buenas tardes, PEDIDO 15 flias barrio el carmen, lentejas, urjente",
     {"tipo": "pedido", "lugar": "el carmen", "familias": 15, "productos": {"lenteja"}, "urgencia": 3}),
    ("pedido arroz leche 20 san jorge", {"tipo": "pedido", "lugar": "san jorge", "familias": 20, "productos": {"arroz", "leche"}}),
    ("PEDIDO 50 BELEN 30 KILOS ARROZ", {"tipo": "pedido", "lugar": "belen", "familias": 50, "productos": {"arroz"}, "kg_arroz": 30}),
    ("pedido 10 la sultana pañales leche", {"tipo": "pedido", "lugar": "la sultana", "familias": 10, "productos": {"pañales", "leche"}}),
    ("derrumbe en la via al magdalena nadie pasa", {"tipo": "cierre", "lugar": "la via al magdalena", "bloqueados": T}),
    ("somos 8 abuelos en el albergue de la francia sin comida",
     {"tipo": "pedido", "lugar": "el albergue de la francia", "personas": 8, "urgencia": 3}),
    ("CIERE AVENIDA SANTANDER ARBOL", {"tipo": "cierre", "lugar": "avenida santander", "bloqueados": T}),
    ("ENTRGADO DX9PRT", {"tipo": "entregado", "codigo": "DX-9PRT"}),
    ("hola como estan", {"tipo": "fallo"}),
    ("PEDIDO 5 BEBES 3 NINOS VILLAMARIA FORMULA",
     {"tipo": "pedido", "lugar": "villamaria", "bebes": 5, "personas": 3, "productos": {"leche de fórmula"}, "urgencia": 3}),
]


def _comparar(x, e: dict) -> list[str]:
    """Campos que salieron mal. Vacía si el SMS se leyó bien."""
    mal = []
    tipo = "fallo" if x.fallo else "entregado" if x.entregado else x.tipo
    if tipo != e["tipo"]:
        return [f"tipo: {tipo} en vez de {e['tipo']}"]
    if tipo == "entregado" and x.entregado != e["codigo"]:
        mal.append(f"código: {x.entregado}")
    if tipo == "cierre":
        if x.cierre.lugar != e["lugar"]:
            mal.append(f"lugar: {x.cierre.lugar!r}")
        if x.cierre.tipos_bloqueados != e["bloqueados"]:
            mal.append(f"bloqueados: {x.cierre.tipos_bloqueados}")
    if tipo == "pedido":
        p = x.pedido
        for campo in ("lugar", "familias", "personas", "bebes"):
            if p.model_dump()[campo] != e.get(campo):
                mal.append(f"{campo}: {p.model_dump()[campo]!r}")
        if "productos" in e and {q.producto for q in p.productos} != e["productos"]:
            mal.append(f"productos: {[q.producto for q in p.productos]}")
        if p.urgencia != e.get("urgencia", 2):
            mal.append(f"urgencia: {p.urgencia}")
        if "kg_arroz" in e and next((q.kg for q in p.productos if q.producto == "arroz"), None) != e["kg_arroz"]:
            mal.append("kilos de arroz")
    return mal


@pytest.mark.parametrize("texto,esperado", CASOS, ids=[f"sms{i:02d}" for i in range(1, len(CASOS) + 1)])
def test_cada_sms(texto, esperado):
    assert _comparar(leer_sms(texto), esperado) == []


def test_reporte_de_lectura():
    filas, bien = [], 0
    for i, (texto, e) in enumerate(CASOS, 1):
        mal = _comparar(leer_sms(texto), e)
        bien += not mal
        filas.append(f"| {i} | `{texto}` | {'bien' if not mal else '; '.join(mal)} |")
    informe = (f"# Lector de SMS por reglas\n\n{bien} de {len(CASOS)} SMS leídos bien (todos los campos). "
               "Medido por nosotros sobre veinte SMS sintéticos escritos por el equipo, con errores de tipeo, "
               "orden variable y relleno. No son mensajes reales.\n\n"
               "**Salvedad.** Los veinte casos y las reglas los escribió la misma sesión, así que las reglas están "
               "ajustadas a estos casos: el resultado no es una medición independiente. Para tener una, otra persona "
               "del equipo escribe veinte SMS nuevos sin mirar `entrada/sms.py` y se corren con "
               "`python -m entrada.sms \"...\"`.\n\n"
               "| # | SMS | Resultado |\n|---|---|---|\n" + "\n".join(filas) + "\n")
    Path(__file__).with_name("reporte_sms.md").write_text(informe, encoding="utf-8")
    print(f"\nSMS leídos bien: {bien} de {len(CASOS)}")
    assert bien >= 18


def test_ningun_sms_lanza_excepcion():
    for raro in ["", "   ", "1234", "????", "pedido", "cierre", "entregado", "x" * 500, "PEDIDO 99999 ZZZ"]:
        leer_sms(raro)


# ---------- la conversación por SMS ----------

@pytest.fixture
def mesa_sms(con):
    return Mesa(con, extraer=leer_sms, elegir=None)


def test_pedido_por_sms_y_confirmacion_con_si(con, mesa_sms):
    r = sms.atender_sms(mesa_sms, "sms-prueba-1", "PEDIDO 40 SAN JOSE ARROZ LECHE")
    assert r.startswith("Recibido: pedido 40 fam arroz leche en San Jose") and "Responda SI" in r
    assert len(r) <= LIMITE_SMS and r.isascii()
    fin = sms.atender_sms(mesa_sms, "sms-prueba-1", "si")
    assert "San Jose" in fin and len(fin) <= LIMITE_SMS
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert p["punto_id"] is not None and p["familias"] == 40
    assert "sms-prueba-1" not in "\n".join(con.iterdump())          # el remitente queda como hash


def test_bebes_por_sms_pregunta_familias_y_acepta_el_numero(con, mesa_sms):
    sms.atender_sms(mesa_sms, "sms-prueba-2", "PEDIDO 6 BEBES LA ENEA LECHE URGENTE")
    r = sms.atender_sms(mesa_sms, "sms-prueba-2", "si")
    assert "Para cuantas familias? Responda con el numero." in r and len(r) <= LIMITE_SMS
    ok = sms.atender_sms(mesa_sms, "sms-prueba-2", "8")
    assert "8 familias" in ok
    assert con.execute("SELECT familias FROM pedidos").fetchone()[0] == 8


def test_cierre_por_sms(con, mesa_sms):
    r = sms.atender_sms(mesa_sms, "sms-prueba-3", "ciere via a chinchina no pasan camiones")
    assert "cierre, no pasa camion" in r and len(r) <= LIMITE_SMS
    c = con.execute("SELECT * FROM cierres").fetchone()
    assert c["tipos_bloqueados"] == '["camion"]' and c["estado"] == "reportado"


def test_entregado_por_sms_cierra_el_paquete(con, mesa_sms):
    con.execute("INSERT INTO pedidos(id, creado_en, estado) VALUES (77, ?, 'asignado')", (db.ahora(),))
    con.execute("INSERT INTO paquetes(codigo, pedido_id, kg, estado) VALUES ('DX-7K2Q', 77, 30, 'en_ruta')")
    con.commit()
    r = sms.atender_sms(mesa_sms, "sms-prueba-4", "entregado dx 7k2q")
    assert "DX-7K2Q quedo entregado" in r
    assert con.execute("SELECT estado FROM paquetes").fetchone()[0] == "entregado"
    assert con.execute("SELECT estado FROM pedidos WHERE id=77").fetchone()[0] == "entregado"
    quien = con.execute("SELECT quien FROM bitacora WHERE accion='entregar paquete'").fetchone()[0]
    assert quien.startswith("remitente ") and "sms-prueba-4" not in quien
    otra = sms.atender_sms(mesa_sms, "sms-prueba-4", "ENTREGADO DX-7K2Q")      # dos veces: no aplica
    assert "No encontre" in otra


def test_lo_que_no_se_entiende_se_guarda(con, mesa_sms):
    r = sms.atender_sms(mesa_sms, "sms-prueba-5", "hola como estan")
    assert len(r) <= LIMITE_SMS
    assert con.execute("SELECT texto_original FROM pedidos").fetchone()[0] == "hola como estan"
    assert r == sms.corto(SIN_LEER)


def test_sin_red_el_bot_lee_por_reglas_sin_llamar_al_modelo(con, monkeypatch):
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")

    def no_llamar(texto):
        raise AssertionError("con DESPACHOX_SIN_RED=1 no se llama al modelo")
    x = Mesa(con, extraer=no_llamar, elegir=None).leer("PEDIDO 40 SAN JOSE ARROZ LECHE")
    assert x.pedido.familias == 40 and not x.fallo


def test_respuestas_siempre_caben_en_un_sms():
    largo = "Entendí: " + "muchísimas cosas " * 30
    assert len(sms.corto(largo)) <= LIMITE_SMS and sms.corto("José, Fátima").isascii()
