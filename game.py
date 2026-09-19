import pygame

from arrow import Arrow, DIRECTION_VECTORS, is_path_clear
from levels import LEVELS
from random_levels import generate_random_level
from ui import (
    Button,
    draw_game_screen,
    draw_level_select_screen,
    draw_pause_overlay,
    draw_result_screen,
    draw_start_screen,
    get_board_geometry,
    get_font,
    get_grid_position,
)


START = "start"
PLAYING = "playing"
LEVEL_CLEAR = "level_clear"
GAME_OVER = "game_over"
ALL_CLEAR = "all_clear"
PAUSED = "paused"
LEVEL_SELECT = "level_select"

FLYING_SPEED = 700


class Game:
    """管理游戏状态、鼠标事件、动画和关卡流程。"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = START

        self.level_index = 0
        self.game_mode = "main"
        self.current_level = LEVELS[0]
        self.random_level = None
        self.arrows = []
        self.mistakes_left = 0

        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.level_start_time = 0
        self.mistakes_used = 0
        self.result_time_seconds = 0
        self.moves_count = 0
        self.auto_solving = False
        self.auto_solve_next_time = 0

        window_width, _ = self.screen.get_size()

        self.start_button = Button(
            x=window_width // 2 - 120,
            y=450,
            width=240,
            height=58,
            text="主线关卡",
            font_size=22,
        )

        self.back_button = Button(
            x=30,
            y=635,
            width=130,
            height=42,
            text="返回首页",
            font_size=18,
            outline=True,
        )

        self.restart_button = Button(
            x=660,
            y=36,
            width=92,
            height=46,
            text="重置",
            font_size=16,
            outline=True,
        )

        self.pause_button = Button(
            x=768,
            y=36,
            width=92,
            height=46,
            text="暂停",
            font_size=16,
            outline=True,
        )

        self.hint_button = Button(
            x=740,
            y=602,
            width=130,
            height=36,
            text="提示",
            font_size=16,
            outline=True,
        )

        self.auto_solve_button = Button(
            x=740,
            y=647,
            width=130,
            height=36,
            text="AI 自动求解",
            font_size=14,
            outline=True,
        )

        self.resume_button = Button(
            x=window_width // 2 - 120,
            y=380,
            width=240,
            height=58,
            text="继续游戏",
            font_size=22,
        )

        self.level_select_button = Button(
            x=window_width // 2 - 120,
            y=522,
            width=240,
            height=58,
            text="关卡选择",
            font_size=22,
            outline=True,
        )

        self.random_mode_button = Button(
            x=window_width // 2 - 120,
            y=594,
            width=240,
            height=58,
            text="随机挑战",
            font_size=22,
            outline=True,
        )

        self.level_buttons = []
        for index in range(len(LEVELS)):
            col = index % 3
            row = index // 3
            self.level_buttons.append(
                Button(
                    x=170 + col * 190,
                    y=225 + row * 110,
                    width=160,
                    height=72,
                    text=f"LEVEL {index + 1:02d}",
                    font_size=20,
                    outline=True,
                )
            )

        self.select_back_button = Button(
            x=window_width // 2 - 100,
            y=545,
            width=200,
            height=54,
            text="返回首页",
            font_size=20,
            outline=True,
        )

        self.retry_button = Button(
            x=window_width // 2 - 120,
            y=390,
            width=240,
            height=60,
            text="重新挑战",
            font_size=25,
        )

        self.clear_replay_button = Button(
            x=285,
            y=395,
            width=150,
            height=58,
            text="重玩本关",
            font_size=20,
            outline=True,
        )

        self.next_button = Button(
            x=465,
            y=395,
            width=150,
            height=58,
            text="下一关",
            font_size=20,
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

        self.game_mode = "main"
        self.current_level = level
        self.level_index = level_index
        self.mistakes_left = level["max_mistakes"]

        self.arrows = []

        for row, col, direction in level["arrows"]:
            arrow = Arrow(row, col, direction)

            # 保存棋盘大小，供 UI 绘制使用
            arrow.board_rows = level["rows"]
            arrow.board_cols = level["cols"]
            arrow.opacity = 0

            self.arrows.append(arrow)

        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.level_start_time = pygame.time.get_ticks()
        self.mistakes_used = 0
        self.result_time_seconds = 0
        self.moves_count = 0
        self.stop_auto_solve()

    def load_random_level(self, create_new=True):
        """载入随机挑战；点击重置时复用当前题目。"""
        if create_new or self.random_level is None:
            self.random_level = generate_random_level()

        level = self.random_level
        self.game_mode = "random"
        self.current_level = level
        self.level_index = 0
        self.mistakes_left = 3
        self.arrows = []

        for row, col, direction in level["arrows"]:
            arrow = Arrow(row, col, direction)
            arrow.board_rows = level["rows"]
            arrow.board_cols = level["cols"]
            arrow.opacity = 0
            self.arrows.append(arrow)

        self.feedback_message = "随机挑战已生成！"
        self.feedback_end_time = pygame.time.get_ticks() + 1200
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.level_start_time = pygame.time.get_ticks()
        self.mistakes_used = 0
        self.result_time_seconds = 0
        self.moves_count = 0
        self.stop_auto_solve()

    def restart_level(self):
        """重新开始当前关卡。"""
        if self.game_mode == "random":
            self.load_random_level(create_new=False)
        else:
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

    def start_random_game(self):
        """生成并开始一局新的随机挑战。"""
        self.load_random_level(create_new=True)
        self.state = PLAYING

    def get_level(self):
        """取得当前模式正在使用的关卡。"""
        return self.current_level

    def stop_auto_solve(self):
        """停止 AI 自动求解并恢复按钮文字。"""
        self.auto_solving = False
        self.auto_solve_next_time = 0
        if hasattr(self, "auto_solve_button"):
            self.auto_solve_button.text = "AI 自动求解"
            self.auto_solve_button.font = get_font(14, True)

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

    def show_hint(self):
        """高亮一个当前可以安全飞出棋盘的箭头。"""
        level = self.get_level()
        safe_arrows = [
            arrow
            for arrow in self.arrows
            if arrow.state == "idle"
            and is_path_clear(
                arrow,
                self.arrows,
                level["rows"],
                level["cols"],
            )
        ]

        if not safe_arrows:
            self.hinted_arrow = None
            self.feedback_message = "暂时没有可提示的箭头"
        else:
            # 连续点击提示时轮换推荐，避免总是指向同一个箭头。
            if self.hinted_arrow in safe_arrows:
                index = (safe_arrows.index(self.hinted_arrow) + 1) % len(safe_arrows)
            else:
                index = 0
            self.hinted_arrow = safe_arrows[index]
            self.feedback_message = "紫色高亮的箭头可以安全飞出！"

        self.feedback_end_time = pygame.time.get_ticks() + 1800

    def is_input_locked(self):
        """动画或碰撞反馈期间禁止再次点击箭头。"""
        if any(
            arrow.state == "flying"
            for arrow in self.arrows
        ):
            return True

        return self.blocked_arrow is not None

    def toggle_auto_solve(self):
        """启动或停止 AI 逐步自动求解。"""
        if self.auto_solving:
            self.stop_auto_solve()
            self.feedback_message = "已停止自动求解"
        else:
            self.auto_solving = True
            self.hinted_arrow = None
            self.auto_solve_next_time = pygame.time.get_ticks()
            self.auto_solve_button.text = "停止自动求解"
            self.auto_solve_button.font = get_font(13, True)
            self.feedback_message = "AI 正在分析并逐步求解……"

        self.feedback_end_time = pygame.time.get_ticks() + 1200

    def update_auto_solve(self):
        """动画结束后自动点击一个路径畅通的箭头。"""
        if not self.auto_solving or self.is_input_locked() or not self.arrows:
            return

        now = pygame.time.get_ticks()
        if now < self.auto_solve_next_time:
            return

        level = self.get_level()
        safe_arrow = next(
            (
                arrow
                for arrow in self.arrows
                if arrow.state == "idle"
                and is_path_clear(
                    arrow,
                    self.arrows,
                    level["rows"],
                    level["cols"],
                )
            ),
            None,
        )

        if safe_arrow is None:
            self.stop_auto_solve()
            self.feedback_message = "AI 未找到安全路径"
            self.feedback_end_time = now + 1200
            return

        self.handle_arrow_click(safe_arrow)
        self.auto_solve_next_time = now + 520

    def handle_arrow_click(self, arrow):
        """处理玩家点击箭头后的结果。"""
        level = self.get_level()
        self.moves_count += 1
        self.hinted_arrow = None

        path_clear = is_path_clear(
            arrow=arrow,
            arrows=self.arrows,
            rows=level["rows"],
            cols=level["cols"],
        )

        if path_clear:
            arrow.state = "flying"
            arrow.flight_distance = 0
            arrow.flight_start = pygame.time.get_ticks()
            arrow.offset_x = 0
            arrow.offset_y = 0

            self.blocked_arrow = None
            self.feedback_message = "路径畅通，箭头正在飞出！"
            self.feedback_end_time = (
                pygame.time.get_ticks() + 700
            )

        else:
            arrow.state = "blocked"
            arrow.collision_start = pygame.time.get_ticks()
            self.blocked_arrow = arrow

            self.mistakes_left -= 1
            self.mistakes_used += 1
            self.feedback_message = "前方有其他箭头阻挡！"
            self.feedback_end_time = (
                pygame.time.get_ticks() + 300
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
        level = self.get_level()
        finished_arrows = []

        _, _, actual_cell_size = get_board_geometry(
            self.screen,
            level["rows"],
            level["cols"],
        )

        for arrow in self.arrows:
            if arrow.state != "flying":
                continue

            row_step, col_step = DIRECTION_VECTORS[
                arrow.direction
            ]

            target_distance = (
                self.get_flight_target_distance(
                    arrow,
                    level["rows"],
                    level["cols"],
                    actual_cell_size,
                )
            )
            arrow.flight_target = target_distance

            # 0.42 秒的三次缓出动画，先快后慢地飞离棋盘。
            elapsed = pygame.time.get_ticks() - arrow.flight_start
            # 先用 0.05 秒蓄力微缩，再在 0.37 秒内高速弹射。
            progress = 0.0 if elapsed < 50 else min(1.0, (elapsed - 50) / 370)
            eased = 1 - (1 - progress) ** 3
            arrow.flight_distance = target_distance * eased
            arrow.offset_x = col_step * arrow.flight_distance
            arrow.offset_y = row_step * arrow.flight_distance

            if progress >= 1.0:
                finished_arrows.append(arrow)

        for arrow in finished_arrows:
            self.arrows.remove(arrow)

        if finished_arrows and not self.arrows:
            self.stop_auto_solve()
            self.feedback_message = ""
            self.result_time_seconds = max(
                1,
                (pygame.time.get_ticks() - self.level_start_time) // 1000,
            )

            if self.game_mode == "random":
                self.state = ALL_CLEAR
            elif self.level_index == len(LEVELS) - 1:
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

            elif event.key == pygame.K_p and self.state in {PLAYING, PAUSED}:
                self.state = PLAYING if self.state == PAUSED else PAUSED

            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        mouse_position = event.pos

        if self.state == START:
            if self.start_button.contains(mouse_position):
                self.start_new_game()

            elif self.level_select_button.contains(mouse_position):
                self.state = LEVEL_SELECT

            elif self.random_mode_button.contains(mouse_position):
                self.start_random_game()

        elif self.state == LEVEL_SELECT:
            if self.select_back_button.contains(mouse_position):
                self.state = START
                return
            for index, button in enumerate(self.level_buttons):
                if button.contains(mouse_position):
                    self.load_level(index)
                    self.state = PLAYING
                    return

        elif self.state == PLAYING:
            if self.back_button.contains(mouse_position):
                self.state = START
                return

            if self.restart_button.contains(mouse_position):
                self.restart_level()
                return

            if self.pause_button.contains(mouse_position):
                self.state = PAUSED
                return

            if self.hint_button.contains(mouse_position):
                if not self.is_input_locked():
                    self.show_hint()
                return

            if self.auto_solve_button.contains(mouse_position):
                self.toggle_auto_solve()
                return

            if self.is_input_locked():
                return

            level = self.get_level()

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

            elif self.clear_replay_button.contains(mouse_position):
                self.restart_level()

            elif self.home_button.contains(mouse_position):
                self.state = START

        elif self.state == GAME_OVER:
            if self.retry_button.contains(mouse_position):
                self.restart_level()

            elif self.home_button.contains(mouse_position):
                self.state = START

        elif self.state == ALL_CLEAR:
            if self.all_restart_button.contains(mouse_position):
                if self.game_mode == "random":
                    self.start_random_game()
                else:
                    self.start_new_game()

            elif self.home_button.contains(mouse_position):
                self.state = START

        elif self.state == PAUSED:
            if self.resume_button.contains(mouse_position):
                self.state = PLAYING
            elif self.pause_button.contains(mouse_position):
                self.state = PLAYING
            elif self.back_button.contains(mouse_position):
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
        self.update_auto_solve()

        # 关卡载入或重置后，箭头平滑淡入。
        for arrow in self.arrows:
            if arrow.opacity < 255:
                arrow.opacity = min(255, arrow.opacity + int(700 * delta_time))

    def draw(self):
        """根据当前状态绘制界面。"""
        if self.state == START:
            draw_start_screen(
                self.screen,
                self.start_button,
                self.level_select_button,
                self.random_mode_button,
            )

        elif self.state == LEVEL_SELECT:
            draw_level_select_screen(
                self.screen,
                self.level_buttons,
                self.select_back_button,
            )

        elif self.state == PLAYING:
            level = self.get_level()

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
                pause_button=self.pause_button,
                hint_button=self.hint_button,
                auto_solve_button=self.auto_solve_button,
                hinted_arrow=self.hinted_arrow,
                mode_text=("随机挑战" if self.game_mode == "random" else "主线关卡"),
            )

        elif self.state == LEVEL_CLEAR:
            level = self.get_level()
            draw_game_screen(
                self.screen, level, self.level_index + 1,
                self.arrows, self.mistakes_left,
                self.back_button, self.restart_button,
                "", None, self.pause_button,
            )
            draw_result_screen(
                screen=self.screen,
                title=f"第 {self.level_index + 1} 关通关",
                message="恭喜你完成本关，准备挑战下一关！",
                title_color=(45, 150, 90),
                primary_button=self.next_button,
                home_button=self.home_button,
                stats_text=f"步数 {self.moves_count}  ·  用时 {self.result_time_seconds} 秒",
                secondary_button=self.clear_replay_button,
            )

        elif self.state == GAME_OVER:
            level = self.get_level()
            draw_game_screen(
                self.screen, level, self.level_index + 1,
                self.arrows, self.mistakes_left,
                self.back_button, self.restart_button,
                "", None, self.pause_button,
            )
            draw_result_screen(
                screen=self.screen,
                title="挑战失败",
                message="失误机会已经用完，请重新尝试本关。",
                title_color=(205, 65, 65),
                primary_button=self.retry_button,
                home_button=self.home_button,
                stats_text=f"步数 {self.moves_count}  ·  失误 {self.mistakes_used} 次",
            )

        elif self.state == ALL_CLEAR:
            level = self.get_level()
            draw_game_screen(
                self.screen, level, self.level_index + 1,
                self.arrows, self.mistakes_left,
                self.back_button, self.restart_button,
                "", None, self.pause_button,
            )
            draw_result_screen(
                screen=self.screen,
                title=("随机挑战通关" if self.game_mode == "random" else "全部通关"),
                message=(
                    "恭喜你完成了本次随机挑战！"
                    if self.game_mode == "random"
                    else f"恭喜你完成了全部 {len(LEVELS)} 个关卡！"
                ),
                title_color=(45, 150, 90),
                primary_button=self.all_restart_button,
                home_button=self.home_button,
                stats_text=f"步数 {self.moves_count}  ·  用时 {self.result_time_seconds} 秒",
            )

        elif self.state == PAUSED:
            level = self.get_level()
            draw_game_screen(
                screen=self.screen,
                level=level,
                level_number=self.level_index + 1,
                arrows=self.arrows,
                mistakes_left=self.mistakes_left,
                back_button=self.back_button,
                restart_button=self.restart_button,
                feedback_message="游戏已暂停",
                blocked_arrow=None,
                pause_button=self.pause_button,
            )
            draw_pause_overlay(self.screen, self.resume_button)

        pygame.display.flip()

    def run(self):
        """运行游戏主循环。"""
        while self.running:
            delta_time = self.clock.tick(60) / 1000

            for event in pygame.event.get():
                self.handle_event(event)

            self.update(delta_time)
            self.draw()
