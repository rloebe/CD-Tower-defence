"""Izometrická projekce: převod mezi světem (políčka) a obrazovkou (pixely).

Svět: x doprava, y k divákovi, z nahoru. Jedno políčko = 1.0.
Kamera se dívá shora pod úhlem 55° a je pootočená o -12° (jako v Unrailed).
Logika hry počítá jen v políčkách, na pixely se převádí až při kreslení.
"""

import math

import settings as s


def to_screen(x, y, z=0.0):
    """Bod ve světě -> bod na obrazovce (pixely)."""
    # 1) pootočení kolem svislé osy
    rx = x * s.COS_YAW - y * s.SIN_YAW
    ry = x * s.SIN_YAW + y * s.COS_YAW
    # 2) sklon kamery: hloubka se zkrátí, výška posune nahoru
    sx = s.ORIGIN_X + s.TILE * rx
    sy = s.ORIGIN_Y + s.TILE * (ry * s.SIN_PITCH - z * s.COS_PITCH)
    return (sx, sy)


def to_world(sx, sy):
    """Bod na obrazovce -> bod na zemi ve světě (z = 0). Opak to_screen."""
    rx = (sx - s.ORIGIN_X) / s.TILE
    ry = (sy - s.ORIGIN_Y) / s.TILE / s.SIN_PITCH
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
