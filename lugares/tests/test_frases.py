"""Mide el resolvedor con un banco de frases escritas como en un chat.

    python -m lugares.tests.test_frases        # imprime la tabla y cada frase que no fue acierto seguro

Cada fila de frases.csv: frase, reporte (pedido o cierre) y el lugar esperado (`nombre` del
nomenclátor) o `ninguno` si el sistema no debe proponer nada. Se mide sin modelo de lenguaje.

  acierto seguro    propuso un solo lugar y era el correcto
  por opciones      no se comprometió, pero el correcto estaba entre las opciones ofrecidas
  no sé             no se comprometió y el correcto no estaba entre las opciones (o no existía)
  error seguro      propuso con seguridad un lugar equivocado: el caso grave, debe ser cero
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from datos import db
from lugares import nomenclator as R

FRASES = Path(__file__).resolve().parent / "frases.csv"
TIPOS = {"pedido": ("barrio", "punto", "sitio", "vereda"), "cierre": ("via", "sitio")}


def medir(con) -> tuple[Counter, list[dict]]:
    cuenta, detalle = Counter(), []
    with open(FRASES, encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    for fila in filas:
        esperado = fila["esperado"].strip()
        r = R.resolver(con, fila["frase"], tipos=TIPOS[fila["reporte"]], elegir=None)
        nombres = [c.nombre for c in r.candidatos]
        if r.seguro:
            clase = "acierto seguro" if r.elegido.nombre == esperado else "error seguro"
        elif esperado in nombres:
            clase = "por opciones"
        else:
            clase = "no sé"
        cuenta[clase] += 1
        detalle.append({**fila, "clase": clase, "propuesto": r.elegido.nombre if r.elegido else "",
                        "opciones": nombres[:3], "puntaje": r.candidatos[0].puntaje if r.candidatos else 0})
    return cuenta, detalle


def _base(ruta):
    con = db.conectar(ruta)
    R.cargar_semilla(con)
    return con


def test_ningun_error_seguro(tmp_path, capsys):
    cuenta, detalle = medir(_base(tmp_path / "t.db"))
    total = sum(cuenta.values())
    with capsys.disabled():
        print(f"\nresolvedor, {total} frases: " + ", ".join(
            f"{k} {cuenta[k]}" for k in ("acierto seguro", "por opciones", "no sé", "error seguro")))
    graves = [d for d in detalle if d["clase"] == "error seguro"]
    assert total >= 40
    assert not graves, "propuso con seguridad un lugar equivocado: " + "; ".join(
        f"«{d['frase']}» -> {d['propuesto']} (era {d['esperado']})" for d in graves)
    assert cuenta["acierto seguro"] + cuenta["por opciones"] >= total // 2    # que siga siendo útil


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        cuenta, detalle = medir(_base(Path(d) / "t.db"))
    print(f"UMBRAL_SEGURO={R.UMBRAL_SEGURO} MARGEN={R.MARGEN} frases={sum(cuenta.values())}")
    for k in ("acierto seguro", "por opciones", "no sé", "error seguro"):
        print(f"  {k:15} {cuenta[k]:3}")
    for x in detalle:
        if x["clase"] != "acierto seguro":
            print(f"  [{x['clase']}] «{x['frase']}» esperado={x['esperado']} propuesto={x['propuesto'] or '-'} "
                  f"opciones={x['opciones']} puntaje={x['puntaje']}")
