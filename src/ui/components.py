"""通用UI组件函数"""

from . import colors


def center(text: str, width: int = 55) -> str:
    """将文本居中对齐到指定宽度"""
    # 移除ANSI转义序列计算可见长度
    import re
    visible = re.sub(r'\033\[[0-9;]*m', '', text)
    pad = max(0, (width - len(visible)) // 2)
    return " " * pad + text


def divider(width: int = 55, char: str = "─") -> str:
    """生成分隔线"""
    return char * width


def header(title: str, width: int = 55) -> str:
    """生成标题栏"""
    title_bar = f" {title} "
    pad = (width - len(title_bar)) // 2
    line = "═" * width
    top = f"╔{line}╗"
    mid = f"║{' ' * pad}{title_bar}{' ' * (width - len(title_bar) - pad)}║"
    bot = f"╚{line}╝"
    return f"{top}\n{mid}\n{bot}"


def box(title: str, content_lines: list[str], width: int = 55) -> str:
    """生成带边框的文本框"""
    inner_w = width - 2  # 减去左右边框
    lines = []

    # 顶部：左上角 + 标题线 + 右上角
    title_str = f" {title} "
    if len(title_str) >= inner_w:
        top_line = title_str[:inner_w]
    else:
        top_line = title_str + "─" * (inner_w - len(title_str))
    lines.append(f"┌{top_line}┐")

    # 内容行
    for line in content_lines:
        import re
        visible = re.sub(r'\033\[[0-9;]*m', '', line)
        if len(visible) > inner_w:
            # 如果内容过长，截断（考虑ANSI转义）
            lines.append(f"│{line[:inner_w]}│")
        else:
            pad = inner_w - len(visible)
            lines.append(f"│{line}{' ' * pad}│")

    # 底部
    lines.append(f"└{'─' * inner_w}┘")

    return "\n".join(lines)


def progress_bar(pct: float, width: int = 20) -> str:
    """生成进度条字符串

    Args:
        pct: 百分比 (0-100)
        width: 进度条宽度

    Returns:
        格式化的进度条字符串
    """
    pct = max(0, min(100, pct))
    filled = int(width * pct / 100)
    empty = width - filled

    bar = f"{colors.GREEN}{'█' * filled}{colors.RESET}"
    bar += f"{colors.WHITE}{'░' * empty}{colors.RESET}"
    return f"[{bar}] {pct:5.1f}%"
