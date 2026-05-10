"""UI 组件测试"""
import sys
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.ui.components import box, progress_bar, center, header, divider
from src.ui.colors import C


class TestCenter:
    """center() 居中对齐测试。"""
    @staticmethod
    def run_all():
        TestCenter.test_short_text_padded()
        TestCenter.test_exact_fit()
        TestCenter.test_empty_string()
        TestCenter.test_long_text_unchanged()
        TestCenter.test_with_color_codes()
        print("  [PASS] All Center tests")

    @staticmethod
    def test_short_text_padded():
        result = center("hi", 10)
        assert result.startswith("    ")  # left-padded
        assert result.endswith("hi")  # original text preserved

    @staticmethod
    def test_exact_fit():
        text = "A" * 20
        result = center(text, 20)
        assert result == text

    @staticmethod
    def test_empty_string():
        result = center("", 10)
        assert result.strip() == ""  # only spaces

    @staticmethod
    def test_long_text_unchanged():
        result = center("This is a very long text", 10)
        assert "This is a very long text" in result

    @staticmethod
    def test_with_color_codes():
        result = center(f"{C.RED}test{C.RESET}", 10)
        assert result.endswith("test" + C.RESET)


class TestDivider:
    @staticmethod
    def run_all():
        TestDivider.test_default_width()
        TestDivider.test_custom_width()
        TestDivider.test_custom_char()
        print("  [PASS] All Divider tests")

    @staticmethod
    def test_default_width():
        result = divider()
        assert len(result) == 55

    @staticmethod
    def test_custom_width():
        result = divider(width=30)
        assert len(result) == 30

    @staticmethod
    def test_custom_char():
        result = divider(width=20, char="-")
        assert result == "-" * 20


class TestHeader:
    @staticmethod
    def run_all():
        TestHeader.test_basic()
        TestHeader.test_has_borders()
        print("  [PASS] All Header tests")

    @staticmethod
    def test_basic():
        result = header("Test Title")
        assert "Test Title" in result

    @staticmethod
    def test_has_borders():
        result = header("Test")
        assert result.startswith("╔")
        assert "║" in result
        assert result.endswith("╝")


class TestProgressBar:
    @staticmethod
    def run_all():
        TestProgressBar.test_zero()
        TestProgressBar.test_hundred()
        TestProgressBar.test_half()
        TestProgressBar.test_has_percentage()
        print("  [PASS] All ProgressBar tests")

    @staticmethod
    def test_zero():
        result = progress_bar(0, width=20)
        visible = re.sub(r'\033\[[0-9;]*m', '', result)
        assert visible.count("█") == 0
        assert "0.0%" in visible

    @staticmethod
    def test_hundred():
        result = progress_bar(100, width=20)
        visible = re.sub(r'\033\[[0-9;]*m', '', result)
        assert visible.count("░") == 0
        assert "100.0%" in visible

    @staticmethod
    def test_half():
        result = progress_bar(50, width=20)
        visible = re.sub(r'\033\[[0-9;]*m', '', result)
        assert visible.count("█") == 10
        assert visible.count("░") == 10

    @staticmethod
    def test_has_percentage():
        result = progress_bar(75, width=10)
        assert "%" in result


class TestBox:
    @staticmethod
    def run_all():
        TestBox.test_basic()
        TestBox.test_empty_content()
        TestBox.test_has_borders()
        TestBox.test_content_preserved()
        print("  [PASS] All Box tests")

    @staticmethod
    def test_basic():
        result = box("Title", ["line1", "line2"])
        assert "line1" in result
        assert "line2" in result

    @staticmethod
    def test_empty_content():
        result = box("Title", [])
        assert "Title" in result

    @staticmethod
    def test_has_borders():
        result = box("Title", ["content"])
        assert result.startswith("┌")
        assert "│" in result
        assert result.strip().endswith("┘")

    @staticmethod
    def test_content_preserved():
        result = box("Test", ["hello world"])
        assert "hello world" in result


if __name__ == "__main__":
    print("Running UI component tests...")
    TestCenter.run_all()
    TestDivider.run_all()
    TestHeader.run_all()
    TestProgressBar.run_all()
    TestBox.run_all()
    print("\nAll UI component tests passed!")
