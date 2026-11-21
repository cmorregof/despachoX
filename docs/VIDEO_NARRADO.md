# Video narrado de Convite · receta para Jacobo

Adaptada de la receta que Carlos usó en el video de Hefestus (v3, 6 de noviembre de 2026). Sirve para el video de respaldo de la demo: de 60 a 90 segundos, en español, con voz sintética de ElevenLabs y música de fondo. A ElevenLabs se le pasa solo el texto plano de cada escena. El montaje lo hace ffmpeg.

## Antes de grabar

- Reinicia la base con el botón «Reiniciar datos de prueba», en la pestaña Bitácora. Los pedidos urgentes vencen cuatro horas después del reinicio.
- Entra al tablero antes de empezar a grabar. La clave no puede salir en el video.
- Teléfono en «no molestar». En el chat no puede verse ningún nombre ni teléfono real.
- El cierre se dicta con «solo pasa moto». El lector por reglas entiende mal «sí pasa moto».
- El `ENTREGADO` se manda desde el mismo teléfono que hizo el pedido. Desde otro no vale.
- No abras la pestaña Informe. Con la base de la demo muestra dos alertas de vencimiento.
- Graba el video mudo a 1080p y 30 cuadros por segundo. La voz va después.

## Prompt para Claude

Cópialo en Claude, con el conector de ElevenLabs activo, y cambia lo que está entre corchetes.

```
Quiero narrar el video de demostración [RUTA_DEL_VIDEO_MUDO.mp4] con voz sintética y música de fondo. El video muestra Convite, una mesa de despacho de ayuda alimentaria para el Banco Arquidiocesano de Alimentos de Manizales. Dura entre 60 y 90 segundos.

1. Escenas. Mira el video y arma una lista de escenas con su tiempo de inicio en segundos (un escenas.json con {"t", "escena"}). La última entrada es "end" con la duración total.

2. Guion. Parte del borrador de docs/VIDEO_NARRADO.md y ajústalo a lo que de verdad se ve en cada escena. Escribe en español de Colombia un texto por escena, en un guion_narracion.md con una tabla: escena, ventana (s), palabras, habla estimada (s), texto. Calcula unas 2,3 palabras por segundo y marca con ⚠ las escenas cuyo texto no cabe en su ventana. Estilo: frases cortas y declarativas, una idea por frase, tono sereno, sin superlativos ni mercadeo, sin rayas para incisos y sin «no es X, sino Y». Describe lo que se ve en pantalla y por qué importa. No digas ninguna cifra que no esté en pantalla o en docs/SIMULACION.md, sección 9, y toda cifra de simulación lleva la palabra «simulación». Las cifras se escriben como se dicen («noventa y ocho coma tres por ciento», «treinta jornadas»). Los códigos de paquete no se leen. Muéstrame el guion y espera mi aprobación antes de generar audio.

3. Voz. Usa el conector de ElevenLabs (creative_generate_speech): voz [NOMBRE] (voice_id [ID], de la tabla de docs/VIDEO_NARRADO.md), el modelo multilingüe más reciente que ofrezca el conector, una generación por escena, y el texto plano de la escena como prompt, sin etiquetas de emoción. Antes de generar, estima el costo y dímelo. Guarda los audios como n01.mp3, n02.mp3, …

4. Montaje por escena con ffmpeg. Cada audio empieza 0,4 s después del inicio de su escena y deja 0,6 s de cola. Si el audio no cabe, se congela el último cuadro de la escena (tpad=stop_mode=clone); nunca se corta la voz. Video en libx264, crf 20, 30 fps, yuv420p; audio en AAC, 160 kb/s, 44,1 kHz estéreo. Une los segmentos con concat y quita los metadatos (-map_metadata -1).

5. Volumen de la voz: loudnorm I=-16, TP=-1.5, LRA=11.

6. Música. Busca 2 o 3 pistas instrumentales con licencia CC BY (Kevin MacLeod en incompetech.com sirve) y móntalas para que yo elija. Mezcla: la pista en bucle con un crossfade de 4 s hasta cubrir la duración, ganancia 0,32, fade de entrada de 2,5 s y de salida de 5 s, atenuada bajo la voz con sidechaincompress (threshold=0.03, ratio=6, attack=30, release=600), luego amix con normalize=0 y loudnorm I=-16 al final. Deja también una versión sin música.

7. Créditos. Escribe CREDITOS.md con la atribución CC BY de la pista elegida, una nota de que la voz es sintética (ElevenLabs) y otra de que los pedidos y los lotes del video son de prueba.

8. Comprueba que el archivo final pesa menos de 50 MB y dura entre 60 y 90 segundos.
```

## Voces en español de Colombia

Salen de la biblioteca de ElevenLabs, consultada el 21 de noviembre de 2026. Nadie del equipo las ha oído todavía: escucha la muestra de cada una antes de elegir.

| Voz | voice_id | Cómo la describe ElevenLabs |
|---|---|---|
| Robert, colombiano paisa | `AQkGeuTY47dqKKfZBMOO` | Masculina, acento paisa, cálida y conversacional |
| Charlie, profesional y agradable | `35JqiQmWmu3et0NGVNUW` | Masculina, fluida y serena, para contenido informativo |
| Marcus, narración educativa | `xOIP6U1wFJZGZqtVhMKY` | Masculina, seria y explicativa |
| Claudia Isabel | `heUagVbSyc7SphaYWFT3` | Femenina, cálida, para cursos y videos educativos |
| Milena, narradora versátil | `UZPkivpygDffhcwKJsx6` | Femenina, clara y segura |

La primera es la que más se acerca al acento de la región.

## Borrador del guion

Siete escenas. Ajusta las ventanas a tu grabación. A 2,3 palabras por segundo caben unas 170 palabras en 75 segundos.

| # | Lo que se ve | Texto |
|---|---|---|
| 1 | Portada con el logo | Convite es una mesa de despacho de ayuda alimentaria. La hicimos para que la comida llegue aunque la vía se cierre. |
| 2 | Chat: llega un pedido | Una junta pide por chat, con sus palabras. El sistema lee el pedido y le pregunta por el lugar antes de guardarlo. |
| 3 | Tablero: el pedido en la cola | El pedido entra a la mesa del banco de alimentos, con sus familias y sus kilos. |
| 4 | Tablero: calcular y aprobar | El optimizador reparte los pedidos entre camión, campero y moto, y saca primero lo que vence primero. El despachador aprueba el plan con su nombre. |
| 5 | Chat: un conductor reporta un derrumbe | Un conductor avisa que hay un derrumbe en la avenida del Centro. El cierre queda reportado hasta que una persona lo confirma. |
| 6 | Tablero: confirmar y recalcular | El despachador confirma y pide recalcular. El camión ya no llega a San José, así que el pedido pasa a un campero. |
| 7 | Chat: ENTREGADO y tabla por territorio | Quien recibe confirma con el código del paquete, y la entrega queda en la tabla de su comuna. Los datos de este video son de prueba. |

No digas en el video que los tres puntos críticos siguen a tiempo si no se ve en pantalla.

## Montaje por escena (Python y ffmpeg)

`VIDEO_MUDO.mp4` es tu grabación. `escenas.json` y los `nNN.mp3` salen de los pasos 1 y 3.

```python
import json, subprocess
esc = json.load(open('escenas.json'))
t = [e['t'] for e in esc]; t[0] = 0.0          # t[-1] = duración total del video mudo
LEAD, TAIL = 0.4, 0.6
N = len(esc) - 1
dur = [float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration',
       '-of','csv=p=0', f'n{i:02d}.mp3']).decode()) for i in range(1, N+1)]
lst = []
for i in range(N):
    a, b = t[i], t[i+1]; S = b - a; L = max(S, LEAD + dur[i] + TAIL); pad = L - S
    vf = f"trim=start={a}:end={b},setpts=PTS-STARTPTS" + (f",tpad=stop_mode=clone:stop_duration={pad:.3f}" if pad > 0.01 else "")
    af = f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{L:.3f}"
    out = f'seg{i+1:02d}.mp4'
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','VIDEO_MUDO.mp4','-i',f'n{i+1:02d}.mp3','-filter_complex',
        f"[0:v]{vf}[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,{af}[a]",'-map','[v]','-map','[a]',
        '-r','30','-c:v','libx264','-crf','20','-preset','medium','-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','160k','-t',f'{L:.3f}', out], check=True)
    lst.append(f"file '{out}'")
open('lista.txt','w').write("\n".join(lst) + "\n")
```

```bash
ffmpeg -y -f concat -safe 0 -i lista.txt -c copy -map_metadata -1 voz.mp4
ffmpeg -y -i voz.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100 -c:a aac -b:a 160k -map_metadata -1 demo_sin_musica.mp4
```

## Música con atenuación bajo la voz

`L` es la duración del video narrado en segundos.

```bash
L=75.0; M=musica/PISTA.mp3
ffmpeg -y -i demo_sin_musica.mp4 -i $M -i $M -filter_complex "[1:a][2:a]acrossfade=d=4[mm];[mm]atrim=0:$L,asetpts=PTS-STARTPTS,aresample=44100,aformat=channel_layouts=stereo,volume=0.32,afade=t=in:d=2.5,afade=t=out:st=$(python3 -c "print($L-5)"):d=5[mus];[0:a]asplit=2[voz][sc];[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=600[duck];[voz][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 160k -map_metadata -1 demo.mp4
```

## Orden recomendado para hoy

1. Graba el video mudo y súbelo ya al Drive, sin voz. Ese es el respaldo mínimo.
2. Si queda tiempo, hazle la narración con esta receta y reemplaza el archivo.
3. Avisa en `torre/CANAL.md` el nombre del archivo, su duración y si lleva voz.

El video, la música y los audios no van al repositorio: van a la carpeta del Drive.
