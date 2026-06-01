"""economy — economía mínima Capa 1/2 (Semana 2).

Stub. A implementar (mínimo): trabajar genera ingreso, consumir gasta. Lo justo para
que las decisiones tengan consecuencia. Mantener mínima: que no se coma el foco. Emite
INCOME / EXPENSE. El invariante de conservación de dinero vigila este system.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("economy: pendiente Semana 2")
