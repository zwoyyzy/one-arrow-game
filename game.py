import pygame

from arrow import Arrow, DIRECTION_VECTORS, is_path_clear
from levels import LEVELS
from ui import (
    Button,
    draw_game_screen,
    draw_result_screen,
    draw_start_screen,
    get_board_geometry,
    get_grid_position,
)


START = "start"
PLAYING = "playing"
LEVEL_CLEAR = "level_clear"
GAME_OVER = "game_over"
ALL_CLEAR = "all_clear"

FLYING_SPEED = 700


class Game:
    """管理游戏状态、鼠标事件、动画和关卡流程。"""

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
        self.pending_game_over = False

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

        self.restart_button = Button(
            x=705,
            y=625,
            width=160,
            height=50,
            text="重新开始",
            font_size=22,
        )

        self.retry_button = Button(
            x=window_width // 2 - 120,
            y=390,
            width=240,
            height=60,
            text="重新挑战",
            font_size=25,
        )

        self.next_button = Button(
            x=window_width // 2 - 120,
            y=390,
            width=240,
            height=60,
            text="下一关",
            font_size=25,
        )

        self.all_restart_button = Button(
            x=window_width // 2 - 120,
            y=390,
            width=240,
            height=60,
            text="重新开始游戏",
            font_size=23,
        )

        self.home_button = Button(
            x=window_width // 2 - 120,
            y=480,
            width=240,
            height=60,
            text="返回首页",
            font_size=25,
        )

        self.load_level(0)

    def load_level(self, level_index):
        """根据关卡初始数据重新创建箭头。"""
        level = LEVELS[level_index]

        self.level_index = level_index
        self.mistakes_left = level["max_mistakes"]

        self.arrows = []

        for row, col, direction in level["arrows"]:
            arrow = Arrow(row, col, direction)

            # 保存棋盘大小，供 UI 绘制使用
            arrow.board_rows = level["rows"]
            arrow.board_cols = level["cols"]

            self.arrows.append(arrow)

        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None
        self.pending_game_over = False

    def restart_level(self):
        """重新开始当前关卡。"""
        current_level = self.level_index
        self.load_level(current_level)
        self.state = PLAYING

        # 用明显提示确认重置确实执行了，即使棋盘原本就是初始布局。
        self.feedback_message = "本关已重新开始！"
        self.feedback_end_time = pygame.time.get_ticks() + 1000

    def start_new_game(self):
        """从第一关开始新的游戏。"""
        self.load_level(0)
        self.state = PLAYING

    def find_arrow(self, row, col):
        """查找指定格子中可以点击的箭头。"""
        for arrow in self.arrows:
            if (
                arrow.row == row
                and arrow.col == col
                and arrow.state == "idle"
            ):
                return arrow

        return None

    def is_input_locked(self):
        """动画或碰撞反馈期间禁止再次点击箭头。"""
        if any(
            arrow.state == "flying"
            for arrow in self.arrows
        ):
            return True

        return self.blocked_arrow is not None

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
            arrow.state = "flying"
            arrow.flight_distance = 0
            arrow.offset_x = 0
            arrow.offset_y = 0

            self.blocked_arrow = None
            self.feedback_message = "路径畅通，箭头正在飞出！"
            self.feedback_end_time = (
                pygame.time.get_ticks() + 700
            )

        else:
            arrow.state = "blocked"
            self.blocked_arrow = arrow

            self.mistakes_left -= 1
            self.feedback_message = "前方有其他箭头阻挡！"
            self.feedback_end_time = (
                pygame.time.get_ticks() + 800
            )

            if self.mistakes_left <= 0:
                self.pending_game_over = True

    def get_flight_target_distance(
        self,
        arrow,
        rows,
        cols,
        cell_size,
    ):
        """计算箭头完全飞出棋盘需要移动的距离。"""
        if arrow.direction == "up":
            return (arrow.row + 1) * cell_size

        if arrow.direction == "down":
            return (rows - arrow.row) * cell_size

        if arrow.direction == "left":
            return (arrow.col + 1) * cell_size

        return (cols - arrow.col) * cell_size

    def update_flying_arrows(self, delta_time):
        """更新箭头飞出动画。"""
        level = LEVELS[self.level_index]
        finished_arrows = []

        _, _, actual_cell_size = get_board_geometry(
            self.screen,
            level["rows"],
            level["cols"],
        )

        for arrow in self.arrows:
            if arrow.state != "flying":
                continue

            arrow.flight_distance += (
                FLYING_SPEED * delta_time
            )

            row_step, col_step = DIRECTION_VECTORS[
                arrow.direction
            ]

            arrow.offset_x = (
                col_step * arrow.flight_distance
            )

            arrow.offset_y = (
                row_step * arrow.flight_distance
            )

            target_distance = (
                self.get_flight_target_distance(
                    arrow,
                    level["rows"],
                    level["cols"],
                    actual_cell_size,
                )
            )

            if arrow.flight_distance >= target_distance:
                finished_arrows.append(arrow)

        for arrow in finished_arrows:
            self.arrows.remove(arrow)

        if finished_arrows and not self.arrows:
            self.feedback_message = ""

            if self.level_index == len(LEVELS) - 1:
                self.state = ALL_CLEAR
            else:
                self.state = LEVEL_CLEAR

    def handle_event(self, event):
        """处理关闭、键盘和鼠标事件。"""
        if event.type == pygame.QUIT:
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == START:
                    self.running = False
                else:
                    self.state = START

            # 备用测试快捷键：R 键也会重置当前关卡。
            elif event.key == pygame.K_r and self.state == PLAYING:
                self.restart_level()

            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        mouse_position = event.pos

        if self.state == START:
            if self.start_button.contains(mouse_position):
                self.start_new_game()

        elif self.state == PLAYING:
            if self.back_button.contains(mouse_position):
                self.state = START
                return

            if self.restart_button.contains(mouse_position):
                self.restart_level()
                return

            if self.is_input_locked():
                return

            level = LEVELS[self.level_index]

            grid_position = get_grid_position(
                self.screen,
                mouse_position,
                level["rows"],
                level["cols"],
            )

            if grid_position is None:
                return

            row, col = grid_position
            arrow = self.find_arrow(row, col)

            if arrow is not None:
                self.handle_arrow_click(arrow)

        elif self.state == LEVEL_CLEAR:
            if self.next_button.contains(mouse_position):
                self.load_level(self.level_index + 1)
                self.state = PLAYING

            elif self.home_button.contains(mouse_position):
                self.state = START

        elif self.state == GAME_OVER:
            if self.retry_button.contains(mouse_position):
                self.restart_level()

            elif self.home_button.contains(mouse_position):
                self.state = START

        elif self.state == ALL_CLEAR:
            if self.all_restart_button.contains(mouse_position):
                self.start_new_game()

            elif self.home_button.contains(mouse_position):
                self.state = START

    def update_feedback(self):
        """更新碰撞提示和失败判断。"""
        if self.feedback_end_time == 0:
            return

        current_time = pygame.time.get_ticks()

        if current_time < self.feedback_end_time:
            return

        self.feedback_message = ""
        self.feedback_end_time = 0

        if self.blocked_arrow is not None:
            self.blocked_arrow.state = "idle"
            self.blocked_arrow = None

        if self.pending_game_over:
            self.pending_game_over = False
            self.state = GAME_OVER

    def update(self, delta_time):
        """更新游戏动画和反馈状态。"""
        if self.state != PLAYING:
            return

        self.update_flying_arrows(delta_time)
        self.update_feedback()

    def draw(self):
        """根据当前状态绘制界面。"""
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
                restart_button=self.restart_button,
                feedback_message=self.feedback_message,
                blocked_arrow=self.blocked_arrow,
            )

        elif self.state == LEVEL_CLEAR:
            draw_result_screen(
                screen=self.screen,
                title=f"第 {self.level_index + 1} 关通关",
                message="恭喜你完成本关，准备挑战下一关！",
                title_color=(45, 150, 90),
                primary_button=self.next_button,
                home_button=self.home_button,
            )

        elif self.state == GAME_OVER:
            draw_result_screen(
                screen=self.screen,
                title="挑战失败",
                message="失误机会已经用完，请重新尝试本关。",
                title_color=(205, 65, 65),
                primary_button=self.retry_button,
                home_button=self.home_button,
            )

        elif self.state == ALL_CLEAR:
            draw_result_screen(
                screen=self.screen,
                title="全部通关",
                message="恭喜你完成了全部三个关卡！",
                title_color=(45, 150, 90),
                primary_button=self.all_restart_button,
                home_button=self.home_button,
            )

        pygame.display.flip()

    def run(self):
        """运行游戏主循环。"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(delta_time)
            self.draw()
