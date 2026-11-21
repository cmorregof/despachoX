# Entrega en iNNOVO · sábado 21 de noviembre

Este archivo dice qué se sube al Drive para iNNOVO, quién lo revisa y a qué hora. La ventana de entrega va de la 1:00 a las 2:30 p. m. del sábado. Las reglas salen de `docs/PLATAFORMA_INNOVO.md`, que Carlos revisó en la plataforma el viernes a las 3:00 p. m. con su cuenta UNAL. Los responsables de cada fila son una propuesta, y Carlos los confirma.

**Aporta a** todos los criterios, porque el jurado califica lo que logra abrir. La evidencia que deja es la entrega registrada en iNNOVO y una captura de pantalla de esa entrega.

## Reglas de la plataforma

Las cinco reglas de esta sección están citadas de `docs/PLATAFORMA_INNOVO.md`.

1. La entrega se hace en la «sección Entregables, botón «Registrar entrega»». La plataforma «pide dos campos: nombre del entregable y **enlace de Google Drive**».
2. «El acceso al archivo depende de los permisos de Drive, así que hay que compartirlo de forma que el jurado lo pueda abrir.»
3. «La agenda marca «Últimos ajustes y entrega» el sábado de 1:00 a 2:30 p. m., con la instrucción de comprobar que los archivos solicitados estén cargados a tiempo.»
4. El pitch de preselección va el «sábado 2:30 a 3:30 p. m. (el sitio anterior decía 2:00)».
5. Del equipo hay «**solo dos cuentas vinculadas** (Samuel y Carlos)». Jacobo, Nicolás y José Manuel «deben entrar con su correo para quedar vinculados».

El mismo archivo trae un aviso más. Con la cuenta de Carlos, el «**formato de prototipo MVP**» y la «**plantilla de presentación**» daban «acceso denegado», y según el archivo «pueden fijar la forma del entregable». Si la mesa los comparte antes de la 1:00 p. m., se revisan antes de cargar.

**Hora del pitch sin resolver.** `CLAUDE.md` y el relevo de Fable ponen el pitch a las 2:00 p. m., y la plataforma lo pone a las 2:30. La página de la hackathon, revisada por máquina el sábado a las 12:05 a. m., todavía dice «2:00 – 3:30 p. m.» para el pitch de selección. Este plan cierra la entrega a la 1:45 p. m., así que sirve con cualquiera de las dos horas. Carlos confirma la hora en la mesa.

## Qué se sube

Todo va en una sola carpeta de Drive, llamada «DespachoX · Equipo 19 · Vertical 04». En iNNOVO se registra una sola entrega con el enlace de esa carpeta. Dentro de la carpeta va además un documento corto, «Enlaces», con los tres enlaces que no son archivos.

| # | Qué | Sale de | Antes de subir | Prepara | Revisa |
|---|---|---|---|---|---|
| 1 | Ficha de los seis componentes, en PDF | `docs/FICHA_CORTA.md` | Quitar los corchetes pendientes, como «[por definir con el Banco]» y «[Video de respaldo: por grabar.]». Poner los números nuevos de la simulación donde vaya un [SIM]. Dejar «por verificar» en toda cifra que Samuel no haya abierto. Revisar las frases de las discrepancias D3, D7, D12, D15, D16 y D18 de `docs/FUENTES.md`, que están en este archivo | Samuel | Carlos |
| 2 | Anexo técnico de la ficha, en PDF, sin la nota interna | `docs/FICHA.md` | Borrar la línea que empieza con «Nota interna, se borra antes de cargar» (hoy es la línea 6) y los corchetes pendientes, como «[Pendiente: lo graba Jacobo…]». Las mismas reglas de cifras de la fila 1. Aquí tocan las discrepancias D3, D7, D8, D9, D12, D14, D15, D16, D18, D19, D21 y D24 | Samuel | Carlos |
| 3 | Informe corto, en PDF | `docs/informe/informe_corto.pdf` | Si cambia alguna cifra, recompilar con `docs/informe/compilar.sh`. Las fuentes tipográficas Ancízar no están en el repositorio, así que solo compila el computador de Carlos. El PDF de hoy trae frases de las discrepancias D3, D7, D8, D9, D10, D11, D14, D18, D21 y D24 | Carlos | Samuel |
| 4 | Enlace al video de respaldo | Lo graba Jacobo con `docs/GUION_DEMO.md` | Subirlo a la misma carpeta, o como video no listado, y abrirlo sin sesión | Jacobo | Carlos |
| 5 | Enlace al repositorio | https://github.com/cmorregof/despachoX | Que la sección «Para el jurado» siga arriba en `README.md`. Que `main` tenga lo fusionado en la mañana. Que `git ls-files` no muestre ningún `.env` ni clave (el `.env.example` sí va, con los valores vacíos) | Carlos | Jacobo |
| 6 | Enlace al tablero y al bot | https://despachox-production.up.railway.app/ y https://t.me/despachox_bot | Abrir el tablero desde un celular con datos móviles. Antes de la demo, reiniciar la base de la nube como dice el aviso de Fable de las 12:12 a. m. en `torre/CANAL.md`. Se pone `DESPACHOX_REINICIAR=1` en Railway, se espera el redespliegue y se quita la variable, porque si se queda borra la base en cada despliegue | Jacobo | Samuel |

## Horario

| Hora | Qué | Quién |
|---|---|---|
| 12:00 m. | Termina la mentoría 2. Se anotan los ajustes que pidan los mentores | Samuel |
| 12:00 a 12:40 | Ajustes de texto en la ficha y en el anexo, sin funciones nuevas | Samuel, con Carlos |
| 12:40 | PDF de la ficha y del anexo, con los comandos de abajo. Se revisa que el anexo no traiga la nota interna | Samuel |
| 12:50 | Carpeta de Drive con los tres PDF y el documento «Enlaces». Permiso «Cualquier persona con el enlace», como lector | Carlos |
| 1:00 | Abre la ventana de entrega. Una persona distinta de quien subió abre cada elemento en una ventana de incógnito y en un celular con datos móviles | Jacobo |
| 1:15 | Registro en iNNOVO, con el nombre «DespachoX · Equipo 19 · Vertical 04» y el enlace de la carpeta | Samuel |
| 1:20 | Comprobación en iNNOVO de que la entrega aparece y abre, con captura de pantalla | Carlos |
| 1:45 | Límite del equipo. Desde esta hora no se cambia ningún archivo de la carpeta | Todos |
| 2:30 | Cierra la ventana de iNNOVO | |

## Cómo sacar los PDF

La forma más simple es abrir el archivo en GitHub y usar «Imprimir» del navegador, con destino «Guardar como PDF». GitHub dibuja las tablas, y así no hace falta instalar nada.

Si el computador tiene pandoc y LuaLaTeX, estos comandos sacan los dos PDF desde la raíz del repositorio. El segundo borra antes la nota interna.

```
pandoc docs/FICHA_CORTA.md -o DespachoX_ficha.pdf --pdf-engine=lualatex -V geometry:margin=2cm
sed '/Nota interna, se borra antes de cargar/d' docs/FICHA.md > /tmp/ficha_anexo.md
pandoc /tmp/ficha_anexo.md -o DespachoX_ficha_anexo.pdf --pdf-engine=lualatex -V geometry:margin=2cm
```

## Lista final, antes de registrar

- [ ] Ningún PDF trae «Nota interna», «[por definir», «[Pendiente», «[Video» ni «[SIM]».
- [ ] Cada cifra de la ficha está en `docs/FUENTES.md`, y la que nadie abrió sigue diciendo «por verificar».
- [ ] Las frases con discrepancia en `docs/FUENTES.md` quedaron corregidas por Carlos o Fable, o se quitaron.
- [ ] Las cifras de la simulación son las de la corrida nueva, con su línea base, el número de escenarios y los supuestos.
- [ ] Ningún documento trae nombres, teléfonos ni direcciones exactas de personas afectadas (Ley 1581 de 2012).
- [ ] Los seis elementos abren sin sesión de Google, en incógnito y en un celular con datos móviles.
- [ ] La entrega aparece en iNNOVO con el nombre acordado, y su captura queda guardada.
- [ ] Jacobo, Nicolás y José Manuel vincularon su cuenta en iNNOVO.

## Lo que decide Carlos

1. Si se sube solo la ficha corta o también el anexo técnico.
2. La hora del pitch, 2:00 o 2:30 p. m.
3. Si el jurado recibe el mismo enlace del tablero que se usa en la demo. La base de la nube es una sola, así que lo que haga el jurado en el tablero se ve después en la demo.
4. Los responsables de cada fila de esta lista.
