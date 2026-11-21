"""Clave del tablero.

El tablero de la nube es público y su dirección está en un repositorio público.
Si existe la variable DESPACHOX_CLAVE_TABLERO, el tablero pide esa clave antes de
mostrar la mesa. Si no existe, queda abierto, como antes. La clave nunca va en el
repositorio: se define en Railway y se comparte por fuera.
"""
from __future__ import annotations

import hmac
import os
from pathlib import Path

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


BOT = "https://t.me/despachox_bot"
_MARCA = Path(__file__).resolve().parents[1] / "recursos" / "marca"

_ESTILO = """
<style>
[data-testid="stMarkdownContainer"] .inicio-ceja {font-size:0.82rem; font-weight:700; letter-spacing:0.14em; color:#5C6A62; margin:0 0 0.6rem 0;}
[data-testid="stMarkdownContainer"] .inicio-titulo {font-size:clamp(1.9rem, 4.2vw, 2.7rem); line-height:1.12; font-weight:800; color:#1F5C4A; margin:0 0 1rem 0;}
[data-testid="stMarkdownContainer"] .inicio-bajada {font-size:1.08rem; line-height:1.55; color:#1C2A24; margin:0 0 1.6rem 0; max-width:34rem;}
[data-testid="stMarkdownContainer"] .inicio-pasos {display:flex; flex-wrap:wrap; gap:0.6rem; margin:1.6rem 0 0 0; padding:0; list-style:none;}
[data-testid="stMarkdownContainer"] .inicio-pasos li {background:#E4EADB; border:1px solid #CBD6C4; border-radius:999px; padding:0.35rem 0.9rem; margin:0;
                  font-size:0.9rem; color:#1C2A24;}
[data-testid="stMarkdownContainer"] .inicio-nota {font-size:0.92rem; line-height:1.5; color:#5C6A62; margin:1.2rem 0 0 0; max-width:34rem;}
[data-testid="stMarkdownContainer"] .inicio-nota a {color:#1F5C4A; font-weight:700;}
[data-testid="stMarkdownContainer"] .inicio-pie {font-size:0.82rem; color:#5C6A62; margin-top:2.4rem; border-top:1px solid #CBD6C4; padding-top:0.9rem;}
div[data-testid="stForm"] {background:#FFFFFF; border:1px solid #CBD6C4; border-radius:16px; padding:1.2rem 1.3rem 1rem;
                           max-width:34rem; box-shadow:0 6px 24px rgba(28,42,36,0.06);}
div[data-testid="stImage"] img {border-radius:20px;}
</style>
"""


def _inicio(st, error: bool) -> str | None:
    """Pantalla de entrada: dice qué es la mesa, pide la clave y devuelve lo que se escribió al enviar."""
    st.markdown(_ESTILO, unsafe_allow_html=True)
    izquierda, derecha = st.columns([5, 6], gap="large", vertical_alignment="center")
    with izquierda:
        st.markdown(
            '<p class="inicio-ceja">MANIZALES · CALDAS</p>'
            '<p class="inicio-titulo">Que la comida llegue aunque la vía se cierre</p>'
            '<p class="inicio-bajada">Mesa de despacho de ayuda alimentaria para los barrios y las veredas de Manizales.</p>',
            unsafe_allow_html=True)
        with st.form("entrada", border=False):
            dada = st.text_input("Clave de la mesa", type="password", key="clave_tablero",
                                 placeholder="Clave", label_visibility="collapsed")
            enviado = st.form_submit_button("Entrar a la mesa", type="primary", width="stretch")
        if error:
            st.error("Esa clave no abre la mesa. Revísala o pídesela al equipo.")
        st.markdown(
            f'<p class="inicio-nota">¿Sin clave? Haz un pedido de prueba en '
            f'<a href="{BOT}" target="_blank" rel="noopener">Telegram</a>.</p>',
            unsafe_allow_html=True)
    with derecha:
        imagen = _MARCA / "hero_convite_inicio.jpg"
        if imagen.exists():
            st.image(str(imagen), width="stretch")
    st.markdown('<p class="inicio-pie">Equipo 19 · Hackathon UNAL Manizales 2026 · Datos de prueba</p>', unsafe_allow_html=True)
    return dada if enviado else None


def clave_ok() -> bool:
    """Pide la clave si hace falta. Devuelve True cuando se puede mostrar la mesa."""
    import streamlit as st

    clave = os.environ.get(VARIABLE, "")
    if not clave or st.session_state.get("clave_ok"):
        return True
    dada = _inicio(st, error=bool(st.session_state.get("clave_error")))
    if dada is not None:
        if clave_valida(dada, clave):
            st.session_state["clave_ok"] = True
            st.session_state.pop("clave_error", None)
        else:
            st.session_state["clave_error"] = True
        st.rerun()
    return False
