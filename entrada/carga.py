"""Prueba de carga del bot: N mensajes sintéticos por el mismo camino que un mensaje de Telegram.

    python -m entrada.carga --n 5000 --concurrencia 50                 # extractor falso, sin red
    python -m entrada.carga --n 5000 --concurrencia 50 --fallos 0.05   # 5 % de lecturas que fallan
    python -m entrada.carga --n 100 --concurrencia 10 --extractor real # con ANTHROPIC_API_KEY; cuesta

Cada mensaje entra por `bot.Manejadores.texto` con un Telegram simulado, desde un chat distinto, sobre
una base temporal con la semilla de puntos. Nunca toca la base compartida. Los mensajes son los quince
de `pruebas/mensajes.py`, sintéticos y sin datos de nadie.

Reporta mensajes por minuto, tiempo de respuesta medio, p95 y máximo, errores, mensajes perdidos (lo
que debía quedar en la base y no quedó) y, con el extractor real, tokens y costo con el precio público.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import random
import statistics
import sys
import tempfile
import time

try:                                   # opcional: solo para medir la memoria
    import psutil
except ImportError:
    psutil = None
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

from datos import db
from entrada import extraer as E
from entrada.bot import Manejadores
from entrada.flujo import SIN_LEER, Mesa
from entrada.privacidad import limpiar
from entrada.pruebas.mensajes import MENSAJES


def extractor_falso(latencia_s: float, fallos: float, semilla: int = 7):
    """Devuelve la lectura esperada de cada mensaje tras una espera parecida a la del modelo
    (exponencial con esa media). Con probabilidad `fallos` imita una API caída tras los reintentos."""
    tabla = {limpiar(m["texto"]): m["esperado"] for m in MENSAJES}
    azar = random.Random(semilla)

    def extraer(texto: str) -> E.Extraccion:
        if latencia_s:
            time.sleep(azar.expovariate(1 / latencia_s))
        if azar.random() < fallos:
            return E.crudo(texto)
        return E.Extraccion(**tabla.get(texto, {"tipo": "otro"}), texto=texto)
    return extraer


def _base_temporal() -> "db.sqlite3.Connection":
    con = db.conectar(Path(tempfile.mkdtemp(prefix="carga_")) / "carga.db")
    with open(db.RAIZ / "semilla" / "puntos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            con.execute("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                        (r["id"], r["nombre"], r["barrio"], r["comuna"], r["lat"], r["lon"], r["critico"]))
    con.commit()
    return con


class _Cronometro:
    """Mide cuánto del tiempo pasa en el hilo del bot (base y lugares), que es lo que no corre en paralelo."""

    def __init__(self, mesa: Mesa):
        self.segundos = 0.0
        original = mesa.atender_seguro

        def medido(chat_id, x):
            t = time.perf_counter()
            try:
                return original(chat_id, x)
            finally:
                self.segundos += time.perf_counter() - t
        mesa.atender_seguro = medido


async def _correr(n: int, concurrencia: int, extraer, cache_lugares: bool = False) -> dict:
    con = _base_temporal()
    # Sin desempate de lugares con modelo y sin el respaldo por reglas: se mide el camino del modelo,
    # y una lectura fallida tiene que quedar cruda. El respaldo por reglas se prueba en test_sms.py.
    mesa = Mesa(con, extraer=extraer, elegir=None, respaldo_reglas=False)
    if cache_lugares:
        from entrada import cache_lugares as cache
        cache.instalar()
    crono = _Cronometro(mesa)
    m = Manejadores(mesa)
    asyncio.get_running_loop().set_default_executor(ThreadPoolExecutor(max_workers=concurrencia))
    textos = [MENSAJES[i % len(MENSAJES)]["texto"] for i in range(n)]
    tiempos, esperas, errores, respuestas, crudos, esperadas = [], [], [], 0, 0, 0
    memoria = {"pico": 0}
    proceso = psutil.Process() if psutil else None

    async def vigilar_memoria():
        while proceso:
            memoria["pico"] = max(memoria["pico"], proceso.memory_info().rss)
            await asyncio.sleep(0.5)
    filas_de = _filas_por_texto()
    cupo = asyncio.Semaphore(concurrencia)

    async def uno(i: int, texto: str):
        nonlocal respuestas, crudos, esperadas
        llegada = time.perf_counter()               # todos llegan a la vez: la espera en fila cuenta
        async with cupo:
            enviados = []

            async def reply_text(t, reply_markup=None, parse_mode=None):
                enviados.append(t)
            msj = SimpleNamespace(text=texto, location=None, reply_text=reply_text)
            t0 = time.perf_counter()
            try:
                await m.texto(SimpleNamespace(effective_chat=SimpleNamespace(id=10_000 + i),
                                              effective_message=msj), None)
            except Exception as e:                      # en el bot real esto acaba en Manejadores.error
                errores.append(type(e).__name__)
            fin = time.perf_counter()
            tiempos.append(fin - t0)                    # atención: desde que el bot lo toma
            esperas.append(fin - llegada)               # lo que espera la persona: desde que llegó
            respuestas += bool(enviados)
            crudo = SIN_LEER in enviados
            crudos += crudo
            esperadas += 1 if crudo else filas_de[texto]

    t0 = time.perf_counter()
    vigia = asyncio.create_task(vigilar_memoria())
    await asyncio.gather(*(uno(i, t) for i, t in enumerate(textos)))
    total = time.perf_counter() - t0
    vigia.cancel()
    if proceso:
        info = proceso.memory_info()
        memoria["pico"] = max(memoria["pico"], getattr(info, "peak_wset", 0), info.rss)

    filas = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("pedidos", "cierres")}
    integridad = con.execute("PRAGMA integrity_check").fetchone()[0]
    claves = con.execute("PRAGMA foreign_key_check").fetchall()
    con.close()
    if cache_lugares:
        cache.quitar()
    return {"n": n, "concurrencia": concurrencia, "segundos": total, "tiempos": tiempos,
            "errores": errores, "sin_respuesta": n - respuestas, "filas": filas, "crudos": crudos,
            "hilo_bot_s": crono.segundos, "esperadas": esperadas, "esperas": esperas,
            "memoria_mb": memoria["pico"] / 2**20 if proceso else None,
            "integridad": integridad, "claves_rotas": len(claves), "cache_lugares": cache_lugares}


def _filas_por_texto() -> dict[str, int]:
    """Filas que deja cada mensaje leído como se espera: una por pedido y una por cierre."""
    return {m["texto"]: bool(m["esperado"].get("pedido")) + bool(m["esperado"].get("cierre")) for m in MENSAJES}


def informe(r: dict, extractor: str, fallos: float, latencia: float) -> str:
    ts = sorted(r["tiempos"])
    es = sorted(r["esperas"])

    def pct(xs, q):
        return xs[int(q * (len(xs) - 1))]
    guardadas = r["filas"]["pedidos"] + r["filas"]["cierres"]
    lineas = [
        f"Extractor: {extractor}" + (f" (latencia media simulada {latencia:g} s, fallos {fallos:.0%})"
                                     if extractor == "falso" else f" ({E.MODELO})"),
        f"Mensajes: {r['n']} · concurrencia {r['concurrencia']} · duración {r['segundos']:.1f} s",
        f"Ritmo: {r['n'] / r['segundos'] * 60:,.0f} mensajes por minuto",
        f"Espera de la persona (desde que llegó): mediana {pct(es, .5):.1f} s · p95 {pct(es, .95):.1f} s · "
        f"máximo {es[-1]:.1f} s",
        f"Atención (desde que el bot lo toma): mediana {pct(ts, .5):.2f} s · p95 {pct(ts, .95):.2f} s · "
        f"máximo {ts[-1]:.2f} s",
        f"Memoria máxima del proceso: " + (f"{r['memoria_mb']:.0f} MB" if r["memoria_mb"] else "sin medir (falta psutil)"),
        f"Integridad de la base al final: {r['integridad']} · claves foráneas rotas: {r['claves_rotas']}",
        f"Caché de lugares: {'sí' if r['cache_lugares'] else 'no'}",
        f"Tiempo en el hilo del bot (base y lugares, no paralelo): {r['hilo_bot_s']:.1f} s "
        f"({r['hilo_bot_s'] / r['n'] * 1000:.1f} ms por mensaje)",
        f"Errores: {len(r['errores'])}" + (f" ({', '.join(sorted(set(r['errores'])))})" if r["errores"] else ""),
        f"Mensajes sin respuesta: {r['sin_respuesta']}",
        f"Filas en la base: {r['filas']['pedidos']} pedidos y {r['filas']['cierres']} cierres",
    ]
    lineas.append(f"Lecturas fallidas guardadas como texto crudo para el despachador: {r['crudos']}")
    if extractor == "falso":
        lineas.append(f"Mensajes perdidos: {r['esperadas'] - guardadas} (filas esperadas {r['esperadas']}, "
                      f"guardadas {guardadas})")
    if extractor == "real":
        u = E.USO
        costo = u["entrada"] / 1e6 * E.PRECIO_ENTRADA_MTOK + u["salida"] / 1e6 * E.PRECIO_SALIDA_MTOK
        lineas += [
            f"Llamadas al modelo: {u['llamadas']} · fallidas tras reintentos: {u['fallos']}",
            f"Tokens: {u['entrada']:,} de entrada y {u['salida']:,} de salida "
            f"({u['entrada'] / max(1, u['llamadas']):.0f} y {u['salida'] / max(1, u['llamadas']):.0f} por llamada)",
            f"Costo de la corrida: {costo:.4f} USD · por cada 10 000 mensajes: {costo / r['n'] * 10_000:.2f} USD "
            f"(precio público {E.PRECIO_ENTRADA_MTOK:g} / {E.PRECIO_SALIDA_MTOK:g} USD por millón de tokens)",
        ]
    return "\n".join(lineas)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--concurrencia", type=int, default=32)
    ap.add_argument("--extractor", choices=["falso", "real"], default="falso")
    ap.add_argument("--latencia", type=float, default=1.8, help="segundos medios del extractor falso "
                    "(1,8 s es lo medido con el modelo real a las 15:00)")
    ap.add_argument("--fallos", type=float, default=0.0, help="fracción de lecturas que fallan (extractor falso)")
    ap.add_argument("--json", help="guarda el resultado sin los tiempos individuales")
    ap.add_argument("--cache-lugares", action="store_true", help="usa el caché de entrada/cache_lugares.py")
    a = ap.parse_args(argv)
    if a.extractor == "real":
        from dotenv import load_dotenv
        load_dotenv(db.RAIZ.parent / ".env")
        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Falta ANTHROPIC_API_KEY en .env para el extractor real.", file=sys.stderr)
            return 1
        extraer = E.extraer
    else:
        extraer = extractor_falso(a.latencia, a.fallos)
    r = asyncio.run(_correr(a.n, a.concurrencia, extraer, a.cache_lugares))
    texto = informe(r, a.extractor, a.fallos, a.latencia)
    print(texto)
    if a.json:
        Path(a.json).write_text(json.dumps({k: v for k, v in r.items() if k not in ("tiempos", "esperas")} |
                                           {"informe": texto}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
