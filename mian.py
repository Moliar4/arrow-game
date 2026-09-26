import pygame
import sys
import math
import json
import os
import time

pygame.init()

# ==================== 配置 ====================
COLS, ROWS = 7, 7
CELL = 78
MARGIN_TOP = 130
MARGIN_SIDE = 60
WIDTH = COLS * CELL + MARGIN_SIDE * 2
HEIGHT = ROWS * CELL + MARGIN_TOP + 90
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

font_xs = load_font(14)
font_sm = load_font(16)
font_md = load_font(22)
font_lg = load_font(30, bold=True)
font_xl = load_font(48, bold=True)

# ==================== 莫兰迪配色 ====================
BG_TOP = (250, 246, 238)
BG_BOTTOM = (238, 232, 220)
BOARD_BG = (252, 250, 245)
BOARD_BORDER = (214, 205, 190)
CELL_FILL = (255, 253, 250)
CELL_LINE = (232, 225, 212)

ARROW_COLORS = [
    (196, 138, 138), (138, 168, 196), (196, 178, 128), (138, 186, 158),
    (178, 148, 196), (206, 158, 128), (148, 178, 178), (196, 158, 168),
]
ARROW_HIGHLIGHT = (232, 100, 100)
ARROW_HIT = (224, 60, 60)
ARROW_SHADOW = (210, 202, 192)
ARROW_OUTLINE = (85, 78, 72)

TEXT_DARK = (78, 72, 68)
TEXT_MID = (130, 122, 116)
TEXT_LIGHT = (170, 162, 156)

BTN_NORMAL = (168, 184, 176)
BTN_HOVER = (148, 168, 158)
BTN_TEXT = (255, 255, 255)
BTN_ALT = (200, 178, 158)
BTN_ALT_HOVER = (180, 158, 138)
CLOSE_BG = (208, 160, 160)
CLOSE_HOVER = (188, 130, 130)

PANEL_BG = (255, 252, 246)
PANEL_BORDER = (218, 208, 192)

OVERLAY = (60, 55, 52, 160)
DIALOG_BG = (252, 250, 245)
DIALOG_BORDER = (200, 190, 178)

STAR_GOLD = (232, 196, 100)
STAR_GREY = (210, 205, 195)

# ==================== 进度存档 ====================
SAVE_FILE = "progress.json"

def load_progress():
    """读取进度，不存在则返回默认"""
    default = {
        "unlocked": 1,        # 已解锁到第几关（1 表示只解锁第 1 关）
        "best_scores": {},    # {"1": 850, "2": 720, ...}
        "best_stars": {},     # {"1": 3, "2": 2, ...}
    }
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k in default:
                    if k not in data:
                        data[k] = default[k]
                return data
        except Exception:
            return default
    return default


def save_progress(progress):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ==================== 关卡数据（6 关） ====================
LEVELS = [
    # 第 1 关
    [
        (0, 1, 'up'), (0, 3, 'up'), (0, 5, 'up'),
        (6, 1, 'down'), (6, 3, 'down'), (6, 5, 'down'),
        (2, 0, 'left'), (4, 0, 'left'),
        (2, 6, 'right'), (4, 6, 'right'),
        (3, 2, 'left'), (3, 4, 'right'),
        (5, 2, 'left'), (5, 4, 'right'),
        (4, 3, 'up'),
    ],
    # 第 2 关
    [
        (0, 1, 'up'), (0, 3, 'up'), (0, 5, 'up'),
        (6, 1, 'down'), (6, 3, 'down'), (6, 5, 'down'),
        (1, 0, 'left'), (3, 0, 'left'), (5, 0, 'left'),
        (1, 6, 'right'), (3, 6, 'right'), (5, 6, 'right'),
        (2, 2, 'left'), (2, 4, 'right'),
        (4, 2, 'left'), (4, 4, 'right'),
        (3, 3, 'up'),
    ],
    # 第 3 关
    [
        (0, 0, 'up'), (0, 2, 'up'), (0, 4, 'up'), (0, 6, 'up'),
        (6, 0, 'down'), (6, 2, 'down'), (6, 4, 'down'), (6, 6, 'down'),
        (1, 0, 'left'), (3, 0, 'left'), (5, 0, 'left'),
        (1, 6, 'right'), (3, 6, 'right'), (5, 6, 'right'),
        (1, 3, 'up'), (3, 3, 'up'), (5, 3, 'up'),
        (3, 1, 'left'), (3, 5, 'right'),
        (2, 2, 'left'), (2, 4, 'right'),
        (4, 2, 'left'), (4, 4, 'right'),
    ],
    # 第 4 关
    [
        (0, 1, 'up'), (0, 4, 'up'),
        (6, 1, 'down'), (6, 4, 'down'),
        (2, 0, 'left'), (4, 0, 'left'),
        (2, 6, 'right'), (4, 6, 'right'),
        (1, 2, 'left'), (1, 4, 'right'),
        (3, 2, 'up'), (3, 4, 'up'),
        (5, 2, 'down'), (5, 4, 'down'),
        (2, 3, 'left'), (4, 3, 'right'),
        (3, 3, 'up'),
    ],
    # 第 5 关
    [
        (0, 0, 'up'), (0, 3, 'up'), (0, 6, 'up'),
        (6, 0, 'down'), (6, 3, 'down'), (6, 6, 'down'),
        (1, 0, 'left'), (3, 0, 'left'), (5, 0, 'left'),
        (1, 6, 'right'), (3, 6, 'right'), (5, 6, 'right'),
        (2, 1, 'left'), (2, 5, 'right'),
        (4, 1, 'left'), (4, 5, 'right'),
        (3, 2, 'up'), (3, 4, 'up'),
        (2, 3, 'left'), (4, 3, 'right'),
        (3, 3, 'up'),
    ],
    # 第 6 关
    [
        (0, 0, 'up'), (0, 2, 'up'), (0, 4, 'up'), (0, 6, 'up'),
        (6, 0, 'down'), (6, 2, 'down'), (6, 4, 'down'), (6, 6, 'down'),
        (1, 0, 'left'), (5, 0, 'left'),
        (1, 6, 'right'), (5, 6, 'right'),
        (2, 2, 'up'), (2, 4, 'up'),
        (4, 2, 'down'), (4, 4, 'down'),
        (3, 1, 'left'), (3, 5, 'right'),
        (2, 3, 'up'), (4, 3, 'down'),
        (3, 3, 'up'),
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


def rounded_polygon(surface, color, points, radius):
    n = len(points)
    if n < 3 or radius <= 0:
        pygame.draw.polygon(surface, color, points)
        return
    new_points = []
    for i in range(n):
        p_prev = points[(i - 1) % n]
        p_curr = points[i]
        p_next = points[(i + 1) % n]
        v1x = p_prev[0] - p_curr[0]
        v1y = p_prev[1] - p_curr[1]
        v2x = p_next[0] - p_curr[0]
        v2y = p_next[1] - p_curr[1]
        len1 = math.hypot(v1x, v1y) or 1
        len2 = math.hypot(v2x, v2y) or 1
        u1x, u1y = v1x / len1, v1y / len1
        u2x, u2y = v2x / len2, v2y / len2
        r = min(radius, len1 / 2, len2 / 2)
        a = (p_curr[0] + u1x * r, p_curr[1] + u1y * r)
        b = (p_curr[0] + u2x * r, p_curr[1] + u2y * r)
        steps = 6
        for t in range(steps + 1):
            tt = t / steps
            x = (1 - tt) ** 2 * a[0] + 2 * (1 - tt) * tt * p_curr[0] + tt ** 2 * b[0]
            y = (1 - tt) ** 2 * a[1] + 2 * (1 - tt) * tt * p_curr[1] + tt ** 2 * b[1]
            new_points.append((x, y))
    pygame.draw.polygon(surface, color, new_points)


def draw_cartoon_arrow(surface, cx, cy, direction, color, scale=1.0, wobble=0.0):
    s = 24 * scale
    if s < 4:
        return
    angle = {'right': 0, 'up': -90, 'left': 180, 'down': 90}[direction]
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)

    def rot(px, py):
        return (px * cos_a - py * sin_a + cx + wobble, px * sin_a + py * cos_a + cy)

    outline = [
        rot(-s, -s * 0.3), rot(-s * 0.1, -s * 0.3), rot(-s * 0.1, -s * 0.65),
        rot(s, 0),
        rot(-s * 0.1, s * 0.65), rot(-s * 0.1, s * 0.3), rot(-s, s * 0.3),
    ]
    shadow = [(x + 3, y + 4) for (x, y) in outline]
    rounded_polygon(surface, ARROW_SHADOW, shadow, s * 0.35)
    rounded_polygon(surface, color, outline, s * 0.35)
    pygame.draw.polygon(surface, ARROW_OUTLINE, outline, 2)
    


def draw_arrow_button(surface, rect, text, mouse, color=None, hover_color=None):
    if color is None:
        color = BTN_NORMAL
    if hover_color is None:
        hover_color = BTN_HOVER
    c = hover_color if rect.collidepoint(mouse) else color
    draw_rounded_rect(surface, c, rect, radius=rect.height // 2)
    t = font_md.render(text, True, BTN_TEXT)
    surface.blit(t, (rect.x + (rect.w - t.get_width()) // 2,
                     rect.y + (rect.h - t.get_height()) // 2))


def draw_close_button(surface):
    close_rect = pygame.Rect(WIDTH - 58, 18, 44, 44)
    mouse = pygame.mouse.get_pos()
    color = CLOSE_HOVER if close_rect.collidepoint(mouse) else CLOSE_BG
    draw_rounded_rect(surface, color, close_rect, radius=14)
    cx0, cy0 = close_rect.center
    d = 10
    pygame.draw.line(surface, BTN_TEXT, (cx0 - d, cy0 - d), (cx0 + d, cy0 + d), 3)
    pygame.draw.line(surface, BTN_TEXT, (cx0 - d, cy0 + d), (cx0 + d, cy0 - d), 3)
    return close_rect


def draw_star(surface, cx, cy, size, filled):
    """五角星"""
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = size if i % 2 == 0 else size * 0.45
        x = cx + r * math.cos(angle)
        y = cy - r * math.sin(angle)
        points.append((x, y))
    color = STAR_GOLD if filled else STAR_GREY
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, ARROW_OUTLINE, points, 2)


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


def find_blocker(arrows, row, col, direction):
    best = None
    for (r, c, d) in arrows:
        if r == row and c == col:
            continue
        if direction == 'right' and r == row and c > col:
            if best is None or c < best[1]:
                best = (r, c)
        elif direction == 'left' and r == row and c < col:
            if best is None or c > best[1]:
                best = (r, c)
        elif direction == 'down' and c == col and r > row:
            if best is None or r < best[0]:
                best = (r, c)
        elif direction == 'up' and c == col and r < row:
            if best is None or r > best[0]:
                best = (r, c)
    return best


def calc_score(elapsed, mistakes):
    """得分公式：基础 1000，每用 1 秒扣 20，每失误 1 次扣 100，最低 0"""
    score = max(0, int(1000 - elapsed * 20 - mistakes * 100))
    return score


def calc_stars(elapsed, mistakes):
    """星级：3 星 / 2 星 / 1 星"""
    if elapsed <= 20 and mistakes == 0:
        return 3
    if elapsed <= 40 and mistakes <= 1:
        return 2
    return 1


# ==================== 退出确认弹窗 ====================
def draw_quit_dialog():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    screen.blit(overlay, (0, 0))
    dw, dh = 420, 220
    dx = WIDTH // 2 - dw // 2
    dy = HEIGHT // 2 - dh // 2
    dialog = pygame.Rect(dx, dy, dw, dh)
    draw_rounded_rect(screen, DIALOG_BG, dialog, radius=20, border=2, border_color=DIALOG_BORDER)
    title = font_lg.render("确定退出游戏吗？", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, dy + 40))
    sub = font_sm.render("退出后进度将不会保存", True, TEXT_MID)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, dy + 90))
    mouse = pygame.mouse.get_pos()
    yes_rect = pygame.Rect(WIDTH // 2 - 150, dy + 140, 120, 48)
    yes_color = CLOSE_HOVER if yes_rect.collidepoint(mouse) else CLOSE_BG
    draw_rounded_rect(screen, yes_color, yes_rect, radius=24)
    yt = font_md.render("退出", True, BTN_TEXT)
    screen.blit(yt, (yes_rect.x + (yes_rect.w - yt.get_width()) // 2,
                     yes_rect.y + (yes_rect.h - yt.get_height()) // 2))
    no_rect = pygame.Rect(WIDTH // 2 + 30, dy + 140, 120, 48)
    no_color = BTN_HOVER if no_rect.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, no_color, no_rect, radius=24)
    nt = font_md.render("取消", True, BTN_TEXT)
    screen.blit(nt, (no_rect.x + (no_rect.w - nt.get_width()) // 2,
                     no_rect.y + (no_rect.h - nt.get_height()) // 2))
    pygame.display.flip()
    return yes_rect, no_rect


# ==================== 结果弹窗 ====================
def draw_result_dialog(title, sub_text, buttons, color,
                       elapsed=None, mistakes=None, score=None, stars=None):
    """结果弹窗，支持显示用时/失误/得分/星级"""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY)
    screen.blit(overlay, (0, 0))

    dh = 360 if score is not None else 300
    dw = 500
    dx = WIDTH // 2 - dw // 2
    dy = HEIGHT // 2 - dh // 2
    dialog = pygame.Rect(dx, dy, dw, dh)
    draw_rounded_rect(screen, DIALOG_BG, dialog, radius=24, border=3, border_color=color)

    # 顶部装饰条
    top_bar = pygame.Rect(dialog.x + 20, dialog.y + 18, dialog.w - 40, 8)
    draw_rounded_rect(screen, color, top_bar, radius=4)

    # 标题
    t = font_xl.render(title, True, TEXT_DARK)
    screen.blit(t, (WIDTH // 2 - t.get_width() // 2, dy + 42))

    # 副标题
    if sub_text:
        s = font_md.render(sub_text, True, TEXT_MID)
        screen.blit(s, (WIDTH // 2 - s.get_width() // 2, dy + 105))

    # 统计信息
    if score is not None:
        # 星级
        star_y = dy + 155
        star_size = 22
        star_gap = 60
        start_x = WIDTH // 2 - star_gap
        for i in range(3):
            draw_star(screen, start_x + i * star_gap, star_y, star_size, i < stars)

        # 用时、失误、得分
        info1 = font_sm.render(f"用时 {elapsed:.1f} 秒    失误 {mistakes} 次", True, TEXT_MID)
        screen.blit(info1, (WIDTH // 2 - info1.get_width() // 2, dy + 195))
        info2 = font_lg.render(f"得分 {score}", True, color)
        screen.blit(info2, (WIDTH // 2 - info2.get_width() // 2, dy + 225))

    # 按钮
    mouse = pygame.mouse.get_pos()
    btn_rects = []
    n = len(buttons)
    btn_w, btn_h = 130, 48
    gap = 18
    total_w = n * btn_w + (n - 1) * gap
    start_x = WIDTH // 2 - total_w // 2
    btn_y = dy + dh - 78

    for i, (text, is_primary) in enumerate(buttons):
        x = start_x + i * (btn_w + gap)
        rect = pygame.Rect(x, btn_y, btn_w, btn_h)
        base_color = color if is_primary else BTN_ALT
        hover_color = color if is_primary else BTN_ALT_HOVER
        c = hover_color if rect.collidepoint(mouse) else base_color
        draw_rounded_rect(screen, c, rect, radius=24)
        t2 = font_sm.render(text, True, BTN_TEXT)
        screen.blit(t2, (rect.x + (rect.w - t2.get_width()) // 2,
                         rect.y + (rect.h - t2.get_height()) // 2))
        btn_rects.append(rect)

    pygame.display.flip()
    return btn_rects


# ==================== 主页面 ====================
def draw_main_screen(music_on, volume, progress):
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)
    title = font_xl.render("一箭又一箭", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    sub = font_sm.render("点击箭头，让它飞出去", True, TEXT_MID)
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 125))

    mouse = pygame.mouse.get_pos()

    panel = pygame.Rect(WIDTH // 2 - 240, 175, 480, 350)
    draw_rounded_rect(screen, PANEL_BG, panel, radius=24, border=2, border_color=PANEL_BORDER)

    ptitle = font_md.render("设 置", True, TEXT_DARK)
    screen.blit(ptitle, (WIDTH // 2 - ptitle.get_width() // 2, panel.y + 18))

    # 音乐
    music_label = font_sm.render("音乐", True, TEXT_DARK)
    screen.blit(music_label, (panel.x + 40, panel.y + 75))
    music_btn = pygame.Rect(panel.right - 160, panel.y + 68, 120, 40)
    mc = BTN_HOVER if music_btn.collidepoint(mouse) else BTN_NORMAL
    draw_rounded_rect(screen, mc, music_btn, radius=20)
    mt = font_sm.render("开" if music_on else "关", True, BTN_TEXT)
    screen.blit(mt, (music_btn.x + (music_btn.w - mt.get_width()) // 2,
                     music_btn.y + (music_btn.h - mt.get_height()) // 2))

    # 音量
    vol_label = font_sm.render("音量", True, TEXT_DARK)
    screen.blit(vol_label, (panel.x + 40, panel.y + 135))
    vol_minus = pygame.Rect(panel.right - 220, panel.y + 128, 44, 40)
    vol_plus = pygame.Rect(panel.right - 60, panel.y + 128, 44, 40)
    for r, txt in [(vol_minus, "-"), (vol_plus, "+")]:
        c = BTN_HOVER if r.collidepoint(mouse) else BTN_NORMAL
        draw_rounded_rect(screen, c, r, radius=20)
        t = font_md.render(txt, True, BTN_TEXT)
        screen.blit(t, (r.x + (r.w - t.get_width()) // 2,
                        r.y + (r.h - t.get_height()) // 2))





        
    bar_rect = pygame.Rect(panel.right - 170, panel.y + 138, 100, 20)
    draw_rounded_rect(screen, (230, 224, 214), bar_rect, radius=10)
    fill_w = int(bar_rect.w * volume / 100)
    if fill_w > 0:
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.h)
        draw_rounded_rect(screen, BTN_NORMAL, fill_rect, radius=10)
    # 百分比显示在进度条内部居中
    vol_text = font_xs.render(f"{volume}%", True, TEXT_DARK)
    screen.blit(vol_text, (bar_rect.x + (bar_rect.w - vol_text.get_width()) // 2,
                           bar_rect.y + (bar_rect.h - vol_text.get_height()) // 2))




    

    # 进度显示
    prog_text = font_sm.render(
        f"已解锁关卡：{progress.get('unlocked', 1)} / {len(LEVELS)}",
        True, TEXT_MID)
    screen.blit(prog_text, (WIDTH // 2 - prog_text.get_width() // 2, panel.y + 195))

    # 开始按钮
    start_btn = pygame.Rect(WIDTH // 2 - 130, panel.y + 240, 260, 56)
    draw_arrow_button(screen, start_btn, "开 始 游 戏", mouse)

    close_rect = draw_close_button(screen)
    pygame.display.flip()
    return start_btn, music_btn, vol_minus, vol_plus, close_rect


# ==================== 关卡选择 ====================
def draw_level_select(level, progress):
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)
    title = font_lg.render("选择关卡", True, TEXT_DARK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

    mouse = pygame.mouse.get_pos()
    buttons = []
    cols = 3
    btn_w, btn_h = 130, 100
    gap = 26
    total_w = cols * btn_w + (cols - 1) * gap
    start_x = WIDTH // 2 - total_w // 2
    start_y = 100

    unlocked = progress.get("unlocked", 1)
    best_stars = progress.get("best_stars", {})

    for i in range(len(LEVELS)):
        row = i // cols
        col = i % cols
        x = start_x + col * (btn_w + gap)
        y = start_y + row * (btn_h + gap)
        rect = pygame.Rect(x, y, btn_w, btn_h)
        hovered = rect.collidepoint(mouse)

        # 是否解锁
        is_unlocked = (i + 1) <= unlocked
        if is_unlocked:
            c = BTN_HOVER if hovered else BTN_NORMAL
        else:
            c = (210, 205, 200)  # 灰色未解锁

        draw_rounded_rect(screen, c, rect, radius=20)

        # 关卡数字
        label = font_xl.render(f"{i + 1}", True, BTN_TEXT if is_unlocked else (240, 238, 234))
        screen.blit(label, (rect.x + (rect.w - label.get_width()) // 2,
                            rect.y + 18))

        # 星级（已解锁且已玩过）
        key = str(i + 1)
        stars = best_stars.get(key, 0)
        if is_unlocked and stars > 0:
            star_size = 8
            star_gap = 20
            sx = rect.x + rect.w // 2 - star_gap
            for s in range(3):
                draw_star(screen, sx + s * star_gap, rect.y + rect.h - 22,
                          star_size, s < stars)
        elif is_unlocked:
            sub = font_xs.render("未挑战", True, BTN_TEXT)
            screen.blit(sub, (rect.x + (rect.w - sub.get_width()) // 2,
                              rect.y + rect.h - 28))
        else:
            sub = font_xs.render("未解锁", True, (240, 238, 234))
            screen.blit(sub, (rect.x + (rect.w - sub.get_width()) // 2,
                              rect.y + rect.h - 28))

        buttons.append((rect, i, is_unlocked))

    back_btn = pygame.Rect(30, 30, 100, 44)
    draw_arrow_button(screen, back_btn, "返回", mouse)

    close_rect = draw_close_button(screen)
    pygame.display.flip()
    return buttons, back_btn, close_rect


# ==================== 游戏界面 ====================
def draw_game(arrows, anim, level, mistakes, hover_pos, message, msg_alpha, elapsed):
    draw_vertical_gradient(screen, BG_TOP, BG_BOTTOM)

    level_text = font_lg.render(f"关卡 {level + 1}", True, TEXT_DARK)
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 22))

    # 顶部信息：剩余箭头 / 失误 / 计时
    remaining = len(arrows) + (1 if anim and anim['type'] == 'fly' else 0)
    remain_text = font_sm.render(f"剩余 {remaining}", True, TEXT_MID)
    mistakes_text = font_sm.render(
        f"失误 {mistakes} / {MAX_MISTAKES}", True,
        ARROW_HIT if mistakes >= MAX_MISTAKES - 1 else TEXT_MID)
    time_text = font_sm.render(f"用时 {elapsed:.1f}s", True, TEXT_MID)

    gap = 24
    total_w = remain_text.get_width() + gap + mistakes_text.get_width() + gap + time_text.get_width()
    start_x = WIDTH // 2 - total_w // 2
    screen.blit(remain_text, (start_x, 62))
    screen.blit(mistakes_text, (start_x + remain_text.get_width() + gap, 62))
    screen.blit(time_text, (start_x + remain_text.get_width() + gap
                            + mistakes_text.get_width() + gap, 62))

    # 棋盘
    board_rect = pygame.Rect(MARGIN_SIDE, MARGIN_TOP, COLS * CELL, ROWS * CELL)
    draw_rounded_rect(screen, BOARD_BG, board_rect, radius=16,
                      border=2, border_color=BOARD_BORDER)

    for r in range(ROWS):
        for c in range(COLS):
            cell_rect = pygame.Rect(
                MARGIN_SIDE + c * CELL + 4,
                MARGIN_TOP + r * CELL + 4,
                CELL - 8, CELL - 8)
            draw_rounded_rect(screen, CELL_FILL, cell_rect, radius=10)
            pygame.draw.rect(screen, CELL_LINE, cell_rect, 2, border_radius=10)

    anim_arrow = anim['arrow'] if anim else None
    for (r, c, d) in arrows:
        if anim_arrow == (r, c, d):
            continue
        cx = MARGIN_SIDE + c * CELL + CELL // 2
        cy = MARGIN_TOP + r * CELL + CELL // 2
        color_idx = (r * 3 + c * 5) % len(ARROW_COLORS)
        color = ARROW_COLORS[color_idx]
        if hover_pos == (r, c) and anim is None:
            color = ARROW_HIGHLIGHT
            cell_rect = pygame.Rect(
                MARGIN_SIDE + c * CELL + 4,
                MARGIN_TOP + r * CELL + 4,
                CELL - 8, CELL - 8)
            pygame.draw.rect(screen, ARROW_HIGHLIGHT, cell_rect, 3, border_radius=10)
        draw_cartoon_arrow(screen, cx, cy, d, color, 1.0)

    if anim:
        (r, c, d) = anim['arrow']
        cx = MARGIN_SIDE + c * CELL + CELL // 2
        cy = MARGIN_TOP + r * CELL + CELL // 2
        color_idx = (r * 3 + c * 5) % len(ARROW_COLORS)
        base_color = ARROW_COLORS[color_idx]

        if anim['type'] == 'fly':
            progress = anim['progress']
            offset = progress * CELL * 5
            if d == 'right':
                cx += offset
            elif d == 'left':
                cx -= offset
            elif d == 'up':
                cy -= offset
            else:
                cy += offset
            alpha = max(0, 255 - int(progress * 320))
            scale = max(0.1, 1.0 - progress * 0.5)
            tmp_size = int(CELL * 3)
            tmp = pygame.Surface((tmp_size, tmp_size), pygame.SRCALPHA)
            draw_cartoon_arrow(tmp, tmp_size // 2, tmp_size // 2, d, base_color, scale)
            tmp.set_alpha(alpha)
            screen.blit(tmp, (cx - tmp_size // 2, cy - tmp_size // 2))

        elif anim['type'] == 'collide':
            progress = anim['progress']
            travel = anim.get('travel', CELL * 0.5)
            if progress < 0.4:
                t = progress / 0.4
                offset = t * travel
                color = base_color
                wobble = 0.0
            elif progress < 0.85:
                t = (progress - 0.4) / 0.45
                offset = travel
                color = ARROW_HIT
                wobble = math.sin(t * math.pi * 8) * 6 * (1 - t)
            else:
                t = (progress - 0.85) / 0.15
                offset = travel * (1 - t)
                color = ARROW_HIT
                wobble = 0.0
            if d == 'right':
                cx += offset
            elif d == 'left':
                cx -= offset
            elif d == 'up':
                cy -= offset
            else:
                cy += offset
            draw_cartoon_arrow(screen, cx, cy, d, color, 1.0, wobble=wobble)

    mouse = pygame.mouse.get_pos()

    btn_y = HEIGHT - 58
    back_btn = pygame.Rect(MARGIN_SIDE, btn_y, 110, 44)
    restart_btn = pygame.Rect(WIDTH // 2 - 70, btn_y, 140, 44)
    draw_arrow_button(screen, back_btn, "返回", mouse, BTN_ALT, BTN_ALT_HOVER)
    draw_arrow_button(screen, restart_btn, "重新开始", mouse)

    close_rect = draw_close_button(screen)

    if message and msg_alpha > 0:
        mt = font_md.render(message, True, ARROW_HIGHLIGHT)
        tmp = pygame.Surface((mt.get_width(), mt.get_height()), pygame.SRCALPHA)
        tmp.blit(mt, (0, 0))
        tmp.set_alpha(msg_alpha)
        screen.blit(tmp, (WIDTH // 2 - mt.get_width() // 2, MARGIN_TOP - 40))

    pygame.display.flip()
    return back_btn, restart_btn, close_rect


# ==================== 主流程 ====================
def main():
    clock = pygame.time.Clock()
    scene = 'main'
    level = 0
    arrows = []
    mistakes = 0
    hover_pos = None
    anim = None
    message = ""
    msg_timer = 0
    wait_release = False
    show_quit_dialog = False
    music_on = True
    volume = 60

    # 计时
    level_start_time = 0.0
    elapsed = 0.0

    # 进度
    progress = load_progress()

    while True:
        mouse = pygame.mouse.get_pos()

        # 退出确认弹窗
        if show_quit_dialog:
            yes_rect, no_rect = draw_quit_dialog()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_progress(progress)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    if yes_rect.collidepoint(event.pos):
                        save_progress(progress)
                        pygame.quit()
                        sys.exit()
                    if no_rect.collidepoint(event.pos):
                        show_quit_dialog = False
                        wait_release = True
            if not pygame.mouse.get_pressed()[0]:
                wait_release = False
            clock.tick(60)
            continue

        # 主页面
        if scene == 'main':
            start_btn, music_btn, vol_minus, vol_plus, close_rect = draw_main_screen(
                music_on, volume, progress)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_progress(progress)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    if close_rect.collidepoint(event.pos):
                        show_quit_dialog = True
                        wait_release = True
                    elif music_btn.collidepoint(event.pos):
                        music_on = not music_on
                        wait_release = True
                    elif vol_minus.collidepoint(event.pos):
                        volume = max(0, volume - 10)
                        wait_release = True
                    elif vol_plus.collidepoint(event.pos):
                        volume = min(100, volume + 10)
                        wait_release = True
                    elif start_btn.collidepoint(event.pos):
                        scene = 'select'
                        wait_release = True
            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

        # 关卡选择
        elif scene == 'select':
            buttons, back_btn, close_rect = draw_level_select(level, progress)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_progress(progress)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    if close_rect.collidepoint(event.pos):
                        show_quit_dialog = True
                        wait_release = True
                    elif back_btn.collidepoint(event.pos):
                        scene = 'main'
                        wait_release = True
                    else:
                        for rect, idx, is_unlocked in buttons:
                            if rect.collidepoint(event.pos) and is_unlocked:
                                level = idx
                                arrows = list(LEVELS[level])
                                mistakes = 0
                                message = ""
                                anim = None
                                level_start_time = time.time()
                                elapsed = 0.0
                                scene = 'playing'
                                wait_release = True
                                break
            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

        # 游戏界面
        elif scene == 'playing':
            # 更新计时
            elapsed = time.time() - level_start_time

            hover_pos = None
            if anim is None and MARGIN_TOP <= mouse[1] <= MARGIN_TOP + ROWS * CELL \
               and MARGIN_SIDE <= mouse[0] <= MARGIN_SIDE + COLS * CELL:
                col = (mouse[0] - MARGIN_SIDE) // CELL
                row = (mouse[1] - MARGIN_TOP) // CELL
                for (r, c, d) in arrows:
                    if r == row and c == col:
                        hover_pos = (r, c)
                        break

            back_btn, restart_btn, close_rect = draw_game(
                arrows, anim, level, mistakes, hover_pos, message,
                min(255, msg_timer * 8), elapsed)

            if anim:
                if anim['type'] == 'fly':
                    anim['progress'] += 0.07
                    if anim['progress'] >= 1.0:
                        anim = None
                elif anim['type'] == 'collide':
                    anim['progress'] += 0.04
                    if anim['progress'] >= 1.0:
                        anim = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    save_progress(progress)
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and not wait_release:
                    mx, my = event.pos
                    if close_rect.collidepoint(mx, my):
                        show_quit_dialog = True
                        wait_release = True
                        continue
                    if restart_btn.collidepoint(mx, my):
                        arrows = list(LEVELS[level])
                        mistakes = 0
                        message = ""
                        anim = None
                        level_start_time = time.time()
                        elapsed = 0.0
                        wait_release = True
                        continue
                    if back_btn.collidepoint(mx, my):
                        scene = 'select'
                        wait_release = True
                        continue
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
                                anim = {'type': 'fly', 'arrow': clicked, 'progress': 0.0}
                                message = "飞出！"
                                msg_timer = 40
                            else:
                                blocker = find_blocker(arrows, r, c, d)
                                travel = CELL * 0.85
                                if blocker:
                                    br, bc = blocker
                                    if d == 'right':
                                        travel = (bc - c) * CELL - CELL * 0.85
                                    elif d == 'left':
                                        travel = (c - bc) * CELL - CELL * 0.85
                                    elif d == 'down':
                                        travel = (br - r) * CELL - CELL * 0.85
                                    elif d == 'up':
                                        travel = (r - br) * CELL - CELL * 0.85
                                    travel = max(CELL * 0.3, travel)
                                anim = {'type': 'collide', 'arrow': clicked,
                                        'progress': 0.0, 'travel': travel}
                                message = "被挡住了！"
                                msg_timer = 40
                                mistakes += 1
                            wait_release = True

            if not pygame.mouse.get_pressed()[0]:
                wait_release = False

            if msg_timer > 0:
                msg_timer -= 1

            # 通关
            if not arrows and anim is None:
                elapsed = time.time() - level_start_time
                score = calc_score(elapsed, mistakes)
                stars = calc_stars(elapsed, mistakes)

                # 更新进度
                key = str(level + 1)
                if score > progress["best_scores"].get(key, -1):
                    progress["best_scores"][key] = score
                if stars > progress["best_stars"].get(key, 0):
                    progress["best_stars"][key] = stars
                # 解锁下一关
                if level + 2 > progress["unlocked"] and level + 2 <= len(LEVELS):
                    progress["unlocked"] = level + 2
                save_progress(progress)

                if level + 1 < len(LEVELS):
                    title = "通关！"
                    sub = f"第 {level + 1} 关完成"
                    buttons = [("下一关", True), ("重玩", False), ("返回", False)]
                else:
                    title = "全部通关！"
                    sub = "恭喜你完成所有关卡"
                    buttons = [("重玩", True), ("返回", False)]

                rects = draw_result_dialog(title, sub, buttons, BTN_NORMAL,
                                           elapsed, mistakes, score, stars)
                choosing = True
                while choosing:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save_progress(progress)
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            if level + 1 < len(LEVELS):
                                if rects[0].collidepoint(mx, my):
                                    level += 1
                                    arrows = list(LEVELS[level])
                                    mistakes = 0
                                    message = ""
                                    anim = None
                                    level_start_time = time.time()
                                    elapsed = 0.0
                                    scene = 'playing'
                                    choosing = False
                                elif rects[1].collidepoint(mx, my):
                                    arrows = list(LEVELS[level])
                                    mistakes = 0
                                    message = ""
                                    anim = None
                                    level_start_time = time.time()
                                    elapsed = 0.0
                                    scene = 'playing'
                                    choosing = False
                                elif rects[2].collidepoint(mx, my):
                                    scene = 'select'
                                    choosing = False
                            else:
                                if rects[0].collidepoint(mx, my):
                                    level = 0
                                    arrows = list(LEVELS[level])
                                    mistakes = 0
                                    message = ""
                                    anim = None
                                    level_start_time = time.time()
                                    elapsed = 0.0
                                    scene = 'playing'
                                    choosing = False
                                elif rects[1].collidepoint(mx, my):
                                    scene = 'select'
                                    choosing = False
                wait_release = True

            # 失败
            if mistakes >= MAX_MISTAKES:
                title = "失败！"
                sub = f"第 {level + 1} 关失误已达上限"
                buttons = [("重新开始", True), ("返回", False)]
                rects = draw_result_dialog(title, sub, buttons, CLOSE_BG)
                choosing = True
                while choosing:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            save_progress(progress)
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mx, my = event.pos
                            if rects[0].collidepoint(mx, my):
                                arrows = list(LEVELS[level])
                                mistakes = 0
                                anim = None
                                message = ""
                                level_start_time = time.time()
                                elapsed = 0.0
                                scene = 'playing'
                                choosing = False
                            elif rects[1].collidepoint(mx, my):
                                scene = 'select'
                                choosing = False
                wait_release = True

        clock.tick(60)


if __name__ == "__main__":
    main()
