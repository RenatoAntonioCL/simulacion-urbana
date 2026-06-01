"""wellbeing — bienestar ponderado por rasgos (Capa 1, Semana 2).

Stub. A implementar: bienestar = f(salud, necesidades psicológicas, relaciones,
economía, descanso), ponderado por los rasgos del agente. Un agente sociable sufre más
el aislamiento; uno ambicioso, el estancamiento. Resultado en [0, 1].
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("wellbeing: pendiente Semana 2")
