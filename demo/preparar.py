"""Deja lista la base local de la demo y imprime la lista de chequeo.

Uso, desde la raíz del repositorio:
    .venv/bin/python -m demo.preparar                 # base en datos/demo.db (o DESPACHOX_DB si está fijada)
    .venv/bin/python -m demo.preparar --db datos/despachox.db   # la base que usa el tablero local
    .venv/bin/python -m demo.preparar --solo-revisar  # no toca la base: solo dependencias y archivos

Qué hace: revisa Python, dependencias, la red vial y los CSV de la semilla; reinicia la base con la
semilla sintética (despacho.semilla --cargar --reiniciar); comprueba conteos y nomenclátor; imprime
`[ok]` o `[FALLA]` por cada punto y sale con código 1 si algo falla.
No llama a Telegram ni a ningún modelo: fija DESPACHOX_SIN_RED=1.
"""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
GRAFO_REPO = RAIZ / "despliegue" / "grafo" / "manizales_region.graphml"
CONTEOS = {"puntos": 15, "acopios": 2, "vehiculos": 5, "lotes": 34, "pedidos": 20}
OBLIGATORIAS = ("ortools", "osmnx", "networkx", "scipy", "pydantic", "streamlit", "folium",
                "streamlit_folium", "segno", "fpdf")
OPCIONALES = {"telegram": "bot de Telegram (python-telegram-bot)", "anthropic": "modelo de lenguaje",
              "dotenv": "lectura de .env"}


def fijar_entorno(db: str | None = None) -> Path:
    """Debe llamarse antes de importar `datos.db`: la ruta se lee al importar."""
    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    os.chdir(RAIZ)
    os.environ["DESPACHOX_SIN_RED"] = "1"
    ruta = Path(db) if db else Path(os.environ.get("DESPACHOX_DB") or RAIZ / "datos" / "demo.db")
    ruta = ruta if ruta.is_absolute() else RAIZ / ruta
    os.environ["DESPACHOX_DB"] = str(ruta)
    if not os.environ.get("DESPACHOX_GRAFO") and GRAFO_REPO.exists():
        os.environ["DESPACHOX_GRAFO"] = str(GRAFO_REPO)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


class Lista:
    def __init__(self) -> None:
        self.fallas = 0

    def ok(self, texto: str, detalle: str = "") -> None:
        print(f"  [ok]    {texto}" + (f"  ({detalle})" if detalle else ""))

    def falla(self, texto: str, como_arreglar: str = "") -> None:
        self.fallas += 1
        print(f"  [FALLA] {texto}" + (f"\n          -> {como_arreglar}" if como_arreglar else ""))

    def aviso(self, texto: str) -> None:
        print(f"  [aviso] {texto}")

    def chequear(self, cond: bool, texto: str, detalle: str = "", como_arreglar: str = "") -> bool:
        (self.ok(texto, detalle) if cond else self.falla(texto + (f"  ({detalle})" if detalle else ""), como_arreglar))
        return cond


def revisar_entorno(lista: Lista) -> None:
    print("Entorno")
    v = sys.version_info
    lista.chequear(v >= (3, 10), f"Python {v.major}.{v.minor}.{v.micro}", como_arreglar="usar python3.12 con el .venv")
    for m in OBLIGATORIAS:
        if importlib.util.find_spec(m) is not None:      # sin importar: streamlit avisa al importarse fuera del tablero
            lista.ok(f"módulo {m}")
        else:
            lista.falla(f"módulo {m}: no está instalado", ".venv/bin/pip install -r requirements.txt (con internet)")
    for m, para in OPCIONALES.items():
        if importlib.util.find_spec(m) is None:
            lista.aviso(f"falta {m} ({para}); la demo por terminal no lo necesita")
    grafo = Path(os.environ.get("DESPACHOX_GRAFO") or GRAFO_REPO)
    lista.chequear(grafo.exists(), f"red vial {grafo.name}", f"{grafo.stat().st_size / 1e6:.1f} MB" if grafo.exists() else "",
                   "copiar despliegue/grafo/manizales_region.graphml o fijar DESPACHOX_GRAFO")
    for a in ("puntos", "acopios", "vehiculos", "lotes", "pedidos", "vias"):
        p = RAIZ / "datos" / "semilla" / f"{a}.csv"
        lista.chequear(p.exists(), f"semilla {a}.csv", como_arreglar="git pull; los CSV vienen en el repositorio")


def cargar_base(lista: Lista, ruta: Path) -> None:
    print(f"Base {ruta}")
    for sufijo in ("", "-wal", "-shm"):
        f = Path(str(ruta) + sufijo)
        if f.exists():
            f.unlink()          # base nueva: se borra también el WAL, así no queda nada de ensayos anteriores
    from datos import db
    from despacho import semilla
    con = db.conectar()
    try:
        r = semilla.cargar(reiniciar=True, con=con)
        for tabla, esperado in CONTEOS.items():
            n = r["filas"][tabla]
            lista.chequear(n == esperado, f"{tabla}: {n}", f"esperado {esperado}", "git pull; la semilla cambió")
        for tabla in ("planes", "cierres", "paquetes", "ubicaciones"):
            n = con.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            lista.chequear(n == 0, f"{tabla} vacía", f"{n} filas" if n else "")
        estados = dict(con.execute("SELECT estado, COUNT(*) FROM pedidos GROUP BY estado").fetchall())
        lista.chequear(estados == {"confirmado": 17, "nuevo": 3}, "pedidos: 17 confirmados y 3 nuevos", str(estados))
        lista.chequear((r["lugares"] or 0) > 0, f"nomenclátor: {r['lugares']} apodos")
        _revisar_lugares(lista, con)
    finally:
        con.close()


def _revisar_lugares(lista: Lista, con) -> None:
    import lugares
    from lugares import nomenclator
    for texto, tipos in (("san jose", ("barrio", "punto", "sitio", "vereda")), ("avenida del centro", ("via", "sitio"))):
        res = nomenclator.resolver(con, texto, tipos=tipos, elegir=None)
        nombre = res.elegido.nombre if res.elegido else None
        lista.chequear(res.metodo == "exacto" and res.seguro, f"«{texto}» -> {nombre}", f"{res.metodo}, seguro={res.seguro}",
                       "el bot daría una lista de opciones en vez de «Sí, es ahí»")
    # el punto 14 y la vía de la demo
    p = con.execute("SELECT nombre, critico FROM puntos WHERE id=14").fetchone()
    lista.chequear(p is not None and p["nombre"] == "Salón comunal San José", "punto 14 = Salón comunal San José",
                   p["nombre"] if p else "no existe")
    criticos = [r["nombre"] for r in con.execute("SELECT nombre FROM puntos WHERE critico=1 ORDER BY id")]
    lista.chequear(len(criticos) == 3, "3 puntos críticos", ", ".join(criticos))
    v = con.execute("SELECT 1 FROM lugares WHERE alias='avenida del centro' AND osm_u=582617778 AND osm_v=323215241").fetchone()
    lista.chequear(v is not None, "vía avenida del Centro con su arista 582617778 -> 323215241")
    lista.chequear(lugares is not None, "módulo lugares importa")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Prepara la base local y la lista de chequeo de la demo.")
    ap.add_argument("--db", help="ruta de la base (por defecto DESPACHOX_DB o datos/demo.db)")
    ap.add_argument("--solo-revisar", action="store_true", help="no reinicia la base")
    args = ap.parse_args(argv)
    ruta = fijar_entorno(args.db)
    lista = Lista()
    revisar_entorno(lista)
    if lista.fallas == 0 and not args.solo_revisar:
        cargar_base(lista, ruta)
    elif lista.fallas:
        print("Base: no se toca hasta que el entorno esté bien")
    print()
    if lista.fallas:
        print(f"Hay {lista.fallas} falla(s). La demo en vivo no está lista; usa el video de respaldo.")
        return 1
    print("Todo listo." + ("" if args.solo_revisar else f" Base limpia en {ruta}."))
    if not args.solo_revisar:
        print("Para que el tablero la vea: export DESPACHOX_DB=" + str(ruta))
        print("Ensayo por terminal:         .venv/bin/python -m demo.correr")
    return 0


if __name__ == "__main__":
    sys.exit(main())
