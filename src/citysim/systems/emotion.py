"""emotion — emoción transitoria por appraisal (ADR-0006, Semana 3).

No es un system del scheduler: es una función pura que devuelve la señal emocional
actual de un agente leyendo su memoria. Se llama desde decision.py cada tick y nunca
se almacena. Prohibido guardar "persona triste" como campo de Person.

La tristeza emerge de (recuerdos negativos recientes × resiliencia baja) y decae
sola con el tiempo porque age_ticks crece y el peso cae exponencialmente.
"""

from __future__ import annotations

import math

from ..state.person import Person


def compute(person: Person) -> float:
    """Señal emocional en [-1, 1]. Negativo = malestar; positivo = bienestar.

    Resiliencia alta → tasa de decaimiento mayor → los recuerdos pesan menos con el tiempo.
    """
    if not person.memory:
        return 0.0

    # La señal es la suma ponderada de los valences (sin normalizar), clampeada a [-1,1].
    # Así, un recuerdo muy antiguo pierde peso absoluto y el mood se acerca a 0 (olvido),
    # en vez de mantenerse al nivel del valence sin importar la antigüedad.
    decay_rate = 0.05 + 0.20 * person.traits.resilience
    raw = 0.0
    for trace in person.memory:
        weight = trace.intensity * math.exp(-decay_rate * trace.age_ticks)
        raw += weight * trace.valence

    return max(-1.0, min(1.0, raw))
