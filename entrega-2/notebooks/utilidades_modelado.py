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
