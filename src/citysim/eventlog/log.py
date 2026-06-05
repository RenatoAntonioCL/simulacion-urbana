"""EventLog — buffer + persistencia del historial de eventos (fuente de verdad)."""

from __future__ import annotations

import json
from pathlib import Path

from ..state.event import Event
from ..state.world import World
from .apply import apply_event


class EventLog:
    """Acumula eventos, los aplica al World y persiste el historial.

    El historial completo es la fuente de verdad del run: con el seed y el log se puede
    auditar y, en principio, reconstruir el estado.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    def commit(self, world: World, events: list[Event]) -> None:
        """Aplica una tanda de eventos al World, en orden, y los registra.

        Es el único camino por el que el estado cambia (ADR-0001).
        """
        for ev in events:
            apply_event(world, ev)
            self._events.append(ev)

    @property
    def events(self) -> list[Event]:
        return self._events

    def __len__(self) -> int:
        return len(self._events)

    def to_json(self, path: str | Path) -> None:
        """Serializa el historial a JSON (ADR-0009: JSON primero)."""
        data = [
            {
                "type": ev.type.value,
                "tick": ev.tick,
                "scale": ev.scale.value,
                "payload": ev.payload,
                "cause": ev.cause,
            }
            for ev in self._events
        ]
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def fingerprint(self) -> str:
        """Huella estable del log, para el test de determinismo (mismo seed ⇒ misma huella)."""
        import hashlib

        h = hashlib.sha256()
        for ev in self._events:
            h.update(repr((ev.type.value, ev.tick, ev.scale.value, sorted(ev.payload.items()))).encode())
        return h.hexdigest()
