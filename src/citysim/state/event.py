"""Event — la fuente de verdad del sistema (ADR-0001).

Todo cambio relevante se representa como un Event inmutable. Los systems los **emiten**;
solo `eventlog/apply.py` los **aplica** sobre el World. Esto da auditoría causal,
reproducibilidad y la base para la proyección offline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import EventType, TimeScale


@dataclass(frozen=True)
class Event:
    """Un hecho ocurrido en el mundo.

    Attributes:
        type: qué clase de hecho (ver EventType).
        tick: tick horario absoluto en que ocurrió.
        scale: escala del proceso que lo emitió.
        payload: datos del hecho (ids, montos, etc.). Referencias por id (ADR-0004).
        cause: id del evento que lo causó, si lo hay (cadena causal auditable).
    """

    type: EventType
    tick: int
    scale: TimeScale = TimeScale.HOURLY
    payload: dict[str, Any] = field(default_factory=dict)
    cause: int | None = None
