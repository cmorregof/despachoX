# Relevo · coordinación del proyecto (Fable)

Viernes 20 de noviembre, 23:38. Reemplaza al relevo de las 18:08. Si este chat se corta, el siguiente empieza aquí.

## Estado en una frase

`main` está en 917b42b con 342 pruebas en verde: se fusionó `carlos-despacho` con factor crítico 3, empaque 1,2 en fruta con frío, alertas de silencio sin comida y `despacho/territorio.py`. Esta noche trabajan ocho agentes de Fable, siete en su propia rama, y nada de eso entra a `main` sin revisión.

## Agentes de la noche (entregan antes de las 5:30 a. m.)

| Rama | Entrega | Criterio |
|---|---|---|
| sin rama (`/home/claude/sim-noche`) | Simulación con velocidades medidas: `docs/SIMULACION.md` §9 y una frase para el pitch, hacia las 6:00 a. m. La cadena escribe en `/tmp/simnoche/cadena.log` | 2 y 6 |
| `pitch-noche` | `pitch/GUION.md` (3 minutos y 1 minuto), `pitch/DIAPOSITIVAS.md`, `pitch/CIFRAS_PITCH.md` | todos |
| `defensa-noche` | `docs/PLAN_30_90.md`, `docs/RIESGOS.md`, `pitch/PREGUNTAS_JURADO.md` | 4 y 5 |
| `fuentes-noche` | `docs/FUENTES.md` consolidado, `docs/VERIFICAR_SAMUEL.md`, `ENTREGA.md`, sección del jurado en `README.md` | 1 y 6 |
| `qa-noche` | `docs/QA_NOCHE.md` y arreglos pequeños con prueba (QR, silencio, Ley 1581, paridad con Railway) | 2 y 5 |
| `a25` | `despacho/a25.py`, lluvia sintética marcada, gancho apagado por defecto, `docs/A25.md` | 3 |
| `demo-noche` | `demo/` (preparar, correr, lista de chequeo), `despacho/bench.py` y `despacho/BENCH.md`, pruebas de propiedades | 2 |
| `manuscrito` | `docs/manuscrito/` en inglés (LaTeX), `VENUES.md`, `CITAS_POR_VERIFICAR.md` | largo plazo |

Los agentes del guion y del manuscrito se lanzaron primero con el modelo Fable y cayeron porque ese cupo se agotó hasta las 6:00 a. m.; se relanzaron con Opus a las 23:35. Los clones de los agentes están en `/home/claude/wt/<rama>`.

## Qué hacer a las 6:00 a. m.

1. Leer `/tmp/simnoche/cadena.log` y el informe del agente de simulación. Llenar los [SIM] del guion y de las diapositivas con los números nuevos, con la línea base, el número de escenarios y los supuestos.
2. Revisar cada rama antes de fusionar. Las de documentos (`pitch-noche`, `defensa-noche`, `fuentes-noche`) las puede fusionar Fable. `qa-noche` se fusiona si la suite pasa. `a25` y `demo-noche` necesitan el sí de Carlos antes de las 8:30 a. m., porque traen funciones nuevas.
3. Correr la medición completa de `despacho/bench.py` cuando la simulación haya terminado.
4. Dejar a Carlos el resumen de la mañana: qué hay, qué se fusiona antes de las 8:30 y qué decide él.
5. Antes de la demo: pulsar «Reiniciar datos de prueba» en el tablero de la nube.

## Riesgos abiertos

- Railway redespliega con `fpdf2`, `pypdfium2` y `zxing-cpp`. A las 23:30 el tablero servía la página de Streamlit; falta verlo con clics.
- Jacobo debe mostrar `resumen.verificar` y la pestaña «Territorio».
- Si el cupo de Opus se agota antes de las 6:00 a. m., los agentes se detienen. Lo empujado queda en sus ramas, y el proceso de la simulación sigue solo y escribe en `/home/claude/sim-noche/despacho/sim/resultados_velocidades/`.

## Pendiente de antes

1. Sección del piloto en el informe de contexto.
2. Cifras del pitch abiertas por una persona (Samuel, con `docs/VERIFICAR_SAMUEL.md`).
3. Antes de subir al Drive: quitar la nota interna de la ficha y agregar el enlace al video de respaldo.

## Cómo se trabaja

- Fable sube a `main` solo documentos de coordinación; el código va en ramas y se fusiona con el sí de Carlos, que autorizó a Fable a hacer las fusiones.
- Las fuentes Ancízar del informe corto no se suben al repositorio público (`docs/informe/fuentes/` está ignorado). Están en la carpeta Proyecto Godel de Carlos.
- Toda cifra del pitch, con fuente abierta por una persona.
- Congelamiento: sábado 8:30 a. m. Mentoría 2: 10:30 a. m. Entrega en iNNOVO: 1:00 a 2:30 p. m. Pitch: 2:00 p. m.
