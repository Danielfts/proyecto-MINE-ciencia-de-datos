"""Motor de escenarios: aplica a cada predio las tarifas y los límites de un escenario.

Es determinista: las mismas reglas y los mismos datos dan siempre el mismo
impuesto. Se valida reproduciendo el IPU facturado en 2026 con las reglas del
acuerdo vigente (sección 4 del reporte).

Pendiente: todo el cálculo. Aquí están la forma del escenario y las funciones que
usan la API y la aplicación.
"""

from dataclasses import dataclass, field


@dataclass
class RangoTarifa:
    """Tarifa (por mil) para un destino económico y un rango de avalúo."""

    destino: str
    avaluo_desde: float
    avaluo_hasta: float | None  # None: sin tope
    tarifa_por_mil: float


@dataclass
class LimiteCrecimiento:
    """Límite al aumento del impuesto frente al año anterior, por rango de avalúo."""

    avaluo_desde: float
    avaluo_hasta: float | None
    aumento_maximo: float  # 0.3 = 30 %


@dataclass
class Escenario:
    nombre: str
    tarifas: list[RangoTarifa] = field(default_factory=list)
    limites: list[LimiteCrecimiento] = field(default_factory=list)


def calcular_ipu(predios, escenario):
    """IPU 2027 de cada predio con las reglas del escenario.

    Recibe la tabla de predios (avalúo, destino, IPU del año anterior) y devuelve
    la misma tabla con el impuesto pleno, el impuesto con límites y el límite aplicado.
    """
    raise NotImplementedError("Pendiente: el cálculo del motor de escenarios")


def indicadores(resultado):
    """KPIs y guardrails del escenario (tabla 1 del reporte): convergencia hacia el
    pleno, choque en la cola, meta de recaudo, progresividad y legalidad."""
    raise NotImplementedError("Pendiente: los indicadores del escenario")
