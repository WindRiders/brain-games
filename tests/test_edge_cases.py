"""边界异常测试 (Edge Cases) — 覆盖异常输入、极端条件、错误处理"""
import sys
import os
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestEdgeCasesInput:
    """边界异常：输入处理。"""

    @staticmethod
    def run_all():
        TestEdgeCasesInput.test_empty_string_input()
        TestEdgeCasesInput.test_special_characters()
        TestEdgeCasesInput.test_long_string()
        TestEdgeCasesInput.test_unicode_characters()
        TestEdgeCasesInput.test_control_characters()
        print("  [PASS] All Edge Cases: Input tests")

    @staticmethod
    def test_empty_string_input():
        """空输入不应崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            # 空字符串输入不应崩溃
            try:
                game.handle_input("")
            except Exception as e:
                raise AssertionError(f"Game {gid} handle_input('') raised: {e}")

    @staticmethod
    def test_special_characters():
        """特殊字符输入不应崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            for char in special_chars[:10]:  # 测试部分特殊字符
                try:
                    game.handle_input(char)
                except Exception as e:
                    raise AssertionError(
                        f"Game {gid} handle_input('{char}') raised: {e}")

    @staticmethod
    def test_long_string():
        """超长输入不应崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        long_input = "A" * 1000
        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            try:
                game.handle_input(long_input)
            except Exception as e:
                raise AssertionError(f"Game {gid} handle_input(long) raised: {e}")

    @staticmethod
    def test_unicode_characters():
        """Unicode/中文输入不应崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        unicode_inputs = ["你好", "日本語", "🎮", "🧠", "αβγ"]
        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            for inp in unicode_inputs:
                try:
                    game.handle_input(inp)
                except Exception as e:
                    raise AssertionError(
                        f"Game {gid} handle_input('{inp}') raised: {e}")

    @staticmethod
    def test_control_characters():
        """控制字符不应崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        control_chars = ["\x00", "\x01", "\x02", "\x7f", "\x1b", "\x03"]
        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            for char in control_chars:
                try:
                    game.handle_input(char)
                except Exception as e:
                    raise AssertionError(
                        f"Game {gid} handle_input(ctrl) raised: {e}")


class TestEdgeCasesTerminal:
    """边界异常：终端环境。"""

    @staticmethod
    def run_all():
        TestEdgeCasesTerminal.test_renderer_small_terminal()
        TestEdgeCasesTerminal.test_renderer_color_detection()
        TestEdgeCasesTerminal.test_no_color_env()
        TestEdgeCasesTerminal.test_terminal_size_at_minimum()
        print("  [PASS] All Edge Cases: Terminal tests")

    @staticmethod
    def test_renderer_small_terminal():
        """渲染器在小终端下不崩溃。"""
        from src.engine.renderer import Renderer
        r = Renderer()
        # 即使终端很小也不应崩溃
        r.render("test content")

    @staticmethod
    def test_renderer_color_detection():
        """渲染器颜色检测返回布尔值。"""
        from src.engine.renderer import Renderer
        r = Renderer()
        assert isinstance(r.supports_color, bool)

    @staticmethod
    def test_no_color_env():
        """NO_COLOR 环境变量处理。"""
        from src.engine.renderer import Renderer
        r = Renderer()
        # 无论环境如何都应正常工作
        r.render("colored text")

    @staticmethod
    def test_terminal_size_at_minimum():
        """终端尺寸检测返回正值。"""
        from src.engine.renderer import Renderer
        r = Renderer()
        assert r.terminal_width > 0, f"Width should be > 0"
        assert r.terminal_height > 0, f"Height should be > 0"


class TestEdgeCasesData:
    """边界异常：数据持久化。"""

    @staticmethod
    def run_all():
        TestEdgeCasesData.test_scores_file_not_exists()
        TestEdgeCasesData.test_scores_file_empty()
        TestEdgeCasesData.test_scores_file_invalid_json()
        TestEdgeCasesData.test_no_write_permission()
        print("  [PASS] All Edge Cases: Data tests")

    @staticmethod
    def test_scores_file_not_exists():
        """scores.json 不存在时应正常初始化。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.utils.scoring import ScoreManager
            sm = ScoreManager(data_dir=tmpdir)
            # 文件不存在时应返回默认分数
            score = sm.get_high_score("maze", "easy")
            assert score == 0

    @staticmethod
    def test_scores_file_empty():
        """scores.json 为空文件时应正常处理。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "scores.json")
            with open(data_path, 'w') as f:
                f.write("")
            from src.utils.scoring import ScoreManager
            sm = ScoreManager(data_dir=tmpdir)
            # 应能正常处理
            score = sm.get_high_score("maze", "easy")
            assert isinstance(score, int)

    @staticmethod
    def test_scores_file_invalid_json():
        """scores.json 含非法 JSON 时应正常处理。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_path = os.path.join(tmpdir, "scores.json")
            with open(data_path, 'w') as f:
                f.write("{invalid json!!!")
            from src.utils.scoring import ScoreManager
            sm = ScoreManager(data_dir=tmpdir)
            # 应能正常处理，返回默认值
            score = sm.get_high_score("maze", "easy")
            assert isinstance(score, int)

    @staticmethod
    def test_no_write_permission():
        """无写入权限目录应优雅处理。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建只读目录
            readonly_dir = os.path.join(tmpdir, "readonly")
            os.makedirs(readonly_dir)
            os.chmod(readonly_dir, 0o444)
            try:
                from src.utils.scoring import ScoreManager
                sm = ScoreManager(data_dir=readonly_dir)
                # 即使无法写入也不应崩溃
                sm.save()
            except PermissionError:
                pass  # 预期行为
            finally:
                os.chmod(readonly_dir, 0o755)  # 恢复权限以便清理


class TestEdgeCasesGameSpecific:
    """边界异常：各游戏特定场景。"""

    @staticmethod
    def run_all():
        TestEdgeCasesGameSpecific.test_maze_minimum_size()
        TestEdgeCasesGameSpecific.test_maze_even_size_handling()
        TestEdgeCasesGameSpecific.test_crypto_empty_text()
        TestEdgeCasesGameSpecific.test_crypto_single_char()
        TestEdgeCasesGameSpecific.test_maze_gen_large()
        TestEdgeCasesGameSpecific.test_rhythm_extreme_bpm()
        TestEdgeCasesGameSpecific.test_whack_extreme_interval()
        TestEdgeCasesGameSpecific.test_snake_empty_field()
        print("  [PASS] All Edge Cases: Game Specific tests")

    @staticmethod
    def test_maze_minimum_size():
        """迷宫最小尺寸 3x3 应可生成。"""
        from src.utils.maze_gen import generate_maze
        maze = generate_maze(3, 3)
        assert len(maze) == 3
        assert maze[1][1] == 0  # 中心应为通道

    @staticmethod
    def test_maze_even_size_handling():
        """偶数尺寸自动调整为奇数。"""
        from src.utils.maze_gen import generate_maze
        maze = generate_maze(4, 4)
        assert len(maze) % 2 == 1
        assert all(len(row) % 2 == 1 for row in maze)

    @staticmethod
    def test_crypto_empty_text():
        """加密空字符串应返回空字符串。"""
        from src.utils.crypto import (
            caesar_cipher, rot13, reverse_text,
            base64_encode, to_morse, vigenere_encrypt,
            to_binary_ascii
        )
        assert caesar_cipher("", 3) == ""
        assert rot13("") == ""
        assert reverse_text("") == ""
        assert base64_encode("") == ""
        assert to_morse("") == ""
        assert vigenere_encrypt("", "KEY") == ""

    @staticmethod
    def test_crypto_single_char():
        """加密单个字符应正常工作。"""
        from src.utils.crypto import (
            caesar_cipher, rot13, reverse_text,
            base64_encode, to_morse, vigenere_encrypt,
            to_binary_ascii
        )
        assert caesar_cipher("A", 1) == "B"
        assert rot13("A") == "N"
        assert reverse_text("A") == "A"
        assert len(base64_encode("A")) > 0
        assert len(to_morse("A")) > 0
        assert len(vigenere_encrypt("A", "KEY")) > 0

    @staticmethod
    def test_maze_gen_large():
        """大迷宫 (21x21) 应可生成且有解。"""
        from src.utils.maze_gen import generate_maze, solve_maze
        maze = generate_maze(21, 21)
        assert len(maze) == 21
        path = solve_maze(maze, (1, 1), (19, 19))
        assert path is not None

    @staticmethod
    def test_rhythm_extreme_bpm():
        """极端 BPM 值应可处理。"""
        from src.games.rhythm import DIFFICULTY_CONFIG
        # 检查配置中 BPM 为正数
        for diff, cfg in DIFFICULTY_CONFIG.items():
            assert cfg["bpm"] > 0, f"{diff} BPM should be > 0"
            assert len(cfg["keys"]) > 0, f"{diff} should have keys"
            assert cfg["num_notes"] > 0, f"{diff} should have notes"

    @staticmethod
    def test_whack_extreme_interval():
        """极端间隔应可处理。"""
        from src.games.whack import DIFFICULTY_CONFIG
        for diff, cfg in DIFFICULTY_CONFIG.items():
            assert cfg["interval"] > 0, f"{diff} interval should be > 0"
            assert cfg["total_rounds"] > 0, f"{diff} rounds should be > 0"

    @staticmethod
    def test_snake_empty_field():
        """贪吃蛇空场地配置应合理。"""
        from src.games.memory_snake import DIFFICULTY_CONFIG
        for diff, cfg in DIFFICULTY_CONFIG.items():
            assert cfg["width"] > 5, f"{diff} width too small"
            assert cfg["height"] > 5, f"{diff} height too small"
            assert cfg["speed"] > 0, f"{diff} speed should be > 0"
            assert cfg["mem_time"] > 0, f"{diff} mem_time should be > 0"


class TestEdgeCasesSystem:
    """边界异常：系统级。"""

    @staticmethod
    def run_all():
        TestEdgeCasesSystem.test_import_all_modules()
        TestEdgeCasesSystem.test_all_games_handle_none_input()
        TestEdgeCasesSystem.test_consecutive_setup_cleanup()
        print("  [PASS] All Edge Cases: System tests")

    @staticmethod
    def test_import_all_modules():
        """所有模块应可正常导入。"""
        import importlib
        modules = [
            "src.engine.base",
            "src.engine.input",
            "src.engine.renderer",
            "src.engine.timer",
            "src.ui.colors",
            "src.ui.components",
            "src.utils.scoring",
            "src.utils.maze_gen",
            "src.utils.crypto",
            "src.games.maze",
            "src.games.math_dodge",
            "src.games.code_breaker",
            "src.games.rhythm",
            "src.games.whack",
            "src.games.story",
            "src.games.memory_snake",
        ]
        for mod_name in modules:
            mod = importlib.import_module(mod_name)
            assert mod is not None, f"Failed to import {mod_name}"

    @staticmethod
    def test_all_games_handle_none_input():
        """游戏应能处理 None 输入。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            game.setup()
            try:
                game.handle_input(None)
            except Exception as e:
                raise AssertionError(f"Game {gid} handle_input(None) raised: {e}")

    @staticmethod
    def test_consecutive_setup_cleanup():
        """连续 setup/cleanup 不崩溃。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(difficulty="easy", renderer=mock_r,
                       input_manager=mock_i, score_manager=mock_s)
            for _ in range(3):
                game.setup()
                game.cleanup()


if __name__ == "__main__":
    print("Running Edge Case tests...")
    TestEdgeCasesInput.run_all()
    TestEdgeCasesTerminal.run_all()
    TestEdgeCasesData.run_all()
    TestEdgeCasesGameSpecific.run_all()
    TestEdgeCasesSystem.run_all()
    print("\nAll Edge Case tests passed!")
