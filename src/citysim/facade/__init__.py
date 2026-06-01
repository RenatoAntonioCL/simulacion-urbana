"""Fachada del núcleo (ADR-0011): la única superficie pública para los clientes.

Un cliente —una UI de escritorio hoy, un motor gráfico mañana— importa solo de aquí y
puede crear, avanzar, leer, guardar y cargar un mundo sin tocar el resto del paquete:

    from citysim.config import SimConfig
    from citysim.facade import Simulation

    sim = Simulation(SimConfig(seed=42, n_persons=100))
    sim.advance_days(30)
    estado = sim.state()
    sim.save("mundo.json")
"""

from __future__ import annotations

from .dto import (
    EventDTO,
    HouseholdDTO,
    PersonDTO,
    PlaceDTO,
    RelationshipDTO,
    WorldStateDTO,
)
from .simulation import Simulation

__all__ = [
    "Simulation",
    "PersonDTO",
    "HouseholdDTO",
    "PlaceDTO",
    "RelationshipDTO",
    "EventDTO",
    "WorldStateDTO",
]
