# Entrega final (entrega 2)

Fecha límite: **domingo 29 de noviembre de 2026, 11:59 PM**. Los pendientes están en [TODO.md](../TODO.md). Participan los cuatro integrantes, incluido Gabriel Bejarano, que no participó en la primera entrega.

**Estado:** andamiaje. Cada pieza tiene su estructura y lo que pide el enunciado; el contenido está por escribir (los textos que empiezan con "Pendiente").

**Cómo hacerlo:** el [sitio de prácticas del curso](https://datascience-uniandes.github.io/PracticasMachineLearning/) (PracticasMachineLearning) es la referencia principal para la preparación de datos, la validación, los modelos y el despliegue: sus prácticas y sus guías cortas con código. Cada notebook y el [producto](producto/README.md) enlazan las que le corresponden, y [course-contents/](../course-contents/README.md#relación-con-el-proyecto) relaciona cada actividad con su material del curso.

| Entregable | Actividad | Dónde | Límite |
| --- | --- | --- | --- |
| Reporte ejecutivo en PDF, incremental | Todas | [reporte/](reporte/) | 12 páginas, una columna, Arial 12 |
| Notebook de preparación de datos | 8 (20 %) | [notebooks/08-preparacion-de-datos.ipynb](notebooks/08-preparacion-de-datos.ipynb) | |
| Diagrama de bloques de la preparación | 8 | [diagramas/preparacion.mmd](diagramas/preparacion.mmd) | Recomendado |
| Notebook de estrategia de validación | 9 (5 %) | [notebooks/09-estrategia-de-validacion.ipynb](notebooks/09-estrategia-de-validacion.ipynb) | |
| Notebook de construcción y evaluación del modelo | 10 (20 %) | [notebooks/10-construccion-y-evaluacion-del-modelo.ipynb](notebooks/10-construccion-y-evaluacion-del-modelo.ipynb) | Al menos 3 algoritmos |
| Producto de datos: motor, modelo, API y aplicación web | 11 (20 %) | [producto/](producto/README.md) | Al menos 3 componentes |
| Diagrama de arquitectura | 11 | [diagramas/arquitectura.mmd](diagramas/arquitectura.mmd) | |
| Bitácora de interacciones con la organización | 12 (15 %) | [bitacora-stakeholders.md](bitacora-stakeholders.md) | Al menos 3 interacciones |
| Evidencias de las interacciones (grabaciones) | 12 | [evidencias/](evidencias/README.md) | No se suben: solo el README |
| Conclusiones | 13 (15 %) | Sección 13 del reporte | |
| Video de sustentación (YouTube) | Todas | Fuente en [video/](video/) | 12 minutos, con participación similar de todos |
| Guion del video | | [video/guion.md](video/guion.md) | |
| Diapositivas del video | | `video/diapositivas.pptx` y `.pdf` (se generan) | |
| Declaración de uso de IA | | [../uso-de-ia/entrega-2/USO_DE_IA.md](../uso-de-ia/entrega-2/USO_DE_IA.md) | |

La autoevaluación y la evaluación grupal (actividad 14, 10 %) son un formulario que llega el 30 de noviembre; no hay archivo en el repositorio.

## Reporte

[reporte/reporte.tex](reporte/reporte.tex) parte del reporte de la primera entrega, porque el enunciado pide un reporte incremental: las secciones 1 a 7 son las de la primera entrega, que deben **ajustarse según la retroalimentación** ([../entrega-1/retroalimentacion.md](../entrega-1/retroalimentacion.md)) y resumirse para dejar sitio, y las secciones 8 a 13 son nuevas. Cada sección tiene, en comentarios, lo que pide el enunciado, su peso y, en las secciones 1 a 7, lo que dijo la rúbrica.

Se compila igual que el de la primera entrega, desde la carpeta `reporte/`:

```bash
latexmk reporte.tex
```

**Espacio fijo por sección.** Cada sección tiene un espacio fijo, en páginas, según su peso en la nota y su importancia, y los espacios suman exactamente 12 (el reparto y su razón están en un comentario al comienzo de `reporte.tex`). Al final de cada sección se rellena con espacio en blanco lo que le sobra, así que cada sección empieza siempre en el mismo lugar y el PDF tiene 12 páginas mientras ninguna se pase. Si una se pasa, la compilación lo avisa (`Espacio fijo: sección N (… páginas) se pasa por N líneas`) y aparece una marca amarilla al final de la sección: hay que acortarla. Mientras tanto el PDF tiene más de 12 páginas. Lo implementa [reporte/espacio.tex](reporte/espacio.tex); `\espaciovisiblefalse` quita, para la versión que se entrega, el texto gris que dice cuántas líneas le sobran a cada sección.

**Heredado de la primera entrega.** Las secciones 1 a 7 llevan al comienzo la marca amarilla "Heredado de la primera entrega · pendiente de aprobación" (`\heredado`): son el texto de la primera entrega sin cambios. Se quita de cada sección cuando el equipo la apruebe. La sección 6 ya no la lleva: se reescribió con las mejoras del issue #1 y espera la revisión del equipo. Hoy esas secciones se pasan de su espacio, porque ocupaban 6 páginas y ahora tienen 3,65.

- Las mismas reglas de la [primera entrega](../entrega-1/README.md#reporte): el PDF se sube, debe compilarse con Arial (`pdffonts reporte.pdf`) y la compilación avisa si se pasa de **12** páginas (`pdfinfo reporte.pdf`).
- Las fuentes van en [reporte/referencias.bib](reporte/referencias.bib), que empieza con las de la primera entrega.
- El wireframe de la sección 2 se toma de `entrega-1/reporte/imagenes/`; las imágenes nuevas van en `reporte/imagenes/`.
- `\urlvideo` apunta a YouTube en general hasta que se publique el video.
- Los integrantes del título salen de `\integrantescompacto` (y de `\integrantesportada` si se vuelve a la portada), definidos en el reporte.

## Notebooks

Se ejecutan en orden: el 06 primero y después los demás, porque cada uno lee lo que escribe el anterior:

| Orden | Notebook | Lee | Escribe |
| --- | --- | --- | --- |
| 0 | [06-entendimiento-de-los-datos.ipynb](notebooks/06-entendimiento-de-los-datos.ipynb) — **de la primera entrega, con las mejoras del issue #1; pendiente de aprobación** | `datos/predios/predios.parquet` | Nada |
| 1 | [08-preparacion-de-datos.ipynb](notebooks/08-preparacion-de-datos.ipynb) | `datos/predios/predios.parquet` | `datos/modelado/predios_preparados.parquet` |
| 2 | [09-estrategia-de-validacion.ipynb](notebooks/09-estrategia-de-validacion.ipynb) | Lo que escribe el 08 | `datos/modelado/particion.parquet` |
| 3 | [10-construccion-y-evaluacion-del-modelo.ipynb](notebooks/10-construccion-y-evaluacion-del-modelo.ipynb) | Lo que escriben el 08 y el 09 | `producto/artefactos/modelo.joblib` |

- **Archivos intermedios:** ninguno se sube al repositorio (identifican al municipio o están entrenados con sus datos). Si falta uno, el notebook que lo necesita se detiene con un mensaje que dice qué ejecutar antes.
- **Lo compartido** (rutas, semilla, columnas reservadas y estilo) está en [notebooks/utilidades_modelado.py](notebooks/utilidades_modelado.py). Las funciones del análisis exploratorio están en [notebooks/utilidades_eda.py](notebooks/utilidades_eda.py).
- **Heredado de la primera entrega:** el notebook 06 y `utilidades_eda.py` son copias de `entrega-1/notebooks/`, con una marca visible al comienzo ("Heredado de la primera entrega · pendiente de aprobación"). `utilidades_eda.py` sigue sin cambios; el notebook 06 ya tiene las mejoras del issue #1, que la marca enumera. Las de `entrega-1/` quedan como se entregaron. La marca se quita cuando el equipo apruebe el contenido.
- **Salidas, gráficas y datos:** las mismas reglas que en la [primera entrega](../entrega-1/README.md#notebook). Ninguna salida muestra datos personales ni nada que identifique al municipio.
- **Transformaciones que aprenden de los datos** (imputación, escalado, codificación) se ajustan solo con entrenamiento, dentro del pipeline del notebook 10; el notebook 08 las define.

## Producto de datos

Ver [producto/README.md](producto/README.md): qué hace cada componente y cómo se ejecutan la API y la aplicación.

## Video

[video/video_entrega_2.py](video/video_entrega_2.py) tiene la portada, las secciones 1 a 7 de la primera entrega y una sección por actividad nueva (8 a 13), con la narración por escribir. Las secciones 1 a 7 se toman sin cambios del [video de la primera entrega](../entrega-1/video/video_entrega_1.py), con sus mismos integrantes, y cada diapositiva lleva la marca "Heredado de la primera entrega · pendiente de aprobación" (también en el guion) hasta que el equipo decida si las ajusta según la retroalimentación o las aprueba tal cual. El reparto entre los cuatro integrantes es provisional: Daniel abre y presenta el producto, Nicolas la preparación y la validación, Joubert los modelos y Gabriel la retroalimentación de la organización y las conclusiones.

Desde la raíz del repositorio:

```bash
# Borrador mudo de una sección o del video completo
VOZ_SERVICIO=silencio uv run manim -ql entrega-2/video/video_entrega_2.py VideoCompleto

# Guion para leer, con la duración y el reparto del tiempo
uv run python -m herramientas_video.guion entrega-2/video/video_entrega_2.py

# Prototipo con voz (Gemini TTS; necesita el archivo .env)
uv run manim -qh --fps 30 entrega-2/video/video_entrega_2.py VideoCompleto

# Diapositivas, cuando el video ya no vaya a cambiar
uv run python -m herramientas_video.diapositivas entrega-2/video/video_entrega_2.py
```

El flujo completo está en [herramientas_video/README.md](../herramientas_video/README.md).
