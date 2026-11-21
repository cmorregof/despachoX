"""T1 · vista por territorio, con una base temporal y datos sintéticos."""
import csv
import json
from datetime import timedelta

import pytest

from despacho import territorio
from despacho.tests.conftest import AHORA, iso


@pytest.fixture
def base(con):
    """Tres comunas: Norte (un punto crítico y uno normal), Sur (sin pedidos) y un punto sin comuna."""
    for id, barrio, comuna, critico in [(1, "Alfa", "Norte", 1), (2, "Beta", "Norte", 0),
                                        (3, "Gama", "Sur", 0), (4, "Delta", None, 0)]:
        con.execute("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,5.06,-75.5,?)",
                    (id, f"Punto {barrio}", barrio, comuna, critico))
    for nombre, tipo in [("Alfa", "barrio"), ("Beta", "barrio"), ("Gama", "barrio"), ("Delta", "barrio"),
                         ("Vereda Inventada", "vereda")]:
        for alias in (nombre.lower(), f"barrio {nombre.lower()}"):
            con.execute("INSERT INTO lugares(nombre,alias,tipo,lat,lon) VALUES (?,?,?,5.06,-75.5)",
                        (nombre, alias, tipo))

    def pedido(id, punto, horas_antes, estado, limite_h=None, kg=20, familias=2, duplicado=None):
        con.execute("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,"
                    "limite_en,estado,duplicado_de,texto_original,remitente_hash) VALUES (?,?,?,?,?,?,3,?,?,?,?,?)",
                    (id, iso(AHORA - timedelta(hours=horas_antes)), punto, familias, kg,
                     json.dumps([{"producto": "arroz", "kg": kg}]),
                     iso(AHORA - timedelta(hours=horas_antes - limite_h)) if limite_h else None,
                     estado, duplicado, "texto privado", "hash privado"))

    def entrega(codigo, pedido_id, horas_antes, kg=20):
        con.execute("INSERT INTO paquetes(codigo,pedido_id,kg,estado,entregado_en) VALUES (?,?,?,'entregado',?)",
                    (codigo, pedido_id, kg, iso(AHORA - timedelta(hours=horas_antes))))

    pedido(1, 1, 10, "entregado", limite_h=4)    # crítico: creado hace 10 h, límite hace 6 h
    entrega("DX-AAAA", 1, 7)                       # entregado hace 7 h: a tiempo (3 h de espera)
    pedido(2, 1, 9, "entregado", limite_h=4)     # crítico: límite hace 5 h
    entrega("DX-CCCC", 2, 3)                       # entregado hace 3 h: tarde (6 h de espera)
    pedido(3, 2, 8, "entregado")                  # sin limite_en: no entra al porcentaje
    entrega("DX-DDDD", 3, 4, kg=15)
    pedido(4, 2, 5, "confirmado")                 # abierto hace 5 h
    pedido(5, 2, 4, "nuevo", duplicado=4)        # duplicado: no cuenta
    pedido(6, 4, 2, "asignado")                   # punto sin comuna
    pedido(7, 3, 30, "descartado")                # descartado: no cuenta
    con.commit()
    return con


def fila(filas, t):
    return next(f for f in filas if f["territorio"] == t)


def test_resumen_por_comuna(base):
    filas = territorio.resumen(base, ahora=AHORA)
    assert [f["territorio"] for f in filas] == ["Norte", "Sur", "sin comuna"]
    n = fila(filas, "Norte")
    assert (n["puntos"], n["puntos_criticos"], n["pedidos"], n["familias"]) == (2, 1, 4, 8)
    assert n["kg_pedidos"] == 80 and n["entregados"] == 3 and n["kg_entregados"] == 55
    assert (n["a_tiempo"], n["pct_a_tiempo"]) == (1, 50.0)          # el pedido sin límite no cuenta
    assert (n["criticos_a_tiempo"], n["pct_criticos_a_tiempo"]) == (1, 50.0)
    assert n["espera_mediana_h"] == 4.0                              # 3, 4 y 6 h
    assert n["pendiente_mas_viejo_h"] == 5.0
    s = fila(filas, "Sur")                                           # comuna sin pedidos que cuenten
    assert s["pedidos"] == 0 and s["pct_a_tiempo"] is None and s["pendiente_mas_viejo_h"] is None
    sc = fila(filas, "sin comuna")
    assert sc["pedidos"] == 1 and sc["pendiente_mas_viejo_h"] == 2.0


def test_periodo_filtra_por_creacion(base):
    filas = territorio.resumen(base, desde=AHORA - timedelta(hours=6), ahora=AHORA)
    assert fila(filas, "Norte")["pedidos"] == 1                      # solo el pedido 4


def test_silencio_lista_barrios_y_veredas_sin_pedidos(base):
    callados = territorio.silencio(base)
    assert [(c["nombre"], c["tipo"]) for c in callados] == [("Gama", "barrio"), ("Vereda Inventada", "vereda")]
    assert callados[0]["comuna"] == "Sur"                            # el descartado de Gama no cuenta


def test_alerta_por_silencio_no_cuenta_como_pedido(base):
    base.execute("INSERT INTO pedidos(id,creado_en,punto_id,urgencia,estado,origen) "
                 "VALUES (9,?,3,3,'confirmado','silencio')", (iso(AHORA),))
    base.commit()
    assert fila(territorio.resumen(base, ahora=AHORA), "Sur")["pedidos"] == 0
    assert "Gama" in [c["nombre"] for c in territorio.silencio(base)]


def test_linea_de_ordenes_y_csv_sin_datos_personales(base, tmp_path, monkeypatch, capsys):
    from datos import db
    ruta = base.execute("PRAGMA database_list").fetchone()["file"]
    monkeypatch.setattr(db.conectar, "__defaults__", (ruta,))
    salida = tmp_path / "territorio.csv"
    assert territorio.main(["--csv", str(salida)]) == 0
    texto = capsys.readouterr().out
    assert "Norte" in texto and "sin pedidos registrados: 2" in texto
    assert "privado" not in texto
    with salida.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert [f["territorio"] for f in filas] == ["Norte", "Sur", "sin comuna"]
    assert "privado" not in salida.read_text(encoding="utf-8")
    assert (tmp_path / "territorio_sin_pedidos.csv").exists()
