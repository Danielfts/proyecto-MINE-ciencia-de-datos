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

# Características: todas se conocen antes del pago de la vigencia 2026
NUMERICAS = [
    "log_avaluo", "log_ipu", "tarifa_efectiva", "log_area_construida", "log_area_registral",
    "log_area_terreno", "n_unidades", "n_construcciones", "pisos_edificio", "anio_construccion",
    "n_titulares", "log_predios_mismo_titular",
]
CATEGORICAS = [
    "historial_2025", "novedad_numero_predial", "condicion_predio", "destinacion_economica",
    "zona", "resultado_visita", "tipo_derecho", "tipo_predio", "autoriza_notificaciones",
]
BINARIAS = ["visita_exitosa_efectiva", "avaluo_cero", "anio_sospechoso", "tiene_matricula",
            "titular_juridico"]
CARACTERISTICAS = NUMERICAS + CATEGORICAS + BINARIAS


def crear_preprocesador(escalar=True, min_frecuencia=30):
    """ColumnTransformer de las características del modelo de pago.

    - Numéricas: imputación con la mediana más una columna indicadora de cada faltante
      y, si `escalar`, estandarización (la necesita la regresión logística; a los árboles
      no les cambia nada).
    - Categóricas: one-hot, con las categorías de menos de `min_frecuencia` predios
      agrupadas en una sola ("infrequent") y las que no se vieron en entrenamiento en ceros.
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
