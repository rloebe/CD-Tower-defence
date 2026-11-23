"""Trať: body, po kterých jedou nepřátelé, výpočty vzdáleností a kreslení mapy."""

import math

import pygame

import settings

# Body trati v pixelech. Nepřátelé jedou od prvního bodu k poslednímu.
# První bod je mimo obrazovku, aby nepřátelé "přijeli" zleva.
PATH = [
    (-30, 150),
    (200, 150),
    (200, 450),
    (420, 450),
    (420, 230),
    (650, 230),
    (650, 520),
    (860, 520),
    (860, 360),
    (905, 360),
]

# Cílová stanice (obdélník na konci trati)
STATION_RECT = pygame.Rect(870, 290, 85, 130)
STATION_NAME = "Praha hl. n."
START_NAME = "Kolín"

TRACK_WIDTH = 34  # šířka štěrkového lože v pixelech


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
    closest_x = ax + t * dx
    closest_y = ay + t * dy
    return math.hypot(px - closest_x, py - closest_y)


def is_on_path(pos, path=PATH, margin=TRACK_WIDTH / 2):
    """True, když je bod `pos` blíž k trati než `margin` pixelů.

    Hodí se pro kontrolu, jestli se na místo dá postavit věž.
    """
    return any(distance_to_segment(pos, a, b) < margin for a, b in zip(path, path[1:]))


# ---------- Kreslení ----------

_font_cache = {}


def _font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def _draw_background(surface):
    surface.fill(settings.GRASS)
    # jemná šachovnice, aby tráva nebyla úplně plochá
    tile = 48
    for x in range(0, settings.WIDTH, tile):
        for y in range(settings.HUD_HEIGHT, settings.HEIGHT, tile):
            if (x // tile + y // tile) % 2 == 0:
                pygame.draw.rect(surface, settings.GRASS_DARK, (x, y, tile, tile))


def _draw_rails(surface, path):
    # 1) štěrkové lože
    for a, b in zip(path, path[1:]):
        pygame.draw.line(surface, settings.BALLAST, a, b, TRACK_WIDTH)
    for point in path:
        pygame.draw.circle(surface, settings.BALLAST, point, TRACK_WIDTH // 2)

    # 2) pražce a 3) kolejnice, úsek po úseku
    for (x1, y1), (x2, y2) in zip(path, path[1:]):
        length = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / length, (y2 - y1) / length  # směr úseku
        nx, ny = -uy, ux  # kolmice na směr

        steps = int(length // 14)
        for i in range(steps + 1):
            cx, cy = x1 + ux * i * 14, y1 + uy * i * 14
            pygame.draw.line(
                surface, settings.SLEEPER,
                (cx - nx * 13, cy - ny * 13), (cx + nx * 13, cy + ny * 13), 4,
            )

        for side in (-7, 7):
            pygame.draw.line(
                surface, settings.RAIL,
                (x1 + nx * side, y1 + ny * side), (x2 + nx * side, y2 + ny * side), 3,
            )
    for x, y in path[1:-1]:
        pygame.draw.circle(surface, settings.RAIL, (x, y), 8, 3)


def _draw_station(surface):
    roof = STATION_RECT.inflate(10, 0)
    roof.height = 24
    roof.bottom = STATION_RECT.top + 6
    pygame.draw.rect(surface, settings.STATION, STATION_RECT, border_radius=4)
    pygame.draw.rect(surface, settings.STATION_ROOF, roof, border_radius=4)
    # okna
    for row in range(3):
        for col in range(2):
            window = pygame.Rect(0, 0, 16, 18)
            window.topleft = (STATION_RECT.x + 16 + col * 34, STATION_RECT.y + 22 + row * 32)
            pygame.draw.rect(surface, settings.WHITE, window, border_radius=2)

    label = _font(22).render(STATION_NAME, True, settings.WHITE)
    box = label.get_rect(midbottom=(STATION_RECT.centerx - 20, STATION_RECT.top - 26))
    box.right = min(box.right, settings.WIDTH - 6)
    pygame.draw.rect(surface, settings.CD_BLUE, box.inflate(10, 6), border_radius=4)
    surface.blit(label, box)


def _draw_start_sign(surface):
    label = _font(22).render(START_NAME, True, settings.WHITE)
    box = label.get_rect(topleft=(10, PATH[0][1] - 52))
    pygame.draw.rect(surface, settings.CD_BLUE, box.inflate(10, 6), border_radius=4)
    surface.blit(label, box)


def draw_track(surface, path=PATH):
    """Nakreslí celou mapu: trávu, trať, start a cílovou stanici."""
    _draw_background(surface)
    _draw_rails(surface, path)
    _draw_station(surface)
    _draw_start_sign(surface)
