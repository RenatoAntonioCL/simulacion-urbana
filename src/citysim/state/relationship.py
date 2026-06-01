"""Relationship — un vínculo con peso entre dos personas (Semana 4 / Capa 4).

Las relaciones dejan de ser un booleano: son entidades con fuerza. Esto es lo que hace
que una muerte importe: el dolor se propaga por la red proporcional a la fuerza del
vínculo (systems/contagion.py, systems/death.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .enums import RelType


@dataclass
class Relationship:
    id: int
    a_id: int               # Person.id (ADR-0004)
    b_id: int               # Person.id
    type: RelType = RelType.FRIEND
    strength: float = 0.5   # qué tan importante es el vínculo, [0, 1]
    reciprocity: float = 0.5  # ¿es correspondido?, [0, 1]
    shared_events: list[int] = field(default_factory=list)  # ids de Event compartidos
