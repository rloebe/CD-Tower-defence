"""Stav hry a pravidla: peníze, zpoždění, nepřátelé, vlny, výhra a prohra.

Tady se nic nekreslí, takže se to dá testovat bez otevřeného okna.
"""

import settings
import track
from enemies import Enemy
from waves import WaveManager


class Game:
    def __init__(self, tower_manager=None):
        # tower_manager = objekt z towers.py (Matěj). V testech může být None.
        self.tower_manager = tower_manager
        self.path = track.PATH
        self.state = "menu"  # "menu" | "playing" | "won" | "lost"
        self.reset()

    def reset(self):
        """Vrátí všechno na začátek (nová hra)."""
        self.money = settings.START_MONEY
        self.delay = 0  # nasbírané minuty zpoždění
        self.max_delay = settings.MAX_DELAY
        self.enemies = []
        self.waves = WaveManager()
        self.kills = 0
        if self.tower_manager is not None:
            self.tower_manager.reset()

    def start(self):
        """Začne novou hru (z menu nebo po konci hry)."""
        self.reset()
        self.state = "playing"

    @property
    def wave_in_progress(self):
        """True, dokud nepřátelé vyjíždějí nebo jsou ještě na trati."""
        return self.waves.spawning or len(self.enemies) > 0

    def start_next_wave(self):
        """Spustí další vlnu, ale jen když právě žádná neběží."""
        if self.state != "playing" or self.wave_in_progress:
            return False
        return self.waves.start_next_wave()

    def update(self, dt):
        """Jeden krok hry. `dt` = čas od minulého snímku v sekundách."""
        if self.state != "playing":
            return

        # 1) vypustit nové nepřátele
        for kind in self.waves.update(dt):
            self.enemies.append(Enemy(kind, self.path))

        # 2) posunout nepřátele
        for enemy in self.enemies:
            enemy.update(dt)

        # 3) věže střílejí
        if self.tower_manager is not None:
            self.tower_manager.update(dt, self)

        # 4) vyhodnotit odstraněné a ty, co dojeli do stanice
        remaining = []
        for enemy in self.enemies:
            if not enemy.alive:
                self.money += enemy.reward
                self.kills += 1
            elif enemy.reached_end:
                self.delay += enemy.delay
            else:
                remaining.append(enemy)
        self.enemies = remaining

        # 5) konec hry?
        if self.delay >= self.max_delay:
            self.state = "lost"
        elif self.waves.all_started and not self.wave_in_progress:
            self.state = "won"
