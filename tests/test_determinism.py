"""Gate de la Semana 1: mismo seed ⇒ mismo run, reproducible.

Nota sobre el alcance actual: en la Semana 1 el único system es `aging`, que es
determinista y seed-independiente. Por eso el LOG de eventos todavía no diverge entre
seeds: la semilla solo afecta la población inicial (que el seeder genera con el RNG).
La divergencia del log por seed aparecerá al sumar systems estocásticos (Semanas 3-4),
y este test deberá fortalecerse entonces. Hoy validamos:
  - mismo seed ⇒ mismo log (reproducibilidad), y
  - seeds distintos ⇒ poblaciones iniciales distintas.
"""

from __future__ import annotations

from citysim.config import SimConfig
from citysim.eventlog.log import EventLog
from citysim.scheduler.clock import Scheduler
from citysim.seed.seeder import seed_world


def _log_fingerprint(seed: int, days: int) -> str:
    config = SimConfig(seed=seed)
    world = seed_world(config)
    log = EventLog()
    Scheduler(config).run(world, log, days=days)
    return log.fingerprint()


def _world_fingerprint(seed: int) -> tuple:
    world = seed_world(SimConfig(seed=seed))
    return tuple(round(world.persons[i].money, 6) for i in range(len(world.persons)))


def test_same_seed_same_log():
    assert _log_fingerprint(42, 15) == _log_fingerprint(42, 15)


def test_same_seed_same_initial_world():
    assert _world_fingerprint(42) == _world_fingerprint(42)


def test_different_seed_different_initial_world():
    assert _world_fingerprint(42) != _world_fingerprint(7)
