"""API REST del producto de datos: expone el motor de escenarios, el modelo de
pago, la simulación de perfiles hipotéticos y la exportación congelada.

Desde la raíz del repositorio:

    uv run uvicorn api:app --app-dir entrega-2/producto --reload

Documentación interactiva: http://127.0.0.1:8000/docs

Variables de entorno (útiles para Docker):
- PREDIOS_PATH: ruta a `predios.parquet` (por defecto `datos/predios/predios.parquet`)
- MODELO_PATH: ruta a `modelo.joblib` (por defecto `entrega-2/producto/artefactos/modelo.joblib`)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import modelo as mod
import motor
import preparacion as prep

# --- Estado cargado en memoria ----------------------------------------------


class EstadoServicio:
    predios: pd.DataFrame | None = None
    modelo: mod.ModeloPago | None = None
    probabilidades_base: np.ndarray | None = None
    error_datos: str | None = None
    error_modelo: str | None = None


estado = EstadoServicio()


def _cargar_datos() -> None:
    try:
        estado.predios = prep.cargar_y_preparar_predios()
        estado.error_datos = None
    except Exception as exc:  # pragma: no cover
        estado.predios = None
        estado.error_datos = str(exc)


def _cargar_modelo() -> None:
    try:
        estado.modelo = mod.cargar()
        estado.error_modelo = None
        if estado.predios is not None:
            estado.probabilidades_base = estado.modelo.probabilidad_pago(estado.predios)
        else:
            estado.probabilidades_base = None
    except Exception as exc:
        estado.modelo = None
        estado.probabilidades_base = None
        estado.error_modelo = str(exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _cargar_datos()
    _cargar_modelo()
    yield


app = FastAPI(
    title="Transición predial 2027",
    description=(
        "API de apoyo a la decisión para Multiaservi Consultores: simula escenarios "
        "de tarifas y límites del impuesto predial unificado (IPU) 2027, estima el "
        "recaudo esperado con un modelo de ML intercambiable y genera exportaciones "
        "congeladas de cifras agregadas para el Concejo."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --- Esquemas Pydantic ------------------------------------------------------


class RangoTarifaIn(BaseModel):
    destino: str
    avaluo_desde: float = Field(ge=0)
    avaluo_hasta: float | None = Field(default=None, gt=0)
    tarifa_por_mil: float = Field(ge=0, le=33)


class LimiteCrecimientoIn(BaseModel):
    avaluo_desde: float = Field(ge=0)
    avaluo_hasta: float | None = Field(default=None, gt=0)
    aumento_maximo: float = Field(ge=0)


class EscenarioIn(BaseModel):
    nombre: str = "Escenario personalizado"
    tarifas: list[RangoTarifaIn] = Field(default_factory=list)
    limites: list[LimiteCrecimientoIn] = Field(default_factory=list)
    meta_recaudo: float | None = Field(default=None, ge=0)
    descripcion: str = ""


class ComparacionIn(BaseModel):
    escenarios: list[EscenarioIn] = Field(min_length=1, max_length=10)


class PerfilHipoteticoIn(BaseModel):
    """Perfil sintético de un predio para ilustrar el motor determinista y el modelo ML.

    No corresponde a ningún contribuyente real.
    """

    avaluo_catastral: float = Field(gt=0, description="Avalúo catastral en pesos COP")
    ipu_2026: float = Field(ge=0, description="Impuesto predial facturado en 2026 en pesos COP")
    destinacion_economica: str = "Habitacional"
    zona: str = "Urbano"
    condicion_predio: str = "NPH"
    historial_2025: str = "Pagó 2025"
    area_construida_m2: float = Field(default=120.0, ge=0)
    area_terreno_m2: float | None = Field(default=150.0, ge=0)
    area_registral_m2: float | None = Field(default=150.0, ge=0)
    pisos_edificio: float = Field(default=2.0, ge=0)
    anio_construccion: int | None = Field(default=2015, ge=1900, le=2026)
    n_unidades: int = Field(default=1, ge=0)
    n_construcciones: int = Field(default=1, ge=0)
    n_titulares: int = Field(default=1, ge=1)
    predios_mismo_titular: int = Field(default=1, ge=1)
    titular_juridico: bool = False
    tiene_matricula: bool = True
    novedad_numero_predial: str = "Sin_Novedad"
    resultado_visita: str = "Exitoso"
    visita_exitosa_efectiva: bool = True
    tipo_derecho: str = "Dominio"
    autoriza_notificaciones: str = "Sí"
    escenario: EscenarioIn | None = None


def _exigir_datos() -> pd.DataFrame:
    if estado.predios is None:
        _cargar_datos()
    if estado.predios is None:
        raise HTTPException(
            status_code=503,
            detail=f"Datos no disponibles: {estado.error_datos or 'falta predios.parquet'}",
        )
    return estado.predios


def _a_escenario(modelo_in: EscenarioIn) -> motor.Escenario:
    return motor.escenario_desde_dict(modelo_in.model_dump())


# --- Rutas ------------------------------------------------------------------


@app.get("/salud")
def salud() -> dict[str, Any]:
    """Estado de la API, disponibilidad de los datos y metadatos del modelo ML activo."""
    return {
        "estado": "ok",
        "datos_disponibles": estado.predios is not None,
        "n_predios": int(len(estado.predios)) if estado.predios is not None else 0,
        "error_datos": estado.error_datos,
        "modelo_disponible": estado.modelo is not None,
        "modelo": estado.modelo.info if estado.modelo is not None else None,
        "error_modelo": estado.error_modelo,
    }


@app.post("/modelo/recargar")
def recargar_modelo() -> dict[str, Any]:
    """Recarga `modelo.joblib` desde disco sin reiniciar el servidor.

    Permite cambiar el modelo (árbol, regresión logística, gradient boosting)
    reemplazando únicamente el archivo `.joblib`.
    """
    _cargar_modelo()
    if estado.modelo is None:
        raise HTTPException(
            status_code=404,
            detail=estado.error_modelo or "No se pudo cargar el modelo desde disco.",
        )
    return {"estado": "recargado", "modelo": estado.modelo.info}


@app.get("/escenarios/predefinidos")
def obtener_predefinidos() -> dict[str, Any]:
    """Escenarios de referencia, tarifas base 2026 y catálogos para el formulario."""
    predef = motor.escenarios_predefinidos()
    catalogos: dict[str, Any] = {
        "grupos_destino": prep.GRUPOS_DESTINO,
        "rangos_avaluo": [
            {"desde": d, "hasta": h} for d, h in motor.RANGOS_AVALUO_DEFECTO
        ],
        "tarifas_referencia_2026": motor.TARIFAS_REFERENCIA_2026,
        "destinaciones_economicas": [
            "Habitacional",
            "Comercial",
            "Industrial",
            "Agricola",
            "Agropecuario",
            "Lote_Urbanizado_No_Construido",
            "Lote_Urbanizable_No_Urbanizado",
            "Forestal",
            "Institucional",
            "Educativo",
            "Recreacional",
        ],
        "zonas": ["Urbano", "Rural"],
        "condiciones_predio": ["NPH", "PH.Unidad_Predial", "Condominio.Unidad_Predial", "Informal"],
        "historiales_2025": ["Pagó 2025", "Sin registro 2025", "No pagó 2025"],
        "novedades_predial": [
            "Sin_Novedad",
            "Predio_Nuevo",
            "Desenglobe",
            "Englobe",
            "Cambio_Numero_Predial",
        ],
    }
    if estado.predios is not None:
        tasas_grupo = (
            estado.predios.groupby(prep.GRUPO)[prep.OBJETIVO].mean().mul(100.0).round(1).to_dict()
        )
        catalogos["tasas_pago_2026_por_historial"] = tasas_grupo

    return {
        "escenarios": {k: motor.escenario_a_dict(v) for k, v in predef.items()},
        "catalogos": catalogos,
    }


@app.post("/escenarios/simular")
def simular(escenario_in: EscenarioIn) -> dict[str, Any]:
    """Simula un escenario 2027 y devuelve KPIs, recaudo esperado, guardrails y gráficas."""
    predios = _exigir_datos()
    escenario = _a_escenario(escenario_in)
    calculado = motor.calcular_ipu(predios, escenario)
    resumen = motor.indicadores(
        calculado,
        probabilidades=estado.probabilidades_base,
        meta_recaudo=escenario.meta_recaudo,
        modelo_info=estado.modelo.info if estado.modelo is not None else None,
    )
    resumen["nombre_escenario"] = escenario.nombre
    return resumen


@app.post("/escenarios/comparar")
def comparar(solicitud: ComparacionIn) -> dict[str, Any]:
    """Evalúa varios escenarios en paralelo para la tabla comparativa y la frontera KPI 1 vs KPI 2."""
    predios = _exigir_datos()
    filas: list[dict[str, Any]] = []
    for esc_in in solicitud.escenarios:
        esc = _a_escenario(esc_in)
        calculado = motor.calcular_ipu(predios, esc)
        res = motor.indicadores(
            calculado,
            probabilidades=estado.probabilidades_base,
            meta_recaudo=esc.meta_recaudo,
            modelo_info=estado.modelo.info if estado.modelo is not None else None,
        )
        kpis = res["kpis"]
        rec_ml = res["recaudo_esperado"]
        filas.append(
            {
                "nombre": esc.nombre,
                "convergencia_2027_pct": kpis["convergencia_2027_pct"],
                "brecha_cerrada_pct": kpis["brecha_cerrada_pct"],
                "choque_mediano_top1": kpis["choque_mediano_top1"],
                "choque_mediano_top5": kpis["choque_mediano_top5"],
                "recaudo_facturado_2027": kpis["recaudo_facturado_2027"],
                "variacion_recaudo_pct": kpis["variacion_recaudo_pct"],
                "recaudo_esperado_2027": rec_ml["esperado_2027"],
                "cumple_meta": kpis["cumple_meta"],
                "guardrails_cumplidos": sum(1 for g in res["guardrails"] if g["cumple"]),
                "guardrails_total": len(res["guardrails"]),
                "alertas": [g["titulo"] for g in res["guardrails"] if not g["cumple"]],
            }
        )
    return {"comparacion": filas}


@app.post("/escenarios/exportar")
def exportar(escenario_in: EscenarioIn) -> dict[str, Any]:
    """Exportación congelada y versionada (HTML + JSON agregado) del escenario elegido."""
    predios = _exigir_datos()
    escenario = _a_escenario(escenario_in)
    calculado = motor.calcular_ipu(predios, escenario)
    resumen = motor.indicadores(
        calculado,
        probabilidades=estado.probabilidades_base,
        meta_recaudo=escenario.meta_recaudo,
        modelo_info=estado.modelo.info if estado.modelo is not None else None,
    )
    return motor.generar_exportacion_congelada(escenario, resumen)


@app.post("/hipotetico/simular")
def simular_perfil_hipotetico(perfil: PerfilHipoteticoIn) -> dict[str, Any]:
    """Combina motor determinista + modelo ML sobre un perfil sintético de predio.

    Uso exclusivamente ilustrativo: no consulta ni expone predios ni personas reales.
    """
    escenario = (
        _a_escenario(perfil.escenario)
        if perfil.escenario is not None
        else motor.escenarios_predefinidos()["progresivo_2027"]
    )
    determinista = motor.simular_hipotetico(
        avaluo_catastral=perfil.avaluo_catastral,
        ipu_2026=perfil.ipu_2026,
        destinacion_economica=perfil.destinacion_economica,
        zona=perfil.zona,
        escenario=escenario,
    )

    prediccion_ml: dict[str, Any] = {"disponible": False}
    if estado.modelo is not None:
        pred = estado.modelo.predecir_hipotetico(perfil.model_dump())
        prob = pred["probabilidad_pago"]
        pred["disponible"] = True
        pred["aporte_recaudo_esperado_2027"] = round(determinista["ipu_2027"] * prob, 0)
        pred["aporte_recaudo_esperado_2026"] = round(determinista["ipu_2026"] * prob, 0)
        if estado.predios is not None:
            tasa_hist = (
                estado.predios.loc[
                    estado.predios[prep.GRUPO] == perfil.historial_2025, prep.OBJETIVO
                ].mean()
            )
            pred["tasa_referencia_historial_pct"] = (
                round(float(tasa_hist * 100.0), 1) if pd.notna(tasa_hist) else None
            )
        prediccion_ml = pred

    return {
        "es_perfil_sintetico": True,
        "escenario_aplicado": escenario.nombre,
        "determinista": determinista,
        "modelo_pago": prediccion_ml,
        "nota": (
            "Simulación ilustrativa sobre un perfil hipotético. El modelo estima "
            "probabilidad de pago con patrones de 2026 para agregar recaudo esperado; "
            "no predice elasticidad ante el cambio tarifario ni califica contribuyentes."
        ),
    }
