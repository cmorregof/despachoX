import json

import pytest

from triage import entrada_datos as ed

SAL = b"sal-de-prueba"


def _escribir(tmp_path, nombre, texto, codificacion="utf-8"):
    ruta = tmp_path / nombre
    ruta.write_bytes(texto.encode(codificacion))
    return ruta


def test_csv_basico_con_alias_y_hash(tmp_path):
    ruta = _escribir(tmp_path, "s.csv",
                     "Fecha,Telefono,Mensaje,Latitud,Longitud,Familias,productos,lugar_confirmado\n"
                     "2026-11-20T10:00:00,tel-sintetico-1,Necesitamos agua,5.06,-75.5,4,\"arroz,agua\",sí\n")
    filas, errores = ed.leer(ruta, sal=SAL)
    assert errores == []
    f = filas[0]
    assert f["recibida_en"] == "2026-11-20T10:00:00-05:00"
    assert f["remitente_hash"] != "tel-sintetico-1" and len(f["remitente_hash"]) == 32
    assert "tel-sintetico-1" not in json.dumps(f)
    assert f["productos"] == ["arroz", "agua"] and f["familias"] == 4
    assert f["lugar_confirmado"] is True and f["canal"] == "chat"


def test_hash_ya_calculado_se_conserva():
    h = "ab" * 32
    assert ed.hash_remitente(h, SAL) == h
    assert ed.hash_remitente("tel-sintetico-1", SAL) == ed.hash_remitente("tel-sintetico-1", SAL)
    assert ed.hash_remitente("tel-sintetico-1", SAL) != ed.hash_remitente("tel-sintetico-1", b"otra")


def test_csv_vacio(tmp_path):
    filas, errores = ed.leer(_escribir(tmp_path, "v.csv", ""), sal=SAL)
    assert filas == [] and errores[0]["motivo"] == "archivo_vacio"
    filas, errores = ed.leer(_escribir(tmp_path, "h.csv", "fecha,remitente\n"), sal=SAL)
    assert filas == [] and errores


def test_columnas_desconocidas(tmp_path):
    ruta = _escribir(tmp_path, "c.csv", "fecha,remitente,color,zapato\n2026-11-20 10:00,u1,rojo,1\n")
    filas, errores = ed.leer(ruta, sal=SAL)
    assert len(filas) == 1
    assert {e["campo"] for e in errores if e["motivo"] == "columna_desconocida"} == {"color", "zapato"}


def test_separador_punto_y_coma_y_latin1(tmp_path):
    texto = ("fecha;remitente;mensaje;lat;lon\n"
             "20/11/2026 10:30;u1;Necesitamos atención en el puente, niños sin comida;5,06;-75,5\n")
    ruta = _escribir(tmp_path, "l.csv", texto, "latin-1")
    filas, errores = ed.leer(ruta, sal=SAL)
    assert errores == []
    assert filas[0]["texto"].startswith("Necesitamos atención")
    assert filas[0]["lat"] == 5.06 and filas[0]["lon"] == -75.5
    assert filas[0]["recibida_en"] == "2026-11-20T10:30:00-05:00"


def test_bom_utf8(tmp_path):
    ruta = tmp_path / "b.csv"
    ruta.write_bytes("﻿fecha,remitente\n2026-11-20 10:00,u1\n".encode("utf-8"))
    filas, errores = ed.leer(ruta, sal=SAL)
    assert len(filas) == 1 and errores == []


def test_fechas_invalidas_y_zonas_horarias(tmp_path):
    ruta = _escribir(tmp_path, "f.csv",
                     "fecha,remitente\nayer,u1\n31/02/2026 10:00,u2\n2026-11-20T15:00:00Z,u3\n,u4\n")
    filas, errores = ed.leer(ruta, sal=SAL)
    assert len(filas) == 1 and filas[0]["recibida_en"] == "2026-11-20T10:00:00-05:00"
    rechazadas = [e for e in errores if e["rechazada"]]
    assert {e["fila"] for e in rechazadas} == {1, 2, 4}


def test_coordenadas_cero_familias_raras_y_sin_remitente(tmp_path):
    ruta = _escribir(tmp_path, "r.csv",
                     "fecha,remitente,lat,lon,familias\n"
                     "2026-11-20 10:00,u1,0,0,muchas\n"
                     "2026-11-20 10:00,,5.06,-75.5,3\n"
                     "2026-11-20 10:00,u3,abc,-75.5,-4\n")
    filas, errores = ed.leer(ruta, sal=SAL)
    assert len(filas) == 2
    assert filas[0]["lat"] == 0.0 and filas[0]["familias"] is None
    assert filas[1]["lat"] is None and filas[1]["familias"] is None
    assert any(e["campo"] == "remitente" and e["rechazada"] for e in errores)
    assert any(e["campo"] == "familias" for e in errores)


def test_json_lista_y_no_lista(tmp_path):
    ruta = _escribir(tmp_path, "a.json", json.dumps([
        {"timestamp": "2026-11-20T10:00:00", "chat_id": 99, "texto": "hola 🙏", "productos": ["Arroz"]},
        "basura", {"fecha": "x"}]))
    filas, errores = ed.leer(ruta, sal=SAL)
    assert len(filas) == 1 and filas[0]["texto"] == "hola 🙏" and filas[0]["productos"] == ["arroz"]
    assert len([e for e in errores if e["rechazada"]]) >= 2
    filas, errores = ed.leer(_escribir(tmp_path, "o.json", '{"a": 1}'), sal=SAL)
    assert filas == [] and errores[0]["motivo"] == "json_no_es_lista"
    filas, errores = ed.leer(_escribir(tmp_path, "m.json", "[{malo"), sal=SAL)
    assert filas == [] and errores[0]["motivo"].startswith("json_invalido")


def test_archivo_inexistente_da_mensaje_claro(tmp_path):
    with pytest.raises(FileNotFoundError, match="No existe"):
        ed.leer(tmp_path / "no_esta.csv", sal=SAL)


def test_canal_y_booleanos():
    f, e = ed.normalizar_fila({"fecha": "2026-11-20 10:00", "remitente": "u", "canal": "paloma",
                               "lugar_confirmado": "quizas"}, 1, SAL)
    assert f["canal"] == "chat" and f["lugar_confirmado"] is False and len(e) == 2
    f, _ = ed.normalizar_fila({"fecha": "2026-11-20 10:00", "remitente": "u", "canal": "Manual",
                               "lugar_confirmado": "TRUE"}, 1, SAL)
    assert f["canal"] == "manual" and f["lugar_confirmado"] is True


def test_fecha_y_hora_separadas():
    f, _ = ed.normalizar_fila({"fecha": "20/11/2026", "hora": "08:15", "remitente": "u"}, 1, SAL)
    assert f["recibida_en"] == "2026-11-20T08:15:00-05:00"
