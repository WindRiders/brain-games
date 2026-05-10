"""G2 弹幕大脑游戏 — 躲避数学弹幕"""

import time
import os
import sys
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.ui import colors as C
from src.ui.components import box, progress_bar, center, header, divider

# 补充 colors.py 中没有的颜色
DIM = "\033[2m"  # 暗色/灰色

# ── 难度配置 ──────────────────────────────────────────────────
DIFFICULTY_CONFIG = {
    "easy":   {"options": 2, "speed": 1, "max_val": 10, "total_questions": 10, "ops": ["+", "-"]},
    "normal": {"options": 3, "speed": 2, "max_val": 20, "total_questions": 10, "ops": ["+", "-", "*"]},
    "hard":   {"options": 4, "speed": 3, "max_val": 50, "total_questions": 10, "ops": ["+", "-", "*"]},
}

# ── 数学题生成 ──────────────────────────────────────────────────
def generate_question(difficulty, max_val):
    """根据难度生成一道数学题。

    返回: (question_str, correct_answer, wrong_answers_list)
    """
    ops = DIFFICULTY_CONFIG.get(difficulty, DIFFICULTY_CONFIG["easy"])["ops"]

    if difficulty == "easy":
        # 简单: a ± b (0-10)
        op = random.choice(["+", "-"])
        if op == "+":
            a = random.randint(0, max_val)
            b = random.randint(0, max_val - a)
            correct = a + b
        else:
            a = random.randint(0, max_val)
            b = random.randint(0, a)
            correct = a - b
        question_str = f"{a}+{b}" if op == "+" else f"{a}-{b}"

    elif difficulty == "normal":
        # 普通: a ± b 或 a × b (0-20)
        op = random.choice(["+", "-", "*"])
        if op == "+":
            a = random.randint(0, max_val)
            b = random.randint(0, max(max_val - a, 1))
            correct = a + b
        elif op == "-":
            a = random.randint(0, max_val)
            b = random.randint(0, a)
            correct = a - b
        else:
            a = random.randint(0, min(max_val, 12))
            b = random.randint(0, min(max_val, 12))
            correct = a * b
        if op == "+":
            question_str = f"{a}+{b}"
        elif op == "-":
            question_str = f"{a}-{b}"
        else:
            question_str = f"{a}×{b}"

    else:
        # 困难: a ± b × c 或 (a ± b) × c (0-50)
        op = random.choice(["+", "-", "*"])
        if op == "+":
            a = random.randint(0, max_val)
            b = random.randint(0, max(max_val - a, 1))
            correct = a + b
            question_str = f"{a}+{b}"
        elif op == "-":
            a = random.randint(0, max_val)
            b = random.randint(0, a)
            correct = a - b
            question_str = f"{a}-{b}"
        else:
            # 混合运算: a ± b × c 或 (a ± b) × c
            form = random.choice(["mixed", "paren"])
            if form == "mixed":
                a = random.randint(1, 20)
                b = random.randint(1, 20)
                c = random.randint(2, 5)
                op_inner = random.choice(["+", "-"])
                if op_inner == "+":
                    a = min(a, max_val)
                    correct = a + b * c
                else:
                    if a < b:
                        a, b = b, a
                    correct = a - b * c
                    if correct < 0:
                        correct = abs(correct)
                question_str = f"{a}{op_inner}{b}×{c}"
            else:
                a = random.randint(1, 15)
                b = random.randint(1, 15)
                c = random.randint(2, 5)
                op_inner = random.choice(["+", "-"])
                if op_inner == "+":
                    a = min(a, max_val - b)
                    correct = (a + b) * c
                else:
                    if a < b:
                        a, b = b, a
                    correct = (a - b) * c
                if correct < 0:
                    correct = abs(correct)
                question_str = f"({a}{op_inner}{b})×{c}"

    # 生成错误答案
    wrong_answers = _generate_wrong_answers(correct, max_val)

    return question_str, correct, wrong_answers


def _generate_wrong_answers(correct, max_val, count=3):
    """生成与正确答案不同的错误答案。"""
    wrongs = []
    span = max(5, abs(correct) // 2 + 1)

    # 策略1: 在正确答案附近偏移
    for _ in range(count * 10):
        if len(wrongs) >= count:
            break
        offset = random.randint(1, span)
        sign = random.choice([-1, 1])
        wrong = correct + sign * offset
        if wrong != correct and wrong >= 0 and wrong not in wrongs:
            wrongs.append(wrong)

    # 策略2: 随机填充
    lo = max(0, correct - 10)
    hi = max(lo + 1, min(correct + 10, max_val * 2))
    while len(wrongs) < count:
        wrong = random.randint(lo, hi)
        if wrong != correct and wrong not in wrongs and wrong >= 0:
            wrongs.append(wrong)

    return wrongs


# ── 弹幕 x 位置预设 ─────────────────────────────────────────────
_X_POSITIONS = {
    2: [6, 30],
    3: [4, 20, 37],
    4: [2, 15, 29, 43],
}


# ═══════════════════════════════════════════════════════════════
#  MathDodgeGame 类
# ═══════════════════════════════════════════════════════════════
class MathDodgeGame(BaseGame):
    """弹幕大脑游戏 — 接住正确的数学答案，躲避错误的！"""

    # ── 常量 ──
    WIDTH = 55           # 画面宽度
    PLAYER_Y = 19        # 玩家所在行
    BULLET_START_Y = 2   # 弹幕起始行
    BULLET_HIT_Y = 18    # 弹幕判定行（到达此行时检测碰撞）
    PLAYER_MIN_X = 2     # 玩家最小 x
    PLAYER_MAX_X = 48    # 玩家最大 x
    PLAYER_STEP = 2      # 每次移动步长

    # ── 初始化 ──
    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "弹幕大脑"

        # 游戏状态
        self._player_x = 25
        self._bullets = []            # 当前活跃弹幕列表
        self._question_idx = 0        # 已出题数 (0-based)
        self._total_questions = 10
        self._base_speed = 1
        self._options = 2
        self._max_val = 10
        self._ops = ["+", "-"]
        self._consecutive = 0         # 连续答对次数
        self._game_over = False
        self._won = False
        self._question_resolved = False  # 当前题目是否已判定
        self._current_question = None # (question_str, correct, wrongs)
        self._flash_color = None      # 上一帧闪烁颜色
        self._last_result = ""        # "✓ 正确!", "✗ 错误!", "⏱ 超时!"

    # ── setup ──
    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        self._options = config["options"]
        self._base_speed = config["speed"]
        self._max_val = config["max_val"]
        self._total_questions = config["total_questions"]
        self._ops = config["ops"]
        self.score = 0
        self._player_x = 25
        self._bullets = []
        self._question_idx = 0
        self._consecutive = 0
        self._game_over = False
        self._won = False
        self._question_resolved = False
        self._current_question = None
        self._flash_color = None
        self._last_result = ""
        self._spawn_next_question()

    # ── handle_input ──
    def handle_input(self, key):
        if key is None:
            return True
        if key == "q":
            self._game_over = True
            return False
        if key == "h":
            return True  # 帮助由 game_loop 处理
        if key in ("a", "left"):
            self._player_x = max(self.PLAYER_MIN_X, self._player_x - self.PLAYER_STEP)
        elif key in ("d", "right"):
            self._player_x = min(self.PLAYER_MAX_X, self._player_x + self.PLAYER_STEP)
        return True

    # ── 出题 ──
    def _spawn_next_question(self):
        if self._question_idx >= self._total_questions:
            self._game_over = True
            self._won = True
            return

        question_str, correct, wrongs = generate_question(self.difficulty, self._max_val)
        self._current_question = (question_str, correct, wrongs)
        self._question_resolved = False
        self._last_result = ""

        # 组合答案并打乱
        all_answers = [correct] + wrongs[:self._options - 1]
        random.shuffle(all_answers)

        x_positions = _X_POSITIONS.get(self._options, _X_POSITIONS[2])
        self._bullets = []
        for i, ans in enumerate(all_answers):
            is_correct = (ans == correct)
            bullet_text = f"[{question_str}=? {ans}]"
            self._bullets.append({
                "x": x_positions[i],
                "y": self.BULLET_START_Y,
                "text": bullet_text,
                "answer": ans,
                "is_correct": is_correct,
                "hit": False,
            })

        self._question_idx += 1

    # ── 当前速度（随进度逐渐加快） ──
    def _get_current_speed(self):
        boost = self._question_idx // 4   # 每 4 题加速 1
        return self._base_speed + boost

    # ── 判定 ──
    def _resolve(self, is_correct):
        """判定结果: True=答对, False=答错, None=超时。"""
        self._question_resolved = True
        if is_correct is True:
            self.score += 100
            self._consecutive += 1
            if self._consecutive >= 3:
                self.score += 50
            self._flash_color = C.GREEN
            self._last_result = f"{C.BGREEN}✓ +100{C.RESET}"
            if self._consecutive >= 3:
                self._last_result += f" {C.BYELLOW}连击+50!{C.RESET}"
        elif is_correct is False:
            self.score -= 50
            self._consecutive = 0
            self._flash_color = C.RED
            self._last_result = f"{C.RED}✗ -50{C.RESET}"
        else:
            self.score -= 30
            self._consecutive = 0
            self._flash_color = C.YELLOW
            self._last_result = f"{C.BYELLOW}⏱ -30 超时{C.RESET}"

    # ── update ──
    def update(self):
        if self._game_over:
            return

        speed = self._get_current_speed()

        # 移动弹幕
        for b in self._bullets:
            b["y"] += speed

        # 碰撞检测
        if not self._question_resolved:
            for b in self._bullets:
                if b["y"] >= self.BULLET_HIT_Y and not b["hit"]:
                    bw = len(b["text"])
                    if self._player_x >= b["x"] and self._player_x < b["x"] + bw:
                        b["hit"] = True
                        self._resolve(b["is_correct"])
                        break

            # 超时检测：所有弹幕都越过玩家行
            if not self._question_resolved and all(b["y"] >= self.PLAYER_Y for b in self._bullets):
                self._resolve(None)

        # 当前题目已判定且所有弹幕已离开屏幕，出下一题
        if self._question_resolved and all(b["y"] >= self.PLAYER_Y + 1 for b in self._bullets):
            self._spawn_next_question()

    # ── render ──
    def render(self):
        lines = []

        # ── 第 0 行: 状态栏 ──
        q_done = min(self._question_idx, self._total_questions)
        status = (
            f"  {C.BOLD}{C.BGREEN}得分: {self.score}{C.RESET}  "
            f"{C.BOLD}{C.BYELLOW}连击: {self._consecutive}{C.RESET}  "
            f"{C.BOLD}{C.CYAN}题目: {q_done}/{self._total_questions}{C.RESET}"
        )
        lines.append(center(status, self.WIDTH))

        # ── 第 1 行: 题目提示 / 上次结果 ──
        if self._current_question and not self._game_over:
            q_str, correct, wrongs = self._current_question
            lines.append(center(f"{C.BWHITE}{q_str}=?{C.RESET}", self.WIDTH))
        elif self._last_result:
            lines.append(center(self._last_result, self.WIDTH))
        else:
            lines.append("")

        # ── 第 2-17 行: 弹幕区域 ──
        # 创建空白网格
        grid_rows = 16  # y=2..17
        grid = [[" " for _ in range(self.WIDTH)] for _ in range(grid_rows)]

        for b in self._bullets:
            by = b["y"]
            if by < 2 or by > 17:
                continue
            row_idx = by - 2
            txt = b["text"]
            # 命中过的弹幕显示不同颜色
            if b["hit"]:
                color = C.BGREEN if b["is_correct"] else C.RED
            else:
                color = C.CYAN

            for ci, ch in enumerate(txt):
                col = b["x"] + ci
                if 0 <= col < self.WIDTH:
                    grid[row_idx][col] = f"{color}{ch}{C.RESET}"

        for r in range(grid_rows):
            line = "".join(grid[r])
            lines.append(line)

        # ── 第 18 行: 分隔线 ──
        lines.append(f"{DIM}{'─' * self.WIDTH}{C.RESET}")

        # ── 第 19 行: 玩家 ──
        player_line = [" " for _ in range(self.WIDTH)]
        if 0 <= self._player_x < self.WIDTH:
            player_line[self._player_x] = f"{C.BOLD}{C.BWHITE}@{C.RESET}"
        lines.append("".join(player_line))

        # ── 第 20 行: 操作提示 ──
        lines.append(f"  {DIM}← A              D →{C.RESET}")

        self._renderer.render_frame(lines)

    # ── render_final (游戏结束画面) ──
    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 弹 幕 大 脑 "))
        lines.append("")

        if self._won:
            lines.append(center(f"{C.BGREEN}🎉 游戏完成！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}连击最高: {self._consecutive} 连击{C.RESET}" if self._consecutive > 0 else "", self.WIDTH))
        lines.append("")

        high = self._score_manager.get_high_score(self.name, self.difficulty)
        new_high = self._score_manager.set_high_score(self.name, self.difficulty, self.score)
        if new_high:
            lines.append(center(f"{C.BYELLOW}🏆 新纪录！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"历史最高: {C.BYELLOW}{high}{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{DIM}按任意键返回主菜单...{C.RESET}", self.WIDTH))

        self._renderer.render_frame(lines)

    # ── game_loop ──
    def game_loop(self):
        while not self._game_over:
            key = self._input_manager.get_key_nonblocking()
            if key is not None:
                if key == "h":
                    help_text = self.show_help()
                    self._renderer.clear()
                    print(help_text)
                    print("\n  按任意键继续...")
                    self._input_manager.get_key()
                    continue
                if not self.handle_input(key):
                    break

            self.update()
            self.render()
            time.sleep(0.05)

        # 游戏结束画面
        self._render_final()
        print("\n  ", end="")
        self._input_manager.get_key()

    # ── show_help ──
    def show_help(self) -> str:
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        return (
            f"\n  {C.BOLD}{C.CYAN}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  {C.BWHITE}@{C.RESET} 是你的角色，在底部左右移动\n"
            f"  空中会落下数学弹幕，每个弹幕包含一个答案\n"
            f"  {C.BGREEN}接到正确答案{C.RESET} → +100 分\n"
            f"  {C.RED}接到错误答案{C.RESET}   → -50 分\n"
            f"  {C.BYELLOW}漏接{C.RESET}           → -30 分\n"
            f"  {C.BYELLOW}连续答对 3 题{C.RESET}  → +50 连击奖励\n"
            f"\n  操作: A/← 左移  D/→ 右移  Q 退出  H 帮助\n"
            f"  每题 {config['options']} 个选项，每关 {config['total_questions']} 题\n"
            f"  速度会逐渐加快，做好准备！\n"
        )
