"""economy — economía mínima (Capa 1, escala horaria).

Lo justo para que las decisiones tengan consecuencia: quien **trabaja** (acción en curso
== work y tiene empleo) recibe un salario por hora; quien **consume** gasta. Lee la
acción que dejó `decision` (en `current_action`) y emite INCOME / EXPENSE. No muta: el
dinero solo cambia por estos eventos, que es lo que vigila el invariante de conservación.

Va en Capa 1 (plan, Semana 2). La economía rica —ahorro, comercio, inversión— se reserva
para `L2_ECONOMY` en el post-MVP.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.world import World
from .base import SystemSpec, TickContext
from .decision import ACTION_CONSUME, ACTION_WORK

_WAGE = 50.0          # ingreso por hora trabajada
_CONSUME_COST = 30.0  # gasto por hora de consumo


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        if person.current_action == ACTION_WORK and person.employer_id is not None:
            events.append(
                Event(
                    type=EventType.INCOME,
                    tick=ctx.tick,
                    scale=TimeScale.HOURLY,
                    payload={"person_id": person.id, "amount": _WAGE},
                )
            )
        elif person.current_action == ACTION_CONSUME:
            # Solo se gasta lo que se tiene: así la conservación de dinero es exacta.
            amount = min(_CONSUME_COST, person.money)
            if amount > 0:
                events.append(
                    Event(
                        type=EventType.EXPENSE,
                        tick=ctx.tick,
                        scale=TimeScale.HOURLY,
                        payload={"person_id": person.id, "amount": amount},
                    )
                )
    return events


SPEC = SystemSpec(
    name="economy",
    fn=step,
    scale=TimeScale.HOURLY,
    layer=Layer.L1_BASE,
    order=60,
)
