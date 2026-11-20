import pytest

from entrada.privacidad import hash_remitente, limpiar


@pytest.mark.parametrize("texto, prohibido", [
    ("somos 20 familias mi cel es 3105551234", "3105551234"),
    ("llamar al 310 555 12 34 urgente", "555"),
    ("tel +57 311-555-0101", "0101"),
    ("cc 1.053.123.456 de Manizales", "053"),
    ("cedula 30123456", "30123456"),
    ("fijo 606 887 1234", "887"),
    ("escriban a alguien@correo.com", "@"),
    ("me llamo Pedro Gomez y somos 20 familias", "Pedro"),
    ("Habla doña Rosa Marín del comité", "Rosa"),
    ("Soy María Pérez, necesitamos agua", "María"),
    ("mi nombre es juan carlos somos 12", "juan"),
])
def test_quita_lo_que_parece_dato_personal(texto, prohibido):
    assert prohibido not in limpiar(texto)


@pytest.mark.parametrize("texto", [
    "somos 40 familias en san jose no hay arroz ni leche",
    "necesitamos 50 kilos de arroz y 20 de frijol para 30 familias",
    "pedimos 20 30 40 kilos segun alcance",
    "soy del comite de san jose somos 40",
    "derrumbe en la via a chinchina km 12 no pasan camiones",
    "somos 1200 personas en 3 albergues",
])
def test_no_toca_las_cifras_del_pedido(texto):
    assert limpiar(texto) == texto


def test_hash_estable_con_sal_y_sin_el_id(monkeypatch):
    a = hash_remitente(123456789)
    assert a == hash_remitente("123456789") and "123456789" not in a and len(a) == 32
    assert a != hash_remitente(123456780)
    monkeypatch.setenv("DESPACHOX_SAL", "otra-sal")
    assert hash_remitente(123456789) != a


def test_sal_en_archivo_junto_a_la_base(monkeypatch, tmp_path):
    monkeypatch.delenv("DESPACHOX_SAL")
    monkeypatch.setenv("DESPACHOX_DB", str(tmp_path / "x.db"))
    a = hash_remitente(5)
    assert (tmp_path / "x.sal").exists() and a == hash_remitente(5)
