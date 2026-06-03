"""goals — objetivos dinámicos (Capa 1, escala diaria, Semana 3).

Metas que se forman, persiguen y logran. Cumplir una meta deja una traza positiva en
la memoria del agente (via GOAL_ACHIEVED applier), que mejora el ánimo. Emite
GOAL_FORMED / GOAL_ACHIEVED / GOAL_ABANDONED.

Metas de Capa 1:
  - "earn_more" : inseguridad + ambición → meta de dinero. Lograda al superar el objetivo.
  - "find_work" : desempleo + ambición → buscar empleo. Lograda al conseguir trabajo.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.person import Person
from ..state.world import World
from .base import SystemSpec, TickContext

_SECURITY_LOW = 0.35
_AMBITION_EARN = 0.50
_AMBITION_WORK = 0.40
_EARN_TARGET_MULT = 1.5


def _active_kinds(person: Person) -> set[str]:
    return {g.kind for g in person.goals if g.active}


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        t = person.traits
        n = person.needs
        achieved: set[str] = set()

        # Logros sobre metas existentes
        for goal in person.goals:
            if not goal.active:
                continue
            if goal.kind == "earn_more" and person.money >= goal.target:
                events.append(Event(
                    type=EventType.GOAL_ACHIEVED,
                    tick=ctx.tick,
                    scale=TimeScale.DAILY,
                    payload={"person_id": person.id, "kind": goal.kind},
                ))
                achieved.add(goal.kind)
            elif goal.kind == "find_work" and person.employer_id is not None:
                events.append(Event(
                    type=EventType.GOAL_ACHIEVED,
                    tick=ctx.tick,
                    scale=TimeScale.DAILY,
                    payload={"person_id": person.id, "kind": goal.kind},
                ))
                achieved.add(goal.kind)

        # Formación de nuevas metas (excluye las recién logradas)
        active = _active_kinds(person) - achieved

        if "earn_more" not in active and n.security < _SECURITY_LOW and t.ambition > _AMBITION_EARN:
            target = max(person.money * _EARN_TARGET_MULT, person.money + 500.0)
            events.append(Event(
                type=EventType.GOAL_FORMED,
                tick=ctx.tick,
                scale=TimeScale.DAILY,
                payload={"person_id": person.id, "kind": "earn_more", "target": target},
            ))

        if "find_work" not in active and person.employer_id is None and t.ambition > _AMBITION_WORK:
            events.append(Event(
                type=EventType.GOAL_FORMED,
                tick=ctx.tick,
                scale=TimeScale.DAILY,
                payload={"person_id": person.id, "kind": "find_work", "target": 1.0},
            ))

    return events


SPEC = SystemSpec(
    name="goals",
    fn=step,
    scale=TimeScale.DAILY,
    layer=Layer.L1_BASE,
    order=30,
)
