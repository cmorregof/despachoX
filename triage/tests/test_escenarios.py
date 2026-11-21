"""Los 10 escenarios de aceptación de C.1, cada uno en su base temporal."""
import pytest

from triage import db as tdb
from triage import sinteticos


@pytest.fixture
def base(tmp_path):
    con = tdb.conectar(tmp_path / "escenario.db")
    yield con
    con.close()


def _correr(base, n):
    r = sinteticos.correr_escenario(base, n)
    assert r["cumple"], f"Escenario {n} ({r['clave']}) no cumple: {r['medido']}"
    return r["medido"]


def test_1_ataque(base):
    m = _correr(base, 1)
    assert m["solicitudes"] == 200
    assert m["fraccion_cuarentena"] >= 0.95 and m["cupo_consumido"] == 0


def test_2_replica(base):
    m = _correr(base, 2)
    assert m["fraccion_cuarentena"] < 0.05 and m["posible_nuevo_evento"] >= 1


def test_3_vereda(base):
    m = _correr(base, 3)
    assert m["estado_vereda"] != "cuarentena"
    assert m["prioridad_vereda"] == m["prioridad_urbana"]


def test_4_silencio(base):
    m = _correr(base, 4)
    assert m["es_debil_a_las_3h"] == 1 and m["tarea_a_las_3h"] == "abierta"
    assert m["tarea_6h_despues"] == "escalada"


def test_5_chat_desde_zona_debil(base):
    m = _correr(base, 5)
    assert m["estado"] == "espera_agente"
    assert base.execute("SELECT COUNT(*) FROM solicitudes WHERE estado='confirmada_regla'"
                        ).fetchone()[0] == 0


def test_6_agente_lejos(base):
    m = _correr(base, 6)
    assert m["ok"] is False and m["motivo"] == "ubicacion_agente"


def test_7_extractor_roto(base):
    m = _correr(base, 7)
    assert m["guardadas"] == m["entradas"] == 30 and m["errores_internos"] == 0
    assert m["sin_campos_en_cola_con_marca"] == 10


def test_8_inyeccion(base):
    m = _correr(base, 8)
    assert m["marca_inyeccion"] and m["estado"] != "confirmada_regla"


def test_9_mismo_archivo_dos_veces(base):
    m = _correr(base, 9)
    assert m["guardadas_1"] == m["guardadas_2"] and m["duplicados_2"] == m["filas_validas"]
    filas = base.execute("SELECT hash_mensaje, COUNT(*) c FROM solicitudes GROUP BY hash_mensaje "
                         "HAVING c > 1").fetchall()
    assert filas == []


def test_10_concentracion(base):
    m = _correr(base, 10)
    assert m["marca"] and m["estado"] == "en_cola"


def test_escenarios_son_deterministas(tmp_path):
    a = tdb.conectar(tmp_path / "a.db")
    b = tdb.conectar(tmp_path / "b.db")
    assert sinteticos.correr_escenario(a, 1)["medido"] == sinteticos.correr_escenario(b, 1)["medido"]
    a.close()
    b.close()


def test_linea_de_comandos(tmp_path, capsys):
    from pathlib import Path
    from triage import correr
    db = str(tmp_path / "cli.db")
    sucio = str(Path(__file__).parent / "datos" / "externo_sucio.csv")
    reporte = tmp_path / "externo.md"
    assert correr.main(["--db", db]) == 2                                  # falta la entrada
    assert correr.main(["--db", db, "--solicitudes", str(tmp_path / "no.csv")]) == 2
    assert correr.main(["--db", db, "--escenario", "todos"]) == 2          # sin --reiniciar
    assert correr.main(["--db", db, "--reiniciar", "--escenario", "nada"]) == 2
    import pytest as _pytest
    with _pytest.raises(SystemExit) as e:
        correr.main([])                                                    # falta --db
    assert e.value.code == 2
    assert correr.main(["--db", db, "--reiniciar", "--solicitudes", sucio,
                        "--reporte", str(reporte)]) == 0
    texto = reporte.read_text(encoding="utf-8")
    assert "## Errores de lectura" in texto and "fecha_invalida" in texto and "falta_remitente" in texto
    assert correr.main(["--db", db, "--reiniciar", "--escenario", "inyeccion",
                        "--reporte", str(tmp_path / "e.md")]) == 0


def test_nombres_de_escenario():
    assert sinteticos.numero_de("ataque") == 1 and sinteticos.numero_de("10") == 10
    assert sinteticos.numero_de("nada") is None
