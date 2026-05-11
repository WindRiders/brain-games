#!/usr/bin/env python3
"""游戏生命周期测试 — 验证游戏在反复创建/销毁/切换中的稳定性

测试场景:
- 重复 setup/cleanup 不泄漏资源
- 游戏间切换不互相影响
- 中断后恢复不崩溃
- 异常输入流不崩溃
- 分数文件损坏后恢复
"""
import sys
import os
import tempfile
import json
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.games import get_game_class
from src.engine.renderer import Renderer
from src.engine.input import InputManager
from src.utils.scoring import ScoreManager


def _env():
    """创建测试环境"""
    tmpdir = tempfile.mkdtemp()
    renderer = Renderer()
    renderer.render_frame = MagicMock()
    renderer.clear = MagicMock()
    renderer.show_cursor = MagicMock()
    renderer.hide_cursor = MagicMock()
    renderer.shake_screen = MagicMock()
    renderer.flash = MagicMock()
    input_mgr = InputManager()
    score_mgr = ScoreManager(data_dir=tmpdir)
    return renderer, input_mgr, score_mgr, tmpdir


def _make_game(gid, difficulty="easy"):
    """创建并初始化游戏"""
    cls = get_game_class(gid)
    r, i, s, d = _env()
    g = cls(difficulty=difficulty, renderer=r, input_manager=i, score_manager=s)
    g.name = g.name or f"Game{gid}"
    g.setup()
    return g, r, i, s, d


# ── LC-01: 重复 setup/cleanup ──
class TestRepeatSetupCleanup:
    @staticmethod
    def run_all():
        for gid in range(1, 8):
            TestRepeatSetupCleanup._test_game(gid)
        print("  [PASS] All RepeatSetupCleanup tests")

    @staticmethod
    def _test_game(gid: int):
        """重复 setup/cleanup 3 次"""
        cls = get_game_class(gid)
        r, i, s, d = _env()

        for attempt in range(3):
            g = cls(difficulty="easy", renderer=r, input_manager=i, score_manager=s)
            g.name = g.name or f"Game{gid}"
            g.setup()
            # Send some inputs
            g.handle_input("q")
            g.cleanup()

        # Verify no resource leak (cleanup called without error)


# ── LC-02: 游戏间切换 ──
class TestGameSwitching:
    @staticmethod
    def run_all():
        TestGameSwitching.test_sequential_games()
        TestGameSwitching.test_random_order()
        print("  [PASS] All GameSwitching tests")

    @staticmethod
    def test_sequential_games():
        """依次玩 G1→G2→...→G7"""
        for gid in range(1, 8):
            g, *_ = _make_game(gid)
            g.handle_input("q")
            g.cleanup()

    @staticmethod
    def test_random_order():
        """随机顺序切换"""
        order = [3, 1, 7, 2, 5, 4, 6]
        for gid in order:
            g, *_ = _make_game(gid)
            g.handle_input("q")
            g.cleanup()


# ── LC-03: 中断恢复 ──
class TestInterruptRecovery:
    @staticmethod
    def run_all():
        TestInterruptRecovery.test_q_then_setup()
        TestInterruptRecovery.test_h_then_setup()
        TestInterruptRecovery.test_multiple_interrupts()
        print("  [PASS] All InterruptRecovery tests")

    @staticmethod
    def test_q_then_setup():
        """输入 q 后重新 setup"""
        g, *_ = _make_game(1)
        g.handle_input("q")
        g.cleanup()
        # Create new game
        g2, *_ = _make_game(1)
        g2.handle_input("q")
        g2.cleanup()

    @staticmethod
    def test_h_then_setup():
        """输入 h (help) 后重新 setup"""
        g, *_ = _make_game(3)
        g.handle_input("h")
        g.handle_input("q")
        g.cleanup()
        g2, *_ = _make_game(3)
        g2.handle_input("q")
        g2.cleanup()

    @staticmethod
    def test_multiple_interrupts():
        """多次输入 q"""
        g, *_ = _make_game(5)
        g.handle_input("q")
        g.handle_input("q")  # Should not crash
        g.handle_input("q")
        g.cleanup()


# ── LC-04: 异常输入流 ──
class TestAbnormalInputFlow:
    @staticmethod
    def run_all():
        TestAbnormalInputFlow.test_random_chars()
        TestAbnormalInputFlow.test_special_chars()
        TestAbnormalInputFlow.test_none_inputs()
        TestAbnormalInputFlow.test_mixed_inputs()
        print("  [PASS] All AbnormalInputFlow tests")

    @staticmethod
    def test_random_chars():
        """随机字符输入"""
        g, *_ = _make_game(1)
        import string
        for ch in string.ascii_letters + string.digits + string.punctuation:
            g.handle_input(ch)
        g.handle_input("q")
        g.cleanup()

    @staticmethod
    def test_special_chars():
        """特殊字符输入"""
        g, *_ = _make_game(3)
        special = ["\x00", "\x01", "\x03", "\x1b", "\x7f", "\x08", "\n", "\r", "\t"]
        for ch in special:
            g.handle_input(ch)
        g.handle_input("q")
        g.cleanup()

    @staticmethod
    def test_none_inputs():
        """None 输入"""
        g, *_ = _make_game(7)
        for _ in range(10):
            g.handle_input(None)
        g.handle_input("q")
        g.cleanup()

    @staticmethod
    def test_mixed_inputs():
        """混合输入"""
        g, *_ = _make_game(6)
        inputs = ["q", "h", "q", "xyz", "q", ""]
        for inp in inputs:
            g._process_command(inp)
        g.cleanup()


# ── LC-05: 分数文件损坏恢复 ──
class TestScoreFileRecovery:
    @staticmethod
    def run_all():
        TestScoreFileRecovery.test_empty_file()
        TestScoreFileRecovery.test_invalid_json()
        TestScoreFileRecovery.test_corrupted_file()
        print("  [PASS] All ScoreFileRecovery tests")

    @staticmethod
    def test_empty_file():
        """空分数文件"""
        tmpdir = tempfile.mkdtemp()
        score_path = os.path.join(tmpdir, "scores.json")
        with open(score_path, "w") as f:
            f.write("")  # Empty file

        sm = ScoreManager(data_dir=tmpdir)
        # Should handle gracefully
        val = sm.get_high_score("Test", "easy")
        assert isinstance(val, int)

    @staticmethod
    def test_invalid_json():
        """非法 JSON"""
        tmpdir = tempfile.mkdtemp()
        score_path = os.path.join(tmpdir, "scores.json")
        with open(score_path, "w") as f:
            f.write("{invalid json!!!")

        sm = ScoreManager(data_dir=tmpdir)
        # Should handle gracefully
        val = sm.get_high_score("Test", "easy")
        assert isinstance(val, int)

    @staticmethod
    def test_corrupted_file():
        """损坏的分数文件"""
        tmpdir = tempfile.mkdtemp()
        score_path = os.path.join(tmpdir, "scores.json")
        with open(score_path, "w") as f:
            f.write("null")  # Valid JSON but wrong type

        sm = ScoreManager(data_dir=tmpdir)
        # Should handle gracefully
        val = sm.get_high_score("Test", "easy")
        assert isinstance(val, int)

        # After recovery, should be able to write
        sm.set_high_score("Test", "easy", 100)
        assert sm.get_high_score("Test", "easy") == 100


if __name__ == "__main__":
    print("Running Game Lifecycle tests...")
    TestRepeatSetupCleanup.run_all()
    TestGameSwitching.run_all()
    TestInterruptRecovery.run_all()
    TestAbnormalInputFlow.run_all()
    TestScoreFileRecovery.run_all()
    print("\nAll Game Lifecycle tests passed!")
