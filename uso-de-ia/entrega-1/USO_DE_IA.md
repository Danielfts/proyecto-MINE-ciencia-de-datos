# Declaración de uso de IA

Partes del proyecto en las que se utilizó inteligencia artificial, según lo exige el enunciado.

## Herramientas

- **Claude Code** (CLI y extensión de VS Code), con el modelo Claude Opus 5.5 de Anthropic: trabajo dentro del repositorio (código, notebooks, LaTeX, commits).
- **Claude Cowork** (app de escritorio de Claude), con el mismo modelo: explicación de temas del curso, consulta de fuentes y revisión del reporte.
- **Servidor MCP de PostgreSQL** (`crystaldba/postgres-mcp`) en modo de solo lectura: permitió a la IA consultar la base catastral sin poder modificarla.
- **Gemini TTS por Vertex AI** (Google): voz de prototipo del video. Gemini también transcribe los clips para revisar la pronunciación. La voz final es la de cada integrante.

## Partes del proyecto en las que se utilizó IA

Los números remiten a la lista de pasos de la sección siguiente.

### Implementación

Entorno de Python y herramientas del video (pasos 1 y 2); construcción del archivo de datos y unión de la facturación (pasos 4 y 7); código del notebook de entendimiento de los datos (pasos 6 y 8).

### Interpretación de resultados

Lectura de las variables de facturación y pago (paso 7); apoyo en la interpretación del análisis de facturación y pago (paso 8); revisión de las cifras del reporte (paso 9).

### Documentación

Documentación de la base catastral, de su versión podada y del archivo de datos (pasos 3 y 5); edición del reporte para cumplir el límite de páginas (paso 9).

## Pasos más relevantes, en orden cronológico

1. **Entorno de Python reproducible** (12 oct., implementación). La IA definió las dependencias y generó `pyproject.toml`, `uv.lock`, `requirements.txt` y `environment.yml` para que el entorno se instale igual con uv, pip o conda, y documentó en el README la instalación por plataforma. Las tres rutas se probaron en Linux x64; para las demás plataformas se revisó qué binarios publica cada paquete.
2. **Herramientas para el video** (12 oct., implementación). La IA adaptó un flujo de trabajo ya probado en otro proyecto del equipo: escenas narradas con manim, voz de prototipo con Gemini TTS, generación del guion con el tiempo de cada integrante frente al límite y exportación de las diapositivas (`herramientas_video/`).
3. **Documentación y poda de la base catastral** (12 y 13 oct., documentación). Con acceso de solo lectura, la IA documentó la base LADM-COL (`datos/README.md`). A pedido del equipo, que definió el criterio de poda, determinó qué tablas se pueden eliminar, escribió el script de poda y generó el diagrama entidad-relación y el diccionario de la base podada (`datos/base-podada/`). La base podada se comparó con la original mediante huellas MD5 de tablas, llaves y filas.
4. **Archivo de datos sin datos personales** (14 oct., implementación). El equipo definió el diseño: un solo parquet con un predio por fila, las relaciones de uno a muchos anidadas y los datos de los titulares reducidos a conteos. La IA escribió la consulta SQL y el script de Python que lo construyen (`datos/predios/`), y el script se detiene si aparece un campo no previsto. En el notebook, escribió la carga de los datos y la lista de columnas reservadas, cuyos valores no se muestran en ninguna salida.
5. **Diccionario de datos en PDF** (15 oct., documentación). Diccionario en LaTeX que muestra el anidamiento del archivo con un diagrama y un árbol de campos, con definiciones tomadas del diccionario oficial del modelo LADM-COL y un apartado sobre la estructura del número predial nacional. Un script comprobó que los campos coinciden con el esquema del parquet.
6. **Código del análisis exploratorio y de calidad** (13 a 15 oct., implementación). La estructura del notebook sigue el proceso de exploración de las diapositivas de EDA del curso. Sobre la base que preparó el equipo (librerías, estilo de las gráficas y carga de los datos), la IA escribió el código de las etapas 3 a 7:
   - `utilidades_eda.py`: funciones adaptadas de las del primer parcial del curso (resúmenes y gráficas univariadas, atípicos, pruebas de hipótesis con revisión de supuestos mediante QQ-plot y Levene, V de Cramér) y una bitácora de calidad que genera su tabla resumen desde el código.
   - Atributos derivados por predio a partir de construcciones y unidades, y la definición de la unidad de análisis.
   - Reglas de calidad: valores de relleno, conformidad de formatos y dominios (expresiones regulares, listas de valores válidos y distancia de Levenshtein), consistencia entre columnas y tablas, unicidad y relevancia.
   - Técnicas univariadas y multivariadas, gráficas y no gráficas: correlaciones, tablas estratificadas, pruebas por régimen, PCA y una regresión descriptiva con errores agrupados.
   - Revisión automática de que las salidas no muestren datos personales ni identifiquen al municipio.
7. **Facturación y pago en el archivo de datos** (18 oct., interpretación e implementación). La IA respondió preguntas del equipo sobre las variables de facturación con cálculos agregados. Mostró que el valor pagado incluye la sobretasa ambiental y descuenta el pronto pago, por qué el valor pagado de 2026 sería una fuga de información y cuánto coinciden el avalúo catastral y el de la facturación. Con esa información, el equipo decidió mantener un solo archivo, tomar la base catastral como fuente de verdad y agregar solo tres columnas (IPU facturado 2026, pago 2026 y pago 2025). La IA las incorporó a la construcción del parquet, que se detiene sin escribir si cambia el número de predios o si las sumas no coinciden con las de la fuente.
8. **Análisis de facturación y pago en el notebook** (18 oct., implementación e interpretación). Con la pregunta de negocio y el enfoque analítico ya definidos por el equipo, la IA agregó al notebook la concentración del impuesto en los predios de mayor valor, la tasa de pago por zona, régimen, destino y decil de avalúo y una prueba chi-cuadrado del pago de 2026 frente al de 2025. También ajustó las interpretaciones que dependían de esos datos.
9. **Edición y revisión del reporte** (18 oct., documentación e interpretación). A pedido del equipo, la IA recortó y compactó secciones del reporte para bajarlo de 12 a 6 páginas, quitando repeticiones y texto genérico. Después revisó el reporte completo: recalculó las cifras verificables y señaló afirmaciones imprecisas para que el equipo las corrigiera.

## Prompts más relevantes

Copiados textualmente, en el idioma en que se escribieron. Lo que va entre corchetes reemplaza rutas locales u omite parte del texto.

- Entorno (paso 1):
  > scaffold a python environment reproducible for all my teammates. Make it compatible with both pip, conda or uv. We will use this env for the general data analysis and science work, and also throw in the manim community library to build the videos we are asked for each delivery

  > btw, this env might be used by colleages who use different oses, and architectures (windows, mac, intel, amd and or arm etc)
- Herramientas del video (paso 2):
  > create a directory for deliverable 1, with a latex scaffolding for the pdf report, a python scaffolding for the manim video and a scaffolding for the video script for the members to read. We will prototype the video and its script using the gemini text to speech api. so scaffold that to use with manim. I will reference another unrelated project where we already implemented a manim + gemini tts workflow: [ruta local] Explore that workspace and copy the description of the workflow to this project so it can be reliably used in the future.
- Poda de la base (paso 3):
  > here's the task: I want a sort of "minified" version of this database and its schema for this project. First, I want you to determine the "minimum" possible set of tables such that all empty tables are removed such that no join chains are broken between tables that would otherwise have been reachable. A sort of "pruning". When you are done with that, I want you to tell me the most straightforward approach to create a pruned database from the full one so that we are able to do so. Also, I want you to create matching pruned documentation for this new dataset: an ER diagram like the original one built with mermaid and a data dictionary. all in spanish of course.
- Archivo de datos (paso 4):
  > how viable is it to make a single parquet with nested data for the one to many relationships from the core table (lc_predio)? here is what i want: a single parquet with the most data we can have from our pruned dataset, with an important caveat: all personal data from the party tables must be removed and reduced to basic aggregations (like, how many owners, the type of owners (persona natural or juridica) etc). We wont include any specifics about people.
- Fuga de información (paso 7):
  > why can indpago be a feature and vlr paga not? how does it contribute to our model goal?
- Revisión del reporte (paso 9):
  > all sections are done. do a GENERAL audit of the report's quality: it does not have to be perfect, it just has to not have slop, obviously generic stuff or blatantly incorrect statements.

## Flujo de trabajo apoyado por IA

- **Dos herramientas en paralelo.** En una misma sesión de trabajo se alternaron turnos entre Claude Code, para la implementación en el repositorio, y Claude Cowork, para el apoyo conceptual. En algunos casos una herramienta redactó el prompt que se ejecutó en la otra (paso 7).
- **Partes conceptuales.** En la problemática, los KPIs, la ideación del producto y el enfoque analítico, el equipo aportó el conocimiento del negocio y tomó las decisiones. La IA se usó para explicar los conceptos del curso (ASUM-DM, productos de datos, fuga de información), consultar el marco legal, calcular agregados que respaldan las cifras, dibujar el wireframe y pasar a texto las decisiones del equipo. Un ejemplo del contexto que dio el equipo para la ideación:
  > la decisión no se puede automatizar. La mejor preparación para presentar una propuesta en debate es una decisión humana basada en información organizada para decidir, y considerar varios escenarios [...]. Necesitamos apoyo a la decisión.
- **Fundamentación.** Las respuestas se apoyaron en el enunciado, las diapositivas y lecturas del curso y la documentación del repositorio. Lo que es criterio de la IA y no de las fuentes quedó marcado como tal.
- **Privacidad.** El acceso a la base fue de solo lectura. La IA trabajó con agregados y no con datos por predio, y los archivos de datos quedan fuera del repositorio. Antes de cada commit se revisó que nada de lo publicado contuviera datos personales, credenciales ni información que identifique al municipio.
- **Verificación.** Los notebooks se volvieron a ejecutar de principio a fin después de cada cambio. Los PDF se revisaron con `pdffonts` (Arial) y `pdfinfo` (límite de páginas). Los datos derivados se compararon con su fuente (huellas MD5, sumas y conteos), y en el video se revisaron cuadros de cada escena. La revisión de la voz se hizo con transcripción automática.
