"""Nepřátelé = problémy na trati, které jedou ke stanici a způsobují zpoždění.

Pozice a rychlost jsou v políčkách (viz docs/vizualni-design.md).
"""

import pygame

import iso
import settings
import sprites
import track

# Vlastnosti jednotlivých typů nepřátel.
#   speed  = políček za sekundu
#   hp     = kolik poškození vydrží
#   delay  = kolik minut zpoždění přidá, když dojede do stanice
#   reward = kolik Kč dostane hráč, když ho odstraní
#   radius = poloměr v políčkách (pro zásahy)
#   size   = velikost postavičky na obrazovce v pixelech
ENEMY_TYPES = {
    "cow": {"name": "Kráva na trati", "speed": 1.4, "hp": 30, "delay": 5, "reward": 10, "radius": 0.3, "size": 44},
    "signal": {"name": "Porucha návěstidla", "speed": 2.4, "hp": 15, "delay": 3, "reward": 8, "radius": 0.25, "size": 40},
    "tree": {"name": "Spadlý strom", "speed": 0.9, "hp": 80, "delay": 8, "reward": 20, "radius": 0.35, "size": 48},
    "closure": {"name": "Výluka", "speed": 0.6, "hp": 600, "delay": 30, "reward": 100, "radius": 0.5, "size": 62},
}


class Enemy:
    def __init__(self, kind, path=track.PATH):
        stats = ENEMY_TYPES[kind]
        self.kind = kind
        self.name = stats["name"]
        self.speed = stats["speed"]
        self.max_hp = stats["hp"]
        self.hp = stats["hp"]
        self.delay = stats["delay"]
        self.reward = stats["reward"]
        self.radius = stats["radius"]
        self.size = stats["size"]

        self.path = path
        self.path_length = track.path_length(path)
        self.progress = 0.0  # ujetá vzdálenost po trati (věže míří na toho nejdál)
        self.x, self.y = path[0]

        self.alive = True  # False = odstraněn věží
        self.reached_end = False  # True = dojel do stanice

        # zpomalení (např. od výpravčího): násobek rychlosti a jak dlouho ještě platí
        self.slow_factor = 1.0
        self.slow_timer = 0.0

        # animace: fáze kroku a jestli jde doleva (pak se postavička zrcadlí)
        self.phase = 0.0
        self.facing_left = False

    @property
    def pos(self):
        return (self.x, self.y)

    def apply_slow(self, factor, duration):
        """Zpomalí nepřítele na `factor` (0.5 = poloviční rychlost) na `duration` sekund."""
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def update(self, dt):
        """Posune nepřítele po trati. `dt` = čas od minulého snímku v sekundách."""
        if not self.alive or self.reached_end:
            return

        factor = 1.0
        if self.slow_timer > 0:
            factor = self.slow_factor
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        self.progress += self.speed * factor * dt
        self.phase += dt * factor  # zpomalený nepřítel i pomaleji šlape
        if self.progress >= self.path_length:
            self.progress = self.path_length
            self.reached_end = True

        old_x, old_y = self.x, self.y
        self.x, self.y = track.point_at_distance(self.path, self.progress)
        # kam se posunul na obrazovce: když doleva, otočíme ho
        screen_dx = iso.to_screen(self.x, self.y)[0] - iso.to_screen(old_x, old_y)[0]
        if abs(screen_dx) > 1e-6:
            self.facing_left = screen_dx < 0

    def take_damage(self, amount):
        """Ubere životy. Vrátí True, pokud tím nepřítel zmizel."""
        if not self.alive:
            return False
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    # ---------- Kreslení ----------

    def draw(self, surface):
        sx, sy = iso.to_screen(self.x, self.y)
        if self.slow_timer > 0:
            ring = pygame.Rect(0, 0, self.size * 0.9, self.size * 0.45)
            ring.center = (sx, sy)
            pygame.draw.ellipse(surface, (127, 184, 255), ring, 3)

        # postavička stojí "nohama" na trati
        center = (sx, sy - self.size * 14 / 60)
        sprites.draw_sprite(surface, self.kind, center, self.size, phase=self.phase, flip=self.facing_left)

        if self.hp < self.max_hp:
            width = int(self.size * 0.7)
            left = int(sx - width / 2)
            top = int(center[1] - self.size / 2 - 4)
            pygame.draw.rect(surface, settings.RED, (left, top, width, 5))
            pygame.draw.rect(surface, settings.GREEN, (left, top, int(width * self.hp / self.max_hp), 5))
