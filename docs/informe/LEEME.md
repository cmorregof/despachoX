Cómo añadir una sección al informe de contexto de DespachoX (`informe_contexto.tex`, documento vivo):
1. Crea `secciones/NN_nombre.tex` y empiézalo con `\section{Título}`; el número NN fija el orden de lectura.
2. Añade `\input{secciones/NN_nombre}` en `informe_contexto.tex`, en el lugar que le toca entre los demás `\input`.
3. Toda cifra nueva lleva fecha de corte y nivel de evidencia, y su fuente entra al anexo (`secciones/10_anexo_fuentes.tex`) con «no» en «abierta por una persona».
4. Sube `\versioninforme` y `\fechaversion` al inicio de `informe_contexto.tex` y compila con `./compilar.sh`, que deja el PDF y borra los auxiliares.
