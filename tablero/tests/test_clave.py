"""Pruebas de la clave del tablero (tablero/clave.py)."""
from tablero.clave import clave_valida


def test_sin_clave_configurada_el_tablero_queda_abierto():
    assert clave_valida(None, None)
    assert clave_valida("", "")
    assert clave_valida("cualquier cosa", "")


def test_clave_correcta_abre_la_mesa():
    assert clave_valida("clave-de-prueba", "clave-de-prueba")


def test_clave_incorrecta_o_vacia_no_abre():
    assert not clave_valida("otra", "clave-de-prueba")
    assert not clave_valida("clave-de-prueb", "clave-de-prueba")
    assert not clave_valida("", "clave-de-prueba")
    assert not clave_valida(None, "clave-de-prueba")
