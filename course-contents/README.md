# Material de referencia del curso

Esta carpeta guarda el material del curso MINE-4101 que usamos como referencia para fundamentar el trabajo del proyecto. Su contenido **no se versiona**: todo lo que hay aquí, salvo este README, está en el `.gitignore` del repositorio. Cada integrante debe copiar el material en su copia local.

## Contenido esperado

### Documentos del curso

| Archivo | Contenido |
| --- | --- |
| `Programa MINE4101 202620.pdf` | Programa del curso |
| `Cronograma MINE4101 202620.pdf` | Cronograma del semestre |

### Diapositivas

En el orden del cronograma. Por ahora cubren las clases 1 a 6; las diapositivas de las clases siguientes (machine learning, interpretabilidad, despliegue, etc.) deben agregarse aquí a medida que se publiquen.

| Archivo | Clase | Temas | Tutorial asociado |
| --- | --- | --- | --- |
| `introduccion_curso.pdf` (7 diapositivas) | 1 | Plan de temas, evaluación, reglas de entrega de talleres y del proyecto final, herramientas de trabajo | — |
| `fundamentos_ciencia_datos.pdf` (18) | 1 | Qué es y qué no es la ciencia de datos; partir de una pregunta de negocio; tipos de tareas (descriptiva, diagnóstica, predictiva, prescriptiva); casos de uso; habilidades; perspectiva de negocio (costos vs. ROI); fallas típicas (datos sesgados, fuga de información, métrica equivocada); ciclo de vida y roles | — |
| `productos_datos_valor.pdf` (25) | 2 | Qué es un producto de datos y su anatomía (inputs, lógica, interfaz, operación, resultados); producto de datos vs. software tradicional; modelo operativo; Design Thinking, Agile, CRISP-DM, ASUM-DM y MLOps; creación y medición de valor (KPIs vs. métricas de modelo, guardrails, uplift y pensamiento causal, model-first bias) | — |
| `eda.pdf` (71) | 3 y 4 | Objetivos del EDA e insights; tipos de variables; EDA univariado no gráfico (frecuencias, tendencia central, dispersión, posición, forma, atípicos); EDA multivariado no gráfico (tablas cruzadas, correlación, regresión lineal, PCA); visualización (marcas y canales, expresividad y efectividad, tipos de gráficas, mapas, storytelling); reducción de dimensionalidad (PCA, t-SNE, UMAP) | Tutorial 1: `data-analysis-tutorial/` |
| `calidad_limpieza_datos.pdf` (24) | 5 | Dimensiones de calidad (completitud, consistencia, conformidad, relevancia, precisión, procesabilidad, disponibilidad, temporalidad, credibilidad); taxonomía de problemas (atributo, registro, columna, tabla, múltiples tablas); técnicas de limpieza (diccionarios, similitud, duplicados, expresiones regulares, imputación de faltantes) | Tutorial 2: `data-quality-tutorial/` |
| `estadistica_inferencial.pdf` (22) | 6 | Población vs. muestra; error estándar; intervalos de confianza; hipótesis nula y alternativa, nivel de significancia y p-value; pasos de una prueba; significancia estadística vs. práctica; pruebas comunes (t-test, z-test, ANOVA, chi-cuadrado, correlación) | Tutorial 3: `hypothesis-testing-tutorial-master/` |

#### Relación con el proyecto

| Actividad del proyecto (ver [TODO.md](../TODO.md)) | Diapositivas de apoyo |
| --- | --- |
| 1. Problemática y entendimiento del negocio | `fundamentos_ciencia_datos.pdf`, `productos_datos_valor.pdf` (KPIs y medición de valor) |
| 2. Ideación | `productos_datos_valor.pdf` (anatomía del producto, Design Thinking) |
| 4. Enfoque analítico | `estadistica_inferencial.pdf`, `eda.pdf`, `productos_datos_valor.pdf` (métricas de modelo vs. de negocio) |
| 5. Recolección de datos | `calidad_limpieza_datos.pdf` |
| 6. Entendimiento de los datos | `eda.pdf`, `calidad_limpieza_datos.pdf` |
| 8. Preparación de datos | `calidad_limpieza_datos.pdf` (técnicas de limpieza e imputación) |
| Metodología ASUM-DM y formato de entrega | `productos_datos_valor.pdf`, `introduccion_curso.pdf` |

### Tutoriales

Notebooks de los tutoriales del curso, con sus datasets en las carpetas `data/`. Se obtienen de la organización [datascience-uniandes](https://github.com/datascience-uniandes) en GitHub.

| Carpeta | Repositorio de origen | Notebooks | Datasets |
| --- | --- | --- | --- |
| `data-analysis-tutorial/` | [data-analysis-tutorial](https://github.com/datascience-uniandes/data-analysis-tutorial) | `airbnb/eda.ipynb`, `fifa/eda.ipynb`, `fifa/dim-reduction.ipynb` | `airbnb/data/listings.csv.gz`, `fifa/data/fifa.csv`, `fifa/data/fifa_clean.csv` |
| `data-quality-tutorial/` | [data-quality-tutorial](https://github.com/datascience-uniandes/data-quality-tutorial) | `data-quality-tutorial.ipynb` | `data/homicides.csv` |
| `hypothesis-testing-tutorial-master/` | [hypothesis-testing-tutorial](https://github.com/datascience-uniandes/hypothesis-testing-tutorial) | `hypothesis-testing.ipynb`, `business-case.ipynb` | `data/listings.csv.gz`, `data/titanic.csv` |

Al copiar un tutorial clonado, elimine su carpeta `.git` para no dejar repositorios anidados dentro de este.

### Lecturas

Lecturas citadas en el programa, el cronograma y las diapositivas. La numeración [n] es la del programa; los capítulos son los que el cronograma recomienda para cada clase. Los PDF de acceso abierto se guardan en `lecturas/` (no versionada, como el resto de esta carpeta).

#### Acceso abierto, guardadas en `lecturas/`

| Archivo | Referencia | Dónde se cita | Fuente y licencia |
| --- | --- | --- | --- |
| `zech-2018-pneumonia-generalization-plos-med.pdf` | Zech et al. "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs". *PLOS Medicine*, 2018 | `fundamentos_ciencia_datos.pdf` (fuga de información) | [PMC6219764](https://pmc.ncbi.nlm.nih.gov/articles/PMC6219764/), acceso abierto |
| `ghosh-2018-eda-tools-tabular-industrial-visual-informatics.pdf` | Ghosh et al. "A comprehensive review of tools for exploratory analysis of tabular industrial datasets". *Visual Informatics* 2(4), 2018 | `eda.pdf` | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2468502X18300561), acceso abierto con licencia Creative Commons |
| `comision-europea-open-data-metadata-quality-modulo-2.2.pdf` | Comisión Europea (Open Data Support). *Open Data & Metadata Quality*, módulo de formación 2.2 | `calidad_limpieza_datos.pdf` | [Interoperable Europe](https://interoperable-europe.ec.europa.eu/sites/default/files/document/2014-02/D3.1.7%20Training%20Module%202.2%20Open%20Data%20Quality_EUI_v0.04.pdf). Las diapositivas la fechan en 2012; este PDF es la versión de 2014 con el mismo título |

#### Libros gratuitos en línea (solo en HTML)

| Referencia | Capítulos del cronograma | Dónde leerlo |
| --- | --- | --- |
| [2] Lau, Gonzalez y Nolan. *Learning Data Science*. O'Reilly, 2023 | Clase 1: cap. 1 | [textbook.ds100.org](https://www.textbook.ds100.org/intro), licencia CC BY-NC-ND 4.0 |
| [12] Molnar. *Interpretable Machine Learning*, 2.ª ed., 2022 | Clase 12: cap. 3-9, 13-18 | [christophm.github.io/interpretable-ml-book](https://christophm.github.io/interpretable-ml-book/), licencia CC BY-NC-SA 4.0. Hoy publica la 3.ª edición, así que la numeración de capítulos puede no coincidir con la del cronograma; el PDF se vende en Leanpub |

#### Hay que conseguirlas por cuenta propia

Libros comerciales. El programa indica que están en la biblioteca de la Universidad (los de O'Reilly, normalmente por la plataforma O'Reilly Learning a la que da acceso la biblioteca).

| Referencia | Capítulos del cronograma |
| --- | --- |
| [1] O'Neil y Schutt. *Doing Data Science*. O'Reilly, 2013 | Clase 1: cap. 1 |
| [3] Vaughan. *Data Science: The Hard Parts*. O'Reilly, 2023 | Clase 2: cap. 1, 2, 6, 14. Clase 4: cap. 7, 8 |
| [4] Provost y Fawcett. *Data Science for Business*. O'Reilly, 2013 | Clase 2: cap. 1, 2, 11, 13. Clase 9: cap. 7. Clase 10: cap. 3. Clase 11: cap. 8 |
| [5] Bruce, Bruce y Gedeck. *Practical Statistics for Data Scientists*, 2.ª ed. O'Reilly, 2020 | Clase 3: cap. 1. Clase 6: cap. 2, 3. Clase 11: cap. 3-5 |
| [6] 365 Careers. *Statistics for Data Science and Business Analysis*. O'Reilly, 2021 (curso en video) | Clase 3: cap. 2. Clase 6: cap. 3-5 |
| [7] Nussbaumer Knaflic. *Storytelling with Data*. Wiley, 2015 | Clase 4: cap. 8, 9 |
| [8] Moses, Gavish y Vorwerck. *Data Quality Fundamentals*. O'Reilly, 2022 | Clase 5: cap. 1, 3 |
| [9] McGregor. *Practical Python Data Wrangling and Data Quality*. O'Reilly, 2021 | Clase 5: cap. 3, 6 |
| [10] George. *Practical Data Science with Python*. Packt, 2021 (en O'Reilly Learning) | Clase 2: cap. 1. Clase 3: cap. 4, 5. Clase 6: cap. 8, 9 |
| [11] Géron. *Hands-On Machine Learning*. O'Reilly | Clase 9: cap. 2-6. Clase 10: cap. 7, 8. El programa cita la 3.ª ed. (Scikit-Learn, Keras y TensorFlow, 2022) y el cronograma la edición con Scikit-Learn y PyTorch (2025); conviene confirmar con los profesores a cuál corresponden los capítulos |
| [13] Huyen. *AI Engineering*. O'Reilly, 2025 | Clase 13: cap. 1, 4-6 |
| [14] Huyen. *Designing Machine Learning Systems*. O'Reilly, 2022 | Clase 14: cap. 7-9 |
| [15] Haviv. *Implementing MLOps in the Enterprise*. O'Reilly, 2023 | Clase 14: cap. 1-7 |
| [16] Nielsen. *Practical Fairness*. O'Reilly, 2020 | Clase 15: cap. 1, 2, 7-11 |

Referencias de las diapositivas sin copia abierta:

| Referencia | Dónde se cita | Situación |
| --- | --- | --- |
| Obermeyer et al. "Dissecting racial bias in an algorithm used to manage the health of populations". *Science* 366, 2019 | `fundamentos_ciencia_datos.pdf` (métrica equivocada) | De pago en *Science*; consultarlo por la biblioteca |
| Galhardas, H. *Data Cleaning*, 2004 | `calidad_limpieza_datos.pdf` | No se pudo identificar el documento exacto; preguntar a los profesores |
| Murali, T. *Data Quality - Proven Approaches to Data Quality*, 2005 | `calidad_limpieza_datos.pdf` | No se pudo identificar el documento exacto; preguntar a los profesores |

#### Enlaces web citados en las diapositivas

Páginas de acceso libre; no se descargan.

- `fundamentos_ciencia_datos.pdf`: [flujo de trabajo de ciencia de datos (Business Science)](https://www.business-science.io/business/2019/06/27/data-science-workflow.html)
- `productos_datos_valor.pdf`: [The data product lifecycle (Data Minded)](https://medium.com/datamindedbe/the-data-product-lifecycle-4903c9752527), [ciclo de vida del software (Datarob)](https://datarob.com/essentials-software-development-life-cycle/), [modelo de madurez de MLOps (Microsoft)](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model), [Evaluating uplift models (Towards Data Science)](https://towardsdatascience.com/evaluating-uplift-models-8a078996a113/), [introducción a visualización (John Guerra)](https://johnguerra.co/lectures/information_visualization_spring2021/01_Introduction/)
- `eda.pdf`: [Data Viz Project](https://datavizproject.com/), [Understanding UMAP (PAIR)](https://pair-code.github.io/understanding-umap/), [PCA explicado visualmente (Towards Data Science)](https://towardsdatascience.com/principal-component-analysis-pca-explained-visually-with-zero-math-1cbf392b9e7d), [PCA vs. t-SNE vs. UMAP (Towards Data Science)](https://towardsdatascience.com/dimensionality-reduction-for-data-visualization-pca-vs-tsne-vs-umap-be4aa7b1cb29), [regresión lineal múltiple y visualización (aegis4048)](https://aegis4048.github.io/mutiple_linear_regression_and_visualization_in_python), [economía circular (DANE)](https://www.dane.gov.co/index.php/estadisticas-por-tema/ambientales/economia-circular), [resultados primera vuelta 2026 (John Guerra)](https://johnguerra.co/viz/resultadosPrimeraVuelta2026/?lang=es)
