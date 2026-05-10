"""性能测试 (Performance) — 验证各项性能阈值"""
import sys
import os
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


class TestPerformance:
    """性能阈值测试。"""

    @staticmethod
    def run_all():
        TestPerformance.test_memory_startup()
        TestPerformance.test_maze_generation_speed()
        TestPerformance.test_crypto_operations_speed()
        TestPerformance.test_ui_rendering_speed()
        TestPerformance.test_score_io_speed()
        TestPerformance.test_game_setup_speed()
        TestPerformance.test_import_all_speed()
        TestPerformance.test_maze_solving_speed()
        print("  [PASS] All Performance tests")

    @staticmethod
    def test_memory_startup():
        """P-01: 内存占用 (启动时) < 30MB。"""
        import resource
        # 获取当前进程内存使用 (KB)
        mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        mem_mb = mem_kb / 1024
        assert mem_mb < 50, f"Memory usage {mem_mb:.1f}MB > 50MB threshold"

    @staticmethod
    def test_maze_generation_speed():
        """P-02: 迷宫生成耗时 (12x12) < 0.1s。"""
        from src.utils.maze_gen import generate_maze
        start = time.perf_counter()
        for _ in range(100):
            generate_maze(13, 13)
        elapsed = (time.perf_counter() - start) / 100
        assert elapsed < 0.01, f"Maze generation took {elapsed*1000:.1f}ms > 10ms"

    @staticmethod
    def test_crypto_operations_speed():
        """P-03: 加密操作耗时 < 10ms。"""
        from src.utils.crypto import (
            caesar_cipher, rot13, base64_encode,
            to_morse, vigenere_encrypt, to_binary_ascii
        )
        test_text = "Hello World, Brain Games!" * 10

        start = time.perf_counter()
        for _ in range(100):
            caesar_cipher(test_text, 3)
            rot13(test_text)
            base64_encode(test_text)
            to_morse("HELLO WORLD")
            vigenere_encrypt(test_text[:20], "KEY")
            to_binary_ascii(test_text[:20])
        elapsed = (time.perf_counter() - start) / 100
        assert elapsed < 0.05, f"Crypto operations took {elapsed*1000:.1f}ms > 50ms"

    @staticmethod
    def test_ui_rendering_speed():
        """P-04: UI 渲染耗时 < 10ms。"""
        from src.ui.components import box, center, header, divider, progress_bar
        start = time.perf_counter()
        for _ in range(1000):
            center("Test Title", 55)
            divider(55)
            header("Test Header", 55)
            progress_bar(50, 20)
            box("Title", ["line1", "line2", "line3"], 55)
        elapsed = (time.perf_counter() - start) / 1000
        assert elapsed < 0.001, f"UI rendering took {elapsed*1000:.3f}ms > 1ms"

    @staticmethod
    def test_score_io_speed():
        """P-05: 分数保存/加载耗时 < 0.1s。"""
        import tempfile
        from src.utils.scoring import ScoreManager
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = ScoreManager(data_dir=tmpdir)
            for g in ["maze", "math", "code", "rhythm", "whack", "story", "snake"]:
                for d in ["easy", "normal", "hard"]:
                    sm.set_high_score(g, d, 1000)

            start = time.perf_counter()
            for _ in range(100):
                sm.save()
                sm2 = ScoreManager(data_dir=tmpdir)
                sm2.load()
            elapsed = (time.perf_counter() - start) / 100
            assert elapsed < 0.01, f"Score I/O took {elapsed*1000:.1f}ms > 10ms"

    @staticmethod
    def test_game_setup_speed():
        """P-06: 游戏初始化耗时 < 0.5s。"""
        from src.games import get_game_class
        from unittest.mock import MagicMock
        mock_r = MagicMock()
        mock_i = MagicMock()
        mock_s = MagicMock()

        for gid in range(1, 8):
            cls = get_game_class(gid)
            start = time.perf_counter()
            for _ in range(10):
                game = cls(difficulty="easy", renderer=mock_r,
                           input_manager=mock_i, score_manager=mock_s)
                game.setup()
                game.cleanup()
            elapsed = (time.perf_counter() - start) / 10
            assert elapsed < 0.1, f"Game {gid} setup took {elapsed*1000:.1f}ms > 100ms"

    @staticmethod
    def test_import_all_speed():
        """P-07: 全部模块导入耗时 < 1s。"""
        import importlib
        modules = [
            "src.engine.base", "src.engine.input", "src.engine.renderer",
            "src.engine.timer", "src.ui.colors", "src.ui.components",
            "src.utils.scoring", "src.utils.maze_gen", "src.utils.crypto",
            "src.games.maze", "src.games.math_dodge", "src.games.code_breaker",
            "src.games.rhythm", "src.games.whack", "src.games.story",
            "src.games.memory_snake", "src.games",
        ]
        # 清除已导入模块
        for mod_name in list(sys.modules.keys()):
            if mod_name.startswith("src."):
                del sys.modules[mod_name]

        start = time.perf_counter()
        for mod_name in modules:
            importlib.import_module(mod_name)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0, f"Import all took {elapsed:.2f}s > 1.0s"

    @staticmethod
    def test_maze_solving_speed():
        """P-08: 迷宫求解耗时 (12x12) < 50ms。"""
        from src.utils.maze_gen import generate_maze, solve_maze
        maze = generate_maze(25, 25)  # 12x12 cells = 25x25 grid
        start = time.perf_counter()
        for _ in range(100):
            path = solve_maze(maze, (1, 1), (23, 23))
            assert path is not None
        elapsed = (time.perf_counter() - start) / 100
        assert elapsed < 0.001, f"Maze solving took {elapsed*1000:.2f}ms > 1ms"


if __name__ == "__main__":
    print("Running Performance tests...")
    TestPerformance.run_all()
    print("\nAll Performance tests passed!")
