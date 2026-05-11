#!/usr/bin/env python3
"""GameTimer 全面测试"""
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.engine.timer import GameTimer


class TestTimerComprehensive:
    @staticmethod
    def run_all():
        TestTimerComprehensive.test_create_and_start()
        TestTimerComprehensive.test_elapsed_increases()
        TestTimerComprehensive.test_stop()
        TestTimerComprehensive.test_pause_resume()
        TestTimerComprehensive.test_get_remaining()
        TestTimerComprehensive.test_format_time()
        TestTimerComprehensive.test_reset()
        TestTimerComprehensive.test_elapsed_precision()
        print("  [PASS] All TimerComprehensive tests")

    @staticmethod
    def test_create_and_start():
        t = GameTimer()
        assert t.is_running is False
        t.start()
        assert t.is_running is True

    @staticmethod
    def test_elapsed_increases():
        t = GameTimer()
        t.start()
        e1 = t.get_elapsed()
        time.sleep(0.05)
        e2 = t.get_elapsed()
        assert e2 > e1

    @staticmethod
    def test_stop():
        t = GameTimer()
        t.start()
        time.sleep(0.02)
        elapsed_before = t.get_elapsed()
        t.stop()
        assert t.is_running is False
        time.sleep(0.05)
        elapsed_after = t.get_elapsed()
        assert abs(elapsed_after - elapsed_before) < 0.02

    @staticmethod
    def test_pause_resume():
        t = GameTimer()
        t.start()
        time.sleep(0.03)
        paused_elapsed = t.get_elapsed()
        t.pause()
        assert t.is_paused is True
        time.sleep(0.05)
        while_paused = t.get_elapsed()
        assert abs(while_paused - paused_elapsed) < 0.02
        t.resume()
        assert t.is_paused is False
        time.sleep(0.03)
        after_resume = t.get_elapsed()
        assert after_resume > while_paused

    @staticmethod
    def test_get_remaining():
        t = GameTimer()
        t.start()
        remaining = t.get_remaining(5.0)
        assert remaining > 0
        assert remaining <= 5.0

    @staticmethod
    def test_format_time():
        t = GameTimer()
        t.start()
        time.sleep(0.02)
        result = t.format_time()
        assert isinstance(result, str)
        assert len(result) > 0

    @staticmethod
    def test_reset():
        t = GameTimer()
        t.start()
        time.sleep(0.02)
        assert t.get_elapsed() > 0
        t.stop()
        t2 = GameTimer()
        assert t2.get_elapsed() == 0

    @staticmethod
    def test_elapsed_precision():
        t = GameTimer()
        t.start()
        e = t.get_elapsed()
        assert isinstance(e, float)


if __name__ == "__main__":
    print("Running Timer Comprehensive tests...")
    TestTimerComprehensive.run_all()
    print("\nAll Timer tests passed!")
