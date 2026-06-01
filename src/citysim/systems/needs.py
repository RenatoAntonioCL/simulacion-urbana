"""needs — recalcula las necesidades psicológicas (Capa 1, escala horaria).

Las necesidades son señales de satisfacción en [0, 1] que **derivan** del estado
observable: la seguridad sube con el dinero, el propósito/autonomía con el empleo, y la
pertenencia/estímulo decaen si no se alimentan (eso lo reponen las acciones, vía el
aplicador de ACTION_CHOSEN). El system no muta: emite NEEDS_RECALCULATED y solo cuando
algún valor cambió de forma apreciable, para que el log siga siendo significativo.
"""

from __future__ import annotations

from ..state.enums import EventType, Layer, TimeScale
from ..state.event import Event
from ..state.person import Person
from ..state.world import World
from .base import SystemSpec, TickContext, clamp01

_DRIFT = 0.10        # qué tan rápido cada necesidad se acerca a su objetivo por tick
_EPSILON = 1e-3      # cambio mínimo para emitir un evento (evita ruido en el log)
_MONEY_REF = 5000.0  # dinero de referencia para saturar la seguridad


def _targets(person: Person) -> dict[str, float]:
    employed = person.employer_id is not None
    return {
        "belonging": 0.30,                       # decae si no se socializa
        "autonomy": 0.60 if employed else 0.40,
        "purpose": 0.70 if employed else 0.35,
        "security": clamp01(person.money / _MONEY_REF),
        "stimulation": 0.30,                     # decae si no se consume / no hay variedad
    }


def step(world: World, ctx: TickContext) -> list[Event]:
    events: list[Event] = []
    for person in world.living_persons():
        n = person.needs
        target = _targets(person)
        new = {
            "belonging": clamp01(n.belonging + _DRIFT * (target["belonging"] - n.belonging)),
            "autonomy": clamp01(n.autonomy + _DRIFT * (target["autonomy"] - n.autonomy)),
            "purpose": clamp01(n.purpose + _DRIFT * (target["purpose"] - n.purpose)),
            "security": clamp01(n.security + _DRIFT * (target["security"] - n.security)),
            "stimulation": clamp01(n.stimulation + _DRIFT * (target["stimulation"] - n.stimulation)),
        }
        current = {
            "belonging": n.belonging, "autonomy": n.autonomy, "purpose": n.purpose,
            "security": n.security, "stimulation": n.stimulation,
        }
        if any(abs(new[k] - current[k]) >= _EPSILON for k in new):
            events.append(
                Event(
                    type=EventType.NEEDS_RECALCULATED,
                    tick=ctx.tick,
                    scale=TimeScale.HOURLY,
                    payload={"person_id": person.id, **new},
                )
            )
    return events


SPEC = SystemSpec(
    name="needs",
    fn=step,
    scale=TimeScale.HOURLY,
    layer=Layer.L1_BASE,
    order=20,
)
