"""G7 贪吃蛇记忆游戏 — 按顺序吃食物的贪吃蛇"""

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
    "easy":   {"width": 20, "height": 15, "mem_time": 5.0, "obstacles": 0,  "speed": 0.25},
    "normal": {"width": 20, "height": 15, "mem_time": 3.0, "obstacles": 3,  "speed": 0.20},
    "hard":   {"width": 25, "height": 20, "mem_time": 2.0, "obstacles": 5,  "speed": 0.15},
}

# 食物 Unicode 序号
CIRCLED_NUMS = {
    1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤",
    6: "⑥", 7: "⑦", 8: "⑧", 9: "⑨",
}

STAR_CHAR = "★"
SNAKE_HEAD_CHAR = "█"
SNAKE_BODY_CHAR = "█"
OBSTACLE_CHAR = "#"
EMPTY_CHAR = "·"


# ═══════════════════════════════════════════════════════════════
#  MemorySnakeGame 类
# ═══════════════════════════════════════════════════════════════
class MemorySnakeGame(BaseGame):
    """贪吃蛇记忆游戏 — 按顺序吃食物的贪吃蛇！"""

    WIDTH = 55

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "贪吃蛇记忆"

    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        self._field_w = config["width"]
        self._field_h = config["height"]
        self._mem_time = config["mem_time"]
        self._num_obstacles = config["obstacles"]
        self._move_interval = config["speed"]

        self.score = 0
        self._level = 1
        self._max_level = 0
        self._game_over = False
        self._won = False
        self._phase = "memorize"  # "memorize" or "play"
        self._mem_timer = GameTimer()
        self._move_timer = GameTimer()

        # 蛇: [(x, y), ...] 头部在最后
        cx = self._field_w // 2
        cy = self._field_h // 2
        self._snake = [(cx - 2, cy), (cx - 1, cy), (cx, cy)]
        self._direction = "right"
        self._next_direction = "right"

        # 食物: [(x, y, number), ...]
        self._foods = []
        self._next_food_num = 1  # 下一个要吃的食物编号

        # 障碍物: set of (x, y)
        self._obstacles = set()

        # 状态
        self._message = ""
        self._message_color = ""
        self._consecutive_levels = 0  # 连续通关数
        self._total_foods_eaten = 0
        self._last_result = ""

        self._generate_level()

    def _generate_level(self):
        """生成当前关卡"""
        num_foods = self._level
        cx = self._field_w // 2
        cy = self._field_h // 2

        # 重置蛇
        self._snake = [(cx - 2, cy), (cx - 1, cy), (cx, cy)]
        self._direction = "right"
        self._next_direction = "right"
        self._next_food_num = 1

        # 生成障碍物
        self._obstacles = set()
        if self._num_obstacles > 0:
            for _ in range(self._num_obstacles):
                for _attempt in range(100):
                    ox = random.randint(2, self._field_w - 3)
                    oy = random.randint(2, self._field_h - 3)
                    # 不能放在蛇身上
                    if (ox, oy) not in self._snake:
                        # 障碍物占3格横放
                        if (ox + 1, oy) not in self._snake and (ox + 2, oy) not in self._snake:
                            if ox + 2 < self._field_w:
                                self._obstacles.add((ox, oy))
                                self._obstacles.add((ox + 1, oy))
                                self._obstacles.add((ox + 2, oy))
                                break

        # 生成食物（不在蛇和障碍物上）
        occupied = set(self._snake) | self._obstacles
        self._foods = []
        placed = 0
        for _ in range(1000):
            if placed >= num_foods:
                break
            fx = random.randint(1, self._field_w - 2)
            fy = random.randint(1, self._field_h - 2)
            if (fx, fy) not in occupied:
                self._foods.append((fx, fy, placed + 1))
                occupied.add((fx, fy))
                placed += 1

        # 进入记忆阶段
        self._phase = "memorize"
        self._mem_timer = GameTimer()
        self._mem_timer.start()

    def _get_circled(self, n: int) -> str:
        """获取带圈数字"""
        if 1 <= n <= 9:
            return CIRCLED_NUMS[n]
        return str(n)

    def _is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self._field_w and 0 <= y < self._field_h

    def handle_input(self, key):
        if key is None:
            return True
        if key == "q":
            self._game_over = True
            return False
        if key == "h":
            return True

        # 方向控制（记忆阶段不允许移动）
        if self._phase == "play":
            dir_map = {
                "w": "up", "up": "up",
                "s": "down", "down": "down",
                "a": "left", "left": "left",
                "d": "right", "right": "right",
            }
            new_dir = dir_map.get(key)
            if new_dir:
                # 不能反向掉头
                opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
                if opposites.get(new_dir) != self._direction:
                    self._next_direction = new_dir

        return True

    def update(self):
        if self._game_over:
            return

        if self._phase == "memorize":
            # 检查记忆时间是否结束
            elapsed = self._mem_timer.get_elapsed()
            if elapsed >= self._mem_time:
                self._phase = "play"
                self._move_timer = GameTimer()
                self._move_timer.start()
            return

        # 游戏阶段 - 基于定时器移动
        elapsed = self._move_timer.get_elapsed()
        if elapsed < self._move_interval:
            return

        # 重置移动计时器
        self._move_timer = GameTimer()
        self._move_timer.start()

        # 更新方向
        self._direction = self._next_direction

        # 计算新头部位置
        head_x, head_y = self._snake[-1]
        if self._direction == "up":
            head_y -= 1
        elif self._direction == "down":
            head_y += 1
        elif self._direction == "left":
            head_x -= 1
        elif self._direction == "right":
            head_x += 1

        # 碰撞检测：撞墙
        if not self._is_in_bounds(head_x, head_y):
            self._game_over = True
            self._won = False
            self._last_result = f"{C.BRED}💥 撞墙了！游戏结束{C.RESET}"
            return

        # 碰撞检测：撞自己
        if (head_x, head_y) in self._snake[1:]:  # 不检测尾部（会移动）
            self._game_over = True
            self._won = False
            self._last_result = f"{C.BRED}💥 撞到自己了！游戏结束{C.RESET}"
            return

        # 碰撞检测：撞障碍物
        if (head_x, head_y) in self._obstacles:
            self._game_over = True
            self._won = False
            self._last_result = f"{C.BRED}💥 撞到障碍物了！游戏结束{C.RESET}"
            return

        # 检查是否吃到食物
        food_idx = None
        for i, (fx, fy, fn) in enumerate(self._foods):
            if fx == head_x and fy == head_y:
                if fn == self._next_food_num:
                    # 正确顺序
                    food_idx = i
                    points = 100 * self._level
                    self.score += points
                    self._total_foods_eaten += 1
                    self._message = f"✓ 吃对 {self._get_circled(fn)}! +{points}"
                    self._message_color = C.BGREEN
                    break
                else:
                    # 错误顺序
                    self._game_over = True
                    self._won = False
                    self._last_result = f"{C.BRED}✗ 吃错了！应该吃 {self._get_circled(self._next_food_num)}{C.RESET}"
                    return

        # 移动蛇
        if food_idx is not None:
            # 吃到食物：不移除尾部（蛇变长）
            self._snake.append((head_x, head_y))
            self._foods.pop(food_idx)
            self._next_food_num += 1

            # 检查是否吃完本关
            if not self._foods:
                # 关卡完成
                self._consecutive_levels += 1
                level_bonus = 500 + 200 * self._level
                self.score += level_bonus
                self._message = f"🎉 第 {self._level} 关完成! +{level_bonus}"
                self._message_color = C.BYELLOW
                self._max_level = max(self._max_level, self._level)
                self._level += 1

                # 短暂显示结果后进入下一关
                self._phase = "memorize"
                self._generate_level()
        else:
            # 没吃到食物：正常移动
            self._snake.append((head_x, head_y))
            self._snake.pop(0)  # 移除尾部

    def _render_field(self) -> list[str]:
        """渲染游戏场地"""
        lines = []

        # 顶部边框
        top = f"┌{'─' * self._field_w}┐"
        lines.append(f"  {top}")

        # 创建字符网格
        grid = [[" " for _ in range(self._field_w)] for _ in range(self._field_h)]

        # 填充空字符
        for y in range(self._field_h):
            for x in range(self._field_w):
                grid[y][x] = f"{DIM}{EMPTY_CHAR}{C.RESET}"

        # 障碍物
        for ox, oy in self._obstacles:
            if 0 <= oy < self._field_h and 0 <= ox < self._field_w:
                grid[oy][ox] = f"{DIM}{OBSTACLE_CHAR}{C.RESET}"

        # 食物
        if self._phase == "memorize":
            # 记忆阶段：显示数字
            for fx, fy, fn in self._foods:
                if 0 <= fy < self._field_h and 0 <= fx < self._field_w:
                    circled = self._get_circled(fn)
                    grid[fy][fx] = f"{C.BYELLOW}[{C.BWHITE}{circled}{C.BYELLOW}]{C.RESET}"
        else:
            # 游戏阶段：显示星号
            for fx, fy, fn in self._foods:
                if 0 <= fy < self._field_h and 0 <= fx < self._field_w:
                    if fn == self._next_food_num:
                        # 当前应该吃的食物：高亮
                        grid[fy][fx] = f"{C.BGREEN}{STAR_CHAR}{C.RESET}"
                    else:
                        grid[fy][fx] = f"{C.YELLOW}{STAR_CHAR}{C.RESET}"

        # 蛇身
        for i, (sx, sy) in enumerate(self._snake):
            if 0 <= sy < self._field_h and 0 <= sx < self._field_w:
                if i == len(self._snake) - 1:
                    # 蛇头
                    grid[sy][sx] = f"{C.BWHITE}{SNAKE_HEAD_CHAR}{C.RESET}"
                else:
                    # 蛇身
                    grid[sy][sx] = f"{C.CYAN}{SNAKE_BODY_CHAR}{C.RESET}"

        # 拼接行
        for y in range(self._field_h):
            row = "".join(grid[y])
            lines.append(f"  {C.RESET}│{row}{C.RESET}│")

        # 底部边框
        bot = f"└{'─' * self._field_w}┘"
        lines.append(f"  {bot}")

        return lines

    def render(self):
        lines = []

        # 状态栏
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        lines.append(center(f"{C.BGREEN}🐍 贪吃蛇记忆{C.RESET} — {C.BWHITE}第 {self._level} 关{C.RESET}  {DIM}({diff_name}){C.RESET}", self.WIDTH))
        lines.append("")

        if self._phase == "memorize":
            # 记忆阶段
            elapsed = self._mem_timer.get_elapsed()
            remaining = max(0, self._mem_time - elapsed)
            pct = max(0, (remaining / self._mem_time) * 100)

            lines.append(center(f"{C.BYELLOW}⏰ 记忆阶段！记住食物顺序！{C.RESET}", self.WIDTH))
            lines.append(center(f"  {progress_bar(pct, 30)}  剩余: {remaining:.1f}s", self.WIDTH))
            lines.append("")

            # 食物列表
            food_list = "  ".join(f"{C.BYELLOW}[{C.BWHITE}{self._get_circled(fn)}{C.BYELLOW}]{C.RESET}" for _, _, fn in sorted(self._foods, key=lambda f: f[2]))
            lines.append(center(f"需要吃: {food_list}", self.WIDTH))
            lines.append("")

            # 渲染场地
            field_lines = self._render_field()
            lines.extend(field_lines)

        else:
            # 游戏阶段
            next_food = self._get_circled(self._next_food_num)
            eaten = "  ".join(
                f"{C.BGREEN}{self._get_circled(i)}{C.RESET}"
                for i in range(1, self._next_food_num)
            )
            if not eaten:
                eaten = f"{DIM}无{C.RESET}"

            lines.append(center(f"需要吃: {C.BYELLOW}{next_food}{C.RESET}  "
                                f"已吃: {eaten}  "
                                f"得分: {C.BGREEN}{self.score}{C.RESET}", self.WIDTH))
            lines.append("")

            if self._message:
                lines.append(center(self._message, self.WIDTH))
                lines.append("")

            # 渲染场地
            field_lines = self._render_field()
            lines.extend(field_lines)

            lines.append("")
            lines.append(center(f"{DIM}WASD/方向键控制  [Q]退出 [H]帮助{C.RESET}", self.WIDTH))

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
                    # 如果在记忆阶段，重新开始记忆
                    if self._phase == "memorize":
                        self._mem_timer = GameTimer()
                        self._mem_timer.start()
                    continue
                if not self.handle_input(key):
                    break

            self.update()
            self.render()
            time.sleep(0.02)

        # 游戏结束画面
        self._render_final()
        print("\n  ", end="")
        self._input_manager.get_key()

    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 贪 吃 蛇 记 忆 "))
        lines.append("")

        if self._won or self._max_level > 0:
            lines.append(center(f"{C.BGREEN}🐍 游戏完成！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}最高关卡: {self._max_level}{C.RESET}", self.WIDTH))
        lines.append(center(f"总食物: {C.BGREEN}{self._total_foods_eaten}{C.RESET}  "
                            f"连续通关: {C.BYELLOW}{self._consecutive_levels}{C.RESET}", self.WIDTH))
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
        return (
            f"\n  {C.BOLD}{C.BGREEN}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  经典贪吃蛇 + 记忆顺序挑战！\n"
            f"  每关出现 N 个带编号的食物(N=关卡数)\n"
            f"  记住编号顺序，然后按 ①→②→③... 吃！\n"
            f"\n  {C.BGREEN}吃对顺序{C.RESET} → +{100} × 关卡数\n"
            f"  {C.BYELLOW}完成关卡{C.RESET} → +500 + {200} × 关卡数\n"
            f"  {C.BRED}吃错/撞墙/撞自己{C.RESET} → 游戏结束\n"
            f"\n  场地: {config['width']}×{config['height']}  "
            f"记忆: {config['mem_time']}秒  "
            f"速度: {config['speed']}s\n"
            f"  障碍物: {config['obstacles']}个\n"
            f"\n  操作: WASD/方向键  [Q]退出  [H]帮助\n"
        )
