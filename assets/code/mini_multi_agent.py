# -*- coding: utf-8 -*-
"""mini_multi_agent.py —— 三个角色的多智能体流水线（零依赖）

进阶篇 · 进·3 的配套代码：
研究员 → 程序员 → 评审，后一个 Agent 吃前一个的输出。
原理对照：进·3「多智能体协作」——单个循环没变，变的是「循环之间怎么串」。
"""
from __future__ import print_function


class Role:
    """一个角色 = 名字 + 职责 + 一个 work() 函数（这里用最简单的规则模拟）。"""

    def __init__(self, name, duty, work):
        self.name = name
        self.duty = duty
        self.work = work

    def run(self, text):
        print(f"  └─ [{self.name}] {self.duty}")
        return self.work(text)


def make_agents():
    """组建三角色流水线。"""
    researcher = Role(
        "研究员", "收集需求，输出任务清单",
        lambda text: "任务清单：\n1. 写一个计算平均值的函数\n2. 写三个测试用例",
    )
    programmer = Role(
        "程序员", "根据清单产出代码",
        lambda text: "def average(nums):\n    return sum(nums) / len(nums)",
    )
    reviewer = Role(
        "评审", "检查代码，给改进意见",
        lambda text: "评审意见：缺少空列表处理，建议加 if not nums 分支。",
    )
    return [researcher, programmer, reviewer]


def main():
    print("多智能体流水线开始（角色：研究员 → 程序员 → 评审）")
    print()
    output = "原始需求：实现一个求平均值的工具函数"
    for role in make_agents():
        output = role.run(output)
        print(f"    产出：{output}")
        print()
    print("流水线结束。每个 Agent 内部其实都是一个「想 → 做 → 看」的循环。")


if __name__ == "__main__":
    main()
