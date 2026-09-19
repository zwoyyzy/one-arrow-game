import math
from pathlib import Path

import pygame


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

BLOCKED_ARROW_COLOR = (225, 76, 76)
BLOCKED_BORDER_COLOR = (150, 40, 40)

BOARD_LEFT = 225
BOARD_TOP = 135
CELL_SIZE = 90


def get_font(size, bold=False):
    """读取 Windows 中文字体。"""
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

    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font


def draw_centered_text(screen, text, font, color, center):
    """在指定位置居中绘制文字。"""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center)
    screen.blit(text_surface, text_rect)


class Button:
    """通用按钮。"""

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
        """绘制按钮。"""
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
    """绘制开始界面。"""
    screen.fill(BACKGROUND_COLOR)

    window_width, _ = screen.get_size()

    title_font = get_font(58, bold=True)
    subtitle_font = get_font(25)
    rule_font = get_font(21)
    tip_font = get_font(17)

    draw_centered_text(
        screen,
        "一箭又一箭",
        title_font,
        TITLE_COLOR,
        (window_width // 2, 150),
    )

    draw_centered_text(
        screen,
        "观察箭头方向，按照正确顺序清空棋盘",
        subtitle_font,
        TEXT_COLOR,
        (window_width // 2, 220),
    )

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

    start_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    draw_centered_text(
        screen,
        "使用鼠标进行操作",
        tip_font,
        (130, 140, 160),
        (window_width // 2, 625),
    )


def get_grid_position(mouse_position, rows, cols):
    """将鼠标坐标转换为棋盘行列坐标。"""
    mouse_x, mouse_y = mouse_position

    board_width = cols * CELL_SIZE
    board_height = rows * CELL_SIZE

    inside_board = (
        BOARD_LEFT <= mouse_x < BOARD_LEFT + board_width
        and BOARD_TOP <= mouse_y < BOARD_TOP + board_height
    )

    if not inside_board:
        return None

    col = (mouse_x - BOARD_LEFT) // CELL_SIZE
    row = (mouse_y - BOARD_TOP) // CELL_SIZE

    return row, col


def draw_status_bar(
    screen,
    level_number,
    remaining_arrows,
    mistakes_left,
):
    """绘制顶部状态栏。"""
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

    mistake_color = (
        (205, 65, 65)
        if mistakes_left <= 1
        else TITLE_COLOR
    )

    mistake_text = label_font.render(
        f"剩余失误：{mistakes_left}",
        True,
        mistake_color,
    )

    screen.blit(level_text, (55, 55))
    screen.blit(arrow_text, (350, 55))
    screen.blit(mistake_text, (650, 55))


def draw_board(screen, rows, cols):
    """绘制棋盘。"""
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
    """根据方向计算箭头多边形顶点。"""
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


def draw_arrow(screen, arrow, blocked=False):
    """绘制箭头、飞行动画和碰撞晃动。"""
    center_x = (
        BOARD_LEFT
        + arrow.col * CELL_SIZE
        + CELL_SIZE // 2
        + arrow.offset_x
    )

    center_y = (
        BOARD_TOP
        + arrow.row * CELL_SIZE
        + CELL_SIZE // 2
        + arrow.offset_y
    )

    if blocked:
        shake = int(
            math.sin(pygame.time.get_ticks() * 0.045) * 7
        )

        if arrow.direction in {"left", "right"}:
            center_x += shake
        else:
            center_y += shake

        fill_color = BLOCKED_ARROW_COLOR
        border_color = BLOCKED_BORDER_COLOR

    else:
        fill_color = ARROW_COLOR
        border_color = ARROW_BORDER_COLOR

    points = get_arrow_points(
        center_x,
        center_y,
        arrow.direction,
    )

    pygame.draw.polygon(
        screen,
        fill_color,
        points,
    )

    pygame.draw.polygon(
        screen,
        border_color,
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
    restart_button,
    feedback_message,
    blocked_arrow,
):
    """绘制游戏界面。"""
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
            blocked=(arrow is blocked_arrow),
        )

    if feedback_message:
        if blocked_arrow is not None:
            message_color = (200, 55, 55)
        else:
            message_color = (45, 145, 85)

        message = feedback_message
    else:
        message_color = TEXT_COLOR
        message = "点击箭头，检查它前进方向上的路径"

    message_font = get_font(
        18,
        bold=bool(feedback_message),
    )

    draw_centered_text(
        screen,
        message,
        message_font,
        message_color,
        (450, 608),
    )

    back_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    restart_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )


def draw_result_screen(
    screen,
    title,
    message,
    title_color,
    primary_button,
    home_button,
):
    """绘制通关或失败结果界面。"""
    screen.fill(BACKGROUND_COLOR)

    window_width, _ = screen.get_size()

    title_font = get_font(55, bold=True)
    message_font = get_font(23)

    draw_centered_text(
        screen,
        title,
        title_font,
        title_color,
        (window_width // 2, 210),
    )

    draw_centered_text(
        screen,
        message,
        message_font,
        TEXT_COLOR,
        (window_width // 2, 300),
    )

    primary_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    home_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )