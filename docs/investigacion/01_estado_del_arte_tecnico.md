# 01 · Estado del arte técnico y académico — DespachoX

Hackathon UNAL Manizales 2026 · Vertical 04 "Logística y abastecimiento" · Consultado el 20-nov-2026.
Convención: cada afirmación lleva su fuente. "No verificado" = no pude confirmarlo en una fuente primaria o en su ficha bibliográfica.

---

## 1. Logística humanitaria de última milla: qué dice la literatura

| Trabajo | Qué aporta | Conclusión útil para nosotros |
|---|---|---|
| Özdamar, Ekinci y Küçükyazici (2004), *Annals of OR* 129:217-245 ([RePEc](https://ideas.repec.org/a/spr/annopr/v129y2004i1p217-24510.1023-banor.0000030690.27939.39.html)) | Modelo para un sistema de apoyo a decisiones en desastres. Problema de transporte dinámico que se **re-resuelve a intervalos** con nuevas solicitudes, suministros y vehículos. Rutas abiertas: los vehículos no vuelven al depósito. | Re-planificar periódicamente es el patrón clásico. Respalda el "recalcular" de DespachoX. |
| Balcik, Beamon y Smilowitz (2008), *J. of Intelligent Transportation Systems* 12(2):51-63 ([IAOR](https://iaorifors.com/paper/66066), [researchr](https://researchr.org/publication/BalcikBS08/bibtex)) | Modelo entero mixto que decide asignación de suministros y rutas en la última milla, con límites de oferta, capacidad y tiempos de entrega. Busca minimizar costo y maximizar beneficio de forma equitativa. | Asignar (qué recibe cada punto) y rutear (cómo llega) se deciden juntos y tienen trade-offs. |
| Campbell, Vandenbussche y Hermann (2008), *Transportation Science* 42(2):127-145 ([RePEc](https://ideas.repec.org/a/inm/ortrsc/v42y2008i2p127-145.html)) | Proponen minimizar el **tiempo de llegada máximo** o el **promedio**, en vez del costo. | Según el resumen de [Matl et al. (arXiv 2016)](https://ar5iv.labs.arxiv.org/html/1605.08565): minimizar costo dispara los tiempos de llegada; minimizar tiempos sube el costo solo moderadamente. |
| Huang, Smilowitz y Balcik (2012), *Transp. Res. Part E* 48(1):2-18 ([RePEc](https://ideas.repec.org/a/eee/transe/v48y2012i1p2-18.html)) | Define métricas de **eficiencia** (costo), **eficacia** (rapidez y suficiencia) y **equidad** (uniformidad del servicio). | La función objetivo cambia la estructura de las rutas. Hay que reportar las tres familias, no solo km. |
| Holguín-Veras et al. (2013), *J. of Operations Management* 31(5):262-280 ([UC Davis ITS](https://itspubs.ucdavis.edu/publication_detail.php?id=2372)) | Recomiendan minimizar **costo social = costo logístico + costo de privación** (valor económico del sufrimiento por no recibir el bien). | Comparan proxies (penalizaciones, restricciones de equidad, demanda insatisfecha) y muestran que dan resultados distintos. |
| Holguín-Veras et al. (2016), *J. of Operations Management* 45:44-56 ([Penn State](https://pure.psu.edu/en/publications/econometric-estimation-of-deprivation-cost-functions-a-contingent/)) | Estiman funciones de costo de privación para agua potable con valoración contingente. | El costo de privación es **no lineal** en el tiempo de privación. Forma funcional exacta: no verificada (no leí el texto completo). |
| Anaya-Arenas, Renaud y Ruiz (2014), *Annals of OR* 223:53-79 ([RePEc](https://ideas.repec.org/a/spr/annopr/v223y2014i1p53-7910.1007-s10479-014-1581-y.html)) | Revisión sistemática de redes de distribución de ayuda. | Buen punto de entrada para citar el campo. |
| Beamon y Balcik (2008), *Int. J. of Public Sector Management* 21(1):4-25 ([Emerald](https://www.emerald.com/insight/content/doi/10.1108/09513550810846087/full/html)) | Marco de medición de desempeño para cadenas humanitarias, con entrevistas a World Vision. | Las métricas comerciales no bastan. Las categorías concretas de métricas: no verificadas. |

**Función objetivo recomendada.** La literatura converge en que minimizar costo o distancia es inadecuado ([Campbell et al. 2008](https://ideas.repec.org/a/inm/ortrsc/v42y2008i2p127-145.html); [Huang et al. 2012](https://ideas.repec.org/a/eee/transe/v48y2012i1p2-18.html)). La opción teóricamente preferida es el costo social con costo de privación ([Holguín-Veras et al. 2013](https://itspubs.ucdavis.edu/publication_detail.php?id=2372)). Para 24 horas, propongo un proxy declarado: penalizar el retraso de cada pedido con un coeficiente que crece con la prioridad (crítico, perecedero) y penalizar fuertemente la no entrega. Hay que decir en voz alta que es un proxy, no una función de privación estimada.

## 2. Ruteo con red dañada, flota heterogénea y perecederos

**Dinámico.** La referencia estándar es la revisión de Pillac, Gendreau, Guéret y Medaglia (2013), *EJOR* 225(1):1-11 ([PolyPublie](https://publications.polymtl.ca/13267/)). No pude leer su resumen; la clasificación "reoptimización periódica vs. continua" que suele atribuírsele queda **no verificada**. Özdamar et al. (2004) ya usa re-solución periódica ([RePEc](https://ideas.repec.org/a/spr/annopr/v129y2004i1p217-24510.1023-banor.0000030690.27939.39.html)).

**Red incierta.** Escribano Macías et al. (2020), *OR Spectrum* 42(4):1089-1125, modelan un VRP estocástico donde drones revelan el daño de la red antes de rutear vehículos terrestres; prueban en la red de Haití ([RePEc](https://ideas.repec.org/a/spr/orspec/v42y2020i4d10.1007_s00291-020-00602-z.html)). Nuestro equivalente barato: los conductores son los "sensores" que revelan cierres.

**Flota y accesibilidad.** Banerjee, Sen y Mukhopadhyay (2025, preprint) modelan un VRP rico para desastres con vehículos heterogéneos, tiempos de viaje por tipo y restricciones de qué tipo de vehículo accede a qué nodo ([arXiv 2509.13227](https://arxiv.org/abs/2509.13227)). Es exactamente nuestra situación camión/4x4/moto/a pie.

**Perecederos.** Buelvas Padilla et al. (2018), *Logistics Research* 11:2, autores colombianos, modelan un VRPTW multiobjetivo que equilibra daño del alimento y distancia ([BVL](https://www.bvl.de/lore/all-volumes--issues/volume-11/issue-1/vehicle-routing-problem-for-the-minimization-of-perishable-food-damage-considering-road-conditions)). No encontré una formulación humanitaria estándar de "vida útil como ventana dura"; lo razonable es modelar el vencimiento como cota superior de tiempo.

### Receta concreta con OR-Tools (implementable en horas)

1. **Matrices por perfil.** Con osmnx, filtrar el grafo por perfil (camión: vías primarias/secundarias; 4x4: + destapadas; moto: + senderos; a pie: todo). Calcular una matriz de tiempo por perfil entre depósito(s) y puntos. Unidades enteras (segundos), porque OR-Tools trabaja con `int64` ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h)).
2. **Costo por vehículo.** Un callback de tránsito por perfil y `SetArcCostEvaluatorOfVehicle` para cada vehículo. Dimensión de tiempo con `AddDimensionWithVehicleTransits` (un evaluador por vehículo) ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h)).
3. **Capacidad.** `AddDimensionWithVehicleCapacity` con capacidades distintas por vehículo (kg; opcional una segunda dimensión de volumen) ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h); [guía CVRP](https://developers.google.com/optimization/routing/cvrp)).
4. **Acceso por nodo.** `SetAllowedVehiclesForIndex(vehículos, nodo)` para puntos que solo alcanza la moto o el 4x4. Ojo: si el nodo está en una disyunción, puede quedar sin visitar igual ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h)). El acceso por **arco** se resuelve en la matriz del perfil (tiempo muy grande o nodo no permitido).
5. **Ventanas y perecederos.** `CumulVar(i).SetRange(inicio, fin)` para ventanas duras ([guía VRPTW](https://developers.google.com/optimization/routing/vrptw)). Para urgencia blanda: `SetCumulVarSoftUpperBound(i, objetivo, coef)`, que suma `coef × retraso` y está pensado para tardanza ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h)). Perecedero: cota dura = vencimiento − margen; coeficiente alto.
6. **No visitados.** `AddDisjunction([i], penalización)` para cada pedido. Penalización > suma de distancias para que solo se descarte lo infactible; puede variar por nodo ([guía penalizaciones](https://developers.google.com/optimization/routing/penalties)). Usar penalización ∝ kg perecederos × prioridad: un perecedero descartado = desperdicio.
7. **Búsqueda.** Primera solución `PATH_CHEAPEST_ARC` o `PARALLEL_CHEAPEST_INSERTION`; metaheurística `GUIDED_LOCAL_SEARCH`, que la documentación llama la más eficiente para VRP; fijar `time_limit` ([opciones de ruteo](https://developers.google.com/optimization/routing/routing_options)). Las metaheurísticas de OR-Tools no paran solas; sin límite no terminan ([manual OR-Tools](https://lia.disi.unibo.it/Staff/MicheleLombardi/or-tools-doc/user_manual/manual/metaheuristics/metaheuristics_summary.html)). Sugerencia: 10-30 s por re-plan.
8. **Re-planificación tras cierre.** Quitar la arista del grafo, recalcular solo las filas/columnas afectadas, poner como inicio de cada vehículo su posición actual, sacar lo ya entregado y re-resolver. Se puede sembrar con la ruta previa (`ReadAssignmentFromRoutes`), pero puede fallar si la ruta vieja ya no es factible ([routing.h](https://raw.githubusercontent.com/google/or-tools/stable/ortools/constraint_solver/routing.h); [hilo or-tools-discuss](https://groups.google.com/g/or-tools-discuss/c/rvnbHeftYzs)). Fallback: resolver desde cero. Los nodos nuevos deben ir en disyunción o la solución previa deja de ser factible ([mismo hilo](https://groups.google.com/g/or-tools-discuss/c/rvnbHeftYzs)).

### Límites conocidos de OR-Tools

- Matrices estáticas: no hay tiempos dependientes del instante en la API básica (los ejemplos usan una sola matriz de duración; [issue PyVRP #453](https://github.com/PyVRP/PyVRP/issues/453)). Un cierre se modela re-resolviendo.
- Un solo núcleo por resolución, según un comentario en el mismo issue ([PyVRP #453](https://github.com/PyVRP/PyVRP/issues/453)). No verificado en documentación oficial.
- Solo enteros: escalar tiempos y kg.
- Sin garantía de óptimo; con límite de tiempo puede devolver un óptimo local no alcanzado (`ROUTING_PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED`) o fallar por tiempo (`ROUTING_FAIL_TIMEOUT`) ([opciones](https://developers.google.com/optimization/routing/routing_options)).
- Costos por tramo convexos (privación no lineal) no se expresan directo en Python; la función de costo por tramos existe en C++ pero su exposición en Python: no verificada.
- Re-sembrar con la solución anterior es frágil ([hilo](https://groups.google.com/g/or-tools-discuss/c/rvnbHeftYzs)).

## 3. Herramientas existentes

| Herramienta | Qué hace | Licencia | ¿Resuelve nuestro problema? / hueco |
|---|---|---|---|
| **OR-Tools** | Solver VRP con dimensiones, ventanas, disyunciones | Apache 2.0 (no verificado en esta sesión) | Núcleo de optimización. No trae red vial ni flujo de pedidos. |
| **VROOM** | Resuelve CVRP, VRPTW, flota heterogénea multi-depósito, pickup-delivery; *skills* y prioridad por trabajo; usa OSRM, ORS o Valhalla o matriz propia ([GitHub](https://github.com/vroom-project/vroom)) | BSD-2-Clause | Alternativa rápida. Las *skills* sirven para "solo moto". No menciona perfiles de ruteo por vehículo. |
| **OSRM** | Rutas y matrices muy rápidas (CH, MLD) ([Wikipedia](https://en.wikipedia.org/wiki/Open_Source_Routing_Machine)) | BSD simplificada | Preprocesa el grafo; cerrar vías implica re-procesar. Manejo de cierres en caliente: no verificado. |
| **Valhalla** | Costeo dinámico en tiempo de ejecución, matrices, TSP, multimodal ([GitHub](https://github.com/Valhalla/valhalla)) | MIT | Bueno para cierres sin re-procesar. Requiere montar servidor. |
| **openrouteservice** | Direcciones, matrices, isócronas; optimización vía VROOM como servicio aparte ([GitHub](https://github.com/GIScience/openrouteservice)) | GPL-3.0 / LGPL-3.0 | API pública con cuotas. Parámetro de polígonos a evitar: no verificado en esta sesión. |
| **ORS para desastres (HeiGIT)** | Integra vías bloqueadas (Copernicus EMS, organizaciones) y las evita al rutear; API con datos OSM cada 10 min ([taller ORS](https://giscience.github.io/openrouteservice-workshop/usecases/disaster_portal.html)). En el sismo de Venezuela (24-jun-2026) montaron instancia con bloqueos de HDX, actualización manual inmediata y re-cálculo con reportes de campo ([HeiGIT](https://heigit.org/?p=43303)) | — | **Referente más cercano**. Rutea punto a punto; no asigna pedidos a flota ni prioriza perecederos. Cobertura de Colombia: no verificada. |
| **GraphHopper** | Motor de ruteo; perfiles configurables por JSON/YAML para bloquear o evitar áreas ([blog 1.0](https://www.graphhopper.com/blog/2020/05/25/graphhopper-routing-engine-1-0-released/)) | Apache 2.0 | Ruteo, no VRP (jsprit es proyecto aparte). |
| **osmnx** | Descarga y modela redes OSM; velocidades, tiempos y rutas en Python ([README](https://raw.githubusercontent.com/gboeing/osmnx/main/README.md)) | MIT | Ideal para prototipo: borrar una arista = cierre. Lento para matrices grandes. Exige atribución OSM. |
| **pgRouting** | Dijkstra, A*, K-caminos, TSP en PostGIS; costo calculado por SQL en vivo ([OSGeo Live](https://live.osgeo.org/en/overview/pgrouting_overview.html)) | GPL v2+ | Cierres = UPDATE en SQL. Exige PostGIS; excesivo para 24 h. |
| **Sahana Eden** | Plataforma de gestión de desastres; inventario y activos ([FLOSS Manuals](https://archive.flossmanuals.net/sahana-eden/why-sahana-eden.html)) | MIT | Registro e inventario; no se reporta optimización de rutas. |
| **LMMS (World Vision)** | Registro de hogares con tarjetas legibles por máquina, escaneo en distribución, control de inventario; piloto 2008 en Kenia y Lesoto, ~5.800 hogares ([ALNAP 2009](https://library.alnap.org/system/files/content/resource/files/main/innovationcasestudyno3-lmms.pdf)) | No declarada (co-creado con FieldWorker) | Trazabilidad en el punto de entrega, no ruteo. Referente para nuestro QR. |
| **WFP Optimus** | Optimiza canasta, abastecimiento y red de entrega; 44 operaciones; ahorro de US$273.000 en Haití ([WFP Innovation](https://innovation.wfp.org/project/optimus)) | Propietario/interno | Nivel estratégico (qué comprar y dónde). No despacha vehículos. |
| **WFP DOTS** | Motor que centraliza datos operativos; ~400 usuarios semanales ([WFP 2019](https://publications.wfp.org/2019/beyond-apr/Digital_Transformation.html)) | Interno | Visibilidad, no ruteo. |
| **WFP SCOPE** | Registro de beneficiarios, deduplicación, transferencias en efectivo y especie, conciliación ([manual SCOPE](https://usermanual.scope.wfp.org/scope-cards/content/common_topics/introduction/1_introduction.htm)) | Interno | Identidad y entitlements, no ruteo. |
| **Logistics Cluster LogIE** | Plataforma de intercambio de información logística: mapa multicapa, validación, API ([LogCluster](https://logcluster.org/fr/logie-asdf)) | — | Fuente de capas de acceso; no despacha. |
| **HOT Tasking Manager** | Coordina voluntarios que mapean en OSM ([OSM Wiki](https://wiki.openstreetmap.org/wiki/OSM_Tasking_Manager)) | FreeBSD | Mejora la red base; no reporta daños en tiempo real. |
| **Ushahidi** | Reportes ciudadanos geolocalizados; Haití 2010: ~40.000 reportes ([Wikipedia](https://en.wikipedia.org/wiki/Ushahidi)) | AGPL (v3) | Recolección de reportes; no los convierte en pedidos ni rutas. |
| **KoBoToolbox** | Formularios offline, XLSForm/ODK ([Kobo](https://kobotoolbox.org/about-us/software)) | "Código abierto" (licencia exacta no verificada) | Datos estructurados, pero exige formulario; no chat libre. |
| **RC2 Relief (IFRC)** | Sobre ODK-X: registro, distribución con códigos de barras, offline ([presentación](https://www.sambuz.com/doc/relief-tool-ppt-presentation-118237)) | No declarada | Distribución y registro; sin ruteo. |

**Lectura:** el ecosistema está partido. Unos rutean (ORS, Valhalla, VROOM). Otros registran y trazan (LMMS, SCOPE, RC2, Kobo). Otros recogen reportes (Ushahidi). No encontré una herramienta abierta que una pedidos por chat → optimización de flota mixta con perecederos → re-plan por cierres → trazabilidad.

## 4. LLM/NLP para estructurar reportes y pedidos

- **AIDR** (Imran et al., WWW 2014): clasifica mensajes de crisis con aprendizaje automático y etiquetas humanas en tiempo real; AUC de 80 % en informativo/no informativo en el sismo de Pakistán 2013 ([QCRI](https://qcai.qcri.org/publications/aidr-artificial-intelligence-for-disaster-response)). Lección: humano en el ciclo.
- **CrisisNLP** (Imran, Mitra y Castillo, LREC 2016): corpus etiquetados de crisis 2013-2015, en inglés, español y francés ([CrisisNLP](https://crisisnlp.qcri.org/lrec2016/lrec2016.html)).
- **LLM cero-disparo** (McDaniel et al., 2024): GPT-4o, Gemini y Claude en CrisisBench; el rendimiento varía mucho entre datasets ([arXiv 2410.00182](https://arxiv.org/abs/2410.00182)).
- **Robustez** (Imran et al., WWW 2025): los LLM fallan más justo en **pedidos urgentes y necesidades**, son vulnerables a errores de tipeo, y los ejemplos en el prompt ayudan poco ([QCRI](https://qcai.qcri.org/publications/evaluating-robustness-of-llms-on-crisis-related-microblogs-across-events-information-types-and-linguistic-features)).
- **Chatbots humanitarios** (The Engine Room para IFRC, 2023): proceder con cautela; costos de mantenimiento, privacidad de datos, expectativas de usuarios y necesidad de interacción humana ([The Engine Room](https://www.theengineroom.org/?p=26694)). No encontré evaluaciones publicadas de chatbots LLM por WhatsApp/Telegram para pedidos de ayuda; **no verificado** que existan.

**Implicación:** extracción a JSON con esquema estricto, campos de confianza, confirmación de vuelta al comité ("¿Entendí bien: 40 mercados, barrio X?") y aprobación humana. Nunca despachar sin validar cantidades y ubicación.

## 5. Cómo evaluar: diseño de simulación mínimo y honesto

**Qué hace la literatura.** Compara funciones objetivo sobre las mismas instancias y reporta costo y tiempos de llegada ([Campbell et al. 2008](https://ideas.repec.org/a/inm/ortrsc/v42y2008i2p127-145.html)). Separa eficiencia, eficacia y equidad ([Huang et al. 2012](https://ideas.repec.org/a/eee/transe/v48y2012i1p2-18.html)). Compara políticas heurísticas contra una referencia ([Cook y Lodree 2017](https://ideas.repec.org/a/eee/transe/v106y2017icp353-371.html), que muestran que una política intuitiva puede ser casi óptima: la línea base no debe ser un hombre de paja).

**Diseño propuesto.**

| Elemento | Propuesta |
|---|---|
| Red | OSM real de Manizales/municipio vecino vía osmnx. |
| Demanda | 30-80 puntos (comités), ~20 % críticos (hospital, albergue). Pedidos con kg, % perecedero y vencimiento (6-48 h). Llegada de pedidos en el tiempo (proceso de Poisson). |
| Flota | p. ej. 2 camiones, 2 4x4, 4 motos, 2 a pie; capacidades y velocidades declaradas. |
| Disrupciones | k cierres aleatorios de aristas durante el horizonte; el sistema los conoce solo cuando un conductor los reporta. |
| Escenarios | Bajo / medio / alto daño × demanda normal / pico. |
| Réplicas | ≥ 30 semillas por escenario, **mismas semillas** para ambas políticas (números aleatorios comunes). Reportar media e IC 95 % de la diferencia pareada. |
| Línea base razonable | FIFO por orden de llegada, vehículo libre más cercano con capacidad, camino más corto en la red original, re-ruteo local solo cuando el conductor topa el cierre. Sin prioridad por vencimiento. Es lo que haría un despachador con hoja de cálculo y WhatsApp. |
| Variante intermedia | Mismo optimizador sin re-planificación (plan único). Aísla el valor de recalcular. |
| Métricas | % entregas a tiempo en críticos; % kg perecedero vencido; tiempo de llegada medio y máximo; demanda no atendida; equidad (peor tasa de cumplimiento por punto o Gini); km y horas-vehículo; latencia de re-plan. |
| Supuestos a declarar | Velocidades por perfil; tiempos de servicio; LLM sin errores en la simulación (o con tasa de error inyectada); cierres conocidos al reportarse; demanda sintética. |

## 6. Qué hueco ocupa DespachoX

- Une en un flujo lo que hoy está repartido: entrada por chat, optimización, re-plan por cierres y trazabilidad QR. No encontré una herramienta abierta que lo haga completo (sección 3).
- Toma el dato de cierres del conductor, como el portal de HeiGIT toma reportes de campo ([HeiGIT](https://heigit.org/?p=43303)), pero lo usa para **reasignar pedidos a la flota**, no solo para trazar una ruta.
- Flota mixta con acceso por tipo de vehículo, incluido a pie y tracción animal: modelado en literatura reciente ([arXiv 2509.13227](https://arxiv.org/abs/2509.13227)), raro en herramientas listas para usar.
- Objetivo humanitario explícito (retraso ponderado + no entrega + vencimiento), alineado con [Campbell et al.](https://ideas.repec.org/a/inm/ortrsc/v42y2008i2p127-145.html) y como proxy de [Holguín-Veras et al.](https://itspubs.ucdavis.edu/publication_detail.php?id=2372).
- Perecederos como restricción de primer orden, conectado al indicador del reto (< 5 % de desperdicio).
- Humano al mando: el LLM propone, el despachador aprueba. Coherente con AIDR y con las advertencias sobre chatbots.
- Lo que **no** es nuevo: el solver, el motor de ruteo y la idea de re-planificar. El aporte es la integración y el ajuste al contexto local.

## 7. Riesgos técnicos y cómo evitarlos

| Riesgo | Mitigación |
|---|---|
| osmnx lento al calcular matrices | Recortar el grafo al área (bbox); calcular matrices solo entre nodos de interés; cachear; recalcular solo lo afectado por un cierre. |
| Grafo desconectado tras cierre | Detectar nodos inalcanzables por perfil; quitar ese vehículo con `SetAllowedVehiclesForIndex`; si nadie llega, marcar "sin acceso" y alertar al humano. |
| Solver sin solución o lento | Disyunción en todos los pedidos; `time_limit` fijo; fallback a resolver desde cero si falla la siembra. |
| Unidades mezcladas | Todo en segundos y gramos enteros; pruebas unitarias de la matriz. |
| LLM inventa cantidades o lugares | Esquema JSON estricto; validar contra catálogo de barrios; confirmación al comité; aprobación humana. Inyectar errores en la simulación. |
| Voz en español coloquial | Transcribir y mostrar el texto al despachador; no confiar en la transcripción para cantidades sin confirmar. Calidad no verificada. |
| Simulación sesgada a favor | Línea base razonable, mismas semillas, publicar supuestos, incluir escenarios donde ganamos poco. |
| Datos personales | Guardar el mínimo; QR con ID opaco, no nombres ([The Engine Room](https://www.theengineroom.org/?p=26694)). |
| Atribución OSM | Mostrar "© OpenStreetMap contributors" en mapa y presentación ([README osmnx](https://raw.githubusercontent.com/gboeing/osmnx/main/README.md)). |

---

### No verificado en esta investigación

- Licencia exacta de OR-Tools (se asume Apache 2.0) y de KoBoToolbox.
- Clasificación y conclusiones de Pillac et al. (2013); solo verifiqué la ficha.
- Categorías concretas de métricas de Beamon y Balcik (2008).
- Forma funcional del costo de privación de Holguín-Veras et al. (2016).
- Que OR-Tools use un solo núcleo (solo un comentario en GitHub) y que su costo por tramos esté expuesto en Python.
- Parámetro de polígonos a evitar en ORS y manejo de cierres en caliente en OSRM.
- Cobertura de Colombia del ORS para desastres.
- Existencia de evaluaciones publicadas de chatbots LLM por WhatsApp/Telegram para pedidos de ayuda.
- Ficha completa de de la Torre, Dolinskaya y Smilowitz (2012), "Disaster relief routing: integrating research and practice" (apareció en búsqueda; no pude abrirla).
