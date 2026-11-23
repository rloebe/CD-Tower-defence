"""Obrazovky a ovládání: načítání, menu, horní lišta, konec hry.

DOČASNÁ ZÁKLADNÍ VERZE (jen klávesy a text), aby šla hra spustit.
Plná verze podle docs/vizualni-design.md přijde v dalším kroku.
main.py volá jen funkce níže, takže stačí zachovat jejich názvy a parametry.
"""

import pygame

import iso
import settings

_font_cache = {}


def _font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def _text(surface, text, size, center, color=settings.WHITE):
    image = _font(size).render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def _shade(surface, alpha):
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 24, 48, alpha))
    surface.blit(overlay, (0, 0))


def handle_event(event, game):
    """Převede klávesu/klik na akci pro main.py, nebo vrátí None."""
    if game.state == "loading" and event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
        return "skip_loading"
    if event.type != pygame.KEYDOWN:
        return None
    if event.key == pygame.K_ESCAPE:
        return "quit"
    if game.state == "menu" and event.key == pygame.K_RETURN:
        return "start"
    if game.state == "playing":
        if event.key == pygame.K_SPACE:
            return "next_wave"
        if event.key == pygame.K_p:
            return "pause"
        if event.key == pygame.K_f:
            return "speed"
    if game.state in ("won", "lost"):
        if event.key == pygame.K_r:
            return "restart"
        if event.key == pygame.K_m:
            return "menu"
    return None


def draw_loading(surface, game):
    _shade(surface, 160)
    cx = settings.WIDTH // 2
    _text(surface, "VÝLUKA", 120, (cx, 250))
    bar = pygame.Rect(cx - 180, 450, 360, 8)
    pygame.draw.rect(surface, (28, 42, 64), bar)
    pygame.draw.rect(surface, settings.YELLOW, (bar.x, bar.y, int(bar.width * game.load_progress), bar.height))
    _text(surface, f"Načítání… {int(game.load_progress * 100)} %", 26, (cx, 485))


def draw_menu(surface, game):
    _shade(surface, 140)
    cx = settings.WIDTH // 2
    _text(surface, "VÝLUKA", 120, (cx, 230))
    _text(surface, "Ubraň trať před problémy, než dojedou do stanice.", 30, (cx, 310))
    _text(surface, "Enter = hrát    Esc = konec", 30, (cx, 400))


def draw_hud(surface, game):
    pygame.draw.rect(surface, settings.CD_BLUE, (0, 0, settings.WIDTH, settings.HUD_HEIGHT))
    y = settings.HUD_HEIGHT // 2
    _text(surface, f"Rozpočet: {game.money} Kč", 30, (120, y))
    _text(surface, f"Zpoždění: {game.delay} / {game.max_delay} min", 30, (380, y))
    _text(surface, f"Vlna: {game.waves.current} / {game.waves.total}", 30, (600, y))
    hint = "Pauza (P)" if game.paused else ("Mezerník = další vlna" if not game.wave_in_progress else f"{game.speed}× (F)")
    _text(surface, hint, 26, (840, y), settings.YELLOW)
    for popup in game.popups:
        rise = popup["t"] * 30
        if popup["coin"]:
            sx, sy = iso.to_screen(popup["x"], popup["y"], 1.3)
            _text(surface, popup["text"] + " Kč", 26, (sx, sy - rise), settings.YELLOW)
        else:
            _text(surface, popup["text"], 26, (700, 104 - rise), settings.RED)


def draw_end_screen(surface, game):
    _shade(surface, 170)
    cx = settings.WIDTH // 2
    if game.state == "won":
        _text(surface, "Vlaky jedou včas!", 72, (cx, 240), settings.GREEN)
    else:
        _text(surface, "Cestující to vzdali", 72, (cx, 240), settings.RED)
    _text(surface, f"Odstraněno problémů: {game.kills}    Zpoždění: {game.delay} min", 32, (cx, 320))
    _text(surface, "R = hrát znovu    M = menu    Esc = konec", 30, (cx, 400))
