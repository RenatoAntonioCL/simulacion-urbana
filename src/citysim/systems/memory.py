"""memory — memoria episódica por agente (Semana 3).

Stub. A implementar: copiar a la memoria del agente los eventos significativos del
tick, con peso que decae en el tiempo (no se borra, se atenúa). Conecta memoria →
decisión: un evento negativo pasado sesga decisiones futuras.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("memory: pendiente Semana 3")
