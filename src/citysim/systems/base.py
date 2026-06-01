"""Contrato de los systems y su contexto de ejecución.

Un System es una función pura `(World, TickContext) -> list[Event]`. No muta el World.
Toda aleatoriedad sale de `ctx.rng` (ADR-0002). Cada system se describe con un
`SystemSpec` que declara su escala y su capa, para que el scheduler lo ordene y filtre.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from ..rng import Rng
from ..state.enums import Layer, TimeScale
from ..state.event import Event
from ..state.world import World


@dataclass
class TickContext:
    """Lo que un system recibe además del World."""

    tick: int
    scale: TimeScale
    rng: Rng


class System(Protocol):
    """Firma de un system. Lee el mundo, devuelve eventos; nunca muta."""

    def __call__(self, world: World, ctx: TickContext) -> list[Event]: ...


@dataclass
class SystemSpec:
    """Registro de un system: qué hace, en qué escala y bajo qué capa corre.

    `order` fija la posición dentro de una misma escala (ver el bucle del agente en
    ARCHITECTURE.md §5).
    """

    name: str
    fn: System
    scale: TimeScale
    layer: Layer
    order: int = 100


# Funciones puras de ayuda compartidas por varios systems.

def clamp01(x: float) -> float:
    """Restringe a [0, 1]. Sostiene el invariante de rangos válidos."""
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


# Marcador de tipo para fábricas de systems (útil al parametrizar por config).
SystemFactory = Callable[[], SystemSpec]
