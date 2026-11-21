"""Las métricas dan lo esperado en casos de juguete, y el script del modelo respeta su tope sin llamar a la red.

    PYTHONPATH=. python -m pytest evaluacion/lector/tests -q
"""
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[3]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from evaluacion.lector import evaluar as EV  # noqa: E402
from evaluacion.lector import medir_modelo as MM  # noqa: E402


def _pedido(lugar_texto, lugar_nombre, familias=None, personas=None, bebes=None, productos=(), urgencia=2,
            ambiguo=None):
    return {"lugar_texto": lugar_texto, "lugar_nombre": lugar_nombre, "lugar_tipo": "barrio" if lugar_nombre else None,
            "lugar_ambiguo": ambiguo, "familias": familias, "personas": personas, "bebes": bebes,
            "productos": [{"producto": p, "kg": kg} for p, kg in productos], "urgencia": urgencia}


def _reg(texto, pedidos, tipo="pedido", faltan=(), id_="t1", origen="generado", variante="sin_tildes"):
    return {"id": id_, "origen": origen, "variante": variante, "etiquetas": [variante], "texto": texto,
            "oro": {"tipo": tipo, "pedidos": pedidos, "cierre": None, "entregado": None}, "faltan": list(faltan)}


def _lectura(lugar, familias=None, personas=None, bebes=None, productos=(), urgencia=2, tipo="pedido"):
    return {"tipo": tipo, "fallo": False, "entregado": None, "cierre": None,
            "pedido": {"lugar": lugar, "familias": familias, "personas": personas, "bebes": bebes,
                       "productos": [{"producto": p, "kg": kg} for p, kg in productos], "urgencia": urgencia,
                       "horas_limite": None}}


@pytest.fixture(scope="module")
def L(tmp_path_factory):
    return EV.Lugares(EV.base_de_lugares(tmp_path_factory.mktemp("lector")))


def test_wilson():
    assert EV.wilson(0, 0) == (None, None)
    lo, hi = EV.wilson(5, 10)
    assert round(lo, 4) == 0.2366 and round(hi, 4) == 0.7634
    lo, hi = EV.wilson(10, 10)
    assert hi == pytest.approx(1.0) and round(lo, 4) == 0.7225


def test_productos_precision_exhaustividad_y_f1(L):
    reg = _reg("no necesitamos arroz, si leche y panela para 15 familias en chipre",
               [_pedido("chipre", "Chipre", familias=15, productos=[("leche", None), ("panela", None)])])
    lect = _lectura("si", familias=15, productos=[("arroz", None), ("leche", None), ("panela", None)])
    cal = EV.calificar(reg, lect, L)
    assert cal["productos"] == {"vp": 2, "fp": 1, "fn": 0, "perdidos": 0}
    assert cal["campos"]["familias"] and cal["campos"]["conteo_exacto"] and cal["campos"]["urgencia"]
    assert not cal["campos"]["productos_exactos"] and not cal["campos"]["lugar_extraido"]
    assert not cal["campos"]["mensaje_sin_errores"]
    m = EV.agregar([cal])
    assert m["productos"]["precision"] == pytest.approx(2 / 3) and m["productos"]["exhaustividad"] == 1.0
    assert m["productos"]["f1"] == pytest.approx(0.8)
    assert m["familias"] == {"n": 1, "aciertos": 1, "proporcion": 1.0, "ic95": list(EV.wilson(1, 1))}


def test_lectura_perfecta_y_mismo_punto_de_entrega(L):
    reg = _reg("PEDIDO 30 ALBERGUE TEMPORAL ARRAYANES ARROZ 20 KILOS LECHE",
               [_pedido("albergue temporal arrayanes", "Albergue temporal Arrayanes", familias=30,
                        productos=[("arroz", None), ("leche", 20)])])
    lect = _lectura("arrayanes", familias=30, productos=[("arroz", None), ("leche", 20.0)])
    cal = EV.calificar(reg, lect, L)
    assert cal["clase_lugar"] == "acierto seguro"            # el barrio y el albergue son el mismo punto
    assert cal["campos"]["_kg"] == [True]
    assert cal["campos"]["mensaje_sin_errores"]


def test_abstencion_y_lugar_inventado(L):
    reg = _reg("hay 44 familias sin panela quedamos atentos",
               [_pedido(None, None, familias=44, productos=[("panela", None)])], faltan=["lugar"])
    cal = EV.calificar(reg, _lectura("quedamos atentos", familias=44, productos=[("panela", None)]), L)
    assert cal["campos"]["abstencion_lugar"] is False and cal["clase_lugar"] == "inventa sin compromiso"
    cal = EV.calificar(reg, _lectura(None, familias=44, productos=[("panela", None)]), L)
    assert cal["campos"]["abstencion_lugar"] is True and cal["campos"]["mensaje_sin_errores"]


def test_personas_leidas_como_familias(L):
    reg = _reg("en bavaria hay 25 pers sin agua", [_pedido("bavaria", "Bavaria", personas=25, productos=[("agua", None)])])
    cal = EV.calificar(reg, _lectura("bavaria", familias=25, productos=[("agua", None)]), L)
    assert cal["campos"]["personas_como_familias"] is True and cal["campos"]["personas"] is False


def test_dos_pedidos_se_empareja_con_el_mejor_y_no_se_detecta(L):
    reg = _reg("40 familias en chipre necesitan arroz y en solferino hay 12 familias sin agua",
               [_pedido("chipre", "Chipre", familias=40, productos=[("arroz", None)]),
                _pedido("solferino", "Solferino", familias=12, productos=[("agua", None)])])
    cal = EV.calificar(reg, _lectura("solferino", familias=12, productos=[("arroz", None), ("agua", None)]), L)
    assert cal["campos"]["dos_pedidos_detectados"] is False
    assert cal["campos"]["lugar_acierto_seguro"] and cal["campos"]["familias"]
    assert cal["productos"] == {"vp": 1, "fp": 1, "fn": 0, "perdidos": 1}   # el arroz de Chipre iría a Solferino
    p = EV.agregar([cal])["productos"]
    assert p["exhaustividad"] == 1.0 and p["exhaustividad_con_perdidos"] == pytest.approx(0.5)


def test_lugar_ambiguo_no_debe_comprometerse(L):
    reg = _reg("en el tablazo hay 18 familias sin comida",
               [_pedido("el tablazo", None, familias=18, ambiguo=["Alto Tablazo", "Bajo Tablazo"])])
    cal = EV.calificar(reg, _lectura("el tablazo", familias=18), L)
    assert cal["campos"]["lugar_dudoso_sin_compromiso"] and cal["clase_lugar"] in ("por opciones", "no sé")


def test_tipo_entrega_y_otro(L):
    reg = {"id": "d", "origen": "a_mano", "variante": "entrega", "etiquetas": [], "texto": "ENTREGADO DX-4MQ7",
           "oro": {"tipo": "entrega", "pedidos": [], "cierre": None, "entregado": "DX-4MQ7"}, "faltan": []}
    lect = EV.a_dict(EV.lectura_reglas(reg["texto"]))
    cal = EV.calificar(reg, lect, L)
    assert lect["tipo"] == "entrega" and cal["campos"]["codigo_entrega"] and cal["campos"]["mensaje_sin_errores"]
    otro = {**reg, "texto": "hola como estan", "oro": {"tipo": "otro", "pedidos": [], "cierre": None, "entregado": None}}
    lect = EV.a_dict(EV.lectura_reglas(otro["texto"]))
    assert lect["tipo"] == "otro" and lect["fallo"] and EV.calificar(otro, lect, L)["campos"]["tipo"]


def test_con_otro_conjunto_la_salida_va_fuera_del_repositorio(tmp_path, monkeypatch, capsys):
    otro = tmp_path / "reales.jsonl"
    otro.write_text("", encoding="utf-8")
    adentro = EV.AQUI / "no_debe_crearse"
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")
    assert EV.main(["--conjunto", str(otro)]) == 2
    assert EV.main(["--conjunto", str(otro), "--salida", str(adentro)]) == 2
    # medir_modelo no corre con DESPACHOX_SIN_RED=1; sin la variable y sin --confirmo-gasto tampoco llama al modelo
    monkeypatch.delenv("DESPACHOX_SIN_RED")
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    assert MM.main(["--conjunto", str(otro), "--salida", str(adentro)]) == 2
    out = capsys.readouterr().out
    assert "obligatoria" in out and out.count("dentro del repositorio") == 2 and not adentro.exists()
    assert EV.carpeta_de_salida(otro, tmp_path / "s", EV.AQUI) == tmp_path / "s"
    assert EV.carpeta_de_salida(EV.CONJUNTO, None, EV.AQUI) == EV.AQUI      # el congelado puede quedarse aquí


def test_evaluar_no_deja_carpetas_temporales(monkeypatch, tmp_path):
    monkeypatch.setattr(EV.tempfile, "tempdir", str(tmp_path))
    EV.evaluar(EV.cargar_conjunto()[:2], medir_tiempo=False)
    assert list(tmp_path.iterdir()) == []


def test_evaluar_de_punta_a_punta_en_tres_mensajes(L):
    conjunto = EV.cargar_conjunto()
    sms = [r for r in conjunto if r["variante"] == "sms"][:3]
    res = EV.evaluar(sms, con=L.con, medir_tiempo=False)
    assert res["metricas"]["todos"]["tipo"]["aciertos"] == 3
    assert set(res["metricas"]) >= {"todos", "generados", "variante:sms"}


# ---------- script del extractor con modelo: tope duro, sin red ----------

def _falso(texto):
    from entrada.extraer import crudo
    return crudo(texto)               # como si el modelo hubiera fallado: el bot sigue con las reglas


def test_el_tope_nunca_se_pasa():
    t = MM.Tope(_falso, 3)
    for _ in range(3):
        t("PEDIDO 1 CHIPRE ARROZ")
    with pytest.raises(MM.TopeAlcanzado):
        t("PEDIDO 1 CHIPRE ARROZ")
    assert t.llamadas == 3
    assert MM.Tope(_falso, 10_000).tope == MM.TOPE_LLAMADAS == 330


def test_medir_hace_una_llamada_por_mensaje_y_para_en_el_tope(L):
    conjunto = EV.cargar_conjunto()[:8]
    res, contador = MM.medir(conjunto, _falso, tope=4)
    assert contador.llamadas == 4 and len(res["lecturas"]) == 4


def test_sin_red_o_sin_clave_no_llama(monkeypatch):
    def prohibido(texto):
        raise AssertionError("no debía llamar al modelo")
    monkeypatch.setattr("entrada.extraer.extraer", prohibido)
    monkeypatch.setenv("DESPACHOX_SIN_RED", "1")
    assert MM.main(["--confirmo-gasto"]) == 2
    monkeypatch.delenv("DESPACHOX_SIN_RED")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **k: False)
    assert MM.main(["--confirmo-gasto"]) == 2
