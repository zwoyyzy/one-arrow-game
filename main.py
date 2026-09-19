import pygame

from game import Game


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_TITLE = "一箭又一箭"


def main():
    """程序入口。"""
    # 预设为单声道、低延迟音频；必须在 pygame.init() 前调用。
    pygame.mixer.pre_init(44100, -16, 1, 512)
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
