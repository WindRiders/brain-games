#!/usr/bin/env python3
"""为 GitHub README 生成游戏界面截图"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/root/brain-games/screenshots"
os.makedirs(OUT, exist_ok=True)

BG = (10, 10, 26)
BG2 = (18, 18, 42)
BG3 = (26, 26, 58)
FG = (224, 224, 240)
DIM = (128, 128, 160)
ACCENT = (0, 229, 255)
ACCENT2 = (255, 110, 199)
GOLD = (255, 215, 64)
GREEN = (105, 240, 174)
RED = (255, 82, 82)
PURPLE = (179, 136, 255)
ORANGE = (255, 171, 64)
W, H = 800, 500

FONT = None
FONT_BOLD = None
FONT_BIG = None
FONT_MONO = None

try:
    FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    FONT_BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    FONT_BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
    FONT_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    FONT_MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    FONT_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    FONT_MEDIUM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_SCORE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
except Exception:
    FONT = ImageFont.load_default()
    FONT_BOLD = FONT
    FONT_BIG = FONT
    FONT_TITLE = FONT
    FONT_MONO = FONT
    FONT_SMALL = FONT
    FONT_MEDIUM = FONT
    FONT_SCORE = FONT


def new_img():
    return Image.new("RGB", (W, H), BG)


def rounded_rect(draw, xy, r, fill, outline=None):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline)


def text_c(draw, text, y, font=FONT, fill=FG):
    """居中文本"""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=font, fill=fill)


def text_l(draw, text, x, y, font=FONT, fill=FG):
    draw.text((x, y), text, font=font, fill=fill)


def game_header(draw, title, score="0", extra=""):
    """绘制游戏通用顶部栏"""
    rounded_rect(draw, (20, 12, W-20, 46), 8, BG2)
    text_l(draw, title, 36, 18, FONT_BOLD, ACCENT)
    if extra:
        text_l(draw, extra, 200, 18, FONT_SMALL, DIM)
    if score:
        bbox = draw.textbbox((0, 0), str(score), font=FONT_SCORE)
        tw = bbox[2] - bbox[0]
        text_l(draw, str(score), W - 40 - tw, 14, FONT_SCORE, GOLD)


def screenshot_main_menu():
    """主菜单截图"""
    img = new_img()
    d = ImageDraw.Draw(img)

    # 标题
    text_c(d, "Brain Games", 30, FONT_TITLE, ACCENT)
    text_c(d, "🧠 脑力训练合集 — 浏览器版", 90, FONT_MEDIUM, DIM)

    # 游戏卡片
    games = [
        ("1", "记忆迷宫", "观看迷宫后凭记忆走出", ACCENT),
        ("2", "弹幕大脑", "躲避错误答案,碰正确答案", GREEN),
        ("3", "密码破译", "破解层层加密的密文", GOLD),
        ("4", "节奏大师", "跟随节拍精准按键", ACCENT2),
        ("5", "打地鼠", "快速反应击打目标", ORANGE),
        ("6", "故事解谜", "文字冒险推理破案", PURPLE),
        ("7", "贪吃蛇记忆", "按顺序吃苹果的贪吃蛇", RED),
    ]

    card_w, card_h = 360, 48
    start_x = 30
    start_y = 130
    for i, (num, name, desc, color) in enumerate(games):
        col = i % 2
        row = i // 2
        cx = start_x + col * (card_w + 16)
        cy = start_y + row * (card_h + 8)
        if row == 3 and col == 0:
            cx = start_x + card_w // 2 + 8

        rounded_rect(d, (cx, cy, cx + card_w, cy + card_h), 10, BG2, BG3)

        # 编号圆圈
        rounded_rect(d, (cx + 12, cy + 10, cx + 40, cy + 38), 14, color)
        text_l(d, num, cx + 21, cy + 11, FONT_BOLD, BG)

        # 游戏名称和描述
        text_l(d, name, cx + 50, cy + 8, FONT_BOLD, FG)
        text_l(d, desc, cx + 50, cy + 28, FONT_SMALL, DIM)

    # 底部按钮
    rounded_rect(d, (W//2-120, 440, W//2+30, 470), 8, BG3)
    text_c(d, "🏆 最高分", 444, FONT_SMALL, FG)
    rounded_rect(d, (W//2+45, 440, W//2+120, 470), 8, BG3)
    text_c(d, "重置分数", 444, FONT_SMALL, RED)

    img.save(f"{OUT}/01-main-menu.png")
    print("  ✓ 01-main-menu.png")


def screenshot_maze():
    """记忆迷宫"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "🔍 记忆迷宫", "0", "记忆阶段... 4s")

    # 迷宫
    mx, my = 120, 80
    cell = 18
    mw, mh = 17, 17
    # 绘制迷宫墙壁
    for y in range(mh):
        for x in range(mw):
            if (x % 2 == 0 or y % 2 == 0) and not (x == 1 and y == 1) and not (x == mw-2 and y == mh-2):
                px, py = mx + x*cell, my + y*cell
                rounded_rect(d, (px, py, px+cell, py+cell), 2, BG3)
    # 出口
    ex, ey = mx + (mw-2)*cell, my + (mh-2)*cell
    rounded_rect(d, (ex, ey, ex+cell, ey+cell), 2, GREEN)
    # 玩家
    px, py = mx + cell, my + cell
    d.ellipse([px+2, py+2, px+cell-2, py+cell-2], fill=ACCENT)

    text_c(d, "方向键移动 | Q 退出", 430, FONT_SMALL, DIM)
    img.save(f"{OUT}/02-maze.png")
    print("  ✓ 02-maze.png")


def screenshot_math_dodge():
    """弹幕大脑"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "弹幕大脑", "150", "❤️ x2   🔥 x3")

    # 游戏区域背景
    rounded_rect(d, (40, 65, W-40, 390), 10, BG2)

    # 玩家（底部中央圆形）
    d.ellipse([W//2-18, 400, W//2+18, 436], fill=ACCENT)
    d.ellipse([W//2-12, 406, W//2+12, 430], fill=BG)

    # 子弹 - 正确（绿色）
    positions = [(150, 100), (350, 160), (550, 120), (250, 200), (450, 250), (600, 300)]
    nums = ["42", "17", "8", "25", "50", "33"]
    for i, (bx, by) in enumerate(positions):
        color = GREEN if i % 2 == 0 else RED
        d.ellipse([bx-18, by-18, bx+18, by+18], fill=color)
        text_l(d, nums[i], bx-14, by-10, FONT_BOLD, (0, 0, 0))

    # 问题
    rounded_rect(d, (W//2-150, 75, W//2+150, 100), 8, (0, 0, 0, 0))
    text_c(d, "计算: 7 × 6 = ?", 80, FONT_MONO, GOLD)

    text_c(d, "WASD / 方向键 移动 | 碰正确数字得分", 445, FONT_SMALL, DIM)
    img.save(f"{OUT}/03-math-dodge.png")
    print("  ✓ 03-math-dodge.png")


def screenshot_code_breaker():
    """密码破译"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "🔐 密码破译", "250", "第 3/7 关   ⏱ 28s")

    # 内容区
    rounded_rect(d, (60, 70, W-60, 280), 10, BG2)
    text_c(d, "破解以下密文:", 90, FONT_SMALL, DIM)
    text_c(d, "S K F W H Q", 130, FONT_BIG, ACCENT)

    # 输入框
    rounded_rect(d, (200, 300, 500, 340), 8, BG3, ACCENT)
    text_l(d, "输入原文...", 216, 308, FONT_MONO, DIM)
    # 提交按钮
    rounded_rect(d, (510, 300, 570, 340), 8, ACCENT)
    text_c(d, "提交", 308, FONT_BOLD, BG)

    # 提示按钮
    rounded_rect(d, (250, 360, 500, 390), 8, BG3)
    text_c(d, "💡 提示 (2)", 366, FONT_SMALL, FG)

    text_c(d, "输入 + 回车提交 | 计时破译 | Q 退出", 445, FONT_SMALL, DIM)
    img.save(f"{OUT}/04-code-breaker.png")
    print("  ✓ 04-code-breaker.png")


def screenshot_rhythm():
    """节奏大师"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "🎵 节奏大师", "850", "🔥 5  12/30")

    # 游戏区域
    rounded_rect(d, (40, 65, W-40, 390), 10, BG2)

    # 轨道线
    lanes = [W//5, W*2//5, W*3//5, W*4//5]
    for lx in lanes:
        d.line([(lx, 65), (lx, 390)], fill=BG3, width=1)

    # 判定线
    d.line([(80, 330), (W-80, 330)], fill=GOLD, width=2)

    # 音符
    notes = [
        (lanes[0], 120, RED), (lanes[2], 160, ACCENT),
        (lanes[1], 200, GREEN), (lanes[3], 240, ACCENT2),
        (lanes[0], 280, RED), (lanes[2], 310, ACCENT),
    ]
    for nx, ny, color in notes:
        d.ellipse([nx-18, ny-18, nx+18, ny+18], fill=color)
        text_l(d, "D" if color==RED else "F" if color==GREEN else "J" if color==ACCENT else "K",
               nx-6, ny-8, FONT_BOLD, BG if color != RED else (0,0,0))

    text_c(d, "D    F    J    K  | 跟随节拍按键", 445, FONT_SMALL, DIM)
    img.save(f"{OUT}/05-rhythm.png")
    print("  ✓ 05-rhythm.png")


def screenshot_whack():
    """打地鼠"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "🔨 打地鼠", "300", "第 5/12 轮  命中:3 漏:1")

    # 九宫格
    grid_x, grid_y = 200, 100
    hole_size = 80
    gap = 16
    for row in range(3):
        for col in range(3):
            hx = grid_x + col * (hole_size + gap)
            hy = grid_y + row * (hole_size + gap)
            is_active = (row == 1 and col == 1)
            color = ACCENT2 if is_active else BG3
            d.ellipse([hx, hy, hx+hole_size, hy+hole_size], fill=color)
            if is_active:
                text_c(d, "🐹", hy + hole_size//2 - 24, FONT_BIG, FG)

    text_c(d, "鼠标点击地鼠 | 限时反应", 420, FONT_SMALL, DIM)
    img.save(f"{OUT}/06-whack.png")
    print("  ✓ 06-whack.png")


def screenshot_story():
    """故事解谜"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "📖 故事解谜", "65", "")

    # 文本框
    rounded_rect(d, (60, 65, W-60, 250), 10, BG2)
    story_lines = [
        "深夜，你收到一条匿名消息：",
        '"老图书馆地下室藏着秘密。午夜12点，"',
        '"一个人来，带手电筒。"',
        "",
        "你站在废弃图书馆的铁门前，冷风穿过破窗。"
    ]
    for i, line in enumerate(story_lines):
        text_l(d, line, 80, 80 + i*24, FONT, FG if line else DIM)

    # 选项按钮
    choices = [
        "推开铁门进去 (+10)",
        "绕到后门 (+5)",
        "先观察四周 (+15)",
    ]
    for i, ch in enumerate(choices):
        cy = 270 + i * 42
        rounded_rect(d, (60, cy, W-60, cy+36), 8, BG3)
        text_l(d, ch, 76, cy+6, FONT, FG)

    text_c(d, "点击选项推进故事 | 多分支剧情 | Q 退出", 445, FONT_SMALL, DIM)
    img.save(f"{OUT}/07-story.png")
    print("  ✓ 07-story.png")


def screenshot_snake():
    """贪吃蛇记忆"""
    img = new_img()
    d = ImageDraw.Draw(img)
    game_header(d, "🐍 贪吃蛇记忆", "200", "👀 记住顺序!  第1/6")

    # 游戏区域
    gx, gy = 60, 75
    gs = 18
    gw, gh = 24, 20

    # 网格
    for xx in range(gw+1):
        d.line([(gx+xx*gs, gy), (gx+xx*gs, gy+gh*gs)], fill=(21,21,48), width=1)
    for yy in range(gh+1):
        d.line([(gx, gy+yy*gs), (gx+gw*gs, gy+yy*gs)], fill=(21,21,48), width=1)

    # 蛇
    snake = [(5, 10), (4, 10), (3, 10)]
    for i, (sx, sy) in enumerate(snake):
        alpha = 1 - i*0.2
        color = tuple(int(c*alpha) for c in ACCENT)
        rounded_rect(d, (gx+sx*gs+1, gy+sy*gs+1, gx+(sx+1)*gs-1, gy+(sy+1)*gs-1), 3, color)

    # 顺序苹果（显示阶段）
    apples = [(8, 3), (15, 8), (2, 15), (18, 5), (10, 12), (20, 16)]
    for i, (ax, ay) in enumerate(apples):
        alpha = 0.3 + 0.7*(i/5)
        color = tuple(int(c*alpha) for c in GOLD)
        rounded_rect(d, (gx+ax*gs+1, gy+ay*gs+1, gx+(ax+1)*gs-1, gy+(ay+1)*gs-1), 3, color)
        text_l(d, str(i+1), gx+ax*gs+gs//2-4, gy+ay*gs+gs//2-8, FONT_SMALL, (0,0,0))

    text_c(d, "方向键移动 | 按顺序吃苹果 | Q 退出", 445, FONT_SMALL, DIM)
    img.save(f"{OUT}/08-snake.png")
    print("  ✓ 08-snake.png")


def screenshot_gameover():
    """游戏结束弹窗"""
    img = new_img()
    d = ImageDraw.Draw(img)

    # 半透明背景
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 180))
    img.paste(overlay, (0, 0), overlay)

    # 弹窗
    bx, by = W//2-200, H//2-120
    rounded_rect(d, (bx, by, bx+400, by+240), 12, BG2, ACCENT)

    text_c(d, "记忆迷宫 — 普通", by+24, FONT_MEDIUM, FG)
    text_c(d, "350", by+60, FONT_TITLE, GOLD)
    text_c(d, "🎉 新纪录!", by+110, FONT_BOLD, ACCENT2)
    text_c(d, "最高分: 350", by+136, FONT_SMALL, DIM)

    # 按钮
    rounded_rect(d, (bx+30, by+180, bx+180, by+210), 8, ACCENT)
    text_c(d, "🔄 再来一次", by+184, FONT_SMALL, BG)
    rounded_rect(d, (bx+220, by+180, bx+370, by+210), 8, BG3)
    text_c(d, "🏠 主菜单", by+184, FONT_SMALL, FG)

    img.save(f"{OUT}/09-gameover.png")
    print("  ✓ 09-gameover.png")


def screenshot_difficulty():
    """难度选择"""
    img = new_img()
    d = ImageDraw.Draw(img)

    text_c(d, "选择难度 — 记忆迷宫", 60, FONT_BIG, ACCENT)

    diffs = [
        ("简单", "轻松上手", GREEN),
        ("普通", "适度挑战", GOLD),
        ("困难", "极限脑力", RED),
    ]
    for i, (name, desc, color) in enumerate(diffs):
        cx = 160 + i*180
        rounded_rect(d, (cx, 140, cx+150, 240), 12, BG2, BG3)
        text_c(d, name, 170, FONT_MEDIUM, color)
        text_c(d, desc, 200, FONT_SMALL, DIM)

    rounded_rect(d, (W//2-100, 300, W//2+100, 330), 8, BG3)
    text_c(d, "← 返回主菜单", 305, FONT_SMALL, FG)

    img.save(f"{OUT}/00-difficulty.png")
    print("  ✓ 00-difficulty.png")


if __name__ == "__main__":
    print("生成截图...")
    screenshot_difficulty()
    screenshot_main_menu()
    screenshot_maze()
    screenshot_math_dodge()
    screenshot_code_breaker()
    screenshot_rhythm()
    screenshot_whack()
    screenshot_story()
    screenshot_snake()
    screenshot_gameover()
    print("完成! 截图保存在 screenshots/")