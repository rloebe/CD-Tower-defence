"""Testy okolního života: kdy a kudy jezdí vlak a auta, traktor, krávy a kouř.

Kreslí se jen do malých obrázků v paměti, takže okno není potřeba.
"""

import pytest

import ambient
from ambient import Ambient


def run(life, seconds, step=1 / 60):
    """Nechá okolní život běžet `seconds` sekund."""
    for _ in range(int(round(seconds / step))):
        life.update(step)


def test_first_train_comes_after_four_seconds():
    life = Ambient(seed=1)
    run(life, ambient.FIRST_TRAIN - 0.1)
    assert life.train is None
    run(life, 0.2)
    assert life.train is not None
    # další vlak je naplánovaný za 22–38 s
    pause = life.next_train - life.time
    assert ambient.TRAIN_PAUSE[0] - 0.2 <= pause <= ambient.TRAIN_PAUSE[1]


def test_train_moves_and_disappears():
    life = Ambient(seed=1)
    life.train = {"dir": 1, "x": 3.0}
    life.next_train = 1000  # ať nepřijede další
    run(life, 1.0)
    assert life.train["x"] == pytest.approx(3.0 + ambient.TRAIN_SPEED)
    run(life, 10.0)  # 3 + 4,5 × 11 = 52,5 > 29 -> zmizel
    assert life.train is None


def test_train_has_locomotive_and_three_coaches():
    life = Ambient(seed=1)
    life.train = {"dir": 1, "x": 10.0}
    positions = life.train_car_positions()
    assert len(positions) == 4
    # lokomotiva vpředu: její pravý konec je přesně na čele vlaku
    assert positions[0] + ambient.CAR_LENGTH == pytest.approx(10.0)
    # vozy jdou za sebou s mezerou 0,12
    assert positions[0] - positions[1] == pytest.approx(ambient.CAR_LENGTH + ambient.CAR_GAP)
    # každý vůz se řadí podle hloubky zvlášť: 4 vozy + traktor + 2 krávy
    assert len(life.drawables()) == 4 + 1 + 2


def test_cars_drive_in_their_lane_and_leave():
    life = Ambient(seed=2)
    life.next_car = 1000
    life.cars = [{"lane": 0, "x": 1.0, "color": 0}, {"lane": 1, "x": 23.0, "color": 1}]
    run(life, 1.0)
    assert life.cars[0]["x"] == pytest.approx(1.0 + ambient.CAR_SPEED)  # horní pruh doprava
    assert life.cars[1]["x"] == pytest.approx(23.0 - ambient.CAR_SPEED)  # dolní pruh doleva
    run(life, 12.0)  # obě auta už sjela ze silnice x 0–24
    assert life.cars == []


def test_new_car_is_scheduled_after_one_appears():
    life = Ambient(seed=3)
    run(life, ambient.FIRST_CAR + 0.05)
    assert len(life.cars) == 1
    pause = life.next_car - life.time
    assert ambient.CAR_PAUSE[0] - 0.1 <= pause <= ambient.CAR_PAUSE[1]


def test_tractor_goes_there_and_back():
    x0, right0 = ambient.tractor_position(0.0)
    assert x0 == pytest.approx(ambient.TRACTOR_LEFT) and right0
    # za 11,5 s ujede 4,6 políčka = je na pravém konci a otáčí se
    x1, right1 = ambient.tractor_position(ambient.TRACTOR_SPAN / ambient.TRACTOR_SPEED + 0.1)
    assert x1 == pytest.approx(ambient.TRACTOR_LEFT + ambient.TRACTOR_SPAN, abs=0.05)
    assert not right1
    # nikdy nevyjede z oranice
    for t in range(0, 60):
        x, _ = ambient.tractor_position(t * 0.5)
        assert ambient.TRACTOR_LEFT <= x <= ambient.TRACTOR_LEFT + ambient.TRACTOR_SPAN


def test_cows_stay_near_their_spot():
    for cow in ambient.COWS:
        center_x, y, amplitude = cow[0], cow[1], cow[2]
        for t in range(0, 100):
            x, cow_y, _ = ambient.cow_position(t * 0.3, cow)
            assert abs(x - center_x) <= amplitude + 1e-9
            assert cow_y == y


def test_smoke_puff_rises_grows_and_fades():
    x, y, z, size, opacity = ambient.puff(1.0, 2.0, 1.62, 0.0, 5)
    assert (x, y, z, size, opacity) == (1.0, 2.0, 1.62, 5, 0.6)
    x, y, z, size, opacity = ambient.puff(1.0, 2.0, 1.62, 1.0, 5)
    assert z == pytest.approx(2.62)  # vystoupal o 1 políčko
    assert x == pytest.approx(1.35)  # vítr ho posunul doprava
    assert size == 14  # z 5 na 14 logických pixelů
    assert opacity == 0  # zmizel


def test_there_is_smoke_from_every_house_and_kolin():
    assert len(ambient.chimneys()) == 3 + 1
