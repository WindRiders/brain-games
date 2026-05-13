#!/usr/bin/env python3
"""Brain Games — 终端脑力训练合集。

7款脑力训练游戏，纯Python标准库实现。
运行: python3 main.py
"""

import sys
import os
import time

# 确保项目根目录在 Python 路径中
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.engine.input import InputManager
from src.engine.renderer import Renderer
from src.utils.scoring import ScoreManager
from src.ui.colors import C
from src.ui.components import center, header, divider, box
from src.games import get_game_list, get_game_class, get_game_name


# ============================================================
# 主菜单
# ============================================================

def draw_main_menu(scores: ScoreManager) -> str:
    """绘制主菜单画面。"""
    lines = []
    lines.append("")
    lines.append(center(f"{C.BCYAN}{C.BOLD}  _____ _             _     ____    {C.RESET}", 55))
    lines.append(center(f"{C.BCYAN}{C.BOLD} |  ___(_)_ __   __ _| |__ / ___|   {C.RESET}", 55))
    lines.append(center(f"{C.BCYAN}{C.BOLD} | |_  | | '_ \\ / _` | '_ \\ |   / _ \\  {C.RESET}", 55))
    lines.append(center(f"{C.BCYAN}{C.BOLD} |  _| | | | | | (_| | |_) | |__| (_) | {C.RESET}", 55))
    lines.append(center(f"{C.BCYAN}{C.BOLD} |_|   |_|_| |_|\\__,_|_.__(_)____\\___/  {C.RESET}", 55))
    lines.append("")
    lines.append(center(f"{C.BYELLOW}{C.BOLD}★ 终 端 脑 力 训 练 合 集 ★{C.RESET}", 55))
    lines.append("")
    lines.append(divider(55))

    games = get_game_list()
    lines.append(f"  {C.BOLD}请选择游戏：{C.RESET}")
    lines.append("")

    for g in games:
        gid = g["id"]
        name = g["name"]
        desc = g["desc"]
        available = g["available"]
        if available:
            lines.append(f"  {C.BGREEN}[{gid}]{C.RESET} {name: <12} - {desc}")
        else:
            lines.append(f"  {C.DIM}[{gid}]{C.RESET} {C.DIM}{name: <12} - {desc} (未实现){C.RESET}")

    lines.append("")
    lines.append(f"  {C.BCYAN}[S]{C.RESET} 查看最高分    {C.BCYAN}[R]{C.RESET} 重置分数    {C.BCYAN}[Q]{C.RESET} 退出")
    lines.append(divider(55))
    lines.append("")

    return "\n".join(lines)


def draw_scores_menu(scores: ScoreManager) -> str:
    """显示最高分菜单。"""
    lines = []
    lines.append("")
    lines.append(center(f"{C.BYELLOW}{C.BOLD}★ 最 高 分 ★{C.RESET}", 55))
    lines.append("")
    lines.append(scores.show_all())
    lines.append("")
    lines.append(center(f"{C.DIM}按任意键返回主菜单...{C.RESET}", 55))
    lines.append("")
    return "\n".join(lines)


def draw_difficulty_menu(game_name: str) -> str:
    """显示难度选择菜单。"""
    lines = []
    lines.append("")
    lines.append(center(f"{C.BCYAN}{C.BOLD}{game_name}{C.RESET}", 55))
    lines.append("")
    lines.append(divider(55))
    lines.append(f"  {C.BOLD}选择难度：{C.RESET}")
    lines.append("")
    lines.append(f"  {C.BGREEN}[1]{C.RESET} 简单  — 入门体验")
    lines.append(f"  {C.BYELLOW}[2]{C.RESET} 普通  — 标准挑战")
    lines.append(f"  {C.BRED}[3]{C.RESET} 困难  — 极限脑力")
    lines.append("")
    lines.append(f"  {C.BCYAN}[Q]{C.RESET} 返回主菜单")
    lines.append(divider(55))
    lines.append("")
    return "\n".join(lines)


def draw_confirm(text: str) -> str:
    """显示确认提示。"""
    lines = []
    lines.append("")
    lines.append(center(text, 55))
    lines.append(center(f"{C.BGREEN}[Y]{C.RESET} 确认    {C.BRED}[N]{C.RESET} 取消", 55))
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 主循环
# ============================================================

DIFFICULTY_MAP = {"1": "easy", "2": "normal", "3": "hard"}
DIFFICULTY_NAMES = {"easy": "简单", "normal": "普通", "hard": "困难"}


def main():
    """主入口函数。"""
    renderer = Renderer()
    input_mgr = InputManager()
    scores = ScoreManager()

    input_mgr.init()
    renderer.hide_cursor()

    try:
        while True:
            # 显示主菜单
            menu_text = draw_main_menu(scores)
            renderer.render(menu_text)

            # 等待用户输入
            while True:
                key = input_mgr.get_key()
                key = key.lower()

                if key in ("q", "\x1b"):
                    # 退出程序
                    renderer.render(
                        center(f"\n{C.BCYAN}感谢游玩 Brain Games!{C.RESET}", 55)
                        + "\n"
                        + center(f"{C.DIM}再见!{C.RESET}", 55)
                        + "\n"
                    )
                    time.sleep(1)
                    return

                if key == "s":
                    # 查看最高分
                    score_text = draw_scores_menu(scores)
                    renderer.render(score_text)
                    input_mgr.get_key()  # 等待任意键
                    break

                if key == "r":
                    # 重置分数
                    confirm = draw_confirm("确定要重置所有分数吗？")
                    renderer.render(confirm)
                    confirm_key = input_mgr.get_key().lower()
                    if confirm_key == "y":
                        scores.reset()
                        renderer.render(
                            center(f"\n{C.BGREEN}分数已重置!{C.RESET}", 55) + "\n"
                        )
                        time.sleep(1)
                    break

                if key in ("1", "2", "3", "4", "5", "6", "7"):
                    game_id = int(key)
                    game_class = get_game_class(game_id)

                    if game_class is None:
                        renderer.render(
                            center(f"\n{C.BRED}该游戏暂未实现!{C.RESET}", 55) + "\n"
                            + center(f"{C.DIM}按任意键返回{C.RESET}", 55) + "\n"
                        )
                        input_mgr.get_key()
                        break

                    # 难度选择
                    game_name = get_game_name(game_id)
                    renderer.render(draw_difficulty_menu(game_name))

                    diff_key = input_mgr.get_key().lower()
                    if diff_key in ("q", "\x1b"):
                        break

                    difficulty = DIFFICULTY_MAP.get(diff_key)
                    if difficulty is None:
                        break

                    diff_name = DIFFICULTY_NAMES[difficulty]

                    # 启动游戏
                    game = game_class(
                        difficulty=difficulty,
                        renderer=renderer,
                        input_manager=input_mgr,
                        score_manager=scores,
                    )
                    game.name = game_name

                    try:
                        renderer.render(
                            center(f"\n{C.BCYAN}正在启动 {game_name} ({diff_name})...{C.RESET}", 55) + "\n"
                        )
                        time.sleep(0.5)
                        game.run()
                    except KeyboardInterrupt:
                        pass
                    except Exception as e:
                        renderer.show_cursor()
                        renderer.render(
                            center(f"\n{C.BRED}游戏出错: {e}{C.RESET}", 55) + "\n"
                            + center(f"{C.DIM}按任意键返回{C.RESET}", 55) + "\n"
                        )
                        input_mgr.get_key()

                    break

    finally:
        input_mgr.cleanup()
        renderer.show_cursor()


if __name__ == "__main__":
    import subprocess
    if len(sys.argv) > 1 and sys.argv[1] in ("-w", "--web"):
        # 启动 Web 版
        web_server = os.path.join(PROJECT_ROOT, "web", "server.py")
        print("🧠 启动 Brain Games Web 版...")
        subprocess.run([sys.executable, web_server])
    else:
        main()
