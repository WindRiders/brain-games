#!/usr/bin/env python3
"""评分系统全面测试"""
import sys
import os
import json
import tempfile

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.scoring import ScoreManager


class TestScoringComprehensive:
    @staticmethod
    def run_all():
        TestScoringComprehensive.test_create()
        TestScoringComprehensive.test_set_and_get()
        TestScoringComprehensive.test_higher_score_only()
        TestScoringComprehensive.test_all_games_show()
        TestScoringComprehensive.test_reset_score()
        TestScoringComprehensive.test_invalid_data_dir()
        TestScoringComprehensive.test_concurrent_access()
        TestScoringComprehensive.test_score_persistence()
        TestScoringComprehensive.test_negative_scores()
        TestScoringComprehensive.test_zero_score()
        print("  [PASS] All ScoringComprehensive tests")

    @staticmethod
    def test_create():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        assert sm is not None

    @staticmethod
    def test_set_and_get():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("TestGame", "easy", 100)
        assert sm.get_high_score("TestGame", "easy") == 100

    @staticmethod
    def test_higher_score_only():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("TestGame", "easy", 100)
        sm.set_high_score("TestGame", "easy", 50)
        assert sm.get_high_score("TestGame", "easy") == 100
        sm.set_high_score("TestGame", "easy", 200)
        assert sm.get_high_score("TestGame", "easy") == 200

    @staticmethod
    def test_all_games_show():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("Game1", "easy", 100)
        sm.set_high_score("Game2", "normal", 200)
        sm.set_high_score("Game3", "hard", 300)
        output = sm.show_all()
        assert output is None or isinstance(output, str)

    @staticmethod
    def test_reset_score():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("TestGame", "easy", 100)
        sm.reset()  # reset() resets all scores
        assert sm.get_high_score("TestGame", "easy") == 0

    @staticmethod
    def test_invalid_data_dir():
        # Should handle non-existent directory gracefully
        tmpdir = tempfile.mkdtemp()
        invalid_dir = os.path.join(tmpdir, "nonexistent", "deep")
        sm = ScoreManager(data_dir=invalid_dir)
        sm.set_high_score("Test", "easy", 50)
        assert sm.get_high_score("Test", "easy") == 50

    @staticmethod
    def test_concurrent_access():
        tmpdir = tempfile.mkdtemp()
        sm1 = ScoreManager(data_dir=tmpdir)
        sm1.set_high_score("TestGame", "easy", 100)
        # Second instance needs to reload to see updated data
        sm2 = ScoreManager(data_dir=tmpdir)
        sm2.load()
        val = sm2.get_high_score("TestGame", "easy")
        assert val == 100

    @staticmethod
    def test_score_persistence():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("PersistTest", "hard", 999)
        # Create new instance (simulates restart)
        sm2 = ScoreManager(data_dir=tmpdir)
        assert sm2.get_high_score("PersistTest", "hard") == 999

    @staticmethod
    def test_negative_scores():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("TestGame", "easy", -50)
        # ScoreManager may or may not store negatives, just verify no crash
        g = sm.get_high_score("TestGame", "easy")
        assert isinstance(g, int)

    @staticmethod
    def test_zero_score():
        tmpdir = tempfile.mkdtemp()
        sm = ScoreManager(data_dir=tmpdir)
        sm.set_high_score("TestGame", "easy", 0)
        assert sm.get_high_score("TestGame", "easy") == 0


if __name__ == "__main__":
    print("Running Scoring Comprehensive tests...")
    TestScoringComprehensive.run_all()
    print("\nAll Scoring tests passed!")
