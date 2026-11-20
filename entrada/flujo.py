"""La conversación, sin Telegram: qué se guarda y qué se contesta ante cada mensaje.

`Mesa` recibe texto, botones y ubicaciones, y devuelve `Respuesta` (texto y botones). `bot.py` solo
traduce entre Telegram y esta clase, así el flujo completo se prueba sin red.

Orden ante un mensaje: se limpia, se lee con el modelo, se guarda la fila de inmediato con el lugar
pendiente y se pregunta por la ubicación. El punto del pedido o las coordenadas del cierre solo se
escriben cuando la persona confirma (lugares.confirmar) o envía su ubicación (lugares.corregir_con_pin).
"""
from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from typing import Callable

import lugares
from entrada import guardar
from entrada.extraer import Extraccion, extraer as extraer_con_modelo
from entrada.privacidad import hash_remitente, limpiar

TIPOS = {"pedidos": ("barrio", "punto", "sitio", "vereda"), "cierres": ("via", "sitio")}
NOMBRE_VEHICULO = {"camion": "camión", "campero": "campero", "moto": "moto"}
QUIEN = "remitente"
_USAR_MODELO = object()      # por defecto, el desempate de lugares/ con modelo
_PIN = "pin"                 # nombre del lugar cuando solo hay coordenadas enviadas por chat
_SI = re.compile(r"^(si|sip|correcto|exacto|eso es|asi es|es ahi|ahi es|afirmativo)( es ahi| es| señor| señora| correcto)?$")
_CORTESIA = re.compile(r"^(muchas )?(gracias|ok|okay|vale|listo|bueno|dale|entendido)( gracias| muchas gracias)?$")

AYUDA = ("Soy la mesa de despacho de ayuda alimentaria. Escríbeme con tus palabras:\n"
         "• qué necesitan y dónde: «Somos 40 familias en San José, no hay arroz ni leche»\n"
         "• o qué vía está cerrada: «Derrumbe en la vía a Chinchiná, no pasan camiones»\n"
         "Un despachador revisa cada mensaje. Con /estado ves cómo van tus pedidos.\n"
         "No escribas nombres, cédulas ni teléfonos: no hacen falta.")
NO_ENTENDI = ("No entendí si es un pedido de ayuda o un reporte de vía cerrada. Por ejemplo: «Somos 40 "
              "familias en San José, no hay arroz ni leche» o «Derrumbe en la vía a Chinchiná, no pasan camiones».")
SIN_LEER = ("Recibí tu mensaje y quedó guardado. No pude leerlo automáticamente, así que un despachador "
            "lo revisará.")
COMO_ENVIAR_PIN = ("Toca el botón «Enviar mi ubicación» que aparece abajo, o usa el clip del chat y elige "
                   "Ubicación. También puedes escribirme un barrio o una vía cercana.")


@dataclass
class Respuesta:
    texto: str
    botones: list[tuple[str, str]] = field(default_factory=list)    # (etiqueta, dato del botón)
    pedir_ubicacion: bool = False       # el bot muestra el teclado que comparte la ubicación


@dataclass
class Pendiente:
    """Un reporte de este chat que todavía no tiene lugar confirmado."""
    tabla: str
    fila_id: int
    contexto: str
    ubicacion_id: int | None = None     # None: el mensaje no decía dónde


class Mesa:
    def __init__(self, con: sqlite3.Connection, extraer: Callable[[str], Extraccion] = extraer_con_modelo,
                 elegir=_USAR_MODELO):
        self.con = con
        self.extraer = extraer
        self.elegir = lugares.nomenclator.elegir_con_modelo if elegir is _USAR_MODELO else elegir
        self.pendientes: dict[str, list[Pendiente]] = {}
        lugares.cargar_semilla(con)

    # ---------- mensajes de texto ----------

    def leer(self, texto: str) -> Extraccion:
        """Limpia y extrae. Es el único paso lento (llama al modelo); no toca la base."""
        return self.extraer(limpiar(texto))

    def recibir_texto(self, chat_id, texto: str) -> list[Respuesta]:
        return self.atender(chat_id, self.leer(texto))

    def atender(self, chat_id, x: Extraccion) -> list[Respuesta]:
        rem = hash_remitente(chat_id)
        cola = self.pendientes.get(rem) or []
        if cola and (x.tipo == "otro" or _solo_lugar(x)):
            dicho = lugares.normalizar(x.texto)
            if _SI.match(dicho):                                # «sí» escrito vale como el botón
                u = self.con.execute("SELECT lugar_id FROM ubicaciones WHERE id=?",
                                     (cola[0].ubicacion_id or 0,)).fetchone()
                if u is not None and u["lugar_id"] is not None:
                    return [self.pulsar(chat_id, f"s:{cola[0].ubicacion_id}")]
                return [Respuesta("¿Cuál es? Toca una de las opciones del mensaje anterior, escríbeme el "
                                  "barrio o la vía, o envíame la ubicación.")]
            if _CORTESIA.match(dicho):
                return [Respuesta("Con gusto. Tu reporte sigue sin lugar confirmado: usa los botones del "
                                  "mensaje anterior o envíame la ubicación.")]
            r = self._reubicar(rem, cola[0], _lugar_de(x) or x.texto, exigir_candidato=x.fallo)
            if r is not None:
                return [r]
        if x.fallo:
            guardar.guardar_crudo(self.con, x.texto, rem)
            return [Respuesta(SIN_LEER)]
        if x.tipo == "otro":
            return [Respuesta(NO_ENTENDI)]
        respuestas = []
        if x.pedido is not None:
            fila = guardar.guardar_pedido(self.con, x.pedido, x.texto, rem)
            respuestas.append(self._preguntar(rem, "pedidos", fila, x.pedido.lugar, x, _resumen_pedido(x)))
        if x.cierre is not None:
            fila = guardar.guardar_cierre(self.con, x.cierre, x.texto)
            respuestas.append(self._preguntar(rem, "cierres", fila, x.cierre.lugar, x, _resumen_cierre(x)))
        return respuestas

    def _preguntar(self, rem: str, tabla: str, fila: int, lugar: str | None, x: Extraccion,
                   resumen: str) -> Respuesta:
        p = Pendiente(tabla, fila, x.texto)
        self.pendientes.setdefault(rem, []).append(p)
        cabeza = f"{resumen} Queda en revisión del despachador."
        dudas = [d for d in x.dudas if d.strip()][:2]
        if dudas:
            cabeza += "\nMe falta saber: " + " ".join(dudas)
        if not lugar:
            que = "se necesita la ayuda" if tabla == "pedidos" else "está el cierre"
            return Respuesta(f"{cabeza}\n\nNo me dijiste dónde {que}. Escríbeme el barrio o la vía, "
                             "o envíame la ubicación.", [("Enviar mi ubicación", "p:0")])
        r = self._resolver(p, lugar)
        return Respuesta(f"{cabeza}\n\n{r.pregunta}", _botones(r))

    def _resolver(self, p: Pendiente, lugar: str, con_modelo: bool = True):
        r = lugares.resolver(self.con, lugar, tabla=p.tabla, fila_id=p.fila_id, contexto=p.contexto,
                             tipos=TIPOS[p.tabla], elegir=self.elegir if con_modelo else None)
        p.ubicacion_id = r.ubicacion_id
        return r

    def _reubicar(self, rem: str, p: Pendiente, texto: str, exigir_candidato: bool = False) -> Respuesta | None:
        """La persona contestó con texto libre («no, es más abajo, por la terminal»): se vuelve a
        resolver con ese texto y la propuesta anterior queda rechazada."""
        lugar = re.sub(r"^\s*(?:no+|nop|nel|negativo)\b[\s,.;:]*", "", texto, flags=re.I).strip()
        lugar = re.sub(r"^(?:(?:es|queda|era|sino|mas bien|más bien|en)\b\s*)+", "", lugar, flags=re.I).strip()
        if not lugar:
            return Respuesta("Entonces, ¿dónde es? Escríbeme un barrio o una vía cercana, o envíame la "
                             "ubicación.", [("Enviar mi ubicación", f"p:{p.ubicacion_id or 0}")])
        if exigir_candidato and not lugares.nomenclator.buscar(self.con, lugar, TIPOS[p.tabla]):
            return None         # no se pudo leer y no suena a lugar: se guarda como mensaje aparte
        self._rechazar(p.ubicacion_id)
        r = self._resolver(p, lugar)
        return Respuesta(r.pregunta, _botones(r))

    def _rechazar(self, ubicacion_id: int | None) -> None:
        if ubicacion_id:
            self.con.execute("UPDATE ubicaciones SET estado='rechazada', confirmado_por=?, confirmado_en=? "
                             "WHERE id=? AND estado='propuesta'", (QUIEN, lugares.nomenclator.db.ahora(), ubicacion_id))
            self.con.commit()

    # ---------- botones ----------

    def pulsar(self, chat_id, dato: str) -> Respuesta:
        """Datos de botón: `s:<ubicacion>` sí; `c:<ubicacion>:<lugar>` otra opción; `p:<ubicacion>` pin."""
        rem = hash_remitente(chat_id)
        partes = (dato or "").split(":")
        try:
            accion, uid = partes[0], int(partes[1])
            lugar_id = int(partes[2]) if accion == "c" else None
        except (IndexError, ValueError):
            return Respuesta("No reconocí ese botón. Escríbeme de nuevo, por favor.")
        if accion == "p":
            return Respuesta(COMO_ENVIAR_PIN, pedir_ubicacion=True)
        u = self.con.execute("SELECT * FROM ubicaciones WHERE id=?", (uid,)).fetchone()
        if u is None or accion not in ("s", "c") or (accion == "s" and u["lugar_id"] is None):
            return Respuesta("No encontré ese reporte. Escríbeme de nuevo, por favor.")
        if u["estado"] != "propuesta":
            return Respuesta("Ese lugar ya quedó resuelto. Si hay algo nuevo, escríbeme otro mensaje.")
        if accion == "c" and lugar_id not in {c["lugar_id"] for c in json.loads(u["candidatos"] or "[]")}:
            return Respuesta("Esa opción ya no está disponible. Escríbeme el lugar de nuevo.")
        if not lugares.confirmar(self.con, uid, quien=QUIEN, lugar_id=lugar_id):
            return Respuesta("No pude confirmar ese lugar. Envíame la ubicación o escríbeme un barrio cercano.",
                             [("Enviar mi ubicación", f"p:{uid}")])
        return Respuesta(self._cerrar(rem, u["tabla"], u["fila_id"], uid))

    # ---------- ubicación de Telegram ----------

    def recibir_ubicacion(self, chat_id, lat: float, lon: float) -> Respuesta:
        rem = hash_remitente(chat_id)
        cola = self.pendientes.get(rem) or []
        if not cola:
            return Respuesta("Gracias. No tengo un reporte tuyo pendiente de ubicar: escríbeme primero qué "
                             "necesitan o qué vía está cerrada.")
        p = cola[0]
        nombre = None
        if p.ubicacion_id is None:      # el mensaje no traía lugar: se crea la propuesta para poder fijarla
            nombre = f"{_PIN} {lat:.4f}, {lon:.4f}"
            self._resolver(p, nombre, con_modelo=False)
        lugares.corregir_con_pin(self.con, p.ubicacion_id, lat, lon, quien=QUIEN, nombre=nombre)
        return Respuesta(self._cerrar(rem, p.tabla, p.fila_id, p.ubicacion_id))

    def _cerrar(self, rem: str, tabla: str, fila_id: int, ubicacion_id: int) -> str:
        """Texto de cierre tras confirmar, y lo que sigue pendiente de ese chat."""
        cola = [p for p in self.pendientes.get(rem, []) if (p.tabla, p.fila_id) != (tabla, fila_id)]
        self.pendientes[rem] = cola
        u = self.con.execute("SELECT u.lat, u.lon, l.nombre FROM ubicaciones u LEFT JOIN lugares l "
                             "ON l.id = u.lugar_id WHERE u.id=?", (ubicacion_id,)).fetchone()
        donde = u["nombre"] if u and u["nombre"] and not u["nombre"].startswith(_PIN) \
            else "la ubicación que enviaste"
        if tabla == "pedidos":
            texto = f"Listo, el pedido #{fila_id} quedó ubicado en {donde}. El despachador lo revisa y lo programa."
            previo = guardar.marcar_duplicado(self.con, fila_id)
            if previo:
                texto += (f" Ya había un pedido reciente de ese punto (#{previo}); el despachador decide si "
                          "es el mismo.")
        else:
            texto = (f"Listo, el cierre quedó ubicado en {donde}. El despachador lo confirma antes de "
                     "cambiar las rutas.")
        if cola:
            texto += " Falta ubicar tu otro reporte: usa los botones del mensaje anterior."
        return texto

    # ---------- /estado ----------

    def estado(self, chat_id) -> Respuesta:
        filas = guardar.pedidos_de(self.con, hash_remitente(chat_id))
        if not filas:
            return Respuesta("No tengo pedidos tuyos todavía.")
        nombres = {"nuevo": "en revisión", "confirmado": "confirmado, esperando ruta", "asignado": "asignado a un vehículo",
                   "entregado": "entregado", "descartado": "descartado"}
        lineas = []
        for f in filas:
            donde = f["punto"] or "sin lugar confirmado"
            extra = f" (posible repetido del #{f['duplicado_de']})" if f["duplicado_de"] else ""
            lineas.append(f"#{f['id']} · {f['creado_en'][11:16]} · {donde} · {nombres.get(f['estado'], f['estado'])}{extra}")
        return Respuesta("Tus últimos pedidos:\n" + "\n".join(lineas))


def _solo_lugar(x: Extraccion) -> bool:
    """El modelo vio un pedido o un cierre que solo trae un lugar: es la respuesta a «¿dónde es?»."""
    if x.pedido is not None and x.cierre is None:
        return bool(x.pedido.lugar) and x.pedido.familias is None and not x.pedido.productos
    return False


def _lugar_de(x: Extraccion) -> str | None:
    return x.pedido.lugar if _solo_lugar(x) else None


def _resumen_pedido(x: Extraccion) -> str:
    p = x.pedido
    partes = []
    if p.familias:
        partes.append(f"{p.familias} familias")
    if p.lugar:
        partes.append(f"en {p.lugar}")
    cabeza = " ".join(partes) or "un pedido de ayuda"
    productos = [f"{q.producto} ({q.kg:g} kg)" if q.kg else q.producto for q in p.productos]
    if productos:
        cabeza += ", " + _lista(productos)
    if p.urgencia == 3:
        cabeza += ", urgente"
    if p.horas_limite:
        cabeza += f", plazo de {p.horas_limite:g} horas"
    return f"Entendí: {cabeza}."


def _resumen_cierre(x: Extraccion) -> str:
    c = x.cierre
    donde = f" en {c.lugar}" if c.lugar else ""
    todos = set(c.tipos_bloqueados) == set(NOMBRE_VEHICULO)
    paso = "no pasa ningún vehículo" if todos else "no pasa " + _lista([NOMBRE_VEHICULO[t] for t in c.tipos_bloqueados])
    return f"Entendí: vía cerrada{donde}, {c.descripcion.rstrip('.')}; {paso}."


def _lista(cosas: list[str]) -> str:
    return cosas[0] if len(cosas) == 1 else ", ".join(cosas[:-1]) + " y " + cosas[-1]


def _botones(r) -> list[tuple[str, str]]:
    """Sí (si hay propuesta), un botón por cada alternativa y «Enviar mi ubicación»."""
    uid = r.ubicacion_id
    botones = []
    if r.elegido is not None:
        botones.append(("Sí, es ahí", f"s:{uid}"))
    for c in r.candidatos:
        if r.elegido is None or c.lugar_id != r.elegido.lugar_id:
            botones.append((f"{c.nombre} ({c.tipo})"[:40], f"c:{uid}:{c.lugar_id}"))
    botones.append(("Enviar mi ubicación", f"p:{uid}"))
    return botones
