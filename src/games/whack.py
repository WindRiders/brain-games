"""G5 打地鼠游戏 — 快速反应击中目标"""

import time
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.ui import colors as C
from src.ui.components import box, center, header, divider, progress_bar
from src.engine.timer import GameTimer

# 补充 colors.py 中没有的颜色
DIM = "\033[2m"  # 暗色/灰色

# ── 难度配置 ──────────────────────────────────────────────────
DIFFICULTY_CONFIG = {
    "easy":   {"moles_per_round": 1, "interval": 3.0, "total_rounds": 20},
    "normal": {"moles_per_round": (1, 2), "interval": 2.0, "total_rounds": 25},
    "hard":   {"moles_per_round": (1, 3), "interval": 1.0, "total_rounds": 30},
}

# 3x3 格子编号
GRID = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]

# 格子宽度
CELL_W = 11
CELL_H = 2


# ═══════════════════════════════════════════════════════════════
#  WhackAMoleGame 类
# ═══════════════════════════════════════════════════════════════
class WhackAMoleGame(BaseGame):
    """打地鼠游戏 — 快速反应击中目标！"""

    WIDTH = 55

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "打地鼠"

    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        self._moles_range = config["moles_per_round"]
        self._interval = config["interval"]
        self._total_rounds = config["total_rounds"]

        self.score = 0
        self._combo = 0
        self._max_combo = 0
        self._current_round = 0
        self._moles_active = set()   # 当前轮出现的格子编号
        self._last_result = ""       # 上一轮结果文字
        self._last_result_color = ""
        self._game_over = False
        self._won = False
        self._round_start = 0.0
        self._round_done = False     # 当前轮是否已处理
        self._timer = GameTimer()
        self._hit_count = 0
        self._miss_count = 0

    def _pick_moles(self) -> set:
        """随机选择本轮出现的地鼠格子"""
        if isinstance(self._moles_range, tuple):
            count = random.randint(self._moles_range[0], self._moles_range[1])
        else:
            count = self._moles_range
        count = min(count, 9)
        return set(random.sample(range(1, 10), count))

    def _render_grid(self) -> list[str]:
        """渲染 3x3 网格"""
        lines = []

        # 顶部边框
        top = ""
        for col in range(3):
            top += f"┌{'─' * CELL_W}┐" if col == 0 else f"┬{'─' * CELL_W}┐"
        # 修正：整行
        top_parts = []
        for col in range(3):
            if col == 0:
                top_parts.append(f"┌{'─' * CELL_W}")
            elif col == 2:
                top_parts.append(f"{'─' * CELL_W}┐")
            else:
                top_parts.append(f"{'─' * CELL_W}")
        top_line = top_parts[0] + "┬" + top_parts[1] + "┬" + top_parts[2]
        lines.append(f"  {top_line}")

        # 第一行内容（格子1-3）
        row_lines = self._render_row(0, [1, 2, 3])
        lines.extend(row_lines)

        # 中间分隔线
        mid = ""
        for col in range(3):
            if col == 0:
                mid += f"├{'─' * CELL_W}"
            elif col == 2:
                mid += f"{'─' * CELL_W}┤"
            else:
                mid += f"{'─' * CELL_W}"
        mid_line = mid[:0] + f"├{'─' * CELL_W}┼{'─' * CELL_W}┼{'─' * CELL_W}┤"
        lines.append(f"  {mid_line}")

        # 第二行内容（格子4-6）
        row_lines = self._render_row(1, [4, 5, 6])
        lines.extend(row_lines)

        # 中间分隔线
        lines.append(f"  {mid_line}")

        # 第三行内容（格子7-9）
        row_lines = self._render_row(2, [7, 8, 9])
        lines.extend(row_lines)

        # 底部边框
        bot_line = f"└{'─' * CELL_W}┴{'─' * CELL_W}┴{'─' * CELL_W}┘"
        lines.append(f"  {bot_line}")

        return lines

    def _render_row(self, row: int, cell_ids: list[int]) -> list[str]:
        """渲染一行（包含格子内编号和地鼠）"""
        rows = []

        # 编号行
        cells = []
        for cid in cell_ids:
            if cid in self._moles_active:
                cell = f"{C.BG_YELLOW}{C.BOLD}  🐹 {cid}  {C.RESET}"
                # 补齐到 CELL_W 可见宽度
                visible = f"  🐹 {cid}  "
                pad = CELL_W - len(visible)
                cell = f"{C.BG_YELLOW}{C.BOLD}  🐹 {cid}  {' ' * pad}{C.RESET}"
            else:
                pad = CELL_W - len(f"  {cid}  ")
                cell = f"  {cid}  {' ' * pad}"
            cells.append(cell)

        row1 = ""
        for i, cell in enumerate(cells):
            if i == 0:
                row1 += f"│{cell}"
            elif i == 2:
                row1 += f"│{cell}│"
            else:
                row1 += f"│{cell}"
        rows.append(f"  {row1}")

        # 空白行
        row2 = ""
        for i in range(3):
            if i == 0:
                row2 += f"│{' ' * CELL_W}"
            elif i == 2:
                row2 += f"{' ' * CELL_W}│"
            else:
                row2 += f"{' ' * CELL_W}"
        rows.append(f"  {row2}")

        return rows

    def _process_result(self, key: str):
        """处理玩家输入"""
        self._round_done = True
        try:
            pressed = int(key)
        except ValueError:
            self._last_result = f"{C.BRED}无效按键{C.RESET}"
            self._last_result_color = C.RED
            self._combo = 0
            self._miss_count += 1
            return

        hit = False
        for mole in self._moles_active:
            if mole == pressed:
                hit = True
                break

        if hit:
            self._moles_active.discard(pressed)
            self.score += 100
            self._combo += 1
            self._max_combo = max(self._max_combo, self._combo)
            self._hit_count += 1

            bonus_text = ""
            if self._combo > 0 and self._combo % 5 == 0:
                self.score += 200
                bonus_text = f" {C.BYELLOW}🔥连击+200!{C.RESET}"

            self._last_result = f"{C.BGREEN}✓打中! +100{C.RESET}{bonus_text}"
        else:
            self._combo = 0
            self._miss_count += 1
            self._last_result = f"{C.RED}✗没打到!{C.RESET}"

    def handle_input(self, key):
        if key is None:
            return True
        if key == "q":
            self._game_over = True
            return False
        if key == "h":
            return True

        if not self._round_done and key in "123456789":
            self._process_result(key)

        return True

    def update(self):
        if self._game_over or self._round_done:
            return

        # 检查超时
        elapsed = self._timer.get_elapsed()
        if elapsed >= self._interval:
            self._round_done = True
            self.score -= 30
            self._combo = 0
            self._miss_count += 1
            self._last_result = f"{C.BRED}✗跑掉了! -30{C.RESET}"

    def render(self):
        lines = []

        if self._round_done:
            # 显示结果
            diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
            lines.append(center(f"{C.BOLD}{C.BYELLOW}打 地 鼠 — {diff_name}难度{C.RESET}", self.WIDTH))
            lines.append("")
            lines.append(center(f"{C.BOLD}{C.BGREEN}得分: {self.score}{C.RESET}  "
                                f"{C.BOLD}{C.BCYAN}回合: {self._current_round}/{self._total_rounds}{C.RESET}  "
                                f"{C.BOLD}{C.BMAGENTA}连击: {self._combo}{C.RESET}", self.WIDTH))
            lines.append("")

            # 网格（没有地鼠）
            grid_lines = self._render_grid()
            lines.extend(grid_lines)
            lines.append("")

            lines.append(center(self._last_result, self.WIDTH))
            lines.append("")
            lines.append(center(f"{DIM}按任意键继续...{C.RESET}", self.WIDTH))

            self._renderer.render_frame(lines)
            return

        # 游戏进行中
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        lines.append(center(f"{C.BOLD}{C.BYELLOW}打 地 鼠 — {diff_name}难度{C.RESET}", self.WIDTH))
        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}得分: {self.score}{C.RESET}  "
                            f"{C.BOLD}{C.BCYAN}回合: {self._current_round}/{self._total_rounds}{C.RESET}  "
                            f"{C.BOLD}{C.BMAGENTA}连击: {self._combo}{C.RESET}", self.WIDTH))
        lines.append("")

        # 网格
        grid_lines = self._render_grid()
        lines.extend(grid_lines)
        lines.append("")

        # 倒计时进度条
        elapsed = self._timer.get_elapsed()
        pct = max(0, 100 - (elapsed / self._interval * 100))
        lines.append(center(f"  {progress_bar(pct, 30)}  剩余: {max(0, self._interval - elapsed):.1f}s", self.WIDTH))

        if self._last_result:
            lines.append(center(self._last_result, self.WIDTH))

        lines.append("")
        lines.append(center(f"{DIM}按数字键 1-9 打地鼠  [Q]退出 [H]帮助{C.RESET}", self.WIDTH))

        self._renderer.render_frame(lines)

    def _start_round(self):
        """开始新一轮"""
        self._current_round += 1
        if self._current_round > self._total_rounds:
            self._game_over = True
            self._won = True
            return

        self._moles_active = self._pick_moles()
        self._round_done = False
        self._timer = GameTimer()
        self._timer.start()

    def game_loop(self):
        self._start_round()

        while not self._game_over:
            key = self._input_manager.get_key_nonblocking()
            if key is not None:
                if key == "h":
                    help_text = self.show_help()
                    self._renderer.clear()
                    print(help_text)
                    print("\n  按任意键继续...")
                    self._input_manager.get_key()
                    # 重新初始化当前轮
                    self._start_round()
                    continue
                if not self.handle_input(key):
                    break

            self.update()
            self.render()
            time.sleep(0.03)

            # 如果本轮已处理，等待按键进入下一轮
            if self._round_done and not self._game_over:
                # 清掉缓冲区中的按键
                self._input_manager.get_key()
                self._start_round()

        # 游戏结束画面
        self._render_final()
        print("\n  ", end="")
        self._input_manager.get_key()

    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 打 地 鼠 "))
        lines.append("")

        if self._won:
            lines.append(center(f"{C.BGREEN}🎉 游戏完成！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}最高连击: {self._max_combo}{C.RESET}", self.WIDTH))
        lines.append(center(f"命中: {C.BGREEN}{self._hit_count}{C.RESET}  "
                            f"未命中: {C.BRED}{self._miss_count}{C.RESET}", self.WIDTH))
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

    def show_help(self) -> str:
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        if isinstance(config["moles_per_round"], tuple):
            mole_desc = f"{config['moles_per_round'][0]}-{config['moles_per_round'][1]}只/轮"
        else:
            mole_desc = f"{config['moles_per_round']}只/轮"

        return (
            f"\n  {C.BOLD}{C.BYELLOW}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  3x3 九宫格中会随机出现地鼠 🐹\n"
            f"  快速按下对应的数字键(1-9)击打！\n"
            f"\n  {C.BGREEN}打中{C.RESET} → +100 分\n"
            f"  {C.BRED}超时{C.RESET} → -30 分\n"
            f"  {C.BYELLOW}连击5次{C.RESET} → +200 额外奖励\n"
            f"\n  每轮 {mole_desc}，间隔 {config['interval']}s，共 {config['total_rounds']} 轮\n"
            f"  操作: 数字键1-9 打地鼠  [Q]退出  [H]帮助\n"
        )
