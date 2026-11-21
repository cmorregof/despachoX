import math
from datetime import timedelta

from triage import censo
from triage.geo import Zona
from triage.tests.conftest import cuadrado_wkt, zonas_basicas, LAT0, LON0


def test_tope_con_censo(params):
    z = Zona(id=1, nombre="A", lat=5.06, lon=-75.5, hogares=1000, afectacion=0.2)
    assert censo.hogares_afectados(z, params) == 200
    assert censo.tope_familias(z, params) == math.ceil(200 * 1.2)


def test_tope_sin_censo_y_minimo(params):
    filas, _ = censo.normalizar_zonas([{"nombre": "Sin dato", "lat": 5.06, "lon": -75.5}], params)
    z = Zona(id=1, **{k: v for k, v in filas[0].items()})
    assert z.calidad_dato == "estimado" and z.personas is None
    assert censo.tope_familias(z, params) == params["T_min"]
    cero = Zona(id=2, nombre="Cero", lat=5.06, lon=-75.5, hogares=0, afectacion=0.5)
    assert censo.tope_familias(cero, params) == params["T_min"]


def test_respaldo_por_mediana_de_comuna(params):
    filas = [{"nombre": "A", "comuna": "X", "lat": 5.06, "lon": -75.5, "personas": 1000},
             {"nombre": "B", "comuna": "X", "lat": 5.07, "lon": -75.5, "personas": 3000},
             {"nombre": "C", "comuna": "X", "lat": 5.08, "lon": -75.5},
             {"nombre": "D", "comuna": "Y", "lat": 5.09, "lon": -75.5}]
    zonas, errores = censo.normalizar_zonas(filas, params)
    assert errores == []
    c, d = zonas[2], zonas[3]
    assert c["personas"] == 2000 and c["hogares"] == round(2000 / 3)
    assert c["calidad_dato"] == "estimado"
    assert d["personas"] == 2000           # mediana de todas
    assert c["afectacion"] == params["a_prior"]


def test_albergue_por_ocupacion(params):
    z = Zona(id=1, nombre="Coliseo", tipo="albergue", lat=5.06, lon=-75.5, ocupacion=300,
             tamano_hogar=3.0, afectacion=1.0, hogares=50)
    assert censo.tope_familias(z, params) == math.ceil(300 / 3.0 * 1.2)


def test_tope_de_solicitudes(params):
    chica = Zona(id=1, nombre="V", lat=5.0, lon=-75.5, hogares=10, afectacion=0.1)
    assert censo.tope_solicitudes(chica, params) == params["S_min"]
    grande = Zona(id=2, nombre="G", lat=5.0, lon=-75.5, hogares=1000, afectacion=0.2)
    assert censo.tope_solicitudes(grande, params) == math.ceil(2 * 240 / 10)


def test_area_desde_poligono_y_densidad(params):
    filas, _ = censo.normalizar_zonas([{"nombre": "P", "lat": LAT0, "lon": LON0, "personas": 5000,
                                        "geom_wkt": cuadrado_wkt(LAT0, LON0, 1000)}], params)
    z = Zona(id=1, **filas[0])
    assert abs(z.area_km2 - 1.0) < 0.01
    assert abs(censo.densidad(z) - 5000) < 50


def test_filas_invalidas_no_tumban(params):
    zonas, errores = censo.normalizar_zonas([{"nombre": "", "lat": 5, "lon": -75.5},
                                             {"nombre": "Sin lat"}, "no es dict",
                                             {"nombre": "Ok", "lat": "5,06", "lon": "-75,5",
                                              "tipo": "palacio", "afectacion": 7}], params)
    assert len(zonas) == 1 and zonas[0]["tipo"] == "barrio" and zonas[0]["afectacion"] == 1.0
    assert sum(e["rechazada"] for e in errores) == 3


def test_semilla_y_carga(con, params):
    zonas = censo.zonas_desde_semilla(params)
    assert len(zonas) > 100
    assert all(z["calidad_dato"] == "estimado" for z in zonas)
    assert zonas == censo.zonas_desde_semilla(params)           # determinista
    ids = censo.cargar_zonas(con, zonas)
    assert censo.cargar_zonas(con, zonas) == ids                 # idempotente
    assert len(censo.zonas_de_base(con)) == len(zonas)


def test_cupo_consumido(con, params, zonas_sinteticas, ahora):
    z = zonas_sinteticas[0]
    for i, (estado, fam, horas) in enumerate([("confirmada_regla", 10, 1), ("confirmada", 5, 2),
                                              ("en_cola", 50, 1), ("confirmada", 7, 100)]):
        con.execute("INSERT INTO solicitudes(recibida_en, hash_mensaje, remitente_hash, zona_id, "
                    "familias_efectivas, estado) VALUES (?,?,?,?,?,?)",
                    ((ahora - timedelta(hours=horas)).isoformat(timespec="seconds"), f"h{i}", "r",
                     z.id, fam, estado))
    assert censo.cupo_consumido(con, z.id, ahora, params) == 15


def test_zonas_basicas_cargan(zonas_sinteticas):
    assert len(zonas_sinteticas) == len(zonas_basicas())
    alb = [z for z in zonas_sinteticas if z.tipo == "albergue"][0]
    assert alb.ocupacion == 300
