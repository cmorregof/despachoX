"""La conversación, sin Telegram: qué se guarda y qué se contesta ante cada mensaje.

`Mesa` recibe texto, botones y ubicaciones, y devuelve `Respuesta` (texto y botones). `bot.py` solo
traduce entre Telegram y esta clase, así el flujo completo se prueba sin red.

Orden ante un mensaje: se limpia, se lee con el modelo, se guarda la fila de inmediato con el lugar
pendiente y se pregunta por la ubicación. El punto del pedido o las coordenadas del cierre solo se
escriben cuando la persona confirma (lugares.confirmar) o envía su ubicación (lugares.corregir_con_pin).
"""
from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from dataclasses import dataclass, field
from typing import Callable

import lugares
from datos import db
from entrada import guardar, raciones, silencio
from entrada.extraer import Extraccion, Producto, extraer as extraer_con_modelo
from entrada.privacidad import hash_remitente, limpiar

log = logging.getLogger("entrada.flujo")
TIPOS = {"pedidos": ("barrio", "punto", "sitio", "vereda"), "cierres": ("via", "sitio")}
NOMBRE_VEHICULO = {"camion": "camión", "campero": "campero", "moto": "moto"}
QUIEN = "remitente"
_USAR_MODELO = object()      # por defecto, el desempate de lugares/ con modelo
_PIN = "pin"                 # nombre del lugar cuando solo hay coordenadas enviadas por chat
_SI = re.compile(r"^(si|sip|correcto|exacto|eso es|asi es|es ahi|ahi es|afirmativo)( es ahi| es| señor| señora| correcto)?$")
_NUMERO = re.compile(r"^(?:son|somos|como|unas|unos|para|de|aprox\w*|mas o menos|\s)*(\d{1,4})"
                     r"\s*(?:familias?|flias?|hogares)?\s*$")
ESPERA_FAMILIAS_S = 120     # tras dos minutos sin respuesta el pedido se queda con lo que hay
# «ENTREGADO DX-7KQ3», o el código solo: lo lee la regla, porque el esquema del modelo no tiene dónde
# poner un código de paquete y con el modelo activo la entrega no quedaba registrada (revisión QA).
_PARECE_ENTREGA = re.compile(r"\bdx\W?[a-z0-9]{4,6}\b|^\W*entreg", re.I)
_CORTESIA = re.compile(r"^(muchas )?(gracias|ok|okay|vale|listo|bueno|dale|entendido)( gracias| muchas gracias)?$")

EJEMPLOS = ("Somos 40 familias en San José, no hay arroz ni leche",
            "Derrumbe en la vía a Chinchiná, no pasan camiones")


def ayuda(con_voz: bool = False) -> str:
    """Primer mensaje: tres líneas y dos ejemplos. Va en HTML: en Telegram, tocar un <code> lo copia."""
    como = "Escríbeme o mándame una nota de voz" if con_voz else "Escríbeme"
    return ("Hola. Aquí se pide comida para tu barrio o se avisa de una vía cerrada.\n"
            f"{como} con lo que necesitan, para cuántas familias y dónde.\n"
            "Una persona de la mesa revisa cada mensaje. Con /estado ves cómo va tu pedido.\n\n"
            "Toca un ejemplo para copiarlo:\n" + "\n".join(f"<code>{e}</code>" for e in EJEMPLOS) +
            "\n\nNo escribas nombres, cédulas ni teléfonos: no hacen falta.")


AYUDA = ayuda()
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
    preguntar_familias: bool = False    # el mensaje no dijo cuántas familias: se pregunta al ubicar
    familias_estimadas: int | None = None


class Mesa:
    def __init__(self, con: sqlite3.Connection, extraer: Callable[[str], Extraccion] = extraer_con_modelo,
                 elegir=_USAR_MODELO, reloj: Callable[[], float] = time.monotonic, respaldo_reglas: bool = True):
        self.con = con
        self.respaldo_reglas = respaldo_reglas      # si el modelo falla, intentar con el lector de SMS
        self.reloj = reloj
        self.por_familias: dict[str, tuple[int, float]] = {}    # remitente -> (pedido, vence)
        self.extraer = extraer
        self.elegir = lugares.nomenclator.elegir_con_modelo if elegir is _USAR_MODELO else elegir
        self.pendientes: dict[str, list[Pendiente]] = {}
        lugares.cargar_semilla(con)

    # ---------- mensajes de texto ----------

    def leer(self, texto: str) -> Extraccion:
        """Limpia y extrae. Es el único paso lento (llama al modelo); no toca la base.

        Sin red (`DESPACHOX_SIN_RED=1`) no se llama al modelo: lee el lector de SMS por reglas. Si el
        modelo falla, también se intenta con las reglas antes de guardar el texto crudo."""
        from entrada.sms import leer_sms
        limpio = limpiar(texto)
        if os.environ.get("DESPACHOX_SIN_RED") == "1":
            return leer_sms(limpio)
        if _PARECE_ENTREGA.search(limpio):
            por_reglas = leer_sms(limpio)
            if por_reglas.entregado:
                return por_reglas
        x = self.extraer(limpio)
        if x.fallo and self.respaldo_reglas:
            por_reglas = leer_sms(limpio)
            if not por_reglas.fallo:
                return por_reglas
        return x

    def recibir_texto(self, chat_id, texto: str) -> list[Respuesta]:
        return self.atender(chat_id, self.leer(texto))

    def atender_seguro(self, chat_id, x: Extraccion) -> list[Respuesta]:
        """`atender`, pero si algo falla al guardar o ubicar (base ocupada, error inesperado) el
        mensaje no se pierde: se deshace lo a medias y se guarda como texto crudo para el despachador."""
        try:
            return self.atender(chat_id, x)
        except Exception as e:
            log.error("falló al atender un mensaje (%s); se guarda crudo", type(e).__name__)
            self.con.rollback()
            guardar.guardar_crudo(self.con, x.texto, hash_remitente(chat_id))
            return [Respuesta(SIN_LEER)]

    def atender(self, chat_id, x: Extraccion) -> list[Respuesta]:
        rem = hash_remitente(chat_id)
        if x.entregado:
            return [self._entregar(rem, x.entregado)]
        n = self._familias_respondidas(rem, x)
        if n is not None:
            return [self._fijar_familias(rem, self.por_familias.pop(rem)[0], n, f"{n}")]
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
            dicho = x.pedido.familias is not None
            lineas, dudas, estimadas = _completar(x)
            fila = guardar.guardar_pedido(self.con, x.pedido, x.texto, rem, lineas, dudas)
            r = self._preguntar(rem, "pedidos", fila, x.pedido.lugar, x, _resumen_pedido(x, lineas, estimadas),
                                notas=[d for d in dudas if d.startswith("Familias")])
            self.pendientes[rem][-1].preguntar_familias = not dicho
            self.pendientes[rem][-1].familias_estimadas = x.pedido.familias if estimadas else None
            respuestas.append(r)
        if x.cierre is not None:
            fila = guardar.guardar_cierre(self.con, x.cierre, x.texto)
            respuestas.append(self._preguntar(rem, "cierres", fila, x.cierre.lugar, x, _resumen_cierre(x)))
        return respuestas

    def _preguntar(self, rem: str, tabla: str, fila: int, lugar: str | None, x: Extraccion,
                   resumen: str, notas: list[str] | None = None) -> Respuesta:
        p = Pendiente(tabla, fila, x.texto)
        self.pendientes.setdefault(rem, []).append(p)
        cabeza = f"{resumen} Queda en revisión del despachador."
        if notas:
            cabeza += "\n" + " ".join(notas)
        dudas = [d for d in x.dudas if d.strip() and not d.startswith("Leído por reglas")][:2]   # nota interna
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
        if accion == "f":                   # f:<pedido>:<familias>; vale aunque hayan pasado los dos minutos
            try:
                n = int(partes[2])
            except (IndexError, ValueError):
                return Respuesta("No reconocí ese botón. Escríbeme de nuevo, por favor.")
            if not 0 < n <= 2000:           # el mismo tope que un número escrito
                return Respuesta("No reconocí ese botón. Escríbeme de nuevo, por favor.")
            dueno = self.con.execute("SELECT remitente_hash FROM pedidos WHERE id=?", (uid,)).fetchone()
            if dueno is None or dueno["remitente_hash"] != rem:     # botón forjado desde otro chat
                return Respuesta("No encontré ese reporte. Escríbeme de nuevo, por favor.")
            self.por_familias.pop(rem, None)
            etiqueta = next((e for e, v in raciones.RANGOS if v == n), str(n))
            return self._fijar_familias(rem, uid, n, etiqueta)
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
        return self._cerrar(rem, u["tabla"], u["fila_id"], uid)

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
        return self._cerrar(rem, p.tabla, p.fila_id, p.ubicacion_id)

    def _cerrar(self, rem: str, tabla: str, fila_id: int, ubicacion_id: int) -> Respuesta:
        """Texto de cierre tras confirmar, lo que sigue pendiente de ese chat y, si el pedido no
        dijo cuántas familias, la única pregunta que falta."""
        este = next((p for p in self.pendientes.get(rem, []) if (p.tabla, p.fila_id) == (tabla, fila_id)), None)
        cola = [p for p in self.pendientes.get(rem, []) if (p.tabla, p.fila_id) != (tabla, fila_id)]
        self.pendientes[rem] = cola
        u = self.con.execute("SELECT u.lat, u.lon, l.nombre FROM ubicaciones u LEFT JOIN lugares l "
                             "ON l.id = u.lugar_id WHERE u.id=?", (ubicacion_id,)).fetchone()
        donde = u["nombre"] if u and u["nombre"] and not u["nombre"].startswith(_PIN) \
            else "la ubicación que enviaste"
        if tabla == "pedidos":
            texto = f"Listo, el pedido #{fila_id} quedó ubicado en {donde}. El despachador lo revisa y lo programa."
            previo = guardar.marcar_duplicado(self.con, fila_id)
            punto = self.con.execute("SELECT punto_id FROM pedidos WHERE id=?", (fila_id,)).fetchone()
            silencio.apagar(self.con, punto["punto_id"] if punto else None)     # el punto ya habló
            if previo:
                texto += (f" Ya había un pedido reciente de ese punto (#{previo}); el despachador decide si "
                          "es el mismo.")
        else:
            texto = (f"Listo, el cierre quedó ubicado en {donde}. El despachador lo confirma antes de "
                     "cambiar las rutas.")
        if cola:
            texto += " Falta ubicar tu otro reporte: usa los botones del mensaje anterior."
        if este is not None and este.preguntar_familias:
            self.por_familias[rem] = (fila_id, self.reloj() + ESPERA_FAMILIAS_S)
            est = este.familias_estimadas
            botones = [(f"Sí, unas {est}", f"f:{fila_id}:{est}")] if est else []
            botones += [(e, f"f:{fila_id}:{v}") for e, v in raciones.RANGOS]
            pregunta = f"¿Para cuántas familias es? Calculé unas {est}." if est else "¿Para cuántas familias es?"
            return Respuesta(f"{texto}\n\n{pregunta} Toca una opción o escribe el número.", botones)
        return Respuesta(texto)

    # ---------- ENTREGADO DX-7KQ3 ----------

    def _entregar(self, rem: str, codigo: str) -> Respuesta:
        """Confirmación de entrega por chat o SMS. Solo vale si la manda el destino (quien pidió para
        ese punto) o el conductor asignado. La marca la hace despacho/, que la anota en la bitácora
        con un código del remitente (nunca su número). Un código inexistente y uno que este remitente
        no puede confirmar reciben la misma respuesta, para que nadie pueda probar códigos a ciegas."""
        from despacho.paquetes import entregar, normalizar_codigo
        codigo = normalizar_codigo(codigo)
        quien = f"remitente {rem[:8]}"
        como = guardar.quien_confirma(self.con, codigo, rem)
        if como and entregar(self.con, codigo, quien=f"{quien} ({como})"):
            return Respuesta(f"Gracias. El paquete {codigo} quedó entregado.")
        db.anotar(self.con, quien, "entrega rechazada",
                                      f"{codigo}: {'paquete no vivo' if como else 'no es el destino ni el conductor, o no existe'}")
        return Respuesta(f"No pude confirmar el paquete {codigo}. Revisa el código. Solo lo puede confirmar "
                         "quien pidió para ese punto o el conductor que lo lleva, desde su propio chat o número.")

    # ---------- ¿para cuántas familias? ----------

    def _familias_respondidas(self, rem: str, x: Extraccion) -> int | None:
        """Si este chat tiene la pregunta abierta y el mensaje es un número, ese número."""
        abierta = self.por_familias.get(rem)
        if abierta is None:
            return None
        if self.reloj() > abierta[1]:           # pasaron los dos minutos: queda con lo que había
            del self.por_familias[rem]
            return None
        m = _NUMERO.match(lugares.normalizar(x.texto))
        if m and 0 < int(m.group(1)) <= 2000:
            return int(m.group(1))
        p = x.pedido
        if p is not None and p.familias and not p.lugar and not p.productos and x.cierre is None:
            return p.familias
        return None

    def _fijar_familias(self, rem: str, pedido_id: int, n: int, como: str) -> Respuesta:
        nota = f"Familias dichas por el remitente al preguntarle: {como} (se guardó {n})."
        if not guardar.actualizar_familias(self.con, pedido_id, n, nota):
            return Respuesta("Ese pedido ya está en un plan. Si cambió algo, escríbeme un mensaje nuevo.")
        return Respuesta(f"Gracias. El pedido #{pedido_id} quedó para {n} familias. El despachador lo "
                         "revisa y lo programa.")

    # ---------- /estado ----------

    def estado(self, chat_id) -> Respuesta:
        filas = guardar.pedidos_de(self.con, hash_remitente(chat_id))
        if not filas:
            return Respuesta("No tengo pedidos tuyos todavía. Escríbeme qué necesitan y dónde.")
        lineas = []
        for f in filas:
            donde = f"en {f['punto']}" if f["punto"] else "sin lugar confirmado"
            lineas.append(f"• Pedido #{f['id']}, de las {_hora(f['creado_en'])}, {donde}: {_estado_humano(f)}")
        return Respuesta("Así van tus pedidos:\n" + "\n".join(lineas))


def _hora(iso: str | None) -> str:
    """«2026-11-20T16:30:00-05:00» -> «4:30 p. m.»"""
    try:
        h, m = int(iso[11:13]), iso[14:16]
    except (TypeError, ValueError, IndexError):
        return "hora sin dato"
    return f"{h % 12 or 12}:{m} {'a. m.' if h < 12 else 'p. m.'}"


def _estado_humano(f) -> str:
    """Los estados de la base dichos como los entiende quien pidió: recibido, en revisión, va en
    camino, entregado."""
    e = f["estado"]
    if e == "nuevo":
        texto = "recibido. Falta que confirmes el lugar" if not f["punto"] else \
            "recibido. Una persona de la mesa lo está revisando"
    elif e == "confirmado":
        texto = "en revisión. Ya lo aceptaron y le están buscando vehículo"
    elif e == "asignado":
        texto = "va en camino" + (f", llegada estimada {_hora(f['llegada'])}" if f["llegada"] else "")
    elif e == "entregado":
        texto = "entregado"
    elif e == "descartado":
        texto = "no se va a despachar. Si todavía lo necesitan, escríbeme de nuevo"
    else:
        texto = e
    if f["duplicado_de"] and e in ("nuevo", "confirmado"):
        texto += f" (parece el mismo pedido #{f['duplicado_de']}; la mesa lo junta si es así)"
    return texto


def _solo_lugar(x: Extraccion) -> bool:
    """El modelo vio un pedido o un cierre que solo trae un lugar: es la respuesta a «¿dónde es?»."""
    if x.pedido is not None and x.cierre is None:
        return bool(x.pedido.lugar) and x.pedido.familias is None and not x.pedido.productos
    return False


def _lugar_de(x: Extraccion) -> str | None:
    return x.pedido.lugar if _solo_lugar(x) else None


def _completar(x: Extraccion) -> tuple[list[dict], list[str], bool]:
    """Aplica las reglas de `raciones` a lo que leyó el modelo: conserva productos para bebés,
    estima familias desde personas o bebés y pone kilos por ración. Devuelve las líneas de
    productos, las dudas que quedan anotadas y si las familias son estimadas."""
    p = x.pedido
    dudas = [d for d in x.dudas if d.strip()]
    for faltante in raciones.faltantes_para_bebes(x.texto, [q.producto for q in p.productos]):
        p.productos.append(Producto(producto=faltante, kg=None))
        dudas.append(f"Se añadió {faltante}: el mensaje lo nombra y es para bebés.")
    estimadas = False
    if p.familias is None:
        personas, bebes = (p.personas, p.bebes) if (p.personas or p.bebes) else raciones.contar_en_texto(x.texto)
        fam, nota = raciones.familias_desde(personas, bebes)
        if fam:
            p.familias, estimadas = fam, True
            dudas.append(nota)
        else:
            dudas.append("Falta el número de familias: se preguntó al remitente.")
    lineas = [{"producto": raciones.canonico(q.producto), "kg": q.kg} for q in p.productos]
    dudas += raciones.completar_kilos(lineas, p.familias)
    return lineas, dudas, estimadas


def _resumen_pedido(x: Extraccion, lineas: list[dict] | None = None, estimadas: bool = False) -> str:
    p = x.pedido
    partes = []
    if p.familias:
        partes.append(f"{'unas ' if estimadas else ''}{p.familias} familias")
    if p.lugar:
        partes.append(f"en {p.lugar}")
    cabeza = " ".join(partes) or "un pedido de ayuda"
    lineas = lineas if lineas is not None else [q.model_dump() for q in p.productos]
    productos = [f"{q['producto']} ({q['kg']:g} kg{' aprox.' if q.get('supuesto') else ''})" if q.get("kg")
                 else q["producto"] for q in lineas]
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
