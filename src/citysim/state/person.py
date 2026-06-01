"""Person — un individuo.

Combina tres escalas de estado psicológico (ADR-0006):
  - Traits   : constantes fijadas al nacer. Se almacenan.
  - memory   : registro acumulativo que decae lento. Se almacena.
  - emoción  : NO está aquí. Es transitoria y se recalcula cada tick (systems/emotion).

Prohibido almacenar estados psicológicos arbitrarios ("persona triste"). La emoción
emerge de condiciones observables; ver systems/emotion.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Traits:
    """Rasgos: constantes de personalidad fijadas al nacer (Semana 2).

    Modulan cómo el agente evalúa todo lo demás. Valores en [0, 1]. Se fijan con
    variación poblacional y herencia parcial de los progenitores.
    """

    sociability: float = 0.5       # necesidad de vínculo, tolerancia al aislamiento
    ambition: float = 0.5          # peso de carrera vs ocio
    risk_tolerance: float = 0.5    # cómo evalúa decisiones inciertas
    conscientiousness: float = 0.5  # planificación, constancia, hábitos
    resilience: float = 0.5        # velocidad de recuperación tras eventos negativos


@dataclass
class Needs:
    """Necesidades psicológicas (Semana 2). Valores en [0, 1].

    El bienestar pasa a depender de estas, ponderadas por los rasgos, no solo del dinero.
    """

    belonging: float = 0.5   # vínculos sociales activos
    autonomy: float = 0.5    # control sobre las propias decisiones
    purpose: float = 0.5     # sentirse útil / competente
    security: float = 0.5    # estabilidad económica y física
    stimulation: float = 0.5  # novedad, variedad


@dataclass
class MemoryTrace:
    """Un evento significativo recordado por el agente (Semana 3).

    No se borra: se atenúa. El peso efectivo decrece con la antigüedad.
    """

    event_type: str
    valence: float      # signo/calidad del recuerdo en [-1, 1]
    intensity: float    # fuerza inicial en [0, 1]
    age_ticks: int = 0  # antigüedad; el peso decae en función de esto


@dataclass
class Goal:
    """Meta dinámica (Semana 3): se forma, se persigue, se logra o se abandona."""

    kind: str
    target: float
    progress: float = 0.0
    active: bool = True


@dataclass
class Person:
    """Un individuo de la simulación."""

    id: int

    # --- Estado base (Semana 1) ---
    age: float = 0.0          # años
    money: float = 0.0
    time: float = 24.0        # horas disponibles en el tick/día
    energy: float = 1.0       # [0, 1]
    wellbeing: float = 0.5    # [0, 1]
    health: float = 1.0       # [0, 1]
    location_id: int | None = None  # Place.id actual
    alive: bool = True

    # Vínculos estructurales por id (ADR-0004)
    household_id: int | None = None
    employer_id: int | None = None

    # --- Identidad (Semana 2) ---
    traits: Traits = field(default_factory=Traits)
    needs: Needs = field(default_factory=Needs)

    # --- Trayectoria (Semana 3) ---
    memory: list[MemoryTrace] = field(default_factory=list)
    goals: list[Goal] = field(default_factory=list)
