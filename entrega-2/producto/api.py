"""API REST del producto de datos: expone el motor de escenarios, el modelo y la exportación.

Desde la raíz del repositorio:

    uv run uvicorn api:app --app-dir entrega-2/producto --reload

La documentación interactiva queda en http://127.0.0.1:8000/docs.

Pendiente: las rutas de escenarios responden 501 hasta que el motor y el modelo
estén listos.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import modelo
import motor

app = FastAPI(
    title="Transición predial 2027",
    description="Escenarios de tarifas y límites del impuesto predial, con recaudo esperado.",
    version="0.1.0",
)


class RangoTarifa(BaseModel):
    destino: str
    avaluo_desde: float
    avaluo_hasta: float | None = None
    tarifa_por_mil: float


class LimiteCrecimiento(BaseModel):
    avaluo_desde: float
    avaluo_hasta: float | None = None
    aumento_maximo: float


class Escenario(BaseModel):
    nombre: str
    tarifas: list[RangoTarifa] = []
    limites: list[LimiteCrecimiento] = []


@app.get("/salud")
def salud():
    """Si la API está arriba y si el modelo ya está entrenado."""
    return {"estado": "ok", "modelo_disponible": modelo.disponible()}


@app.post("/escenarios/simular")
def simular(escenario: Escenario):
    """IPU 2027 por predio, indicadores y recaudo esperado de un escenario."""
    try:
        motor.calcular_ipu(None, motor.Escenario(**escenario.model_dump()))
    except NotImplementedError as pendiente:
        raise HTTPException(status_code=501, detail=str(pendiente))


@app.post("/escenarios/exportar")
def exportar(escenario: Escenario):
    """Exportación congelada y versionada del escenario elegido (tablas, gráficas y
    textos en lenguaje llano), insumo del material para el Concejo."""
    raise HTTPException(status_code=501, detail="Pendiente: la exportación del escenario")
