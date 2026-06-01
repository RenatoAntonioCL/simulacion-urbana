"""needs — recalcula las necesidades psicológicas (Capa 1, Semana 2).

Stub. A implementar: derivar pertenencia/autonomía/propósito/seguridad/estímulo a
partir de condiciones observables (trabajo, vínculos, dinero, rutina). Devuelve eventos
de actualización; nunca muta el World.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("needs: pendiente Semana 2")
