# Encargo A3 · Pedidos por SMS (Samuel)

Empieza cuando termines la etapa 1 de `encargos/A2_BOT_SAMUEL.md`. Sigue en la rama `samuel-bot`. Plan Pro: no leas lo que no haga falta.

---

Soy Samuel, dueño de `entrada/`. Después de un sismo los datos móviles colapsan primero; los SMS suelen aguantar más. Quiero que DespachoX reciba pedidos, cierres y confirmaciones de entrega por SMS, sin internet y sin modelo de lenguaje.

Lee: `docs/SIN_CONEXION.md` (formato de SMS y escalera de degradación), `entrada/flujo.py` y `entrada/guardar.py`.

## 1. Lector por reglas (lo principal; antes del congelamiento)

`entrada/sms.py`, función `leer_sms(texto) -> Extraccion` que devuelve el mismo objeto que el extractor con modelo, para reutilizar todo lo demás.

- Formato de `docs/SIN_CONEXION.md`: `PEDIDO 40 SAN JOSE ARROZ LECHE`, `PEDIDO 6 BEBES LA ENEA LECHE URGENTE`, `CIERRE AV DEL CENTRO CAMION`, `ENTREGADO DX7K2Q`.
- Tolerante: minúsculas, sin tildes, orden variable, palabras de relleno, errores de tipeo en las palabras clave (`PEDIDOS`, `PEDDO`, `CIERE`).
- Productos con una lista conocida (la de la tabla de raciones). Lo que no es número, producto ni palabra clave se trata como lugar y se resuelve con `lugares.resolver(..., elegir=None)`, sin modelo.
- `ENTREGADO CODIGO` llama a la función de entrega de `despacho/` (pregúntale a Carlos por el canal el nombre exacto).
- Lo que no se entiende se guarda como pedido `nuevo` con el texto, nunca se descarta.
- La respuesta al remitente es un SMS corto, de menos de 160 caracteres: «Recibido: 40 fam San José, arroz leche. Responda SI o el barrio correcto.»
- Úsalo también en el bot cuando el modelo falla o con `DESPACHOX_SIN_RED=1`.
- Pruebas: veinte SMS con errores y su resultado esperado; reporta cuántos se leen bien.

## 2. Entrada por SMS (si alcanza; si no, al plan de 30 días)

Busca y compara, con enlaces oficiales y sin inventar precios:
- una aplicación Android de código abierto que convierte un celular en pasarela SMS y reenvía cada mensaje a una dirección en la red local (funciona sin internet: celular y portátil en el mismo wifi del acopio);
- un proveedor de SMS en la nube con números de Colombia, para cuando sí hay internet en el acopio.

Implementa un receptor mínimo en `entrada/pasarela_sms.py`: una ruta HTTP que recibe el SMS de la pasarela, lo pasa por `leer_sms` y por el mismo flujo, y devuelve la respuesta para que la pasarela la envíe. Pruébalo con un `curl` que simule a la pasarela. Si hay un celular Android disponible, pruébalo de verdad y graba un video corto.

Escribe `entrada/SMS.md`: cómo se monta en un acopio sin internet, qué se compró o instaló, cuánto cuesta y qué falta.

## Reglas

- No toques `despacho/`, `lugares/`, `tablero/` ni `datos/esquema.sql`. Lo que necesites, pídelo por el canal.
- Ningún número de teléfono real en el repositorio ni en las pruebas. El número del remitente se guarda como hash, igual que el chat de Telegram.
- Al cerrar cada parte: torre al día, LISTO en el canal, push a `samuel-bot` y aviso a Carlos.

**Aporta a:** criterio 5 (riesgo de conectividad), criterio 2 (demo sin internet) y la pregunta del jurado «¿y si no hay datos?».
