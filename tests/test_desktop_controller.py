"""Tests del cliente de escritorio — presenter y layout (ADR-0011/0012).

Corren **sin pantalla**: ejercitan el `SimController` y `layout`, que son Python puro y
no importan pygame. Verifican que el cliente maneja la fachada correctamente y que
respeta la regla de capas (solo habla con `citysim.facade`/`citysim.config`).
"""

from __future__ import annotations

import ast
from pathlib import Path

from citysim.facade import Simulation
from citysim_desktop import layout
from citysim_desktop.controller import SimController

DESKTOP_SRC = Path(__file__).resolve().parents[1] / "src" / "citysim_desktop"


def _world() -> SimController:
    c = SimController()
    c.create_world(seed=42, n_persons=40, n_households=10, n_businesses=5)
    return c


# --- Avance vía el controlador -----------------------------------------------

def test_create_then_step_advances_one_tick():
    c = _world()
    assert c.screen == "world"
    assert c.clock == (0, 0, 0)
    c.step()
    tick, _day, hour = c.clock
    assert tick == 1 and hour == 1


def test_n_steps_reach_n_ticks():
    c = _world()
    for _ in range(30):
        c.step()
    assert c.clock[0] == 30


def test_update_advances_proportional_to_speed_and_is_deterministic():
    a = _world()
    b = _world()
    a.set_speed(10)
    b.set_speed(10)
    a.toggle_play()
    b.toggle_play()
    # 0.25 s a 10 ticks/s = 2.5 → 2 ticks enteros, resto acumulado.
    a.update(0.25)
    b.update(0.25)
    assert a.clock[0] == 2
    assert a.clock == b.clock
    # El resto (0.5) se completa en el siguiente paso.
    a.update(0.25)
    assert a.clock[0] == 5  # 2.5 + 2.5 = 5.0


def test_paused_update_does_not_advance():
    c = _world()
    c.set_speed(60)
    # playing es False por defecto tras crear.
    c.update(1.0)
    assert c.clock[0] == 0


# --- Persistencia vía el controlador -----------------------------------------

def test_save_load_via_controller_reproduces_state(tmp_path):
    c = _world()
    for _ in range(48):
        c.step()
    path = tmp_path / "w.json"
    c.save(path)

    loaded = SimController()
    loaded.load(path)
    assert loaded.screen == "world"
    assert loaded.clock == c.clock
    assert loaded.world_state() == c.world_state()


# --- Aislamiento de capas (ADR-0011) -----------------------------------------

def test_client_only_imports_facade_and_config():
    """Ningún módulo de citysim_desktop importa de citysim salvo facade/config."""
    allowed = {"citysim.facade", "citysim.config"}
    offenders: list[str] = []
    for py in DESKTOP_SRC.glob("*.py"):
        tree = ast.parse(py.read_text(), filename=str(py))
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
            elif isinstance(node, ast.Import):
                mod = node.names[0].name
            if mod and mod.startswith("citysim") and mod not in allowed:
                offenders.append(f"{py.name}: {mod}")
    assert not offenders, f"imports prohibidos hacia el núcleo: {offenders}"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
        elif isinstance(node, ast.Import):
            mods.update(alias.name for alias in node.names)
    return mods


def test_controller_and_layout_do_not_import_pygame():
    """controller y layout deben poder importarse sin pygame (corren sin display)."""
    for name in ("controller.py", "layout.py"):
        mods = _imported_modules(DESKTOP_SRC / name)
        assert not any(m.split(".")[0] == "pygame" for m in mods), (
            f"{name} no debería importar pygame"
        )


# --- Layout determinista ------------------------------------------------------

def test_layout_is_deterministic_and_within_canvas():
    c = _world()
    state = c.world_state()
    w, h = 800, 600
    pos1 = layout.place_positions(state.places, w, h)
    pos2 = layout.place_positions(state.places, w, h)
    assert pos1 == pos2  # mismo mundo ⇒ misma disposición

    for place in state.places:
        x, y = pos1[place.id]
        assert 0 <= x <= w and 0 <= y <= h

    for person in state.persons:
        px, py = layout.person_position(person, pos1)
        # Cerca del lienzo (con holgura por el jitter).
        assert -50 <= px <= w + 50 and -50 <= py <= h + 50


def test_empty_places_layout_is_safe():
    assert layout.place_positions((), 800, 600) == {}


# --- HUD agregado -------------------------------------------------------------

def test_total_money_matches_state():
    c = _world()
    c.step()
    state = c.world_state()
    expected = sum(p.money for p in state.persons if p.alive)
    assert c.total_money() == expected
