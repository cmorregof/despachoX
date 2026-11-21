"""Filtro antibots y antifraude (B.4). Nunca borra: su peor resultado es `cuarentena`."""
from __future__ import annotations

import json
import math
import re
import sqlite3
import unicodedata
from datetime import datetime, timedelta

import numpy as np
from scipy.stats import poisson

from triage import censo, config, geo
from triage import db as tdb
from triage.entrada_datos import a_iso, parsear_fecha

# B.4.7: instrucciones dirigidas al sistema. Se buscan sobre texto sin tildes y en minúsculas.
PATRONES_INYECCION = [re.compile(p) for p in (
    r"\bignor(a|e|en)\b",
    r"\bolvida (las|tus) (instrucciones|reglas)",
    r"\bmarca(lo|la)? como (verificad[oa]|real|confirmad[oa])",
    r"\beres un[ao]?\b",
    r"\bsystem\b",
    r"\bprompt\b",
    r"\baprueba (esto|este pedido|esta solicitud)",
)]
QUIEN_REGLA = "regla:triage"


# ---------- texto ----------
def normalizar_texto(texto) -> str:
    """Minúsculas, sin tildes, sin signos, dígitos como '#', espacios colapsados (B.4.4)."""
    if not texto:
        return ""
    s = unicodedata.normalize("NFKD", str(texto).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\d", "#", s)
    s = re.sub(r"[^a-z#ñ\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tejas(texto_normalizado: str, k: int = 5) -> set:
    s = texto_normalizado or ""
    if not s:
        return set()
    if len(s) < k:
        return {s}
    return {s[i:i + k] for i in range(len(s) - k + 1)}


def jaccard(a, b) -> float:
    a, b = set(a or ()), set(b or ())
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def detectar_inyeccion(texto) -> bool:
    if not texto:
        return False
    s = unicodedata.normalize("NFKD", str(texto).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    return any(p.search(s) for p in PATRONES_INYECCION)


# ---------- remitente ----------
class CubetaFichas:
    """Cubeta de fichas que se reconstruye con el historial del remitente (B.4.1)."""

    def __init__(self, capacidad: float, recarga_h: float):
        self.capacidad = max(0.0, float(capacidad))
        self.recarga_h = float(recarga_h) if recarga_h and recarga_h > 0 else math.inf

    def fichas(self, previos: list[datetime], t: datetime) -> float:
        """Fichas disponibles en t, repitiendo las decisiones pasadas en orden."""
        fichas = self.capacidad
        ultimo = None
        for p in sorted(x for x in previos if x is not None and x <= t):
            if ultimo is not None:
                fichas = min(self.capacidad, fichas + (p - ultimo).total_seconds() / 3600 / self.recarga_h)
            ultimo = p
            if fichas >= 1:
                fichas -= 1
        if ultimo is not None:
            fichas = min(self.capacidad, fichas + (t - ultimo).total_seconds() / 3600 / self.recarga_h)
        return fichas

    def admite(self, previos: list[datetime], t: datetime) -> bool:
        return self.fichas(previos, t) >= 1 - 1e-9


def cadencia(tiempos: list[datetime], cv_min: float, n_min: int = 4) -> bool:
    """Cadencia de máquina: CV de los intervalos < cv_min, o intervalos de media 0 (B.4.5)."""
    ts = sorted(t for t in tiempos if t is not None)
    if len(ts) < n_min:
        return False
    dt = np.diff([t.timestamp() for t in ts])
    media = float(np.mean(dt))
    if media <= 0:
        return True
    return float(np.std(dt)) / media < cv_min


def es_nuevo(remitente, t: datetime, params: dict) -> bool:
    if remitente is None:
        return True
    pc = parsear_fecha(remitente["primer_contacto"])
    return pc is None or pc > t - timedelta(hours=params["nuevo_h"])


def es_lider_de(remitente, zona_id) -> bool:
    if remitente is None or remitente["rol"] != "lider" or zona_id is None:
        return False
    try:
        zonas = json.loads(remitente["zonas"] or "[]")
    except (TypeError, ValueError):
        return False
    return zona_id in zonas or str(zona_id) in [str(z) for z in zonas]


# ---------- ráfagas ----------
def p_rafaga(n: int, lam: float, w_h: float) -> float:
    """p = 1 − F_Poisson(N − 1; λ·w)."""
    if n is None or n <= 0:
        return 1.0
    mu = (lam or 0.0) * (w_h or 0.0)
    if not math.isfinite(mu) or mu <= 0:
        return 0.0
    return float(poisson.sf(n - 1, mu))


def lambda_zona(zona, params: dict) -> float:
    """Tasa esperada de solicitudes por hora en la zona (B.4.2)."""
    lam_h = geo.numero(getattr(zona, "lambda_h", None))
    if lam_h is not None:
        return max(params["lambda_min"], lam_h)
    return max(params["lambda_min"], censo.hogares_afectados(zona, params) * params["q"] / 24)


def evento_global_activo(con: sqlite3.Connection, t: datetime, params: dict) -> bool:
    filas = con.execute("SELECT detalle FROM bitacora WHERE accion='posible_nuevo_evento' "
                        "AND quien LIKE 'regla:%' ORDER BY id DESC LIMIT 50").fetchall()
    for f in filas:
        try:
            d = json.loads(f["detalle"])
            desde, hasta = parsear_fecha(d.get("desde")), parsear_fecha(d.get("hasta"))
        except (TypeError, ValueError, AttributeError):
            continue
        if desde and hasta and desde <= t < hasta:
            return True
    return False


def evaluar_rafaga(con: sqlite3.Connection, zona, t: datetime, params: dict) -> dict:
    """B.4.2 y B.4.3 para la zona en el instante t. Actualiza rafaga_hasta y la bitácora."""
    p = params
    w = p["w_rafaga_h"]
    n = con.execute("SELECT COUNT(*) FROM solicitudes WHERE zona_id=? AND recibida_en > ? "
                    "AND recibida_en <= ?", (zona.id, a_iso(t - timedelta(hours=w)), a_iso(t))
                    ).fetchone()[0]
    global_activo = evento_global_activo(con, t, p)
    lam = lambda_zona(zona, p) * (p["k_evento"] if global_activo else 1)
    pv = p_rafaga(n, lam, w)
    hasta = parsear_fecha(con.execute("SELECT rafaga_hasta FROM zonas WHERE id=?",
                                      (zona.id,)).fetchone()[0])
    if pv < p["alpha_rafaga"]:
        nuevo = t + timedelta(hours=p["rafaga_dur_h"])
        if hasta is None or nuevo > hasta:
            hasta = nuevo
            con.execute("UPDATE zonas SET rafaga_hasta=? WHERE id=?", (a_iso(hasta), zona.id))
        if not global_activo:
            global_activo = _revisar_global(con, t, p)
    return {"n": n, "lambda": lam, "p": pv, "en_rafaga": hasta is not None and hasta > t,
            "global": global_activo}


def _revisar_global(con: sqlite3.Connection, t: datetime, p: dict) -> bool:
    afectadas = con.execute("SELECT id, rafaga_hasta FROM zonas WHERE afectacion > 0").fetchall()
    if not afectadas:
        return False
    desde = t - timedelta(hours=p["ventana_global_h"])
    en_rafaga = 0
    for f in afectadas:
        h = parsear_fecha(f["rafaga_hasta"])
        if h is None:
            continue
        inicio = h - timedelta(hours=p["rafaga_dur_h"])
        if desde < inicio <= t:
            en_rafaga += 1
    fraccion = en_rafaga / len(afectadas)
    if fraccion > p["umbral_global"]:
        tdb.anotar_regla(con, QUIEN_REGLA, "posible_nuevo_evento",
                         {"desde": a_iso(t), "hasta": a_iso(t + timedelta(hours=p["evento_dur_h"])),
                          "zonas_en_rafaga": en_rafaga, "zonas_afectadas": len(afectadas),
                          "fraccion": round(fraccion, 3)}, t)
        return True
    return False


# ---------- texto coordinado y salto ----------
def grupo_coordinado(con: sqlite3.Connection, sid: int, remitente_hash: str, texto, t: datetime,
                     params: dict, cache: dict | None = None) -> list:
    """Solicitudes de OTROS remitentes en la ventana con texto casi igual (Jaccard ≥ umbral)."""
    cache = {} if cache is None else cache
    k = params["teja"]
    a = tejas(normalizar_texto(texto), k)
    if not a:
        return []
    filas = con.execute(
        "SELECT id, remitente_hash, texto, recibida_en, estado, pedido_id FROM solicitudes "
        "WHERE recibida_en >= ? AND recibida_en <= ? AND id != ? AND remitente_hash != ?",
        (a_iso(t - timedelta(hours=params["ventana_coord_h"])), a_iso(t), sid, remitente_hash)
    ).fetchall()
    grupo = []
    for f in filas:
        b = cache.get(f["id"])
        if b is None:
            b = tejas(normalizar_texto(f["texto"]), k)
            cache[f["id"]] = b
        if jaccard(a, b) >= params["jaccard_texto"]:
            grupo.append(f)
    return grupo


def hay_salto(con: sqlite3.Connection, sid: int, remitente, zona, t: datetime,
              zonas_por_id: dict, params: dict) -> bool:
    """B.4.6: el mismo remitente pide para zonas a más de salto_km en menos de una hora."""
    if remitente is None or zona is None:
        return False
    filas = con.execute(
        "SELECT DISTINCT zona_id FROM solicitudes WHERE remitente_hash=? AND id != ? "
        "AND zona_id IS NOT NULL AND zona_id != ? AND recibida_en >= ? AND recibida_en <= ?",
        (remitente["remitente_hash"], sid, zona.id,
         a_iso(t - timedelta(hours=params["ventana_salto_h"])), a_iso(t))).fetchall()
    for f in filas:
        otra = zonas_por_id.get(f["zona_id"])
        if otra is None:
            continue
        if geo.haversine_m(zona.lat, zona.lon, otra.lat, otra.lon) > params["salto_km"] * 1000:
            if not (es_lider_de(remitente, zona.id) and es_lider_de(remitente, otra.id)):
                return True
    return False


# ---------- salida de la cuarentena (B.4.8) ----------
def _exigir_humano(quien):
    if not config.es_humano(quien):
        raise PermissionError("Solo una persona puede liberar o descartar solicitudes.")


def liberar(con: sqlite3.Connection, ids, quien: str, ahora: datetime | None = None,
            params: dict | None = None, extractor=None) -> list[int]:
    """Devuelve solicitudes en cuarentena al paso 3 del embudo. Exige una persona."""
    _exigir_humano(quien)
    from triage import embudo   # importación diferida: embudo usa este módulo
    from datos import db as datos_db
    liberadas = []
    for sid in ids or []:
        f = con.execute("SELECT estado FROM solicitudes WHERE id=?", (sid,)).fetchone()
        if f is None or f["estado"] != "cuarentena":
            continue
        con.execute("UPDATE solicitudes SET estado='recibida', motivo_cuarentena=NULL WHERE id=?", (sid,))
        embudo.reprocesar(con, sid, desde=3, params=params, ahora=ahora, extractor=extractor,
                          commit=False)
        liberadas.append(sid)
    con.commit()
    datos_db.anotar(con, quien, "liberar_cuarentena", json.dumps({"ids": liberadas}))
    return liberadas


def descartar(con: sqlite3.Connection, ids, quien: str) -> list[int]:
    """Descarta solicitudes. Exige una persona."""
    _exigir_humano(quien)
    from triage import embudo
    return embudo.cambiar_estado(con, ids, "descartada", quien)
