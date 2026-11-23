"""Testy nepřátel: pohyb, poškození, zpomalení."""

from enemies import ENEMY_TYPES, Enemy

STRAIGHT = [(0, 0), (100, 0)]  # rovná trať dlouhá 100 px


def test_enemy_moves_by_speed():
    enemy = Enemy("cow", STRAIGHT)
    enemy.update(0.5)
    assert enemy.progress == ENEMY_TYPES["cow"]["speed"] * 0.5
    assert enemy.pos == (enemy.progress, 0)


def test_enemy_reaches_end():
    enemy = Enemy("signal", STRAIGHT)
    for _ in range(100):
        enemy.update(0.1)
    assert enemy.reached_end
    assert enemy.pos == (100, 0)


def test_take_damage_and_die():
    enemy = Enemy("cow", STRAIGHT)
    assert enemy.take_damage(10) is False
    assert enemy.hp == 20
    assert enemy.take_damage(25) is True
    assert not enemy.alive
    assert enemy.hp == 0


def test_dead_enemy_cannot_be_killed_twice():
    enemy = Enemy("signal", STRAIGHT)
    enemy.take_damage(999)
    assert enemy.take_damage(10) is False


def test_slow_halves_speed_and_wears_off():
    enemy = Enemy("cow", STRAIGHT)
    enemy.apply_slow(0.5, 1.0)
    enemy.update(0.5)
    assert enemy.progress == ENEMY_TYPES["cow"]["speed"] * 0.5 * 0.5
    enemy.update(1.0)  # zpomalení vyprší
    assert enemy.slow_factor == 1.0
