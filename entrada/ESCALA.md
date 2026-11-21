# ¿Cuántos mensajes aguanta el bot?

Medición del 20 de noviembre de 2026, rama `samuel-bot`. Para el componente 5 de la ficha (viabilidad).

**Qué es medido, qué es supuesto.** Los tiempos, el ritmo y los mensajes perdidos son **medidos por nosotros** con `entrada/carga.py` en un portátil Windows, sobre una base temporal. Los mensajes son los quince sintéticos de `entrada/pruebas/mensajes.py`. El modelo se reemplazó por un extractor falso que tarda en promedio 1,8 s, lo que tardó el modelo real a las 15:00 (`entrada/pruebas/reporte_campos.md`, una corrida). El costo es **estimado**: la corrida con el modelo real (100 mensajes) no se hizo porque en este equipo no hay clave de Anthropic.

## Resultado

| Escenario | Mensajes | Ritmo | Respuesta media | p95 | Máximo | Errores | Perdidos |
|---|---:|---:|---:|---:|---:|---:|---:|
| Todos a la vez, API sana | 5.000 | 914 por minuto | 2,8 s | 6,5 s | 19,2 s | 0 | 0 de 5.000 |
| Todos a la vez, 5 % de lecturas fallidas | 1.000 | 934 por minuto | 2,6 s | 6,2 s | 12,2 s | 0 | 0 de 1.002 filas |

En la segunda corrida, 59 lecturas fallaron (el 5 % simulado), y las 59 quedaron guardadas como texto crudo para que las revise el despachador. Concurrencia: 50 mensajes a la vez.

Para repetirlo:

```bash
python -m entrada.carga --n 5000 --concurrencia 50 --latencia 1.8
python -m entrada.carga --n 1000 --concurrencia 50 --latencia 1.8 --fallos 0.05
python -m entrada.carga --n 100 --concurrencia 10 --extractor real     # pendiente: necesita ANTHROPIC_API_KEY
```

## Qué aguanta hoy

- **El pico del encargo, 500 mensajes en 10 minutos (50 por minuto), con margen de unas 18 veces.** El techo medido es de unos 900 mensajes por minuto, y la prueba fue más dura que ese pico: los 5.000 mensajes llegaron a la vez, no repartidos.
- **10.000 mensajes al día son unos 7 por minuto**, muy por debajo del techo.
- **Ningún mensaje se pierde.** Si la API falla, el SDK de Anthropic reintenta dos veces con espera creciente ante 429, errores 5xx (529 es sobrecarga) y fallas de red, y respeta `retry-after`. Si los tres intentos fallan, el mensaje se guarda crudo. Si falla la base (por ejemplo, bloqueada), se deshace lo que quedó a medias y también se guarda crudo. Las dos cosas tienen prueba en `entrada/pruebas/test_escala.py`.

## Dónde está el cuello de botella

El modelo se llama en paralelo (`concurrent_updates`, 32 por defecto). Lo que corre de a uno, en el hilo del bot, es guardar en la base y ubicar el lugar. Esa parte tomó **65 ms por mensaje**, y el hilo estuvo ocupado el 98 % de la corrida: eso pone el techo de unos 900 por minuto. Es también la razón del máximo de 19 s: los mensajes hacían fila para esa parte.

Con un perfil de 150 mensajes, el 97 % de esos 65 ms se va en `lugares/nomenclator.buscar`, que compara el texto con `difflib` contra todos los nombres y apodos del nomenclátor. Los commits a SQLite pesan poco: unos 2 por mensaje, de 2 ms cada uno, en modo WAL. Por eso no hizo falta tocarlos. Se le avisó al dueño de `lugares/` por el canal.

## Costo (estimado, sin medir)

Precio público de `claude-haiku-5-5`: 0,10 USD por millón de tokens de entrada y 0,50 USD por millón de salida (prompts de hasta 100.000 tokens). Suponemos entre 1.000 y 2.000 tokens de entrada por mensaje (instrucciones, esquema y texto) y entre 150 y 500 de salida (la lectura más el razonamiento con esfuerzo bajo):

| | Por mensaje | Por cada 10.000 mensajes |
|---|---:|---:|
| Supuesto bajo (1.000 entrada, 150 salida) | 0,000175 USD | **1,75 USD** |
| Supuesto alto (2.000 entrada, 500 salida) | 0,00045 USD | **4,50 USD** |

La corrida `--extractor real` reemplaza este supuesto por los tokens medidos: los cuenta desde `usage` y escribe el costo por cada 10.000 mensajes.

## Qué haría falta para cien mil mensajes al día

Cien mil al día son unos 70 por minuto en promedio, dentro del techo de hoy. Lo que no aguanta es un pico de miles en pocos minutos. Para eso, en orden:

1. **Sacar la ubicación de lugares del hilo del bot.** Un índice que filtre candidatos antes de `difflib`, o un caché por texto, porque la gente repite los mismos barrios. Es el cambio que más rinde y no exige infraestructura nueva.
2. **Webhook en vez de polling.** Telegram entrega cada mensaje por HTTP, y se pueden correr varias copias del bot detrás de un balanceador.
3. **Una cola entre recibir y procesar.** El bot recibe, guarda el texto crudo y confirma de inmediato. Varios trabajadores leen con el modelo y ubican el lugar. Si se cae un trabajador, el mensaje sigue en la cola.
4. **PostgreSQL en vez de SQLite**, cuando haya varias copias del bot escribiendo a la vez. SQLite admite un solo escritor.
5. **Respetar los límites de envío de Telegram y de la cuenta de Anthropic.** Hay que consultar los dos antes de una emergencia real; no los medimos.

## Límites de esta medición

- El modelo real no se midió bajo carga: no sabemos cómo se comporta su tiempo de respuesta con 50 llamadas a la vez ni cuándo aparece el límite de tasa de la cuenta.
- La prueba corre en un portátil, no en el servidor de Railway.
- Sin desempate de lugares con modelo. Con él, los mensajes ambiguos harían una segunda llamada al modelo dentro del hilo del bot.
- Mensajes cortos y repetidos de un conjunto de quince.
