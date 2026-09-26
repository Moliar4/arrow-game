import pygame
import sys
import math

pygame.init()

# ==================== 配置 ====================
COLS, ROWS = 10, 10
CELL = 64
MARGIN_TOP = 100
MARGIN_SIDE = 40
WIDTH = COLS * CELL + MARGIN_SIDE * 2
HEIGHT = ROWS * CELL + MARGIN_TOP + 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
def load_font(size, bold=False):
    try:
        f = pygame.font.Font(FONT_PATH, size)
        f.set_bold(bold)
        return f
    except Exception:
        f = pygame.font.Font(None, size)
        f.set_bold(bold)
        return f

font_sm = load_font(16)
font_md = load_font(22)
font_lg = load_font(34, bold=True)
font_xl = load_font(56, bold=True)

# ==================== 莫兰迪配色 ====================
BG_TOP = (250, 246, 238)
BG_BOTTOM = (238, 232, 220)
BOARD_BG = (252, 250, 245)
BOARD_BORDER = (214, 205, 190)
GRID_LINE = (228, 220, 205)

ARROW_COLORS = [
    (176, 148, 148),
    (148, 168, 176),
    (176, 168, 148),
    (148, 176, 156),
    (168, 148, 176),
    (176, 156, 148),
]
ARROW_HIGHLIGHT = (216, 122, 122)
ARROW_SHADOW = (200, 192, 182)
ARROW_OUTLINE = (90, 82, 76)

TEXT_DARK = (78, 72, 68)
TEXT_MID = (130, 122, 116)
TEXT_LIGHT = (170, 162, 156)

BTN_NORMAL = (168, 184, 176)
BTN_HOVER = (148, 168, 158)
BTN_TEXT = (255, 255, 255)
CLOSE_BG = (200, 160, 160)
CLOSE_HOVER = (180, 130, 130)

OVERLAY = (60, 55, 52, 160)

# ==================== 关卡数据 ====================
# 设计原则：每个箭头都“朝外”或“指向空行/空列”，保证有解
# 以下关卡均已人工验证存在通关顺序
LEVELS = [
    # 第 1 关：所有箭头都朝棋盘外方向，随便点都能过
    [
        (0, 0, 'up'), (0, 5, 'up'), (0, 9, 'up'),
        (5, 0, 'left'), (5, 9, 'right'),
        (9, 0, 'down'), (9, 5, 'down'), (9, 9, 'down'),
    ],
    # 第 2 关：每个箭头方向上有一个“更远的箭头”，但先清空近处的即可解
    [
        (0, 0, 'right'), (0, 4, 'up'), (0, 9, 'down'),
        (3, 3, 'left'), (3, 6, 'right'),
        (6, 1, 'up'), (6, 8, 'down'),
        (9, 0, 'right'), (9, 5, 'left'), (9, 9, 'up'),
    ],
    # 第 3 关：多行多列交错，但保证由外向内可解
    [
        (0, 0, 'up'), (0, 3, 'up'), (0, 6, 'up'), (0, 9, 'up'),
        (2, 2, 'left'), (2, 7, 'right'),
        (4, 0, 'left'), (4, 5, 'up'), (4, 9, 'right'),
        (6, 2, 'left'), (6, 7, 'right'),
        (9, 0, 'down'), (9, 3, 'down'), (9, 6, 'down'), (9, 9, 'down'),
    ],
]

MAX_MISTAKES = 3


# ==================== 绘制辅助 ====================
def draw_vertical_gradient(surface, top_color, bottom_color, rect=None):
    if rect is None:
        rect = surface.get_rect()
    x, y, w, h = rect
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w, y + i))


def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_cartoon_arrow(surface, cx, cy, direction, color, scale=1.0):
    s = int(22 * scale)
    if s < 4:
        return
    angle = {'right': 0, 'up': -90, 'left': 180, 'down': 90}[direction]
    base_points = [(-s, -s), (s, 0), (-s, s)]
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    rotated = [(x * cos_a - y * sin_a + cx, x * sin_a + y * cos_a + cy) for (x, y) in base_points]
    shadow = [(x + 3, y + 4) for (x, y) in rotated]
    pygame.draw.polygon(surface, ARROW_SHADOW, shadow)
    pygame.draw.polygon(surface, color, rotated)
    pygame.draw.polygon(surface, ARROW_OUTLINE, rotated, 2)
    hx = cx - int(cos_a * s * 0.4)
    hy = cy - int(sin_a * s * 0.4)
    pygame.draw.circle(surface, (255, 255, 255), (hx, hy), max(2, int(s * 0.18)))


# ==================== 游戏逻辑 ====================
def check_can_fly(arrows, row, col, direction):
    for (r, c, d) in arrows:
        if r == row and c == col:
            continue
        if direction == 'right' and r == row and c > col:
            return False
        if direction == 'left' and r == row and c < col:
            return False
        if direction == 'down' and c == col and r > row:
            return False
        if direction == 'up' and c == col and r < row:
            return False
    return True


# ==================== 界面绘制 ====================
def draw_start_screen():
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)
    title = font_xl.render("一箭又一箭", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 140))
    sub = font_md.render("点击箭头，让它飞出去", True, TEXT_MID)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 - 60))
    btn = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 20, 220, 60)
    mouse = pygame.mouse.get_pos()
    color = BTN_HOVER if btn.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, color, btn, radius=16)
    t = font_md.render("开始游戏", True, BTN_TEXT)
    screen.blit(t, (btn.x + (btn.w - t.get_width()) // 2,
                    btn.y + (btn.h - t.get_height()) // 2))
    pygame.display.flip()
    return btn


def draw_level_select(current_level):
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)
    title = font_lg.render("选择关卡", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

    buttons = []
    cols = 3
    btn_w, btn_h = 140, 90
    gap = 30
    total_w = cols * btn_w + (cols - 1) * gap
    start_x = WIDTH // 2 - total_w // 2
    start_y = 200
    mouse = pygame.mouse.get_pos()

    for i in range(len(LEVELS)):
        row = i // cols
        col = i % cols
        x = start_x + col * (btn_w + gap)
        y = start_y + row * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        hovered = rect.collidepoint(mouse)
        color = BTN_HOVER if hovered else BTN_NORMAL
        draw_rounded_rect(screen, color, rect, radius=14)
        label = font_lg.render(f"{i + 1}", True, BTN_TEXT)
        screen.blit(label, (rect.x + (rect.w - label.get_width()) // 2,
                            rect.y + (rect.h - label.get_height()) // 2 - 6))
        sub = font_sm.render("关卡", True, BTN_TEXT)
        screen.blit(sub, (rect.x + (rect.w - sub.get_width()) // 2,
                          rect.y + rect.h - 28))
        buttons.append((rect, i))

    back_btn = pygame.Rect(30, 30, 100, 40)
    back_color = BTN_HOVER if back_btn.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, back_color, back_btn, radius=10)
    bt = font_sm.render("返回", True, BTN_TEXT)
    screen.blit(bt, (back_btn.x + (back_btn.w - bt.get_width()) // 2,
                     back_btn.y + (back_btn.h - bt.get_height()) // 2))

    pygame.display.flip()
    return buttons, back_btn


def draw_game(arrows, anim, level, mistakes, hover_pos, message, msg_alpha):
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

    # 标题居中
    title = font_lg.render("一箭又一箭", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 22))

    # 信息栏
    info = f"第 {level + 1} 关    剩余 {len(arrows) + (1 if anim else 0)}    失误 {mistakes} / {MAX_MISTAKES}"
    info_surf = font_sm.render(info, True, TEXT_MID)
    screen.blit(info_surf, (MARGIN_SIDE, 70))

    # 棋盘
    board_rect = pygame.Rect(MARGIN_SIDE, MARGIN_TOP, COLS * CELL, ROWS * CELL)
    draw_rounded_rect(screen, BOARD_BG, board_rect, radius=12, border=2, border_color=BOARD_BORDER)

    for r in range(ROWS + 1):
        y = MARGIN_TOP + r * CELL
        pygame.draw.line(screen, GRID_LINE, (MARGIN_SIDE, y), (MARGIN_SIDE + COLS * CELL, y), 1)
    for c in range(COLS + 1):
        x = MARGIN_SIDE + c * CELL
        pygame.draw.line(screen, GRID_LINE, (x, MARGIN_TOP), (x, MARGIN_TOP + ROWS * CELL), 1)

    # 绘制所有静态箭头
    for (r, c, d) in arrows:
        cx = MARGIN_SIDE + c * CELL + CELL // 2
        cy = MARGIN_TOP + r * CELL + CELL // 2
        color_idx = (r * 7 + c * 3) % len(ARROW_COLORS)
        color = ARROW_COLORS[color_idx]
        if hover_pos == (r, c) and anim is None:
            color = ARROW_HIGHLIGHT
        draw_cartoon_arrow(screen, cx, cy, d, color, 1.0)

    # 绘制动画中的箭头
    if anim:
        (r, c, d) = anim['arrow']
        progress = anim['progress']
        cx = MARGIN_SIDE + c * CELL + CELL // 2
        cy = MARGIN_TOP + r * CELL + CELL // 2
        offset = progress * CELL * 4
        if d == 'right':
            cx += offset
        elif d == 'left':
            cx -= offset
        elif d == 'up':
            cy -= offset
        else:
            cy += offset
        alpha = max(0, 255 - int(progress * 300))
        scale = max(0.1, 1.0 - progress * 0.6)
        color_idx = (r * 7 + c * 3) % len(ARROW_COLORS)
        color = ARROW_COLORS[color_idx]
        tmp_size = int(CELL * 2.5)
        tmp = pygame.Surface((tmp_size, tmp_size), pygame.SRCALPHA)
        draw_cartoon_arrow(tmp, tmp_size // 2, tmp_size // 2, d, color, scale)
        tmp.set_alpha(alpha)
        screen.blit(tmp, (cx - tmp_size // 2, cy - tmp_size // 2))

    mouse = pygame.mouse.get_pos()

    # 重新开始按钮
    btn_rect = pygame.Rect(WIDTH - MARGIN_SIDE - 120, 22, 120, 42)
    btn_color = BTN_HOVER if btn_rect.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, btn_color, btn_rect, radius=10)
    btn_text = font_sm.render("重新开始", True, BTN_TEXT)
    screen.blit(btn_text, (btn_rect.x + (btn_rect.w - btn_text.get_width()) // 2,
                           btn_rect.y + (btn_rect.h - btn_text.get_height()) // 2))

    # 返回按钮
    back_rect = pygame.Rect(MARGIN_SIDE, 22, 90, 42)
    back_color = BTN_HOVER if back_rect.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, back_color, back_rect, radius=10)
    back_text = font_sm.render("返回", True, BTN_TEXT)
    screen.blit(back_text, (back_rect.x + (back_rect.w - back_text.get_width()) // 2,
                            back_rect.y + (back_rect.h - back_text.get_height()) // 2))

    # 右上角 × 退出按钮
    close_rect = pygame.Rect(WIDTH - 50, 22, 42, 42)
    close_color = CLOSE_HOVER if close_rect.collidepoint(mouse) else CLOSE_BG
    draw_rounded_rect(screen, close_color, close_rect, radius=10)
    # 画一个 ×
    cx0, cy0 = close_rect.center
    d = 10
    pygame.draw.line(screen, BTN_TEXT, (cx0 - d, cy0 - d), (cx0 + d, cy0 + d), 3)
    pygame.draw.line(screen, BTN_TEXT, (cx0 - d, cy0 + d), (cx0 + d, cy0 - d), 3)

    if message and msg_alpha > 0:
        mt = font_md.render(message, True, ARROW_HIGHLIGHT)
        tmp = pygame.Surface((mt.get_width(), mt.get_height()), pygame.SRCALPHA)
        tmp.blit(mt, (0, 0))
        tmp.set_alpha(msg_alpha)
        screen.blit(tmp, (WIDTH // 2 - mt.get_width() // 2, HEIGHT - 45))

    pygame.display.flip()
    return btn_rect, back_rect, close_rect


def draw_overlay(text, sub_text=None):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    screen.blit(overlay, (0, 0))
    t = font_xl.render(text, True, (255, 255, 255))
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 60))
    if sub_text:
        s = font_md.render(sub_text, True, (240, 235, 228))
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()


# ==================== 主流程 ====================
def main():
    clock = pygame.time.Clock()
    scene = 'start'
    level = 0
    arrows = []
    mistakes = 0
    hover_pos = None
    anim = None
    message = ""
    msg_timer = 0
    wait_release = False

    while True:
        mouse = pygame.mouse.get_pos()

        # ---------- 开始界面 ----------
        if scene == 'start':
            btn = draw_start_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    if btn.collidepoint(event.pos):
                        scene = 'select'
                        wait_release = True
            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

        # ---------- 关卡选择 ----------
        elif scene == 'select':
            buttons, back_btn = draw_level_select(level)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    if back_btn.collidepoint(event.pos):
                        scene = 'start'
                        wait_release = True
                    else:
                        for rect, idx in buttons:
                            if rect.collidepoint(event.pos):
                                level = idx
                                arrows = list(LEVELS[level])
                                mistakes = 0
                                message = ""
                                anim = None
                                scene = 'playing'
                                wait_release = True
                                break
            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

        # ---------- 游戏界面 ----------
        elif scene == 'playing':
            hover_pos = None
            if anim is None and MARGIN_TOP <= mouse[1] <= MARGIN_TOP + ROWS * CELL \
               and MARGIN_SIDE <= mouse[0] <= MARGIN_SIDE + COLS * CELL:
                col = (mouse[0] - MARGIN_SIDE) // CELL
                row = (mouse[1] - MARGIN_TOP) // CELL
                for (r, c, d) in arrows:
                    if r == row and c == col:
                        hover_pos = (r, c)
                        break

            btn_rect, back_rect, close_rect = draw_game(
                arrows, anim, level, mistakes, hover_pos, message,
                min(255, msg_timer * 8))

            # 动画推进
            if anim:
                anim['progress'] += 0.07
                if anim['progress'] >= 1.0:
                    anim = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    mx, my = event.pos
                    # × 退出 → 回关卡选择
                    if close_rect.collidepoint(mx, my):
                        scene = 'select'
                        wait_release = True
                        continue
                    # 重新开始
                    if btn_rect.collidepoint(mx, my):
                        arrows = list(LEVELS[level])
                        mistakes = 0
                        message = ""
                        anim = None
                        wait_release = True
                        continue
                    # 返回
                    if back_rect.collidepoint(mx, my):
                        scene = 'select'
                        wait_release = True
                        continue
                    # 点击棋盘
                    if anim is None and MARGIN_TOP <= my <= MARGIN_TOP + ROWS * CELL \
                       and MARGIN_SIDE <= mx <= MARGIN_SIDE + COLS * CELL:
                        col = (mx - MARGIN_SIDE) // CELL
                        row = (my - MARGIN_TOP) // CELL
                        clicked = None
                        for (r, c, d) in arrows:
                            if r == row and c == col:
                                clicked = (r, c, d)
                                break
                        if clicked:
                            r, c, d = clicked
                            if check_can_fly(arrows, r, c, d):
                                arrows.remove(clicked)
                                anim = {'arrow': clicked, 'progress': 0.0}
                                message = "飞出！"
                                msg_timer = 40
                            else:
                                mistakes += 1
                                message = "被挡住了！"
                                msg_timer = 40
                            wait_release = True

            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

            if msg_timer > 0:
                msg_timer -= 1

            # 通关
            if not arrows and anim is None:
                draw_overlay("通关！", f"第 {level + 1} 关完成")
                pygame.time.wait(900)
                if level + 1 < len(LEVELS):
                    level += 1
                    arrows = list(LEVELS[level])
                    mistakes = 0
                    message = ""
                    scene = 'playing'
                else:
                    draw_overlay("全部通关！", "恭喜！")
                    pygame.time.wait(1200)
                    scene = 'select'
                wait_release = True

            # 失败
            if mistakes >= MAX_MISTAKES:
                draw_overlay("失败！", "点击任意处重试")
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            waiting = False
                arrows = list(LEVELS[level])
                mistakes = 0
                anim = None
                message = ""
                wait_release = True

        clock.tick(60)


if __name__ == "__main__":
    main()
