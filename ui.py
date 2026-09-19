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


def get_font(size, bold=False):
    """直接读取 Windows 中文字体，避免 Pygame 扫描字体时报错。"""
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

            # 如果没有找到专门的粗体字体，则由 Pygame 设置粗体
            if bold and font_path.name != "msyhbd.ttc":
                font.set_bold(True)

            return font

    # 如果没有找到中文字体，则使用 Pygame 默认字体
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

    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_font(28, bold=True)

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

    # 开始按钮
    start_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )

    # 底部提示
    draw_centered_text(
        screen,
        "使用鼠标进行操作",
        tip_font,
        (130, 140, 160),
        (window_width // 2, 625),
    )


def draw_game_placeholder(screen, back_button):
    """临时游戏界面，下一阶段会替换为正式棋盘。"""
    screen.fill(BACKGROUND_COLOR)

    window_width, _ = screen.get_size()

    title_font = get_font(42, bold=True)
    text_font = get_font(25)

    draw_centered_text(
        screen,
        "第 1 关",
        title_font,
        TITLE_COLOR,
        (window_width // 2, 170),
    )

    draw_centered_text(
        screen,
        "开始按钮运行正常",
        text_font,
        TEXT_COLOR,
        (window_width // 2, 280),
    )

    draw_centered_text(
        screen,
        "下一阶段将在这里绘制棋盘和箭头",
        text_font,
        TEXT_COLOR,
        (window_width // 2, 330),
    )

    back_button.draw(
        screen,
        pygame.mouse.get_pos(),
    )