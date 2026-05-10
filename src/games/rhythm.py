"""G4 节奏大师游戏 — 按键节奏挑战"""

import time
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.ui import colors as C
from src.ui.components import box, center, header, divider

# 补充 colors.py 中没有的颜色
DIM = "\033[2m"  # 暗色/灰色

# ── 难度配置 ──────────────────────────────────────────────────
DIFFICULTY_CONFIG = {
    "easy":   {"bpm": 60,  "keys": [" "],       "num_notes": 15},
    "normal": {"bpm": 90,  "keys": ["A", "D"],   "num_notes": 20},
    "hard":   {"bpm": 120, "keys": ["D", "F", "J", "K"], "num_notes": 25},
}

# ── 渲染常量 ──────────────────────────────────────────────────
WIDTH = 55
JUDGE_X = 0              # 判定区 x 位置
TRAVEL_WIDTH = 42        # 音符移动区域宽度
TRAVEL_RIGHT = JUDGE_X + TRAVEL_WIDTH  # 最右侧 x
TRAVEL_DURATION = 2.5    # 音符从右到左需要多少秒
NOTE_DISPLAY = "┌─┐"     # 音符外框
NOTE_CHAR_FMT = "│{}│"   # 音符内字符
NOTE_WIDTH = 3           # 音符占用宽度
PERFECT_WINDOW = 0.15    # Perfect 误差阈值 (秒)
GOOD_WINDOW = 0.35       # Good 误差阈值 (秒)


# ═══════════════════════════════════════════════════════════════
#  RhythmGame 类
# ═══════════════════════════════════════════════════════════════
class RhythmGame(BaseGame):
    """节奏大师游戏 — 跟随节拍按键"""

    WIDTH = WIDTH

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "节奏大师"

    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["normal"])
        self.bpm = config["bpm"]
        self.keys = config["keys"]
        self.num_notes = config["num_notes"]

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self._game_over = False
        self._won = False
        self._notes = []
        self._judgments = []  # 最近的判定结果 [(text, color, time)]
        self._total_perfect = 0
        self._total_good = 0
        self._total_miss = 0
        self._start_time = 0
        self._game_started = False
        self._last_key_time = {}
        self._note_hit_times = {}  # track hit times for position calc
        self._countdown = 3  # 倒计时

        # 预生成音符
        self._generate_notes()

    def _generate_notes(self):
        """根据 BPM 预生成所有音符"""
        beat_interval = 60.0 / self.bpm  # 每个节拍间隔(秒)
        self._notes = []

        for i in range(self.num_notes):
            target_time = 2.0 + i * beat_interval  # 从2秒开始，每个节拍一个音符
            key = random.choice(self.keys)
            # 计算轨道: 单键=0, 双键=0/1, 四键=0/1/2/3
            track = self.keys.index(key)

            self._notes.append({
                "track": track,
                "key": key,
                "target_time": target_time,
                "hit": False,
                "missed": False,
            })

    def _get_elapsed(self):
        """获取游戏已进行时间"""
        if not self._game_started:
            return 0.0
        return time.perf_counter() - self._start_time

    def _get_note_x(self, note):
        """计算音符的 x 位置（基于时间）"""
        elapsed = self._get_elapsed()
        time_until_target = note["target_time"] - elapsed

        # 音符应该在 TRAVEL_DURATION 前出现，在 target_time 到达判定区
        if time_until_target > TRAVEL_DURATION:
            return TRAVEL_RIGHT  # 还没出现，保持在右边
        elif time_until_target <= -0.5:
            return -NOTE_WIDTH  # 已经飞过去了
        else:
            # 线性映射: TRAVEL_DURATION -> TRAVEL_RIGHT, 0 -> JUDGE_X
            progress = time_until_target / TRAVEL_DURATION  # 1.0 = 刚出现, 0.0 = 到达
            x = JUDGE_X + int(progress * TRAVEL_WIDTH)
            return max(JUDGE_X, min(TRAVEL_RIGHT, x))

    def handle_input(self, key):
        if key is None:
            return True
        if key == "q":
            self._game_over = True
            return False
        if key == "h":
            return True  # 帮助由 game_loop 处理

        # 倒计时阶段
        if self._countdown > 0:
            return True

        # 检查是否是对应的游戏键
        if key.upper() in [k.upper() for k in self.keys]:
            key_upper = key.upper()
            now = self._get_elapsed()

            # 找到最近的未命中音符（匹配的键）
            best_note = None
            best_diff = float("inf")

            for note in self._notes:
                if note["hit"] or note["missed"]:
                    continue
                if note["key"].upper() != key_upper:
                    continue

                diff = abs(now - note["target_time"])
                if diff < best_diff:
                    best_diff = diff
                    best_note = note

            if best_note is not None:
                if best_diff <= PERFECT_WINDOW:
                    best_note["hit"] = True
                    self._total_perfect += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    pts = 100 + self.combo * 10
                    self.score += pts
                    self._add_judgment(f"Perfect! ★ +{pts}", C.BGREEN)
                elif best_diff <= GOOD_WINDOW:
                    best_note["hit"] = True
                    self._total_good += 1
                    self.combo += 1
                    self.max_combo = max(self.max_combo, self.combo)
                    pts = 50 + self.combo * 5
                    self.score += pts
                    self._add_judgment(f"Good! +{pts}", C.BYELLOW)
                # else: 太远了，不处理（可能是误触）

        return True

    def _add_judgment(self, text, color):
        """添加判定结果显示"""
        self._judgments.append((text, color, time.perf_counter()))
        # 只保留最近2条
        if len(self._judgments) > 2:
            self._judgments = self._judgments[-2:]

    def _check_auto_miss(self):
        """检查是否有音符已经飞过判定区且未被击中"""
        elapsed = self._get_elapsed()
        for note in self._notes:
            if note["hit"] or note["missed"]:
                continue
            # 如果已经超过判定时间 + GOOD_WINDOW 还没有被击中
            if elapsed > note["target_time"] + GOOD_WINDOW:
                note["missed"] = True
                self._total_miss += 1
                self.combo = 0
                self._add_judgment("Miss!", C.RED)

    def _check_game_end(self):
        """检查游戏是否结束"""
        if not self._game_started:
            return
        elapsed = self._get_elapsed()
        # 最后一个音符的判定时间 + 缓冲
        if self._notes:
            last_note_time = max(n["target_time"] for n in self._notes)
            if elapsed > last_note_time + GOOD_WINDOW + 1.0:
                self._game_over = True
                self._won = True

    def _check_all_perfect(self):
        """检查是否全部 Perfect"""
        total_hit = self._total_perfect + self._total_good
        if total_hit == 0:
            return False
        return self._total_good == 0 and self._total_miss == 0

    def _get_rank(self):
        """获取评级"""
        total = len(self._notes)
        if total == 0:
            return "C"
        all_perfect = self._total_good == 0 and self._total_miss == 0 and self._total_perfect == total
        if all_perfect:
            return "S"
        if self._total_perfect / total >= 0.9:
            return "A"
        pg_ratio = (self._total_perfect + self._total_good) / total
        if pg_ratio >= 0.7:
            return "B"
        return "C"

    def update(self):
        if self._game_over:
            return

        # 倒计时
        if self._countdown > 0:
            elapsed = self._get_elapsed()
            self._countdown = 3 - int(elapsed)
            if self._countdown <= 0:
                self._countdown = 0
                self._game_started = True
                self._start_time = time.perf_counter() + 0.5  # 短暂延迟后正式开始
                # Adjust: reset start_time properly
                self._start_time = time.perf_counter() + 2.0
            return

        elapsed = self._get_elapsed()

        # 自动判定错过
        self._check_auto_miss()

        # 检查游戏结束
        self._check_game_end()

        # 清理旧判定
        now = time.perf_counter()
        self._judgments = [(t, c, ts) for t, c, ts in self._judgments if now - ts < 2.0]

    def render(self):
        lines = []

        # ── 倒计时 ──
        if self._countdown > 0:
            count_str = f"{C.BOLD}{C.BCYAN}{self._countdown}{C.RESET}"
            lines.append(center(f"♪ {C.BOLD}{C.BCYAN}节奏大师{C.RESET}  BPM:{self.bpm} ♪", self.WIDTH))
            lines.append("")
            lines.append(center(f"准备开始... {count_str}", self.WIDTH))
            lines.append("")
            lines.append(center(f"{DIM}音符: {len(self._notes)}  按键: {' '.join(self.keys)}{C.RESET}", self.WIDTH))
            self._renderer.render_frame(lines)
            return

        # ── 标题行 ──
        header_text = f"♪ {C.BOLD}{C.BCYAN}节奏大师{C.RESET}  BPM:{self.bpm}  Combo:{self.combo} ♪"
        lines.append(center(header_text, self.WIDTH))
        lines.append(center(f"{C.BGREEN}得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append("")

        # ── 轨道渲染区 ──
        num_tracks = len(self.keys)

        # 创建网格 [轨道行][列]
        grid = [[" " for _ in range(WIDTH)] for _ in range(num_tracks)]

        # 渲染判定区标记
        for t in range(num_tracks):
            if WIDTH > 4:
                grid[t][0] = f"{C.BWHITE}[{C.RESET}"
                if WIDTH > 5:
                    grid[t][1] = f"{C.BWHITE}={C.RESET}"
                if WIDTH > 6:
                    grid[t][2] = f"{C.BWHITE}]{C.RESET}"

        # 渲染音符
        for note in self._notes:
            if note["hit"] or note["missed"]:
                continue

            x = self._get_note_x(note)
            track = note["track"]

            if x < 0 or x >= WIDTH - NOTE_WIDTH + 1:
                continue

            if track >= num_tracks:
                continue

            # 判断颜色：靠近判定区变亮
            elapsed = self._get_elapsed()
            time_diff = abs(elapsed - note["target_time"])
            if time_diff < PERFECT_WINDOW:
                color = C.BGREEN
            elif time_diff < GOOD_WINDOW:
                color = C.BYELLOW
            else:
                color = C.CYAN

            row = grid[track]
            # 绘制音符: ┌─┐ / │K│
            if 0 <= x < WIDTH:
                row[x] = f"{color}┌{C.RESET}"
            if 0 <= x + 1 < WIDTH:
                row[x + 1] = f"{color}─{C.RESET}"
            if 0 <= x + 2 < WIDTH:
                row[x + 2] = f"{color}┐{C.RESET}"

            # 第二行: 字符
            if track + 1 < num_tracks:
                row2 = grid[track]
                if 0 <= x < WIDTH:
                    row[x] = f"{color}│{C.RESET}"
                if 0 <= x + 1 < WIDTH:
                    key_char = note["key"] if note["key"] != " " else "␣"
                    row[x + 1] = f"{color}{key_char}{C.RESET}"
                if 0 <= x + 2 < WIDTH:
                    row[x + 2] = f"{color}│{C.RESET}"

        # 输出轨道行
        for t in range(num_tracks):
            line = "".join(grid[t])
            lines.append(line)

        # ── 判定区底部 ──
        judge_line = f"{C.BWHITE}[判定区]{C.RESET}" + f"{DIM}{'─' * (WIDTH - len('[判定区]'))}{C.RESET}"
        lines.append(judge_line)
        lines.append("")

        # ── 判定结果 ──
        if self._judgments:
            latest = self._judgments[-1]
            lines.append(center(f"{latest[1]}{latest[0]}{C.RESET}", self.WIDTH))
            lines.append("")

        # ── 进度/操作提示 ──
        hit_count = self._total_perfect + self._total_good + self._total_miss
        progress = f"音符: {hit_count}/{self.num_notes}"
        lines.append(f"  {DIM}{progress}  按键: {'  '.join(f'[{k}]' if k != ' ' else '[空格]' for k in self.keys)}  [Q]退出{C.RESET}")

        self._renderer.render_frame(lines)

    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 节 奏 大 师 "))
        lines.append("")

        if self._won:
            lines.append(center(f"{C.BGREEN}🎵 演奏完成！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束{C.RESET}", self.WIDTH))

        lines.append("")

        # 评级
        rank = self._get_rank()
        rank_colors = {"S": C.BYELLOW, "A": C.BGREEN, "B": C.BCYAN, "C": C.BWHITE}
        rank_color = rank_colors.get(rank, C.BWHITE)
        lines.append(center(f"{C.BOLD}{rank_color}评级: {rank}{C.RESET}", self.WIDTH))
        lines.append("")

        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}最大连击: {self.max_combo}{C.RESET}", self.WIDTH))
        lines.append("")

        # 统计
        stats = [
            f"{C.BGREEN}Perfect: {self._total_perfect}{C.RESET}",
            f"{C.BYELLOW}Good:    {self._total_good}{C.RESET}",
            f"{C.RED}Miss:    {self._total_miss}{C.RESET}",
        ]
        for stat in stats:
            lines.append(center(stat, self.WIDTH))

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
        # 开始倒计时
        self._start_time = time.perf_counter()

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
            time.sleep(0.03)

        # 游戏结束画面
        self._render_final()
        print("\n  ", end="")
        self._input_manager.get_key()

    def show_help(self) -> str:
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["normal"])
        key_display = "空格" if config["keys"] == [" "] else " / ".join(config["keys"])
        return (
            f"\n  {C.BOLD}{C.CYAN}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  音符从右向左移动，到达左侧判定区时\n"
            f"  按下对应的按键！\n"
            f"\n  {C.BGREEN}Perfect{C.RESET} → 误差 < 0.15s → +100 + Combo×10\n"
            f"  {C.BYELLOW}Good{C.RESET}     → 误差 < 0.35s → +50 + Combo×5\n"
            f"  {C.RED}Miss{C.RESET}     → 误差过大 → 0分，连击清零\n"
            f"  {C.BYELLOW}全Perfect{C.RESET} → 额外 +1000 分\n"
            f"\n  按键: {key_display}\n"
            f"  BPM: {config['bpm']}  音符数: {config['num_notes']}\n"
            f"  操作: [Q]退出  [H]帮助\n"
        )
