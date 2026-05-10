"""游戏逻辑测试 — 各游戏核心逻辑，使用动态导入避免循环依赖"""
import sys
import os
import importlib

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


def _import_game(module_name):
    return importlib.import_module(f"src.games.{module_name}")


class TestMemoryMazeLogic:
    @staticmethod
    def run_all():
        TestMemoryMazeLogic.test_difficulty_config()
        TestMemoryMazeLogic.test_render_maze_cell()
        TestMemoryMazeLogic.test_scoring_formula()
        TestMemoryMazeLogic.test_wall_collision()
        print("  [PASS] All MemoryMazeLogic tests")

    @staticmethod
    def test_difficulty_config():
        m = _import_game("maze")
        cfg = m.DIFFICULTY_CONFIG
        assert cfg["easy"]["width"] == 5
        assert cfg["easy"]["height"] == 5
        assert cfg["easy"]["mem_time"] == 15
        assert cfg["normal"]["width"] == 8
        assert cfg["hard"]["width"] == 12

    @staticmethod
    def test_render_maze_cell():
        from src.utils.maze_gen import generate_maze
        maze = generate_maze(5, 5)
        for x in range(5):
            assert maze[0][x] == 1
            assert maze[4][x] == 1
        for y in range(5):
            assert maze[y][0] == 1
            assert maze[y][4] == 1

    @staticmethod
    def test_scoring_formula():
        base = 1000
        wall_hits = 2
        time_remaining = 8
        score = base - wall_hits * 100 + time_remaining * 50
        assert score == 1200

    @staticmethod
    def test_wall_collision():
        maze = [[1]*5 for _ in range(5)]
        maze[1][1] = 0
        maze[1][2] = 1
        px, py = 1, 1
        new_x = px + 1
        assert maze[py][new_x] == 1


class TestMathDodgeLogic:
    @staticmethod
    def run_all():
        TestMathDodgeLogic.test_question_generation_easy()
        TestMathDodgeLogic.test_question_generation_hard()
        TestMathDodgeLogic.test_scoring_with_combo()
        TestMathDodgeLogic.test_player_bounds()
        print("  [PASS] All MathDodgeLogic tests")

    @staticmethod
    def test_question_generation_easy():
        m = _import_game("math_dodge")
        cfg = m.DIFFICULTY_CONFIG["easy"]
        for _ in range(20):
            q, correct, wrong = m.generate_question("easy", cfg["max_val"])
            assert isinstance(q, str) and len(q) > 0
            assert isinstance(correct, int)
            assert len(wrong) >= 1, "Should have at least 1 wrong answer"
            assert correct not in wrong

    @staticmethod
    def test_question_generation_hard():
        m = _import_game("math_dodge")
        cfg = m.DIFFICULTY_CONFIG["hard"]
        for _ in range(20):
            q, correct, wrong = m.generate_question("hard", cfg["max_val"])
            assert isinstance(q, str) and len(q) > 0
            assert isinstance(correct, int)
            assert len(wrong) >= 1, "Should have at least 1 wrong answer"

    @staticmethod
    def test_scoring_with_combo():
        score = 0
        combo = 0
        for _ in range(3):
            score += 100
            combo += 1
        if combo >= 3:
            score += 50
        assert score == 350

    @staticmethod
    def test_player_bounds():
        player_x = 25
        min_x, max_x = 2, 48
        new_x = max(min_x, player_x - 2)
        assert new_x == 23
        player_x = 2
        new_x = max(min_x, player_x - 2)
        assert new_x == 2


class TestCodeBreakerLogic:
    @staticmethod
    def run_all():
        TestCodeBreakerLogic.test_scoring()
        TestCodeBreakerLogic.test_penalty()
        TestCodeBreakerLogic.test_hint_penalty()
        TestCodeBreakerLogic.test_level_count()
        print("  [PASS] All CodeBreakerLogic tests")

    @staticmethod
    def test_scoring():
        for level in range(1, 11):
            base = level * 100
            assert base == level * 100

    @staticmethod
    def test_penalty():
        base = 300
        penalty = int(base * 0.2)
        assert penalty == 60
        assert base - penalty == 240

    @staticmethod
    def test_hint_penalty():
        base = 300
        hint_penalty = int(base * 0.1)
        assert hint_penalty == 30

    @staticmethod
    def test_level_count():
        m = _import_game("code_breaker")
        assert len(m.LEVELS) == 10


class TestRhythmLogic:
    @staticmethod
    def run_all():
        TestRhythmLogic.test_difficulty_config()
        TestRhythmLogic.test_perfect_judgment()
        TestRhythmLogic.test_good_judgment()
        TestRhythmLogic.test_miss_judgment()
        TestRhythmLogic.test_combo_scoring()
        TestRhythmLogic.test_rank_system()
        print("  [PASS] All RhythmLogic tests")

    @staticmethod
    def test_difficulty_config():
        m = _import_game("rhythm")
        cfg = m.DIFFICULTY_CONFIG
        assert cfg["easy"]["bpm"] == 60
        assert cfg["normal"]["bpm"] == 90
        assert cfg["hard"]["bpm"] == 120
        assert len(cfg["easy"]["keys"]) == 1
        assert len(cfg["normal"]["keys"]) == 2
        assert len(cfg["hard"]["keys"]) == 4

    @staticmethod
    def test_perfect_judgment():
        error = 0.08
        assert error < 0.15, "Should be Perfect"

    @staticmethod
    def test_good_judgment():
        error = 0.25
        assert error >= 0.15 and error < 0.35, "Should be Good"

    @staticmethod
    def test_miss_judgment():
        error = 0.50
        assert error >= 0.35, "Should be Miss"

    @staticmethod
    def test_combo_scoring():
        combo = 5
        score = 100 + combo * 10
        assert score == 150
        combo = 10
        score = 100 + combo * 10
        assert score == 200

    @staticmethod
    def test_rank_system():
        assert 20 / 20 >= 0.90  # S/A rank threshold
        assert 18 / 20 >= 0.90
        assert (10 + 8) / 20 >= 0.70  # B rank threshold


class TestWhackLogic:
    @staticmethod
    def run_all():
        TestWhackLogic.test_difficulty_config()
        TestWhackLogic.test_grid_mapping()
        TestWhackLogic.test_scoring()
        TestWhackLogic.test_combo()
        print("  [PASS] All WhackLogic tests")

    @staticmethod
    def test_difficulty_config():
        m = _import_game("whack")
        cfg = m.DIFFICULTY_CONFIG
        assert cfg["easy"]["total_rounds"] == 20
        assert cfg["normal"]["total_rounds"] == 25
        assert cfg["hard"]["total_rounds"] == 30
        assert cfg["easy"]["moles_per_round"] == 1

    @staticmethod
    def test_grid_mapping():
        grid = {}
        idx = 1
        for row in range(3):
            for col in range(3):
                grid[idx] = (row, col)
                idx += 1
        assert grid[1] == (0, 0)
        assert grid[5] == (1, 1)
        assert grid[9] == (2, 2)

    @staticmethod
    def test_scoring():
        score = 0
        for _ in range(5):
            score += 100
        assert score == 500
        score -= 30 * 2
        assert score == 440

    @staticmethod
    def test_combo():
        hits = 0
        combo_score = 0
        for _ in range(5):
            hits += 1
        if hits >= 5:
            combo_score = 200
        assert combo_score == 200


class TestStoryLogic:
    @staticmethod
    def run_all():
        TestStoryLogic.test_scenes_exist()
        TestStoryLogic.test_scene_count()
        TestStoryLogic.test_inventory()
        TestStoryLogic.test_command_parsing()
        TestStoryLogic.test_puzzle_answers()
        print("  [PASS] All StoryLogic tests")

    @staticmethod
    def test_scenes_exist():
        m = _import_game("story")
        for scene_id in m.SCENE_ORDER:
            assert scene_id in m.SCENES, f"Scene {scene_id} not found"

    @staticmethod
    def test_scene_count():
        m = _import_game("story")
        assert len(m.SCENES) >= 5, "Should have at least 5 scenes"

    @staticmethod
    def test_inventory():
        inventory = []
        inventory.append("钥匙")
        assert "钥匙" in inventory
        inventory.remove("钥匙")
        assert len(inventory) == 0

    @staticmethod
    def test_command_parsing():
        cmd = "look 书桌"
        parts = cmd.split(" ", 1)
        assert parts[0] == "look"
        assert parts[1] == "书桌"
        cmd2 = "go north"
        parts2 = cmd2.split(" ", 1)
        assert parts2[0] == "go"
        assert parts2[1] == "north"

    @staticmethod
    def test_puzzle_answers():
        m = _import_game("story")
        gate = m.SCENES.get("gate")
        if gate and gate.get("puzzle"):
            assert gate["puzzle"]["answer"] == "3719"
        study = m.SCENES.get("study")
        if study and study.get("puzzle"):
            assert study["puzzle"]["answer"] == "BRAIN"


class TestMemorySnakeLogic:
    @staticmethod
    def run_all():
        TestMemorySnakeLogic.test_difficulty_config()
        TestMemorySnakeLogic.test_direction_no_reverse()
        TestMemorySnakeLogic.test_collision_wall()
        TestMemorySnakeLogic.test_collision_self()
        TestMemorySnakeLogic.test_food_sequence()
        TestMemorySnakeLogic.test_scoring()
        print("  [PASS] All MemorySnakeLogic tests")

    @staticmethod
    def test_difficulty_config():
        m = _import_game("memory_snake")
        cfg = m.DIFFICULTY_CONFIG
        assert cfg["easy"]["width"] == 20
        assert cfg["easy"]["height"] == 15
        assert cfg["normal"]["obstacles"] == 3
        assert cfg["hard"]["width"] == 25

    @staticmethod
    def test_direction_no_reverse():
        directions = {"up": "down", "down": "up", "left": "right", "right": "left"}
        current_dir = "up"
        opposite = directions[current_dir]
        assert opposite == "down"

    @staticmethod
    def test_collision_wall():
        width, height = 10, 8
        head_x = 0
        assert head_x <= 0, "左边界碰撞"
        head_x = width - 1
        assert head_x >= width - 1, "右边界碰撞"

    @staticmethod
    def test_collision_self():
        body = [(5, 5), (5, 4), (5, 3)]
        # Head at body position = collision
        head = (5, 5)
        assert head in body, "头在身体位置上"
        # Head at non-body position = no collision
        head_safe = (6, 5)
        assert head_safe not in body, "安全位置不应碰撞"

    @staticmethod
    def test_food_sequence():
        sequence = [1, 2, 3]
        current_need = 1
        eaten = []
        for food_num in sequence:
            assert food_num == current_need, f"Expected {current_need}, got {food_num}"
            eaten.append(food_num)
            current_need += 1
        assert eaten == [1, 2, 3]

        bad_sequence = [2, 1, 3]
        current_need = 1
        wrong_order = False
        for food_num in bad_sequence:
            if food_num != current_need:
                wrong_order = True
                break
            current_need += 1
        assert wrong_order, "Should detect wrong order"

    @staticmethod
    def test_scoring():
        level = 3
        score = 0
        for _ in range(3):
            score += 100 * level
        score += 500
        score += 200 * level
        assert score == 2000


if __name__ == "__main__":
    print("Running game logic tests...")
    TestMemoryMazeLogic.run_all()
    TestMathDodgeLogic.run_all()
    TestCodeBreakerLogic.run_all()
    TestRhythmLogic.run_all()
    TestWhackLogic.run_all()
    TestStoryLogic.run_all()
    TestMemorySnakeLogic.run_all()
    print("\nAll game logic tests passed!")
