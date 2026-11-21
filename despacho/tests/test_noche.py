"""Decisiones de Carlos del viernes por la noche: factor crítico 3, empaque 1,2 solo en fruta en
frío y alertas de silencio que nunca salen con comida."""
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]


def _valor_al_importar(expresion: str, variable: str, valor: str | None = None) -> str:
    """Evalúa `expresion` en un proceso nuevo, con la variable de entorno quitada o fijada."""
    env = {k: v for k, v in os.environ.items() if k != variable}
    if valor is not None:
        env[variable] = valor
    r = subprocess.run([sys.executable, "-c", f"from despacho import optimizar; print({expresion})"],
                       env=env, cwd=RAIZ, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


# ---------- factor crítico ----------

@pytest.mark.parametrize("valor, esperado", [(None, "3"), ("", "3"), ("1", "1"), ("10", "10")])
def test_factor_critico_por_defecto_es_3(valor, esperado):
    assert _valor_al_importar("optimizar.FACTOR_CRITICO", "DESPACHOX_FACTOR_CRITICO", valor) == esperado


# ---------- empaque activo de la patente UNAL 37476 ----------

def test_factor_empaque_por_defecto_es_1_2():
    assert _valor_al_importar("optimizar.FACTOR_EMPAQUE_ACTIVO", "DESPACHOX_FACTOR_EMPAQUE") == "1.2"
    assert _valor_al_importar("optimizar.FACTOR_EMPAQUE_ACTIVO", "DESPACHOX_FACTOR_EMPAQUE", "1.5") == "1.5"


def test_nota_del_empaque_dice_de_donde_sale():
    from despacho import optimizar
    assert optimizar.NOTA_EMPAQUE == ("cota inferior medida en gulupa a 8 °C en la solicitud de la patente "
                                      "UNAL 37476; pendiente de datos del ICTA para otros productos")


@pytest.mark.parametrize("producto, frio, empaque, perecedero, aplica", [
    ("fruta", True, 1, 1, True),
    ("Frutas", True, 1, 1, True),
    ("gulupa", True, 1, 1, True),
    ("tomate de árbol", True, 1, 1, True),
    ("fruta", False, 1, 1, False),        # acopio sin frío
    ("fruta", True, 0, 1, False),         # sin empaque
    ("fruta", True, 1, 0, False),         # no perecedera
    ("leche", True, 1, 1, False),         # la patente no mide otros productos
    ("verdura", True, 1, 1, False),
    ("tomate", True, 1, 1, False),
    (None, True, 1, 1, False),
])
def test_empaque_solo_alarga_fruta_perecedera_en_frio(monkeypatch, producto, frio, empaque, perecedero, aplica):
    from despacho import optimizar
    from despacho.tests.conftest import AHORA, iso
    from datetime import timedelta
    monkeypatch.setattr(optimizar, "FACTOR_EMPAQUE_ACTIVO", 1.2)
    lote = {"producto": producto, "perecedero": perecedero, "empaque_activo": empaque,
            "vence_en": iso(AHORA + timedelta(hours=10))}
    assert optimizar.factor_empaque(lote, frio) == (1.2 if aplica else 1.0)
    assert optimizar.vence_efectivo(lote, AHORA, frio) == AHORA + timedelta(hours=12 if aplica else 10)


def test_fruta_con_empaque_en_acopio_sin_frio_no_gana_tiempo(mundo, con, grafo, ahora, monkeypatch):
    """Con 1,2 la fruta que vence en 31 min alcanzaría a salir; sin frío el factor es 1,0 y no sale."""
    import json
    from datetime import timedelta
    from despacho import optimizar
    monkeypatch.setattr(optimizar, "FACTOR_EMPAQUE_ACTIVO", 1.2)
    mundo.lote(2, producto="fruta", kg=50, perecedero=1, vence=ahora + timedelta(minutes=31), empaque=1)
    mundo.pedido(1, 3, 20, producto="fruta")
    mundo.listo()
    r = json.loads(con.execute("SELECT resumen FROM planes WHERE id=?",
                               (optimizar.planificar(con, segundos=1, g=grafo, ahora=ahora),)).fetchone()[0])
    assert r["pedidos_atendidos"] == 0
    assert r["sin_atender"][0]["motivo"] == "sin inventario para este pedido"


def test_semilla_empaque_solo_en_fruta_del_acopio_con_frio():
    import csv
    carpeta = RAIZ / "datos" / "semilla"
    with open(carpeta / "acopios.csv", encoding="utf-8") as f:
        frio = {r["id"]: r["tiene_frio"] == "1" for r in csv.DictReader(f)}
    with open(carpeta / "lotes.csv", encoding="utf-8") as f:
        lotes = list(csv.DictReader(f))
    con_empaque = [l for l in lotes if l["empaque_activo"] == "1"]
    assert con_empaque, "la semilla debe mostrar al menos un lote con empaque"
    assert all(l["producto"] == "fruta" and frio[l["acopio_id"]] for l in con_empaque)
    assert all(l["empaque_activo"] == "1" for l in lotes if l["producto"] == "fruta" and frio[l["acopio_id"]])
