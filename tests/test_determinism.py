"""Gate de determinismo: mismo seed ⇒ mismo run, reproducible.

Desde la Semana 2 el log **diverge por seed**: los rasgos se siembran con el RNG y guían
las decisiones, así que dos seeds producen historias distintas. Validamos:
  - mismo seed ⇒ mismo log (reproducibilidad),
  - seeds distintos ⇒ logs distintos (la semilla importa de punta a punta),
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


def test_different_seed_different_log():
    assert _log_fingerprint(42, 15) != _log_fingerprint(7, 15)


def test_same_seed_same_initial_world():
    assert _world_fingerprint(42) == _world_fingerprint(42)


def test_different_seed_different_initial_world():
    assert _world_fingerprint(42) != _world_fingerprint(7)
