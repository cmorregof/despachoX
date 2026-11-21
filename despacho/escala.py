"""Medición de la mesa con muchos pedidos (encargo S3): tablero y optimizador sobre una base temporal.

    python -m despacho.escala --tablero --pedidos 15000              # consultas del tablero y AppTest
    python -m despacho.escala --planificar 50 100 250 500 1000       # planificar por tamaño
    python -m despacho.escala --planificar 15000 --agrupar           # con DESPACHOX_AGRUPAR=1
    python -m despacho.escala --todo --json salida.json

Todo corre en local: base temporal con la semilla sintética, puntos de entrega en todos los barrios
de `datos/semilla/barrios.csv` y pedidos sintéticos sin datos de nadie. No toca la base compartida,
ni Railway, ni Telegram, ni la API de Anthropic. Los resultados se reportan tal como salen; el
documento es `docs/ESCALA_DESPACHO.md`.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import psutil
except ImportError:          # la memoria queda sin medir
    psutil = None

from datos import db
from despacho import semilla as mod_semilla

RAIZ = Path(__file__).resolve().parent.parent
BARRIOS = RAIZ / "datos" / "semilla" / "barrios.csv"
HORAS_ATRAS = 3                         # los pedidos llegaron en las últimas 3 horas: ninguno nace vencido
LIMITE_H = {3: 4, 2: 10, 1: 20}          # mismos valores que la semilla
FRACCION_CRITICOS = 0.10                 # puntos críticos entre los barrios añadidos (SUPUESTO)
SEMILLA = 2026
# Frases sintéticas que a veces acompañan al pedido, para que el resumen del modelo tenga qué leer.
EXTRAS = ["", "", "", "", "hay bebés y no tenemos leche", "hay varios adultos mayores enfermos",
          "no tenemos agua desde ayer", "la carne y la leche se nos dañaron porque no hay luz",
          "una señora necesita insulina", "somos del albergue de la escuela", "ya nos llegó algo pero no alcanzó",
          "urgente por favor", "no sé cuántos somos, llegaron más familias anoche", "mandan desde la junta",
          "el camino está feo pero entra una moto", "???", "necesitamos pañales y leche en polvo"]


# ---------- base sintética ----------

def base_escala(ruta: Path, n_pedidos: int, fraccion_nuevo: float = 0.5, semilla: int = SEMILLA,
                factor_lotes: float | None = None, ahora: datetime | None = None):
    """Base temporal: semilla completa, un punto por barrio y `n_pedidos` sintéticos.

    fraccion_nuevo: parte de los pedidos en estado `nuevo` (el resto, `confirmado`).
    factor_lotes: multiplica los kilos de cada lote. None = lo justo para que el inventario no
    sea el cuello de botella (demanda confirmada × 1,3 sobre la semilla), para medir el ruteo.
    Devuelve (con, ahora, resumen).
    """
    rng = random.Random(semilla)
    ahora = ahora or datetime.now(db.BOGOTA).replace(microsecond=0)
    con = db.conectar(ruta)
    mod_semilla.cargar(reiniciar=True, con=con)
    con.execute("DELETE FROM pedidos")
    # Un punto de entrega por barrio o vereda que aún no sea punto de la semilla.
    puntos = {r["barrio"]: dict(r) for r in con.execute("SELECT * FROM puntos")}
    siguiente = con.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM puntos").fetchone()[0]
    with open(BARRIOS, encoding="utf-8-sig", newline="") as f:
        for b in csv.DictReader(f):
            if b["nombre"] in puntos:
                continue
            critico = int(rng.random() < FRACCION_CRITICOS)
            tipo = "Albergue temporal" if critico else rng.choice(mod_semilla.TIPOS_PUNTO)
            fila = {"id": siguiente, "nombre": f"{tipo} {b['nombre']}", "barrio": b["nombre"],
                    "comuna": b["comuna"], "lat": float(b["lat"]), "lon": float(b["lon"]), "critico": critico}
            con.execute("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                        tuple(fila.values()))
            puntos[b["nombre"]] = fila
            siguiente += 1
    lista = list(puntos.values())
    # Unos barrios piden mucho más que otros (pesos exponenciales), como en un sismo real.
    pesos = [rng.expovariate(1.0) + 0.05 for _ in lista]
    filas, kg_confirmado = [], 0.0
    for i in range(1, n_pedidos + 1):
        p = rng.choices(lista, weights=pesos)[0]
        familias = rng.randint(3, 40)
        productos = rng.sample(mod_semilla.NO_PERECEDEROS, rng.randint(1, 3))
        if rng.random() < 0.6:
            productos += rng.sample(mod_semilla.PERECEDEROS, 1)
        lineas = [{"producto": x, "kg": round(familias * mod_semilla.KG_POR_FAMILIA[x], 1)} for x in productos]
        kg = round(sum(l["kg"] for l in lineas), 1)
        urgencia = 3 if p["critico"] else rng.choice([1, 2, 2, 3])
        creado = ahora - timedelta(minutes=rng.randint(1, HORAS_ATRAS * 60))
        estado = "nuevo" if rng.random() < fraccion_nuevo else "confirmado"
        if estado == "confirmado":
            kg_confirmado += kg
        filas.append((i, creado.isoformat(timespec="seconds"), p["id"], familias, kg,
                      json.dumps(lineas, ensure_ascii=False), urgencia,
                      (creado + timedelta(hours=LIMITE_H[urgencia])).isoformat(timespec="seconds"), estado,
                      f"Somos {familias} familias en {p['barrio']}, necesitamos {', '.join(productos)}."
                      + (f" {extra}." if (extra := rng.choice(EXTRAS)) else ""),
                      hashlib.sha256(f"sintetico-{semilla}-{i}".encode()).hexdigest()[:16]))
    con.executemany("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,"
                    "limite_en,estado,texto_original,remitente_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?)", filas)
    kg_lotes = con.execute("SELECT SUM(kg) FROM lotes").fetchone()[0] or 1.0
    if factor_lotes is None:
        factor_lotes = max(1.0, round(kg_confirmado * 1.3 / kg_lotes, 2))
    if factor_lotes != 1.0:
        con.execute("UPDATE lotes SET kg = ROUND(kg * ?, 1)", (factor_lotes,))
    con.commit()
    resumen = {"pedidos": n_pedidos, "nuevos": sum(1 for f in filas if f[8] == "nuevo"),
               "confirmados": sum(1 for f in filas if f[8] == "confirmado"), "puntos": len(lista),
               "puntos_criticos": sum(p["critico"] for p in lista), "kg_confirmado": round(kg_confirmado, 1),
               "factor_lotes": factor_lotes, "kg_lotes": round(kg_lotes * factor_lotes, 1),
               "vehiculos": con.execute("SELECT COUNT(*) FROM vehiculos").fetchone()[0],
               "capacidad_flota_kg": con.execute("SELECT SUM(capacidad_kg) FROM vehiculos").fetchone()[0]}
    return con, ahora, resumen


def _ruta_temporal(nombre: str) -> Path:
    return Path(tempfile.mkdtemp(prefix="escala_")) / f"{nombre}.db"


def _memoria_mb() -> float | None:
    return psutil.Process().memory_info().rss / 2**20 if psutil else None


# ---------- tablero ----------

def _cronometrar(f, *args, repeticiones: int = 3) -> tuple[float, object]:
    """Mediana de `repeticiones` corridas, en segundos, y el último resultado."""
    tiempos, r = [], None
    for _ in range(repeticiones):
        t = time.perf_counter()
        r = f(*args)
        tiempos.append(time.perf_counter() - t)
    return statistics.median(tiempos), r


def medir_consultas(con) -> dict:
    """Segundos (mediana de 3) de cada lectura de tablero/datos.py, agrupadas por pestaña."""
    from tablero import datos as T
    plan = T.plan_vigente(con)
    medidas = {}
    for nombre, f, args in [
        ("plan_vigente", T.plan_vigente, (con,)),
        ("rutas", T.rutas, (con, plan)),
        ("por_revisar", T.por_revisar, (con,)),
        ("grupos_por_revisar", T.grupos_por_revisar, (con,)),
        ("indicadores", T.indicadores, (con, plan)),
        ("sin_atender", T.sin_atender, (con, plan)),
        ("cierres_sin_aplicar", T.cierres_sin_aplicar, (con, plan)),
        ("territorio", T.territorio, (con,)),
        ("informe", T.informe, (con,)),
        ("bitacora", T.bitacora, (con,)),
    ]:
        s, r = _cronometrar(f, *args)
        medidas[nombre] = round(s, 3)
    pestanas = {"Mesa": ["plan_vigente", "rutas", "por_revisar", "grupos_por_revisar", "indicadores",
                         "cierres_sin_aplicar"],
                "Plan en detalle": ["sin_atender"], "Territorio": ["territorio"],
                "Informe": ["informe"], "Bitácora": ["bitacora"]}
    return {"consultas_s": medidas,
            "por_pestana_s": {k: round(sum(medidas[x] for x in v), 3) for k, v in pestanas.items()}}


def medir_apptest(ruta: Path, espera_s: int = 900) -> dict:
    """Pinta `tablero/app.py` con streamlit.testing.v1.AppTest sobre la base `ruta`.

    Todas las pestañas se pintan en la misma corrida (st.tabs), así que se mide el total y, por
    aparte, cuánto de ese total se fue en cada función de datos, envuelta con un cronómetro.
    """
    from streamlit.testing.v1 import AppTest
    from tablero import datos as T
    db.RUTA_DB = Path(ruta)
    db.conectar.__defaults__ = (Path(ruta),)     # la ruta por defecto se fijó al importar
    acumulado: dict[str, float] = {}

    def envolver(nombre):
        original = getattr(T, nombre)

        def medida(*a, **k):
            t = time.perf_counter()
            try:
                return original(*a, **k)
            finally:
                acumulado[nombre] = acumulado.get(nombre, 0.0) + time.perf_counter() - t
        return original, medida

    # `filas` no se envuelve: la llaman las otras funciones y se contaría dos veces.
    nombres = ["plan_vigente", "rutas", "por_revisar", "grupos_por_revisar", "indicadores", "sin_atender",
               "cierres_sin_aplicar", "cambios_del_recalculo", "territorio", "informe", "bitacora"]
    originales = {}
    for n in nombres:
        originales[n], medida = envolver(n)
        setattr(T, n, medida)
    antes = _memoria_mb()
    try:
        t = time.perf_counter()
        at = AppTest.from_file(str(RAIZ / "tablero" / "app.py"), default_timeout=espera_s)
        at.run()
        total = time.perf_counter() - t
        error = str(at.exception[0].value) if at.exception else None
        elementos = {"markdown": len(at.markdown), "dataframe": len(at.dataframe), "button": len(at.button)}
    finally:
        for n, f in originales.items():
            setattr(T, n, f)
    return {"segundos_total": round(total, 2), "error": error, "elementos": elementos,
            "datos_s": {k: round(v, 3) for k, v in sorted(acumulado.items())},
            "render_s": round(total - sum(acumulado.values()), 2),
            "memoria_mb_antes": antes and round(antes), "memoria_mb_despues": _memoria_mb() and round(_memoria_mb())}


def medir_tablero(n_pedidos: int, fraccion_nuevo: float = 0.5, apptest: bool = True,
                  agrupar: bool = False) -> dict:
    """Con `agrupar`, la medición corre con DESPACHOX_AGRUPAR=1: «Por revisar» muestra grupos."""
    ruta = _ruta_temporal(f"tablero_{n_pedidos}")
    t = time.perf_counter()
    con, ahora, base = base_escala(ruta, n_pedidos, fraccion_nuevo)
    base["segundos_generar"] = round(time.perf_counter() - t, 1)
    previo = os.environ.get("DESPACHOX_AGRUPAR")
    os.environ["DESPACHOX_AGRUPAR"] = "1" if agrupar else "0"
    try:
        r = {"base": base, "agrupar": agrupar, "consultas": medir_consultas(con)}
        con.close()
        if apptest:
            r["apptest"] = medir_apptest(ruta)
    finally:
        if previo is None:
            os.environ.pop("DESPACHOX_AGRUPAR", None)
        else:
            os.environ["DESPACHOX_AGRUPAR"] = previo
    return r


# ---------- optimizador ----------

def medir_planificar(n_pedidos: int, segundos: int = 8, g=None, agrupar: bool = False) -> dict:
    """Un plan con `n_pedidos` confirmados, la flota de la semilla y el límite de hoy."""
    from despacho import matriz as mod_matriz
    from despacho import optimizar
    ruta = _ruta_temporal(f"plan_{n_pedidos}")
    t = time.perf_counter()
    con, ahora, base = base_escala(ruta, n_pedidos, fraccion_nuevo=0.0)
    base["segundos_generar"] = round(time.perf_counter() - t, 1)
    if g is None:
        from despacho import red
        g = red.cargar()
    matriz_s = {"total": 0.0}
    original = mod_matriz.calcular

    def calcular_medido(*a, **k):
        t0 = time.perf_counter()
        try:
            return original(*a, **k)
        finally:
            matriz_s["total"] += time.perf_counter() - t0
    mod_matriz.calcular = calcular_medido
    previo = os.environ.get("DESPACHOX_AGRUPAR")
    os.environ["DESPACHOX_AGRUPAR"] = "1" if agrupar else "0"
    antes = _memoria_mb()
    try:
        t = time.perf_counter()
        plan_id = optimizar.planificar(con, motivo="escala", segundos=segundos, g=g, ahora=ahora)
        total = time.perf_counter() - t
    finally:
        mod_matriz.calcular = original
        if previo is None:
            os.environ.pop("DESPACHOX_AGRUPAR", None)
        else:
            os.environ["DESPACHOX_AGRUPAR"] = previo
    fila = con.execute("SELECT segundos_calculo, resumen FROM planes WHERE id=?", (plan_id,)).fetchone()
    resumen = json.loads(fila["resumen"]) if fila else {}
    paradas = con.execute("SELECT COUNT(*) FROM paradas WHERE plan_id=?", (plan_id,)).fetchone()[0]
    con.close()
    crit = resumen.get("criticos") or {}
    grupos = resumen.get("grupos") or {}
    return {"n": n_pedidos, "agrupar": agrupar, "base": base, "plan_id": plan_id,
            "segundos_total": round(total, 1), "segundos_calculo": fila["segundos_calculo"] if fila else None,
            "segundos_matrices": round(matriz_s["total"], 1), "limite_solver_s": segundos,
            "vacio": resumen.get("vacio"), "motivo_vacio": resumen.get("motivo_vacio"),
            "considerados": resumen.get("pedidos_considerados"), "atendidos": resumen.get("pedidos_atendidos"),
            "paradas": paradas, "kg_planeados": resumen.get("kg_planeados"),
            "criticos_paradas": crit.get("paradas"), "criticos_a_tiempo": crit.get("a_tiempo"),
            "sin_atender": len(resumen.get("sin_atender") or []),
            "motivos_sin_atender": sorted({x.get("motivo") for x in resumen.get("sin_atender") or []}),
            "grupos": len(grupos) or None,
            "pedidos_en_grupos": sum(len(v) for v in grupos.values()) or None,
            "solver": resumen.get("solver"),
            "memoria_mb_antes": antes and round(antes), "memoria_mb_despues": _memoria_mb() and round(_memoria_mb())}


# ---------- informe ----------

def maquina() -> dict:
    cpu = platform.processor() or platform.machine()
    try:
        import subprocess
        if sys.platform == "darwin":
            cpu = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True,
                                 text=True, timeout=5).stdout.strip() or cpu
    except Exception:  # noqa: BLE001
        pass
    return {"sistema": f"{platform.system()} {platform.release()}", "cpu": cpu,
            "memoria_gb": round(psutil.virtual_memory().total / 2**30) if psutil else None,
            "python": platform.python_version(), "fecha": datetime.now(db.BOGOTA).isoformat(timespec="minutes")}


def tabla_planificar(filas: list[dict]) -> str:
    out = ["| Pedidos | Grupos | Segundos totales | De ellos, matrices | Considerados | Atendidos | Críticos a tiempo | Sin atender |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in filas:
        crit = f"{r['criticos_a_tiempo']} de {r['criticos_paradas']}" if r["criticos_paradas"] is not None else "—"
        out.append(f"| {r['n']} | {r['grupos'] or '—'} | {r['segundos_total']} | {r['segundos_matrices']} | "
                   f"{r['considerados']} | {r['atendidos']} | {crit} | {r['sin_atender']} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tablero", action="store_true", help="mide las consultas del tablero y el AppTest")
    ap.add_argument("--pedidos", type=int, default=15000, help="pedidos para la medición del tablero")
    ap.add_argument("--sin-apptest", action="store_true")
    ap.add_argument("--planificar", type=int, nargs="*", help="tamaños para medir planificar")
    ap.add_argument("--segundos", type=int, default=8, help="límite del solver (el de hoy: 8)")
    ap.add_argument("--agrupar", action="store_true", help="tablero y planificar con DESPACHOX_AGRUPAR=1")
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--json", help="guarda todo el resultado")
    a = ap.parse_args(argv)
    salida = {"maquina": maquina(), "tablero": None, "planificar": []}
    if a.tablero or a.todo:
        salida["tablero"] = medir_tablero(a.pedidos, apptest=not a.sin_apptest, agrupar=a.agrupar)
        print(json.dumps(salida["tablero"], ensure_ascii=False, indent=1))
    tamanos = a.planificar if a.planificar else ([50, 100, 250, 500, 1000] if a.todo else [])
    if tamanos:
        from despacho import red
        g = red.cargar()
        for n in tamanos:
            r = medir_planificar(n, a.segundos, g, a.agrupar)
            salida["planificar"].append(r)
            print(json.dumps({k: v for k, v in r.items() if k not in ("base", "solver")}, ensure_ascii=False),
                  flush=True)
        print(tabla_planificar(salida["planificar"]))
    if a.json:
        Path(a.json).write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
