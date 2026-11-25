"""Aplicación web del producto de datos: la superficie interactiva para la consultora.

Sigue el wireframe de la sección 2 del reporte: (1) tarifas y límites; (2) alertas;
(3) indicadores; (4) lectura en lenguaje llano; (5) gráficas. Consume la API
(api.py), que debe estar corriendo. Desde la raíz del repositorio, en otra terminal:

    uv run python entrega-2/producto/app.py

Queda en http://127.0.0.1:8050. La dirección de la API se cambia con API_URL.

Pendiente: los controles y el contenido de cada zona. Colores y fuente siguen
identidad/README.md: blanco, negro y amarillo, sin serifas.
"""

import os

import requests
from dash import Dash, Input, Output, html

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")

AMARILLO, NEGRO, GRIS = "#FFFF00", "#000000", "#666666"
FUENTE = "Arial, 'Liberation Sans', Helvetica, sans-serif"


def zona(numero, titulo, texto):
    """Un bloque del wireframe, con su número y un contenido pendiente."""
    return html.Section(
        [
            html.H2(f"{numero}. {titulo}", style={"fontSize": "1.1rem", "margin": "0 0 8px",
                                                  "borderBottom": f"3px solid {AMARILLO}"}),
            html.P(f"Pendiente: {texto}", style={"color": GRIS, "margin": 0}),
        ],
        style={"border": f"1px solid {NEGRO}", "padding": "12px 16px", "background": "white"},
    )


app = Dash(__name__, title="Transición predial 2027")
app.layout = html.Div(
    [
        html.Header(
            [
                html.H1("Transición predial 2027", style={"margin": 0, "fontSize": "1.5rem"}),
                html.Span(id="estado-api", style={"fontSize": "0.9rem"}),
            ],
            style={"background": AMARILLO, "color": NEGRO, "padding": "12px 20px",
                   "display": "flex", "justifyContent": "space-between", "alignItems": "center"},
        ),
        html.Main(
            [
                zona(1, "Tarifas y límites", "tarifas por destino y rango de avalúo, y límites de crecimiento por rango"),
                zona(2, "Alertas", "guardrails que el escenario incumple"),
                zona(3, "Indicadores", "KPIs del escenario y recaudo esperado"),
                zona(4, "Lectura en lenguaje llano", "qué significa el escenario para el Concejo y los contribuyentes"),
                zona(5, "Gráficas", "distribución del aumento y convergencia hacia el pleno"),
            ],
            style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                   "gap": "16px", "padding": "20px"},
        ),
    ],
    style={"fontFamily": FUENTE, "color": NEGRO, "background": "#f5f5f5", "minHeight": "100vh",
           "margin": 0},
)


@app.callback(Output("estado-api", "children"), Input("estado-api", "id"))
def estado_api(_):
    """Muestra si la API responde y si el modelo ya está entrenado."""
    try:
        salud = requests.get(f"{API_URL}/salud", timeout=2).json()
    except requests.RequestException:
        return f"API sin respuesta en {API_URL}"
    modelo = "modelo listo" if salud.get("modelo_disponible") else "modelo pendiente"
    return f"API en línea · {modelo}"


if __name__ == "__main__":
    app.run(debug=True)
