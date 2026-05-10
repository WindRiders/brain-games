"""计时器测试"""
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.engine.timer import GameTimer


class TestGameTimer:
    @staticmethod
    def run_all():
        TestGameTimer.test_start_and_elapsed()
        TestGameTimer.test_stop()
        TestGameTimer.test_pause_resume()
        TestGameTimer.test_get_remaining()
        TestGameTimer.test_format_time()
        TestGameTimer.test_elapsed_monotonic()
        print("  [PASS] All GameTimer tests")

    @staticmethod
    def test_start_and_elapsed():
        timer = GameTimer()
        timer.start()
        time.sleep(0.1)
        elapsed = timer.get_elapsed()
        assert elapsed >= 0.08, f"Expected >= 0.08, got {elapsed}"
        timer.stop()

    @staticmethod
    def test_stop():
        timer = GameTimer()
        timer.start()
        time.sleep(0.05)
        timer.stop()
        elapsed_after_stop = timer.get_elapsed()
        time.sleep(0.1)
        elapsed_later = timer.get_elapsed()
        assert abs(elapsed_after_stop - elapsed_later) < 0.01, "Timer should not advance after stop"

    @staticmethod
    def test_pause_resume():
        timer = GameTimer()
        timer.start()
        time.sleep(0.05)
        t1 = timer.get_elapsed()
        timer.pause()
        time.sleep(0.1)
        t2 = timer.get_elapsed()
        assert abs(t2 - t1) < 0.01, "Timer should not advance while paused"
        timer.resume()
        time.sleep(0.05)
        t3 = timer.get_elapsed()
        assert t3 > t2 + 0.03, "Timer should advance after resume"
        timer.stop()

    @staticmethod
    def test_get_remaining():
        timer = GameTimer()
        timer.start()
        remaining = timer.get_remaining(10)
        assert remaining <= 10
        assert remaining > 9
        timer.stop()

    @staticmethod
    def test_format_time():
        timer = GameTimer()
        timer.start()
        time.sleep(0.05)
        fmt = timer.format_time()
        assert isinstance(fmt, str)
        assert "s" in fmt or ":" in fmt
        timer.stop()

    @staticmethod
    def test_elapsed_monotonic():
        timer = GameTimer()
        timer.start()
        t1 = timer.get_elapsed()
        time.sleep(0.02)
        t2 = timer.get_elapsed()
        assert t2 >= t1, "Elapsed time should not decrease"
        timer.stop()


if __name__ == "__main__":
    print("Running timer tests...")
    TestGameTimer.run_all()
    print("\nAll timer tests passed!")
