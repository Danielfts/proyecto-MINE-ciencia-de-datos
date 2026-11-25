# Material de referencia del curso

Esta carpeta guarda el material del curso MINE-4101 que usamos como referencia para fundamentar el trabajo del proyecto. Su contenido **no se versiona**: todo lo que hay aquí, salvo este README, está en el `.gitignore` del repositorio. Cada integrante debe copiar el material en su copia local.

## Contenido esperado

Una copia de todo lo publicado en Bloque Neón, con la misma estructura de módulos y semanas de la sección *Contenido* y los nombres de archivo del LMS (copia consolidada el 23 de noviembre de 2026), más el clon del sitio de las prácticas y las lecturas de `lecturas/`. Cada material está una sola vez.

| Carpeta | Material | Enlaces del LMS |
| --- | --- | --- |
| `Generalidades/` | Programa y cronograma del curso | |
| `Módulo 0. Introducción/Semana 1/` | Introducción al curso; Fundamentos de la Ciencia de Datos | |
| `Módulo 0. Introducción/Semana 2/` | Productos de datos, métodos y creación de valor | |
| `Módulo 1. Análisis y limpieza de datos/Semana 3/` | Análisis Exploratorio de Datos (EDA); Tutorial 1 | [data-analysis-tutorial](https://github.com/datascience-uniandes/data-analysis-tutorial/) |
| `Módulo 1. .../Semana 6/` | Calidad y limpieza de datos; Tutorial 2 | [data-quality-tutorial](https://github.com/datascience-uniandes/data-quality-tutorial) |
| `Módulo 1. .../Semana 7/` | Estadística inferencial; Tutorial 3 | [hypothesis-testing-tutorial](https://github.com/datascience-uniandes/hypothesis-testing-tutorial/) |
| `Módulo 2. Machine Learning y MLOps/Semana 9/` | Fundamentos de modelos comunes supervisados | Práctica 1 |
| `Módulo 2. .../Semana 10/` | Fundamentos de modelos comunes no supervisados | Práctica 3 |
| `Módulo 2. .../Semana 11/` | Métricas avanzadas y generación de valor | Práctica 4 |
| `Módulo 2. .../Semana 12/` | Interpretabilidad | |
| `Módulo 2. .../Semana 13/` | IA generativa en ciencia de datos | |
| `Módulo 2. .../Semana 14/` | Despliegue de modelos; tutorial de despliegue con FastAPI y Docker | [model-deployment-tutorial](https://github.com/datascience-uniandes/model-deployment-tutorial) |
| `Módulo 2. .../Semana 15/` | Atributos en ML | |
| `PracticasMachineLearning/` | Clon del sitio de las prácticas: las siete prácticas y sus guías (ver [Prácticas](#prácticas)) | [sitio de las prácticas](https://datascience-uniandes.github.io/PracticasMachineLearning) |
| `Talleres/`, `Parciales/` | Enunciados y datasets de los talleres y del primer parcial; simulacro del segundo | |
| `Proyecto final/` | Enunciado (el mismo `Proyecto Final.pdf` de la raíz) | |
| `Clases Virtuales/` y los `.html` de algunas semanas | Páginas del LMS con los enlaces a las grabaciones en Zoom | |
| `lecturas/` | Lecturas de acceso abierto (ver [Lecturas](#lecturas)) | |

Las semanas 4, 5 y 8 están vacías en el LMS. Los cuestionarios solo se consultan en Bloque Neón.

### Relación con el proyecto

| Actividad del proyecto (ver [TODO.md](../TODO.md)) | Material de apoyo |
| --- | --- |
| 1. Problemática y entendimiento del negocio | Fundamentos de la Ciencia de Datos; Productos de datos (KPIs y medición de valor) |
| 2. Ideación | Productos de datos (anatomía del producto, Design Thinking) |
| 4. Enfoque analítico | Estadística inferencial; EDA; Productos de datos (métricas de modelo frente a métricas de negocio); Métricas avanzadas y generación de valor |
| 5. Recolección de datos | Calidad y limpieza de datos |
| 6. Entendimiento de los datos | EDA; Calidad y limpieza de datos; tutoriales 1 a 3 |
| 8. Preparación de datos | Calidad y limpieza de datos (limpieza e imputación); Atributos en ML; práctica 2 (actividad 2, ingeniería de características); guías `pipeline`, `one-hot`, `estandarizar`, `escalar-variables`, `nulos`, `caracteristicas-derivadas` |
| 9. Estrategia de validación | Fundamentos de modelos supervisados; guías `division-datos`, `validacion-cruzada`, `seleccion-hiperparametros`, `gridsearchcv` |
| 10. Construcción y evaluación del modelo | Fundamentos de modelos supervisados; Métricas avanzadas y generación de valor; Interpretabilidad; práctica 2 (clasificación) y práctica 5 (interpretabilidad); guías `regresion-logistica`, `arbol-decision`, `gradient-boosting`, `curva-roc`, `matriz-confusion`, `comparar-metricas`, `impacto-negocio`, `shap` |
| 11. Producto de datos | Despliegue de modelos y su tutorial (FastAPI y Docker); práctica 6 (despliegue); guías `guardar-modelo`, `api-fastapi`, `docker`, `docker-compose` |
| 3. Aspectos éticos, 13. Conclusiones | Práctica 7 (justicia) y guía `justicia` |
| Metodología ASUM-DM y formato de entrega | Productos de datos; Introducción al curso |

### Prácticas

El sitio de prácticas del curso, [PracticasMachineLearning](https://datascience-uniandes.github.io/PracticasMachineLearning), es **la referencia principal de cómo hacer** la preparación de datos, la validación, los modelos y el despliegue de la entrega final. Su repositorio, [datascience-uniandes/PracticasMachineLearning](https://github.com/datascience-uniandes/PracticasMachineLearning), se clona en `PracticasMachineLearning/`, en esta carpeta, y se actualiza con `git -C course-contents/PracticasMachineLearning pull`:

```bash
git clone https://github.com/datascience-uniandes/PracticasMachineLearning.git course-contents/PracticasMachineLearning
```

A diferencia de los tutoriales, este clon conserva su carpeta `.git` para poder actualizarse; como toda la carpeta está en el `.gitignore`, git no lo ve. Es la única copia de las prácticas en esta carpeta: la que venía con el material del LMS, idéntica al clon, se quitó el 25 de noviembre de 2026. El LMS solo enlaza las prácticas 1, 3 y 4, pero el sitio tiene las siete:

| Práctica | Tema | Dónde |
| --- | --- | --- |
| 1 | Regresión lineal | `docs/talleres/practica-1/` |
| 2 | Clasificación (incluye ingeniería de características y ensambles) | `docs/talleres/practica-2/` |
| 3 | Agrupación | `docs/talleres/practica-3/` |
| 4 | Pruebas A/B | `docs/talleres/practica-4/` |
| 5 | Interpretabilidad | `docs/talleres/practica-5/` |
| 6 | Despliegue | `docs/talleres/practica-6/` |
| 7 | Justicia | `docs/talleres/practica-7/` |

`docs/ayudas/` tiene guías cortas con código (una por técnica o métrica: pipelines, validación cruzada, curvas, SHAP, FastAPI, Docker, entre otras), y `docs/datos/`, los datasets de las prácticas. El sitio se ve en el navegador o localmente con `mkdocs serve` (ver su README). Las rutas de la tabla y de [Relación con el proyecto](#relación-con-el-proyecto) son relativas a `PracticasMachineLearning/`; en línea, `docs/ayudas/pipeline.md` es `https://datascience-uniandes.github.io/PracticasMachineLearning/ayudas/pipeline/`.

### Tutoriales

Están dentro de la semana que los usa (tutoriales 1 a 3 en el módulo 1, el de despliegue en la semana 14). Son copias de los repositorios de la organización [datascience-uniandes](https://github.com/datascience-uniandes) en GitHub, con sus datasets en las carpetas `data/`. Al copiar un tutorial clonado, elimine su carpeta `.git` para no dejar repositorios anidados dentro de este.

### Lecturas

Lecturas citadas en el programa, el cronograma y las diapositivas. La numeración [n] es la del programa; los capítulos son los que el cronograma recomienda para cada clase. Los PDF de acceso abierto se guardan en `lecturas/` (no versionada, como el resto de esta carpeta).

#### Acceso abierto, guardadas en `lecturas/`

| Archivo | Referencia | Dónde se cita | Fuente y licencia |
| --- | --- | --- | --- |
| `zech-2018-pneumonia-generalization-plos-med.pdf` | Zech et al. "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs". *PLOS Medicine*, 2018 | *Fundamentos de la Ciencia de Datos* (fuga de información) | [PMC6219764](https://pmc.ncbi.nlm.nih.gov/articles/PMC6219764/), acceso abierto |
| `ghosh-2018-eda-tools-tabular-industrial-visual-informatics.pdf` | Ghosh et al. "A comprehensive review of tools for exploratory analysis of tabular industrial datasets". *Visual Informatics* 2(4), 2018 | *Análisis Exploratorio de Datos (EDA)* | [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2468502X18300561), acceso abierto con licencia Creative Commons |
| `comision-europea-open-data-metadata-quality-modulo-2.2.pdf` | Comisión Europea (Open Data Support). *Open Data & Metadata Quality*, módulo de formación 2.2 | *Calidad y limpieza de datos* | [Interoperable Europe](https://interoperable-europe.ec.europa.eu/sites/default/files/document/2014-02/D3.1.7%20Training%20Module%202.2%20Open%20Data%20Quality_EUI_v0.04.pdf). Las diapositivas la fechan en 2012; este PDF es la versión de 2014 con el mismo título |

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
| Obermeyer et al. "Dissecting racial bias in an algorithm used to manage the health of populations". *Science* 366, 2019 | *Fundamentos de la Ciencia de Datos* (métrica equivocada) | De pago en *Science*; consultarlo por la biblioteca |
| Galhardas, H. *Data Cleaning*, 2004 | *Calidad y limpieza de datos* | No se pudo identificar el documento exacto; preguntar a los profesores |
| Murali, T. *Data Quality - Proven Approaches to Data Quality*, 2005 | *Calidad y limpieza de datos* | No se pudo identificar el documento exacto; preguntar a los profesores |

#### Enlaces web citados en las diapositivas

Páginas de acceso libre; no se descargan.

- *Fundamentos de la Ciencia de Datos*: [flujo de trabajo de ciencia de datos (Business Science)](https://www.business-science.io/business/2019/06/27/data-science-workflow.html)
- *Productos de datos, métodos y creación de valor*: [The data product lifecycle (Data Minded)](https://medium.com/datamindedbe/the-data-product-lifecycle-4903c9752527), [ciclo de vida del software (Datarob)](https://datarob.com/essentials-software-development-life-cycle/), [modelo de madurez de MLOps (Microsoft)](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model), [Evaluating uplift models (Towards Data Science)](https://towardsdatascience.com/evaluating-uplift-models-8a078996a113/), [introducción a visualización (John Guerra)](https://johnguerra.co/lectures/information_visualization_spring2021/01_Introduction/)
- *Análisis Exploratorio de Datos (EDA)*: [Data Viz Project](https://datavizproject.com/), [Understanding UMAP (PAIR)](https://pair-code.github.io/understanding-umap/), [PCA explicado visualmente (Towards Data Science)](https://towardsdatascience.com/principal-component-analysis-pca-explained-visually-with-zero-math-1cbf392b9e7d), [PCA vs. t-SNE vs. UMAP (Towards Data Science)](https://towardsdatascience.com/dimensionality-reduction-for-data-visualization-pca-vs-tsne-vs-umap-be4aa7b1cb29), [regresión lineal múltiple y visualización (aegis4048)](https://aegis4048.github.io/mutiple_linear_regression_and_visualization_in_python), [economía circular (DANE)](https://www.dane.gov.co/index.php/estadisticas-por-tema/ambientales/economia-circular), [resultados primera vuelta 2026 (John Guerra)](https://johnguerra.co/viz/resultadosPrimeraVuelta2026/?lang=es)
