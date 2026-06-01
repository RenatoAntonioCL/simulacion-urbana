"""decision — decisión satisficiente, no optimizadora (ADR-0007, Semana 2/3).

Stub. A implementar: el agente elige la primera opción "suficientemente buena" según
sus pesos personales, con información incompleta y sesgo emocional (cuando la emoción
exista, Semana 3), sujeto a dinero, tiempo y energía. Emite ACTION_CHOSEN.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("decision: pendiente Semana 2")
