"""Testy věží: stavění (peníze, volné políčko, tráva), střelba a zpomalení.

Běží bez okna: věže testujeme přes try_build a update, ne přes myš a kreslení.
"""

from types import SimpleNamespace

import pytest

import settings
import track
import world
from enemies import Enemy
from game import Game
from towers import FLASH_TIME, Tower, TowerManager

# Rovná trať po řádku y = 0.5 (střed řádku 0), dlouhá 10 políček.
STRAIGHT = [(0, 0.5), (10, 0.5)]


def playing_game():
    """Nová hra ve stavu "playing" se správcem věží a počátečními penězi."""
    game = Game(TowerManager(), state="menu")
    game.start()
    return game


def free_grass():
    """Nějaké políčko, kam se smí stavět (vezmeme první ze seznamu BUILDABLE)."""
    return sorted(world.BUILDABLE)[0]


def enemy_at(x, kind="cow"):
    """Nepřítel na rovné trati, posunutý na pozici x (políčka)."""
    enemy = Enemy(kind, STRAIGHT)
    enemy.progress = x
    enemy.x, enemy.y = x, 0.5
    return enemy


def run_towers(manager, enemies, seconds, step=1 / 60):
    """Nechá věže běžet `seconds` sekund (bez pohybu nepřátel)."""
    fake_game = SimpleNamespace(enemies=enemies)
    for _ in range(int(seconds / step)):
        manager.update(step, fake_game)


# ---------- stavění ----------

def test_build_on_grass_costs_money():
    game = playing_game()
    manager = game.tower_manager
    col, row = free_grass()
    game.selected_tower = "worker"

    assert manager.try_build(col, row, game) is True
    assert game.money == settings.START_MONEY - settings.TOWER_TYPES["worker"]["price"]
    assert len(manager.towers) == 1
    tower = manager.towers[0]
    assert (tower.kind, tower.col, tower.row) == ("worker", col, row)


def test_cannot_build_on_track():
    game = playing_game()
    # políčko (1, 3) leží na trati (úsek y = 3.5 od x = -2.5 do 3.5)
    assert not track.can_build(1, 3)
    assert game.tower_manager.try_build(1, 3, game) is False
    assert game.money == settings.START_MONEY
    assert game.tower_manager.towers == []


def test_cannot_build_twice_on_same_tile():
    game = playing_game()
    col, row = free_grass()
    assert game.tower_manager.try_build(col, row, game) is True
    money_after_first = game.money
    assert game.tower_manager.try_build(col, row, game) is False
    assert game.money == money_after_first
    assert len(game.tower_manager.towers) == 1


def test_cannot_build_without_money():
    game = playing_game()
    game.selected_tower = "draisine"
    game.money = settings.TOWER_TYPES["draisine"]["price"] - 1
    col, row = free_grass()
    assert game.tower_manager.try_build(col, row, game) is False
    assert game.money == settings.TOWER_TYPES["draisine"]["price"] - 1


def test_new_game_removes_towers():
    game = playing_game()
    col, row = free_grass()
    game.tower_manager.try_build(col, row, game)
    game.start()  # nová hra zavolá reset() správce věží
    assert game.tower_manager.towers == []
    assert game.money == settings.START_MONEY


# ---------- střelba ----------

def test_worker_hits_enemy_closest_to_station():
    manager = TowerManager()
    manager.towers.append(Tower("worker", 2, 0))  # střed (2.5, 0.5)
    behind = enemy_at(1.5)
    ahead = enemy_at(3.5)  # dál po trati = blíž Praze, na toho má mířit

    run_towers(manager, [behind, ahead], 0.5)

    damage = settings.TOWER_TYPES["worker"]["damage"]
    assert ahead.hp == ahead.max_hp - damage
    assert behind.hp == behind.max_hp


def test_worker_waits_for_cooldown():
    manager = TowerManager()
    manager.towers.append(Tower("worker", 2, 0))
    enemy = enemy_at(3.0, kind="tree")  # strom vydrží hodně, nezmizí

    # za 0,9 s (méně než rate = 1 s) stihne vystřelit jen jednou
    run_towers(manager, [enemy], 0.9)
    damage = settings.TOWER_TYPES["worker"]["damage"]
    assert enemy.hp == enemy.max_hp - damage

    # po další sekundě už podruhé
    run_towers(manager, [enemy], 1.0)
    assert enemy.hp == enemy.max_hp - 2 * damage


def test_tower_ignores_enemy_out_of_range():
    manager = TowerManager()
    manager.towers.append(Tower("worker", 2, 0))
    far = enemy_at(9.0)  # 6,5 políčka daleko, dosah je 2,3
    run_towers(manager, [far], 2.0)
    assert far.hp == far.max_hp
    assert manager.shots == []


def test_dispatcher_slows_everyone_in_range_without_damage():
    manager = TowerManager()
    manager.towers.append(Tower("dispatcher", 2, 0))
    first, second = enemy_at(2.0), enemy_at(3.5)
    far = enemy_at(8.0)

    run_towers(manager, [first, second, far], 0.1)

    stats = settings.TOWER_TYPES["dispatcher"]
    for enemy in (first, second):
        assert enemy.slow_factor == stats["slow"]
        assert enemy.slow_timer == pytest.approx(stats["slow_time"])
        assert enemy.hp == enemy.max_hp
    assert far.slow_factor == 1.0
    assert len(manager.pulses) == 1


def test_shot_disappears_when_target_is_gone():
    manager = TowerManager()
    manager.towers.append(Tower("draisine", 2, 0))
    enemy = enemy_at(5.0)  # 2,5 políčka daleko: střela chvíli letí
    run_towers(manager, [enemy], 1 / 60)
    assert len(manager.shots) == 1

    enemy.alive = False  # zničila ho mezitím jiná věž
    run_towers(manager, [enemy], 1 / 60)
    assert manager.shots == []


def test_tower_animates_after_shot():
    manager = TowerManager()
    tower = Tower("worker", 2, 0)
    manager.towers.append(tower)
    run_towers(manager, [enemy_at(3.0, kind="tree")], 1 / 60)
    assert tower.flash == pytest.approx(FLASH_TIME)
