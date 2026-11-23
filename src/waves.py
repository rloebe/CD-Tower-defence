"""Vlny nepřátel: kdo přijede, kolik jich je a jak rychle po sobě."""

# Každá vlna je seznam skupin (typ nepřítele, počet, rozestup v sekundách).
# Skupiny ve vlně přijíždějí jedna po druhé.
WAVES = [
    [("cow", 6, 1.2)],
    [("cow", 8, 1.0)],
    [("signal", 6, 0.7), ("cow", 5, 1.0)],
    [("tree", 3, 2.0), ("signal", 8, 0.6)],
    [("cow", 10, 0.7), ("tree", 4, 1.6)],
    [("signal", 15, 0.4), ("tree", 5, 1.4)],
    [("cow", 12, 0.5), ("signal", 8, 0.4), ("tree", 6, 1.2)],
    [("closure", 1, 3.0), ("signal", 10, 0.5), ("tree", 6, 1.2)],
]


class WaveManager:
    def __init__(self, waves=WAVES):
        self.waves = waves
        self.current = 0  # kolik vln už začalo (0 = ještě žádná)
        self.queue = []  # nepřátelé, kteří v této vlně ještě nevyjeli: (typ, rozestup)
        self.timer = 0.0  # za kolik sekund vyjede další

    @property
    def total(self):
        return len(self.waves)

    @property
    def spawning(self):
        """True, dokud z aktuální vlny ještě někdo nevyjel."""
        return len(self.queue) > 0

    @property
    def all_started(self):
        return self.current >= self.total

    def start_next_wave(self):
        """Spustí další vlnu. Vrátí False, když to teď nejde."""
        if self.spawning or self.all_started:
            return False
        for kind, count, interval in self.waves[self.current]:
            for _ in range(count):
                self.queue.append((kind, interval))
        self.current += 1
        self.timer = 0.0  # první nepřítel vyjede hned
        return True

    def update(self, dt):
        """Odpočítá čas a vrátí seznam typů nepřátel, kteří mají právě teď vyjet."""
        to_spawn = []
        self.timer -= dt
        while self.queue and self.timer <= 0:
            kind, interval = self.queue.pop(0)
            to_spawn.append(kind)
            self.timer += interval
        return to_spawn
