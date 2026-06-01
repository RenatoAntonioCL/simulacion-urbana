"""Seeder — construye la población inicial de forma determinista.

Escala MVP: 100 personas · 30 hogares · 20 empresas · 1 barrio. Toda la aleatoriedad
sale del RNG sembrado (ADR-0002): mismo seed ⇒ misma población.

Semana 1 genera estado base (sin rasgos). Los rasgos y necesidades se incorporan en la
Semana 2 (con variación poblacional y herencia parcial).
"""

from __future__ import annotations

from ..config import SimConfig
from ..rng import Rng
from ..state.enums import PlaceType
from ..state.household import Household
from ..state.person import Person
from ..state.place import Place
from ..state.world import World


def seed_world(config: SimConfig) -> World:
    """Devuelve un World poblado de forma determinista a partir del config."""
    world = World()
    rng = Rng(config.seed).derive("seeder")

    # --- Lugares: 1 barrio, viviendas y empresas ---
    next_place_id = 0
    for _ in range(config.n_households):
        world.places[next_place_id] = Place(
            id=next_place_id, type=PlaceType.HOME, capacity=6, location_id=0
        )
        next_place_id += 1
    for _ in range(config.n_businesses):
        world.places[next_place_id] = Place(
            id=next_place_id, type=PlaceType.BUSINESS, capacity=20, location_id=0,
            open_hour=8, close_hour=18,
        )
        next_place_id += 1

    home_ids = [p.id for p in world.places.values() if p.type is PlaceType.HOME]

    # --- Personas ---
    for pid in range(config.n_persons):
        world.persons[pid] = Person(
            id=pid,
            age=rng.uniform(0, 80),
            money=rng.uniform(0, 5000),
            energy=rng.uniform(0.5, 1.0),
            wellbeing=0.5,
            health=rng.uniform(0.7, 1.0),
        )
        world.born_count += 1

    # --- Hogares: repartir personas en hogares ---
    person_ids = list(world.persons.keys())
    rng.shuffle(person_ids)
    for hid in range(config.n_households):
        world.households[hid] = Household(id=hid, dwelling_id=home_ids[hid], location_id=0)

    for i, pid in enumerate(person_ids):
        hid = i % config.n_households
        world.households[hid].member_ids.append(pid)
        world.persons[pid].household_id = hid
        world.persons[pid].location_id = world.households[hid].dwelling_id

    return world
