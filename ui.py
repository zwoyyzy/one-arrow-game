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


def get_star_points(
    center,
    outer_radius,
    inner_ratio=0.45,
):
    """计算新粗犷主义五角星的十个顶点。"""
    center_x, center_y = center
    points = []

    for index in range(10):
        angle = math.radians(
            -90 + index * 36
        )

        radius = (
            outer_radius
            if index % 2 == 0
            else outer_radius * inner_ratio
        )

        points.append(
            (
                int(
                    center_x
                    + math.cos(angle) * radius
                ),
                int(
                    center_y
                    + math.sin(angle) * radius
                ),
            )
        )

    return points


def draw_brutal_star(
    screen,
    center,
    radius,
    unlocked,
):
    """绘制带粗黑轮廓和右下硬阴影的立体星星。"""
    shadow_points = get_star_points(
        (
            center[0] + 4,
            center[1] + 4,
        ),
        radius,
    )

    star_points = get_star_points(
        center,
        radius,
    )

    pygame.gfxdraw.filled_polygon(
        screen,
        shadow_points,
        BLACK,
    )
    pygame.gfxdraw.aapolygon(
        screen,
        shadow_points,
        BLACK,
    )

    fill_color = (
        (255, 184, 0)
        if unlocked
        else (208, 208, 208)
    )

    pygame.gfxdraw.filled_polygon(
        screen,
        star_points,
        fill_color,
    )
    pygame.gfxdraw.aapolygon(
        screen,
        star_points,
        BLACK,
    )
    pygame.draw.polygon(
        screen,
        BLACK,
        star_points,
        width=3,
    )


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


def draw_start_screen(screen, start_button, level_select_button=None,
                      random_button=None, continue_button=None,
                      save_summary=None):
    """绘制开始界面。"""
    screen.fill(CREAM)
    width, height = screen.get_size()
    mouse = pygame.mouse.get_pos()

    draw_rotated_card(screen, (610, 180), ACID_YELLOW, "一箭又一箭",
                      -2, (width // 2, 255), 62, 10)
    draw_rotated_card(screen, (430, 65), WHITE,
                      "ARROW PUZZLE : NEO-BRUTALISM", 2,
                      (width // 2, 139), 17, 6)
    badge = pygame.Rect(width // 2 - 180, 365, 360, 58)
    draw_brutal_card(screen, badge, PURPLE, 28, 5, 3)
    draw_centered_text(screen, "CLICK · THINK · POP !", get_font(18, True),
                       WHITE, badge.center)

    if continue_button:
        hovered = save_summary is not None and continue_button.contains(mouse)
        rect = continue_button.rect.move(-3, -3) if hovered else continue_button.rect
        draw_brutal_card(screen, rect, CYAN if save_summary else PALE,
                         8, 9 if hovered else 6, 3)
        title = save_summary["title"] if save_summary else "继续关卡 · 暂无存档"
        detail = (save_summary["detail"] if save_summary
                  else "开始一局游戏后将自动保存进度")
        color = BLACK if save_summary else DISABLED
        draw_centered_text(screen, title, get_font(22, True), color,
                           (rect.centerx, rect.centery - 14))
        draw_centered_text(screen, detail, get_font(14, True), color,
                           (rect.centerx, rect.centery + 18))

    start_button.draw(screen, mouse)
    if level_select_button:
        level_select_button.draw(screen, mouse)
    if random_button:
        random_button.draw(screen, mouse)
    draw_centered_text(screen, "PURE PYGAME · ZERO EXTERNAL ASSETS",
                       get_font(14, True), BLACK, (width // 2, height - 25))


def draw_sound_settings_overlay(
    screen,
    audio,
    bgm_button,
    fly_button,
    close_button,
):
    """绘制背景音乐和箭头飞出音效设置弹窗。"""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((18, 18, 18, 165))
    screen.blit(overlay, (0, 0))

    width, height = screen.get_size()
    modal = pygame.Rect(width // 2 - 270, 145, 540, 390)
    draw_brutal_card(screen, modal, WHITE, 12, 10, 4)

    title = pygame.Rect(width // 2 - 190, 175, 380, 62)
    draw_brutal_card(screen, title, ACID_YELLOW, 8, 6, 3)
    draw_centered_text(screen, "声音设置", get_font(28, True), BLACK, title.center)

    mouse = pygame.mouse.get_pos()
    for button in (bgm_button, fly_button, close_button):
        button.draw(screen, mouse)

    draw_centered_text(
        screen,
        "可分别关闭背景音乐或箭头飞出音效",
        get_font(14, True),
        BLACK,
        (width // 2, 555),
    )


def draw_level_icon(screen, level_index, center, muted=False):
    """在统一的 40x40 安全区域内绘制关卡图标。"""
    ink = (75, 75, 75) if muted else BLACK
    accent = (135, 135, 135) if muted else {
        0: (188, 126, 66),
        1: (91, 151, 127),
        2: (154, 94, 55),
        3: (116, 82, 54),
        4: (224, 166, 42),
    }.get(level_index, CYAN)
    x, y = center

    if level_index == 0:
        pygame.draw.line(screen, ink, (x - 15, y), (x + 10, y), 4)
        pygame.draw.polygon(screen, accent, [(x + 5, y - 8), (x + 18, y), (x + 5, y + 8)])
        pygame.draw.polygon(screen, ink, [(x + 5, y - 8), (x + 18, y), (x + 5, y + 8)], 2)
        pygame.draw.polygon(screen, accent, [(x - 16, y), (x - 23, y - 5), (x - 13, y - 4), (x - 13, y + 4), (x - 23, y + 5)])
        pygame.draw.polygon(screen, ink, [(x - 16, y), (x - 23, y - 5), (x - 13, y - 4), (x - 13, y + 4), (x - 23, y + 5)], 2)
    elif level_index == 1:
        for offset, color in ((-5, (194, 102, 86)), (0, accent), (5, (73, 131, 169))):
            pygame.draw.line(screen, ink, (x - 16, y + offset), (x + 7, y + offset), 2)
            pygame.draw.polygon(screen, color, [(x + 5, y + offset - 4), (x + 16, y + offset), (x + 5, y + offset + 4)])
            pygame.draw.polygon(screen, ink, [(x + 5, y + offset - 4), (x + 16, y + offset), (x + 5, y + offset + 4)], 1)
    elif level_index == 2:
        body = pygame.Rect(x - 8, y - 7, 16, 22)
        pygame.draw.polygon(screen, accent, [(body.left, body.top), (body.right, body.top), (body.right - 3, body.bottom), (body.left + 3, body.bottom)])
        pygame.draw.polygon(screen, ink, [(body.left, body.top), (body.right, body.top), (body.right - 3, body.bottom), (body.left + 3, body.bottom)], 2)
        for arrow_x in (x - 5, x, x + 5):
            pygame.draw.line(screen, ink, (arrow_x, y - 6), (arrow_x, y - 16), 2)
            pygame.draw.polygon(screen, accent, [(arrow_x, y - 18), (arrow_x - 3, y - 13), (arrow_x + 3, y - 13)])
    elif level_index == 3:
        bow_rect = pygame.Rect(x - 15, y - 16, 24, 32)
        pygame.draw.arc(screen, accent, bow_rect, -math.pi / 2, math.pi / 2, 4)
        pygame.draw.arc(screen, ink, bow_rect, -math.pi / 2, math.pi / 2, 2)
        pygame.draw.line(screen, ink, (x - 7, y - 15), (x - 7, y + 15), 1)
        pygame.draw.line(screen, ink, (x - 7, y), (x + 16, y), 2)
        pygame.draw.polygon(screen, accent, [(x + 17, y), (x + 10, y - 4), (x + 10, y + 4)])
    else:
        for radius, color in ((15, accent), (10, WHITE), (5, CORAL)):
            pygame.draw.circle(screen, color, (x, y), radius)
            pygame.draw.circle(screen, ink, (x, y), radius, width=2)
        pygame.draw.line(screen, ink, (x - 18, y + 17), (x + 13, y - 14), 2)
        pygame.draw.polygon(screen, accent, [(x + 16, y - 17), (x + 9, y - 16), (x + 16, y - 10)])


def draw_level_select_screen(
    screen,
    level_buttons,
    back_button,
    level_progress,
    feedback_message="",
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

    for index, button in enumerate(level_buttons):
        record = level_progress[index]
        # 第一关默认点亮；通关上一关后，当前待挑战关卡点亮。
        unlocked = index == 0 or level_progress[index - 1]["completed"]
        hovered = unlocked and button.contains(mouse)
        rect = button.rect.move(-3, -3) if hovered else button.rect

        draw_brutal_card(
            screen,
            rect,
            WHITE if unlocked else (105, 105, 105),
            8,
            9 if hovered else 6,
            3,
        )

        icon_badge = pygame.Rect(
            rect.left + 9,
            rect.top + 9,
            42,
            42,
        )
        draw_brutal_card(
            screen,
            icon_badge,
            PALE if unlocked else (125, 125, 125),
            6,
            3,
            2,
        )

        draw_centered_text(
            screen,
            f"LEVEL {index + 1:02d}",
            get_font(19, True),
            BLACK if unlocked else (45, 45, 45),
            (rect.left + 106, rect.y + 30),
        )

        draw_level_icon(
            screen,
            index,
            icon_badge.center,
            muted=not unlocked,
        )

        if unlocked:
            for star_index in range(3):
                draw_brutal_star(
                    screen,
                    (
                        rect.centerx - 32 + star_index * 32,
                        rect.y + 73,
                    ),
                    11,
                    unlocked=star_index < record["stars"],
                )

            best_time = record["best_time"]
            draw_centered_text(
                screen,
                (
                    f"最佳 {best_time} 秒"
                    if best_time is not None
                    else "尚未通关"
                ),
                get_font(14, True),
                BLACK,
                (rect.centerx, rect.y + 104),
            )
        else:
            lock_body = pygame.Rect(rect.centerx - 15, rect.y + 57, 30, 25)
            pygame.draw.arc(
                screen,
                BLACK,
                pygame.Rect(rect.centerx - 12, rect.y + 39, 24, 30),
                math.pi,
                math.pi * 2,
                width=5,
            )
            pygame.draw.rect(screen, BLACK, lock_body, border_radius=3)
            pygame.draw.circle(screen, (105, 105, 105), (rect.centerx, rect.y + 68), 3)
            draw_centered_text(
                screen,
                "锁定",
                get_font(14, True),
                BLACK,
                (rect.centerx, rect.y + 101),
            )

    if feedback_message:
        notice = pygame.Rect(width // 2 - 150, 515, 300, 42)
        draw_brutal_card(screen, notice, CORAL, 8, 5, 3)
        draw_centered_text(
            screen,
            feedback_message,
            get_font(16, True),
            WHITE,
            notice.center,
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
    timer_seconds=0,
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
        205,
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

    minutes = timer_seconds // 60
    seconds = timer_seconds % 60
    separator_x = remain_card.x + 91

    pygame.draw.line(
        screen,
        BLACK,
        (separator_x, remain_card.y + 10),
        (separator_x, remain_card.bottom - 10),
        width=2,
    )

    draw_centered_text(
        screen,
        f"剩余 {remaining_arrows}",
        get_font(14, True),
        BLACK,
        (remain_card.x + 45, remain_card.centery),
    )

    draw_centered_text(
        screen,
        f"计时 {minutes:02d}:{seconds:02d}",
        get_font(13, True),
        BLACK,
        (remain_card.x + 148, remain_card.centery),
    )

    life_card = pygame.Rect(
        remain_card.right + 18,
        header.y + 14,
        165,
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
            life_card.x + 41,
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
        + 86
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
    timer_seconds=0,
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
        timer_seconds,
    )

        # 计算棋盘外框顶部位置
    _, grid_top, _ = get_board_geometry(
        screen,
        level["rows"],
        level["cols"],
    )

    header_bottom = 116
    board_top = grid_top - BOARD_PADDING

    # 在顶部状态栏和棋盘之间垂直居中
    mode_y = (
        header_bottom
        + (
            board_top
            - header_bottom
        ) // 2
    )

    draw_centered_text(
        screen,
        mode_text,
        get_font(18, True),
        PURPLE,
        (
            screen.get_width() // 2,
            mode_y,
        ),
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
    star_count=0,
    reference_time=0,
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
        118 if star_count else 145,
        550,
        475 if star_count else 395,
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
            180 if star_count else 220,
        ),
    )

    draw_centered_text(
        screen,
        message,
        get_font(19, True),
        BLACK,
        (
            width // 2,
            230 if star_count else 285,
        ),
    )

    if star_count:
        star_card = pygame.Rect(
            width // 2 - 175,
            260,
            350,
            100,
        )

        draw_brutal_card(
            screen,
            star_card,
            WHITE,
            10,
            6,
            3,
        )

        star_centers = (
            (width // 2 - 78, 312),
            (width // 2, 301),
            (width // 2 + 78, 312),
        )

        star_radii = (
            27,
            33,
            27,
        )

        for index in range(3):
            draw_brutal_star(
                screen,
                star_centers[index],
                star_radii[index],
                unlocked=index < star_count,
            )

    if stats_text:
        stats = pygame.Rect(
            width // 2 - 195,
            380 if star_count else 315,
            390,
            44 if star_count else 46,
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
            (
                f"{stats_text}  ·  AI参考 {reference_time} 秒"
                if star_count and reference_time
                else stats_text
            ),
            get_font(14 if star_count else 16, True),
            BLACK,
            stats.center,
        )

    mouse = pygame.mouse.get_pos()

    # 星级弹窗重新排列按钮，增加阴影之间的实际空隙。
    if star_count:
        if secondary_button:
            secondary_button.rect.size = (140, 50)
            secondary_button.rect.topleft = (
                width // 2 - 160,
                442,
            )

            primary_button.rect.size = (140, 50)
            primary_button.rect.topleft = (
                width // 2 + 20,
                442,
            )
        else:
            primary_button.rect.size = (210, 50)
            primary_button.rect.midtop = (
                width // 2,
                442,
            )

        home_button.rect.size = (210, 50)
        home_button.rect.midtop = (
            width // 2,
            516,
        )
    else:
        if secondary_button:
            secondary_button.rect.size = (150, 58)
            secondary_button.rect.topleft = (
                width // 2 - 165,
                395,
            )

            primary_button.rect.size = (150, 58)
            primary_button.rect.topleft = (
                width // 2 + 15,
                395,
            )
        else:
            primary_button.rect.size = (240, 60)
            primary_button.rect.midtop = (
                width // 2,
                390,
            )

        home_button.rect.size = (240, 60)
        home_button.rect.midtop = (
            width // 2,
            480,
        )

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
