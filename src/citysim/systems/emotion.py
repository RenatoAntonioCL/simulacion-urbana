"""emotion — emoción transitoria por appraisal (ADR-0006, Semana 3).

Stub. A implementar: señal que emerge de la brecha esperado-vs-real, sesga la decisión
mientras dura y decae a velocidad fijada por la resiliencia del agente. NUNCA se
almacena como estado fijo: se recalcula cada tick. "Persona triste" persistido está
prohibido; la pena emerge de (alto neuroticismo + duelo reciente) y decae.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("emotion: pendiente Semana 3")
