"""wellbeing — bienestar ponderado por rasgos (Capa 1, escala horaria).

El bienestar deja de ser "dinero": es el promedio de las necesidades **ponderado por los
rasgos**. Un agente sociable pesa más su pertenencia; uno ambicioso, su propósito y
autonomía; uno cauto, su seguridad. Por eso dos agentes con las mismas necesidades pero
rasgos opuestos tienen bienestar distinto. Corre **después** de `needs` (order 30 > 20).
Emite WELLBEING_RECALCULATED solo cuando el valor cambia de forma apreciable.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.person import Person
from ..state.world import World
from .base import SystemSpec, TickContext, clamp01

_EPSILON = 1e-3


def _wellbeing(person: Person) -> float:
    t = person.traits
    n = person.needs
    # Pesos = 0.5 base + sesgo por rasgo. Suma ponderada normalizada → [0, 1].
    weights = {
        "belonging": 0.5 + t.sociability,
        "autonomy": 0.5 + t.ambition,
        "purpose": 0.5 + t.conscientiousness,
        "security": 0.5 + (1.0 - t.risk_tolerance),
        "stimulation": 0.5 + t.risk_tolerance,
    }
    values = {
        "belonging": n.belonging, "autonomy": n.autonomy, "purpose": n.purpose,
        "security": n.security, "stimulation": n.stimulation,
    }
    total_w = sum(weights.values())
    score = sum(weights[k] * values[k] for k in weights) / total_w
    return clamp01(score)


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        new = _wellbeing(person)
        if abs(new - person.wellbeing) >= _EPSILON:
            events.append(
                Event(
                    type=EventType.WELLBEING_RECALCULATED,
                    tick=ctx.tick,
                    scale=TimeScale.HOURLY,
                    payload={"person_id": person.id, "wellbeing": new},
                )
            )
    return events


SPEC = SystemSpec(
    name="wellbeing",
    fn=step,
    scale=TimeScale.HOURLY,
    layer=Layer.L1_BASE,
    order=30,
)
