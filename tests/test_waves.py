"""Testy vln: kolik nepřátel vyjede a kdy."""

from waves import WAVES, WaveManager

TEST_WAVES = [
    [("cow", 3, 1.0)],
    [("signal", 2, 0.5), ("tree", 1, 1.0)],
]


def spawn_everything(manager, seconds, step=0.1):
    spawned = []
    for _ in range(int(seconds / step)):
        spawned += manager.update(step)
    return spawned


def test_first_enemy_spawns_immediately():
    manager = WaveManager(TEST_WAVES)
    manager.start_next_wave()
    assert manager.update(0.01) == ["cow"]


def test_wave_spawns_all_enemies_in_order():
    manager = WaveManager(TEST_WAVES)
    manager.start_next_wave()
    assert spawn_everything(manager, 5) == ["cow", "cow", "cow"]
    assert not manager.spawning

    manager.start_next_wave()
    assert spawn_everything(manager, 5) == ["signal", "signal", "tree"]


def test_cannot_start_wave_while_spawning():
    manager = WaveManager(TEST_WAVES)
    assert manager.start_next_wave() is True
    assert manager.start_next_wave() is False
    assert manager.current == 1


def test_cannot_start_more_waves_than_exist():
    manager = WaveManager(TEST_WAVES)
    for _ in TEST_WAVES:
        manager.start_next_wave()
        spawn_everything(manager, 5)
    assert manager.all_started
    assert manager.start_next_wave() is False


def test_real_waves_have_eight_waves_and_a_boss_at_the_end():
    assert len(WAVES) == 8
    last_wave_kinds = [kind for kind, _, _ in WAVES[-1]]
    assert "closure" in last_wave_kinds
