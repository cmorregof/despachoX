"""Quince mensajes sintéticos con la lectura que se espera de cada uno. Ninguno es de una persona real.

`esperado` es a la vez la respuesta del extractor falso de las pruebas y la referencia contra la que
se mide el extractor real (test_campos.py). Solo se califican los campos listados en `califica`.
"""
TODOS = ["camion", "campero", "moto"]


def _p(lugar, familias, productos, urgencia=2, horas=None):
    return {"lugar": lugar, "familias": familias, "urgencia": urgencia, "horas_limite": horas,
            "productos": [{"producto": x, "kg": None} if isinstance(x, str) else {"producto": x[0], "kg": x[1]}
                          for x in productos]}


def _c(lugar, descripcion, tipos=TODOS):
    return {"lugar": lugar, "descripcion": descripcion, "tipos_bloqueados": tipos}


BASE_PEDIDO = ["tipo", "lugar", "familias", "productos", "urgencia"]
BASE_CIERRE = ["tipo", "cierre.lugar", "cierre.tipos_bloqueados"]

MENSAJES = [
    {"id": 1, "nota": "sin puntuación ni tildes; el caso del encargo",
     "texto": "somos 40 familias en san jose no hay arroz ni leche",
     "esperado": {"tipo": "pedido", "pedido": _p("san jose", 40, ["arroz", "leche"])}, "califica": BASE_PEDIDO},
    {"id": 2, "nota": "errores de tipeo y urgencia por niños",
     "texto": "buenas tardes necesitamso mercado para 25 familias del barrio la enea urjente hay niños sin comer",
     "esperado": {"tipo": "pedido", "pedido": _p("la enea", 25, ["mercado"], 3)}, "califica": BASE_PEDIDO},
    {"id": 3, "nota": "abreviatura «flias» y barrio partido en dos palabras",
     "texto": "aca en villa hermosa somos como 60 flias sin agua ni panela desde ayer",
     "esperado": {"tipo": "pedido", "pedido": _p("villa hermosa", 60, ["agua", "panela"])}, "califica": BASE_PEDIDO},
    {"id": 4, "nota": "kilos explícitos",
     "texto": "URGENTE albergue de san jorge 30 familias necesitan 50 kilos de arroz y 20 de frijol",
     "esperado": {"tipo": "pedido", "pedido": _p("albergue de san jorge", 30, [("arroz", 50), ("frijol", 20)], 3)},
     "califica": BASE_PEDIDO + ["kg"]},
    {"id": 5, "nota": "puede esperar",
     "texto": "en chipre 12 familias necesitan lentejas y aceite pero podemos esperar hasta mañana",
     "esperado": {"tipo": "pedido", "pedido": _p("chipre", 12, ["lenteja", "aceite"], 1)}, "califica": BASE_PEDIDO},
    {"id": 6, "nota": "plazo en horas",
     "texto": "comedor de belen 80 familias leche y huevos lo necesitamos en 3 horas porfa",
     "esperado": {"tipo": "pedido", "pedido": _p("comedor de belen", 80, ["leche", "huevo"], 2, 3)},
     "califica": ["tipo", "lugar", "familias", "productos", "horas_limite"]},
    {"id": 7, "nota": "no dice dónde ni qué: debe quedar en dudas",
     "texto": "nesecitamos ayuda somos 15 familias",
     "esperado": {"tipo": "pedido", "pedido": _p(None, 15, []), "dudas": ["¿En qué barrio están?", "¿Qué productos necesitan?"]},
     "califica": ["tipo", "lugar", "familias", "productos", "dudas"]},
    {"id": 8, "nota": "cierre solo para camiones",
     "texto": "derrumbe en la via a chinchina no pasan camiones",
     "esperado": {"tipo": "cierre", "cierre": _c("via a chinchina", "derrumbe", ["camion"])}, "califica": BASE_CIERRE},
    {"id": 9, "nota": "cierre total sin puntuación",
     "texto": "se cayo un arbol en la avenida santander no pasa nadie",
     "esperado": {"tipo": "cierre", "cierre": _c("avenida santander", "árbol caído")}, "califica": BASE_CIERRE},
    {"id": 10, "nota": "tipeo en la vía; solo pasan motos",
     "texto": "ojo la panamerciana esta tapada x un deslizamiento solo pasan motos",
     "esperado": {"tipo": "cierre", "cierre": _c("panamericana", "deslizamiento", ["camion", "campero"])},
     "califica": BASE_CIERRE},
    {"id": 11, "nota": "cierre total",
     "texto": "puente caido por la salida a letras paso cerrado total",
     "esperado": {"tipo": "cierre", "cierre": _c("salida a letras", "puente caído")}, "califica": BASE_CIERRE},
    {"id": 12, "nota": "sitio por fuera del casco urbano, dicho con apodo",
     "texto": "derrumbe por la siria no hay paso",
     "esperado": {"tipo": "cierre", "cierre": _c("la siria", "derrumbe")}, "califica": BASE_CIERRE},
    {"id": 13, "nota": "mezcla pedido y cierre",
     "texto": "somos 35 familias en el carmen sin arroz ni aceite y ademas la avenida paralela esta cerrada "
              "por un derrumbe no pasan camiones",
     "esperado": {"tipo": "pedido", "pedido": _p("el carmen", 35, ["arroz", "aceite"]),
                  "cierre": _c("avenida paralela", "derrumbe", ["camion"])},
     "califica": BASE_PEDIDO + ["cierre.lugar", "cierre.tipos_bloqueados"]},
    {"id": 14, "nota": "no es pedido ni cierre",
     "texto": "hola buenas como hago para ser voluntario",
     "esperado": {"tipo": "otro"}, "califica": ["tipo"]},
    {"id": 15, "nota": "trae nombre y teléfono inventados: no deben guardarse",
     "texto": "me llamo Pedro Gomez cel 3105551234 somos 20 familias en fatima necesitamos agua",
     "esperado": {"tipo": "pedido", "pedido": _p("fatima", 20, ["agua"])}, "califica": BASE_PEDIDO},
]
