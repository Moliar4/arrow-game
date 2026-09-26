import pygame
import sys

pygame.init()

# 窗口设置
CELL = 100
COLS, ROWS = 5, 5
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL + 80
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")
font = pygame.font.SysFont("simhei", 24)
big_font = pygame.font.SysFont("simhei", 36)

# 关卡数据：每个箭头用 (行, 列, 方向) 表示
# 方向: 'up', 'down', 'left', 'right'
LEVELS = [
    [
        (0, 0, 'right'), (0, 3, 'up'),
        (2, 1, 'left'), (2, 4, 'right'),
        (4, 2, 'up'), (4, 4, 'right'),
    ],
]

# 颜色
BG = (245, 245, 220)
GRID = (200, 200, 200)
ARROW = (60, 60, 60)
HIGHLIGHT = (220, 60, 60)
TEXT = (30, 30, 30)

def draw_arrow(surface, row, col, direction, color):
    cx = col * CELL + CELL // 2
    cy = row * CELL + CELL // 2
    size = 30
    if direction == 'right':
        points = [(cx - size, cy - size), (cx + size, cy), (cx - size, cy + size)]
    elif direction == 'left':
        points = [(cx + size, cy - size), (cx - size, cy), (cx + size, cy + size)]
    elif direction == 'up':
        points = [(cx - size, cy + size), (cx, cy - size), (cx + size, cy + size)]
    else:  # down
        points = [(cx - size, cy - size), (cx, cy + size), (cx + size, cy - size)]
    pygame.draw.polygon(surface, color, points)

def draw_game(arrows, level, mistakes, highlight=None):
    screen.fill(BG)
    # 画网格
    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(c * CELL, r * CELL + 80, CELL, CELL)
            pygame.draw.rect(screen, GRID, rect, 1)
    # 画箭头
    for (r, c, d) in arrows:
        color = HIGHLIGHT if highlight == (r, c) else ARROW
        draw_arrow(screen, r, c, d, color)
    # 顶部信息
    info = f"关卡 {level + 1}   剩余箭头 {len(arrows)}   失误 {mistakes}/3"
    text = font.render(info, True, TEXT)
    screen.blit(text, (10, 20))
    restart_rect = pygame.Rect(WIDTH - 120, 15, 100, 35)
    pygame.draw.rect(screen, (180, 180, 180), restart_rect)
    rt = font.render("重新开始", True, TEXT)
    screen.blit(rt, (WIDTH - 115, 22))
    pygame.display.flip()
    return restart_rect

def check_can_fly(arrows, row, col, direction):
    """检查箭头前方是否有阻挡"""
    for (r, c, d) in arrows:
        if (r, c) == (row, col):
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

def main():
    clock = pygame.time.Clock()
    level = 0
    arrows = LEVELS[level][:]
    mistakes = 0
    max_mistakes = 3
    message = ""
    msg_timer = 0

    while True:
        restart_rect = draw_game(arrows, level, mistakes)
        if message:
            mt = big_font.render(message, True, HIGHLIGHT)
            screen.blit(mt, (WIDTH // 2 - mt.get_width() // 2, HEIGHT - 50))
            pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # 重新开始按钮
                if restart_rect.collidepoint(mx, my):
                    arrows = LEVELS[level][:]
                    mistakes = 0
                    message = ""
                    continue
                # 点击棋盘
                if my >= 80:
                    col = mx // CELL
                    row = (my - 80) // CELL
                    for (r, c, d) in arrows[:]:
                        if r == row and c == col:
                            if check_can_fly(arrows, r, c, d):
                                arrows.remove((r, c, d))
                                message = "飞出！"
                                msg_timer = 30
                            else:
                                mistakes += 1
                                message = "被挡住了！"
                                msg_timer = 30
                            break

        # 通关判断
        if not arrows:
            message = "通关！"
            msg_timer = 120
            level += 1
            if level >= len(LEVELS):
                message = "全部通关！"
                msg_timer = 99999
            else:
                arrows = LEVELS[level][:]
                mistakes = 0

        # 失败判断
        if mistakes >= max_mistakes:
            message = "失败！点击重新开始"
            msg_timer = 99999

        if msg_timer > 0:
            msg_timer -= 1
            if msg_timer == 0:
                message = ""

        clock.tick(30)

if __name__ == "__main__":
    main()
