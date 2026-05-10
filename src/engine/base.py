"""游戏抽象基类"""

from abc import ABC, abstractmethod
from typing import Any


class BaseGame(ABC):
    """游戏抽象基类，所有游戏必须继承此类"""

    def __init__(self, difficulty: str, renderer: Any, input_manager: Any, score_manager: Any):
        """初始化游戏

        Args:
            difficulty: 难度级别 ("easy", "medium", "hard")
            renderer: Renderer 实例
            input_manager: InputManager 实例
            score_manager: ScoreManager 实例
        """
        self.name: str = "未命名游戏"
        self.difficulty: str = difficulty
        self.score: int = 0
        self.running: bool = False
        self._renderer = renderer
        self._input_manager = input_manager
        self._score_manager = score_manager

    @abstractmethod
    def setup(self):
        """游戏初始化设置（子类实现）"""
        ...

    @abstractmethod
    def game_loop(self):
        """游戏主循环（子类实现）"""
        ...

    @abstractmethod
    def handle_input(self, key: str) -> bool:
        """处理输入

        Args:
            key: 按键字符串

        Returns:
            True 继续游戏，False 退出游戏
        """
        ...

    @abstractmethod
    def update(self):
        """更新游戏状态（子类实现）"""
        ...

    @abstractmethod
    def render(self):
        """渲染游戏画面（子类实现）"""
        ...

    def get_score(self) -> int:
        """获取当前分数"""
        return self.score

    def save_score(self):
        """保存当前分数（如果是最高的则保存）"""
        if self._score_manager is not None:
            self._score_manager.set_high_score(
                self.name, self.difficulty, self.score
            )

    def show_help(self) -> str:
        """显示游戏帮助信息（子类可重写）"""
        return f"\n  {self.name} - {self.difficulty}难度\n  按 q 退出游戏\n"

    def cleanup(self):
        """清理资源"""
        self.running = False
        if self._renderer is not None:
            self._renderer.show_cursor()

    def run(self):
        """运行游戏"""
        try:
            self.running = True
            self._input_manager.init()
            self._renderer.hide_cursor()
            self.setup()
            self.game_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()
            self._input_manager.cleanup()
