"""layout — disposición visual determinista a partir de los ids (sin pygame).

El núcleo no tiene geometría: `location_id` es una referencia abstracta, no una
coordenada (ADR-0004). La posición en pantalla es, por tanto, asunto del cliente. Aquí
derivamos posiciones **estables y deterministas** desde los ids: el mismo mundo se ve
igual siempre, y dos clientes muestran lo mismo.

Funciones puras: reciben DTOs + tamaño del lienzo y devuelven coordenadas. No dibujan.
"""

from __future__ import annotations

import math

from citysim.facade import PersonDTO, PlaceDTO

Point = tuple[float, float]


def place_positions(
    places: tuple[PlaceDTO, ...] | list[PlaceDTO],
    width: int,
    height: int,
    margin: int = 60,
) -> dict[int, Point]:
    """Ubica cada lugar en una grilla determinada por su id, dentro del lienzo."""
    positions: dict[int, Point] = {}
    n = len(places)
    if n == 0:
        return positions

    cols = max(1, math.ceil(math.sqrt(n)))
    rows = max(1, math.ceil(n / cols))

    usable_w = max(1, width - 2 * margin)
    usable_h = max(1, height - 2 * margin)
    step_x = usable_w / max(1, cols - 1) if cols > 1 else 0
    step_y = usable_h / max(1, rows - 1) if rows > 1 else 0

    # Orden estable por id para que la grilla no dependa del orden de iteración.
    for slot, place in enumerate(sorted(places, key=lambda p: p.id)):
        col = slot % cols
        row = slot // cols
        x = margin + col * step_x if cols > 1 else width / 2
        y = margin + row * step_y if rows > 1 else height / 2
        positions[place.id] = (x, y)
    return positions


def person_position(
    person: PersonDTO,
    place_pos: dict[int, Point],
    jitter: float = 18.0,
) -> Point:
    """Posición de una persona: junto a su lugar actual, con desplazamiento determinista.

    El jitter se deriva del id de la persona (no del azar) para que su punto sea estable
    entre frames y entre runs con el mismo mundo. Si la persona no tiene lugar conocido,
    cae al centro de la nube de lugares (o al origen si no hay lugares).
    """
    base = place_pos.get(person.location_id) if person.location_id is not None else None
    if base is None:
        base = _centroid(place_pos)

    # Ángulo y radio deterministas a partir del id.
    angle = (person.id * 137.508) % 360  # ángulo áureo: reparte sin solaparse
    radius = jitter * (0.4 + 0.6 * ((person.id % 7) / 6.0))
    dx = radius * math.cos(math.radians(angle))
    dy = radius * math.sin(math.radians(angle))
    return (base[0] + dx, base[1] + dy)


def _centroid(place_pos: dict[int, Point]) -> Point:
    if not place_pos:
        return (0.0, 0.0)
    xs = [p[0] for p in place_pos.values()]
    ys = [p[1] for p in place_pos.values()]
    return (sum(xs) / len(xs), sum(ys) / len(ys))
