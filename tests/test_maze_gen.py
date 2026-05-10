"""迷宫生成算法测试"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.utils.maze_gen import generate_maze, solve_maze


def test_maze_dimensions():
    """迷宫尺寸正确。"""
    for w, h in [(5, 5), (7, 7), (9, 9), (11, 11)]:
        maze = generate_maze(w, h)
        assert len(maze) == h, f"高度应为 {h}, 实际 {len(maze)}"
        assert all(len(row) == w for row in maze), f"宽度应为 {w}"
    print("  [PASS] test_maze_dimensions")


def test_maze_boundary_walls():
    """迷宫边界全是墙壁。"""
    maze = generate_maze(7, 7)
    for x in range(7):
        assert maze[0][x] == 1, "顶边应为墙"
        assert maze[6][x] == 1, "底边应为墙"
    for y in range(7):
        assert maze[y][0] == 1, "左边应为墙"
        assert maze[y][6] == 1, "右边应为墙"
    print("  [PASS] test_maze_boundary_walls")


def test_maze_has_start_end():
    """起点(1,1)和终点为通道。"""
    maze = generate_maze(7, 7)
    assert maze[1][1] == 0, "起点(1,1)应为通道"
    assert maze[5][5] == 0, "终点(5,5)应为通道"
    print("  [PASS] test_maze_has_start_end")


def test_maze_is_solvable():
    """迷宫有解（BFS验证）。"""
    for _ in range(10):
        maze = generate_maze(9, 9)
        path = solve_maze(maze, (1, 1), (7, 7))
        assert path is not None, "迷宫应有解"
        assert len(path) > 0, "路径不应为空"
        assert path[0] == (1, 1), "路径起点应为(1,1)"
        assert path[-1] == (7, 7), "路径终点应为(7,7)"
    print("  [PASS] test_maze_is_solvable")


def test_maze_all_passages_connected():
    """所有通道连通（flood fill验证）。"""
    maze = generate_maze(7, 7)
    # 从(1,1)开始 flood fill
    visited = set()
    stack = [(1, 1)]
    while stack:
        y, x = stack.pop()
        if (y, x) in visited:
            continue
        if y < 0 or y >= 7 or x < 0 or x >= 7:
            continue
        if maze[y][x] != 0:
            continue
        visited.add((y, x))
        stack.extend([(y-1, x), (y+1, x), (y, x-1), (y, x+1)])

    # 统计所有通道
    total_passages = sum(
        1 for y in range(7) for x in range(7) if maze[y][x] == 0
    )
    assert len(visited) == total_passages, f"所有通道应连通: {len(visited)} vs {total_passages}"
    print("  [PASS] test_maze_all_passages_connected")


def test_even_dimensions_adjusted():
    """偶数尺寸自动调整为奇数。"""
    maze = generate_maze(6, 6)
    assert len(maze) % 2 == 1, "高度应为奇数"
    assert all(len(row) % 2 == 1 for row in maze), "宽度应为奇数"
    print("  [PASS] test_even_dimensions_adjusted")


def test_maze_different_each_time():
    """每次生成不同迷宫（概率性测试）。"""
    mazes = set()
    for _ in range(5):
        maze = generate_maze(7, 7)
        mazes.add(tuple(tuple(row) for row in maze))
    # 至少有不同的（5次随机生成完全相同的概率极低）
    assert len(mazes) > 1, "应生成不同迷宫"
    print("  [PASS] test_maze_different_each_time")


if __name__ == "__main__":
    print("Running maze generation tests...")
    test_maze_dimensions()
    test_maze_boundary_walls()
    test_maze_has_start_end()
    test_maze_is_solvable()
    test_maze_all_passages_connected()
    test_even_dimensions_adjusted()
    test_maze_different_each_time()
    print("\nAll maze tests passed!")
