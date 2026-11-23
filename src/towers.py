"""Věže (pracovníci a technika ČD).

ZATÍM JEN PRÁZDNÁ KOSTRA, kterou doplní Matěj: typy věží, stavění myší,
střelba, utrácení peněz. main.py a game.py volají jen metody níže,
takže stačí zachovat jejich názvy a parametry.
"""


class TowerManager:
    def __init__(self):
        self.towers = []

    def reset(self):
        """Volá se při nové hře. Smaže všechny věže."""
        self.towers = []

    def handle_event(self, event, game):
        """Myš/klávesy během hry (např. stavění věže kliknutím)."""

    def update(self, dt, game):
        """Věže míří a střílejí na nepřátele v `game.enemies`."""

    def draw(self, surface, game):
        """Nakreslí věže a střely."""
