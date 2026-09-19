from dataclasses import dataclass


VALID_DIRECTIONS = {"up", "down", "left", "right"}

DIRECTION_VECTORS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


@dataclass
class Arrow:
    """保存箭头的位置、方向和动画状态。"""

    row: int
    col: int
    direction: str

    state: str = "idle"
    offset_x: float = 0.0
    offset_y: float = 0.0
    flight_distance: float = 0.0
    opacity: int = 255
    collision_start: int = 0
    flight_start: int = 0
    flight_target: float = 0.0

    def __post_init__(self):
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(f"无效的箭头方向：{self.direction}")


def is_path_clear(arrow, arrows, rows, cols):
    """判断箭头前进方向上是否存在其他箭头。"""
    row_step, col_step = DIRECTION_VECTORS[arrow.direction]

    check_row = arrow.row + row_step
    check_col = arrow.col + col_step

    # 正在飞出的箭头不再阻挡其他箭头
    occupied_positions = {
        (other_arrow.row, other_arrow.col)
        for other_arrow in arrows
        if other_arrow is not arrow
        and other_arrow.state != "flying"
    }

    while 0 <= check_row < rows and 0 <= check_col < cols:
        if (check_row, check_col) in occupied_positions:
            return False

        check_row += row_step
        check_col += col_step

    return True
