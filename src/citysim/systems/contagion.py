"""contagion — difusión por la red de relaciones (Semana 4).

Stub. A implementar: estados de ánimo y conductas se difunden por la red, con
intensidad proporcional a la fuerza del vínculo. De aquí emergen los fenómenos
colectivos (olas de pesimismo/optimismo, pánico, modas).
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("contagion: pendiente Semana 4")
