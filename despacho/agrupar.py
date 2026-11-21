"""Agrupa pedidos por punto de entrega y ventana de tiempo (encargo S3, parte 2).

Es una regla determinista con código: ST-DBSCAN de `triage/cluster.py` sobre el punto y la hora
del pedido, partido por punto de entrega, con familias y kilos sumados y topados por zona (T_z de
`triage/censo.py`). El modelo no decide qué va junto. Se activa con DESPACHOX_AGRUPAR=1.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

from datos import db
from despacho.cierres import normalizar
from triage import censo, cluster, config, geo
from triage.geo import Zona

EPS_S_M = 250        # mismos valores que triage/config PARAMETROS_DEFECTO eps_s_m, eps_t_h
EPS_T_H = 6
VARIABLE = "DESPACHOX_AGRUPAR"
KG_POR_FAMILIA = 10.0          # mismo supuesto que optimizar.KG_POR_FAMILIA
URGENCIA_DEFECTO = 2
_SI = {"1", "si", "sí", "true"}


def activo(valor: bool | None = None) -> bool:
    """True si DESPACHOX_AGRUPAR está en 1/si/sí/true (o si `valor` es True). Apagado por defecto."""
    if valor is not None:
        return bool(valor)
    return os.environ.get(VARIABLE, "").strip().lower() in _SI


def _fecha(texto) -> datetime | None:
    if not texto:
        return None
    try:
        d = datetime.fromisoformat(str(texto))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=db.BOGOTA)


def _familias(p: dict) -> int:
    f = geo.numero(p.get("familias"))
    return int(f) if f and f > 0 else 1


def _kg(p: dict) -> float:
    kg = geo.numero(p.get("kg_estimado"))
    return float(kg) if kg and kg > 0 else _familias(p) * KG_POR_FAMILIA


def _urgencia(p: dict) -> int:
    u = geo.numero(p.get("urgencia"))
    return int(u) if u is not None else URGENCIA_DEFECTO


def _lineas(p: dict) -> list[dict]:
    """Productos con kilos, con el mismo reparto que optimizar._demanda_lineas.

    Los productos sin kilos se reparten lo que falte para completar los kilos del pedido.
    Un pedido sin productos no aporta líneas (es un mercado genérico por kilos).
    """
    try:
        crudo = json.loads(p.get("productos") or "[]")
    except (TypeError, ValueError):
        return []
    if not isinstance(crudo, list):
        return []
    con_kg, sin_kg = [], []
    for l in crudo:
        l = {"producto": l} if isinstance(l, str) else l
        if not isinstance(l, dict):
            continue
        nombre = str(l.get("producto") or "").strip()
        if not nombre:
            continue
        kg = geo.numero(l.get("kg")) or 0.0
        (con_kg if kg > 0 else sin_kg).append({"producto": nombre, "kg": max(0.0, kg)})
    if sin_kg:
        resto = _kg(p) - sum(l["kg"] for l in con_kg)
        if resto <= 0:
            resto = KG_POR_FAMILIA * _familias(p) * len(sin_kg) / (len(con_kg) + len(sin_kg))
        for l in sin_kg:
            l["kg"] = resto / len(sin_kg)
    return con_kg + sin_kg


@dataclass
class Grupo:
    clave: str
    punto_id: int
    pedido_ids: list[int]
    pedidos: list[dict]
    familias: int
    familias_declaradas: int
    tope_familias: int | None
    sobre_tope: bool
    kg: float
    kg_declarados: float
    productos: list[dict]
    urgencia: int
    limite_en: str | None
    creado_en: str
    zona: str | None
    critico: bool

    @property
    def madre(self) -> dict:
        """El pedido más antiguo (menor creado_en, luego menor id)."""
        return min(self.pedidos, key=lambda p: (_fecha(p.get("creado_en")) or datetime.max.replace(
            tzinfo=db.BOGOTA), p["id"]))

    def como_pedido(self) -> dict:
        """Una fila con la forma de `pedidos` para que `planificar` la trate como un pedido más."""
        return {
            "id": self.madre["id"], "creado_en": self.creado_en, "punto_id": self.punto_id,
            "familias": self.familias, "kg_estimado": round(self.kg, 3),
            "productos": json.dumps(self.productos, ensure_ascii=False),
            "urgencia": self.urgencia, "limite_en": self.limite_en, "estado": "confirmado",
            "origen": "mensaje", "texto_original": None, "remitente_hash": None,
            "duplicado_de": None, "grupo": self.clave, "miembros": list(self.pedido_ids),
        }


def _clave(punto_id: int, ids: list[int]) -> str:
    texto = f"{punto_id}:" + ",".join(str(i) for i in ids)
    return hashlib.sha1(texto.encode("utf-8")).hexdigest()[:12]


def _zonas(zonas: list | None, p: dict) -> list[Zona]:
    if zonas is None:
        zonas = censo.zonas_desde_semilla(p)
    salida = []
    for i, z in enumerate(zonas, start=1):
        if isinstance(z, Zona):
            salida.append(z)
        else:
            d = dict(z)
            d.setdefault("id", i)
            if d["id"] is None:
                d["id"] = i
            salida.append(Zona.desde_fila(d))
    return salida


def _armar(punto_id: int, miembros: list[dict], punto: dict, zona: Zona | None, p: dict) -> Grupo:
    miembros = sorted(miembros, key=lambda x: x["id"])
    ids = [m["id"] for m in miembros]
    declaradas = sum(_familias(m) for m in miembros)
    kg_decl = sum(_kg(m) for m in miembros)
    tope = censo.tope_familias(zona, p) if zona is not None else None
    familias = min(declaradas, tope) if tope is not None else declaradas
    factor = familias / declaradas if declaradas else 1.0
    # Productos sumados por nombre normalizado; se muestra el nombre del pedido más antiguo.
    por_nombre: dict[str, dict] = {}
    for m in sorted(miembros, key=lambda x: (_fecha(x.get("creado_en")) or datetime.max.replace(
            tzinfo=db.BOGOTA), x["id"])):
        for l in _lineas(m):
            n = normalizar(l["producto"])
            fila = por_nombre.setdefault(n, {"producto": l["producto"], "kg": 0.0})
            fila["kg"] += l["kg"]
    productos = [{"producto": f["producto"], "kg": round(f["kg"] * factor, 3)}
                 for f in por_nombre.values()]
    limites = [(d, m["limite_en"]) for m in miembros if (d := _fecha(m.get("limite_en")))]
    creados = [(d, m["creado_en"]) for m in miembros if (d := _fecha(m.get("creado_en")))]
    return Grupo(
        clave=_clave(punto_id, ids), punto_id=punto_id, pedido_ids=ids, pedidos=miembros,
        familias=familias, familias_declaradas=declaradas, tope_familias=tope,
        sobre_tope=tope is not None and declaradas > tope,
        kg=kg_decl * factor, kg_declarados=kg_decl, productos=productos,
        urgencia=max(_urgencia(m) for m in miembros),
        limite_en=min(limites)[1] if limites else None,
        creado_en=min(creados)[1] if creados else miembros[0].get("creado_en"),
        zona=zona.nombre if zona is not None else None,
        critico=bool(geo.numero(punto.get("critico"))),
    )


def _agrupables(pedidos: list[dict], puntos: dict[int, dict]) -> list[dict]:
    return [q for q in pedidos if q.get("punto_id") is not None and q["punto_id"] in puntos
            and q.get("origen") != "silencio"]


def sin_agrupar(pedidos: list[dict], puntos: dict[int, dict]) -> list[dict]:
    """Los pedidos que `agrupar` deja fuera: sin punto, con punto desconocido u origen silencio."""
    dentro = {id(q) for q in _agrupables(pedidos, puntos)}
    return [q for q in pedidos if id(q) not in dentro]


def st_dbscan_min2(lat, lon, t_horas, eps_s_m: float, eps_t_h: float) -> np.ndarray:
    """Misma partición que `cluster.st_dbscan(..., min_samples=2)`, en O(n log n).

    Con min_samples=2 todo punto con un vecino es núcleo y no hay puntos frontera, así que los
    clústeres son las componentes conexas del grafo «a menos de eps_s y eps_t». Como muchos
    pedidos comparten las coordenadas del punto, basta unir cada pedido con el siguiente en el
    tiempo dentro de su lugar, y con el anterior y el siguiente de cada lugar vecino. Las
    etiquetas pueden numerarse distinto que en st_dbscan; los grupos son los mismos.
    """
    lat = np.atleast_1d(np.asarray(lat, dtype=float))
    lon = np.atleast_1d(np.asarray(lon, dtype=float))
    t = np.atleast_1d(np.asarray(t_horas, dtype=float))
    n = len(lat)
    etiquetas = np.full(n, cluster.RUIDO, dtype=int)
    idx = np.flatnonzero(np.isfinite(lat) & np.isfinite(lon) & np.isfinite(t))
    if len(idx) < 2:
        return etiquetas
    lat0, lon0 = float(np.mean(lat[idx])), float(np.mean(lon[idx]))
    lugares, lugar = np.unique(np.c_[lat[idx], lon[idx]], axis=0, return_inverse=True)
    lugar = np.asarray(lugar).ravel()
    orden = idx[np.lexsort((t[idx], lugar))]          # por lugar y luego por hora
    lugar_ord = lugar[np.lexsort((t[idx], lugar))]
    cortes = np.flatnonzero(np.diff(lugar_ord)) + 1
    por_lugar = np.split(orden, cortes)
    origen, destino = [], []
    # Mismo lugar: consecutivos en el tiempo.
    mismo = (lugar_ord[1:] == lugar_ord[:-1]) & (np.diff(t[orden]) <= eps_t_h)
    origen.append(orden[:-1][mismo])
    destino.append(orden[1:][mismo])
    # Lugares vecinos: anterior y siguiente en el tiempo del otro lugar.
    x, y = geo.proyectar(lugares[:, 0], lugares[:, 1], lat0, lon0)
    for a, b in cKDTree(np.c_[x, y]).query_pairs(eps_s_m, output_type="ndarray"):
        pa, pb = por_lugar[a], por_lugar[b]
        tb = t[pb]
        pos = np.searchsorted(tb, t[pa])
        for k in (pos - 1, pos):
            ok = (k >= 0) & (k < len(pb))
            cerca = np.zeros(len(pa), dtype=bool)
            cerca[ok] = np.abs(tb[k[ok]] - t[pa[ok]]) <= eps_t_h
            origen.append(pa[cerca])
            destino.append(pb[k[cerca]])
    o, d = np.concatenate(origen), np.concatenate(destino)
    grafo = coo_matrix((np.ones(len(o)), (o, d)), shape=(n, n))
    _, comp = connected_components(grafo, directed=False)
    tamano = np.bincount(comp, minlength=n)
    unido = tamano[comp] >= 2
    etiquetas[unido] = comp[unido]
    return etiquetas


def agrupar(pedidos: list[dict], puntos: dict[int, dict], ahora: datetime | None = None,
            zonas: list | None = None, params: dict | None = None) -> list[Grupo]:
    """Grupos por punto de entrega y ventana de tiempo, ordenados por urgencia y límite."""
    p = config.completar(params) if params is None or "T_min" not in params else params
    validos = sorted(_agrupables(pedidos, puntos), key=lambda q: q["id"])
    if not validos:
        return []
    # Sin `ahora`, el más reciente: el ST-DBSCAN solo usa diferencias de tiempo.
    fechas = [_fecha(q.get("creado_en")) for q in validos]
    if ahora is None:
        ahora = max((f for f in fechas if f is not None), default=datetime.now(db.BOGOTA))
    elif ahora.tzinfo is None:
        ahora = ahora.replace(tzinfo=db.BOGOTA)
    lat = np.array([geo.numero(puntos[q["punto_id"]].get("lat")) or np.nan for q in validos])
    lon = np.array([geo.numero(puntos[q["punto_id"]].get("lon")) or np.nan for q in validos])
    t = np.array([(f - ahora).total_seconds() / 3600 if f else np.nan for f in fechas])
    etiquetas = st_dbscan_min2(lat, lon, t, EPS_S_M, EPS_T_H)

    # Un grupo = un clúster y un punto; el ruido va solo.
    cubetas: dict[tuple, list[dict]] = {}
    for q, e in zip(validos, etiquetas):
        llave = (q["punto_id"], int(e)) if e != cluster.RUIDO else (q["punto_id"], "r", q["id"])
        cubetas.setdefault(llave, []).append(q)

    lista_zonas = _zonas(zonas, p)
    por_id = {z.id: z for z in lista_zonas}
    zona_de_punto: dict[int, Zona | None] = {}
    for pid in sorted({q["punto_id"] for q in validos}):
        pt = puntos[pid]
        zid, _ = geo.asignar_zona(pt.get("lat"), pt.get("lon"), lista_zonas, params=p)
        zona_de_punto[pid] = por_id.get(zid) if zid is not None else None

    grupos = [_armar(pid, miembros, puntos[pid], zona_de_punto[pid], p)
              for (pid, *_), miembros in cubetas.items()]
    lejano = datetime.max.replace(tzinfo=db.BOGOTA)
    grupos.sort(key=lambda g: (-g.urgencia, _fecha(g.limite_en) or lejano, g.punto_id, g.clave))
    return grupos


_SQL_PUNTOS = "SELECT * FROM puntos"


def _desde_base(con: sqlite3.Connection, estado: str, ahora: datetime | None) -> list[Grupo]:
    filas = [dict(r) for r in con.execute(
        "SELECT * FROM pedidos WHERE estado=? AND duplicado_de IS NULL AND punto_id IS NOT NULL "
        "ORDER BY id", (estado,))]
    puntos = {r["id"]: dict(r) for r in con.execute(_SQL_PUNTOS)}
    return agrupar(filas, puntos, ahora=ahora)


def agrupar_desde_base(con: sqlite3.Connection, ahora: datetime | None = None) -> list[Grupo]:
    """Grupos de los pedidos confirmados de la base."""
    return _desde_base(con, "confirmado", ahora)


def grupos_nuevos(con: sqlite3.Connection, ahora: datetime | None = None) -> list[Grupo]:
    """Grupos de los pedidos nuevos (para «Por revisar» del tablero)."""
    return _desde_base(con, "nuevo", ahora)


def _cronometro(n: int = 15_000, semilla: int = 2026) -> None:
    """Agrupa n pedidos sintéticos sobre puntos.csv y barrios.csv y mide el tiempo."""
    import csv
    import time
    from datetime import timedelta
    from pathlib import Path

    raiz = Path(__file__).resolve().parent.parent / "datos" / "semilla"
    puntos: dict[int, dict] = {}
    with open(raiz / "puntos.csv", encoding="utf-8-sig", newline="") as f:
        for d in csv.DictReader(f):
            puntos[int(d["id"])] = {"id": int(d["id"]), "nombre": d["nombre"], "lat": float(d["lat"]),
                                    "lon": float(d["lon"]), "critico": int(d["critico"])}
    siguiente = max(puntos) + 1
    with open(raiz / "barrios.csv", encoding="utf-8-sig", newline="") as f:
        for d in csv.DictReader(f):
            puntos[siguiente] = {"id": siguiente, "nombre": d["nombre"], "lat": float(d["lat"]),
                                 "lon": float(d["lon"]), "critico": 0}
            siguiente += 1
    rng = np.random.default_rng(semilla)
    ahora = datetime(2026, 11, 21, 12, 0, tzinfo=db.BOGOTA)
    ids_puntos = sorted(puntos)
    productos = ["arroz", "frijol", "aceite", "panela", "leche", "agua", "verdura"]
    pedidos = []
    for i in range(1, n + 1):
        fam = int(rng.integers(1, 20))
        elegidos = rng.choice(productos, size=int(rng.integers(1, 4)), replace=False)
        pedidos.append({
            "id": i, "creado_en": (ahora - timedelta(minutes=int(rng.integers(0, 72 * 60))))
            .isoformat(timespec="seconds"),
            "punto_id": int(rng.choice(ids_puntos)), "familias": fam, "kg_estimado": fam * 10.0,
            "productos": json.dumps([{"producto": str(x), "kg": 0} for x in elegidos]),
            "urgencia": int(rng.integers(1, 4)),
            "limite_en": (ahora + timedelta(hours=int(rng.integers(2, 48)))).isoformat(timespec="seconds"),
            "estado": "confirmado", "origen": "mensaje", "texto_original": None,
            "remitente_hash": None, "duplicado_de": None,
        })
    t0 = time.perf_counter()
    grupos = agrupar(pedidos, puntos, ahora=ahora)
    seg = time.perf_counter() - t0
    topados = sum(g.sobre_tope for g in grupos)
    print(f"{n} pedidos sobre {len(puntos)} puntos (72 h) -> {len(grupos)} grupos "
          f"({topados} sobre tope) en {seg:.2f} s")


if __name__ == "__main__":
    _cronometro()
