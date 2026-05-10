"""评分系统测试"""
import sys
import os
import json
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.scoring import ScoreManager


def test_save_and_load():
    """分数保存和加载。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        sm.save()

        sm2 = ScoreManager(data_dir=tmpdir)
        assert sm2.get_high_score("maze", "easy") == 500
    print("  [PASS] test_save_and_load")


def test_high_score_update():
    """新纪录更新。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        result = sm.set_high_score("maze", "easy", 800)
        assert result is True, "新纪录应返回True"
        assert sm.get_high_score("maze", "easy") == 800
    print("  [PASS] test_high_score_update")


def test_no_update_if_lower():
    """低于纪录不更新。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        result = sm.set_high_score("maze", "easy", 300)
        assert result is False, "低于纪录应返回False"
        assert sm.get_high_score("maze", "easy") == 500
    print("  [PASS] test_no_update_if_lower")


def test_reset():
    """重置分数。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        sm.set_high_score("math", "normal", 300)
        sm.reset()
        assert sm.get_high_score("maze", "easy") == 0
        assert sm.get_high_score("math", "normal") == 0
    print("  [PASS] test_reset")


def test_default_score_is_zero():
    """默认分数为0。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        assert sm.get_high_score("nonexistent", "easy") == 0
    print("  [PASS] test_default_score_is_zero")


def test_different_games_independent():
    """不同游戏分数独立。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        sm.set_high_score("math", "easy", 300)
        assert sm.get_high_score("maze", "easy") == 500
        assert sm.get_high_score("math", "easy") == 300
    print("  [PASS] test_different_games_independent")


def test_different_difficulties_independent():
    """不同难度分数独立。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        sm.set_high_score("maze", "hard", 1000)
        assert sm.get_high_score("maze", "easy") == 500
        assert sm.get_high_score("maze", "hard") == 1000
    print("  [PASS] test_different_difficulties_independent")


def test_show_all_returns_string():
    """show_all 返回格式化字符串。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("maze", "easy", 500)
        result = sm.show_all()
        assert isinstance(result, str)
        assert "maze" in result or "记忆" in result
    print("  [PASS] test_show_all_returns_string")


def test_persistence_across_instances():
    """分数跨实例持久化。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        sm1 = ScoreManager(data_dir=tmpdir)
        sm1.set_high_score("rhythm", "hard", 2000)
        sm1.save()

        sm2 = ScoreManager(data_dir=tmpdir)
        assert sm2.get_high_score("rhythm", "hard") == 2000
    print("  [PASS] test_persistence_across_instances")


if __name__ == "__main__":
    print("Running scoring tests...")
    test_save_and_load()
    test_high_score_update()
    test_no_update_if_lower()
    test_reset()
    test_default_score_is_zero()
    test_different_games_independent()
    test_different_difficulties_independent()
    test_show_all_returns_string()
    test_persistence_across_instances()
    print("\nAll scoring tests passed!")
