"""Place — un lugar físico (casa, empresa, escuela, hospital, comercio, parque)."""

from __future__ import annotations

from dataclasses import dataclass

from .enums import PlaceType


@dataclass
class Place:
    id: int
    type: PlaceType
    capacity: int = 0
    location_id: int = 0   # barrio / coordenada abstracta
    open_hour: int = 0     # horario de apertura (hora del día)
    close_hour: int = 24
