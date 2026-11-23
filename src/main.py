"""Spuštění hry: okno, hlavní smyčka (události -> logika -> kreslení).

Hra běží přes celou obrazovku v jejím skutečném rozlišení. Pro ladění jde
spustit v okně 960 × 640:  python src/main.py --okno
"""

import sys

import pygame

import settings
import ui


def make_windows_sharp():
    """Řekne Windows, že si hra kreslí ostře sama.

    Bez toho Windows při zvětšení zobrazení (např. 125 % nebo 150 % na
    noteboocích) okno hry samy roztáhnou a obraz je rozmazaný a "pixelatý".
    Na jiných systémech se nic nestane.
    """
    if sys.platform != "win32":
        return
    import ctypes

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Windows 8.1 a novější
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # starší Windows
        except Exception:
            pass


def open_screen(windowed):
    """Otevře okno (přes celou obrazovku nebo 960 × 640) a nastaví zvětšení.

    Celá hra je navržená pro logickou plochu 960 × 640. Tady spočítáme, kolikrát
    ji zvětšit (SCALE), aby se vešla na monitor, a o kolik ji posunout (OFFSET),
    aby byla uprostřed. Mapa se kreslí i do okrajů, takže nevzniknou černé pruhy.
    """
    if windowed:
        screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    else:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # (0, 0) = rozlišení monitoru
    width, height = screen.get_size()
    settings.SCREEN_W, settings.SCREEN_H = width, height
    settings.SCALE = min(width / settings.WIDTH, height / settings.HEIGHT)
    settings.OFFSET_X = round((width - settings.WIDTH * settings.SCALE) / 2)
    settings.OFFSET_Y = round((height - settings.HEIGHT * settings.SCALE) / 2)
    return screen


def main():
    make_windows_sharp()
    pygame.init()
    screen = open_screen(windowed="--okno" in sys.argv)
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    # Moduly s kreslením mapy a věží se načtou až teď, když už známe velikost obrazovky.
    import scenery
    import towers
    from game import Game

    scene = scenery.Scenery()  # mapa se vykreslí jen jednou, tady
    game = Game(towers.TowerManager())

    # Okolní život (projíždějící vlaky, auta, traktor, kouř) je v ambient.py (Matěj).
    # Když soubor ještě neexistuje, hra prostě běží bez něj.
    try:
        import ambient

        life = ambient.Ambient()
    except ImportError:
        life = None
    running = True

    while running:
        # čas od minulého snímku v sekundách; omezený, aby se po zaseknutí
        # (např. přetažení okna) nepřátelé najednou "neteleportovali" o kus dál
        dt = min(clock.tick(settings.FPS) / 1000, 0.05)

        # 1) události (klávesy, myš, zavření okna)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            action = ui.handle_event(event, game)
            if action == "quit":
                running = False
            elif action in ("start", "restart"):
                game.start()
            elif action == "menu":
                game.go_to_menu()
            elif action == "next_wave":
                game.start_next_wave()
            elif action == "pause":
                game.toggle_pause()
            elif action == "speed":
                game.toggle_speed()
            elif action == "skip_loading":
                game.skip_loading()
            elif action is None and game.state == "playing":
                # klik, který nebyl na tlačítko rozhraní, patří věžím (stavění)
                game.tower_manager.handle_event(event, game)

        # 2) logika
        game.update(dt)
        scene.update(dt)
        if life:
            life.update(dt)  # běží pořád (i v menu a při pauze), je to jen dekorace

        # 3) kreslení: mapa je vidět vždy (i za načítáním a menu)
        screen.fill((0, 0, 0))
        scene.draw(screen, game, extra=life.drawables() if life else ())
        if life:
            life.draw_overlay(screen)  # kouř je nad vším ostatním na mapě
        if game.state in ("playing", "won", "lost"):
            game.tower_manager.draw(screen, game)
        ui.draw(screen, game)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
