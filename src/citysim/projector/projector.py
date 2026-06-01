"""Proyección offline (Semana 4) — stub.

Al reconectar NO se simula tick a tick el tiempo ausente: se proyecta un estado
consistente separando procesos por naturaleza:

  Deterministas (calculables en salto): envejecimiento, contratos, pagos recurrentes,
    demografía base.
  Estocásticos (muestreados, no simulados): accidentes, encuentros sociales, eventos de
    salud agudos.
"""

from __future__ import annotations

from ..rng import Rng
from ..state.world import World


def project_forward(world: World, elapsed_days: int, rng: Rng) -> World:
    """Proyecta el mundo `elapsed_days` hacia adelante sin simular cada tick."""
    raise NotImplementedError("projector: pendiente Semana 4")
