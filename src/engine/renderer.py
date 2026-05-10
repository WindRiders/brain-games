"""终端渲染器"""

import sys
import os
import time
import shutil


class Renderer:
    """终端渲染器，处理清屏、渲染、光标控制等"""

    def __init__(self):
        self._supports_color = self._check_color_support()
        self._terminal_width, self._terminal_height = self._get_terminal_size()

    @staticmethod
    def _check_color_support() -> bool:
        """检测终端是否支持颜色"""
        if os.environ.get("TERM") == "dumb":
            return False
        if os.environ.get("NO_COLOR"):
            return False
        if sys.platform == "win32":
            # Windows 10+ 支持 ANSI，检查版本
            try:
                import platform
                major = int(platform.release().split(".")[0])
                return major >= 10
            except Exception:
                return False
        return True

    @staticmethod
    def _get_terminal_size() -> tuple[int, int]:
        """获取终端尺寸"""
        try:
            cols, rows = shutil.get_terminal_size(fallback=(80, 24))
            return cols, rows
        except Exception:
            return 80, 24

    def clear(self):
        """清屏"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()

    def render(self, content: str):
        """清屏后输出内容"""
        self.clear()
        sys.stdout.write(content)
        sys.stdout.flush()

    def render_frame(self, lines: list[str]):
        """渲染一帧（字符串列表）"""
        self.clear()
        for line in lines:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def hide_cursor(self):
        """隐藏光标"""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def show_cursor(self):
        """显示光标"""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def shake_screen(self, times: int = 3):
        """屏幕震动效果"""
        self.hide_cursor()
        for _ in range(times):
            # 右移
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.write("  ")
            sys.stdout.flush()
            time.sleep(0.05)
            # 回到原位
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            time.sleep(0.05)
        self.show_cursor()

    def flash(self, color: str, duration: float = 0.2):
        """闪烁效果（用指定颜色填充屏幕）"""
        self.hide_cursor()
        sys.stdout.write("\033[2J\033[H")
        # 输出彩色背景覆盖
        lines = self._terminal_height
        cols = self._terminal_width
        for _ in range(lines):
            sys.stdout.write(f"{color}{' ' * cols}\033[0m\n")
        sys.stdout.flush()
        time.sleep(duration)
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        self.show_cursor()

    @property
    def supports_color(self) -> bool:
        return self._supports_color

    @property
    def terminal_width(self) -> int:
        return self._terminal_width

    @property
    def terminal_height(self) -> int:
        return self._terminal_height
