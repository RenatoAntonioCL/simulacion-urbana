"""Vista de Ciudadano (Semana 4) — stub.

Vista de solo-lectura: Trabajo · Familia · Transporte. No muta el estado; solo lo
proyecta para el rol. Para el MVP basta con esta única vista.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..state.world import World


@dataclass
class CitizenView:
    """Proyección de solo-lectura del mundo desde la perspectiva de un ciudadano."""

    world: World
    person_id: int

    def summary(self) -> dict:
        raise NotImplementedError("observers.citizen: pendiente Semana 4")
