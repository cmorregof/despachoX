"""Línea de comandos del triage (B.11).

    python -m triage.correr --db RUTA (--solicitudes ARCHIVO | --escenario NOMBRE|todos) [...]

Código de salida: 0 si corrió (aunque haya filas con error), 2 si faltó un argumento o un archivo.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from datos import db as datos_db
from triage import censo, cola, config, embudo, entrada_datos, puntaje, sinteticos
from triage import db as tdb
from triage.entrada_datos import a_iso, parsear_fecha

SALIDA_OK, SALIDA_ARGUMENTOS = 0, 2


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"error: {message}", file=sys.stderr)
        sys.exit(SALIDA_ARGUMENTOS)


def _argumentos(argv):
    ap = _Parser(prog="python -m triage.correr", description="Triage de solicitudes de DespachoX.")
    ap.add_argument("--db", required=True, help="base SQLite (usa una temporal para pruebas)")
    ap.add_argument("--zonas", help="zonas.csv o .json (por defecto: las de la semilla)")
    ap.add_argument("--solicitudes", help="solicitudes.csv o .json")
    ap.add_argument("--escenario", help="nombre o número de un escenario de C.1, o 'todos'")
    ap.add_argument("--ahora", help="hora simulada ISO (por defecto, la de la última solicitud)")
    ap.add_argument("--hora-evento", help="hora del sismo ISO, para detectar zonas débiles")
    ap.add_argument("--reiniciar", action="store_true", help="borra solo las tablas de triage antes")
    ap.add_argument("--integrar", action="store_true", help="escribe en pedidos (NO usar en pruebas)")
    ap.add_argument("--reporte", help="ruta del reporte en Markdown")
    return ap.parse_args(argv)


# ---------- reporte ----------
def _tabla(filas, columnas):
    if not filas:
        return ["_(ninguno)_", ""]
    salida = ["| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
    for f in filas:
        salida.append("| " + " | ".join(str(f.get(c, "")).replace("|", "/") for c in columnas) + " |")
    return salida + [""]


def _conteos(titulo, d):
    lineas = [f"**{titulo}**", ""]
    if not d:
        return lineas + ["_(ninguno)_", ""]
    return lineas + [f"- `{k}`: {v}" for k, v in d.items()] + [""]


def estado_base(con, ahora: datetime, params: dict) -> dict:
    """Lo que el reporte muestra de la base: conteos, ráfagas, débiles, umbral y lotes."""
    base = embudo.resumen_base(con)
    zonas = censo.zonas_de_base(con)
    rafaga = [{"zona": z.nombre, "rafaga_hasta": z.rafaga_hasta} for z in zonas if z.rafaga_hasta]
    tareas = {f["zona_id"]: dict(f) for f in con.execute("SELECT * FROM tareas_campo ORDER BY id")}
    debiles_ = [{"zona": z.nombre, "tarea": tareas.get(z.id, {}).get("id", ""),
                 "estado_tarea": tareas.get(z.id, {}).get("estado", ""),
                 "prioridad": round(tareas.get(z.id, {}).get("prioridad") or 0, 1)}
                for z in zonas if z.es_debil]
    desde = a_iso(ahora - timedelta(hours=params["ventana_umbral_h"]))
    vals = [r[0] for r in con.execute("SELECT p_real FROM solicitudes WHERE recibida_en > ? AND "
                                      "recibida_en <= ? AND p_real IS NOT NULL", (desde, a_iso(ahora)))]
    umbral = puntaje.umbral_detalle(vals, params)
    revision = []
    for z in zonas:
        n = con.execute("SELECT COUNT(*) FROM solicitudes WHERE zona_id=? AND recibida_en > ? AND "
                        "recibida_en <= ?", (z.id, a_iso(ahora - timedelta(hours=params["ventana_S_h"])),
                                              a_iso(ahora))).fetchone()[0]
        s = censo.tope_solicitudes(z, params)
        if n > s:
            revision.append({"zona": z.nombre, "solicitudes_24h": n, "S_z": s})
    return {"base": base, "rafaga": rafaga, "debiles": debiles_, "umbral": umbral,
            "lotes": cola.lotes(con, ahora, params)[:10], "revision_S": revision}


def _seccion_estado(e) -> list[str]:
    L = [f"Total de solicitudes en la base: **{e['base']['total']}**", ""]
    L += _conteos("Por estado", e["base"]["por_estado"])
    L += _conteos("Por marca", e["base"]["por_marca"])
    L += _conteos("Motivos de cuarentena", e["base"]["motivos_cuarentena"])
    u = e["umbral"]
    L += [f"**Umbral usado** tau* = {u['tau']:.3f} (tau_c = {u['tau_c']:.3f}, tau_cap = "
          f"{u['tau_cap']:.3f}, V = {u['V']} en la última hora, K = {u['K']})", ""]
    L += ["**Zonas en ráfaga**", ""] + _tabla(e["rafaga"], ["zona", "rafaga_hasta"])
    L += ["**Zonas que superan S_z (revisión de ráfaga)**", ""] + _tabla(
        e["revision_S"], ["zona", "solicitudes_24h", "S_z"])
    L += ["**Zonas débiles y sus tareas**", ""] + _tabla(e["debiles"],
                                                         ["zona", "tarea", "estado_tarea", "prioridad"])
    lotes = [dict(l, marcas=", ".join(f"{k}:{v}" for k, v in l["marcas"].items()),
                  muestra=", ".join(map(str, l["muestra"]))) for l in e["lotes"]]
    L += ["**Los 10 lotes de mayor prioridad**", ""] + _tabla(
        lotes, ["zona", "solicitudes", "familias", "prioridad", "marcas", "muestra"])
    return L


def reporte_solicitudes(args, ahora, params, resumen, errores, e) -> str:
    L = ["# Reporte de triage", "",
         f"- Archivo: `{Path(args.solicitudes).name}`",
         f"- Hora simulada: {a_iso(ahora)}",
         f"- Hora del evento: {params.get('hora_evento') or 'no dada'}",
         f"- Filas leídas: {resumen['recibidas']}; nuevas: {resumen['nuevas']}; "
         f"duplicado exacto: {resumen['duplicado_exacto']}; errores internos: "
         f"{len(resumen['error_interno'])}",
         f"- Integrar en pedidos: {'sí' if args.integrar else 'no'}", "",
         "## Este lote", ""]
    L += _conteos("Por estado", resumen["por_estado"])
    L += _conteos("Por marca", resumen["por_marca"])
    L += ["## Estado de la base", ""] + _seccion_estado(e)
    L += ["## Errores de lectura", ""]
    filas_err = [dict(x, tipo="rechazada" if x.get("rechazada") else "aviso") for x in errores]
    L += _tabla(filas_err, ["fila", "campo", "motivo", "tipo"])
    if resumen["error_interno"]:
        L += ["## Errores internos (la solicitud quedó en cola)", ""] + _tabla(
            resumen["error_interno"], ["fila", "error"])
    L += ["_Datos sintéticos o de prueba. Parámetros SUPUESTO en triage/config.py._", ""]
    return "\n".join(L)


def reporte_escenarios(resultados) -> str:
    cumplen = sum(r["cumple"] for r in resultados)
    L = ["# Reporte de triage · escenarios de aceptación (C.1)", "",
         f"Escenarios corridos: **{len(resultados)}**; cumplen: **{cumplen}**. Semilla 2026, datos "
         "sintéticos sobre los barrios de `datos/semilla/barrios.csv`; cada escenario en tablas de "
         "triage recién creadas. Parámetros: los SUPUESTO de `triage/config.py`.", "",
         "| # | Escenario | Debe cumplirse | Medido | Cumple |", "|---|---|---|---|---|"]
    for r in resultados:
        medido = "; ".join(f"{k}={v}" for k, v in r["medido"].items() if k != "motivos")
        L.append(f"| {r['numero']} | {r['titulo']} | {r['criterio']} | {medido} | "
                 f"{'sí' if r['cumple'] else '**no**'} |")
    L.append("")
    for r in resultados:
        L += [f"## {r['numero']}. {r['titulo']}", "", f"- Criterio: {r['criterio']}",
              f"- Cumple: **{'sí' if r['cumple'] else 'no'}**",
              f"- Hora simulada: {a_iso(r['ahora'])}",
              "- Medido: `" + json.dumps(r["medido"], ensure_ascii=False, default=str) + "`", ""]
        L += _seccion_estado(r["estado"])
    return "\n".join(L)


# ---------- principal ----------
def main(argv=None) -> int:
    args = _argumentos(argv)
    if not args.solicitudes and not args.escenario:
        print("error: falta --solicitudes o --escenario", file=sys.stderr)
        return SALIDA_ARGUMENTOS
    for nombre in ("solicitudes", "zonas"):
        ruta = getattr(args, nombre)
        if ruta and not Path(ruta).is_file():
            print(f"error: no existe el archivo de {nombre}: {ruta}", file=sys.stderr)
            return SALIDA_ARGUMENTOS
    if args.escenario and not args.reiniciar:
        print("error: --escenario necesita --reiniciar (borra las tablas de triage de la base)",
              file=sys.stderr)
        return SALIDA_ARGUMENTOS
    numeros = None
    if args.escenario:
        numeros = list(sinteticos.ESCENARIOS) if args.escenario.strip().lower() == "todos" else \
            [sinteticos.numero_de(args.escenario)]
        if None in numeros:
            print(f"error: escenario desconocido: {args.escenario}", file=sys.stderr)
            return SALIDA_ARGUMENTOS
    ahora_arg = parsear_fecha(args.ahora) if args.ahora else None
    evento = parsear_fecha(args.hora_evento) if args.hora_evento else None
    if (args.ahora and ahora_arg is None) or (args.hora_evento and evento is None):
        print("error: --ahora y --hora-evento deben ser fechas ISO 8601", file=sys.stderr)
        return SALIDA_ARGUMENTOS
    try:
        Path(args.db).resolve().parent.mkdir(parents=True, exist_ok=True)
        con = tdb.conectar(args.db)
    except Exception as e:
        print(f"error: no se pudo abrir la base {args.db}: {e}", file=sys.stderr)
        return SALIDA_ARGUMENTOS
    if args.reiniciar:
        tdb.reiniciar(con)

    if numeros:
        resultados = []
        for n in numeros:
            tdb.reiniciar(con)
            r = sinteticos.correr_escenario(con, n)
            r["estado"] = estado_base(con, r["ahora"], r["params"])
            resultados.append(r)
            print(f"Escenario {n:>2} {r['clave']:<15} {'cumple' if r['cumple'] else 'NO CUMPLE'}")
        texto = reporte_escenarios(resultados)
        print(f"{sum(r['cumple'] for r in resultados)} de {len(resultados)} escenarios cumplen.")
    else:
        if args.zonas:
            zonas, err_z = censo.leer_zonas(args.zonas)
        else:
            zonas, err_z = censo.zonas_desde_semilla(config.cargar(con)), []
        censo.cargar_zonas(con, zonas)
        if evento is not None:
            v = config.guardar_version(con, dict(config.cargar(con), hora_evento=a_iso(evento)))
            config.aprobar_version(con, v, "operador:linea_de_comandos")
        params = config.cargar(con)
        sal = entrada_datos.resolver_sal(None, args.db)
        filas, errores = entrada_datos.leer(args.solicitudes, sal=sal)
        errores = [dict(e, campo=f"zonas:{e['campo']}") for e in err_z] + errores
        ultima = max((parsear_fecha(f["recibida_en"]) for f in filas), default=None)
        ahora = ahora_arg or ultima or parsear_fecha(datos_db.ahora())
        resumen = embudo.procesar_lote(con, filas, params, ahora, integrar=args.integrar)
        e = estado_base(con, ahora, params)
        texto = reporte_solicitudes(args, ahora, params, resumen, errores, e)
        rechazadas = sum(1 for x in errores if x.get("rechazada"))
        print(f"Leídas {len(filas)} filas válidas, {rechazadas} rechazadas, "
              f"{len(errores) - rechazadas} avisos.")
        print(f"Nuevas {resumen['nuevas']}, duplicadas {resumen['duplicado_exacto']}, "
              f"errores internos {len(resumen['error_interno'])}.")
        print("Por estado: " + ", ".join(f"{k}={v}" for k, v in resumen["por_estado"].items()))
    if args.reporte:
        ruta = Path(args.reporte)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        print(f"Reporte: {ruta}")
    con.close()
    return SALIDA_OK


if __name__ == "__main__":
    sys.exit(main())
