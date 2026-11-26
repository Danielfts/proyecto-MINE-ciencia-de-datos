"""Lo que comparten los notebooks de la entrega final (actividades 8, 9 y 10).

Rutas de los archivos que pasan de un notebook al siguiente, la semilla, las
columnas cuyos valores no se muestran y la configuración de tablas y gráficas.
Las funciones del análisis exploratorio están en utilidades_eda.py, en esta
carpeta (heredado de la primera entrega).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Raíz del repositorio: dos carpetas arriba de esta (entrega-2/notebooks/)
RAIZ = Path(__file__).resolve().parents[2]

# Semilla para todo lo que use azar: la misma de la primera entrega
SEMILLA = 4101

# Archivos que no están en el repositorio: identifican al municipio (*.parquet está
# en .gitignore). Cada notebook escribe el suyo y lo lee el siguiente.
ARCHIVO_PREDIOS = RAIZ / "datos" / "predios" / "predios.parquet"  # entrada (datos/predios/)
CARPETA_MODELADO = RAIZ / "datos" / "modelado"
ARCHIVO_PREPARADO = CARPETA_MODELADO / "predios_preparados.parquet"  # lo escribe el 08
ARCHIVO_PARTICION = CARPETA_MODELADO / "particion.parquet"  # lo escribe el 09
# El mejor modelo lo escribe el 10 y lo usa el producto (entrega-2/producto/).
# Tampoco se sube: está entrenado con los datos del municipio.
CARPETA_ARTEFACTOS = RAIZ / "entrega-2" / "producto" / "artefactos"
ARCHIVO_MODELO = CARPETA_ARTEFACTOS / "modelo.joblib"

# Columnas que identifican al municipio, pueden traer nombres o dicen cuánto pagó el
# dueño de un predio: sus valores no aparecen en ninguna salida. Es la misma lista de
# la etapa 2 del notebook 06; las variables derivadas de estas columnas (por ejemplo,
# la variable objetivo) se muestran solo agregadas.
COLUMNAS_RESERVADAS = [
    "departamento", "municipio", "numero_predial", "codigo_orip", "matricula_inmobiliaria",
    "codigo_homologado", "id_operacion", "ente_emisor",
    "nombre", "observaciones", "numero_fuente", "observacion_fuente",
    "manzana_vereda", "numero_terreno", "edificio", "piso", "unidad",
    "ipu_facturado_2026", "pago_2026", "pago_2025",
]

# Colores de la identidad visual (ver identidad/README.md)
AMARILLO, NEGRO, GRIS = "#FFFF00", "#000000", "#666666"
AZUL = "#2a78d6"  # segunda serie de la paleta, después del negro


def configurar():
    """Opciones de tablas y el estilo de las gráficas del proyecto."""
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 100)
    pd.options.display.float_format = "{:.2f}".format
    plt.style.use(RAIZ / "identidad" / "graficas.mplstyle")


def exigir(archivo, como_obtenerlo):
    """Detiene el notebook con un mensaje claro si falta un archivo de entrada."""
    if not archivo.exists():
        raise FileNotFoundError(f"Falta {archivo.relative_to(RAIZ)}: {como_obtenerlo}")
    return archivo


# --- Variables del modelo de pago (las define el notebook 08) -----------------------
# Variable objetivo: 1 si el predio pagó la vigencia 2026 a la fecha de extracción. Está
# en COLUMNAS_RESERVADAS: se muestra solo agregada.
OBJETIVO = "pago_2026"
# Clase de interés para la precisión, el recall y el F1: los predios que no pagan
# (pos_label=CLASE_NO_PAGA en las métricas de scikit-learn; ver la estrategia del notebook 09)
CLASE_NO_PAGA = 0
# Grupo del historial de 2025: estratifica la partición (09) y separa las métricas (10)
GRUPO = "historial_2025"
# Grupo de partición: los predios de un mismo dueño grande van juntos al mismo subconjunto
# (notebook 09). No es una característica.
GRUPO_PARTICION = "grupo_particion"

# Características: todas se conocen antes del pago de la vigencia 2026. El impuesto
# facturado (y la tarifa efectiva que sale de él) no entra: algunos valores exactos de la
# tarifa separan casi perfectamente a los que pagaron, lo que indica que el valor registrado
# depende del pago (ver la etapa 5 del notebook 08). Se usa solo para el recaudo esperado.
NUMERICAS = [
    "log_avaluo", "log_area_construida", "log_area_registral",
    "log_area_terreno", "n_unidades", "n_construcciones", "pisos_edificio", "anio_construccion",
    "n_titulares", "log_predios_mismo_titular", "tasa_2025_mismo_dueno", "tasa_2025_mismo_edificio",
]
CATEGORICAS = [
    "historial_2025", "novedad_numero_predial", "condicion_predio", "destinacion_economica",
    "zona", "resultado_visita", "tipo_derecho", "autoriza_notificaciones",
]
BINARIAS = ["visita_exitosa_efectiva", "avaluo_cero", "anio_sospechoso", "tiene_matricula",
            "titular_juridico"]
CARACTERISTICAS = NUMERICAS + CATEGORICAS + BINARIAS


def crear_preprocesador(escalar=True, min_frecuencia=30):
    """ColumnTransformer de las características del modelo de pago.

    - Numéricas: imputación con la mediana más una columna indicadora de cada faltante
      y, si `escalar`, estandarización (la necesita la regresión logística; a los árboles
      no les cambia nada).
    - Categóricas: one-hot, con las categorías de menos de `min_frecuencia` predios de
      entrenamiento agrupadas en una sola columna ("infrequent"). Una categoría que no se vio
      en entrenamiento va a esa columna si la variable la tiene, y si no, queda en ceros.
    - Binarias: pasan sin cambios (ya son 0 y 1).

    Todo lo que aprende de los datos (medianas, medias, desviaciones, categorías) se ajusta
    con `fit`, así que dentro del Pipeline del notebook 10 se ajusta solo con entrenamiento.
    """
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    pasos_numericas = [("imputacion", SimpleImputer(strategy="median", add_indicator=True))]
    if escalar:
        pasos_numericas.append(("estandarizacion", StandardScaler()))
    return ColumnTransformer([
        ("numericas", Pipeline(pasos_numericas), NUMERICAS),
        ("categoricas", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=min_frecuencia,
                                      sparse_output=False), CATEGORICAS),
        ("binarias", "passthrough", BINARIAS),
    ], verbose_feature_names_out=True)


# --- Partición por grupos (notebook 09) ----------------------------------------------
PROPORCIONES = {"entrenamiento": 0.70, "validación": 0.15, "prueba": 0.15}


def particion_por_grupos(grupo, estrato, semilla, intentos=200):
    """Partición 70/15/15 que no separa grupos y conserva la proporción de cada estrato.

    1. Los grupos de más de un predio se reparten al azar entre los subconjuntos hasta
       completar el 15 % de prueba y el 15 % de validación (por número de predios).
    2. Los predios que forman su propio grupo completan, estrato por estrato, lo que le
       falta a cada subconjunto para tener la proporción del conjunto completo.
    3. Se repite `intentos` veces con la misma semilla y se queda la partición cuyas
       proporciones (de los estratos y de los subconjuntos) se apartan menos del objetivo.

    Devuelve una Series con el subconjunto de cada fila, en el orden de `grupo`.
    """
    import numpy as np

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
        asignacion = pd.Series(np.where(acumulado <= cortes[0], "prueba",
                                        np.where(acumulado <= cortes[1], "validación", "entrenamiento")),
                               index=orden)
        sub = grupo.map(asignacion).where(multiple)
        for est in total.index:
            libres = rng.permutation(np.flatnonzero(~multiple & (estrato == est).to_numpy()))
            ya = sub[(estrato == est) & sub.notna()].value_counts().reindex(nombres, fill_value=0)
            falta = (pd.Series(PROPORCIONES) * total[est] - ya).clip(lower=0)
            falta = falta / falta.sum() * len(libres) if falta.sum() > 0 else pd.Series(PROPORCIONES) * len(libres)
            cuotas = np.floor(falta).astype(int)
            for k in np.argsort(-(falta - cuotas).to_numpy())[:len(libres) - cuotas.sum()]:
                cuotas.iloc[k] += 1
            inicio = 0
            for nombre in nombres:
                sub.iloc[libres[inicio:inicio + cuotas[nombre]]] = nombre
                inicio += cuotas[nombre]
        desvio_estratos = max((estrato[sub == s].value_counts(normalize=True).reindex(total.index, fill_value=0)
                               - total / len(estrato)).abs().max() for s in nombres)
        desvio_tamanos = max(abs((sub == s).mean() - PROPORCIONES[s]) for s in nombres)
        if mejor is None or desvio_estratos + desvio_tamanos < mejor[0]:
            mejor = (desvio_estratos + desvio_tamanos, sub.copy())
    return mejor[1]


# --- Interacciones con el historial (regresión logística) ----------------------------
from sklearn.base import BaseEstimator, TransformerMixin  # noqa: E402


class InteraccionesHistorial(TransformerMixin, BaseEstimator):
    """Agrega el producto de cada variable numérica o binaria por el indicador de los
    grupos del historial donde el pago es incierto (pagó 2025 y sin registro de 2025).

    Así la regresión logística puede darle a cada variable un efecto distinto según el
    historial, como mostró el notebook 06; los árboles encuentran esas interacciones solos.
    Va después del preprocesador, que debe entregar un DataFrame
    (`crear_preprocesador().set_output(transform="pandas")`). Con `activar=False` no hace
    nada, para comparar las dos versiones como un hiperparámetro más.
    """

    GRUPOS = ("Pagó 2025", "Sin registro 2025")

    def __init__(self, activar=True):
        self.activar = activar

    def fit(self, X, y=None):
        self.grupos_ = [f"categoricas__{GRUPO}_{g}" for g in self.GRUPOS
                        if f"categoricas__{GRUPO}_{g}" in X.columns]
        self.base_ = [c for c in X.columns if c.startswith(("numericas__", "binarias__"))]
        self.columnas_ = list(X.columns)
        self.n_features_in_ = X.shape[1]
        return self

    def _nombres_nuevos(self):
        return [f"interaccion__{g.removeprefix('categoricas__')} x {b.split('__', 1)[1]}"
                for g in self.grupos_ for b in self.base_]

    def transform(self, X):
        if not self.activar:
            return X
        productos = [X[g] * X[b] for g in self.grupos_ for b in self.base_]
        nuevas = pd.DataFrame(dict(zip(self._nombres_nuevos(), productos)), index=X.index)
        return pd.concat([X, nuevas], axis=1)

    def get_feature_names_out(self, input_features=None):
        import numpy as np

        return np.array(self.columnas_ + (self._nombres_nuevos() if self.activar else []), dtype=object)


# --- Métricas (estrategia del notebook 09) ------------------------------------------
def metricas(y, p, umbral=0.5):
    """ROC-AUC, log-loss y precisión, recall y F1 de la clase "no paga".

    `p` es la probabilidad de pagar; un predio se señala como "no paga" si p < umbral.
    El ROC-AUC queda vacío si la clase minoritaria tiene menos de 10 predios (por ejemplo,
    los que no pagaron 2025: en validación y prueba solo uno de ellos pagó), porque con
    tan pocos casos no dice nada.
    """
    import numpy as np
    from sklearn.metrics import f1_score, log_loss, precision_score, recall_score, roc_auc_score

    # El log-loss es el de scikit-learn sin recorte propio: una probabilidad de 0 o 1 que
    # resulte equivocada pesa lo que debe pesar (el árbol tiene hojas puras)
    y = np.asarray(y)
    p = np.asarray(p, dtype=float)
    pred = (p >= umbral).astype(int)
    argumentos = {"pos_label": CLASE_NO_PAGA, "zero_division": 0}
    minoritaria = min((y == 1).sum(), (y == 0).sum())
    return {
        "predios": len(y),
        "ROC-AUC": roc_auc_score(y, p) if minoritaria >= 10 else np.nan,
        "log-loss": log_loss(y, p, labels=[0, 1]),
        "precisión no paga": precision_score(y, pred, **argumentos),
        "recall no paga": recall_score(y, pred, **argumentos),
        "F1 no paga": f1_score(y, pred, **argumentos),
    }


def metricas_por_grupo(datos, p, umbral=0.5):
    """`metricas` en total y en cada grupo del historial. `datos` trae OBJETIVO y GRUPO."""
    import numpy as np

    p = np.asarray(p)
    filas = {"Total": metricas(datos[OBJETIVO], p, umbral)}
    for grupo in sorted(datos[GRUPO].unique()):
        m = (datos[GRUPO] == grupo).to_numpy()
        filas[grupo] = metricas(datos.loc[m, OBJETIVO], p[m], umbral)
    return pd.DataFrame(filas).T


def umbral_f1(y, p):
    """Umbral de probabilidad que maximiza el F1 de "no paga" (se elige en validación)."""
    import numpy as np

    umbrales = np.round(np.arange(0.05, 0.96, 0.01), 2)
    f1 = [metricas(y, p, u)["F1 no paga"] for u in umbrales]
    return float(umbrales[int(np.argmax(f1))])


def graficar_roc_calibracion(y, probabilidades, titulo=""):
    """Curvas ROC y de calibración de varios modelos sobre el mismo conjunto.

    `probabilidades` es un diccionario {nombre: probabilidad de pagar}. La calibración usa
    10 intervalos de igual número de predios.
    """
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import roc_auc_score, roc_curve

    colores = [NEGRO, AMARILLO, GRIS, AZUL]
    estilos = ["--", "-", "-", "-"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for (nombre, p), color, estilo in zip(probabilidades.items(), colores, estilos):
        fpr, tpr, _ = roc_curve(y, p)
        ax1.plot(fpr, tpr, color=color, linestyle=estilo, linewidth=2,
                 label=f"{nombre} (AUC = {roc_auc_score(y, p):.3f})")
        real, predicha = calibration_curve(y, p, n_bins=10, strategy="quantile")
        ax2.plot(predicha, real, color=color, linestyle=estilo, marker="o", markeredgecolor=NEGRO, label=nombre)
    ax1.plot([0, 1], [0, 1], color=GRIS, linestyle=":", linewidth=1, label="Azar")
    ax1.set_xlabel("Tasa de falsos positivos"); ax1.set_ylabel("Tasa de verdaderos positivos")
    ax1.set_title(f"Curva ROC {titulo}".strip()); ax1.legend(loc="lower right")
    ax2.plot([0, 1], [0, 1], color=GRIS, linestyle=":", linewidth=1, label="Calibración perfecta")
    ax2.set_xlabel("Probabilidad de pago predicha"); ax2.set_ylabel("Proporción que pagó")
    ax2.set_title(f"Curva de calibración {titulo}".strip()); ax2.legend(loc="upper left")
    plt.tight_layout()
    return fig


def graficar_calibracion_por_grupo(datos, probabilidades, grupos=("Pagó 2025", "Sin registro 2025"), n_bins=5):
    """Curva de calibración de varios modelos dentro de cada grupo del historial.

    `datos` trae OBJETIVO y GRUPO; `probabilidades` es {nombre: probabilidad de pagar}, en
    el orden de `datos`. El grupo que no pagó 2025 no se grafica: en validación y prueba
    tiene un solo pago. Usa `n_bins` intervalos de igual número de predios; la línea base,
    que da la misma probabilidad a todo el grupo, queda como un solo punto.
    """
    import numpy as np
    from sklearn.calibration import calibration_curve

    colores = [NEGRO, AMARILLO, GRIS, AZUL]
    estilos = ["--", "-", "-", "-"]
    fig, ejes = plt.subplots(1, len(grupos), figsize=(6.5 * len(grupos), 5), squeeze=False)
    for ax, grupo in zip(ejes[0], grupos):
        m = (datos[GRUPO] == grupo).to_numpy()
        y = datos.loc[m, OBJETIVO].to_numpy()
        for (nombre, p), color, estilo in zip(probabilidades.items(), colores, estilos):
            p = np.asarray(p)[m]
            if np.unique(p).size == 1:
                ax.plot(p[:1], [y.mean()], color=color, marker="D", markersize=9, markeredgecolor=NEGRO,
                        linestyle="none", label=nombre)
                continue
            real, predicha = calibration_curve(y, p, n_bins=n_bins, strategy="quantile")
            ax.plot(predicha, real, color=color, linestyle=estilo, marker="o", markeredgecolor=NEGRO, label=nombre)
        ax.plot([0, 1], [0, 1], color=GRIS, linestyle=":", linewidth=1, label="Calibración perfecta")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_xlabel("Probabilidad de pago predicha"); ax.set_ylabel("Proporción que pagó")
        ax.set_title(f"{grupo} ({m.sum():,} predios)".replace(",", " ")); ax.legend(loc="upper left")
    plt.tight_layout()
    return fig
