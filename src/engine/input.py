"""跨平台输入管理器"""

import sys
import os

# 方向键序列 (ANSI 转义)
ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"
ARROW_LEFT = "\x1b[D"
ARROW_RIGHT = "\x1b[C"


class InputManager:
    """跨平台终端输入管理器"""

    def __init__(self):
        self._platform = self._detect_platform()
        self._initialized = False
        # Linux/macOS 状态
        self._old_settings = None
        self._fd = None

    @staticmethod
    def _detect_platform() -> str:
        """检测运行平台"""
        if sys.platform == "win32":
            return "windows"
        return "posix"

    def init(self):
        """初始化输入管理器，设置终端原始模式"""
        if self._initialized:
            return

        if self._platform == "windows":
            # Windows: 使用 msvcrt
            import msvcrt
            self._msvcrt = msvcrt
            self._tty_mode = False
        else:
            # Linux/macOS: 检查是否真实 TTY
            self._fd = sys.stdin.fileno()
            if os.isatty(self._fd):
                # 真实终端：使用 termios/tty 原始模式
                import tty
                import termios
                self._tty = tty
                self._termios = termios
                self._old_settings = termios.tcgetattr(self._fd)
                tty.setraw(self._fd)
                self._tty_mode = True
            else:
                # 非 TTY 环境（管道、重定向、沙箱）：fallback 模式
                self._tty_mode = False

        self._initialized = True

    def _read_escape_sequence(self) -> str:
        """读取 ANSI 转义序列（方向键等）"""
        if self._platform == "windows":
            ch2 = self._msvcrt.getch()
            seq = ch2.decode("latin-1", errors="replace")
            if ch2 == b"\xe0" or ch2 == b"\x00":
                ch3 = self._msvcrt.getch()
                key_map = {
                    b"H": "up",
                    b"P": "down",
                    b"K": "left",
                    b"M": "right",
                }
                return key_map.get(ch3, seq)
            return seq
        else:
            # POSIX: 已经读取了 \x1b，继续读后面的
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                arrow_map = {"A": "up", "B": "down", "C": "right", "D": "left"}
                return arrow_map.get(ch3, ch3)
            return ch2

    def get_key(self) -> str:
        """阻塞获取按键

        Returns:
            按键字符串。Esc 返回 'q'，方向键返回 'up'/'down'/'left'/'right'
        """
        if not self._initialized:
            raise RuntimeError("InputManager not initialized. Call init() first.")

        if self._platform == "windows":
            ch = self._msvcrt.getch()
            if ch == b"\x1b":  # Esc
                return "q"
            if ch == b"\xe0" or ch == b"\x00":  # 扩展键前缀
                return self._read_escape_sequence()
            return ch.decode("utf-8", errors="replace")
        elif self._tty_mode:
            # TTY 原始模式：逐字符读取
            ch = sys.stdin.read(1)
            if ch == "\x1b":  # Esc 前缀
                result = self._read_escape_sequence()
                if result == "\x1b":
                    return "q"
                return result
            return ch
        else:
            # 非 TTY fallback：行缓冲模式，读整行
            line = sys.stdin.readline()
            if not line:
                return "q"  # EOF
            return line.rstrip("\r\n")

    def get_key_nonblocking(self) -> str | None:
        """非阻塞获取按键

        Returns:
            按键字符串，如果没有按键则返回 None
        """
        if not self._initialized:
            raise RuntimeError("InputManager not initialized. Call init() first.")

        if self._platform == "windows":
            if not self._msvcrt.kbhit():
                return None
            ch = self._msvcrt.getch()
            if ch == b"\x1b":
                return "q"
            if ch == b"\xe0" or ch == b"\x00":
                return self._read_escape_sequence()
            return ch.decode("utf-8", errors="replace")
        elif self._tty_mode:
            import select
            if not select.select([sys.stdin], [], [], 0)[0]:
                return None
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # 尝试非阻塞读取后续字节
                import select
                if select.select([sys.stdin], [], [], 0.01)[0]:
                    result = self._read_escape_sequence()
                    if result == "\x1b":
                        return "q"
                    return result
                return "q"  # 单独的 Esc
            return ch
        else:
            # 非 TTY fallback：不阻塞，有数据即读整行
            import select
            if not select.select([sys.stdin], [], [], 0)[0]:
                return None
            line = sys.stdin.readline()
            if not line:
                return "q"  # EOF
            return line.rstrip("\r\n")

    def cleanup(self):
        """恢复终端设置"""
        if not self._initialized:
            return

        if self._platform == "posix" and self._tty_mode and self._old_settings is not None:
            self._termios.tcsetattr(self._fd, self._termios.TCSADRAIN, self._old_settings)

        self._initialized = False

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
