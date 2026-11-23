"""Spuštění hry: okno, hlavní smyčka (události -> logika -> kreslení)."""

import pygame

import scenery
import settings
import towers
import ui
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.TITLE)
    clock = pygame.time.Clock()

    scene = scenery.Scenery()  # mapa se vykreslí jen jednou, tady
    game = Game(towers.TowerManager())
    running = True

    while running:
        # čas od minulého snímku v sekundách; omezený, aby se po zaseknutí nic "nepřeskočilo"
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
                game.tower_manager.handle_event(event, game)

        # 2) logika
        game.update(dt)
        scene.update(dt)

        # 3) kreslení: mapa je vidět vždy (i za načítáním a menu)
        scene.draw(screen, game)
        if game.state in ("playing", "won", "lost"):
            game.tower_manager.draw(screen, game)
            ui.draw_hud(screen, game)
        if game.state == "loading":
            ui.draw_loading(screen, game)
        elif game.state == "menu":
            ui.draw_menu(screen, game)
        elif game.state in ("won", "lost"):
            ui.draw_end_screen(screen, game)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
