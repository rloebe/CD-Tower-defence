"""Nepřátelé = problémy na trati, které jedou ke stanici a způsobují zpoždění."""

import pygame

import settings
import track

# Vlastnosti jednotlivých typů nepřátel.
#   speed  = pixely za sekundu
#   hp     = kolik poškození vydrží
#   delay  = kolik minut zpoždění přidá, když dojede do stanice
#   reward = kolik Kč dostane hráč, když ho odstraní
ENEMY_TYPES = {
    "cow": {"name": "Kráva na trati", "speed": 70, "hp": 30, "delay": 5, "reward": 10, "radius": 14},
    "signal": {"name": "Porucha návěstidla", "speed": 120, "hp": 15, "delay": 3, "reward": 8, "radius": 12},
    "tree": {"name": "Spadlý strom", "speed": 45, "hp": 80, "delay": 8, "reward": 20, "radius": 16},
    "closure": {"name": "Výluka", "speed": 30, "hp": 600, "delay": 30, "reward": 100, "radius": 24},
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

        self.path = path
        self.path_length = track.path_length(path)
        self.progress = 0.0  # ujetá vzdálenost po trati (věže míří na toho nejdál)
        self.pos = path[0]

        self.alive = True  # False = odstraněn věží
        self.reached_end = False  # True = dojel do stanice

        # zpomalení (např. od výpravčího): násobek rychlosti a jak dlouho ještě platí
        self.slow_factor = 1.0
        self.slow_timer = 0.0

    def apply_slow(self, factor, duration):
        """Zpomalí nepřítele na `factor` (0.5 = poloviční rychlost) na `duration` sekund."""
        self.slow_factor = min(self.slow_factor, factor)
        self.slow_timer = max(self.slow_timer, duration)

    def update(self, dt):
        """Posune nepřítele po trati. `dt` = čas od minulého snímku v sekundách."""
        if not self.alive or self.reached_end:
            return

        speed = self.speed
        if self.slow_timer > 0:
            speed *= self.slow_factor
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_factor = 1.0

        self.progress += speed * dt
        if self.progress >= self.path_length:
            self.progress = self.path_length
            self.reached_end = True
        self.pos = track.point_at_distance(self.path, self.progress)

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
        x, y = int(self.pos[0]), int(self.pos[1])
        if self.kind == "cow":
            _draw_cow(surface, x, y)
        elif self.kind == "signal":
            _draw_signal(surface, x, y)
        elif self.kind == "tree":
            _draw_tree(surface, x, y)
        else:
            _draw_closure(surface, x, y)

        if self.slow_timer > 0:
            pygame.draw.circle(surface, (120, 180, 255), (x, y), self.radius + 4, 2)
        self._draw_hp_bar(surface, x, y)

    def _draw_hp_bar(self, surface, x, y):
        if self.hp == self.max_hp:
            return
        width = self.radius * 2
        top = y - self.radius - 10
        pygame.draw.rect(surface, settings.RED, (x - width // 2, top, width, 4))
        filled = int(width * self.hp / self.max_hp)
        pygame.draw.rect(surface, settings.GREEN, (x - width // 2, top, filled, 4))


def _draw_cow(surface, x, y):
    pygame.draw.ellipse(surface, settings.WHITE, (x - 14, y - 9, 28, 18))
    pygame.draw.circle(surface, settings.BLACK, (x - 4, y - 2), 4)
    pygame.draw.circle(surface, settings.BLACK, (x + 6, y + 3), 3)
    pygame.draw.circle(surface, settings.WHITE, (x + 15, y - 5), 6)
    pygame.draw.circle(surface, (235, 160, 170), (x + 18, y - 3), 3)
    pygame.draw.ellipse(surface, settings.BLACK, (x - 14, y - 9, 28, 18), 1)


def _draw_signal(surface, x, y):
    points = [(x, y - 13), (x - 12, y + 9), (x + 12, y + 9)]
    pygame.draw.polygon(surface, settings.YELLOW, points)
    pygame.draw.polygon(surface, settings.BLACK, points, 2)
    pygame.draw.line(surface, settings.BLACK, (x, y - 5), (x, y + 2), 3)
    pygame.draw.circle(surface, settings.BLACK, (x, y + 6), 2)


def _draw_tree(surface, x, y):
    pygame.draw.rect(surface, (110, 70, 35), (x - 16, y - 4, 32, 8), border_radius=3)
    pygame.draw.circle(surface, (40, 120, 50), (x + 12, y - 4), 10)
    pygame.draw.circle(surface, (50, 140, 60), (x + 4, y + 4), 8)


def _draw_closure(surface, x, y):
    rect = pygame.Rect(x - 24, y - 14, 48, 28)
    pygame.draw.rect(surface, settings.WHITE, rect)
    for i in range(3):
        pygame.draw.rect(surface, settings.RED, (rect.x + 4 + i * 16, rect.y, 8, rect.height))
    pygame.draw.rect(surface, settings.BLACK, rect, 2)
