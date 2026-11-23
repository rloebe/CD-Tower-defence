"""Rozložení mapy podle designu (docs/vizualni-design.md). Vše v políčkách.

Jen data a výpočty – nic se tu nekreslí. Kreslí to scenery.py.
Odsud se taky počítá, kde se smí stavět věže (BUILDABLE).
"""

import random

import iso
import settings
import track

# ---------- koleje a silnice ----------
SIDING = [(15.0, 9.0), (20.5, 9.0)]  # vedlejší kolej v Praze s odstavenou soupravou
MAIN_Y = 14.6  # hlavní trať dole (jen projíždějící vlaky, dekorace)
MAINLINE = [(-6.0, MAIN_Y), (27.0, MAIN_Y)]
ROAD_X = 9.5  # svislá silnice (přes přejezd)
ROAD_Y = 13.5  # vodorovná silnice dole
ROAD_HALF = 0.4  # polovina šířky silnice
CROSSING = (9.5, 4.5)  # železniční přejezd
CROSSING_POSTS = [(8.9, 3.95, 1), (10.1, 5.05, -1)]  # sloupky se závorou: x, y, směr závory

# ---------- budovy a pole: (x0, y0, šířka, hloubka) ----------
PRAHA = (15.0, 4.6, 3.5, 1.8)
KOLIN = (0.3, 1.7, 2.2, 1.05)
BARN = (8.6, 1.3, 1.8, 1.2)
WHEAT = (6.5, 11.2, 6.0, 1.8)
PLOW = (12.6, 2.2, 6.0, 2.1)
HOUSES = [  # x0, y0, šířka, hloubka, barva zdi, barva střechy
    (13.2, 11.7, 1.5, 1.15, (242, 235, 221), (200, 85, 61)),
    (15.3, 11.6, 1.7, 1.25, (244, 227, 181), (142, 74, 50)),
    (17.6, 11.75, 1.4, 1.1, (233, 238, 242), (200, 85, 61)),
]
HAYSTACKS = [(7.4, 2.0), (11.2, 1.8)]
SIGNALS = [(2.85, 2.85), (13.9, 8.3)]

# skály a stromy na skalní plošině vzadu: (sloupec, řádek, výška skály)
ROCKS_HIGH = [(-4, 0, 2), (-3, 1, 1), (-2, 0, 2), (-1, -1, 1), (1, -1, 2), (2, -1, 3), (3, 0, 1),
              (5, -1, 2), (6, -1, 1), (13, 1, 1), (19, 0, 2), (20, 1, 2), (21, 1, 1)]
TREES_HIGH = [(-1, 0), (0, 0), (-2, 1), (-3, 0), (1, 0), (2, 0), (4, 0), (4, -1), (7, 0), (8, 0),
              (9, 0), (10, 0), (11, 0), (12, 0), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1)]

# oblasti, kam se nic nedá (pole, budovy, nádraží, pastvina): x0, y0, x1, y1
RECTS = [
    (6.4, 11.0, 12.6, 13.05),  # pšenice
    (12.5, 2.1, 18.7, 4.4),  # oranice
    (14.8, 4.4, 20.6, 9.6),  # nádraží Praha + souprava
    (8.4, 1.1, 10.6, 2.7),  # stodola
    (-0.2, 1.4, 2.95, 3.1),  # nádraží Kolín
    (4.2, 1.35, 7.0, 2.55),  # pastvina s kravami
]
for h in HOUSES:
    RECTS.append((h[0] - 0.25, h[1] - 0.25, h[0] + h[2] + 0.25, h[1] + h[3] + 0.25))


def is_plateau(col, row):
    """True, když políčko leží na skalní plošině vzadu (výška 1)."""
    return row <= 0 or (row == 1 and (col <= -1 or col >= 13))


def path_dist(x, y, path):
    """Vzdálenost bodu od nejbližšího úseku cesty (v políčkách)."""
    return min(track.distance_to_segment((x, y), a, b) for a, b in zip(path, path[1:]))


def on_road(x, y, margin=0.0):
    on_vertical = abs(x - ROAD_X) < ROAD_HALF + margin and 2.4 - margin < y < ROAD_Y + ROAD_HALF + margin
    on_horizontal = abs(y - ROAD_Y) < ROAD_HALF + margin
    return on_vertical or on_horizontal


def in_rect(x, y, margin=0.0):
    return any(r[0] - margin < x < r[2] + margin and r[1] - margin < y < r[3] + margin for r in RECTS)


# Pozor: kontroly "je to vidět na obrazovce" a "není to pod panelem" se dělají
# v logických pixelech (iso.to_logical), takže nezáleží na velikosti monitoru.
def under_picker(sx, sy):
    px, py, pw, ph = settings.PICKER_RECT
    return px - 16 <= sx <= px + pw + 16 and sy >= py - 12


# ---------- stožáry trakčního vedení podél trati ----------
def _poles():
    poles = []
    total = track.path_length(track.PATH)
    d = 3.0
    while d < total - 0.6:
        px, py = track.point_at_distance(track.PATH, d)
        ux, uy = track.direction_at_distance(track.PATH, d)
        qx, qy = px + uy * 0.58, py - ux * 0.58  # stožár stojí kousek vedle koleje
        near_crossing = abs(px - CROSSING[0]) < 1.3 and abs(py - CROSSING[1]) < 1.3
        if not (near_crossing or in_rect(qx, qy) or is_plateau(int(qx // 1), int(qy // 1)) or qx < -1.5):
            poles.append((qx, qy, px, py))
        d += 3.4
    return poles


POLES = _poles()


# ---------- náhodně rozházené stromy, keře a kameny (vždy stejně díky seed) ----------
def _scatter():
    rng = random.Random(777)
    placed = []
    decor = {"trees": [], "bushes": [], "rocks": []}

    def free(x, y, r):
        if is_plateau(int((x - r) // 1), int((y - r) // 1)) or is_plateau(int((x + r) // 1), int((y - r) // 1)):
            return False
        if path_dist(x, y, track.PATH) < 2.2 + r or path_dist(x, y, SIDING) < 0.8 + r or path_dist(x, y, MAINLINE) < 0.8 + r:
            return False
        if on_road(x, y, r + 0.1) or in_rect(x, y, r):
            return False
        sx, sy = iso.to_logical(x, y)
        if sx < 10 or sx > 950 or sy < 70 or sy > 650 or under_picker(sx, sy):
            return False
        return all(((x - q[0]) ** 2 + (y - q[1]) ** 2) ** 0.5 > q[2] + r + 0.15 for q in placed)

    for kind, count, radius in (("trees", 18, 0.4), ("bushes", 16, 0.3), ("rocks", 10, 0.25)):
        n = tries = 0
        while n < count and tries < 2000:
            tries += 1
            x, y = -1 + rng.random() * 22, 1.3 + rng.random() * 15
            if not free(x, y, radius):
                continue
            placed.append((x, y, radius))
            if kind == "rocks":
                decor[kind].append((x, y, 0.25 + rng.random() * 0.2, 0.15 + rng.random() * 0.2))
            else:
                decor[kind].append((x, y))
            n += 1
    return decor


DECOR = _scatter()


# ---------- kde se smí stavět věže ----------
def _buildable():
    used = set()
    things = (DECOR["trees"] + DECOR["bushes"] + [r[:2] for r in DECOR["rocks"]] + HAYSTACKS + SIGNALS
              + [p[:2] for p in POLES] + [c[:2] for c in CROSSING_POSTS])
    for x, y in things:
        used.add((int(x // 1), int(y // 1)))

    tiles = set()
    for row in range(1, 17):
        for col in range(-1, 21):
            cx, cy = col + 0.5, row + 0.5
            if is_plateau(col, row) or (col, row) in used:
                continue
            if path_dist(cx, cy, track.PATH) < 0.9 or path_dist(cx, cy, SIDING) < 0.9 or path_dist(cx, cy, MAINLINE) < 0.9:
                continue
            if on_road(cx, cy, 0.3) or in_rect(cx, cy, 0.2):
                continue
            sx, sy = iso.to_logical(cx, cy)
            if sx < 24 or sx > 936 or sy < 90 or sy > 622 or under_picker(sx, sy):
                continue
            tiles.add((col, row))
    return tiles


BUILDABLE = _buildable()
