"""¿Un pin enviado por cualquier chat cambia cómo se ubica «avenida del centro» para los demás?
Desde la raíz del repositorio:  DESPACHOX_SAL=x .venv/bin/python docs/qa_noche/envenenar.py
Sin red: el extractor del modelo es falso y el desempate con modelo está apagado (elegir=None).
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DESPACHOX_SAL", "sal-qa")

from datos import db                                    # noqa: E402
from despacho import semilla                             # noqa: E402
from entrada.extraer import Cierre, Extraccion           # noqa: E402
from entrada.flujo import Mesa                           # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="qa-env-"))
con = db.conectar(tmp / "b.db")
semilla.cargar(reiniciar=True, con=con)


def extractor(texto):
    return Extraccion(tipo="cierre", texto=texto,
                      cierre=Cierre(lugar="avenida del centro", descripcion="derrumbe", tipos_bloqueados=["camion"]))


m = Mesa(con, extraer=extractor, elegir=None)
antes = m.recibir_texto(1, "derrumbe en la avenida del centro, no pasa camion")
print("ANTES :", antes[0].texto.split("\n")[-1][:110], "| botones:", [b[0] for b in antes[0].botones])

atacante = m.recibir_texto(666, "derrumbe en la avenida del centro")
m.recibir_ubicacion(666, 4.7110, -74.0721)          # un pin en Bogotá
print("lugares aprendidos:", [dict(r) for r in con.execute(
    "SELECT nombre, alias, tipo, round(lat,3) lat, round(lon,3) lon FROM lugares WHERE origen='aprendido'")])

despues = m.recibir_texto(2, "derrumbe en la avenida del centro, no pasa camion")
print("DESPUÉS:", despues[0].texto.split("\n")[-1][:110], "| botones:", [b[0] for b in despues[0].botones])
