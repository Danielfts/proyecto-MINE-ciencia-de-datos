# Producto de datos

Herramienta de apoyo a la decisión para Multiaservi Consultores: compara escenarios de tarifas y límites del impuesto predial unificado (IPU) 2027 de un municipio colombiano y estima el recaudo esperado de cada uno. Implementa los cuatro componentes definidos en la sección 2 del [reporte de la primera entrega](../../entrega-1/reporte/reporte.pdf): motor determinista, modelo de ML, API REST (FastAPI) y aplicación web (Dash).

Todas las salidas de escenarios son **estrictamente agregadas** (sin exponer datos personales, predios individuales ni el nombre del municipio). La segunda pestaña permite probar un **perfil de predio hipotético** de forma ilustrativa.

| Archivo | Componente | Función |
| --- | --- | --- |
| [preparacion.py](preparacion.py) | Carga y preparación autocontenida | Replica las transformaciones del notebook 08 sobre `predios.parquet` (18 802 predios privados facturados) y prepara perfiles sintéticos para inferencia |
| [motor.py](motor.py) | Motor determinista de escenarios | Aplica tarifas por destino/avalúo y límites de crecimiento, calcula KPI 1, KPI 2, meta de recaudo, guardrails (legalidad, progresividad, vivienda de menor avalúo), agregados para gráficas, lectura en lenguaje llano y exportación congelada en HTML |
| [modelo.py](modelo.py) | Cargador desacoplado de ML | Carga cualquier `Pipeline` de scikit-learn (`predict_proba`) desde `artefactos/modelo.joblib` (o `MODELO_PATH`), estima probabilidades de pago y recaudo esperado con rango conservador |
| [entrenar_arbol.py](entrenar_arbol.py) | Entrenamiento del modelo provisional | Entrena y exporta el árbol de decisión (`max_depth=8`, `min_samples_leaf=300`) a `artefactos/modelo.joblib` usando la partición por dueño grande del notebook 09 |
| [api.py](api.py) | API REST (FastAPI) | Expone `/salud`, `/escenarios/predefinidos`, `/escenarios/simular`, `/escenarios/comparar`, `/escenarios/exportar`, `/hipotetico/simular` y `/modelo/recargar` |
| [app.py](app.py) | Aplicación web (Dash) | Interfaz en identidad Uniandes con las 5 zonas del wireframe + pestaña de perfil hipotético (determinista + ML) + descarga de escenario congelado |
| `artefactos/` | `modelo.joblib` y `modelo.meta.json` | No se suben al repositorio (entrenados con datos del municipio) |

## Cómo cambiar de modelo de ML sin tocar código

El producto está desacoplado del algoritmo: basta guardar cualquier `Pipeline` de scikit-learn entrenado sobre las 25 características de `preparacion.CARACTERISTICAS` (por ejemplo, el mejor modelo elegido en el [notebook 10](../notebooks/10-construccion-y-evaluacion-del-modelo.ipynb): regresión logística, árbol de decisión, *gradient boosting* o modelo calibrado) en `entrega-2/producto/artefactos/modelo.joblib` —o apuntar la variable `MODELO_PATH` al nuevo `.joblib`— y pulsar **Recargar modelo** en la interfaz (o enviar `POST /modelo/recargar`).

La API detecta automáticamente el tipo de estimador del pipeline y actualiza el recaudo esperado en toda la aplicación.

## Cómo se ejecuta localmente

Desde la raíz del repositorio, con el entorno del proyecto (`uv sync`) y `datos/predios/predios.parquet` ubicado localmente:

1. **Generar el modelo provisional (si aún no existe `artefactos/modelo.joblib`):**

```bash
uv run python entrega-2/producto/entrenar_arbol.py
```

2. **Levantar la API y la aplicación web (en dos terminales):**

```bash
uv run uvicorn api:app --app-dir entrega-2/producto --reload   # API en http://127.0.0.1:8000 (docs en /docs)
uv run python entrega-2/producto/app.py                        # aplicación en http://127.0.0.1:8050
```

## Variables de entorno (preparado para Docker)

Toda la lógica del producto vive dentro de `entrega-2/producto/` sin depender de los notebooks, para facilitar el despliegue en contenedores privados (montando `predios.parquet` y `artefactos/` como volúmenes locales de solo lectura):

| Variable | Servicio | Valor por defecto | Uso |
| --- | --- | --- | --- |
| `PREDIOS_PATH` | `api.py` | `datos/predios/predios.parquet` | Ruta al archivo parquet dentro del contenedor |
| `MODELO_PATH` | `api.py` | `entrega-2/producto/artefactos/modelo.joblib` | Ruta al pipeline `.joblib` activo |
| `API_URL` | `app.py` | `http://127.0.0.1:8000` | URL interna de FastAPI (ej. `http://api:8000` en Docker Compose) |
| `HOST` | `app.py` | `127.0.0.1` | Usar `0.0.0.0` dentro de Docker |
| `PORT` | `app.py` | `8050` | Puerto de la aplicación Dash |

## Arquitectura

El diagrama está en [../diagramas/arquitectura.mmd](../diagramas/arquitectura.mmd) (Mermaid).

## Identidad visual

La aplicación y las exportaciones congeladas siguen [identidad/README.md](../../identidad/README.md): blanco, negro y amarillo (`#FFFF00`) como acento, nunca texto blanco sobre amarillo, y tipografía Arial o sin serifas equivalente.
