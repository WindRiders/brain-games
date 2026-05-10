# Brain Games — 终端脑力训练合集

```
  _____ _             _     ____
 |  ___(_)_ __   __ _| |__ / ___|___  _ __ ___
 | |_  | | '_ \ / _` | '_ \ |   / _ \| '_ ` _ \
 |  _| | | | | | (_| | |_) | |__| (_) | | | | | |
 |_|   |_|_| |_|\__,_|_.__(_)____\___/|_| |_| |_|

        ★ 终 端 脑 力 训 练 合 集 ★
```

## 简介

Brain Games 是一款运行在终端中的脑力训练游戏合集，包含 **7 种不同类型的益智游戏**，专注于训练空间记忆、快速计算、逻辑推理、节奏感、反应速度、综合脑力和多任务处理能力。

- **纯终端体验**：无需图形界面，SSH 远程也可使用
- **零依赖**：仅使用 Python 标准库
- **跨平台**：支持 Linux / macOS / Windows (WSL)
- **三档难度**：简单 / 普通 / 困难

## 快速开始

```bash
# 确保 Python 3.8+
python3 --version

# 运行游戏
python3 main.py
```

## 游戏列表

| 编号 | 游戏 | 训练目标 | 操作 |
|------|------|---------|------|
| 1 | **记忆迷宫** | 空间记忆、路径规划 | WASD 移动 |
| 2 | **弹幕大脑** | 快速计算+反应 | A/D 移动躲避 |
| 3 | **密码破译** | 逻辑推理、模式识别 | 键盘输入答案 |
| 4 | **节奏大师** | 节奏感、专注力 | 空格/A/D/F/J/K |
| 5 | **打地鼠** | 视觉搜索、反应速度 | 数字键 1-9 |
| 6 | **故事解谜** | 综合脑力、阅读理解 | 文字命令 |
| 7 | **贪吃蛇记忆** | 多任务处理、空间记忆 | WASD 控制蛇 |

## 操作说明

### 主菜单
- `1-7`: 选择游戏
- `S`: 查看最高分
- `R`: 重置分数
- `Q`: 退出

### 游戏中通用
- `Q` / `Esc`: 退出当前游戏，返回主菜单
- `H`: 显示/隐藏帮助
- 各游戏具体操作见游戏内帮助

## 项目结构

```
brain-games/
├── main.py                    # 入口文件
├── docs/                      # 文档
│   ├── 01-产品文档.md
│   ├── 02-交互设计文档.md
│   ├── 03-UI设计文档.md
│   ├── 04-架构文档.md
│   ├── 05-开发文档.md
│   ├── 06-测试文档.md
│   └── 07-项目进度.md
├── src/
│   ├── engine/                # 游戏引擎核心
│   │   ├── base.py            # 游戏基类
│   │   ├── input.py           # 输入管理
│   │   ├── renderer.py        # 渲染引擎
│   │   └── timer.py           # 计时系统
│   ├── games/                 # 游戏实现
│   │   ├── maze.py            # G1: 记忆迷宫
│   │   ├── math_dodge.py      # G2: 弹幕大脑
│   │   ├── code_breaker.py    # G3: 密码破译
│   │   ├── rhythm.py          # G4: 节奏大师
│   │   ├── whack.py           # G5: 打地鼠
│   │   ├── story.py           # G6: 故事解谜
│   │   └── memory_snake.py    # G7: 贪吃蛇记忆
│   ├── ui/                    # UI组件
│   │   ├── colors.py          # 颜色常量
│   │   └── components.py      # 通用UI组件
│   └── utils/                 # 工具函数
│       ├── scoring.py         # 评分管理
│       ├── maze_gen.py        # 迷宫生成
│       └── crypto.py          # 加密/解密
├── tests/                     # 测试
│   ├── test_maze_gen.py
│   ├── test_crypto.py
│   └── test_scoring.py
├── README.md
└── requirements.txt
```

## 技术栈

- **语言**: Python 3.8+
- **依赖**: 无（纯标准库）
- **终端**: ANSI 转义序列
- **输入**: termios (Linux/macOS) / msvcrt (Windows)
- **测试**: pytest

## 开发

```bash
# 运行测试
python3 -m pytest tests/ -v

# 代码检查
python3 -m py_compile main.py
python3 -m py_compile src/**/*.py
```

## 许可证

MIT License | Copyright (c) 2026 [WindRiders](https://github.com/WindRiders)
