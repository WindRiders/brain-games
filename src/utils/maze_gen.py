"""迷宫生成与求解"""

import random
from collections import deque


def generate_maze(width: int, height: int) -> list[list[int]]:
    """生成迷宫

    使用递归回溯（深度优先）算法。

    Args:
        width: 迷宫宽度（必须为奇数）
        height: 迷宫高度（必须为奇数）

    Returns:
        二维列表，0=通道，1=墙壁
    """
    if width % 2 == 0:
        width += 1
    if height % 2 == 0:
        height += 1

    # 初始化全部为墙壁
    maze = [[1] * width for _ in range(height)]

    def _carve(x: int, y: int):
        """递归 carving"""
        maze[y][x] = 0
        # 四个方向 (步长为2)
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            # 检查边界
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                if maze[ny][nx] == 1:
                    # 打通中间的墙
                    maze[y + dy // 2][x + dx // 2] = 0
                    _carve(nx, ny)

    # 从 (1, 1) 开始 carving
    _carve(1, 1)

    return maze


def solve_maze(
    maze: list[list[int]], start: tuple[int, int], end: tuple[int, int]
) -> list[tuple[int, int]]:
    """用 BFS 求解迷宫最短路径

    Args:
        maze: 迷宫二维列表 (0=通道, 1=墙壁)
        start: 起点 (x, y)
        end: 终点 (x, y)

    Returns:
        路径坐标列表，无解则返回空列表
    """
    height = len(maze)
    width = len(maze[0]) if height > 0 else 0

    sx, sy = start
    ex, ey = end

    # BFS
    queue: deque[tuple[int, int, list[tuple[int, int]]]] = deque()
    queue.append((sx, sy, [(sx, sy)]))
    visited: set[tuple[int, int]] = {(sx, sy)}

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        x, y, path = queue.popleft()

        if (x, y) == (ex, ey):
            return path

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < width
                and 0 <= ny < height
                and maze[ny][nx] == 0
                and (nx, ny) not in visited
            ):
                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))

    return []  # 无解
