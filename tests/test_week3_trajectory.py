"""Gate Semana 3 — Trayectoria: el pasado pesa.

Gate: dos agentes idénticos en rasgos pero con historias distintas (uno con un
recuerdo negativo reciente, otro sin él) deben comportarse distinto hoy. La emoción
decae: tras un shock, el malestar se recupera a un ritmo coherente con la resiliencia.
"""

from __future__ import annotations

import pytest

from citysim.state.person import MemoryTrace, Needs, Person, Traits
from citysim.systems import decision, emotion as emotion_sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _person(pid: int, resilience: float = 0.3, **kwargs) -> Person:
    traits = Traits(
        ambition=0.6,
        sociability=0.4,
        risk_tolerance=0.5,
        conscientiousness=0.5,
        resilience=resilience,
    )
    needs = Needs(
        belonging=0.5,
        autonomy=0.5,
        purpose=0.5,
        security=0.40,
        stimulation=0.60,
    )
    return Person(
        id=pid,
        employer_id=1,
        money=2000.0,
        energy=0.50,
        traits=traits,
        needs=needs,
        **kwargs,
    )


def _bad_memory(age_ticks: int = 2) -> MemoryTrace:
    return MemoryTrace(event_type="unemployment", valence=-0.8, intensity=0.9, age_ticks=age_ticks)


# ---------------------------------------------------------------------------
# Tests de emotion.compute()
# ---------------------------------------------------------------------------

class TestEmotionCompute:
    def test_sin_memoria_neutral(self):
        p = _person(1)
        assert emotion_sys.compute(p) == 0.0

    def test_memoria_negativa_da_mal_animo(self):
        p = _person(1)
        p.memory = [_bad_memory()]
        assert emotion_sys.compute(p) < 0.0

    def test_memoria_positiva_da_buen_animo(self):
        p = _person(1)
        p.memory = [MemoryTrace("goal_achieved", valence=0.8, intensity=0.8, age_ticks=0)]
        assert emotion_sys.compute(p) > 0.0

    def test_emocion_decae_con_el_tiempo(self):
        p_reciente = _person(1)
        p_reciente.memory = [_bad_memory(age_ticks=1)]
        p_viejo = _person(2)
        p_viejo.memory = [_bad_memory(age_ticks=30)]
        assert emotion_sys.compute(p_viejo) > emotion_sys.compute(p_reciente)

    def test_resiliencia_acelera_recuperacion(self):
        resiliente = _person(1, resilience=0.9)
        fragil = _person(2, resilience=0.1)
        for p in (resiliente, fragil):
            p.memory = [_bad_memory(age_ticks=10)]
        assert emotion_sys.compute(resiliente) > emotion_sys.compute(fragil)


# ---------------------------------------------------------------------------
# Gate: historias distintas → decisiones distintas
# ---------------------------------------------------------------------------

class TestHistoriaShapesDecision:
    """Dos agentes con rasgos idénticos pero distinta memoria deciden distinto."""

    def _par(self):
        alice = _person(1)
        bob = _person(2)
        # Alice tiene recuerdo reciente de desempleo (simula un despido)
        alice.memory = [_bad_memory(age_ticks=2)]
        return alice, bob

    def test_animos_distintos(self):
        alice, bob = self._par()
        assert emotion_sys.compute(alice) < emotion_sys.compute(bob)

    def test_decisiones_distintas(self):
        """Gate central: mismos rasgos, distinta historia → distinta acción."""
        alice, bob = self._par()
        assert decision.choose(alice) != decision.choose(bob)

    def test_alice_descansa_bob_trabaja(self):
        """El despido de Alice la lleva a descansar; Bob, sin ese peso, trabaja."""
        alice, bob = self._par()
        assert decision.choose(bob) == "work"
        assert decision.choose(alice) == "rest"
