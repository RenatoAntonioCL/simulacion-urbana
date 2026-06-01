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


@dataclass(frozen=True)
class PersonDTO:
    """Vista de una persona (estado base — Semana 1).

    Los campos de identidad/trayectoria (traits, needs, memory, goals) se incorporarán
    a este DTO cuando sus capas estén activas; hoy no se exponen porque el MVP corre con
    la Capa 1.
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
