"""游戏注册模块"""

GAME_REGISTRY: dict = {}


def _get_registry() -> dict:
    """获取游戏注册表（延迟加载）"""
    global GAME_REGISTRY
    if GAME_REGISTRY:
        return GAME_REGISTRY

    registry = {}

    game_defs = [
        {
            "id": 1,
            "name": "记忆迷宫",
            "module": "maze",
            "class": "MemoryMazeGame",
            "desc": "短暂记忆迷宫布局，凭记忆走出去",
        },
        {
            "id": 2,
            "name": "弹幕大脑",
            "module": "math_dodge",
            "class": "MathDodgeGame",
            "desc": "躲避错误答案，触碰正确答案",
        },
        {
            "id": 3,
            "name": "密码破译",
            "module": "code_breaker",
            "class": "CodeBreakerGame",
            "desc": "破解层层加密的密码",
        },
        {
            "id": 4,
            "name": "节奏大师",
            "module": "rhythm",
            "class": "RhythmGame",
            "desc": "跟随节拍精准按键",
        },
        {
            "id": 5,
            "name": "打地鼠",
            "module": "whack",
            "class": "WhackAMoleGame",
            "desc": "快速反应击中目标",
        },
        {
            "id": 6,
            "name": "故事解谜",
            "module": "story",
            "class": "StoryPuzzleGame",
            "desc": "文字冒险解开谜题",
        },
        {
            "id": 7,
            "name": "贪吃蛇记忆",
            "module": "memory_snake",
            "class": "MemorySnakeGame",
            "desc": "按顺序吃食物的贪吃蛇",
        },
    ]

    for gdef in game_defs:
        entry = {
            "name": gdef["name"],
            "desc": gdef["desc"],
            "module": gdef["module"],
            "class_name": gdef["class"],
            "class": None,
        }
        try:
            mod = __import__(f"src.games.{gdef['module']}", fromlist=[gdef["class"]])
            entry["class"] = getattr(mod, gdef["class"])
        except (ImportError, AttributeError):
            pass

        registry[gdef["id"]] = entry

    GAME_REGISTRY = registry
    return registry


def get_game_list() -> list[dict]:
    """获取可玩游戏列表"""
    reg = _get_registry()
    result = []
    for idx in sorted(reg.keys()):
        info = reg[idx]
        available = info["class"] is not None
        result.append({
            "id": idx,
            "name": info["name"],
            "desc": info["desc"],
            "available": available,
        })
    return result


def get_game_class(game_id: int):
    """根据 ID 获取游戏类"""
    reg = _get_registry()
    entry = reg.get(game_id)
    if entry and entry["class"] is not None:
        return entry["class"]
    return None


def get_game_name(game_id: int) -> str:
    """根据 ID 获取游戏名称"""
    reg = _get_registry()
    entry = reg.get(game_id)
    return entry["name"] if entry else "未知游戏"
