"""Comprueba que la velocidad medida quedó igual en el mundo simulado y en el optimizador.

    DESPACHOX_SIN_RED=1 python -m analisis.sensibilidad.verificar

Escribe `analisis/sensibilidad/verificacion_velocidades.md` con tres cosas:
1. la velocidad media por tipo de vía y vehículo antes y después del parche, contra el CSV;
2. la comparación de las matrices de tiempos de la simulación y del optimizador, como la prueba
   `despacho/sim/tests/test_supuestos.py`, pero con el parche puesto;
3. que los multiplicadores 0,8 y 1,2 no cambian los puntos ni los cierres de una semilla.
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from despacho.sim import red_sim

from . import velocidad_medida as vm

AQUI = Path(__file__).resolve().parent
TIPOS = red_sim.TIPOS
SEMILLAS = (20261150, 20261151, 20261152)


def _num(x, dec=1):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "s. d."
    return f"{x:.{dec}f}".replace(".", ",")


def medias_modelo(ruta) -> tuple:
    """km/h medios por tipo de vía según el `travel_time` del grafo, por el factor de cada vehículo."""
    import networkx as nx
    g = nx.read_graphml(ruta)
    largo, seg = defaultdict(float), defaultdict(float)
    for u, v, d in g.edges(data=True):
        if u == v:
            continue
        via = red_sim._via(d.get("highway", ""))
        largo[via] += float(d.get("length", 0.0))
        seg[via] += float(d["travel_time"])
    return {via: {t: 3.6 * largo[via] / (seg[via] * red_sim.FACTOR_TIEMPO[t]) for t in TIPOS} for via in largo}, largo


def medias_red(r) -> dict:
    """km/h medios por tipo de vía en la `Red` parcheada (solo tramos por los que pasa el vehículo)."""
    out = {}
    via = np.array(r.via)
    for v in sorted(set(r.via)):
        sel = via == v
        out[v] = {}
        for t in TIPOS:
            ok = sel & np.isfinite(r.segundos[t])
            out[v][t] = 3.6 * r.largo_m[ok].sum() / r.segundos[t][ok].sum() if ok.any() else float("nan")
    return out


def comparar_matrices(semilla: int) -> dict:
    """Máxima diferencia en segundos entre `Conocimiento.tiempos` y `matriz.calcular`, por vehículo."""
    from despacho import matriz, red
    from despacho.sim.escenario import generar
    from despacho.sim.red_sim import Conocimiento

    esc = generar(semilla, "auto")
    con = Conocimiento(esc.red, esc.sitios)
    r = esc.red
    lugares = [matriz.Lugar(f"s{i}", float(r.lat[n]), float(r.lon[n])) for i, n in enumerate(esc.sitios)]
    suyas = matriz.calcular(red.cargar(), lugares)
    out = {}
    for tipo in TIPOS:
        mia = con.tiempos(tipo).copy()
        suya = suyas[tipo].segundos.astype(float)
        suya[suya >= matriz.INALCANZABLE] = np.inf
        np.fill_diagonal(mia, 0.0)
        mismos_inf = bool(np.array_equal(np.isinf(mia), np.isinf(suya)))
        ok = np.isfinite(mia) & np.isfinite(suya)
        out[tipo] = (mismos_inf, float(np.abs(mia[ok] - suya[ok]).max()), float(np.median(mia[ok])))
    return out


def huella(semilla: int) -> tuple:
    """Puntos, críticos y cierres de la semilla: deben ser iguales con cualquier multiplicador."""
    from despacho.sim.escenario import generar
    esc = generar(semilla, "auto")
    return (tuple((q.nodo, q.critico) for q in esc.puntos), tuple((c.aristas, c.t_ocurre, c.tipos) for c in esc.cierres),
            len(esc.pedidos), len(esc.vehiculos))


def main() -> None:
    ruta = red_sim.ruta_cache()
    vel = vm.leer_velocidades()
    modelo, km_via = medias_modelo(ruta)
    L = ["# Verificación de la velocidad medida", "",
         "Generado por `python -m analisis.sensibilidad.verificar`. Velocidades en km/h, media por "
         "longitud (largo total entre segundos totales) de los tramos de cada tipo de vía del grafo "
         f"`{Path(ruta).name}`.", "",
         "## 1. Velocidad media por tipo de vía: modelo, CSV y red parcheada (multiplicador 1)", "",
         "| Tipo de vía | km del grafo | Vehículo | Modelo (travel_time × factor) | CSV | Simulación parcheada | Diferencia con el CSV |",
         "|---|---:|---|---:|---:|---:|---:|"]
    r1 = vm.red_medida(ruta, 1.0, vel)
    sim1 = medias_red(r1)
    peor = 0.0
    for via in sorted(km_via, key=lambda v: -km_via[v]):
        for t in TIPOS:
            csv_v = vm.kmh(vel, via, t, 1.0)
            s = sim1.get(via, {}).get(t, float("nan"))
            dif = s - csv_v if math.isfinite(s) else float("nan")
            if math.isfinite(dif) and not (t == "camion" and via in red_sim.VIAS_SIN_CAMION):
                peor = max(peor, abs(dif))
            L.append(f"| {via} | {_num(km_via[via] / 1000)} | {t} | {_num(modelo[via][t])} | {_num(csv_v)} | "
                     f"{_num(s)} | {_num(dif, 2)} |")
    L += ["", f"Mayor diferencia entre la red parcheada y el CSV: {_num(peor, 3)} km/h, sin contar el camión en "
          "`residential`. El camión no puede usar esas vías. Solo pasa por los pares de nodos que tienen, "
          "además del tramo residencial, un tramo paralelo apto de otro tipo, y su media sale de esos tramos.", "",
          "La columna «Modelo» es la velocidad que la simulación usaba antes: el `travel_time` del grafo (el "
          "`maxspeed` de OSM donde existe y, si no, `VELOCIDADES`) dividido por `FACTOR_TIEMPO`.", ""]

    L += ["## 2. Multiplicadores 0,8 y 1,2", "",
          "| Multiplicador | Tipo de vía | Vehículo | CSV × multiplicador | Simulación parcheada |", "|---:|---|---|---:|---:|"]
    for mult in (0.8, 1.2):
        rm = vm.red_medida(ruta, mult, vel)
        sm = medias_red(rm)
        for via in ("primary", "secondary", "tertiary", "residential"):
            for t in TIPOS:
                L.append(f"| {_num(mult)} | {via} | {t} | {_num(vm.kmh(vel, via, t, mult))} | {_num(sm[via][t])} |")
    L.append("")

    L += ["## 3. Simulación frente al optimizador, con el parche puesto", "",
          "Misma comprobación que `test_misma_matriz_de_tiempos_que_el_optimizador`: segundos entre el "
          "acopio y los puntos de una semilla, calculados por `Conocimiento.tiempos` (simulación) y por "
          "`despacho.matriz.calcular` (optimizador). El optimizador redondea a segundos enteros.", "",
          "| Multiplicador | Semilla | Vehículo | Mismos pares sin camino | Máxima diferencia (s) | Mediana del tiempo entre sitios (s) |",
          "|---:|---|---|---|---:|---:|"]
    huellas = {}
    todo_ok = True
    for mult in (1.0, 0.8, 1.2):
        vm.aplicar(mult)
        for s in SEMILLAS:
            for t, (mismos, dif, mediana) in comparar_matrices(s).items():
                todo_ok &= mismos and dif <= 1.0
                L.append(f"| {_num(mult)} | {s} | {t} | {'sí' if mismos else 'no'} | {_num(dif, 2)} | {_num(mediana, 0)} |")
            huellas[(mult, s)] = huella(s)
    L += ["", f"Resultado: {'las dos matrices coinciden en todos los casos' if todo_ok else 'HAY DIFERENCIAS'} "
          "(tolerancia de 1 s).", ""]

    iguales = all(huellas[(m, s)] == huellas[(1.0, s)] for m in (0.8, 1.2) for s in SEMILLAS)
    L += ["## 4. Escenarios con cada multiplicador", "",
          "Escalar todas las velocidades por el mismo número no cambia los caminos más cortos, así que "
          "los puntos, los críticos, los cierres, los pedidos y la flota de cada semilla deben quedar "
          f"iguales. Comprobado en las semillas {', '.join(map(str, SEMILLAS))}: "
          f"{'iguales' if iguales else 'DISTINTOS'}.", ""]
    (AQUI / "verificacion_velocidades.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
