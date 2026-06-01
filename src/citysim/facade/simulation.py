"""Simulation — la fachada del núcleo (ADR-0011).

Única superficie que los clientes (UI de escritorio hoy; un motor gráfico mañana) pueden
tocar. Orquesta el núcleo —seeder, scheduler, eventlog— y traduce el estado a DTOs de
solo lectura. No contiene reglas de simulación (eso vive en `systems/`) ni muta el
`World` a mano (solo el eventlog lo hace, vía el scheduler).

Convenciones del núcleo respetadas:
  - El tiempo del `World` es HORARIO (`world.tick`); la unidad base de avance es el tick.
  - El determinismo viene del seed del `SimConfig` (ADR-0002): no se crea RNG nuevo.
  - El guardado es por *replay* (config + ticks), no por serialización del `World`: como
    el seeder y los systems son deterministas, reconstruir re-ejecutando los ticks da un
    estado bit-a-bit idéntico, y evita serializar punteros (ADR-0004).
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from .. import invariants
from ..config import SimConfig
from ..eventlog.log import EventLog
from ..scheduler.clock import Scheduler
from ..seed.seeder import seed_world
from ..state.enums import EventType, Layer
from ..state.world import World
from .dto import (
    EventDTO,
    HouseholdDTO,
    PersonDTO,
    PlaceDTO,
    RelationshipDTO,
    WorldStateDTO,
)


class Simulation:
    """Un mundo simulado, manejado a través de operaciones de alto nivel."""

    def __init__(self, config: SimConfig | None = None) -> None:
        self._config = config if config is not None else SimConfig()
        self._world: World = seed_world(self._config)
        self._log = EventLog()
        self._scheduler = Scheduler(self._config)

    # --- Avance ---------------------------------------------------------------

    def advance(self, ticks: int = 1) -> None:
        """Avanza `ticks` horarios, reutilizando el scheduler del núcleo."""
        if ticks < 0:
            raise ValueError("ticks no puede ser negativo")
        for _ in range(ticks):
            self._scheduler.tick(self._world, self._log)

    def advance_days(self, days: int) -> None:
        """Avanza `days` días (= days * 24 ticks horarios)."""
        if days < 0:
            raise ValueError("days no puede ser negativo")
        self.advance(days * 24)

    # --- Reloj (lectura) ------------------------------------------------------

    @property
    def config(self) -> SimConfig:
        return self._config

    @property
    def tick(self) -> int:
        return self._world.tick

    @property
    def day(self) -> int:
        return self._world.day

    @property
    def hour(self) -> int:
        return self._world.hour

    # --- Lectura de estado (solo DTOs) ---------------------------------------

    def state(self) -> WorldStateDTO:
        """Foto completa del mundo como DTOs de solo lectura."""
        w = self._world
        return WorldStateDTO(
            tick=w.tick,
            day=w.day,
            hour=w.hour,
            n_persons_alive=len(w.living_persons()),
            born_count=w.born_count,
            dead_count=w.dead_count,
            persons=tuple(PersonDTO.from_entity(p) for p in w.persons.values()),
            households=tuple(HouseholdDTO.from_entity(h) for h in w.households.values()),
            places=tuple(PlaceDTO.from_entity(pl) for pl in w.places.values()),
            relationships=tuple(
                RelationshipDTO.from_entity(r) for r in w.relationships.values()
            ),
        )

    def persons(self) -> list[PersonDTO]:
        return [PersonDTO.from_entity(p) for p in self._world.persons.values()]

    def person(self, pid: int) -> PersonDTO | None:
        p = self._world.persons.get(pid)
        return PersonDTO.from_entity(p) if p is not None else None

    def recent_events(self, n: int | None = None) -> list[EventDTO]:
        """Eventos recientes como DTOs.

        - `n=None`: los del último tick horario, es decir desde el último Event TICK
          (inclusive) hasta el final del log.
        - `n=k`: los últimos `k` eventos.
        """
        events = self._log.events
        if n is not None:
            if n < 0:
                raise ValueError("n no puede ser negativo")
            tail = events[len(events) - n :] if n else []
            return [EventDTO.from_entity(e) for e in tail]

        # Último tick: retroceder hasta el último Event TICK.
        start = 0
        for i in range(len(events) - 1, -1, -1):
            if events[i].type is EventType.TICK:
                start = i
                break
        return [EventDTO.from_entity(e) for e in events[start:]]

    # --- Invariantes ----------------------------------------------------------

    def check_invariants(self) -> None:
        """Reutiliza los invariantes del núcleo sobre el estado actual."""
        invariants.check_all(self._world)

    # --- Persistencia (replay: config + ticks) -------------------------------

    def save(self, path: str | Path) -> None:
        """Guarda el mundo como `config + ticks`. Reconstruible por replay (ver módulo)."""
        data = {
            "config": _config_to_dict(self._config),
            "ticks": self._world.tick,
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Simulation":
        """Carga un mundo guardado: reconstruye desde el seed y re-ejecuta los ticks."""
        data = json.loads(Path(path).read_text())
        config = _config_from_dict(data["config"])
        sim = cls(config)
        sim.advance(int(data["ticks"]))
        return sim


# --- Serialización del SimConfig (privado) -----------------------------------

def _config_to_dict(config: SimConfig) -> dict:
    return {
        "seed": config.seed,
        "n_persons": config.n_persons,
        "n_households": config.n_households,
        "n_businesses": config.n_businesses,
        "n_neighborhoods": config.n_neighborhoods,
        "sim_days": config.sim_days,
        "active_layers": sorted(layer.value for layer in config.active_layers),
    }


def _config_from_dict(data: dict) -> SimConfig:
    base = SimConfig()
    return replace(
        base,
        seed=data["seed"],
        n_persons=data["n_persons"],
        n_households=data["n_households"],
        n_businesses=data["n_businesses"],
        n_neighborhoods=data["n_neighborhoods"],
        sim_days=data["sim_days"],
        active_layers={Layer(v) for v in data["active_layers"]},
    )
