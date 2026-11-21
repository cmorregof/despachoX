"""Vista por territorio (encargos/T1_TERRITORIO.md, parte B), con una base temporal y datos sintéticos."""
import csv
import json
from datetime import datetime, timedelta

import pytest

from datos import db
from despacho import territorio

H0 = datetime(2026, 11, 21, 6, 0, tzinfo=db.BOGOTA)
AHORA = H0 + timedelta(hours=10)                      # 16:00


def iso(horas):
    return (H0 + timedelta(hours=horas)).isoformat(timespec="seconds")


@pytest.fixture
def base(con):
    puntos = [  # id, nombre, barrio, comuna, crítico
        (1, "Albergue Norte", "Norte Alto", "Comuna Inventada Norte", 1),
        (2, "Comedor Norte", "Norte Bajo", "Comuna Inventada Norte", 0),
        (3, "Salón Sur", "Sur", "Comuna Inventada Sur", 0),            # comuna sin pedidos que cuenten
        (4, "Punto de entrega Finca X", "Finca X", None, 0),            # sin comuna y barrio desconocido
        (5, "Punto de entrega La Enea", "La Enea", None, 0),            # sin comuna; su barrio la trae
        (6, "Salón JAC vereda La Aurora", None, None, 0),                # rural, sin barrio
    ]
    con.executemany("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,5.06,-75.5,?)",
                    puntos)

    def pedido(id, punto, creado_h, limite_h=None, estado="confirmado", familias=10, kg=100.0,
               duplicado_de=None, origen="mensaje", entregado_h=None, kg_entregado=None):
        con.execute("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,limite_en,"
                    "estado,duplicado_de,texto_original,remitente_hash,origen) VALUES (?,?,?,?,?,?,2,?,?,?,?,?,?)",
                    (id, iso(creado_h), punto, familias, kg, None, iso(limite_h) if limite_h is not None else None,
                     estado, duplicado_de, "texto que no debe salir", "hash que no debe salir", origen))
        if entregado_h is not None:
            con.execute("INSERT INTO paquetes(codigo,pedido_id,kg,estado,entregado_en) VALUES (?,?,?,'entregado',?)",
                        (f"DX-{id:04d}", id, kg if kg_entregado is None else kg_entregado, iso(entregado_h)))

    pedido(1, 1, 4, limite_h=7, estado="entregado", entregado_h=6)               # crítico, a tiempo, 2 h
    pedido(2, 1, 3, limite_h=5, estado="entregado", entregado_h=9, kg_entregado=80)   # crítico, tarde, 6 h
    pedido(3, 1, 4, limite_h=7, duplicado_de=1)                                  # duplicado: no cuenta
    pedido(4, 2, 2, limite_h=None, estado="entregado", entregado_h=3)            # sin límite: fuera del %
    pedido(5, 2, 1, limite_h=8, estado="confirmado")                             # abierto y ya vencido
    pedido(6, 4, 9, limite_h=20, estado="asignado", familias=None, kg=None)      # sin comuna, en plazo
    pedido(7, 3, 2, limite_h=4, estado="descartado")                             # descartado: no cuenta
    pedido(8, 3, 2, origen="silencio", familias=None, kg=None)                   # alerta: no es pedido
    pedido(9, 5, 5, limite_h=9, estado="confirmado")                             # La Enea -> Tesorito
    pedido(10, 6, 5, limite_h=20, estado="nuevo")                                # vereda La Aurora
    con.executemany("INSERT INTO lugares(nombre,alias,tipo,lat,lon,punto_id) VALUES (?,?,?,5.06,-75.5,?)", [
        ("Norte Alto", "norte alto", "barrio", 1),
        ("Norte Bajo", "norte bajo", "barrio", None),       # tiene pedidos por el barrio del punto 2
        ("20 de Julio", "20 de julio", "barrio", None),     # callado; su comuna sale de barrios.csv
        ("20 de Julio", "veinte de julio", "barrio", None),  # otro apodo: no se repite
        ("La Aurora", "la aurora", "vereda", None),         # tiene pedidos por el nombre del punto 6
        ("El Guineo", "el guineo", "vereda", None),         # callada
        ("Sur", "sur", "barrio", 3),                        # solo descartados y alertas: callado
    ])
    con.commit()
    return con


def fila(tabla, territorio_):
    return next(f for f in tabla if f["territorio"] == territorio_)


def test_resumen_por_comuna(base):
    tabla = territorio.resumen(base, ahora=AHORA)
    assert all(list(f) == list(territorio.COLUMNAS) for f in tabla)
    norte = fila(tabla, "Comuna Inventada Norte")
    assert {k: norte[k] for k in ("puntos", "puntos_criticos", "pedidos", "familias", "kg_pedidos", "entregados",
                                  "kg_entregados")} == {
        "puntos": 2, "puntos_criticos": 1, "pedidos": 4, "familias": 40, "kg_pedidos": 400.0,
        "entregados": 3, "kg_entregados": 280.0}
    # Evaluados: el 1 (a tiempo), el 2 (tarde) y el 5 (abierto con el límite vencido). El 4 no tiene límite.
    assert (norte["a_tiempo"], norte["evaluados"], norte["pct_a_tiempo"]) == (1, 3, 33.3)
    assert (norte["criticos_a_tiempo"], norte["criticos_evaluados"], norte["pct_criticos_a_tiempo"]) == (1, 2, 50.0)
    assert norte["espera_mediana_h"] == 2.0                  # esperas de 2, 6 y 1 h
    assert norte["pendiente_mas_viejo_h"] == 9.0             # el 5, creado a las 7:00, a las 16:00


def test_comuna_sin_pedidos_y_sin_comuna(base):
    tabla = territorio.resumen(base, ahora=AHORA)
    sur = fila(tabla, "Comuna Inventada Sur")
    assert sur["pedidos"] == 0 and sur["puntos"] == 0 and sur["pct_a_tiempo"] is None
    assert sur["pendiente_mas_viejo_h"] is None              # el descartado y la alerta no cuentan
    sin = fila(tabla, territorio.SIN_COMUNA)
    assert tabla[-1] is sin                                  # «sin comuna» va al final
    assert (sin["puntos"], sin["pedidos"], sin["evaluados"]) == (2, 2, 0)   # Finca X y la vereda, en plazo
    assert sin["familias"] == 10 and sin["kg_pedidos"] == 100.0             # el pedido sin kilos no inventa
    assert fila(tabla, "Tesorito")["pedidos"] == 1           # La Enea: comuna por su barrio
    assert fila(tabla, "Nuevo Horizonte")["pedidos"] == 0    # comunas de barrios.csv sin puntos también salen


def test_periodo_y_sin_datos_personales(base):
    tabla = territorio.resumen(base, desde=iso(3.5), hasta=iso(8), ahora=AHORA)
    norte = fila(tabla, "Comuna Inventada Norte")
    assert norte["pedidos"] == 1 and norte["a_tiempo"] == 1   # solo el 1, creado a las 10:00
    texto = json.dumps(territorio.resumen(base, ahora=AHORA) + territorio.silencio(base), ensure_ascii=False)
    assert "no debe salir" not in texto


def test_silencio_lista_barrios_y_veredas_sin_pedidos(base):
    callados = territorio.silencio(base)
    assert [(s["nombre"], s["tipo"], s["comuna"]) for s in callados] == [
        ("Sur", "barrio", "Comuna Inventada Sur"),         # comuna por su punto
        ("20 de Julio", "barrio", "La Macarena"),          # comuna por barrios.csv
        ("El Guineo", "vereda", None)]
    assert all(s["estado"] == "sin pedidos registrados" for s in callados)
    assert all("necesidad" not in s["estado"] for s in callados)
    assert callados[-1]["comuna"] is None
    # Con un periodo sin pedidos, todo el nomenclátor de barrios y veredas queda sin pedidos registrados.
    assert len(territorio.silencio(base, desde=iso(30))) == 6


def test_linea_de_ordenes_sobre_la_semilla(con, tmp_path, monkeypatch, capsys):
    from despacho import semilla
    semilla.cargar(reiniciar=True, con=con)
    ruta = con.execute("PRAGMA database_list").fetchone()["file"]
    monkeypatch.setattr(db.conectar, "__defaults__", (ruta,))
    salida = tmp_path / "territorio.csv"
    assert territorio.main(["--csv", str(salida)]) == 0
    impreso = capsys.readouterr().out
    assert "Resumen por territorio" in impreso and "sin pedidos registrados" in impreso
    with open(salida, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert list(filas[0]) == list(territorio.COLUMNAS)
    assert sum(int(f["pedidos"]) for f in filas) == 20       # los 20 pedidos de la semilla
    with open(tmp_path / "territorio_sin_pedidos.csv", encoding="utf-8") as f:
        assert list(csv.DictReader(f))[0]["estado"] == "sin pedidos registrados"
