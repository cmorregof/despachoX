"""Reproduce por terminal, paso a paso, docs/GUION_DEMO.md y verifica cada resultado esperado.

Uso, desde la raíz del repositorio:
    .venv/bin/python -m demo.correr                  # con pausas: Enter avanza (para ensayar en voz alta)
    .venv/bin/python -m demo.correr --sin-pausas     # de corrido; sirve de prueba de humo
    .venv/bin/python -m demo.correr --db datos/despachox.db   # sobre la base que ve el tablero

Siempre empieza reiniciando la base con la semilla (demo.preparar). Sin Telegram, sin red y sin
modelo: el texto del barrio y el del cierre los lee el lector por reglas (entrada/sms.py), no el
modelo. Cada paso lo marca como «[por reglas, sin modelo]». En la demo real los lee el modelo y el
resultado esperado es el mismo, pero eso NO lo prueba este ensayo. Las acciones del despachador
(confirmar, aprobar) usan las mismas funciones que los botones del tablero.

Código de salida: 0 si todas las verificaciones pasan, 1 si alguna falla.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time

from demo import preparar

CHAT = "chat-ensayo-demo"       # sintético: se guarda solo su hash
MSG_PEDIDO = "somos 40 familias en san jose no hay arroz ni leche"
MSG_CIERRE = "derrumbe en la avenida del centro, no pasa camion, si pasa moto"
FLOTA_PLAN1 = {"Camión 1", "Camión 2", "Campero 2"}
LIMITE_PLAN_S = 10.0            # lo que promete el guion para cada cálculo


class Ensayo:
    def __init__(self, pausas: bool) -> None:
        self.pausas = pausas
        self.resultados: list[tuple[str, bool, str]] = []

    def titulo(self, t: str) -> None:
        print(f"\n=== {t} ===")

    def dice(self, frase: str) -> None:
        print(f"  Quien habla: «{frase}»")

    def pausa(self, que: str = "") -> None:
        if self.pausas:
            input(f"  [Enter para seguir{': ' + que if que else ''}] ")

    def hecho(self, texto: str) -> None:
        print(f"  -> {texto}")

    def verifica(self, cond: bool, esperado: str, obtenido: str = "") -> bool:
        self.resultados.append((esperado, bool(cond), obtenido))
        print(f"  [{'ok' if cond else 'FALLA'}] {esperado}" + (f"  (obtenido: {obtenido})" if obtenido else ""))
        return bool(cond)


def resumen(con, plan_id: int) -> dict:
    r = con.execute("SELECT resumen FROM planes WHERE id=?", (plan_id,)).fetchone()
    return json.loads(r["resumen"]) if r and r["resumen"] else {}


def rutas(con, plan_id: int) -> dict[str, list[tuple[int, int, str]]]:
    """vehículo -> [(orden, pedido_id, barrio)] del plan."""
    out: dict[str, list] = {}
    for r in con.execute("SELECT v.nombre, v.tipo, pa.orden, pa.pedido_id, pu.barrio FROM paradas pa "
                         "JOIN vehiculos v ON v.id=pa.vehiculo_id JOIN puntos pu ON pu.id=pa.punto_id "
                         "WHERE pa.plan_id=? ORDER BY v.id, pa.orden", (plan_id,)):
        out.setdefault(r["nombre"], []).append((r["orden"], r["pedido_id"], r["barrio"]))
    return out


def tipo_de(con, plan_id: int, pedido_id: int) -> str | None:
    r = con.execute("SELECT v.tipo FROM paradas pa JOIN vehiculos v ON v.id=pa.vehiculo_id "
                    "WHERE pa.plan_id=? AND pa.pedido_id=?", (plan_id, pedido_id)).fetchone()
    return r["tipo"] if r else None


def imprimir_plan(con, plan_id: int) -> None:
    for veh, ps in rutas(con, plan_id).items():
        print(f"     {veh}: " + " > ".join(f"{b} (pedido {p})" for _, p, b in ps))


def calcular(e: Ensayo, con, g, func, **kw) -> tuple[int, float]:
    t = time.perf_counter()
    plan = func(con, g=g, **kw)
    return plan, time.perf_counter() - t


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ensayo por terminal del guion de la demo, con verificaciones.")
    ap.add_argument("--sin-pausas", action="store_true", help="no espera Enter entre pasos")
    ap.add_argument("--db", help="base a usar (se reinicia); por defecto datos/demo.db")
    ap.add_argument("--segundos", type=int, default=3, help="búsqueda del optimizador (el guion usa 3)")
    args = ap.parse_args(argv)
    ruta = preparar.fijar_entorno(args.db)
    e = Ensayo(pausas=not args.sin_pausas)

    # --- Paso 0: base limpia ---
    e.titulo("Preparación: base limpia con la semilla sintética")
    lista = preparar.Lista()
    preparar.revisar_entorno(lista)
    if lista.fallas == 0:
        preparar.cargar_base(lista, ruta)
    if lista.fallas:
        print(f"\nLa preparación falló ({lista.fallas}). No se sigue.")
        return 1

    from datos import db
    from despacho import optimizar, recalcular, red
    from entrada.flujo import Mesa
    from entrada.sms import leer_sms
    from tablero import datos as T

    con = db.conectar()
    g = red.cargar()
    mesa = Mesa(con, extraer=leer_sms, elegir=None)     # lector por reglas: sin modelo, sin Telegram

    # --- 0:00 a 0:20: plan 1 ---
    e.titulo("0:00 a 0:20 · Dónde estamos: plan 1 con los 17 pedidos confirmados")
    e.dice("Hay diecisiete pedidos confirmados y un plan propuesto para tres vehículos.")
    p1, t1 = calcular(e, con, g, optimizar.planificar, motivo="inicial", segundos=args.segundos)
    r1 = resumen(con, p1)
    e.hecho(f"plan {p1} calculado en {t1:.1f} s")
    imprimir_plan(con, p1)
    e.verifica(r1.get("pedidos_atendidos") == 17 and r1.get("pedidos_considerados") == 17,
               "plan 1: 17 de 17 pedidos", f"{r1.get('pedidos_atendidos')} de {r1.get('pedidos_considerados')}")
    c = r1.get("criticos", {})
    e.verifica(c.get("a_tiempo") == 3 and c.get("paradas") == 3, "plan 1: 3 de 3 críticos a tiempo",
               f"{c.get('a_tiempo')} de {c.get('paradas')}")
    e.verifica(set(rutas(con, p1)) == FLOTA_PLAN1, "plan 1: tres vehículos con ruta (Camión 1, Camión 2, Campero 2)",
               ", ".join(sorted(rutas(con, p1))))
    e.verifica(r1.get("paradas_con_retraso") == 0, "plan 1: ninguna parada con retraso", str(r1.get("paradas_con_retraso")))
    e.verifica(t1 < LIMITE_PLAN_S, f"plan 1: menos de {LIMITE_PLAN_S:.0f} s", f"{t1:.1f} s")
    estado = con.execute("SELECT estado FROM planes WHERE id=?", (p1,)).fetchone()["estado"]
    e.verifica(estado == "propuesto", "plan 1 queda propuesto, sin aprobar", estado)
    e.pausa("llega el pedido de San José")

    # --- 0:20 a 0:55: pedido por chat ---
    e.titulo("0:20 a 0:55 · Un barrio pide por chat   [por reglas, sin modelo]")
    print(f"  Mensaje: {MSG_PEDIDO}")
    e.dice("El modelo solo leyó el mensaje. No decide nada: pregunta si el lugar es ese.")
    resp = mesa.recibir_texto(CHAT, MSG_PEDIDO)
    print(f"  Bot: {resp[0].texto.splitlines()[-1]}" if resp else "  Bot: (sin respuesta)")
    e.verifica(bool(resp) and "Ubiqué «san jose» en: San José (barrio). ¿Es correcto?" in resp[0].texto,
               "el bot pregunta «Ubiqué «san jose» en: San José (barrio). ¿Es correcto?»",
               resp[0].texto.splitlines()[-1] if resp else "")
    si = next((d for et, d in (resp[0].botones if resp else []) if d.startswith("s:")), None)
    e.verifica(si is not None, "hay un botón «Sí, es ahí»", str([b[0] for b in resp[0].botones]) if resp else "")
    if si is not None:
        fin = mesa.pulsar(CHAT, si)
        print(f"  Bot (tras tocar «Sí, es ahí»): {fin.texto.splitlines()[0]}")
        # sin familias en el mensaje el bot pregunta; aquí el mensaje las trae, así que no debe preguntar
    ped = con.execute("SELECT * FROM pedidos WHERE id=21").fetchone()
    e.verifica(ped is not None and ped["punto_id"] == 14 and ped["familias"] == 40 and ped["estado"] == "nuevo",
               "pedido 21: punto 14, 40 familias, estado nuevo",
               f"punto {ped['punto_id']}, {ped['familias']} familias, {ped['estado']}" if ped else "no existe")
    u = con.execute("SELECT confirmado_por, estado FROM ubicaciones WHERE tabla='pedidos' AND fila_id=21").fetchone()
    e.verifica(u is not None and u["estado"] == "confirmada" and u["confirmado_por"] == "remitente",
               "ubicación del pedido confirmada por el remitente", f"{dict(u) if u else None}")
    e.pausa("el despachador confirma y calcula")

    # --- 0:55 a 1:30: confirmar y plan 2 ---
    e.titulo("0:55 a 1:30 · El despachador lo suma al plan")
    e.dice("El despachador confirma el pedido y pide un plan. El plan es una propuesta hasta que alguien lo aprueba.")
    e.verifica(T.cambiar_estado(con, "pedidos", 21, "confirmado", "despachador (ensayo)"), "Confirmar pedido 21")
    p2, t2 = calcular(e, con, g, optimizar.planificar, motivo="pedido nuevo", segundos=args.segundos)
    r2 = resumen(con, p2)
    e.hecho(f"plan {p2} calculado en {t2:.1f} s")
    imprimir_plan(con, p2)
    e.verifica(r2.get("pedidos_atendidos") == 18 and r2.get("pedidos_considerados") == 18,
               "plan 2: 18 de 18 pedidos", f"{r2.get('pedidos_atendidos')} de {r2.get('pedidos_considerados')}")
    c = r2.get("criticos", {})
    e.verifica(c.get("a_tiempo") == 3 and c.get("paradas") == 3, "plan 2: 3 de 3 críticos a tiempo",
               f"{c.get('a_tiempo')} de {c.get('paradas')}")
    e.verifica(tipo_de(con, p2, 21) == "camion", "plan 2: a San José (pedido 21) lo atiende un camión", str(tipo_de(con, p2, 21)))
    e.verifica(t2 < LIMITE_PLAN_S, f"plan 2: menos de {LIMITE_PLAN_S:.0f} s", f"{t2:.1f} s")
    e.verifica(optimizar.aprobar(con, p2, "despachador (ensayo)"), "Aprobar plan 2")
    e.pausa("un jurado reporta el derrumbe")

    # --- 1:30 a 2:05: cierre ---
    e.titulo("1:30 a 2:05 · Un jurado reporta un derrumbe   [por reglas, sin modelo]")
    print(f"  Mensaje: {MSG_CIERRE}")
    resp = mesa.recibir_texto(CHAT, MSG_CIERRE)
    print(f"  Bot: {resp[0].texto.splitlines()[-1]}" if resp else "  Bot: (sin respuesta)")
    # El lector por reglas conserva el artículo («la avenida del centro»); el guion no lo trae. Se acepta
    # cualquiera de los dos: lo que importa es que ubique la vía y pregunte con un solo «Sí, es ahí».
    e.verifica(bool(resp) and re.search(r"Ubiqué «(la )?avenida del centro» en: avenida del Centro \(via\)\. ¿Es correcto\?",
                                        resp[0].texto) is not None,
               "el bot pregunta «Ubiqué «(la) avenida del centro» en: avenida del Centro (via). ¿Es correcto?»",
               resp[0].texto.splitlines()[-1] if resp else "")
    si = next((d for et, d in (resp[0].botones if resp else []) if d.startswith("s:")), None)
    e.verifica(si is not None, "hay un botón «Sí, es ahí»")
    if si is not None:
        print(f"  Bot (tras tocar «Sí, es ahí»): {mesa.pulsar(CHAT, si).texto.splitlines()[0]}")
    ci = con.execute("SELECT * FROM cierres WHERE id=1").fetchone()
    e.verifica(ci is not None and ci["estado"] == "reportado", "cierre 1 queda «reportado», no cierra la vía por un mensaje",
               ci["estado"] if ci else "no existe")
    e.dice("El sistema no cierra la vía por un mensaje: la deja reportada hasta que el despachador la confirme.")
    e.pausa("el despachador confirma el cierre y recalcula")

    # --- 2:05 a 2:35: recalcular ---
    e.titulo("2:05 a 2:35 · El plan cambia")
    e.verifica(T.cambiar_estado(con, "cierres", 1, "confirmado", "despachador (ensayo)"), "Confirmar cierre 1")
    p3, t3 = calcular(e, con, g, recalcular.recalcular, segundos=args.segundos)
    r3 = resumen(con, p3)
    e.hecho(f"plan {p3} recalculado en {t3:.1f} s (cierre confirmado -> plan propuesto)")
    imprimir_plan(con, p3)
    avisos = r3.get("avisos", [])
    e.verifica(any("punto:14 quedó aislado de la red" in a for a in avisos) and any(a.startswith("camion:") for a in avisos),
               "aviso «camion: punto:14 quedó aislado de la red»", "; ".join(a for a in avisos if "aislado" in a) or str(avisos))
    e.verifica(tipo_de(con, p3, 21) == "campero", "el pedido 21 pasa de un camión a un campero", str(tipo_de(con, p3, 21)))
    en_camion = [p for p in (14, 17, 21) if tipo_de(con, p3, p) == "camion"]
    e.verifica(not en_camion, "ninguno de los pedidos de San José (14, 17, 21) va en camión", str(en_camion or "ninguno"))
    e.verifica(r3.get("pedidos_atendidos") == 18 and r3.get("pedidos_considerados") == 18,
               "plan 3: 18 de 18 pedidos", f"{r3.get('pedidos_atendidos')} de {r3.get('pedidos_considerados')}")
    c = r3.get("criticos", {})
    e.verifica(c.get("a_tiempo") == 3 and c.get("paradas") == 3, "plan 3: 3 de 3 críticos a tiempo",
               f"{c.get('a_tiempo')} de {c.get('paradas')}")
    e.verifica(r3.get("paradas_con_retraso") == 0, "plan 3: ninguna parada con retraso", str(r3.get("paradas_con_retraso")))
    e.verifica(r3.get("cierres_aplicados") == [1], "el plan aplicó el cierre 1", str(r3.get("cierres_aplicados")))
    e.verifica(t3 < LIMITE_PLAN_S, f"recálculo: menos de {LIMITE_PLAN_S:.0f} s", f"{t3:.1f} s")
    e.dice("Con la avenida cerrada, el camión ya no llega a San José. El sistema lo pasa a un campero.")
    e.pausa("el despachador aprueba")

    # --- 2:35 a 3:00: aprobar ---
    e.titulo("2:35 a 3:00 · Decide una persona")
    e.verifica(optimizar.aprobar(con, p3, "despachador (ensayo)"), "Aprobar plan 3")
    pl = con.execute("SELECT estado, aprobado_por, aprobado_en FROM planes WHERE id=?", (p3,)).fetchone()
    e.verifica(pl["estado"] == "aprobado" and bool(pl["aprobado_por"]) and bool(pl["aprobado_en"]),
               "plan 3 aprobado con quién y cuándo", f"{pl['aprobado_por']} · {pl['aprobado_en']}")
    previo = con.execute("SELECT estado FROM planes WHERE id=?", (p2,)).fetchone()["estado"]
    e.verifica(previo == "reemplazado", "el plan 2 queda reemplazado", previo)
    bit = [r["accion"] for r in con.execute("SELECT accion FROM bitacora")]
    e.verifica("aprobar plan" in bit and "confirmar cierre" in bit, "la bitácora tiene confirmar cierre y aprobar plan")
    n = con.execute("SELECT COUNT(*) FROM paquetes WHERE estado='en_ruta'").fetchone()[0]
    e.verifica(n == 18, "18 paquetes en ruta, uno por pedido, con su código de QR", str(n))
    e.dice("El modelo leyó. El optimizador calculó. Quien decidió fue una persona, y quedó escrito quién y cuándo.")

    # --- cierre ---
    print("\n=== Resumen ===")
    malas = [x for x in e.resultados if not x[1]]
    print(f"  Verificaciones: {len(e.resultados) - len(malas)} de {len(e.resultados)} bien.")
    print(f"  Tiempos de cálculo con grafo ya cargado, límite de búsqueda {args.segundos} s: "
          f"plan 1 {t1:.1f} s, plan 2 {t2:.1f} s, recálculo {t3:.1f} s.")
    print(f"  Base usada: {ruta}")
    for esperado, _, obtenido in malas:
        print(f"  FALLÓ: {esperado}  (obtenido: {obtenido})")
    con.close()
    if malas:
        print("\nLa demo NO sale igual que el guion. Si es la mañana del sábado: usar el video.")
        return 1
    print("\nLa demo sale igual que el guion (con el lector por reglas, no con el modelo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
