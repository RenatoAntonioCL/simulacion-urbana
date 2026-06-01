"""Tests de invariantes (Semana 1). Si uno falla, se para y se arregla; no se acumula."""

from __future__ import annotations

from citysim import invariants
from citysim.config import SimConfig
from citysim.eventlog.log import EventLog
from citysim.scheduler.clock import Scheduler
from citysim.seed.seeder import seed_world


def _run(seed: int = 42, days: int = 30):
    config = SimConfig(seed=seed)
    world = seed_world(config)
    log = EventLog()
    Scheduler(config).run(world, log, days=days)
    return world, log


def test_seeded_world_is_valid():
    world = seed_world(SimConfig(seed=42))
    invariants.check_all(world)
    assert len(world.persons) == 100
    assert len(world.households) == 30


def test_population_balance_after_run():
    world, _ = _run()
    invariants.check_population_balance(world)


def test_valid_ranges_after_run():
    world, _ = _run()
    invariants.check_valid_ranges(world)


def test_referential_integrity_after_run():
    world, _ = _run()
    invariants.check_referential_integrity(world)
