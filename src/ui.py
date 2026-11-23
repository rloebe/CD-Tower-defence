"""Obrazovky a ovládání: načítání, menu, horní lišta, výběr věží, konec hry.

Vzhled podle docs/vizualni-design.md. Jak to funguje:
- Všechny rozměry tady jsou v LOGICKÝCH pixelech (návrh 960 × 640). Funkce L()
  a R() je převedou na skutečné pixely obrazovky (zvětšení + vycentrování).
- Každé tlačítko se při kreslení zapíše do seznamu _buttons (obdélník + akce).
  Když hráč klikne, handle_event() se podívá, do kterého tlačítka se trefil.
  Tlačítka se tedy kreslí i "klikají" podle stejného obdélníku.
- main.py volá draw() každý snímek a handle_event() pro každou událost.
"""

import pygame

import iso
import settings
import sprites
import track
import world

# ---------- barvy z designu ----------
WHITE = (255, 255, 255)
LABEL = (207, 225, 245)  # popisky v liště
TEXT_DIM = (228, 238, 248)
YELLOW = settings.SIGNAL_YELLOW
DARK_TEXT = (28, 36, 48)
PANEL = (10, 24, 44)
CD_BLUE = settings.CD_BLUE

# tlačítka nakreslená v tomto snímku: [(obdélník na obrazovce, akce)]
_buttons = []
# přepínač "Místa ke stavbě" (zvýraznit všechna volná místa)
_show_spots = False
# předkreslená vrstva se zvýrazněnými místy ke stavbě (mění se jen při stavbě věže)
_spots_cache = {"key": None, "image": None}
_font_cache = {}

TIPS = [
    "Tip: Výpravčí nestřílí, ale zpomalí všechno v dosahu.",
    "Tip: Věže míří na problém, který je nejblíž stanici.",
    "Tip: Na konci přijede výluka – šetři na drezínu.",
]


# =====================================================================
# Pomocné funkce: převod souřadnic, písmo, text, panely, tlačítka
# =====================================================================

def L(x, y):
    """Bod v logických pixelech -> skutečné pixely na obrazovce."""
    return (settings.OFFSET_X + x * settings.SCALE, settings.OFFSET_Y + y * settings.SCALE)


def R(x, y, w, h):
    """Obdélník v logických pixelech -> pygame.Rect ve skutečných pixelech."""
    left, top = L(x, y)
    return pygame.Rect(round(left), round(top), round(w * settings.SCALE), round(h * settings.SCALE))


def font(size):
    """Písmo dané velikosti (v logických pixelech). Ukládá se, aby se nevytvářelo každý snímek."""
    real = max(8, round(size * 1.35 * settings.SCALE))  # výchozí písmo pygame je menší, proto × 1,35
    if real not in _font_cache:
        _font_cache[real] = pygame.font.Font(None, real)
    return _font_cache[real]


def text(surface, content, size, pos, color=WHITE, anchor="center"):
    """Napíše text. pos je v logických pixelech, anchor říká, který bod textu tam má být."""
    image = font(size).render(content, True, color)
    rect = image.get_rect(**{anchor: L(*pos)})
    surface.blit(image, rect)
    return rect


def cut_corners(rect, cut):
    """Body obdélníku se dvěma zkosenými rohy (vlevo nahoře a vpravo dole) – styl z designu."""
    c = cut * settings.SCALE
    x, y, w, h = rect
    return [(x + c, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h), (x, y + c)]


def panel(surface, x, y, w, h, color=PANEL, alpha=230, cut=12):
    """Tmavě modrý poloprůhledný panel se zkosenými rohy. Vrací jeho obdélník."""
    rect = R(x, y, w, h)
    # průhlednost jde jen přes vlastní obrázek se SRCALPHA, proto ho kreslíme zvlášť
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(layer, (*color, alpha), cut_corners((0, 0, rect.w, rect.h), cut))
    surface.blit(layer, rect)
    return rect


_shade_cache = {}


def shade_screen(surface, color, alpha):
    """Ztmaví celou obrazovku (pod menu, načítáním a koncem hry).

    Poloprůhledná vrstva přes celou obrazovku se vytvoří jen jednou a uloží,
    protože vytvářet ji každý snímek znovu by bylo zbytečně pomalé.
    """
    key = (surface.get_size(), color, alpha)
    if key not in _shade_cache:
        layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        layer.fill((*color, alpha))
        _shade_cache[key] = layer
    surface.blit(_shade_cache[key], (0, 0))


def button(surface, x, y, w, h, label, action, primary=False, enabled=True, size=17, slant=True):
    """Tlačítko: nakreslí ho a zapíše do _buttons, aby na něj šlo kliknout.

    primary = žluté hlavní tlačítko, jinak průhledné s bílým rámečkem.
    """
    rect = R(x, y, w, h)
    hover = enabled and rect.collidepoint(pygame.mouse.get_pos())
    cut = 8 * settings.SCALE if slant else 0
    shape = [(rect.x + cut, rect.y), (rect.right, rect.y), (rect.right - cut, rect.bottom), (rect.x, rect.bottom)]
    if primary:
        color = (255, 196, 80) if hover else YELLOW
        if not enabled:
            color = (138, 151, 168)  # šedé = teď nejde použít
        pygame.draw.polygon(surface, color, shape)
        text(surface, label, size, _logical(rect.center), DARK_TEXT)
    else:
        if hover:
            layer = pygame.Surface(rect.size, pygame.SRCALPHA)
            layer.fill((255, 255, 255, 40))
            surface.blit(layer, rect)
        pygame.draw.rect(surface, (200, 210, 225), rect, max(1, round(2 * settings.SCALE)))
        text(surface, label, size, _logical(rect.center), WHITE)
    if enabled:
        _buttons.append((rect, action))
    return rect


def _logical(point):
    """Opak L(): skutečné pixely -> logické (pro text uprostřed tlačítka)."""
    return ((point[0] - settings.OFFSET_X) / settings.SCALE, (point[1] - settings.OFFSET_Y) / settings.SCALE)


def coin_icon(surface, x, y, size=26):
    """Mince ze tří plošek (logické souřadnice levého horního rohu)."""
    k = size / 26
    for color, pts in (((255, 216, 74), [(13, 1), (24, 7), (13, 13), (2, 7)]),
                       ((232, 184, 0), [(2, 7), (13, 13), (13, 25), (2, 19)]),
                       ((201, 145, 0), [(13, 13), (24, 7), (24, 19), (13, 25)])):
        pygame.draw.polygon(surface, color, [L(x + px * k, y + py * k) for px, py in pts])


def clock_icon(surface, x, y):
    """Šestiúhelníkové hodiny (ikona zpoždění)."""
    pygame.draw.polygon(surface, (242, 244, 247), [L(x + a, y + b) for a, b in [(13, 1), (23, 7), (23, 19), (13, 25), (3, 19), (3, 7)]])
    pygame.draw.polygon(surface, (210, 213, 220), [L(x + a, y + b) for a, b in [(13, 1), (23, 7), (23, 19), (13, 13)]])
    pygame.draw.polygon(surface, DARK_TEXT, [L(x + a, y + b) for a, b in [(12, 6), (14, 6), (14, 14), (12, 14)]])
    pygame.draw.polygon(surface, DARK_TEXT, [L(x + a, y + b) for a, b in [(12, 12), (19, 15), (18, 17), (12, 14)]])


def delay_color(delay):
    """Barva pruhu zpoždění: zelená, od 30 min žlutá, od 45 min červená."""
    if delay >= 45:
        return settings.RED
    if delay >= 30:
        return YELLOW
    return settings.GREEN


# =====================================================================
# Ovládání
# =====================================================================

def handle_event(event, game):
    """Převede klik nebo klávesu na akci pro main.py.

    Vrací "start", "restart", "menu", "next_wave", "pause", "speed",
    "skip_loading", "quit", "ui" (rozhraní to vyřídilo samo) nebo None
    (událost patří věžím – např. klik na trávu = stavba).
    """
    global _show_spots

    if game.state == "loading" and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
        return "skip_loading"

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # tlačítka nakreslená naposledy; odzadu, aby vyhrálo to nakreslené navrchu
        for rect, action in reversed(_buttons):
            if rect.collidepoint(event.pos):
                if action.startswith("select:"):
                    game.selected_tower = action.split(":")[1]
                    return "ui"
                if action == "toggle_spots":
                    _show_spots = not _show_spots
                    return "ui"
                return action
        # klik na lištu nebo panel výběru nesmí postavit věž "pod" nimi
        if game.state == "playing" and _over_interface(event.pos):
            return "ui"
        return None

    if event.type != pygame.KEYDOWN:
        return None
    if event.key == pygame.K_ESCAPE:
        return "quit"
    if game.state == "menu" and event.key == pygame.K_RETURN:
        return "start"
    if game.state == "playing":
        keys = {pygame.K_SPACE: "next_wave", pygame.K_p: "pause", pygame.K_f: "speed"}
        if event.key in keys:
            return keys[event.key]
        # klávesy 1, 2, 3 vyberou věž
        for number, kind in zip((pygame.K_1, pygame.K_2, pygame.K_3), settings.TOWER_ORDER):
            if event.key == number:
                game.selected_tower = kind
                return "ui"
    if game.state in ("won", "lost"):
        if event.key == pygame.K_r:
            return "restart"
        if event.key == pygame.K_m:
            return "menu"
    return None


def _over_interface(pos):
    """Je bod (skutečné pixely) nad horní lištou nebo nad panelem výběru věží?"""
    top_bar = pygame.Rect(0, 0, settings.SCREEN_W, R(0, 0, 0, settings.HUD_HEIGHT).bottom)
    return top_bar.collidepoint(pos) or R(*settings.PICKER_RECT).collidepoint(pos)


# =====================================================================
# Kreslení
# =====================================================================

def draw(surface, game):
    """Nakreslí rozhraní podle stavu hry (volá main.py každý snímek)."""
    _buttons.clear()
    pygame.mouse.set_visible(True)
    if game.state == "loading":
        draw_loading(surface, game)
    elif game.state == "menu":
        draw_menu(surface, game)
    else:
        draw_hud(surface, game)
        if game.state in ("won", "lost"):
            draw_end_screen(surface, game)


# ---------- načítání ----------

def draw_loading(surface, game):
    """Název hry přes ztmavenou mapu, malý ukazatel průběhu a vláček, který po něm jede."""
    shade_screen(surface, (8, 24, 48), 180)
    text(surface, "ČESKÉ DRÁHY · TOWER DEFENCE", 13, (480, 150), LABEL)
    text(surface, "VÝLUKA", 112, (480, 222))
    text(surface, "Ubraň trať z Kolína do Prahy", 18, (480, 292), TEXT_DIM)

    # plynulý průběh: zpočátku pomalu, uprostřed rychle, na konci zpomalí (jako rozjezd a brzdění vlaku)
    p = game.load_progress
    eased = 2 * p * p if p < 0.5 else 1 - (-2 * p + 2) ** 2 / 2
    bar_x, bar_y, bar_w = 300, 470, 360
    pygame.draw.rect(surface, (225, 228, 234), R(bar_x, bar_y - 2, bar_w, 2))  # kolejnice
    pygame.draw.rect(surface, (28, 42, 64), R(bar_x, bar_y, bar_w, 8))
    pygame.draw.rect(surface, YELLOW, R(bar_x, bar_y, bar_w * eased, 8))
    _mini_train(surface, bar_x + bar_w * eased, bar_y - 2, game.load_progress)

    percent = int(eased * 100)
    text(surface, f"Načítání… {percent} %" if percent < 100 else "Hotovo – vlak je ve stanici!", 15, (480, 498))
    text(surface, TIPS[int(game.load_progress * 3) % len(TIPS)], 13, (480, 522), (220, 235, 216))
    button(surface, 840, 600, 100, 30, "Přeskočit", "skip_loading", size=13, slant=False)


def _mini_train(surface, front_x, rail_y, progress):
    """Malý vláček (lokomotiva + vagon) stojící na kolejnici; přední konec je ve front_x.

    Kreslí se 3× větší do vlastního obrázku a pak se plynule zmenší, aby byl hladký.
    """
    ss = 3
    k = settings.SCALE * ss
    width, height = 84, 16  # logické pixely
    image = pygame.Surface((round(width * k), round(height * k)), pygame.SRCALPHA)

    def rect(x, y, w, h, color):
        pygame.draw.rect(image, color, (x * k, y * k, w * k, h * k))

    # souřadnice v obrázku: přední konec vláčku je vpravo (x = 84), kolejnice dole (y = 16)
    rect(4, 3, 36, 10, (0, 84, 159))        # vagon
    rect(4, 4, 36, 3, (242, 244, 247))      # bílý pruh s okny
    for wx in range(7, 38, 6):
        rect(wx, 4.6, 3, 1.8, (111, 166, 204))
    rect(40, 9, 3, 1.5, (34, 38, 44))       # spřáhlo
    rect(43, 3, 34, 10, (0, 84, 159))       # lokomotiva
    rect(43, 2, 30, 1.2, (42, 108, 181))    # střecha
    pygame.draw.polygon(image, (30, 111, 191), [(77 * k, 3 * k), (83 * k, 8 * k), (83 * k, 13 * k), (77 * k, 13 * k)])  # čelo
    rect(43, 8.5, 40, 1.2, (242, 244, 247))  # bílý pruh
    rect(79, 10, 4, 3, (255, 199, 44))       # žluté čelo dole
    rect(78, 4.5, 3, 3, (191, 228, 255))     # okno stanoviště
    for wx in (48, 54, 60, 66):
        rect(wx, 4.5, 4, 2.5, (191, 228, 255))
    pygame.draw.line(image, (201, 205, 211), (55 * k, 2 * k), (60 * k, 0), max(1, round(k * 0.7)))  # sběrač
    for cx in (9, 15, 29, 35, 47, 53, 67, 73):  # kola
        pygame.draw.circle(image, (34, 38, 44), (cx * k, 14 * k), 1.8 * k)

    image = pygame.transform.smoothscale(image, (round(width * settings.SCALE), round(height * settings.SCALE)))
    left, top = L(front_x - width + 1, rail_y - height)
    surface.blit(image, (left, top))


# ---------- menu ----------

def draw_menu(surface, game):
    """Hlavní menu přes ztmavenou mapu: název a tlačítka Hrát / Ukončit."""
    shade_screen(surface, (8, 24, 48), 140)
    panel(surface, 180, 110, 600, 300, alpha=235, cut=24)
    text(surface, "ČESKÉ DRÁHY · TOWER DEFENCE", 13, (480, 148), LABEL)
    text(surface, "VÝLUKA", 88, (480, 207))
    text(surface, "Ubraň trať před problémy, než dojedou do stanice.", 18, (480, 264), TEXT_DIM)
    button(surface, 328, 306, 150, 48, "Hrát", "start", primary=True, size=20)
    button(surface, 492, 306, 140, 48, "Ukončit", "quit", size=18, slant=False)
    text(surface, "Myš – stavba věží · Mezerník – další vlna · P – pauza · F – zrychlení", 14, (480, 440), TEXT_DIM)


# ---------- hra: horní lišta, panel nad Prahou, výběr věží, stavění ----------

def draw_hud(surface, game):
    """Všechno rozhraní během hry."""
    _draw_build_help(surface, game)
    _draw_popups(surface, game)
    _draw_station_panel(surface, game)
    _draw_top_bar(surface, game)
    _draw_banner(surface, game)
    _draw_picker(surface, game)


def _draw_top_bar(surface, game):
    """Modrá lišta nahoře: rozpočet, zpoždění, vlna a tlačítka."""
    bar = pygame.Rect(0, 0, settings.SCREEN_W, R(0, 0, 0, settings.HUD_HEIGHT).bottom)
    pygame.draw.rect(surface, CD_BLUE, bar)
    # fasety (trojúhelníky ve dvou odstínech) jako v designu – přes celou šířku obrazovky
    step = 48 * settings.SCALE
    i = 0
    x = -step
    while x < settings.SCREEN_W:
        h = bar.h
        if i % 3 == 0:
            pygame.draw.polygon(surface, (10, 98, 179), [(x, 0), (x + step, 0), (x + step / 2, h)])
        if i % 4 == 1:
            pygame.draw.polygon(surface, (0, 74, 140), [(x + step / 2, h), (x + step, 0), (x + step * 1.5, h)])
        x += step
        i += 1
    pygame.draw.rect(surface, settings.CD_BLUE_DARK, (0, bar.bottom - round(3 * settings.SCALE), settings.SCREEN_W, round(3 * settings.SCALE)))

    coin_icon(surface, 16, 15)
    text(surface, "ROZPOČET", 11, (52, 12), LABEL, "topleft")
    text(surface, f"{game.money} Kč", 20, (52, 25), WHITE, "topleft")

    clock_icon(surface, 160, 15)
    text(surface, "ZPOŽDĚNÍ", 11, (196, 12), LABEL, "topleft")
    pygame.draw.rect(surface, settings.CD_BLUE_DARK, R(196, 29, 150, 12))
    pygame.draw.rect(surface, delay_color(game.delay), R(196, 29, 150 * min(1, game.delay / game.max_delay), 12))
    text(surface, f"{min(game.delay, game.max_delay)} / {game.max_delay} min", 16, (356, 35), WHITE, "midleft")

    text(surface, "VLNA", 11, (480, 12), LABEL, "topleft")
    text(surface, f"{game.waves.current} / {game.waves.total}", 20, (480, 25), WHITE, "topleft")

    can_start = game.state == "playing" and not game.wave_in_progress and not game.waves.all_started
    button(surface, 600, 8, 110, 40, "Pokračovat" if game.paused else "Pauza", "pause", size=14, slant=False)
    button(surface, 718, 8, 50, 40, "2×" if game.speed == 1 else "1×", "speed", size=15, slant=False)
    button(surface, 776, 6, 174, 44, "Další vlna", "next_wave", primary=True, enabled=can_start, size=16)


def _draw_banner(surface, game):
    """Nápověda nahoře uprostřed (na začátku hry a při pauze)."""
    if game.paused:
        message = "Pauza"
    elif game.waves.current == 0 and not _tower_tiles(game):
        message = "1) Vyber věž dole   2) Klikni na trávu vedle trati   3) Spusť vlnu"
    elif game.waves.current == 0:
        message = "Až budeš připraven, klikni na „Další vlna“"
    else:
        return
    width = font(14).size(message)[0] / settings.SCALE + 36
    panel(surface, 480 - width / 2, 66, width, 32, alpha=225, cut=8)
    text(surface, message, 14, (480, 82))


def _draw_station_panel(surface, game):
    """Panel nad nádražím Praha hl. n. se zpožděním vlaků (0–60 min)."""
    anchor = _logical(iso.to_screen(16.75, 5.5, 2.6))  # nad věžičkou nádraží
    x, y = anchor[0] - 75, anchor[1] - 90
    panel(surface, x, y, 150, 62, alpha=232, cut=8)
    pygame.draw.polygon(surface, PANEL, [L(anchor[0] - 7, y + 62), L(anchor[0] + 7, y + 62), L(anchor[0], y + 71)])
    text(surface, "Praha hl. n.", 13, (x + 10, y + 7), WHITE, "topleft")
    color = delay_color(game.delay)
    text(surface, f"{min(game.delay, game.max_delay)}/{game.max_delay} min", 12, (x + 140, y + 8), color, "topright")
    pygame.draw.rect(surface, (28, 42, 64), R(x + 10, y + 27, 130, 10))
    pygame.draw.rect(surface, color, R(x + 10, y + 27, 130 * min(1, game.delay / game.max_delay), 10))
    text(surface, "ZPOŽDĚNÍ VLAKŮ", 10, (x + 10, y + 43), (185, 203, 224), "topleft")


def _draw_popups(surface, game):
    """Vyskakující "+10" s mincí nad zničeným nepřítelem a červené "+5 min" u Prahy."""
    for popup in game.popups:
        q = popup["t"] / settings.POPUP_LIFE  # 0 = právě vznikl, 1 = mizí
        alpha = 255 if q < 0.6 else int(255 * (1 - (q - 0.6) / 0.4))
        if popup["coin"]:
            sx, sy = _logical(iso.to_screen(popup["x"], popup["y"], 1.3))
            image = font(18).render(popup["text"], True, (255, 216, 74))
            pos = (sx - 10, sy - 12 - q * 34)
        else:
            anchor = _logical(iso.to_screen(16.75, 5.5, 2.6))
            image = font(17).render(popup["text"], True, (255, 107, 94))
            pos = (anchor[0] - 110, anchor[1] - 70 - q * 28)
        image.set_alpha(alpha)
        rect = image.get_rect(center=L(*pos))
        surface.blit(image, rect)
        if popup["coin"]:
            coin_icon(surface, pos[0] + rect.w / settings.SCALE / 2 + 3, pos[1] - 9, 18)


def _tower_tiles(game):
    """Políčka, na kterých už stojí věž. Věže (towers.py) mají atributy col a row."""
    towers = getattr(game.tower_manager, "towers", []) if game.tower_manager else []
    return {(t.col, t.row) for t in towers if hasattr(t, "col")}


def _draw_build_help(surface, game):
    """Pomoc při stavění: zvýraznění volných míst, políčko pod myší, průhledná věž a dosah.

    Když na vybranou věž máš peníze, místo kurzoru myši se ukazuje průhledná věž.
    Když ne, je vidět normální kurzor (a nic se nezvýrazní).
    """
    if game.state != "playing":
        return
    kind = game.selected_tower
    stats = settings.TOWER_TYPES[kind]
    affordable = game.money >= stats["price"]
    occupied = _tower_tiles(game)
    mouse = pygame.mouse.get_pos()
    over_map = not _over_interface(mouse)
    col, row = iso.to_tile(*mouse)

    # 1) všechna volná místa ke stavbě (přepínačem, nebo když držíš věž nad mapou)
    if _show_spots or (affordable and over_map):
        surface.blit(_spots_layer(occupied), (0, 0))

    if not over_map:
        return
    # 2) myš nad postavenou věží: ukaž její dosah
    if (col, row) in occupied:
        tower = next(t for t in game.tower_manager.towers if (t.col, t.row) == (col, row))
        _range_ellipse(surface, col + 0.5, row + 0.5, settings.TOWER_TYPES[tower.kind]["range"], tower.kind == "dispatcher")
        return
    if not affordable:
        return
    # 3) "duch" věže pod myší místo kurzoru
    pygame.mouse.set_visible(False)
    ok = track.can_build(col, row)
    tile = [iso.to_screen(col, row), iso.to_screen(col + 1, row), iso.to_screen(col + 1, row + 1), iso.to_screen(col, row + 1)]
    # průhlednou plochu kreslíme do malého obrázku jen o velikosti políčka (rychlejší než přes celou obrazovku)
    box = pygame.Rect(min(p[0] for p in tile) - 2, min(p[1] for p in tile) - 2, 0, 0)
    box.width = round(max(p[0] for p in tile) - box.x + 4)
    box.height = round(max(p[1] for p in tile) - box.y + 4)
    local = [(p[0] - box.x, p[1] - box.y) for p in tile]
    layer = pygame.Surface(box.size, pygame.SRCALPHA)
    pygame.draw.polygon(layer, (255, 255, 255, 90) if ok else (224, 52, 47, 100), local)
    pygame.draw.polygon(layer, (255, 255, 255, 230) if ok else (224, 52, 47, 230), local, max(1, round(2 * settings.SCALE)))
    surface.blit(layer, box)
    if ok:
        _range_ellipse(surface, col + 0.5, row + 0.5, stats["range"], kind == "dispatcher")
    _ghost(surface, kind, col + 0.5, row + 0.5, 200 if ok else 90, game.time)


def _spots_layer(occupied):
    """Průhledná vrstva se zvýrazněnými volnými políčky. Počítá se znovu jen při změně."""
    key = (frozenset(occupied), settings.SCREEN_W, settings.SCREEN_H)
    if _spots_cache["key"] != key:
        layer = pygame.Surface((settings.SCREEN_W, settings.SCREEN_H), pygame.SRCALPHA)
        for col, row in world.BUILDABLE - occupied:
            pts = [iso.to_screen(col + 0.1, row + 0.1), iso.to_screen(col + 0.9, row + 0.1),
                   iso.to_screen(col + 0.9, row + 0.9), iso.to_screen(col + 0.1, row + 0.9)]
            pygame.draw.polygon(layer, (255, 255, 255, 42), pts)
            pygame.draw.polygon(layer, (255, 255, 255, 150), pts, 1)
        _spots_cache["key"], _spots_cache["image"] = key, layer
    return _spots_cache["image"]


def _range_ellipse(surface, x, y, radius, blue=False):
    """Dosah věže: kruh na zemi, který se kamerou zploští na elipsu."""
    width = radius * 2 * settings.TILE * settings.SCALE
    height = width * settings.SIN_PITCH  # sklon kamery zkrátí hloubku
    rect = pygame.Rect(0, 0, round(width), round(height))
    rect.center = iso.to_screen(x, y)
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    fill, line = ((127, 184, 255, 40), (140, 195, 255, 240)) if blue else ((255, 255, 255, 30), (255, 255, 255, 230))
    pygame.draw.ellipse(layer, fill, layer.get_rect())
    pygame.draw.ellipse(layer, line, layer.get_rect(), max(1, round(2 * settings.SCALE)))
    surface.blit(layer, rect)


def _ghost(surface, kind, x, y, alpha, phase):
    """Průhledná věž na políčku pod myší (ukazuje, kam se postaví)."""
    size = 54
    side = round(iso.px(size) * 1.5)
    layer = pygame.Surface((side, side), pygame.SRCALPHA)
    # věž stojí podstavcem na středu políčka (podstavec je 16/60 velikosti pod středem postavičky)
    sprites.draw_sprite(layer, kind, (side / 2, side / 2), size, phase=phase)
    layer.set_alpha(alpha)
    sx, sy = iso.to_screen(x, y)
    surface.blit(layer, (sx - side / 2, sy - iso.px(size) * 16 / 60 - side / 2))


def _draw_picker(surface, game):
    """Panel vlevo dole: tři karty věží (obrázek, název, cena) a přepínač míst ke stavbě."""
    x, y, w, h = settings.PICKER_RECT
    panel(surface, x, y, w, h, alpha=228, cut=12)
    text(surface, "Vyber věž a klikni vedle trati", 12, (x + 12, y + 14), LABEL, "midleft")
    button(surface, x + w - 128, y + 5, 118, 20, f"Místa ke stavbě: {'ZAP' if _show_spots else 'VYP'}",
           "toggle_spots", size=10, slant=False)

    for i, kind in enumerate(settings.TOWER_ORDER):
        stats = settings.TOWER_TYPES[kind]
        cx, cy, cw, ch = x + 12 + i * 112, y + 32, 104, 70
        card = R(cx, cy, cw, ch)
        selected = game.selected_tower == kind
        layer = pygame.Surface(card.size, pygame.SRCALPHA)
        layer.fill((255, 176, 32, 56) if selected else (255, 255, 255, 16))
        surface.blit(layer, card)
        pygame.draw.rect(surface, YELLOW if selected else (70, 84, 104), card, max(1, round(2 * settings.SCALE)))
        icon_center = L(cx + cw / 2, cy + 22)
        sprites.draw_sprite(surface, kind, icon_center, 34, phase=game.time if selected else 0.0)
        text(surface, stats["name"], 11, (cx + cw / 2, cy + 47))
        text(surface, f"{stats['price']} Kč", 13, (cx + cw / 2, cy + 60), (255, 210, 122))
        if game.money < stats["price"]:  # na tuhle věž zatím nemáš: ztmavit kartu
            dim = pygame.Surface(card.size, pygame.SRCALPHA)
            dim.fill((10, 24, 44, 130))
            surface.blit(dim, card)
        _buttons.append((card, f"select:{kind}"))


# ---------- konec hry ----------

def draw_end_screen(surface, game):
    """Výhra / prohra: nadpis, statistika a tlačítka Hrát znovu / Hlavní menu."""
    won = game.state == "won"
    shade_screen(surface, (6, 14, 28) if won else (28, 6, 6), 150)
    panel(surface, 240, 150, 480, 250, alpha=242, cut=24)
    if won:
        text(surface, "Vlaky jedou včas!", 42, (480, 200), (95, 208, 122))
        lines = [f"Přežil jsi všech {game.waves.total} vln.", f"Odstraněno problémů: {game.kills}, zpoždění {game.delay} min."]
    else:
        text(surface, "Cestující to vzdali", 42, (480, 200), (255, 107, 94))
        lines = [f"Zpoždění dosáhlo {game.max_delay} minut ve vlně {game.waves.current}.", f"Odstraněno problémů: {game.kills}."]
    for i, line in enumerate(lines):
        text(surface, line, 16, (480, 250 + i * 24), TEXT_DIM)
    button(surface, 304, 322, 170, 46, "Hrát znovu", "restart", primary=True, size=18)
    button(surface, 486, 322, 170, 46, "Hlavní menu", "menu", size=17, slant=False)
