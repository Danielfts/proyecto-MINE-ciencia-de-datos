"""Carga y preparación de datos para el producto de datos.

Replica exactamente las transformaciones del notebook 08 (unidad de análisis de
18 802 predios privados facturados en 2026, limpieza y 25 características del
modelo de pago) de forma autocontenida dentro de `entrega-2/producto/`, para
facilitar el empaquetado y despliegue con Docker sin depender de la carpeta de
notebooks.

Ninguna función expone datos personales ni columnas reservadas.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

# Raíz del repositorio (dos niveles arriba de entrega-2/producto/)
RAIZ = Path(__file__).resolve().parents[2]
ARCHIVO_PREDIOS_POR_DEFECTO = RAIZ / "datos" / "predios" / "predios.parquet"
SEMILLA = 4101

OBJETIVO = "pago_2026"
GRUPO = "historial_2025"
GRUPO_PARTICION = "grupo_particion"

NUMERICAS = [
    "log_avaluo",
    "log_area_construida",
    "log_area_registral",
    "log_area_terreno",
    "n_unidades",
    "n_construcciones",
    "pisos_edificio",
    "anio_construccion",
    "n_titulares",
    "log_predios_mismo_titular",
    "tasa_2025_mismo_dueno",
    "tasa_2025_mismo_edificio",
]
CATEGORICAS = [
    "historial_2025",
    "novedad_numero_predial",
    "condicion_predio",
    "destinacion_economica",
    "zona",
    "resultado_visita",
    "tipo_derecho",
    "autoriza_notificaciones",
]
BINARIAS = [
    "visita_exitosa_efectiva",
    "avaluo_cero",
    "anio_sospechoso",
    "tiene_matricula",
    "titular_juridico",
]
CARACTERISTICAS = NUMERICAS + CATEGORICAS + BINARIAS

EXCLUIR_CONDICION = [
    "Via",
    "Bien_Uso_Publico",
    "Parque_Cementerio.Matriz",
    "Parque_Cementerio.Unidad_Predial",
]

# Grupos de destino económico para la tabla de tarifas (coherentes con el wireframe)
GRUPOS_DESTINO = [
    "Urbano habitacional",
    "Industrial y comercial",
    "Lotes",
    "Rural habitacional",
    "Agropecuario",
    "Otros usos",
]

_DESTINOS_INDUSTRIAL_COMERCIAL = {
    "Comercial",
    "Industrial",
    "Minero",
    "Recreacional",
    "Salubridad",
    "Servicios_Especiales",
    "Infraestructura_Transporte",
    "Infraestructura_Hidraulica",
    "Infraestructura_Seguridad",
    "Infraestructura_Asociada_Produccion_Agropecuaria",
}

_DESTINOS_AGROPECUARIO = {
    "Agricola",
    "Agropecuario",
    "Pecuario",
    "Agroforestal",
    "Agroindustrial",
    "Acuicola",
    "Forestal",
}


def ruta_predios() -> Path:
    """Ruta al archivo predios.parquet (configurable mediante PREDIOS_PATH)."""
    env = os.environ.get("PREDIOS_PATH")
    return Path(env) if env else ARCHIVO_PREDIOS_POR_DEFECTO


def agrupar_destino(destinacion: str | None, zona: str | None) -> str:
    """Mapea (destinacion_economica, zona) a uno de los 6 grupos tarifarios."""
    dest = str(destinacion or "")
    z = str(zona or "")
    if dest == "Habitacional":
        return "Urbano habitacional" if z == "Urbano" else "Rural habitacional"
    if dest in _DESTINOS_INDUSTRIAL_COMERCIAL:
        return "Industrial y comercial"
    if dest.startswith("Lote_"):
        return "Lotes"
    if dest in _DESTINOS_AGROPECUARIO:
        return "Agropecuario"
    return "Otros usos"


def _desanidar(predios: pd.DataFrame, columna: str) -> pd.DataFrame:
    filas = predios[["id_predio", columna]].explode(columna).dropna(subset=[columna])
    if filas.empty:
        return pd.DataFrame(columns=["id_predio"])
    return pd.concat(
        [
            filas[["id_predio"]].reset_index(drop=True),
            pd.json_normalize(filas[columna].tolist()),
        ],
        axis=1,
    )


def cargar_y_preparar_predios(ruta: str | Path | None = None) -> pd.DataFrame:
    """Lee `predios.parquet` y construye la tabla unificada para motor y modelo.

    Devuelve únicamente las columnas necesarias (sin identificadores públicos ni
    datos personales) sobre la unidad de análisis de predios privados facturados
    en 2026.
    """
    archivo = Path(ruta) if ruta is not None else ruta_predios()
    if not archivo.exists():
        raise FileNotFoundError(
            f"No se encontró {archivo}. Ubique predios.parquet en datos/predios/ "
            "o defina la variable de entorno PREDIOS_PATH."
        )

    predios = pq.read_table(archivo).flatten().to_pandas()
    predios["fecha_visita_predial"] = pd.to_datetime(predios["fecha_visita_predial"])

    construcciones = _desanidar(predios, "construcciones")
    unidades = _desanidar(predios, "unidades")
    predios = predios.drop(columns=["construcciones", "unidades"])

    con_facturacion = predios["pago_2026"].notna()
    sin_excluidos = con_facturacion & ~predios["condicion_predio"].isin(EXCLUIR_CONDICION)
    en_unidad = sin_excluidos & ~predios["tipo"].str.startswith("Predio.Publico")

    predios[OBJETIVO] = predios["pago_2026"].astype("boolean").astype("Int64")
    predios[GRUPO] = (
        predios["pago_2025"]
        .map({True: "Pagó 2025", False: "No pagó 2025"})
        .fillna("Sin registro 2025")
    )

    # --- Limpieza (idéntica a la etapa 4 del notebook 08) ---
    if "total_pisos" in construcciones.columns:
        construcciones["total_pisos"] = construcciones["total_pisos"].mask(
            construcciones["total_pisos"].eq(99)
        )

    fecha_centinela = predios["fecha_visita_predial"].value_counts().idxmax()
    predios["fecha_visita_valida"] = predios["fecha_visita_predial"].mask(
        predios["fecha_visita_predial"].eq(fecha_centinela)
    )

    anio = unidades.groupby("id_predio")["anio_construccion"].median()
    predios["anio_construccion"] = predios["id_predio"].map(anio)
    predios["anio_sospechoso"] = predios["anio_construccion"].eq(2000).astype(int)
    predios["anio_construccion"] = predios["anio_construccion"].mask(
        predios["anio_sospechoso"].eq(1)
    )

    predios["avaluo_cero"] = predios["avaluo_catastral"].le(0).astype(int)

    area_construida = unidades.groupby("id_predio")["area_construida"].sum()
    predios["area_construida_total"] = predios["id_predio"].map(area_construida).fillna(0.0)
    registral_invalida = predios["area_registral_m2"].le(0) | (
        predios["area_construida_total"] > 20 * predios["area_registral_m2"]
    )
    predios["area_registral_valida"] = predios["area_registral_m2"].mask(registral_invalida)

    # --- Nuevas características (idénticas a la etapa 5 del notebook 08) ---
    por_predio = predios.set_index("id_predio")
    predios["n_unidades"] = (
        predios["id_predio"].map(unidades.groupby("id_predio").size()).fillna(0).astype(int)
    )
    predios["n_construcciones"] = (
        predios["id_predio"]
        .map(construcciones.groupby("id_predio").size())
        .fillna(0)
        .astype(int)
    )
    pisos_propios = predios["id_predio"].map(
        construcciones.groupby("id_predio")["total_pisos"].max()
    )

    es_unidad_ph = predios["condicion_predio"].eq("PH.Unidad_Predial")
    pisos_matriz = predios["id_predio_matriz"].map(
        pd.Series(pisos_propios.values, index=predios["id_predio"])
    )
    predios["pisos_edificio"] = pisos_propios.where(~es_unidad_ph, pisos_matriz)
    predios.loc[~es_unidad_ph & predios["n_construcciones"].eq(0), "pisos_edificio"] = 0

    terreno_matriz = predios["id_predio_matriz"].map(por_predio["terreno.area_terreno"])
    area_terreno = predios["terreno.area_terreno"].where(
        ~es_unidad_ph, predios["coeficiente_copropiedad"] * terreno_matriz
    )

    visita_propia = (
        predios["resultado_visita"].eq("Exitoso") & predios["fecha_visita_valida"].notna()
    )
    visita_por_id = pd.Series(visita_propia.values, index=predios["id_predio"])
    predios["visita_exitosa_efectiva"] = (
        visita_propia | predios["id_predio_matriz"].map(visita_por_id).eq(True)
    ).astype(int)

    avaluo_pos = predios["avaluo_catastral"].where(predios["avaluo_catastral"] > 0)
    predios["log_avaluo"] = np.log10(avaluo_pos)
    predios["log_area_construida"] = np.log10(1.0 + predios["area_construida_total"])
    predios["log_area_registral"] = np.log10(predios["area_registral_valida"])
    predios["log_area_terreno"] = np.log10(1.0 + area_terreno)

    predios["novedad_numero_predial"] = predios["tipo_novedad_numero_predial"].fillna(
        "Sin_Novedad"
    )
    predios["zona"] = predios["zona"].map({"00": "Rural", "01": "Urbano"})
    predios["autoriza_notificaciones"] = (
        predios["autoriza_notificaciones"].map({True: "Sí", False: "No"}).fillna("Sin dato")
    )

    predios["n_titulares"] = predios["titulares.n_titulares"]
    predios["log_predios_mismo_titular"] = np.log10(
        predios["titulares.max_predios_mismo_titular"]
    )
    predios["titular_juridico"] = (
        predios["titulares.n_persona_juridica"].fillna(0).gt(0).astype(int)
    )
    predios["tiene_matricula"] = predios["matricula_inmobiliaria"].notna().astype(int)

    n_titular = predios["titulares.max_predios_mismo_titular"]
    dueno = ("T" + n_titular.astype("Int64").astype(str)).where(n_titular >= 10)
    edificio = ("M" + predios["id_predio_matriz"].astype(str)).where(
        predios["id_predio_matriz"].notna()
    )
    pago_previo = predios["pago_2025"].map({True: 1.0, False: 0.0})

    def tasa_otros(clave: pd.Series) -> pd.Series:
        suma = pago_previo.groupby(clave).transform("sum")
        conteo = pago_previo.groupby(clave).transform("count")
        otros = conteo - pago_previo.notna().astype(int)
        return ((suma - pago_previo.fillna(0.0)) / otros).where(clave.notna() & (otros > 0))

    predios["tasa_2025_mismo_dueno"] = tasa_otros(dueno)
    predios["tasa_2025_mismo_edificio"] = tasa_otros(edificio)
    predios[GRUPO_PARTICION] = dueno.fillna("P" + predios["id_predio"].astype(str))

    predios["grupo_destino"] = [
        agrupar_destino(d, z)
        for d, z in zip(predios["destinacion_economica"], predios["zona"])
    ]

    columnas_salida = [
        "id_predio",
        GRUPO_PARTICION,
        OBJETIVO,
        "avaluo_catastral",
        "ipu_facturado_2026",
        "grupo_destino",
    ] + CARACTERISTICAS

    preparados = predios.loc[en_unidad, columnas_salida].reset_index(drop=True)
    preparados[OBJETIVO] = preparados[OBJETIVO].astype(int)
    return preparados


def preparar_predio_hipotetico(perfil: dict[str, Any]) -> pd.DataFrame:
    """Construye una fila con las 25 características esperadas por el pipeline ML.

    Se usa únicamente para perfiles sintéticos/hipotéticos (sin datos reales).
    """
    avaluo = float(perfil.get("avaluo_catastral", 0.0) or 0.0)
    area_construida = max(0.0, float(perfil.get("area_construida_m2", 0.0) or 0.0))
    area_terreno = perfil.get("area_terreno_m2")
    area_registral = perfil.get("area_registral_m2")
    anio_construccion = perfil.get("anio_construccion")
    predios_titular = max(1, int(perfil.get("predios_mismo_titular", 1) or 1))
    n_titulares = max(1, int(perfil.get("n_titulares", 1) or 1))

    avaluo_cero = 1 if avaluo <= 0 else 0
    log_avaluo = float(np.log10(avaluo)) if avaluo > 0 else np.nan
    log_area_construida = float(np.log10(1.0 + area_construida))

    if area_terreno is not None and float(area_terreno) >= 0:
        log_area_terreno = float(np.log10(1.0 + float(area_terreno)))
    else:
        log_area_terreno = np.nan

    if area_registral is not None and float(area_registral) > 0:
        log_area_registral = float(np.log10(float(area_registral)))
    else:
        log_area_registral = np.nan

    anio_sospechoso = 1 if anio_construccion == 2000 else 0
    anio_val = np.nan if (anio_construccion is None or anio_sospechoso == 1) else float(anio_construccion)

    tasa_dueno = perfil.get("tasa_2025_mismo_dueno")
    tasa_edificio = perfil.get("tasa_2025_mismo_edificio")

    fila = {
        "log_avaluo": log_avaluo,
        "log_area_construida": log_area_construida,
        "log_area_registral": log_area_registral,
        "log_area_terreno": log_area_terreno,
        "n_unidades": int(perfil.get("n_unidades", 1 if area_construida > 0 else 0)),
        "n_construcciones": int(perfil.get("n_construcciones", 1 if area_construida > 0 else 0)),
        "pisos_edificio": float(perfil.get("pisos_edificio", 1 if area_construida > 0 else 0)),
        "anio_construccion": anio_val,
        "n_titulares": n_titulares,
        "log_predios_mismo_titular": float(np.log10(predios_titular)),
        "tasa_2025_mismo_dueno": np.nan if tasa_dueno is None else float(tasa_dueno),
        "tasa_2025_mismo_edificio": np.nan if tasa_edificio is None else float(tasa_edificio),
        "historial_2025": str(perfil.get("historial_2025", "Pagó 2025")),
        "novedad_numero_predial": str(perfil.get("novedad_numero_predial", "Sin_Novedad")),
        "condicion_predio": str(perfil.get("condicion_predio", "NPH")),
        "destinacion_economica": str(perfil.get("destinacion_economica", "Habitacional")),
        "zona": str(perfil.get("zona", "Urbano")),
        "resultado_visita": str(perfil.get("resultado_visita", "Exitoso")),
        "tipo_derecho": str(perfil.get("tipo_derecho", "Dominio")),
        "autoriza_notificaciones": str(perfil.get("autoriza_notificaciones", "Sí")),
        "visita_exitosa_efectiva": int(bool(perfil.get("visita_exitosa_efectiva", True))),
        "avaluo_cero": avaluo_cero,
        "anio_sospechoso": anio_sospechoso,
        "tiene_matricula": int(bool(perfil.get("tiene_matricula", True))),
        "titular_juridico": int(bool(perfil.get("titular_juridico", False))),
    }
    return pd.DataFrame([fila], columns=CARACTERISTICAS)
