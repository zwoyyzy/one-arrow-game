from pathlib import Path

import pygame


# 界面颜色
BACKGROUND_COLOR = (242, 247, 255)
TITLE_COLOR = (45, 65, 105)
TEXT_COLOR = (75, 85, 105)

BUTTON_COLOR = (92, 138, 255)
BUTTON_HOVER_COLOR = (70, 115, 235)
BUTTON_TEXT_COLOR = (255, 255, 255)

PANEL_COLOR = (255, 255, 255)
BOARD_COLOR = (255, 255, 255)
GRID_COLOR = (194, 207, 230)

ARROW_COLOR = (69, 105, 180)
ARROW_BORDER_COLOR = (40, 66, 125)


# 棋盘位置和格子大小
BOARD_LEFT = 225
BOARD_TOP = 135
CELL_SIZE = 90


def get_font(size, bold=False):
    """读取 Windows 中文字体，避免 Pygame 扫描字体时报错。"""
    fonts_directory = Path(r"C:\Windows\Fonts")

    if bold:
        font_candidates = [
            fonts_directory / "msyhbd.ttc",
            fonts_directory / "simhei.ttf",
            fonts_directory / "simsun.ttc",
        ]
    else:
        font_candidates = [
            fonts_directory / "msyh.ttc",
            fonts_directory / "simhei.ttf",
            fonts_directory / "simsun.ttc",
        ]

    for font_path in font_candidates:
        if font_path.exists():
            font = pygame.font.Font(str(font_path), size)

            if bold and font_path.name != "msyhbd.ttc":
                font.set_bold(True)

            return font

    # 找不到中文字体时使用 Pygame 默认字体
    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font


def draw_centered_text(screen, text, font, color, center):
    """在指定位置居中绘制文字。"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)


class Button:
    """通用按钮类。"""

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font_size=28,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_font(font_size, bold=True)

    def contains(self, mouse_position):
        """判断鼠标是否位于按钮内部。"""
        return self.rect.collidepoint(mouse_position)

    def draw(self, screen, mouse_position):
        """绘制按钮，并在鼠标悬停时改变颜色。"""
        if self.contains(mouse_position):
            color = BUTTON_HOVER_COLOR
        else:
            color = BUTTON_COLOR

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=14,
        )

        pygame.draw.rect(
            screen,
            (255, 255, 255),
            self.rect,
            width=2,
            border_radius=14,
        )

        draw_centered_text(
            screen,
            self.text,
            self.font,
            BUTTON_TEXT_COLOR,
            self.rect.center,
        )


def draw_start_screen(screen, start_button):
    """绘制游戏开始界面。"""
    screen.fill(BACKGROUND_COLOR)

    window_width, _ = screen.get_size()

    title_font = get_font(58, bold=True)
    subtitle_font = get_font(25)
    rule_font = get_font(21)
    tip_font = get_font(17)

    # 游戏标题
    draw_centered_text(
        screen,
        "一箭又一箭",
        title_font,
        TITLE_COLOR,
        (window_width // 2, 150),
    )

    # 副标题
    draw_centered_text(
        screen,
        "观察箭头方向，按照正确顺序清空棋盘",
        subtitle_font,
        TEXT_COLOR,
        (window_width // 2, 220),
    )

    # 玩法说明面板
    panel_rect = pygame.Rect(
        window_width // 2 - 280,
        275,
        560,
        185,
    )

    pygame.draw.rect(
        screen,
        PANEL_COLOR,
        panel_rect,
        border_radius=18,
    )

    pygame.draw.rect(
        screen,
        (210, 222, 245),
        panel_rect,
        width=2,
        border_radius=18,
    )

    rules = [
        "点击一个箭头，程序会检查它前进方向上的路径。",
        "前方没有其他箭头时，箭头可以飞出棋盘。",
        "前方存在阻挡时，将会消耗一次失误机会。",
        "清除本关所有箭头即可进入下一关。",
    ]

    for index, rule in enumerate(rules):
        rule_surface = rule_font.render(
            f"{index + 1}. {rule}",
            True,
            TEXT_COLOR,
        )

        screen.blit(
            rule_surface,
            (
                panel_rect.x + 35,
                panel_rect.y + 25 + index * 38,
            ),
        )

    # 开始游戏按钮
    start_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    # 底部操作提示
    draw_centered_text(
        screen,
        "使用鼠标进行操作",
        tip_font,
        (130, 140, 160),
        (window_width // 2, 625),
    )


def draw_status_bar(
    screen,
    level_number,
    remaining_arrows,
    mistakes_left,
):
    """绘制游戏顶部的状态栏。"""
    label_font = get_font(23, bold=True)

    level_text = label_font.render(
        f"当前关卡：{level_number}",
        True,
        TITLE_COLOR,
    )

    arrow_text = label_font.render(
        f"剩余箭头：{remaining_arrows}",
        True,
        TITLE_COLOR,
    )

    mistake_text = label_font.render(
        f"剩余失误：{mistakes_left}",
        True,
        TITLE_COLOR,
    )

    screen.blit(level_text, (55, 55))
    screen.blit(arrow_text, (350, 55))
    screen.blit(mistake_text, (650, 55))


def draw_board(screen, rows, cols):
    """绘制游戏棋盘和网格。"""
    board_width = cols * CELL_SIZE
    board_height = rows * CELL_SIZE

    board_rect = pygame.Rect(
        BOARD_LEFT,
        BOARD_TOP,
        board_width,
        board_height,
    )

    pygame.draw.rect(
        screen,
        BOARD_COLOR,
        board_rect,
        border_radius=12,
    )

    for row in range(rows):
        for col in range(cols):
            cell_rect = pygame.Rect(
                BOARD_LEFT + col * CELL_SIZE,
                BOARD_TOP + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(
                screen,
                GRID_COLOR,
                cell_rect,
                width=2,
            )

    pygame.draw.rect(
        screen,
        (155, 175, 210),
        board_rect,
        width=3,
        border_radius=12,
    )


def get_arrow_points(center_x, center_y, direction):
    """根据方向计算箭头多边形的顶点。"""
    # 先定义一个朝右的箭头
    points = [
        (-28, -12),
        (4, -12),
        (4, -26),
        (32, 0),
        (4, 26),
        (4, 12),
        (-28, 12),
    ]

    transformed_points = []

    for x, y in points:
        if direction == "right":
            new_x, new_y = x, y

        elif direction == "left":
            new_x, new_y = -x, y

        elif direction == "up":
            new_x, new_y = y, -x

        elif direction == "down":
            new_x, new_y = y, x

        else:
            raise ValueError(
                f"无法绘制箭头方向：{direction}"
            )

        transformed_points.append(
            (
                center_x + new_x,
                center_y + new_y,
            )
        )

    return transformed_points


def draw_arrow(screen, arrow):
    """在箭头所在的网格中绘制箭头。"""
    center_x = (
        BOARD_LEFT
        + arrow.col * CELL_SIZE
        + CELL_SIZE // 2
    )

    center_y = (
        BOARD_TOP
        + arrow.row * CELL_SIZE
        + CELL_SIZE // 2
    )

    points = get_arrow_points(
        center_x,
        center_y,
        arrow.direction,
    )

    pygame.draw.polygon(
        screen,
        ARROW_COLOR,
        points,
    )

    pygame.draw.polygon(
        screen,
        ARROW_BORDER_COLOR,
        points,
        width=3,
    )


def draw_game_screen(
    screen,
    level,
    level_number,
    arrows,
    mistakes_left,
    back_button,
):
    """绘制游戏界面、棋盘和所有箭头。"""
    screen.fill(BACKGROUND_COLOR)

    draw_status_bar(
        screen,
        level_number,
        len(arrows),
        mistakes_left,
    )

    draw_board(
        screen,
        level["rows"],
        level["cols"],
    )

    for arrow in arrows:
        draw_arrow(
            screen,
            arrow,
        )

    back_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    tip_font = get_font(18)

    draw_centered_text(
        screen,
        "当前阶段只绘制棋盘，下一步实现点击与路径判断",
        tip_font,
        TEXT_COLOR,
        (530, 650),
    )