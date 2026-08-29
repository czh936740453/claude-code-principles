"""
session.py —— 会话保存 / 恢复的最小实现（配合第 6 章）

Claude Code 把一次对话存成「会话」：重启后还能接着聊。
原理很简单：把消息历史序列化成 JSON 存到磁盘，下次再读回来。

用法:
    python session.py
"""
from __future__ import annotations
import json, os, tempfile


class Session:
    """一个会话：一堆消息 + 能存盘 / 能恢复。"""

    def __init__(self, session_id: str, messages: list | None = None):
        self.session_id = session_id
        self.messages = messages or []

    def add(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def save(self, path: str) -> None:
        data = {"session_id": self.session_id, "messages": self.messages}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str) -> "Session":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(data["session_id"], data["messages"])


def main() -> None:
    path = os.path.join(tempfile.gettempdir(), "cc_session_demo.json")

    # 第一次运行：新会话，聊两句，存盘
    s = Session("demo-001")
    s.add("user", "帮我写个问候函数")
    s.add("assistant", "好的：def hi(): print('你好')")
    s.save(path)
    print("已保存会话:", path)

    # 模拟重启：从磁盘恢复，接着聊
    s2 = Session.load(path)
    print("恢复后历史条数:", len(s2.messages))
    s2.add("user", "再加一句再见")
    s2.save(path)
    print("追加后历史条数:", len(s2.messages))
    for m in s2.messages:
        print(f"  [{m['role']}] {m['content']}")

    os.remove(path)


if __name__ == "__main__":
    main()