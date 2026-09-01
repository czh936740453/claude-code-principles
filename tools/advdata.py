# -*- coding: utf-8 -*-
"""进阶篇 · 开源 Agent 实战 —— 三个进阶页面的内容数据（由 build_site.py 使用）"""

ADV_PAGES = [
    {"id": "ext-adv1", "tag": "进·1", "title": "开源 Agent 框架全景",
     "sub": "FRAMEWORK SURVEY",
     "goal": "站在 GitHub 上真实开源项目的肩膀上，看清主流 Agent 框架长什么样、各自怎么组织循环，学会「先全景、再精读」。",
     "summary": "9 个真实开源框架的全景对比：函数式 Runner、代码即行动、图编排、角色协作…… 学完你会知道该从哪个入手。",
     "keywords": "开源 agent 框架 openai agents sdk smolagents langgraph crewai autogen metagpt pydantic autogpt 全景 对比 选型"},
    {"id": "ext-adv2", "tag": "进·2", "title": "精读真实代码：三个 Agent 循环",
     "sub": "CODE READING",
     "goal": "把第 3 章的「代理循环」放到真实代码里：精读 OpenAI Agents SDK、smolagents、claw-code 三个项目的循环实现，逐句看懂。",
     "summary": "三份真实代码精读：Runner.run 的官方循环注释、smolagents 的 ReAct step、claw-code 的 Rust 顺序子代理循环。",
     "keywords": "精读 源码 真实代码 react runner.run step while 循环 smolagents claw-code rust openai agents 读代码"},
    {"id": "ext-adv3", "tag": "进·3", "title": "让 Agent 更聪明：协作、记忆与安全",
     "sub": "ADVANCED TOPICS",
     "goal": "进阶专题：多智能体怎么协作、记忆怎么分层、护栏怎么拦危险输入、怎么观察和评测一个 Agent。",
     "summary": "多智能体协作（角色 / 对话 / handoff / 流水线）、短期与长期记忆 + RAG、输入输出护栏、可观测与评测，附可运行迷你代码。",
     "keywords": "多智能体 multi-agent 协作 crew autogen handoff 记忆 memory rag 护栏 guardrail 提示注入 安全 评测 eval 可观测 trace"},
]

ADV_BLOCKS = {
"ext-adv1": [
    ("h2", "为什么读开源代码", "sec-why"),
    ("p", "第 1–10 章把原理讲透了，但原理只是「骨架」。真实框架是「血肉」：同一个代理循环，不同项目做出了完全不同的产品。读开源代码，就是看别人怎么把骨架做成能用的东西。"),
    ("ul", [
        "**原理落地**：在真实项目里看到 `while` 循环、工具注册表、权限检查长什么样",
        "**对比思维**：同一件事有 4 种做法，横向对比最涨功力",
        "**追新能力**：新框架往往最先实现最新论文里的机制",
    ]),
    ("callout", "tip", "一句话", "读开源代码不是为了抄，是为了看别人怎么踩坑、怎么解决，然后长出你自己的判断力。"),
    ("h2", "九个真实框架全景", "sec-map"),
    ("p", "下表数据抓取自 GitHub 仓库元数据（星标为约数、会随时间变化，仅作热度参考）。"),
    ("table", ["项目", "语言", "星标≈", "一句话定位", "循环风格"],
      [
        ["openai/openai-agents-python", "Python", "2.9 万", "官方 SDK：轻量、面向多智能体工作流", "函数式 Runner.run"],
        ["huggingface/smolagents", "Python", "2.9 万", "极简：让 Agent 用代码思考", "代码即行动（CodeAgent）"],
        ["langchain-ai/langgraph", "Python", "4.1 万", "把 Agent 画成有状态的图", "图编排（节点 + 边）"],
        ["crewAIInc/crewAI", "Python", "5.8 万", "角色扮演式多智能体协作", "角色分工 + 任务队列"],
        ["microsoft/autogen", "Python", "6.1 万", "多智能体对话框架", "智能体互相发消息"],
        ["FoundationAgents/MetaGPT", "Python", "7.0 万", "多智能体「软件公司」流水线", "SOP 角色流水线"],
        ["Significant-Gravitas/AutoGPT", "Python", "18.7 万", "经典自主代理实验", "目标驱动 while 循环"],
        ["pydantic/pydantic-ai", "Python", "2.0 万", "类型安全：全程类型化", "数据模型驱动"],
        ["ultraworkers/claw-code", "Rust", "19.5 万", "Claude Code 的 Rust 重实现", "顺序多子代理编排"],
      ]),
    ("callout", "warn", "注意", "星标只是热度参考，不是质量评分。选框架要看「文档完整度、维护活跃度、社区生态」，比看星标更靠谱。"),
    ("h2", "四种「循环风格」", "sec-styles"),
    ("p", "框架看着多，核心差异其实只有一个：**它怎么组织「感知 → 决策 → 行动 → 观察」这个循环**。记住第 3 章的循环，你就拿到了看穿所有框架的「透视镜」。"),
    ("h3", "① 函数式 Runner：你调用，它循环"),
    ("p", "openai-agents-python 把整个循环封装进一个函数 `Runner.run(agent, input)`。你只管描述「哪个 Agent + 什么输入」，循环由 SDK 内部跑完，直到出现最终输出或达到最大轮数。"),
    ("code", None, "text", '''result = await Runner.run(starting_agent=agent, input="帮我写一个 hello.py")
# SDK 内部（官方注释版）：
#   1. 调用 Agent
#   2. 有最终输出？→ 结束
#   3. 有 handoff？→ 换 Agent 再跑
#   4. 否则执行工具调用，然后回到第 1 步'''),
    ("h3", "② 代码即行动：让模型直接写代码"),
    ("p", "smolagents 的 CodeAgent 不让模型挑工具，而是让模型**直接写 Python 代码**，SDK 负责执行。循环 = 模型写代码 → 执行 → 把输出放回上下文 → 再写。代码本身就是「行动」。"),
    ("h3", "③ 图编排：把循环画成一张图"),
    ("p", "LangGraph 把状态转移画成图：节点 = 要做的动作，边 = 转移条件。循环就是沿着边走，还支持条件分支、人工介入、随时查看中间状态。"),
    ("h3", "④ 角色协作：循环与循环互相配合"),
    ("p", "CrewAI / AutoGen / MetaGPT 把一个循环升级成多个循环协作：不同角色（研究员、程序员、评审）各自跑自己的循环，把结果传给下一个人。"),
    ("h2", "该从哪个入手", "sec-choice"),
    ("table", ["你的情况", "推荐", "理由"],
      [
        ["第一次写 Agent", "smolagents", "代码最少，概念最直白"],
        ["想用官方 API", "openai-agents-python", "官方维护，文档最全"],
        ["要可控、可可视化", "LangGraph", "图直观，状态可查"],
        ["要做多角色协作", "CrewAI / AutoGen", "开箱即用"],
        ["想对照本站原理", "claw-code", "和十章内容一一对应"],
      ]),
    ("callout", "tip", "学习顺序", "先「精读一个」再「横向对比」。本站「进·2」带你精读三个真实循环，建议读完再来选型。"),
    ("h2", "代码实验室", "sec-lab"),
    ("p", "一个零依赖小助手：回答几个问题，帮你打分推荐最合适的框架。"),
    ("code", "choose_framework.py", "python", ""),
    ("p", "运行步骤：保存为 `choose_framework.py`，执行 `python choose_framework.py`，按提示回答 y / n。"),
    ("quiz", [
      {"q": "openai-agents-python 的核心入口是？", "opts": [("A", "Runner.run"), ("B", "main()"), ("C", "while True"), ("D", "agent.step")], "ans": "A",
       "explain": "整个循环被封装在 Runner.run(agent, input) 里。", "back": ("函数式 Runner", "sec-styles")},
      {"q": "哪种循环风格让模型直接生成代码作为行动？", "opts": [("A", "函数式"), ("B", "代码即行动"), ("C", "图编排"), ("D", "角色协作")], "ans": "B",
       "explain": "smolagents 的 CodeAgent 让模型直接写 Python 代码。", "back": ("代码即行动", "sec-styles")},
      {"q": "LangGraph 的核心抽象是？", "opts": [("A", "角色"), ("B", "图（节点 + 边）"), ("C", "对话"), ("D", "任务队列")], "ans": "B",
       "explain": "它把状态转移画成图，循环就是沿着边走。", "back": ("图编排", "sec-styles")},
      {"q": "关于 GitHub 星标数，正确的是？", "opts": [("A", "越高代表框架越好"), ("B", "只是热度参考"), ("C", "决定框架质量"), ("D", "与学习价值完全无关")], "ans": "B",
       "explain": "星标是热度不是质量；选型看文档、维护与生态。", "back": ("九个真实框架全景", "sec-map")},
    ]),
    ("summary", [
      "读开源代码 = 看别人怎么把同一个骨架做成产品",
      "9 个真实框架、4 种循环风格：函数式 / 代码即行动 / 图编排 / 角色协作",
      "星标是热度不是质量；选型看文档、维护、生态",
      "先精读一个再横向对比（本站「进·2」带读三个）",
    ]),
    ("myths", [
      ('星标最多的框架一定最好', '星标只是热度参考，选型要看文档完整度、维护活跃度与社区生态。'),
      ('学 Agent 必须从最复杂的框架开始', '新手从 smolagents 这类「代码最少」的开始，更容易建立直觉。'),
      ('框架之间差异巨大、互不相通', '它们只是同一套「感知 → 决策 → 行动 → 观察」循环的不同组织方式。'),
    ]),
    ("challenge", ('打开 GitHub，任选本页两个框架，分别找到它们的「入口函数」（Runner.run / Agent.run / main），各写一句话说明这个入口接收什么、返回什么。', '入口一般都在 README 的第一个示例里；重点看「输入 → 输出」，不要纠结内部细节。')),
],

"ext-adv2": [
    ("h2", "读代码的正确姿势", "sec-how"),
    ("p", "别一上来就逐行读。三步走：**先找入口 → 再找循环 → 最后追数据**。"),
    ("ol", [
        "**找入口**：程序从哪开始？（`Runner.run` / `agent.run` / `main`）",
        "**找循环**：哪个 `while` / `for` / `step` 在反复执行？",
        "**追数据**：messages / context / 记忆是怎么一步步被改写的？",
    ]),
    ("callout", "tip", "心法", "读代码读到「哦，这就是第 3 章那个循环」就成功了，其余细节可以之后再补。"),
    ("h2", "精读 ① OpenAI Agents SDK：Runner.run", "sec-sdk"),
    ("p", "openai-agents-python 的循环几乎没「藏起来」——它的文档注释直接写清了循环长什么样。下面这段来自官方仓库 `src/agents/run.py` 的 `Runner.run` 注释："),
    ("code", None, "text", '''The agent will run in a loop until a final output is generated. The loop runs like so:
  1. The agent is invoked with the given input.
  2. If there is a final output (i.e. the agent produces something of type
     `agent.output_type`), the loop terminates.
  3. If there's a handoff, we run the loop again, with the new agent.
  4. Else, we run tool calls (if any), and re-run the loop.
—— 摘自 openai/openai-agents-python · src/agents/run.py（注释节选）'''),
    ("p", "逐句对照第 3 章："),
    ("table", ["官方注释", "第 3 章概念", "大白话"],
      [
        ["第 1 步 invoke", "感知 + 决策", "把输入丢给模型，模型决定下一步"],
        ["第 2 步 final output", "终止条件", "模型说「这是最终答案」就停"],
        ["第 3 步 handoff", "多智能体交接", "把任务转交给另一个 Agent"],
        ["第 4 步 tool calls + re-run", "行动 + 观察", "跑完工具，结果放回去，回到第 1 步"],
      ]),
    ("p", "真实循环体比注释长得多（还塞了护栏、追踪、会话等），但骨架就是它。run.py 里核心就是这样的 `while`（下面为简化示意，非逐字摘录）："),
    ("code", None, "python", '''            while True:
                # ... 护栏检查（guardrails）、会话、追踪等外层逻辑 ...
                result = await handle_single_turn(current_agent, ...)

                if result.next_step == NextStepFinalOutput:
                    break          # 终止条件：出现最终输出
                # 否则：执行工具调用，结果写回，continue 回到循环头
            # （简化示意：真实代码见 run.py 的 while True 循环体）'''),
    ("callout", "tip", "别被生产代码吓到", "一个能上生产的循环会塞进护栏、追踪、会话、重试……但核心永远是「while + 出口」。看懂骨架，再看细节就轻松了。"),
    ("h2", "精读 ② smolagents：一步一个 ReAct", "sec-smol"),
    ("p", "smolagents 把「循环的一步」写成一个方法 `step()`，注释一句话就说清了 ReAct："),
    ("code", None, "python", '''    def step(self, memory_step: ActionStep) -> Any:
        """
        Perform one step in the ReAct framework: the agent thinks, acts,
        and observes the result.
        Returns either None if the step is not final, or the final answer.
        """
        return list(self._step_stream(memory_step))[-1]
—— 摘自 huggingface/smolagents · src/smolagents/agents.py（节选）'''),
    ("p", "解读三件事："),
    ("ul", [
        "**返回值**：返回 `None` = 还没结束、继续下一轮；返回答案 = 这是最后一步（这就是终止条件）",
        "**`_step_stream`**：一个生成器，一步步产出「思考 → 行动 → 观察」，`[-1]` 取最后一步",
        "**ReAct = Reasoning + Acting**：先想再做的范式，对应第 3 章的「决策 → 行动」",
    ]),
    ("p", "模型输出怎么变成动作？看它的 `extract_action`——把输出按分隔符拆成「思考 + 动作」："),
    ("code", None, "python", '''            split = model_output.split(split_token)
            rationale, action = split[-2], split[-1]
            # NOTE: 从后往前取，解决输出里出现多个分隔符的情况
—— 摘自 smolagents · extract_action（节选）'''),
    ("h2", "精读 ③ claw-code（Rust）：顺序子代理", "sec-claw"),
    ("p", "claw-code 的 `agents` 子命令做的不是「一个循环」，而是**多个子代理的顺序编排**：把一个大任务拆给几个专用 Agent（如 audit / explain / implement），依次跑完。核心是这段 Rust："),
    ("code", None, "rust", '''    for (i, spec) in specs.into_iter().enumerate() {
        println!("== Agent {} / {}: {} ==", i + 1, args.agent.len(), spec.name);
        // ... 为每个 spec 组装配置：preset / permission / model / session ...

        let run_res = run_one(cfg, &mut buf).await;   // 跑一个完整 Agent 循环
        match run_res {
            Ok(()) => {
                let summary = tail_chars(text.as_ref(), 1600);
                println!("  result: OK");
                // ... 输出该 Agent 的结果摘要，再进入下一个 spec
            }
            // ...
        }
    }
—— 摘自 ultraworkers/claw-code · rust/crates/claw-analog/src/agents.rs（节选）'''),
    ("p", "解读："),
    ("ul", [
        "`specs.into_iter().enumerate()`：逐个取出 Agent 配置（名字、preset、权限、模型）",
        "`run_one(cfg, &mut buf).await`：每个 Agent 内部都有一个完整的代理循环（就是第 3 章那个！），跑完把输出写进 buf",
        "`tail_chars(..., 1600)`：只保留结果尾部 1600 字符作为摘要，避免把完整输出都传给下一个环节",
    ]),
    ("callout", "tip", "多智能体 = 多个循环 + 串起来", "单个 Agent 的循环没变，变的是「循环之外」：谁先跑、结果传给谁、共享什么上下文。"),
    ("h2", "三循环对照表", "sec-compare"),
    ("table", ["维度", "Agents SDK", "smolagents", "claw-code"],
      [
        ["语言", "Python", "Python", "Rust"],
        ["循环载体", "while True（内部）", "step() / _step_stream", "for spec（编排）+ 内部循环"],
        ["感知", "invoke with input", "memory_step 上下文", "base_session 继承"],
        ["决策", "模型输出 final / tool / handoff", "模型输出 thought + action", "每个 spec 的 prompt"],
        ["行动", "执行工具调用", "执行生成的代码", "跑子 Agent 循环"],
        ["观察", "工具结果回填", "结果写回 memory", "summary_tail 摘要"],
        ["终止", "final output / max_turns", "final answer / max_steps", "全部 spec 跑完"],
      ]),
    ("h2", "代码实验室", "sec-lab"),
    ("p", "用纯 Python 实现一个约 40 行的 ReAct 循环：想 → 做 → 看 → 再想，最后输出答案。它同时演示了「解析动作」和「最大步数」两个概念。"),
    ("code", "mini_react_agent.py", "python", ""),
    ("p", "运行步骤：保存为 `mini_react_agent.py`，执行 `python mini_react_agent.py`。"),
    ("quiz", [
      {"q": "按 Runner.run 的官方注释，循环的终止条件是什么？", "opts": [("A", "出现最终输出"), ("B", "用户按 Ctrl+C"), ("C", "工具全部执行完"), ("D", "上下文占满")], "ans": "A",
       "explain": "第 2 步：出现 final output 循环终止。", "back": ("精读 ①", "sec-sdk")},
      {"q": "smolagents 的 step() 返回什么表示「还没结束」？", "opts": [("A", "最终答案"), ("B", "None"), ("C", "空字符串"), ("D", "0")], "ans": "B",
       "explain": "返回 None 说明不是最后一步，继续下一轮。", "back": ("精读 ②", "sec-smol")},
      {"q": "ReAct 中的 R 和 A 分别指？", "opts": [("A", "读取与行动"), ("B", "推理与行动"), ("C", "运行与异步"), ("D", "记录与评估")], "ans": "B",
       "explain": "Reasoning + Acting：先想再做的范式。", "back": ("精读 ②", "sec-smol")},
      {"q": "claw-code 的 agents 命令本质上是？", "opts": [("A", "单 Agent 循环"), ("B", "顺序多子代理编排"), ("C", "图编排"), ("D", "对话协商")], "ans": "B",
       "explain": "它把任务拆给多个专用 Agent 依次跑完。", "back": ("精读 ③", "sec-claw")},
    ]),
    ("summary", [
      "读代码三步：找入口 → 找循环 → 追数据",
      "Agents SDK：循环藏在 Runner.run 里，官方注释就是「官方版伪代码」",
      "smolagents：step() 一步一 ReAct，返回 None 继续、返回答案结束",
      "claw-code：顺序子代理编排 = 多个循环 + 共享上下文串起来",
      "三个循环本质相同：都是「感知 → 决策 → 行动 → 观察」",
    ]),
    ("myths", [
      ('真实源码比教程复杂一百倍、肯定看不懂', '骨架就是第 3 章的循环；生产代码只是加了护栏、追踪、会话这些「外层」。'),
      ('注释不重要，代码才重要', 'Agents SDK 的循环描述就写在注释里，官方注释是最优质的一手资料。'),
      ('多智能体 = 一套全新的循环', '单个循环没变，变的是「循环之间怎么串」。'),
    ]),
    ("challenge", ('打开 smolagents 仓库的 `src/smolagents/agents.py`，找到 `step` 和 `_step_stream`，数一数「思考 → 行动 → 观察」各出现在哪几行；再给 mini_react_agent.py 加一个 `max_steps` 参数，超限就打印警告。', '用仓库搜索定位 `_step_stream`；mini_react_agent 里那个 for 循环就是 max_steps 的雏形，把固定值 10 改成参数即可。')),
],

"ext-adv3": [
    ("h2", "三个方向", "sec-topics"),
    ("p", "单个循环能跑起来之后，真正的工程问题才开始：一个 Agent 干不完怎么办？记不住怎么办？乱来怎么办？本章讲三个方向——**协作、记忆、安全**，再补一个「怎么看它干活」。"),
    ("h2", "多智能体协作", "sec-multi"),
    ("p", "为什么要多个 Agent？"),
    ("ul", [
        "**上下文有上限**：一个 Agent 塞不下整个项目（对应第 6 章）",
        "**分工更专注**：每个 Agent 只带自己的角色说明和工具",
        "**视角更多元**：研究、编码、评审各司其职，互相挑错",
    ]),
    ("h3", "四种协作模式"),
    ("table", ["模式", "代表框架", "怎么协作", "类比"],
      [
        ["角色分工", "CrewAI / MetaGPT", "不同角色领任务，产出交接", "公司部门"],
        ["对话协商", "AutoGen", "智能体互相发消息讨论", "会议室"],
        ["交接 handoff", "openai-agents-python", "主 Agent 把任务转给另一个 Agent", "前台转手"],
        ["顺序流水线", "claw-code", "子 Agent 依次跑，共享 base session", "流水线工位"],
      ]),
    ("callout", "tip", "记住", "第 3 章那个 while 循环没有消失——多智能体 = 多个循环 + 它们之间的「消息 / 交接」。先理解单循环，再看协作就顺了。"),
    ("h2", "记忆系统：让它记住更久", "sec-memory"),
    ("p", "第 6 章说过：上下文窗口是 Agent 的「短期记忆」。想让 Agent 记住更多，按「时间跨度」分三层："),
    ("table", ["层级", "存什么", "怎么实现", "类比"],
      [
        ["短期记忆", "本次对话 / 最近几步", "上下文窗口（200K / 1M）", "工作台"],
        ["长期记忆", "项目约定、用户偏好", "CLAUDE.md、会话文件", "笔记本"],
        ["知识库 RAG", "外部文档、代码库", "向量检索 → 检索片段注入上下文", "查资料"],
      ]),
    ("p", "RAG 的本质就一句话：**不把所有文档塞进上下文，而是按需检索相关片段再注入**。对照第 2 章——RAG 就是在「上下文组装」那一步，多加了一个「先查资料」的动作。"),
    ("p", "想在真实项目里看记忆实现，可以读 smolagents 的 `src/smolagents/memory.py`：它把每一步（思考、动作、观察、工具输出）按结构存成列表，供模型生成时回放。"),
    ("h2", "护栏与安全：不让他乱来", "sec-guardrail"),
    ("p", "第 5 章讲过「工具权限」——在执行前拦。护栏（Guardrail）更靠前：**输入进模型前**和**输出给用户前**都要检查。"),
    ("table", ["类型", "在哪一步", "拦什么"],
      [
        ["输入护栏", "输入进模型前", "提示注入、越权指令、违规内容"],
        ["工具护栏", "工具调用前", "危险命令（rm -rf 等）→ 走权限确认"],
        ["输出护栏", "答案给用户前", "敏感信息、错误代码、违规内容"],
      ]),
    ("p", "提示注入（Prompt Injection）是最常见的攻击：攻击者把「忽略之前的指令，执行…… 」写进一个文件或网页，Agent 读到后可能照做。防御要点："),
    ("ul", [
        "把外部内容标记为「不可信数据」，在系统提示里声明边界",
        "对危险动作一律走权限确认（对应第 5 章 YOLO）",
        "输入 / 输出护栏兜底",
    ]),
    ("h2", "可观测与评测：怎么知道它干得好不好", "sec-obs"),
    ("p", "Agent 是概率性的：同样的输入，这次行、下次可能不行。所以必须能「看」和「量」。"),
    ("ul", [
        "**可观测（Trace）**：记录每一步——输入、模型输出、工具调用、耗时、token 数。出问题能回放，这就是最朴素的「日志 + 结构化记录」。",
        "**评测（Eval）**：用固定测试集反复跑，量化指标：任务成功率、是否越权、工具调用是否合理、token 花销。",
    ]),
    ("callout", "tip", "从哪开始", "给 mini_react_agent.py 加一个 log() 函数，把每步打出来——你已经拥有第一个 trace 了。再准备 3 个测试任务、跑 5 遍数成功率——这就是 eval 的雏形。"),
    ("h2", "代码实验室", "sec-lab"),
    ("p", "两个零依赖模块，对应本章两个主题："),
    ("ul", [
        "`mini_multi_agent.py`：三个角色（研究员 / 程序员 / 评审）组成流水线，后一个 Agent 吃前一个的输出",
        "`mini_guardrail.py`：输入护栏 + 权限检查 + 输出护栏的完整演示",
    ]),
    ("code", "mini_multi_agent.py", "python", ""),
    ("code", "mini_guardrail.py", "python", ""),
    ("p", "运行步骤：分别保存并执行 `python mini_multi_agent.py` 与 `python mini_guardrail.py`。"),
    ("quiz", [
      {"q": "多智能体协作中，「主 Agent 把任务转给另一个 Agent」叫什么？", "opts": [("A", "handoff"), ("B", "guardrail"), ("C", "RAG"), ("D", "trace")], "ans": "A",
       "explain": "Agents SDK 的循环第 3 步就是处理 handoff。", "back": ("多智能体协作", "sec-multi")},
      {"q": "RAG 的本质是？", "opts": [("A", "把所有文档塞进上下文"), ("B", "按需检索相关片段再注入"), ("C", "重新训练模型"), ("D", "压缩历史消息")], "ans": "B",
       "explain": "检索 + 注入两步，而不是全量塞入。", "back": ("记忆系统", "sec-memory")},
      {"q": "输入护栏在哪个阶段检查？", "opts": [("A", "输入进模型前"), ("B", "工具执行后"), ("C", "输出给用户前"), ("D", "会话保存后")], "ans": "A",
       "explain": "输入护栏在输入进入模型之前检查。", "back": ("护栏与安全", "sec-guardrail")},
      {"q": "提示注入最常见的载体是？", "opts": [("A", "系统提示"), ("B", "外部内容（文件 / 网页）"), ("C", "模型权重"), ("D", "API Key")], "ans": "B",
       "explain": "攻击者把恶意指令写进外部内容，Agent 读到后可能照做。", "back": ("护栏与安全", "sec-guardrail")},
    ]),
    ("summary", [
      "多智能体 = 多个循环 + 协作（角色 / 对话 / handoff / 流水线）",
      "记忆分三层：短期上下文、长期文件、知识库 RAG",
      "护栏三道：输入、工具、输出；提示注入靠「不可信数据 + 权限确认」防",
      "用 trace 看过程、用 eval 量结果",
    ]),
    ("myths", [
      ('多智能体就是「代码更复杂」', '单个循环没变，只是多了「循环之间怎么串」这一层。'),
      ('RAG = 向量数据库', '向量库只是工具；RAG 的核心是「检索 + 注入」这两步。'),
      ('护栏能 100% 拦住攻击', '没有绝对安全；护栏是降低风险，还要配合权限最小化和人工确认。'),
    ]),
    ("challenge", ('给 mini_multi_agent.py 增加一个「审查」角色（第四个 Agent），检查前面产出里是否包含「TODO」字样，有就提改进意见；再给 mini_guardrail.py 加一条你认为危险的命令规则并测试。', '第四个 Agent 和 reviewer 写法一样，只是 work 函数里判断 "TODO" in text；guardrail 在 DANGEROUS_CMDS 列表加一行即可。')),
],
}
