"""Pruebas de tablero/datos.py con una base temporal. No usan la red vial ni el optimizador."""
import json
import subprocess
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

import lugares
from datos import db
from tablero import datos as T

AHORA = datetime(2026, 11, 20, 10, 0, 0, tzinfo=db.BOGOTA)


def iso(horas: float = 0) -> str:
    return (AHORA + timedelta(hours=horas)).isoformat(timespec="seconds")


def crear_plan(con, plan_id, paradas, *, estado="propuesto", motivo="inicial", resumen=None, horas=0):
    """paradas: [(vehiculo_id, orden, punto_id, pedido_id, llegada en horas, geometria)]"""
    resumen = {"calculado_para": iso(horas), "sin_atender": [], "cierres_aplicados": [],
               "vehiculos": [], **(resumen or {})}
    con.execute("INSERT INTO planes(id, creado_en, motivo, estado, segundos_calculo, resumen) VALUES (?,?,?,?,?,?)",
                (plan_id, iso(horas), motivo, estado, 1.5, json.dumps(resumen)))
    con.executemany(
        "INSERT INTO paradas(plan_id, vehiculo_id, orden, punto_id, pedido_id, llegada_estimada, kg, geometria) "
        "VALUES (?,?,?,?,?,?,?,?)",
        [(plan_id, v, o, pu, pe, iso(h), 10.0, json.dumps(g)) for v, o, pu, pe, h, g in paradas])
    con.commit()


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "t.db")
    c.executemany("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (?,?,?,?,?,?)", [
        (1, "Albergue A", "A", 5.07, -75.52, 1), (2, "Comedor B", "B", 5.06, -75.51, 1),
        (3, "Salón C", "C", 5.05, -75.50, 0)])
    c.execute("INSERT INTO acopios(id,nombre,lat,lon) VALUES (1,'Bodega',5.04,-75.49)")
    c.executemany("INSERT INTO vehiculos(id,nombre,tipo,capacidad_kg,acopio_id) VALUES (?,?,?,?,1)",
                  [(1, "Camión 1", "camion", 3000), (2, "Campero 1", "campero", 600)])
    c.executemany(
        "INSERT INTO pedidos(id,creado_en,punto_id,urgencia,limite_en,estado,duplicado_de,texto_original) "
        "VALUES (?,?,?,?,?,?,?,?)", [
            (1, iso(-1), 1, 3, iso(2), "confirmado", None, "necesitamos mercados"),
            (2, iso(-1), 2, 2, iso(1), "confirmado", None, "falta agua"),
            (3, iso(-1), 3, 1, None, "confirmado", None, "sin afán"),
            (4, iso(-1), 3, 2, iso(4), "nuevo", None, "pedido nuevo"),
            (5, iso(-1), 3, 2, iso(4), "nuevo", 4, "el mismo pedido otra vez"),
            (6, iso(-1), None, 3, iso(4), "nuevo", None, "estamos por la siria"),
            (7, iso(-1), 1, 2, iso(4), "descartado", None, "ruido")])
    c.executemany("INSERT INTO lotes(id,acopio_id,producto,kg,perecedero,vence_en) VALUES (?,?,?,?,?,?)", [
        (1, 1, "arroz", 500, 0, None), (2, 1, "pollo", 40, 1, iso(6)), (3, 1, "leche", 25.5, 1, iso(11.9)),
        (4, 1, "fruta", 70, 1, iso(30)), (5, 1, "pan", 9, 1, iso(-2))])
    c.executemany("INSERT INTO cierres(id,creado_en,lugar,lat,lon,estado,texto_original) VALUES (?,?,?,?,?,?,?)", [
        (1, iso(-1), "vía X", 5.06, -75.5, "reportado", "derrumbe en la vía X"),
        (2, iso(-1), "vía Y", 5.05, -75.5, "confirmado", "árbol caído")])
    c.commit()
    return c


# ---------- indicadores ----------

def test_indicadores_sin_plan(con):
    i = T.indicadores(con, None, AHORA)
    assert i["pedidos_pendientes"] == 5          # 3 confirmados + 2 nuevos; duplicado y descartado no cuentan
    assert i["pedidos_por_confirmar"] == 2
    assert i["kg_vencen_pronto"] == 65.5         # pollo y leche; lo de 30 h y lo ya vencido no
    assert i["cierres_activos"] == 1 and i["cierres_reportados"] == 1
    assert i["puntualidad"]["pct"] is None and i["puntualidad"]["pct_criticos"] is None


def test_puntualidad_separa_criticos_y_cuenta_lo_sin_atender(con):
    crear_plan(con, 1, [(1, 1, 1, 1, 1.0, []),      # crítico, a tiempo
                        (1, 2, 2, 2, 1.5, [])],     # crítico, tarde (límite a 1 h)
               resumen={"sin_atender": [{"pedido_id": 3, "punto_id": 3, "motivo": "no cabe"}]})
    p = T.plan_vigente(con)
    r = T.puntualidad(con, p)
    assert (r["total"], r["a_tiempo"], r["pct"]) == (3, 1, 33.3)
    assert (r["criticos_total"], r["criticos_a_tiempo"], r["pct_criticos"]) == (2, 1, 50.0)
    assert T.sin_atender(con, p) == [{"pedido_id": 3, "punto_id": 3, "punto": "Salón C", "critico": 0,
                                      "motivo": "no cabe"}]


def test_pedido_sin_limite_usa_el_plazo_por_urgencia(con):
    crear_plan(con, 1, [(1, 1, 3, 3, 22.0, [])])     # urgencia 1: 24 h desde que se creó (hace 1 h)
    assert T.paradas(con, T.plan_vigente(con))[0]["a_tiempo"] is True
    con.execute("UPDATE paradas SET llegada_estimada=?", (iso(23.5),))
    assert T.paradas(con, T.plan_vigente(con))[0]["a_tiempo"] is False


# ---------- plan vigente y rutas ----------

def test_plan_vigente_prefiere_la_propuesta(con):
    assert T.plan_vigente(con) is None
    crear_plan(con, 1, [], estado="aprobado")
    crear_plan(con, 2, [], estado="reemplazado")
    assert T.plan_vigente(con)["id"] == 1
    crear_plan(con, 3, [], estado="propuesto")
    assert T.plan_vigente(con)["id"] == 3 and T.plan_aprobado(con)["id"] == 1


def test_rutas_traen_tramos_y_regreso(con):
    tramo, regreso = [[5.04, -75.49], [5.07, -75.52]], [[5.07, -75.52], [5.04, -75.49]]
    crear_plan(con, 1, [(1, 1, 1, 1, 1.0, tramo), (2, 1, 3, 3, 1.0, tramo)],
               resumen={"vehiculos": [{"vehiculo_id": 1, "nombre": "Camión 1", "capacidad_kg": 3000,
                                       "regreso": regreso}]})
    r = T.rutas(con, T.plan_vigente(con))
    assert [x["vehiculo_id"] for x in r] == [1, 2]
    assert r[0]["regreso"] == regreso and r[0]["paradas"][0]["geometria"] == tramo
    assert r[1]["regreso"] == [] and r[1]["nombre"] == "Campero 1"


def test_resumen_dañado_no_rompe(con):
    con.execute("INSERT INTO planes(id, creado_en, estado, resumen) VALUES (1, ?, 'propuesto', 'no es json')",
                (iso(),))
    p = T.plan_vigente(con)
    assert p["resumen"] == {} and T.rutas(con, p) == [] and T.sin_atender(con, p) == []


# ---------- cierres y recálculo ----------

def test_aviso_de_cierre_nuevo(con):
    assert T.cierres_sin_aplicar(con, None) == []                    # sin plan no hay qué recalcular
    crear_plan(con, 1, [(1, 1, 1, 1, 1.0, [])], estado="aprobado", resumen={"cierres_aplicados": [2]})
    assert T.cierres_sin_aplicar(con, T.plan_vigente(con)) == []
    assert T.cambiar_estado(con, "cierres", 1, "confirmado", "Ana")
    assert [c["id"] for c in T.cierres_sin_aplicar(con, T.plan_vigente(con))] == [1]


def test_cierre_que_el_recalculo_no_pudo_aplicar_no_insiste(con):
    crear_plan(con, 1, [], motivo="cierre 2", resumen={"cierres_aplicados": []})
    assert T.cierres_sin_aplicar(con, T.plan_vigente(con)) == []
    T.cambiar_estado(con, "cierres", 1, "confirmado", "Ana")         # confirmado después del plan
    assert [c["id"] for c in T.cierres_sin_aplicar(con, T.plan_vigente(con))] == [1]


def test_comparar_planes(con):
    a, b = [[5.0, -75.5], [5.1, -75.5]], [[5.0, -75.5], [5.05, -75.45], [5.1, -75.5]]
    crear_plan(con, 1, [(1, 1, 1, 1, 0.5, a), (1, 2, 2, 2, 1.0, a), (2, 1, 3, 3, 0.5, a)],
               estado="reemplazado")
    # Una hora después: el camión cambia el orden, el campero hace un desvío de 20 minutos.
    crear_plan(con, 2, [(1, 1, 2, 2, 1.5, a), (1, 2, 1, 1, 2.25, a), (2, 1, 3, 3, 1.5 + 20 / 60, b)],
               motivo="cierre 2", resumen={"reemplaza_a": [1]}, horas=1)
    c = T.cambios_del_recalculo(con, T.plan_vigente(con))
    assert c["anterior"] == 1
    assert [(v["nombre"], v["cambio"]) for v in c["vehiculos"]] == [("Camión 1", "otro orden"),
                                                                    ("Campero 1", "desvío")]
    # Pedido 1: antes a 30 min de la salida, ahora a 75. Es el que más se movió.
    assert c["mayor"] == {"pedido_id": 1, "punto": "Albergue A", "vehiculo": "Camión 1", "minutos": 45}
    assert c["salen"] == [] and c["entran"] == []


def test_un_plan_inicial_no_muestra_cambios(con):
    crear_plan(con, 1, [(1, 1, 1, 1, 0.5, [])], estado="reemplazado")
    crear_plan(con, 2, [(1, 1, 1, 1, 0.5, [])], resumen={"reemplaza_a": [1]})
    assert T.cambios_del_recalculo(con, T.plan_vigente(con)) is None


# ---------- por revisar y cambios de estado ----------

def test_por_revisar_agrupa_duplicados_y_marca_sin_ubicar(con):
    r = T.por_revisar(con)
    assert [d["id"] for d in r["pedidos"]] == [6, 4]                 # el más urgente primero
    sin, con_punto = r["pedidos"]
    assert sin["sin_ubicar"] and not con_punto["sin_ubicar"]
    assert [x["id"] for x in con_punto["duplicados"]] == [5]
    assert [c["id"] for c in r["cierres"]] == [1]


def test_cambios_de_estado_validos_y_bitacora(con):
    assert T.cambiar_estado(con, "pedidos", 4, "confirmado", "Ana")
    assert con.execute("SELECT estado FROM pedidos WHERE id=4").fetchone()[0] == "confirmado"
    ultima = T.bitacora(con, 1)[0]
    assert (ultima["quien"], ultima["accion"], ultima["detalle"]) == ("Ana", "confirmar pedido",
                                                                     "pedidos 4 -> confirmado")
    antes = len(T.bitacora(con))
    assert not T.cambiar_estado(con, "pedidos", 4, "confirmado", "Ana")      # ya no está nuevo
    assert not T.cambiar_estado(con, "pedidos", 6, "confirmado", "Ana")      # sin ubicar
    assert not T.cambiar_estado(con, "pedidos", 4, "entregado", "Ana")       # no es del tablero
    assert not T.cambiar_estado(con, "vehiculos", 1, "fuera", "Ana")
    assert not T.cambiar_estado(con, "pedidos", 999, "descartado", "Ana")
    assert len(T.bitacora(con)) == antes                                     # lo rechazado no se anota


def test_rechazar_solo_un_plan_propuesto(con):
    crear_plan(con, 1, [], estado="aprobado")
    crear_plan(con, 2, [])
    assert not T.cambiar_estado(con, "planes", 1, "rechazado", "Ana")
    assert T.cambiar_estado(con, "planes", 2, "rechazado", "Ana")
    assert T.plan_vigente(con)["id"] == 1
    assert T.bitacora(con, 1)[0]["accion"] == "rechazar plan"


# ---------- ubicaciones ----------

@pytest.fixture
def con_lugares(con):
    assert lugares.cargar_semilla(con) > 100
    return con


def test_ubicacion_propuesta_se_confirma(con_lugares):
    con = con_lugares
    r = lugares.resolver(con, "via a chinchna", tabla="cierres", fila_id=1, tipos=("via",), elegir=None)
    u = T.por_revisar(con)["ubicaciones"]
    assert len(u) == 1 and u[0]["texto"] == "via a chinchna" and u[0]["lugar"] == "vía a Chinchiná"
    assert u[0]["texto_completo"] == "derrumbe en la vía X"
    assert all(c["lugar_id"] != u[0]["lugar_id"] for c in u[0]["alternativas"])
    assert T.confirmar_ubicacion(con, r.ubicacion_id, "Ana")
    assert T.por_revisar(con)["ubicaciones"] == []
    assert con.execute("SELECT lugar FROM cierres WHERE id=1").fetchone()[0] == "vía a Chinchiná"


def test_corregir_con_pin_ubica_el_pedido(con_lugares):
    con = con_lugares
    r = lugares.resolver(con, "zzyx del mico azul", tabla="pedidos", fila_id=6, tipos=("barrio", "sitio"), elegir=None)
    u = T.por_revisar(con)["ubicaciones"][0]
    assert u["lugar_id"] is None and u["lat"] is None            # el resolvedor no inventa
    assert T.corregir_ubicacion(con, r.ubicacion_id, 5.031, -75.47)
    fila = con.execute("SELECT confirmado_por, metodo, estado FROM ubicaciones WHERE id=?",
                       (r.ubicacion_id,)).fetchone()
    assert tuple(fila) == ("despachador", "despachador", "confirmada")
    pedido = T.por_revisar(con)["pedidos"][0]
    assert pedido["id"] == 6 and not pedido["sin_ubicar"]
    assert T.cambiar_estado(con, "pedidos", 6, "confirmado", "Ana")


# ---------- llamada a despacho/ ----------

def falso(stdout="", stderr="", codigo=0, registro=None):
    def correr(orden, **kw):
        if registro is not None:
            registro.append(orden)
        return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=codigo)
    return correr


def test_ejecutar_despacho_lee_el_id(con):
    registro = []
    r = T.ejecutar_despacho("optimizar", "--aprobar", "7", "--quien", "Ana",
                            correr=falso("aviso\n7\n", registro=registro))
    assert r.ok and r.plan_id == 7
    assert registro[0][1:] == ["-m", "despacho.optimizar", "--aprobar", "7", "--quien", "Ana"]


def test_ejecutar_despacho_informa_los_fallos(con):
    r = T.ejecutar_despacho("optimizar", correr=falso("", "el plan 7 no está propuesto", 1))
    assert not r.ok and r.mensaje == "el plan 7 no está propuesto"
    assert not T.ejecutar_despacho("optimizar", correr=falso("-1\n")).ok
    assert not T.ejecutar_despacho("borrar_todo", correr=falso("1\n")).ok

    def lento(orden, **kw):
        raise subprocess.TimeoutExpired(orden, 1)
    r = T.ejecutar_despacho("recalcular", correr=lento, espera_s=1)
    assert not r.ok and "no respondió" in r.mensaje
