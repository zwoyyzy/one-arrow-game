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

BOARD_TOP = 144
DEFAULT_CELL_SIZE = 82


def get_font(size, bold=False):
    fonts = Path(r"C:\Windows\Fonts")
    names = ["msyhbd.ttc", "simhei.ttf", "simsun.ttc"] if bold else ["msyh.ttc", "simhei.ttf", "simsun.ttc"]
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


def draw_centered_text(screen, text, font, color, center):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))


def draw_brutal_card(screen, rect, fill, radius=8, shadow=6, border=3):
    shadow_rect = rect.move(shadow, shadow)
    pygame.draw.rect(screen, BLACK, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, BLACK, rect, width=border, border_radius=radius)


def draw_rotated_card(screen, size, fill, text, angle, center, font_size, shadow=8):
    card = pygame.Surface(size, pygame.SRCALPHA)
    rect = card.get_rect()
    pygame.draw.rect(card, BLACK, rect.move(shadow, shadow), border_radius=8)
    pygame.draw.rect(card, fill, rect.inflate(-shadow, -shadow), border_radius=8)
    pygame.draw.rect(card, BLACK, rect.inflate(-shadow, -shadow), width=4, border_radius=8)
    draw_centered_text(card, text, get_font(font_size, True), BLACK, (rect.centerx - shadow // 2, rect.centery - shadow // 2))
    rotated = pygame.transform.rotozoom(card, angle, 1.0)
    screen.blit(rotated, rotated.get_rect(center=center))


class Button:
    def __init__(self, x, y, width, height, text, font_size=24, outline=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = get_font(font_size, True)
        self.outline = outline
        self.pressed_until = 0

    def contains(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def draw(self, screen, mouse_position):
        hovered = self.contains(mouse_position)
        pressed = pygame.time.get_ticks() < self.pressed_until
        if pressed:
            rect = self.rect.move(5, 5)
            shadow = 0
        elif hovered:
            rect = self.rect.move(-3, -3)
            shadow = 9
        else:
            rect = self.rect
            shadow = 6
        fill = WHITE if self.outline else CYAN
        draw_brutal_card(screen, rect, fill, 8, shadow, 3)
        draw_centered_text(screen, self.text, self.font, BLACK, rect.center)

    def press(self):
        self.pressed_until = pygame.time.get_ticks() + 110


def draw_start_screen(screen, start_button, level_select_button=None):
    screen.fill(CREAM)
    width, height = screen.get_size()
    draw_rotated_card(screen, (610, 180), ACID_YELLOW, "一箭又一箭", -2, (width // 2, 255), 62, 10)
    draw_rotated_card(screen, (430, 65), WHITE, "ARROW PUZZLE : NEO-BRUTALISM", 2, (width // 2, 139), 17, 6)
    badge = pygame.Rect(width // 2 - 180, 365, 360, 58)
    draw_brutal_card(screen, badge, PURPLE, 28, 5, 3)
    draw_centered_text(screen, "CLICK · THINK · POP!", get_font(18, True), WHITE, badge.center)
    start_button.draw(screen, pygame.mouse.get_pos())
    if level_select_button:
        level_select_button.draw(screen, pygame.mouse.get_pos())
    draw_centered_text(screen, "PURE PYGAME · ZERO EXTERNAL ASSETS", get_font(14, True), BLACK, (width // 2, height - 25))


def draw_level_select_screen(screen, level_buttons, back_button):
    screen.fill(CREAM)
    width, _ = screen.get_size()
    title = pygame.Rect(width // 2 - 250, 45, 500, 88)
    draw_brutal_card(screen, title, ACID_YELLOW, 8, 8, 4)
    draw_centered_text(screen, "SELECT YOUR LEVEL", get_font(34, True), BLACK, title.center)
    mouse = pygame.mouse.get_pos()
    for button in level_buttons:
        button.draw(screen, mouse)
    back_button.draw(screen, mouse)


def get_board_geometry(screen, rows, cols):
    width, height = screen.get_size()
    available_width = width - 155
    available_height = height - BOARD_TOP - 92
    cell = min(DEFAULT_CELL_SIZE, available_width // cols, available_height // rows)
    return (width - cols * cell) // 2, BOARD_TOP, cell


def get_grid_position(screen, mouse_position, rows, cols):
    x, y = mouse_position
    left, top, cell = get_board_geometry(screen, rows, cols)
    if not (left <= x < left + cols * cell and top <= y < top + rows * cell):
        return None
    return (y - top) // cell, (x - left) // cell


def draw_header(screen, level_number, remaining_arrows, mistakes_left, max_mistakes, restart_button, pause_button=None, shake=False):
    width, _ = screen.get_size()
    header = pygame.Rect(26, 22, width - 52, 88)
    draw_brutal_card(screen, header, WHITE, 14, 6, 3)
    level_card = pygame.Rect(header.x + 14, header.y + 14, 145, 58)
    draw_brutal_card(screen, level_card, ACID_YELLOW, 7, 4, 3)
    draw_centered_text(screen, f"LEVEL {level_number:02d}", get_font(18, True), BLACK, level_card.center)
    remain_card = pygame.Rect(level_card.right + 18, header.y + 14, 190, 58)
    draw_brutal_card(screen, remain_card, WHITE, 7, 4, 3)
    draw_centered_text(screen, f"剩余: {remaining_arrows}", get_font(18, True), BLACK, remain_card.center)
    life_card = pygame.Rect(remain_card.right + 18, header.y + 14, 180, 58)
    draw_brutal_card(screen, life_card, WHITE, 7, 4, 3)
    base_x = life_card.x + 70 + (int(math.sin(pygame.time.get_ticks() * 0.15) * 5) if shake else 0)
    draw_centered_text(screen, "失误:", get_font(16, True), BLACK, (life_card.x + 38, life_card.centery))
    for index in range(max_mistakes):
        color = BLACK if index < mistakes_left else CORAL
        rect = pygame.Rect(base_x + index * 18, life_card.centery - 7, 14, 14)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, width=2)
    restart_button.draw(screen, pygame.mouse.get_pos())
    if pause_button:
        pause_button.draw(screen, pygame.mouse.get_pos())


def draw_status_bar(screen, level_number, remaining_arrows, mistakes_left):
    dummy = Button(screen.get_width() - 155, 40, 110, 52, "重置", 16, True)
    draw_header(screen, level_number, remaining_arrows, mistakes_left, max(3, mistakes_left), dummy)


def draw_board(screen, rows, cols):
    left, top, cell = get_board_geometry(screen, rows, cols)
    board = pygame.Rect(left - 20, top - 20, cols * cell + 40, rows * cell + 40)
    draw_brutal_card(screen, board, WHITE, 10, 8, 4)
    for row in range(rows):
        for col in range(cols):
            tile = pygame.Rect(left + col * cell + 5, top + row * cell + 5, cell - 10, cell - 10)
            pygame.draw.rect(screen, PALE, tile, border_radius=8)
            pygame.draw.rect(screen, BLACK, tile, width=2, border_radius=8)
            pygame.draw.circle(screen, BLACK, tile.center, max(2, cell // 25))


def get_arrow_points(center_x, center_y, direction, scale=1.0):
    base = [(-25, -8), (5, -8), (5, -20), (29, 0), (5, 20), (5, 8), (-25, 8)]
    result = []
    for x, y in base:
        x, y = x * scale, y * scale
        if direction == "right": nx, ny = x, y
        elif direction == "left": nx, ny = -x, y
        elif direction == "up": nx, ny = y, -x
        elif direction == "down": nx, ny = y, x
        else: raise ValueError(f"无法绘制箭头方向：{direction}")
        result.append((int(center_x + nx), int(center_y + ny)))
    return result


def draw_arrow(screen, arrow, blocked=False, hovered=False):
    rows, cols = getattr(arrow, "board_rows", 5), getattr(arrow, "board_cols", 5)
    left, top, cell = get_board_geometry(screen, rows, cols)
    cx = left + arrow.col * cell + cell // 2 + arrow.offset_x
    cy = top + arrow.row * cell + cell // 2 + arrow.offset_y
    scale = cell / DEFAULT_CELL_SIZE

    if blocked:
        elapsed = max(0, pygame.time.get_ticks() - arrow.collision_start)
        sequence = (6, -6, 6, -6, 0)
        cx += sequence[min(len(sequence) - 1, elapsed // 30)] * scale

    if hovered and arrow.state == "idle" and not blocked:
        cx -= 3
        cy -= 3

    tile_size = int(cell * 0.72)
    tile = pygame.Rect(0, 0, tile_size, tile_size)
    tile.center = (int(cx), int(cy))
    if arrow.state != "flying":
        fill = CORAL if blocked else (CYAN if hovered else ACID_GREEN)
        draw_brutal_card(screen, tile, fill, 8, 7 if hovered else 5, 3)

    opacity = max(0, min(255, getattr(arrow, "opacity", 255)))
    progress = 0.0
    if arrow.state == "flying":
        progress = min(1.0, arrow.flight_distance / max(1, getattr(arrow, "flight_target", 1)))
        opacity = int(255 * (1 - progress))
        ghost = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for factor, alpha in ((0.22, 90), (0.45, 55), (0.68, 28)):
            gx = cx - arrow.offset_x * factor
            gy = cy - arrow.offset_y * factor
            points = get_arrow_points(gx, gy, arrow.direction, scale * 0.84)
            pygame.draw.polygon(ghost, (18, 18, 18, int(alpha * (1 - progress))), points, width=max(2, int(3 * scale)))
        screen.blit(ghost, (0, 0))

    launch_scale = 1.0
    if arrow.state == "flying":
        launch_elapsed = pygame.time.get_ticks() - arrow.flight_start
        if launch_elapsed < 50:
            launch_scale = 1.0 - 0.12 * (launch_elapsed / 50)
    points = get_arrow_points(cx, cy, arrow.direction, scale * 0.84 * launch_scale)
    layer = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    pygame.gfxdraw.filled_polygon(layer, points, (18, 18, 18, opacity))
    pygame.gfxdraw.aapolygon(layer, points, (18, 18, 18, opacity))
    screen.blit(layer, (0, 0))

    if blocked:
        bubble = pygame.Rect(tile.right - 2, tile.top - 24, 92, 30)
        draw_brutal_card(screen, bubble, BLACK, 5, 3, 2)
        draw_centered_text(screen, "BLOCKED!", get_font(12, True), WHITE, bubble.center)


def draw_game_screen(screen, level, level_number, arrows, mistakes_left, back_button, restart_button, feedback_message, blocked_arrow, pause_button=None):
    screen.fill(CREAM)
    draw_header(screen, level_number, len(arrows), mistakes_left, level["max_mistakes"], restart_button, pause_button, blocked_arrow is not None)
    draw_board(screen, level["rows"], level["cols"])
    mouse = pygame.mouse.get_pos()
    hovered = get_grid_position(screen, mouse, level["rows"], level["cols"])
    for arrow in arrows:
        draw_arrow(screen, arrow, arrow is blocked_arrow, hovered == (arrow.row, arrow.col))
    message = feedback_message or "PICK AN ARROW · CHECK THE PATH · POP IT OUT"
    color = CORAL if blocked_arrow else BLACK
    draw_centered_text(screen, message, get_font(15, True), color, (screen.get_width() // 2, screen.get_height() - 22))
    back_button.draw(screen, mouse)


def draw_result_screen(screen, title, message, title_color, primary_button, home_button, stats_text="", secondary_button=None):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((18, 18, 18, 128))
    screen.blit(overlay, (0, 0))
    width, _ = screen.get_size()
    clear = "通关" in title or "全部" in title
    modal = pygame.Rect(width // 2 - 275, 145, 550, 395)
    draw_brutal_card(screen, modal, ACID_GREEN if clear else CORAL, 10, 10, 4)
    heading = "LEVEL CLEAR!" if clear else "GAME OVER!"
    draw_centered_text(screen, heading, get_font(46, True), BLACK, (width // 2, 220))
    draw_centered_text(screen, message, get_font(19, True), BLACK, (width // 2, 285))
    if stats_text:
        stats = pygame.Rect(width // 2 - 180, 315, 360, 46)
        draw_brutal_card(screen, stats, WHITE, 6, 4, 3)
        draw_centered_text(screen, stats_text, get_font(16, True), BLACK, stats.center)
    primary_button.draw(screen, pygame.mouse.get_pos())
    if secondary_button:
        secondary_button.draw(screen, pygame.mouse.get_pos())
    home_button.draw(screen, pygame.mouse.get_pos())
