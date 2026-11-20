"""Carga de datos reales desde otra carpeta, con validación."""
import pytest

from datos import db
from despacho import semilla


@pytest.fixture
def con(tmp_path):
    return db.conectar(tmp_path / "t.db")


def escribir(carpeta, nombre, texto):
    (carpeta / nombre).write_text(texto, encoding="utf-8")


def test_semilla_sintetica_carga_completa(con):
    r = semilla.cargar(con=con)
    assert set(r["origen"].values()) == {"sintético"}
    assert r["filas"] == {"puntos": 15, "acopios": 2, "vehiculos": 5, "lotes": 34, "pedidos": 20}


def test_mezcla_real_y_sintetico_y_dice_cual_es_cual(con, tmp_path):
    escribir(tmp_path, "acopios.csv", "id,nombre,lat,lon\n1,Bodega A,5.0371,-75.4397\n2,Bodega B,5.0774,-75.5218\n")
    escribir(tmp_path, "vehiculos.csv", "id,tipo,capacidad_kg,acopio_id\n1,camion,4500,1\n2,campero,700,2\n")
    r = semilla.cargar(con=con, origen=tmp_path)
    assert r["origen"]["acopios.csv"] == r["origen"]["vehiculos.csv"] == "real"
    assert r["origen"]["pedidos.csv"] == "sintético"
    v = con.execute("SELECT * FROM vehiculos WHERE id=1").fetchone()
    assert (v["lat"], v["lon"], v["estado"]) == (5.0371, -75.4397, "libre")   # sin posición: en su acopio


def test_archivo_malo_se_rechaza_con_fila_y_razon_sin_tocar_la_base(con, tmp_path):
    semilla.cargar(con=con)
    escribir(tmp_path, "vehiculos.csv", "id,tipo,capacidad_kg,acopio_id\n1,tractomula,4500,1\n2,campero,-5,1\n")
    escribir(tmp_path, "lotes.csv", "id,acopio_id,producto,kg,perecedero,vence_en\n1,1,leche,100,1,mañana\n")
    escribir(tmp_path, "puntos.csv", "id,nombre,lat,lon\n1,Punto invertido,-75.5,5.06\n")
    with pytest.raises(SystemExit) as e:
        semilla.cargar(reiniciar=True, con=con, origen=tmp_path)
    mensaje = str(e.value)
    assert "vehiculos.csv, fila 2: `tipo` desconocido" in mensaje
    assert "vehiculos.csv, fila 3: `capacidad_kg` debe ser mayor que cero" in mensaje
    assert "lotes.csv, fila 2: `vence_en` no es una fecha legible" in mensaje
    assert "puntos.csv, fila 2: coordenadas fuera del área" in mensaje
    assert con.execute("SELECT COUNT(*) FROM vehiculos").fetchone()[0] == 5      # sigue la carga anterior


def test_referencia_rota_entre_archivos(con, tmp_path):
    escribir(tmp_path, "acopios.csv", "id,nombre,lat,lon\n7,Bodega única,5.0371,-75.4397\n")
    with pytest.raises(SystemExit) as e:
        semilla.cargar(con=con, origen=tmp_path)
    assert "`acopio_id` 1 no existe en acopios.csv (real)" in str(e.value)


def test_fechas_absolutas_y_relativas(con, tmp_path):
    escribir(tmp_path, "lotes.csv", "id,acopio_id,producto,kg,perecedero,vence_en,vence_en_horas\n"
                                    "1,1,leche,50,1,2026-11-21T14:30,\n2,1,pan,20,1,,12\n3,1,arroz,500,0,,\n")
    semilla.cargar(con=con, origen=tmp_path)
    vence = [r[0] for r in con.execute("SELECT vence_en FROM lotes ORDER BY id")]
    assert vence[0] == "2026-11-21T14:30:00-05:00" and vence[1] is not None and vence[2] is None
