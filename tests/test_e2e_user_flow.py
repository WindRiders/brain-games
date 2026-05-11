#!/usr/bin/env python3
"""真实用户流程端到端测试 — 模拟用户从启动到退出的完整流程

使用真实的菜单渲染函数 + 游戏实例，模拟用户操作流。
不依赖真实 TTY，但测试真实的菜单内容和游戏初始化流程。
"""
import sys
import os
import tempfile
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Import main menu functions
from main import draw_main_menu, draw_difficulty_menu, draw_scores_menu, draw_confirm
from src.games import get_game_class, get_game_list, get_game_name
from src.engine.renderer import Renderer
from src.engine.input import InputManager
from src.utils.scoring import ScoreManager
from unittest.mock import MagicMock


def _strip_ansi(text: str) -> str:
    """去除 ANSI 转义序列"""
    return re.sub(r'\033\[[0-9;]*m', '', text)


def _env():
    """创建测试环境"""
    tmpdir = tempfile.mkdtemp()
    renderer = Renderer()
    renderer.render = lambda x: None
    renderer.render_frame = lambda x: None
    renderer.clear = MagicMock()
    renderer.show_cursor = MagicMock()
    renderer.hide_cursor = MagicMock()
    renderer.shake_screen = MagicMock()
    input_mgr = InputManager()
    score_mgr = ScoreManager(data_dir=tmpdir)
    return renderer, input_mgr, score_mgr, tmpdir


# ── UF-01: 启动 → 主菜单显示 ──
class TestMainMenuDisplay:
    @staticmethod
    def run_all():
        TestMainMenuDisplay.test_menu_renders()
        TestMainMenuDisplay.test_menu_shows_all_games()
        TestMainMenuDisplay.test_menu_has_options()
        TestMainMenuDisplay.test_menu_ascii_art()
        print("  [PASS] All MainMenuDisplay tests")

    @staticmethod
    def test_menu_renders():
        """主菜单能正常渲染"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_main_menu(scores)
        assert len(menu) > 100, "菜单应该有足够的内容"
        assert isinstance(menu, str)

    @staticmethod
    def test_menu_shows_all_games():
        """主菜单显示7个游戏"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_main_menu(scores)

        games = get_game_list()
        clean = _strip_ansi(menu)
        for g in games:
            assert f"[{g['id']}]" in menu, f"菜单应包含游戏 {g['id']}: {g['name']}"
            assert g['name'] in clean, f"菜单应包含游戏名称: {g['name']}"

    @staticmethod
    def test_menu_has_options():
        """主菜单包含操作选项"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_main_menu(scores)

        assert "[S]" in menu or "查看最高分" in menu
        assert "[R]" in menu or "重置分数" in menu
        assert "[Q]" in menu or "退出" in menu

    @staticmethod
    def test_menu_ascii_art():
        """主菜单包含 ASCII 艺术标题"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_main_menu(scores)
        clean = _strip_ansi(menu)
        assert "终" in clean or "脑力" in clean or "训练" in clean


# ── UF-02: 难度菜单 ──
class TestDifficultyMenu:
    @staticmethod
    def run_all():
        TestDifficultyMenu.test_menu_renders()
        TestDifficultyMenu.test_shows_three_difficulties()
        TestDifficultyMenu.test_has_back_option()
        print("  [PASS] All DifficultyMenu tests")

    @staticmethod
    def test_menu_renders():
        """难度菜单能正常渲染"""
        menu = draw_difficulty_menu("记忆迷宫")
        assert len(menu) > 50
        assert isinstance(menu, str)

    @staticmethod
    def test_shows_three_difficulties():
        """难度菜单显示三个难度"""
        menu = draw_difficulty_menu("测试游戏")
        assert "[1]" in menu and "简单" in menu
        assert "[2]" in menu and "普通" in menu
        assert "[3]" in menu and "困难" in menu

    @staticmethod
    def test_has_back_option():
        """难度菜单有返回选项"""
        menu = draw_difficulty_menu("测试游戏")
        assert "[Q]" in menu


# ── UF-03: 分数菜单 ──
class TestScoresMenu:
    @staticmethod
    def run_all():
        TestScoresMenu.test_menu_renders()
        TestScoresMenu.test_empty_scores()
        TestScoresMenu.test_with_scores()
        print("  [PASS] All ScoresMenu tests")

    @staticmethod
    def test_menu_renders():
        """分数菜单能正常渲染"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_scores_menu(scores)
        assert len(menu) > 20

    @staticmethod
    def test_empty_scores():
        """空分数显示"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        menu = draw_scores_menu(scores)
        clean = _strip_ansi(menu)
        assert "最高分" in clean.replace(" ", "") or "暂无分数" in clean

    @staticmethod
    def test_with_scores():
        """有分数时显示"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        scores.set_high_score("记忆迷宫", "easy", 500)
        scores.set_high_score("弹幕大脑", "normal", 300)
        menu = draw_scores_menu(scores)
        clean = _strip_ansi(menu)
        assert "500" in menu
        assert "300" in menu


# ── UF-04: 确认菜单 ──
class TestConfirmDialog:
    @staticmethod
    def run_all():
        TestConfirmDialog.test_renders()
        TestConfirmDialog.test_has_yes_no()
        print("  [PASS] All ConfirmDialog tests")

    @staticmethod
    def test_renders():
        """确认对话框能正常渲染"""
        confirm = draw_confirm("确定要重置所有分数吗？")
        assert len(confirm) > 20
        assert "确定要重置" in confirm

    @staticmethod
    def test_has_yes_no():
        """确认对话框有 Y/N 选项"""
        confirm = draw_confirm("确认操作")
        assert "[Y]" in confirm
        assert "[N]" in confirm


# ── UF-05: 游戏注册 ──
class TestGameRegistry:
    @staticmethod
    def run_all():
        TestGameRegistry.test_game_list_complete()
        TestGameRegistry.test_game_class_available()
        TestGameRegistry.test_game_names()
        print("  [PASS] All GameRegistry tests")

    @staticmethod
    def test_game_list_complete():
        """游戏列表完整"""
        games = get_game_list()
        assert len(games) == 7, f"应有 7 个游戏，实际 {len(games)}"

    @staticmethod
    def test_game_class_available():
        """所有游戏类可获取"""
        for gid in range(1, 8):
            cls = get_game_class(gid)
            assert cls is not None, f"游戏 {gid} 的类不可用"

    @staticmethod
    def test_game_names():
        """游戏名称正确"""
        expected_names = ["记忆迷宫", "弹幕大脑", "密码破译", "节奏大师", "打地鼠", "故事解谜", "贪吃蛇记忆"]
        for gid, expected in enumerate(expected_names, 1):
            name = get_game_name(gid)
            assert name == expected, f"游戏 {gid} 名称应为 {expected}，实际 {name}"


# ── UF-06: 真实游戏流程模拟 ──
class TestRealGameFlow:
    @staticmethod
    def run_all():
        TestRealGameFlow.test_full_game_lifecycle()
        TestRealGameFlow.test_game_with_scores()
        TestRealGameFlow.test_multiple_games_sequence()
        TestRealGameFlow.test_help_then_quit()
        print("  [PASS] All RealGameFlow tests")

    @staticmethod
    def test_full_game_lifecycle():
        """完整游戏流程: 创建 → setup → 输入 → 退出 → cleanup"""
        for gid in range(1, 8):
            cls = get_game_class(gid)
            r, i, s, d = _env()
            g = cls(difficulty="easy", renderer=r, input_manager=i, score_manager=s)
            g.name = get_game_name(gid)
            g.setup()

            # Simulate some player actions
            g.handle_input("h")  # View help
            g.handle_input("a")  # Random input
            g.handle_input("q")  # Quit

            g.cleanup()

    @staticmethod
    def test_game_with_scores():
        """游戏流程包含分数操作"""
        tmpdir = tempfile.mkdtemp()
        scores = ScoreManager(data_dir=tmpdir)
        renderer = Renderer()
        renderer.render_frame = MagicMock()
        renderer.shake_screen = MagicMock()
        input_mgr = InputManager()

        # Play a maze game
        cls = get_game_class(1)
        g = cls(difficulty="easy", renderer=renderer, input_manager=input_mgr, score_manager=scores)
        g.name = "记忆迷宫"
        g.setup()

        # Move around
        g._phase = "walk"  # Skip memorize phase
        for key in ["w", "a", "s", "d"]:
            g.handle_input(key)
        g.handle_input("q")
        g.cleanup()

        # Verify score was potentially saved
        score_path = os.path.join(tmpdir, "scores.json")
        if os.path.exists(score_path):
            with open(score_path) as f:
                data = json.load(f)
            assert isinstance(data, dict)

    @staticmethod
    def test_multiple_games_sequence():
        """连续玩多个游戏"""
        sequence = [1, 3, 5, 7]
        for gid in sequence:
            cls = get_game_class(gid)
            r, i, s, d = _env()
            g = cls(difficulty="easy", renderer=r, input_manager=i, score_manager=s)
            g.name = get_game_name(gid)
            g.setup()
            g.handle_input("q")
            g.cleanup()

    @staticmethod
    def test_help_then_quit():
        """查看帮助后退出"""
        for gid in [2, 4, 6]:
            cls = get_game_class(gid)
            r, i, s, d = _env()
            g = cls(difficulty="easy", renderer=r, input_manager=i, score_manager=s)
            g.name = get_game_name(gid)
            g.setup()

            help_text = g.show_help()
            assert isinstance(help_text, str)
            assert len(help_text) > 10

            g.handle_input("q")
            g.cleanup()


if __name__ == "__main__":
    print("Running User Flow E2E tests...")
    TestMainMenuDisplay.run_all()
    TestDifficultyMenu.run_all()
    TestScoresMenu.run_all()
    TestConfirmDialog.run_all()
    TestGameRegistry.run_all()
    TestRealGameFlow.run_all()
    print("\nAll User Flow E2E tests passed!")
