"""death — muerte emergente con cola de consecuencias (ADR-0010, Semana 4).

Stub. A implementar:
  - Emerge de riesgo acumulado de salud (edad, hábitos, estrés sostenido, acceso a
    salud) + eventos agudos. Factores psicosociales como uno más entre varios, con
    sobriedad. No "la tristeza mata" mecánico.
  - Efectos posteriores (lo que la hace pesar): duelo escalado por vínculo y decaído
    por resiliencia, vacante de rol, shock económico + herencia, reestructuración del
    hogar, huella persistente en la memoria de los vivos, efecto macro en la pirámide.
Emite DEATH y, en cadena, INHERITANCE / RELATIONSHIP_CHANGED / MOVED, etc.
"""

from __future__ import annotations

from ..state.event import Event
from ..state.world import World
from .base import TickContext


def step(world: World, ctx: TickContext) -> list[Event]:
    raise NotImplementedError("death: pendiente Semana 4")
