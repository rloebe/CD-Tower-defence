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


def test_game_starts_with_loading_then_menu():
    game = Game()
    assert game.state == "loading"
    run(game, settings.LOAD_TIME + 0.1)
    assert game.load_progress == 1.0
    assert game.state == "menu"


def test_loading_can_be_skipped():
    game = Game()
    game.skip_loading()
    assert game.state == "menu"


def test_new_game_starts_with_budget_and_no_delay():
    game = Game(state="menu")
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


def test_kill_and_arrival_make_popups_that_disappear():
    game = make_game([[("cow", 2, 0.1)]])
    game.start_next_wave()
    run(game, 0.2)
    game.enemies[0].take_damage(999)
    game.update(1 / 60)
    coin = game.popups[-1]
    assert coin["coin"] and coin["text"] == "+10" and coin["x"] is not None
    while game.delay == 0:  # počkáme, až druhá kráva dojede do Prahy
        game.update(1 / 60)
    assert any(p["text"] == "+5 min" and not p["coin"] for p in game.popups)
    run(game, settings.POPUP_LIFE + 0.1)
    assert game.popups == []


def test_pause_stops_the_game():
    game = make_game([[("cow", 1, 1.0)]])
    game.start_next_wave()
    run(game, 1)
    game.toggle_pause()
    progress = game.enemies[0].progress
    run(game, 2)
    assert game.enemies[0].progress == progress


def test_double_speed_moves_twice_as_far():
    normal = make_game([[("cow", 1, 1.0)]])
    fast = make_game([[("cow", 1, 1.0)]])
    fast.toggle_speed()
    for game in (normal, fast):
        game.start_next_wave()
        run(game, 2)
    assert abs(fast.enemies[0].progress - 2 * normal.enemies[0].progress) < 0.05


def test_back_to_menu_resets_the_game():
    game = make_game([[("cow", 1, 1.0)]])
    game.start_next_wave()
    run(game, 1)
    game.go_to_menu()
    assert game.state == "menu" and game.enemies == [] and game.money == settings.START_MONEY


def test_cannot_start_next_wave_while_enemies_on_track():
    game = make_game([[("cow", 1, 1.0)], [("cow", 1, 1.0)]])
    assert game.start_next_wave()
    game.update(0.1)
    assert game.start_next_wave() is False
