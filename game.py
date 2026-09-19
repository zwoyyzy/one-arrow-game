import pygame

from ui import Button, draw_game_placeholder, draw_start_screen


START = "start"
PLAYING = "playing"


class Game:
    """管理游戏状态、事件和界面绘制。"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = START

        window_width, _ = self.screen.get_size()

        self.start_button = Button(
            x=window_width // 2 - 120,
            y=505,
            width=240,
            height=65,
            text="开始游戏",
        )

        self.back_button = Button(
            x=window_width // 2 - 120,
            y=450,
            width=240,
            height=65,
            text="返回首页",
        )

    def handle_event(self, event):
        """处理键盘和鼠标事件。"""
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == PLAYING:
                    self.state = START
                else:
                    self.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                return

            mouse_position = event.pos

            if self.state == START:
                if self.start_button.contains(mouse_position):
                    self.state = PLAYING

            elif self.state == PLAYING:
                if self.back_button.contains(mouse_position):
                    self.state = START

    def update(self):
        """更新游戏数据，后续将在这里更新动画。"""
        pass

    def draw(self):
        """根据当前状态绘制对应界面。"""
        if self.state == START:
            draw_start_screen(
                self.screen,
                self.start_button,
            )

        elif self.state == PLAYING:
            draw_game_placeholder(
                self.screen,
                self.back_button,
            )

        pygame.display.flip()

    def run(self):
        """运行游戏主循环。"""
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw()

            # 将游戏刷新率限制为每秒 60 帧
            self.clock.tick(60)