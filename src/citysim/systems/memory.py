"""memory — memoria episódica por agente (Capa 1, escala diaria, Semana 3).

Recorre la población cada día, envejece los recuerdos existentes (age_ticks += 1) y
forma nuevos trazos para estados observables significativos (bienestar bajo, desempleo).
La emoción NO se almacena aquí: systems/emotion.py la recalcula cada tick leyendo
esta lista. Emite MEMORY_UPDATED solo para personas con algún cambio.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.world import World
from .base import SystemSpec, TickContext

_MAX_TRACES = 15
_LOW_WELLBEING = 0.30
_HIGH_WELLBEING = 0.75
_UNEMPLOYED_PURPOSE = 0.30


def _significant(person) -> list[dict]:
    """Nuevas trazas basadas en el estado observable del tick actual."""
    new: list[dict] = []
    if person.wellbeing < _LOW_WELLBEING:
        new.append({"event_type": "low_wellbeing", "valence": -0.6, "intensity": 0.7, "age_ticks": 0})
    elif person.wellbeing > _HIGH_WELLBEING:
        new.append({"event_type": "high_wellbeing", "valence": 0.6, "intensity": 0.5, "age_ticks": 0})
    if person.employer_id is None and person.needs.purpose < _UNEMPLOYED_PURPOSE:
        new.append({"event_type": "unemployment", "valence": -0.8, "intensity": 0.9, "age_ticks": 0})
    return new


def _weight(trace: dict) -> float:
    return trace["intensity"] / (1.0 + 0.05 * trace["age_ticks"])


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        aged = [
            {
                "event_type": m.event_type,
                "valence": m.valence,
                "intensity": m.intensity,
                "age_ticks": m.age_ticks + 1,
            }
            for m in person.memory
        ]
        new = _significant(person)
        combined = aged + new
        if not combined:
            continue
        combined.sort(key=_weight, reverse=True)
        combined = combined[:_MAX_TRACES]
        events.append(
            Event(
                type=EventType.MEMORY_UPDATED,
                tick=ctx.tick,
                scale=TimeScale.DAILY,
                payload={"person_id": person.id, "traces": combined},
            )
        )
    return events


SPEC = SystemSpec(
    name="memory",
    fn=step,
    scale=TimeScale.DAILY,
    layer=Layer.L1_BASE,
    order=20,
)
