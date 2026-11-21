"""Puntaje P(real) con log-odds, pesos desde Beta, umbral y aprendizaje auditado (B.5)."""
from __future__ import annotations

import copy
import json
import math
import sqlite3

import numpy as np

from triage import config

EPS = 1e-12


def logit(p: float) -> float:
    p = min(1 - EPS, max(EPS, float(p)))
    return math.log(p / (1 - p))


def media_beta(alpha: float, beta: float) -> float:
    s = alpha + beta
    return alpha / s if s > 0 else 0.5


def peso(b: dict) -> float:
    """w = ln(E[p_r] / E[p_f])."""
    er = media_beta(b["alpha_r"], b["beta_r"])
    ef = media_beta(b["alpha_f"], b["beta_f"])
    return math.log(max(er, EPS) / max(ef, EPS))


def pesos(params: dict) -> dict:
    return {s: peso(b) for s, b in params["senales"].items()}


def p_real(senales_activas, params: dict) -> tuple[float, dict]:
    """P(real) y el desglose {señal: aporte}. `base` es logit(pi_0)."""
    w = pesos(params)
    desglose = {"base": round(logit(params["pi_0"]), 4)}
    L = logit(params["pi_0"])
    for s in sorted(set(senales_activas or ())):
        if s in w:
            L += w[s]
            desglose[s] = round(w[s], 4)
    return 1 / (1 + math.exp(-L)), desglose


def elicitar(respuestas) -> dict:
    """Beta por señal desde la elicitación de expertos (mu_r, mu_f, n_0), promediando parámetros.

    `respuestas`: lista de {"senal", "mu_r", "mu_f", "n_0"} (una por experto y señal).
    Las respuestas inválidas se ignoran.
    """
    acumulado: dict = {}
    for r in respuestas or []:
        try:
            s = str(r["senal"])
            mu_r, mu_f, n0 = float(r["mu_r"]), float(r["mu_f"]), float(r["n_0"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (0 < mu_r < 1 and 0 < mu_f < 1 and n0 > 0):
            continue
        acumulado.setdefault(s, []).append(
            {"alpha_r": mu_r * n0, "beta_r": (1 - mu_r) * n0,
             "alpha_f": mu_f * n0, "beta_f": (1 - mu_f) * n0})
    return {s: {k: float(np.mean([b[k] for b in lista])) for k in lista[0]}
            for s, lista in acumulado.items()}


def umbral_detalle(p_valores, params: dict) -> dict:
    """tau* = max(tau_piso, min(tau_c, tau_cap)) (B.5.3)."""
    r = params["r_costo"]
    tau_c = r / (r + 1)
    vals = np.array([v for v in (p_valores if p_valores is not None else []) if v is not None],
                    dtype=float)
    vals = vals[np.isfinite(vals)]
    V, K = len(vals), params["K_revision_h"]
    tau_cap = 1.0 if V == 0 or K >= V else float(np.quantile(vals, K / V))
    tau = max(params["tau_piso"], min(tau_c, tau_cap))
    return {"tau": tau, "tau_c": tau_c, "tau_cap": tau_cap, "V": V, "K": K}


def umbral(p_valores, params: dict) -> float:
    return umbral_detalle(p_valores, params)["tau"]


def _ajustar_a_peso(b: dict, w_obj: float) -> dict:
    """Mueve la media de la Beta de falsas (o la de reales) para que w = w_obj."""
    er = media_beta(b["alpha_r"], b["beta_r"])
    nf = b["alpha_f"] + b["beta_f"]
    ef = er / math.exp(w_obj)
    if ef >= config.MU_MAX:
        ef = config.MU_MAX
        er = ef * math.exp(w_obj)
        nr = b["alpha_r"] + b["beta_r"]
        b["alpha_r"], b["beta_r"] = er * nr, (1 - er) * nr
    b["alpha_f"], b["beta_f"] = ef * nf, (1 - ef) * nf
    return b


def actualizar(parametros: dict, etiquetas) -> dict:
    """Versión nueva de parámetros con aciertos sumados a alpha y fallos a beta (B.5.4).

    No la aplica: hay que guardarla (config.guardar_version) y aprobarla con un humano.
    Cada peso cambia como máximo ±max_cambio_w.
    """
    nuevo = config.completar(copy.deepcopy(parametros))
    tope = nuevo["max_cambio_w"]
    validas = []
    for e in etiquetas or []:
        try:
            s = e["senales"]
            activas = set(s.keys() if isinstance(s, dict) else s)
            validas.append((activas, bool(e["real"])))
        except (KeyError, TypeError, AttributeError):
            continue
    for senal, b0 in nuevo["senales"].items():
        b = dict(b0)
        w_antes = peso(b)
        for activas, real in validas:
            x = 1.0 if senal in activas else 0.0
            if real:
                b["alpha_r"] += x
                b["beta_r"] += 1 - x
            else:
                b["alpha_f"] += x
                b["beta_f"] += 1 - x
        w_desp = peso(b)
        w_lim = min(w_antes + tope, max(w_antes - tope, w_desp))
        if abs(w_lim - w_desp) > 1e-12:
            b = _ajustar_a_peso(b, w_lim)
        nuevo["senales"][senal] = b
    return nuevo


def etiquetas_desde_bitacora(con: sqlite3.Connection) -> list[dict]:
    """Etiquetas de las confirmaciones y descartes humanos (paso 13)."""
    filas = con.execute("SELECT accion, detalle FROM bitacora WHERE accion IN "
                        "('confirmar_humano', 'descartar_humano') AND quien NOT LIKE 'regla:%' "
                        "ORDER BY id").fetchall()
    ultima: dict = {}
    for f in filas:
        try:
            ids = json.loads(f["detalle"]).get("ids", [])
        except (TypeError, ValueError, AttributeError):
            continue
        for i in ids:
            ultima[i] = f["accion"] == "confirmar_humano"
    etiquetas = []
    for i, real in ultima.items():
        fila = con.execute("SELECT senales FROM solicitudes WHERE id=?", (i,)).fetchone()
        if fila is None:
            continue
        try:
            senales = json.loads(fila["senales"] or "{}")
        except (TypeError, ValueError):
            senales = {}
        etiquetas.append({"id": i, "senales": [s for s in senales if s != "base"], "real": real})
    return etiquetas
