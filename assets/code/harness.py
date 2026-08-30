# -*- coding: utf-8 -*-
"""
harness.py —— 最小 Agent Harness（代理外壳）演示
=================================================

一句话：Harness = 把「大脑 + 手脚 + 门卫 + 记忆」串起来的那层工程代码。

    大脑   = 模型（Model）     只会「想」，不会动手
    手脚   = 工具（Tools）     读文件、跑命令、改代码
    门卫   = 权限（Permissions）决定哪一步允许执行
    记忆   = 会话（Memory）    记录说过什么、做过什么

真正的 Claude Code 就是一个这样的 Harness：模型负责决策，
Harness 负责把决策变成真实世界里的动作，并保证安全。
正文 10 章讲的循环、工具、权限、会话、CLI……在这里全部串起来了。

运行：  python harness.py
"""
import json

# ---------- 1. 大脑：模型（这里用假模型模拟，可换成真实 API） ----------
class FakeModel:
    """假模型：看着「记忆（上下文）」假装思考，返回下一步动作。"""

    def __init__(self):
        self.turn = 0  # 第几次被调用

    def think(self, memory):
        """输入：到目前为止的全部消息（上下文）。
        输出：一个「动作」——要么调用工具（tool_use），要么直接说答案（text）。"""
        self.turn += 1
        if self.turn == 1:
            # 第一步：决定先读文件
            return {"type": "tool_use", "name": "read_file", "input": {"path": "notes.txt"}}
        if self.turn == 2:
            # 第二步：看到文件内容后，决定统计行数
            return {"type": "tool_use", "name": "bash", "input": {"command": "统计行数"}}
        if self.turn == 3:
            # 第三步：想删掉临时文件 —— 这条会被「门卫」拦下来
            return {"type": "tool_use", "name": "bash", "input": {"command": "rm -rf /tmp"}}
        # 第四步：觉得任务完成了，直接输出文字，循环结束
        return {"type": "text", "text": "搞定了：文件已读完、行数已统计，危险命令被门卫拦下。"}

    # 换成真实模型（示意，未在此运行）：
    # def think(self, memory):
    #     resp = anthropic_client.messages.create(
    #         model="claude-sonnet-4-5",
    #         system="你是 Claude Code，一个高效的编程代理。",
    #         messages=memory.messages,       # 把记忆原样发给 API
    #         tools=tools.schemas(),          # 告诉模型有哪些工具可用
    #     )
    #     return parse_response(resp)          # 解析成 tool_use / text

# ---------- 2. 手脚：工具注册表 + 执行 ----------
class Tools:
    """工具 = 名字 + 说明 + 函数。模型只能调用登记过的工具。"""

    def __init__(self):
        self.registry = {
            "read_file": {"desc": "读取文件内容", "fn": self.read_file},
            "bash": {"desc": "执行 shell 命令", "fn": self.bash},
        }

    def schemas(self):
        """给模型看的「工具说明书」（简化版 JSON Schema）。"""
        return [{"name": n, "description": v["desc"]} for n, v in self.registry.items()]

    @staticmethod
    def read_file(path):
        # 真实实现是读磁盘；这里为了演示直接返回一段内容
        return "笔记内容：\n- 买牛奶\n- 写周报\n- 学 Claude Code"

    @staticmethod
    def bash(command):
        # 真实实现会用 subprocess 执行命令；这里是「模拟 shell」只认识几个命令
        if command == "统计行数":
            return "3"
        return f"（模拟 shell）未知命令：{command}"

    def run(self, name, payload):
        tool = self.registry.get(name)
        if not tool:
            return f"错误：没有名为 {name} 的工具"
        return tool["fn"](**payload)

# ---------- 3. 门卫：权限检查（YOLO 分级的超简版） ----------
class Guard:
    """在工具真正执行之前把关：危险命令直接拒绝。"""

    DANGEROUS = ["rm -rf", "format", "del /f", "shutdown"]

    def check(self, name, payload):
        """返回 (是否放行, 理由)。"""
        if name != "bash":
            return True, "读取 / 修改文件属于常规操作，放行"
        cmd = (payload.get("command") or "").lower()
        for bad in self.DANGEROUS:
            if bad in cmd:
                return False, f"命令包含危险模式「{bad}」，拒绝执行"
        return True, "命令无危险，放行"

# ---------- 4. 记忆：会话（短期历史 + 存盘恢复） ----------
class Memory:
    """把「说过什么、做过什么」记下来，这就是模型的上下文。"""

    def __init__(self):
        self.messages = []  # 每条消息：{"role": ..., "content": ...}

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})

    def save(self, path="session.json"):
        """把记忆序列化存盘（对应「会话文件」）。"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def load(self, path="session.json"):
        """从磁盘恢复记忆（对应「断点续聊」）。"""
        try:
            with open(path, encoding="utf-8") as f:
                self.messages = json.load(f)
            print(f"[记忆] 已恢复会话：{len(self.messages)} 条消息")
        except FileNotFoundError:
            print("[记忆] 没有旧会话，从零开始")

# ---------- 5. Harness：把上面四块装成整机 ----------
class Harness:
    """代理外壳本身：负责跑循环、接工具、过门卫、写记忆。"""

    def __init__(self):
        self.model = FakeModel()
        self.tools = Tools()
        self.guard = Guard()
        self.memory = Memory()
        self.max_turns = 6  # 防止死循环：最多转几圈

    def run(self, task):
        print(f"[用户] {task}\n")
        self.memory.add("user", task)
        for turn in range(1, self.max_turns + 1):
            action = self.model.think(self.memory)
            if action["type"] == "text":
                print(f"[输出] {action['text']}")
                break
            # 行动前先过门卫
            allowed, reason = self.guard.check(action["name"], action["input"])
            print(f"[决策] 想调用工具 {action['name']}：{action['input']}")
            print(f"[门卫] {reason}")
            if not allowed:
                print("[行动] （未执行）已被权限拦截\n")
                self.memory.add("tool_result", "权限拒绝：" + reason)
                continue
            result = self.tools.run(action["name"], action["input"])
            print(f"[行动] {action['name']} -> {result}\n")
            self.memory.add("tool_result", result)
        else:
            print("[警告] 达到最大轮数仍未完成，强制停止（终止条件！）")
        self.memory.save()
        print(f"[记忆] 会话已存盘，共 {len(self.messages)} 条消息 → 下次可恢复")

    @property
    def messages(self):
        return self.memory.messages


if __name__ == "__main__":
    Harness().run("帮我看看 notes.txt，统计行数，并清理临时文件")
