"""Motor determinista de escenarios del impuesto predial unificado (IPU) 2027.

Aplica a cada predio de la unidad de análisis las tarifas por mil y los límites
de crecimiento de un escenario, calcula los KPIs y guardrails de la tabla 1 del
reporte, genera agregados para las gráficas y redacta una lectura en lenguaje
llano para la sustentación ante el Concejo.

Todas las salidas expuestas por el motor son agregadas: nunca devuelven ni
identifican predios individuales ni al municipio.
"""

from __future__ import annotations

import hashlib
import html
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
import pandas as pd

import modelo as mod
import preparacion as prep

# --- Estructuras de entrada -------------------------------------------------


@dataclass
class RangoTarifa:
    """Tarifa (por mil) para un grupo de destino económico y un rango de avalúo."""

    destino: str
    avaluo_desde: float
    avaluo_hasta: float | None  # None: sin tope superior
    tarifa_por_mil: float


@dataclass
class LimiteCrecimiento:
    """Límite al aumento del impuesto frente a 2026, por rango de avalúo."""

    avaluo_desde: float
    avaluo_hasta: float | None
    aumento_maximo: float  # 0.30 = 30 %


@dataclass
class Escenario:
    nombre: str
    tarifas: list[RangoTarifa] = field(default_factory=list)
    limites: list[LimiteCrecimiento] = field(default_factory=list)
    meta_recaudo: float | None = None  # None: no perder recaudo frente a 2026
    descripcion: str = ""


# --- Rangos y escenarios predefinidos ---------------------------------------

RANGOS_AVALUO_DEFECTO: list[tuple[float, float | None]] = [
    (0.0, 100_000_000.0),
    (100_000_000.0, 250_000_000.0),
    (250_000_000.0, 500_000_000.0),
    (500_000_000.0, 1_200_000_000.0),
    (1_200_000_000.0, None),
]

# Tarifas nominales de referencia 2026 (por mil) por grupo y rango de avalúo.
# Con estos valores y los límites 30 %–80 %, el IPU facturado de 2026 se ubica
# alrededor de la mitad del IPU pleno (~50 % de convergencia), coherente con el reporte.
TARIFAS_REFERENCIA_2026: dict[str, list[float]] = {
    "Urbano habitacional": [4.0, 4.5, 5.5, 6.5, 7.5],
    "Industrial y comercial": [8.5, 9.5, 10.5, 11.5, 12.5],
    "Lotes": [8.0, 9.0, 10.0, 11.0, 12.0],
    "Rural habitacional": [4.0, 5.0, 6.0, 7.0, 8.0],
    "Agropecuario": [4.5, 5.5, 6.5, 7.5, 8.5],
    "Otros usos": [5.0, 6.0, 7.0, 8.0, 9.0],
}

TARIFAS_PROGRESIVO_2027: dict[str, list[float]] = {
    "Urbano habitacional": [2.2, 3.5, 4.8, 6.5, 8.5],
    "Industrial y comercial": [2.1, 4.0, 6.5, 9.5, 12.8],
    "Lotes": [2.3, 4.2, 7.0, 10.0, 12.5],
    "Rural habitacional": [2.2, 3.5, 5.0, 6.8, 8.8],
    "Agropecuario": [2.2, 3.8, 5.5, 7.2, 9.2],
    "Otros usos": [2.3, 4.0, 6.0, 8.2, 10.0],
}


def _construir_tarifas(tabla: dict[str, list[float]]) -> list[RangoTarifa]:
    rangos: list[RangoTarifa] = []
    for destino in prep.GRUPOS_DESTINO:
        valores = tabla[destino]
        for (desde, hasta), tarifa in zip(RANGOS_AVALUO_DEFECTO, valores):
            rangos.append(
                RangoTarifa(
                    destino=destino,
                    avaluo_desde=desde,
                    avaluo_hasta=hasta,
                    tarifa_por_mil=float(tarifa),
                )
            )
    return rangos


def escenarios_predefinidos() -> dict[str, Escenario]:
    """Cuatro escenarios listos para explorar la frontera entre convergencia y choque."""
    return {
        "base_2026": Escenario(
            nombre="Escenario A · Continuidad 2026 (límites 30 %–80 %)",
            descripcion=(
                "Mantiene la estructura tarifaria de referencia 2026 y los límites "
                "transitorios vigentes (30 % a 80 % según avalúo)."
            ),
            tarifas=_construir_tarifas(TARIFAS_REFERENCIA_2026),
            limites=[
                LimiteCrecimiento(0.0, 100_000_000.0, 0.30),
                LimiteCrecimiento(100_000_000.0, 300_000_000.0, 0.45),
                LimiteCrecimiento(300_000_000.0, 700_000_000.0, 0.60),
                LimiteCrecimiento(700_000_000.0, None, 0.80),
            ],
        ),
        "progresivo_2027": Escenario(
            nombre="Escenario B · Transición progresiva (recomendado)",
            descripcion=(
                "Alivia la tarifa de la vivienda de menor avalúo, refuerza la progresividad "
                "en avalúos altos y aplica topes graduales de 25 % a 70 %."
            ),
            tarifas=_construir_tarifas(TARIFAS_PROGRESIVO_2027),
            limites=[
                LimiteCrecimiento(0.0, 100_000_000.0, 0.25),
                LimiteCrecimiento(100_000_000.0, 300_000_000.0, 0.40),
                LimiteCrecimiento(300_000_000.0, 700_000_000.0, 0.55),
                LimiteCrecimiento(700_000_000.0, None, 0.70),
            ],
        ),
        "acelerado_2027": Escenario(
            nombre="Escenario C · Convergencia acelerada (tope legal)",
            descripcion=(
                "Cierra más rápido la brecha frente al impuesto pleno llevando los límites "
                "superiores al tope legal del 100 % (Ley 44 de 1990), con mayor choque en la cola."
            ),
            tarifas=_construir_tarifas(TARIFAS_REFERENCIA_2026),
            limites=[
                LimiteCrecimiento(0.0, 100_000_000.0, 0.30),
                LimiteCrecimiento(100_000_000.0, 300_000_000.0, 0.60),
                LimiteCrecimiento(300_000_000.0, 700_000_000.0, 0.85),
                LimiteCrecimiento(700_000_000.0, None, 1.00),
            ],
        ),
        "pleno_sin_limites": Escenario(
            nombre="Escenario D · Sin límites (IPU pleno)",
            descripcion=(
                "Escenario de referencia extrema sin topes de crecimiento: muestra la brecha "
                "cerrada al 100 % y evidencia el incumplimiento del tope legal de la Ley 44."
            ),
            tarifas=_construir_tarifas(TARIFAS_REFERENCIA_2026),
            limites=[],
        ),
    }


def escenario_a_dict(escenario: Escenario) -> dict[str, Any]:
    return asdict(escenario)


def escenario_desde_dict(datos: dict[str, Any]) -> Escenario:
    tarifas = [
        RangoTarifa(**t) if not isinstance(t, RangoTarifa) else t
        for t in datos.get("tarifas", [])
    ]
    limites = [
        LimiteCrecimiento(**lim) if not isinstance(lim, LimiteCrecimiento) else lim
        for lim in datos.get("limites", [])
    ]
    return Escenario(
        nombre=str(datos.get("nombre", "Escenario personalizado")),
        tarifas=tarifas,
        limites=limites,
        meta_recaudo=datos.get("meta_recaudo"),
        descripcion=str(datos.get("descripcion", "")),
    )


# --- Cálculo determinista ---------------------------------------------------


def _asignar_tarifas(
    avaluo: np.ndarray, grupo_destino: np.ndarray, tarifas: list[RangoTarifa]
) -> np.ndarray:
    tarifa_arr = np.full(len(avaluo), np.nan, dtype=float)
    por_destino: dict[str, list[RangoTarifa]] = {}
    for r in tarifas:
        por_destino.setdefault(r.destino, []).append(r)

    for destino, rangos in por_destino.items():
        rangos_ord = sorted(rangos, key=lambda r: r.avaluo_desde)
        mask_dest = grupo_destino == destino
        if not np.any(mask_dest):
            continue
        for r in rangos_ord:
            cond = mask_dest & (avaluo >= r.avaluo_desde)
            if r.avaluo_hasta is not None:
                cond &= avaluo < r.avaluo_hasta
            tarifa_arr = np.where(cond, r.tarifa_por_mil, tarifa_arr)
        # Respaldo si algún predio quedó por debajo del mínimo o por encima del máximo
        faltantes = mask_dest & np.isnan(tarifa_arr)
        if np.any(faltantes):
            bajo = faltantes & (avaluo < rangos_ord[0].avaluo_desde)
            tarifa_arr = np.where(bajo, rangos_ord[0].tarifa_por_mil, tarifa_arr)
            tarifa_arr = np.where(
                mask_dest & np.isnan(tarifa_arr), rangos_ord[-1].tarifa_por_mil, tarifa_arr
            )

    if np.any(np.isnan(tarifa_arr)):
        fallback = float(np.nanmedian(tarifa_arr)) if not np.all(np.isnan(tarifa_arr)) else 5.6
        tarifa_arr = np.where(np.isnan(tarifa_arr), fallback, tarifa_arr)
    return tarifa_arr


def _asignar_limites(avaluo: np.ndarray, limites: list[LimiteCrecimiento]) -> np.ndarray:
    if not limites:
        return np.full(len(avaluo), np.inf, dtype=float)
    rangos_ord = sorted(limites, key=lambda r: r.avaluo_desde)
    lim_arr = np.full(len(avaluo), np.nan, dtype=float)
    for r in rangos_ord:
        cond = avaluo >= r.avaluo_desde
        if r.avaluo_hasta is not None:
            cond &= avaluo < r.avaluo_hasta
        lim_arr = np.where(cond, r.aumento_maximo, lim_arr)
    lim_arr = np.where(
        np.isnan(lim_arr) & (avaluo < rangos_ord[0].avaluo_desde),
        rangos_ord[0].aumento_maximo,
        lim_arr,
    )
    lim_arr = np.where(np.isnan(lim_arr), rangos_ord[-1].aumento_maximo, lim_arr)
    return lim_arr


def calcular_ipu(predios: pd.DataFrame, escenario: Escenario) -> pd.DataFrame:
    """IPU 2027 de cada predio con las reglas deterministas del escenario.

    Recibe la tabla preparada de predios (con `avaluo_catastral`,
    `ipu_facturado_2026` y `grupo_destino`) y devuelve una copia con las columnas
    calculadas: `tarifa_por_mil`, `limite_crecimiento`, `ipu_2026`,
    `ipu_pleno_2027`, `ipu_2027`, `limite_aplicado`, `aumento_pesos`,
    `aumento_pct` y `supera_tope_legal`.
    """
    res = predios.copy()
    avaluo = res["avaluo_catastral"].fillna(0.0).to_numpy(dtype=float)
    ipu_2026 = res["ipu_facturado_2026"].fillna(0.0).to_numpy(dtype=float)
    grupos = res["grupo_destino"].to_numpy()

    tarifas = _asignar_tarifas(avaluo, grupos, escenario.tarifas)
    limites = _asignar_limites(avaluo, escenario.limites)

    tiene_avaluo = avaluo > 0.0
    tiene_base_2026 = ipu_2026 > 0.0

    ipu_pleno = np.where(tiene_avaluo, avaluo * (tarifas / 1000.0), ipu_2026)
    finito = tiene_base_2026 & np.isfinite(limites)
    ipu_tope = np.full(len(avaluo), np.inf, dtype=float)
    ipu_tope[finito] = ipu_2026[finito] * (1.0 + limites[finito])

    # El límite de crecimiento solo frena aumentos respecto a 2026 (nunca impide rebajas)
    sube = tiene_avaluo & tiene_base_2026 & (ipu_pleno > ipu_2026)
    ipu_2027 = np.where(sube, np.minimum(ipu_pleno, ipu_tope), ipu_pleno)
    limite_aplicado = sube & (ipu_pleno > ipu_tope + 1e-6)

    aumento_pesos = ipu_2027 - ipu_2026
    aumento_pct = np.divide(
        aumento_pesos,
        ipu_2026,
        out=np.full_like(aumento_pesos, np.nan, dtype=float),
        where=tiene_base_2026,
    )
    supera_tope_legal = tiene_base_2026 & (ipu_2027 > 2.0 * ipu_2026 + 1.0)

    res["tarifa_por_mil"] = tarifas
    res["limite_crecimiento"] = limites
    res["ipu_2026"] = ipu_2026
    res["ipu_pleno_2027"] = ipu_pleno
    res["ipu_2027"] = ipu_2027
    res["limite_aplicado"] = limite_aplicado
    res["aumento_pesos"] = aumento_pesos
    res["aumento_pct"] = aumento_pct
    res["supera_tope_legal"] = supera_tope_legal
    return res


def simular_hipotetico(
    avaluo_catastral: float,
    ipu_2026: float,
    destinacion_economica: str,
    zona: str,
    escenario: Escenario,
) -> dict[str, Any]:
    """Cálculo determinista para un perfil sintético de predio (sin datos reales)."""
    grupo = prep.agrupar_destino(destinacion_economica, zona)
    fila = pd.DataFrame(
        [
            {
                "avaluo_catastral": float(avaluo_catastral),
                "ipu_facturado_2026": float(ipu_2026),
                "grupo_destino": grupo,
            }
        ]
    )
    calculado = calcular_ipu(fila, escenario).iloc[0]
    aum_pct = None if pd.isna(calculado["aumento_pct"]) else float(calculado["aumento_pct"] * 100.0)
    lim_pct = (
        None
        if not np.isfinite(calculado["limite_crecimiento"])
        else float(calculado["limite_crecimiento"] * 100.0)
    )
    return {
        "grupo_destino": grupo,
        "avaluo_catastral": float(avaluo_catastral),
        "tarifa_por_mil": round(float(calculado["tarifa_por_mil"]), 2),
        "limite_crecimiento_pct": None if lim_pct is None else round(lim_pct, 1),
        "ipu_2026": round(float(calculado["ipu_2026"]), 0),
        "ipu_pleno_2027": round(float(calculado["ipu_pleno_2027"]), 0),
        "ipu_2027": round(float(calculado["ipu_2027"]), 0),
        "limite_aplicado": bool(calculado["limite_aplicado"]),
        "aumento_pesos": round(float(calculado["aumento_pesos"]), 0),
        "aumento_pct": None if aum_pct is None else round(aum_pct, 1),
        "supera_tope_legal": bool(calculado["supera_tope_legal"]),
        "ahorro_por_limite": round(
            max(0.0, float(calculado["ipu_pleno_2027"] - calculado["ipu_2027"])), 0
        ),
    }


# --- Indicadores, guardrails, gráficas y lectura llana ----------------------


def _fmt_mil_m(valor: float) -> str:
    return f"${valor / 1e9:,.1f} mil M".replace(",", " ")


def _fmt_m(valor: float) -> str:
    return f"${valor / 1e6:,.1f} M".replace(",", " ")


def indicadores(
    resultado: pd.DataFrame,
    probabilidades: np.ndarray | None = None,
    meta_recaudo: float | None = None,
    modelo_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """KPIs, guardrails, datos para gráficas y lectura en lenguaje llano."""
    n_predios = int(len(resultado))
    ipu_2026_tot = float(resultado["ipu_2026"].sum())
    ipu_pleno_tot = float(resultado["ipu_pleno_2027"].sum())
    ipu_2027_tot = float(resultado["ipu_2027"].sum())

    # --- KPI 1: Convergencia hacia el pleno ---
    conv_2027 = (ipu_2027_tot / ipu_pleno_tot * 100.0) if ipu_pleno_tot > 0 else 0.0
    conv_2026 = (ipu_2026_tot / ipu_pleno_tot * 100.0) if ipu_pleno_tot > 0 else 0.0
    brecha_2026 = max(0.0, ipu_pleno_tot - ipu_2026_tot)
    brecha_2027 = max(0.0, ipu_pleno_tot - ipu_2027_tot)
    brecha_cerrada_pct = (
        ((brecha_2026 - brecha_2027) / brecha_2026 * 100.0) if brecha_2026 > 0 else 0.0
    )

    # --- KPI 2: Choque en la cola (1 % y 5 % de mayor IPU 2027) ---
    corte_1 = float(resultado["ipu_2027"].quantile(0.99))
    corte_5 = float(resultado["ipu_2027"].quantile(0.95))
    top1 = resultado[resultado["ipu_2027"] >= corte_1]
    top5 = resultado[resultado["ipu_2027"] >= corte_5]

    aum_total = float(resultado["aumento_pesos"].sum())
    aum_med_top1 = float(top1["aumento_pesos"].median()) if not top1.empty else 0.0
    aum_med_top5 = float(top5["aumento_pesos"].median()) if not top5.empty else 0.0
    part_top1 = (float(top1["aumento_pesos"].sum()) / aum_total * 100.0) if aum_total > 0 else 0.0
    part_top5 = (float(top5["aumento_pesos"].sum()) / aum_total * 100.0) if aum_total > 0 else 0.0

    # --- Meta de recaudo facturado ---
    meta = float(meta_recaudo) if meta_recaudo is not None else ipu_2026_tot
    var_recaudo_pct = ((ipu_2027_tot - ipu_2026_tot) / ipu_2026_tot * 100.0) if ipu_2026_tot > 0 else 0.0
    cumple_meta = ipu_2027_tot >= meta - 1.0

    # --- Recaudo esperado con modelo ML ---
    recaudo_ml: dict[str, Any] = {
        "disponible": probabilidades is not None,
        "modelo_nombre": (modelo_info or {}).get("nombre", "No disponible"),
        "modelo_clase": (modelo_info or {}).get("clase", ""),
        "esperado_2027": None,
        "esperado_2026": None,
        "observado_2026": None,
        "rango_bajo_2027": None,
        "rango_alto_2027": None,
        "tasa_recaudo_esperada_pct": None,
        "desglose_historial": [],
    }
    if prep.OBJETIVO in resultado.columns:
        recaudo_ml["observado_2026"] = float(
            (resultado["ipu_2026"] * resultado[prep.OBJETIVO]).sum()
        )

    if probabilidades is not None:
        probs = np.asarray(probabilidades, dtype=float)
        esp_2027 = mod.recaudo_esperado(resultado["ipu_2027"], probs)
        esp_2026 = mod.recaudo_esperado(resultado["ipu_2026"], probs)
        bajo, alto = mod.intervalo_recaudo_esperado(resultado["ipu_2027"], probs)
        recaudo_ml.update(
            {
                "esperado_2027": esp_2027,
                "esperado_2026": esp_2026,
                "rango_bajo_2027": bajo,
                "rango_alto_2027": alto,
                "tasa_recaudo_esperada_pct": (esp_2027 / ipu_2027_tot * 100.0)
                if ipu_2027_tot > 0
                else 0.0,
            }
        )
        if prep.GRUPO in resultado.columns:
            tmp = resultado[[prep.GRUPO, "ipu_2027", "ipu_2026"]].copy()
            tmp["prob"] = probs
            tmp["esp_2027"] = tmp["ipu_2027"] * tmp["prob"]
            orden_grupos = ["Pagó 2025", "Sin registro 2025", "No pagó 2025"]
            for grp in orden_grupos:
                sub = tmp[tmp[prep.GRUPO] == grp]
                if sub.empty:
                    continue
                recaudo_ml["desglose_historial"].append(
                    {
                        "grupo": grp,
                        "predios": int(len(sub)),
                        "prob_promedio_pct": round(float(sub["prob"].mean() * 100.0), 1),
                        "facturado_2027": float(sub["ipu_2027"].sum()),
                        "esperado_2027": float(sub["esp_2027"].sum()),
                    }
                )

    # --- Gráfica 3 + Guardrail de Progresividad: tarifa efectiva por decil ---
    pos = resultado[resultado["avaluo_catastral"] > 0].copy()
    pos["decil"] = pd.qcut(pos["avaluo_catastral"], 10, labels=list(range(1, 11)))
    tarifa_por_decil: list[dict[str, Any]] = []
    for d in range(1, 11):
        sub = pos[pos["decil"] == d]
        av_sum = float(sub["avaluo_catastral"].sum())
        t_2026 = float(sub["ipu_2026"].sum()) / av_sum * 1000.0 if av_sum > 0 else 0.0
        t_2027 = float(sub["ipu_2027"].sum()) / av_sum * 1000.0 if av_sum > 0 else 0.0
        t_pleno = float(sub["ipu_pleno_2027"].sum()) / av_sum * 1000.0 if av_sum > 0 else 0.0
        tarifa_por_decil.append(
            {
                "decil": d,
                "predios": int(len(sub)),
                "avaluo_mediano_m": round(float(sub["avaluo_catastral"].median() / 1e6), 1),
                "tarifa_2026": round(t_2026, 2),
                "tarifa_2027": round(t_2027, 2),
                "tarifa_plena_2027": round(t_pleno, 2),
            }
        )

    caidas_prog: list[tuple[int, int]] = []
    for i in range(len(tarifa_por_decil) - 1):
        if tarifa_por_decil[i + 1]["tarifa_2027"] < tarifa_por_decil[i]["tarifa_2027"] - 0.05:
            caidas_prog.append((tarifa_por_decil[i]["decil"], tarifa_por_decil[i + 1]["decil"]))

    # --- Guardrail de Legalidad (Ley 44 de 1990) ---
    n_ilegales = int(resultado["supera_tope_legal"].sum())

    # --- Guardrail de Vivienda de menor avalúo (habitacional <= 100 M, tope <= 30 %) ---
    es_vivienda_baja = (
        resultado["grupo_destino"].isin(["Urbano habitacional", "Rural habitacional"])
        & (resultado["avaluo_catastral"] > 0)
        & (resultado["avaluo_catastral"] <= 100_000_000.0)
        & (resultado["ipu_2026"] > 0)
    )
    n_vivienda_supera = int((es_vivienda_baja & (resultado["aumento_pct"] > 0.30 + 1e-6)).sum())
    n_vivienda_baja = int(es_vivienda_baja.sum())

    guardrails = [
        {
            "clave": "legalidad",
            "titulo": "Legalidad",
            "cumple": n_ilegales == 0,
            "predios_afectados": n_ilegales,
            "detalle": (
                "Ningún predio supera el tope legal del doble del impuesto de 2026 (Ley 44)."
                if n_ilegales == 0
                else f"{n_ilegales:,} predios superan el tope legal del doble del impuesto de 2026.".replace(",", " ")
            ),
        },
        {
            "clave": "progresividad",
            "titulo": "Progresividad",
            "cumple": len(caidas_prog) == 0,
            "caidas": caidas_prog,
            "detalle": (
                "La tarifa efectiva es creciente o estable en los 10 deciles de avalúo."
                if len(caidas_prog) == 0
                else (
                    "La tarifa efectiva baja entre los deciles "
                    + ", ".join(f"{a} y {b}" for a, b in caidas_prog[:3])
                    + ("…" if len(caidas_prog) > 3 else ".")
                )
            ),
        },
        {
            "clave": "vivienda_menor_avaluo",
            "titulo": "Vivienda de menor avalúo",
            "cumple": n_vivienda_supera == 0,
            "predios_afectados": n_vivienda_supera,
            "total_grupo": n_vivienda_baja,
            "detalle": (
                f"Ninguno de los {n_vivienda_baja:,} predios habitacionales de hasta $100 M sube más de 30 %.".replace(",", " ")
                if n_vivienda_supera == 0
                else f"{n_vivienda_supera:,} predios habitacionales de hasta $100 M suben más del 30 % vigente en 2026.".replace(",", " ")
            ),
        },
    ]

    # --- Gráfica 1: Brecha cerrada / convergencia por destino ---
    brecha_por_destino: list[dict[str, Any]] = []
    for grp in prep.GRUPOS_DESTINO:
        sub = resultado[resultado["grupo_destino"] == grp]
        if sub.empty:
            continue
        p_pleno = float(sub["ipu_pleno_2027"].sum())
        p_2026 = float(sub["ipu_2026"].sum())
        p_2027 = float(sub["ipu_2027"].sum())
        c26 = p_2026 / p_pleno * 100.0 if p_pleno > 0 else 0.0
        c27 = p_2027 / p_pleno * 100.0 if p_pleno > 0 else 0.0
        b26 = max(0.0, p_pleno - p_2026)
        b27 = max(0.0, p_pleno - p_2027)
        cerrada = ((b26 - b27) / b26 * 100.0) if b26 > 0 else 0.0
        brecha_por_destino.append(
            {
                "destino": grp,
                "predios": int(len(sub)),
                "convergencia_2026_pct": round(c26, 1),
                "convergencia_2027_pct": round(c27, 1),
                "brecha_cerrada_pct": round(cerrada, 1),
                "ipu_2026_mil_m": round(p_2026 / 1e9, 2),
                "ipu_2027_mil_m": round(p_2027 / 1e9, 2),
            }
        )

    # --- Gráfica 2: Distribución del aumento porcentual del IPU ---
    aum_validos = resultado["aumento_pct"].dropna() * 100.0
    cortes = [-np.inf, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0, np.inf]
    etiquetas = [
        "≤ 0 %",
        "0–10 %",
        "10–20 %",
        "20–30 %",
        "30–40 %",
        "40–50 %",
        "50–60 %",
        "60–80 %",
        "80–100 %",
        "> 100 %",
    ]
    conteos = pd.cut(aum_validos, bins=cortes, labels=etiquetas, right=True).value_counts().reindex(
        etiquetas, fill_value=0
    )
    distribucion_aumento = [
        {
            "rango": et,
            "predios": int(cnt),
            "porcentaje": round(float(cnt / len(aum_validos) * 100.0), 1) if len(aum_validos) else 0.0,
        }
        for et, cnt in conteos.items()
    ]
    mediana_aum_pct = float(aum_validos.median()) if not aum_validos.empty else 0.0
    pct_con_tope = float(resultado["limite_aplicado"].mean() * 100.0) if n_predios else 0.0

    # --- Zona 4: Lectura en lenguaje llano ---
    signo_rec = "sube" if var_recaudo_pct >= 0 else "baja"
    frase_ml = (
        f" y, manteniendo el comportamiento de pago observado en 2026 ({recaudo_ml['modelo_nombre']}), "
        f"se recaudarían cerca de {_fmt_mil_m(recaudo_ml['esperado_2027'])} "
        f"(rango estimado: {_fmt_mil_m(recaudo_ml['rango_bajo_2027'])} a {_fmt_mil_m(recaudo_ml['rango_alto_2027'])})"
        if recaudo_ml["disponible"]
        else ""
    )
    incumplidos = [g["titulo"].lower() for g in guardrails if not g["cumple"]]
    frase_guardrails = (
        " El escenario cumple los tres guardrails definidos (legalidad, progresividad y vivienda de menor avalúo)."
        if not incumplidos
        else f" Atención: el escenario presenta alertas en {', '.join(incumplidos)} que deben revisarse antes de radicar el proyecto de acuerdo."
    )
    en_palabras_simples = (
        f"Con este escenario, el IPU facturado alcanza el {conv_2027:.1f} % del impuesto pleno "
        f"(cerrando el {brecha_cerrada_pct:.1f} % de la brecha de 2026). "
        f"La mitad de los predios tiene un aumento de hasta {mediana_aum_pct:.1f} % frente a 2026 "
        f"(con límite aplicado al {pct_con_tope:.1f} % de los predios); en el 1 % de mayor impuesto, "
        f"el aumento mediano es de {_fmt_m(aum_med_top1)}. "
        f"El recaudo facturado {signo_rec} {abs(var_recaudo_pct):.1f} % hasta {_fmt_mil_m(ipu_2027_tot)}"
        f"{frase_ml}.{frase_guardrails}"
    )

    return {
        "n_predios": n_predios,
        "kpis": {
            "convergencia_2027_pct": round(conv_2027, 1),
            "convergencia_2026_pct": round(conv_2026, 1),
            "brecha_cerrada_pct": round(brecha_cerrada_pct, 1),
            "ipu_pleno_2027": ipu_pleno_tot,
            "choque_mediano_top1": aum_med_top1,
            "choque_mediano_top5": aum_med_top5,
            "participacion_aumento_top1_pct": round(part_top1, 1),
            "participacion_aumento_top5_pct": round(part_top5, 1),
            "recaudo_facturado_2026": ipu_2026_tot,
            "recaudo_facturado_2027": ipu_2027_tot,
            "variacion_recaudo_pct": round(var_recaudo_pct, 1),
            "meta_recaudo": meta,
            "cumple_meta": bool(cumple_meta),
            "mediana_aumento_pct": round(mediana_aum_pct, 1),
            "pct_predios_con_tope": round(pct_con_tope, 1),
        },
        "recaudo_esperado": recaudo_ml,
        "guardrails": guardrails,
        "en_palabras_simples": en_palabras_simples,
        "graficas": {
            "brecha_por_destino": brecha_por_destino,
            "distribucion_aumento": distribucion_aumento,
            "tarifa_por_decil": tarifa_por_decil,
        },
    }


# --- Exportación congelada para el Concejo ----------------------------------


def generar_exportacion_congelada(
    escenario: Escenario, resumen: dict[str, Any]
) -> dict[str, Any]:
    """Produce una versión congelada y trazable (hash + HTML autocontenido) del escenario."""
    marca_tiempo = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload_canonico = json.dumps(escenario_a_dict(escenario), sort_keys=True, ensure_ascii=False)
    codigo_version = hashlib.sha256(payload_canonico.encode("utf-8")).hexdigest()[:10]

    kpis = resumen["kpis"]
    rec_ml = resumen["recaudo_esperado"]
    nombre_html = html.escape(escenario.nombre)
    texto_llano = html.escape(resumen["en_palabras_simples"])

    filas_guardrails = "".join(
        f"<tr><td><strong>{html.escape(g['titulo'])}</strong></td>"
        f"<td>{'✓ Cumple' if g['cumple'] else '⚠ Alerta'}</td>"
        f"<td>{html.escape(g['detalle'])}</td></tr>"
        for g in resumen["guardrails"]
    )
    filas_destinos = "".join(
        f"<tr><td>{html.escape(d['destino'])}</td>"
        f"<td style='text-align:right'>{d['predios']:,}</td>"
        f"<td style='text-align:right'>{d['convergencia_2026_pct']:.1f} %</td>"
        f"<td style='text-align:right'>{d['convergencia_2027_pct']:.1f} %</td>"
        f"<td style='text-align:right'>${d['ipu_2027_mil_m']:.2f} mil M</td></tr>".replace(",", " ")
        for d in resumen["graficas"]["brecha_por_destino"]
    )
    filas_deciles = "".join(
        f"<tr><td style='text-align:center'>{d['decil']}</td>"
        f"<td style='text-align:right'>${d['avaluo_mediano_m']:.1f} M</td>"
        f"<td style='text-align:right'>{d['tarifa_2026']:.2f} ‰</td>"
        f"<td style='text-align:right'>{d['tarifa_2027']:.2f} ‰</td></tr>"
        for d in resumen["graficas"]["tarifa_por_decil"]
    )
    bloque_ml = (
        f"<p><strong>Recaudo esperado (modelo {html.escape(rec_ml['modelo_nombre'])}):</strong> "
        f"{_fmt_mil_m(rec_ml['esperado_2027'])} "
        f"(rango conservador: {_fmt_mil_m(rec_ml['rango_bajo_2027'])} – {_fmt_mil_m(rec_ml['rango_alto_2027'])}; "
        f"tasa esperada: {rec_ml['tasa_recaudo_esperada_pct']:.1f} %).</p>"
        if rec_ml["disponible"]
        else "<p><em>Modelo de probabilidad de pago no cargado al momento de la exportación.</em></p>"
    )

    documento_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8" />
<title>Escenario congelado · {nombre_html}</title>
<style>
  body {{ font-family: Arial, 'Liberation Sans', Helvetica, sans-serif; color: #000; margin: 0; background: #fff; }}
  header {{ background: #FFFF00; color: #000; padding: 18px 28px; border-bottom: 3px solid #000; }}
  header h1 {{ margin: 0; font-size: 20px; }}
  header p {{ margin: 4px 0 0; font-size: 13px; }}
  main {{ max-width: 920px; margin: 24px auto; padding: 0 24px 36px; }}
  h2 {{ font-size: 16px; border-bottom: 3px solid #FFFF00; padding-bottom: 4px; margin-top: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 14px 0; }}
  .card {{ border: 1px solid #000; padding: 12px; }}
  .card .lbl {{ font-size: 11px; text-transform: uppercase; color: #555; }}
  .card .val {{ font-size: 22px; font-weight: bold; margin-top: 4px; }}
  .llano {{ background: #f8f8f8; border-left: 5px solid #FFFF00; padding: 12px 16px; line-height: 1.5; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
  th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
  th {{ background: #000; color: #fff; }}
  footer {{ margin-top: 28px; font-size: 11px; color: #555; border-top: 1px solid #ccc; padding-top: 10px; }}
</style>
</head>
<body>
<header>
  <h1>Transición predial 2027 — Escenario congelado</h1>
  <p>{nombre_html} · Versión <code>{codigo_version}</code> · Generado: {marca_tiempo} · Un municipio colombiano ({resumen['n_predios']:,} predios privados facturados)</p>
</header>
<main>
  <h2>Lectura en lenguaje llano</h2>
  <div class="llano">{texto_llano}</div>

  <h2>Indicadores principales</h2>
  <div class="grid">
    <div class="card"><div class="lbl">KPI 1 · Convergencia</div><div class="val">{kpis['convergencia_2027_pct']:.1f} %</div><div>IPU pleno · 2026: {kpis['convergencia_2026_pct']:.1f} %</div></div>
    <div class="card"><div class="lbl">KPI 2 · Choque en el 1 % superior</div><div class="val">+{_fmt_m(kpis['choque_mediano_top1'])}</div><div>Mediana 5 % superior: +{_fmt_m(kpis['choque_mediano_top5'])}</div></div>
    <div class="card"><div class="lbl">Meta · Recaudo facturado 2027</div><div class="val">{_fmt_mil_m(kpis['recaudo_facturado_2027'])}</div><div>Frente a 2026: {kpis['variacion_recaudo_pct']:+.1f} %</div></div>
  </div>
  {bloque_ml}

  <h2>Verificación de guardrails</h2>
  <table><thead><tr><th>Guardrail</th><th>Estado</th><th>Detalle</th></tr></thead><tbody>{filas_guardrails}</tbody></table>

  <h2>Convergencia por grupo de destino</h2>
  <table><thead><tr><th>Grupo</th><th style="text-align:right">Predios</th><th style="text-align:right">Conv. 2026</th><th style="text-align:right">Conv. 2027</th><th style="text-align:right">IPU 2027</th></tr></thead><tbody>{filas_destinos}</tbody></table>

  <h2>Progresividad: tarifa efectiva por decil de avalúo</h2>
  <table><thead><tr><th style="text-align:center">Decil</th><th style="text-align:right">Avalúo mediano</th><th style="text-align:right">Tarifa ef. 2026</th><th style="text-align:right">Tarifa ef. 2027</th></tr></thead><tbody>{filas_deciles}</tbody></table>

  <footer>
    <strong>Nota metodológica y de privacidad:</strong> Documento de cifras estrictamente agregadas para sustentación técnica ante el Concejo Municipal (Ley 1581 de 2012 y Ley 1712 de 2014). El recaudo esperado es una estimación basada en patrones de pago observados en 2026 y no modela cambios de comportamiento ante aumentos tarifarios distintos.
  </footer>
</main>
</body>
</html>"""

    return {
        "codigo_version": codigo_version,
        "generado_utc": marca_tiempo,
        "nombre_archivo": f"escenario-2027-{codigo_version}.html",
        "escenario": escenario_a_dict(escenario),
        "resumen": resumen,
        "html": documento_html,
    }
