"""Invariantes del sistema — la espina anti-deuda técnica (plan, §espina).

Propiedades que NUNCA deben romperse. Se chequean en cada run. Si una falla, se para y
se arregla: no se acumula deuda. Cada función levanta AssertionError con contexto.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .state.enums import EventType
from .state.world import World

if TYPE_CHECKING:
    from .eventlog.log import EventLog


def check_population_balance(world: World) -> None:
    """Cuadre poblacional: vivos + muertos = nacidos. Sin fugas."""
    living = len(world.living_persons())
    dead = world.dead_count
    born = world.born_count
    assert living + dead == born, (
        f"Cuadre poblacional roto: vivos({living}) + muertos({dead}) != nacidos({born})"
    )


def check_valid_ranges(world: World) -> None:
    """Rangos válidos: energía, bienestar, salud, rasgos y necesidades ∈ [0, 1]; edad ≥ 0."""
    for p in world.persons.values():
        assert p.age >= 0, f"Persona {p.id}: edad negativa ({p.age})"
        scalars = (("energy", p.energy), ("wellbeing", p.wellbeing), ("health", p.health))
        traits = (
            ("sociability", p.traits.sociability), ("ambition", p.traits.ambition),
            ("risk_tolerance", p.traits.risk_tolerance),
            ("conscientiousness", p.traits.conscientiousness),
            ("resilience", p.traits.resilience),
        )
        needs = (
            ("belonging", p.needs.belonging), ("autonomy", p.needs.autonomy),
            ("purpose", p.needs.purpose), ("security", p.needs.security),
            ("stimulation", p.needs.stimulation),
        )
        for name, value in scalars + traits + needs:
            assert 0.0 <= value <= 1.0, f"Persona {p.id}: {name} fuera de [0,1] ({value})"


def check_referential_integrity(world: World) -> None:
    """Integridad referencial: relaciones y hogares apuntan a entidades existentes."""
    for rel in world.relationships.values():
        assert rel.a_id in world.persons, f"Relación {rel.id}: a_id inexistente ({rel.a_id})"
        assert rel.b_id in world.persons, f"Relación {rel.id}: b_id inexistente ({rel.b_id})"
    for hh in world.households.values():
        for mid in hh.member_ids:
            assert mid in world.persons, f"Hogar {hh.id}: integrante inexistente ({mid})"


def check_money_conservation(world: World, log: "EventLog") -> None:
    """Conservación de dinero: no aparece ni desaparece sin un evento que lo explique.

    El dinero total actual debe cuadrar con el inicial (sembrado) más la suma de los
    INCOME menos los EXPENSE registrados. Si no cuadra, algún system movió dinero por
    fuera de un evento (rompe ADR-0001).
    """
    current = sum(p.money for p in world.persons.values())
    net = 0.0
    for ev in log.events:
        if ev.type is EventType.INCOME:
            net += ev.payload["amount"]
        elif ev.type is EventType.EXPENSE:
            net -= ev.payload["amount"]
    expected = world.initial_money_total + net
    assert abs(current - expected) < 1e-6, (
        f"Conservación de dinero rota: total({current:.6f}) != "
        f"inicial({world.initial_money_total:.6f}) + neto({net:.6f})"
    )


def check_all(world: World, log: "EventLog | None" = None) -> None:
    """Chequea todos los invariantes de estado de una vez.

    Si se pasa el `log`, incluye la conservación de dinero (necesita el historial).
    """
    check_population_balance(world)
    check_valid_ranges(world)
    check_referential_integrity(world)
    if log is not None:
        check_money_conservation(world, log)
