"""Base temporal con los puntos, barrios y vías de la semilla real. Ninguna prueba toca la red."""
import csv

import pytest

from datos import db
from entrada.extraer import Extraccion
from entrada.flujo import Mesa
from entrada.privacidad import limpiar
from entrada.pruebas.mensajes import MENSAJES


@pytest.fixture(autouse=True)
def _sal(monkeypatch):
    monkeypatch.setenv("DESPACHOX_SAL", "sal-de-prueba")


@pytest.fixture(autouse=True)
def _cliente_nuevo(monkeypatch):
    """Cada prueba arma su propio cliente de Anthropic (el extractor guarda uno para todo el proceso)."""
    from entrada import extraer as E
    monkeypatch.setattr(E, "_cliente_compartido", None)


@pytest.fixture
def con(tmp_path):
    c = db.conectar(tmp_path / "prueba.db")
    with open(db.RAIZ / "semilla" / "puntos.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c.execute("INSERT INTO puntos(id,nombre,barrio,comuna,lat,lon,critico) VALUES (?,?,?,?,?,?,?)",
                      (r["id"], r["nombre"], r["barrio"], r["comuna"], r["lat"], r["lon"], r["critico"]))
    c.commit()
    yield c
    c.close()


def extractor_falso(extra: dict | None = None):
    """Devuelve la lectura esperada de cada mensaje de ejemplo; lo demás es `otro`."""
    tabla = {limpiar(m["texto"]): m["esperado"] for m in MENSAJES}
    tabla.update({limpiar(k): v for k, v in (extra or {}).items()})

    def extraer(texto: str) -> Extraccion:
        return Extraccion(**tabla.get(texto, {"tipo": "otro"}), texto=texto)
    return extraer


@pytest.fixture
def mesa(con):
    return Mesa(con, extraer=extractor_falso(), elegir=None)
