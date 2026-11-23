"""Společné konstanty hry. Žádná logika, jen čísla a barvy."""

# Okno
WIDTH = 960
HEIGHT = 640
HUD_HEIGHT = 56  # horní lišta (rozpočet, zpoždění, vlna)
FPS = 60
TITLE = "Výluka – ČD Tower Defence"

# Panel s výběrem věží vlevo dole (pod ním se nestaví): x, y, šířka, výška v pixelech
PICKER_RECT = (16, 528, 352, 112)

# Pravidla
START_MONEY = 150  # Kč na začátku hry
MAX_DELAY = 60  # minut zpoždění = prohra
LOAD_TIME = 3.4  # sekund trvá načítací obrazovka
POPUP_LIFE = 1.2  # sekund visí "+10 Kč" / "+5 min"

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
