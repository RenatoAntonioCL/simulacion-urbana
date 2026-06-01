"""Tests del directorio de datos del usuario y del modo smoke (ADR-0013).

`paths` es Python puro (sin pygame): se testea siempre. El smoke necesita pygame, así que
se saltea si no está instalado.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from citysim_desktop import paths


def test_user_data_dir_windows(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path))
    d = paths.user_data_dir("citysim")
    assert d == tmp_path / "citysim"
    assert d.is_dir()


def test_user_data_dir_macos(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "darwin")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    d = paths.user_data_dir("citysim")
    assert d == tmp_path / "Library" / "Application Support" / "citysim"
    assert d.is_dir()


def test_user_data_dir_linux_xdg(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    d = paths.user_data_dir("citysim")
    assert d == tmp_path / "citysim"
    assert d.is_dir()


def test_user_data_dir_linux_fallback(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    d = paths.user_data_dir("citysim")
    assert d == tmp_path / ".local" / "share" / "citysim"


def test_default_save_path_is_under_data_dir(monkeypatch, tmp_path):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    p = paths.default_save_path("citysim")
    assert p == tmp_path / "citysim" / "world_save.json"


# --- Modo smoke (requiere pygame) --------------------------------------------

def test_smoke_runs_headless(monkeypatch):
    """El arranque headless crea un mundo, avanza y termina sin lanzar."""
    pg = pytest.importorskip("pygame")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    # Algunos builds de pygame no traen el módulo de fuentes utilizable (p. ej. el bug
    # de pygame.font en Python 3.14). Si no se puede inicializar, no es lo que probamos.
    try:
        pg.font.init()
        pg.font.Font(None, 16)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"pygame.font no disponible en este entorno: {exc}")

    from citysim_desktop import view

    view.run_smoke(ticks=24)  # no debe lanzar
