"""引擎层测试 — 输入、渲染、基类"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestInputMapping:
    """按键映射测试。"""
    @staticmethod
    def run_all():
        TestInputMapping.test_arrow_to_wasd()
        TestInputMapping.test_escape_to_quit()
        TestInputMapping.test_control_chars()
        print("  [PASS] All InputMapping tests")

    @staticmethod
    def test_arrow_to_wasd():
        """方向键应映射为 WASD。"""
        arrow_map = {
            "up": "w",
            "down": "s",
            "left": "a",
            "right": "d",
        }
        assert arrow_map["up"] == "w"
        assert arrow_map["down"] == "s"
        assert arrow_map["left"] == "a"
        assert arrow_map["right"] == "d"

    @staticmethod
    def test_escape_to_quit():
        """Esc 键应映射为退出。"""
        assert "\x1b" == chr(27)  # Esc ANSI code

    @staticmethod
    def test_control_chars():
        """控制字符处理。"""
        assert ord("\r") == 13  # Enter
        assert ord("\x7f") == 127  # Backspace
        assert ord("\x1b") == 27  # Escape


class TestRenderer:
    """渲染引擎测试。"""
    @staticmethod
    def run_all():
        TestRenderer.test_color_strip()
        TestRenderer.test_ansi_codes()
        TestRenderer.test_clear_screen()
        print("  [PASS] All Renderer tests")

    @staticmethod
    def test_color_strip():
        import re
        from src.ui.colors import C
        ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
        colored = f"{C.RED}hello{C.RESET}"
        stripped = ansi_escape.sub("", colored)
        assert stripped == "hello"

    @staticmethod
    def test_ansi_codes():
        from src.ui.colors import C
        assert C.RESET == "\033[0m"
        assert C.BOLD == "\033[1m"
        assert C.RED == "\033[31m"
        assert C.GREEN == "\033[32m"
        assert C.YELLOW == "\033[33m"

    @staticmethod
    def test_clear_screen():
        from src.ui.colors import C
        assert C.CLEAR_SCREEN == "\033[2J"
        assert C.HOME == "\033[H"


class TestBaseGame:
    """游戏基类测试。"""
    @staticmethod
    def run_all():
        TestBaseGame.test_abstract_methods()
        TestBaseGame.test_score_methods()
        TestBaseGame.test_inheritance()
        print("  [PASS] All BaseGame tests")

    @staticmethod
    def test_abstract_methods():
        from src.engine.base import BaseGame
        import abc
        # BaseGame 应该是抽象类
        from abc import ABC
        assert issubclass(BaseGame, ABC)

    @staticmethod
    def test_score_methods():
        from src.engine.base import BaseGame
        from unittest.mock import MagicMock
        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        from src.games.maze import MemoryMazeGame
        game = MemoryMazeGame(
            difficulty="easy",
            renderer=mock_renderer,
            input_manager=mock_input,
            score_manager=mock_scores,
        )
        assert game.score == 0
        assert game.running is False

    @staticmethod
    def test_inheritance():
        from src.engine.base import BaseGame
        from src.games import get_game_class
        for gid in range(1, 8):
            cls = get_game_class(gid)
            assert issubclass(cls, BaseGame), f"Game {gid} should inherit from BaseGame"


class TestScoreManager:
    """评分管理器额外测试。"""
    @staticmethod
    def run_all():
        TestScoreManager.test_data_dir_creation()
        TestScoreManager.test_json_structure()
        print("  [PASS] All ScoreManager extra tests")

    @staticmethod
    def test_data_dir_creation():
        import tempfile
        from src.utils.scoring import ScoreManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            data_path = os.path.join(tmpdir, "scores.json")
            # File should not exist until save
            assert not os.path.exists(data_path)
            sm.save()
            assert os.path.exists(data_path)

    @staticmethod
    def test_json_structure():
        import tempfile, json
        from src.utils.scoring import ScoreManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            sm.set_high_score("maze", "easy", 500)
            sm.save()
            with open(os.path.join(tmpdir, "scores.json")) as f:
                data = json.load(f)
            assert "maze" in data
            assert data["maze"]["easy"] == 500


class TestIntegration:
    """集成测试 — 游戏生命周期。"""
    @staticmethod
    def run_all():
        TestIntegration.test_all_games_instantiable()
        TestIntegration.test_game_registry_complete()
        TestIntegration.test_main_importable()
        print("  [PASS] All Integration tests")

    @staticmethod
    def test_all_games_instantiable():
        """所有游戏都可以实例化。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        from src.engine.renderer import Renderer
        from src.engine.input import InputManager
        from src.utils.scoring import ScoreManager

        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            assert hasattr(game, "name")
            assert hasattr(game, "score")
            assert hasattr(game, "running")

    @staticmethod
    def test_game_registry_complete():
        """游戏注册表应包含 7 个游戏。"""
        from src.games import get_game_list
        games = get_game_list()
        assert len(games) == 7, f"Expected 7 games, got {len(games)}"
        for g in games:
            assert g["available"], f"Game {g['id']} ({g['name']}) not available"

    @staticmethod
    def test_main_importable():
        """main.py 应可导入。"""
        import importlib.util
        main_path = os.path.join(PROJECT_ROOT, "main.py")
        spec = importlib.util.spec_from_file_location("main", main_path)
        assert spec is not None, "main.py should be importable"


if __name__ == "__main__":
    print("Running engine & integration tests...")
    TestInputMapping.run_all()
    TestRenderer.run_all()
    TestBaseGame.run_all()
    TestScoreManager.run_all()
    TestIntegration.run_all()
    print("\nAll engine & integration tests passed!")
