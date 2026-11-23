"""Testy trati: délka, body na trati, kontrola stavění vedle trati."""

import track

# jednoduchá trať ve tvaru L: 100 px doprava, pak 50 px dolů
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


def test_real_map_starts_off_screen_and_ends_in_station():
    start = track.PATH[0]
    end = track.PATH[-1]
    assert start[0] < 0
    assert track.STATION_RECT.collidepoint(end)
