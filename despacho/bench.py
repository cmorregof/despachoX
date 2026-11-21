"""Mide cuánto tarda el optimizador: primera optimización y reoptimización tras cerrar un tramo.

Uso, desde la raíz del repositorio:
    .venv/bin/python -m despacho.bench                         # medición completa (ver BENCH.md)
    .venv/bin/python -m despacho.bench --rapido                # prueba corta: tamaño demo, 1 repetición
    .venv/bin/python -m despacho.bench --tamanos demo,medio --repeticiones 3 --segundos 3
    .venv/bin/python -m despacho.bench --salida /tmp/bench.md  # además guarda la tabla en un archivo

Qué mide, por tamaño y por repetición (base nueva cada vez, red vial ya cargada):
  primera       `optimizar.planificar` con todos los pedidos confirmados (matrices + solver + escritura).
  reoptimizar   se aprueba ese plan, se confirma el cierre de la avenida del Centro (arista de
                datos/semilla/vias.csv) y se mide `recalcular.recalcular`.
El solver de OR-Tools corre hasta su límite de tiempo (`--segundos`), así que cada medición vale
aproximadamente ese límite más el costo de las matrices y de escribir el plan. El número útil para
el pitch es el total, y la columna «extra» (total menos el límite) dice cuánto cuesta lo demás.

Tamaños (pedidos sintéticos con semilla fija; los puntos son los 15 de la semilla, así que varios
pedidos comparten punto). La flota crece con los pedidos para que el modelo sea comparable:
  demo    18 pedidos, 5 vehículos  (la semilla con el pedido 21 confirmado, como en el guion)
  medio   60 pedidos, 12 vehículos
  grande  150 pedidos, 25 vehículos
Reporta además nproc, CPU, memoria, versión de OR-Tools y la carga del sistema durante cada medición
(uso de CPU de TODA la máquina, leído de /proc/stat, no solo de este proceso).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import random
import resource
import shutil
import statistics
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DESPACHOX_SIN_RED", "1")
if not os.environ.get("DESPACHOX_GRAFO") and (RAIZ / "despliegue/grafo/manizales_region.graphml").exists():
    os.environ["DESPACHOX_GRAFO"] = str(RAIZ / "despliegue/grafo/manizales_region.graphml")

TAMANOS = {"demo": (18, 5), "medio": (60, 12), "grande": (150, 25)}
TIPOS_FLOTA = [("camion", 3000), ("campero", 600), ("camion", 2000), ("campero", 600), ("moto", 40)]


def cpu_ocupada() -> tuple[int, int]:
    """(ocupado, total) en ticks de toda la máquina, desde /proc/stat."""
    with open("/proc/stat") as f:
        v = [int(x) for x in f.readline().split()[1:]]
    total = sum(v[:8])
    return total - v[3] - v[4], total          # menos idle e iowait


def info_maquina() -> dict:
    cpu = "?"
    try:
        with open("/proc/cpuinfo") as f:
            cpu = next(l.split(":", 1)[1].strip() for l in f if l.startswith("model name"))
    except (OSError, StopIteration):
        cpu = platform.processor() or platform.machine()
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for l in f:
                k, v = l.split(":")
                mem[k] = int(v.split()[0]) // 1024
    except OSError:
        pass
    import ortools
    return {"nproc": os.cpu_count(), "cpu": cpu, "mem_total_mb": mem.get("MemTotal"),
            "mem_disponible_mb": mem.get("MemAvailable"), "ortools": ortools.__version__,
            "python": platform.python_version(), "carga_inicial": os.getloadavg(),
            "fecha": datetime.now().astimezone().isoformat(timespec="seconds")}


def construir_base(ruta: Path, n_pedidos: int, n_vehiculos: int) -> None:
    """Base con la semilla y pedidos y flota sintéticos del tamaño pedido."""
    for s in ("", "-wal", "-shm"):
        Path(str(ruta) + s).unlink(missing_ok=True)
    from datos import db
    from despacho import semilla
    con = db.conectar(ruta)
    semilla.cargar(reiniciar=True, con=con)
    ahora = datetime.now(db.BOGOTA).replace(microsecond=0)
    con.execute("UPDATE pedidos SET estado='confirmado'")        # tamaño demo: el pedido 21 ya confirmado
    if n_pedidos == 18:
        con.execute("DELETE FROM pedidos WHERE id IN (18,19,20)")
        con.execute("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,limite_en,"
                    "estado,texto_original) VALUES (21,?,14,40,80,?,2,?, 'confirmado','sintético')",
                    (ahora.isoformat(), json.dumps([{"producto": "arroz", "kg": 40}, {"producto": "leche", "kg": 40}]),
                     (ahora + timedelta(hours=10)).isoformat()))
    else:
        con.execute("DELETE FROM pedidos")
        rng = random.Random(7000 + n_pedidos)
        puntos = [r["id"] for r in con.execute("SELECT id FROM puntos")]
        criticos = {r["id"] for r in con.execute("SELECT id FROM puntos WHERE critico=1")}
        productos = ["arroz", "frijol", "lenteja", "aceite", "panela", "agua", "leche", "pan", "huevos", "fruta"]
        for i in range(1, n_pedidos + 1):
            punto = rng.choice(puntos)
            fam = rng.randint(8, 40)
            lineas = [{"producto": p, "kg": round(fam * rng.choice([0.5, 1, 2]), 1)} for p in rng.sample(productos, rng.randint(1, 3))]
            urg = 3 if punto in criticos else rng.choice([1, 2, 2, 3])
            con.execute("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,productos,urgencia,limite_en,"
                        "estado,texto_original) VALUES (?,?,?,?,?,?,?,?, 'confirmado','sintético')",
                        (i, (ahora - timedelta(minutes=rng.randint(5, 120))).isoformat(), punto, fam,
                         round(sum(l["kg"] for l in lineas), 1), json.dumps(lineas), urg,
                         (ahora + timedelta(hours={3: 4, 2: 10, 1: 20}[urg])).isoformat()))
        # inventario holgado para que el límite sea la ruta y no el stock
        con.execute("UPDATE lotes SET kg = kg * ?", (max(1.0, n_pedidos / 10),))
    base = con.execute("SELECT COUNT(*) FROM vehiculos").fetchone()[0]
    for k in range(base + 1, n_vehiculos + 1):
        tipo, cap = TIPOS_FLOTA[(k - 1) % len(TIPOS_FLOTA)]
        acopio = 1 + (k % 2)
        a = con.execute("SELECT lat, lon FROM acopios WHERE id=?", (acopio,)).fetchone()
        con.execute("INSERT INTO vehiculos(id,nombre,tipo,capacidad_kg,acopio_id,lat,lon,estado) "
                    "VALUES (?,?,?,?,?,?,?, 'libre')", (k, f"{tipo.capitalize()} extra {k}", tipo, cap, acopio, a["lat"], a["lon"]))
    con.commit()
    con.close()


def una_medicion(plantilla: Path, g, segundos: int) -> dict:
    from datos import db
    from despacho import optimizar, recalcular
    tmp = Path(tempfile.mkdtemp(prefix="bench-")) / "b.db"
    shutil.copy(plantilla, tmp)
    con = db.conectar(tmp)
    out: dict = {}
    try:
        for nombre in ("primera", "reoptimizar"):
            if nombre == "reoptimizar":
                optimizar.aprobar(con, out["plan_primera"], "bench")
                c = con.execute("INSERT INTO cierres(creado_en, descripcion, lugar, estado, tipos_bloqueados) "
                                "VALUES (?, 'bench', 'avenida del centro', 'confirmado', '[\"camion\"]')",
                                (db.ahora(),)).lastrowid
                con.commit()
            c0, t0, l0 = cpu_ocupada(), time.perf_counter(), os.getloadavg()[0]
            if nombre == "primera":
                plan = optimizar.planificar(con, motivo="bench", segundos=segundos, g=g)
            else:
                plan = recalcular.recalcular(con, segundos=segundos, g=g)
            dt = time.perf_counter() - t0
            c1 = cpu_ocupada()
            r = con.execute("SELECT resumen FROM planes WHERE id=?", (plan,)).fetchone()
            res = json.loads(r["resumen"]) if r and r["resumen"] else {}
            out[nombre] = dt
            out[f"plan_{nombre}"] = plan
            out[f"cpu_{nombre}"] = 100.0 * (c1[0] - c0[0]) / max(1, c1[1] - c0[1])
            out[f"carga_{nombre}"] = (l0, os.getloadavg()[0])
            out[f"atendidos_{nombre}"] = f"{res.get('pedidos_atendidos')}/{res.get('pedidos_considerados')}"
            out[f"vacio_{nombre}"] = bool(res.get("vacio"))
    finally:
        con.close()
        shutil.rmtree(tmp.parent, ignore_errors=True)
    return out


def p90(xs: list[float]) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.9 * len(xs) + 0.999999) - 1)] if len(xs) > 1 else xs[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Tiempo de la primera optimización y de la reoptimización.")
    ap.add_argument("--tamanos", default="demo,medio,grande", help="lista separada por comas: demo,medio,grande")
    ap.add_argument("--repeticiones", type=int, default=5)
    ap.add_argument("--segundos", type=int, default=3, help="límite de búsqueda del solver (la demo usa 3)")
    ap.add_argument("--rapido", action="store_true", help="prueba corta: solo tamaño demo, 1 repetición")
    ap.add_argument("--salida", help="guarda también el informe en este archivo")
    args = ap.parse_args(argv)
    tamanos = ["demo"] if args.rapido else [t.strip() for t in args.tamanos.split(",") if t.strip()]
    reps = 1 if args.rapido else args.repeticiones
    for t in tamanos:
        if t not in TAMANOS:
            ap.error(f"tamaño desconocido: {t}")

    from despacho import red
    m = info_maquina()
    t0 = time.perf_counter()
    g = red.cargar()
    carga_grafo = time.perf_counter() - t0
    lineas = ["# Medición del optimizador", "",
              f"- Fecha: {m['fecha']}",
              f"- Máquina: nproc={m['nproc']}, {m['cpu']}, memoria {m['mem_total_mb']} MB "
              f"({m['mem_disponible_mb']} MB disponibles al empezar)",
              f"- OR-Tools {m['ortools']}, Python {m['python']}",
              f"- Carga del sistema al empezar (1, 5, 15 min): {', '.join(f'{x:.2f}' for x in m['carga_inicial'])}",
              f"- Límite de búsqueda: {args.segundos} s; repeticiones: {reps}; carga de la red vial: {carga_grafo:.1f} s "
              "(se hace una vez y no entra en las medidas)", "",
              "| tamaño | pedidos | vehículos | paso | mediana (s) | p90 (s) | mín–máx (s) | extra sobre el límite (s) | atendidos | CPU de la máquina (%) | carga 1 min |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    with tempfile.TemporaryDirectory(prefix="bench-plantillas-") as d:
        for tam in tamanos:
            n_ped, n_veh = TAMANOS[tam]
            plantilla = Path(d) / f"{tam}.db"
            construir_base(plantilla, n_ped, n_veh)
            res = []
            for i in range(reps):
                res.append(una_medicion(plantilla, g, args.segundos))
                print(f"[{tam}] repetición {i + 1}/{reps}: primera {res[-1]['primera']:.2f} s, "
                      f"reoptimizar {res[-1]['reoptimizar']:.2f} s", file=sys.stderr, flush=True)
            for paso, nombre in (("primera", "primera optimización"), ("reoptimizar", "reoptimización tras cierre")):
                xs = [r[paso] for r in res]
                med = statistics.median(xs)
                cpu = statistics.median(r[f"cpu_{paso}"] for r in res)
                carga = statistics.median(r[f"carga_{paso}"][1] for r in res)
                aten = "/".join(sorted({r[f"atendidos_{paso}"] for r in res}))
                vac = " (¡plan vacío!)" if any(r[f"vacio_{paso}"] for r in res) else ""
                lineas.append(f"| {tam} | {n_ped} | {n_veh} | {nombre} | {med:.2f} | {p90(xs):.2f} | "
                              f"{min(xs):.2f}–{max(xs):.2f} | {med - args.segundos:.2f} | {aten}{vac} | {cpu:.0f} | {carga:.2f} |")
    lineas += ["", f"Pico de memoria de este proceso: {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024} MB.",
               f"Carga del sistema al terminar: {', '.join(f'{x:.2f}' for x in os.getloadavg())}."]
    if reps < 5:
        lineas.append(f"AVISO: solo {reps} repetición(es); mediana y p90 no son representativos.")
    texto = "\n".join(lineas)
    print(texto)
    if args.salida:
        Path(args.salida).write_text(texto + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
