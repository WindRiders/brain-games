#!/usr/bin/env python3
"""渲染引擎测试 — Renderer 类全面覆盖"""
import sys
import os
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.engine.renderer import Renderer


class TestRendererBasics:
    @staticmethod
    def run_all():
        TestRendererBasics.test_init()
        TestRendererBasics.test_terminal_size()
        TestRendererBasics.test_render_frame()
        TestRendererBasics.test_render_frame_empty()
        TestRendererBasics.test_clear()
        TestRendererBasics.test_hide_show_cursor()
        TestRendererBasics.test_shake_screen()
        TestRendererBasics.test_flash()
        print("  [PASS] All RendererBasics tests")

    @staticmethod
    def test_init():
        r = Renderer()
        assert hasattr(r, "terminal_width")
        assert hasattr(r, "terminal_height")
        assert r.terminal_width > 0
        assert r.terminal_height > 0

    @staticmethod
    def test_terminal_size():
        r = Renderer()
        w = r.terminal_width
        h = r.terminal_height
        assert isinstance(w, int) and w > 0
        assert isinstance(h, int) and h > 0

    @staticmethod
    def test_render_frame():
        r = Renderer()
        lines = ["Hello", "World"]
        r.render_frame(lines)  # Should not crash

    @staticmethod
    def test_render_frame_empty():
        r = Renderer()
        r.render_frame([])  # Should not crash

    @staticmethod
    def test_clear():
        r = Renderer()
        r.clear()

    @staticmethod
    def test_hide_show_cursor():
        r = Renderer()
        r.hide_cursor()
        r.show_cursor()

    @staticmethod
    def test_shake_screen():
        r = Renderer()
        r.shake_screen(times=2)

    @staticmethod
    def test_flash():
        r = Renderer()
        r.flash(color="\033[31m")  # Should not crash


class TestRendererStyling:
    @staticmethod
    def run_all():
        TestRendererStyling.test_color_codes_exist()
        TestRendererStyling.test_box_component()
        TestRendererStyling.test_header_component()
        TestRendererStyling.test_divider_component()
        TestRendererStyling.test_progress_bar_component()
        print("  [PASS] All RendererStyling tests")

    @staticmethod
    def test_color_codes_exist():
        from src.ui import colors as C
        assert hasattr(C, "RED")
        assert hasattr(C, "GREEN")
        assert hasattr(C, "BLUE")
        assert hasattr(C, "RESET")
        assert hasattr(C, "BOLD")
        assert len(C.RED) > 0
        assert len(C.RESET) > 0

    @staticmethod
    def test_box_component():
        from src.ui.components import box
        result = box("Title", ["Line 1", "Line 2"], 40)
        assert isinstance(result, str)
        assert "Title" in result
        assert "Line 1" in result
        assert "Line 2" in result

    @staticmethod
    def test_header_component():
        from src.ui.components import header
        result = header(" Test ")
        assert isinstance(result, str)
        assert "Test" in result

    @staticmethod
    def test_divider_component():
        from src.ui.components import divider
        result = divider(40)
        assert isinstance(result, str)
        assert len(result) > 0

    @staticmethod
    def test_progress_bar_component():
        from src.ui.components import progress_bar
        result = progress_bar(50, 20)
        assert isinstance(result, str)
        result0 = progress_bar(0, 20)
        result100 = progress_bar(100, 20)
        assert len(result100) > 0


if __name__ == "__main__":
    print("Running Renderer tests...")
    TestRendererBasics.run_all()
    TestRendererStyling.run_all()
    print("\nAll Renderer tests passed!")
