# -*- coding: utf-8 -*-
"""choose_framework.py —— 开源 Agent 框架选型小助手（零依赖）

进阶篇 · 进·1 的配套代码：
回答几个 y/n 问题，根据「你的情况」推荐最合适的开源框架。
原理对照：进·1 的「该从哪个入手」选型表。
"""
from __future__ import print_function


def ask(question):
    """问一个 y/n 问题，循环直到用户给出合法回答。"""
    while True:
        ans = input(question + " (y/n) ").strip().lower()
        if ans in ("y", "n", "yes", "no"):
            return ans.startswith("y")


def recommend(answers):
    """根据回答字典返回 (推荐框架, 理由)。

    answers 形如 {"first": bool, "official": bool, "control": bool, "multi": bool, "learn": bool}
    """
    # 从上到下命中第一条，顺序即优先级
    if answers.get("learn"):
        return "smolagents", "你想对照本站原理学习 → smolagents 代码最少、概念最直白"
    if answers.get("first"):
        return "smolagents", "第一次写 Agent → 从代码最少的开始，最容易建立直觉"
    if answers.get("official"):
        return "openai-agents-python", "想用官方 API → 官方维护、文档最全、生态最稳"
    if answers.get("control"):
        return "langgraph", "要可控、可可视化 → 把循环画成图，状态一目了然"
    if answers.get("multi"):
        return "crewAI / autogen", "要做多角色协作 → 开箱即用的角色分工与对话协商"
    return "claw-code", "想对照本站十章原理 → 它是 Claude Code 的 Rust 重实现"


def main():
    print("=" * 56)
    print("开源 Agent 框架选型助手")
    print("回答几个问题，帮你找到合适的入手框架。")
    print("=" * 56)

    answers = {
        "first":    ask("Q1 你是第一次写 Agent 吗？"),
        "official": ask("Q2 你希望用官方维护的 SDK 吗？"),
        "control":  ask("Q3 你需要把流程可视化、可精确控制吗？"),
        "multi":    ask("Q4 你的任务需要多个角色协作吗？"),
        "learn":    ask("Q5 你想对照本站原理（Claude Code）学习吗？"),
    }

    name, reason = recommend(answers)
    print()
    print("推荐：", name)
    print("理由：", reason)
    print()
    print("下一步：去 GitHub 搜对应仓库，读 README 第一个示例，"
          "找到它的「入口函数」（Runner.run / Agent.run / main）。")


if __name__ == "__main__":
    main()
