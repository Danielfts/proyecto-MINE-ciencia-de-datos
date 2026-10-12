# Videos de sustentación (manim + Gemini TTS)

Los videos de cada entrega se hacen con [Manim Community](https://www.manim.community/). La narración se prototipa con Gemini TTS: se escribe el guion dentro del video, se escucha con una voz sintética y se ajusta, y al final cada integrante lee su parte.

Todo se corre **desde la raíz del repositorio**, con el entorno del proyecto (`uv sync`).

| Archivo | Qué es |
| --- | --- |
| `entrega-N/video/video_entrega_N.py` | Un video: sus escenas y su guion |
| `entrega-N/video/guion.md` | El guion que lee cada integrante. Se genera, no se edita |
| `entrega-N/video/diapositivas.pptx` y `.pdf` | Las diapositivas que se suben con la entrega. Se generan |
| `escena.py` | Escena narrada (`EscenaNarrada`), paleta y ayudas (`lista`, `figura`, `ajustar`) |
| `voz.py` | Servicios de voz (Gemini TTS y un sustituto mudo) y reglas de pronunciación |
| `creditos.py` | Integrantes, curso y la voz de prototipo de cada integrante |
| `guion.py` | Genera `guion.md` y mide cuánto dura el video y cuánto habla cada quien |
| `diapositivas.py` | Genera las diapositivas (PPTX y PDF) |
| `revisar_voz.py` | Transcribe clips de voz para revisar la pronunciación |
| `media/` (en la raíz) | Todo lo generado: videos, voz, capturas. No se sube a git |

## Configuración de la voz

1. Copie `.env.template` como `.env` en la raíz del repositorio y ponga la llave en `GEMINI_API_KEY`. El `.env` no se sube a git.
2. La llave es de **Vertex AI** (un proyecto de Google Cloud con Vertex AI habilitado). Una llave que solo tenga acceso a la API de Gemini no sirve, salvo con `VOZ_VERTEX=0`, que no se ha probado.

Modelo `gemini-3.1-flash-tts-preview`, idioma `es-419`. Cada integrante tiene una voz distinta en `creditos.py`, solo para distinguir quién habla en el prototipo.

Sin `.env`, o con `VOZ_SERVICIO=silencio`, no se genera voz: el video sale mudo, con la duración estimada de cada frase. Quien no tenga llave puede trabajar así.

## Cómo hacer el video de una entrega

1. **Escribir el contenido y el guion** en `video_entrega_N.py`, copiando la forma del que ya existe (ver "Anatomía").
2. **Borrador mudo, por partes.** Renderizar cada escena pequeña en baja calidad y mirar cuadros antes de generar voz:

       VOZ_SERVICIO=silencio uv run manim -ql entrega-1/video/video_entrega_1.py Problematica
       ffmpeg -i media/videos/video_entrega_1/480p15/Problematica.mp4 -vf "fps=1/8,scale=640:-1,tile=3x3" hoja.png

   Buscar texto que se sale del cuadro, elementos encimados y cosas que saltan. La segunda orden necesita ffmpeg; sin él, basta abrir el video. En PowerShell la variable se pone antes: `$env:VOZ_SERVICIO="silencio"; uv run manim ...`.
3. **Generar el guion** y revisar la duración y el reparto:

       uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py

   Escribe `guion.md` junto al video, con la duración total frente al máximo de la entrega y el tiempo de voz de cada integrante. El enunciado pide participación similar de todos.
4. **Render con voz**, uno a la vez:

       uv run manim -qh --fps 30 entrega-1/video/video_entrega_1.py VideoCompleto

   El video queda en `media/videos/video_entrega_1/1080p30/`, con sus subtítulos (`.srt`). Solo se generan los clips de las frases nuevas o cambiadas.
5. **Revisar.** Escuchar el video y pasar por `revisar_voz.py` las frases con siglas o palabras en inglés. Esa revisión es una transcripción automática: si la hace una IA, tiene que decirle a quien lo pidió que nadie ha escuchado el video.
6. **Medir de nuevo** con la voz real del prototipo: `uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py --voz`.
7. **Diapositivas**, cuando el video ya no vaya a cambiar:

       uv run python -m herramientas_video.diapositivas entrega-1/video/video_entrega_1.py

8. **Video final.** Cada integrante lee su parte de `guion.md`. El video se sube a YouTube y su enlace va en el reporte y en el README; las diapositivas y el guion se suben al repositorio.

El paso de la voz de prototipo a las voces grabadas no está automatizado: hay que montar las grabaciones sobre el video o grabarlo mientras se reproduce.

## Anatomía de un video

- Una clase base que hereda de `EscenaNarrada`, con `TITULO`, `LIMITE_MINUTOS` (6 en la primera entrega, 12 en la final), un método `portada`, un método `acto_...` por sección y un `cierre`.
- Al final, escenas pequeñas para probar por partes y `VideoCompleto` con todo.
- `portada` empieza con `self.firma()`: pone abajo los integrantes y el curso, que se van con la portada en `limpiar()`.
- Cada paso es una llamada a `self.narrar((texto, acción), (texto, acción), ..., quien=INTEGRANTE)`. Cada tramo dura lo que tarda en decirse su texto; la acción recibe esos segundos y normalmente llama a `self.paso(d, *animaciones, nota=..., tope=...)`, que no estira la animación más allá de `tope`. Una acción `None` solo deja hablar.
- `quien` es `DANIEL`, `NICOLAS`, `JOUBERT` o `GABRIEL`. Si se omite, sigue hablando el anterior. Define la voz del prototipo, el nombre que sale arriba a la derecha y a quién se le asigna el texto en el guion.
- Cada llamada a `narrar()` es también una diapositiva y un párrafo del guion: conviene que termine en un estado que tenga sentido visto quieto.
- Zonas fijas de la pantalla (14,2 × 8 unidades): `self.seccion("2. ...")` arriba a la izquierda, quien habla arriba a la derecha, `self.nota(...)` abajo con la idea del paso en una frase, y el trabajo en medio. Nada debe pasar de x = ±6,9 ni bajar de y ≈ −2,9.
- `self.seccion(...)` también abre una sección del guion.
- `self.limpiar()` borra todo al terminar una sección.
- Las gráficas de los notebooks se exportan como imagen a `entrega-N/video/imagenes/` y se muestran con `figura(AQUI / "imagenes" / "grafica.png")`.
- Los textos usan `Text`, que no necesita LaTeX. `MathTex` y `Tex` sí lo necesitan.
- Colores y fuente siguen la [identidad visual](../identidad/README.md): fondo negro, texto blanco, `C_AMARILLO` como acento y fuente sin serifas. Los demás colores de `escena.py` son solo para distinguir series en una gráfica.

## Reglas de contenido

- El video es de carácter ejecutivo: resultados y decisiones, no el detalle del procedimiento.
- Todo el texto, hablado y en pantalla, va en español.
- Todos los integrantes participan, con un tiempo similar. `guion.md` muestra el reparto.
- Mostrar, no solo decir: lo que se menciona aparece en pantalla en el momento en que se dice.
- El tiempo se reparte según el peso de cada actividad en la nota; en la primera entrega, el entendimiento de los datos pesa 35 %.

## Voz

- Los clips se guardan en `media/voiceovers/` y se reutilizan mientras el texto, la voz y el modelo no cambien. Cambiar una coma de un `narrar()` genera un clip nuevo, con otra toma.
- El guion se escribe como se ve y `voz.PRONUNCIACION` lo convierte a como debe sonar (siglas, palabras en inglés). Al agregar una regla, comprobar que no cambie el texto de clips ya aprobados.
- `VOZ_SERVICIO=silencio` renderiza un borrador mudo con duraciones estimadas y usa una caché aparte. `VOZ_SOLO_CACHE=1` hace fallar el render si falta algún clip, en vez de generarlo.
- No correr dos renders con voz a la vez: comparten `media/voiceovers/cache.json`.
- La caché no se sube a git: cada integrante genera sus propios clips, y dos tomas del mismo texto no suenan igual.
- El aviso `SoX could not be found` al arrancar no importa: SoX solo se usa para cambiar la velocidad de la voz, que aquí no se hace.

## Tropiezos conocidos

- `objeto.animate...` fija la posición del objeto en el momento en que se escribe. Si se arma antes de mover el objeto, la animación lo devuelve a donde estaba. Armar esas animaciones dentro de la acción, no antes.
- No animar el mismo objeto dos veces en un mismo `play` (por ejemplo `FadeIn` e `Indicate`): el objeto queda fuera de la escena.
- `FadeOut` de un grupo que incluye objetos ya retirados los hace reaparecer un instante. Sacarlos del grupo antes.
- Las acciones definidas dentro de un bucle deben fijar sus variables con argumentos por defecto (`lambda d, fila=fila: ...`).
- Los textos y las fórmulas largas se ajustan con `ajustar(mob, ancho)` para que no se salgan.

## Origen

Este flujo viene de otro proyecto del mismo autor (videos tutoriales narrados con manim y Gemini TTS). Aquí se adaptó a videos con varios integrantes: una voz por integrante, el guion generado con el reparto del tiempo, y textos que no dependen de LaTeX. No se trajo la versión en página web de las diapositivas.
