"""Stav hry a pravidla: obrazovky, peníze, zpoždění, nepřátelé, vlny, výhra a prohra.

Tady se nic nekreslí, takže se to dá testovat bez otevřeného okna.
"""

import settings
import track
from enemies import Enemy
from waves import WaveManager


class Game:
    def __init__(self, tower_manager=None, state="loading"):
        # tower_manager = objekt z towers.py. V testech může být None.
        self.tower_manager = tower_manager
        self.path = track.PATH
        self.state = state  # "loading" | "menu" | "playing" | "won" | "lost"
        self.load_progress = 0.0  # 0–1 během načítání
        self.reset()

    def reset(self):
        """Vrátí všechno na začátek (nová hra)."""
        self.money = settings.START_MONEY
        self.delay = 0  # nasbírané minuty zpoždění
        self.max_delay = settings.MAX_DELAY
        self.enemies = []
        self.waves = WaveManager()
        self.kills = 0
        self.paused = False
        self.speed = 1  # 1 = normálně, 2 = zrychleně
        self.time = 0.0  # herní čas v sekundách (pro animace)
        self.popups = []  # vyskakující "+10" (s mincí) a "+5 min"
        if self.tower_manager is not None:
            self.tower_manager.reset()

    # ---------- přepínání obrazovek ----------

    def start(self):
        """Začne novou hru (z menu nebo po konci hry)."""
        self.reset()
        self.state = "playing"

    def go_to_menu(self):
        self.reset()
        self.state = "menu"

    def skip_loading(self):
        if self.state == "loading":
            self.load_progress = 1.0
            self.state = "menu"

    def toggle_pause(self):
        if self.state == "playing":
            self.paused = not self.paused

    def toggle_speed(self):
        self.speed = 1 if self.speed == 2 else 2

    # ---------- vlny ----------

    @property
    def wave_in_progress(self):
        """True, dokud nepřátelé vyjíždějí nebo jsou ještě na trati."""
        return self.waves.spawning or len(self.enemies) > 0

    def start_next_wave(self):
        """Spustí další vlnu, ale jen když právě žádná neběží."""
        if self.state != "playing" or self.wave_in_progress:
            return False
        self.paused = False
        return self.waves.start_next_wave()

    # ---------- jeden krok hry ----------

    def update(self, dt):
        """Jeden krok hry. `dt` = skutečný čas od minulého snímku v sekundách."""
        if self.state == "loading":
            self.load_progress = min(1.0, self.load_progress + dt / settings.LOAD_TIME)
            if self.load_progress >= 1.0:
                self.state = "menu"
            return

        self._update_popups(dt)
        if self.state != "playing" or self.paused:
            return

        dt *= self.speed
        self.time += dt

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
                self.popups.append({"text": f"+{enemy.reward}", "x": enemy.x, "y": enemy.y, "coin": True, "t": 0.0})
            elif enemy.reached_end:
                self.delay += enemy.delay
                self.popups.append({"text": f"+{enemy.delay} min", "x": None, "y": None, "coin": False, "t": 0.0})
            else:
                remaining.append(enemy)
        self.enemies = remaining

        # 5) konec hry?
        if self.delay >= self.max_delay:
            self.state = "lost"
        elif self.waves.all_started and not self.wave_in_progress:
            self.state = "won"

    def _update_popups(self, dt):
        for popup in self.popups:
            popup["t"] += dt
        self.popups = [p for p in self.popups if p["t"] < settings.POPUP_LIFE]
