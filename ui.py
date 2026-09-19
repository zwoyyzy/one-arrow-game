import math
from pathlib import Path

import pygame
import pygame.gfxdraw


CREAM = (250, 248, 245)
BLACK = (18, 18, 18)
WHITE = (255, 255, 255)
ACID_YELLOW = (255, 230, 0)
ACID_GREEN = (212, 255, 0)
CYAN = (0, 240, 255)
PURPLE = (168, 85, 247)
CORAL = (255, 51, 102)
PALE = (242, 239, 233)
DISABLED = (190, 190, 190)

DEFAULT_CELL_SIZE = 82
GAME_AREA_TOP = 145
GAME_AREA_BOTTOM = 610
BOARD_PADDING = 20


def get_font(size, bold=False):
    """加载支持中文的系统字体。"""
    fonts = Path(r"C:\Windows\Fonts")

    if bold:
        names = [
            "msyhbd.ttc",
            "simhei.ttf",
            "simsun.ttc",
        ]
    else:
        names = [
            "msyh.ttc",
            "simhei.ttf",
            "simsun.ttc",
        ]

    for name in names:
        path = fonts / name

        if path.exists():
            font = pygame.font.Font(str(path), size)

            if bold and name != "msyhbd.ttc":
                font.set_bold(True)

            return font

    font = pygame.font.Font(None, size)
    font.set_bold(bold)
    return font


def draw_centered_text(
    screen,
    text,
    font,
    color,
    center,
):
    """在指定位置居中显示文字。"""
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


def draw_heart(
    screen,
    center,
    size,
    color,
    filled=True,
):
    """使用几何图形绘制心形。"""
    x, y = center
    radius = max(3, size // 4)

    left_center = (
        x - radius,
        y - radius // 2,
    )
    right_center = (
        x + radius,
        y - radius // 2,
    )

    points = [
        (
            x - radius * 2,
            y - radius // 2,
        ),
        (
            x,
            y + radius * 2,
        ),
        (
            x + radius * 2,
            y - radius // 2,
        ),
    ]

    if filled:
        pygame.draw.circle(
            screen,
            color,
            left_center,
            radius,
        )
        pygame.draw.circle(
            screen,
            color,
            right_center,
            radius,
        )
        pygame.draw.polygon(
            screen,
            color,
            points,
        )
    else:
        pygame.draw.circle(
            screen,
            color,
            left_center,
            radius,
            width=2,
        )
        pygame.draw.circle(
            screen,
            color,
            right_center,
            radius,
            width=2,
        )
        pygame.draw.lines(
            screen,
            color,
            False,
            points,
            width=2,
        )


def draw_brutal_card(
    screen,
    rect,
    fill,
    radius=8,
    shadow=6,
    border=3,
):
    """绘制新粗犷主义卡片。"""
    shadow_rect = rect.move(shadow, shadow)

    pygame.draw.rect(
        screen,
        BLACK,
        shadow_rect,
        border_radius=radius,
    )
    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=radius,
    )
    pygame.draw.rect(
        screen,
        BLACK,
        rect,
        width=border,
        border_radius=radius,
    )


def draw_rotated_card(
    screen,
    size,
    fill,
    text,
    angle,
    center,
    font_size,
    shadow=8,
):
    """绘制旋转标题卡片。"""
    card = pygame.Surface(
        size,
        pygame.SRCALPHA,
    )
    rect = card.get_rect()

    pygame.draw.rect(
        card,
        BLACK,
        rect.move(shadow, shadow),
        border_radius=8,
    )
    pygame.draw.rect(
        card,
        fill,
        rect.inflate(-shadow, -shadow),
        border_radius=8,
    )
    pygame.draw.rect(
        card,
        BLACK,
        rect.inflate(-shadow, -shadow),
        width=4,
        border_radius=8,
    )

    draw_centered_text(
        card,
        text,
        get_font(font_size, True),
        BLACK,
        (
            rect.centerx - shadow // 2,
            rect.centery - shadow // 2,
        ),
    )

    rotated = pygame.transform.rotozoom(
        card,
        angle,
        1.0,
    )

    screen.blit(
        rotated,
        rotated.get_rect(center=center),
    )


class Button:
    """游戏按钮。"""

    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        font_size=24,
        outline=False,
    ):
        self.rect = pygame.Rect(
            x,
            y,
            width,
            height,
        )
        self.text = text
        self.font = get_font(font_size, True)
        self.outline = outline
        self.pressed_until = 0

    def contains(self, mouse_position):
        return self.rect.collidepoint(
            mouse_position
        )

    def draw(
        self,
        screen,
        mouse_position,
    ):
        hovered = self.contains(
            mouse_position
        )

        pressed = (
            pygame.time.get_ticks()
            < self.pressed_until
        )

        if pressed:
            rect = self.rect.move(5, 5)
            shadow = 0
        elif hovered:
            rect = self.rect.move(-3, -3)
            shadow = 9
        else:
            rect = self.rect
            shadow = 6

        fill = (
            WHITE
            if self.outline
            else CYAN
        )

        draw_brutal_card(
            screen,
            rect,
            fill,
            8,
            shadow,
            3,
        )

        draw_centered_text(
            screen,
            self.text,
            self.font,
            BLACK,
            rect.center,
        )

    def press(self):
        self.pressed_until = (
            pygame.time.get_ticks() + 110
        )


def draw_start_screen(
    screen,
    start_button,
    level_select_button=None,
    random_button=None,
):
    """绘制开始界面。"""
    screen.fill(CREAM)

    width, height = screen.get_size()

    draw_rotated_card(
        screen,
        (610, 180),
        ACID_YELLOW,
        "一箭又一箭",
        -2,
        (width // 2, 255),
        62,
        10,
    )

    draw_rotated_card(
        screen,
        (430, 65),
        WHITE,
        "ARROW PUZZLE : NEO-BRUTALISM",
        2,
        (width // 2, 139),
        17,
        6,
    )

    badge = pygame.Rect(
        width // 2 - 180,
        365,
        360,
        58,
    )

    draw_brutal_card(
        screen,
        badge,
        PURPLE,
        28,
        5,
        3,
    )

    draw_centered_text(
        screen,
        "CLICK · THINK · POP!",
        get_font(18, True),
        WHITE,
        badge.center,
    )

    mouse = pygame.mouse.get_pos()

    start_button.draw(
        screen,
        mouse,
    )

    if level_select_button:
        level_select_button.draw(
            screen,
            mouse,
        )

    if random_button:
        random_button.draw(
            screen,
            mouse,
        )

    draw_centered_text(
        screen,
        "PURE PYGAME · ZERO EXTERNAL ASSETS",
        get_font(14, True),
        BLACK,
        (
            width // 2,
            height - 25,
        ),
    )


def draw_level_select_screen(
    screen,
    level_buttons,
    back_button,
):
    """绘制关卡选择界面。"""
    screen.fill(CREAM)

    width, _ = screen.get_size()

    title = pygame.Rect(
        width // 2 - 250,
        45,
        500,
        88,
    )

    draw_brutal_card(
        screen,
        title,
        ACID_YELLOW,
        8,
        8,
        4,
    )

    draw_centered_text(
        screen,
        "SELECT YOUR LEVEL",
        get_font(34, True),
        BLACK,
        title.center,
    )

    mouse = pygame.mouse.get_pos()

    for button in level_buttons:
        button.draw(
            screen,
            mouse,
        )

    back_button.draw(
        screen,
        mouse,
    )


def get_board_geometry(
    screen,
    rows,
    cols,
):
    """计算棋盘的位置和格子大小。"""
    width, height = screen.get_size()

    available_width = width - 155

    game_area_bottom = min(
        GAME_AREA_BOTTOM,
        height - 90,
    )

    game_area_height = (
        game_area_bottom
        - GAME_AREA_TOP
    )

    available_height = (
        game_area_height
        - BOARD_PADDING * 2
    )

    cell = min(
        DEFAULT_CELL_SIZE,
        available_width // cols,
        available_height // rows,
    )

    board_height = (
        rows * cell
        + BOARD_PADDING * 2
    )

    board_top = (
        GAME_AREA_TOP
        + (
            game_area_height
            - board_height
        ) // 2
    )

    grid_top = (
        board_top
        + BOARD_PADDING
    )

    grid_left = (
        width - cols * cell
    ) // 2

    return (
        grid_left,
        grid_top,
        cell,
    )


def get_grid_position(
    screen,
    mouse_position,
    rows,
    cols,
):
    """把鼠标位置转换为棋盘行列。"""
    x, y = mouse_position

    left, top, cell = get_board_geometry(
        screen,
        rows,
        cols,
    )

    inside = (
        left <= x < left + cols * cell
        and top <= y < top + rows * cell
    )

    if not inside:
        return None

    row = (y - top) // cell
    col = (x - left) // cell

    return row, col


def draw_header(
    screen,
    level_number,
    remaining_arrows,
    mistakes_left,
    max_mistakes,
    restart_button,
    pause_button=None,
    shake=False,
):
    """绘制顶部状态栏。"""
    width, _ = screen.get_size()

    header = pygame.Rect(
        26,
        22,
        width - 52,
        88,
    )

    draw_brutal_card(
        screen,
        header,
        WHITE,
        14,
        6,
        3,
    )

    level_card = pygame.Rect(
        header.x + 14,
        header.y + 14,
        145,
        58,
    )

    draw_brutal_card(
        screen,
        level_card,
        ACID_YELLOW,
        7,
        4,
        3,
    )

    draw_centered_text(
        screen,
        f"LEVEL {level_number:02d}",
        get_font(18, True),
        BLACK,
        level_card.center,
    )

    remain_card = pygame.Rect(
        level_card.right + 18,
        header.y + 14,
        190,
        58,
    )

    draw_brutal_card(
        screen,
        remain_card,
        WHITE,
        7,
        4,
        3,
    )

    draw_centered_text(
        screen,
        f"剩余: {remaining_arrows}",
        get_font(18, True),
        BLACK,
        remain_card.center,
    )

    life_card = pygame.Rect(
        remain_card.right + 18,
        header.y + 14,
        180,
        58,
    )

    draw_brutal_card(
        screen,
        life_card,
        WHITE,
        7,
        4,
        3,
    )

    if shake:
        shake_x = int(
            math.sin(
                pygame.time.get_ticks()
                * 0.15
            ) * 4
        )
    else:
        shake_x = 0

    draw_centered_text(
        screen,
        "剩余失误",
        get_font(14, True),
        BLACK,
        (
            life_card.x + 45,
            life_card.centery,
        ),
    )

    pulse = (
        1
        if (
            pygame.time.get_ticks() // 350
        ) % 2 == 0
        else 0
    )

    base_x = (
        life_card.x
        + 99
        + shake_x
    )

    for index in range(max_mistakes):
        remaining = (
            index < mistakes_left
        )

        draw_heart(
            screen,
            (
                base_x + index * 24,
                life_card.centery,
            ),
            18 + (
                pulse
                if remaining
                else 0
            ),
            (
                CORAL
                if remaining
                else DISABLED
            ),
            filled=remaining,
        )

    mouse = pygame.mouse.get_pos()

    restart_button.draw(
        screen,
        mouse,
    )

    if pause_button:
        pause_button.draw(
            screen,
            mouse,
        )


def draw_status_bar(
    screen,
    level_number,
    remaining_arrows,
    mistakes_left,
):
    """兼容旧版状态栏调用。"""
    dummy = Button(
        screen.get_width() - 155,
        40,
        110,
        52,
        "重置",
        16,
        True,
    )

    draw_header(
        screen,
        level_number,
        remaining_arrows,
        mistakes_left,
        max(3, mistakes_left),
        dummy,
    )


def draw_board(
    screen,
    rows,
    cols,
):
    """绘制棋盘和空格槽位。"""
    left, top, cell = get_board_geometry(
        screen,
        rows,
        cols,
    )

    board = pygame.Rect(
        left - BOARD_PADDING,
        top - BOARD_PADDING,
        cols * cell + BOARD_PADDING * 2,
        rows * cell + BOARD_PADDING * 2,
    )

    draw_brutal_card(
        screen,
        board,
        WHITE,
        10,
        8,
        4,
    )

    for row in range(rows):
        for col in range(cols):
            tile = pygame.Rect(
                left + col * cell + 5,
                top + row * cell + 5,
                cell - 10,
                cell - 10,
            )

            pygame.draw.rect(
                screen,
                PALE,
                tile,
                border_radius=8,
            )

            pygame.draw.rect(
                screen,
                BLACK,
                tile,
                width=2,
                border_radius=8,
            )

            pygame.draw.circle(
                screen,
                BLACK,
                tile.center,
                max(2, cell // 25),
            )


def get_arrow_points(
    center_x,
    center_y,
    direction,
    scale=1.0,
):
    """计算不同方向箭头的顶点。"""
    base = [
        (-25, -8),
        (5, -8),
        (5, -20),
        (29, 0),
        (5, 20),
        (5, 8),
        (-25, 8),
    ]

    result = []

    for x, y in base:
        x *= scale
        y *= scale

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

        result.append(
            (
                int(center_x + new_x),
                int(center_y + new_y),
            )
        )

    return result


def draw_arrow(
    screen,
    arrow,
    blocked=False,
    hovered=False,
    hinted=False,
):
    """绘制箭头卡片和动画效果。"""
    rows = getattr(
        arrow,
        "board_rows",
        5,
    )
    cols = getattr(
        arrow,
        "board_cols",
        5,
    )

    left, top, cell = get_board_geometry(
        screen,
        rows,
        cols,
    )

    center_x = (
        left
        + arrow.col * cell
        + cell // 2
        + arrow.offset_x
    )

    center_y = (
        top
        + arrow.row * cell
        + cell // 2
        + arrow.offset_y
    )

    scale = cell / DEFAULT_CELL_SIZE

    if blocked:
        elapsed = max(
            0,
            pygame.time.get_ticks()
            - arrow.collision_start,
        )

        sequence = (
            6,
            -6,
            6,
            -6,
            0,
        )

        sequence_index = min(
            len(sequence) - 1,
            elapsed // 30,
        )

        center_x += (
            sequence[sequence_index]
            * scale
        )

    if (
        hovered
        and arrow.state == "idle"
        and not blocked
    ):
        center_x -= 3
        center_y -= 3

    # 箭头卡片与棋盘槽位完全同宽同高。
    tile_size = max(
        24,
        cell - 10,
    )

    tile = pygame.Rect(
        0,
        0,
        tile_size,
        tile_size,
    )

    tile.center = (
        int(center_x),
        int(center_y),
    )

    if arrow.state != "flying":
        if blocked:
            fill = CORAL
        elif hinted:
            fill = PURPLE
        elif hovered:
            fill = CYAN
        else:
            fill = ACID_GREEN

        hint_pulse = (
            2
            if (
                hinted
                and (
                    pygame.time.get_ticks()
                    // 220
                ) % 2 == 0
            )
            else 0
        )

        draw_brutal_card(
            screen,
            tile.inflate(
                hint_pulse,
                hint_pulse,
            ),
            fill,
            8,
            (
                6
                if hinted
                else (
                    4
                    if hovered
                    else 3
                )
            ),
            (
                4
                if hinted
                else 3
            ),
        )

    opacity = max(
        0,
        min(
            255,
            getattr(
                arrow,
                "opacity",
                255,
            ),
        ),
    )

    progress = 0.0

    if arrow.state == "flying":
        progress = min(
            1.0,
            arrow.flight_distance
            / max(
                1,
                getattr(
                    arrow,
                    "flight_target",
                    1,
                ),
            ),
        )

        opacity = int(
            255 * (1 - progress)
        )

        ghost = pygame.Surface(
            screen.get_size(),
            pygame.SRCALPHA,
        )

        for factor, alpha in (
            (0.22, 90),
            (0.45, 55),
            (0.68, 28),
        ):
            ghost_x = (
                center_x
                - arrow.offset_x * factor
            )
            ghost_y = (
                center_y
                - arrow.offset_y * factor
            )

            points = get_arrow_points(
                ghost_x,
                ghost_y,
                arrow.direction,
                scale * 0.84,
            )

            pygame.draw.polygon(
                ghost,
                (
                    18,
                    18,
                    18,
                    int(
                        alpha
                        * (1 - progress)
                    ),
                ),
                points,
                width=max(
                    2,
                    int(3 * scale),
                ),
            )

        screen.blit(
            ghost,
            (0, 0),
        )

    launch_scale = 1.0

    if arrow.state == "flying":
        launch_elapsed = (
            pygame.time.get_ticks()
            - arrow.flight_start
        )

        if launch_elapsed < 50:
            launch_scale = (
                1.0
                - 0.12
                * (
                    launch_elapsed
                    / 50
                )
            )

    points = get_arrow_points(
        center_x,
        center_y,
        arrow.direction,
        scale * 0.84 * launch_scale,
    )

    layer = pygame.Surface(
        screen.get_size(),
        pygame.SRCALPHA,
    )

    pygame.gfxdraw.filled_polygon(
        layer,
        points,
        (
            18,
            18,
            18,
            opacity,
        ),
    )

    pygame.gfxdraw.aapolygon(
        layer,
        points,
        (
            18,
            18,
            18,
            opacity,
        ),
    )

    screen.blit(
        layer,
        (0, 0),
    )

    if blocked:
        bubble = pygame.Rect(
            0,
            0,
            112,
            34,
        )

        bubble.centerx = tile.centerx

        # 顶部空间不足时，把气泡放在箭头下方。
        if tile.top >= 165:
            bubble.bottom = tile.top - 7
        else:
            bubble.top = tile.bottom + 7

        draw_brutal_card(
            screen,
            bubble,
            WHITE,
            6,
            4,
            3,
        )

        draw_centered_text(
            screen,
            "前方阻挡",
            get_font(15, True),
            CORAL,
            bubble.center,
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
    pause_button=None,
    hint_button=None,
    auto_solve_button=None,
    hinted_arrow=None,
    mode_text="主线关卡",
):
    """绘制游戏主界面。"""
    screen.fill(CREAM)

    draw_header(
        screen,
        level_number,
        len(arrows),
        mistakes_left,
        level["max_mistakes"],
        restart_button,
        pause_button,
        blocked_arrow is not None,
    )

    draw_centered_text(
        screen,
        mode_text,
        get_font(13, True),
        PURPLE,
        (screen.get_width() // 2, 128),
    )

    draw_board(
        screen,
        level["rows"],
        level["cols"],
    )

    mouse = pygame.mouse.get_pos()

    hovered = get_grid_position(
        screen,
        mouse,
        level["rows"],
        level["cols"],
    )

    for arrow in arrows:
        draw_arrow(
            screen,
            arrow,
            arrow is blocked_arrow,
            hovered
            == (
                arrow.row,
                arrow.col,
            ),
            arrow is hinted_arrow,
        )

    message = (
        feedback_message
        or "PICK AN ARROW · CHECK THE PATH · POP IT OUT"
    )

    color = (
        CORAL
        if blocked_arrow
        else BLACK
    )

    if blocked_arrow:
        message_card = pygame.Rect(
            screen.get_width() // 2 - 175,
            screen.get_height() - 55,
            350,
            40,
        )

        draw_brutal_card(
            screen,
            message_card,
            WHITE,
            7,
            4,
            3,
        )

        draw_centered_text(
            screen,
            message,
            get_font(17, True),
            color,
            message_card.center,
        )
    else:
        draw_centered_text(
            screen,
            message,
            get_font(15, True),
            color,
            (
                screen.get_width() // 2,
                screen.get_height() - 22,
            ),
        )

    # 这两个按钮必须放在 if/else 外面，
    # 否则发生碰撞时按钮会消失。
    back_button.draw(
        screen,
        mouse,
    )

    if hint_button:
        hint_button.draw(
            screen,
            mouse,
        )

    if auto_solve_button:
        auto_solve_button.draw(
            screen,
            mouse,
        )


def draw_result_screen(
    screen,
    title,
    message,
    title_color,
    primary_button,
    home_button,
    stats_text="",
    secondary_button=None,
):
    """绘制通关或失败弹窗。"""
    overlay = pygame.Surface(
        screen.get_size(),
        pygame.SRCALPHA,
    )

    overlay.fill(
        (
            18,
            18,
            18,
            128,
        )
    )

    screen.blit(
        overlay,
        (0, 0),
    )

    width, _ = screen.get_size()

    clear = (
        "通关" in title
        or "全部" in title
    )

    modal = pygame.Rect(
        width // 2 - 275,
        145,
        550,
        395,
    )

    modal_color = (
        ACID_GREEN
        if clear
        else CORAL
    )

    draw_brutal_card(
        screen,
        modal,
        modal_color,
        10,
        10,
        4,
    )

    heading = (
        "LEVEL CLEAR!"
        if clear
        else "GAME OVER!"
    )

    draw_centered_text(
        screen,
        heading,
        get_font(46, True),
        BLACK,
        (
            width // 2,
            220,
        ),
    )

    draw_centered_text(
        screen,
        message,
        get_font(19, True),
        BLACK,
        (
            width // 2,
            285,
        ),
    )

    if stats_text:
        stats = pygame.Rect(
            width // 2 - 180,
            315,
            360,
            46,
        )

        draw_brutal_card(
            screen,
            stats,
            WHITE,
            6,
            4,
            3,
        )

        draw_centered_text(
            screen,
            stats_text,
            get_font(16, True),
            BLACK,
            stats.center,
        )

    mouse = pygame.mouse.get_pos()

    primary_button.draw(
        screen,
        mouse,
    )

    if secondary_button:
        secondary_button.draw(
            screen,
            mouse,
        )

    home_button.draw(
        screen,
        mouse,
    )


def draw_pause_overlay(
    screen,
    resume_button,
):
    """绘制暂停遮罩和继续游戏按钮。"""
    overlay = pygame.Surface(
        screen.get_size(),
        pygame.SRCALPHA,
    )

    overlay.fill(
        (
            18,
            18,
            18,
            150,
        )
    )

    screen.blit(
        overlay,
        (0, 0),
    )

    width, height = screen.get_size()

    modal = pygame.Rect(
        width // 2 - 190,
        height // 2 - 120,
        380,
        240,
    )

    draw_brutal_card(
        screen,
        modal,
        WHITE,
        12,
        10,
        4,
    )

    draw_centered_text(
        screen,
        "游戏已暂停",
        get_font(38, True),
        BLACK,
        (
            width // 2,
            height // 2 - 55,
        ),
    )

    draw_centered_text(
        screen,
        "休息一下，准备好后继续",
        get_font(16, True),
        BLACK,
        (
            width // 2,
            height // 2 - 12,
        ),
    )

    resume_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )
