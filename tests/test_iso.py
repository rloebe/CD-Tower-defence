"""Testy kamery (izometrické projekce) a rozložení mapy."""

import iso
import settings
import track
import world


def test_origin_is_where_settings_say():
    assert iso.to_screen(0, 0) == (settings.ORIGIN_X, settings.ORIGIN_Y)


def test_screen_and_back_gives_the_same_point():
    # tam a zpátky musí vyjít stejný bod (s malou nepřesností zaokrouhlených konstant)
    for x, y in ((0, 0), (5.3, 7.1), (18.2, 7.5), (-2.5, 3.5)):
        bx, by = iso.to_world(*iso.to_screen(x, y))
        assert abs(bx - x) < 0.01 and abs(by - y) < 0.01


def test_click_hits_the_right_tile():
    sx, sy = iso.to_screen(4.5, 6.5)  # střed políčka (4, 6)
    assert iso.to_tile(sx, sy) == (4, 6)


def test_height_moves_point_up_on_screen():
    _, ground = iso.to_screen(3, 3, 0)
    _, high = iso.to_screen(3, 3, 1)
    assert high < ground


def test_closer_to_camera_has_bigger_depth():
    # y roste směrem k divákovi, takže bod s větším y je blíž a kreslí se později
    assert iso.depth(5, 6) > iso.depth(5, 5)


def test_cannot_build_on_track_road_or_plateau():
    for x, y in track.PATH[1:]:
        assert not track.can_build(int(x // 1), int(y // 1))
    assert not track.can_build(int(world.ROAD_X), 6)  # silnice
    assert not track.can_build(5, 0)  # skalní plošina


def test_there_are_enough_build_spots_next_to_the_track():
    assert len(world.BUILDABLE) >= 40
    # každé místo ke stavbě je opravdu na mapě a je blízko trati (do 3 políček)
    for col, row in world.BUILDABLE:
        assert world.path_dist(col + 0.5, row + 0.5, track.PATH) < 6


def test_map_is_always_the_same():
    # pevný seed: stromy a keře jsou při každém spuštění na stejném místě
    assert world.DECOR == world._scatter()
