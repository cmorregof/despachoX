"""¿Cuántos códigos por segundo puede probar alguien en el wifi del acopio contra la pasarela sin token?
Desde la raíz del repositorio:  DESPACHOX_SAL=x .venv/bin/python docs/qa_noche/fuerza_bruta.py
Base temporal con 20 paquetes en ruta (como la demo). Todo en 127.0.0.1; nada sale de la máquina.
"""
import json
import os
import secrets
import sys
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import Request, urlopen

sys.path.insert(0, os.getcwd())
os.environ.setdefault("DESPACHOX_SAL", "sal-qa")
os.environ.pop("DESPACHOX_SMS_TOKEN", None)

from datos import db                                    # noqa: E402
from despacho import paquetes                            # noqa: E402
from entrada import pasarela_sms                         # noqa: E402

ruta = Path(tempfile.mkdtemp(prefix="qa-fb-")) / "b.db"
con = db.conectar(ruta)
vivos = set()
for i in range(1, 21):
    con.execute("INSERT INTO pedidos(id, creado_en, estado) VALUES (?, ?, 'asignado')", (i, db.ahora()))
    codigo = paquetes._codigo_nuevo(con)
    con.execute("INSERT INTO paquetes(codigo, pedido_id, kg, estado) VALUES (?, ?, 10, 'en_ruta')", (codigo, i))
    vivos.add(codigo)
con.commit()

servidor = pasarela_sms.Pasarela(("127.0.0.1", 0), ruta_db=ruta)
threading.Thread(target=servidor.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{servidor.server_address[1]}/sms"

n, aciertos, inicio = 0, 0, time.monotonic()
while time.monotonic() - inicio < 10:
    intento = "DX-" + "".join(secrets.choice(paquetes.ALFABETO) for _ in range(4))
    cuerpo = json.dumps({"de": "atacante", "texto": f"ENTREGADO {intento}"}).encode()
    with urlopen(Request(url, data=cuerpo, headers={"Content-Type": "application/json"}), timeout=5) as r:
        aciertos += "quedo entregado" in json.loads(r.read())["respuesta"]
    n += 1
s = time.monotonic() - inicio
tasa = n / s
espacio = len(paquetes.ALFABETO) ** 4
print(f"{n} intentos en {s:.1f} s: {tasa:.0f} por segundo, un solo cliente, con nice 19 y la simulación usando los 2 núcleos")
print(f"aciertos por azar: {aciertos}")
print(f"recorrer los {espacio:,} códigos: {espacio / tasa / 60:.1f} min")
print(f"primer acierto esperado con 20 paquetes vivos: {espacio / 20 / tasa / 60:.1f} min")
servidor.shutdown()
