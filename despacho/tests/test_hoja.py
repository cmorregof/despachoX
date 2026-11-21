"""Encargo B3: hoja de ruta impresa con un QR por paquete, sin red."""
import socket
from pathlib import Path

import pytest

from datos import db
from despacho import hoja, optimizar, red
from despacho.tests.conftest import nodo

SEG = 1


def _plan_aprobado(mundo, con, grafo, ahora, cierre=False):
    for i, kg in enumerate([30, 20, 25, 15], start=1):
        mundo.pedido(i, i, kg, urgencia=3 if i == 1 else 2)
    con.execute("UPDATE puntos SET critico=1 WHERE id=1")
    if cierre:
        mundo.cierre(u=nodo(2, 1), v=nodo(2, 2))
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    assert optimizar.aprobar(con, pid, "despachador de prueba")
    return pid


def _codigos_por_vehiculo(con, pid):
    por = {}
    for r in con.execute("SELECT pa.vehiculo_id, pq.codigo FROM paradas pa JOIN paquetes pq "
                         "ON pq.pedido_id = pa.pedido_id WHERE pa.plan_id=?", (pid,)):
        por.setdefault(r["vehiculo_id"], set()).add(r["codigo"])
    return por


def _paginas(ruta):
    pdfium = pytest.importorskip("pypdfium2")
    doc = pdfium.PdfDocument(str(ruta))
    return [doc[i] for i in range(len(doc))]


def test_un_pdf_por_vehiculo_y_cada_qr_decodifica_a_su_paquete(mundo, con, grafo, ahora, tmp_path):
    zxingcpp = pytest.importorskip("zxingcpp")
    pid = _plan_aprobado(mundo, con, grafo, ahora)
    rutas = hoja.generar(con, pid, tmp_path, g=grafo)
    esperados = _codigos_por_vehiculo(con, pid)
    assert len(rutas) == len(esperados) >= 1
    leidos_total = set()
    for ruta in rutas:
        assert ruta.read_bytes().startswith(b"%PDF")
        leidos = set()
        for pagina in _paginas(ruta):
            leidos |= {b.text for b in zxingcpp.read_barcodes(pagina.render(scale=200 / 72).to_pil())}
        assert leidos in esperados.values(), f"{ruta.name}: {leidos}"
        leidos_total |= leidos
    # Una parada, un QR, y cada QR es un código guardado en `paquetes` con estado en_ruta.
    paradas = con.execute("SELECT COUNT(*) FROM paradas WHERE plan_id=?", (pid,)).fetchone()[0]
    assert len(leidos_total) == paradas == 4
    en_ruta = {r[0] for r in con.execute("SELECT codigo FROM paquetes WHERE estado='en_ruta'")}
    assert leidos_total == en_ruta


def test_la_hoja_dice_lo_que_el_conductor_necesita(mundo, con, grafo, ahora, tmp_path):
    pid = _plan_aprobado(mundo, con, grafo, ahora, cierre=True)
    texto = ""
    for ruta in hoja.generar(con, pid, tmp_path, g=grafo):
        texto += " ".join(p.get_textpage().get_text_range() for p in _paginas(ruta))
    assert "Punto 1" in texto and "SÍ" in texto                 # el punto crítico
    assert "arroz 30 kg" in texto
    assert "Cierre 1" in texto                                  # tramo cerrado que la ruta evita
    assert "ENTREGADO DX-XXXX" in texto and "vía cerrada" in texto
    assert "Conductor" in texto and "firma" in texto


def test_sin_ninguna_llamada_de_red(mundo, con, grafo, ahora, tmp_path, monkeypatch):
    pid = _plan_aprobado(mundo, con, grafo, ahora)

    def prohibido(*a, **k):
        raise AssertionError("la hoja de ruta intentó usar la red")

    monkeypatch.setattr(socket.socket, "connect", prohibido)
    monkeypatch.setattr(socket.socket, "connect_ex", prohibido)
    monkeypatch.setattr(socket, "create_connection", prohibido)
    monkeypatch.setattr(socket, "getaddrinfo", prohibido)
    monkeypatch.setattr(red, "descargar", prohibido)
    with pytest.raises(AssertionError):                        # la trampa funciona
        socket.create_connection(("example.org", 80))
    # Con la red vial dada, y sin red vial en disco: en ningún caso se descarga nada.
    assert hoja.generar(con, pid, tmp_path / "con_grafo", g=grafo)
    monkeypatch.setattr(red, "RUTA_GRAFO", tmp_path / "no_existe.graphml")
    monkeypatch.setattr(red, "RUTA_PICKLE", tmp_path / "no_existe.pkl")
    assert hoja.grafo_local() is None
    assert hoja.generar(con, pid, tmp_path / "sin_grafo")


def test_solo_se_imprimen_planes_aprobados(mundo, con, grafo, ahora, tmp_path):
    mundo.pedido(1, 1, 10)
    mundo.listo()
    pid = optimizar.planificar(con, segundos=SEG, g=grafo, ahora=ahora)
    with pytest.raises(ValueError, match="aprobad"):
        hoja.generar(con, pid, tmp_path, g=grafo)
    with pytest.raises(ValueError, match="no hay un plan aprobado"):
        hoja.generar(con, None, tmp_path, g=grafo)


def test_queda_en_la_bitacora_y_toma_el_plan_vigente(mundo, con, grafo, ahora, tmp_path):
    pid = _plan_aprobado(mundo, con, grafo, ahora)
    rutas = hoja.generar(con, None, tmp_path, g=grafo, quien="Carlos")
    assert all(r.name.startswith(f"plan{pid}_") for r in rutas)
    b = con.execute("SELECT quien, detalle FROM bitacora WHERE accion='imprimir hojas de ruta'").fetchone()
    assert b["quien"] == "Carlos" and f"plan {pid}" in b["detalle"] and "4 paquetes" in b["detalle"]


def test_muchas_paradas_siguen_en_otra_hoja():
    datos = {"plan": {"id": 9, "aprobado_por": "x", "aprobado_en": None}, "resumen": {}}
    v = {"nombre": "Camión 1", "tipo": "camion", "capacidad_kg": 5000, "acopio": "Acopio 1",
         "acopio_lat": None, "acopio_lon": None, "regreso": [], "duracion_s": None, "cierres": [],
         "paradas": [{"orden": i, "punto": f"Punto {i}", "barrio": "", "critico": False, "lat": None,
                      "lon": None, "llegada": "10:00", "kg": 5, "pedido_id": i, "entrega": "arroz 5 kg",
                      "supuesta": None, "codigo": f"DX-AA{i:02d}", "estado": "en_ruta", "geometria": []}
                     for i in range(1, 13)]}
    assert hoja._pdf_vehiculo(datos, v, None).pages_count == 2
    v["paradas"] = v["paradas"][:5]
    assert hoja._pdf_vehiculo(datos, v, None).pages_count == 1


def test_linea_de_ordenes(mundo, con, grafo, ahora, tmp_path, monkeypatch, capsys):
    pid = _plan_aprobado(mundo, con, grafo, ahora)
    ruta_db = con.execute("PRAGMA database_list").fetchone()["file"]
    abrir = db.conectar
    monkeypatch.setattr(db, "conectar", lambda: abrir(Path(ruta_db)))
    monkeypatch.setattr(hoja, "grafo_local", lambda: grafo)
    assert hoja.main(["--plan", str(pid), "--salida", str(tmp_path)]) == 0
    assert capsys.readouterr().out.count(".pdf") >= 1
    assert hoja.main(["--plan", "999", "--salida", str(tmp_path)]) == 1



# ---------- arranque sin red (DESPACHOX_SIN_RED=1) ----------

def test_sin_red_la_red_vial_no_intenta_descargarse(monkeypatch, tmp_path):
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")
    monkeypatch.setattr(red, "RUTA_GRAFO", tmp_path / "no_existe.graphml")
    monkeypatch.setattr(red.ox, "graph_from_place",
                        lambda *a, **k: pytest.fail("intentó bajar el grafo sin red"))
    with pytest.raises(RuntimeError, match="DESPACHOX_SIN_RED"):
        red.descargar()


def test_sin_red_el_ubicador_no_llama_al_modelo(monkeypatch):
    import sys
    import types

    from lugares import nomenclator
    llamadas = []
    falso = types.SimpleNamespace(Anthropic=lambda *a, **k: llamadas.append(1))
    monkeypatch.setitem(sys.modules, "anthropic", falso)
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")
    candidatos = [nomenclator.Candidato(1, "La Enea", "barrio", 5.0, -75.5, 0.8, None, None, None)]
    assert nomenclator.elegir_con_modelo("la enea", "", candidatos) is None
    assert llamadas == []
