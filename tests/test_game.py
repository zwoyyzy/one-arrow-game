"""《一箭又一箭》核心功能自动化测试。

运行方式：
    python -m pytest -v

界面布局、动画观感和声音效果仍需要人工测试；本文件主要验证可以通过
代码稳定判断的游戏规则、关卡数据、计时和存档逻辑。
"""

import os

# 让 Pygame 在没有真实窗口和声卡的测试环境中也能初始化。
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from arrow import Arrow, is_path_clear
from game import GAME_OVER, PLAYING, Game
from levels import LEVELS
from random_levels import DIRECTIONS, generate_random_level
import save_manager


class SilentAudio:
    """测试替身：记录音效调用，但不播放声音。"""

    def __init__(self):
        self.played = []
        self.fly_sfx_on = False

    def play(self, name):
        self.played.append(name)


def make_logic_game(arrows, rows=3, cols=3, mistakes=3):
    """创建不依赖真实窗口、声音和本地存档的轻量 Game 对象。"""
    game = Game.__new__(Game)
    game.current_level = {
        "name": "测试关卡",
        "rows": rows,
        "cols": cols,
        "max_mistakes": 3,
        "arrows": [(a.row, a.col, a.direction) for a in arrows],
        "solution": [],
    }
    game.game_mode = "main"
    game.level_index = 0
    game.arrows = arrows
    game.moves_count = 0
    game.mistakes_left = mistakes
    game.mistakes_used = 0
    game.hinted_arrow = None
    game.blocked_arrow = None
    game.pending_game_over = False
    game.feedback_message = ""
    game.feedback_end_time = 0
    game.audio = SilentAudio()
    game.auto_solving = False
    game.timer_running = False
    game.timer_elapsed_ms = 0
    game.timer_resume_ticks = 0
    game.state = PLAYING

    # 测试过程中不读取、写入或删除玩家的真实存档。
    game.save_progress = lambda: None
    game.clear_saved_progress = lambda: None
    return game


def assert_solution_clears_level(level):
    """按照关卡记录的解法逐步消除，验证所有点击当时均路径畅通。"""
    arrows = [Arrow(*item) for item in level["arrows"]]

    for row, col in level["solution"]:
        arrow = next(
            (item for item in arrows if (item.row, item.col) == (row, col)),
            None,
        )
        assert arrow is not None, f"解法包含不存在或重复的坐标：{row, col}"
        assert is_path_clear(arrow, arrows, level["rows"], level["cols"])
        arrows.remove(arrow)

    assert arrows == []


def test_t01_unblocked_arrow_can_leave_board():
    """T01：点击前方无阻挡的箭头时，路径判定为畅通。"""
    arrow = Arrow(1, 1, "right")
    assert is_path_clear(arrow, [arrow], 3, 3) is True


def test_t02_blocked_arrow_costs_one_mistake():
    """T02：被阻挡的箭头不会飞出，并扣除一次失误机会。"""
    target = Arrow(1, 0, "right")
    blocker = Arrow(1, 2, "up")
    game = make_logic_game([target, blocker])

    game.handle_arrow_click(target)

    assert target.state == "blocked"
    assert target in game.arrows
    assert game.mistakes_left == 2
    assert game.mistakes_used == 1
    assert game.feedback_message == "前方有其他箭头阻挡！"


@pytest.mark.parametrize(
    ("row", "col", "direction"),
    [
        (0, 1, "up"),
        (2, 1, "down"),
        (1, 0, "left"),
        (1, 2, "right"),
    ],
)
def test_t03_edge_arrows_do_not_go_out_of_bounds(row, col, direction):
    """T03：位于四条边且朝外的箭头均可正常离开，不发生越界。"""
    arrow = Arrow(row, col, direction)
    assert is_path_clear(arrow, [arrow], 3, 3) is True


def test_t04_all_main_levels_have_valid_complete_solutions():
    """T04：5个主线关卡都可以按照记录的顺序完全通关。"""
    assert len(LEVELS) == 5
    for level in LEVELS:
        assert_solution_clears_level(level)


def test_t05_three_blocked_clicks_trigger_game_over(monkeypatch):
    """T05：三次失误耗尽后，游戏进入失败状态。"""
    target = Arrow(1, 0, "right")
    blocker = Arrow(1, 2, "up")
    game = make_logic_game([target, blocker])

    for _ in range(3):
        target.state = "idle"
        game.blocked_arrow = None
        game.handle_arrow_click(target)

    assert game.mistakes_left == 0
    assert game.pending_game_over is True

    monkeypatch.setattr(pygame.time, "get_ticks", lambda: 10_000)
    game.feedback_end_time = 1
    game.update_feedback()

    assert game.state == GAME_OVER
    assert game.pending_game_over is False
    assert "fail" in game.audio.played


def test_t06_restart_restores_layout_mistakes_and_counter():
    """T06：重新开始后恢复关卡布局、3次失误机会和计数。"""
    game = Game.__new__(Game)
    game.game_mode = "main"
    game.level_index = 0
    game.current_level = LEVELS[0]
    game.arrows = [Arrow(4, 4, "up")]
    game.mistakes_left = 1
    game.mistakes_used = 2
    game.moves_count = 6
    game.auto_solving = False
    game.timer_elapsed_ms = 5000
    game.timer_resume_ticks = 0
    game.timer_running = False
    game.save_progress = lambda: None

    game.restart_level()

    actual = {(a.row, a.col, a.direction) for a in game.arrows}
    assert actual == set(LEVELS[0]["arrows"])
    assert game.mistakes_left == 3
    assert game.mistakes_used == 0
    assert game.moves_count == 0
    assert game.state == PLAYING


def test_t07_pause_excludes_paused_time(monkeypatch):
    """T07：暂停时保存有效用时，暂停期间不继续累计。"""
    game = Game.__new__(Game)
    game.timer_elapsed_ms = 0
    game.timer_resume_ticks = 0
    game.timer_running = False

    ticks = iter((1000, 3500))
    monkeypatch.setattr(pygame.time, "get_ticks", lambda: next(ticks))

    game.start_level_timer()
    game.pause_level_timer()

    assert game.timer_running is False
    assert game.timer_elapsed_ms == 2500
    assert game.get_elapsed_milliseconds() == 2500


def test_t08_hint_selects_a_safe_arrow():
    """T08：提示功能推荐的箭头在当前局面下一定可以安全飞出。"""
    blocked = Arrow(1, 0, "right")
    safe = Arrow(1, 2, "right")
    game = make_logic_game([blocked, safe])

    game.show_hint()

    assert game.hinted_arrow is not None
    assert is_path_clear(game.hinted_arrow, game.arrows, 3, 3)
    assert "可以安全飞出" in game.feedback_message


def test_t09_save_and_load_unfinished_main_game(tmp_path, monkeypatch):
    """T09：未通关对局可以写入JSON并完整读取。"""
    save_file = tmp_path / "savegame.json"
    monkeypatch.setattr(save_manager, "SAVE_FILE", save_file)

    data = {
        "version": 1,
        "mode": "main",
        "level_index": 2,
        "level": LEVELS[2],
        "remaining_arrows": [[2, 0, "down"], [0, 6, "left"]],
        "mistakes_left": 2,
        "mistakes_used": 1,
        "moves_count": 5,
        "elapsed_ms": 12345,
    }

    save_manager.save_game(data)
    restored = save_manager.load_game()

    # JSON 会将元组序列化为列表，因此比较实际存档字段，而不是直接比较
    # 含有元组的原始 LEVELS 字典。
    assert restored["mode"] == data["mode"]
    assert restored["level_index"] == data["level_index"]
    assert restored["remaining_arrows"] == data["remaining_arrows"]
    assert restored["mistakes_left"] == data["mistakes_left"]
    assert restored["mistakes_used"] == data["mistakes_used"]
    assert restored["moves_count"] == data["moves_count"]
    assert restored["elapsed_ms"] == data["elapsed_ms"]
    assert save_file.exists()


def test_t10_random_level_has_four_directions_and_is_solvable():
    """T10：随机关卡规格正确、四方向齐全并且可以完全通关。"""
    level = generate_random_level()

    assert (level["rows"], len(level["arrows"])) in {
        (6, 12),
        (7, 16),
        (8, 20),
    }
    assert level["rows"] == level["cols"]
    assert {direction for _, _, direction in level["arrows"]} == set(DIRECTIONS)
    assert len({(row, col) for row, col, _ in level["arrows"]}) == len(
        level["arrows"]
    )
    assert_solution_clears_level(level)
