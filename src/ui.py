"""Menu, horní lišta a obrazovka konce hry.

ZÁKLADNÍ VERZE, aby šla hra spustit. Matěj ji předělá (tlačítka, vzhled,
výběr věží). main.py volá jen funkce níže, takže stačí zachovat
jejich názvy a parametry.
"""

import pygame

import settings

_font_cache = {}


def _font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.Font(None, size)
    return _font_cache[size]


def _text(surface, text, size, center, color=settings.WHITE):
    image = _font(size).render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def handle_event(event, game):
    """Převede klávesu na akci pro main.py: "start", "restart", "next_wave", "quit" nebo None."""
    if event.type != pygame.KEYDOWN:
        return None
    if event.key == pygame.K_ESCAPE:
        return "quit"
    if game.state == "menu" and event.key == pygame.K_RETURN:
        return "start"
    if game.state in ("won", "lost") and event.key == pygame.K_r:
        return "restart"
    if game.state == "playing" and event.key == pygame.K_SPACE:
        return "next_wave"
    return None


def draw_menu(surface):
    surface.fill(settings.CD_BLUE)
    center_x = settings.WIDTH // 2
    _text(surface, "Zpoždění", 96, (center_x, 220))
    _text(surface, "Ubraň trať před problémy, než dojedou do stanice.", 30, (center_x, 300))
    _text(surface, "Enter = začít    Esc = konec", 30, (center_x, 400))


def draw_hud(surface, game):
    pygame.draw.rect(surface, settings.CD_BLUE, (0, 0, settings.WIDTH, settings.HUD_HEIGHT))
    y = settings.HUD_HEIGHT // 2
    _text(surface, f"Rozpočet: {game.money} Kč", 30, (130, y))
    delay_color = settings.YELLOW if game.delay >= game.max_delay // 2 else settings.WHITE
    _text(surface, f"Zpoždění: {game.delay} / {game.max_delay} min", 30, (400, y), delay_color)
    _text(surface, f"Vlna: {game.waves.current} / {game.waves.total}", 30, (630, y))
    if not game.wave_in_progress:
        _text(surface, "Mezerník = další vlna", 26, (845, y), settings.YELLOW)


def draw_end_screen(surface, game):
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surface.blit(overlay, (0, 0))
    center_x = settings.WIDTH // 2
    if game.state == "won":
        _text(surface, "Vlaky jedou včas!", 72, (center_x, 240), settings.GREEN)
    else:
        _text(surface, "Cestující to vzdali", 72, (center_x, 240), settings.RED)
    _text(surface, f"Odstraněno problémů: {game.kills}    Zpoždění: {game.delay} min", 32, (center_x, 320))
    _text(surface, "R = nová hra    Esc = konec", 30, (center_x, 400))
