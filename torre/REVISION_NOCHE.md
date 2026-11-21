# Revisión de la noche, rama por rama (notas de Fable)

Notas que la sesión de coordinación tomó al llegar cada informe, entre las 23:39 del viernes y las 6:15 del sábado. Complementan `torre/RELEVO_FABLE.md` y `torre/RELEVO_NOCHE2.md`. Son el estado de cada rama cuando llegó su informe: lo que se fusionó después está en el relevo y en el canal.

## demo-noche (terminó 23:39) · HEAD d24cd2d
- Entregó demo/preparar.py, demo/correr.py (33 de 33 verificaciones), demo/CHECKLIST.md, despacho/bench.py y BENCH.md, despacho/tests/test_propiedades.py (25 pasan en 38 s; ninguna xfail).
- Bench de esta noche, no definitivo: 3,3 a 3,6 s por cálculo, acotado por el límite de 3 s del solver; máquina con 2 núcleos al 100 %. El tiempo no crece con el tamaño porque el solver corre hasta su límite. Medición definitiva: `python -m despacho.bench --repeticiones 5 --segundos 3 --salida despacho/bench_resultado.md` con la máquina libre.
- Hallazgos: (1) no existe el botón «Reiniciar datos de prueba»; el reinicio de la nube es `DESPACHOX_REINICIAR=1` en Railway, redesplegar y quitarla (confirmado en despliegue/arranque.sh). (2) docs/GUION_DEMO.md tiene detalles viejos: dice 168 apodos y hoy son 450; `python -m lugares.nomenclator "avenida del centro"` sin filtro ya no da «exacto»; el lector por reglas devuelve «la avenida del centro» con artículo; el plan 3 también avisa `camion: punto:3 quedó aislado`; nombra `entrada.procesar`, que no existe. Arreglar el guion de la demo en la mañana.
- Probar: `python -m demo.preparar`, `python -m demo.correr --sin-pausas`, `python -m pytest despacho/tests/test_propiedades.py`.

## defensa-noche (terminó ~00:00) · HEAD 9b85a37
- Tres archivos nuevos, fusiona sin conflictos: docs/PLAN_30_90.md (4.209 palabras), docs/RIESGOS.md (16 riesgos), pitch/PREGUNTAS_JURADO.md (30 preguntas).
- Revisión automática: 0 rayas, 0 muletillas, 0 «no es…sino». Cifras nuevas comprobadas en datos_publicos/costos.csv (270 COP/kg Bogotá, 1.037.451 COP/día campero ICBF 2021 «verificar antes de usar», 359.400 COP/día bus 2019, 6.395 COP/km cálculo nuestro) y en docs/investigacion/09 (46,1 % de estaciones base caídas, Caldas 28 %, RCN 11-ago-2026).
- Faltan las marcas [SIM] (plan §5 y §7, R6, R14, preguntas 11, 15, 29 y 30) y [P5] (preguntas 4 y 23, tras la visita al Banco). Si entra a25, cambiar «hoy no está en el código» en preguntas 9 y 13 y en R12.
- Decisiones para Carlos: (a) plazo del día 15 para la regla de cambio si el Banco no responde; (b) tareas asignadas al integrante de Ingeniería Industrial (revisión de la formulación con un profesor, medición con odómetro, informe de lecciones); (c) quién responde cada criterio; (d) si el plan de SMS de Claro entra a costos.csv.
- Posibles cruces con Noche-2: docs/PRIVACIDAD.md con R4, aliados/DIRECTORIO.md con la tabla de aliados, revision/JURADO.md con las preguntas.

## pitch-noche (terminó 00:14) · HEAD 6782e4c (con mi arreglo del reinicio)
- pitch/GUION.md: 3 minutos en 8 bloques (por qué, vías sin sismo, para quién, lo que existe, demo de 65 s, qué medimos, piloto, regla de cambio), corte de 2 minutos, añadidos para 5 y versión de 1. pitch/DIAPOSITIVAS.md: 8 + 8 de respaldo (A a H). pitch/CIFRAS_PITCH.md: 21 + 12 + 23 filas; ninguna verificada por persona.
- Revisión automática: 0 rayas, 0 muletillas, 0 «no es…sino».
- La duración del pitch no está en ningún documento; supuso 3 minutos. Preguntar a las 8:30.
- Cifra nueva (conteo suyo, coincide con D15 de fuentes-noche): 4 de los 87 registros de Letras son del sismo (S04, S09, S10, S11); quedan 83.
- Ya aplicó el FUENTES consolidado: «404 toneladas en acopio y habían entregado 41*», sin «en todo el país» ni «al sexto día»; «vía a Pereira» para el cierre del 21 de octubre; la frase de kits no nombra a la Cruz Roja como operador.
- Alinear: pitch/PREGUNTAS_JURADO.md (defensa-noche) y docs/FICHA_CORTA.md todavía dicen «al sexto día… en todo el país» y dan los 87 sin decir que 4 son del sismo.
- Pendiente: [SIM] (C15, C16, diapositivas 6, C, F); figuras por hacer de las diapositivas 3, 6, 7, A, B, C, H (cotejar con figuras_pitch de Noche-2).
- Decisiones para Carlos: duración; quién es la Voz 1 (rol D) y la Voz 2 (sugiere al de Industrial); territorio (recomienda La Macarena y El Tablazo); si se dice en voz alta la comparación con el despachador con oficio; fusionar a25 (cambia la frase a «ya está en el código, por ahora con lluvia de prueba»); el nombre Convite (variante de cierre escrita); frase textual del Banco si hubo visita.
- Arreglé la línea 38 del guion: el reinicio de la nube es DESPACHOX_REINICIAR=1 (no hay botón). Corrección también en el canal (00:12).

## fuentes-noche (terminó ~00:15) · HEAD 2261013
- docs/FUENTES.md con registro consolidado de 117 filas en 17 secciones, discrepancias D1 a D25 y lo que no abrió; docs/VERIFICAR_SAMUEL.md (15 cifras + 8 de reserva); ENTREGA.md (hasta la 1:45 p. m., ya con el reinicio por DESPACHOX_REINICIAR); sección «Para el jurado» al inicio de README.md. No choca con main.
- Revisión automática: 0 rayas, 0 muletillas, 0 «no es…sino»; sin teléfonos ni correos en lo añadido.
- Ninguna cifra verificada por persona; 72 revisadas por máquina; 4 no coinciden con su fuente; 9 son [SIM].
- Discrepancias que tocan ficha e informe: D7 (la Alcaldía no nombra a la Cruz Roja como operador logístico), D8 (SUMA sí registra «solicitudes»), D9 (el PMA «prevé» dar efectivo, no lo «entregó»), D10 (lo del Coliseo es del punto de donaciones del Coliseo Menor; solo está en el informe), D3 (404.587 / 41.163 deja fuera 157.164 kg en tránsito; la nota no dice «sexto día» ni «en todo el país»), D15 (4 de 87 registros de Letras son del sismo), D1 (RCN «uno de los principales», ABACO «principal punto de acopio»; ninguna dice «para el Eje Cafetero»).
- Cifras nuevas con fuente: 157.164 kg en tránsito y 460.317 kg anunciados (Portafolio, 16 ago); Asocapitales 1.449 colapsadas (10 a. m. del 13 ago, n.º 22) y 2.707 (9 p. m. del 13, n.º 24); DANE 400.436 censadas frente a 395.818 de demanda.md; DREF 3.500 kits, 700 en Caldas; DNP 2016 9,76 Mt sobre 28,5 Mt (p. 22); tesis 2019 de la UNAL: 22,6 km/h (p. 50) y 359.400 COP/día (tabla 31).
- Sin abrir: ASIS 2023 (404), ICBF vida útil (403), Las2orillas; SIPI y PDF de la patente quedan para una persona. CARMEN 56031 sin fuente pública.
- Decisiones para Carlos: hora del pitch (la página del evento dice 2:00 a 3:30 y la plataforma 2:30 a 3:30); subir solo la ficha corta o también el anexo; si el jurado recibe el mismo tablero de la demo (una sola base); cómo corregir D7 a D10 en ficha e informe; tamaño de familia (1,8, 2,9 o 4).

## a25 (terminó ~00:15) · HEAD b96ff71
- despacho/a25.py (a25, nivel, alertas_tramos, resumen_a25, riesgo_corredores, temporada, comparar, CLI); datos_publicos/estaciones_a25.csv con _fuentes; datos/demo/lluvia_sintetica.csv con encabezado «LLUVIA SINTÉTICA» y su generador (semilla 2026); 32 pruebas; docs/A25.md (0 rayas, 0 muletillas); 5 filas nuevas al final de docs/FUENTES.md (choca con fuentes-noche al final: dejar ambas).
- Gancho apagado por defecto (DESPACHOX_A25=1 o --a25): costo de arista ×2 en naranja y ×4 en roja, solo en las 8 vías con cierres por ladera; nunca cierra una vía; toca matriz.py, optimizar.py y recalcular.py (145 líneas). Apagado, el plan no cambia (prueba).
- Sobre la fusión con main de las 00:15 pasan 93 de despacho, 24 de despacho/sim y 8 de lugares.
- Cifras: [F] Boletín Ambiental 145 del IDEA (marzo 2018): umbrales 200/300/400 mm (tabla 2, origen Terlien 1996, p. 6), 14 estaciones (tabla 4); reporte A25 de 2020: amarilla o baja, naranja o media, roja o alta. Una persona debe abrir los dos PDF. [M] Con el día del reporte incluido reproduce 36 de 36 valores publicados (Chec-Uribe, 25 ene a 29 feb 2020); sin él, 14 de 29. [C] 5 de 15 tramos de vias.csv quedan a más de 3 km de toda estación: Letras, autopista del Café, Neira, La Siria y vía a Medellín. [M, lluvia sintética] --comparar: apagado 2,3 km en roja y 1,3 en naranja por la Kevin Ángel; encendido 0 y 0,8; en ambos 17/17 y 3/3; rutas +3,7 min (1,3 %). Mide el mecanismo, no un impacto. [S] ×2, ×4 y la cobertura de 3 km no tienen fuente.
- Ojo para el pitch: el corredor de Letras, el más citado, queda fuera de la red de estaciones a 3 km.
- Decisiones para Carlos: fusionar; aprobar factores y cobertura; que el gancho toque solo vías con historial de ladera; la frase «por aprobar» de A25.md §8 diciendo que la lluvia es sintética; si se fusiona, cambiar «hoy no está en el código» en la ficha, FICHA_CORTA y preguntas 9 y 13 y R12 de defensa.
- Pendiente: mostrarlo en el tablero (Jacobo, con resumen_a25); preguntar al IDEA si el día va de 0 a 24 h o de 7 a 7 h, y cuál es la red vigente.

## qa-noche (terminó ~00:17) · HEAD ca195b4
- 8 commits; fusiona sin conflictos con main 2073997; en esa fusión pasan 379 y se omiten 3. Informe en docs/QA_NOCHE.md. Toca entrada/flujo.py, sms.py, pasarela_sms.py, privacidad.py (+ entrada/pruebas/test_qa_noche.py): Samuel debe revisarlos antes de fusionar.
- Paridad con Railway: Python 3.12, main 342 pasan en 1 min 25 s; zxing-cpp y pypdfium2 solo piden libstdc++ y libgcc_s (vienen en python:3.12-slim); arranque.sh responde ok a los 3 s sin variables opcionales.
- Arreglado con 36 pruebas: ENTREGADO por Telegram no registraba la entrega con el modelo activo (ahora la regla lo lee antes); lector de SMS («entrega de mercado en la enea», «no ha llegado DX-7K2Q»); botón f: forjado cambiaba familias de un pedido ajeno (dejaba 99.999); pasarela SMS (Content-Length -1, cliente lento, 401 con DESPACHOX_SMS_TOKEN); quita < y > de entrada y salida del modelo; alerta de silencio nunca se rutea ni se surte.
- Riesgos para la demo: un pin de cualquier chat enseña un apodo, y después «avenida del centro» ofrece una opción en Bogotá (reiniciar justo antes y tocar siempre «Sí» en ensayos); tras reiniciar, las alertas de silencio salen solas (Arrayanes 3 h 4 min, San Jorge 3 h 56 min, Campohermoso 5 h 41 min); no hay botón de reinicio; si se reinicia por SSH, reiniciar el servicio porque el bot guarda las conversaciones en memoria.
- Riesgos ante el jurado sin arreglar: tablero público sin clave (propuesta DESPACHOX_CLAVE_TABLERO, abierta si no existe); código de entrega de 18,58 bits sin tope de intentos (1.401 a 2.058 intentos/s por la pasarela sin token; todo el espacio en 3 a 5 min); tooltips sin escapar (app.py 162, 175, 185, 192, 197); pin del remitente con precisión de un metro (Ley 1581). Sin secretos en 152 commits ni datos personales reales.
- Decisiones para Carlos: commit 341aa81 que fija versiones de Railway; hora del reinicio o subir DESPACHOX_SILENCIO_HORAS; clave del tablero; política de ENTREGADO para el piloto; si el pin de un remitente enseña apodos; si un mensaje descartado cuenta como contacto para el silencio (entrada/silencio.py dice sí; territorio y jacobo-silencio dicen no).
- Avisé a Jacobo y Samuel en el canal a las 00:20.

## manuscrito (terminó ~00:30) · HEAD 4aa2058
- docs/manuscrito/: main.tex, refs.bib (54 referencias revisadas por máquina en Crossref o en la página), main.pdf de 28 páginas (compila con latexmk; 2 citas sin resolver a propósito: PORVERIFICAR_carmen y PORVERIFICAR_patente37476), CITAS_POR_VERIFICAR.md, VENUES.md, figuras/map_manizales.pdf con su script, llenar_resultados.py (llena las tablas 5 a 7 desde resultados.csv; probado solo con el CSV viejo).
- Resumen de 225 palabras más [SIM]; 122 [SIM] y 11 [SIM-CONFIG].
- 8 comentarios CODE-vs-DOC: FEFO es una regla antes del solver; el costo de cada arco incluye 600 s de servicio; un solo viaje por vehículo; en la simulación el empaque 1,2 nunca actúa; personas por familia 4 en raciones.py y 2,9 en el escenario público; kilos por familia 10 en el optimizador y 12 en la simulación.
- Semillas: la corrida de esta noche (20261150 a 20261179) son las de confirmación de §8.3; el factor 3 se eligió con 20261120 a 20261149. No hay solape; corregir la frase del manuscrito que lo deja en duda.
- Discrepancias que tocan ficha y pitch: Semana ubica el cierre Manizales–Fresno en el km 36+800 a 40+300 (Herveo) y no nombra Letras; la recomendación de SMS fue de la CRC, no del MinTIC; LSS (antes SUMA) sí registra solicitudes; las 9 h 46 min del #767 cuentan desde el sismo (4 h 20 min desde el inicio del registro); la nota de los kits es de Es Caldas, no de la Gobernación; la tesis de 2019 habla de velocidades «asignadas» y no confirmó el GPS (docs/datos/flota_perecederos_costos.md dice GPS, tabla 14): una persona debe abrir la tesis; la Alcaldía no nombra a la Cruz Roja como operador.
- Decisiones para Carlos: venue (propone WiP en ISCRAM 2027, 6 a 9 de junio, Perth, convocatoria aún no publicada; luego JHLSCM, acceso abierto sin costo, 10.000 a 11.000 palabras; IJDRR sin verificar; DYNA limita a 10 páginas); autoría; enfoque (modelo y simulación, o territorio y piloto); si se menciona la patente 37476; la división M1, M2 y secundarios sin ajuste por comparaciones múltiples; completar la declaración de uso de IA.

## Lanzado a las 00:30
- Agente `erratas` (Opus): aplica correcciones respaldadas en pitch-noche y defensa-noche; propone en docs/ERRATAS.md (rama erratas) las de ficha, ficha corta, ficha de mentoría e informes, con casilla aplicar o no; arregla docs/GUION_DEMO.md; reúne la evidencia de la tesis sobre GPS. Antes de las 4:30 a. m.
- Mensaje al agente de simulación: escribir «velocidades de la tesis UNAL de 2019 (tabla 14)» con «medidas con GPS: por confirmar», y aclarar que sus semillas son las de confirmación.

## Canal a las 00:11
- Noche-2 (23:48): siete ramas n2-*; sin ANTHROPIC_API_KEY, las evaluaciones son solo por reglas.
- B-despacho (23:50): fusionado a main; 345 pruebas; `resumen.cantidad_supuesta` nuevo.
- Jacobo y Samuel (23:30): nombre Convite (Carlos confirma); definición única de silencio de 6 h (supuesto) con fuente en entrada/silencio.py; rama jacobo-silencio pendiente de fusión.
- Agente del manuscrito esperando permiso de WebFetch desde ~00:10 (Carlos tiene que aprobarlo).
