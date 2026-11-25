# Producto de datos

Herramienta de apoyo a la decisión para Multiaservi Consultores: compara escenarios de tarifas y límites del impuesto predial 2027 de un municipio colombiano y estima el recaudo esperado de cada uno. Los componentes son los de la sección 2 del [reporte de la primera entrega](../../entrega-1/reporte/reporte.pdf), y el enunciado pide al menos tres de cuatro: modelo de ML, API REST, aplicación web y dashboard.

**Estado:** andamiaje. La API y la aplicación arrancan y se comunican; el motor, el modelo y la exportación están por construir.

| Archivo | Componente | Estado |
| --- | --- | --- |
| [motor.py](motor.py) | Motor de escenarios determinista: aplica tarifas y límites a cada predio y calcula los indicadores | Forma del escenario definida; el cálculo está pendiente |
| [modelo.py](modelo.py) | Carga el mejor modelo del [notebook 10](../notebooks/10-construccion-y-evaluacion-del-modelo.ipynb) y calcula la probabilidad de pago y el recaudo esperado | Listo para usar el modelo cuando exista |
| [api.py](api.py) | API REST (FastAPI): `/salud`, `/escenarios/simular`, `/escenarios/exportar` | `/salud` funciona; las rutas de escenarios responden 501 |
| [app.py](app.py) | Aplicación web (Dash), con las cinco zonas del wireframe | Estructura y conexión con la API; el contenido está pendiente |
| `artefactos/` | `modelo.joblib`, que guarda el notebook 10 | No se sube al repositorio: está entrenado con los datos del municipio |

**Cómo hacerlo:** la [práctica 6: Despliegue](https://datascience-uniandes.github.io/PracticasMachineLearning/talleres/practica-6/) del curso y sus guías [guardar el modelo](https://datascience-uniandes.github.io/PracticasMachineLearning/ayudas/guardar-modelo/), [API con FastAPI](https://datascience-uniandes.github.io/PracticasMachineLearning/ayudas/api-fastapi/), [Docker](https://datascience-uniandes.github.io/PracticasMachineLearning/ayudas/docker/) y [Docker Compose](https://datascience-uniandes.github.io/PracticasMachineLearning/ayudas/docker-compose/) son la referencia para la API y el despliegue.

## Cómo se ejecuta

Desde la raíz del repositorio, con el entorno del proyecto (`uv sync`), en dos terminales:

```bash
uv run uvicorn api:app --app-dir entrega-2/producto --reload   # API en http://127.0.0.1:8000 (documentación en /docs)
uv run python entrega-2/producto/app.py                        # aplicación en http://127.0.0.1:8050
```

La aplicación busca la API en `http://127.0.0.1:8000`; otra dirección se indica con la variable `API_URL`. El motor necesita `datos/predios/predios.parquet` y el modelo necesita `artefactos/modelo.joblib`; ninguno está en el repositorio (ver el [README principal](../../README.md#notebooks)).

## Arquitectura

El borrador del diagrama está en [../diagramas/arquitectura.mmd](../diagramas/arquitectura.mmd) (Mermaid). Para dibujarlo como imagen hace falta [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli):

```bash
mmdc -i entrega-2/diagramas/arquitectura.mmd -o entrega-2/diagramas/arquitectura.png -w 1800 -b white
```

## Despliegue

Pendiente: el mecanismo de despliegue que pide el enunciado (actividad 11). El producto es de uso exclusivo de la consultora y trabaja con datos que no se publican, así que el despliegue debe mantener los datos y el modelo fuera de cualquier servicio público.

## Identidad visual

La aplicación usa los colores y la fuente de la [identidad visual](../../identidad/README.md): blanco, negro y amarillo como acento, nunca texto blanco sobre amarillo, y Arial o una fuente sin serifas equivalente.
