"""El generador es determinista y el conjunto congelado es coherente. Sin red; corre en segundos.

    PYTHONPATH=. python -m pytest evaluacion/lector/tests -q
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evaluacion.lector import generar as G  # noqa: E402


def _filas():
    return [json.loads(x) for x in G.CONJUNTO.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_misma_semilla_mismo_texto():
    assert G.texto_generado() == G.texto_generado()


def test_reproduce_la_parte_generada_byte_a_byte():
    assert G.parte_generada() == G.texto_generado().encode("utf-8")


def test_un_clon_con_crlf_tambien_coincide(tmp_path):
    # core.autocrlf=true en Windows: la misma comparación que hace --verificar
    lf = G.CONJUNTO.read_bytes().replace(b"\r\n", b"\n")
    crlf = tmp_path / "conjunto.jsonl"
    crlf.write_bytes(lf.replace(b"\n", b"\r\n"))
    assert G.parte_generada(crlf) == G.parte_generada() == G.texto_generado().encode("utf-8")
    assert len(G.parte_generada(crlf).splitlines()) == G.N


def test_otra_semilla_da_otro_conjunto():
    assert G.texto_generado(G.SEMILLA + 1) != G.texto_generado()


def test_mezcla_declarada():
    rs = G.generar()
    assert len(rs) == G.N == 300
    assert Counter(r["variante"] for r in rs) == dict(G.PLAN)
    assert Counter(r["faltan"][0] for r in rs if r["faltan"]) == {"lugar": 15, "conteo": 15, "productos": 15}
    assert sum(len(r["oro"]["pedidos"]) == 2 for r in rs) == 30


def test_conjunto_con_330_y_su_origen():
    filas = _filas()
    assert len(filas) == 330
    assert Counter(f["origen"] for f in filas) == {"generado": 300, "a_mano": 30}
    assert len({f["id"] for f in filas}) == 330
    assert [f for f in filas[300:]] == [{**d, "origen": "a_mano"} for d in G.leer_dificiles()]


def test_los_lugares_congelados_siguen_en_la_semilla():
    actuales = {(x["nombre"], x["tipo"]) for x in G.lugares_de_la_semilla()}
    with open(G.LUGARES_BASE, encoding="utf-8") as f:
        congelados = {(r["nombre"], r["tipo"]) for r in csv.DictReader(f)}
    assert congelados <= actuales, sorted(congelados - actuales)


def test_el_oro_es_coherente_con_lo_que_se_pidio():
    from entrada import raciones
    catalogo = {c[0] for c in G.CATALOGO}
    assert catalogo <= set(raciones.KG_POR_FAMILIA) | set(raciones.PARA_BEBES) | getattr(raciones, "SIN_RACION", set())
    nombres = {(x["nombre"], x["tipo"]) for t in G.lugares() for x in t}
    for r in G.generar():
        assert r["oro"]["tipo"] == "pedido" and r["origen"] == "generado"
        for p in r["oro"]["pedidos"]:
            assert p["urgencia"] in (1, 2, 3)
            if "lugar" in r["faltan"]:
                assert p["lugar_texto"] is None and p["lugar_nombre"] is None
            else:
                assert p["lugar_texto"] and (p["lugar_nombre"], p["lugar_tipo"]) in nombres
            conteo = [p["familias"], p["personas"], p["bebes"]]
            if "conteo" in r["faltan"]:
                assert conteo == [None, None, None]
            else:
                assert sum(v is not None for v in conteo) == 1
            if "productos" in r["faltan"]:
                assert p["productos"] == []
            else:
                assert p["productos"] and {q["producto"] for q in p["productos"]} <= catalogo


def test_ningun_dato_personal_en_los_textos():
    for f in _filas():
        assert not re.search(r"\d{7,}", f["texto"]), f["id"]        # nada con forma de teléfono o cédula
        assert not re.search(r"[\w.+-]+@[\w-]+\.", f["texto"]), f["id"]
        assert not re.search(r"\b(me llamo|mi nombre es)\b", f["texto"].lower()), f["id"]


def test_numeros_en_palabras():
    assert G.en_palabras(40, "f") == "cuarenta"
    assert G.en_palabras(35) == "treinta y cinco"
    assert G.en_palabras(21, "f") == "veintiuna"
    assert G.en_palabras(21) == "veintiún"
    assert G.en_palabras(171, "f") == "ciento setenta y una"
    assert G.en_palabras(200, "f") == "doscientas"
    assert G.en_palabras(100) == "cien"
