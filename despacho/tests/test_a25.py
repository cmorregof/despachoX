"""Pruebas del A25 (despacho/a25.py) y de su gancho en el optimizador, sin red ni caché."""
import csv
import json
import math
from datetime import date, timedelta

import pytest

from despacho import a25, matriz, optimizar
from despacho.tests.conftest import AISLADO, PUENTE, coords, nodo

SEG = 1
DIA = date(2026, 11, 21)


def serie_constante(mm, fecha=DIA, dias=25):
    return {fecha - timedelta(days=k): mm for k in range(dias)}


def lluvia_de(series, sintetica=True):
    return a25.Lluvia(series=series, sintetica=sintetica, origen="prueba", avisos=[])


# ---------------------------------------------------------------- a25() y nivel()

def test_a25_suma_el_dia_y_los_24_anteriores():
    serie = {date(2026, 11, 1) + timedelta(days=k): float(k + 1) for k in range(30)}   # 1..30 mm
    # El 30 de noviembre: días 6 a 30 → (6 + 30) · 25 / 2 = 450 mm. El día 5 ya no cuenta.
    assert a25.a25(serie, date(2026, 11, 30)) == 450.0
    assert a25.a25(serie, date(2026, 11, 29)) == 450.0 - 30 + 5
    w = a25.ventana(serie, date(2026, 11, 30))
    assert w.completo and w.dias_con_dato == 25


def test_a25_reproduce_el_reporte_del_idea_de_2020():
    """Estación Chec-Uribe, enero y febrero de 2020, del reporte «SAT Deslizamientos-Registro lluvias
    diarias y A25 2020» del IDEA (leído con un extractor automático el 2026-11-20; abrir el PDF para
    confirmar). Con la lluvia diaria desde el 1 de enero se reproducen los 36 A25 publicados del 25
    de enero al 29 de febrero si la ventana incluye el día del reporte. Sin el día no cuadra: el 21
    de enero el A25 sube 20 mm, que es la lluvia de ese mismo día."""
    lluvia_enero = [5.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0,
                    0.0, 0.0, 0.0, 0.8, 20.0, 16.6, 0.0, 1.2, 1.6, 14.8, 4.4, 2.6, 0.0, 0.0, 0.0]
    lluvia_febrero = [0.0, 0.6, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 4.4,
                      0.0, 0.0, 0.0, 16.0, 0.0, 53.8, 0.0, 5.8, 2.0, 16.2, 0.0, 0.0, 0.0]
    a25_enero = {25: 46.0, 26: 55.8, 27: 60.2, 28: 62.8, 29: 62.8, 30: 62.8, 31: 62.8}
    a25_febrero = [62.8, 63.4, 63.4, 63.4, 63.4, 63.4, 63.4, 63.6, 62.8, 62.8, 62.8, 62.8, 62.8, 62.0, 42.0,
                   29.8, 29.8, 28.6, 27.0, 28.2, 23.8, 75.0, 75.0, 80.8, 82.8, 99.0, 98.4, 98.4, 98.4]
    serie = {date(2020, 1, d): mm for d, mm in enumerate(lluvia_enero, start=1)}
    serie.update({date(2020, 2, d): mm for d, mm in enumerate(lluvia_febrero, start=1)})
    esperado = {date(2020, 1, d): v for d, v in a25_enero.items()}
    esperado.update({date(2020, 2, d): v for d, v in enumerate(a25_febrero, start=1)})
    assert len(esperado) == 36
    for dia, valor in esperado.items():
        assert a25.a25(serie, dia) == valor, dia
        assert a25.ventana(serie, dia).completo


@pytest.mark.parametrize("valor, esperado", [
    (0.0, "sin_alerta"), (199.9, "sin_alerta"), (200.0, "amarilla"), (299.9, "amarilla"),
    (300.0, "naranja"), (399.9, "naranja"), (400.0, "roja"), (812.5, "roja"),
    (None, "sin_dato"), (float("nan"), "sin_dato"),
])
def test_bordes_de_cada_umbral(valor, esperado):
    assert a25.nivel(valor) == esperado


def test_la_suma_en_coma_flotante_no_baja_de_nivel():
    for umbral, esperado in ((300.0, "naranja"), (400.0, "roja")):
        serie = {DIA - timedelta(days=k): 1.4 for k in range(1, 25)}
        serie[DIA] = round(umbral - 24 * 1.4, 1)              # 24 · 1,4 + 266,4 = 300,0 mm
        ingenua = 0.0
        for d in sorted(serie):
            ingenua += serie[d]
        assert ingenua < umbral                               # la suma ingenua da 299,99…
        assert a25.a25(serie, DIA) == umbral
        assert a25.nivel(a25.a25(serie, DIA)) == esperado


def test_dias_faltantes_dan_cota_inferior():
    serie = serie_constante(10.0)
    del serie[DIA - timedelta(days=3)]                        # día ausente
    serie[DIA - timedelta(days=5)] = None                     # día vacío
    serie[DIA - timedelta(days=7)] = -1.0                     # dato inválido
    w = a25.ventana(serie, DIA)
    assert w.valor == 220.0 and w.dias_con_dato == 22
    assert set(w.faltantes) == {DIA - timedelta(days=k) for k in (3, 5, 7)}
    assert not w.completo
    assert math.isnan(a25.a25({}, DIA))
    assert a25.nivel(a25.a25({}, DIA)) == "sin_dato"


# ---------------------------------------------------------------- estaciones y tramos

ESTACIONES = [a25.Estacion("norte", "Norte", 5.0800, -75.5000), a25.Estacion("sur", "Sur", 5.0400, -75.5000)]


def test_cada_tramo_toma_la_estacion_mas_cercana():
    lluvia = lluvia_de({"norte": serie_constante(17.0), "sur": serie_constante(9.0)})   # 425 y 225 mm
    lista = [{"tramo": "cerca del norte", "lat": 5.0790, "lon": -75.5010, "osm_u": 1, "osm_v": 2},
             {"tramo": "cerca del sur", "lat": 5.0420, "lon": -75.4990, "osm_u": 3, "osm_v": 4},
             {"tramo": "lejos", "lat": 5.2000, "lon": -75.5000, "osm_u": 5, "osm_v": 6}]
    al = {a["tramo"]: a for a in a25.alertas_tramos(None, DIA, lluvia, ESTACIONES, lista_tramos=lista)}
    assert al["cerca del norte"]["estacion_id"] == "norte" and al["cerca del norte"]["nivel"] == "roja"
    assert al["cerca del sur"]["estacion_id"] == "sur" and al["cerca del sur"]["nivel"] == "amarilla"
    assert al["lejos"]["nivel"] == "fuera_de_red" and al["lejos"]["a25_mm"] is None
    assert al["lejos"]["estacion_mas_cercana"] == "Norte"
    orden = [a["tramo"] for a in a25.alertas_tramos(None, DIA, lluvia, ESTACIONES, lista_tramos=lista)]
    assert orden == ["cerca del norte", "cerca del sur", "lejos"]           # de más a menos grave


def test_estacion_con_huecos_cede_a_una_vecina_completa():
    norte = serie_constante(17.0)
    del norte[DIA]
    lluvia = lluvia_de({"norte": norte, "sur": serie_constante(9.0)})
    lista = [{"tramo": "t", "lat": 5.0700, "lon": -75.5000, "osm_u": 1, "osm_v": 2}]   # 1,1 km y 3,3 km
    a = a25.alertas_tramos(None, DIA, lluvia, ESTACIONES, lista_tramos=lista)[0]
    assert a["estacion_id"] == "norte" and not a["completo"]                # el sur queda fuera de 3 km
    assert "cota inferior" in a["nota"]
    a = a25.alertas_tramos(None, DIA, lluvia, ESTACIONES, cobertura_km=4.0, lista_tramos=lista)[0]
    assert a["estacion_id"] == "sur" and a["completo"] and "se usó Sur" in a["nota"]


def test_los_tramos_salen_del_nomenclator_o_de_vias_csv(con):
    con.execute("INSERT INTO lugares(nombre, alias, tipo, lat, lon, osm_u, osm_v) "
                "VALUES ('vía de prueba', 'via de prueba', 'via', 5.07, -75.50, 1, 2)")
    con.execute("INSERT INTO lugares(nombre, alias, tipo, lat, lon, osm_u, osm_v) "
                "VALUES ('vía de prueba', 'la de prueba', 'via', 5.07, -75.50, 1, 2)")
    con.commit()
    assert [t["tramo"] for t in a25.tramos(con)] == ["vía de prueba"]
    desde_csv = a25.tramos(None)
    assert {"avenida Kevin Ángel", "salida a Letras"} <= {t["tramo"] for t in desde_csv}


def test_estaciones_publicas_con_fuente():
    est = a25.leer_estaciones()
    assert len(est) == 14 and len({e.id for e in est}) == 14
    assert all(5.0 < e.lat < 5.12 and -75.56 < e.lon < -75.45 for e in est)      # casco de Manizales
    with open(a25.RAIZ / "datos_publicos" / "estaciones_a25_fuentes.csv", encoding="utf-8") as f:
        fuentes = {r["id"]: r for r in csv.DictReader(f)}
    assert set(fuentes) == {e.id for e in est}
    assert all("boletin145.pdf" in r["fuente_url"] and r["verificado"] for r in fuentes.values())


def test_lector_marca_la_lluvia_sintetica(tmp_path):
    sint = tmp_path / "s.csv"
    sint.write_text("# LLUVIA SINTÉTICA de prueba\nestacion,fecha,lluvia_mm_sintetica\n"
                    "Chec-Uribe,2026-11-21,3.5\nposgrados,2026-11-21,\nNo Existe,2026-11-21,1\n"
                    "emas,2026-11-21,abc\n", encoding="utf-8")
    l = a25.leer_lluvia(sint)
    assert l.sintetica
    assert l.series["chec_uribe"][DIA] == 3.5                  # por el nombre del reporte de 2020
    assert l.series["posgrados"][DIA] is None and l.series["emas"][DIA] is None
    assert any("No Existe" in a for a in l.avisos) and any("abc" in a for a in l.avisos)
    real = tmp_path / "r.csv"
    real.write_text("estacion,fecha,lluvia_mm\nemas,2026-11-21,2.0\n", encoding="utf-8")
    assert not a25.leer_lluvia(real).sintetica
    malo = tmp_path / "m.csv"
    malo.write_text("estacion,dia,mm\nemas,2026-11-21,2\n", encoding="utf-8")
    with pytest.raises(ValueError):
        a25.leer_lluvia(malo)


def test_la_serie_de_la_demo_es_sintetica_y_muestra_los_cuatro_niveles():
    texto = a25.RUTA_LLUVIA_DEMO.read_text(encoding="utf-8")
    assert texto.startswith("# LLUVIA SINTÉTICA") and "lluvia_mm_sintetica" in texto.splitlines()[1]
    l = a25.leer_lluvia(a25.RUTA_LLUVIA_DEMO)
    assert l.sintetica and not l.avisos and len(l.series) == 14
    niveles = {e["nivel"] for e in a25.alertas_estaciones(DIA, l)}
    assert niveles == {"sin_alerta", "amarilla", "naranja", "roja"}
    assert all(e["completo"] for e in a25.alertas_estaciones(date(2026, 11, 30), l))


def test_resumen_para_el_tablero_es_json_y_avisa_lo_sintetico():
    r = a25.resumen_a25(None, DIA)
    json.dumps(r, ensure_ascii=False)
    assert r["lluvia"] == "sintética" and "SINTÉTICA" in r["aviso"]
    assert sum(r["conteo"].values()) == len(r["tramos"]) and len(r["estaciones"]) == 14
    assert r["umbrales_mm"] == {"amarilla": 200.0, "naranja": 300.0, "roja": 400.0}
    assert r["frase"].startswith(f"{len(r['tramos'])} tramos")


def test_historial_de_cierres_por_ladera():
    h = a25.historial_ladera()
    assert h["avenida Kevin Ángel"] == 2 and h["Panamericana"] == 2 and h["salida a Letras"] > 50
    assert "avenida Santander" not in h


def test_cli_dice_que_la_lluvia_es_sintetica(capsys):
    assert a25.main(["--fecha", "2026-11-21"]) == 0
    salida = capsys.readouterr()
    assert "LLUVIA SINTÉTICA" in salida.out and "LLUVIA SINTÉTICA" in salida.err
    assert "avenida Kevin Ángel" in salida.out
    assert a25.main(["--fecha", "2026-11-21", "--csv"]) == 0
    filas = list(csv.DictReader(capsys.readouterr().out.splitlines()))
    assert filas and all(f["lluvia"] == "sintética" for f in filas)


# ---------------------------------------------------------------- gancho en la matriz

def test_matriz_sin_riesgo_es_la_de_siempre(grafo):
    lugares = [matriz.Lugar(f"n{n}", *coords(grafo, n)) for n in (0, 4, 12, 24)]
    base = matriz.calcular(grafo, lugares)
    for riesgo in (None, {}, {(999, 998): 4.0}, {(0, 1): 1.0}):
        otra = matriz.calcular(grafo, lugares, riesgo=riesgo)
        for t in matriz.TIPOS:
            assert (otra[t].segundos == base[t].segundos).all() and otra[t].costo is None


def test_matriz_encarece_y_conserva_el_tiempo_real(grafo):
    lugares = [matriz.Lugar("a", *coords(grafo, nodo(0, 0))), matriz.Lugar("b", *coords(grafo, nodo(0, 4)))]
    base = matriz.calcular(grafo, lugares, tipos=("campero",))["campero"]
    arista = (nodo(0, 1), nodo(0, 2))
    assert arista in zip(base.camino("a", "b")[:-1], base.camino("a", "b")[1:])
    t_arista = grafo[arista[0]][arista[1]][0]["travel_time"]
    # Factor alto: el camino se desvía, el tiempo real sube y el costo es ese mismo tiempo.
    alto = matriz.calcular(grafo, lugares, tipos=("campero",), riesgo={arista: 10.0, arista[::-1]: 10.0})["campero"]
    camino = alto.camino("a", "b")
    assert arista not in zip(camino[:-1], camino[1:])
    assert alto.tiempo("a", "b") > base.tiempo("a", "b")
    assert alto.costo[0, 1] == alto.segundos[0, 1]
    # Factor bajo: no vale la pena desviarse; se paga el costo y el tiempo real no cambia.
    bajo = matriz.calcular(grafo, lugares, tipos=("campero",), riesgo={arista: 1.2})["campero"]
    assert bajo.tiempo("a", "b") == base.tiempo("a", "b")
    assert bajo.costo[0, 1] == pytest.approx(base.segundos[0, 1] + 0.2 * t_arista, abs=1)


# ---------------------------------------------------------------- gancho en el optimizador

def plan(con, pid):
    p = con.execute("SELECT * FROM planes WHERE id=?", (pid,)).fetchone()
    return json.loads(p["resumen"])


def paradas(con, pid):
    return [(r["vehiculo_id"], r["orden"], r["punto_id"], r["pedido_id"], r["llegada_estimada"], r["kg"],
             r["geometria"])
            for r in con.execute("SELECT * FROM paradas WHERE plan_id=? ORDER BY vehiculo_id, orden", (pid,))]


def usa_arista(con, pid, grafo, u, v):
    a, b = coords(grafo, u), coords(grafo, v)
    for r in con.execute("SELECT geometria FROM paradas WHERE plan_id=?", (pid,)):
        geo = [tuple(p) for p in json.loads(r["geometria"])]
        for p, q in zip(geo[:-1], geo[1:]):
            if {p, q} == {tuple(round(x, 6) for x in a), tuple(round(x, 6) for x in b)}:
                return True
    return False


def corredor(grafo, *aristas):
    salida = []
    for u, v in aristas:
        (la, lo), (lb, lob) = coords(grafo, u), coords(grafo, v)
        salida.append((u, v, (la + lb) / 2, (lo + lob) / 2, grafo[u][v][0]["length"]))
    return {"vía de prueba": salida}


@pytest.fixture
def lluvia_roja(monkeypatch, grafo):
    """El gancho ve una estación en roja (425 mm) en el centro de la malla y una vía de prueba."""
    estacion = [a25.Estacion("centro", "Centro de prueba", *coords(grafo, nodo(2, 2)))]
    lluvia = lluvia_de({"centro": serie_constante(17.0, dias=40)})
    real = a25.riesgo_corredores

    def poner(*aristas):
        monkeypatch.setattr(a25, "riesgo_corredores", lambda g, fecha: real(
            g, fecha, lluvia=lluvia, estaciones=estacion, lista=corredor(grafo, *aristas),
            historial={"vía de prueba": 1}))
    return poner


def test_gancho_apagado_no_cambia_el_plan(mundo, con, grafo, ahora, monkeypatch, lluvia_roja):
    mundo.punto(5, nodo(0, 4))
    mundo.pedido(1, 5, 30)
    mundo.pedido(2, 3, 20)
    mundo.listo()
    monkeypatch.delenv("DESPACHOX_A25", raising=False)
    p0 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    lluvia_roja((nodo(0, 1), nodo(0, 2)))                      # hay alerta roja, pero el gancho está apagado
    p1 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    p2 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora, a25=False)
    assert paradas(con, p0) == paradas(con, p1) == paradas(con, p2)
    for pid in (p0, p1, p2):
        r = plan(con, pid)
        assert "a25" not in r and "a25_factor_costo" not in r["supuestos"]
    assert optimizar._riesgo_a25(grafo, ahora, False) == (None, [])


def test_gancho_encendido_evita_la_via_en_roja_si_hay_desvio(mundo, con, grafo, ahora, lluvia_roja):
    mundo.punto(5, nodo(0, 4))
    mundo.pedido(1, 5, 30)
    mundo.listo()
    arista = (nodo(0, 1), nodo(0, 2))
    p0 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora, a25=False)
    assert usa_arista(con, p0, grafo, *arista)                  # sin gancho va derecho por la fila 0
    lluvia_roja(arista)
    p1 = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora, a25=True)
    r = plan(con, p1)
    assert r["pedidos_atendidos"] == 1 and not usa_arista(con, p1, grafo, *arista)
    assert r["a25"]["activo"] and r["a25"]["lluvia"] == "sintética"
    assert r["a25"]["vias_encarecidas"][0]["nivel"] == "roja"
    assert r["supuestos"]["a25_factor_costo"] == a25.FACTOR_RIESGO
    # El tiempo de llegada es el del desvío real, sin el factor.
    llegada = paradas(con, p1)[0][4]
    assert llegada > paradas(con, p0)[0][4]


def test_gancho_encarece_sin_prohibir(mundo, con, grafo, ahora, lluvia_roja):
    mundo.punto(9, AISLADO)                                    # solo se llega por el puente
    mundo.pedido(1, 9, 20)
    mundo.listo()
    lluvia_roja(PUENTE)
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora, a25=True)
    r = plan(con, pid)
    assert r["pedidos_atendidos"] == 1                          # el puente en roja no cierra la vía
    assert r["a25"]["km_en_alerta_recorridos"] > 0
    assert any("vía de prueba" in a and "despachador decide" in a for a in r["avisos"])


def test_gancho_sin_datos_de_lluvia_no_rompe_el_plan(mundo, con, grafo, ahora, monkeypatch, tmp_path):
    mundo.pedido(1, 1, 20)
    mundo.listo()
    monkeypatch.setenv("DESPACHOX_LLUVIA", str(tmp_path / "no_existe.csv"))
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora, a25=True)
    r = plan(con, pid)
    assert r["pedidos_atendidos"] == 1 and "a25" not in r
    assert any(a.startswith("A25: no se pudo calcular") for a in r["avisos"])


def test_variables_de_entorno_del_gancho(monkeypatch):
    monkeypatch.delenv("DESPACHOX_A25", raising=False)
    assert not a25.gancho_activo()
    monkeypatch.setenv("DESPACHOX_A25", "1")
    assert a25.gancho_activo()
    monkeypatch.setenv("DESPACHOX_A25_FACTOR", "naranja=1.5,roja=3,amarilla=0,x=9")
    assert a25.factores() == {"naranja": 1.5, "roja": 3.0, "amarilla": 1.0}     # nunca menor que 1
    monkeypatch.delenv("DESPACHOX_A25_FACTOR")
    assert a25.factores() == a25.FACTOR_RIESGO


def test_comparar_muestra_lo_que_cambia_sin_guardar_nada(mundo, con, grafo, ahora, lluvia_roja):
    mundo.punto(5, nodo(0, 4))
    mundo.pedido(1, 5, 30)
    mundo.listo()
    lluvia_roja((nodo(0, 1), nodo(0, 2)))
    r = a25.comparar(con, grafo, ahora.date(), segundos=SEG, ahora=ahora)
    assert r["lluvia"] == "sintética"
    assert r["apagado"]["km_en_alerta"]["roja"] > 0 and r["encendido"]["km_en_alerta"]["roja"] == 0
    assert r["apagado"]["pedidos_atendidos"] == r["encendido"]["pedidos_atendidos"] == 1
    assert r["encendido"]["duracion_rutas_min"] >= r["apagado"]["duracion_rutas_min"]
    assert con.execute("SELECT COUNT(*) FROM planes").fetchone()[0] == 0


def test_temporada_cuenta_los_dias_con_ladera_en_alerta(monkeypatch):
    lista = [{"tramo": "avenida Kevin Ángel", "lat": 5.0790, "lon": -75.5010, "osm_u": 1, "osm_v": 2},
             {"tramo": "avenida sin historial", "lat": 5.0420, "lon": -75.4990, "osm_u": 3, "osm_v": 4}]
    monkeypatch.setattr(a25, "tramos", lambda con: lista)
    # Norte: 16 mm durante los 25 días que terminan en DIA (400 mm, roja). El día antes falta el
    # primer día de su ventana y la cota inferior da 384 mm, naranja. Sur: 325 mm, naranja.
    lluvia = lluvia_de({"norte": serie_constante(16.0, dias=25), "sur": serie_constante(13.0, dias=40)})
    filas = a25.temporada(None, DIA - timedelta(days=1), DIA, lluvia, ESTACIONES)
    assert [f["fecha"] for f in filas] == [(DIA - timedelta(days=1)).isoformat(), DIA.isoformat()]
    assert (filas[0]["roja"], filas[0]["naranja"]) == (0, 2)
    assert (filas[1]["roja"], filas[1]["naranja"]) == (1, 1)
    assert filas[0]["ladera_en_alerta"] == ["avenida Kevin Ángel (naranja)"]   # la otra no tiene historial
    assert filas[1]["ladera_en_alerta"] == ["avenida Kevin Ángel (roja)"]
    assert all(f["lluvia"] == "sintética" for f in filas)
