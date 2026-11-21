"""Fase 1: la base temporal tiene las 5 tablas nuevas y las originales quedan iguales."""
import json

import pytest

from datos import db as datos_db
from triage import config
from triage import db as tdb

NUEVAS = {"zonas", "remitentes", "tareas_campo", "solicitudes", "parametros"}


def _esquema(con):
    return {r["name"]: r["sql"] for r in
            con.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")}


def test_crea_tablas_nuevas_sin_tocar_las_originales(tmp_path):
    original = datos_db.conectar(tmp_path / "solo_datos.db")
    antes = _esquema(original)
    original.close()

    con = tdb.conectar(tmp_path / "con_triage.db")
    despues = _esquema(con)
    assert NUEVAS <= set(despues)
    assert not (NUEVAS & set(antes)), "una tabla de triage ya existía en el esquema común"
    for nombre, sql in antes.items():
        assert despues[nombre] == sql, f"cambió la tabla original {nombre}"
    con.close()


def test_siembra_version_1_y_es_idempotente(tmp_path):
    ruta = tmp_path / "t.db"
    con = tdb.conectar(ruta)
    con.close()
    con = tdb.conectar(ruta)
    filas = con.execute("SELECT * FROM parametros").fetchall()
    assert len(filas) == 1
    assert filas[0]["version"] == 1 and filas[0]["aplicada"] == 1
    assert filas[0]["aprobada_por"] == "inicial"
    valores = json.loads(filas[0]["valores"])
    assert valores["semilla"] == 2026 and "senales" in valores
    con.close()


def test_version_nueva_no_se_aplica_sin_humano(con):
    v = config.guardar_version(con, {"tau_piso": 0.75})
    assert config.version_vigente(con)[0] == 1
    with pytest.raises(PermissionError):
        config.aprobar_version(con, v, "regla:v1")
    config.aprobar_version(con, v, "coordinador:ana")
    version, valores = config.version_vigente(con)
    assert version == v and valores["tau_piso"] == 0.75


def test_reiniciar_borra_solo_triage(con):
    con.execute("INSERT INTO puntos(nombre, lat, lon) VALUES ('p', 5.06, -75.5)")
    con.execute("INSERT INTO zonas(nombre, lat, lon) VALUES ('z', 5.06, -75.5)")
    con.commit()
    tdb.reiniciar(con)
    assert con.execute("SELECT COUNT(*) FROM zonas").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM puntos").fetchone()[0] == 1
    assert con.execute("SELECT COUNT(*) FROM parametros").fetchone()[0] == 1


def test_parametros_supuestos_completos():
    p = config.completar({"senales": {"inyeccion": config.beta_desde_lr(0.2)}})
    for clave in ("a_prior", "eps_s_m", "delta", "B_ciudadano", "pi_0", "alpha_sil", "gamma"):
        assert clave in p
    assert set(p["senales"]) == set(config.LR_DEFECTO)
