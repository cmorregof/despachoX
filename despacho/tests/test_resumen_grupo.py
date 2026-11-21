"""Pruebas de despacho/resumen_grupo.py con extractor falso. Ninguna llama a un modelo."""
from __future__ import annotations

from dataclasses import dataclass, field

from datos import db
from despacho import resumen_grupo as R


@dataclass
class G:
    """Grupo de prueba con los campos de despacho/agrupar.Grupo que usa el resumen."""
    clave: str
    punto_id: int
    pedidos: list[dict]
    familias: int = 0
    kg: float = 0.0
    pedido_ids: list[int] = field(default_factory=list)

    def __post_init__(self):
        self.pedido_ids = self.pedido_ids or [p["id"] for p in self.pedidos]


def grupo(n=3, clave="p1-a"):
    pedidos = [{"id": i, "texto_original": f"pedido {i}: arroz y leche para bebés", "familias": 4,
                "kg_estimado": 10.0} for i in range(1, n + 1)]
    return G(clave=clave, punto_id=1, pedidos=pedidos, familias=4 * n, kg=10.0 * n)


def test_texto_para_modelo_lleva_numeros_y_textos_limpios():
    g = grupo(3)
    g.pedidos[1]["texto_original"] = "me llamo Ana Pérez, mi cel 310 555 1234, somos 5 familias"
    g.pedidos[2]["texto_original"] = None
    t = R.texto_para_modelo(g, {1: "Albergue A"})
    assert "Pedidos: 3." in t and "Familias sumadas por el sistema: 12" in t and "30" in t
    assert "Albergue A" in t
    assert "1. pedido 1: arroz y leche para bebés" in t
    assert "310 555 1234" not in t and "Ana" not in t and "[número]" in t
    assert "3. (sin texto)" in t
    assert "Prohibido inventar cantidades" in t


def test_tope_de_60_textos():
    t = R.texto_para_modelo(grupo(75))
    assert "60. pedido 60" in t and "61. pedido 61" not in t
    assert "y 15 textos más." in t


def test_resumir_con_extractor_falso_recorta():
    recibido = []

    def falso(texto):
        recibido.append(texto)
        return "  Piden arroz y leche. " + "x" * 1000
    r = R.resumir(grupo(), falso)
    assert r.startswith("Piden arroz y leche.") and len(r) == R.TOPE_RESUMEN
    assert "Pedidos: 3." in recibido[0]


def test_guardar_y_leer(tmp_path):
    con = db.conectar(tmp_path / "x.db")
    con.execute("INSERT INTO puntos(id,nombre,lat,lon) VALUES (1,'A',5.0,-75.5)")
    g = grupo()
    g.pedido_ids = [3, 1, 2]
    assert R.leer(con, g.clave) is None
    R.guardar(con, g, "Piden arroz.", "falso")
    r = R.leer(con, g.clave)
    assert r["resumen"] == "Piden arroz." and r["modelo"] == "falso" and r["pedido_ids"] == [1, 2, 3]
    R.guardar(con, g, "Otro resumen.", "falso")
    assert R.leer(con, g.clave)["resumen"] == "Otro resumen."


def test_resumir_y_guardar_no_repite(tmp_path):
    con = db.conectar(tmp_path / "x.db")
    con.execute("INSERT INTO puntos(id,nombre,lat,lon) VALUES (1,'A',5.0,-75.5)")
    llamadas = []

    def falso(texto):
        llamadas.append(texto)
        return "Piden mercados."
    grupos = [grupo(clave="a"), grupo(clave="b")]
    assert R.resumir_y_guardar(con, grupos, falso) == 2
    assert R.resumir_y_guardar(con, grupos, falso) == 0
    assert len(llamadas) == 2
    assert R.resumir_y_guardar(con, grupos, falso, solo_faltantes=False) == 2
    assert len(llamadas) == 4
