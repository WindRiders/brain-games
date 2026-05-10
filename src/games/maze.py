"""G1 记忆迷宫游戏"""

import time
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.engine.timer import GameTimer
from src.ui import colors as C
from src.ui.components import box, progress_bar, center, header, divider
from src.utils.maze_gen import generate_maze, solve_maze
from src.utils.scoring import ScoreManager


# 自定义颜色（colors.py 中没有的）
DIM = "\033[2m"  # 暗色/灰色
GRAY = "\033[90m"  # 亮黑/灰色

# 难度配置
DIFFICULTY_CONFIG = {
    "easy": {"width": 5, "height": 5, "mem_time": 15},
    "normal": {"width": 8, "height": 8, "mem_time": 10},
    "hard": {"width": 12, "height": 12, "mem_time": 5},
}


class MemoryMazeGame(BaseGame):
    """记忆迷宫游戏"""

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "记忆迷宫"
        self.maze = []
        self.maze_h = 0
        self.maze_w = 0
        self.player_y = 1
        self.player_x = 1
        self.end_y = 0
        self.end_x = 0
        self.visited = set()
        self.wall_hits = 0
        self._phase = "memorize"  # "memorize" or "walk"
        self._game_over = False
        self._won = False
        self._mem_time = 0
        self._mem_timer = GameTimer()
        self._walk_timer = GameTimer()

    def setup(self):
        config = DIFFICULTY_CONFIG.get(self.difficulty, DIFFICULTY_CONFIG["easy"])
        self.maze = generate_maze(config["width"], config["height"])
        self.maze_h = len(self.maze)
        self.maze_w = len(self.maze[0])
        self.player_y = 1
        self.player_x = 1
        self.end_y = self.maze_h - 2
        self.end_x = self.maze_w - 2
        self.visited = set()
        self.visited.add((1, 1))
        self.wall_hits = 0
        self.score = 1000
        self._phase = "memorize"
        self._game_over = False
        self._won = False
        self._mem_time = config["mem_time"]
        self._mem_timer.start()

    def handle_input(self, key):
        if key is None:
            return True

        if key == "q":
            return False

        if key == "h":
            return True

        if self._phase == "memorize":
            # 记忆阶段不处理移动，只响应退出
            return True

        if self._phase == "walk":
            if key in ("w", "a", "s", "d"):
                dy, dx = 0, 0
                if key == "w":
                    dy = -1
                elif key == "s":
                    dy = 1
                elif key == "a":
                    dx = -1
                elif key == "d":
                    dx = 1

                new_y = self.player_y + dy
                new_x = self.player_x + dx

                if self.maze[new_y][new_x] == 1:
                    # 撞墙
                    self.wall_hits += 1
                    self.score = max(0, self.score - 100)
                    self._renderer.shake_screen(times=2)
                else:
                    self.player_y = new_y
                    self.player_x = new_x
                    self.visited.add((new_y, new_x))

                    # 检查是否到达终点
                    if (self.player_y, self.player_x) == (self.end_y, self.end_x):
                        self._game_over = True
                        self._won = True
                        remaining = self._walk_timer.get_elapsed()
                        self.score = max(0, 1000 - self.wall_hits * 100 + int(remaining) * 50)

            return True

        return True

    def update(self):
        if self._game_over:
            return

        if self._phase == "memorize":
            remaining = self._mem_timer.get_remaining(self._mem_time)
            if remaining <= 0:
                self._phase = "walk"
                self.player_y = 1
                self.player_x = 1
                self.visited = set()
                self.visited.add((1, 1))
                self._walk_timer.start()

    def render(self):
        lines = []
        lines.append("")
        lines.append(header(" 记 忆 迷 宫 "))
        lines.append("")

        # 渲染迷宫
        lines.append(self._render_maze())
        lines.append("")

        # 底部信息
        if self._phase == "memorize":
            remaining = self._mem_timer.get_remaining(self._mem_time)
            pct = (remaining / self._mem_time) * 100 if self._mem_time > 0 else 0
            lines.append(f"  记忆时间: {progress_bar(pct, width=20)}")
            lines.append(f"  剩余 {int(remaining)} 秒 — 记住迷宫布局！")
        elif self._phase == "walk":
            elapsed = self._walk_timer.get_elapsed()
            lines.append(
                f"  {C.BWHITE}@{C.RESET} = 你  "
                f"{C.BMAGENTA}*{C.RESET} = 路径  "
                f"得分: {C.BGREEN}{self.score}{C.RESET}  "
                f"撞墙: {C.RED}{self.wall_hits}{C.RESET}  "
                f"用时: {elapsed:.1f}s"
            )
            lines.append(f"  WASD/方向键移动  Q退出  H帮助")
        else:
            lines.append(f"  得分: {C.BGREEN}{self.score}{C.RESET}  撞墙: {C.RED}{self.wall_hits}{C.RESET}")
            if self._won:
                lines.append(f"  {C.BGREEN}🎉 恭喜通过迷宫！{C.RESET}")
            else:
                lines.append(f"  {C.RED}游戏结束{C.RESET}")
            lines.append("")
            high = self._score_manager.get_high_score(self.name, self.difficulty)
            new_high = self._score_manager.set_high_score(self.name, self.difficulty, self.score)
            if new_high:
                lines.append(f"  {C.BYELLOW}🏆 新纪录！{C.RESET}")
            else:
                lines.append(f"  历史最高: {C.BYELLOW}{high}{C.RESET}")

        lines.append("")
        self._renderer.render_frame(lines)

    def _render_maze(self):
        lines = []
        border_width = self.maze_w * 2 + 1

        # 顶部边框
        lines.append(f"  {C.DIM}┌{'─' * border_width}┐{C.RESET}")

        for y in range(self.maze_h):
            row_str = ""
            for x in range(self.maze_w):
                cell = self._render_cell(y, x)
                row_str += cell
                if x < self.maze_w - 1:
                    row_str += " "
            lines.append(f"  {C.DIM}│{C.RESET}{row_str}{C.DIM}│{C.RESET}")

        # 底部边框
        lines.append(f"  {C.DIM}└{'─' * border_width}┘{C.RESET}")

        return "\n".join(lines)

    def _render_cell(self, y, x):
        is_wall = self.maze[y][x] == 1
        is_player = (y, x) == (self.player_y, self.player_x)
        is_visited = (y, x) in self.visited
        is_start = (y, x) == (1, 1)
        is_end = (y, x) == (self.end_y, self.end_x)

        # 行走阶段
        if self._phase == "walk":
            if is_player:
                return f"{C.BWHITE}@{C.RESET}"
            elif is_visited and not is_end:
                return f"{C.BMAGENTA}*{C.RESET}"
            elif is_end:
                return f"{C.BYELLOW}E{C.RESET}"
            elif is_wall:
                return f"{GRAY}█{C.RESET}"
            else:
                return f"·"

        # 记忆阶段
        if self._phase == "memorize":
            if is_start:
                return f"{C.BGREEN}S{C.RESET}"
            elif is_end:
                return f"{C.BYELLOW}E{C.RESET}"
            elif is_wall:
                return f"{GRAY}█{C.RESET}"
            else:
                return f"·"

        return f"·"

    def game_loop(self):
        """游戏主循环"""
        # 记忆阶段
        while self._phase == "memorize" and self._game_over is False:
            key = self._input_manager.get_key_nonblocking()

            if key == "q":
                return
            elif key == "h":
                help_text = self.show_help()
                self._renderer.clear()
                print(help_text)
                print("\n  按任意键继续...")
                self._input_manager.get_key()
                self._mem_timer.pause()
                continue
            elif key is not None:
                self._mem_timer.pause()
                time.sleep(0.1)
                self._mem_timer.resume()

            self.update()
            self.render()
            time.sleep(0.05)

        # 行走阶段
        while self._phase == "walk" and not self._game_over:
            key = self._input_manager.get_key_nonblocking()

            if not self.handle_input(key):
                self._game_over = True
                break

            self.update()
            self.render()
            time.sleep(0.05)

        # 游戏结束
        self.render()
        print("\n  按任意键返回主菜单...")
        self._input_manager.get_key()
