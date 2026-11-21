import json
from datetime import timedelta

import pytest

from triage import agentes, antifraude, censo, debiles, embudo, puntaje
from triage.entrada_datos import a_iso
from triage.tests.conftest import desplazar, h


def sol(t, rem, zona=None, texto=None, familias=5, productos=("arroz",),
        lugar=True, norte_m=0.0, **extra):
    texto = f"solicitud {rem} {rem} {rem}" if texto is None else texto
    d = {"recibida_en": a_iso(t), "remitente_hash": h(rem), "texto": texto, "familias": familias,
         "productos": list(productos), "lugar_confirmado": lugar}
    if zona is not None:
        d["lat"], d["lon"] = desplazar(zona.lat, zona.lon, norte_m=norte_m)
    d.update(extra)
    return d


def estados(con):
    return {r["id"]: r["estado"] for r in con.execute("SELECT id, estado FROM solicitudes")}


def fila(con, sid):
    f = dict(con.execute("SELECT * FROM solicitudes WHERE id=?", (sid,)).fetchone())
    f["marcas"] = set(json.loads(f["marcas"]))
    return f


@pytest.fixture
def z(zonas_sinteticas):
    return {x.nombre: x for x in zonas_sinteticas}


def test_confirmada_por_regla_y_bitacora(con, params, z, hora):
    r = embudo.procesar_lote(con, [sol(hora(), "a", z["Barrio A"])], params, hora())
    assert r["por_estado"] == {"confirmada_regla": 1}
    f = fila(con, 1)
    assert f["familias_efectivas"] == 5 and f["zona_id"] == z["Barrio A"].id
    senales = json.loads(f["senales"])
    assert set(senales) == {"base", "lugar_confirmado", "dentro_de_tope"}
    assert f["p_real"] == pytest.approx(puntaje.p_real(["lugar_confirmado", "dentro_de_tope"], params)[0])
    b = con.execute("SELECT * FROM bitacora WHERE accion='confirmar_solicitud'").fetchone()
    assert b["quien"] == "regla:v1" and json.loads(b["detalle"])["id"] == 1


def test_integrar_false_no_toca_pedidos(con, params, z, hora):
    antes = con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    filas = [sol(hora(minutos=i * 30), f"r{i}", z["Barrio B"], productos=(f"p{i}",)) for i in range(6)]
    r = embudo.procesar_lote(con, filas, params, hora(3))
    assert r["por_estado"].get("confirmada_regla", 0) >= 4
    assert con.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0] == antes


def test_integrar_true_crea_pedido_confirmado(con, params, z, hora):
    embudo.procesar_lote(con, [sol(hora(), "a", z["Barrio A"], texto="llamar al 300 123 45 67")],
                         params, hora(), integrar=True)
    p = con.execute("SELECT * FROM pedidos").fetchone()
    assert p["estado"] == "confirmado" and p["familias"] == 5
    assert "123 45" not in p["texto_original"]
    assert fila(con, 1)["pedido_id"] == p["id"]


def test_en_cola_por_bloqueantes(con, params, z, hora):
    filas = [sol(hora(), "sinfam", z["Barrio A"], familias=None),
             sol(hora(), "sinlugar", None, lat=0, lon=0),
             sol(hora(), "absurdo", z["Barrio C"], familias=100000)]
    embudo.procesar_lote(con, filas, params, hora())
    f1, f2, f3 = fila(con, 1), fila(con, 2), fila(con, 3)
    assert f1["estado"] == "en_cola" and "familias_supuestas" in f1["marcas"]
    assert f1["familias_efectivas"] == params["f_bar"]
    assert f2["estado"] == "en_cola" and "sin_ubicar" in f2["marcas"] and f2["zona_id"] is None
    assert f3["estado"] == "en_cola" and {"sobre_tope", "familias_absurdas"} <= f3["marcas"]


def test_duplicado_exacto_e_idempotencia(con, params, z, hora):
    filas = [sol(hora(), "a", z["Barrio A"]), sol(hora(), "b", z["Barrio B"])]
    r1 = embudo.procesar_lote(con, filas, params, hora())
    r2 = embudo.procesar_lote(con, filas, params, hora())
    assert r1["nuevas"] == 2 and r2["nuevas"] == 0 and r2["duplicado_exacto"] == 2
    assert r1["base"] == r2["base"]
    # El mismo texto en el mismo minuto con otra puntuación también es duplicado.
    otra = "¡" + filas[0]["texto"].upper().replace(" ", ",  ") + "!"
    r3 = embudo.procesar_lote(con, [dict(filas[0], texto=otra)], params, hora())
    assert r3["duplicado_exacto"] == 1


def test_cuarentena_por_limite_y_cadencia(con, params, z, hora):
    # Un ciudadano con 4 mensajes en 3 minutos: la cubeta (B = 3) se agota.
    filas = [sol(hora(minutos=i), "rapido", z["Barrio A"], texto=f"mensaje {chr(97 + i)}",
                 productos=(f"p{i}",)) for i in range(4)]
    embudo.procesar_lote(con, filas, params, hora(1))
    f = fila(con, 4)
    assert f["estado"] == "cuarentena" and f["motivo_cuarentena"] == "limite_remitente"
    assert f["zona_id"] == z["Barrio A"].id
    # Un líder (B = 20) con intervalos exactos de 10 min: cadencia de máquina.
    agentes.registrar_lider(con, h("bot"), [z["Barrio B"].id], "coordinador:ana")
    filas = [sol(hora(2, minutos=10 * i), "bot", z["Barrio B"], texto=f"pedido {chr(97 + i)}",
                 productos=(f"q{i}",)) for i in range(4)]
    embudo.procesar_lote(con, filas, params, hora(3))
    assert fila(con, 8)["motivo_cuarentena"] == "cadencia"


def test_rafaga_de_zona_pone_en_cuarentena_a_los_nuevos(con, params, z, hora):
    # Barrio B: lambda = 200·0.05/24 ≈ 0.42/h. Doce mensajes en 12 min desde remitentes nuevos.
    filas = [sol(hora(minutos=i), f"n{i}", z["Barrio B"], texto=f"texto distinto numero {chr(97 + i)} "
                 * (i + 1), productos=(f"p{i}",)) for i in range(12)]
    embudo.procesar_lote(con, filas, params, hora(1))
    motivos = [fila(con, i)["motivo_cuarentena"] for i in range(1, 13)]
    assert "rafaga_zona" in motivos
    assert censo.zona_por_id(con, z["Barrio B"].id).rafaga_hasta is not None


def test_texto_coordinado_retroactivo_y_excepcion_de_lider(con, params, z, hora):
    texto = "Necesitamos mercados urgente en el barrio, somos 20 familias sin comida desde el sismo"
    filas = [sol(hora(minutos=i), f"c{i}", z["Barrio A"], texto=texto, productos=(f"p{i}",))
             for i in range(3)]
    embudo.procesar_lote(con, filas, params, hora(1))
    assert all(fila(con, i)["motivo_cuarentena"] == "texto_coordinado" for i in (1, 2, 3))
    assert censo.cupo_consumido(con, z["Barrio A"].id, hora(1), params) == 0
    # Con un líder de la zona en el grupo, se consolida en vez de ir a cuarentena.
    agentes.registrar_lider(con, h("lider"), [z["Barrio C"].id], "coordinador:ana")
    filas = [sol(hora(3, minutos=i), r, z["Barrio C"], texto=texto, productos=(f"x{i}",))
             for i, r in enumerate(["lider", "d1", "d2"])]
    embudo.procesar_lote(con, filas, params, hora(4))
    assert fila(con, 6)["estado"] == "consolidada" and fila(con, 6)["consolidada_en"] == 4


def test_consolidacion_por_cluster_y_productos(con, params, z, hora):
    zb = z["Barrio C"]
    filas = [sol(hora(minutos=10 * i), f"v{i}", zb, texto=f"pedido numero {chr(97 + i)} distinto",
                 familias=4 + i, productos=("arroz", "agua"), norte_m=20 * i) for i in range(4)]
    filas.append(sol(hora(minutos=50), "otro", zb, texto="necesitamos pañales para bebes",
                     productos=("panales",), norte_m=10))
    embudo.procesar_lote(con, filas, params, hora(1))
    e = estados(con)
    assert e[1] in ("confirmada_regla", "en_cola") and e[2] in ("confirmada_regla", "en_cola")
    assert e[3] == "consolidada" and fila(con, 3)["consolidada_en"] == 1
    assert e[4] == "consolidada" and fila(con, 4)["consolidada_en"] == 1
    assert e[5] != "consolidada"                              # productos distintos
    assert fila(con, 1)["familias_declaradas"] == 7            # máximo, no suma
    assert embudo.consolidar([]) == []


def test_extractor_se_usa_y_si_falla_no_se_cae(con, params, z, hora):
    zona = z["Barrio A"]

    def extractor(texto):
        if "romper" in texto:
            raise RuntimeError("modelo caído")
        return {"familias": 8, "productos": ["leche"], "lat": zona.lat, "lon": zona.lon,
                "lugar_confirmado": True}
    filas = [{"recibida_en": a_iso(hora()), "remitente_hash": h("e1"), "texto": "somos ocho"},
             {"recibida_en": a_iso(hora()), "remitente_hash": h("e2"), "texto": "romper todo"},
             {"recibida_en": a_iso(hora()), "remitente_hash": h("e3"), "texto": "   "}]
    r = embudo.procesar_lote(con, filas, params, hora(), extractor=extractor)
    assert r["error_interno"] == [] and r["nuevas"] == 3
    f1, f2, f3 = fila(con, 1), fila(con, 2), fila(con, 3)
    assert f1["familias_declaradas"] == 8 and f1["zona_id"] == zona.id
    assert f2["estado"] == "en_cola" and {"extraccion_fallida", "extractor_fallo"} <= f2["marcas"]
    assert "sin_texto" in f3["marcas"]


def test_zona_debil_espera_agente_y_validacion_integrada(con, params, z, hora):
    zona = z["Albergue Coliseo"]
    con.execute("UPDATE zonas SET lambda_h=2.0 WHERE id=?", (zona.id,))
    con.commit()
    p = dict(params, hora_evento=a_iso(hora(0)))
    embudo.procesar_lote(con, [], p, hora(3))
    assert censo.zona_por_id(con, zona.id).es_debil == 1
    embudo.procesar_lote(con, [sol(hora(3.5), "vecino", zona, productos=("arroz",))], p, hora(3.5))
    f = fila(con, 1)
    assert f["estado"] == "espera_agente" and f["tarea_id"] is not None
    agentes.enrolar(con, h("agente"), "Cruz Roja", [zona.id], "coordinador:ana")
    r = agentes.validar(con, h("agente"), f["tarea_id"], zona.lat, zona.lon,
                        [{"familias": 30, "productos": ["arroz", "agua"]}], hora(4), p)
    assert r["ok"] and r["consolidadas"] == [1]
    nueva = fila(con, r["solicitudes"][0])
    assert nueva["estado"] in ("confirmada_regla", "en_cola") and "validada_agente" in json.loads(
        nueva["senales"])
    # Topes siguen aplicando: 30 familias en un albergue con tope 120 → dentro.
    assert nueva["familias_efectivas"] == 30


def test_solo_un_humano_confirma_o_descarta(con, params, z, hora):
    embudo.procesar_lote(con, [sol(hora(), "a", z["Barrio A"], familias=None)], params, hora())
    with pytest.raises(PermissionError):
        embudo.cambiar_estado(con, [1], "descartada", "regla:v1")
    with pytest.raises(PermissionError):
        embudo.cambiar_estado(con, [1], "confirmada", "regla:triage")
    with pytest.raises(ValueError):
        embudo.cambiar_estado(con, [1], "inventado", "coordinador:ana")
    embudo.cambiar_estado(con, [1], "confirmada", "despachador:luis")
    assert fila(con, 1)["estado"] == "confirmada"
    antifraude.descartar(con, [1], "despachador:luis")
    assert fila(con, 1)["estado"] == "descartada"
    etiquetas = puntaje.etiquetas_desde_bitacora(con)
    assert etiquetas == [{"id": 1, "senales": ["dentro_de_tope", "lugar_confirmado"], "real": False}]


def test_liberar_devuelve_al_paso_3(con, params, z, hora):
    texto = "Necesitamos mercados urgente en el barrio, somos 20 familias sin comida desde el sismo"
    filas = [sol(hora(minutos=i), f"c{i}", z["Barrio A"], texto=texto, productos=(f"p{i}",))
             for i in range(3)]
    embudo.procesar_lote(con, filas, params, hora(1))
    assert fila(con, 3)["estado"] == "cuarentena"
    assert antifraude.liberar(con, [3, 99], "coordinador:ana") == [3]
    f = fila(con, 3)
    assert f["estado"] in ("confirmada_regla", "en_cola") and "liberada" in f["marcas"]
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='liberar_cuarentena'").fetchone()[0] == 1


def test_cada_estado_se_alcanza(con, params, z, hora):
    """recibida (en tránsito) y los otros siete estados aparecen en la base."""
    vistos = set()
    texto = "Necesitamos mercados urgente en el barrio, somos 20 familias sin comida desde el sismo"
    embudo.procesar_lote(con, [sol(hora(), "ok", z["Barrio A"]),
                               sol(hora(), "cola", None, lat=0, lon=0)]
                         + [sol(hora(minutos=i), f"c{i}", z["Barrio B"], texto=texto,
                                productos=(f"p{i}",)) for i in range(3)], params, hora(1))
    vistos |= set(estados(con).values())
    embudo.procesar_lote(con, [sol(hora(2, minutos=5 * i), f"k{i}", z["Barrio C"],
                                   productos=("arroz", "agua")) for i in range(3)], params, hora(3))
    vistos |= set(estados(con).values())
    zona = z["Albergue Coliseo"]
    con.execute("UPDATE zonas SET lambda_h=2.0 WHERE id=?", (zona.id,))
    con.commit()
    p = dict(params, hora_evento=a_iso(hora(0)))
    embudo.procesar_lote(con, [], p, hora(3))
    embudo.procesar_lote(con, [sol(hora(3.5), "debil", zona)], p, hora(3.5))
    vistos |= set(estados(con).values())
    embudo.cambiar_estado(con, [2], "confirmada", "despachador:luis")
    embudo.cambiar_estado(con, [1], "descartada", "despachador:luis")
    embudo.cambiar_estado(con, [3], "recibida", "despachador:luis")
    vistos |= set(estados(con).values())
    assert vistos == set(embudo.ESTADOS)


def test_ningun_dato_tumba_el_lote(con, params, z, hora):
    basura = [None, 5, "texto", {}, {"recibida_en": "nunca", "remitente_hash": "x"},
              {"recibida_en": a_iso(hora()), "remitente_hash": h("raro"), "lat": "abc",
               "lon": float("nan"), "familias": "muchas", "productos": {"producto": 3},
               "texto": "🙏🙏 ¿?", "canal": "agente"}]
    r = embudo.procesar_lote(con, basura, params, hora())
    assert r["nuevas"] == 1 and len(r["filas_invalidas"]) >= 5 and r["error_interno"] == []
    f = fila(con, 1)
    assert f["estado"] == "en_cola" and f["canal"] == "chat" and "canal_no_verificado" in f["marcas"]
    assert embudo.procesar_lote(con, [], params, hora())["nuevas"] == 0
