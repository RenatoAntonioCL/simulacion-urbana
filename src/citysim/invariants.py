"""Invariantes del sistema — la espina anti-deuda técnica (plan, §espina).

Propiedades que NUNCA deben romperse. Se chequean en cada run. Si una falla, se para y
se arregla: no se acumula deuda. Cada función levanta AssertionError con contexto.
"""

from __future__ import annotations

from .state.world import World


def check_population_balance(world: World) -> None:
    """Cuadre poblacional: vivos + muertos = nacidos. Sin fugas."""
    living = len(world.living_persons())
    dead = world.dead_count
    born = world.born_count
    assert living + dead == born, (
        f"Cuadre poblacional roto: vivos({living}) + muertos({dead}) != nacidos({born})"
    )


def check_valid_ranges(world: World) -> None:
    """Rangos válidos: energía, bienestar, salud ∈ [0, 1]; edad ≥ 0."""
    for p in world.persons.values():
        assert p.age >= 0, f"Persona {p.id}: edad negativa ({p.age})"
        for name, value in (("energy", p.energy), ("wellbeing", p.wellbeing), ("health", p.health)):
            assert 0.0 <= value <= 1.0, f"Persona {p.id}: {name} fuera de [0,1] ({value})"


def check_referential_integrity(world: World) -> None:
    """Integridad referencial: relaciones y hogares apuntan a entidades existentes."""
    for rel in world.relationships.values():
        assert rel.a_id in world.persons, f"Relación {rel.id}: a_id inexistente ({rel.a_id})"
        assert rel.b_id in world.persons, f"Relación {rel.id}: b_id inexistente ({rel.b_id})"
    for hh in world.households.values():
        for mid in hh.member_ids:
            assert mid in world.persons, f"Hogar {hh.id}: integrante inexistente ({mid})"


def check_all(world: World) -> None:
    """Chequea todos los invariantes de estado de una vez."""
    check_population_balance(world)
    check_valid_ranges(world)
    check_referential_integrity(world)
