"""
permissions.py —— YOLO 式风险分级器骨架（配合第 5 章）

真实 Claude Code 里有个 classifyYoloAction()，用「危险程度」决定
一个工具调用要不要先问用户。这里用规则模拟同一思路：
    低风险 -> 直接放行；中风险 -> 询问；高风险 -> 拒绝。

用法:
    python permissions.py
"""
from __future__ import annotations
from dataclasses import dataclass

# 风险等级：数字越大越危险
LOW, MEDIUM, HIGH = 1, 2, 3

# 一条规则：命令里出现这些词，风险升一级
RISKY_KEYWORDS = {
    "rm": HIGH, "format": HIGH, "shutdown": HIGH,
    "drop": HIGH, "delete": HIGH, "mv": MEDIUM, "chmod": MEDIUM,
}

@dataclass
class Decision:
    level: int
    action: str          # allow / ask / deny
    reason: str


def classify_yolo(action: str, command: str, mode: str) -> Decision:
    """模拟 YOLO 分类：动作 + 命令 + 权限模式 -> 决策。"""
    level = LOW
    for word, risk in RISKY_KEYWORDS.items():
        if word in command.lower():
            level = max(level, risk)

    if mode == "bypassPermissions":
        return Decision(level, "allow", "bypass 模式：全部放行")
    if mode == "plan":
        return Decision(level, "deny", "plan 模式：只规划不执行")

    if level == HIGH:
        return Decision(level, "deny", f"高风险命令，拒绝执行（{command}）")
    if level == MEDIUM:
        return Decision(level, "ask", f"中风险，需要用户确认（{command}）")
    return Decision(level, "allow", f"低风险，自动放行（{command}）")


def main() -> None:
    tests = [
        ("Bash", "ls -la", "default"),
        ("Bash", "rm -rf /tmp/x", "default"),
        ("Bash", "mv a.txt b.txt", "default"),
        ("Bash", "rm -rf /tmp/x", "plan"),
        ("Bash", "rm -rf /tmp/x", "bypassPermissions"),
    ]
    for action, command, mode in tests:
        d = classify_yolo(action, command, mode)
        print(f"[{mode:>16}] {command:<22} -> {d.action:<5} (风险{d.level}, {d.reason})")


if __name__ == "__main__":
    main()