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
