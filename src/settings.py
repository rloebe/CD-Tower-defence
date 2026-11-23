"""Společné konstanty hry. Žádná logika, jen čísla a barvy."""

# Okno: hra je navržená pro "logickou" plochu 960 × 640 (všechny rozměry v kódu
# jsou v těchto logických pixelech). Na skutečné obrazovce se vše zvětší o SCALE
# a vycentruje posunem OFFSET – main.py to nastaví podle rozlišení monitoru.
WIDTH = 960
HEIGHT = 640
HUD_HEIGHT = 56  # horní lišta (rozpočet, zpoždění, vlna)
FPS = 60
TITLE = "Delay – ČD Tower Defence"

# Skutečná obrazovka (nastaví main.py při spuštění; výchozí = okno 960 × 640)
SCREEN_W = WIDTH
SCREEN_H = HEIGHT
SCALE = 1.0  # kolikrát je obrazovka větší než logická plocha
OFFSET_X = 0  # o kolik pixelů je logická plocha posunutá, aby byla uprostřed
OFFSET_Y = 0

# Panel s výběrem věží vlevo dole (pod ním se nestaví): x, y, šířka, výška v pixelech
PICKER_RECT = (16, 528, 352, 112)

# Pravidla
START_MONEY = 150  # Kč na začátku hry
MAX_DELAY = 60  # minut zpoždění = prohra
LOAD_TIME = 3.4  # sekund trvá načítací obrazovka
POPUP_LIFE = 1.2  # sekund visí "+10 Kč" / "+5 min"

# Věže: společná data pro výběr věží (ui.py) i jejich chování (towers.py).
#   price = cena v Kč, range = dosah v políčkách, damage = poškození jedné střely,
#   rate = sekund mezi výstřely, slow / slow_time = zpomalení (výpravčí)
TOWER_TYPES = {
    "worker": {"name": "Traťový dělník", "price": 50, "range": 2.3, "damage": 10, "rate": 1.0},
    "draisine": {"name": "Pracovní drezína", "price": 120, "range": 3.1, "damage": 25, "rate": 1.2},
    "dispatcher": {"name": "Výpravčí", "price": 80, "range": 2.1, "damage": 0, "rate": 1.0, "slow": 0.5, "slow_time": 1.5},
}
TOWER_ORDER = ["worker", "draisine", "dispatcher"]  # pořadí v panelu výběru

# Kamera (izometrie jako v Unrailed): svět v políčkách -> obrazovka v pixelech
TILE = 46  # velikost políčka v pixelech
ORIGIN_X = 10  # kde na obrazovce leží bod (0, 0)
ORIGIN_Y = 168
COS_YAW = 0.9781  # pootočení kamery o -12°
SIN_YAW = -0.2079
SIN_PITCH = 0.8192  # sklon kamery 55°
COS_PITCH = 0.5736

# Barvy (R, G, B)
CD_BLUE = (0, 84, 159)
CD_BLUE_LIGHT = (10, 98, 179)
CD_BLUE_DARK = (0, 58, 112)
PANEL = (10, 24, 44)
SIGNAL_YELLOW = (255, 176, 32)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRASS = [(141, 203, 79), (136, 198, 76), (147, 208, 84)]
BALLAST = (173, 161, 140)
BALLAST_EDGE = (142, 130, 111)
SLEEPER = (107, 75, 46)
RAIL = (225, 228, 234)
RAIL_SHADOW = (95, 99, 107)
ROAD = (194, 154, 102)
ROAD_EDGE = (156, 116, 74)
RED = (224, 52, 47)
GREEN = (63, 176, 90)
YELLOW = (255, 176, 32)
