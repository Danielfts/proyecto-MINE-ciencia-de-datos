# Proyecto Final — MINE-4101 Ciencia de Datos Aplicada

Proyecto final del curso MINE-4101: Ciencia de Datos Aplicada (semestre 2026-20), Universidad de los Andes.

## Integrantes

Estos son los nombres que deben aparecer en todas las entregas y artefactos del proyecto (reportes, diapositivas, videos y documentación):

- Daniel Felipe Triviño Santana
- Nicolas Bedoya Figueroa
- Joubert Daniel Álvarez
- Gabriel Bejarano

## Organización del repositorio

| Carpeta o archivo | Contenido |
| --- | --- |
| [entrega-1/](entrega-1/README.md) | Primera entrega: reporte en LaTeX, notebook de entendimiento de los datos, video de sustentación, guion y diapositivas |
| [datos/](datos/README.md) | Documentación de la base de datos catastral (modelo LADM-COL) que sirve de fuente al proyecto, y los modelos INTERLIS y el diccionario de datos de los que sale su estructura. En [datos/base-podada/](datos/base-podada/README.md): la versión reducida de la base que usa el proyecto, con su diagrama entidad-relación, su [diccionario de datos](datos/base-podada/diccionario-de-datos.md) y el script que la crea. En [datos/predios/](datos/predios/README.md): cómo convertir la base podada en un archivo parquet con un predio por fila y sin datos personales |
| [identidad/](identidad/README.md) | Identidad visual del proyecto (colores, tipografía y logo de la Universidad de los Andes) y el estilo de los reportes y de las gráficas |
| [herramientas_video/](herramientas_video/README.md) | Herramientas y flujo de trabajo para hacer los videos con manim y Gemini TTS |
| [course-contents/](course-contents/README.md) | Material de referencia del curso (no versionado; el README indica qué debe contener) |
| [Proyecto Final.pdf](Proyecto%20Final.pdf) | Enunciado del proyecto |
| [TODO.md](TODO.md) | Pendientes y fechas límite de cada entrega |
| [USO_DE_IA.md](USO_DE_IA.md) | Declaración de uso de IA |
| `pyproject.toml`, `uv.lock`, `requirements.txt`, `environment.yml` | Entorno de Python |

## Notebooks

Se ejecutan en este orden, con el [entorno de Python](#entorno-de-python) instalado. Leen el archivo `datos/predios/predios.parquet`, que no está en el repositorio porque identifica al municipio: hay que pedirlo al equipo o construirlo a partir de la base podada, como indica [datos/predios/](datos/predios/README.md).

| Orden | Notebook | Actividad | Estado |
| --- | --- | --- | --- |
| 1 | [entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb](entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb) | 6. Entendimiento de los datos | En desarrollo: carga los datos (etapa 2); las etapas 3 a 8 están por desarrollar |

Se abren con JupyterLab (`uv run jupyter lab`) o con VS Code y se ejecutan de arriba abajo. También desde la terminal, en la raíz del repositorio:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.record_timing=False entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb
```

## Entorno de Python

Un solo entorno para el análisis de datos, los notebooks y los videos de sustentación (hechos con [Manim Community](https://www.manim.community/)). Usa Python 3.12 y las mismas versiones de todas las librerías sin importar la herramienta con la que se instale.

Incluye: numpy, pandas, scipy, statsmodels, scikit-learn, matplotlib, seaborn, ydata-profiling, Levenshtein, pyarrow (archivos parquet), JupyterLab, manim y lo necesario para narrar los videos (manim-voiceover y el cliente de Gemini).

### Instalación

Elija **una** de las tres opciones.

**Opción A: uv (recomendada).** [uv](https://docs.astral.sh/uv/) descarga Python 3.12 si hace falta y crea el entorno en `.venv/`.

```bash
uv sync
uv run jupyter lab
```

**Opción B: conda.** Funciona con conda, mamba o micromamba. Es la opción con menos requisitos del sistema, porque trae precompiladas las librerías gráficas de manim.

```bash
conda env create -f environment.yml
conda activate proyecto-mine
jupyter lab
```

**Opción C: pip.** Requiere tener Python 3.12 instalado.

```bash
python3.12 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter lab
```

### Requisitos del sistema según la plataforma

Con conda no hay que instalar nada más. Con uv o pip, algunas dependencias de manim no se publican precompiladas para todas las plataformas y se compilan al instalar:

| Plataforma | Con uv o pip hay que instalar antes |
| --- | --- |
| Windows x64 (Intel/AMD) | Nada |
| macOS Apple Silicon | `xcode-select --install` y `brew install cairo pkg-config` |
| macOS Intel | Lo mismo que Apple Silicon; compila más paquetes y tarda más. Se recomienda conda |
| Linux x64, Debian/Ubuntu | `sudo apt install build-essential pkg-config python3-dev libcairo2-dev libpango1.0-dev` |
| Linux x64, Fedora | `sudo dnf install gcc gcc-c++ pkgconf-pkg-config python3-devel cairo-devel pango-devel` |
| Linux ARM64 | Use conda. Además necesita un compilador de C++ para una dependencia (`phik`) |
| Windows ARM | Use la versión x64 de Python o de Miniforge, que corre emulada. Varias dependencias no tienen versión nativa para ARM |

El entorno se verificó con las tres opciones en Linux x64. Lo indicado para las demás plataformas sale de los binarios que publican PyPI y conda-forge para las versiones fijadas.

Para escribir fórmulas en los videos (`Tex`, `MathTex`) manim necesita además una instalación de LaTeX: MiKTeX en Windows, MacTeX en macOS o TeX Live en Linux. No se necesita instalar ffmpeg.

### Verificación

Con el entorno activado (con uv, anteponga `uv run` a cada comando):

```bash
python -c "import pandas, sklearn, seaborn, ydata_profiling, manim; print('ok')"
manim checkhealth
```

En VS Code, seleccione el intérprete del entorno (`.venv` o `proyecto-mine`) para los notebooks.

### Agregar o actualizar dependencias

Las dependencias se declaran en [pyproject.toml](pyproject.toml) y las versiones exactas quedan en `uv.lock`. [requirements.txt](requirements.txt) se genera a partir de ese archivo y no se edita a mano.

```bash
uv add <paquete>
uv export --format requirements-txt --no-hashes --no-emit-project -o requirements.txt
```

Si cambia la versión de `pycairo`, `manimpango`, `moderngl`, `glcontext` o `argon2-cffi-bindings` en `requirements.txt`, actualice la misma versión en [environment.yml](environment.yml). Suba juntos `pyproject.toml`, `uv.lock`, `requirements.txt` y `environment.yml`.
