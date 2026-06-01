"""Household — un hogar.

Agrupa individuos y genera dinámicas familiares. En la v2 también propaga shocks
(muerte, despido, nacimiento) entre integrantes y puede reestructurarse o disolverse.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Household:
    id: int
    member_ids: list[int] = field(default_factory=list)  # Person.id (ADR-0004)
    income: float = 0.0
    expenses: float = 0.0
    dwelling_id: int | None = None   # Place.id de la vivienda
    location_id: int | None = None
