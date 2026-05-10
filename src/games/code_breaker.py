"""G3 密码破译游戏 — 10关加密挑战"""

import time
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.engine.timer import GameTimer
from src.ui import colors as C
from src.ui.components import box, center, header, divider
from src.utils.crypto import caesar_cipher, reverse_text, vigenere_encrypt, to_morse, to_binary_ascii

# 补充 colors.py 中没有的颜色
DIM = "\033[2m"  # 暗色/灰色

# ── 难度配置 ──────────────────────────────────────────────────
DIFFICULTY_CONFIG = {
    "easy":   {"max_hints": 5, "time_limit": 180},
    "normal": {"max_hints": 3, "time_limit": 120},
    "hard":   {"max_hints": 1, "time_limit": 90},
}

# ── 关卡数据 ──────────────────────────────────────────────────
SUBSTITUTION_TABLE = {
    'A': 'S', 'B': 'V', 'C': 'I', 'D': 'F', 'E': 'T',
    'F': 'G', 'G': 'R', 'H': 'U', 'I': 'J', 'J': 'K',
    'K': 'L', 'L': 'Z', 'M': 'X', 'N': 'C', 'O': 'V',
    'P': 'B', 'Q': 'N', 'R': 'M', 'S': 'Q', 'T': 'W',
    'U': 'E', 'V': 'R', 'W': 'T', 'X': 'Y', 'Y': 'U',
    'Z': 'I', 'a': 's', 'b': 'v', 'c': 'i', 'd': 'f',
    'e': 't', 'f': 'g', 'g': 'r', 'h': 'u', 'i': 'j',
    'j': 'k', 'k': 'l', 'l': 'z', 'm': 'x', 'n': 'c',
    'o': 'v', 'p': 'b', 'q': 'n', 'r': 'm', 's': 'q',
    't': 'w', 'u': 'e', 'v': 'r', 'w': 't', 'x': 'y',
    'y': 'u', 'z': 'i',
}

REVERSE_SUBSTITUTION_TABLE = {v: k for k, v in SUBSTITUTION_TABLE.items()}


def _build_substitution_cipher():
    """加密 Fifteen -> Svssgrra using the substitution table."""
    result = []
    for ch in "Fifteen":
        if ch in SUBSTITUTION_TABLE:
            result.append(SUBSTITUTION_TABLE[ch])
        else:
            result.append(ch)
    return "".join(result)


def _build_level10_cipher():
    """综合挑战: 先用凯撒(位移3)再反转"""
    step1 = caesar_cipher("Code Breaker", 3)  # Frgh Euhdnhu
    step2 = reverse_text(step1)
    return step2


def _build_vigenere_cipher():
    """维吉尼亚: KEY加密"""
    return vigenere_encrypt("Hello World", "KEY")


LEVELS = [
    {
        "name": "凯撒位移",
        "hint_text": "每个字母向后移动了3位... 试试向前推3位",
        "ciphertext": "Khoor Zruog",
        "answer": "Hello World",
    },
    {
        "name": "凯撒随机",
        "hint_text": "凯撒大帝的经典密码，位移量在2-7之间",
        "ciphertext": None,  # 运行时随机生成
        "answer": None,
        "shift": None,
    },
    {
        "name": "反转字符串",
        "hint_text": "将文字从后往前读...",
        "ciphertext": "!dlroW olleH",
        "answer": "Hello World!",
    },
    {
        "name": "ROT13",
        "hint_text": "ROT13: 每个字母向后移动13位 (移26位回到原位)",
        "ciphertext": "Uryyb Jbeyq",
        "answer": "Hello World",
    },
    {
        "name": "简单替换",
        "hint_text": "每个字母被替换为另一个固定字母，见对照表",
        "ciphertext": _build_substitution_cipher(),
        "answer": "Fifteen",
        "substitution_table": SUBSTITUTION_TABLE,
    },
    {
        "name": "维吉尼亚密码",
        "hint_text": "密钥是 'KEY'，用密钥循环移位每个字母",
        "ciphertext": _build_vigenere_cipher(),
        "answer": "Hello World",
        "key": "KEY",
    },
    {
        "name": "Base64 编码",
        "hint_text": "这是一种常见的编码方式，以 = 结尾",
        "ciphertext": "SGVsbG8=",
        "answer": "Hello",
    },
    {
        "name": "摩尔斯电码",
        "hint_text": "点和划组成的电报码，字母间用空格分隔",
        "ciphertext": ".... . .-.. .-.. ---",
        "answer": "HELLO",
    },
    {
        "name": "二进制 ASCII",
        "hint_text": "每8位二进制代表一个字符",
        "ciphertext": "01001000 01100101 01101100 01101100 01101111",
        "answer": "Hello",
    },
    {
        "name": "综合挑战",
        "hint_text": "先用凯撒位移(3位)，然后再反转了字符串",
        "ciphertext": _build_level10_cipher(),
        "answer": "Code Breaker",
    },
]

# ── 生成第2关随机凯撒 ─────────────────────────────────────────
def _init_level2():
    shift = random.randint(2, 7)
    LEVELS[1]["shift"] = shift
    LEVELS[1]["ciphertext"] = caesar_cipher("Hello World", shift)
    LEVELS[1]["answer"] = "Hello World"
    LEVELS[1]["hint_text"] = f"凯撒大帝的经典密码，位移量 = {shift} (但先别告诉你，试试猜)"
    # Actually, let's not give away the shift in the hint
    LEVELS[1]["hint_text"] = "凯撒大帝的经典密码，位移量在2-7之间，从密文中找规律"


# ═══════════════════════════════════════════════════════════════
#  CodeBreakerGame 类
# ═══════════════════════════════════════════════════════════════
class CodeBreakerGame(BaseGame):
    """密码破译游戏 — 10关加密挑战"""

    WIDTH = 55

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "密码破译"

    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["normal"])
        self.max_hints_per_level = config["max_hints"]
        self.time_limit = config["time_limit"]

        self.lives = 3
        self.current_level = 0
        self.total_levels = 10
        self._input_buffer = ""
        self._game_over = False
        self._won = False
        self._hint_count = 0  # 当前关已用提示数
        self._hints_used_total = 0
        self._level_penalty = 0  # 当前关已扣除分数
        self._flash_color = None
        self._last_result = ""
        self._level_start_time = 0
        self._timer = GameTimer()

        # 初始化第2关随机位移
        _init_level2()

        # 开始第一关
        self._start_level()

    def _start_level(self):
        """开始当前关卡"""
        self._input_buffer = ""
        self._hint_count = 0
        self._level_penalty = 0
        self._flash_color = None
        self._last_result = ""
        self._timer.start()
        self._level_start_time = time.perf_counter()

    def _get_level_score(self):
        """获取当前关卡的基础分"""
        return (self.current_level + 1) * 100

    def _get_elapsed(self):
        return self._timer.get_elapsed()

    def handle_input(self, key):
        if key is None:
            return True
        if key == "q":
            self._game_over = True
            return False
        if key == "h":
            self._use_hint()
            return True
        if key in ("\r", "enter"):
            self._submit_answer()
            return True
        if key == "\x7f" or key == "\b":  # Backspace
            if self._input_buffer:
                self._input_buffer = self._input_buffer[:-1]
            return True
        # 可打印字符
        if len(key) == 1 and key.isprintable():
            self._input_buffer += key
        return True

    def _use_hint(self):
        """使用提示"""
        level = LEVELS[self.current_level]
        max_hints = min(self.max_hints_per_level, 2)  # 每关最多2次提示
        if self._hint_count < max_hints:
            self._hint_count += 1
            self._hints_used_total += 1
            # 扣10%当前关分数
            penalty = int(self._get_level_score() * 0.1)
            self._level_penalty += penalty
            self.score = max(0, self.score)
            self._last_result = f"{C.BYELLOW}提示 #{self._hint_count} (-{penalty}分){C.RESET}"

    def _submit_answer(self):
        """提交答案"""
        level = LEVELS[self.current_level]
        player_answer = self._input_buffer.strip()
        correct_answer = level["answer"]

        if player_answer == correct_answer:
            # 正确!
            level_score = self._get_level_score()
            earned = level_score - self._level_penalty
            self.score += max(0, earned)
            self._flash_color = C.GREEN
            self._last_result = f"{C.BGREEN}✓ 正确! +{max(0, earned)}{C.RESET}"
            self.current_level += 1
            if self.current_level >= self.total_levels:
                self._game_over = True
                self._won = True
            else:
                self._start_level()
        else:
            # 错误!
            self.lives -= 1
            penalty = int(self._get_level_score() * 0.2)
            self._level_penalty += penalty
            self._flash_color = C.RED
            self._last_result = f"{C.RED}✗ 错误! -{penalty}{C.RESET}"
            self._input_buffer = ""
            if self.lives <= 0:
                self._game_over = True
                self._won = False

    def _check_timeout(self):
        """检查是否超时"""
        if self._timer.get_elapsed() >= self.time_limit:
            self._game_over = True
            self._won = False
            self._last_result = f"{C.BYELLOW}⏱ 超时!{C.RESET}"

    def update(self):
        if self._game_over:
            return
        self._check_timeout()

    def render(self):
        level = LEVELS[self.current_level]
        lines = []

        # ── 标题行 ──
        title = f"密码破译 — 第 {self.current_level + 1}/{self.total_levels} 关"
        lines.append(center(f"{C.BOLD}{C.BCYAN}{'═' * self.WIDTH}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BOLD}{C.BCYAN}{title}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BOLD}{C.BCYAN}{'═' * self.WIDTH}{C.RESET}", self.WIDTH))
        lines.append("")

        # ── 状态栏 ──
        elapsed = int(self._timer.get_elapsed())
        remaining = max(0, self.time_limit - elapsed)
        hearts = C.RED + "♥" * self.lives + C.RESET + DIM + "♡" * (3 - self.lives) + C.RESET if self.lives < 3 else C.RED + "♥" * 3 + C.RESET
        score_color = C.BGREEN if self.score > 0 else C.BWHITE
        status = (
            f"{score_color}得分: {self.score}{C.RESET}  "
            f"{C.BOLD}生命: {hearts}{C.RESET}  "
            f"{C.BYELLOW}⏱ {remaining}s/{self.time_limit}s{C.RESET}"
        )
        lines.append(center(status, self.WIDTH))
        lines.append("")

        # ── 加密文本框 ──
        cipher_text = f'"{level["ciphertext"]}"'
        cipher_display = f"{C.BOLD}{C.BCYAN}{cipher_text}{C.RESET}"
        level_name = f"({level['name']})"
        lines.append(box(f" 加密文本 {DIM}{level_name}{C.RESET}", [
            center(cipher_display, self.WIDTH - 2),
        ], self.WIDTH))
        lines.append("")

        # ── 第5关额外显示对照表 ──
        if self.current_level == 4 and level.get("substitution_table"):
            table_lines = []
            # Show first row: A B C ... M
            row1 = " ".join(f"{ch}->{SUBSTITUTION_TABLE[ch]}" for ch in "ABCDEFGHIJKLM")
            row2 = " ".join(f"{ch}->{SUBSTITUTION_TABLE[ch]}" for ch in "NOPQRSTUVWXYZ")
            table_lines.append(f"  {DIM}{row1}{C.RESET}")
            table_lines.append(f"  {DIM}{row2}{C.RESET}")
            lines.append(box(" 替换对照表", table_lines, self.WIDTH))
            lines.append("")

        # ── 提示框 ──
        max_hints = min(self.max_hints_per_level, 2)
        hint_color = C.BLUE if self._hint_count < max_hints else DIM
        hint_line = f"{hint_color}{level['hint_text']}{C.RESET}" if self._hint_count == 0 else (
            f"{hint_color}提示 #{self._hint_count}/{max_hints}: {level['hint_text']}{C.RESET}"
        )
        lines.append(box(" 提示 [H]", [hint_line], self.WIDTH))
        lines.append("")

        # ── 上次结果 ──
        if self._last_result:
            lines.append(center(self._last_result, self.WIDTH))
            lines.append("")

        # ── 输入行 ──
        cursor = f"{C.BOLD}{C.BWHITE}█{C.RESET}"
        input_display = f"{C.BWHITE}你的答案 > {self._input_buffer}{cursor}{C.RESET}"
        lines.append(center(input_display, self.WIDTH))
        lines.append("")

        # ── 操作提示 ──
        lines.append(f"  {DIM}[H]提示  [Q]退出  [Backspace]删除  [Enter]提交{C.RESET}")

        self._renderer.render_frame(lines)

    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 密 码 破 译 "))
        lines.append("")

        if self._won:
            lines.append(center(f"{C.BGREEN}🎉 全部破解!{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束 — 第 {self.current_level + 1} 关{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}通过关卡: {self.current_level}/{self.total_levels}{C.RESET}", self.WIDTH))
        lines.append(center(f"提示使用: {self._hints_used_total} 次", self.WIDTH))
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
                    self._timer.resume()
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

    def show_help(self) -> str:
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["normal"])
        return (
            f"\n  {C.BOLD}{C.CYAN}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  {C.BWHITE}10{C.RESET} 关加密挑战，每关一种加密方式\n"
            f"  根据密文和提示，猜出原文\n"
            f"\n  {C.BGREEN}答对{C.RESET} → 关卡序号 × 100 分\n"
            f"  {C.RED}答错{C.RESET} → 扣除当前关 20% 分数\n"
            f"  {C.BYELLOW}提示{C.RESET} → 扣除当前关 10% 分数 (每关最多{min(config['max_hints'], 2)}次)\n"
            f"  {C.BYELLOW}生命{C.RESET} → 共 3 次错误机会，用完游戏结束\n"
            f"\n  操作: 输入答案  [Enter]提交  [H]提示  [Q]退出\n"
            f"  时间限制: {config['time_limit']} 秒\n"
        )
