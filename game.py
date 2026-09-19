import pygame

from arrow import Arrow, is_path_clear
from levels import LEVELS
from ui import (
    Button,
    draw_game_screen,
    draw_start_screen,
    get_grid_position,
)


START = "start"
PLAYING = "playing"


class Game:
    """管理游戏状态、事件和界面绘制。"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = START

        self.level_index = 0
        self.arrows = []
        self.mistakes_left = 0

        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None

        window_width, _ = self.screen.get_size()

        self.start_button = Button(
            x=window_width // 2 - 120,
            y=505,
            width=240,
            height=65,
            text="开始游戏",
        )

        self.back_button = Button(
            x=35,
            y=625,
            width=160,
            height=50,
            text="返回首页",
            font_size=22,
        )

        self.load_level(0)

    def load_level(self, level_index):
        """根据初始数据重新创建当前关卡。"""
        level = LEVELS[level_index]

        self.level_index = level_index
        self.mistakes_left = level["max_mistakes"]

        self.arrows = [
            Arrow(row, col, direction)
            for row, col, direction in level["arrows"]
        ]

        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None

    def find_arrow(self, row, col):
        """查找指定格子中的箭头。"""
        for arrow in self.arrows:
            if arrow.row == row and arrow.col == col:
                return arrow

        return None

    def handle_arrow_click(self, arrow):
        """处理玩家点击箭头后的结果。"""
        level = LEVELS[self.level_index]

        path_clear = is_path_clear(
            arrow=arrow,
            arrows=self.arrows,
            rows=level["rows"],
            cols=level["cols"],
        )

        if path_clear:
            self.arrows.remove(arrow)
            self.blocked_arrow = None
            self.feedback_message = "路径畅通，箭头成功飞出！"
        else:
            self.mistakes_left -= 1
            self.blocked_arrow = arrow
            self.feedback_message = "前方有其他箭头阻挡！"

        # 反馈显示 800 毫秒
        self.feedback_end_time = pygame.time.get_ticks() + 800

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

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        mouse_position = event.pos

        if self.state == START:
            if self.start_button.contains(mouse_position):
                self.load_level(0)
                self.state = PLAYING

        elif self.state == PLAYING:
            if self.back_button.contains(mouse_position):
                self.state = START
                return

            level = LEVELS[self.level_index]

            grid_position = get_grid_position(
                mouse_position,
                level["rows"],
                level["cols"],
            )

            # 点击棋盘外或空格时不进行处理
            if grid_position is None:
                return

            row, col = grid_position
            arrow = self.find_arrow(row, col)

            if arrow is not None:
                self.handle_arrow_click(arrow)

    def update(self):
        """更新反馈信息的显示时间。"""
        current_time = pygame.time.get_ticks()

        if (
            self.feedback_end_time > 0
            and current_time >= self.feedback_end_time
        ):
            self.feedback_message = ""
            self.feedback_end_time = 0
            self.blocked_arrow = None

    def draw(self):
        """根据当前状态绘制对应界面。"""
        if self.state == START:
            draw_start_screen(
                self.screen,
                self.start_button,
            )

        elif self.state == PLAYING:
            level = LEVELS[self.level_index]

            draw_game_screen(
                screen=self.screen,
                level=level,
                level_number=self.level_index + 1,
                arrows=self.arrows,
                mistakes_left=self.mistakes_left,
                back_button=self.back_button,
                feedback_message=self.feedback_message,
                blocked_arrow=self.blocked_arrow,
            )

        pygame.display.flip()

    def run(self):
        """运行游戏主循环。"""
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw()
            self.clock.tick(60)