import math

import pygame

from audio import AudioManager
from arrow import Arrow, DIRECTION_VECTORS, is_path_clear
from levels import LEVELS
from random_levels import generate_random_level
from save_manager import (
    clear_save,
    load_game,
    load_level_progress,
    save_game,
    save_level_progress,
)
from ui import (
    Button,
    draw_game_screen,
    draw_level_select_screen,
    draw_pause_overlay,
    draw_result_screen,
    draw_sound_settings_overlay,
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
        self.audio = AudioManager()
        self.audio.start_bgm()
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
        self.timer_elapsed_ms = 0
        self.timer_resume_ticks = 0
        self.timer_running = False
        self.mistakes_used = 0
        self.result_time_seconds = 0
        self.initial_arrow_count = 0
        self.reference_time_seconds = 0
        self.star_count = 0
        self.moves_count = 0
        self.auto_solving = False
        self.auto_solve_next_time = 0
        self.saved_progress = load_game()
        self.level_progress = load_level_progress(len(LEVELS))

        # 兼容功能加入前的主线存档：已到达第 N 关，说明之前关卡已经通关。
        if self.saved_progress:
            saved_level_index = max(
                0,
                min(
                    len(LEVELS) - 1,
                    int(self.saved_progress.get("level_index", 0)),
                ),
            )
            progress_changed = False
            for index in range(saved_level_index):
                if not self.level_progress[index]["completed"]:
                    self.level_progress[index]["completed"] = True
                    progress_changed = True
            if progress_changed:
                try:
                    save_level_progress(self.level_progress)
                except OSError:
                    pass

        window_width, _ = self.screen.get_size()

        self.start_button = Button(
            x=150,
            y=565,
            width=180,
            height=54,
            text="主线关卡",
            font_size=20,
        )

        self.music_button = Button(
            x=30,
            y=24,
            width=130,
            height=36,
            text="声音设置",
            font_size=16,
        )
        self.sound_panel_open = False
        self.sound_bgm_button = Button(
            x=300, y=300, width=300, height=54,
            text="背景音乐：开", font_size=19,
        )
        self.sound_fly_button = Button(
            x=300, y=370, width=300, height=54,
            text="箭头飞出：开", font_size=19,
        )
        self.sound_close_button = Button(
            x=350, y=465, width=200, height=52,
            text="完成", font_size=19, outline=True,
        )

        self.continue_button = Button(
            x=window_width // 2 - 230,
            y=455,
            width=460,
            height=82,
            text="继续关卡",
            font_size=23,
        )

        self.back_button = Button(
            x=30,
            y=585,
            width=130,
            height=42,
            text="返回首页",
            font_size=18,
            outline=True,
        )

        self.restart_button = Button(
            x=660,
            y=42,
            width=92,
            height=46,
            text="重置",
            font_size=16,
            outline=True,
        )

        self.pause_button = Button(
            x=768,
            y=42,
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
            x=360,
            y=565,
            width=180,
            height=54,
            text="关卡选择",
            font_size=20,
            outline=True,
        )

        self.random_mode_button = Button(
            x=570,
            y=565,
            width=180,
            height=54,
            text="随机挑战",
            font_size=20,
            outline=True,
        )

        self.level_buttons = []
        for index in range(len(LEVELS)):
            col = index % 3
            row = index // 3
            self.level_buttons.append(
                Button(
                    x=170 + col * 190,
                    y=205 + row * 155,
                    width=160,
                    height=118,
                    text=f"LEVEL {index + 1:02d}",
                    font_size=20,
                    outline=True,
                )
            )

        self.select_back_button = Button(
            x=window_width // 2 - 100,
            y=570,
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

        self.initial_arrow_count = len(self.arrows)
        self.reference_time_seconds = self.get_ai_reference_time()
        self.star_count = 0
        self.feedback_message = ""
        self.feedback_end_time = 0
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.level_start_time = pygame.time.get_ticks()
        self.reset_level_timer()
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

        self.initial_arrow_count = len(self.arrows)
        self.reference_time_seconds = self.get_ai_reference_time()
        self.star_count = 0
        self.feedback_message = "随机挑战已生成！"
        self.feedback_end_time = pygame.time.get_ticks() + 1200
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.level_start_time = pygame.time.get_ticks()
        self.reset_level_timer()
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
        self.start_level_timer()

        # 用明显提示确认重置确实执行了，即使棋盘原本就是初始布局。
        self.feedback_message = "本关已重新开始！"
        self.feedback_end_time = pygame.time.get_ticks() + 1000
        self.save_progress()

    def start_new_game(self):
        """从第一关开始新的游戏。"""
        self.load_level(0)

        self.state = PLAYING
        self.start_level_timer()
        self.save_progress()

    def start_random_game(self):
        """生成并开始一局新的随机挑战。"""
        self.load_random_level(create_new=True)
        self.state = PLAYING
        self.start_level_timer()
        self.save_progress()

    def get_level(self):
        """取得当前模式正在使用的关卡。"""
        return self.current_level

    def update_music_button(self):
        """根据当前页面放置音乐开关，并同步视觉状态。"""
        if self.state in {
            PLAYING,
            PAUSED,
            LEVEL_CLEAR,
            GAME_OVER,
            ALL_CLEAR,
        }:
            # 游戏页左下角竖排：返回首页在上，音乐开关在下。
            self.music_button.rect.topleft = (30, 638)
            self.music_button.rect.size = (130, 36)
        elif self.state == LEVEL_SELECT:
            self.music_button.rect.topleft = (30, 635)
            self.music_button.rect.size = (120, 42)
        else:
            self.music_button.rect.topleft = (30, 24)
            self.music_button.rect.size = (120, 42)

        self.music_button.text = "声音设置"
        # 中文按钮使用稍小的常规字重，避免四个字挤在粗黑边框里。
        self.music_button.font = get_font(16, False)
        self.music_button.outline = False

    def toggle_music(self):
        """只切换背景音乐，不影响游戏操作音效。"""
        self.sound_panel_open = True
        self.update_music_button()

    def update_sound_buttons(self):
        self.sound_bgm_button.text = (
            "背景音乐：开" if self.audio.music_on else "背景音乐：关"
        )
        self.sound_fly_button.text = (
            "箭头飞出：开" if self.audio.fly_sfx_on else "箭头飞出：关"
        )

    def reset_level_timer(self):
        """将当前关卡计时恢复到零并保持停止状态。"""
        self.timer_elapsed_ms = 0
        self.timer_resume_ticks = 0
        self.timer_running = False

    def start_level_timer(self):
        """从当前累计时间开始或继续计时。"""
        if not self.timer_running:
            self.timer_resume_ticks = pygame.time.get_ticks()
            self.timer_running = True

    def pause_level_timer(self):
        """暂停计时并保存已经经过的有效游戏时间。"""
        if self.timer_running:
            self.timer_elapsed_ms += (
                pygame.time.get_ticks() - self.timer_resume_ticks
            )
            self.timer_running = False

    def get_elapsed_seconds(self):
        """返回不包含暂停时段的当前关卡秒数。"""
        elapsed_ms = self.timer_elapsed_ms

        if self.timer_running:
            elapsed_ms += pygame.time.get_ticks() - self.timer_resume_ticks

        return elapsed_ms // 1000

    def get_elapsed_milliseconds(self):
        """返回当前关卡累计的有效游戏毫秒数。"""
        elapsed_ms = self.timer_elapsed_ms

        if self.timer_running:
            elapsed_ms += pygame.time.get_ticks() - self.timer_resume_ticks

        return max(0, elapsed_ms)

    def get_save_data(self):
        """将当前对局转换为 JSON 存档数据。"""
        level = self.get_level()
        return {
            "version": 1,
            "mode": self.game_mode,
            "level_index": self.level_index,
            "level": {
                "name": level["name"],
                "rows": level["rows"],
                "cols": level["cols"],
                "max_mistakes": level["max_mistakes"],
                "arrows": [list(item) for item in level["arrows"]],
                "solution": [list(item) for item in level.get("solution", [])],
            },
            "remaining_arrows": [
                [arrow.row, arrow.col, arrow.direction]
                for arrow in self.arrows
                if arrow.state != "flying"
            ],
            "mistakes_left": self.mistakes_left,
            "mistakes_used": self.mistakes_used,
            "moves_count": self.moves_count,
            "elapsed_ms": self.get_elapsed_milliseconds(),
        }

    def save_progress(self):
        """自动保存尚未结束的当前对局。"""
        if (
            self.game_mode != "main"
            or self.state not in {PLAYING, PAUSED}
            or not self.arrows
        ):
            return
        data = self.get_save_data()
        if not data["remaining_arrows"]:
            return
        try:
            save_game(data)
            self.saved_progress = data
        except OSError:
            pass

    def clear_saved_progress(self):
        """清除已经结束的对局存档。"""
        clear_save()
        self.saved_progress = None

    def continue_saved_game(self):
        """恢复最近一次主线关卡进度。"""
        data = load_game()
        if not data:
            self.saved_progress = None
            return

        try:
            level = data["level"]
            mode = data["mode"]
            if mode != "main":
                raise ValueError("只允许恢复主线关卡存档")
            rows = int(level["rows"])
            cols = int(level["cols"])
            restored_arrows = []
            for row, col, direction in data["remaining_arrows"]:
                row, col = int(row), int(col)
                if not (0 <= row < rows and 0 <= col < cols):
                    raise ValueError("箭头坐标超出棋盘")
                arrow = Arrow(row, col, direction)
                arrow.board_rows = rows
                arrow.board_cols = cols
                arrow.opacity = 255
                restored_arrows.append(arrow)
            if not restored_arrows:
                raise ValueError("存档中没有剩余箭头")

            self.game_mode = mode
            self.level_index = int(data.get("level_index", 0))
            self.current_level = level
            self.random_level = None
            self.arrows = restored_arrows
            self.mistakes_left = max(0, int(data["mistakes_left"]))
            self.mistakes_used = max(0, int(data.get("mistakes_used", 0)))
            self.moves_count = max(0, int(data["moves_count"]))
            self.timer_elapsed_ms = max(0, int(data["elapsed_ms"]))
        except (KeyError, TypeError, ValueError):
            self.clear_saved_progress()
            return

        self.timer_resume_ticks = 0
        self.timer_running = False
        self.initial_arrow_count = len(level["arrows"])
        self.reference_time_seconds = self.get_ai_reference_time()
        self.star_count = 0
        self.result_time_seconds = 0
        self.feedback_message = "已恢复上次游戏进度！"
        self.feedback_end_time = pygame.time.get_ticks() + 1400
        self.blocked_arrow = None
        self.hinted_arrow = None
        self.pending_game_over = False
        self.stop_auto_solve()
        self.state = PLAYING
        self.start_level_timer()
        self.saved_progress = data

    def get_save_summary(self):
        """生成首页继续卡片显示的信息。"""
        data = self.saved_progress
        if not data:
            return None
        level_number = int(data.get("level_index", 0)) + 1
        elapsed = max(0, int(data.get("elapsed_ms", 0))) // 1000
        return {
            "title": (
                f"继续主线 · LEVEL {level_number:02d}"
            ),
            "detail": (
                f"剩余 {len(data.get('remaining_arrows', []))} 支箭头"
                f"  ·  剩余 {data.get('mistakes_left', 0)} 次失误"
                f"  ·  {elapsed // 60:02d}:{elapsed % 60:02d}"
            ),
        }

    def save_next_level_and_return_home(self):
        """通关弹窗返回首页时，把下一主线关卡作为继续入口保存。"""
        next_index = self.level_index + 1

        if next_index >= len(LEVELS):
            self.clear_saved_progress()
            self.state = START
            return

        self.load_level(next_index)
        self.state = PLAYING
        self.start_level_timer()
        self.save_progress()
        self.pause_level_timer()
        self.state = START

    def get_ai_reference_time(self):
        """根据 AI 每步动画耗时计算本关自动求解参考时间。"""
        return max(1, math.ceil(self.initial_arrow_count * 0.52))

    def calculate_star_count(self, elapsed_seconds):
        """按 AI 参考时间将通关成绩划分为一至三星。"""
        reference = self.reference_time_seconds
        three_star_limit = math.ceil(reference * 1.35 + 2)
        two_star_limit = math.ceil(reference * 2.0 + 3)

        if elapsed_seconds <= three_star_limit:
            return 3
        if elapsed_seconds <= two_star_limit:
            return 2
        return 1

    def is_level_unlocked(self, level_index):
        """第一关默认点亮，其余关卡在上一关通关后点亮。"""
        return (
            level_index == 0
            or self.level_progress[level_index - 1]["completed"]
        )

    def record_level_result(self):
        """记录主线关卡的最高星级和最短通关时间。"""
        if self.game_mode != "main":
            return

        record = self.level_progress[self.level_index]
        record["completed"] = True
        record["stars"] = max(record["stars"], self.star_count)

        best_time = record["best_time"]
        if best_time is None or self.result_time_seconds < best_time:
            record["best_time"] = self.result_time_seconds

        try:
            save_level_progress(self.level_progress)
        except OSError:
            pass

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
            # “箭头飞出”开关同时控制成功点击音和飞出音，避免关闭后仍听到前置啵声。
            if self.audio.fly_sfx_on:
                self.audio.play("click")
                self.audio.play("fly")
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
            # 被阻挡时仍保留点击和碰撞反馈，不受飞出音效开关影响。
            self.audio.play("click")
            self.audio.play("block")
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
                if self.game_mode == "main":
                    self.clear_saved_progress()
            else:
                self.save_progress()

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

        if finished_arrows and self.arrows:
            self.save_progress()

        if finished_arrows and not self.arrows:
            if self.game_mode == "main":
                self.clear_saved_progress()
            self.stop_auto_solve()
            self.pause_level_timer()
            self.feedback_message = ""
            self.result_time_seconds = max(
                1,
                self.get_elapsed_seconds(),
            )
            self.star_count = self.calculate_star_count(
                self.result_time_seconds
            )

            if self.game_mode == "main":
                self.record_level_result()

            if self.game_mode == "random":
                self.audio.play("clear")
                self.state = ALL_CLEAR
            elif self.level_index == len(LEVELS) - 1:
                self.audio.play("clear")
                self.state = ALL_CLEAR
            else:
                self.audio.play("clear")
                self.state = LEVEL_CLEAR

    def handle_event(self, event):
        """处理关闭、键盘和鼠标事件。"""
        if event.type == pygame.QUIT:
            self.save_progress()
            self.running = False
            return

        if event.type == pygame.KEYDOWN:
            if self.sound_panel_open and event.key == pygame.K_ESCAPE:
                self.sound_panel_open = False
                return

            if event.key == pygame.K_ESCAPE:
                if self.state == START:
                    self.running = False
                else:
                    if self.state == PLAYING:
                        self.pause_level_timer()
                    self.save_progress()
                    self.state = START

            # 备用测试快捷键：R 键也会重置当前关卡。
            elif event.key == pygame.K_r and self.state == PLAYING:
                self.restart_level()

            elif event.key == pygame.K_p and self.state in {PLAYING, PAUSED}:
                if self.state == PLAYING:
                    self.pause_level_timer()
                    self.state = PAUSED
                    self.save_progress()
                else:
                    self.start_level_timer()
                    self.state = PLAYING

            return

        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        if event.button != 1:
            return

        mouse_position = event.pos

        if self.sound_panel_open:
            if self.sound_bgm_button.contains(mouse_position):
                self.audio.toggle_bgm()
                self.update_sound_buttons()
            elif self.sound_fly_button.contains(mouse_position):
                self.audio.toggle_fly_sfx()
                self.update_sound_buttons()
            elif self.sound_close_button.contains(mouse_position):
                self.sound_panel_open = False
            return

        self.update_music_button()
        if self.music_button.contains(mouse_position):
            self.toggle_music()
            return

        if self.state == START:
            if self.saved_progress and self.continue_button.contains(mouse_position):
                self.continue_saved_game()

            elif self.start_button.contains(mouse_position):
                self.start_new_game()

            elif self.level_select_button.contains(mouse_position):
                self.feedback_message = ""
                self.feedback_end_time = 0
                self.state = LEVEL_SELECT

            elif self.random_mode_button.contains(mouse_position):
                self.start_random_game()

        elif self.state == LEVEL_SELECT:
            if self.select_back_button.contains(mouse_position):
                self.state = START
                return
            for index, button in enumerate(self.level_buttons):
                if button.contains(mouse_position):
                    if not self.is_level_unlocked(index):
                        self.feedback_message = "需通关上一关解锁"
                        self.feedback_end_time = pygame.time.get_ticks() + 1600
                        return
                    self.load_level(index)
                    self.state = PLAYING
                    self.start_level_timer()
                    self.save_progress()
                    return

        elif self.state == PLAYING:
            if self.back_button.contains(mouse_position):
                self.pause_level_timer()
                self.save_progress()
                self.state = START
                return

            if self.restart_button.contains(mouse_position):
                self.restart_level()
                return

            if self.pause_button.contains(mouse_position):
                self.pause_level_timer()
                self.state = PAUSED
                self.save_progress()
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
                self.start_level_timer()
                self.save_progress()

            elif self.clear_replay_button.contains(mouse_position):
                self.restart_level()

            elif self.home_button.contains(mouse_position):
                self.save_next_level_and_return_home()

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
                self.start_level_timer()
                self.state = PLAYING
            elif self.pause_button.contains(mouse_position):
                self.start_level_timer()
                self.state = PLAYING
            elif self.back_button.contains(mouse_position):
                self.save_progress()
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
            self.stop_auto_solve()
            self.pause_level_timer()
            self.audio.play("fail")
            self.state = GAME_OVER
            if self.game_mode == "main":
                self.clear_saved_progress()

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
        self.update_music_button()
        if self.state == START:
            draw_start_screen(
                self.screen,
                self.start_button,
                self.level_select_button,
                self.random_mode_button,
                self.continue_button,
                self.get_save_summary(),
            )

        elif self.state == LEVEL_SELECT:
            draw_level_select_screen(
                self.screen,
                self.level_buttons,
                self.select_back_button,
                self.level_progress,
                (
                    self.feedback_message
                    if pygame.time.get_ticks() < self.feedback_end_time
                    else ""
                ),
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
                timer_seconds=self.get_elapsed_seconds(),
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
                star_count=self.star_count,
                reference_time=self.reference_time_seconds,
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
                star_count=self.star_count,
                reference_time=self.reference_time_seconds,
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
                timer_seconds=self.get_elapsed_seconds(),
            )
            draw_pause_overlay(self.screen, self.resume_button)

        self.music_button.draw(
            self.screen,
            pygame.mouse.get_pos(),
        )

        if self.sound_panel_open:
            self.update_sound_buttons()
            draw_sound_settings_overlay(
                self.screen,
                self.audio,
                self.sound_bgm_button,
                self.sound_fly_button,
                self.sound_close_button,
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
