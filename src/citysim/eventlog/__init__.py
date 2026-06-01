"""eventlog/ — el registro. Aplica eventos al estado y guarda el historial.

Único componente con permiso de escritura sobre el World (ADR-0001).
"""

from .apply import apply_event
from .log import EventLog

__all__ = ["EventLog", "apply_event"]
