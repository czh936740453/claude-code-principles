"""
cli_repl.py —— 极简交互式 REPL（配合第 7 章）

Claude Code 的交互模式本质是一个 REPL：
    打印提示符 -> 读一行输入 -> 解析（斜杠命令? 普通对话?）-> 响应 -> 循环

用法:
    python cli_repl.py
    在提示符后输入：hello、/help、/status、/quit
"""
from __future__ import annotations

def handle_slash(cmd: str) -> str:
    """斜杠命令分发：/开头的指令走这里。"""
    if cmd == "/help":
        return "可用命令: /help /status /quit；直接输入文字开始对话"
    if cmd == "/status":
        return "会话: demo | 模式: default | 已用上下文: 12%"
    if cmd == "/quit":
        return "__QUIT__"
    return f"(未知命令 {cmd}，试试 /help)"


def main() -> None:
    print("Claude Code 迷你版（输入 /quit 退出）")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见")
            break
        if not line:
            continue
        if line.startswith("/"):
            reply = handle_slash(line)
            if reply == "__QUIT__":
                print("再见")
                break
        else:
            reply = f"[模拟模型] 你说的是：{line}"
        print(reply)


if __name__ == "__main__":
    main()