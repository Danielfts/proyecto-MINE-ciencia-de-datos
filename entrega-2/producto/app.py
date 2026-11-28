"""Aplicación web del producto de datos: interfaz interactiva para Multiaservi Consultores.

Organizada en dos pestañas que consumen la API REST (`api.py`):
1. Simulador de escenarios 2027 — sigue las cinco zonas del wireframe de la sección 2
   del reporte: (1) tarifas por mil y límites de crecimiento; (2) alertas de guardrails;
   (3) indicadores del escenario y recaudo esperado (modelo ML); (4) lectura en palabras
   simples; (5) gráficas, más comparación entre escenarios y exportación congelada.
2. Perfil de predio hipotético — permite ingresar un perfil sintético (sin consultar
   predios ni personas reales) para ver el cálculo determinista (antes vs. después) y la
   probabilidad de pago estimada por el modelo ML activo.

Identidad visual (identidad/README.md): amarillo (#FFFF00), negro (#000000), blanco y
tipografía Arial/sin serifas. Nunca texto blanco sobre amarillo ni mención al municipio.

Uso desde la raíz del repositorio (con la API corriendo en http://127.0.0.1:8000):

    uv run python entrega-2/producto/app.py

Variables de entorno (útiles para Docker):
- API_URL: URL base de FastAPI (por defecto http://127.0.0.1:8000)
- HOST: interfaz de escucha de Dash (por defecto 127.0.0.1; usar 0.0.0.0 en Docker)
- PORT: puerto de Dash (por defecto 8050)
- DASH_DEBUG: "true"/"false" (por defecto false)
"""

from __future__ import annotations

import copy
import os
from typing import Any

import plotly.graph_objects as go
import requests
from dash import ALL, Dash, Input, Output, State, ctx, dash_table, dcc, html

import motor
import preparacion as prep

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000").rstrip("/")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8050"))
DEBUG = os.environ.get("DASH_DEBUG", "false").lower() in ("1", "true", "yes")

# Identidad visual (identidad/README.md)
AMARILLO = "#FFFF00"
NEGRO = "#000000"
BLANCO = "#FFFFFF"
GRIS_FONDO = "#F5F5F5"
GRIS_BORDE = "#D4D4D4"
GRIS_TEXTO = "#555555"
AZUL = "#2A78D6"
FUENTE = "Arial, 'Liberation Sans', Helvetica, sans-serif"

ESCENARIOS_INICIALES = {
    k: motor.escenario_a_dict(v) for k, v in motor.escenarios_predefinidos().items()
}
CLAVE_INICIAL = "progresivo_2027"
TARIFAS_REF_2026 = motor.TARIFAS_REFERENCIA_2026

DESTINACIONES_OPCIONES = [
    {"label": "Habitacional", "value": "Habitacional"},
    {"label": "Comercial", "value": "Comercial"},
    {"label": "Industrial", "value": "Industrial"},
    {"label": "Agrícola", "value": "Agricola"},
    {"label": "Agropecuario", "value": "Agropecuario"},
    {"label": "Lote urbanizado no construido", "value": "Lote_Urbanizado_No_Construido"},
    {"label": "Lote urbanizable no urbanizado", "value": "Lote_Urbanizable_No_Urbanizado"},
    {"label": "Forestal", "value": "Forestal"},
    {"label": "Institucional", "value": "Institucional"},
    {"label": "Educativo", "value": "Educativo"},
    {"label": "Recreacional", "value": "Recreacional"},
]

CONDICIONES_OPCIONES = [
    {"label": "NPH (No Propiedad Horizontal)", "value": "NPH"},
    {"label": "Propiedad Horizontal (unidad)", "value": "PH.Unidad_Predial"},
    {"label": "Condominio (unidad)", "value": "Condominio.Unidad_Predial"},
    {"label": "Informal", "value": "Informal"},
]

HISTORIAL_OPCIONES = [
    {"label": "Pagó 2025", "value": "Pagó 2025"},
    {"label": "Sin registro 2025 (predio nuevo / desenglobe)", "value": "Sin registro 2025"},
    {"label": "No pagó 2025", "value": "No pagó 2025"},
]

NOVEDAD_OPCIONES = [
    {"label": "Sin novedad", "value": "Sin_Novedad"},
    {"label": "Predio nuevo", "value": "Predio_Nuevo"},
    {"label": "Desenglobe", "value": "Desenglobe"},
    {"label": "Englobe", "value": "Englobe"},
    {"label": "Cambio número predial", "value": "Cambio_Numero_Predial"},
]


# --- Utilidades de formato y cliente HTTP -----------------------------------


def _fmt_cop(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"${valor:,.0f}".replace(",", " ")


def _fmt_m(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"${valor / 1e6:,.1f} M".replace(",", " ")


def _fmt_mil_m(valor: float | None) -> str:
    if valor is None:
        return "—"
    return f"${valor / 1e9:,.1f} mil M".replace(",", " ")


def _api_get(ruta: str, timeout: float = 5.0) -> tuple[dict[str, Any] | None, str | None]:
    try:
        resp = requests.get(f"{API_URL}{ruta}", timeout=timeout)
        resp.raise_for_status()
        return resp.json(), None
    except requests.RequestException as exc:
        return None, f"No se pudo conectar con la API ({API_URL}): {exc}"


def _api_post(
    ruta: str, payload: dict[str, Any] | None = None, timeout: float = 15.0
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        resp = requests.post(f"{API_URL}{ruta}", json=payload, timeout=timeout)
        if not resp.ok:
            try:
                detalle = resp.json().get("detail", resp.text)
            except ValueError:
                detalle = resp.text
            return None, f"Error {resp.status_code}: {detalle}"
        return resp.json(), None
    except requests.RequestException as exc:
        return None, f"No se pudo conectar con la API ({API_URL}): {exc}"


def _tarifas_a_filas(escenario: dict[str, Any], destino: str) -> list[dict[str, Any]]:
    rangos = [t for t in escenario.get("tarifas", []) if t.get("destino") == destino]
    rangos.sort(key=lambda r: float(r.get("avaluo_desde", 0)))
    refs = TARIFAS_REF_2026.get(destino, [])
    filas: list[dict[str, Any]] = []
    for idx, r in enumerate(rangos):
        desde_m = round(float(r["avaluo_desde"]) / 1e6, 1)
        hasta = r.get("avaluo_hasta")
        hasta_txt = "en adelante" if hasta is None else str(round(float(hasta) / 1e6, 1))
        ref_val = refs[idx] if idx < len(refs) else (refs[-1] if refs else None)
        filas.append(
            {
                "desde_m": desde_m,
                "hasta_m": hasta_txt,
                "tarifa_2027": round(float(r["tarifa_por_mil"]), 2),
                "tarifa_2026": f"{ref_val:.1f} ‰" if ref_val is not None else "—",
            }
        )
    return filas


def _limites_a_filas(escenario: dict[str, Any]) -> list[dict[str, Any]]:
    limites = sorted(
        escenario.get("limites", []), key=lambda r: float(r.get("avaluo_desde", 0))
    )
    if not limites:
        return [{"desde_m": 0.0, "hasta_m": "en adelante", "limite_pct": "Sin límite"}]
    filas: list[dict[str, Any]] = []
    for r in limites:
        hasta = r.get("avaluo_hasta")
        filas.append(
            {
                "desde_m": round(float(r["avaluo_desde"]) / 1e6, 1),
                "hasta_m": "en adelante" if hasta is None else str(round(float(hasta) / 1e6, 1)),
                "limite_pct": round(float(r["aumento_maximo"]) * 100.0, 1),
            }
        )
    return filas


def _parse_hasta_m(valor: Any) -> float | None:
    if valor is None:
        return None
    txt = str(valor).strip().lower()
    if txt in ("", "en adelante", "none", "inf", "sin tope", "-"):
        return None
    try:
        num = float(txt.replace(",", "."))
        return num * 1e6 if num > 0 else None
    except ValueError:
        return None


# --- Estilos reutilizables --------------------------------------------------

ESTILO_TARJETA = {
    "background": BLANCO,
    "border": f"1px solid {GRIS_BORDE}",
    "borderRadius": "6px",
    "padding": "14px 16px",
}

ESTILO_INSIGNIA_NUM = {
    "display": "inline-flex",
    "alignItems": "center",
    "justifyContent": "center",
    "width": "22px",
    "height": "22px",
    "borderRadius": "50%",
    "background": NEGRO,
    "color": BLANCO,
    "fontSize": "12px",
    "fontWeight": "bold",
    "marginRight": "8px",
    "flexShrink": 0,
}

ESTILO_BOTON_SEC = {
    "background": BLANCO,
    "color": NEGRO,
    "border": f"1px solid {NEGRO}",
    "borderRadius": "4px",
    "padding": "7px 12px",
    "fontSize": "13px",
    "fontWeight": "600",
    "cursor": "pointer",
    "fontFamily": FUENTE,
}

ESTILO_BOTON_PRI = {
    "background": NEGRO,
    "color": BLANCO,
    "border": f"1px solid {NEGRO}",
    "borderRadius": "4px",
    "padding": "7px 14px",
    "fontSize": "13px",
    "fontWeight": "600",
    "cursor": "pointer",
    "fontFamily": FUENTE,
}


def _titulo_zona(numero: int, titulo: str, subtitulo: str | None = None) -> html.Div:
    items: list[Any] = [
        html.Span(str(numero), style=ESTILO_INSIGNIA_NUM),
        html.Span(titulo, style={"fontWeight": "700", "fontSize": "15px", "color": NEGRO}),
    ]
    if subtitulo:
        items.append(
            html.Span(
                f"  {subtitulo}",
                style={"fontSize": "12px", "color": GRIS_TEXTO, "marginLeft": "6px"},
            )
        )
    return html.Div(
        items,
        style={"display": "flex", "alignItems": "center", "marginBottom": "10px", "flexWrap": "wrap"},
    )


def _fig_vacia(mensaje: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=mensaje,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font={"family": FUENTE, "size": 13, "color": GRIS_TEXTO},
    )
    fig.update_layout(
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        xaxis={"visible": False},
        yaxis={"visible": False},
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        height=240,
    )
    return fig


# --- Aplicación Dash --------------------------------------------------------

app = Dash(__name__, title="Transición predial 2027", suppress_callback_exceptions=True)

app.layout = html.Div(
    [
        # Estado en cliente
        dcc.Store(id="store-escenario", data=copy.deepcopy(ESCENARIOS_INICIALES[CLAVE_INICIAL])),
        dcc.Store(id="store-destino-activo", data=prep.GRUPOS_DESTINO[0]),
        dcc.Store(id="store-ultimo-resultado", data=None),
        dcc.Store(id="store-mostrar-comparacion", data=False),
        dcc.Download(id="descarga-exportacion"),
        # Encabezado institucional (franja amarilla, texto negro, sin nombre de municipio)
        html.Header(
            [
                html.Div(
                    [
                        html.H1(
                            "Transición predial 2027",
                            style={"margin": 0, "fontSize": "20px", "fontWeight": "700"},
                        ),
                        html.Div(
                            "Simulador de escenarios · uso interno de la consultora · un municipio colombiano",
                            style={"fontSize": "12px", "color": NEGRO, "marginTop": "2px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Span(
                            id="estado-api",
                            style={
                                "fontSize": "12px",
                                "fontWeight": "600",
                                "background": BLANCO,
                                "color": NEGRO,
                                "border": f"1px solid {NEGRO}",
                                "borderRadius": "4px",
                                "padding": "5px 10px",
                            },
                        ),
                        html.Button(
                            "Recargar modelo",
                            id="btn-recargar-modelo",
                            n_clicks=0,
                            style={**ESTILO_BOTON_SEC, "padding": "5px 10px", "fontSize": "12px"},
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center", "gap": "8px", "flexWrap": "wrap"},
                ),
            ],
            style={
                "background": AMARILLO,
                "color": NEGRO,
                "padding": "12px 24px",
                "borderBottom": f"3px solid {NEGRO}",
                "display": "flex",
                "justifyContent": "space-between",
                "alignItems": "center",
                "flexWrap": "wrap",
                "gap": "10px",
            },
        ),
        # Pestañas principales
        dcc.Tabs(
            id="pestana-activa",
            value="escenarios",
            style={"fontFamily": FUENTE, "borderBottom": f"1px solid {GRIS_BORDE}"},
            children=[
                dcc.Tab(
                    label="1. Simulador de escenarios 2027 (agregado)",
                    value="escenarios",
                    style={"padding": "10px 18px", "fontWeight": "600", "background": GRIS_FONDO, "color": NEGRO},
                    selected_style={
                        "padding": "10px 18px",
                        "fontWeight": "700",
                        "background": BLANCO,
                        "color": NEGRO,
                        "borderTop": f"3px solid {NEGRO}",
                    },
                ),
                dcc.Tab(
                    label="2. Perfil de predio hipotético (determinista + modelo ML)",
                    value="hipotetico",
                    style={"padding": "10px 18px", "fontWeight": "600", "background": GRIS_FONDO, "color": NEGRO},
                    selected_style={
                        "padding": "10px 18px",
                        "fontWeight": "700",
                        "background": BLANCO,
                        "color": NEGRO,
                        "borderTop": f"3px solid {NEGRO}",
                    },
                ),
            ],
        ),
        # Contenedor principal
        html.Main(
            [
                # ===================== PESTAÑA 1: ESCENARIOS =====================
                html.Div(
                    id="vista-escenarios",
                    children=[
                        # Barra de control de escenarios
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label(
                                            "Escenario base:",
                                            style={"fontSize": "12px", "fontWeight": "700", "marginRight": "8px"},
                                        ),
                                        dcc.Dropdown(
                                            id="dropdown-escenario",
                                            options=[
                                                {"label": v["nombre"], "value": k}
                                                for k, v in ESCENARIOS_INICIALES.items()
                                            ],
                                            value=CLAVE_INICIAL,
                                            clearable=False,
                                            style={"minWidth": "340px", "fontSize": "13px"},
                                        ),
                                    ],
                                    style={"display": "flex", "alignItems": "center", "flexWrap": "wrap", "gap": "6px"},
                                ),
                                html.Div(
                                    [
                                        html.Label(
                                            "Nombre:",
                                            style={"fontSize": "12px", "fontWeight": "700"},
                                        ),
                                        dcc.Input(
                                            id="input-nombre-escenario",
                                            type="text",
                                            value=ESCENARIOS_INICIALES[CLAVE_INICIAL]["nombre"],
                                            style={
                                                "padding": "6px 10px",
                                                "border": f"1px solid {GRIS_BORDE}",
                                                "borderRadius": "4px",
                                                "width": "270px",
                                                "fontSize": "13px",
                                                "fontFamily": FUENTE,
                                            },
                                        ),
                                    ],
                                    style={"display": "flex", "alignItems": "center", "gap": "6px"},
                                ),
                                html.Div(
                                    [
                                        html.Button(
                                            "Comparar escenarios",
                                            id="btn-comparar",
                                            n_clicks=0,
                                            style=ESTILO_BOTON_SEC,
                                        ),
                                        html.Button(
                                            "Exportar escenario congelado",
                                            id="btn-exportar",
                                            n_clicks=0,
                                            style=ESTILO_BOTON_PRI,
                                        ),
                                    ],
                                    style={"display": "flex", "gap": "8px", "flexWrap": "wrap"},
                                ),
                            ],
                            style={
                                **ESTILO_TARJETA,
                                "display": "flex",
                                "justifyContent": "space-between",
                                "alignItems": "center",
                                "flexWrap": "wrap",
                                "gap": "12px",
                                "marginBottom": "16px",
                            },
                        ),
                        # Banner de error API (oculto si todo está bien)
                        html.Div(id="banner-error-api", style={"marginBottom": "12px"}),
                        # Cuadrícula principal (2 columnas como en mockup.png)
                        html.Div(
                            [
                                # -------- Columna izquierda: Zonas 1 y 2 --------
                                html.Div(
                                    [
                                        # Zona 1: Tarifas por mil
                                        html.Section(
                                            [
                                                _titulo_zona(1, "Tarifas por mil"),
                                                html.Div(
                                                    [
                                                        html.Button(
                                                            grp,
                                                            id={"type": "pill-destino", "index": grp},
                                                            n_clicks=0,
                                                            style={
                                                                "borderRadius": "999px",
                                                                "padding": "5px 11px",
                                                                "fontSize": "12px",
                                                                "fontWeight": "600",
                                                                "cursor": "pointer",
                                                                "fontFamily": FUENTE,
                                                                "border": f"1px solid {NEGRO}",
                                                                "background": NEGRO
                                                                if grp == prep.GRUPOS_DESTINO[0]
                                                                else BLANCO,
                                                                "color": BLANCO
                                                                if grp == prep.GRUPOS_DESTINO[0]
                                                                else NEGRO,
                                                            },
                                                        )
                                                        for grp in prep.GRUPOS_DESTINO
                                                    ],
                                                    style={
                                                        "display": "flex",
                                                        "flexWrap": "wrap",
                                                        "gap": "6px",
                                                        "marginBottom": "12px",
                                                    },
                                                ),
                                                dash_table.DataTable(
                                                    id="tabla-tarifas",
                                                    columns=[
                                                        {
                                                            "name": "Avalúo desde (M)",
                                                            "id": "desde_m",
                                                            "type": "numeric",
                                                            "editable": True,
                                                        },
                                                        {
                                                            "name": "Hasta (M)",
                                                            "id": "hasta_m",
                                                            "type": "text",
                                                            "editable": True,
                                                        },
                                                        {
                                                            "name": "Tarifa 2027 (‰)",
                                                            "id": "tarifa_2027",
                                                            "type": "numeric",
                                                            "editable": True,
                                                        },
                                                        {
                                                            "name": "Ref. 2026",
                                                            "id": "tarifa_2026",
                                                            "type": "text",
                                                            "editable": False,
                                                        },
                                                    ],
                                                    data=_tarifas_a_filas(
                                                        ESCENARIOS_INICIALES[CLAVE_INICIAL],
                                                        prep.GRUPOS_DESTINO[0],
                                                    ),
                                                    editable=True,
                                                    row_deletable=False,
                                                    style_table={"overflowX": "auto"},
                                                    style_cell={
                                                        "fontFamily": FUENTE,
                                                        "fontSize": "12px",
                                                        "padding": "6px 8px",
                                                        "textAlign": "right",
                                                        "color": NEGRO,
                                                        "border": f"1px solid {GRIS_BORDE}",
                                                    },
                                                    style_header={
                                                        "fontWeight": "700",
                                                        "background": GRIS_FONDO,
                                                        "color": NEGRO,
                                                        "textAlign": "center",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {"column_id": "tarifa_2027"},
                                                            "backgroundColor": "#FFFDF0",
                                                            "fontWeight": "700",
                                                            "border": f"1px solid {NEGRO}",
                                                        },
                                                        {
                                                            "if": {"column_id": "tarifa_2026"},
                                                            "color": GRIS_TEXTO,
                                                        },
                                                    ],
                                                ),
                                                html.Div(
                                                    [
                                                        html.Button(
                                                            "+ Agregar rango",
                                                            id="btn-agregar-rango",
                                                            n_clicks=0,
                                                            style={
                                                                **ESTILO_BOTON_SEC,
                                                                "fontSize": "12px",
                                                                "padding": "5px 10px",
                                                                "borderStyle": "dashed",
                                                            },
                                                        ),
                                                        html.Span(
                                                            "Edite los valores en amarillo y presione Enter.",
                                                            style={"fontSize": "11px", "color": GRIS_TEXTO},
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex",
                                                        "justifyContent": "space-between",
                                                        "alignItems": "center",
                                                        "marginTop": "10px",
                                                        "gap": "8px",
                                                        "flexWrap": "wrap",
                                                    },
                                                ),
                                            ],
                                            style={**ESTILO_TARJETA, "marginBottom": "14px"},
                                        ),
                                        # Límites de crecimiento del IPU
                                        html.Section(
                                            [
                                                html.Div(
                                                    "Límites de crecimiento del IPU",
                                                    style={"fontWeight": "700", "fontSize": "15px"},
                                                ),
                                                html.Div(
                                                    "Aumento máximo frente al impuesto de 2026, según el avalúo (tope legal Ley 44: 100 %).",
                                                    style={
                                                        "fontSize": "12px",
                                                        "color": GRIS_TEXTO,
                                                        "margin": "4px 0 10px",
                                                    },
                                                ),
                                                dash_table.DataTable(
                                                    id="tabla-limites",
                                                    columns=[
                                                        {
                                                            "name": "Avalúo desde (M)",
                                                            "id": "desde_m",
                                                            "type": "numeric",
                                                            "editable": True,
                                                        },
                                                        {
                                                            "name": "Hasta (M)",
                                                            "id": "hasta_m",
                                                            "type": "text",
                                                            "editable": True,
                                                        },
                                                        {
                                                            "name": "Límite 2027 (%)",
                                                            "id": "limite_pct",
                                                            "type": "text",
                                                            "editable": True,
                                                        },
                                                    ],
                                                    data=_limites_a_filas(
                                                        ESCENARIOS_INICIALES[CLAVE_INICIAL]
                                                    ),
                                                    editable=True,
                                                    style_table={"overflowX": "auto"},
                                                    style_cell={
                                                        "fontFamily": FUENTE,
                                                        "fontSize": "12px",
                                                        "padding": "6px 8px",
                                                        "textAlign": "right",
                                                        "color": NEGRO,
                                                        "border": f"1px solid {GRIS_BORDE}",
                                                    },
                                                    style_header={
                                                        "fontWeight": "700",
                                                        "background": GRIS_FONDO,
                                                        "color": NEGRO,
                                                        "textAlign": "center",
                                                    },
                                                    style_data_conditional=[
                                                        {
                                                            "if": {"column_id": "limite_pct"},
                                                            "backgroundColor": "#FFFDF0",
                                                            "fontWeight": "700",
                                                            "border": f"1px solid {NEGRO}",
                                                        }
                                                    ],
                                                ),
                                            ],
                                            style={**ESTILO_TARJETA, "marginBottom": "14px"},
                                        ),
                                        # Zona 2: Alertas de guardrails
                                        html.Section(
                                            [
                                                _titulo_zona(2, "Alertas de guardrails"),
                                                html.Div(id="contenedor-guardrails"),
                                            ],
                                            style=ESTILO_TARJETA,
                                        ),
                                    ],
                                    style={"minWidth": "0"},
                                ),
                                # -------- Columna derecha: Zonas 3, 4 y 5 --------
                                html.Div(
                                    [
                                        # Zona 3: Indicadores del escenario
                                        html.Section(
                                            [
                                                _titulo_zona(
                                                    3,
                                                    "Indicadores del escenario",
                                                    "frente a la línea base 2026",
                                                ),
                                                html.Div(id="contenedor-kpis"),
                                                html.Div(
                                                    id="contenedor-recaudo-ml",
                                                    style={"marginTop": "12px"},
                                                ),
                                            ],
                                            style={**ESTILO_TARJETA, "marginBottom": "14px"},
                                        ),
                                        # Zona 4: En palabras simples
                                        html.Section(
                                            [
                                                _titulo_zona(4, "En palabras simples"),
                                                html.Div(
                                                    id="texto-palabras-simples",
                                                    style={
                                                        "fontSize": "14px",
                                                        "lineHeight": "1.55",
                                                        "color": NEGRO,
                                                        "borderLeft": f"4px solid {AMARILLO}",
                                                        "paddingLeft": "12px",
                                                    },
                                                ),
                                            ],
                                            style={**ESTILO_TARJETA, "marginBottom": "14px"},
                                        ),
                                        # Panel de comparación (visible al pulsar "Comparar escenarios")
                                        html.Div(
                                            id="panel-comparacion",
                                            style={"display": "none", "marginBottom": "14px"},
                                        ),
                                        # Zona 5: Gráficas
                                        html.Section(
                                            [
                                                _titulo_zona(5, "Gráficas"),
                                                html.Div(
                                                    [
                                                        html.Div(
                                                            dcc.Graph(
                                                                id="grafica-brecha",
                                                                config={"displayModeBar": False},
                                                            ),
                                                            style={
                                                                "border": f"1px solid {GRIS_BORDE}",
                                                                "borderRadius": "6px",
                                                                "padding": "6px",
                                                                "background": BLANCO,
                                                            },
                                                        ),
                                                        html.Div(
                                                            dcc.Graph(
                                                                id="grafica-aumento",
                                                                config={"displayModeBar": False},
                                                            ),
                                                            style={
                                                                "border": f"1px solid {GRIS_BORDE}",
                                                                "borderRadius": "6px",
                                                                "padding": "6px",
                                                                "background": BLANCO,
                                                            },
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "grid",
                                                        "gridTemplateColumns": "repeat(auto-fit, minmax(290px, 1fr))",
                                                        "gap": "12px",
                                                        "marginBottom": "12px",
                                                    },
                                                ),
                                                html.Div(
                                                    dcc.Graph(
                                                        id="grafica-deciles",
                                                        config={"displayModeBar": False},
                                                    ),
                                                    style={
                                                        "border": f"1px solid {GRIS_BORDE}",
                                                        "borderRadius": "6px",
                                                        "padding": "6px",
                                                        "background": BLANCO,
                                                    },
                                                ),
                                            ],
                                            style=ESTILO_TARJETA,
                                        ),
                                    ],
                                    style={"minWidth": "0"},
                                ),
                            ],
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "minmax(340px, 1fr) minmax(520px, 2fr)",
                                "gap": "16px",
                                "alignItems": "start",
                            },
                        ),
                    ],
                ),
                # ===================== PESTAÑA 2: PERFIL HIPOTÉTICO =====================
                html.Div(
                    id="vista-hipotetico",
                    style={"display": "none"},
                    children=[
                        html.Div(
                            [
                                html.Strong("Perfil sintético ilustrativo · "),
                                html.Span(
                                    "Esta vista permite probar las dos partes del producto "
                                    "(motor determinista + modelo de probabilidad de pago) sobre "
                                    "un predio hipotético con el escenario configurado en la "
                                    "pestaña 1. No consulta registros reales ni atribuye riesgo a "
                                    "contribuyentes individuales (Ley 1581 de 2012)."
                                ),
                            ],
                            style={
                                "background": "#FFFDE6",
                                "border": f"1px solid {NEGRO}",
                                "borderLeft": f"6px solid {AMARILLO}",
                                "padding": "10px 14px",
                                "borderRadius": "4px",
                                "fontSize": "13px",
                                "marginBottom": "16px",
                            },
                        ),
                        html.Div(
                            [
                                # Formulario del perfil hipotético
                                html.Section(
                                    [
                                        html.H2(
                                            "Características del predio hipotético",
                                            style={
                                                "fontSize": "16px",
                                                "margin": "0 0 12px",
                                                "borderBottom": f"3px solid {AMARILLO}",
                                                "paddingBottom": "4px",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Div(
                                                    [
                                                        html.Label("Avalúo catastral (millones COP)", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-avaluo-m", type="number", value=240, min=1, step=5, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("IPU facturado en 2026 (miles COP)", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-ipu2026-k", type="number", value=580, min=0, step=10, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Destinación económica", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(id="hip-destino", options=DESTINACIONES_OPCIONES, value="Habitacional", clearable=False, style={"marginTop": "4px", "fontSize": "13px"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Zona", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(id="hip-zona", options=[{"label": "Urbano", "value": "Urbano"}, {"label": "Rural", "value": "Rural"}], value="Urbano", clearable=False, style={"marginTop": "4px", "fontSize": "13px"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Condición del predio", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(id="hip-condicion", options=CONDICIONES_OPCIONES, value="NPH", clearable=False, style={"marginTop": "4px", "fontSize": "13px"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Historial de pago 2025", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(id="hip-historial", options=HISTORIAL_OPCIONES, value="Pagó 2025", clearable=False, style={"marginTop": "4px", "fontSize": "13px"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Área construida (m²)", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-area-const", type="number", value=120, min=0, step=10, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Área de terreno (m²)", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-area-terr", type="number", value=160, min=0, step=10, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Pisos del edificio", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-pisos", type="number", value=2, min=0, max=40, step=1, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Año de construcción", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-anio", type="number", value=2015, min=1940, max=2026, step=1, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Novedad número predial", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(id="hip-novedad", options=NOVEDAD_OPCIONES, value="Sin_Novedad", clearable=False, style={"marginTop": "4px", "fontSize": "13px"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Predios del mismo titular", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Input(id="hip-predios-titular", type="number", value=1, min=1, max=500, step=1, style={"width": "100%", "padding": "6px", "marginTop": "4px", "boxSizing": "border-box"}),
                                                    ]
                                                ),
                                                html.Div(
                                                    [
                                                        html.Label("Tipo de titular", style={"fontSize": "12px", "fontWeight": "700"}),
                                                        dcc.Dropdown(
                                                            id="hip-juridico",
                                                            options=[
                                                                {"label": "Persona natural", "value": "natural"},
                                                                {"label": "Persona jurídica", "value": "juridica"},
                                                            ],
                                                            value="natural",
                                                            clearable=False,
                                                            style={"marginTop": "4px", "fontSize": "13px"},
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "repeat(auto-fit, minmax(190px, 1fr))",
                                                "gap": "12px",
                                            },
                                        ),
                                        html.Div(
                                            html.Button(
                                                "Simular perfil hipotético",
                                                id="btn-simular-hipotetico",
                                                n_clicks=0,
                                                style={**ESTILO_BOTON_PRI, "marginTop": "14px", "width": "100%", "padding": "10px"},
                                            )
                                        ),
                                    ],
                                    style=ESTILO_TARJETA,
                                ),
                                # Resultados del perfil hipotético
                                html.Div(id="resultados-hipotetico"),
                            ],
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "minmax(340px, 1fr) minmax(420px, 1.3fr)",
                                "gap": "16px",
                                "alignItems": "start",
                            },
                        ),
                    ],
                ),
            ],
            style={"padding": "18px 24px 36px", "maxWidth": "1480px", "margin": "0 auto"},
        ),
    ],
    style={
        "fontFamily": FUENTE,
        "color": NEGRO,
        "background": GRIS_FONDO,
        "minHeight": "100vh",
        "margin": 0,
    },
)


# --- Callbacks --------------------------------------------------------------


@app.callback(
    Output("vista-escenarios", "style"),
    Output("vista-hipotetico", "style"),
    Input("pestana-activa", "value"),
)
def cambiar_pestana(pestana: str):
    if pestana == "hipotetico":
        return {"display": "none"}, {"display": "block"}
    return {"display": "block"}, {"display": "none"}


@app.callback(
    Output("estado-api", "children"),
    Input("estado-api", "id"),
    Input("btn-recargar-modelo", "n_clicks"),
)
def actualizar_estado_api(_, n_recargas: int):
    if ctx.triggered_id == "btn-recargar-modelo" and n_recargas:
        _api_post("/modelo/recargar")
    salud, err = _api_get("/salud", timeout=3.0)
    if err or not salud:
        return f"API sin respuesta en {API_URL}"
    n_pred = salud.get("n_predios", 0)
    info_mod = salud.get("modelo")
    if info_mod:
        mod_txt = info_mod.get("nombre", "Modelo listo")
    else:
        mod_txt = "modelo pendiente"
    return f"API en línea · {n_pred:,} predios · Modelo: {mod_txt}".replace(",", " ")


@app.callback(
    Output("store-escenario", "data"),
    Output("store-destino-activo", "data"),
    Output("input-nombre-escenario", "value"),
    Output("tabla-tarifas", "data"),
    Output("tabla-limites", "data"),
    Output({"type": "pill-destino", "index": ALL}, "style"),
    Input("dropdown-escenario", "value"),
    Input("input-nombre-escenario", "value"),
    Input({"type": "pill-destino", "index": ALL}, "n_clicks"),
    Input("tabla-tarifas", "data"),
    Input("tabla-limites", "data"),
    Input("btn-agregar-rango", "n_clicks"),
    State("store-escenario", "data"),
    State("store-destino-activo", "data"),
    State({"type": "pill-destino", "index": ALL}, "id"),
)
def sincronizar_escenario(
    clave_escenario: str,
    nombre_txt: str,
    _clicks_pills,
    filas_tarifas: list[dict[str, Any]],
    filas_limites: list[dict[str, Any]],
    _clicks_agregar: int,
    escenario_actual: dict[str, Any],
    destino_activo: str,
    ids_pills: list[dict[str, str]],
):
    disparador = ctx.triggered_id
    escenario = copy.deepcopy(escenario_actual or ESCENARIOS_INICIALES[CLAVE_INICIAL])
    destino = destino_activo or prep.GRUPOS_DESTINO[0]

    if disparador == "dropdown-escenario" and clave_escenario in ESCENARIOS_INICIALES:
        escenario = copy.deepcopy(ESCENARIOS_INICIALES[clave_escenario])
        nombre_out = escenario["nombre"]
        filas_tar_out = _tarifas_a_filas(escenario, destino)
        filas_lim_out = _limites_a_filas(escenario)
    elif isinstance(disparador, dict) and disparador.get("type") == "pill-destino":
        destino = disparador["index"]
        nombre_out = escenario["nombre"]
        filas_tar_out = _tarifas_a_filas(escenario, destino)
        filas_lim_out = _limites_a_filas(escenario)
    elif disparador == "input-nombre-escenario":
        escenario["nombre"] = nombre_txt or "Escenario personalizado"
        nombre_out = escenario["nombre"]
        filas_tar_out = filas_tarifas
        filas_lim_out = filas_limites
    elif disparador == "btn-agregar-rango":
        nuevas_filas = list(filas_tarifas or [])
        ultimo_desde = float(nuevas_filas[-1]["desde_m"]) + 200.0 if nuevas_filas else 0.0
        ultima_tarifa = float(nuevas_filas[-1]["tarifa_2027"]) if nuevas_filas else 5.0
        if nuevas_filas and str(nuevas_filas[-1].get("hasta_m", "")).strip().lower() == "en adelante":
            nuevas_filas[-1]["hasta_m"] = str(round(ultimo_desde, 1))
        nuevas_filas.append(
            {
                "desde_m": round(ultimo_desde, 1),
                "hasta_m": "en adelante",
                "tarifa_2027": round(min(33.0, ultima_tarifa + 0.5), 2),
                "tarifa_2026": "—",
            }
        )
        otros = [t for t in escenario.get("tarifas", []) if t.get("destino") != destino]
        for fila in nuevas_filas:
            try:
                desde = max(0.0, float(fila["desde_m"])) * 1e6
                tar = max(0.0, min(33.0, float(fila["tarifa_2027"])))
            except (TypeError, ValueError):
                continue
            otros.append(
                {
                    "destino": destino,
                    "avaluo_desde": desde,
                    "avaluo_hasta": _parse_hasta_m(fila.get("hasta_m")),
                    "tarifa_por_mil": tar,
                }
            )
        escenario["tarifas"] = otros
        nombre_out = escenario["nombre"]
        filas_tar_out = _tarifas_a_filas(escenario, destino)
        filas_lim_out = filas_limites
    elif disparador == "tabla-tarifas":
        otros = [t for t in escenario.get("tarifas", []) if t.get("destino") != destino]
        for fila in filas_tarifas or []:
            try:
                desde = max(0.0, float(str(fila["desde_m"]).replace(",", "."))) * 1e6
                tar = max(0.0, min(33.0, float(str(fila["tarifa_2027"]).replace(",", "."))))
            except (TypeError, ValueError):
                continue
            otros.append(
                {
                    "destino": destino,
                    "avaluo_desde": desde,
                    "avaluo_hasta": _parse_hasta_m(fila.get("hasta_m")),
                    "tarifa_por_mil": tar,
                }
            )
        escenario["tarifas"] = otros
        nombre_out = escenario["nombre"]
        filas_tar_out = filas_tarifas
        filas_lim_out = filas_limites
    elif disparador == "tabla-limites":
        nuevos_limites: list[dict[str, Any]] = []
        for fila in filas_limites or []:
            lim_raw = str(fila.get("limite_pct", "")).strip().lower()
            if lim_raw in ("sin límite", "sin limite", "none", ""):
                continue
            try:
                desde = max(0.0, float(str(fila["desde_m"]).replace(",", "."))) * 1e6
                pct = max(0.0, float(lim_raw.replace("%", "").replace(",", ".")))
            except (TypeError, ValueError):
                continue
            nuevos_limites.append(
                {
                    "avaluo_desde": desde,
                    "avaluo_hasta": _parse_hasta_m(fila.get("hasta_m")),
                    "aumento_maximo": pct / 100.0,
                }
            )
        escenario["limites"] = nuevos_limites
        nombre_out = escenario["nombre"]
        filas_tar_out = filas_tarifas
        filas_lim_out = filas_limites
    else:
        nombre_out = escenario["nombre"]
        filas_tar_out = _tarifas_a_filas(escenario, destino)
        filas_lim_out = _limites_a_filas(escenario)

    estilos_pills = [
        {
            "borderRadius": "999px",
            "padding": "5px 11px",
            "fontSize": "12px",
            "fontWeight": "600",
            "cursor": "pointer",
            "fontFamily": FUENTE,
            "border": f"1px solid {NEGRO}",
            "background": NEGRO if pid["index"] == destino else BLANCO,
            "color": BLANCO if pid["index"] == destino else NEGRO,
        }
        for pid in ids_pills
    ]
    return escenario, destino, nombre_out, filas_tar_out, filas_lim_out, estilos_pills


@app.callback(
    Output("banner-error-api", "children"),
    Output("contenedor-guardrails", "children"),
    Output("contenedor-kpis", "children"),
    Output("contenedor-recaudo-ml", "children"),
    Output("texto-palabras-simples", "children"),
    Output("grafica-brecha", "figure"),
    Output("grafica-aumento", "figure"),
    Output("grafica-deciles", "figure"),
    Output("store-ultimo-resultado", "data"),
    Input("store-escenario", "data"),
    Input("btn-recargar-modelo", "n_clicks"),
)
def actualizar_simulacion(escenario: dict[str, Any], _n_recargas: int):
    res, err = _api_post("/escenarios/simular", escenario)
    if err or not res:
        aviso = html.Div(
            f"⚠ {err or 'No se pudo ejecutar la simulación.'}",
            style={
                "background": AMARILLO,
                "color": NEGRO,
                "border": f"2px solid {NEGRO}",
                "padding": "10px 14px",
                "borderRadius": "4px",
                "fontWeight": "600",
                "fontSize": "13px",
            },
        )
        vacia = _fig_vacia("Sin conexión con la API")
        return aviso, html.Div("Sin datos"), html.Div(), html.Div(), "—", vacia, vacia, vacia, None

    kpis = res["kpis"]
    rec_ml = res["recaudo_esperado"]
    guardrails = res["guardrails"]
    graf = res["graficas"]

    # --- Zona 2: Guardrails ---
    tarjetas_guardrails = []
    for g in guardrails:
        cumple = g["cumple"]
        tarjetas_guardrails.append(
            html.Div(
                [
                    html.Span(
                        "✓ " if cumple else "⚠ ",
                        style={"fontWeight": "700", "fontSize": "14px"},
                    ),
                    html.Strong(f"{g['titulo']}: "),
                    html.Span(g["detalle"]),
                ],
                style={
                    "padding": "9px 11px",
                    "marginBottom": "8px",
                    "borderRadius": "4px",
                    "fontSize": "12.5px",
                    "lineHeight": "1.4",
                    "background": "#FAFAFA" if cumple else "#FFFCE0",
                    "border": f"1px dashed {GRIS_BORDE}" if cumple else f"1.5px solid {NEGRO}",
                    "borderLeft": f"4px solid {NEGRO}" if cumple else f"5px solid {AMARILLO}",
                    "color": NEGRO,
                },
            )
        )

    # --- Zona 3: 3 tarjetas KPI ---
    conv = kpis["convergencia_2027_pct"]
    conv_26 = kpis["convergencia_2026_pct"]
    barra_ancho = f"{min(100.0, max(0.0, conv)):.1f}%"

    tarjetas_kpis = html.Div(
        [
            # KPI 1
            html.Div(
                [
                    html.Div("KPI 1 · CONVERGENCIA", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                    html.Div(f"{conv:.1f} %", style={"fontSize": "28px", "fontWeight": "700", "margin": "4px 0"}),
                    html.Div(
                        f"del IPU pleno · 2026: {conv_26:.1f} % (cierra {kpis['brecha_cerrada_pct']:.1f} %)",
                        style={"fontSize": "12px", "color": GRIS_TEXTO},
                    ),
                    html.Div(
                        html.Div(
                            style={
                                "width": barra_ancho,
                                "height": "8px",
                                "background": NEGRO,
                                "borderRadius": "4px",
                            }
                        ),
                        style={
                            "width": "100%",
                            "height": "8px",
                            "background": "#E6E6E6",
                            "borderRadius": "4px",
                            "marginTop": "8px",
                            "overflow": "hidden",
                        },
                    ),
                ],
                style={**ESTILO_TARJETA, "background": "#FCFCFC"},
            ),
            # KPI 2
            html.Div(
                [
                    html.Div("KPI 2 · CHOQUE EN LA COLA", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                    html.Div(
                        f"+{_fmt_m(kpis['choque_mediano_top1'])}",
                        style={"fontSize": "28px", "fontWeight": "700", "margin": "4px 0"},
                    ),
                    html.Div(
                        f"aumento mediano en el 1 % de mayor IPU ({kpis['participacion_aumento_top1_pct']:.1f} % del aumento total)",
                        style={"fontSize": "12px", "color": GRIS_TEXTO},
                    ),
                    html.Div(
                        f"5 % de mayor IPU: +{_fmt_m(kpis['choque_mediano_top5'])}",
                        style={"fontSize": "12px", "fontWeight": "600", "marginTop": "6px"},
                    ),
                ],
                style={**ESTILO_TARJETA, "background": "#FCFCFC"},
            ),
            # META
            html.Div(
                [
                    html.Div("META · RECAUDO FACTURADO", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                    html.Div(
                        _fmt_mil_m(kpis["recaudo_facturado_2027"]),
                        style={"fontSize": "28px", "fontWeight": "700", "margin": "4px 0"},
                    ),
                    html.Div(
                        f"frente a 2026 ({_fmt_mil_m(kpis['recaudo_facturado_2026'])}): {kpis['variacion_recaudo_pct']:+.1f} %",
                        style={"fontSize": "12px", "color": GRIS_TEXTO},
                    ),
                    html.Div(
                        "✓ Cumple la meta" if kpis["cumple_meta"] else "⚠ Por debajo de la meta",
                        style={
                            "fontSize": "12px",
                            "fontWeight": "700",
                            "marginTop": "6px",
                            "display": "inline-block",
                            "padding": "2px 8px",
                            "borderRadius": "3px",
                            "background": "#EFEFEF" if kpis["cumple_meta"] else AMARILLO,
                            "border": f"1px solid {NEGRO}",
                        },
                    ),
                ],
                style={**ESTILO_TARJETA, "background": "#FCFCFC"},
            ),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(210px, 1fr))",
            "gap": "10px",
        },
    )

    # --- Zona 3b: Recaudo esperado (Modelo ML) ---
    if rec_ml["disponible"]:
        filas_hist = [
            html.Tr(
                [
                    html.Td(d["grupo"], style={"padding": "4px 8px", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                    html.Td(f"{d['predios']:,}".replace(",", " "), style={"padding": "4px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                    html.Td(f"{d['prob_promedio_pct']:.1f} %", style={"padding": "4px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                    html.Td(_fmt_mil_m(d["facturado_2027"]), style={"padding": "4px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                    html.Td(_fmt_mil_m(d["esperado_2027"]), style={"padding": "4px 8px", "textAlign": "right", "fontWeight": "700", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                ]
            )
            for d in rec_ml.get("desglose_historial", [])
        ]
        bloque_ml = html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    f"RECAUDO ESPERADO · MODELO ML ({rec_ml['modelo_nombre'].upper()})",
                                    style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO},
                                ),
                                html.Div(
                                    _fmt_mil_m(rec_ml["esperado_2027"]),
                                    style={"fontSize": "28px", "fontWeight": "700", "margin": "4px 0"},
                                ),
                                html.Div(
                                    f"facturado × probabilidad de pago · tasa esperada: {rec_ml['tasa_recaudo_esperada_pct']:.1f} %",
                                    style={"fontSize": "12px", "color": GRIS_TEXTO},
                                ),
                                html.Div(
                                    f"rango conservador: {_fmt_mil_m(rec_ml['rango_bajo_2027'])} – {_fmt_mil_m(rec_ml['rango_alto_2027'])}",
                                    style={"fontSize": "12px", "fontWeight": "600", "marginTop": "4px"},
                                ),
                            ],
                            style={"minWidth": "240px"},
                        ),
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("Historial 2025", style={"textAlign": "left", "padding": "4px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                                            html.Th("Predios", style={"textAlign": "right", "padding": "4px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                                            html.Th("Prob. media", style={"textAlign": "right", "padding": "4px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                                            html.Th("Facturado", style={"textAlign": "right", "padding": "4px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                                            html.Th("Esperado", style={"textAlign": "right", "padding": "4px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                                        ]
                                    )
                                ),
                                html.Tbody(filas_hist),
                            ],
                            style={"borderCollapse": "collapse", "fontSize": "12px", "flex": "1", "minWidth": "300px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "flex-start",
                        "gap": "18px",
                        "flexWrap": "wrap",
                    },
                ),
                html.Div(
                    "Nota: las probabilidades provienen del modelo entrenado con el comportamiento de 2026 "
                    "y no modelan cambios de pago ante aumentos tarifarios distintos.",
                    style={"fontSize": "11px", "color": GRIS_TEXTO, "marginTop": "8px"},
                ),
            ],
            style={
                "border": f"1.5px dashed {NEGRO}",
                "borderRadius": "6px",
                "padding": "12px 14px",
                "background": "#FCFCFC",
            },
        )
    else:
        bloque_ml = html.Div(
            "Recaudo esperado no disponible: falta generar `entrega-2/producto/artefactos/modelo.joblib`.",
            style={
                "border": f"1.5px dashed {NEGRO}",
                "borderRadius": "6px",
                "padding": "12px 14px",
                "background": "#FFFCE0",
                "fontSize": "13px",
            },
        )

    # --- Gráfica 1: Brecha cerrada / convergencia por destino ---
    dest_datos = graf["brecha_por_destino"]
    fig_brecha = go.Figure()
    fig_brecha.add_trace(
        go.Bar(
            name="2026",
            x=[d["destino"] for d in dest_datos],
            y=[d["convergencia_2026_pct"] for d in dest_datos],
            marker={"color": "#B5B5B5", "line": {"color": NEGRO, "width": 0.8}},
            hovertemplate="%{x}<br>Convergencia 2026: %{y:.1f} %<extra></extra>",
        )
    )
    fig_brecha.add_trace(
        go.Bar(
            name="Escenario 2027",
            x=[d["destino"] for d in dest_datos],
            y=[d["convergencia_2027_pct"] for d in dest_datos],
            marker={"color": AMARILLO, "line": {"color": NEGRO, "width": 1.2}},
            hovertemplate="%{x}<br>Convergencia 2027: %{y:.1f} %<extra></extra>",
        )
    )
    fig_brecha.update_layout(
        title={"text": "Convergencia al IPU pleno por destino (%)", "font": {"size": 13, "family": FUENTE, "color": NEGRO}},
        barmode="group",
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        font={"family": FUENTE, "color": NEGRO, "size": 11},
        yaxis={"range": [0, 108], "gridcolor": "#EAEAEA", "title": "% del pleno"},
        xaxis={"tickangle": -18},
        legend={"orientation": "h", "y": 1.12, "x": 0},
        margin={"l": 45, "r": 12, "t": 52, "b": 56},
        height=270,
    )

    # --- Gráfica 2: Distribución del aumento del IPU 2027 vs 2026 ---
    dist_datos = graf["distribucion_aumento"]
    colores_aum = [
        AMARILLO if d["rango"] == "> 100 %" else "#4A4A4A" for d in dist_datos
    ]
    fig_aumento = go.Figure(
        go.Bar(
            x=[d["rango"] for d in dist_datos],
            y=[d["porcentaje"] for d in dist_datos],
            customdata=[d["predios"] for d in dist_datos],
            marker={"color": colores_aum, "line": {"color": NEGRO, "width": 0.9}},
            hovertemplate="Aumento %{x}<br>%{y:.1f} % (%{customdata:,} predios)<extra></extra>",
        )
    )
    fig_aumento.update_layout(
        title={"text": "Distribución del aumento del IPU 2027 vs. 2026", "font": {"size": 13, "family": FUENTE, "color": NEGRO}},
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        font={"family": FUENTE, "color": NEGRO, "size": 11},
        yaxis={"gridcolor": "#EAEAEA", "title": "% de predios"},
        xaxis={"tickangle": -25},
        margin={"l": 45, "r": 12, "t": 44, "b": 56},
        height=270,
    )

    # --- Gráfica 3: Tarifa efectiva por decil de avalúo ---
    dec_datos = graf["tarifa_por_decil"]
    fig_deciles = go.Figure()
    fig_deciles.add_trace(
        go.Scatter(
            name="Escenario 2027",
            x=[d["decil"] for d in dec_datos],
            y=[d["tarifa_2027"] for d in dec_datos],
            mode="lines+markers",
            line={"color": NEGRO, "width": 2.6},
            marker={"color": AMARILLO, "size": 8, "line": {"color": NEGRO, "width": 1.4}},
            customdata=[d["avaluo_mediano_m"] for d in dec_datos],
            hovertemplate="Decil %{x} (avalúo mediano $%{customdata:.0f} M)<br>Tarifa ef. 2027: %{y:.2f} ‰<extra></extra>",
        )
    )
    fig_deciles.add_trace(
        go.Scatter(
            name="Línea base 2026",
            x=[d["decil"] for d in dec_datos],
            y=[d["tarifa_2026"] for d in dec_datos],
            mode="lines+markers",
            line={"color": "#777777", "width": 1.8, "dash": "dash"},
            marker={"color": "#777777", "size": 5},
            hovertemplate="Decil %{x}<br>Tarifa ef. 2026: %{y:.2f} ‰<extra></extra>",
        )
    )
    fig_deciles.update_layout(
        title={"text": "Progresividad: tarifa efectiva (IPU / avalúo) por decil de avalúo", "font": {"size": 13, "family": FUENTE, "color": NEGRO}},
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        font={"family": FUENTE, "color": NEGRO, "size": 11},
        xaxis={"tickmode": "linear", "dtick": 1, "title": "Decil de avalúo catastral (1 = menor avalúo, 10 = mayor avalúo)"},
        yaxis={"gridcolor": "#EAEAEA", "title": "Tarifa efectiva (‰)"},
        legend={"orientation": "h", "y": 1.14, "x": 0},
        margin={"l": 50, "r": 16, "t": 54, "b": 44},
        height=265,
    )

    return (
        None,
        tarjetas_guardrails,
        tarjetas_kpis,
        bloque_ml,
        res["en_palabras_simples"],
        fig_brecha,
        fig_aumento,
        fig_deciles,
        res,
    )


@app.callback(
    Output("store-mostrar-comparacion", "data"),
    Output("panel-comparacion", "style"),
    Output("panel-comparacion", "children"),
    Input("btn-comparar", "n_clicks"),
    State("store-mostrar-comparacion", "data"),
    State("store-escenario", "data"),
    prevent_initial_call=True,
)
def alternar_comparacion(_n: int, visible: bool, escenario_actual: dict[str, Any]):
    nuevo_estado = not bool(visible)
    if not nuevo_estado:
        return False, {"display": "none", "marginBottom": "14px"}, []

    lista = list(ESCENARIOS_INICIALES.values())
    nombres_base = {e["nombre"] for e in lista}
    if escenario_actual and escenario_actual.get("nombre") not in nombres_base:
        lista.append(escenario_actual)

    res, err = _api_post("/escenarios/comparar", {"escenarios": lista})
    if err or not res:
        return (
            True,
            {**ESTILO_TARJETA, "display": "block", "marginBottom": "14px"},
            html.Div(f"No se pudo comparar escenarios: {err}", style={"color": NEGRO}),
        )

    filas = res["comparacion"]
    fig_frontera = go.Figure(
        go.Scatter(
            x=[f["convergencia_2027_pct"] for f in filas],
            y=[f["choque_mediano_top1"] / 1e6 for f in filas],
            mode="markers+text",
            text=[f["nombre"].split("·")[0].strip() for f in filas],
            textposition="top center",
            marker={
                "size": 13,
                "color": [AMARILLO if f["guardrails_cumplidos"] == f["guardrails_total"] else "#888888" for f in filas],
                "line": {"color": NEGRO, "width": 1.6},
            },
            customdata=[f["nombre"] for f in filas],
            hovertemplate="%{customdata}<br>Convergencia: %{x:.1f} %<br>Choque mediano top 1 %: +$%{y:.1f} M<extra></extra>",
        )
    )
    fig_frontera.update_layout(
        title={"text": "Frontera entre KPI 1 (convergencia) y KPI 2 (choque en el 1 % superior)", "font": {"size": 13, "family": FUENTE, "color": NEGRO}},
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        font={"family": FUENTE, "color": NEGRO, "size": 11},
        xaxis={"title": "KPI 1 · Convergencia al IPU pleno (%)", "gridcolor": "#EAEAEA"},
        yaxis={"title": "KPI 2 · Aumento mediano top 1 % (millones COP)", "gridcolor": "#EAEAEA"},
        margin={"l": 55, "r": 20, "t": 44, "b": 42},
        height=245,
    )

    tabla = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Escenario", style={"textAlign": "left", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                        html.Th("Conv. 2027", style={"textAlign": "right", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                        html.Th("Choque top 1 %", style={"textAlign": "right", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                        html.Th("Facturado", style={"textAlign": "right", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                        html.Th("Esperado (ML)", style={"textAlign": "right", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                        html.Th("Guardrails", style={"textAlign": "center", "padding": "6px 8px", "borderBottom": f"2px solid {NEGRO}"}),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(f["nombre"], style={"padding": "6px 8px", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                            html.Td(f"{f['convergencia_2027_pct']:.1f} %", style={"padding": "6px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                            html.Td(f"+{_fmt_m(f['choque_mediano_top1'])}", style={"padding": "6px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                            html.Td(_fmt_mil_m(f["recaudo_facturado_2027"]), style={"padding": "6px 8px", "textAlign": "right", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                            html.Td(_fmt_mil_m(f["recaudo_esperado_2027"]), style={"padding": "6px 8px", "textAlign": "right", "fontWeight": "700", "borderBottom": f"1px solid {GRIS_BORDE}"}),
                            html.Td(
                                f"{f['guardrails_cumplidos']}/{f['guardrails_total']}"
                                + ("" if not f["alertas"] else f" ({', '.join(f['alertas'])})"),
                                style={"padding": "6px 8px", "textAlign": "center", "borderBottom": f"1px solid {GRIS_BORDE}"},
                            ),
                        ]
                    )
                    for f in filas
                ]
            ),
        ],
        style={"width": "100%", "borderCollapse": "collapse", "fontSize": "12px", "marginBottom": "10px"},
    )

    contenido = [
        html.Div(
            "Comparación de escenarios (amarillo = cumple todos los guardrails)",
            style={"fontWeight": "700", "fontSize": "14px", "marginBottom": "8px", "borderBottom": f"3px solid {AMARILLO}", "paddingBottom": "4px"},
        ),
        tabla,
        dcc.Graph(figure=fig_frontera, config={"displayModeBar": False}),
    ]
    return True, {**ESTILO_TARJETA, "display": "block", "marginBottom": "14px"}, contenido


@app.callback(
    Output("descarga-exportacion", "data"),
    Input("btn-exportar", "n_clicks"),
    State("store-escenario", "data"),
    prevent_initial_call=True,
)
def exportar_escenario(_n: int, escenario: dict[str, Any]):
    res, err = _api_post("/escenarios/exportar", escenario)
    if err or not res:
        return None
    return {"content": res["html"], "filename": res["nombre_archivo"]}


@app.callback(
    Output("resultados-hipotetico", "children"),
    Input("btn-simular-hipotetico", "n_clicks"),
    Input("pestana-activa", "value"),
    Input("store-escenario", "data"),
    State("hip-avaluo-m", "value"),
    State("hip-ipu2026-k", "value"),
    State("hip-destino", "value"),
    State("hip-zona", "value"),
    State("hip-condicion", "value"),
    State("hip-historial", "value"),
    State("hip-area-const", "value"),
    State("hip-area-terr", "value"),
    State("hip-pisos", "value"),
    State("hip-anio", "value"),
    State("hip-novedad", "value"),
    State("hip-predios-titular", "value"),
    State("hip-juridico", "value"),
)
def actualizar_hipotetico(
    _n_clicks: int,
    pestana: str,
    escenario: dict[str, Any],
    avaluo_m: float,
    ipu2026_k: float,
    destino: str,
    zona: str,
    condicion: str,
    historial: str,
    area_const: float,
    area_terr: float,
    pisos: float,
    anio: int,
    novedad: str,
    predios_titular: int,
    tipo_titular: str,
):
    if pestana != "hipotetico" and ctx.triggered_id != "btn-simular-hipotetico":
        return html.Div()

    payload = {
        "avaluo_catastral": max(1.0, float(avaluo_m or 240)) * 1e6,
        "ipu_2026": max(0.0, float(ipu2026_k or 0)) * 1e3,
        "destinacion_economica": destino or "Habitacional",
        "zona": zona or "Urbano",
        "condicion_predio": condicion or "NPH",
        "historial_2025": historial or "Pagó 2025",
        "area_construida_m2": max(0.0, float(area_const or 0)),
        "area_terreno_m2": max(0.0, float(area_terr or 0)),
        "area_registral_m2": max(1.0, float(area_terr or 100)),
        "pisos_edificio": max(0.0, float(pisos or 0)),
        "anio_construccion": int(anio) if anio else None,
        "n_unidades": 1 if (area_const or 0) > 0 else 0,
        "n_construcciones": 1 if (area_const or 0) > 0 else 0,
        "predios_mismo_titular": max(1, int(predios_titular or 1)),
        "titular_juridico": tipo_titular == "juridica",
        "novedad_numero_predial": novedad or "Sin_Novedad",
        "escenario": escenario,
    }
    res, err = _api_post("/hipotetico/simular", payload)
    if err or not res:
        return html.Div(
            f"⚠ No se pudo ejecutar la simulación hipotética: {err}",
            style={**ESTILO_TARJETA, "background": "#FFFCE0", "border": f"1.5px solid {NEGRO}"},
        )

    det = res["determinista"]
    ml = res["modelo_pago"]

    # Gráfica comparativa antes vs después
    fig_bar = go.Figure(
        go.Bar(
            x=["IPU 2026 (actual)", "IPU 2027 (escenario)", "IPU pleno 2027"],
            y=[det["ipu_2026"] / 1e3, det["ipu_2027"] / 1e3, det["ipu_pleno_2027"] / 1e3],
            marker={
                "color": ["#B5B5B5", AMARILLO, NEGRO],
                "line": {"color": NEGRO, "width": 1.2},
            },
            hovertemplate="%{x}: $%{y:,.0f} mil<extra></extra>",
        )
    )
    fig_bar.update_layout(
        paper_bgcolor=BLANCO,
        plot_bgcolor=BLANCO,
        font={"family": FUENTE, "color": NEGRO, "size": 11},
        yaxis={"title": "Miles de pesos COP", "gridcolor": "#EAEAEA"},
        margin={"l": 55, "r": 12, "t": 16, "b": 34},
        height=205,
    )

    aum_pct_txt = "N/A" if det["aumento_pct"] is None else f"{det['aumento_pct']:+.1f} %"
    lim_txt = (
        "Sin límite"
        if det["limite_crecimiento_pct"] is None
        else f"{det['limite_crecimiento_pct']:.0f} %"
    )
    bloque_det = html.Section(
        [
            html.H2(
                f"Parte 1 · Motor determinista ({res['escenario_aplicado']})",
                style={"fontSize": "15px", "margin": "0 0 10px", "borderBottom": f"3px solid {AMARILLO}", "paddingBottom": "4px"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("IPU 2026 (ACTUAL)", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                            html.Div(_fmt_cop(det["ipu_2026"]), style={"fontSize": "22px", "fontWeight": "700", "marginTop": "4px"}),
                        ],
                        style={**ESTILO_TARJETA, "background": "#FCFCFC"},
                    ),
                    html.Div(
                        [
                            html.Div("IPU 2027 (CON ESCENARIO)", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                            html.Div(_fmt_cop(det["ipu_2027"]), style={"fontSize": "22px", "fontWeight": "700", "marginTop": "4px"}),
                            html.Div(f"Cambio: {_fmt_cop(det['aumento_pesos'])} ({aum_pct_txt})", style={"fontSize": "12px", "color": GRIS_TEXTO}),
                        ],
                        style={**ESTILO_TARJETA, "background": "#FFFDF0", "border": f"1.5px solid {NEGRO}"},
                    ),
                    html.Div(
                        [
                            html.Div("IPU PLENO 2027", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                            html.Div(_fmt_cop(det["ipu_pleno_2027"]), style={"fontSize": "22px", "fontWeight": "700", "marginTop": "4px"}),
                            html.Div(f"Tarifa: {det['tarifa_por_mil']:.2f} ‰ ({det['grupo_destino']})", style={"fontSize": "12px", "color": GRIS_TEXTO}),
                        ],
                        style={**ESTILO_TARJETA, "background": "#FCFCFC"},
                    ),
                ],
                style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(170px, 1fr))", "gap": "10px", "marginBottom": "10px"},
            ),
            html.Div(
                f"Límite aplicable: {lim_txt} · "
                + (
                    f"Tope activado (ahorro frente al pleno: {_fmt_cop(det['ahorro_por_limite'])})."
                    if det["limite_aplicado"]
                    else "El predio no alcanza el tope de crecimiento."
                )
                + (" ⚠ Supera el tope legal de la Ley 44 (doble de 2026)." if det["supera_tope_legal"] else " ✓ Respeta el tope legal de la Ley 44."),
                style={"fontSize": "12.5px", "marginBottom": "8px"},
            ),
            dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),
        ],
        style={**ESTILO_TARJETA, "marginBottom": "14px"},
    )

    # Parte 2: Modelo ML
    if ml.get("disponible"):
        prob_pct = ml["probabilidad_pago"] * 100.0
        tasa_ref = ml.get("tasa_referencia_historial_pct")
        bloque_ml = html.Section(
            [
                html.H2(
                    f"Parte 2 · Probabilidad de pago ({ml['modelo_nombre']})",
                    style={"fontSize": "15px", "margin": "0 0 10px", "borderBottom": f"3px solid {AMARILLO}", "paddingBottom": "4px"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div("PROBABILIDAD ESTIMADA DE PAGO", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                                html.Div(f"{prob_pct:.1f} %", style={"fontSize": "30px", "fontWeight": "700", "margin": "4px 0"}),
                                html.Div(
                                    f"Clasificación orientativa (umbral {ml['umbral_referencia']:.2f}): {ml['clase_orientativa']}",
                                    style={"fontSize": "12px", "fontWeight": "600"},
                                ),
                                html.Div(
                                    html.Div(
                                        style={
                                            "width": f"{min(100.0, max(0.0, prob_pct)):.1f}%",
                                            "height": "10px",
                                            "background": NEGRO,
                                            "borderRadius": "4px",
                                        }
                                    ),
                                    style={"width": "100%", "height": "10px", "background": "#E6E6E6", "borderRadius": "4px", "marginTop": "8px"},
                                ),
                            ],
                            style={**ESTILO_TARJETA, "background": "#FCFCFC"},
                        ),
                        html.Div(
                            [
                                html.Div("APORTE AL RECAUDO ESPERADO 2027", style={"fontSize": "11px", "fontWeight": "700", "color": GRIS_TEXTO}),
                                html.Div(_fmt_cop(ml["aporte_recaudo_esperado_2027"]), style={"fontSize": "26px", "fontWeight": "700", "margin": "4px 0"}),
                                html.Div(
                                    f"IPU 2027 ({_fmt_cop(det['ipu_2027'])}) × {prob_pct:.1f} %",
                                    style={"fontSize": "12px", "color": GRIS_TEXTO},
                                ),
                                html.Div(
                                    f"Referencia del grupo '{historial}' en 2026: {tasa_ref:.1f} %"
                                    if tasa_ref is not None
                                    else "",
                                    style={"fontSize": "12px", "marginTop": "6px", "fontWeight": "600"},
                                ),
                            ],
                            style={**ESTILO_TARJETA, "background": "#FCFCFC"},
                        ),
                    ],
                    style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(210px, 1fr))", "gap": "10px"},
                ),
                html.Div(
                    res["nota"],
                    style={"fontSize": "11.5px", "color": GRIS_TEXTO, "marginTop": "10px", "lineHeight": "1.45"},
                ),
            ],
            style=ESTILO_TARJETA,
        )
    else:
        bloque_ml = html.Section(
            "Modelo ML no disponible en la API.",
            style={**ESTILO_TARJETA, "background": "#FFFCE0"},
        )

    return html.Div([bloque_det, bloque_ml])


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
