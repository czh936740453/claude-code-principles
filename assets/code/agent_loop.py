"""
agent_loop.py —— 最小可运行的「代理循环」(Agent Loop)（配合第 3 章）

真实 Claude Code 的核心就是一个 while 循环：
    感知当前状态 -> 模型决定下一步 -> 调用工具 -> 把结果放回上下文 -> 继续
这里用 mock_model() 模拟「模型」，用工具表模拟「工具」，把循环本身跑给你看。

用法:
    python agent_loop.py
"""
from __future__ import annotations
import time

# ---------- 1. 模拟的「大模型」：根据状态决定下一步 ----------
def mock_model(step: int, history: list) -> dict:
    """真实场景中这里调用 Anthropic API，返回文本或 tool_use。"""
    if step == 0:
        return {"kind": "tool_use", "name": "read_file", "input": {"path": "notes.txt"}}
    if step == 1:
        return {"kind": "tool_use", "name": "bash", "input": {"command": "echo 完成 >> notes.txt"}}
    return {"kind": "text", "text": "任务完成，笔记已更新。"}

# ---------- 2. 工具注册表 + 执行器 ----------
def read_file(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "(文件不存在，工具已安全返回)"

def bash(command: str) -> str:
    return f"(模拟执行: {command})"

TOOLS = {"read_file": read_file, "bash": bash}   # 名字 -> 函数，这就是工具表

# ---------- 3. 代理主循环 ----------
def main() -> None:
    step, history = 0, []
    for _ in range(10):                       # 最大步数保护，防止死循环
        msg = mock_model(step, history)       # 1) 感知 + 决策
        if msg["kind"] == "text":
            print("[Agent]", msg["text"])     # 模型认为任务完成
            break
        tool = TOOLS[msg["name"]]             # 2) 行动：查表执行工具
        result = tool(**msg["input"])
        print(f"[工具] {msg['name']}{msg['input']} -> {result}")
        history.append(result)                # 3) 观察：结果放回历史
        step += 1
        time.sleep(0.3)                       # 放慢，便于观察循环

if __name__ == "__main__":
    main()