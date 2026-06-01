"""Aleatoriedad determinista (ADR-0002).

Un único generador sembrado se crea al arranque y se inyecta en todo el sistema vía
`TickContext`. **Nunca** se usa el `random` global. Los sub-streams (p. ej. uno por
system) se derivan de forma determinista del seed maestro para no perder
reproducibilidad.

    rng = Rng(seed=42)
    sub = rng.derive("economy")   # determinista a partir de (seed, "economy")
"""

from __future__ import annotations

import random
import zlib


class Rng:
    """Envoltura fina sobre `random.Random` con derivación determinista de streams."""

    def __init__(self, seed: int) -> None:
        self.seed = seed
        self._r = random.Random(seed)

    def derive(self, label: str) -> "Rng":
        """Crea un sub-generador reproducible a partir de (seed maestro, etiqueta).

        Mismo seed + misma etiqueta => misma secuencia, siempre. Permite que cada
        system tenga su propio stream sin acoplarse al orden de llamadas de los demás.
        """
        mixed = self.seed ^ zlib.crc32(label.encode("utf-8"))
        return Rng(mixed & 0xFFFFFFFF)

    # --- API mínima delegada (se amplía según haga falta) ---

    def random(self) -> float:
        return self._r.random()

    def uniform(self, a: float, b: float) -> float:
        return self._r.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._r.randint(a, b)

    def choice(self, seq):
        return self._r.choice(seq)

    def gauss(self, mu: float, sigma: float) -> float:
        return self._r.gauss(mu, sigma)

    def shuffle(self, seq) -> None:
        self._r.shuffle(seq)
