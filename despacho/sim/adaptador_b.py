"""Adaptador al optimizador de B (`despacho/optimizar.py`, OR-Tools).

Traduce el `Estado` de la simulación a las filas que el optimizador lee de la base y llama a
su modelo (`optimizar._resolver`), que no toca la base. Así la simulación mide el mismo modelo
que usa el producto: su surtido de lotes, sus ventanas, sus pesos y su búsqueda.

Lo que hay que saber de ese modelo, porque condiciona a las políticas:
- planea UN viaje por vehículo y solo asigna pedidos nuevos a vehículos que están en el acopio;
- a un vehículo en ruta le conserva lo que lleva a bordo y le reordena las entregas;
- el límite de búsqueda es de segundos enteros, con mínimo de 1 s por llamada.

Con velocidades medidas (`DESPACHOX_SIM_VELOCIDADES=medidas`), el modelo de B tiene que planear
con los mismos tiempos que la jornada simulada. Sin tocar `optimizar.py` ni `matriz.py`, el
adaptador arma una copia del grafo por tipo de vehículo con el `travel_time` de las velocidades
medidas, y durante cada llamada `matriz.calcular` lee la copia de cada tipo. Sin la variable
no se arma ninguna copia ni se reemplaza nada: el modelo recibe el grafo de `red.cargar()`.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

from .red_sim import TIPOS, modo_velocidades, ruta_cache, segundos_medidos, velocidades_medidas, _via

T0 = (2026, 8, 11, 6, 0)          # hora 0 de la jornada simulada (fecha de adorno)
LOTE_SECO = 900_000               # lote ficticio de no perecederos, sin límite
LOTE_A_BORDO = 1_000_000          # lotes ficticios para lo que ya va cargado
_GRAFOS_MEDIDOS: dict = {}        # id del grafo -> (grafo, {tipo: copia con velocidades medidas})


def grafos_medidos(g) -> dict:
    """{tipo: copia de `g` con `travel_time` = segundos medidos / factor del tipo en matriz.py}.

    `matriz._red_del_tipo` multiplica `travel_time` por su factor; al dividir aquí por el mismo
    factor, cada tipo queda con los segundos de `datos_publicos/velocidades.csv`.
    """
    if id(g) not in _GRAFOS_MEDIDOS:
        from despacho import matriz

        tabla = velocidades_medidas()
        copias = {}
        for tipo in TIPOS:
            h = g.copy()
            factor = matriz.FACTOR_TIEMPO[tipo]
            for _, _, d in h.edges(data=True):
                largo = float(d.get("length", 0.0)) or 1.0
                d["travel_time"] = segundos_medidos(tabla, _via(d.get("highway", "")), largo)[tipo] / factor
            copias[tipo] = h
        _GRAFOS_MEDIDOS[id(g)] = (g, copias)
    return _GRAFOS_MEDIDOS[id(g)][1]


class OptimizadorB:
    nombre = "despacho/optimizar.py (OR-Tools, un viaje por vehículo)"
    un_viaje = True

    def __init__(self, limite_s: float = 1.0):
        from datos import db
        from despacho import optimizar, red

        self.mod, self.limite = optimizar, max(1, int(round(limite_s)))
        self.nombre = f"despacho/optimizar.py (OR-Tools, {self.limite} s por llamada, un viaje por vehículo)"
        mio = ruta_cache()
        if mio is None or Path(mio).resolve() != Path(red.RUTA_GRAFO).resolve():
            raise RuntimeError("La simulación y el optimizador deben leer el mismo grafo: "
                               f"{mio} frente a {red.RUTA_GRAFO}")
        self.g = red.cargar()
        self.t0 = datetime(*T0, tzinfo=db.BOGOTA)
        self.fallos, self.vacios, self.llamadas = 0, 0, 0
        self._esc, self._fijos = None, None
        self.velocidades = modo_velocidades()
        self._por_tipo = None
        if self.velocidades == "medidas":
            from despacho import matriz

            self._matriz, self._calcular = matriz, matriz.calcular
            self._por_tipo = grafos_medidos(self.g)
            self.nombre = self.nombre[:-1] + ", velocidades medidas)"

    def _calcular_medido(self, g, lugares, cierres=None, tipos=TIPOS):
        """`matriz.calcular` con la copia del grafo de cada tipo de vehículo."""
        resultado = {}
        for tipo in tipos:
            resultado.update(self._calcular(self._por_tipo.get(tipo, g), lugares, cierres, (tipo,)))
        return resultado

    def matrices(self, lugares, cierres=None, tipos=TIPOS) -> dict:
        """Las matrices que recibe el modelo de B en cada llamada (para las pruebas)."""
        from despacho import matriz

        if self._por_tipo is None:
            return matriz.calcular(self.g, lugares, cierres, tipos)
        return self._calcular_medido(self.g, lugares, cierres, tipos)

    def _iso(self, t: float) -> str:
        return (self.t0 + timedelta(seconds=float(t))).isoformat(timespec="seconds")

    def _datos_fijos(self, esc):
        if self._esc is not esc:
            r = esc.red
            if not r.origen.startswith("OpenStreetMap"):
                raise RuntimeError("El optimizador de B necesita la red de OpenStreetMap, no la malla")
            lugar = lambda nodo: {"lat": float(r.lat[nodo]), "lon": float(r.lon[nodo])}
            self._fijos = {
                "puntos": {q.id: {"id": q.id, "nombre": f"punto {q.id}", "critico": int(q.critico),
                                  **lugar(q.nodo)} for q in esc.puntos},
                "acopios": {1: {"id": 1, "nombre": "acopio", "tiene_frio": 1, **lugar(esc.acopio_nodo)}},
            }
            self._esc = esc
        return self._fijos

    def resolver(self, estado):
        esc, r = estado.esc, estado.esc.red
        fijos = self._datos_fijos(esc)
        ahora = self.t0 + timedelta(seconds=float(estado.t))
        vehiculos, bloqueos, a_bordo = [], {}, []
        for v in estado.vehiculos:
            if v.estado == "fuera":
                continue
            fila = {"id": v.id, "nombre": f"{v.tipo} {v.id}", "tipo": v.tipo, "capacidad_kg": v.cap,
                    "acopio_id": 1, "lat": None, "lon": None, "estado": "libre"}
            if v.estado != "libre":
                nodo, _ = v.ref(estado.t)
                fila.update(estado="en_ruta", lat=float(r.lat[nodo]), lon=float(r.lon[nodo]))
                for pid in v.a_bordo:
                    bloqueos[pid] = v.id
                    a_bordo.append(pid)
            vehiculos.append(fila)

        def fila_pedido(q, estado_ped, productos):
            return {"id": q.id, "creado_en": self._iso(q.creado), "punto_id": q.punto_id,
                    "familias": q.familias, "kg_estimado": q.kg, "productos": json.dumps(productos),
                    "urgencia": q.urgencia, "limite_en": self._iso(q.limite), "estado": estado_ped}

        pedidos = [fila_pedido(q, "confirmado", [{"producto": "abarrotes", "kg": q.kg - q.kg_perecedero},
                                                 {"producto": "perecedero", "kg": q.kg_perecedero}])
                   for q in estado.pendientes]
        lotes = [{"id": LOTE_SECO, "acopio_id": 1, "producto": "abarrotes", "kg": 1e9,
                  "perecedero": 0, "vence_en": None}]
        lotes += [{"id": lid, "acopio_id": 1, "producto": "perecedero", "kg": kg, "perecedero": 1,
                   "vence_en": self._iso(vence)} for lid, kg, vence in estado.inventario]
        for pid in a_bordo:               # lo cargado se surte de su propio lote, con su vencimiento real
            q = estado.pedido(pid)
            nombre = f"cargado{pid:06d}"
            vence = estado.vence_a_bordo.get(pid, float("inf"))
            pedidos.append(fila_pedido(q, "asignado", [{"producto": nombre, "kg": q.kg}]))
            lotes.append({"id": LOTE_A_BORDO + pid, "acopio_id": 1, "producto": nombre, "kg": q.kg,
                          "perecedero": int(vence < float("inf")),
                          "vence_en": self._iso(vence) if vence < float("inf") else None})
        pedidos.sort(key=lambda p: p["id"])

        tipos_de = {}
        for tipo in TIPOS:
            for e in estado.con.cerradas[tipo]:
                tipos_de.setdefault(e, []).append(tipo)
        cierres = [{"id": k + 1, "estado": "confirmado", "osm_u": int(r.osm_id[r.eu[e]]),
                    "osm_v": int(r.osm_id[r.ev[e]]), "tipos_bloqueados": json.dumps(tipos)}
                   for k, (e, tipos) in enumerate(sorted(tipos_de.items()))]

        datos = {**fijos, "pedidos": pedidos, "ya_asignados": [], "lotes": lotes,
                 "vehiculos": vehiculos, "cierres": cierres}
        self.llamadas += 1
        try:
            if self._por_tipo is None:
                resultado = self.mod._resolver(datos, self.g, ahora, self.limite, bloqueos)
            else:
                with mock.patch.object(self._matriz, "calcular", self._calcular_medido):
                    resultado = self.mod._resolver(datos, self.g, ahora, self.limite, bloqueos)
        except Exception:                 # el optimizador real devuelve plan vacío; aquí se cuenta
            self.fallos += 1
            return None
        self.ultimo_resumen = resultado["resumen"]
        if not resultado["paradas"]:
            self.vacios += 1
        rutas = {v["id"]: [] for v in vehiculos}
        for p in sorted(resultado["paradas"], key=lambda p: (p["vehiculo_id"], p["orden"])):
            rutas[p["vehiculo_id"]].append(p["pedido_id"])
        return rutas
