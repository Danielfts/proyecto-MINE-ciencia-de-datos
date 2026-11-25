"""Modelo de probabilidad de pago y recaudo esperado.

El modelo lo entrena y lo guarda el notebook 10
(entrega-2/notebooks/10-construccion-y-evaluacion-del-modelo.ipynb) en
artefactos/modelo.joblib, que no se sube al repositorio: está entrenado con los
datos del municipio.
"""

from pathlib import Path

import joblib

ARCHIVO_MODELO = Path(__file__).resolve().parent / "artefactos" / "modelo.joblib"


def disponible():
    return ARCHIVO_MODELO.exists()


def cargar():
    """El pipeline completo (transformaciones y clasificador) del mejor modelo."""
    if not disponible():
        raise FileNotFoundError(
            f"Falta {ARCHIVO_MODELO.name}: ejecute el notebook 10, que lo guarda en artefactos/"
        )
    return joblib.load(ARCHIVO_MODELO)


def probabilidad_pago(modelo, predios):
    """Probabilidad de que cada predio pague la vigencia."""
    return modelo.predict_proba(predios)[:, 1]


def recaudo_esperado(ipu, probabilidad):
    """R_esperado = suma de IPU_i · p_i (sección 4 del reporte)."""
    return float((ipu * probabilidad).sum())
