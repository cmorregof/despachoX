"""Clave del tablero.

El tablero de la nube es público y su dirección está en un repositorio público.
Si existe la variable DESPACHOX_CLAVE_TABLERO, el tablero pide esa clave antes de
mostrar la mesa. Si no existe, queda abierto, como antes. La clave nunca va en el
repositorio: se define en Railway y se comparte por fuera.
"""
from __future__ import annotations

import hmac
import os

VARIABLE = "DESPACHOX_CLAVE_TABLERO"


def clave_valida(dada: str | None, clave: str | None) -> bool:
    """Dice si se puede abrir la mesa.

    Sin clave configurada, siempre. Con clave, solo si la dada coincide; la
    comparación tarda lo mismo acierte o no.
    """
    if not clave:
        return True
    if not dada:
        return False
    return hmac.compare_digest(dada.encode("utf-8"), clave.encode("utf-8"))


def clave_ok() -> bool:
    """Pide la clave si hace falta. Devuelve True cuando se puede mostrar la mesa."""
    import streamlit as st

    clave = os.environ.get(VARIABLE, "")
    if not clave or st.session_state.get("clave_ok"):
        return True
    dada = st.text_input("Clave del tablero", type="password", key="clave_tablero")
    if dada:
        if clave_valida(dada, clave):
            st.session_state["clave_ok"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta.")
    return False
