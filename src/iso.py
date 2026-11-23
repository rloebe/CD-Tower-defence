"""Izometrická projekce: převod mezi světem (políčka) a obrazovkou (pixely).

Svět: x doprava, y k divákovi, z nahoru. Jedno políčko = 1.0.
Kamera se dívá shora pod úhlem 55° a je pootočená o -12° (jako v Unrailed).
Logika hry počítá jen v políčkách, na pixely se převádí až při kreslení.

Výsledek se navíc zvětší o settings.SCALE a posune o settings.OFFSET_X/Y,
aby hra vyplnila celou obrazovku (na každém monitoru jinak).
"""

import math
from contextlib import contextmanager

import settings as s


def to_logical(x, y, z=0.0):
    """Bod ve světě (políčka) -> bod na logické ploše 960 × 640 (bez zvětšení)."""
    # 1) pootočení kolem svislé osy
    rx = x * s.COS_YAW - y * s.SIN_YAW
    ry = x * s.SIN_YAW + y * s.COS_YAW
    # 2) sklon kamery: hloubka se zkrátí, výška posune nahoru
    lx = s.ORIGIN_X + s.TILE * rx
    ly = s.ORIGIN_Y + s.TILE * (ry * s.SIN_PITCH - z * s.COS_PITCH)
    return (lx, ly)


def to_screen(x, y, z=0.0):
    """Bod ve světě (políčka) -> bod na obrazovce (skutečné pixely)."""
    lx, ly = to_logical(x, y, z)
    # zvětšení a vycentrování na skutečnou obrazovku
    return (s.OFFSET_X + lx * s.SCALE, s.OFFSET_Y + ly * s.SCALE)


def to_world(sx, sy):
    """Bod na obrazovce -> bod na zemi ve světě (z = 0). Opak to_screen."""
    lx = (sx - s.OFFSET_X) / s.SCALE
    ly = (sy - s.OFFSET_Y) / s.SCALE
    rx = (lx - s.ORIGIN_X) / s.TILE
    ry = (ly - s.ORIGIN_Y) / s.TILE / s.SIN_PITCH
    # zpětné pootočení
    x = rx * s.COS_YAW + ry * s.SIN_YAW
    y = -rx * s.SIN_YAW + ry * s.COS_YAW
    return (x, y)


def to_tile(sx, sy):
    """Bod na obrazovce -> políčko (sloupec, řádek), na které ukazuje myš."""
    x, y = to_world(sx, sy)
    return (math.floor(x), math.floor(y))


def depth(x, y):
    """Jak daleko je bod od kamery. Menší = dál = kreslit dřív."""
    return x * s.SIN_YAW + y * s.COS_YAW


def px(logical):
    """Rozměr v logických pixelech (návrh 960 × 640) -> skutečné pixely."""
    return logical * s.SCALE


@contextmanager
def supersample(factor):
    """Na chvíli vše zvětší `factor`-krát (např. 2×).

    Používá se při předkreslování mapy: nakreslíme ji 2× větší a pak plynule
    zmenšíme. Zmenšení zprůměruje okraje, takže hrany nejsou "zubaté" (antialiasing).
    """
    saved = (s.SCALE, s.OFFSET_X, s.OFFSET_Y)
    s.SCALE, s.OFFSET_X, s.OFFSET_Y = saved[0] * factor, saved[1] * factor, saved[2] * factor
    try:
        yield
    finally:
        s.SCALE, s.OFFSET_X, s.OFFSET_Y = saved
