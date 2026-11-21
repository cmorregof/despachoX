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


def test_sin_tope_lee_todos_los_textos():
    t = R.texto_para_modelo(grupo(75))
    assert "75. pedido 75" in t and "textos más" not in t


def test_tope_de_textos_opcional():
    t = R.texto_para_modelo(grupo(75), tope_textos=60)
    assert "60. pedido 60" in t and "61. pedido 61" not in t
    assert "y 15 textos más." in t


def test_resumir_con_extractor_falso_no_corta():
    recibido = []

    def falso(texto):
        recibido.append(texto)
        return "  Piden arroz y leche. " + "x" * 1000
    r = R.resumir(grupo(), falso)
    assert r.startswith("Piden arroz y leche.") and len(r) == len("Piden arroz y leche. ") + 1000
    assert len(R.resumir(grupo(), falso, tope=100)) == 100
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


# ---------- la mesa entera y el comando ----------

def _grupos_de_prueba(con):
    from despacho import agrupar
    con.executemany("INSERT INTO puntos(id,nombre,barrio,lat,lon,critico) VALUES (?,?,?,?,?,?)",
                    [(1, "Albergue A", "A", 5.07, -75.52, 1), (2, "Salón B", "B", 5.05, -75.50, 0)])
    con.executemany("INSERT INTO pedidos(id,creado_en,punto_id,familias,kg_estimado,urgencia,estado,texto_original) "
                    "VALUES (?,?,?,?,?,?,'nuevo',?)", [
        (1, "2026-11-21T10:00:00-05:00", 1, 10, 100, 3, "Somos 10 familias en A, necesitamos arroz. hay bebés."),
        (2, "2026-11-21T10:10:00-05:00", 1, 5, 50, 2, "Somos 5 familias en A, necesitamos agua."),
        (3, "2026-11-21T10:20:00-05:00", 2, 8, 80, 1, "Somos 8 familias en B, necesitamos panela.")])
    con.commit()
    return agrupar.grupos_nuevos(con)


def test_texto_mesa_trae_totales_y_una_linea_por_grupo(tmp_path):
    from datos import db
    from despacho import resumen_grupo as R
    con = db.conectar(tmp_path / "m.db")
    grupos = _grupos_de_prueba(con)
    t = R.texto_mesa(grupos, {grupos[0].clave: "piden arroz y agua; hay bebés"}, {1: "Albergue A", 2: "Salón B"})
    assert "2 grupos" in t and "1 en puntos críticos" in t
    assert "Albergue A (CRÍTICO) · 2 pedidos · 15 familias" in t and "piden arroz y agua; hay bebés" in t
    assert "Salón B · 1 pedidos" in t and "panela" in t            # sin resumen, van los textos
    assert "No ordene los grupos" in t


def test_resumir_mesa_guarda_y_no_repite(tmp_path):
    from datos import db
    from despacho import resumen_grupo as R
    con = db.conectar(tmp_path / "m.db")
    grupos = _grupos_de_prueba(con)
    llamadas = []
    extractor = lambda t: llamadas.append(t) or "resumen de la mesa"
    assert R.resumir_mesa(con, grupos, extractor, "falso") is True
    assert R.leer_mesa(con, grupos)["resumen"] == "resumen de la mesa"
    assert R.resumir_mesa(con, grupos, extractor, "falso") is False      # ya existe
    assert len(llamadas) == 1
    con.execute("UPDATE pedidos SET estado='confirmado' WHERE id=3")
    con.commit()
    from despacho import agrupar
    assert R.leer_mesa(con, agrupar.grupos_nuevos(con)) is None          # cambió la mesa: otra clave


def test_comando_falso_resume_grupos_y_mesa(tmp_path, monkeypatch, capsys):
    import json
    from datos import db
    from despacho import resumen_grupo as R
    monkeypatch.setenv("DESPACHOX_AGRUPAR", "1")
    con = db.conectar(tmp_path / "m.db")
    _grupos_de_prueba(con)
    con.close()
    assert R.main(["--resumir", "--falso", "--db", str(tmp_path / "m.db")]) == 0
    r = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert r["grupos"] == 2 and r["resumidos"] == 2 and r["mesa"] is True and r["llamadas"] == 0
    assert r["sin_resumen"] == 0 and r["modelo"] == "falso" and r["modelo_mesa"] == "falso"
    con = db.conectar(tmp_path / "m.db")
    assert con.execute("SELECT COUNT(*) FROM resumenes_grupo").fetchone()[0] == 3
    assert "resumen de ensayo" in con.execute("SELECT resumen FROM resumenes_grupo WHERE clave LIKE 'mesa:%'").fetchone()[0]
    assert con.execute("SELECT COUNT(*) FROM bitacora WHERE accion='resumir grupos'").fetchone()[0] == 1


def test_resumen_vacio_no_se_guarda(tmp_path):
    from datos import db
    from despacho import resumen_grupo as R
    con = db.conectar(tmp_path / "m.db")
    grupos = _grupos_de_prueba(con)
    assert R.resumir_y_guardar(con, grupos, lambda t: "", "falso", a_la_vez=4) == 0
    assert con.execute("SELECT COUNT(*) FROM resumenes_grupo").fetchone()[0] == 0
