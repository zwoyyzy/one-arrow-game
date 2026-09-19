"""随机挑战关卡生成器。

生成后会使用与游戏相同的路径规则进行求解验证。只有包含四种方向、
具有足够阻挡关系并且能够完全清除的布局才会交给游戏使用。
"""

import random

from arrow import Arrow, is_path_clear


DIRECTIONS = ("up", "down", "left", "right")


def find_solution(arrows_data, rows, cols):
    """返回一条可通关顺序；无法通关时返回 None。"""
    arrows = [Arrow(*item) for item in arrows_data]
    solution = []

    while arrows:
        safe_arrows = [
            arrow
            for arrow in arrows
            if is_path_clear(arrow, arrows, rows, cols)
        ]

        if not safe_arrows:
            return None

        # 随机选择当前安全箭头，让不同关卡的参考解法也不完全相同。
        arrow = random.choice(safe_arrows)
        solution.append((arrow.row, arrow.col))
        arrows.remove(arrow)

    return solution


def count_initial_blocked(arrows_data, rows, cols):
    """统计初始状态下被其他箭头阻挡的数量。"""
    arrows = [Arrow(*item) for item in arrows_data]
    return sum(
        not is_path_clear(arrow, arrows, rows, cols)
        for arrow in arrows
    )


def generate_random_level():
    """生成一个包含四方向、带阻挡且保证可通关的随机挑战。"""
    size, arrow_count = random.choice(
        ((6, 12), (7, 16), (8, 20))
    )

    positions = [
        (row, col)
        for row in range(size)
        for col in range(size)
    ]

    # 每种方向数量相同，保证四种方向一定出现。
    directions = [
        direction
        for direction in DIRECTIONS
        for _ in range(arrow_count // 4)
    ]

    for _ in range(3000):
        selected_positions = random.sample(positions, arrow_count)
        random.shuffle(directions)
        arrows_data = [
            (row, col, direction)
            for (row, col), direction in zip(
                selected_positions,
                directions,
            )
        ]

        blocked_count = count_initial_blocked(
            arrows_data,
            size,
            size,
        )

        # 至少约三分之一的箭头受到阻挡，才有足够的解谜感。
        if blocked_count < arrow_count // 3:
            continue

        solution = find_solution(
            arrows_data,
            size,
            size,
        )

        if solution is not None:
            return {
                "name": "随机挑战",
                "rows": size,
                "cols": size,
                "max_mistakes": 3,
                "arrows": arrows_data,
                "solution": solution,
            }

    # 极少数情况下连续筛选失败，使用已验证的主线第三关作为安全后备。
    from levels import LEVELS

    fallback = LEVELS[2]
    return {
        "name": "随机挑战",
        "rows": fallback["rows"],
        "cols": fallback["cols"],
        "max_mistakes": 3,
        "arrows": list(fallback["arrows"]),
        "solution": list(fallback["solution"]),
    }
