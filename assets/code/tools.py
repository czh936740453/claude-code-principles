"""
tools.py —— 工具系统的迷你实现（配合第 4 章）

核心思想：工具 = 一个名字 + 一段说明 + 一个函数。
代理拿到模型的 tool_use 请求后，查表 -> 校验参数 -> 执行 -> 返回结果。

用法:
    python tools.py
"""
from __future__ import annotations


class Tool:
    """一个工具：名字、用途说明、参数说明、真正的函数。"""

    def __init__(self, name: str, description: str, func, params: dict):
        self.name = name
        self.description = description      # 给模型看的说明
        self.func = func                    # 真正执行的函数
        self.params = params                # 参数说明（真实场景是 JSON Schema）

    def run(self, **kwargs):
        # 参数校验：只允许声明过的参数，防止乱传
        unknown = set(kwargs) - set(self.params)
        if unknown:
            raise ValueError(f"未知参数: {unknown}")
        return self.func(**kwargs)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(文件不存在)"

def _bash(command: str) -> str:
    return f"(模拟执行: {command})"


def build_tool_registry() -> dict[str, Tool]:
    """返回工具注册表：模型只能调用这里登记的工具。"""
    return {
        "read_file": Tool(
            "read_file", "读取指定文件的全部内容", _read,
            {"path": "要读取的文件路径"},
        ),
        "bash": Tool(
            "bash", "执行一条 shell 命令并返回输出", _bash,
            {"command": "要执行的命令"},
        ),
    }


def dispatch(registry: dict[str, Tool], name: str, args: dict) -> str:
    """调度器：名字 -> 查表 -> 执行。找不到就报错，绝不静默。"""
    if name not in registry:
        return f"(错误: 没有叫 {name} 的工具)"
    return registry[name].run(**args)


def main() -> None:
    registry = build_tool_registry()
    # 模拟一次工具调用协议：模型返回 tool_use，代理调度，结果回填
    calls = [
        ("read_file", {"path": "demo.txt"}),
        ("bash", {"command": "echo hello"}),
        ("不存在的工具", {}),
    ]
    for name, args in calls:
        print(f"tool_use: {name}{args}")
        print("   ->", dispatch(registry, name, args))


if __name__ == "__main__":
    main()