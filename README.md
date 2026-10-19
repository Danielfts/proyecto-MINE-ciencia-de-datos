# Proyecto Final — MINE-4101 Ciencia de Datos Aplicada

Proyecto final del curso MINE-4101: Ciencia de Datos Aplicada (semestre 2026-20), Universidad de los Andes.

## Integrantes

Estos son los nombres que deben aparecer en todas las entregas y artefactos del proyecto (reportes, diapositivas, videos y documentación):

- Daniel Felipe Triviño Santana
- Nicolas Bedoya Figueroa
- Joubert Daniel Álvarez

## Alcance

**Organización.** Multiaservi Consultores Ltda., firma de contabilidad pública y gestión tributaria territorial, asesora a la alcaldía de un municipio colombiano que acaba de terminar una actualización catastral. Los avalúos subieron de forma abrupta (en la mediana, cerca de cuatro veces entre 2025 y 2026), y aun con tarifas más bajas y límites transitorios al crecimiento del impuesto predial, en 2026 se facturó apenas la mitad del impuesto que corresponde a los nuevos avalúos.

**Problema.** Para la vigencia 2027, última en la que rigen esos límites, la alcaldía debe radicar ante el Concejo una política de tarifas y límites que acerque el impuesto a los nuevos avalúos sin choques excesivos, sin perder progresividad ni recaudo y con el menor costo político posible.

**Producto de datos.** Una herramienta de apoyo a la decisión para la consultora, que permite comparar escenarios de tarifas y límites. La decisión la toman personas; el producto no la automatiza. Componentes:

- un motor de escenarios determinista, que aplica tarifas y límites a cada predio;
- un modelo de *machine learning* que estima la probabilidad de que cada predio pague la vigencia y convierte el recaudo facturado en recaudo esperado;
- una API REST (FastAPI) y una aplicación web (Dash) para operarlos;
- una exportación congelada del escenario elegido, como insumo para la sustentación ante el Concejo.

**Indicadores.** Dos KPIs que se oponen a propósito: la convergencia del impuesto facturado hacia el pleno y el choque del aumento en los predios de mayor impuesto. Además, una meta de recaudo y dos guardrails: progresividad y legalidad.

**Datos.** El levantamiento catastral en el modelo LADM-COL y la facturación del impuesto predial 2025-2026. Contienen datos personales e identifican al municipio, así que no se publican: el repositorio documenta su estructura y cómo se construye el archivo de análisis.

**Fuera del alcance.** Los avalúos (el producto no los calcula ni los modifica), las PQR de los contribuyentes, el momento del pago, la cartera y sus intereses, y el recaudo diario.

**Entregas.** La primera entrega cubre las actividades 1 a 7: problemática, ideación, aspectos éticos, enfoque analítico, recolección y entendimiento de los datos. Los modelos y el producto se construyen para la entrega final.

## Conclusiones (insights)

De la primera entrega (sección 7 del [reporte](entrega-1/reporte/reporte.pdf) y etapa 8 del [notebook de entendimiento de los datos](entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb)):

1. **Los datos alcanzan para las dos preguntas del proyecto.** La facturación cubre el 87 % de los predios del levantamiento. Los problemas de calidad principales son valores de relleno y faltantes que dependen del régimen y de la visita; se marcan como faltantes y no impiden el análisis.
2. **El catastro anterior estaba desactualizado.** El 64 % de los predios individuales tiene alguna novedad en su número predial y el 10 % son predios nuevos.
3. **El avalúo depende casi solo del tamaño.** Con pocas variables se reproduce con un error relativo mediano de 13 %; la antigüedad y la altura aportan poco.
4. **El historial de pago es la señal más fuerte, pero no basta.** Pagó en 2026 el 80,3 % de quienes pagaron en 2025 y el 0,3 % de quienes no. Aun así, cerca del 20 % de quienes pagaron en 2025 no pagó en 2026, y de los predios sin registro en 2025 (sobre todo nuevos y desenglobes) pagó el 56 %: ahí está la incertidumbre que debe resolver el modelo.
5. **El impuesto se concentra en la cola.** El 1 % de los predios con mayor impuesto factura el 46,8 % del total y el 10 %, el 81,4 %. El choque que mide el KPI 2 recae en pocos predios, que pagan la mayor parte del impuesto.

**Próximas acciones:** validar el motor de escenarios reproduciendo el impuesto facturado en 2026 con las tarifas vigentes, confirmar con Hacienda la fecha de corte del pago y, en la entrega final, preparar los datos y separar entrenamiento, validación y prueba.

## Organización del repositorio

| Carpeta o archivo | Contenido |
| --- | --- |
| [entrega-1/](entrega-1/README.md) | Primera entrega: reporte ([PDF](entrega-1/reporte/reporte.pdf) y fuente en LaTeX), notebook de entendimiento de los datos, video de sustentación ([en YouTube](https://youtu.be/gj6foaegdeE)), guion y diapositivas |
| [datos/](datos/README.md) | Documentación de la base de datos catastral (modelo LADM-COL) que sirve de fuente al proyecto, y los modelos INTERLIS y el diccionario de datos de los que sale su estructura. En [datos/base-podada/](datos/base-podada/README.md): la versión reducida de la base que usa el proyecto, con su diagrama entidad-relación, su [diccionario de datos](datos/base-podada/diccionario-de-datos.md) y el script que la crea. En [datos/predios/](datos/predios/README.md): cómo convertir la base podada en un archivo parquet con un predio por fila y sin datos personales |
| [identidad/](identidad/README.md) | Identidad visual del proyecto (colores, tipografía y logo de la Universidad de los Andes) y el estilo de los reportes y de las gráficas |
| [herramientas_video/](herramientas_video/README.md) | Herramientas y flujo de trabajo para hacer los videos con manim y Gemini TTS |
| [course-contents/](course-contents/README.md) | Material de referencia del curso (no versionado; el README indica qué debe contener) |
| [Proyecto Final.pdf](Proyecto%20Final.pdf) | Enunciado del proyecto |
| [TODO.md](TODO.md) | Pendientes y fechas límite de cada entrega |
| [USO_DE_IA.md](USO_DE_IA.md) | Declaración de uso de IA |
| `pyproject.toml`, `uv.lock`, `requirements.txt`, `environment.yml` | Entorno de Python |

## Notebooks

Se ejecutan en este orden, con el [entorno de Python](#entorno-de-python) instalado. Leen el archivo `datos/predios/predios.parquet`, que no está en el repositorio porque identifica al municipio. Se descarga del [almacenamiento institucional de la Universidad](https://uniandes-my.sharepoint.com/:u:/r/personal/d_trivino_uniandes_edu_co/Documents/CollegeSemesters/2026_2/Ciencia%20de%20Datos/datasets/predios.parquet?d=w86352a73a04e416d8149f8782df4e840&csf=1&web=1&e=jxKQvW), con acceso restringido a cuentas autorizadas (si no tiene acceso, pídalo al equipo), o se construye a partir de la base podada y del Excel de facturación del impuesto predial, como indica [datos/predios/](datos/predios/README.md#cómo-se-construye).

| Orden | Notebook | Actividad | Estado |
| --- | --- | --- | --- |
| 1 | [entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb](entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb) | 6. Entendimiento de los datos | Completo: análisis, interpretaciones y conclusiones |

Se abren con JupyterLab (`uv run jupyter lab`) o con VS Code y se ejecutan de arriba abajo. También desde la terminal, en la raíz del repositorio:

```bash
uv run jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.record_timing=False entrega-1/notebooks/06-entendimiento-de-los-datos.ipynb
```

## Entorno de Python

Python 3.12. Los archivos del entorno están en la raíz del repositorio: [pyproject.toml](pyproject.toml) declara las dependencias, `uv.lock` fija sus versiones exactas para uv, [requirements.txt](requirements.txt) es para pip y [environment.yml](environment.yml) para conda.
