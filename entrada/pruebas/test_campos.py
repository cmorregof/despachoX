"""Mide cuántos campos extrae bien el modelo real en los quince mensajes. Necesita ANTHROPIC_API_KEY
(en el entorno o en .env); sin ella se omite. Deja el reporte en entrada/pruebas/reporte_campos.md.

    python -m pytest entrada/pruebas/test_campos.py -s
"""
import os
import unicodedata
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

from entrada import extraer as E
from entrada.privacidad import limpiar
from entrada.pruebas.mensajes import MENSAJES

RAIZ = Path(__file__).resolve().parents[2]
REPORTE = Path(__file__).with_name("reporte_campos.md")
MINIMO = 0.80        # por debajo de esto la prueba falla; el número exacto va al reporte


def _plano(s) -> str:
    t = unicodedata.normalize("NFKD", str(s or "").lower())
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).split())


def _producto(s) -> str:
    p = _plano(s)
    return p[:-1] if p.endswith("s") and len(p) > 4 else p      # huevos = huevo, lentejas = lenteja


def _lugar_igual(dicho, esperado) -> bool:
    if esperado is None or dicho is None:
        return dicho is None and esperado is None
    a, b = _plano(dicho), _plano(esperado)
    return a == b or b in a or a in b                            # «barrio la enea» vale por «la enea»


def calificar(x: E.Extraccion, m: dict) -> dict[str, bool]:
    """Un resultado por campo calificable del mensaje."""
    e = m["esperado"]
    ep, ec, p, c = e.get("pedido") or {}, e.get("cierre") or {}, x.pedido, x.cierre
    r = {}
    for campo in m["califica"]:
        if campo == "tipo":
            r[campo] = x.tipo == e["tipo"]
        elif campo == "lugar":
            r[campo] = p is not None and _lugar_igual(p.lugar, ep["lugar"])
        elif campo == "familias":
            r[campo] = p is not None and p.familias == ep["familias"]
        elif campo == "urgencia":
            r[campo] = p is not None and p.urgencia == ep["urgencia"]
        elif campo == "horas_limite":
            r[campo] = p is not None and p.horas_limite == ep["horas_limite"]
        elif campo == "productos":
            r[campo] = p is not None and ({_producto(q.producto) for q in p.productos}
                                          == {_producto(q["producto"]) for q in ep["productos"]})
        elif campo == "kg":
            r[campo] = p is not None and ({_producto(q.producto): q.kg for q in p.productos}
                                          == {_producto(q["producto"]): q["kg"] for q in ep["productos"]})
        elif campo == "dudas":
            r[campo] = bool(x.dudas)
        elif campo == "cierre.lugar":
            r[campo] = c is not None and _lugar_igual(c.lugar, ec["lugar"])
        elif campo == "cierre.tipos_bloqueados":
            r[campo] = c is not None and sorted(c.tipos_bloqueados) == sorted(ec["tipos_bloqueados"])
        else:
            raise KeyError(campo)
    return r


def test_el_calificador_da_pleno_con_la_referencia():
    for m in MENSAJES:
        assert all(calificar(E.Extraccion(**m["esperado"]), m).values()), m["id"]
    assert len(MENSAJES) == 15


def test_campos_extraidos_con_el_modelo_real():
    load_dotenv(RAIZ / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        pytest.skip("sin ANTHROPIC_API_KEY: no se mide el extractor real")
    filas, bien, total, fallos = [], 0, 0, 0
    for m in MENSAJES:
        x = E.extraer(limpiar(m["texto"]))
        fallos += x.fallo
        r = calificar(x, m)
        bien, total = bien + sum(r.values()), total + len(r)
        malos = ", ".join(k for k, v in r.items() if not v) or "ninguno"
        filas.append(f"| {m['id']} | {m['nota']} | {sum(r.values())}/{len(r)} | {malos} |")
    pct = 100 * bien / total
    REPORTE.write_text(
        f"# Campos extraídos por el modelo en los quince mensajes de ejemplo\n\n"
        f"Medido el {datetime.now():%Y-%m-%d %H:%M} con `{E.MODELO}`, una corrida, sin reintentos. "
        f"Los mensajes son sintéticos y los escribió el equipo, así que el número mide el extractor "
        f"sobre estos casos y no sobre mensajes reales.\n\n"
        f"**{bien} de {total} campos correctos ({pct:.1f} %).** Llamadas que fallaron: {fallos} de {len(MENSAJES)}.\n\n"
        f"| # | Caso | Campos bien | Campos mal |\n|---|---|---|---|\n" + "\n".join(filas) + "\n",
        encoding="utf-8")
    print(f"\nCampos correctos: {bien}/{total} ({pct:.1f} %). Reporte: {REPORTE}")
    assert fallos == 0 and bien / total >= MINIMO
