"""Modelo de probabilidad de pago y recaudo esperado (interfaz desacoplada).

Carga cualquier Pipeline compatible con scikit-learn (`predict_proba`) guardado en
`artefactos/modelo.joblib` (o en la ruta definida por `MODELO_PATH`). Para cambiar
del árbol de decisión a otro modelo (regresión logística, gradient boosting o un
modelo calibrado), basta reemplazar el archivo `.joblib` y llamar a `/modelo/recargar`
o reiniciar la API: no hace falta modificar `api.py` ni `app.py`.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

import preparacion as prep

CARPETA_ARTEFACTOS = Path(__file__).resolve().parent / "artefactos"
ARCHIVO_MODELO_POR_DEFECTO = CARPETA_ARTEFACTOS / "modelo.joblib"

_NOMBRES_AMIGABLES = {
    "DecisionTreeClassifier": "Árbol de decisión",
    "LogisticRegression": "Regresión logística",
    "HistGradientBoostingClassifier": "Gradient Boosting",
    "GradientBoostingClassifier": "Gradient Boosting",
    "RandomForestClassifier": "Bosque aleatorio",
    "CalibratedClassifierCV": "Modelo calibrado",
}


def ruta_modelo() -> Path:
    """Ruta al archivo del modelo (configurable con la variable MODELO_PATH)."""
    env = os.environ.get("MODELO_PATH")
    return Path(env) if env else ARCHIVO_MODELO_POR_DEFECTO


def ruta_metadatos(archivo_modelo: Path | None = None) -> Path:
    modelo_path = archivo_modelo or ruta_modelo()
    return modelo_path.with_suffix(".meta.json")


def disponible(archivo_modelo: Path | None = None) -> bool:
    return (archivo_modelo or ruta_modelo()).exists()


def _extraer_estimador(objeto: Any) -> Any:
    """Obtiene el clasificador final de un Pipeline o devuelve el objeto tal cual."""
    if isinstance(objeto, dict) and "pipeline" in objeto:
        objeto = objeto["pipeline"]
    if hasattr(objeto, "steps") and objeto.steps:
        return objeto.steps[-1][1]
    return objeto


def _describir_pipeline(pipeline: Any, archivo: Path) -> dict[str, Any]:
    estimador = _extraer_estimador(pipeline)
    clase = estimador.__class__.__name__
    nombre = _NOMBRES_AMIGABLES.get(clase, clase)
    fecha_archivo = datetime.fromtimestamp(archivo.stat().st_mtime, tz=timezone.utc).isoformat()

    info: dict[str, Any] = {
        "nombre": nombre,
        "clase": clase,
        "archivo": archivo.name,
        "actualizado_utc": fecha_archivo,
        "umbral_defecto": 0.5,
        "metricas_validacion": {},
    }

    # Si existe un archivo .meta.json más reciente o coetáneo, agrega sus metadatos
    meta_path = ruta_metadatos(archivo)
    if meta_path.exists() and meta_path.stat().st_mtime >= archivo.stat().st_mtime - 2:
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("clase") in (None, clase):
                info.update({k: v for k, v in meta.items() if v is not None})
        except (OSError, json.JSONDecodeError):
            pass

    if isinstance(pipeline, dict):
        for clave in ("nombre", "umbral_defecto", "metricas_validacion", "version"):
            if clave in pipeline:
                info[clave] = pipeline[clave]

    return info


class ModeloPago:
    """Envoltorio ligero sobre el pipeline de scikit-learn para inferencia uniforme."""

    def __init__(self, pipeline: Any, info: dict[str, Any]):
        self.pipeline = pipeline["pipeline"] if isinstance(pipeline, dict) else pipeline
        self.info = info

    def probabilidad_pago(self, predios: pd.DataFrame) -> np.ndarray:
        """Probabilidad estimada de que cada predio pague la vigencia."""
        X = predios[prep.CARACTERISTICAS]
        proba = self.pipeline.predict_proba(X)[:, 1]
        return np.clip(np.asarray(proba, dtype=float), 0.0, 1.0)

    def predecir_hipotetico(self, perfil: dict[str, Any]) -> dict[str, Any]:
        """Estima la probabilidad de pago para un perfil sintético de predio."""
        fila = prep.preparar_predio_hipotetico(perfil)
        prob = float(self.probabilidad_pago(fila)[0])
        umbral = float(self.info.get("umbral_defecto", 0.5))
        return {
            "probabilidad_pago": prob,
            "probabilidad_no_pago": 1.0 - prob,
            "umbral_referencia": umbral,
            "clase_orientativa": "Paga" if prob >= umbral else "No paga",
            "modelo_nombre": self.info.get("nombre", "Modelo de pago"),
            "modelo_clase": self.info.get("clase", ""),
        }


def cargar(archivo_modelo: Path | None = None) -> ModeloPago:
    """Carga el pipeline completo desde disco y construye su envoltorio."""
    archivo = archivo_modelo or ruta_modelo()
    if not archivo.exists():
        raise FileNotFoundError(
            f"Falta {archivo.name}: ejecute el notebook 10 o "
            "`uv run python entrega-2/producto/entrenar_arbol.py` para generarlo."
        )
    objeto = joblib.load(archivo)
    info = _describir_pipeline(objeto, archivo)
    return ModeloPago(objeto, info)


def probabilidad_pago(modelo: ModeloPago | Any, predios: pd.DataFrame) -> np.ndarray:
    """Compatibilidad directa: probabilidad de pago sobre una tabla de predios."""
    if isinstance(modelo, ModeloPago):
        return modelo.probabilidad_pago(predios)
    return np.clip(np.asarray(modelo.predict_proba(predios[prep.CARACTERISTICAS])[:, 1], dtype=float), 0.0, 1.0)


def recaudo_esperado(ipu: pd.Series | np.ndarray, probabilidad: pd.Series | np.ndarray) -> float:
    """R_esperado = suma de IPU_i · p_i (sección 4 del reporte)."""
    ipu_arr = np.asarray(ipu, dtype=float)
    prob_arr = np.asarray(probabilidad, dtype=float)
    return float(np.nansum(ipu_arr * prob_arr))


def intervalo_recaudo_esperado(
    ipu: pd.Series | np.ndarray,
    probabilidad: pd.Series | np.ndarray,
    margen_calibracion: float = 0.03,
) -> tuple[float, float]:
    """Rango conservador del recaudo esperado.

    Combina la desviación estándar binomial (Bernoulli independientes) con un
    margen de calibración (±3 puntos porcentuales en la probabilidad media),
    para comunicar que el recaudo esperado es una estimación con incertidumbre.
    """
    ipu_arr = np.nan_to_num(np.asarray(ipu, dtype=float), nan=0.0)
    p = np.clip(np.nan_to_num(np.asarray(probabilidad, dtype=float), nan=0.0), 0.0, 1.0)
    esperado = float(np.sum(ipu_arr * p))
    std_binomial = float(np.sqrt(np.sum((ipu_arr ** 2) * p * (1.0 - p))))
    bajo = float(np.sum(ipu_arr * np.clip(p - margen_calibracion, 0.0, 1.0)) - 1.96 * std_binomial)
    alto = float(np.sum(ipu_arr * np.clip(p + margen_calibracion, 0.0, 1.0)) + 1.96 * std_binomial)
    return max(0.0, min(bajo, esperado)), max(alto, esperado)
