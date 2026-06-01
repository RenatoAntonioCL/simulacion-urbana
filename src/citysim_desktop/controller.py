"""SimController — el presenter del cliente de escritorio (ADR-0011).

Python puro: **no importa pygame**. Mantiene la `Simulation`, traduce las intenciones
de la UI (crear mundo, play/pausa, paso, velocidad, guardar, cargar) en llamadas a la
fachada, y expone lo que la vista necesita dibujar (DTOs de solo lectura + estado de UI).

Esta separación es lo que hace testeable al cliente sin pantalla y lo que deja la vista
(Pygame hoy; un motor gráfico mañana) como una pieza reemplazable.

Importa SOLO de `citysim.facade` y `citysim.config` (regla de cliente, ADR-0011).
"""

from __future__ import annotations

from pathlib import Path

from citysim.config import SimConfig
from citysim.facade import EventDTO, Simulation, WorldStateDTO

# Pantallas de la UI.
SCREEN_CREATE = "create"
SCREEN_WORLD = "world"

# Velocidad: cuántos ticks horarios se avanzan por segundo al estar en play.
MIN_SPEED = 1
MAX_SPEED = 240
DEFAULT_SPEED = 12


class SimController:
    """Estado y operaciones del cliente, independientes del motor de dibujo."""

    def __init__(self) -> None:
        self.screen: str = SCREEN_CREATE
        self._sim: Simulation | None = None
        self.playing: bool = False
        self.speed: int = DEFAULT_SPEED  # ticks por segundo
        self._accumulator: float = 0.0   # ticks pendientes (fracción acumulada)

    # --- Creación -------------------------------------------------------------

    def create_world(
        self,
        *,
        seed: int = 42,
        n_persons: int = 100,
        n_households: int = 30,
        n_businesses: int = 20,
    ) -> None:
        """Crea un mundo nuevo desde la config y pasa a la pantalla del mundo."""
        config = SimConfig(
            seed=seed,
            n_persons=n_persons,
            n_households=n_households,
            n_businesses=n_businesses,
        )
        self._sim = Simulation(config)
        self.screen = SCREEN_WORLD
        self.playing = False
        self._accumulator = 0.0

    @property
    def has_world(self) -> bool:
        return self._sim is not None

    # --- Reloj / playback -----------------------------------------------------

    def toggle_play(self) -> None:
        if self._sim is not None:
            self.playing = not self.playing

    def set_speed(self, ticks_per_second: int) -> None:
        self.speed = max(MIN_SPEED, min(MAX_SPEED, ticks_per_second))

    def faster(self) -> None:
        self.set_speed(self.speed * 2)

    def slower(self) -> None:
        self.set_speed(self.speed // 2)

    def step(self) -> None:
        """Avanza exactamente un tick horario (sin importar el estado de play)."""
        if self._sim is not None:
            self._sim.advance(1)

    def update(self, dt: float) -> None:
        """Avanza la simulación según el tiempo transcurrido (`dt` en segundos).

        Solo avanza ticks **enteros**; la fracción se acumula para el próximo frame, de
        modo que el ritmo no depende del framerate y el avance sigue siendo determinista.
        """
        if self._sim is None or not self.playing:
            return
        self._accumulator += dt * self.speed
        whole = int(self._accumulator)
        if whole > 0:
            self._sim.advance(whole)
            self._accumulator -= whole

    @property
    def clock(self) -> tuple[int, int, int]:
        """(tick, día, hora). Si no hay mundo, todo en cero."""
        if self._sim is None:
            return (0, 0, 0)
        return (self._sim.tick, self._sim.day, self._sim.hour)

    # --- Lectura para la vista (solo DTOs) ------------------------------------

    def world_state(self) -> WorldStateDTO | None:
        return self._sim.state() if self._sim is not None else None

    def recent_events(self, n: int = 12) -> list[EventDTO]:
        if self._sim is None:
            return []
        return self._sim.recent_events(n)

    def total_money(self) -> float:
        """Agregado simple para el HUD: dinero total de las personas vivas."""
        state = self.world_state()
        if state is None:
            return 0.0
        return sum(p.money for p in state.persons if p.alive)

    # --- Persistencia ---------------------------------------------------------

    def save(self, path: str | Path) -> None:
        if self._sim is not None:
            self._sim.save(path)

    def load(self, path: str | Path) -> None:
        """Carga un mundo guardado y pasa a la pantalla del mundo."""
        self._sim = Simulation.load(path)
        self.screen = SCREEN_WORLD
        self.playing = False
        self._accumulator = 0.0
