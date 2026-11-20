# Relevo · sesión de coordinación del proyecto (Fable → nuevo chat)

Viernes 20 de noviembre, 4:50 p. m. Lo deja la sesión que coordinó el proyecto desde la mañana, porque su conversación está demasiado larga. Quien la reciba es el nuevo coordinador: lleva la estrategia, la ficha, el pitch, los encargos y el canal. Carlos es el capitán.

## Cómo leer el estado en diez minutos

1. `README.md`: qué hay construido, estado, quién hace qué y cómo se trabaja (ramas, fusiones a las 6:30 p. m., 11:00 p. m. y 8:00 a. m.).
2. `docs/PROBLEMA.md`: el problema.
3. `SAMUEL.md`, `JACOBO.md`, `CARLOS.md`: tareas vigentes.
4. `torre/CANAL.md` desde las 15:05: lo último de cada sesión.
5. `docs/SIN_CONEXION.md`, `docs/SUGERENCIAS.md`, `docs/PLATAFORMA_INNOVO.md`, `docs/investigacion/06_patentes_sipi.md`.

## Estado en una frase

El MVP funciona en la nube de punta a punta (bot https://t.me/despachox_bot, tablero https://despachox-production.up.railway.app); falta la mitad de la rúbrica que no es código: ficha, fuentes verificadas, datos reales, aliados y capacidades UNAL bien sustentadas.

## Frentes abiertos

| Frente | Quién | Dónde |
|---|---|---|
| Bot: entender a un vecino, comodidad, escala medida | Samuel con su Claude Code | `encargos/A2_BOT_SAMUEL.md`, rama `samuel-bot` |
| Bot: pedidos por SMS | Samuel, después de A2 etapa 1 | `encargos/A3_SMS_SAMUEL.md` |
| Tablero: fallos de demo, resumen con Opus, pantalla para miles, mapa sin internet, botón de hojas de ruta | Jacobo con su Claude Code | `encargos/C2_TABLERO_JACOBO.md`, tarea 3 de `JACOBO.md`, rama `jacobo-tablero` |
| Despacho: hoja de ruta impresa con QR y arranque en portátil sin red | Sesión B-despacho de Carlos | `encargos/B3_SIN_CONEXION_CARLOS.md`, rama `carlos-despacho` |
| Simulación: barrido del factor de puntos críticos | Sesión simulacion de Carlos | `encargos/S2_SIMULACION_CRITICOS.md` |
| **Ficha completa** | Un agente Opus lanzado por Fable a las 4:25 p. m. | Rama **`ficha`** cuando termine: `docs/FICHA.md`, `docs/FICHA_MENTORIA.md`, `docs/FUENTES.md`. **Revisarla antes de fusionar** (cifras, que no prometa lo que el código no hace, reglas de redacción de Carlos) |

## Lo que se supo en la mesa a las 4:40 p. m.

- **No habrá datos de la organización.** El kit no está habilitado; Bogotá mandará una carpeta con una lista de patentes y no se compromete a dar datos. Los datos los conseguimos nosotros, de fuentes públicas.
- **Patentes:** no hay un mínimo. Lo que ven con buenos ojos es usar capacidades UNAL de cualquier sede. Recomendaron leer el documento completo y las reivindicaciones en SIPI. **Carlos ya descargó el documento completo** de la patente: pídeselo como adjunto.
- **Otros equipos construyen antenas wifi.** Es vistoso. Decisión: no competir en hardware; DespachoX es la mesa de despacho que corre sobre cualquier red. Ver la sección de canales sin internet abajo.

## Primera acción del nuevo chat: seis agentes Opus en paralelo, más uno opcional

Cada agente arranca sin contexto: dale el encargo completo de abajo, el repositorio (`github.com/cmorregof/despachoX`) y estas reglas comunes:

> Reglas comunes: cada dato con enlace a su fuente y fecha de consulta; no inventes cifras, coordenadas, números de patente ni contactos; lo que no verifiques va marcado «no verificado»; parafrasea, no copies; nada de datos personales de afectados; escribe en español, frases cortas. Entrega en los archivos indicados. No hagas commit: el coordinador revisa y sube a una rama `datos`.

### Datos públicos para reemplazar la semilla sintética (cuatro agentes)

Formato de salida: CSV con la cabecera exacta de `datos/README.md` (para cargarlos con `python -m despacho.semilla --cargar --origen datos_publicos/`), en `datos_publicos/`, más un informe `docs/datos/<tema>.md` con fuentes, supuestos y lo que faltó.

1. **Puntos de entrega y acopios reales de Manizales.** Albergues habilitados tras el sismo, comedores comunitarios, centros de acopio, el Banco de Alimentos y su sede, instituciones educativas usadas como albergue, juntas de acción comunal por comuna. Coordenadas desde OpenStreetMap (Nominatim con una consulta por segundo) o la fuente oficial; nunca de memoria. Marca cuáles son puntos críticos y por qué (albergue, comedor, hogar infantil, ancianato). Salida: `puntos.csv`, `acopios.csv`.
2. **Demanda.** Población y hogares por comuna y barrio de Manizales (DANE, proyecciones, Alcaldía), damnificados del sismo por comuna o barrio si existen, y composición y peso de la canasta o kit de ayuda alimentaria estándar en Colombia (UNGRD, PMA, ABACO, Cruz Roja): kilos por familia por día y por producto. Salida: parámetros de raciones para `entrada/raciones.py` y una tabla de demanda esperada por punto.
3. **Vías y riesgo.** Cierres y derrumbes en las vías de Manizales y sus accesos después del 10 de agosto de 2026 (fechas, duración, tramo, tipo de vehículo que pasaba), antecedentes de 2017 a 2025, y la amenaza por movimientos en masa por sector (SGC, SIMMA, Corpocaldas, IDEA-UNAL). Salida: lista de tramos con historial de cierre amarrables a `datos/semilla/vias.csv` y escenarios de cierre realistas para la simulación.
4. **Flota, perecederos y costos.** Tipos de vehículo que usan Cruz Roja, Defensa Civil y bancos de alimentos, con capacidad útil; velocidades realistas en ladera urbana; vida útil de los productos de la canasta con y sin frío (FAO u otra fuente técnica); costo por kilómetro o por viaje de un despacho. Salida: `vehiculos.csv` realista y una tabla de vida útil por producto para `lotes.csv`.

### Patentes y capacidades UNAL (dos agentes)

5. **Lectura a fondo de las dos patentes vigentes.** Patente 37476 (expediente 14245775, empaque que captura etileno) y patente 33335 (expediente 15111163, control de vehículos con RFID). Con el documento completo que adjunte Carlos y las reivindicaciones de SIPI (https://sipi.sic.gov.co): qué protege cada reivindicación, para qué productos y condiciones se probó, cuántos días de vida útil reporta, y cómo se usaría de verdad en DespachoX (parámetro del modelo, hito del piloto). Salida: `docs/investigacion/07_patentes_a_fondo.md`.
6. **Portafolio de capacidades UNAL de todas las sedes.** Patentes (SIPI por titular y por clasificación B65, A23, G06Q, G08G, G01, H04), grupos de investigación (GrupLAC, Hermes), laboratorios, software y bases de datos de las nueve sedes que sirvan a logística humanitaria, conservación de alimentos, monitoreo de vías y laderas, y **comunicaciones sin internet** (radio, LoRa, redes de malla, SMS). Para cada una: qué es, sede, responsable público, en qué parte de DespachoX entraría y qué tan fuerte es (alta, media, decorativa). Salida: `docs/investigacion/08_capacidades_unal.md`, con un «paquete recomendado» de tres a cinco capacidades.

### Opcional y recomendado (un agente más)

7. **Canales para pedir ayuda sin internet.** Comparar, con fuentes: SMS con pasarela Android, LoRa con Meshtastic (nodos baratos, mensajes de texto en malla de varios kilómetros, librería de Python para leerlos desde un portátil), aplicaciones de malla por Bluetooth, radio VHF de los organismos de socorro, y difusión por radio comunitaria. Para cada uno: costo, alcance, qué hardware, quién lo opera, y cómo entra un mensaje a DespachoX (todos deberían terminar en el mismo lector de `entrada/`). Salida: `docs/investigacion/09_canales_sin_internet.md`.

## Decisión sobre las antenas de otros equipos

DespachoX no construye red. Es la capa de despacho que corre sobre cualquier red: Telegram cuando hay datos, SMS cuando no, LoRa o radio cuando nada más funciona, y papel con QR al final. El mensaje para el pitch: «ellos llevan la señal; nosotros decidimos qué se hace con ella». Acciones: (1) que todos los canales terminen en el mismo lector de mensajes (ya previsto en A3); (2) si el agente 7 confirma que Meshtastic es viable, añadir un receptor que lea los mensajes de un nodo LoRa conectado al portátil, con un simulador si no hay hardware; (3) proponer a un equipo de la vertical de energía y conectividad una alianza para el piloto, y que alguien camine hasta su mesa hoy.

## Pendientes de personas (no los resuelve ningún agente)

- Franja de mentoría de DespachoX (5:00 o 7:00 p. m.).
- Cómo se escoge en la preselección y cuánto dura el pitch.
- Fernando Bernal: anualidad 2026 de la patente 37476, condiciones para un piloto y datos de vida útil.
- Un profesor de logística de la Sede y un usuario real (Banco de Alimentos, Cruz Roja, Defensa Civil, gestión del riesgo).

## Reglas que el nuevo coordinador mantiene

- Las de `CLAUDE.md`, y las preferencias de redacción de Carlos para todo texto que vaya al jurado.
- Nadie sube directo a `main` salvo para documentos de coordinación; el código va en ramas y Carlos fusiona.
- Todo dato del pitch, con fuente verificada por una persona.
