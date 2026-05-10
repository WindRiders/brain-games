"""G6 故事解谜游戏 — 文字冒险解开谜题"""

import time
import textwrap
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.base import BaseGame
from src.ui import colors as C
from src.ui.components import box, center, header, divider, progress_bar
from src.engine.timer import GameTimer

# 补充 colors.py 中没有的颜色
DIM = "\033[2m"  # 暗色/灰色

BOX_WIDTH = 52
WRAP_WIDTH = 50


def wrap_text(text: str, width: int = WRAP_WIDTH) -> list[str]:
    """自动换行文本"""
    import re
    # 先移除 ANSI 转义序列来计算长度
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    if len(clean) <= width:
        return [text]

    lines = []
    # 简单换行：按空格分割
    words = text.split(' ')
    current = ""
    current_len = 0

    for word in words:
        word_clean = re.sub(r'\033\[[0-9;]*m', '', word)
        wlen = len(word_clean)
        if current_len + wlen + (1 if current else 0) <= width:
            if current:
                current += " " + word
            else:
                current = word
            current_len += wlen + (1 if current_len > 0 else 0)
        else:
            lines.append(current)
            current = word
            current_len = wlen

    if current:
        lines.append(current)

    return lines


# ── 场景数据 ──────────────────────────────────────────────────
SCENES = {
    "gate": {
        "id": "gate",
        "title": "庄园大门",
        "description": (
            "你站在一座古老庄园的大门前。铁艺大门上"
            "布满锈迹，门柱上有一个密码锁。门牌号隐"
            "约可见：「3-7-1-9」。大门紧锁，似乎需"
            "要输入密码才能打开。"
        ),
        "items": [
            {"name": "门牌号", "description": "门柱上刻着数字：3-7-1-9", "takeable": False},
        ],
        "exits": {"south": "gate_outside", "north": "hall"},
        "puzzle": {
            "type": "password",
            "question": "密码锁上写着「请输入四位数字密码」",
            "answer": "3719",
            "hint": "看看门柱上有什么线索...",
        },
        "required_items": [],
        "locked": True,  # 初始锁住
    },
    "hall": {
        "id": "hall",
        "title": "大厅",
        "description": (
            "你进入了庄园大厅。高高的天花板上悬挂着"
            "一盏水晶吊灯，房间中央有一张书桌，桌上"
            "散落着一些信件。左侧是一个大书架，上面"
            "摆满了旧书。角落里有一个锁着的抽屉柜。"
        ),
        "items": [
            {"name": "旧信件", "description": "一封泛黄的信，上面写着：'信在钟楼之巅'", "takeable": True},
            {"name": "钥匙串", "description": "一串铜钥匙，其中一把刻着'书房'", "takeable": False},  # 需要先找到
            {"name": "书桌", "description": "一张橡木书桌，抽屉已经空了。", "takeable": False},
            {"name": "书架", "description": "书架上有一排书，书脊上的字母拼起来似乎是个词。", "takeable": False},
        ],
        "exits": {"south": "gate", "east": "study", "west": "corridor"},
        "puzzle": {
            "type": "find_item",
            "question": "你需要找到一把能打开抽屉柜的钥匙。",
            "answer": "旧信件",
            "hint": "仔细搜索房间的每个角落...",
        },
        "required_items": [],
    },
    "study": {
        "id": "study",
        "title": "书房",
        "description": (
            "书房里弥漫着旧纸张的味道。房间中央有一"
            "个大书架，书架上有一排特别显眼的书，书"
            "脊上分别写着字母。墙上挂着一幅画，画中"
            "是一座钟楼。"
        ),
        "items": [
            {"name": "字母书B", "description": "一本蓝色封面的书，书脊上写着'B'", "takeable": False},
            {"name": "字母书R", "description": "一本红色封面的书，书脊上写着'R'", "takeable": False},
            {"name": "字母书A", "description": "一本绿色封面的书，书脊上写着'A'", "takeable": False},
            {"name": "字母书I", "description": "一本紫色封面的书，书脊上写着'I'", "takeable": False},
            {"name": "字母书N", "description": "一本橙色封面的书，书脊上写着'N'", "takeable": False},
        ],
        "exits": {"west": "hall"},
        "puzzle": {
            "type": "word",
            "question": "书架上的书脊字母可以组成一个单词。请按照正确顺序排列它们。",
            "answer": "BRAIN",
            "hint": "想想这些字母能拼出什么有意义的英文单词...",
        },
        "required_items": [],
    },
    "corridor": {
        "id": "corridor",
        "title": "走廊",
        "description": (
            "一条长长的走廊，两侧是画像。走廊尽头有"
            "三名守卫站成一排。墙壁上有一块告示牌。"
            "走廊通向钟楼。"
        ),
        "items": [
            {"name": "告示牌", "description": "告示牌上写着：'三人中只有一人说真话'", "takeable": False},
        ],
        "exits": {"east": "hall", "north": "clocktower"},
        "puzzle": {
            "type": "logic",
            "question": (
                "三个守卫的供词：\n"
                "  守卫甲说：'乙在说谎'\n"
                "  守卫乙说：'丙在说谎'\n"
                "  守卫丙说：'甲和乙都在说谎'\n"
                "  已知只有一人说真话，谁说真话？"
            ),
            "answer": "乙",
            "hint": "假设每个人说真话，看看是否矛盾...",
        },
        "required_items": [],
    },
    "clocktower": {
        "id": "clocktower",
        "title": "钟楼",
        "description": (
            "你登上了钟楼。巨大的钟摆在头顶摆动，发"
            "出沉重的滴答声。钟楼顶部的壁龛中放着一"
            "个古老的盒子。盒子上有两个锁：一个需要"
            "密码，一个需要单词。"
        ),
        "items": [
            {"name": "古老盒子", "description": "一个精美的木盒，上面有两个锁。", "takeable": False},
        ],
        "exits": {"south": "corridor"},
        "puzzle": {
            "type": "password",
            "question": (
                "盒子上的第一个锁需要四位数字密码。\n"
                "提示：想想你在大门上看到的数字。"
            ),
            "answer": "3719",
            "hint": "还记得庄园大门的门牌号吗？",
        },
        "required_items": ["旧信件"],
    },
}

# 场景顺序ID
SCENE_ORDER = ["gate", "hall", "study", "corridor", "clocktower"]

# 场景 emoji
SCENE_EMOJI = {
    "gate": "🚪",
    "hall": "🏛️",
    "study": "📚",
    "corridor": "🏰",
    "clocktower": "🕰️",
}

# 方向中文名
DIR_CN = {
    "north": "北",
    "south": "南",
    "east": "东",
    "west": "西",
}


# ═══════════════════════════════════════════════════════════════
#  StoryPuzzleGame 类
# ═══════════════════════════════════════════════════════════════
class StoryPuzzleGame(BaseGame):
    """故事解谜游戏 — 第一章：消失的信"""

    WIDTH = 55

    def __init__(self, difficulty, renderer, input_manager, score_manager):
        super().__init__(difficulty, renderer, input_manager, score_manager)
        self.name = "故事解谜"

    def setup(self):
        import copy
        # 深拷贝场景数据避免修改原始数据
        self._scenes = {}
        for sid, sdata in SCENES.items():
            self._scenes[sid] = copy.deepcopy(sdata)
            # 添加运行时状态
            self._scenes[sid]["_items_taken"] = set()
            self._scenes[sid]["_puzzle_solved"] = False

        self.score = 0
        self.inventory = []
        self.visited_scenes = set()
        self.current_scene = "gate"
        self._game_over = False
        self._won = False
        self._hint_used = False
        self._total_hints = 0
        self._puzzles_solved = 0
        self._message = ""
        self._message_color = ""
        self._timer = GameTimer()
        self._timer.start()
        self._input_buffer = ""
        self._awaiting_input = False
        self._input_label = ""
        self._pending_callback = None  # (type, callback)

    def _get_scene(self) -> dict:
        """获取当前场景数据"""
        return self._scenes.get(self.current_scene, {})

    def _get_scene_index(self) -> int:
        """获取当前场景在顺序中的索引"""
        try:
            return SCENE_ORDER.index(self.current_scene)
        except ValueError:
            return 0

    def _is_scene_locked(self, scene_id: str) -> bool:
        """检查场景是否锁住"""
        scene = self._scenes.get(scene_id, {})
        if not scene.get("required_items"):
            return False
        # 检查背包中是否有需要的物品
        for item in scene["required_items"]:
            if item not in self.inventory:
                return True
        return False

    def _render_scene(self) -> list[str]:
        """渲染当前场景"""
        lines = []
        scene = self._get_scene()
        title = scene.get("title", "未知场景")
        idx = self._get_scene_index()

        # 标题栏
        lines.append(f"  {C.BOLD}{'═' * BOX_WIDTH}{C.RESET}")
        lines.append(center(f"{C.BCYAN}故事解谜 — 第一章：消失的信{C.RESET}", BOX_WIDTH))
        lines.append(center(f"{C.BWHITE}场景 {idx + 1}/{len(SCENE_ORDER)}：{title}{C.RESET}", BOX_WIDTH))
        lines.append(f"  {C.BOLD}{'═' * BOX_WIDTH}{C.RESET}")
        lines.append("")

        # 场景描述（自动换行）
        desc = scene.get("description", "")
        wrapped = wrap_text(desc, WRAP_WIDTH)
        for wline in wrapped:
            lines.append(f"  {wline}")
        lines.append("")

        # 物品列表
        items = scene.get("items", [])
        if items:
            lines.append(f"  {C.BYELLOW}你注意到:{C.RESET}")
            for item in items:
                iname = item["name"]
                # 检查物品是否已被拾取
                if item.get("takeable") and iname in self._get_scene()["_items_taken"]:
                    lines.append(f"    {DIM}- {iname} (已拾取){C.RESET}")
                else:
                    lines.append(f"    {C.BGREEN}- {iname}{C.RESET}")
            lines.append("")

        # 出口信息
        exits = scene.get("exits", {})
        if exits:
            exit_strs = []
            for d, target in exits.items():
                dcn = DIR_CN.get(d, d)
                locked = self._is_scene_locked(target)
                if locked:
                    exit_strs.append(f"{C.RED}{dcn}(锁住){C.RESET}")
                else:
                    exit_strs.append(f"{C.BCYAN}{dcn}{C.RESET}")
            lines.append(f"  {C.BOLD}出口: {', '.join(exit_strs)}{C.RESET}")
            lines.append("")

        # 谜题状态
        puzzle = scene.get("puzzle")
        if puzzle and not scene["_puzzle_solved"]:
            lines.append(f"  {C.BMAGENTA}🧩 谜题: {puzzle['question']}{C.RESET}")
            lines.append("")

        # 背包
        if self.inventory:
            lines.append(f"  {C.BOLD}┌─ 你的物品 {'─' * (BOX_WIDTH - 10)}┐{C.RESET}")
            for item_name in self.inventory:
                lines.append(f"  {C.BOLD}│{C.RESET}  🎒 {item_name}")
            lines.append(f"  {C.BOLD}└{'─' * (BOX_WIDTH - 1)}┘{C.RESET}")
        else:
            lines.append(f"  {C.BOLD}┌─ 你的物品 {'─' * (BOX_WIDTH - 10)}┐{C.RESET}")
            lines.append(f"  {C.BOLD}│{C.RESET}  (空)")
            lines.append(f"  {C.BOLD}└{'─' * (BOX_WIDTH - 1)}┘{C.RESET}")

        lines.append("")

        # 消息
        if self._message:
            lines.append(f"  {self._message_color}{self._message}{C.RESET}")
            lines.append("")

        # 输入提示
        if self._awaiting_input:
            lines.append(f"  {C.BWHITE}{self._input_label}{C.RESET} > {self._input_buffer}█")
        else:
            lines.append(f"  {C.BWHITE}你要做什么？{C.RESET} > █")

        return lines

    def _process_command(self, cmd: str) -> bool:
        """处理玩家命令。返回 True 继续游戏"""
        self._message = ""
        self._message_color = ""
        cmd = cmd.strip().lower()

        if not cmd:
            return True

        if cmd in ("q", "quit", "退出"):
            self._game_over = True
            return False

        if cmd in ("h", "help", "帮助"):
            self._show_help_inline()
            return True

        if cmd in ("inventory", "inv", "背包"):
            if self.inventory:
                self._message = "背包: " + ", ".join(self.inventory)
            else:
                self._message = "背包是空的"
            self._message_color = C.BCYAN
            return True

        if cmd.startswith("look"):
            self._cmd_look(cmd)
            return True

        if cmd.startswith("take"):
            self._cmd_take(cmd)
            return True

        if cmd.startswith("use"):
            self._cmd_use(cmd)
            return True

        if cmd.startswith("go") or cmd.startswith(("north", "south", "east", "west", "n", "s", "e", "w")):
            return self._cmd_go(cmd)

        if cmd.startswith("solve"):
            return self._cmd_solve(cmd)

        # 未知命令
        self._message = "未知命令。输入 'help' 查看帮助。"
        self._message_color = C.BYELLOW
        return True

    def _cmd_look(self, cmd: str):
        """查看命令"""
        parts = cmd.split(None, 1)
        scene = self._get_scene()

        if len(parts) < 2:
            # 查看整个场景
            self._message = scene.get("description", "")
            self._message_color = C.WHITE
            return

        target = parts[1].lower()

        # 搜索场景中的物品
        for item in scene.get("items", []):
            if item["name"].lower() == target:
                if item.get("takeable") and item["name"] in self._get_scene()["_items_taken"]:
                    self._message = f"你已经拾取了 {item['name']}。"
                else:
                    self._message = item["description"]
                self._message_color = C.WHITE
                return

        # 搜索背包
        for inv_item in self.inventory:
            if inv_item.lower() == target:
                self._message = f"你背包里的 {inv_item}。"
                self._message_color = C.WHITE
                return

        self._message = f"这里没有 {target}。"
        self._message_color = C.BYELLOW

    def _cmd_take(self, cmd: str):
        """拾取命令"""
        parts = cmd.split(None, 1)
        if len(parts) < 2:
            self._message = "用法: take <物品名>"
            self._message_color = C.BYELLOW
            return

        target = parts[1].lower()
        scene = self._get_scene()

        for item in scene.get("items", []):
            if item["name"].lower() == target:
                if not item.get("takeable", False):
                    self._message = f"{item['name']} 无法拾取。"
                    self._message_color = C.BYELLOW
                    return
                if item["name"] in self._get_scene()["_items_taken"]:
                    self._message = f"你已经拾取了 {item['name']}。"
                    self._message_color = C.BYELLOW
                    return

                self.inventory.append(item["name"])
                self._get_scene()["_items_taken"].add(item["name"])
                self._message = f"你拾取了 {item['name']}！"
                self._message_color = C.BGREEN
                return

        self._message = f"这里没有 {target}。"
        self._message_color = C.BYELLOW

    def _cmd_use(self, cmd: str):
        """使用命令"""
        parts = cmd.split(None, 1)
        if len(parts) < 2:
            self._message = "用法: use <物品名>"
            self._message_color = C.BYELLOW
            return

        target = parts[1].lower()

        if target not in [i.lower() for i in self.inventory]:
            self._message = f"你没有 {target}。"
            self._message_color = C.BYELLOW
            return

        self._message = f"你使用了 {target}，但似乎没有什么特别的效果。"
        self._message_color = C.WHITE

    def _cmd_go(self, cmd: str) -> bool:
        """移动命令"""
        parts = cmd.split()
        if cmd.startswith("go "):
            if len(parts) < 2:
                self._message = "用法: go <方向> (north/south/east/west)"
                self._message_color = C.BYELLOW
                return True
            direction = parts[1].lower()
        else:
            direction = cmd.split()[0].lower()

        # 映射
        dir_map = {
            "n": "north", "north": "north", "北": "north",
            "s": "south", "south": "south", "南": "south",
            "e": "east", "east": "east", "东": "east",
            "w": "west", "west": "west", "西": "west",
        }
        direction = dir_map.get(direction, direction)

        scene = self._get_scene()
        exits = scene.get("exits", {})

        if direction not in exits:
            self._message = f"不能往 {DIR_CN.get(direction, direction)} 走。"
            self._message_color = C.BYELLOW
            return True

        target_id = exits[direction]

        # 检查是否锁住
        if self._is_scene_locked(target_id):
            target_scene = self._scenes.get(target_id, {})
            needed = target_scene.get("required_items", [])
            self._message = f"需要 {' 和 '.join(needed)} 才能进入！"
            self._message_color = C.BRED
            return True

        self.current_scene = target_id
        self.visited_scenes.add(target_id)
        self._message = f"你来到了 {SCENE_EMOJI.get(target_id, '')} {self._scenes[target_id]['title']}。"
        self._message_color = C.BCYAN
        return True

    def _cmd_solve(self, cmd: str) -> bool:
        """解谜命令"""
        parts = cmd.split(None, 1)
        if len(parts) < 2:
            self._message = "用法: solve <答案>"
            self._message_color = C.BYELLOW
            return True

        scene = self._get_scene()
        puzzle = scene.get("puzzle")

        if not puzzle:
            self._message = "这里没有谜题需要解决。"
            self._message_color = C.BYELLOW
            return True

        if scene["_puzzle_solved"]:
            self._message = "这个谜题已经解决了。"
            self._message_color = C.BYELLOW
            return True

        answer = parts[1].strip().lower()
        correct_answer = puzzle["answer"].strip().lower()

        if answer == correct_answer:
            scene["_puzzle_solved"] = True
            self._puzzles_solved += 1
            self._message = f"🎉 正确！谜题解开了！"
            self._message_color = C.BGREEN

            # 解锁大门
            if self.current_scene == "gate":
                self._scenes["gate"]["locked"] = False
                self._message = f"🎉 正确！大门打开了！"

            return True
        else:
            self._message = f"答案不正确。试试 'hint' 获取提示。"
            self._message_color = C.BRED
            return True

    def _show_help_inline(self):
        """显示内联帮助"""
        self._message = (
            "命令: look [物体] | take [物品] | use [物品] | "
            "go [方向] | solve [答案] | inventory | hint | help | quit"
        )
        self._message_color = C.BYELLOW

    def _cmd_hint(self):
        """提示命令"""
        scene = self._get_scene()
        puzzle = scene.get("puzzle")

        if not puzzle:
            self._message = "这里没有谜题。"
            self._message_color = C.BYELLOW
            return

        if scene["_puzzle_solved"]:
            self._message = "谜题已经解决。"
            self._message_color = C.BYELLOW
            return

        self._hint_used = True
        self._total_hints += 1
        self.score -= 100
        self._message = f"💡 提示: {puzzle.get('hint', '无')}  (使用提示 -100分)"
        self._message_color = C.BYELLOW

    def handle_input(self, key):
        if key is None:
            return True

        if key == "q":
            self._game_over = True
            return False

        # 处理输入
        if self._awaiting_input:
            if key == "\r" or key == "\n":
                cmd = self._input_buffer
                self._input_buffer = ""
                self._awaiting_input = False

                if cmd.lower() in ("hint", "提示", "h"):
                    self._cmd_hint()
                    return True

                return self._process_command(cmd)

            elif key == "\x7f" or key == "\x08":  # Backspace
                self._input_buffer = self._input_buffer[:-1]
            elif key == "h" and not self._input_buffer:
                self._show_help_inline()
            elif len(key) == 1 and key.isprintable():
                self._input_buffer += key
            return True

        return True

    def update(self):
        if self._game_over:
            return

        # 检查所有谜题是否都解决了
        all_solved = True
        for sid in SCENE_ORDER:
            scene = self._scenes[sid]
            if scene.get("puzzle") and not scene["_puzzle_solved"]:
                all_solved = False
                break

        if all_solved and self._puzzles_solved >= 5:
            self._game_over = True
            self._won = True

    def render(self):
        lines = self._render_scene()

        # 底部操作提示
        lines.append("")
        lines.append(f"  {DIM}[look/take/go/solve/inventory/hint/quit]{C.RESET}")

        self._renderer.render_frame(lines)

    def game_loop(self):
        self.visited_scenes.add(self.current_scene)

        while not self._game_over:
            # 确保处于输入模式
            if not self._awaiting_input:
                self._awaiting_input = True
                self._input_label = "你要做什么？"
                self._input_buffer = ""

            key = self._input_manager.get_key_nonblocking()
            if key is not None:
                if not self.handle_input(key):
                    break

            self.update()
            self.render()
            time.sleep(0.05)

        # 计算最终分数
        self._calculate_final_score()

        # 游戏结束画面
        self._render_final()
        print("\n  ", end="")
        self._input_manager.get_key()

    def _calculate_final_score(self):
        """计算最终分数"""
        if not self._won:
            return

        # 章节通关 +500
        self.score += 500

        # 无提示通关 +1000
        if not self._hint_used:
            self.score += 1000

        # 用时<15分钟 +300
        elapsed = self._timer.get_elapsed()
        if elapsed < 900:  # 15分钟 = 900秒
            self.score += 300

    def _render_final(self):
        lines = []
        lines.append("")
        lines.append(header(" 故事解谜 — 第一章：消失的信 "))
        lines.append("")

        if self._won:
            lines.append(center(f"{C.BGREEN}🎉 恭喜！你成功解开了所有谜题！{C.RESET}", self.WIDTH))
            lines.append("")
            lines.append(center(f"{C.BWHITE}你找到了消失的信件，揭开了庄园的秘密。{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"{C.RED}游戏结束{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{C.BOLD}{C.BGREEN}最终得分: {self.score}{C.RESET}", self.WIDTH))
        lines.append(center(f"{C.BYELLOW}解谜数: {self._puzzles_solved}/{len(SCENE_ORDER)}{C.RESET}", self.WIDTH))
        lines.append(center(f"用时: {self._timer.format_time()}", self.WIDTH))
        lines.append(center(f"提示使用: {self._total_hints} 次", self.WIDTH))
        lines.append("")

        high = self._score_manager.get_high_score(self.name, self.difficulty)
        new_high = self._score_manager.set_high_score(self.name, self.difficulty, self.score)
        if new_high:
            lines.append(center(f"{C.BYELLOW}🏆 新纪录！{C.RESET}", self.WIDTH))
        else:
            lines.append(center(f"历史最高: {C.BYELLOW}{high}{C.RESET}", self.WIDTH))

        lines.append("")
        lines.append(center(f"{DIM}按任意键返回主菜单...{C.RESET}", self.WIDTH))

        self._renderer.render_frame(lines)

    def show_help(self) -> str:
        diff_name = {"easy": "简单", "normal": "普通", "hard": "困难"}.get(self.difficulty, self.difficulty)
        return (
            f"\n  {C.BOLD}{C.BCYAN}═══ {self.name} — {diff_name}难度 ═══{C.RESET}\n"
            f"\n  第一章：消失的信\n"
            f"  探索庄园，解开谜题，找到消失的信件！\n"
            f"\n  {C.BWHITE}可用命令:{C.RESET}\n"
            f"    look [物体]  - 查看物体\n"
            f"    take [物品]  - 拾取物品\n"
            f"    use [物品]   - 使用物品\n"
            f"    go [方向]    - 移动(north/south/east/west)\n"
            f"    solve [答案] - 提交谜题答案\n"
            f"    inventory    - 查看背包\n"
            f"    hint         - 获取提示(-100分)\n"
            f"    help         - 显示帮助\n"
            f"    quit         - 退出游戏\n"
            f"\n  {C.BGREEN}通关 +500  无提示 +1000  用时<15min +300\n"
            f"  {C.BYELLOW}使用提示 -100/次{C.RESET}\n"
            f"  操作: [Q]退出  [H]帮助\n"
        )
