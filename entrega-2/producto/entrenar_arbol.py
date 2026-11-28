"""Entrena y guarda el árbol de decisión inicial en `artefactos/modelo.joblib`.

Sigue exactamente el preprocesamiento del notebook 08, la partición por dueño
grande del notebook 09 y los mejores hiperparámetros del árbol de decisión del
notebook 10 (`max_depth=8`, `min_samples_leaf=300`, sin pesos balanceados).

Cuando el notebook 10 elija el modelo definitivo y lo guarde en
`entrega-2/producto/artefactos/modelo.joblib`, la API y la aplicación web lo
tomarán automáticamente sin cambiar código.

Uso desde la raíz del repositorio:

    uv run python entrega-2/producto/entrenar_arbol.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import f1_score, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

import modelo as mod
import preparacion as prep

PROPORCIONES = {"entrenamiento": 0.70, "validación": 0.15, "prueba": 0.15}


def _particion_por_grupos(
    grupo: pd.Series, estrato: pd.Series, semilla: int, intentos: int = 200
) -> pd.Series:
    grupo = pd.Series(grupo).reset_index(drop=True)
    estrato = pd.Series(estrato).reset_index(drop=True)
    rng = np.random.default_rng(semilla)
    tam = grupo.map(grupo.value_counts())
    multiple = (tam > 1).to_numpy()
    total = estrato.value_counts()
    nombres = list(PROPORCIONES)
    cortes = np.cumsum([PROPORCIONES["prueba"], PROPORCIONES["validación"]])
    tam_grupos = grupo[multiple].value_counts()

    mejor = None
    for _ in range(intentos):
        orden = rng.permutation(tam_grupos.index.to_numpy())
        acumulado = tam_grupos.reindex(orden).cumsum() / multiple.sum()
        asignacion = pd.Series(
            np.where(
                acumulado <= cortes[0],
                "prueba",
                np.where(acumulado <= cortes[1], "validación", "entrenamiento"),
            ),
            index=orden,
        )
        sub = grupo.map(asignacion).where(multiple)
        for est in total.index:
            libres = rng.permutation(np.flatnonzero(~multiple & (estrato == est).to_numpy()))
            ya = (
                sub[(estrato == est) & sub.notna()]
                .value_counts()
                .reindex(nombres, fill_value=0)
            )
            falta = (pd.Series(PROPORCIONES) * total[est] - ya).clip(lower=0)
            falta = (
                falta / falta.sum() * len(libres)
                if falta.sum() > 0
                else pd.Series(PROPORCIONES) * len(libres)
            )
            cuotas = np.floor(falta).astype(int)
            for k in np.argsort(-(falta - cuotas).to_numpy())[: len(libres) - cuotas.sum()]:
                cuotas.iloc[k] += 1
            inicio = 0
            for nombre in nombres:
                sub.iloc[libres[inicio : inicio + cuotas[nombre]]] = nombre
                inicio += cuotas[nombre]
        desvio_estratos = max(
            (
                estrato[sub == s]
                .value_counts(normalize=True)
                .reindex(total.index, fill_value=0)
                - total / len(estrato)
            )
            .abs()
            .max()
            for s in nombres
        )
        desvio_tamanos = max(abs((sub == s).mean() - PROPORCIONES[s]) for s in nombres)
        if mejor is None or desvio_estratos + desvio_tamanos < mejor[0]:
            mejor = (desvio_estratos + desvio_tamanos, sub.copy())
    return mejor[1]


def crear_pipeline_arbol(
    max_depth: int = 8,
    min_samples_leaf: int = 300,
    min_frecuencia: int = 30,
    semilla: int = prep.SEMILLA,
) -> Pipeline:
    preprocesador = ColumnTransformer(
        [
            (
                "numericas",
                Pipeline([("imputacion", SimpleImputer(strategy="median", add_indicator=True))]),
                prep.NUMERICAS,
            ),
            (
                "categoricas",
                OneHotEncoder(
                    handle_unknown="infrequent_if_exist",
                    min_frequency=min_frecuencia,
                    sparse_output=False,
                ),
                prep.CATEGORICAS,
            ),
            ("binarias", "passthrough", prep.BINARIAS),
        ],
        verbose_feature_names_out=True,
    )
    return Pipeline(
        [
            ("preprocesamiento", preprocesador),
            (
                "modelo",
                DecisionTreeClassifier(
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                    class_weight=None,
                    random_state=semilla,
                ),
            ),
        ]
    )


def main() -> None:
    datos = prep.cargar_y_preparar_predios()
    estrato = (
        datos[prep.GRUPO]
        + " · "
        + datos[prep.OBJETIVO].map({1: "pagó 2026", 0: "no pagó 2026"})
        + " · "
        + datos["condicion_predio"]
    )
    subconjunto = _particion_por_grupos(datos[prep.GRUPO_PARTICION], estrato, prep.SEMILLA)

    ent = datos[subconjunto == "entrenamiento"]
    val = datos[subconjunto == "validación"]

    pipeline = crear_pipeline_arbol()
    pipeline.fit(ent[prep.CARACTERISTICAS], ent[prep.OBJETIVO])

    p_val = pipeline.predict_proba(val[prep.CARACTERISTICAS])[:, 1]
    y_val = val[prep.OBJETIVO].to_numpy()
    metricas_val = {
        "roc_auc": round(float(roc_auc_score(y_val, p_val)), 4),
        "log_loss": round(float(log_loss(y_val, p_val, labels=[0, 1])), 4),
        "f1_no_paga_05": round(float(f1_score(y_val, (p_val >= 0.5).astype(int), pos_label=0)), 4),
        "n_entrenamiento": int(len(ent)),
        "n_validacion": int(len(val)),
        "n_hojas": int(pipeline.named_steps["modelo"].get_n_leaves()),
        "profundidad": int(pipeline.named_steps["modelo"].get_depth()),
    }

    destino = mod.ruta_modelo()
    destino.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, destino)

    meta = {
        "nombre": "Árbol de decisión (provisional)",
        "clase": "DecisionTreeClassifier",
        "version": "arbol-d8-leaf300",
        "umbral_defecto": 0.5,
        "entrenado_utc": datetime.now(timezone.utc).isoformat(),
        "metricas_validacion": metricas_val,
    }
    mod.ruta_metadatos(destino).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Modelo guardado en {destino}")
    print(f"Métricas en validación (partición por dueño): {metricas_val}")


if __name__ == "__main__":
    main()
