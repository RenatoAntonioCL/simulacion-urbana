"""aging — envejecimiento y demografía base (Capa 1, escala poblacional).

System de ejemplo funcional de la Semana 1: el mundo solo envejece y registra el paso
del tiempo (todavía sin decisiones de los agentes). Demuestra el contrato: lee el
World, devuelve eventos, no muta nada.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from .base import SystemSpec, TickContext
from ..state.world import World

# Un paso poblacional representa, en el MVP, el avance de un día de edad.
_YEARS_PER_DAY = 1.0 / 365.0


def step(world: World, ctx: TickContext) -> list[Event]:
    """Emite un evento AGED por cada persona viva. No muta el World."""
    events: list[Event] = []
    for person in world.living_persons():
        events.append(
            Event(
                type=EventType.AGED,
                tick=ctx.tick,
                scale=TimeScale.POPULATION,
                payload={"person_id": person.id, "delta_years": _YEARS_PER_DAY},
            )
        )
    return events


SPEC = SystemSpec(
    name="aging",
    fn=step,
    scale=TimeScale.POPULATION,
    layer=Layer.L1_BASE,
    order=10,
)
