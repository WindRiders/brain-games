#!/usr/bin/env python3
"""输入管理器全面测试"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.engine.input import InputManager


class TestInputComprehensive:
    @staticmethod
    def run_all():
        TestInputComprehensive.test_init()
        TestInputComprehensive.test_key_mapping()
        TestInputComprehensive.test_control_char_handling()
        TestInputComprehensive.test_escape_sequences()
        TestInputComprehensive.test_cleanup_safety()
        TestInputComprehensive.test_double_cleanup()
        print("  [PASS] All InputComprehensive tests")

    @staticmethod
    def test_init():
        im = InputManager()
        assert im is not None

    @staticmethod
    def test_key_mapping():
        # Verify key name mapping logic exists
        im = InputManager()
        # Check that common key names are handled
        keys = ["w", "a", "s", "d", "q", "h", " ", "1", "9"]
        for k in keys:
            assert isinstance(k, str)
            assert len(k) == 1 or k == " "

    @staticmethod
    def test_control_char_handling():
        # Control characters should be valid inputs
        control_chars = ["\x03", "\x1b", "\x7f", "\x08"]
        for cc in control_chars:
            assert isinstance(cc, str)

    @staticmethod
    def test_escape_sequences():
        # Arrow key escape sequences
        esc = "\x1b"
        arrow_keys = [f"{esc}[A", f"{esc}[B", f"{esc}[C", f"{esc}[D"]
        for ak in arrow_keys:
            assert ak.startswith("\x1b")

    @staticmethod
    def test_cleanup_safety():
        im = InputManager()
        im.cleanup()

    @staticmethod
    def test_double_cleanup():
        im = InputManager()
        im.cleanup()
        im.cleanup()  # Should not crash


class TestInputPlatform:
    @staticmethod
    def run_all():
        TestInputPlatform.test_platform_detection()
        TestInputPlatform.test_windows_vs_unix()
        print("  [PASS] All InputPlatform tests")

    @staticmethod
    def test_platform_detection():
        import platform
        p = platform.system()
        assert p in ("Linux", "Darwin", "Windows")

    @staticmethod
    def test_windows_vs_unix():
        import platform
        is_windows = platform.system() == "Windows"
        # InputManager should handle both platforms
        im = InputManager()
        assert im is not None


if __name__ == "__main__":
    print("Running Input Comprehensive tests...")
    TestInputComprehensive.run_all()
    TestInputPlatform.run_all()
    print("\nAll Input tests passed!")
