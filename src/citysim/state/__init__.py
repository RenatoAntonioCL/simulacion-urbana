"""state/ — modelos de datos puros (ADR-0003).

Solo datos, sin lógica de negocio. La lógica vive en `systems/`. Las entidades se
referencian entre sí por `id` (ADR-0004) para que el estado sea serializable y la
integridad referencial sea testeable.
"""

from .enums import EventType, Layer, PlaceType, RelType, TimeScale
from .event import Event
from .household import Household
from .person import MemoryTrace, Needs, Person, Traits
from .place import Place
from .relationship import Relationship
from .world import World

__all__ = [
    "Event",
    "EventType",
    "Household",
    "Layer",
    "MemoryTrace",
    "Needs",
    "Person",
    "Place",
    "PlaceType",
    "RelType",
    "Relationship",
    "TimeScale",
    "Traits",
    "World",
]
