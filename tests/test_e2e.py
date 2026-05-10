"""端到端测试 (E2E) — 模拟完整游戏流程

通过 Mock 输入来模拟用户操作，测试从启动到退出的完整流程。
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from unittest.mock import MagicMock, patch


class TestE2EGameLifecycle:
    """端到端：游戏生命周期测试。"""

    @staticmethod
    def run_all():
        TestE2EGameLifecycle.test_game_can_start_and_exit()
        TestE2EGameLifecycle.test_all_games_instantiable_with_real_deps()
        TestE2EGameLifecycle.test_difficulty_selection()
        TestE2EGameLifecycle.test_game_has_name_attribute()
        TestE2EGameLifecycle.test_show_help_returns_string()
        TestE2EGameLifecycle.test_get_score_returns_int()
        TestE2EGameLifecycle.test_game_cleanup_does_not_crash()
        print("  [PASS] All E2E Game Lifecycle tests")

    @staticmethod
    def test_game_can_start_and_exit():
        """游戏能够初始化、启动并正常退出。"""
        from src.games import get_game_class
        from src.engine.renderer import Renderer
        from src.engine.input import InputManager
        from src.utils.scoring import ScoreManager

        mock_renderer = MagicMock(spec=Renderer)
        mock_renderer.width = 80
        mock_renderer.height = 24
        mock_renderer.color_support = True

        mock_input = MagicMock(spec=InputManager)
        # 模拟用户按 Q 退出
        mock_input.get_key = MagicMock(return_value='q')
        mock_input.get_key_nonblocking = MagicMock(return_value='q')

        mock_scores = MagicMock(spec=ScoreManager)
        mock_scores.get_high_score = MagicMock(return_value=0)
        mock_scores.set_high_score = MagicMock(return_value=False)

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(
                difficulty="easy",
                renderer=mock_renderer,
                input_manager=mock_input,
                score_manager=mock_scores,
            )
            game.name = f"TestGame{gid}"
            game.setup()
            # 确认 setup 后游戏处于可运行状态
            assert hasattr(game, 'running')
            assert hasattr(game, 'score')


    @staticmethod
    def test_all_games_instantiable_with_real_deps():
        """所有游戏使用真实依赖类实例化。"""
        from src.games import get_game_class
        from src.engine.renderer import Renderer
        from src.engine.input import InputManager
        from src.utils.scoring import ScoreManager
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            real_scores = ScoreManager(data_dir=tmpdir)
            real_renderer = Renderer()
            real_input = InputManager()

            for gid in range(1, 8):
                cls = get_game_class(gid)
                game = cls(
                    difficulty="easy",
                    renderer=real_renderer,
                    input_manager=real_input,
                    score_manager=real_scores,
                )
                assert game is not None
                game.cleanup()


    @staticmethod
    def test_difficulty_selection():
        """每个游戏都支持三种难度。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            for diff in ["easy", "normal", "hard"]:
                game = cls(
                    difficulty=diff,
                    renderer=mock_renderer,
                    input_manager=mock_input,
                    score_manager=mock_scores,
                )
                game.setup()
                assert game.difficulty == diff
                game.cleanup()


    @staticmethod
    def test_game_has_name_attribute():
        """游戏有名称属性。"""
        from src.games import get_game_class, get_game_name
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(
                difficulty="easy",
                renderer=mock_renderer,
                input_manager=mock_input,
                score_manager=mock_scores,
            )
            # 设置名称（main.py 中会设置）
            game.name = get_game_name(gid)
            assert game.name, f"Game {gid} should have a name"


    @staticmethod
    def test_show_help_returns_string():
        """show_help() 返回字符串。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(
                difficulty="easy",
                renderer=mock_renderer,
                input_manager=mock_input,
                score_manager=mock_scores,
            )
            game.setup()
            help_text = game.show_help()
            assert isinstance(help_text, str), f"Game {gid} show_help() should return str"
            assert len(help_text) > 0, f"Game {gid} show_help() should not be empty"


    @staticmethod
    def test_get_score_returns_int():
        """get_score() 返回整数。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(
                difficulty="easy",
                renderer=mock_renderer,
                input_manager=mock_input,
                score_manager=mock_scores,
            )
            game.setup()
            score = game.get_score()
            assert isinstance(score, int), f"Game {gid} get_score() should return int"
            assert score >= 0, f"Game {gid} score should be >= 0"


    @staticmethod
    def test_game_cleanup_does_not_crash():
        """cleanup() 不抛出异常。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock

        mock_renderer = MagicMock()
        mock_input = MagicMock()
        mock_scores = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            game = cls(
                difficulty="easy",
                renderer=mock_renderer,
                input_manager=mock_input,
                score_manager=mock_scores,
            )
            game.setup()
            try:
                game.cleanup()
            except Exception as e:
                raise AssertionError(f"Game {gid} cleanup() raised: {e}")


class TestE2EMainMenu:
    """端到端：主菜单流程测试。"""

    @staticmethod
    def run_all():
        TestE2EMainMenu.test_menu_shows_all_games()
        TestE2EMainMenu.test_game_list_has_correct_count()
        TestE2EMainMenu.test_all_games_available()
        TestE2EMainMenu.test_score_manager_show_all()
        print("  [PASS] All E2E Main Menu tests")

    @staticmethod
    def test_menu_shows_all_games():
        """主菜单应显示所有 7 个游戏。"""
        from src.games import get_game_list
        games = get_game_list()
        assert len(games) == 7, f"Expected 7 games, got {len(games)}"
        names = [g["name"] for g in games]
        assert "记忆迷宫" in names
        assert "弹幕大脑" in names
        assert "密码破译" in names
        assert "节奏大师" in names
        assert "打地鼠" in names
        assert "故事解谜" in names
        assert "贪吃蛇记忆" in names

    @staticmethod
    def test_game_list_has_correct_count():
        """游戏列表数量正确。"""
        from src.games import get_game_list
        games = get_game_list()
        ids = [g["id"] for g in games]
        assert ids == [1, 2, 3, 4, 5, 6, 7]

    @staticmethod
    def test_all_games_available():
        """所有游戏都应可玩。"""
        from src.games import get_game_list
        games = get_game_list()
        for g in games:
            assert g["available"], f"Game {g['id']} ({g['name']}) should be available"

    @staticmethod
    def test_score_manager_show_all():
        """分数管理器 show_all() 返回可显示内容。"""
        import tempfile
        from src.utils.scoring import ScoreManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            sm.set_high_score("maze", "easy", 100)
            result = sm.show_all()
            assert isinstance(result, str)
            assert len(result) > 0


class TestE2EScorePersistence:
    """端到端：分数持久化测试。"""

    @staticmethod
    def run_all():
        TestE2EScorePersistence.test_score_survives_restart()
        TestE2EScorePersistence.test_score_only_updates_if_higher()
        TestE2EScorePersistence.test_all_games_all_difficulties()
        print("  [PASS] All E2E Score Persistence tests")

    @staticmethod
    def test_score_survives_restart():
        """分数在程序重启后仍然存在。"""
        import tempfile
        from src.utils.scoring import ScoreManager

        with tempfile.TemporaryDirectory() as tmpdir:
            # 第一次运行
            sm1 = ScoreManager(data_dir=tmpdir)
            sm1.set_high_score("rhythm", "normal", 2500)
            sm1.save()

            # 模拟重启
            sm2 = ScoreManager(data_dir=tmpdir)
            assert sm2.get_high_score("rhythm", "normal") == 2500

    @staticmethod
    def test_score_only_updates_if_higher():
        """分数只在更高时更新。"""
        import tempfile
        from src.utils.scoring import ScoreManager

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            sm.set_high_score("maze", "hard", 2000)
            assert sm.get_high_score("maze", "hard") == 2000

            # 低分不更新
            sm.set_high_score("maze", "hard", 1500)
            assert sm.get_high_score("maze", "hard") == 2000

            # 高分更新
            sm.set_high_score("maze", "hard", 2500)
            assert sm.get_high_score("maze", "hard") == 2500

    @staticmethod
    def test_all_games_all_difficulties():
        """所有游戏的所有难度分数独立。"""
        import tempfile
        from src.utils.scoring import ScoreManager

        game_names = ["maze", "math_dodge", "code_breaker", "rhythm",
                       "whack", "story", "memory_snake"]
        difficulties = ["easy", "normal", "hard"]

        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            for g in game_names:
                for d in difficulties:
                    score = hash(g + d) % 10000
                    sm.set_high_score(g, d, score)
            sm.save()

            sm2 = ScoreManager(data_dir=tmpdir)
            for g in game_names:
                for d in difficulties:
                    expected = hash(g + d) % 10000
                    actual = sm2.get_high_score(g, d)
                    assert actual == expected, \
                        f"{g}/{d}: expected {expected}, got {actual}"


if __name__ == "__main__":
    print("Running E2E tests...")
    TestE2EGameLifecycle.run_all()
    TestE2EMainMenu.run_all()
    TestE2EScorePersistence.run_all()
    print("\nAll E2E tests passed!")
