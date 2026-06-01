"""decision — decisión satisficiente, no optimizadora (ADR-0007, Capa 1, escala horaria).

El agente evalúa un puñado de acciones y elige la **primera "suficientemente buena"** en
un orden fijo, según pesos personales (rasgos + necesidades). No optimiza global ni usa
azar: la heterogeneidad nace de los rasgos (sembrados) y de las necesidades. Sin emoción
ni memoria todavía (Semana 3). Emite ACTION_CHOSEN cada tick con la actividad elegida.

Cómo produce diversidad: un ambicioso cruza el umbral en `work`; un sociable no llega en
`work` pero sí en `socialize`. Mismos números, distinta decisión.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.person import Person
from ..state.world import World
from .base import SystemSpec, TickContext, clamp01

# Acciones posibles (Capa 1). Orden = prioridad de evaluación satisficiente.
ACTION_WORK = "work"
ACTION_SOCIALIZE = "socialize"
ACTION_REST = "rest"
ACTION_CONSUME = "consume"
ACTIONS = (ACTION_WORK, ACTION_SOCIALIZE, ACTION_REST, ACTION_CONSUME)

_THRESHOLD = 0.55      # "suficientemente bueno"
_MIN_WORK_ENERGY = 0.2  # sin energía no se puede trabajar


def _scores(person: Person) -> dict[str, float]:
    t = person.traits
    n = person.needs
    can_work = person.employer_id is not None and person.energy >= _MIN_WORK_ENERGY
    return {
        ACTION_WORK: clamp01(0.6 * t.ambition + 0.4 * (1.0 - n.security)) if can_work else 0.0,
        ACTION_SOCIALIZE: clamp01(0.6 * t.sociability + 0.4 * (1.0 - n.belonging)),
        ACTION_REST: clamp01(1.0 - person.energy),
        ACTION_CONSUME: clamp01(0.5 * (1.0 - n.stimulation) + 0.5 * clamp01(person.money / 5000.0)),
    }


def choose(person: Person) -> str:
    """Devuelve la acción elegida: la primera sobre el umbral, o la de mayor puntaje."""
    scores = _scores(person)
    for action in ACTIONS:
        if scores[action] >= _THRESHOLD:
            return action
    return max(ACTIONS, key=lambda a: scores[a])


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        action = choose(person)
        events.append(
            Event(
                type=EventType.ACTION_CHOSEN,
                tick=ctx.tick,
                scale=TimeScale.HOURLY,
                payload={"person_id": person.id, "action": action},
            )
        )
    return events


SPEC = SystemSpec(
    name="decision",
    fn=step,
    scale=TimeScale.HOURLY,
    layer=Layer.L1_BASE,
    order=40,
)
