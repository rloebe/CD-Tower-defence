"""Testy trati: délka, body na trati, směr jízdy, poloha vůči trati."""

import iso
import track
import world

# jednoduchá trať ve tvaru L: 100 políček doprava, pak 50 dolů
L_PATH = [(0, 0), (100, 0), (100, 50)]


def test_path_length():
    assert track.path_length(L_PATH) == 150


def test_point_at_start_middle_and_end():
    assert track.point_at_distance(L_PATH, 0) == (0, 0)
    assert track.point_at_distance(L_PATH, 50) == (50, 0)
    assert track.point_at_distance(L_PATH, 125) == (100, 25)
    assert track.point_at_distance(L_PATH, 150) == (100, 50)


def test_point_outside_path_is_clamped():
    assert track.point_at_distance(L_PATH, -10) == (0, 0)
    assert track.point_at_distance(L_PATH, 999) == (100, 50)


def test_is_on_path():
    assert track.is_on_path((50, 5), L_PATH, margin=10)  # těsně vedle prvního úseku
    assert track.is_on_path((105, 30), L_PATH, margin=10)  # vedle druhého úseku
    assert not track.is_on_path((50, 40), L_PATH, margin=10)  # daleko od trati


def test_direction_along_the_path():
    assert track.direction_at_distance(L_PATH, 10) == (1, 0)  # první úsek jede doprava
    assert track.direction_at_distance(L_PATH, 120) == (0, 1)  # druhý úsek dolů
    assert track.direction_at_distance(L_PATH, 999) == (0, 1)  # za koncem = směr posledního úseku


def test_real_track_starts_off_screen_and_ends_at_praha():
    start_x, _ = iso.to_screen(*track.PATH[0])
    assert start_x < 0  # nepřátelé přijíždějí zleva zpoza okraje obrazovky
    end_x, end_y = track.PATH[-1]
    px, py, pw, pd = world.PRAHA
    assert px <= end_x <= px + pw + 0.5  # konec trati je u nádraží Praha
    assert py + pd < end_y  # zarážedlo je před budovou, ne v ní


def test_real_track_length():
    assert round(track.path_length(track.PATH), 1) == 40.7
