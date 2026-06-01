"""Semana 2 — Identidad: rasgos, necesidades, decisión y economía mínima.

El test central es el **gate**: dos agentes con economía similar pero rasgos opuestos
toman decisiones distintas de forma consistente. Si convergieran, los pesos no servirían.
"""

from __future__ import annotations

from collections import Counter

from citysim.config import SimConfig
from citysim.eventlog.log import EventLog
from citysim.facade import Simulation
from citysim.scheduler.clock import Scheduler
from citysim.seed.seeder import seed_world
from citysim.state.enums import EventType, PlaceType
from citysim.state.person import Person, Traits
from citysim.state.place import Place
from citysim.state.world import World
from citysim.systems import decision


def _ambitious() -> Person:
    return Person(
        id=1, age=30, money=2500, energy=0.9, employer_id=900,
        traits=Traits(sociability=0.1, ambition=0.9, risk_tolerance=0.5,
                      conscientiousness=0.6, resilience=0.5),
    )


def _sociable() -> Person:
    return Person(
        id=2, age=30, money=2500, energy=0.9, employer_id=900,
        traits=Traits(sociability=0.9, ambition=0.1, risk_tolerance=0.5,
                      conscientiousness=0.6, resilience=0.5),
    )


# --- Gate: rasgos opuestos ⇒ decisiones distintas ----------------------------

def test_opposite_traits_choose_differently_one_shot():
    """Con la misma economía, el ambicioso elige trabajar y el sociable socializar."""
    assert decision.choose(_ambitious()) == decision.ACTION_WORK
    assert decision.choose(_sociable()) == decision.ACTION_SOCIALIZE


def test_opposite_traits_stay_differentiated_over_time():
    """A lo largo de varios ticks, la acción dominante de cada uno difiere y es estable."""
    world = World()
    world.places[900] = Place(id=900, type=PlaceType.BUSINESS, capacity=10)
    world.persons[1] = _ambitious()
    world.persons[2] = _sociable()
    world.initial_money_total = sum(p.money for p in world.persons.values())

    log = EventLog()
    Scheduler(SimConfig(seed=1)).run(world, log, days=1)  # 24 ticks

    chosen: dict[int, Counter] = {1: Counter(), 2: Counter()}
    for ev in log.events:
        if ev.type is EventType.ACTION_CHOSEN:
            chosen[ev.payload["person_id"]][ev.payload["action"]] += 1

    dom_ambitious = chosen[1].most_common(1)[0][0]
    dom_sociable = chosen[2].most_common(1)[0][0]
    assert dom_ambitious == decision.ACTION_WORK
    assert dom_sociable == decision.ACTION_SOCIALIZE
    assert dom_ambitious != dom_sociable


# --- Rasgos sembrados con variación ------------------------------------------

def test_seeded_traits_vary_across_population():
    world = seed_world(SimConfig(seed=42))
    ambitions = {round(p.traits.ambition, 4) for p in world.persons.values()}
    # Si todos fueran 0.5 (sin variación), habría un único valor.
    assert len(ambitions) > 50
    assert all(0.0 <= p.traits.ambition <= 1.0 for p in world.persons.values())


# --- La economía mueve dinero, conservándolo ---------------------------------

def test_economy_moves_money_and_conserves_it():
    sim = Simulation(SimConfig(seed=42))
    before = sum(p.money for p in sim.state().persons)
    sim.advance_days(10)
    after = sum(p.money for p in sim.state().persons)
    assert after != before              # la economía efectivamente movió dinero
    sim.check_invariants()              # …pero conservándolo (incluye el check de dinero)


# --- La emoción NO se persiste (ADR-0006) ------------------------------------

def test_person_does_not_store_emotion():
    import dataclasses

    field_names = {f.name for f in dataclasses.fields(Person)}
    for forbidden in ("emotion", "mood", "feeling", "emocion", "animo"):
        assert forbidden not in field_names, f"Person no debe persistir '{forbidden}' (ADR-0006)"


# --- La fachada expone la identidad (aditivo) --------------------------------

def test_facade_exposes_traits_and_needs():
    sim = Simulation(SimConfig(seed=42))
    sim.advance_days(2)
    p = sim.state().persons[0]
    # Rasgos y necesidades presentes y en rango.
    assert 0.0 <= p.traits.ambition <= 1.0
    assert 0.0 <= p.needs.belonging <= 1.0
    # current_action existe (puede ser None antes de decidir, str tras avanzar).
    assert p.current_action is None or isinstance(p.current_action, str)
