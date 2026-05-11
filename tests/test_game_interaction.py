#!/usr/bin/env python3
"""游戏交互深度测试 — handle_input / update / render 全面覆盖

每个游戏都经过：
- 初始状态验证
- 各种输入组合
- 状态转换
- 边界行为
- 计分验证
"""
import sys
import os
import tempfile
from unittest.mock import MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.games import get_game_class
from src.engine.renderer import Renderer
from src.engine.input import InputManager
from src.utils.scoring import ScoreManager


def _env():
    tmpdir = tempfile.mkdtemp()
    renderer = Renderer()
    renderer.render_frame = MagicMock()
    renderer.clear = MagicMock()
    renderer.show_cursor = MagicMock()
    renderer.hide_cursor = MagicMock()
    renderer.shake_screen = MagicMock()
    input_mgr = InputManager()
    score_mgr = ScoreManager(data_dir=tmpdir)
    return renderer, input_mgr, score_mgr, tmpdir


def _make_game(gid, difficulty="easy"):
    cls = get_game_class(gid)
    r, i, s, d = _env()
    g = cls(difficulty=difficulty, renderer=r, input_manager=i, score_manager=s)
    g.name = g.name or f"Game{gid}"
    g.setup()
    return g, r, i, s, d


# ── G1 记忆迷宫 ───────────────────────────────────────────────
class TestMemoryMazeInteraction:
    @staticmethod
    def run_all():
        TestMemoryMazeInteraction.test_initial_state()
        TestMemoryMazeInteraction.test_move_no_collision()
        TestMemoryMazeInteraction.test_wall_collision()
        TestMemoryMazeInteraction.test_quit()
        TestMemoryMazeInteraction.test_help_passthrough()
        TestMemoryMazeInteraction.test_none_input()
        TestMemoryMazeInteraction.test_all_difficulties()
        print("  [PASS] All MemoryMazeInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(1)
        assert g._phase == "memorize"
        assert g.player_y == 1
        assert g.player_x == 1
        assert g.score == 1000
        assert g.wall_hits == 0
        assert (1, 1) in g.visited
        g.cleanup()

    @staticmethod
    def test_move_no_collision():
        g, *_ = _make_game(1)
        g._phase = "walk"
        old_y, old_x = g.player_y, g.player_x
        moved = False
        for key, dy, dx in [("w", -1, 0), ("s", 1, 0), ("a", 0, -1), ("d", 0, 1)]:
            ny, nx = old_y + dy, old_x + dx
            if 0 <= ny < g.maze_h and 0 <= nx < g.maze_w and g.maze[ny][nx] == 0:
                g.handle_input(key)
                assert g.player_y == ny
                assert g.player_x == nx
                assert g.wall_hits == 0
                moved = True
                break
        if moved:
            assert (g.player_y, g.player_x) in g.visited
        g.cleanup()

    @staticmethod
    def test_wall_collision():
        g, *_ = _make_game(1)
        g._phase = "walk"
        # Find a wall and a path cell adjacent to it, then walk INTO the wall
        for y in range(g.maze_h):
            for x in range(g.maze_w):
                if g.maze[y][x] == 1:
                    # (dy, dx) = direction FROM wall TO path
                    # key = direction FROM path INTO wall (opposite)
                    for dy, dx, key in [
                        (-1, 0, "s"),   # path above wall -> go south into wall
                        (1, 0, "w"),    # path below wall -> go north into wall
                        (0, -1, "d"),   # path left of wall -> go east into wall
                        (0, 1, "a"),    # path right of wall -> go west into wall
                    ]:
                        ny, nx = y + dy, x + dx  # neighbor position (path cell)
                        if 0 <= ny < g.maze_h and 0 <= nx < g.maze_w and g.maze[ny][nx] == 0:
                            g.player_y = ny
                            g.player_x = nx
                            old_score = g.score
                            g.handle_input(key)
                            assert g.wall_hits >= 1
                            assert g.score == old_score - 100
                            g.cleanup()
                            return
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(1)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_help_passthrough():
        g, *_ = _make_game(1)
        result = g.handle_input("h")
        assert result is True
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(1)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()

    @staticmethod
    def test_all_difficulties():
        for diff in ["easy", "normal", "hard"]:
            g, *_ = _make_game(1, diff)
            assert g._phase == "memorize"
            assert g.score == 1000
            g.cleanup()


# ── G3 密码破译 ──────────────────────────────────────────────
class TestCodeBreakerInteraction:
    @staticmethod
    def run_all():
        TestCodeBreakerInteraction.test_initial_state()
        TestCodeBreakerInteraction.test_correct_answer()
        TestCodeBreakerInteraction.test_wrong_answer()
        TestCodeBreakerInteraction.test_hint_usage()
        TestCodeBreakerInteraction.test_backspace()
        TestCodeBreakerInteraction.test_type_input()
        TestCodeBreakerInteraction.test_quit()
        TestCodeBreakerInteraction.test_none_input()
        print("  [PASS] All CodeBreakerInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(3)
        assert g.current_level == 0
        assert g.lives == 3
        assert g.score == 0
        assert g._input_buffer == ""
        g.cleanup()

    @staticmethod
    def test_correct_answer():
        g, *_ = _make_game(3)
        level = g.current_level
        if level == 0:
            for ch in "Hello World":
                g.handle_input(ch)
            g.handle_input("\r")
            assert g.current_level > level or g._game_over
            assert g.score > 0
        g.cleanup()

    @staticmethod
    def test_wrong_answer():
        g, *_ = _make_game(3)
        old_lives = g.lives
        old_score = g.score
        g.handle_input("wrong answer")
        g.handle_input("\r")
        assert g.lives == old_lives - 1
        assert g.score <= old_score
        g.cleanup()

    @staticmethod
    def test_hint_usage():
        g, *_ = _make_game(3)
        g.handle_input("h")
        # hint should not crash
        g.cleanup()

    @staticmethod
    def test_backspace():
        g, *_ = _make_game(3)
        for ch in "abc":
            g.handle_input(ch)
        assert g._input_buffer == "abc"
        g.handle_input("\x7f")
        assert g._input_buffer == "ab"
        g.handle_input("\x7f")
        assert g._input_buffer == "a"
        g.handle_input("\x7f")
        assert g._input_buffer == ""
        g.cleanup()

    @staticmethod
    def test_type_input():
        g, *_ = _make_game(3)
        for ch in "Test Input":
            g.handle_input(ch)
        assert g._input_buffer == "Test Input"
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(3)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(3)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()


# ── G5 打地鼠 ─────────────────────────────────────────────────
class TestWhackInteraction:
    @staticmethod
    def run_all():
        TestWhackInteraction.test_initial_state()
        TestWhackInteraction.test_hit_mole()
        TestWhackInteraction.test_miss_mole()
        TestWhackInteraction.test_invalid_key()
        TestWhackInteraction.test_quit()
        TestWhackInteraction.test_none_input()
        TestWhackInteraction.test_all_difficulties()
        print("  [PASS] All WhackInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(5)
        assert g._current_round == 0
        assert g._total_rounds > 0
        assert g.score == 0
        assert g._combo == 0
        g.cleanup()

    @staticmethod
    def test_hit_mole():
        g, *_ = _make_game(5)
        g._moles_active = {5}
        g._round_done = False
        old_score = g.score
        g.handle_input("5")
        assert g.score > old_score
        assert g._combo == 1
        g.cleanup()

    @staticmethod
    def test_miss_mole():
        g, *_ = _make_game(5)
        g._moles_active = {1}
        g._round_done = False
        g.handle_input("9")
        assert g._combo == 0
        g.cleanup()

    @staticmethod
    def test_invalid_key():
        g, *_ = _make_game(5)
        g._moles_active = {1}
        g._round_done = False
        g.handle_input("x")
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(5)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(5)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()

    @staticmethod
    def test_all_difficulties():
        for diff in ["easy", "normal", "hard"]:
            g, *_ = _make_game(5, diff)
            assert g._total_rounds > 0
            g.cleanup()


# ── G7 贪吃蛇记忆 ─────────────────────────────────────────────
class TestSnakeInteraction:
    @staticmethod
    def run_all():
        TestSnakeInteraction.test_initial_state()
        TestSnakeInteraction.test_direction_change()
        TestSnakeInteraction.test_no_reverse()
        TestSnakeInteraction.test_quit()
        TestSnakeInteraction.test_none_input()
        TestSnakeInteraction.test_memorize_phase_input_ignored()
        TestSnakeInteraction.test_all_difficulties()
        print("  [PASS] All SnakeInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(7)
        assert g._phase == "memorize"
        assert g._level == 1
        assert len(g._snake) == 3
        assert g.score == 0
        assert g._next_food_num == 1
        g.cleanup()

    @staticmethod
    def test_direction_change():
        g, *_ = _make_game(7)
        g._phase = "play"
        # From initial "right": can go up/down, not left (opposite)
        g.handle_input("w")
        assert g._next_direction == "up"
        g.handle_input("s")
        assert g._next_direction == "down"
        # From "right": "a" (left) is opposite, should be rejected
        g.handle_input("a")
        assert g._next_direction == "down"  # unchanged
        g.cleanup()

    @staticmethod
    def test_no_reverse():
        g, *_ = _make_game(7)
        g._phase = "play"
        # Initial direction is "right"
        assert g._direction == "right"
        # Try reverse: from "right", pressing "a" (left) should be rejected
        g.handle_input("a")
        assert g._next_direction == "right"  # unchanged
        # Set direction to "up" and try "down"
        g._direction = "up"
        g._next_direction = "up"  # sync
        g.handle_input("s")
        assert g._next_direction == "up"  # unchanged (reverse rejected)
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(7)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(7)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()

    @staticmethod
    def test_memorize_phase_input_ignored():
        g, *_ = _make_game(7)
        assert g._phase == "memorize"
        g.handle_input("w")
        assert g._next_direction == "right"
        g.handle_input("a")
        assert g._next_direction == "right"
        g.cleanup()

    @staticmethod
    def test_all_difficulties():
        for diff in ["easy", "normal", "hard"]:
            g, *_ = _make_game(7, diff)
            assert g._phase == "memorize"
            g.cleanup()


# ── G4 节奏大师 ──────────────────────────────────────────────
class TestRhythmInteraction:
    @staticmethod
    def run_all():
        TestRhythmInteraction.test_initial_state()
        TestRhythmInteraction.test_note_generation()
        TestRhythmInteraction.test_quit()
        TestRhythmInteraction.test_none_input()
        TestRhythmInteraction.test_all_difficulties()
        TestRhythmInteraction.test_judgment_windows()
        print("  [PASS] All RhythmInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(4)
        assert g.num_notes > 0
        assert len(g._notes) == g.num_notes
        assert g.score == 0
        assert g.combo == 0
        assert g._countdown == 3
        g.cleanup()

    @staticmethod
    def test_note_generation():
        g, *_ = _make_game(4)
        for note in g._notes:
            assert "track" in note
            assert "key" in note
            assert "target_time" in note
            assert note["hit"] is False
            assert note["missed"] is False
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(4)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(4)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()

    @staticmethod
    def test_all_difficulties():
        for diff in ["easy", "normal", "hard"]:
            g, *_ = _make_game(4, diff)
            assert g.num_notes > 0
            g.cleanup()

    @staticmethod
    def test_judgment_windows():
        from src.games.rhythm import PERFECT_WINDOW, GOOD_WINDOW
        assert PERFECT_WINDOW == 0.15
        assert GOOD_WINDOW == 0.35
        assert PERFECT_WINDOW < GOOD_WINDOW


# ── G2 弹幕大脑 ──────────────────────────────────────────────
class TestMathDodgeInteraction:
    @staticmethod
    def run_all():
        TestMathDodgeInteraction.test_initial_state()
        TestMathDodgeInteraction.test_quit()
        TestMathDodgeInteraction.test_none_input()
        TestMathDodgeInteraction.test_all_difficulties()
        TestMathDodgeInteraction.test_question_validity()
        print("  [PASS] All MathDodgeInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(2)
        assert hasattr(g, "score")
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(2)
        result = g.handle_input("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(2)
        result = g.handle_input(None)
        assert result is True
        g.cleanup()

    @staticmethod
    def test_all_difficulties():
        for diff in ["easy", "normal", "hard"]:
            g, *_ = _make_game(2, diff)
            g.cleanup()

    @staticmethod
    def test_question_validity():
        from src.games.math_dodge import generate_question, DIFFICULTY_CONFIG
        for diff in ["easy", "normal", "hard"]:
            cfg = DIFFICULTY_CONFIG[diff]
            for _ in range(10):
                q, correct, wrong = generate_question(diff, cfg["max_val"])
                assert isinstance(q, str) and len(q) > 0
                assert isinstance(correct, int)
                assert correct not in wrong
                assert len(wrong) >= cfg["options"] - 1


# ── G6 故事解谜 ──────────────────────────────────────────────
class TestStoryInteraction:
    @staticmethod
    def run_all():
        TestStoryInteraction.test_initial_state()
        TestStoryInteraction.test_look_command()
        TestStoryInteraction.test_inventory_command()
        TestStoryInteraction.test_take_command()
        TestStoryInteraction.test_go_command()
        TestStoryInteraction.test_solve_command()
        TestStoryInteraction.test_unknown_command()
        TestStoryInteraction.test_quit()
        TestStoryInteraction.test_none_input()
        print("  [PASS] All StoryInteraction tests")

    @staticmethod
    def test_initial_state():
        g, *_ = _make_game(6)
        assert g.current_scene == "gate"
        assert g.inventory == []
        assert g.score == 0
        assert g._puzzles_solved == 0
        g.cleanup()

    @staticmethod
    def test_look_command():
        g, *_ = _make_game(6)
        g._process_command("look")
        assert g._message != ""
        g._process_command("look 门牌号")
        assert g._message != ""
        g.cleanup()

    @staticmethod
    def test_inventory_command():
        g, *_ = _make_game(6)
        g._process_command("inventory")
        assert "空" in g._message
        g._process_command("inv")
        assert "空" in g._message
        g.cleanup()

    @staticmethod
    def test_take_command():
        g, *_ = _make_game(6)
        # gate scene has no takeable items
        g._process_command("take 门牌号")
        assert "无法拾取" in g._message
        # 旧信件 is in hall scene, not accessible from gate
        g._process_command("take 旧信件")
        assert "没有" in g._message or "这里没有" in g._message
        # Test taking non-existent item
        g._process_command("take 不存在的物品")
        assert "没有" in g._message
        g.cleanup()

    @staticmethod
    def test_go_command():
        g, *_ = _make_game(6)
        # gate is initially locked for north exit
        g._process_command("go north")
        # Should not crash
        g.cleanup()

    @staticmethod
    def test_solve_command():
        g, *_ = _make_game(6)
        g._process_command("solve 3719")
        g.cleanup()

    @staticmethod
    def test_unknown_command():
        g, *_ = _make_game(6)
        g._process_command("foobar")
        assert "未知命令" in g._message
        g.cleanup()

    @staticmethod
    def test_quit():
        g, *_ = _make_game(6)
        result = g._process_command("q")
        assert result is False
        g.cleanup()

    @staticmethod
    def test_none_input():
        g, *_ = _make_game(6)
        result = g._process_command("")
        assert result is True
        g.cleanup()


if __name__ == "__main__":
    print("Running Game Interaction tests...")
    TestMemoryMazeInteraction.run_all()
    TestCodeBreakerInteraction.run_all()
    TestWhackInteraction.run_all()
    TestSnakeInteraction.run_all()
    TestRhythmInteraction.run_all()
    TestMathDodgeInteraction.run_all()
    TestStoryInteraction.run_all()
    print("\nAll Game Interaction tests passed!")
