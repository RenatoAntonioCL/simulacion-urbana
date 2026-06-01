"""goals — objetivos dinámicos (Semana 3).

Stub. A implementar: metas que se forman, persiguen, logran o abandonan. Cumplir o
frustrar una meta mueve el bienestar. Un agente sin metas activas debería notarlo
(caída de propósito). Emite GOAL_FORMED / GOAL_ACHIEVED / GOAL_ABANDONED.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("goals: pendiente Semana 3")
