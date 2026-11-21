"""Resumen de un grupo de pedidos, y de toda la mesa, para el despachador, leído por el modelo.

    python -m despacho.resumen_grupo --resumir            # grupos de pedidos nuevos sin resumen + la mesa
    python -m despacho.resumen_grupo --resumir --falso    # sin modelo, para ensayar la vista
    python -m despacho.resumen_grupo --resumir --todos    # vuelve a resumir aunque ya haya resumen

Regla: el modelo lee y resume; no decide. Las familias, los kilos, la urgencia y la prioridad del grupo
los suma `despacho/agrupar.py` con código, y el resumen no los cambia. El despachador confirma cada grupo.

El texto se guarda en la tabla `resumenes_grupo` (datos/esquema.sql) y el tablero lo muestra con la
etiqueta «leído por el modelo». En las pruebas el extractor es falso: aquí no se llama a ninguna API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Iterable

from datos import db
from entrada.privacidad import limpiar

# Sin topes (decisión de Carlos, 21 nov 12:55): el modelo lee todos los textos del grupo y el resumen no se
# corta. `tope_textos` y `tope` siguen como parámetros opcionales para quien quiera limitarlos.
TOPE_TEXTOS = None
TOPE_RESUMEN = None
TOPE_GRUPOS_MESA = None
MAX_TOKENS_GRUPO = 1500
MAX_TOKENS_MESA = 4000
A_LA_VEZ = 8                     # llamadas al modelo en paralelo
REINTENTOS_SDK = 4               # el SDK reintenta 429 y 5xx con espera creciente
PASADAS = 3                      # pasadas sobre los grupos que quedaron sin resumen (límite de tasa)
# Sonnet resume cada grupo (muchas llamadas, lectura) y Opus lee la mesa entera (una llamada).
# Decisión de Carlos, 21 nov 12:55. Se cambian con DESPACHOX_MODELO_RESUMEN_GRUPO y DESPACHOX_MODELO_RESUMEN.
MODELO_GRUPO = os.environ.get("DESPACHOX_MODELO_RESUMEN_GRUPO") or "claude-sonnet-5-5"
MODELO = os.environ.get("DESPACHOX_MODELO_RESUMEN") or "claude-opus-5-5"
USO = {"llamadas": 0, "fallos": 0, "entrada": 0, "salida": 0}
SISTEMA = ("Usted ayuda al despachador de una mesa de ayuda alimentaria después de un sismo en Manizales. "
           "Solo lee y resume lo que dicen los pedidos. No decide prioridades, rutas ni cantidades: los "
           "números que recibe los calculó el sistema y no se cambian. Escribe en español, claro y corto, "
           "sin títulos ni viñetas.")

INSTRUCCION = (
    "Escriba para el despachador dos o tres líneas en español, tratándolo de usted: qué piden estos "
    "pedidos, qué casos especiales aparecen (bebés, adultos mayores, enfermos, alimentos que necesitan "
    "frío, agua) y qué no se entiende. Las familias y los kilos de arriba ya están sumados por el "
    "sistema: no los recalcule. Prohibido inventar cantidades o cambiar las dadas. No decida prioridad "
    "ni ruta.")


def texto_para_modelo(grupo, puntos: dict | None = None, tope_textos: int | None = TOPE_TEXTOS) -> str:
    """Arma la entrada del modelo: cabecera con los números del código y los textos limpios, numerados.

    `puntos` es opcional: {punto_id: nombre}. Sin él, la cabecera dice solo el id del punto.
    `tope_textos`: cuántos textos como máximo (None = todos).
    """
    nombre = (puntos or {}).get(grupo.punto_id)
    punto = f"punto {grupo.punto_id}" + (f" ({limpiar(nombre)})" if nombre else "")
    lineas = [
        f"Grupo de pedidos del {punto}.",
        f"Pedidos: {len(grupo.pedidos)}. Familias sumadas por el sistema: {grupo.familias}. "
        f"Kilos sumados por el sistema: {grupo.kg:g}.",
        "",
        "Textos de los pedidos:",
    ]
    for i, p in enumerate(grupo.pedidos[:tope_textos], start=1):
        texto = limpiar(p.get("texto_original")) if p.get("texto_original") else ""
        lineas.append(f"{i}. {texto or '(sin texto)'}")
    sobran = len(grupo.pedidos) - tope_textos if tope_textos else 0
    if sobran > 0:
        lineas.append(f"y {sobran} textos más.")
    lineas += ["", INSTRUCCION]
    return "\n".join(lineas)


INSTRUCCION_MESA = (
    "Escriba para el despachador, tratándolo de usted, entre seis y diez líneas sobre toda la mesa: qué "
    "piden en conjunto estos grupos, en qué grupos aparecen casos especiales (bebés, adultos mayores, "
    "enfermos, alimentos que necesitan frío, agua), qué grupos tienen textos que no se entienden o se "
    "contradicen, y qué se repite mucho. Nombre los grupos por su punto. Los números de arriba los sumó "
    "el sistema: no los recalcule ni invente otros. No ordene los grupos ni decida cuál atender primero: "
    "eso lo decide el despachador.")


def texto_mesa(grupos: list, resumenes: dict[str, str] | None = None, puntos: dict | None = None) -> str:
    """Entrada del modelo para resumir toda la mesa: totales del código y una línea por grupo.

    `resumenes` es {clave: resumen del grupo}; cuando un grupo no tiene resumen van sus dos primeros textos.
    """
    resumenes = resumenes or {}
    nombres = puntos or {}
    criticos = sum(1 for g in grupos if g.critico)
    lineas = [
        f"Mesa con {len(grupos)} grupos de pedidos por revisar, {criticos} en puntos críticos.",
        f"Pedidos: {sum(len(g.pedidos) for g in grupos)}. Familias sumadas por el sistema: "
        f"{sum(g.familias for g in grupos)}. Kilos sumados por el sistema: {sum(g.kg for g in grupos):.0f}.",
        "", "Grupos (punto · pedidos · familias · kilos · urgencia · lo leído):",
    ]
    for i, g in enumerate(grupos[:TOPE_GRUPOS_MESA], start=1):   # None = todos
        nombre = limpiar(nombres.get(g.punto_id) or f"punto {g.punto_id}")
        leido = resumenes.get(g.clave)
        if not leido:
            textos = [limpiar(p.get("texto_original")) for p in g.pedidos[:2] if p.get("texto_original")]
            leido = " / ".join(textos) or "(sin texto)"
        lineas.append(f"{i}. {nombre}{' (CRÍTICO)' if g.critico else ''} · {len(g.pedidos)} pedidos · "
                      f"{g.familias} familias · {g.kg:.0f} kg · urgencia {g.urgencia} · {leido}")
    if TOPE_GRUPOS_MESA and len(grupos) > TOPE_GRUPOS_MESA:
        lineas.append(f"y {len(grupos) - TOPE_GRUPOS_MESA} grupos más.")
    lineas += ["", INSTRUCCION_MESA]
    return "\n".join(lineas)


def resumir(grupo, extractor: Callable[[str], str], puntos: dict | None = None,
            tope: int | None = TOPE_RESUMEN) -> str:
    """Pasa el texto del grupo al extractor (inyectado). `tope` recorta la respuesta; None no corta."""
    salida = extractor(texto_para_modelo(grupo, puntos)) or ""
    salida = str(salida).strip()
    return salida[:tope] if tope else salida


def extractor_modelo(max_tokens: int = MAX_TOKENS_GRUPO, modelo: str | None = None) -> Callable[[str], str]:
    """Devuelve un extractor que llama a Claude con `modelo` (por defecto `MODELO_GRUPO`) y cuenta tokens.

    Lee ANTHROPIC_API_KEY del entorno o del `.env` de la raíz del repositorio. Si la llamada falla,
    devuelve cadena vacía (no se guarda resumen) y lo cuenta como fallo. Importa `anthropic` al usarse.
    """
    from dotenv import load_dotenv
    load_dotenv(db.ruta_env())
    modelo = modelo or MODELO_GRUPO
    import anthropic
    cliente = anthropic.Anthropic(timeout=180, max_retries=REINTENTOS_SDK)

    def extraer(texto: str) -> str:
        try:
            r = cliente.messages.create(model=modelo, max_tokens=max_tokens, system=SISTEMA,
                                        output_config={"effort": "low"},
                                        messages=[{"role": "user", "content": texto}])
        except Exception as e:  # noqa: BLE001 - sin clave, sin red o límite: el grupo queda sin resumen
            print(f"aviso: el modelo no respondió ({type(e).__name__}: {str(e)[:160]})", file=sys.stderr)
            USO["llamadas"] += 1
            USO["fallos"] += 1
            return ""
        USO["llamadas"] += 1
        if getattr(r, "usage", None) is not None:
            USO["entrada"] += r.usage.input_tokens or 0
            USO["salida"] += r.usage.output_tokens or 0
            por_modelo = USO.setdefault("por_modelo", {}).setdefault(modelo, {"entrada": 0, "salida": 0, "llamadas": 0})
            por_modelo["entrada"] += r.usage.input_tokens or 0
            por_modelo["salida"] += r.usage.output_tokens or 0
            por_modelo["llamadas"] += 1
        if r.stop_reason == "max_tokens":
            print(f"aviso: un resumen llegó al tope de {max_tokens} tokens y quedó cortado", file=sys.stderr)
        return "".join(getattr(b, "text", "") for b in r.content)
    return extraer


def extractor_falso(texto: str) -> str:
    """Sin modelo: una línea con lo que más se repite en los textos, para ensayar la vista."""
    import re
    palabras = re.findall(r"necesitamos ([^.\n]+)", texto)
    productos: dict[str, int] = {}
    for w in palabras:
        for x in w.split(","):
            x = x.strip()
            if x:
                productos[x] = productos.get(x, 0) + 1
    top = ", ".join(k for k, _ in sorted(productos.items(), key=lambda kv: -kv[1])[:4])
    n = len(re.findall(r"^\d+\. ", texto, flags=re.M))
    return (f"(resumen de ensayo, sin modelo) {n} textos leídos; lo más pedido: {top or 'no se distingue'}. "
            "No se detectaron casos especiales porque este extractor no lee el contenido.")


# ---------- base ----------

def _ids(grupo) -> str:
    return json.dumps(sorted(int(i) for i in grupo.pedido_ids))


def guardar(con: sqlite3.Connection, grupo, resumen: str, modelo: str | None) -> None:
    """Guarda o reemplaza el resumen del grupo por su clave."""
    con.execute("INSERT OR REPLACE INTO resumenes_grupo(clave, punto_id, pedido_ids, resumen, modelo, creado_en) "
                "VALUES (?,?,?,?,?,?)",
                (grupo.clave, grupo.punto_id, _ids(grupo), resumen, modelo, db.ahora()))
    con.commit()


def leer(con: sqlite3.Connection, clave: str) -> dict | None:
    """El resumen guardado de un grupo, o None. `pedido_ids` vuelve como lista."""
    fila = con.execute("SELECT * FROM resumenes_grupo WHERE clave=?", (clave,)).fetchone()
    if fila is None:
        return None
    d = dict(fila)
    d["pedido_ids"] = json.loads(d["pedido_ids"] or "[]")
    return d


def resumir_y_guardar(con: sqlite3.Connection, grupos: Iterable, extractor: Callable[[str], str],
                      modelo: str = "falso", solo_faltantes: bool = True, puntos: dict | None = None,
                      a_la_vez: int = 1) -> int:
    """Resume los grupos sin resumen guardado (o todos, si `solo_faltantes` es False). Devuelve cuántos.

    `a_la_vez` > 1 llama al extractor en hilos; la base se escribe desde este hilo. Un resumen vacío
    (el modelo no respondió) no se guarda.
    """
    pendientes = [g for g in grupos if not (solo_faltantes and leer(con, g.clave) is not None)]
    if a_la_vez > 1 and len(pendientes) > 1:
        with ThreadPoolExecutor(max_workers=a_la_vez) as ex:
            textos = list(ex.map(lambda g: resumir(g, extractor, puntos), pendientes))
    else:
        textos = [resumir(g, extractor, puntos) for g in pendientes]
    n = 0
    for g, t in zip(pendientes, textos):
        if t:
            guardar(con, g, t, modelo)
            n += 1
    return n


# ---------- la mesa entera ----------

def clave_mesa(grupos: list) -> str:
    """Cambia cuando cambian los grupos: así un resumen viejo no se muestra como vigente."""
    return "mesa:" + hashlib.sha1(",".join(sorted(g.clave for g in grupos)).encode()).hexdigest()[:12]


def leer_mesa(con: sqlite3.Connection, grupos: list) -> dict | None:
    return leer(con, clave_mesa(grupos)) if grupos else None


def resumir_mesa(con: sqlite3.Connection, grupos: list, extractor: Callable[[str], str], modelo: str = "falso",
                 puntos: dict | None = None, solo_faltante: bool = True) -> bool:
    """Un resumen de toda la mesa a partir de los resúmenes por grupo. True si se guardó uno."""
    if not grupos:
        return False
    clave = clave_mesa(grupos)
    if solo_faltante and leer(con, clave) is not None:
        return False
    resumenes = {}
    for g in grupos:
        r = leer(con, g.clave)
        if r:
            resumenes[g.clave] = r["resumen"]
    texto = (extractor(texto_mesa(grupos, resumenes, puntos)) or "").strip()
    if not texto:
        return False
    ids = json.dumps(sorted(int(i) for g in grupos for i in g.pedido_ids))
    con.execute("INSERT OR REPLACE INTO resumenes_grupo(clave, punto_id, pedido_ids, resumen, modelo, creado_en) "
                "VALUES (?,?,?,?,?,?)", (clave, None, ids, texto, modelo, db.ahora()))
    con.commit()
    return True


def costo_usd() -> float:
    """Costo estimado de las llamadas de `USO`, con el precio público de cada modelo."""
    from entrada.extraer import PRECIOS_MTOK
    total = 0.0
    for modelo, u in USO.get("por_modelo", {}).items():
        pe, ps = PRECIOS_MTOK.get(modelo, (0.0, 0.0))
        total += u["entrada"] / 1e6 * pe + u["salida"] / 1e6 * ps
    return total


def resumir_mesa_completa(con: sqlite3.Connection, falso: bool = False, todos: bool = False,
                          a_la_vez: int = A_LA_VEZ, pasadas: int = PASADAS) -> dict:
    """Agrupa los pedidos nuevos, resume los grupos que falten (Sonnet) y después la mesa (Opus).

    Hace hasta `pasadas` pasadas sobre los grupos que queden sin resumen, por si el límite de tasa
    rechazó llamadas. Deja las cifras en la bitácora. Devuelve las cifras.
    """
    from despacho import agrupar
    t0 = time.perf_counter()
    grupos = agrupar.grupos_nuevos(con)
    puntos = {r["id"]: r["nombre"] for r in con.execute("SELECT id, nombre FROM puntos")}
    if falso:
        ex_grupo = ex_mesa = extractor_falso
        modelo_grupo = modelo_mesa = "falso"
    else:
        ex_grupo, modelo_grupo = extractor_modelo(), MODELO_GRUPO
        ex_mesa, modelo_mesa = extractor_modelo(max_tokens=MAX_TOKENS_MESA, modelo=MODELO), MODELO
    n = resumir_y_guardar(con, grupos, ex_grupo, modelo_grupo, solo_faltantes=not todos, puntos=puntos,
                          a_la_vez=a_la_vez)
    for _ in range(max(0, pasadas - 1)):           # segunda y tercera pasada solo sobre los que faltan
        faltan = [g for g in grupos if leer(con, g.clave) is None]
        if not faltan:
            break
        time.sleep(5)
        n += resumir_y_guardar(con, faltan, ex_grupo, modelo_grupo, solo_faltantes=True, puntos=puntos,
                               a_la_vez=max(1, a_la_vez // 2))
    sin_resumen = sum(1 for g in grupos if leer(con, g.clave) is None)
    mesa = resumir_mesa(con, grupos, ex_mesa, modelo_mesa, puntos, solo_faltante=not todos)
    cifras = {"grupos": len(grupos), "resumidos": n, "sin_resumen": sin_resumen, "mesa": mesa,
              "modelo": modelo_grupo, "modelo_mesa": modelo_mesa,
              "segundos": round(time.perf_counter() - t0, 1), "llamadas": USO["llamadas"], "fallos": USO["fallos"],
              "tokens_entrada": USO["entrada"], "tokens_salida": USO["salida"], "costo_usd": round(costo_usd(), 4),
              "por_modelo": USO.get("por_modelo", {})}
    db.anotar(con, "modelo", "resumir grupos", json.dumps(cifras, ensure_ascii=False))
    return cifras


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Resume con el modelo los grupos de pedidos nuevos y la mesa.")
    ap.add_argument("--resumir", action="store_true", help="resume los grupos sin resumen y la mesa")
    ap.add_argument("--falso", action="store_true", help="sin modelo: texto de ensayo")
    ap.add_argument("--todos", action="store_true", help="vuelve a resumir aunque ya haya resumen")
    ap.add_argument("--db", help="ruta de la base (por defecto, la de DESPACHOX_DB)")
    ap.add_argument("--a-la-vez", type=int, default=A_LA_VEZ)
    ap.add_argument("--pasadas", type=int, default=PASADAS, help="pasadas sobre los grupos que queden sin resumen")
    a = ap.parse_args(argv)
    if not a.resumir:
        ap.print_help()
        return 2
    con = db.conectar(Path(a.db)) if a.db else db.conectar()
    try:
        r = resumir_mesa_completa(con, falso=a.falso, todos=a.todos, a_la_vez=a.a_la_vez, pasadas=a.pasadas)
    finally:
        con.close()
    print(json.dumps(r, ensure_ascii=False))
    return 0 if not r["sin_resumen"] else 1


if __name__ == "__main__":
    sys.exit(main())
