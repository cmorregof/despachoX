from entrada import extraer as E


def test_sin_clave_no_lanza_y_devuelve_otro_con_el_texto(monkeypatch):
    for v in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE"):
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://127.0.0.1:9")     # nada escucha ahí: tampoco hay red
    monkeypatch.setenv("ANTHROPIC_CONFIG_DIR", "/nonexistent")
    monkeypatch.setattr(E, "SEGUNDOS", 0.5)
    x = E.extraer("somos 40 familias en san jose")
    assert x.tipo == "otro" and x.fallo and x.texto == "somos 40 familias en san jose"


def test_si_el_modelo_responde_mal_no_lanza(monkeypatch):
    import anthropic

    class Roto:
        def __init__(self, **k):
            raise RuntimeError("sin servicio")
    monkeypatch.setattr(anthropic, "Anthropic", Roto)
    assert E.extraer("hola").fallo


def test_respuesta_del_modelo_se_valida_y_se_recorta(monkeypatch):
    import anthropic
    from types import SimpleNamespace
    lectura = E.Lectura(tipo="otro", dudas=[], cierre=None, pedido=E.Pedido(
        lugar=" San José ", familias=-3, urgencia=9, horas_limite=500,
        productos=[E.Producto(producto=" Arroz ", kg=0), E.Producto(producto="", kg=None)]))
    pedido = {}

    class Falso:
        def __init__(self, **k):
            self.messages = self

        def parse(self, **k):
            pedido.update(k)
            return SimpleNamespace(stop_reason="end_turn", parsed_output=lectura)
    monkeypatch.setattr(anthropic, "Anthropic", Falso)
    x = E.extraer("  somos familias en San José sin arroz ")
    assert pedido["output_format"] is E.Lectura and pedido["model"] == E.MODELO
    assert "somos familias" in pedido["messages"][0]["content"]
    assert x.tipo == "pedido" and not x.fallo                      # había pedido: el tipo se corrige
    p = x.pedido
    assert (p.lugar, p.familias, p.urgencia, p.horas_limite) == ("San José", None, 3, None)
    assert [(q.producto, q.kg) for q in p.productos] == [("arroz", None)]


def test_vacio_es_otro_sin_fallo():
    x = E.extraer("   ")
    assert x.tipo == "otro" and not x.fallo
