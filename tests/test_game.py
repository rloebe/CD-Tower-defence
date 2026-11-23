"""Testy pravidel hry: peníze, zpoždění, výhra a prohra (bez věží a bez okna)."""

import settings
from game import Game
from waves import WaveManager


def run(game, seconds, step=1 / 60):
    for _ in range(int(seconds / step)):
        game.update(step)


def make_game(waves):
    game = Game()
    game.start()
    game.waves = WaveManager(waves)
    return game


def test_new_game_starts_with_budget_and_no_delay():
    game = Game()
    assert game.state == "menu"
    game.start()
    assert game.state == "playing"
    assert game.money == settings.START_MONEY
    assert game.delay == 0


def test_enemy_reaching_station_adds_delay():
    game = make_game([[("cow", 1, 1.0)]])
    game.start_next_wave()
    run(game, 60)
    assert game.delay == 5  # kráva = 5 minut
    assert game.enemies == []


def test_killing_enemy_gives_money():
    game = make_game([[("cow", 1, 1.0)], [("cow", 1, 1.0)]])
    game.start_next_wave()
    game.update(0.1)
    game.enemies[0].take_damage(999)
    game.update(0.1)
    assert game.money == settings.START_MONEY + 10
    assert game.kills == 1
    assert game.delay == 0


def test_too_much_delay_loses_the_game():
    game = make_game([[("closure", 2, 0.5)]])  # 2 × 30 min = 60 min
    game.start_next_wave()
    run(game, 200)
    assert game.state == "lost"


def test_clearing_all_waves_wins_the_game():
    game = make_game([[("cow", 2, 0.5)], [("signal", 2, 0.5)]])
    for _ in range(2):
        assert game.start_next_wave()
        for _ in range(120):  # "věž", která všechno hned odstraní
            game.update(1 / 60)
            for enemy in game.enemies:
                enemy.take_damage(999)
    game.update(1 / 60)
    assert game.state == "won"
    assert game.kills == 4


def test_cannot_start_next_wave_while_enemies_on_track():
    game = make_game([[("cow", 1, 1.0)], [("cow", 1, 1.0)]])
    assert game.start_next_wave()
    game.update(0.1)
    assert game.start_next_wave() is False
