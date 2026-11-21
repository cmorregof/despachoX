import math

import numpy as np
import pytest

from triage import config, puntaje


def test_logit_de_pi0():
    assert puntaje.logit(0.9) == pytest.approx(2.1972, abs=1e-4)
    assert puntaje.logit(0.9) == pytest.approx(math.log(9), abs=1e-12)
    assert math.isfinite(puntaje.logit(1.0)) and math.isfinite(puntaje.logit(0.0))


@pytest.mark.parametrize("senal,lr", list(config.LR_DEFECTO.items()))
def test_peso_reconstruido_desde_beta(params, senal, lr):
    assert abs(puntaje.peso(params["senales"][senal]) - math.log(lr)) < 1e-6


def test_p_real_y_desglose(params):
    p, d = puntaje.p_real([], params)
    assert p == pytest.approx(0.9)
    p, d = puntaje.p_real(["lider_registrado", "lugar_confirmado", "desconocida"], params)
    L = math.log(9) + math.log(5) + math.log(2)
    assert p == pytest.approx(1 / (1 + math.exp(-L)))
    assert set(d) == {"base", "lider_registrado", "lugar_confirmado"}
    assert d["lider_registrado"] == pytest.approx(1.6094, abs=1e-4)


def test_elicitar_promedia_expertos():
    r = puntaje.elicitar([
        {"senal": "x", "mu_r": 0.6, "mu_f": 0.2, "n_0": 10},
        {"senal": "x", "mu_r": 0.4, "mu_f": 0.2, "n_0": 10},
        {"senal": "y", "mu_r": 2.0, "mu_f": 0.1, "n_0": 10},       # inválida
        {"senal": "z"}])                                             # incompleta
    assert set(r) == {"x"}
    assert r["x"]["alpha_r"] == pytest.approx(5.0) and r["x"]["beta_r"] == pytest.approx(5.0)
    assert puntaje.peso(r["x"]) == pytest.approx(math.log(0.5 / 0.2))


def test_umbral_gana_el_costo(params):
    assert puntaje.umbral([0.5, 0.9, 0.95], params) == pytest.approx(0.8)
    assert puntaje.umbral([], params) == pytest.approx(0.8)


def test_umbral_gana_la_capacidad(params):
    p = np.linspace(0.5, 0.9, 100)                     # V = 100, K = 60 → cuantil 0.6 = 0.74
    d = puntaje.umbral_detalle(p, params)
    assert 0.7 < d["tau"] < 0.8 and d["tau"] == pytest.approx(d["tau_cap"])
    assert d["tau"] == pytest.approx(0.74, abs=1e-9)


def test_umbral_gana_el_piso(params):
    q = dict(params, K_revision_h=10)
    assert puntaje.umbral(np.linspace(0.5, 0.9, 100), q) == pytest.approx(0.7)
    assert puntaje.umbral([float("nan"), None, 0.9], params) == pytest.approx(0.8)


def test_actualizar_con_tope_de_cambio(params):
    # Muchas etiquetas que vuelven 'inyeccion' muy frecuente en reales: el peso subiría mucho.
    etiquetas = [{"senales": ["inyeccion"], "real": True}] * 500
    nuevo = puntaje.actualizar(params, etiquetas)
    w0 = puntaje.peso(params["senales"]["inyeccion"])
    w1 = puntaje.peso(nuevo["senales"]["inyeccion"])
    assert w1 == pytest.approx(w0 + 0.5, abs=1e-9)
    # En sentido contrario también se limita.
    nuevo2 = puntaje.actualizar(params, [{"senales": ["validada_agente"], "real": False}] * 500)
    w = puntaje.peso(params["senales"]["validada_agente"])
    assert puntaje.peso(nuevo2["senales"]["validada_agente"]) == pytest.approx(w - 0.5, abs=1e-9)
    # Cambios pequeños pasan sin recorte; la entrada no se modifica.
    poco = puntaje.actualizar(params, [{"senales": {"lugar_confirmado": 0.69}, "real": True}])
    assert abs(puntaje.peso(poco["senales"]["lugar_confirmado"]) - math.log(2)) < 0.5
    assert puntaje.peso(params["senales"]["inyeccion"]) == pytest.approx(math.log(0.1))
    assert puntaje.actualizar(params, ["basura", {"real": True}]) == config.completar(params)


def test_version_nueva_no_se_aplica_sin_humano(con, params):
    nuevo = puntaje.actualizar(params, [{"senales": ["inyeccion"], "real": True}] * 50)
    v = config.guardar_version(con, nuevo)
    assert config.version_vigente(con)[0] == 1
    with pytest.raises(PermissionError):
        config.aprobar_version(con, v, "regla:v1")
    with pytest.raises(PermissionError):
        config.aprobar_version(con, v, "")
    assert config.version_vigente(con)[0] == 1
    config.aprobar_version(con, v, "despachador:luis")
    assert config.version_vigente(con)[0] == v
