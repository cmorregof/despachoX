"""Parámetros del triage y sus versiones.

Todo número marcado SUPUESTO en ESPEC_TRIAGE vive aquí, en PARAMETROS_DEFECTO, y se puede
sobrescribir. Las versiones se guardan en la tabla `parametros`; una versión nueva solo se
aplica cuando una persona la aprueba (aprobar_version).
"""
from __future__ import annotations

import copy
import json
import math
import sqlite3
from datetime import datetime

from datos import db as datos_db

# Recuadro de Manizales (B.2.4). No es un SUPUESTO: es el límite del área de trabajo.
RECUADRO_MANIZALES = {"lat_min": 4.90, "lat_max": 5.20, "lon_min": -75.70, "lon_max": -75.30}

# Razones de verosimilitud por señal (B.5.2, SUPUESTO). Se guardan como Beta con n_0.
LR_DEFECTO = {
    "lider_registrado": 5.0,
    "lugar_confirmado": 2.0,
    "dentro_de_tope": 1.5,
    "sobre_tope": 0.5,
    "concentracion_remitente": 0.4,
    "salto_ubicacion": 0.3,
    "inyeccion": 0.1,
    "validada_agente": 50.0,
}
N0_DEFECTO = 10          # SUPUESTO: tamaño de muestra equivalente de la elicitación
MU_F_DEFECTO = 0.1       # SUPUESTO: probabilidad de la señal en solicitudes falsas
MU_MAX = 0.99            # tope de una media Beta para que la distribución no degenere


def beta_desde_lr(lr: float, n0: float = N0_DEFECTO) -> dict:
    """Expresa una razón de verosimilitud como dos Beta (B.5.2)."""
    mu_f = MU_F_DEFECTO
    mu_r = lr * mu_f
    if mu_r > MU_MAX:
        mu_r = MU_MAX
        mu_f = MU_MAX / lr
    return {"alpha_r": mu_r * n0, "beta_r": (1 - mu_r) * n0,
            "alpha_f": mu_f * n0, "beta_f": (1 - mu_f) * n0}


PARAMETROS_DEFECTO: dict = {
    # B.2 censo
    "a_prior": 0.10, "tamano_hogar_defecto": 3.0,
    "r_max_poligono_m": 500, "r_max_centroide_m": 1500,
    # B.3 clústeres y topes
    "eps_s_m": 250, "eps_t_h": 6, "min_samples": 3,
    "delta": 0.20, "T_min": 5, "ciclo_h": 72,
    "f_bar": 10, "m": 2, "S_min": 3, "phi": 0.25,
    "ventana_S_h": 24, "factor_absurdo": 10,
    # B.4 antibots
    "B_ciudadano": 3, "B_registrado": 20, "recarga_h": 2,
    "q": 0.05, "lambda_min": 0.1, "alpha_rafaga": 0.001, "rafaga_dur_h": 2, "eta": 0.2,
    "w_rafaga_h": 1, "nuevo_h": 72,
    "umbral_global": 0.40, "k_evento": 3, "evento_dur_h": 6, "ventana_global_h": 1,
    "jaccard_texto": 0.85, "k_coordinado": 3, "ventana_coord_h": 1, "min_nuevos_coord": 2,
    "teja": 5, "min_largo_coord": 30,
    "cv_min": 0.1, "n_min_cadencia": 4, "salto_km": 3, "ventana_salto_h": 1,
    # B.5 puntaje y umbral
    "pi_0": 0.90, "r_costo": 4, "tau_piso": 0.70, "K_revision_h": 60, "ventana_umbral_h": 1,
    "epsilon": 0.05, "max_cambio_w": 0.5,
    # B.6 zonas débiles y agentes
    "alpha_sil": 0.01, "T_min_sil_h": 3, "t_escala_h": 6, "auditoria_agente": 0.10,
    "agente_r_poligono_m": 500, "agente_r_centroide_m": 1500,
    # B.7 consolidación, decisión y cola
    "jaccard_productos": 0.5,
    "bloqueantes": ["sobre_tope", "familias_supuestas", "familias_absurdas", "inyeccion",
                    "sin_ubicar", "extraccion_fallida", "concentracion_remitente"],
    "u_albergue": 3, "u_critico": 3, "u_otro": 1, "beta_ais": 1.0, "gamma": 0.5,
    "muestra_lote": 3, "kg_por_familia": 12,
    # Control
    "semilla": 2026, "hora_evento": None,
    "senales": {s: beta_desde_lr(lr) for s, lr in LR_DEFECTO.items()},
}

# Acciones que las reglas del triage escriben en la bitácora (las borra --reiniciar).
ACCIONES_REGLA = ("confirmar_solicitud", "posible_nuevo_evento", "cuarentena_retroactiva",
                  "zona_debil", "escalar_tarea", "tarea_validada")


def es_humano(quien) -> bool:
    """Una persona (o un agente en terreno) firma con algo que no empieza por 'regla:'."""
    return isinstance(quien, str) and bool(quien.strip()) and not quien.strip().startswith("regla:")


def completar(params: dict | None) -> dict:
    """Mezcla los parámetros dados sobre los de defecto (las señales, por señal)."""
    base = copy.deepcopy(PARAMETROS_DEFECTO)
    for k, v in (params or {}).items():
        if k == "senales" and isinstance(v, dict):
            for s, b in v.items():
                base["senales"][s] = dict(b)
        else:
            base[k] = copy.deepcopy(v)
    return base


def _a_json(valores: dict) -> str:
    def defecto(o):
        if isinstance(o, datetime):
            return o.isoformat(timespec="seconds")
        if isinstance(o, float) and not math.isfinite(o):
            return None
        return str(o)
    return json.dumps(valores, ensure_ascii=False, sort_keys=True, default=defecto)


def version_vigente(con: sqlite3.Connection) -> tuple[int, dict]:
    """La última versión aplicada y sus valores completos."""
    fila = con.execute("SELECT version, valores FROM parametros WHERE aplicada=1 "
                       "ORDER BY version DESC LIMIT 1").fetchone()
    if fila is None:
        return 0, completar(None)
    try:
        valores = json.loads(fila["valores"])
    except (TypeError, ValueError):
        valores = {}
    return int(fila["version"]), completar(valores if isinstance(valores, dict) else {})


def cargar(con: sqlite3.Connection) -> dict:
    return version_vigente(con)[1]


def guardar_version(con: sqlite3.Connection, valores: dict, creada_en: str | None = None) -> int:
    """Guarda una versión nueva SIN aplicarla. Devuelve su número."""
    fila = con.execute("SELECT COALESCE(MAX(version), 0) AS v FROM parametros").fetchone()
    version = int(fila["v"]) + 1
    con.execute("INSERT INTO parametros(version, creada_en, aplicada, valores) VALUES (?,?,0,?)",
                (version, creada_en or datos_db.ahora(), _a_json(completar(valores))))
    con.commit()
    return version


def aprobar_version(con: sqlite3.Connection, version: int, quien: str) -> None:
    """Aplica una versión. Solo una persona puede hacerlo."""
    if not es_humano(quien):
        raise PermissionError("Solo una persona puede aprobar una versión de parámetros.")
    fila = con.execute("SELECT version FROM parametros WHERE version=?", (version,)).fetchone()
    if fila is None:
        raise ValueError(f"No existe la versión {version}.")
    con.execute("UPDATE parametros SET aplicada=1, aprobada_por=? WHERE version=?", (quien, version))
    con.commit()
    datos_db.anotar(con, quien, "aprobar_parametros", json.dumps({"version": version}))


def sembrar(con: sqlite3.Connection) -> None:
    """Si `parametros` está vacía, inserta la versión 1 aplicada."""
    if con.execute("SELECT COUNT(*) FROM parametros").fetchone()[0] == 0:
        con.execute("INSERT INTO parametros(version, creada_en, aprobada_por, aplicada, valores) "
                    "VALUES (1, ?, 'inicial', 1, ?)", (datos_db.ahora(), _a_json(PARAMETROS_DEFECTO)))
        con.commit()
