import json

import pytest

from triage import agentes, debiles
from triage.entrada_datos import a_iso
from triage.tests.conftest import desplazar, h


def _stub(con, sid, desde, params, ahora):
    """Sustituto de los pasos 7 a 10 del embudo (la integración real se prueba en test_embudo)."""
    con.execute("UPDATE solicitudes SET estado='confirmada_regla' WHERE id=?", (sid,))


@pytest.fixture
def tarea(con, params, zonas_sinteticas, hora):
    zona = zonas_sinteticas[0]
    con.execute("UPDATE zonas SET es_debil=1 WHERE id=?", (zona.id,))
    tid = debiles.crear_tarea(con, zona, hora(), "zona_silenciosa", params)
    con.commit()
    return tid, zona


def test_enrolar_exige_humano(con):
    with pytest.raises(PermissionError):
        agentes.enrolar(con, h("a"), "Cruz Roja", [1], "regla:v1")


def test_no_agente(con, params, tarea, hora):
    tid, zona = tarea
    r = agentes.validar(con, h("ciudadano"), tid, zona.lat, zona.lon, [{"familias": 3}], hora(1),
                        params, procesar=_stub)
    assert r["ok"] is False and r["motivo"] == "no_es_agente"
    agentes.registrar_lider(con, h("lider"), [zona.id], "coordinador:ana")
    r = agentes.validar(con, h("lider"), tid, zona.lat, zona.lon, [], hora(1), params, procesar=_stub)
    assert r["motivo"] == "no_es_agente"


def test_fuera_de_zona(con, params, tarea, hora):
    tid, zona = tarea
    agentes.enrolar(con, h("agente"), "Defensa Civil", [zona.id], "coordinador:ana")
    lejos = desplazar(zona.lat, zona.lon, norte_m=2000)
    r = agentes.validar(con, h("agente"), tid, lejos[0], lejos[1], [{"familias": 3}], hora(1),
                        params, procesar=_stub)
    assert r == {"ok": False, "motivo": "ubicacion_agente", "solicitudes": [], "consolidadas": [],
                 "en_cola": [], "auditoria": False}
    r = agentes.validar(con, h("agente"), tid, None, None, [], hora(1), params, procesar=_stub)
    assert r["motivo"] == "ubicacion_agente"


def test_validacion_correcta(con, params, tarea, hora):
    tid, zona = tarea
    # Dos solicitudes por chat esperando al agente: una cubierta (arroz, agua) y otra no.
    for i, prods in enumerate((["arroz", "agua"], ["panales"])):
        con.execute("INSERT INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, zona_id, "
                    "productos, estado, tarea_id) VALUES (?,?,?,?,?,'espera_agente',?)",
                    (a_iso(hora(0.5)), f"e{i}", h(f"c{i}"), zona.id, json.dumps(prods), tid))
    agentes.enrolar(con, h("agente"), "Defensa Civil", [zona.id], "coordinador:ana")
    cerca = desplazar(zona.lat, zona.lon, norte_m=300)
    r = agentes.validar(con, h("agente"), tid, cerca[0], cerca[1],
                        [{"familias": 12, "productos": ["arroz", "agua", "aceite"]}], hora(1),
                        params, procesar=_stub)
    assert r["ok"] and len(r["solicitudes"]) == 1
    nueva = con.execute("SELECT * FROM solicitudes WHERE id=?", (r["solicitudes"][0],)).fetchone()
    assert nueva["canal"] == "agente" and "validada_agente" in json.loads(nueva["marcas"])
    assert nueva["zona_id"] == zona.id and nueva["familias_declaradas"] == 12
    assert len(r["consolidadas"]) == 1 and len(r["en_cola"]) == 1
    estados = dict(con.execute("SELECT hash_mensaje, estado FROM solicitudes WHERE hash_mensaje "
                               "IN ('e0','e1')").fetchall())
    assert estados == {"e0": "consolidada", "e1": "en_cola"}
    assert con.execute("SELECT estado FROM tareas_campo WHERE id=?", (tid,)).fetchone()[0] == "validada"
    # Una tarea validada no se vuelve a validar.
    r2 = agentes.validar(con, h("agente"), tid, cerca[0], cerca[1], [{}], hora(2), params,
                         procesar=_stub)
    assert r2["motivo"] == "tarea_invalida"


def test_auditoria_de_agente_cerca_del_10_por_ciento(params):
    import random
    marcadas = sum(random.Random(f"{params['semilla']}:{h('ag')}:{t}").random()
                   < params["auditoria_agente"] for t in range(2000))
    assert 0.07 < marcadas / 2000 < 0.13
