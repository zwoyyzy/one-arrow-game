from dataclasses import dataclass


VALID_DIRECTIONS = {"up", "down", "left", "right"}


@dataclass
class Arrow:
    """保存一个箭头在棋盘中的位置和方向。"""

    row: int
    col: int
    direction: str

    def __post_init__(self):
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(f"无效的箭头方向：{self.direction}")