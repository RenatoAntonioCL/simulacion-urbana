"""Tests de la capa de fachada (ADR-0011).

Verifican el contrato que protege a los clientes: determinismo a través de la fachada,
round-trip de guardado, aislamiento de los DTOs y que los invariantes siguen pasando.
"""

from __future__ import annotations

from citysim.config import SimConfig
from citysim.facade import Simulation


def _sim(seed: int = 42) -> Simulation:
    return Simulation(SimConfig(seed=seed))


# --- Determinismo a través de la fachada (refuerza ADR-0002) -----------------

def test_same_config_same_state_and_log():
    a = _sim(42)
    b = _sim(42)
    a.advance_days(15)
    b.advance_days(15)

    assert a.tick == b.tick
    assert a.state() == b.state()
    assert a.recent_events() == b.recent_events()
    # La huella del log interno también debe coincidir.
    assert a._log.fingerprint() == b._log.fingerprint()


def test_advance_equivalence_ticks_vs_days():
    by_days = _sim(42)
    by_ticks = _sim(42)
    by_days.advance_days(3)
    by_ticks.advance(3 * 24)
    assert by_days.state() == by_ticks.state()


# --- Round-trip de guardado (replay) -----------------------------------------

def test_save_load_roundtrip(tmp_path):
    original = _sim(42)
    original.advance_days(10)

    path = tmp_path / "mundo.json"
    original.save(path)
    loaded = Simulation.load(path)

    assert loaded.tick == original.tick
    assert loaded.state() == original.state()

    # Avanzar ambas lo mismo tras la carga produce estados idénticos.
    original.advance_days(5)
    loaded.advance_days(5)
    assert loaded.state() == original.state()


def test_save_preserves_custom_config(tmp_path):
    sim = Simulation(SimConfig(seed=7, n_persons=50, n_households=10, n_businesses=5))
    sim.advance_days(2)
    path = tmp_path / "custom.json"
    sim.save(path)

    loaded = Simulation.load(path)
    assert loaded.config.seed == 7
    assert loaded.config.n_persons == 50
    assert loaded.config.n_households == 10
    assert loaded.config.n_businesses == 5
    assert loaded.state() == sim.state()


# --- Aislamiento de los DTOs --------------------------------------------------

def test_mutating_dto_does_not_touch_world():
    sim = _sim(42)
    sim.advance_days(1)

    pid = next(iter(sim._world.persons))
    before = sim._world.persons[pid].money

    dto = sim.person(pid)
    # PersonDTO es frozen: no se puede reasignar el campo.
    import dataclasses

    try:
        dto.money = 999999.0  # type: ignore[misc]
        raise AssertionError("el DTO debería ser inmutable (frozen)")
    except dataclasses.FrozenInstanceError:
        pass

    assert sim._world.persons[pid].money == before


def test_mutating_event_payload_dto_does_not_touch_world():
    sim = _sim(42)
    sim.advance_days(1)

    events = sim.recent_events()
    assert events, "debería haber al menos el evento TICK del último tick"

    # Mutar el payload copiado de un DTO no debe alterar el log/estado interno.
    snapshot = sim._log.fingerprint()
    for e in events:
        e.payload["inyectado"] = "no debería propagarse"
    assert sim._log.fingerprint() == snapshot


# --- Invariantes vía fachada --------------------------------------------------

def test_invariants_hold_after_advance():
    sim = _sim(42)
    sim.check_invariants()  # estado inicial sano
    sim.advance_days(30)
    sim.check_invariants()  # estado final sano


# --- Lectura de eventos -------------------------------------------------------

def test_recent_events_last_tick_starts_with_tick():
    sim = _sim(42)
    sim.advance(1)
    events = sim.recent_events()
    assert events[0].type == "tick"
    assert events[0].tick == 1


def test_recent_events_n_returns_tail():
    sim = _sim(42)
    sim.advance(5)
    last_two = sim.recent_events(2)
    assert len(last_two) == 2


# --- Acoplamiento: el cliente solo necesita citysim.facade -------------------

def test_client_only_imports_facade(tmp_path):
    """Crear, avanzar, leer, guardar y cargar usando solo la fachada y SimConfig."""
    from citysim.config import SimConfig
    from citysim.facade import Simulation

    sim = Simulation(SimConfig(seed=42))
    sim.advance_days(1)
    _ = sim.state()
    _ = sim.recent_events()
    path = tmp_path / "w.json"
    sim.save(path)
    reloaded = Simulation.load(path)
    assert reloaded.state() == sim.state()
