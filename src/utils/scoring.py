"""分数管理器"""

import json
import os
from pathlib import Path


class ScoreManager:
    """管理游戏分数，存储在 JSON 文件中"""

    def __init__(self, data_dir: str | None = None):
        if data_dir is None:
            data_dir = str(Path.home() / ".brain_games")
        self._data_dir = data_dir
        self._scores_file = os.path.join(data_dir, "scores.json")
        self._data: dict[str, dict[str, int]] = {}
        self.load()

    def _ensure_dir(self):
        """确保数据目录存在"""
        os.makedirs(self._data_dir, exist_ok=True)

    def load(self):
        """从文件加载分数数据"""
        try:
            if os.path.exists(self._scores_file):
                with open(self._scores_file, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            else:
                self._data = {}
        except (json.JSONDecodeError, IOError):
            self._data = {}

    def save(self):
        """保存分数数据到文件"""
        self._ensure_dir()
        with open(self._scores_file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def get_high_score(self, game_name: str, difficulty: str) -> int:
        """获取最高分

        Args:
            game_name: 游戏名称
            difficulty: 难度

        Returns:
            最高分，不存在则返回 0
        """
        game_data = self._data.get(game_name, {})
        return game_data.get(difficulty, 0)

    def set_high_score(self, game_name: str, difficulty: str, score: int) -> bool:
        """设置最高分（仅当新分数更高时更新）

        Args:
            game_name: 游戏名称
            difficulty: 难度
            score: 新分数

        Returns:
            如果更新了最高分返回 True，否则返回 False
        """
        current = self.get_high_score(game_name, difficulty)
        if score > current:
            if game_name not in self._data:
                self._data[game_name] = {}
            self._data[game_name][difficulty] = score
            self.save()
            return True
        return False

    def show_all(self) -> str:
        """格式化显示所有分数

        Returns:
            格式化的表格字符串
        """
        if not self._data:
            return "\n  暂无分数记录\n"

        lines = []
        # 表头
        header = f"{'游戏':<15} {'难度':<10} {'最高分':>8}"
        lines.append(header)
        lines.append("─" * 35)

        for game_name in sorted(self._data.keys()):
            game_data = self._data[game_name]
            for difficulty in sorted(game_data.keys()):
                score = game_data[difficulty]
                lines.append(f"{game_name:<15} {difficulty:<10} {score:>8}")

        return "\n" + "\n".join(lines) + "\n"

    def reset(self):
        """重置所有分数"""
        self._data = {}
        self.save()
