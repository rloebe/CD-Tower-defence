"""Postavičky (nepřátelé i věže) nakreslené z mnohoúhelníků, včetně animací.

Tvary jsou převzaté 1:1 z designu (docs/design-prototyp/Sprite.dc.html).
Každá postavička je seznam tvarů a každý tvar je:
    (barva, body, značka_animace, barva_při_bliknutí)
- body jsou v "malých" souřadnicích od -30 do 30 (střed postavičky je 0, 0),
  při kreslení se přepočítají na skutečnou velikost v pixelech,
- značka animace (např. "legA") říká, jak se má tvar hýbat (viz _offsets),
- barva při bliknutí se použije každou druhou třetinu sekundy (blikající světla).
Tvary se kreslí v pořadí, v jakém jsou v seznamu – co je dál, je navrchu.

Jediná veřejná funkce je draw_sprite(); používají ji enemies.py a towers.py.
"""

import math

import pygame

import settings

# poloprůhledný stín pod postavičkou (R, G, B, průhlednost)
SHADOW = (0, 0, 0, 56)

# Společný podstavec všech věží (šestiúhelník s boky)
_BASE = [
    (SHADOW, [(-16, 20), (18, 18), (22, 22), (14, 25), (-12, 25)]),
    ("#A9AFB7", [(-16, 14), (-8, 10), (8, 10), (16, 14), (8, 18), (-8, 18)]),
    ("#7E848C", [(-16, 14), (-8, 18), (-8, 22), (-16, 18)]),
    ("#6C7179", [(-8, 18), (8, 18), (8, 22), (-8, 22)]),
    ("#5A5F66", [(8, 18), (16, 14), (16, 18), (8, 22)]),
]

# Společná hlava pracovníků (dělník, výpravčí) – při stání se mírně pohupuje ("bob")
_HEAD = [
    ("#F0BE93", [(0, -22), (-5, -19), (-5, -14), (0, -12)], "bob"),
    ("#D9A077", [(0, -22), (5, -19), (5, -14), (0, -12)], "bob"),
]

SPRITES = {
    # ---------- nepřátelé ----------
    "cow": [
        (SHADOW, [(-20, 12), (18, 12), (22, 15), (16, 18), (-16, 18), (-22, 15)]),
        # nohy: dvojice A a B se střídají při chůzi
        ("#2A2A2A", [(-8, 8), (-5, 8), (-5, 14), (-8, 14)], "legB"),
        ("#2A2A2A", [(11, 8), (14, 8), (14, 14), (11, 14)], "legA"),
        ("#3A3A3A", [(-14, 8), (-10, 8), (-10, 15), (-14, 15)], "legA"),
        ("#3A3A3A", [(6, 8), (10, 8), (10, 15), (6, 15)], "legB"),
        ("#353535", [(-19, -6), (-22, 2), (-20, 3), (-18, -4)], "tail"),
        # tělo (světlá horní a tmavší spodní plocha) a skvrny
        ("#F4F1EA", [(-18, -9), (10, -10), (15, 0), (-19, 0)], "body"),
        ("#D6D0C3", [(-19, 0), (15, 0), (12, 9), (-16, 9)], "body"),
        ("#2B2B2B", [(-11, -9), (-3, -9), (-5, -2), (-12, -3)], "body"),
        ("#2B2B2B", [(2, 1), (9, 0), (8, 7), (1, 7)], "body"),
        # hlava: ucho, hlava, roh, čumák, oko
        ("#D6D0C3", [(12, -13), (9, -16), (14, -10)], "head"),
        ("#F4F1EA", [(12, -13), (23, -11), (24, -2), (15, 0)], "head"),
        ("#E6D9B5", [(14, -13), (15, -18), (17, -12)], "head"),
        ("#E8A3A8", [(20, -5), (26, -4), (25, 2), (19, 1)], "head"),
        ("#1C1C1C", [(17, -9), (19, -9), (19, -7), (17, -7)], "head"),
    ],
    "signal": [
        (SHADOW, [(-10, 18), (10, 18), (12, 21), (-12, 21)]),
        ("#5A5F66", [(-8, 14), (8, 14), (6, 19), (-6, 19)]),
        # stožár a hlava návěstidla poskakují ("hop")
        ("#7E848C", [(-2, -4), (0, -4), (0, 15), (-2, 15)], "hop"),
        ("#5A5F66", [(0, -4), (2, -4), (2, 15), (0, 15)], "hop"),
        ("#3A3F47", [(-9, -24), (0, -25), (0, -2), (-9, -3)], "hop"),
        ("#2A2E35", [(0, -25), (9, -24), (9, -3), (0, -2)], "hop"),
        # porouchané červené světlo bliká, zelené je zhasnuté
        ("#6B1F1F", [(-4, -18), (-2, -21.5), (2, -21.5), (4, -18), (2, -14.5), (-2, -14.5)], "hop", "#FF3B30"),
        ("#1F4A2A", [(-4, -9), (-2, -12.5), (2, -12.5), (4, -9), (2, -5.5), (-2, -5.5)], "hop"),
        ("#C7CAD0", [(-10, -30), (-6, -33), (-2, -30), (-2, -27), (-6, -25), (-10, -27)], "smoke"),
        # jiskra: při bliknutí zmizí (None = nekreslit)
        ("#FFCC00", [(12, -28), (5, -17), (10, -17), (4, -6), (17, -20), (12, -20), (17, -28)], "hop", None),
    ],
    "tree": [
        (SHADOW, [(-22, 8), (18, 8), (24, 12), (-18, 13)]),
        ("#7E5530", [(-6, -5), (-2, -14), (0, -13), (-3, -5)], "bob"),
        ("#9A6A3C", [(-22, -4), (10, -6), (12, 0), (-22, 1)], "bob"),
        ("#6E4A28", [(-22, 1), (12, 0), (11, 6), (-21, 6)], "bob"),
        ("#C89A63", [(-22, -4), (-26, 1), (-21, 6), (-22, 1)], "bob"),
        # koruna se třese ("leaves")
        ("#2F7039", [(-1, -5), (4, -14), (10, 4)], "leaves"),
        ("#2F7039", [(10, 4), (24, -6), (22, 8)], "leaves"),
        ("#2F7039", [(18, -20), (28, -12), (24, -6)], "leaves"),
        ("#3F8F4A", [(4, -14), (24, -6), (10, 4)], "leaves"),
        ("#57A85C", [(4, -14), (18, -20), (24, -6)], "leaves"),
    ],
    "closure": [
        (SHADOW, [(-26, 16), (26, 16), (28, 21), (-28, 21)]),
        # zábrana "chodí" na dvou nohách
        ("#5A5F66", [(-20, 0), (-16, 0), (-16, 17), (-20, 17)], "legA"),
        ("#5A5F66", [(16, 0), (20, 0), (20, 17), (16, 17)], "legB"),
        ("#3A3F47", [(-24, 15), (-12, 15), (-12, 18), (-24, 18)], "legA"),
        ("#3A3F47", [(12, 15), (24, 15), (24, 18), (12, 18)], "legB"),
        # deska s červenobílými pruhy
        ("#F4F4F4", [(-26, -14), (26, -14), (26, -6), (-26, -6)], "body"),
        ("#D9D9D9", [(-26, -6), (26, -6), (26, 2), (-26, 2)], "body"),
        ("#E0342F", [(-22, -14), (-14, -14), (-18, -6), (-26, -6)], "body"),
        ("#E0342F", [(-6, -14), (2, -14), (-2, -6), (-10, -6)], "body"),
        ("#E0342F", [(10, -14), (18, -14), (14, -6), (6, -6)], "body"),
        ("#B8241F", [(-26, -6), (-18, -6), (-22, 2), (-26, 2)], "body"),
        ("#B8241F", [(-10, -6), (-2, -6), (-6, 2), (-14, 2)], "body"),
        ("#B8241F", [(6, -6), (14, -6), (10, 2), (2, 2)], "body"),
        ("#B8241F", [(22, -6), (26, -6), (26, 2), (18, 2)], "body"),
        # oranžová výstražná lampa bliká
        ("#FFB347", [(-5, -23), (0, -24), (0, -14), (-6, -14)], "body", "#FFE7A8"),
        ("#FF8A1F", [(0, -24), (5, -23), (6, -14), (0, -14)], "body", "#FFC970"),
    ],
    # ---------- věže ----------
    "worker": _BASE + [
        ("#2C3E66", [(-6, 2), (-1, 2), (-1, 15), (-6, 15)]),
        ("#22325A", [(1, 2), (6, 2), (6, 15), (1, 15)]),
        ("#E86A0E", [(-12, -10), (-8, -12), (-8, -2), (-11, 0)], "bob"),
        # pravá ruka s klíčem se při zásahu zvedne ("arm")
        ("#C85A0C", [(8, -12), (12, -10), (13, -1), (8, -2)], "arm"),
        ("#FF8A2A", [(-8, -12), (0, -13), (0, 3), (-8, 2)], "bob"),
        ("#E86A0E", [(0, -13), (8, -12), (8, 2), (0, 3)], "bob"),
        ("#E9ECEF", [(-8, -4), (8, -4), (8, -1), (-8, -1)], "bob"),
        ("#B8BEC6", [(12, -1), (14, -1), (18, -12), (16, -12)], "arm"),
        ("#9AA0A8", [(15, -15), (20, -13), (19, -10), (16, -11)], "arm"),
    ] + _HEAD + [
        ("#FFD84A", [(-7, -19), (0, -26), (0, -19)], "bob"),
        ("#E8B800", [(0, -26), (7, -19), (0, -19)], "bob"),
        ("#D4A800", [(-8, -19), (8, -19), (7, -17), (-7, -17)], "bob"),
    ],
    "draisine": _BASE + [
        ("#3A3F47", [(2, -10), (5, -10), (16, -22), (14, -24)]),
        ("#22262C", [(15, -22), (17, -22), (17, -16), (15, -16)], "swing"),
        ("#3A3F47", [(-18, 6), (18, 6), (16, 12), (-16, 12)]),
        ("#22262C", [(-15, 13), (-13, 9.5), (-9, 9.5), (-7, 13), (-9, 16.5), (-13, 16.5)]),
        ("#22262C", [(7, 13), (9, 9.5), (13, 9.5), (15, 13), (13, 16.5), (9, 16.5)]),
        # karoserie se otřásá ("rumble"), maják bliká
        ("#F2B705", [(-18, -6), (10, -6), (10, 6), (-18, 6)], "rumble"),
        ("#C99100", [(10, -6), (18, -10), (18, 6), (10, 6)], "rumble"),
        ("#FFD23F", [(-18, -6), (10, -6), (18, -10), (-10, -10)], "rumble"),
        ("#F2B705", [(-16, -20), (-2, -20), (-2, -6), (-16, -6)], "rumble"),
        ("#C99100", [(-2, -20), (4, -24), (4, -8), (-2, -6)], "rumble"),
        ("#FFE066", [(-16, -20), (-2, -20), (4, -24), (-10, -24)], "rumble"),
        ("#BFE4FF", [(-14, -18), (-4, -18), (-14, -11)], "rumble"),
        ("#86C1EC", [(-4, -18), (-4, -11), (-14, -11)], "rumble"),
        ("#FF7A1A", [(-11, -27), (-7, -27), (-6, -24), (-12, -24)], "rumble", "#FFE08A"),
    ],
    "dispatcher": _BASE + [
        ("#1E2B45", [(-6, 2), (-1, 2), (-1, 15), (-6, 15)]),
        ("#16223A", [(1, 2), (6, 2), (6, 15), (1, 15)]),
        ("#00549F", [(-9, -12), (-13, -10), (-12, 0), (-9, -1)], "bob"),
        ("#1F6FC0", [(-9, -12), (0, -13), (0, 5), (-10, 4)], "bob"),
        ("#00549F", [(0, -13), (9, -12), (10, 4), (0, 5)], "bob"),
        # ruka s plácačkou se při pulzu zvedne ("paddle")
        ("#1F6FC0", [(8, -12), (11, -13), (15, -22), (12, -23)], "paddle"),
        ("#F2F4F7", [(-3, -13), (3, -13), (0, -9)], "bob"),
        ("#6B4A2B", [(13, -22), (15, -22), (16, -27), (14, -27)], "paddle"),
        ("#2FA84F", [(16, -37), (10.8, -34), (10.8, -28), (16, -25)], "paddle"),
        ("#F2F4F7", [(16, -37), (21.2, -34), (21.2, -28), (16, -25)], "paddle"),
    ] + _HEAD + [
        # červená čepice výpravčího
        ("#E0342F", [(-6, -19), (0, -19), (0, -25), (-5, -24)], "bob"),
        ("#B8241F", [(0, -19), (6, -19), (5, -24), (0, -25)], "bob"),
        ("#22262C", [(-8, -19), (6, -19), (5, -17), (-8, -17)], "bob"),
    ],
}

# Postavička se kreslí do čtverce -40..40 (o kousek větší než -30..30),
# aby se nic neuřízlo, např. zvednutá plácačka výpravčího sahá až na -37.
_HALF = 40


def _offsets(phase, action):
    """Spočítá posun (dx, dy) každé značky animace v daném okamžiku.

    phase  = čas v sekundách, jak dlouho už se postavička hýbe (určuje krok chůze)
    action = 0–1, jak moc právě "pracuje" (1 = právě vystřelila, pak klesá k 0)
    Používáme sinus, protože se plynule opakuje – nohy jdou tam a zpátky.
    """
    w = math.sin(phase * 9)  # krok chůze: -1 až 1, zhruba 1,4 kroku za sekundu
    return {
        "legA": (w * 1.6, -max(0.0, w) * 1.8),  # noha dopředu a nahoru
        "legB": (-w * 1.6, -max(0.0, -w) * 1.8),  # druhá noha naopak
        "body": (0, -abs(w) * 0.9),  # tělo se při každém kroku mírně zvedne
        "head": (0, -abs(w) * 0.9 + math.sin(phase * 9 + 1.2) * 0.8),  # kývání hlavou
        "tail": (math.sin(phase * 6) * 1.6, -abs(w) * 0.9),  # ocas
        "hop": (0, -abs(math.sin(phase * 7)) * 3),  # poskakování
        "smoke": (math.sin(phase * 3) * 1.5, -((phase * 6) % 6)),  # kouř stoupá a znovu začne
        "leaves": (math.sin(phase * 11) * 0.9, math.cos(phase * 13) * 0.5),  # třesoucí se listí
        "bob": (0, math.sin(phase * 4) * 0.6),  # klidné dýchání
        "arm": (action * 2, math.sin(phase * 4) * 0.6 - action * 6),  # máchnutí klíčem
        "paddle": (0, math.sin(phase * 4) * 0.6 - action * 6),  # zvednutí plácačky
        "swing": (math.sin(phase * 3) * 1.6, 0),  # houpající se hák jeřábu
        "rumble": (0, math.sin(phase * 25) * 0.35),  # rychlé otřásání motoru
    }


# Postavičky kreslíme 2× větší a pak je plynule zmenšíme – tím se hrany
# vyhladí (antialiasing), protože pygame jinak kreslí mnohoúhelníky "zubatě".
SUPERSAMPLE = 2


def draw_sprite(surface, kind, center, size, phase=0.0, action=0.0, flip=False):
    """Nakreslí postavičku.

    surface = kam kreslit (obrazovka)
    kind    = "cow" | "signal" | "tree" | "closure" | "worker" | "draisine" | "dispatcher"
    center  = střed postavičky na obrazovce ve skutečných pixelech (x, y), např. z iso.to_screen
    size    = velikost postavičky v logických pixelech (návrh 960 × 640); zvětší se o settings.SCALE
    phase   = čas animace v sekundách
    action  = 0–1, jak moc právě pracuje (věže při střele)
    flip    = True = zrcadlově otočit (nepřítel jede doleva)
    """
    real_size = size * settings.SCALE  # velikost na skutečné obrazovce
    scale = real_size * SUPERSAMPLE / 60  # kolik pixelů (ve 2× větším obrázku) je jedna "malá" jednotka
    side = int(_HALF * 2 * scale) + 2
    # Kreslíme nejdřív do vlastního průhledného obrázku (SRCALPHA), protože
    # jen tak jde stín kreslit poloprůhledně a celou postavičku zrcadlově otočit.
    image = pygame.Surface((side, side), pygame.SRCALPHA)

    offsets = _offsets(phase, action)
    blink = int(phase * 3) % 2 == 0  # světla blikají třikrát za sekundu

    for shape in SPRITES[kind]:
        color, points = shape[0], shape[1]
        tag = shape[2] if len(shape) > 2 else None
        if len(shape) > 3 and blink:
            color = shape[3]
        if color is None:
            continue  # tvar je právě "zhasnutý"
        dx, dy = offsets.get(tag, (0, 0))
        # z malých souřadnic (-40..40) na pixely v obrázku (0..side)
        pixels = [((x + dx + _HALF) * scale, (y + dy + _HALF) * scale) for x, y in points]
        pygame.draw.polygon(image, color, pixels)

    # plynulé zmenšení na skutečnou velikost = vyhlazené hrany
    final_side = max(1, round(side / SUPERSAMPLE))
    image = pygame.transform.smoothscale(image, (final_side, final_side))
    if flip:
        image = pygame.transform.flip(image, True, False)
    surface.blit(image, (center[0] - final_side / 2, center[1] - final_side / 2))
