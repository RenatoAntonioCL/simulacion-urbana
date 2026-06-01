"""systems/ — las reglas. Funciones puras: (World, TickContext) -> list[Event].

Ningún system muta el World; emiten eventos que el eventlog aplica (ADR-0001). Cada
system declara su escala y su capa; el scheduler decide cuáles corren (ADR-0005, 0008).
"""

from .base import System, SystemSpec, TickContext

__all__ = ["System", "SystemSpec", "TickContext"]
