"""Lector de SMS por reglas: sin internet y sin modelo de lenguaje.

    leer_sms("PEDIDO 40 SAN JOSE ARROZ LECHE")      -> Extraccion(tipo="pedido", ...)
    leer_sms("PEDIDO 6 BEBES LA ENEA LECHE URGENTE")
    leer_sms("CIERRE AV DEL CENTRO CAMION")          -> Extraccion(tipo="cierre", ...)
    leer_sms("ENTREGADO DX7K2Q")                     -> Extraccion(tipo="otro", entregado="DX-7K2Q")

Devuelve el mismo objeto que el extractor con modelo, así el resto del flujo no cambia. El formato
está en `docs/SIN_CONEXION.md`. Es tolerante: minúsculas, sin tildes, orden variable, palabras de
relleno y errores de tipeo en las palabras clave (`PEDDO`, `CIERE`). El número son familias, o
personas o bebés si lo dice. Los productos salen de la tabla de `raciones`. Lo que no es palabra
clave, número, producto ni relleno se toma como el lugar, y lo ubica `lugares/` sin modelo.

Lo que no se entiende vuelve con `fallo=True`, y el flujo lo guarda como pedido `nuevo` con el
texto: nunca se descarta. Como el extractor con modelo, este lector solo lee: no decide nada.
"""
from __future__ import annotations

import re
import sys
from difflib import SequenceMatcher

from entrada import raciones
from entrada.extraer import Cierre, Extraccion, Pedido, Producto, crudo
from lugares import normalizar

VEHICULOS = {"camion": "camion", "camiones": "camion", "campero": "campero", "camperos": "campero",
             "jeep": "campero", "moto": "moto", "motos": "moto"}
TODOS = ["camion", "campero", "moto"]
# Palabras clave y sus sinónimos. Las dos primeras columnas se comparan con tolerancia a errores.
CLAVES = {"pedido": "pedido", "pedidos": "pedido", "pedimos": "pedido", "necesitamos": "pedido",
          "cierre": "cierre", "cierres": "cierre", "cerrado": "cierre", "cerrada": "cierre",
          "bloqueo": "cierre", "bloqueada": "cierre", "bloqueado": "cierre",
          "entregado": "entregado", "entregada": "entregado", "entrega": "entregado",
          "entregamos": "entregado"}
DESCRIPCIONES = {"derrumbe": "derrumbe", "deslizamiento": "deslizamiento", "arbol": "árbol caído",
                 "puente": "puente caído", "inundacion": "inundación", "hueco": "hueco en la vía",
                 "accidente": "accidente"}
FAMILIAS = {"familias", "familia", "flias", "flia", "fam", "fams", "hogares", "hogar"}
PERSONAS = {"personas", "persona", "gente", "adultos", "adulto", "ninos", "nino", "ninas", "nina",
            "abuelos", "ancianos", "mayores", "habitantes", "vecinos", "menores"}
BEBES = {"bebes", "bebe", "bebito", "bebitos", "lactantes", "recien"}
KILOS = {"kg", "kilos", "kilo", "k", "kgs"}
URGENTE = {"urgente", "urjente", "urgencia", "urge", "urgentes", "emergencia"}
ESPERA = {"esperar", "espera"}
VULNERABLES = BEBES | {"ninos", "nino", "ninas", "abuelos", "ancianos", "mayores", "enfermos"}
# Relleno: se quita de los bordes del lugar, nunca de adentro («la enea», «av del centro»).
RELLENO = {"hola", "buenas", "buenos", "dias", "tardes", "noches", "por", "favor", "porfa", "gracias",
           "somos", "hay", "en", "para", "de", "del", "sin", "y", "e", "con", "ni", "no", "tenemos",
           "desde", "ayer", "hoy", "manana", "aca", "aqui", "barrio", "sector", "el", "la", "los", "las",
           "nos", "falta", "faltan", "queda", "quedo", "pasa", "pasan", "nadie", "total", "solo",
           "numero", "esta", "estan", "un", "una", "que", "se", "cayo", "mas", "o", "menos", "como",
           "unas", "unos", "comida", "mercado", "mercados", "ayuda", "alimentos",
           # presentación y marcas que deja privacidad.limpiar: nunca son el lugar
           "me", "llamo", "mi", "soy", "nombre", "cel", "celular", "telefono", "tel", "whatsapp",
           "correo", "cedula", "cc"}
ABREVIATURAS = {"av": "avenida", "avda": "avenida", "cra": "carrera", "kra": "carrera", "cll": "calle",
                "b": "barrio", "q": "que", "x": "por", "xfa": "por favor"}
LIMITE_SMS = 160
# Un código sin «DX» solo vale en un mensaje así de corto («ENTREGADO 7K2Q gracias»): en uno largo,
# palabras como «enea» o «para» caben en el alfabeto de los códigos (revisión QA de la noche).
CORTO = 3
# Antes de «entregado», cambian el sentido: «todavía no nos han entregado DX-7KQ3» es un reclamo.
NEGACIONES = {"no", "nunca", "jamas", "todavia", "aun", "ni", "sin", "falta", "faltan"}
_CODIGO = re.compile(r"^(dx)?[a-z0-9]{4,6}$")
_DX_SEPARADO = re.compile(r"\bdx\s+([a-z0-9]{4,6})\b")      # «DX-4MQ7» llega como «dx 4mq7»
_TILDES = str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU")


def _parecido(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _clave(token: str, primera: bool) -> str | None:
    """La palabra clave que este token quiso escribir. Con errores de tipeo solo se acepta en la
    primera palabra, que es la que dice el tipo: en otra posición, «entrada» no es «entregada»."""
    if token in CLAVES:
        return CLAVES[token]
    if not primera or len(token) < 5:
        return None
    mejor = max(CLAVES, key=lambda k: _parecido(token, k))
    return CLAVES[mejor] if _parecido(token, mejor) >= 0.8 else None


def _catalogo() -> dict[str, str]:
    """Cada forma escrita de un producto -> su nombre en la bodega."""
    nombres = set(raciones.KG_POR_FAMILIA) | set(raciones.PARA_BEBES) | raciones.SIN_RACION | {"mercado"}
    tabla = {normalizar(n): n for n in nombres}
    tabla.update({normalizar(k): raciones.canonico(k) for k in raciones.SINONIMOS})
    tabla.update({"panales": "pañales", "panal": "pañales", "formula": "leche de fórmula",
                  "huevo": "huevos", "lentejas": "lenteja", "frijoles": "frijol", "verduras": "verdura",
                  "frutas": "fruta", "harina": "harina de maíz", "aguas": "agua"})
    return tabla


CATALOGO = _catalogo()


def _producto(tokens: list[str], i: int) -> tuple[str | None, int]:
    """El producto que empieza en tokens[i] (puede ser de varias palabras) y cuántos tokens ocupa."""
    for largo in (3, 2, 1):
        frase = " ".join(tokens[i:i + largo])
        if len(tokens[i:i + largo]) == largo and frase in CATALOGO:
            return CATALOGO[frase], largo
    t = tokens[i]
    if len(t) >= 5:                                 # «arros», «lechee», «panela»
        mejor = max((k for k in CATALOGO if " " not in k), key=lambda k: _parecido(t, k))
        if _parecido(t, mejor) >= 0.84:
            return CATALOGO[mejor], 1
    return None, 0


def _lugar(tramos: list[list[str]]) -> str | None:
    """El tramo de palabras sin clasificar más largo, sin relleno en los bordes."""
    mejor = []
    for tramo in tramos:
        while tramo and tramo[0] in RELLENO and not (tramo[0] in {"la", "el", "los", "las"} and len(tramo) > 1
                                                       and tramo[1] not in RELLENO):
            tramo = tramo[1:]
        while tramo and tramo[-1] in RELLENO:
            tramo = tramo[:-1]
        if len(tramo) > len(mejor):
            mejor = tramo
    return " ".join(mejor) or None


def leer_sms(texto: str) -> Extraccion:
    """Lee un SMS con reglas. Nunca lanza excepción ni llama a la red."""
    texto = (texto or "").strip()
    if not texto:
        return Extraccion(tipo="otro", texto=texto)
    try:
        return _leer(texto)
    except Exception:                       # una regla mal escrita no puede perder el mensaje
        return crudo(texto)


def _es_codigo(t: str, corto: bool = True) -> bool:
    """Un código de paquete: «dx» más 4 a 6 signos, o, si el mensaje es corto, 4 signos del alfabeto
    de despacho/paquetes.py que no sean un producto (el alfabeto no tiene o, s, l ni i, así que «jose»
    no pasa). En un mensaje largo, «enea» o «para» no son un código."""
    from despacho.paquetes import ALFABETO
    if t.startswith("dx") and _CODIGO.match(t):
        return True
    return corto and len(t) == 4 and all(c in ALFABETO.lower() for c in t) and t not in CATALOGO


def _leer(texto: str) -> Extraccion:
    tokens = [ABREVIATURAS.get(t, t) for t in _DX_SEPARADO.sub(r"dx\1", normalizar(texto)).split()]
    tokens = " ".join(tokens).split()                   # «xfa» -> «por favor»
    corto = len(tokens) <= CORTO
    clave = pos_clave = None
    numero = unidad = None
    extra = {"personas": None, "bebes": None}     # «5 bebés 3 niños»: el segundo número también cuenta
    productos: list[Producto] = []
    kilos_pendientes = None
    vehiculos: list[str] = []
    solo_pasan = False
    urgencia = 2
    vulnerables = False
    descripcion = None
    codigo = None
    tramos, actual = [], []

    i = 0
    while i < len(tokens):
        t = tokens[i]
        consumido = 1
        clasificado = True
        k = _clave(t, i == 0)
        if k and clave is None:
            clave, pos_clave = k, i
        elif k and k == clave:
            pass
        elif t.isdigit():
            n = int(t)
            siguiente = tokens[i + 1] if i + 1 < len(tokens) else ""
            if siguiente in KILOS:
                kilos_pendientes = float(n)
                consumido = 2
            elif numero is None and 0 < n <= 5000:
                numero = n
                if siguiente in FAMILIAS | PERSONAS | BEBES:
                    unidad = "familias" if siguiente in FAMILIAS else "bebes" if siguiente in BEBES else "personas"
                    vulnerables |= siguiente in VULNERABLES
                    consumido = 2
            elif 0 < n <= 5000 and siguiente in PERSONAS | BEBES:
                extra["bebes" if siguiente in BEBES else "personas"] = n
                vulnerables |= siguiente in VULNERABLES
                consumido = 2
            else:
                clasificado = False
        elif t in FAMILIAS:
            pass
        elif t in BEBES | PERSONAS:
            vulnerables |= t in VULNERABLES
        elif t in URGENTE:
            urgencia = 3
        elif t in ESPERA:
            urgencia = 1
        elif t in VEHICULOS:
            vehiculos.append(VEHICULOS[t])
            solo_pasan |= i >= 2 and tokens[i - 1] in {"pasan", "pasa"} and tokens[i - 2] == "solo"
        elif t in DESCRIPCIONES:
            descripcion = DESCRIPCIONES[t]
        elif clave == "entregado" and codigo is None and _es_codigo(t, corto):
            codigo = t
        else:
            p, largo = _producto(tokens, i)
            if p and p != "mercado":
                kg = kilos_pendientes
                kilos_pendientes = None
                if not any(q.producto == p for q in productos):
                    productos.append(Producto(producto=p, kg=kg))
                consumido = largo
            elif p == "mercado":
                consumido = largo
            else:
                clasificado = False
        if clasificado:
            if actual:
                tramos.append(actual)
            actual = []
        else:
            actual.append(t)
        i += consumido
    if actual:
        tramos.append(actual)
    if kilos_pendientes and productos and productos[-1].kg is None:     # «arroz 50 kilos»
        productos[-1].kg = kilos_pendientes

    # Sin palabra clave: se deduce de lo que trae, como haría una persona.
    if clave is None:
        if len(tokens) == 1 and _es_codigo(tokens[0], corto=False):    # el código solo, como lo deja el QR;
            clave = "entregado"                                         # «no ha llegado DX-7KQ3» no es entrega
        elif numero is not None or productos:
            clave = "pedido"
        elif vehiculos or descripcion:
            clave = "cierre"
    if clave == "entregado":
        if any(t in NEGACIONES for t in tokens[:pos_clave or 0]):   # un reclamo: lo lee el despachador
            return crudo(texto)
        codigo = codigo or next((t for t in tokens if _es_codigo(t, corto)), None)
        if not codigo:
            return crudo(texto)
        from despacho.paquetes import normalizar_codigo
        return Extraccion(tipo="otro", texto=texto, entregado=normalizar_codigo(codigo))

    lugar = _lugar(tramos)
    if clave == "cierre":
        bloqueados = sorted(set(TODOS) - set(vehiculos)) if solo_pasan else sorted(set(vehiculos))
        return Extraccion(tipo="cierre", texto=texto, cierre=Cierre(
            lugar=lugar, descripcion=descripcion or "cierre reportado por SMS",
            tipos_bloqueados=bloqueados or TODOS), dudas=["Leído por reglas, sin modelo."])
    if clave == "pedido" and (numero is not None or productos or lugar):
        familias = numero if unidad in (None, "familias") else None
        return Extraccion(tipo="pedido", texto=texto, pedido=Pedido(
            lugar=lugar, familias=familias,
            personas=numero if unidad == "personas" else extra["personas"],
            bebes=numero if unidad == "bebes" else extra["bebes"],
            productos=productos, urgencia=3 if vulnerables and urgencia == 2 else urgencia, horas_limite=None),
            dudas=["Leído por reglas, sin modelo."])
    return crudo(texto)


# ---------- respuesta en un solo SMS ----------

def a_gsm(texto: str) -> str:
    """Sin tildes: una sola letra fuera del alfabeto GSM-7 baja el límite del SMS de 160 a 70."""
    return texto.translate(_TILDES)


def corto(texto: str, limite: int = LIMITE_SMS) -> str:
    texto = a_gsm(" ".join(texto.split()))
    return texto if len(texto) <= limite else texto[:limite - 3].rstrip(" ,.") + "..."


def _resumen(x: Extraccion) -> str:
    if x.pedido is not None:
        p = x.pedido
        partes = []
        if p.bebes:                     # lo que dijo la persona, antes que las familias que estimó la mesa
            partes.append(f"{p.bebes} bebes")
        elif p.personas:
            partes.append(f"{p.personas} pers")
        elif p.familias:
            partes.append(f"{p.familias} fam")
        partes += [q.producto for q in p.productos]
        if p.urgencia == 3:
            partes.append("URGENTE")
        return "pedido " + " ".join(partes) if partes else "pedido"
    if x.cierre is not None:
        c = x.cierre
        quien = "nadie" if set(c.tipos_bloqueados) == set(TODOS) else "/".join(c.tipos_bloqueados)
        return f"cierre, no pasa {quien}"
    return "mensaje"


def respuesta_sms(con, x: Extraccion, respuestas) -> str:
    """Convierte las respuestas del flujo (texto largo y botones de Telegram) en un SMS corto."""
    partes = []
    for r in respuestas:
        datos = [d for _, d in r.botones]
        si = next((d for d in datos if d.startswith("s:")), None)
        alternativas = [e.split(" (")[0] for e, d in r.botones if d.startswith("c:")]
        if si:
            u = con.execute("SELECT l.nombre FROM ubicaciones u JOIN lugares l ON l.id = u.lugar_id WHERE u.id=?",
                            (int(si.split(":")[1]),)).fetchone()
            donde = u["nombre"] if u else "el lugar"
            partes.append(f"Recibido: {_resumen(x)} en {donde}. Responda SI o el barrio correcto.")
        elif alternativas:
            opciones = " o ".join(alternativas[:2])
            partes.append(f"Recibido: {_resumen(x)}. Es en {opciones}? Responda con el barrio.")
        elif any(d.startswith("f:") for d in datos):
            partes.append(r.texto.split("\n")[0] + " Para cuantas familias? Responda con el numero.")
        elif datos and all(d.startswith("p:") for d in datos):
            partes.append(f"Recibido: {_resumen(x)}. Donde es? Responda con el barrio o la via.")
        else:
            partes.append(r.texto.split("\n")[0])
    return corto(" | ".join(partes) or "Recibido. La mesa lo revisa.")


def atender_sms(mesa, numero: str, texto: str) -> str:
    """Un SMS de punta a punta: lo lee, lo guarda con el mismo flujo del bot y devuelve el SMS de
    respuesta. `numero` se convierte en hash dentro del flujo; nunca se guarda en claro."""
    x = mesa.leer(texto)
    return respuesta_sms(mesa.con, x, mesa.atender_seguro(numero, x))


if __name__ == "__main__":      # python -m entrada.sms "PEDIDO 40 SAN JOSE ARROZ LECHE"
    for t in sys.argv[1:]:
        print(leer_sms(t).model_dump_json(indent=2, exclude_none=True))
