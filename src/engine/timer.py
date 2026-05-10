"""游戏计时器"""

import time


class GameTimer:
    """游戏计时器，支持开始、暂停、恢复、停止"""

    def __init__(self):
        self._start_time: float | None = None
        self._elapsed: float = 0.0
        self._running: bool = False
        self._paused: bool = False

    def start(self):
        """开始计时"""
        self._start_time = time.perf_counter()
        self._elapsed = 0.0
        self._running = True
        self._paused = False

    def pause(self):
        """暂停计时"""
        if self._running and not self._paused:
            self._elapsed += time.perf_counter() - self._start_time
            self._paused = True
            self._start_time = None

    def resume(self):
        """恢复计时"""
        if self._running and self._paused:
            self._start_time = time.perf_counter()
            self._paused = False

    def stop(self):
        """停止计时"""
        if self._running and not self._paused:
            self._elapsed += time.perf_counter() - self._start_time
        self._running = False
        self._paused = False
        self._start_time = None

    def get_elapsed(self) -> float:
        """获取已消耗时间（秒）"""
        if self._running and not self._paused and self._start_time is not None:
            return self._elapsed + (time.perf_counter() - self._start_time)
        return self._elapsed

    def get_remaining(self, total: float) -> float:
        """获取剩余时间（秒）

        Args:
            total: 总时间

        Returns:
            剩余时间，如果已超时则返回 0
        """
        elapsed = self.get_elapsed()
        return max(0.0, total - elapsed)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def format_time(self) -> str:
        """格式化当前时间为 MM:SS 格式"""
        total_seconds = int(self.get_elapsed())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
