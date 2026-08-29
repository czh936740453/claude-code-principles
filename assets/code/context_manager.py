"""
context_manager.py —— token 估算 + 压缩触发（配合第 6 章）

上下文窗口是稀缺资源。代理每轮都要算：现在用了多少 token？
超过阈值就触发「压缩」（compact）：把旧消息浓缩成摘要，腾出空间。

用法:
    python context_manager.py
"""
from __future__ import annotations

# 粗略估算：中文约 1 字 ≈ 1 token，英文约 4 字符 ≈ 1 token
def estimate_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    other = len(text) - cjk
    return cjk + max(1, other // 4)


class ContextManager:
    def __init__(self, window: int = 200_000, compact_ratio: float = 0.8):
        self.window = window                  # 上下文窗口大小（token）
        self.ratio = compact_ratio            # 到达窗口 80% 就压缩
        self.history: list[dict] = []

    @property
    def usage(self) -> int:
        return sum(estimate_tokens(m["content"]) for m in self.history)

    @property
    def should_compact(self) -> bool:
        return self.usage >= self.window * self.ratio

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})
        if self.should_compact:
            self.compact()

    def compact(self) -> None:
        """把最早的一半消息压成一段摘要（真实实现会调用模型生成摘要）。"""
        old = self.history[: len(self.history) // 2]
        kept = self.history[len(self.history) // 2 :]
        digest = "「摘要」" + "；".join(m["content"][:20] for m in old)
        self.history = [{"role": "system", "content": digest}] + kept
        print(f"   [压缩] {len(old)} 条旧消息 -> 1 条摘要，当前 {self.usage} tokens")


def main() -> None:
    cm = ContextManager(window=200, compact_ratio=0.6)   # 小窗口，方便演示
    for i in range(10):
        cm.add("user", f"第 {i} 条消息：" + "很长的内容" * 10)
        print(f"写入后 {cm.usage} tokens / 窗口 {cm.window}")


if __name__ == "__main__":
    main()