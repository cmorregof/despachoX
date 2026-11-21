"""Lectura y validación de solicitudes (y zonas) en CSV o JSON de cualquier origen (B.10).

Nunca lanza una excepción por el contenido: una fila mala va a la lista de errores y se salta.
Solo falla, con un mensaje claro, si el archivo no existe.
El remitente en claro se convierte a hash al leer y nunca se guarda en claro.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import unicodedata
from datetime import datetime
from pathlib import Path

from datos import db as datos_db
from triage.geo import numero

BOGOTA = datos_db.BOGOTA
FORMATOS_FECHA = ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%d-%m-%Y %H:%M")
CANALES = ("chat", "agente", "manual")

ALIAS = {
    "recibida_en": ("recibida_en", "fecha", "hora", "timestamp"),
    "remitente": ("remitente", "remitente_hash", "chat_id", "telefono"),
    "texto": ("texto", "mensaje"),
    "lat": ("lat", "latitud"),
    "lon": ("lon", "longitud"),
    "familias": ("familias", "familias_declaradas"),
    "productos": ("productos",),
    "tipo_punto": ("tipo_punto",),
    "canal": ("canal",),
    "lugar_confirmado": ("lugar_confirmado",),
}
CONOCIDAS = {a for alias in ALIAS.values() for a in alias}
VERDADERO = {"1", "si", "sí", "true", "verdadero", "x", "s", "yes"}
FALSO = {"0", "no", "false", "falso", "n", ""}
_HASH = re.compile(r"^[0-9a-f]{32}$|^[0-9a-f]{64}$")


# ---------- utilidades ----------
def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))


def clave(k) -> str:
    return re.sub(r"\s+", "_", sin_tildes(str(k)).strip().lower())


def a_iso(dt: datetime) -> str:
    return dt.astimezone(BOGOTA).isoformat(timespec="seconds")


def parsear_fecha(v) -> datetime | None:
    """ISO 8601 o dd/mm/aaaa hh:mm. Sin zona horaria se asume Bogotá. Inválida: None."""
    if isinstance(v, datetime):
        dt = v
    else:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        dt = None
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            for fmt in FORMATOS_FECHA:
                try:
                    dt = datetime.strptime(s, fmt)
                    break
                except ValueError:
                    continue
        if dt is None:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=BOGOTA)
    try:
        return dt.astimezone(BOGOTA)
    except (OverflowError, ValueError):
        return None


def resolver_sal(sal=None, ruta_db=None) -> bytes:
    """La sal del hash: argumento, DESPACHOX_SAL o un archivo .sal fuera de git."""
    if sal:
        return sal if isinstance(sal, bytes) else str(sal).encode()
    env = os.environ.get("DESPACHOX_SAL")
    if env:
        return env.encode()
    ruta = Path(ruta_db).with_suffix(".sal") if ruta_db else Path(__file__).with_name(".sal")
    if not ruta.exists():
        ruta.write_text(secrets.token_hex(32), encoding="utf-8")
    return ruta.read_text(encoding="utf-8").strip().encode()


def hash_remitente(valor, sal) -> str:
    """HMAC-SHA256 con sal (igual que entrada/). Un hash ya calculado se conserva."""
    s = str(valor).strip()
    if _HASH.match(s.lower()) and re.search(r"[a-f]", s.lower()):
        return s.lower()
    sal_b = sal() if callable(sal) else sal
    return hmac.new(sal_b, s.encode(), hashlib.sha256).hexdigest()[:32]


def parsear_productos(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return []
        if s.startswith("["):
            try:
                v = json.loads(s)
            except ValueError:
                v = s.strip("[]").split(",")
        else:
            v = re.split(r"[,;|]", s)
    if isinstance(v, dict):
        v = [v]
    if not isinstance(v, (list, tuple)):
        v = [v]
    salida = []
    for p in v:
        if isinstance(p, dict):
            p = p.get("producto") or p.get("nombre")
        if p is None:
            continue
        n = sin_tildes(str(p)).strip().strip("'\"").lower()
        if n and n not in salida:
            salida.append(n)
    return salida


def parsear_bool(v) -> bool | None:
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = sin_tildes(str(v)).strip().lower()
    if s in VERDADERO:
        return True
    if s in FALSO:
        return False
    return None


def parsear_familias(v) -> int | None:
    """Entero positivo o None (faltante, cero, negativo o no numérico)."""
    x = numero(v)
    if x is None or x != x or x <= 0 or x > 1e9:
        return None
    return int(round(x))


# ---------- lectura del archivo ----------
def _decodificar(datos: bytes) -> str:
    for cod in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return datos.decode(cod)
        except UnicodeDecodeError:
            continue
    return datos.decode("latin-1", errors="replace")


def _separador(texto: str) -> str:
    for linea in texto.splitlines():
        if linea.strip():
            return ";" if linea.count(";") > linea.count(",") else ","
    return ","


def leer_tabla(ruta) -> tuple[list[dict], list[dict]]:
    """Filas crudas con claves normalizadas (minúsculas, sin tildes) y errores de archivo."""
    ruta = Path(ruta)
    if not ruta.exists() or not ruta.is_file():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    texto = _decodificar(ruta.read_bytes())
    errores: list[dict] = []
    if not texto.strip():
        return [], [{"fila": 0, "campo": "archivo", "motivo": "archivo_vacio", "rechazada": True}]
    if ruta.suffix.lower() == ".json" or texto.lstrip()[:1] in ("[", "{"):
        try:
            datos = json.loads(texto)
        except ValueError as e:
            return [], [{"fila": 0, "campo": "archivo", "motivo": f"json_invalido: {e.msg}",
                         "rechazada": True}]
        if not isinstance(datos, list):
            return [], [{"fila": 0, "campo": "archivo", "motivo": "json_no_es_lista",
                         "rechazada": True}]
        filas = []
        for i, d in enumerate(datos, start=1):
            if isinstance(d, dict):
                filas.append({clave(k): v for k, v in d.items()})
            else:
                filas.append(None)
                errores.append({"fila": i, "campo": "fila", "motivo": "no_es_objeto",
                                "rechazada": True})
        return filas, errores
    try:
        lector = csv.DictReader(io.StringIO(texto), delimiter=_separador(texto))
        filas = []
        for d in lector:
            fila = {clave(k): (v.strip() if isinstance(v, str) else v)
                    for k, v in d.items() if k is not None}
            if any(v not in (None, "") for v in fila.values()):
                filas.append(fila)
    except csv.Error as e:
        return [], [{"fila": 0, "campo": "archivo", "motivo": f"csv_invalido: {e}", "rechazada": True}]
    if not filas:
        errores.append({"fila": 0, "campo": "archivo", "motivo": "sin_filas", "rechazada": True})
    return filas, errores


def _valor(crudo: dict, campo: str):
    for a in ALIAS[campo]:
        v = crudo.get(a)
        if v not in (None, ""):
            return a, v
    return None, None


def normalizar_fila(crudo, n: int, sal=None) -> tuple[dict | None, list[dict]]:
    """Valida una fila. Devuelve (fila o None si se rechaza, errores de esa fila)."""
    errores: list[dict] = []

    def err(campo, motivo, rechazada=False):
        errores.append({"fila": n, "campo": campo, "motivo": motivo, "rechazada": rechazada})

    if not isinstance(crudo, dict):
        err("fila", "no_es_objeto", True)
        return None, errores
    crudo = {clave(k): v for k, v in crudo.items()}
    # fecha (con fecha y hora en columnas separadas, se unen)
    if crudo.get("recibida_en") in (None, "") and crudo.get("fecha") and crudo.get("hora"):
        crudo["recibida_en"] = f"{crudo['fecha']} {crudo['hora']}"
    _, f = _valor(crudo, "recibida_en")
    t = parsear_fecha(f)
    if f is None:
        err("recibida_en", "falta_fecha", True)
    elif t is None:
        err("recibida_en", f"fecha_invalida: {str(f)[:40]}", True)
    _, r = _valor(crudo, "remitente")
    if r is None or not str(r).strip():
        err("remitente", "falta_remitente", True)
    if any(e["rechazada"] for e in errores):
        return None, errores

    fila = {"fila": n, "recibida_en": a_iso(t)}
    try:
        fila["remitente_hash"] = hash_remitente(r, sal if sal is not None else resolver_sal)
    except Exception as e:  # sal ilegible o similar: la fila no se puede guardar sin hash
        err("remitente", f"hash_fallido: {type(e).__name__}", True)
        return None, errores
    _, texto = _valor(crudo, "texto")
    fila["texto"] = "" if texto is None else str(texto)
    for campo in ("lat", "lon"):
        a, v = _valor(crudo, campo)
        x = numero(v)
        if v is not None and x is None:
            err(campo, "no_numerico")
        fila[campo] = x
    _, fam = _valor(crudo, "familias")
    fila["familias"] = parsear_familias(fam)
    if fam is not None and fila["familias"] is None:
        err("familias", f"familias_invalidas: {str(fam)[:20]}")
    _, prods = _valor(crudo, "productos")
    fila["productos"] = parsear_productos(prods)
    _, tp = _valor(crudo, "tipo_punto")
    fila["tipo_punto"] = sin_tildes(str(tp)).strip().lower() if tp is not None else None
    _, canal = _valor(crudo, "canal")
    c = sin_tildes(str(canal)).strip().lower() if canal is not None else "chat"
    if c not in CANALES:
        err("canal", f"canal_desconocido: {c[:20]}")
        c = "chat"
    fila["canal"] = c
    _, lc = _valor(crudo, "lugar_confirmado")
    b = parsear_bool(lc)
    if lc is not None and b is None:
        err("lugar_confirmado", "no_booleano")
    fila["lugar_confirmado"] = bool(b)
    return fila, errores


def leer(ruta, sal=None) -> tuple[list[dict], list[dict]]:
    """(filas_validas, errores) de un CSV o JSON de solicitudes."""
    crudas, errores = leer_tabla(ruta)
    validas = []
    desconocidas = set()
    for i, crudo in enumerate(crudas, start=1):
        if crudo is None:
            continue
        desconocidas |= {k for k in crudo if k not in CONOCIDAS}
        try:
            fila, errs = normalizar_fila(crudo, i, sal)
        except Exception as e:  # defensa final: ninguna fila tumba la lectura
            fila, errs = None, [{"fila": i, "campo": "fila", "motivo": f"error: {type(e).__name__}",
                                 "rechazada": True}]
        errores.extend(errs)
        if fila is not None:
            validas.append(fila)
    for k in sorted(desconocidas):
        errores.append({"fila": 0, "campo": k, "motivo": "columna_desconocida", "rechazada": False})
    return validas, errores
