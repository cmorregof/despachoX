# Cifras del pitch · DespachoX

Versión 1, sábado 21 de noviembre, poco después de la medianoche, rama `pitch-noche`. Cada cifra o hecho que se dice en voz alta en `pitch/GUION.md` tiene aquí su fila, con la frase exacta, la fuente, el tipo y el estado. Las cifras que solo salen en pantalla van en una tabla aparte.

## Cómo leer esta tabla

**La regla del equipo no cambia.** Una cifra va al pitch solo cuando una persona abrió su fuente y la anotó en `docs/FUENTES.md`. En el guion, toda cifra por verificar lleva un asterisco.

**Dónde está `docs/FUENTES.md`.** En `main` tiene tres filas, y ninguna es de estas cifras. La versión consolidada está en la rama `fuentes-noche` (commit `b4a6389`), con una sección por tema y una tabla de discrepancias numeradas de D1 a D25. Las referencias de la columna «Fuente» apuntan a esa versión, y valen igual si la rama se fusiona.

**Tipo.**

- **Fuente.** Tomada de una fuente externa.
- **Medido.** Lo midió el equipo, y se repite con el código o los datos del repositorio.
- **Estimado.** Estimación con supuestos declarados.
- **Cálculo nuestro.** Cuenta o resta hecha por el equipo sobre datos de una fuente.
- **Inferencia.** Conclusión nuestra a partir de la evidencia.
- **Plan.** Decisión o propuesta del equipo, que no necesita fuente externa.
- **Sintético.** Dato de prueba de la demo.

**Estado.**

- **Verificada por persona.** Alguien del equipo abrió la fuente y anotó su nombre y la hora. A esta hora ninguna cifra está así.
- **Revisada por máquina.** Un lector automático la encontró en su fuente la noche del 20 de noviembre (rama `fuentes-noche`, o esta rama cuando se dice). No reemplaza a una persona.
- **Por verificar.** Nadie la ha abierto, o la máquina no pudo.
- **Pendiente.** El número todavía no existe. Es el caso de [SIM].

## Versión de tres minutos

| # | Frase exacta del guion | Fuente | Tipo | Estado |
|---|---|---|---|---|
| C01 | Bloque 1: «Manizales fue uno de los principales puntos de acopio de la red de bancos de alimentos*» | Noticias RCN, 10 ago 2026, https://www.noticiasrcn.com/colombia/bancos-de-alimentos-activan-corredor-humanitario-tras-sismo-de-7-4-en-colombia-1048906. En el repositorio: `docs/FICHA.md`, tabla «Cifras de la ficha», y `docs/datos/puntos_y_acopios.md`, fila 1. `docs/FUENTES.md` (`fuentes-noche`), sección 3, fila «ABACO activó un corredor humanitario» | Fuente | Revisada por máquina. Falta persona. Se dice «uno de los principales» y nunca «el principal» (D1) |
| C02 | Bloque 1 y versión de un minuto: «Seis días después, los bancos de alimentos tenían 404 toneladas en acopio y habían entregado 41*» | Portafolio, 16 ago 2026, 4:20 p. m., https://www.portafolio.co/economia/regiones/flypass-paga-peajes-de-57-camiones-para-acelerar-la-entrega-de-ayudas-tras-el-terremoto-en-colombia-500521. Cifras exactas: 404.587 kg y 41.163 kg, que se dicen truncadas a toneladas. En el repositorio: `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 1, punto 4, y la figura `docs/informe/figuras/barras_abaco.pdf`. `docs/FUENTES.md` (`fuentes-noche`), sección 3, fila «Al sexto día», y D3 | Fuente. «Seis días después» es cálculo nuestro con la fecha de la nota | Revisada por máquina: las dos cifras están en la nota. Falta persona. La nota atribuye las cifras a «los Bancos de Alimentos», no dice «en todo el país» ni «sexto día», y suma 157.164 kg en tránsito (D3) |
| C03 | Bloque 2: «En Manizales las vías se cierran también sin sismo» | Se sostiene con C04 y C05 y con los cierres de 2017, 2021 y 2023 de `docs/FUENTES.md` (`fuentes-noche`), sección 6, fila «Antecedentes sin sismo» | Fuente | La nota de la ANI de 2021 está revisada por máquina. Las demás, por verificar |
| C04 | Bloque 2: «La salida a Letras suma 87 registros de cierre por derrumbe o deslizamiento desde 2017*» | `datos_publicos/cierres_historicos.csv`, filas de la salida a Letras con causa de remoción en masa; cada fila trae su enlace al registro #767 de INVÍAS o a la nota de prensa. Tabla en `docs/datos/vias_y_riesgo.md`, sección 3. `docs/FUENTES.md` (`fuentes-noche`), sección 6, fila «87 registros», y D15 | Fuente, con conteo nuestro | Recontado por máquina dos veces el 20 nov, en `fuentes-noche` y en esta rama: 87 filas. Falta que una persona abra cinco filas al azar. Son registros y no eventos, los conteos son mínimos y no sirven para comparar años |
| C05 | Bloque 2: «y solo 4 son del sismo*» | Las filas S04, S09, S10 y S11 del mismo CSV, con causa «deslizamiento causado por el sismo» o «deslizamiento por el sismo». Sin ellas quedan 83 filas, de 2017 a enero de 2026. `docs/FUENTES.md` (`fuentes-noche`), D15 | Cálculo nuestro sobre fuente | Contado por máquina en esta rama y en `fuentes-noche`. Falta persona. **Cifra nueva de esta rama en el pitch** |
| C06 | Bloque 3: «Es para quien despacha en el Banco Arquidiocesano de Alimentos y para quienes le piden, como comedores, hogares infantiles y juntas de barrio y de vereda» | El usuario es la propuesta del equipo (`docs/investigacion/10_problema_usuarios_alternativas.md`, sección 4.5; `docs/DECISIONES_9PM.md`, decisión 1). El nombre del Banco: Las2orillas y una monografía de 2020 (`docs/FUENTES.md`, `fuentes-noche`, sección 10) | Inferencia y plan. El nombre es fuente | El Banco no ha visto la propuesta. La nota de Las2orillas está por verificar, porque la máquina no pudo abrirla |
| C07 | Bloque 4: «Hay piezas sueltas, pensadas para la emergencia, y ninguna une el pedido, el vehículo, la vía y la entrega» | Las piezas (RUD, AccessRC y KoboCollect, SUMA/LSS y la plataforma de ABACO): `docs/investigacion/10_problema_usuarios_alternativas.md`, secciones 1 a 3, y `docs/FUENTES.md` (`fuentes-noche`), sección 4. «Pensadas para la emergencia» es lectura nuestra y sigue el principio de Carlos de las 5:19 p. m. (`docs/MENTORIA_1.md`) | Fuente para las piezas. Inferencia para «pensadas para la emergencia» y para «ninguna une», que se limita a las fuentes revisadas | Las piezas, revisadas por máquina salvo el DREF de la IFRC, que la máquina no pudo leer |
| C08 | Bloque 4: «Por ejemplo, el registro de damnificados cerró el 4 de septiembre y dejó por fuera a familias rurales dispersas*» | Vanguardia, 5 oct 2026, https://www.vanguardia.com/colombia/2026/10/05/procuraduria-pide-a-la-ungrd-agilizar-ayudas-para-damnificados-por-el-terremoto/. En el repositorio: `docs/PILOTO.md`, sección 1. `docs/FUENTES.md` (`fuentes-noche`), sección 4, fila «RUD», y D23 | Fuente | Revisada por máquina. Falta persona. La nota habla de auxilios económicos y no de comida, y dice «zonas rurales dispersas y territorios étnicos» |
| C09 | Demo, 1:06: «El plan aprobado ya incluye un pedido de prueba que llegó por chat desde San José» | El mensaje sintético «somos 40 familias en san jose no hay arroz ni leche», `docs/GUION_DEMO.md`, paso «0:20 a 0:55» | Sintético | Se ve en pantalla |
| C10 | Demo, 1:16: «El 21 de octubre, un deslizamiento dejó a un carril la vía a Pereira, y solo pasaban livianos*» | Registro #767 de INVÍAS, objectids 5166664 y 5168264; la consulta está en la fila S22 de `datos_publicos/cierres_historicos.csv`. En el repositorio: `docs/datos/vias_y_riesgo.md`, sección 2, «Septiembre a noviembre». `docs/FUENTES.md` (`fuentes-noche`), sección 6, fila «El 21 de octubre» | Fuente | Revisada por máquina con consulta directa. Falta persona. El registro nombra el tramo «Puente La Libertad-Tres Puertas», PR 19+300, en Santa Rosa de Cabal (Risaralda), con alterna por La Siria. Hubo cierre total desde las 3:32 p. m. y un carril para livianos desde las 11:26 p. m. «Vía a Pereira» es lectura nuestra |
| C11 | Demo, 1:16: «Quien lo sabe primero es el conductor» | `docs/PROBLEMA.md`, sección 3. La apoya el desfase del registro oficial el día del sismo (A03) | Inferencia | No aplica |
| C12 | Demo, 1:51: «el camión ya no llega a San José. El sistema le pasa el pedido a un campero, que sí entra, y los tres puntos críticos siguen a tiempo*» | Ensayo con la semilla: 18 de 18 pedidos, 3 de 3 críticos a tiempo y el pedido 21 en un campero. `docs/GUION_DEMO.md`, «Resultado esperado»; `torre/TORRE_CAPITAN.md`, ensayo del agente B-noche | Medido, sobre la semilla sintética | Medido por un agente el 20 nov a las 11:15 p. m. Falta que una persona lo vea en el ensayo de la mañana |
| C13 | Bloque 6: «Cada paquete lleva un código QR, y la entrega queda registrada cuando ese código llega por chat o SMS» | `despacho/paquetes.py`, `despacho/hoja.py` y `entrada/sms.py`; `docs/FICHA_CORTA.md`, componente 2. `docs/FUENTES.md` (`fuentes-noche`), sección 13 | Medido | Por chat, medido. Por SMS, el lector acertó 20 de 20 mensajes sintéticos en una prueba no independiente, y la pasarela no se ha probado con un celular real |
| C14 | Bloque 6: «Con esos registros, el prototipo arma una tabla por comuna y vereda que mide el piloto» | `despacho/territorio.py` (en `main` desde las 11:15 p. m.); `encargos/T1_TERRITORIO.md` | Medido | La función corre. Falta confirmar que la pestaña «Territorio» del tablero entró antes del congelamiento |
| C15 | Bloque 6: «En [SIM] jornadas simuladas, los críticos a tiempo suben [SIM] puntos frente al despacho por orden de llegada» | La corrida nueva con velocidades medidas, que llega hacia las 6:00 a. m. a `docs/SIMULACION.md` (sección 9, según `docs/FUENTES.md` de `fuentes-noche`, sección 14) | Medido, en simulación | Pendiente. Se llena con el nivel de carga que se cite, la diferencia pareada y su intervalo del 95 %, el número de jornadas y los supuestos. No se usa el +28,6 ni ninguna cifra de la primera corrida |
| C16 | Bloque 6, opcional: «Frente a un despachador con oficio, [SIM].» | La misma corrida | Medido, en simulación | Pendiente. Decirla o no lo decide Carlos después de la mentoría 2 |
| C17 | Bloque 7: «Dura 90 días en la rutina del Banco, con la Unidad de Gestión del Riesgo, en La Macarena y El Tablazo» | `docs/FICHA_CORTA.md`, componente 4; `docs/PLAN_30_90.md` (rama `defensa-noche`), secciones 1 y 4; territorio de `docs/PILOTO_TERRITORIOS.md`, propuesta 1 | Plan | No aplica. El territorio lo decide Carlos y, al final, el Banco |
| C18 | Bloque 7: «Así la capacidad queda en Manizales y se usa entre desastres» | `docs/FICHA_CORTA.md`, componente 4; lecciones de recuperación de `docs/investigacion/10_problema_usuarios_alternativas.md`, sección 5.4 | Inferencia | No aplica |
| C19 | Bloque 7: «Al final suma, tramo por tramo, la alerta de lluvia A25 del IDEA de la UNAL» | IDEA-UNAL, reporte A25 de 2020, https://idea.manizales.unal.edu.co/publicaciones/reportes_meteorologicos/red_manizales/niveles_de_alerta/reportes2020/SAT%20Deslizamientos-Registro%20lluvias%20diarias%20y%20A25%202020.pdf, y Boletín Ambiental 145 de 2018, https://idea.manizales.unal.edu.co/publicaciones/boletines_ambientales/boletin145.pdf. `docs/FUENTES.md` (`fuentes-noche`), sección 8. «Al final» son los días 60 a 90 | Fuente para el indicador. Plan para su uso | Revisada por máquina. Falta persona. No lleva asterisco porque la frase no dice ninguna cifra. La variante «ya está en el código, por ahora con lluvia de prueba» vale solo si Carlos fusiona la rama `a25` |
| C20 | Bloque 8: «Si el Banco no reparte, el piloto pasa al flujo de requerimientos de la UGR y la Gobernación» | `docs/DECISIONES_9PM.md`, decisión 1, aprobada por Carlos a las 10:48 p. m. (canal, 22:50). `docs/PLAN_30_90.md` (rama `defensa-noche`), sección 3, propone aplicarla el día 15 | Plan | No aplica |
| C21 | Bloque 8, variante: «En el Eje Cafetero, el convite era la forma en que los vecinos se juntaban para abrir un camino» | La explicación del nombre que dieron Jacobo y Samuel (canal, 11:30 p. m.) | Explicación del equipo, sin cifra | Solo si Carlos confirma el nombre |

## Versión de un minuto

Repite C02, C03, C06, C17 y C19. Añade tres frases, sin cifras nuevas.

| Frase exacta | Fuente | Tipo | Estado |
|---|---|---|---|
| «Comedores, hogares y juntas piden por chat o SMS, y los conductores reportan los derrumbes» | `entrada/` (bot de Telegram y lector de SMS); `docs/FICHA_CORTA.md`, componente 2 | Medido | Por chat, medido. Por SMS, con la salvedad de C13 |
| «El optimizador reparte entre camión, campero y moto, saca primero lo que vence primero y recalcula si se cierra una vía» | `despacho/optimizar.py` y `despacho/recalcular.py`; `docs/FICHA_CORTA.md`, componente 2 | Medido | Corre en la demo |
| «Todo se mide contra la línea base del propio Banco» | `docs/FICHA_CORTA.md`, componentes 4 y 6; `docs/PLAN_30_90.md` (rama `defensa-noche`), sección 5 | Plan | No aplica |

## Añadidos de cinco minutos

| # | Frase exacta del guion | Fuente | Tipo | Estado |
|---|---|---|---|---|
| A01 | «Manizales está sobre una cuchilla y casi todas sus vías de acceso van por ladera» | `docs/informe/informe_corto.tex`, sección 1, con la figura del mapa. El mismo informe aclara que la dependencia de pocas vías es inferencia nuestra | Inferencia, sobre el mapa | No aplica |
| A02 | «El día del sismo, la Policía anunció al mediodía el cierre de Pereira–Chinchiná*» | Minuto30, 10 ago 2026, 12:03 p. m., https://www.minuto30.com/vias-cerradas-por-sismo-colombia/1715765/, en `docs/datos/vias_y_riesgo.md`, sección 2, «Día 1» | Fuente | Por verificar |
| A03 | «El registro oficial apareció 9 horas y 46 minutos después del sismo*» | Registro #767 de INVÍAS, objectid 5074664: inicio a la 1:00 p. m. y creación a las 5:20 p. m. del 10 de agosto; el sismo fue a las 7:34 a. m. `docs/FUENTES.md` (`fuentes-noche`), sección 6 | Fuente, con resta nuestra | Revisada por máquina con consulta directa. Falta persona |
| A04 | «Para recibir un mercado había que llevar el formato azul de Bomberos*» | Alcaldía de Manizales, 15 ago 2026, https://centrodeinformacion.manizales.gov.co/carpas-de-atencion-cable-aereo-y-linea-de-atencion/. `docs/FUENTES.md` (`fuentes-noche`), sección 3, y D24 | Fuente | Revisada por máquina. Falta persona. No se dice que el formato se entrega después de revisar la vivienda, porque esa nota no lo dice |
| A05 | «los kits se entregaron por turnos en la sede de la Cruz Roja Seccional Caldas*» | Alcaldía de Manizales, 31 ago 2026, https://centrodeinformacion.manizales.gov.co/alcaldia-ugr-y-cruz-roja-intensifican-entrega-de-auxilios-y-alimentos-a-familias-damnificadas-por-el-sismo/. `docs/FUENTES.md` (`fuentes-noche`), sección 3, y D7 | Fuente | Revisada por máquina, que no la encontró igual del todo. Falta persona. La nota no nombra al operador logístico, y por eso la frase no lo hace |
| A06 | «según un estudio de la Javeriana de Cali, las gerencias del FOREC actuaron con autonomía frente a las autoridades locales, y eso debilitó la gobernanza del territorio*» | Pagano y otros, «Reconstruir desde el diálogo social», IEI, Javeriana Cali, 2026, https://www.javerianacali.edu.co/sites/default/files/2026-09/Reconstruir%20desde%20el%20dia%CC%81logo%20social.pdf. `docs/FUENTES.md` (`fuentes-noche`), sección 11 | Fuente | Revisada por máquina. Falta persona. El documento cita a Cuervo Restrepo (2002) para esa afirmación |
| A07 | «Del día 0 al 15, acuerdo y línea base. Del 15 al 30, reconstruimos un mes de despachos del Banco. Del 30 al 60, el Banco reparte como siempre y DespachoX planea en sombra. Del 60 al 90, simulacro con la UGR y decisión escrita del Banco» | `docs/FICHA_CORTA.md`, componente 4; `docs/PLAN_30_90.md` (rama `defensa-noche`), sección 6 | Plan | No aplica |
| A08 | «El piloto cabe en la calamidad pública de Manizales, vigente hasta el 9 de agosto de 2027*» | Alcaldía de Manizales, 16 oct 2026, informe de la UGR al Concejo, https://centrodeinformacion.manizales.gov.co/manizales-presento-informe-al-concejo-de-las-acciones-adelantadas-tras-sismo-del-10-de-agosto/. `docs/FUENTES.md` (`fuentes-noche`), sección 5 | Fuente | Revisada por máquina. Falta persona |
| A09 | «Al Banco le pedimos tres datos sin información personal: sus puntos de entrega, su inventario con vencimientos y un mes de despachos» | `docs/PILOTO.md`, sección 6 | Plan | No aplica |
| A10 | «Sin internet, el plan sale en un portátil y la ruta se imprime con un QR por paquete*» | De la carga de datos a la hoja impresa y una entrega registrada en 23 s, con la red bloqueada: `docs/SIN_CONEXION.md` y `torre/CANAL.md`, entrada de B de las 4:50 p. m. `docs/FUENTES.md` (`fuentes-noche`), sección 13 | Medido | Medido por un agente con la red bloqueada. Falta la prueba con el wifi apagado en el portátil de la demo |
| A11 | «No guardamos el teléfono de quien escribe. Queda como un código» | El remitente se guarda como un código (`remitente_hash`); `docs/FICHA.md`, componente 2 | Medido | Medido. La limpieza de nombres en el texto es heurística y no garantiza que no quede ninguno (`docs/SUGERENCIAS.md`) |
| A12 | La simulación completa, con las dos líneas base, los kilómetros, los perecederos vencidos y la espera del punto peor atendido | La corrida nueva | Medido, en simulación | Pendiente [SIM] |

## Cifras que solo van en pantalla

| # | Diapositiva | Cifra | Fuente | Tipo | Estado |
|---|---|---|---|---|---|
| P01 | 1 | 404.587 kg en acopio, 157.164 kg en tránsito y 41.163 kg entregados | Portafolio, 16 ago 2026 (C02) | Fuente | Revisada por máquina. Falta persona |
| P02 | 2 | «87 registros de cierre desde 2017, 4 del sismo» | C04 y C05 | Fuente, con conteo nuestro | Recontado por máquina. Falta persona |
| P03 | 2 | «21 oct 2026: un carril, solo livianos» | C10 | Fuente | Revisada por máquina. Falta persona |
| P04 | 2 | 50 puntos de entrega reales, 35 críticos, y 2 acopios | `datos_publicos/puntos.csv`, `acopios.csv` y `puntos_acopios_fuentes.csv`. `docs/FUENTES.md` (`fuentes-noche`), sección 9 | Fuente por fila y medido | Por verificar fila por fila |
| P05 | 2, nota | Km 14+700 de la vía a Fresno, 15 nov 2025: 3,6 horas de cierre total y 37 días a un carril | Registro #767, objectids 4881464 y 4881864. `docs/FUENTES.md` (`fuentes-noche`), sección 6 | Fuente | Revisada por máquina con consulta directa. Falta persona |
| P06 | 3 | 204 juntas de acción comunal, 73 de vereda | Alcaldía de Manizales, consolidado de juntas, https://manizales.gov.co/wp-content/uploads/2025/08/CONSOLIDADO-JUNTAS-ACCION-COMUNAL-Y-ADMINISTRADORAS-LOCALES-JAC-JAL.pdf. `docs/FUENTES.md` (`fuentes-noche`), sección 5 | Fuente | Revisada por máquina. Falta persona. El documento no trae fecha |
| P07 | 4 | El RUD cerró el 4 de septiembre | C08 | Fuente | Revisada por máquina. Falta persona |
| P08 | 6 | Tabla por territorio de la demo | `despacho/territorio.py` sobre la base de la demo | Sintético | Lleva la etiqueta «Datos sintéticos de la demo» |
| P09 | 6, C y F | Barras y tabla de la simulación | La corrida nueva | Medido, en simulación | Pendiente [SIM] |
| P10 | 7 | Tres CDI de La Macarena a entre 2,9 y 3,3 km del Banco, y Bajo Tablazo a 9,3 km | `docs/PILOTO_TERRITORIOS.md`, propuesta 1, por la red vial del equipo. `docs/FUENTES.md` (`fuentes-noche`), sección 12 | Medido | Medido por el agente de territorios |
| P11 | 7 | Daños del sismo en El Carmen y en Bajo Tablazo | La Patria, 13 sep 2026, https://www.lapatria.com/manizales/un-mes-del-sismo-en-manizales-estas-son-las-cifras-de-viviendas-afectadas-ayudas-y | Fuente | Por verificar |
| P12 | 7 | En la vereda Java, unas 150 familias incomunicadas, según un líder local | La Patria, 19 mar 2025, https://www.lapatria.com/manizales/sin-paso-en-vereda-de-manizales-colapsa-y-150-familias-quedan-incomunicadas. `docs/FUENTES.md` (`fuentes-noche`), sección 12 | Fuente | Por verificar. Es anterior al sismo |
| P13 | 7 | Calamidad pública vigente hasta el 9 de agosto de 2027 | A08 | Fuente | Revisada por máquina. Falta persona |
| P14 | A | A25: amarilla desde 200 mm, naranja desde 300 y roja desde 400 | C19 | Fuente | Revisada por máquina. Falta persona. No se dice el número de estaciones, porque las fuentes no coinciden (D12) |
| P15 | A, nota | Alerta amarilla del 16 de febrero de 2026, con 200 mm en menos de 25 días | Blu Radio, https://www.bluradio.com/nacion/manizales-entra-en-alerta-amarilla-por-lluvias-que-superan-niveles-historicos-rg10, y Noticias RCN, https://www.noticiasrcn.com/colombia/declaran-alerta-amarilla-en-manizales-por-lluvias-extremas-992470, ambas del 16 feb 2026 | Fuente. Que el umbral sea el del A25 es inferencia | Revisadas por máquina. Falta persona. Ninguna nota nombra al IDEA |
| P16 | A | Patente 37476: factor 1,2, cota inferior en gulupa a 8 °C | Solicitud CO 14-245775, folio 18, en `docs/investigacion/07_patentes_a_fondo.md`, sección 3.4 | Cálculo nuestro sobre fuente | Por verificar. Mide etileno y no vida útil. «Vigente» se dice solo si se confirma la anualidad 2026 |
| P17 | A | 22,6 km/h de un bus medido con GPS en Manizales | Ocampo González (2019), tesis de maestría, UNAL Manizales. `docs/FUENTES.md` (`fuentes-noche`), sección 8 | Fuente | Revisada por máquina. Falta persona |
| P18 | A | Tesis de 2017 sobre la red de ayuda humanitaria de Manizales | https://core.ac.uk/download/427644456.pdf. `docs/FUENTES.md` (`fuentes-noche`), sección 8 | Fuente | Por verificar |
| P19 | A | 178 registros de cierres viales | `datos_publicos/cierres_historicos.csv` | Fuente por fila y medido | Por verificar. La columna `verificado` la llenó un agente |
| P20 | B | 23 s de la carga a una entrega registrada, con la red bloqueada | A10 | Medido | Falta con el wifi apagado |
| P21 | B, nota | El 11 de agosto en la mañana, el 28 % de las estaciones base de Caldas estaba sin servicio | Noticias RCN, 11 ago 2026, https://www.noticiasrcn.com/colombia/senal-movil-en-colombia-46-esta-afectada-1049064. `docs/FUENTES.md` (`fuentes-noche`), sección 7 | Fuente | Revisada por máquina. Falta persona |
| P22 | B, nota | 20 de 20 SMS sintéticos | `entrada/pruebas/reporte_sms.md` | Medido | No es una prueba independiente |
| P23 | E | Las viñetas de los tres territorios | `docs/PILOTO_TERRITORIOS.md`, sección «Para la diapositiva». `docs/FUENTES.md` (`fuentes-noche`), sección 12 | Fuente y medido | Por verificar |

## Cifras que no se dicen, y por qué

- **«Desabastecimiento en 48 horas»**, de la ficha de la vertical. No tiene fuente para este sismo (`docs/PROBLEMA.md`, sección 2).
- **La primera corrida y la segunda ronda de la simulación**, con el +28,6, el 12 a 46, el empate con la experta, los 47 a 75 km, el 0,0 % de vencidos y el 69,1 % y 98,5 % de la ficha. Están en revisión por las velocidades y la vida útil (`docs/FUENTES.md`, `fuentes-noche`, sección 14). En su lugar va [SIM].
- **«Manizales, el principal punto de acopio»** o **«para el Eje Cafetero»**. RCN dice «uno de los principales» (D1).
- **«En todo el país»** y **«al sexto día»** como palabras de la nota de Portafolio. No están en ella (D3).
- **«Autopista del Café»** para el cierre del 21 de octubre. El registro nombra otro tramo, y en voz alta se dice «vía a Pereira».
- **«La Cruz Roja fue el operador logístico»**. La nota de la Alcaldía no nombra al operador (D7).
- **«SUMA no recibe pedidos»**. La OPS dice que SUMA registra solicitudes de artículos (D8).
- **«El PMA entregó efectivo en Valle y Risaralda»**. La nota dice que lo prevé (D9).
- **8.240 damnificados.** No entra en tres minutos. Si se usa, va con su corte del 24 de agosto y nunca junto a las unas 22.000 familias afectadas que reportó EFE el 20 de noviembre, porque miden cosas distintas (`docs/investigacion/10_problema_usuarios_alternativas.md`, sección 5.6).
- **«Vigente» para la patente 37476**, mientras no se confirme la anualidad 2026.
- **Familias por pedido.** El mensaje de la demo dice 40 familias, y una familia vale 1,8, 2,9 o 4 personas según la fuente (D4). Por eso la cifra no se dice en voz alta.

## Orden para verificar antes de la 1:00 p. m.

Primero lo que se dice en los tres minutos, en el orden del guion. Quien verifique anota «Verificada por <nombre>, <hora>» en la fila de `docs/FUENTES.md` (rama `fuentes-noche`, o `main` si ya se fusionó) y cambia el estado aquí. Si la fuente no dice lo mismo, escribe «No coincide», copia lo que dice y avisa a Fable o a Carlos antes de cambiar el guion.

1. **C02**, la nota de Portafolio del 16 de agosto: las dos cifras y a quién se las atribuye. Es la frase que abre el pitch.
2. **C01**, la nota de Noticias RCN del 10 de agosto: «uno de los principales puntos de acopio».
3. **C04 y C05**, el CSV de cierres: cinco filas al azar de la salida a Letras, más las cuatro del sismo (S04, S09, S10 y S11).
4. **C10**, la consulta del registro #767 de la fila S22: el 21 de octubre y «solo livianos».
5. **C08**, la nota de Vanguardia del 5 de octubre: la fecha de cierre del RUD y las zonas rurales dispersas.
6. **P06**, el consolidado de juntas de la Alcaldía, que sale en la diapositiva 3.
7. **C19 y P14**, el reporte A25 de 2020 del IDEA: el indicador y sus umbrales.
8. **P13 y A08**, la nota de la Alcaldía del 16 de octubre: la calamidad hasta el 9 de agosto de 2027.
9. **P11 y P12**, las dos notas de La Patria del territorio, que salen en la diapositiva 7.
10. **C15 y C16**, cuando llegue la simulación: que cada [SIM] coincida con `docs/SIMULACION.md`.

Después, si hay tiempo, los añadidos de cinco minutos, de A02 a A06.
