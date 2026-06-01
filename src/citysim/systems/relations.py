"""relations — vínculos con peso (Capa 4, Semana 4).

Stub. A implementar: crear y actualizar Relationship (tipo, fuerza, reciprocidad,
historia) a partir de encuentros y eventos compartidos. Base para el contagio social y
para que la muerte pese.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("relations: pendiente Semana 4")
