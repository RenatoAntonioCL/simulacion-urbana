"""Aplicadores de eventos: cómo cada EventType muta el World.

Único lugar del sistema con escritura sobre el estado (ADR-0001). Se registra un
aplicador por EventType. Los EventType sin aplicador todavía son no-ops conscientes
(se irán implementando por semana/capa).
"""

from __future__ import annotations

from typing import Callable

from ..state.enums import EventType
from ..state.event import Event
from ..state.world import World

Applier = Callable[[World, Event], None]

_APPLIERS: dict[EventType, Applier] = {}


def applier(event_type: EventType) -> Callable[[Applier], Applier]:
    """Decorador para registrar el aplicador de un EventType."""

    def register(fn: Applier) -> Applier:
        _APPLIERS[event_type] = fn
        return fn

    return register


def apply_event(world: World, event: Event) -> None:
    """Aplica un evento al mundo usando el aplicador registrado.

    Si no hay aplicador para el tipo, es un no-op (se implementará más adelante).
    """
    fn = _APPLIERS.get(event.type)
    if fn is not None:
        fn(world, event)


# --- Aplicadores Semana 1 (mínimos) -----------------------------------------

@applier(EventType.TICK)
def _apply_tick(world: World, event: Event) -> None:
    world.tick = event.tick


@applier(EventType.AGED)
def _apply_aged(world: World, event: Event) -> None:
    pid = event.payload["person_id"]
    delta = event.payload.get("delta_years", 0.0)
    person = world.persons.get(pid)
    if person is not None and person.alive:
        person.age += delta


@applier(EventType.DEATH)
def _apply_death(world: World, event: Event) -> None:
    pid = event.payload["person_id"]
    person = world.persons.get(pid)
    if person is not None and person.alive:
        person.alive = False
        world.dead_count += 1


@applier(EventType.BIRTH)
def _apply_birth(world: World, event: Event) -> None:
    # El seeder/sistema de natalidad construye la Person y la pasa en el payload.
    person = event.payload["person"]
    world.persons[person.id] = person
    world.born_count += 1

# Los demás EventType (INCOME, EXPENSE, GOAL_*, RELATIONSHIP_*, ...) se registran
# aquí a medida que se implementan sus systems (Semanas 2-4).
