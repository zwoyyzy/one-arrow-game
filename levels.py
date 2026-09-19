# 当前阶段先使用第一关测试棋盘和箭头绘制。
# 后续会继续设计并验证三个正式关卡。

LEVELS = [
    {
        "name": "第 1 关",
        "rows": 5,
        "cols": 5,
        "max_mistakes": 3,
        "arrows": [
            (0, 0, "right"),
            (0, 4, "down"),
            (1, 2, "left"),
            (2, 0, "up"),
            (2, 3, "right"),
            (3, 1, "down"),
            (4, 2, "up"),
            (4, 4, "left"),
        ],
    },
]