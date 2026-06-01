"""Configuración del run: semilla, parámetros y flags de capas (ADR-0005).

Las capas no son fases de código: son flags. El scheduler solo corre los systems cuya
capa esté activa. El MVP arranca con la Capa 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .state.enums import Layer


def _default_layers() -> set[Layer]:
    # MVP: solo Capa 1 (Personas · Hogares · Trabajo · Movilidad).
    return {Layer.L1_BASE}


@dataclass
class SimConfig:
    """Parámetros de un run de simulación."""

    seed: int = 42

    # Escala del MVP (ver simulacion_urbana_v2.md → MVP Inicial).
    n_persons: int = 100
    n_households: int = 30
    n_businesses: int = 20
    n_neighborhoods: int = 1

    # Duración objetivo: un año.
    sim_days: int = 365

    # Capas activas (flags, no fases).
    active_layers: set[Layer] = field(default_factory=_default_layers)

    def is_active(self, layer: Layer) -> bool:
        return layer in self.active_layers
