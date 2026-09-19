import pygame

from game import Game


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "一箭又一箭"


def main():
    """程序入口。"""
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
    pygame.display.set_caption(WINDOW_TITLE)

    game = Game(screen)
    game.run()

    pygame.quit()


if __name__ == "__main__":
    main()