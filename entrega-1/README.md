# Primera entrega

Fecha límite: **domingo 18 de octubre de 2026, 11:59 PM**. Los pendientes están en [TODO.md](../TODO.md).

| Entregable | Dónde | Límite |
| --- | --- | --- |
| Reporte ejecutivo en PDF | [reporte/](reporte/) | 6 páginas, una columna, Arial 12 |
| Notebook de entendimiento de los datos (actividad 6) | [notebooks/](notebooks/06-entendimiento-de-los-datos.ipynb) | |
| Video de sustentación (YouTube) | [video/](video/) | 6 minutos, con participación similar de todos |
| Guion del video | [video/guion.md](video/guion.md) | |
| Diapositivas del video | `video/diapositivas.pptx` y `.pdf` (se generan) | |

## Reporte

[reporte/reporte.tex](reporte/reporte.tex) tiene una sección por actividad (1 a 7) y, en comentarios, lo que el enunciado pide en cada una y su peso en la nota. Las fuentes van en [reporte/referencias.bib](reporte/referencias.bib).

Se compila con LuaLaTeX, desde la carpeta `reporte/`:

```bash
latexmk reporte.tex
```

- El PDF resultante, `reporte/reporte.pdf`, se sube al repositorio.
- **Arial:** si el equipo no la tiene instalada (es lo usual en Linux), el PDF sale con una fuente sustituta de las mismas medidas y la compilación lo avisa. La versión que se entrega debe compilarse en un equipo con Arial. `pdffonts reporte.pdf` muestra la fuente usada.
- **Páginas:** la compilación avisa en `reporte.log` si se pasa de 6. `pdfinfo reporte.pdf` muestra el número de páginas.
- Para enlazar un recurso del repositorio: `\repo{entrega-1/video/guion.md}{el guion}`.
- **Estilo:** los colores, el encabezado, la portada y los enlaces vienen de [identidad/estilo-reporte.tex](../identidad/estilo-reporte.tex), que comparten las dos entregas. El recuadro `destacado` resalta el resultado o la cifra clave de una sección.
- **Portada:** cuenta dentro de las 6 páginas, así que deja 5 para el contenido. El enunciado recomienda no gastar páginas en portada ni tabla de contenidos. Con `\portadafalse` en `reporte.tex` se cambia por un título compacto en la primera página.

## Notebook

[notebooks/06-entendimiento-de-los-datos.ipynb](notebooks/06-entendimiento-de-los-datos.ipynb) desarrolla la actividad 6: el análisis exploratorio y la calidad de los datos. Tiene el encabezado, la tabla de contenido, la carga de librerías y de los datos, y una sección por etapa con las técnicas del curso que le corresponden a cada una. Las ocho etapas tienen análisis e interpretación.

- **Funciones:** las que usan varias etapas (resúmenes, gráficas univariadas, pruebas con sus supuestos y la bitácora de calidad que alimenta la tabla de la etapa 6.3) están en [notebooks/utilidades_eda.py](notebooks/utilidades_eda.py).

- **Etapas:** siguen el proceso de exploración de las diapositivas de EDA del curso. La tabla de contenido del notebook indica de dónde sale cada una.
- **Ejecución:** de arriba abajo, con el entorno del proyecto. Las instrucciones están en el [README principal](../README.md#notebooks).
- **Salidas:** se suben con el notebook, y el repositorio es público. No pueden mostrar datos personales ni nada que identifique al municipio; el detalle está en la etapa 2 del notebook.
- **Gráficas:** usan el estilo de [identidad/graficas.mplstyle](../identidad/graficas.mplstyle), que el notebook carga en su primera etapa. Cómo usar sus colores está en [identidad/](../identidad/README.md#gráficas).
- **Datos:** lee `datos/predios/predios.parquet`, la base podada en un solo archivo y sin datos personales (ver [datos/predios/](../datos/predios/README.md)). El archivo no está en el repositorio, así que quien lo clone tiene que pedirlo al equipo o construirlo antes de ejecutar el notebook.

## Video

[video/video_entrega_1.py](video/video_entrega_1.py) tiene la portada y una sección por actividad, con la narración por escribir (los textos que empiezan con "Pendiente"). El reparto entre integrantes es provisional.

Desde la raíz del repositorio:

```bash
# Borrador mudo de una sección o del video completo
VOZ_SERVICIO=silencio uv run manim -ql entrega-1/video/video_entrega_1.py VideoCompleto

# Guion para leer, con la duración y el reparto del tiempo
uv run python -m herramientas_video.guion entrega-1/video/video_entrega_1.py

# Prototipo con voz (Gemini TTS; necesita el archivo .env)
uv run manim -qh --fps 30 entrega-1/video/video_entrega_1.py VideoCompleto

# Diapositivas, cuando el video ya no vaya a cambiar
uv run python -m herramientas_video.diapositivas entrega-1/video/video_entrega_1.py
```

El flujo completo, la configuración de la voz y las reglas para escribir el video están en [herramientas_video/README.md](../herramientas_video/README.md).
