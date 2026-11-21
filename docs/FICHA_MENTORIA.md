# DespachoX · La ficha en una página, para la mentoría 2

Equipo 19 · Vertical 04, Logística y abastecimiento · Sábado 21 de noviembre, 10:30 a. m.
La versión completa, con la fuente y el estado de cada cifra, está en `docs/FICHA.md`. Ninguna fuente ha sido abierta todavía por una persona del equipo, así que toda cifra tomada de una fuente está por verificar.

**Qué cambió desde la mentoría 1.** El piloto ya tiene usuario y territorio. DespachoX entra a la operación diaria del Banco Arquidiocesano de Alimentos de Manizales, en una comuna y una vereda, con la Unidad de Gestión del Riesgo para simulacros y lluvias. El efecto se mide contra la línea base del propio Banco.

| # | Componente | En dos o tres líneas |
|---|---|---|
| 1 | Problema y vertical (20) | La donación llegó y el despacho se atascó. Al sexto día, la red de bancos de alimentos tenía 404.587 kg en acopio y 41.163 kg entregados en todo el país (Portafolio; por verificar). En Manizales se repartió por listas, la salida a Letras suma 87 registros de cierre desde 2017, y lo que existe no despacha |
| 2 | Prototipo (25) | Funciona en la nube de punta a punta, del pedido por chat o SMS al plan aprobado con nombre y al código de entrega, con recálculo ante un cierre. En simulación gana 12 a 46 puntos en críticos a tiempo frente al orden de llegada y empata con un despachador con oficio; se repite con velocidades medidas. La vista por territorio está en construcción |
| 3 | Conocimiento (15) | La capacidad principal es el A25 del IDEA, de la Sede Manizales, que entra en el piloto como riesgo por tramo; el visto bueno de un profesor del IDEA está en gestión. La patente 37476 está en el optimizador como supuesto, con respaldo solo como cota inferior de 1,2 en gulupa a 8 °C |
| 4 | Plan de 30 a 90 días (15) | Días 0 a 15, acuerdo y línea base. Días 15 a 30, reconstrucción en frío de un mes. Días 30 a 60, un día normal de reparto en paralelo. Días 60 a 90, simulacro con la UGR, A25 por tramo y decisión. Si nadie reparte, el piloto pasa al flujo de la UGR y la Gobernación |
| 5 | Viabilidad y aliados (15) | Corre en un portátil o en un servidor pequeño, quien pide no instala nada, y sin internet sigue por SMS y con hoja de ruta impresa. Leer 10.000 mensajes costaría de 1,75 a 4,50 USD, estimado sin medir. Ningún aliado ha visto la propuesta. El IDEA está en gestión, y la llamada al Banco es el sábado a las 8:00 a. m. |
| 6 | Impactos (10) | Los dos indicadores del reto, más kilos entregados sobre kilos en acopio, kilómetros con la misma flota, entregas confirmadas y puntos que dejaron de pedir. Todo se mide contra la línea base del Banco, y la simulación sirve solo de referencia |

**Tres preguntas para los mentores.**

1. La llamada al Banco Arquidiocesano es el sábado a las 8:00 a. m. Para el criterio de viabilidad y aliados, ¿qué evidencia pesa más ante el jurado si no alcanza a llegar una carta: una llamada documentada con nombre y cargo, el interés de la Unidad de Gestión del Riesgo o un correo de intención del Banco?
2. La simulación dice que DespachoX empata con un despachador con oficio en puntos críticos y que le gana en kilómetros y cuando hay pedidos mal ubicados. ¿Lo contamos así en el pitch, o el jurado lo va a leer como que el sistema no aporta?
3. El A25 del IDEA es nuestra capacidad UNAL principal. Entra en el piloto, en los días 60 a 90, y hoy no está en el código. ¿Le basta al jurado el visto bueno de un profesor del IDEA y ese hito, o conviene mostrarlo en el pitch con la alerta amarilla de febrero de 2026?
