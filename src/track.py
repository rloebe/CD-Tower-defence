"""Trať, po které jedou nepřátelé: body v políčkách a výpočty vzdáleností.

Nic se tu nekreslí (to dělá scenery.py), takže se to dá testovat bez okna.
"""

import math

# Body trati v políčkách (viz docs/vizualni-design.md). Nepřátelé jedou od Kolína
# (první bod je mimo obrazovku vlevo) až k zarážedlu v Praze hl. n.
PATH = [
    (-2.5, 3.5),
    (3.5, 3.5),
    (3.5, 9.5),
    (7.5, 9.5),
    (7.5, 4.5),
    (11.5, 4.5),
    (11.5, 10.5),
    (14.5, 10.5),
    (14.5, 7.5),
    (18.2, 7.5),
]

TRACK_HALF_WIDTH = 0.47  # polovina šířky štěrkového lože v políčkách


def path_length(path):
    """Celková délka trati (součet délek všech úseků)."""
    total = 0.0
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        total += math.hypot(x2 - x1, y2 - y1)
    return total


def point_at_distance(path, distance):
    """Vrátí bod (x, y), který leží na trati ve vzdálenosti `distance` od začátku.

    Vzdálenost menší než 0 vrátí začátek, větší než délka trati vrátí konec.
    """
    if distance <= 0:
        return path[0]
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        segment = math.hypot(x2 - x1, y2 - y1)
        if distance <= segment:
            t = distance / segment
            return (x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)
        distance -= segment
    return path[-1]


def direction_at_distance(path, distance):
    """Směr jízdy (jednotkový vektor ux, uy) v daném místě trati."""
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        segment = math.hypot(x2 - x1, y2 - y1)
        if distance <= segment:
            return ((x2 - x1) / segment, (y2 - y1) / segment)
        distance -= segment
    (x1, y1), (x2, y2) = path[-2], path[-1]
    segment = math.hypot(x2 - x1, y2 - y1)
    return ((x2 - x1) / segment, (y2 - y1) / segment)


def distance_to_segment(point, a, b):
    """Nejkratší vzdálenost bodu od úsečky a–b."""
    px, py = point
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    # t = jak daleko po úsečce je nejbližší bod (0 = a, 1 = b)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def is_on_path(pos, path=PATH, margin=TRACK_HALF_WIDTH):
    """True, když je bod `pos` blíž k trati než `margin` políček."""
    return any(distance_to_segment(pos, a, b) < margin for a, b in zip(path, path[1:]))


def can_build(col, row):
    """True, když na políčko (sloupec, řádek) jde postavit věž (jen volná tráva)."""
    import world  # world potřebuje tenhle modul, proto se načte až tady

    return (col, row) in world.BUILDABLE
