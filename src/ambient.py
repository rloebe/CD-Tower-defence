"""Okolní život na mapě: projíždějící vlaky dole, auta, traktor, pasoucí se krávy, kouř z komínů.

Je to jen dekorace – nic z toho neovlivňuje hru (nepřátele, věže, peníze).
Běží pořád: na načítací obrazovce, v menu, ve hře i při pauze.
Chová se stejně jako prototyp (docs/design-prototyp/Hra.dc.html, funkce
ambientStep a část "okolí" v renderVals). Popis je v docs/vizualni-design.md,
oddíl "Okolní život".

Jak to zapadá do hry (volá main.py):
- Ambient()          vytvoří se, až je známá velikost obrazovky (předkreslí vozidla),
- update(dt)         každý snímek posune vlaky, auta a čas,
- drawables()        vrátí seznam (hloubka, funkce_kreslení); scenery.draw je seřadí
                     spolu s domy a nepřáteli, takže vlak správně zmizí za domem,
- draw_overlay(s)    kouř z komínů, kreslí se nad vším.

Proč se vozidla předkreslují: kreslit desítky mnohoúhelníků každý snímek je pomalé.
Proto se každé vozidlo nakreslí JEDNOU do malého obrázku (scenery.bake) a pak
se už jen posouvá. Jde to, protože projekce je lineární: posun o 1 políčko
doprava je na obrazovce vždy stejný posun o pár pixelů.
"""

import math
import random

import pygame

import iso
import scenery
import world
from scenery import box, face_front, face_left, tri

# ---------- vlak na hlavní trati dole ----------
CAR_LENGTH = 2.2  # délka jednoho vozu v políčkách
CAR_GAP = 0.12  # mezera mezi vozy
TRAIN_CARS = 4  # lokomotiva + 3 vagony
TRAIN_SPEED = 4.5  # políček za sekundu
FIRST_TRAIN = 4.0  # sekund po spuštění hry přijede první vlak
TRAIN_PAUSE = (22.0, 38.0)  # další vlak za náhodný počet sekund z tohoto rozsahu

# ---------- auta na silnici dole ----------
LANES = [(13.3, 1), (13.7, -1)]  # (y pruhu, směr): horní pruh doprava, dolní doleva
CAR_SPEED = 2.4  # políček za sekundu
FIRST_CAR = 2.0  # sekund po spuštění přijede první auto (jako v prototypu)
CAR_PAUSE = (9.0, 17.0)  # další auto za náhodný počet sekund z tohoto rozsahu
CAR_COLORS = ["#D6332F", "#F2F4F7", "#2E7DD1", "#FFB020"]
ROAD_START = 0.0  # auta zmizí mimo silnici x 0–24
ROAD_END = 24.0

# ---------- traktor na oranici ----------
TRACTOR_Y = 3.25
TRACTOR_LEFT = 12.8  # nejlevější poloha (x levého okraje traktoru)
TRACTOR_SPAN = 4.6  # o kolik políček popojede, než se otočí (12.8 -> 17.4)
TRACTOR_SPEED = 0.4  # políček za sekundu

# ---------- krávy u stodoly ----------
# (střed x, y, jak daleko chodí na každou stranu, rychlost kývání, posun fáze)
COWS = [(5.0, 1.85, 0.7, 0.3, 0.0), (6.2, 2.2, 0.6, 0.24, 2.0)]
COW_SIZE = 34  # velikost postavičky v logických pixelech

# ---------- kouř ----------
SMOKE_COLOR = (233, 236, 239)  # #E9ECEF
CHIMNEY_Z = 1.62  # výška ústí komínu v políčkách


def tractor_position(time):
    """Kde je traktor v čase `time` (sekundy). Vrací (x levého okraje, jede_doprava).

    Traktor jezdí tam a zpět. Místo složitého otáčení počítáme jen "ujetou
    vzdálenost" u, která se po 2 × TRACTOR_SPAN opakuje (modulo):
    první polovinu jede doprava, druhou polovinu se vrací doleva.
    """
    u = (time * TRACTOR_SPEED) % (2 * TRACTOR_SPAN)
    going_right = u < TRACTOR_SPAN
    offset = u if going_right else 2 * TRACTOR_SPAN - u
    return TRACTOR_LEFT + offset, going_right


def cow_position(time, cow):
    """Kde je kráva v čase `time`. Vrací (x, y, jde_doleva).

    Kráva se kývá kolem svého místa podle sinu (pomalu tam a zpět).
    Směr chůze = znaménko derivace sinu, tedy kosinu: záporný = jde doleva.
    """
    center_x, y, amplitude, speed, offset = cow
    angle = time * speed + offset
    x = center_x + amplitude * math.sin(angle)
    return x, y, math.cos(angle) < 0


def puff(x, y, z, age, start_size):
    """Jeden obláček kouře. `age` = 0 (právě vyšel z komínu) až 1 (zmizel).

    Vrací (střed x, y, z v políčkách, velikost v logických pixelech, neprůhlednost 0–1).
    Obláček stoupá o 1 políčko, posouvá se doprava (vítr), roste a mizí.
    """
    return (x + age * 0.35, y - age * 0.1, z + age * 1.0, start_size + age * 9, 0.6 * (1 - age))


def chimneys():
    """Místa komínů (x, y v políčkách): 3 domky a nádraží Kolín.

    Musí sedět na komíny, které kreslí scenery.py (domek: kvádr 0,18 × 0,18
    na x0 + 0,7·šířka, y0 + 0,2·hloubka; jeho střed je o 0,09 dál).
    """
    spots = [(x0 + w * 0.7 + 0.09, y0 + d * 0.2 + 0.09) for x0, y0, w, d, _, _ in world.HOUSES]
    kx, ky = world.KOLIN[0], world.KOLIN[1]
    spots.append((kx + 1.68, ky + 0.33))
    return spots


# =====================================================================
# Modely vozidel (seznam tvarů pro scenery.bake). Stojí na x = 0,
# při kreslení se posouvají doprava/doleva.
# =====================================================================

def _locomotive_shapes():
    """Lokomotiva ČD: tmavý podvozek, modrá skříň, bílý pruh, okna, žluté čelo, sběrač."""
    y = world.MAIN_Y
    y0, y1 = y - 0.28, y + 0.28
    shapes = box(0.1, y0 + 0.05, CAR_LENGTH - 0.2, 0.46, 0.02, 0.16, tri("#2A2E35"))
    shapes += box(0, y0, CAR_LENGTH, 0.56, 0.18, 0.82, scenery.CD_BLUE_BOX)
    shapes.append((pygame.Color("#F2F4F7"), face_front(0, CAR_LENGTH, y1, 0.36, 0.43)))
    wx = 0.55
    while wx < CAR_LENGTH - 0.2:  # řada oken každých 0,35 políčka
        shapes.append((pygame.Color("#BFE4FF"), face_front(wx, wx + 0.2, y1, 0.6, 0.82)))
        wx += 0.35
    shapes.append((pygame.Color("#BFE4FF"), face_left(0, y0 + 0.08, y1 - 0.08, 0.6, 0.86)))  # čelní okno
    shapes.append((pygame.Color("#FFC72C"), face_left(0, y0, y1, 0.18, 0.36)))  # žlutý pruh na čele
    shapes += box(0.5, y0 + 0.12, 0.9, 0.32, 1.0, 0.07, tri("#8E939A"))  # sběrač na střeše
    return shapes


def _coach_shapes():
    """Vagon: tmavý podvozek, skříň s modrým bokem, bílý pás s okny."""
    y = world.MAIN_Y
    y0, y1 = y - 0.28, y + 0.28
    shapes = box(0.1, y0 + 0.05, CAR_LENGTH - 0.2, 0.46, 0.02, 0.16, tri("#2A2E35"))
    colors = (pygame.Color("#D2D5DC"), pygame.Color("#00549F"), pygame.Color("#004585"))
    shapes += box(0, y0 + 0.02, CAR_LENGTH, 0.52, 0.18, 0.78, colors)
    shapes.append((pygame.Color("#F2F4F7"), face_front(0, CAR_LENGTH, y1 - 0.02, 0.55, 0.92)))
    wx = 0.2
    while wx < CAR_LENGTH - 0.2:  # okna každých 0,34 políčka
        shapes.append((pygame.Color("#6FA6CC"), face_front(wx, wx + 0.22, y1 - 0.02, 0.6, 0.82)))
        wx += 0.34
    return shapes


def _car_shapes(lane_y, color):
    """Auto dlouhé 0,8 políčka: dvě kola, karoserie, kabina s oknem."""
    y0, y1 = lane_y - 0.17, lane_y + 0.17
    body = tri(color)
    wheel = tri("#22262C")
    shapes = box(0.1, y0 + 0.02, 0.12, 0.3, 0, 0.12, wheel)
    shapes += box(0.58, y0 + 0.02, 0.12, 0.3, 0, 0.12, wheel)
    shapes += box(0, y0, 0.8, 0.34, 0.08, 0.2, body)
    shapes += box(0.18, y0 + 0.03, 0.42, 0.28, 0.28, 0.17, body)
    shapes.append((pygame.Color("#BFE4FF"), face_front(0.22, 0.56, y1 - 0.03, 0.3, 0.42)))
    return shapes


def _tractor_shapes(facing_left):
    """Zelený traktor. Kabina je vzadu, takže při jízdě doleva je model zrcadlově přestavěný."""
    y0, y1 = TRACTOR_Y - 0.2, TRACTOR_Y + 0.2
    cab_x = 0.5 if facing_left else 0.05
    hood_x = 0.05 if facing_left else 0.45
    green = tri("#3E9E3A")
    wheel = tri("#22262C")
    shapes = box(0.6 if facing_left else 0.08, y0 - 0.02, 0.28, 0.44, 0, 0.3, wheel)  # velké zadní kolo
    shapes += box(0.08 if facing_left else 0.68, y0 + 0.02, 0.18, 0.36, 0, 0.18, wheel)  # malé přední
    shapes += box(hood_x, y0 + 0.04, 0.5, 0.32, 0.12, 0.2, green)  # kapota
    shapes += box(cab_x, y0, 0.38, 0.4, 0.12, 0.45, green)  # kabina
    shapes.append((pygame.Color("#BFE4FF"), face_front(cab_x + 0.06, cab_x + 0.32, y1, 0.36, 0.52)))
    shapes += box(0.12 if facing_left else 0.78, TRACTOR_Y - 0.03, 0.05, 0.05, 0.32, 0.25, tri("#3A3F47"))  # výfuk
    return shapes


class Vehicle:
    """Předkreslený model vozidla, který se dá posouvat po ose x.

    length = délka v políčkách, y = v jaké řadě jede (políčka),
    build  = funkce, která vrátí tvary modelu (např. _coach_shapes), args = její parametry.
    """

    def __init__(self, length, y, build, *args):
        self.length = length
        self.y = y
        # Kreslíme 2× větší a pak plynule zmenšíme = hladké hrany (stejně jako mapa).
        # Tvary se musí spočítat AŽ UVNITŘ supersample: body tvarů jsou už pixely
        # z iso.to_screen, a ty musí být taky 2× větší, jinak by model vyšel malý a jinde.
        with iso.supersample(scenery.SUPERSAMPLE):
            big_image, big_pos = scenery.bake(build(*args))
        self.image, self.base_pos = scenery.shrink(big_image, big_pos)

    def placed_at(self, x):
        """Vrátí (hloubka, funkce_kreslení) pro vozidlo, jehož levý konec je na x (políčka)."""
        # O kolik pixelů se obrázek posune, když vozidlo přejede z x = 0 na x.
        # Projekce je lineární, takže je to prostě rozdíl dvou bodů na obrazovce.
        sx0, sy0 = iso.to_screen(0, self.y)
        sx1, sy1 = iso.to_screen(x, self.y)
        pos = (round(self.base_pos[0] + sx1 - sx0), round(self.base_pos[1] + sy1 - sy0))
        image = self.image

        # Funkce, kterou scenery.draw zavolá ve správném pořadí. Pamatuje si image a pos.
        def draw(surface):
            surface.blit(image, pos)

        # Hloubka podle středu vozidla: rozhoduje, jestli je před domem, nebo za ním.
        return (iso.depth(x + self.length / 2, self.y), draw)


class Ambient:
    """Všechen okolní život na mapě. Vytvoří ho main.py, až zná velikost obrazovky."""

    def __init__(self, seed=None):
        # seed = pevné "náhodné" číslo pro testy (pak je chování pokaždé stejné)
        self.rng = random.Random(seed)
        self.time = 0.0  # vlastní hodiny okolí v sekundách (běží i v menu a při pauze)

        # vlak: None = žádný nejede; jinak {"dir": 1/-1, "x": poloha čela}
        self.train = None
        self.next_train = FIRST_TRAIN
        # auta: seznam {"lane": 0/1, "x": levý okraj, "color": index barvy}
        self.cars = []
        self.next_car = FIRST_CAR

        # předkreslené modely (jen jednou, tady)
        self.locomotive = Vehicle(CAR_LENGTH, world.MAIN_Y, _locomotive_shapes)
        self.coach = Vehicle(CAR_LENGTH, world.MAIN_Y, _coach_shapes)
        # auta: pro každý pruh a každou barvu jeden obrázek (2 × 4 = 8)
        self.car_models = [[Vehicle(0.8, lane_y, _car_shapes, lane_y, color) for color in CAR_COLORS]
                           for lane_y, _ in LANES]
        # traktor: klíč = jestli je otočený doleva
        self.tractors = {False: Vehicle(0.95, TRACTOR_Y, _tractor_shapes, False),
                         True: Vehicle(0.95, TRACTOR_Y, _tractor_shapes, True)}

    # ---------- pohyb ----------

    def update(self, dt):
        """Posune vlak a auta a vypustí nové. `dt` = čas od minulého snímku v sekundách.

        Traktor, krávy a kouř se nehýbou "krok po kroku": jejich polohu
        spočítáme rovnou z času (self.time) až při kreslení.
        """
        self.time += dt
        self._update_train(dt)
        self._update_cars(dt)

    def _update_train(self, dt):
        """Vlak jede po hlavní trati; když zmizí, naplánuje se další."""
        if self.train is not None:
            self.train["x"] += self.train["dir"] * TRAIN_SPEED * dt
            # vlak zmizí, až jeho čelo přejede kus za okraj mapy
            gone_right = self.train["dir"] > 0 and self.train["x"] > 29
            gone_left = self.train["dir"] < 0 and self.train["x"] < -2
            if gone_right or gone_left:
                self.train = None
        elif self.time >= self.next_train:
            direction = 1 if self.rng.random() < 0.5 else -1
            # doprava: čelo začíná na x = 3 (vlak je ještě celý vlevo mimo obraz)
            # doleva: čelo (levý konec) začíná na x = 20
            self.train = {"dir": direction, "x": 3.0 if direction > 0 else 20.0}
            self.next_train = self.time + self.rng.uniform(*TRAIN_PAUSE)

    def _update_cars(self, dt):
        """Auta jedou po silnici; ta mimo silnici zmizí a občas přijede nové."""
        for car in self.cars:
            direction = LANES[car["lane"]][1]
            car["x"] += direction * CAR_SPEED * dt
        self.cars = [car for car in self.cars if ROAD_START < car["x"] < ROAD_END]

        if self.time >= self.next_car:
            lane = 0 if self.rng.random() < 0.5 else 1
            start_x = 1.0 if LANES[lane][1] > 0 else 23.0
            self.cars.append({"lane": lane, "x": start_x, "color": self.rng.randrange(len(CAR_COLORS))})
            self.next_car = self.time + self.rng.uniform(*CAR_PAUSE)

    def train_car_positions(self):
        """Levé okraje (x) všech vozů vlaku; první je lokomotiva. Bez vlaku prázdný seznam."""
        if self.train is None:
            return []
        front = self.train["x"]
        positions = []
        for i in range(TRAIN_CARS):
            if self.train["dir"] > 0:
                # jede doprava: čelo je pravý konec lokomotivy, vagony jsou za ní (vlevo)
                left = front - (i + 1) * CAR_LENGTH - i * CAR_GAP
            else:
                # jede doleva: čelo je levý konec lokomotivy, vagony jsou za ní (vpravo)
                left = front + i * (CAR_LENGTH + CAR_GAP)
            positions.append(left)
        return positions

    # ---------- kreslení ----------

    def drawables(self):
        """Vše, co se řadí podle hloubky spolu s mapou: seznam (hloubka, funkce_kreslení)."""
        items = []
        # každý vůz zvlášť, protože vlak je dlouhý a každý vůz může být před/za jiným domem
        for i, left in enumerate(self.train_car_positions()):
            model = self.locomotive if i == 0 else self.coach
            items.append(model.placed_at(left))

        for car in self.cars:
            items.append(self.car_models[car["lane"]][car["color"]].placed_at(car["x"]))

        tractor_x, going_right = tractor_position(self.time)
        items.append(self.tractors[not going_right].placed_at(tractor_x))

        for cow in COWS:
            items.append(self._cow_drawable(cow))
        return items

    def _cow_drawable(self, cow):
        """Kráva jako (hloubka, funkce_kreslení). Postavička "cow" ze sprites.py."""
        import sprites  # načte se až tady, stejně jako ostatní kreslení (po otevření okna)

        x, y, facing_left = cow_position(self.time, cow)
        sx, sy = iso.to_screen(x, y)
        # postavička stojí nohama na zemi (nohy jsou 14/60 velikosti pod středem, jako u nepřátel)
        center = (sx, sy - iso.px(COW_SIZE) * 14 / 60)
        phase = self.time * 0.5  # pomalá chůze

        def draw(surface):
            sprites.draw_sprite(surface, "cow", center, COW_SIZE, phase=phase, flip=facing_left)

        return (iso.depth(x, y), draw)

    def draw_overlay(self, surface):
        """Kouř z komínů a z traktoru. Kreslí se nad vším (je vysoko ve vzduchu)."""
        # 3 obláčky z každého komínu, posunuté v čase o třetinu cyklu, aby kouř šel plynule.
        # "+ index * 0.21" posune každý komín jinak, aby nekouřily všechny naráz.
        for index, (cx, cy) in enumerate(chimneys()):
            for i in range(3):
                age = (self.time * 0.3 + i / 3 + index * 0.21) % 1  # cyklus 1 / 0,3 ≈ 3,3 s
                self._draw_puff(surface, puff(cx, cy, CHIMNEY_Z, age, 5))

        # traktor: 2 menší obláčky z výfuku, rychleji (0,7 místo 0,3)
        tractor_x, going_right = tractor_position(self.time)
        exhaust_x = tractor_x + (0.8 if going_right else 0.15)
        for i in range(2):
            age = (self.time * 0.7 + i / 2) % 1
            self._draw_puff(surface, puff(exhaust_x, TRACTOR_Y, 0.6, age, 3))

    def _draw_puff(self, surface, cloud):
        """Nakreslí jeden obláček: světle šedý kosočtverec s danou průhledností."""
        x, y, z, size, opacity = cloud
        sx, sy = iso.to_screen(x, y, z)
        # čtverec o straně `size` otočený o 45° má od středu ke špičce size / √2
        half = iso.px(size) / math.sqrt(2)
        side = math.ceil(half * 2) + 2
        # průhlednost jde jen přes vlastní malý obrázek s alfa kanálem
        layer = pygame.Surface((side, side), pygame.SRCALPHA)
        c = side / 2
        points = [(c, c - half), (c + half, c), (c, c + half), (c - half, c)]
        pygame.draw.polygon(layer, (*SMOKE_COLOR, round(255 * opacity)), points)
        surface.blit(layer, (sx - c, sy - c))
