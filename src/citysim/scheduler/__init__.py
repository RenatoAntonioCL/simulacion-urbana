"""scheduler/ — el reloj. Orquesta los ticks multi-escala y el orden de los systems."""

from .clock import Scheduler, build_default_registry

__all__ = ["Scheduler", "build_default_registry"]
