"""DTOs de la fachada — vistas de solo lectura del estado (ADR-0011).

Son `@dataclass(frozen=True)`: copias planas de lo que un cliente necesita ver. Nunca
se entregan las entidades internas del `World`. Para garantizar el aislamiento:

  - los enums se aplanan a `str`,
  - las colecciones se entregan como tuplas (inmutables),
  - el `payload` de un evento se copia en profundidad (puede contener objetos del núcleo,
    p. ej. el payload de BIRTH lleva un `Person`).

Así, mutar un DTO jamás altera el `World` (refuerza ADR-0001: el estado solo cambia por
eventos aplicados en el eventlog).
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from ..state.event import Event
from ..state.household import Household
from ..state.person import Person
from ..state.place import Place
from ..state.relationship import Relationship
from ..systems import emotion as emotion_sys


@dataclass(frozen=True)
class TraitsDTO:
    """Rasgos de personalidad (Semana 2), constantes en [0, 1]."""

    sociability: float
    ambition: float
    risk_tolerance: float
    conscientiousness: float
    resilience: float


@dataclass(frozen=True)
class NeedsDTO:
    """Necesidades psicológicas (Semana 2), satisfacción en [0, 1]."""

    belonging: float
    autonomy: float
    purpose: float
    security: float
    stimulation: float


@dataclass(frozen=True)
class MemoryTraceDTO:
    """Vista de un recuerdo (Semana 3): no se borra, se atenúa con la antigüedad."""

    event_type: str
    valence: float    # signo/calidad en [-1, 1]
    intensity: float  # fuerza inicial en [0, 1]
    age_ticks: int


@dataclass(frozen=True)
class GoalDTO:
    """Vista de una meta dinámica (Semana 3)."""

    kind: str
    target: float
    progress: float
    active: bool


@dataclass(frozen=True)
class PersonDTO:
    """Vista de una persona.

    Estado base (Semana 1) + identidad (Semana 2: rasgos, necesidades, acción en curso)
    + trayectoria (Semana 3: emoción transitoria, memoria, metas). La `emotion` no es un
    campo del núcleo (ADR-0006): se recalcula aquí desde la memoria al construir el DTO.
    """

    id: int
    age: float
    money: float
    time: float
    energy: float
    wellbeing: float
    health: float
    alive: bool
    location_id: int | None
    household_id: int | None
    employer_id: int | None
    # Semana 2 (aditivo)
    traits: TraitsDTO
    needs: NeedsDTO
    current_action: str | None
    # Semana 3 (aditivo)
    emotion: float
    memory: tuple[MemoryTraceDTO, ...]
    goals: tuple[GoalDTO, ...]

    @classmethod
    def from_entity(cls, p: Person) -> "PersonDTO":
        return cls(
            id=p.id,
            age=p.age,
            money=p.money,
            time=p.time,
            energy=p.energy,
            wellbeing=p.wellbeing,
            health=p.health,
            alive=p.alive,
            location_id=p.location_id,
            household_id=p.household_id,
            employer_id=p.employer_id,
            traits=TraitsDTO(
                sociability=p.traits.sociability,
                ambition=p.traits.ambition,
                risk_tolerance=p.traits.risk_tolerance,
                conscientiousness=p.traits.conscientiousness,
                resilience=p.traits.resilience,
            ),
            needs=NeedsDTO(
                belonging=p.needs.belonging,
                autonomy=p.needs.autonomy,
                purpose=p.needs.purpose,
                security=p.needs.security,
                stimulation=p.needs.stimulation,
            ),
            current_action=p.current_action,
            emotion=emotion_sys.compute(p),
            memory=tuple(
                MemoryTraceDTO(
                    event_type=t.event_type,
                    valence=t.valence,
                    intensity=t.intensity,
                    age_ticks=t.age_ticks,
                )
                for t in p.memory
            ),
            goals=tuple(
                GoalDTO(kind=g.kind, target=g.target, progress=g.progress, active=g.active)
                for g in p.goals
            ),
        )


@dataclass(frozen=True)
class HouseholdDTO:
    id: int
    member_ids: tuple[int, ...]
    income: float
    expenses: float
    dwelling_id: int | None
    location_id: int | None

    @classmethod
    def from_entity(cls, h: Household) -> "HouseholdDTO":
        return cls(
            id=h.id,
            member_ids=tuple(h.member_ids),
            income=h.income,
            expenses=h.expenses,
            dwelling_id=h.dwelling_id,
            location_id=h.location_id,
        )


@dataclass(frozen=True)
class PlaceDTO:
    id: int
    type: str
    capacity: int
    location_id: int
    open_hour: int
    close_hour: int

    @classmethod
    def from_entity(cls, pl: Place) -> "PlaceDTO":
        return cls(
            id=pl.id,
            type=pl.type.value,
            capacity=pl.capacity,
            location_id=pl.location_id,
            open_hour=pl.open_hour,
            close_hour=pl.close_hour,
        )


@dataclass(frozen=True)
class RelationshipDTO:
    id: int
    a_id: int
    b_id: int
    type: str
    strength: float
    reciprocity: float

    @classmethod
    def from_entity(cls, r: Relationship) -> "RelationshipDTO":
        return cls(
            id=r.id,
            a_id=r.a_id,
            b_id=r.b_id,
            type=r.type.value,
            strength=r.strength,
            reciprocity=r.reciprocity,
        )


@dataclass(frozen=True)
class EventDTO:
    type: str
    tick: int
    scale: str
    payload: dict[str, Any]
    cause: int | None

    @classmethod
    def from_entity(cls, e: Event) -> "EventDTO":
        # Copia profunda del payload: puede contener objetos del núcleo (p. ej. un Person
        # en BIRTH). Sin esto, un cliente podría alcanzar y mutar el estado interno.
        return cls(
            type=e.type.value,
            tick=e.tick,
            scale=e.scale.value,
            payload=copy.deepcopy(e.payload),
            cause=e.cause,
        )


@dataclass(frozen=True)
class WorldStateDTO:
    """Foto del mundo en un instante: contadores + colecciones de DTOs."""

    tick: int
    day: int
    hour: int
    n_persons_alive: int
    born_count: int
    dead_count: int
    persons: tuple[PersonDTO, ...]
    households: tuple[HouseholdDTO, ...]
    places: tuple[PlaceDTO, ...]
    relationships: tuple[RelationshipDTO, ...]
