# -*- coding: utf-8 -*-
"""mini_react_agent.py —— 约 40 行的 ReAct 循环（零依赖）

进阶篇 · 进·2 的配套代码：
演示 smolagents 的 ReAct 范式：想（reason）→ 做（act）→ 看（observe）→ 再想……
直到模型给出最终答案或达到最大步数。

原理对照：
- 循环 = 进·2 精读的 Runner.run / step() 骨架（感知 → 决策 → 行动 → 观察）
- max_steps = smolagents 的最大步数保护
"""
from __future__ import print_function


def fake_model(thought, step):
    """模拟大模型：根据当前思考返回 (行动, 参数) 或 (None, 最终答案)。

    真实项目里这里会调用 API；我们把「决策」固定下来，便于观察循环本身。
    """
    if step == 1:
        return ("add", 1)          # 第一次：做加法
    if step == 2:
        return ("add", 2)          # 第二次：再加
    return (None, "计算完成，结果是 3")  # 终止条件：模型给出最终答案


def run(max_steps=10):
    """一个最小 ReAct 循环：想 → 做 → 看 → 再想，直到结束。"""
    thought = "用户让我算 0 + 1 + 2"
    memory = []                    # 观察结果放回这里（相当于上下文）
    result = None

    for step in range(1, max_steps + 1):
        print(f"[{step:02d}] 想：{thought}")

        action, value = fake_model(thought, step)
        if action is None:
            result = value          # 终止条件：出现最终输出
            break

        # 做：执行动作（真实项目里这里是工具调用）
        if action == "add":
            current = memory[-1] if memory else 0
            new_val = current + value
            print(f"    做：调用工具 add({value}) → {new_val}")

        # 看：把观察结果写回记忆，作为下一轮的上下文
        memory.append(new_val)
        thought = f"当前累计 {new_val}，继续下一步"
        print(f"    看：结果已放回上下文，共 {len(memory)} 条观察")

    if result is None:
        print("警告：达到最大步数仍未得到最终答案（max_steps 保护生效）。")
    else:
        print()
        print("最终答案：", result)


if __name__ == "__main__":
    run(max_steps=10)
