"""«Café» dentro de un nombre de lugar no es un producto pedido (revisión del sábado 21 de noviembre)."""
import pytest

from entrada.sms import leer_sms


def _productos(texto):
    x = leer_sms(texto)
    return x.pedido.lugar, [q.producto for q in x.pedido.productos]


@pytest.mark.parametrize("texto, lugar, productos", [
    ("somos 30 familias en villa cafe no hay arroz", "villa cafe", ["arroz"]),
    ("somos 20 familias en la autopista del cafe no hay leche", "la autopista del cafe", ["leche"]),
])
def test_cafe_en_un_nombre_de_lugar_no_es_producto(texto, lugar, productos):
    assert _productos(texto) == (lugar, productos)


@pytest.mark.parametrize("texto, productos", [
    ("somos 30 familias en san jose necesitamos arroz y cafe", ["arroz", "café"]),
    ("30 familias en villa cafe necesitan cafe y panela", ["café", "panela"]),
    ("no hay cafe ni panela en la enea somos 12 familias", ["café", "panela"]),
])
def test_cafe_pedido_sigue_siendo_producto(texto, productos):
    assert _productos(texto)[1] == productos
