"""Mide el extractor con modelo (entrada/extraer.py) sobre el mismo conjunto, con un tope duro de llamadas.

NO SE HA CORRIDO. La noche del 20 al 21 de noviembre no había ANTHROPIC_API_KEY, así que el
extractor con modelo no tiene cifra sobre este conjunto. Con clave, se corre así:

    PYTHONPATH=. python -m evaluacion.lector.medir_modelo                  # solo dice qué haría; no llama
    PYTHONPATH=. python -m evaluacion.lector.medir_modelo --confirmo-gasto # mide, con tope de 330 llamadas
    PYTHONPATH=. python -m evaluacion.lector.medir_modelo --confirmo-gasto --max 30   # una prueba corta

Qué hace:
- Lee cada mensaje como el bot con red (Mesa.leer en entrada/flujo.py): limpia el texto, llama a
  entrada.extraer.extraer y, si la lectura falla, intenta con las reglas de entrada/sms.py.
- Tope duro: TOPE_LLAMADAS = 330, una llamada por mensaje. `--max` puede bajarlo, nunca subirlo. El
  cliente se arma sin reintentos (max_retries=0) para que cada llamada sea una sola petición: el tope
  cuenta peticiones reales. Una llamada que falla se califica como la deja el bot.
- El lugar se resuelve sin modelo (elegir=None), igual que en evaluar.py: así el tope no crece con
  los desempates y las dos cifras se comparan con la misma regla.
- Califica con las mismas funciones de evaluar.py y escribe en evaluacion/lector/modelo/.
- Costo estimado antes de correr, con los supuestos de entrada/ESCALA.md (entre 0,000175 y 0,00045 USD
  por mensaje): entre 0,06 y 0,15 USD por las 330 llamadas. Es un estimado; la corrida reporta los
  tokens medidos y el costo con los precios declarados en entrada/extraer.py.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

TOPE_LLAMADAS = 330
SALIDA = AQUI / "modelo"
COSTO_POR_MENSAJE_USD = (0.000175, 0.00045)      # supuestos bajo y alto de entrada/ESCALA.md


class TopeAlcanzado(RuntimeError):
    pass


class Tope:
    """Envuelve una función de extracción y se niega a pasar de `tope` llamadas."""

    def __init__(self, extraer, tope: int):
        self.extraer = extraer
        self.tope = min(int(tope), TOPE_LLAMADAS)
        self.llamadas = 0

    def __call__(self, texto: str):
        if self.llamadas >= self.tope:
            raise TopeAlcanzado(f"tope de {self.tope} llamadas alcanzado")
        self.llamadas += 1
        return self.extraer(texto)


def leer_como_el_bot(texto: str, extraer):
    """Mesa.leer con red: limpia, extrae con el modelo y, si falla, intenta con las reglas."""
    from entrada.privacidad import limpiar
    from entrada.sms import leer_sms
    limpio = limpiar(texto)
    x = extraer(limpio)
    if x.fallo:
        por_reglas = leer_sms(limpio)
        if not por_reglas.fallo:
            return por_reglas
    return x


def medir(conjunto: list[dict], extraer, tope: int = TOPE_LLAMADAS) -> tuple[dict, Tope]:
    """Califica los primeros `tope` mensajes con `extraer`. Nunca hace más de `tope` llamadas."""
    from evaluacion.lector import evaluar as EV
    contador = Tope(extraer, tope)
    parte = conjunto[:contador.tope]
    res = EV.evaluar(parte, leer=lambda t: leer_como_el_bot(t, contador), calentar=False)
    assert contador.llamadas <= contador.tope
    return res, contador


def _sin_reintentos():
    """Cliente compartido de entrada/extraer.py sin reintentos: una llamada, una petición."""
    import anthropic
    from entrada import extraer as E
    E._cliente_compartido = anthropic.Anthropic(timeout=E.SEGUNDOS, max_retries=0)
    return E


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Mide entrada/extraer.py sobre conjunto.jsonl, con tope de llamadas")
    ap.add_argument("--confirmo-gasto", action="store_true", help="sin esta marca no se llama al modelo")
    ap.add_argument("--max", type=int, default=TOPE_LLAMADAS, help=f"llamadas como máximo (tope duro {TOPE_LLAMADAS})")
    a = ap.parse_args(argv)
    if os.environ.get("DESPACHOX_SIN_RED") == "1":
        print("DESPACHOX_SIN_RED=1: este script llama al modelo, así que no corre sin red. Quita la variable.")
        return 2
    from dotenv import load_dotenv
    load_dotenv(RAIZ / ".env")
    from evaluacion.lector import evaluar as EV
    conjunto = EV.cargar_conjunto()
    n = min(a.max, TOPE_LLAMADAS, len(conjunto))
    lo, hi = (n * c for c in COSTO_POR_MENSAJE_USD)
    print(f"Haría {n} llamadas al modelo (tope duro {TOPE_LLAMADAS}). Costo estimado con los supuestos de "
          f"entrada/ESCALA.md: entre {lo:.2f} y {hi:.2f} USD.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Sin ANTHROPIC_API_KEY: no se mide. Ponla en .env o en el entorno.")
        return 2
    if not a.confirmo_gasto:
        print("No se llamó al modelo. Para medir, repite con --confirmo-gasto.")
        return 0
    E = _sin_reintentos()
    res, contador = medir(conjunto, E.extraer, n)
    uso = dict(E.USO)
    costo = uso["entrada"] / 1e6 * E.PRECIO_ENTRADA_MTOK + uso["salida"] / 1e6 * E.PRECIO_SALIDA_MTOK
    res.update({
        "fecha": datetime.now().astimezone().isoformat(timespec="seconds"),
        "lector": f"entrada.extraer.extraer con {E.MODELO}, sin reintentos, y reglas si falla (Mesa.leer con red); "
                  "lugar con lugares.resolver, elegir=None",
        "maquina": f"{platform.system()} {platform.release()} {platform.machine()}, Python {platform.python_version()}",
        "conjunto": {"ruta": "evaluacion/lector/conjunto.jsonl", "n": n,
                     "sha256": __import__("hashlib").sha256(EV.CONJUNTO.read_bytes()).hexdigest()},
        "llamadas": contador.llamadas, "uso": uso, "costo_usd_medido": costo,
    })
    SALIDA.mkdir(exist_ok=True)
    guardar = {k: v for k, v in res.items() if k not in ("lecturas", "calificaciones")}
    (SALIDA / "resultados.json").write_text(json.dumps(guardar, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with open(SALIDA / "lecturas.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for reg, lect, cal in zip(conjunto, res["lecturas"], res["calificaciones"]):
            f.write(json.dumps({"id": reg["id"], "texto": reg["texto"], "lectura": lect, "campos": cal["campos"],
                                "clase_lugar": cal["clase_lugar"], "errores": cal["errores"]}, ensure_ascii=False) + "\n")
    (SALIDA / "tablas.md").write_text("# Tablas del extractor con modelo (medir_modelo.py)\n\n" + EV.tablas_md(res),
                                      encoding="utf-8")
    print(f"{contador.llamadas} llamadas, {uso['fallos']} fallidas, {uso['entrada']} tokens de entrada y "
          f"{uso['salida']} de salida, {costo:.4f} USD. Resultados en {SALIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
