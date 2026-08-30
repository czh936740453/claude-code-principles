# -*- coding: utf-8 -*-
"""
build_site.py —— 生成「Claude Code 原理图解」全部静态页面。
用法:  python tools/build_site.py
产出:  index.html / about.html / glossary.html / toolbox.html / docs/ch01..ch10.html
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = ROOT / "assets" / "code"

def esc(s):
    return html.escape(str(s), quote=False)

def esc_attr(s):
    return html.escape(str(s), quote=True)

def inline_md(t):
    """极简行内标记：`code`、**加粗**、[文字](链接)。"""
    t = esc(t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t

def detect_lang(fname):
    n = (fname or "").lower()
    if n.endswith(".py"): return "python"
    if n.endswith((".sh",)): return "bash"
    if n.endswith(".json"): return "json"
    if n.endswith((".ts",)): return "typescript"
    if n.endswith(".rs"): return "rust"
    return "text"

def code_figure(fname=None, lang=None, text=None, path=None):
    if fname:
        text = (path if path is not None else CODE_DIR / fname).read_text(encoding="utf-8")
    if lang is None:
        lang = detect_lang(fname)
    df = f' data-file="{fname}"' if fname else ""
    dl = f' data-lang="{lang}"' if lang else ""
    body = esc(text or "")
    return f'<figure class="codeblock"{df}{dl}><pre class="codebody"><code>{body}</code></pre></figure>'

def env_tabs(panes):
    """panes: [(key, label, lang, text), ...]"""
    btns = []
    for i, (k, label, lang, text) in enumerate(panes):
        cls = " active" if i == 0 else ""
        btns.append(f'<button data-pane="{k}" class="{cls.strip()}">{label}</button>')
    panes_html = []
    for i, (k, label, lang, text) in enumerate(panes):
        fig = code_figure(lang=lang, text=text)
        cls = " active" if i == 0 else ""
        panes_html.append(f'<div class="env-pane{cls}" data-pane="{k}">{fig}</div>')
    return ('<div class="envtabs"><div class="tabbar">' + "".join(btns) +
            "</div>" + "".join(panes_html) + "</div>")

def render_blocks(blocks, ch_num=""):
    """把内容块渲染成正文 HTML。"""
    out = []
    h2_count = 0
    h3_count = 0
    for b in blocks:
        k = b[0]
        if k == "h2":
            h2_count += 1
            text, aid = b[1], (b[2] if len(b) > 2 else None)
            hid = aid or f"s{h2_count}"
            out.append(f'<h2 id="{hid}"><span class="h2-num">{ch_num} /</span>{esc(text)}</h2>')
        elif k == "h3":
            h3_count += 1
            text = b[1]
            out.append(f'<h3 id="h{h3_count}">{esc(text)}</h3>')
        elif k == "p":
            out.append(f"<p>{inline_md(b[1])}</p>")
        elif k == "ul":
            items = "".join(f"<li>{inline_md(i)}</li>" for i in b[1])
            out.append(f"<ul>{items}</ul>")
        elif k == "ol":
            items = "".join(f"<li>{inline_md(i)}</li>" for i in b[1])
            out.append(f"<ol>{items}</ol>")
        elif k == "steps":
            items = "".join(
                f"<li><b>{inline_md(t)}</b>{inline_md(d)}</li>" for t, d in b[1])
            out.append(f'<ol class="steps">{items}</ol>')
        elif k == "callout":
            ctype, label, text = b[1], b[2], b[3]
            out.append(f'<div class="callout {ctype}"><span class="co-label">{label}</span>{inline_md(text)}</div>')
        elif k == "code":
            fname, lang, text = b[1], b[2], b[3]
            out.append(code_figure(fname, lang, text))
        elif k == "envtabs":
            out.append(env_tabs(b[1]))
        elif k == "table":
            headers, rows = b[1], b[2]
            th = "".join(f"<th>{inline_md(h)}</th>" for h in headers)
            trs = []
            for row in rows:
                tds = "".join(f"<td>{inline_md(c)}</td>" for c in row)
                trs.append(f"<tr>{tds}</tr>")
            out.append(f'<table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>')
        elif k == "quiz":
            out.append(render_quiz(b[1]))
        elif k == "summary":
            items = "".join(f"<li>{inline_md(i)}</li>" for i in b[1])
            out.append(f'<div class="callout"><span class="co-label">本章小结</span><ul>{items}</ul></div>')
        elif k == "demo":
            out.append(render_demo(b[1]))
        elif k == "html":
            out.append(b[1])
    return "\n".join(out)

def render_quiz(items):
    parts = ['<div class="quiz">']
    for idx, it in enumerate(items, 1):
        opts = "".join(
            f'<button type="button" data-opt="{o[0]}">{o[0]}. {esc(o[1])}</button>' for o in it["opts"])
        back = ""
        if it.get("back"):
            label, aid = it["back"]
            back = f' <a href="#{aid}">回看：{esc(label)}</a>'
        parts.append(
            f'<div class="quiz-item" data-answer="{esc_attr(it["ans"])}">'
            f'<p class="quiz-q">{idx}. {esc(it["q"])}</p>'
            f'<div class="quiz-opts">{opts}</div>'
            f'<div class="quiz-feedback"><span class="mark"></span> '
            f'{esc(it["explain"])}{back}</div></div>')
    parts.append("</div>")
    return "".join(parts)

def render_demo(name):
    if name == "loop":
        return (
            '<div class="demo" id="loopDemo">'
            '<p class="demo-title">试着走一轮代理循环（点击“下一步”）</p>'
            '<div class="loop-grid">'
            '<div class="loop-cell"><span class="ic">01</span><b>感知</b>读取当前状态</div>'
            '<div class="loop-cell"><span class="ic">02</span><b>决策</b>模型决定下一步</div>'
            '<div class="loop-cell"><span class="ic">03</span><b>行动</b>调用工具</div>'
            '<div class="loop-cell"><span class="ic">04</span><b>观察</b>结果回填上下文</div>'
            '</div><div class="demo-log"></div>'
            '<div class="demo-ctrl"><button class="btn btn-next">下一步</button>'
            '<button class="btn btn-reset">重置</button><span class="status"></span></div></div>')
    if name == "tree":
        return (
            '<div class="demo" id="treeDemo">'
            '<p class="demo-title">走一遍权限决策流程（点击分支）</p>'
            '<div class="tree-root"></div>'
            '<div class="demo-ctrl"><button class="btn btn-reset">重新开始</button>'
            '<span class="status"></span></div></div>')
    if name == "ctx":
        return (
            '<div class="demo" id="ctxDemo">'
            '<p class="demo-title">拖动滑块，观察上下文占用与压缩触发</p>'
            '<input type="range" min="10" max="100" value="45" style="width:100%" aria-label="上下文占用">'
            '<div class="ctx-bar" style="margin-top:14px"><i></i><span class="thresh" style="left:80%"></span></div>'
            '<div class="ctx-meta"></div>'
            '<p class="ctx-info" style="font-size:14px;color:var(--text-2);margin-top:10px"></p></div>')
    return ""

# ---------- 章节元数据 ----------
CHAPTERS = [
    {"id": "ch01", "num": "01", "title": "认识 Claude Code", "path": "docs/ch01.html", "part": 1,
     "goal": "搞懂 Claude Code 是什么、解决什么问题，以及它和聊天机器人 / IDE 插件的本质区别。",
     "prereq": "无，零基础可读。",
     "summary": "终端里的 AI 编程代理：你说目标，它自己动手。和聊天机器人、IDE 插件有什么本质区别？",
     "keywords": "claude code 介绍 终端 代理 agent cli 命令行 是什么"},
    {"id": "ch02", "num": "02", "title": "一次对话的完整旅程", "path": "docs/ch02.html", "part": 1,
     "goal": "跟着一次真实对话走一遍：从你按下回车，到它给出答案，中间到底发生了什么。",
     "prereq": "建议先读第 1 章。",
     "summary": "端到端数据流：输入 → 上下文组装 → API → 工具调用 → 循环，一张图看懂全流程。",
     "keywords": "数据流 上下文 api 请求 响应 会话 流程图 端到端"},
    {"id": "ch03", "num": "03", "title": "代理循环 Agent Loop", "path": "docs/ch03.html", "part": 2,
     "goal": "掌握 Claude Code 的心脏——while 循环：感知、决策、行动、观察，循环往复直到完成。",
     "prereq": "建议先读第 2 章。",
     "summary": "核心 while 循环：为什么它是「代理」而不是「单次问答」，用伪代码和可运行例子讲透。",
     "keywords": "agent loop 代理循环 while 工具调用 迭代 终止条件 伪代码"},
    {"id": "ch04", "num": "04", "title": "工具系统", "path": "docs/ch04.html", "part": 2,
     "goal": "理解「工具 = 函数 + 说明」：模型怎么知道能用什么工具、怎么调用、结果怎么回来。",
     "prereq": "建议先读第 3 章。",
     "summary": "工具注册表、tool_use / tool_result 协议、内置工具清单，以及权限怎么拦在中间。",
     "keywords": "工具 tool_use tool_result schema 注册表 bash read edit grep 调度"},
    {"id": "ch05", "num": "05", "title": "权限与安全", "path": "docs/ch05.html", "part": 2,
     "goal": "搞懂「Claude 凭什么能跑我的命令」：权限模式、YOLO 分类器、命令注入检查。",
     "prereq": "建议先读第 3、4 章。",
     "summary": "四种权限模式、YOLO 风险分级、allowlist / denylist，安全边界如何工作。",
     "keywords": "权限 permission yolo 安全 命令注入 allowlist denylist bypass acceptEdits plan"},
    {"id": "ch06", "num": "06", "title": "会话与上下文管理", "path": "docs/ch06.html", "part": 2,
     "goal": "理解「上下文窗口」这个稀缺资源：会话怎么恢复、token 怎么算、快满了怎么办。",
     "prereq": "建议先读第 2、3 章。",
     "summary": "会话持久化、上下文窗口（200K / 1M）、token 预算与压缩机制（compact）。",
     "keywords": "会话 session 上下文 context token 窗口 compact 压缩 历史 恢复"},
    {"id": "ch07", "num": "07", "title": "CLI 与斜杠命令", "path": "docs/ch07.html", "part": 3,
     "goal": "掌握 Claude Code 的「人机界面」：启动方式、交互模式、斜杠命令与隐藏命令。",
     "prereq": "建议先读第 2 章。",
     "summary": "启动参数、REPL 交互、常用斜杠命令，以及 26 个隐藏命令里的代表。",
     "keywords": "cli 命令行 repl 斜杠命令 slash 启动参数 flags 交互 隐藏命令"},
    {"id": "ch08", "num": "08", "title": "配置、环境变量与特性门控", "path": "docs/ch08.html", "part": 3,
     "goal": "看懂它「怎么被开关控制」：配置文件层级、120+ 环境变量、build flags 与 tengu 门控。",
     "prereq": "建议先读第 3 章。",
     "summary": "~/.claude/ 配置、环境变量分类、GrowthBook tengu_* 灰度开关、anthropic-beta 头。",
     "keywords": "配置 config 环境变量 env 特性开关 feature flag tengu growthbook beta"},
    {"id": "ch09", "num": "09", "title": "从公开源码到 Rust 移植", "path": "docs/ch09.html", "part": 4,
     "goal": "了解「源码长什么样、怎么读」：从 cli.js.map 到 1,884 个 TS 文件，再到 Rust 移植的对照。",
     "prereq": "建议先读第 3–6 章。",
     "summary": "sourcemap 原理、TS 架构模块、TS ↔ Rust 对照表、PARITY 思路。",
     "keywords": "源码 sourcemap cli.js.map typescript rust 移植 claw-code parity crate"},
    {"id": "ch10", "num": "10", "title": "自学路线图与实践建议", "path": "docs/ch10.html", "part": 4,
     "goal": "拿到一份可执行的行动清单：怎么读源码、怎么动手复刻、注意什么边界。",
     "prereq": "建议学完全部章节。",
     "summary": "读源码三步法、最小复刻路线、安全与伦理边界、推荐练习。",
     "keywords": "自学 路线图 实践 复刻 阅读源码 练习 安全 伦理"},
]

PARTS = [
    {"n": 1, "title": "认知篇", "sub": "它是什么"},
    {"n": 2, "title": "核心机制篇", "sub": "它怎么工作"},
    {"n": 3, "title": "外围系统篇", "sub": "支撑它的系统"},
    {"n": 4, "title": "研究与移植篇", "sub": "怎么读源码 / 怎么复刻"},
]

SITE = "Claude Code 原理图解"
# ---------- 页面外壳 ----------
BRAND_SVG = (
    '<svg width="22" height="22" viewBox="0 0 64 64" aria-hidden="true">'
    '<rect width="64" height="64" rx="14" fill="#1e1e1e"/>'
    '<rect x="14" y="16" width="36" height="32" rx="5" fill="none" stroke="#f5f5f5" stroke-width="3"/>'
    '<circle cx="44" cy="21" r="2.4" fill="#f5f5f5"/>'
    '<text x="23" y="39" font-family="Consolas, monospace" font-size="17" font-weight="bold" fill="#f5f5f5">&gt;_</text></svg>'
)

THEME_SCRIPT = (
    "<script>(function(){try{var t=localStorage.getItem('cc_theme');"
    "if(t==='dark')document.documentElement.setAttribute('data-theme','dark');}catch(e){}})();</script>"
)

def topbar(prefix, active):
    links = [
        ("index.html", "nav-home", "首页"),
        ("docs/ch01.html", "nav-ch", "章节"),
        ("docs/ext-ah.html", "nav-ext", "拓展"),
        ("glossary.html", "nav-glossary", "术语表"),
        ("toolbox.html", "nav-toolbox", "代码库"),
        ("about.html", "nav-about", "关于"),
    ]
    nav = ""
    for href, cls, label in links:
        a = " active" if cls == active else ""
        nav += f'<a class="{cls}{a}" href="{prefix}{href}">{label}</a>'
    return (
        '<header class="topbar">'
        '<button id="hamburger" class="tb-item hamburger" aria-label="打开目录">\u2630</button>'
        f'<a class="brand" href="{prefix}index.html">{BRAND_SVG}Claude Code 原理图解</a>'
        f"<nav>{nav}</nav>"
        '<span class="spacer"></span>'
        '<span class="tb-progress"><span class="tb-txt">0 / 10</span><span class="bar"><i></i></span></span>'
        '<button class="tb-item" data-fontbtn="0" aria-label="小字号">A-</button>'
        '<button class="tb-item" data-fontbtn="1" aria-label="中字号">A</button>'
        '<button class="tb-item" data-fontbtn="2" aria-label="大字号">A+</button>'
        '<button id="themeToggle" class="tb-item" aria-label="切换深浅色">\u263E</button>'
        "</header>"
    )

def footer(prefix):
    return (
        '<footer class="site-footer"><div class="inner">'
        "<p><strong>Claude Code 原理图解</strong> —— 面向自学的开源原理科普站。</p>"
        "<p>内容基于 <a href=\"https://ccleaks.com/leaks\">ccleaks.com/leaks</a> 的公开源码分析"
        " 与 <a href=\"https://github.com/ultraworkers/claw-code\">ultraworkers/claw-code</a> 的 Rust 移植项目整理，"
        "仅供学习参考；信息可能不准确或已过时，请以官方文档为准。</p>"
        "<p>本站不隶属于 Anthropic，与任何泄露源码无利益关系，仅作学习用途。\u00a9 2026</p>"
        "</div></footer>"
    )

# ---------- 问 Codex 直连窗口 ----------
def codex_widget(prefix):
    """右下角「问 Codex」直连窗口：本机桥接 -> Codex CLI（只读沙箱）。"""
    chips = [
        "代理循环是怎么转起来的？",
        "tool_use 是什么？",
        "YOLO 权限怎么分级？",
        "上下文被占满会怎样？",
    ]
    chip_html = "".join(f'<button type="button">{esc(c)}</button>' for c in chips)
    return (
        '<button id="codexFab" class="codex-fab" type="button" aria-label="问 Codex">'
        '<span class="fab-ico">&gt;_</span><span class="fab-txt">问 Codex</span></button>\n'
        '<aside id="codexChat" class="codex-chat" role="dialog" aria-label="问 Codex 直连窗口">'
        '<div class="codex-head"><b>&gt;_ Codex</b>'
        '<span id="codexStatus" class="codex-status connecting">连接中…</span>'
        '<button id="codexClose" type="button" aria-label="关闭">×</button></div>'
        '<div id="codexMessages" class="codex-msgs"></div>'
        f'<div id="codexChips" class="codex-chips">{chip_html}</div>'
        '<div class="codex-input">'
        '<textarea id="codexInput" rows="1" placeholder="向本机 Codex 提问…（只读沙箱）"></textarea>'
        '<button id="codexSend" type="button">发送</button></div>'
        "</aside>\n"
        f'<script src="{prefix}assets/js/codex-chat.js"></script>\n'
    )

def page_shell(title, desc, body, page_id, prefix, active, with_sidebar=True):
    sidebar = '<aside class="sidebar"><nav id="sidebarNav"></nav></aside>' if with_sidebar else ""
    layout_cls = ' class="content-inner"' if not with_sidebar else ' class="content-inner"'
    return (
        "<!doctype html>\n<html lang=\"zh-CN\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{esc(title)} — {SITE}</title>\n"
        f'<meta name="description" content="{esc_attr(desc)}">\n'
        f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">\n'
        f'<link rel="stylesheet" href="{prefix}assets/css/style.css">\n'
        f"{THEME_SCRIPT}\n</head>\n"
        f'<body data-page="{page_id}">\n'
        '<div class="scrim"></div>\n'
        f"{topbar(prefix, active)}\n"
        '<div class="layout">\n'
        f"{sidebar}\n"
        f'<main class="content"><div class="content-inner">\n'
        f"{body}\n"
        "</div></main>\n</div>\n"
        f"{footer(prefix)}\n"
        f'<script src="{prefix}assets/js/nav.js"></script>\n'
        f'<script src="{prefix}assets/js/main.js"></script>\n'
        f"{codex_widget(prefix)}"
        "</body>\n</html>\n"
    )

# ---------- 首页 ----------
def build_home():
    progress = (
        '<div class="progress-panel" id="homeProgress">'
        '<div class="row">'
        '<span class="big">0 / 10</span>'
        '<span class="bar"><i></i></span>'
        '<button class="btn" id="resetProgress">重置进度</button>'
        "</div>"
        '<div class="hint">学习进度会自动保存在本机浏览器里。</div></div>'
    )
    search = (
        '<div class="search-box">'
        '<input id="searchInput" type="text" placeholder="搜索章节关键词，如：工具、权限、上下文…" '
        'aria-label="站内搜索">'
        '</div><div id="searchResults" class="search-results"></div>'
    )
    poly_section = (
        '<section class="poly-section" aria-label="章节多面体">'
        '<div class="section-head"><h2>章节多面体</h2><span class="en">DRAG TO ROTATE · CLICK A FACE</span></div>'
        '<p class="poly-sub">十个面对应十章：完成的章节点亮成彩色，还没学的保持灰色。拖动旋转，点击任意面直接进入对应章节。</p>'
        '<div class="poly-hint"><span>拖动旋转</span><span>点击任意面进入章节</span><span>完成 = 彩色 · 未完成 = 灰色</span></div>'
        '<div class="poly-scene" id="polyScene">'
        '<div class="poly-spin" id="polySpin"><div class="poly" id="poly"></div></div>'
        '</div>'
        '</section>'
    )
    path_steps = "".join(
        f'<div class="path-step"><span class="pn">Part {p["n"]}</span><b>{esc(p["title"])}</b>'
        f'<span>{esc(p["sub"])}</span></div>' for p in PARTS)
    cards = []
    for c in CHAPTERS:
        cards.append(
            f'<a class="ch-card" href="{c["path"]}">'
            f'<span class="cn">{c["num"]} · Part {c["part"]}'
            f'<span class="tick" data-tick="{c["id"]}"></span></span>'
            f"<b>{esc(c['title'])}</b><span>{esc(c['summary'])}</span></a>")
    search_data = (
        "<script>window.__CHAPTERS__="
        + __import__("json").dumps(
            [{"num": c["num"], "title": c["title"], "summary": c["summary"],
              "keywords": c["keywords"], "path": c["path"]} for c in CHAPTERS]
            + [{"num": "拓", "title": "拓展篇 · Agent 与 Harness",
                "summary": "把十章串成两个上层概念：Agent 是什么、Harness 怎么把大脑手脚门卫记忆装成整机。",
                "keywords": "agent harness 代理外壳 子代理 subagent workflow 记忆 memory mcp hooks 多代理 拓展",
                "path": "docs/ext-ah.html"}],
            ensure_ascii=False)
        + ";</script>"
    )
    body = (
        '<section class="home-hero">'
        '<div class="kicker">SELF-STUDY · CLAUDE CODE INTERNALS</div>'
        "<h1>Claude Code 原理图解</h1>"
        '<p class="sub">用大白话讲清楚终端里的 AI 编程代理到底是怎么工作的：'
        "从一次对话的数据流，到代理循环、工具系统、权限安全、上下文管理，再到怎么读源码、怎么动手复刻。</p>"
        f"{progress}{search}{search_data}</section>"
        f"{poly_section}"
        '<script src="assets/js/poly.js"></script>'
        '<div class="content-inner" style="max-width:820px;padding-top:8px">'
        f'<div class="path-steps">{path_steps}</div>'
        '<div class="section-head"><h2>章节索引</h2><span class="en">10 CHAPTERS · 4 PARTS</span></div>'
        f'<div class="chapter-grid">{"".join(cards)}</div>'
        '<div class="section-head"><h2>拓展阅读</h2><span class="en">EXTENSION · AGENT & HARNESS</span></div>'
        '<div class="chapter-grid"><a class="ch-card" href="docs/ext-ah.html">'
        '<span class="cn">拓 · 拓展篇</span>'
        '<b>Agent 与 Harness（代理外壳）</b>'
        '<span>把十章内容串成两个上层概念：Agent 是什么、Harness 怎么把「大脑 + 手脚 + 门卫 + 记忆」'
        '装成整机。附一个可运行的迷你 Harness 代码。</span></a></div>'
        '<div class="callout"><span class="co-label">怎么学效果最好</span>'
        "建议按顺序从第 1 章读到第 10 章：前两章建立整体认知，中间四章是核心机制，"
        "接着是外围系统，最后两章带你读源码和动手复刻。每章末尾有自测题和可运行的封装代码。"
        "学完十章后，推荐再看「拓展篇 · Agent 与 Harness」，把概念串成整机。</div>"
        "</div>"
    )
    return page_shell("首页 · 学习目录", "Claude Code 基本原理的自学图解站", body, "index", "", "nav-home", with_sidebar=False)

# ---------- 术语表 ----------
GLOSSARY = [
    ("Agent Loop", "代理循环", "核心 while 循环：感知 → 决策 → 行动 → 观察，直到任务完成。", "ch03", "03", "sec-loop"),
    ("Context Window", "上下文窗口", "一次请求里模型能「看到」的全部内容上限，单位是 token。", "ch06", "06", "sec-window"),
    ("Token", "词元", "文本的最小计费/计长单位，中文大致 1 字 ≈ 1 token。", "ch06", "06", "sec-window"),
    ("Compact", "压缩", "上下文快满时把旧消息浓缩成摘要，腾出空间继续工作。", "ch06", "06", "sec-compact"),
    ("System Prompt", "系统提示", "放在最前面、约束模型身份与行为规则的那段指令。", "ch02", "02", "sec-context"),
    ("CLAUDE.md", "项目记忆文件", "放在项目根目录，每次会话自动读入上下文的项目说明。", "ch02", "02", "sec-context"),
    ("tool_use", "工具调用请求", "模型返回的「我想调用某工具」的结构化消息。", "ch04", "04", "sec-protocol"),
    ("tool_result", "工具执行结果", "工具执行完，把结果作为新消息放回上下文的动作。", "ch04", "04", "sec-protocol"),
    ("Tool Registry", "工具注册表", "「工具名 → 函数」的映射表，模型只能调用登记过的工具。", "ch04", "04", "sec-registry"),
    ("YOLO", "权限分类器", "给工具调用按危险程度分级（LOW/MEDIUM/HIGH）决定放行还是询问。", "ch05", "05", "sec-yolo"),
    ("Permission Mode", "权限模式", "default / acceptEdits / plan / bypassPermissions 四种全局策略。", "ch05", "05", "sec-modes"),
    ("allowlist / denylist", "白名单 / 黑名单", "手动指定哪些命令永远放行、哪些永远拒绝。", "ch05", "05", "sec-lists"),
    ("命令注入检查", "Command Injection Check", "在执行前检查命令是否试图绕过权限或注入危险操作。", "ch05", "05", "sec-inject"),
    ("Session", "会话", "一次对话的持久化记录，重启后可以恢复接着聊。", "ch06", "06", "sec-session"),
    ("REPL", "交互式命令行", "Read-Eval-Print Loop：读输入 → 处理 → 输出 → 再读。", "ch07", "07", "sec-repl"),
    ("Slash Command", "斜杠命令", "以 / 开头的内置指令，如 /compact、/status、/init。", "ch07", "07", "sec-slash"),
    ("Feature Flag / Gate", "特性开关", "控制某个功能开不开启的开关，常用于灰度发布。", "ch08", "08", "sec-flags"),
    ("GrowthBook / tengu_*", "灰度发布系统", "Anthropic 内部用的特性门控命名空间（tengu_*）。", "ch08", "08", "sec-gates"),
    ("anthropic-beta 头", "Beta 请求头", "HTTP 头，声明要启用的实验性 API 能力。", "ch08", "08", "sec-beta"),
    ("Source Map", "源码映射", "打包产物与原始源码的映射文件，泄露源头就在 cli.js.map。", "ch09", "09", "sec-sourcemap"),
    ("PARITY", "移植对齐", "Rust 移植版与原始行为逐项对齐的清单/思路。", "ch09", "09", "sec-parity"),
    ("Crate", "Rust 包", "Rust 的模块化单元，相当于一个库或可执行程序。", "ch09", "09", "sec-rust"),
    ("Agent", "代理", "能感知、决策、行动、观察并循环的自主程序，而不是一次性问答。", "ext-ah", "拓", "sec-agent"),
    ("Harness", "代理外壳", "除了模型本身之外的一切工程代码：循环、工具、权限、上下文、记忆、CLI 等，把模型变成能动手的 Agent。", "ext-ah", "拓", "sec-harness"),
    ("Workflow", "工作流", "步骤写死的固定流程，与运行时自主决策的 Agent 相对。", "ext-ah", "拓", "sec-agent"),
    ("Subagent", "子代理", "有独立角色与上下文的小代理，主代理把任务分包给它再回收结果。", "ext-ah", "拓", "sec-subagent"),
    ("Memory", "记忆", "Harness 给模型配的短期（上下文）与长期（CLAUDE.md、会话文件）记忆。", "ext-ah", "拓", "sec-memory"),
    ("Hook", "钩子", "在固定时机（如工具调用前后）触发外部脚本的机制，让 Harness 行为可编程。", "ext-ah", "拓", "sec-hooks"),
    ("MCP", "模型上下文协议", "接入外部工具 / 数据源的标准协议，相当于 Harness 的「万能插口」。", "ext-ah", "拓", "sec-hooks"),
]

def build_glossary():
    items = []
    for term, zh, desc, ch_id, num, anchor in GLOSSARY:
        label = f"第 {num} 章 →" if num.isdigit() else "拓展篇 →"
        items.append(
            '<div class="glossary-term"><div class="gt-head">'
            f"<code>{esc(term)}</code><b>{esc(zh)}</b>"
            f'<a class="gt-ch" href="docs/{ch_id}.html#{anchor}">{label}</a>'
            f"</div><p>{esc(desc)}</p></div>")
    body = (
        '<div class="hero"><div class="chapter-tag">QUICK REFERENCE</div>'
        "<h1>核心术语表</h1>"
        '<p class="goal">看文章时遇到看不懂的词，来这里查。每个术语一句话解释，并指向详细章节。</p></div>'
        f'<div class="glossary-list">{"".join(items)}</div>'
    )
    return page_shell("核心术语表", "Claude Code 核心术语速查", body, "glossary", "", "nav-glossary")

# ---------- 代码库 ----------
def build_toolbox():
    modules = [
        {"file": "mini_agent.py", "ch": "ch01", "ch_num": "01", "ch_title": "认识 Claude Code",
         "desc": "认识「代理」的最小雏形：一个读目标 → 决定 → 动手 → 看结果的循环骨架。",
         "run": ["python mini_agent.py"]},
        {"file": "agent_loop.py", "ch": "ch03", "ch_num": "03", "ch_title": "代理循环 Agent Loop",
         "desc": "最小可运行的代理循环：模拟模型返回工具调用，循环执行直到完成。",
         "run": ["python agent_loop.py"]},
        {"file": "tools.py", "ch": "ch04", "ch_num": "04", "ch_title": "工具系统",
         "desc": "工具注册表 + 调度器：工具 = 名字 + 说明 + 函数，模型只能调用登记过的工具。",
         "run": ["python tools.py"]},
        {"file": "permissions.py", "ch": "ch05", "ch_num": "05", "ch_title": "权限与安全",
         "desc": "YOLO 式风险分级器骨架：按命令危险程度决定放行 / 询问 / 拒绝。",
         "run": ["python permissions.py"]},
        {"file": "session.py", "ch": "ch06", "ch_num": "06", "ch_title": "会话与上下文管理",
         "desc": "会话保存 / 恢复的最小实现：把消息历史序列化成 JSON 存盘，下次读回来。",
         "run": ["python session.py"]},
        {"file": "context_manager.py", "ch": "ch06", "ch_num": "06", "ch_title": "会话与上下文管理",
         "desc": "token 估算 + 压缩触发：计算上下文占用，超过阈值自动把旧消息压成摘要。",
         "run": ["python context_manager.py"]},
        {"file": "cli_repl.py", "ch": "ch07", "ch_num": "07", "ch_title": "CLI 与斜杠命令",
         "desc": "极简交互式 REPL：提示符 → 读输入 → 解析斜杠命令 → 响应 → 循环。",
         "run": ["python cli_repl.py"]},
        {"file": "config.py", "ch": "ch08", "ch_num": "08", "ch_title": "配置、环境变量与特性门控",
         "desc": "环境变量解析 + 特性开关：用环境变量覆盖默认值，控制功能开不开。",
         "run": ["python config.py", "CLAUDECODE_COORDINATOR_MODE=1 python config.py"]},
        {"file": "codex_bridge.py", "ch": "ch10", "ch_num": "10", "ch_title": "自学路线图与实践建议",
         "desc": "本机 Codex 直连桥接服务：让网站的「问 Codex」窗口真正调用本机 Codex CLI（只读沙箱，仅本机流转）。",
         "run": ["python tools\\codex_bridge.py", "powershell -ExecutionPolicy Bypass -File tools\\start_bridge.ps1"],
         "path": ROOT / "tools" / "codex_bridge.py"},
        {"file": "harness.py", "ch": "ext", "ch_num": "拓", "ch_title": "Agent 与 Harness",
         "page": "docs/ext-ah.html",
         "desc": "迷你 Agent Harness：把大脑（模型）+ 手脚（工具）+ 门卫（权限）+ 记忆（会话）串成一个可运行的最小脚手架，正文第 2–8 章一次串起来。",
         "run": ["python harness.py"]},
    ]
    cards = []
    for m in modules:
        run = "".join(f'<kbd>{esc(r)}</kbd>' for r in m["run"])
        cards.append(
            f'<div class="tool-card" data-ch="{m["ch"]}">'
            '<div class="tc-head">'
            f'<code>{esc(m["file"])}</code>'
            + f'<a class="tc-ch" href="{m.get("page", "docs/" + m["ch"] + ".html")}">'
            + (f'第 {m["ch_num"]} 章 · ' if str(m["ch_num"]).isdigit() else "拓展篇 · ")
            + f'{esc(m["ch_title"])} →</a>'
            f'</div><p class="tc-desc">{esc(m["desc"])}</p>'
            f'<div class="runsteps">运行：{run}</div>'
            f'{code_figure(m["file"], "python", path=m.get("path"))}</div>')
    body = (
        '<div class="hero"><div class="chapter-tag">CODE LAB · READY TO RUN</div>'
        "<h1>代码库</h1>"
        '<p class="goal">全部封装好的零依赖 Python 模块，复制或下载即可运行。'
        "每个模块对应一个章节的原理，注释里写清了「为什么这样写」。</p></div>"
        '<div class="tool-filter">'
        '<select id="toolFilterChapter" aria-label="按章节筛选">'
        '<option value="all">全部章节</option>'
        '<option value="ch01">第 01 章</option><option value="ch03">第 03 章</option>'
        '<option value="ch04">第 04 章</option><option value="ch05">第 05 章</option>'
        '<option value="ch06">第 06 章</option><option value="ch07">第 07 章</option>'
        '<option value="ch08">第 08 章</option><option value="ch10">第 10 章</option>'
        '<option value="ext">拓展篇</option>'
        "</select>"
        '<input id="toolFilterText" type="text" placeholder="输入关键词筛选…" aria-label="按关键词筛选">'
        "</div>"
        f'{"".join(cards)}'
    )
    return page_shell("代码库 · 随时调用", "Claude Code 原理配套封装代码", body, "toolbox", "", "nav-toolbox")

# ---------- 关于页 ----------
def build_about():
    body = (
        '<div class="hero"><div class="chapter-tag">ABOUT</div>'
        "<h1>关于本站</h1>"
        '<p class="goal">这个站是给自学者准备的 Claude Code 原理图解，目标是「看得懂、跑得起来、能自己动手」。'
        "</p></div>"
        '<h2 id="s1"><span class="h2-num">/</span>内容来源</h2>'
        "<ul>"
        "<li><a href=\"https://ccleaks.com/leaks\">ccleaks.com/leaks</a> —— 对 Claude Code 公开源码的分析汇总："
        "8 个未发布特性、26 个隐藏命令、32 个构建开关、120+ 环境变量等。</li>"
        "<li><a href=\"https://github.com/ultraworkers/claw-code\">ultraworkers/claw-code</a> —— 用 Rust 重实现的 "
        "Claude Code CLI 移植项目，作为「如何复刻」的对照样例。</li>"
        "</ul>"
        '<h2 id="s2"><span class="h2-num">/</span>免责声明</h2>'
        "<p>本站内容基于上述公开资料的整理与学习用途的再解读，<strong>信息可能不准确或已过时</strong>。"
        "本站不隶属于 Anthropic，也不对任何泄露源码的获取渠道负责。"
        "涉及「泄露」的内容统一表述为「公开源码分析」，请在遵守当地法律与版权规定的前提下学习。</p>"
        '<h2 id="s3"><span class="h2-num">/</span>技术说明</h2>'
        "<ul>"
        "<li>纯静态站点：零依赖、无构建、无 CDN，断网可读，可双击打开或部署到 GitHub Pages。</li>"
        "<li>学习进度、深浅主题、字号、阅读位置只保存在本机浏览器 localStorage，不上传。</li>"
        "<li>代码库模块为 Python 3 零依赖实现，复制或下载即可运行。</li>"
        "<li>「问 Codex」窗口通过本机桥接服务调用本机 Codex CLI（只读沙箱），问题与回答仅在本机流转。</li>"
        "<li>「拓展篇 · Agent 与 Harness」独立于 10 章正文，用于把十章内容串成 Agent / Harness 两个上层概念，并附可运行的迷你 Harness 代码。</li>"
        "</ul>"
        '<h2 id="s4"><span class="h2-num">/</span>致谢</h2>'
        "<p>感谢 ccleaks 的资料整理与 claw-code 的开源移植，为中文自学者提供了难得的学习素材。</p>"
    )
    return page_shell("关于本站", "Claude Code 原理图解 · 关于与免责声明", body, "about", "", "nav-about")
# ================= 第 1 章 =================
CH01 = {"blocks": [
    ("h2", "它是什么：请了个会操作电脑的实习生", "sec-what"),
    ("p", "Claude Code 是一个跑在**终端**里的 AI 编程代理。你把一个目标丢给它，比如「帮我修好这个 bug」，它不会只回你一段话，而是会自己：读文件 → 找原因 → 改代码 → 跑测试 → 告诉你结果。就像请了一个**会操作你电脑的实习生**：你负责下指令，它负责动手。"),
    ("callout", "tip", "打个比方", "普通聊天机器人像「只会说的顾问」——你说什么它答什么；Claude Code 像「会动手的同事」——你说目标，它自己拆解、执行、检查、汇报。"),
    ("h2", "和聊天机器人 / IDE 插件的区别", "sec-compare"),
    ("p", "同样是 AI，为什么 Claude Code 能「动手」？因为它有**工具**，而且有权限调用这些工具（读文件、跑命令、改代码）。下面这张表对比三者的本质差别："),
    ("table", ["维度", "聊天机器人", "IDE 插件", "Claude Code"],
      [["运行位置", "网页 / App", "编辑器里", "终端里"],
       ["能不能动你的电脑", "不能", "只能改当前文件", "能：读文件、跑命令、改代码"],
       ["工作方式", "一问一答", "补全 / 片段", "自主执行一个循环"],
       ["适合场景", "查资料、闲聊", "写代码时的辅助", "完整跑一个开发任务"]]),
    ("h2", "核心体验：你定目标，它跑循环", "sec-feel"),
    ("steps", [
      ("你只做两件事", "说出目标；在关键节点批准或纠正它。"),
      ("它做剩下的事", "读取项目文件、理解现状、制定步骤、调用工具执行、检查结果、遇到问题自己调整。"),
      ("全程可见", "每一步做了什么、跑了什么命令，都在终端里清清楚楚。"),
    ]),
    ("h2", "先看一个最小雏形", "sec-mini"),
    ("p", "下面这个 Python 文件只有几十行，但已经包含了「代理」的全部骨架：一个循环，反复「想下一步 → 动手 → 看结果」。先运行它感受一下，第 3 章会把循环讲透。"),
    ("code", "mini_agent.py", "python", None),
    ("h2", "后面会讲什么", "sec-preview"),
    ("ul", [
      "第 2 章：一次对话从输入到输出的完整数据流",
      "第 3 章：代理循环（心脏）",
      "第 4–6 章：工具、权限、上下文（三大支柱）",
      "第 7–8 章：命令行界面、配置与特性开关",
      "第 9–10 章：怎么读源码、怎么自己复刻",
    ]),
    ("quiz", [
      {"q": "Claude Code 和普通聊天机器人最本质的区别是什么？", "opts": [("A", "它跑得更快"), ("B", "它能通过工具操作你的电脑"), ("C", "它不需要网络")], "ans": "B",
       "explain": "聊天机器人只能「说」，Claude Code 能「做」——通过工具读文件、跑命令、改代码。", "back": ("它是什么", "sec-what")},
      {"q": "「代理（Agent）」这个词强调的是？", "opts": [("A", "它能自主执行多步循环直到完成"), ("B", "它只是一个输入输出接口"), ("C", "它一定在云端运行")], "ans": "A",
       "explain": "代理 = 能感知、决策、行动、观察并循环的自主程序，而不是一次性的问答。", "back": ("核心体验", "sec-feel")},
      {"q": "Claude Code 和 IDE 插件最本质的区别是？", "opts": [("A", "它运行在终端里，能自主调用工具跑完整开发任务"), ("B", "它没有图形界面"), ("C", "它不需要任何模型")], "ans": "A",
       "explain": "IDE 插件偏「补全 / 片段」式辅助，Claude Code 在终端里自主执行整个代理循环。", "back": ("和 IDE 插件的区别", "sec-compare")},
    ]),
    ("summary", [
      "Claude Code 是终端里的 AI 编程代理：你说目标，它动手。",
      "区别在于「工具 + 权限」：它真的能操作你的电脑。",
      "它的工作方式是循环：目标 → 拆解 → 执行 → 检查 → 汇报。",
    ]),
]}

# ================= 第 2 章 =================
CH02 = {"blocks": [
    ("h2", "全景图：一次对话发生了什么", "sec-journey"),
    ("p", "把「你按下回车」到「它给出答案」之间的过程拆开，一共是七步。别被术语吓到，跟着走一遍就懂："),
    ("steps", [
      ("启动 CLI", "你在终端输入 `claude \"帮我看看这个项目\"`，程序开始运行。"),
      ("装载上下文", "它把「系统提示 + CLAUDE.md + 会话历史 + 工具定义」拼成一段很长的输入。"),
      ("发出请求", "把这段输入发给 Anthropic 的 API（一个 HTTP 请求）。"),
      ("流式响应", "API 返回的内容一部分是文字，一部分是「我想调用某个工具」的请求。"),
      ("执行工具", "程序在本地执行工具（读文件、跑命令），把结果拿回来。"),
      ("循环", "把工具结果加进上下文，再次发请求……直到模型觉得任务完成。"),
      ("输出答案", "把最终的文字结果展示给你。"),
    ]),
    ("callout", "note", "记住这一句", "**API 本身是无状态的**：它不记得你，是 Claude Code 在本地负责「记住」并把整个历史每次重新发给它。上下文由客户端组装，这是理解后面一切的关键。"),
    ("h2", "上下文 = 它这次能「看到」的一切", "sec-context"),
    ("p", "每次请求，Claude Code 都会把下面这些东西**拼在一起**发给 API："),
    ("ul", [
      "**系统提示（System Prompt）**：约束行为规则的「人设」，比如「你是 Claude Code，一个高效的编程助手」。",
      "**CLAUDE.md**：项目根目录里的说明文件，相当于给代理的「项目入职手册」。",
      "**会话历史**：之前的所有对话和工具结果。",
      "**工具定义**：每个可用工具的「名字 + 说明 + 参数格式」（JSON Schema）。",
    ]),
    ("h2", "怎么启动它", "sec-start"),
    ("p", "启动方式很简单（注意：Claude Code 需要 API Key 而不是订阅账号登录）："),
    ("envtabs", [
      ("pwsh", "PowerShell", "bash", "$env:ANTHROPIC_API_KEY = \"sk-ant-...\"\nclaude \"帮我看看这个项目\""),
      ("mac", "macOS", "bash", "export ANTHROPIC_API_KEY=\"sk-ant-...\"\nclaude \"帮我看看这个项目\""),
      ("linux", "Linux", "bash", "export ANTHROPIC_API_KEY=\"sk-ant-...\"\nclaude \"帮我看看这个项目\""),
    ]),
    ("h2", "一次请求长什么样", "sec-request"),
    ("p", "简化后的 API 请求就是「把上下文发给服务器」："),
    ("code", None, "json", r'''{
  "model": "claude-opus-4-6",
  "system": "你是 Claude Code，一个高效的编程助手……",
  "messages": [
    {"role": "user", "content": "帮我看看这个项目"},
    {"role": "assistant", "content": "好的，我先读取项目结构……"}
  ],
  "tools": [
    {"name": "read_file", "description": "读取文件内容", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}}}
  ]
}'''),
    ("callout", "warn", "注意", "上下文越长，费用越高、响应越慢。所以后面第 6 章会讲怎么「省着用」——压缩、裁剪、预算管理，这是 Claude Code 的重要工程。"),
    ("h2", "这一章的收获", "sec-takeaway"),
    ("ul", [
      "一次对话 = 多次请求的循环，而不是一次请求。",
      "每次请求都重新发送完整上下文（客户端组装）。",
      "上下文里包含：系统提示、CLAUDE.md、历史、工具定义。",
    ]),
    ("quiz", [
      {"q": "API 服务器记得你和 Claude Code 之前的对话吗？", "opts": [("A", "记得，服务器有记忆"), ("B", "不记得，状态在客户端，历史每次重新发送")], "ans": "B",
       "explain": "API 是无状态的，Claude Code 在本地保存历史并每次组装进上下文。", "back": ("全景图", "sec-journey")},
      {"q": "下面哪一项**不属于**组装进上下文的？", "opts": [("A", "系统提示"), ("B", "CLAUDE.md"), ("C", "你的浏览器历史"), ("D", "工具定义")], "ans": "C",
       "explain": "上下文 = 系统提示 + CLAUDE.md + 会话历史 + 工具定义，跟浏览器历史无关。", "back": ("上下文", "sec-context")},
      {"q": "为什么上下文越长，响应越慢、费用越高？", "opts": [("A", "模型每次都要重新处理全部输入 token"), ("B", "因为网络速度变慢了"), ("C", "因为输出会变长")], "ans": "A",
       "explain": "每次请求都完整重发上下文，模型要处理全部输入 token，所以越长越慢越贵。", "back": ("一次请求", "sec-request")},
    ]),
    ("summary", [
      "一次对话是一连串「发请求 → 收响应 → 执行工具 → 再发请求」的循环。",
      "上下文在客户端组装，每次请求完整重发。",
      "上下文四件套：系统提示、CLAUDE.md、会话历史、工具定义。",
    ]),
]}

# ================= 第 3 章 =================
CH03 = {"blocks": [
    ("h2", "核心：一个 while 循环", "sec-loop"),
    ("p", "Claude Code 的心脏非常朴素——一个 `while` 循环。翻译成大白话就是：**只要还没干完，就一直干下去**。每一次循环做四件事："),
    ("steps", [
      ("感知", "看看当前状态：任务是什么、已经做到哪一步、上一步的结果是什么。"),
      ("决策", "把状态交给模型，让模型决定下一步：继续说、还是调用工具。"),
      ("行动", "如果要调用工具，就在本地执行它。"),
      ("观察", "把工具结果放回上下文，回到第 1 步。"),
    ]),
    ("p", "用伪代码写出来就是这样（注意 `while` 和 `continue`）："),
    ("code", None, "python", r'''while 任务未完成:
    状态 = 收集当前上下文          # 感知
    决定 = 模型(状态)             # 决策
    if 决定是普通文本:
        输出给用户, 结束          # 完成
    if 决定是调用工具:
        结果 = 执行工具(决定)     # 行动
        把结果放回上下文          # 观察
    # 回到 while，继续下一轮'''),
    ("demo", "loop"),
    ("h2", "为什么它叫「代理」而不是「问答」", "sec-why"),
    ("p", "聊天机器人只执行**一次**「输入 → 输出」。代理把这个过程**循环**起来，并且每一步都能**观察结果再决定下一步**——所以它能处理多步骤、需要动手的任务。有没有工具、能不能循环，是代理和聊天的分水岭。"),
    ("h2", "什么时候结束：终止条件", "sec-end"),
    ("p", "循环不能永远跑下去，Claude Code 靠三种方式结束："),
    ("ul", [
      "**模型主动结束**：模型返回普通文本（不再要求调用工具），认为任务完成。",
      "**达到上限**：步数上限、token 预算用尽，强制停止。",
      "**用户打断**：Ctrl+C 或输入 `/quit` 退出。",
    ]),
    ("h2", "跑一个真实的「最小循环」", "sec-run"),
    ("p", "`agent_loop.py` 把这个循环真实地跑给你看：`mock_model()` 模拟「模型」返回工具调用，`TOOLS` 模拟「工具表」，主循环负责把它们串起来："),
    ("code", "agent_loop.py", "python", None),
    ("callout", "tip", "动手试", "把 `agent_loop.py` 下载下来运行，观察终端输出：先调 `read_file`，再调 `bash`，最后模型认为完成、输出文字结束。这就是代理循环的最小形态。"),
    ("quiz", [
      {"q": "代理循环每一步的顺序是？", "opts": [("A", "决策 → 感知 → 行动 → 观察"), ("B", "感知 → 决策 → 行动 → 观察"), ("C", "行动 → 观察 → 感知 → 决策")], "ans": "B",
       "explain": "先感知当前状态，再决策下一步，然后行动（调用工具），最后观察结果，回到循环。", "back": ("核心", "sec-loop")},
      {"q": "循环什么时候正常结束？", "opts": [("A", "模型返回普通文本不再调用工具"), ("B", "永远不结束"), ("C", "每轮固定执行 100 次")], "ans": "A",
       "explain": "模型认为任务完成、返回普通文本时结束；另有步数/token 上限和用户打断等兜底。", "back": ("终止条件", "sec-end")},
      {"q": "代理和聊天机器人的「分水岭」是什么？", "opts": [("A", "能不能循环、有没有工具"), ("B", "界面颜色不一样"), ("C", "模型参数更多")], "ans": "A",
       "explain": "聊天只做一次「输入 → 输出」；代理把过程循环起来并能观察结果再决定下一步。", "back": ("为什么叫代理", "sec-why")},
    ]),
    ("summary", [
      "代理循环 = while 循环：感知 → 决策 → 行动 → 观察。",
      "能不能循环、有没有工具，是代理与聊天的分水岭。",
      "结束方式：模型主动结束 / 达到上限 / 用户打断。",
    ]),
]}

# ================= 第 4 章 =================
CH04 = {"blocks": [
    ("h2", "工具 = 函数 + 说明", "sec-basic"),
    ("p", "对 Claude Code 来说，一个工具就是三样东西：**名字**（怎么称呼它）、**说明**（什么时候用它、怎么用）、**函数**（真正干活的代码）。模型看到的不是代码，而是「说明书」——一段 JSON："),
    ("code", None, "json", r'''{
  "name": "read_file",
  "description": "读取指定文件的全部内容",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {"type": "string", "description": "要读取的文件路径"}
    },
    "required": ["path"]
  }
}'''),
    ("p", "模型读到这份「说明书」，就知道：有个工具叫 `read_file`，用来读文件，需要传一个 `path` 参数。**它不直接调用函数，它只是「请求」调用。**"),
    ("h2", "工具注册表：只能调用登记过的", "sec-registry"),
    ("p", "程序内部维护一张「工具名 → 函数」的表（叫**注册表**）。模型发来 `tool_use` 请求后，程序查表、校验参数、执行、返回结果。查不到就报错，绝不静默。这就是为什么模型永远无法调用你没给它的工具。"),
    ("h2", "调用协议：tool_use 和 tool_result", "sec-protocol"),
    ("p", "模型和程序之间的「工具对话」只有两种消息，像一个接力棒："),
    ("steps", [
      ("模型发出 tool_use", "模型说：「我要调用 read_file，参数是 path=notes.txt」。"),
      ("程序执行工具", "程序在本地真实执行，拿到结果。"),
      ("程序回填 tool_result", "把结果作为一条新消息放回上下文。"),
      ("模型继续", "模型看到结果，决定下一步：继续调用工具，还是结束。"),
    ]),
    ("code", None, "json", r'''// 模型 → 程序：请求调用工具
{"type": "tool_use", "id": "toolu_01", "name": "read_file", "input": {"path": "notes.txt"}}

// 程序 → 模型：回填执行结果
{"type": "tool_result", "tool_use_id": "toolu_01", "content": "今天要买牛奶、写周报"}'''),
    ("h2", "内置工具长什么样", "sec-builtin"),
    ("table", ["工具", "作用", "风险等级"],
      [["Bash", "执行 shell 命令（跑测试、装依赖、操作文件）", "高"],
       ["Read", "读取文件内容", "低"],
       ["Write", "写入 / 覆盖文件", "中"],
       ["Edit", "精准修改文件中的一段", "中"],
       ["Grep / Glob", "搜索文本 / 按模式找文件", "低"],
       ["WebFetch", "抓取网页内容", "低"]]),
    ("h2", "权限拦在哪一步", "sec-gate"),
    ("p", "注意流程里的**闸门**：模型发出 `tool_use` 请求后，程序**不会立刻执行**，而是先过一道**权限检查**（第 5 章详细讲）。只有被允许的工具调用才会真正执行——这是安全设计的核心。"),
    ("code", "tools.py", "python", None),
    ("quiz", [
      {"q": "模型直接调用工具函数吗？", "opts": [("A", "直接调用"), ("B", "只发请求，由程序查表执行"), ("C", "模型自己写代码执行")], "ans": "B",
       "explain": "模型只发 tool_use 请求；程序负责查注册表、校验、执行、回填结果。", "back": ("调用协议", "sec-protocol")},
      {"q": "「工具注册表」的作用是？", "opts": [("A", "限制模型只能调用登记过的工具"), ("B", "给工具排序"), ("C", "记录谁用了工具")], "ans": "A",
       "explain": "注册表是「工具名 → 函数」的映射，模型无法调用没登记的工具。", "back": ("注册表", "sec-registry")},
      {"q": "模型拿到工具时，实际「看到」的是什么？", "opts": [("A", "一份 JSON 说明书：名字 + 说明 + 参数格式"), ("B", "工具的全部 Python 源码"), ("C", "数据库里的调用记录")], "ans": "A",
       "explain": "模型看到的是 JSON Schema 说明书，不是实现代码；执行由程序在本地完成。", "back": ("工具 = 函数 + 说明", "sec-basic")},
    ]),
    ("summary", [
      "工具 = 名字 + 说明书（JSON Schema）+ 函数。",
      "模型只发 tool_use 请求，程序查注册表执行并回填 tool_result。",
      "工具调用前要先过权限闸门。",
    ]),
]}

# ================= 第 5 章 =================
CH05 = {"blocks": [
    ("h2", "问题：Claude 凭什么能跑我的命令？", "sec-problem"),
    ("p", "工具给了 Claude Code 操作你电脑的能力，但能力越大责任越大：它跑 `rm -rf` 怎么办？所以每个工具调用在真正执行前，都要过**权限检查**。这套系统的核心是两样东西：**权限模式**和 **YOLO 分类器**。"),
    ("h2", "四种权限模式", "sec-modes"),
    ("table", ["模式", "行为", "适用"],
      [["default（默认）", "低风险自动执行，中高风险问你", "日常使用"],
       ["acceptEdits", "文件编辑类自动接受，命令仍要问", "写代码为主"],
       ["plan", "只规划、不执行任何工具", "先讨论方案"],
       ["bypassPermissions", "跳过全部确认直接执行", "完全信任的场景（危险）"]]),
    ("h2", "YOLO：给风险分级", "sec-yolo"),
    ("p", "YOLO 是代码里的一个分类器（函数名 `classifyYoloAction`）：把每个工具调用按危险程度分成 `LOW / MEDIUM / HIGH` 三档，再决定："),
    ("ul", [
      "**LOW**（如读文件）→ 直接放行，不打扰你。",
      "**MEDIUM**（如改文件）→ 弹窗问你一句。",
      "**HIGH**（如 `rm -rf`）→ 拒绝或强烈确认。",
    ]),
    ("p", "下面这个交互演示，带你走一遍完整决策流程："),
    ("demo", "tree"),
    ("h2", "allowlist / denylist：手动写死的规则", "sec-lists"),
    ("p", "除了自动分级，你还可以手动指定规则。在 `~/.claude/settings.json` 里配置："),
    ("code", None, "json", r'''{
  "permissions": {
    "allow": [
      "Bash(git status:*)",        // 白名单：git status 永远放行
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(rm -rf:*)",            // 黑名单：rm -rf 永远拒绝
      "Bash(shutdown:*)"
    ]
  }
}'''),
    ("h2", "命令注入检查：防止「披着羊皮的狼」", "sec-inject"),
    ("p", "还有一种攻击叫**命令注入**：看起来在跑安全命令，实际夹带了危险操作，比如 `ls; rm -rf /`。Claude Code 会在执行前检查命令内容，识别这类绕过手段。源码里甚至有 `DISABLE_COMMAND_INJECTION_CHECK` 这样的开关——默认开着，关掉非常危险。"),
    ("code", "permissions.py", "python", None),
    ("callout", "warn", "安全底线", "权限系统是「默认信任 + 分级确认」，不是万能保险。永远不要在 `bypassPermissions` 下跑不确定的命令，也不要把 API Key 交给不信任的来源。"),
    ("quiz", [
      {"q": "「YOLO 分类器」主要做什么？", "opts": [("A", "给工具调用按风险分级并决定放行/询问/拒绝"), ("B", "给代码提速"), ("C", "压缩上下文")], "ans": "A",
       "explain": "classifyYoloAction 把调用分为 LOW/MEDIUM/HIGH 三档，对应自动放行、询问、拒绝。", "back": ("YOLO", "sec-yolo")},
      {"q": "在 plan 模式下，模型能执行 Bash 工具吗？", "opts": [("A", "能，但会先问你"), ("B", "不能，只规划不执行"), ("C", "取决于命令长短")], "ans": "B",
       "explain": "plan 模式拒绝执行任何工具，只输出计划等你批准。", "back": ("权限模式", "sec-modes")},
      {"q": "allowlist / denylist（白/黑名单）的作用是？", "opts": [("A", "手动写死规则：名单内放行、名单外拒绝"), ("B", "让所有命令都必须确认"), ("C", "提高模型的推理速度")], "ans": "A",
       "explain": "除了自动风险分级，你还可以在 settings.json 里手动指定永远放行或永远拒绝的规则。", "back": ("allowlist / denylist", "sec-lists")},
    ]),
    ("summary", [
      "权限模式：default / acceptEdits / plan / bypassPermissions。",
      "YOLO 分类器按风险分级：LOW 放行、MEDIUM 询问、HIGH 拒绝。",
      "allowlist/denylist 手动写死规则；命令注入检查默认开启。",
    ]),
]}

CHAPTER_CONTENT = {"ch01": CH01, "ch02": CH02, "ch03": CH03, "ch04": CH04, "ch05": CH05}# ================= 第 6 章 =================
CH06 = {"blocks": [
    ("h2", "会话：把对话「存下来」", "sec-session"),
    ("p", "Claude Code 每次对话都被保存成**会话（Session）**：包含了消息历史、工具结果、当前目录等信息。下次你想接着聊，一条命令就能恢复——这就是 `claude --resume` 背后做的事。"),
    ("p", "会话文件存在**本地**，而不是云端。所以换一台电脑、删掉目录，历史就没了。它的实现原理很简单：**把消息序列化存成文件，用时再读回来**。下面这个模块就是最小版本："),
    ("code", "session.py", "python", None),
    ("table", ["会话里存了什么", "说明", "例子"],
      [["消息历史", "你说了什么、模型回了什么", "user / assistant / tool 消息"],
       ["工具结果", "工具执行后的输出", "文件内容、命令输出"],
       ["元信息", "会话 id、当前目录、模型", "session-20260829-xxx"]]),
    ("callout", "note", "关键点", "**会话是「记忆的外壳」，上下文是「每次请求实际发出去的内容」**。会话负责持久化，上下文负责每一次请求，别把两者搞混。"),
    ("h2", "上下文窗口：一次能「看到」多少", "sec-window"),
    ("p", "模型的输入有上限，这个上限叫**上下文窗口（Context Window）**。Claude 的模型支持 200K 甚至 1M token 的窗口——听起来很大，但代码、日志、历史消息加起来很快就满了。"),
    ("table", ["窗口", "大约相当于", "够做什么"],
      [["200K tokens", "一本 400–600 页的书", "中等项目：读几个文件 + 多轮修改"],
       ["1M tokens", "两三本《战争与和平》", "大仓库：整库检索 + 长会话"]]),
    ("p", "上下文里的每个字都要花钱（按 token 计费），而且越长响应越慢。所以 Claude Code 必须精打细算：**尽量少带、必要时压缩**。"),
    ("p", "怎么估算 token？粗略规则：中文约 1 字 ≈ 1 token，英文约 4 字符 ≈ 1 token。下面这个模块演示「估算 + 超阈值自动压缩」："),
    ("code", "context_manager.py", "python", None),
    ("h2", "快满了怎么办：压缩 Compact", "sec-compact"),
    ("p", "当上下文快满时，Claude Code 会触发**压缩（Compact）**：把最早的一部分消息交给模型浓缩成一段摘要，替换掉原文，腾出空间继续干活。"),
    ("ul", [
      "**auto-compact**：达到阈值自动压缩，不用你操心。",
      "**/compact 命令**：手动触发压缩。",
      "**history-snip**：把超长的旧消息截断 / 精简。",
      "**context collapse**：极端情况下把整体浓缩成一句话摘要（细节会丢失）。",
    ]),
    ("p", "压缩的本质是**用细节换空间**：旧内容变成「还记得做过 X」的摘要，具体细节就没了。这也是为什么超长会话做复杂任务容易「失忆」。拖动下面的滑块感受一下阈值逻辑："),
    ("demo", "ctx"),
    ("quiz", [
      {"q": "会话（Session）和上下文（Context）的关系是？", "opts": [("A", "完全一样的东西"), ("B", "会话负责持久化存储，上下文负责每次请求的内容"), ("C", "上下文存在云端")], "ans": "B",
       "explain": "会话是「外壳」，把对话存到本地；上下文是每次请求实际发给模型的全部内容。", "back": ("会话", "sec-session")},
      {"q": "上下文快满时，auto-compact 会做什么？", "opts": [("A", "直接报错停止"), ("B", "把旧消息浓缩成摘要腾出空间"), ("C", "换更大的模型")], "ans": "B",
       "explain": "压缩把早期消息变成摘要，用细节换空间，让对话继续。", "back": ("压缩", "sec-compact")},
      {"q": "会话文件存在哪里？", "opts": [("A", "本地磁盘，换电脑或删目录就没了"), ("B", "Anthropic 云端"), ("C", "浏览器缓存")], "ans": "A",
       "explain": "会话序列化存在本地，负责持久化；上下文才是每次请求发出去的内容。", "back": ("会话", "sec-session")},
    ]),
    ("summary", [
      "会话把对话持久化到本地，重启后可恢复接着聊。",
      "上下文窗口是稀缺资源：200K / 1M token，越长越贵越慢。",
      "快满了就压缩：auto-compact、/compact、history-snip。",
    ]),
]}

# ================= 第 7 章 =================
CH07 = {"blocks": [
    ("h2", "REPL：你看到的最小界面", "sec-repl"),
    ("p", "你在终端里和 Claude Code 交互的那个输入框，本质上是一个 **REPL**：Read（读输入）→ Eval（处理）→ Print（输出）→ Loop（循环）。它并不神秘——就是一个 `while` 循环里反复「读一行输入 → 处理 → 打印结果」。"),
    ("code", "cli_repl.py", "python", None),
    ("p", "运行 `python cli_repl.py`，输入 `hello`、`/help`、`/status`、`/quit` 感受一下。你会发现：**斜杠命令和普通对话走的是两条分支**。"),
    ("h2", "启动方式与常用参数", "sec-launch"),
    ("p", "第一次使用会引导你登录（Anthropic 账号或 API Key），并把选择写入配置。常用的启动方式："),
    ("envtabs", [
      ("pwsh", "PowerShell", "bash", "# 交互模式\nclaude\n# 直接给任务\nclaude \"帮我重构这个模块\"\n# 继续上次会话\nclaude --resume"),
      ("mac", "macOS", "bash", "# 交互模式\nclaude\n# 直接给任务\nclaude \"帮我重构这个模块\"\n# 继续上次会话\nclaude --resume"),
      ("linux", "Linux", "bash", "# 交互模式\nclaude\n# 直接给任务\nclaude \"帮我重构这个模块\"\n# 继续上次会话\nclaude --resume"),
    ]),
    ("h2", "斜杠命令：内置指令", "sec-slash"),
    ("p", "在 REPL 里输入以 `/` 开头的命令，就会触发内置指令。常见的公开命令有这些："),
    ("table", ["命令", "作用", "说明"],
      [["/help", "查看帮助", "列出全部命令"],
       ["/init", "初始化项目", "生成 CLAUDE.md"],
       ["/compact", "压缩上下文", "手动触发压缩（第 6 章）"],
       ["/status", "查看会话状态", "会话信息、上下文占用"],
       ["/context", "查看上下文", "当前上下文里有什么"],
       ["/model", "切换模型", "选择 opus / sonnet 等"],
       ["/config", "打开配置", "编辑 settings.json"],
       ["/doctor", "自检", "检查安装和环境"]]),
    ("callout", "tip", "冷知识", "公开源码分析里发现了 **26 个隐藏斜杠命令**——它们没有出现在帮助文档里，属于内部 / 实验功能，比如 `/statusline`（自定义状态栏）、`/buddy`（宠物彩蛋）等。命令本身未必都能用，但能看出团队在实验什么。"),
    ("quiz", [
      {"q": "REPL 中的「L」代表什么？", "opts": [("A", "Loop——循环，读完处理完再读"), ("B", "Language"), ("C", "Line")], "ans": "A",
       "explain": "Read-Eval-Print-Loop：读、处理、输出、循环，是交互式命令行的基本形态。", "back": ("REPL", "sec-repl")},
      {"q": "隐藏斜杠命令和普通命令的区别是？", "opts": [("A", "隐藏命令没写在公开帮助里，多为内部 / 实验功能"), ("B", "隐藏命令一定不能用"), ("C", "隐藏命令运行更快")], "ans": "A",
       "explain": "26 个隐藏命令不显示在帮助文档中，属于内部实验功能。", "back": ("斜杠命令", "sec-slash")},
      {"q": "斜杠命令和普通对话在 REPL 里是什么关系？", "opts": [("A", "走两条不同的分支：/ 开头触发内置指令，其余走对话"), ("B", "完全一样，没区别"), ("C", "斜杠命令不经过 REPL")], "ans": "A",
       "explain": "REPL 读入一行后先判断是否以 / 开头，分别进入指令分支或对话分支。", "back": ("斜杠命令", "sec-slash")},
    ]),
    ("summary", [
      "交互界面 = REPL：读输入 → 处理 → 输出 → 循环。",
      "斜杠命令和普通对话走不同分支，/ 开头触发内置指令。",
      "公开分析发现 26 个隐藏命令，多为实验功能。",
    ]),
]}# ================= 第 8 章 =================
CH08 = {"blocks": [
    ("h2", "配置是怎么分层的", "sec-layers"),
    ("p", "Claude Code 的配置分散在几个地方，按优先级从低到高大致是：**默认值 → 用户级 `~/.claude/settings.json` → 项目级 `.claude/settings.json` → 命令行参数 / 环境变量**。越靠后的越能覆盖前面的。"),
    ("code", None, "json", r'''{
  "permissions": { "allow": [], "deny": [] },
  "model": "claude-sonnet-4-8",
  "env": { "MY_VAR": "value" },
  "hooks": { "PreToolUse": [] }
}'''),
    ("h2", "环境变量：120+ 个开关", "sec-flags"),
    ("p", "环境变量是「不用改文件就能调行为」的方式。公开源码分析里发现了 **120+ 个环境变量**，大致分成几类："),
    ("table", ["类别", "作用", "例子（示意）"],
      [["认证", "API Key、代理地址", "ANTHROPIC_API_KEY、HTTP_PROXY"],
       ["行为", "权限、输出、日志", "权限模式、输出格式、调试日志"],
       ["模型", "覆盖模型选择", "模型名 / 参数"],
       ["实验", "开启内部功能", "各种实验性开关"]]),
    ("p", "原理很简单：程序启动时读环境变量，用它覆盖默认配置。下面这个模块演示「默认值 < 环境变量」的分层逻辑："),
    ("code", "config.py", "python", None),
    ("h2", "特性门控：tengu_* 灰度", "sec-gates"),
    ("p", "大公司发新功能不会「一键全量」，而是**灰度**：先给一小部分用户开，观察没问题再逐步放开。Claude Code 用了一套叫 **GrowthBook** 的特性门控系统，门控键以 `tengu_*` 命名（如 `tengu_enable_buddy`）。"),
    ("p", "除了运行时门控，还有 **32 个构建时 feature flags**——它们在打包（build）时就决定代码要不要包含某个功能，比如 `ENABLE_COORDINATOR`、`ENABLE_KAIROS`、`ENABLE_ULTRAPLAN` 这类开关。"),
    ("callout", "note", "理解重点", "特性门控 = 「代码已经写好，但开不开由开关决定」。这解释了为什么公开分析里能看到一堆没上线的功能：代码在，只是默认被门控关着。"),
    ("h2", "anthropic-beta 头：请求时声明实验能力", "sec-beta"),
    ("p", "有些实验能力需要客户端在**每个 API 请求**里声明。Claude Code 会带上 `anthropic-beta` 请求头，比如公开分析里出现的 `cli-internal-2026-02-09` 这样的值——它告诉服务器「我要用这个内部版本的能力」。"),
    ("quiz", [
      {"q": "tengu_* 门控主要用来做什么？", "opts": [("A", "给新功能做灰度发布，控制开不开"), ("B", "给代码加密"), ("C", "加快编译速度")], "ans": "A",
       "explain": "tengu_* 是 GrowthBook 门控的命名空间：代码已内置、默认关闭，按比例灰度放开。", "back": ("特性门控", "sec-gates")},
      {"q": "环境变量和配置文件的关系是？", "opts": [("A", "环境变量可以覆盖配置文件里的默认值"), ("B", "两者完全无关"), ("C", "配置文件永远优先，环境变量无效")], "ans": "A",
       "explain": "分层规则：默认值 < settings.json < 环境变量 / 命令行参数，越靠后优先级越高。", "back": ("环境变量", "sec-flags")},
      {"q": "anthropic-beta 请求头是干什么用的？", "opts": [("A", "在 API 请求里声明要使用的实验能力"), ("B", "给请求加密"), ("C", "加快响应速度")], "ans": "A",
       "explain": "实验能力要在每个请求带上 anthropic-beta 头声明，比如公开分析里出现的 cli-internal-2026-02-09。", "back": ("anthropic-beta", "sec-beta")},
    ]),
    ("summary", [
      "配置分层：默认值 < settings.json < 环境变量 / 命令行参数。",
      "120+ 环境变量、32 个构建时 flags 控制行为。",
      "tengu_* 灰度门控 + anthropic-beta 头声明实验能力。",
    ]),
]}

# ================= 第 9 章 =================
CH09 = {"blocks": [
    ("h2", "源头：cli.js.map 是什么", "sec-sourcemap"),
    ("p", "Claude Code 用打包工具把大量 TypeScript 源码压缩成一个 `cli.js` 文件。为了让调试器能把压缩代码映射回原始源码，打包器会生成一个 **Source Map**（`.js.map`）。这次公开分析的源头，就是这个 `cli.js.map`——它把压缩代码**反解**成了 **1,884 个原始 TypeScript 文件**。"),
    ("p", "Source Map 长这样（简化）："),
    ("code", None, "json", r'''{
  "version": 3,
  "sources": ["src/cli/commands.ts", "src/cli/agents/loop.ts"],
  "sourcesContent": ["原始 TypeScript 源码……"],
  "mappings": "AAAA;AACA;..."
}'''),
    ("callout", "note", "它说明什么", "Source Map 本身是**调试工具**，不是加密内容。它出现在生产包里，说明团队发布时没把它排除干净——这也提醒所有开发者：**发布前检查产物里有没有 `.map` 文件**。"),
    ("h2", "TS 架构：1,884 个文件怎么组织", "sec-arch"),
    ("p", "这 1,884 个文件按职责大致分成几块：CLI 入口、会话管理、工具实现、权限系统、上下文压缩、配置与门控。理解大项目源码，第一件事是**按「入口 → 依赖 → 数据流」找主线**，而不是从头读到尾。"),
    ("h2", "TS ↔ Rust 对照：claw-code", "sec-parity"),
    ("p", "[ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) 是社区用 **Rust** 重写 Claude Code 的开源项目。它把 TS 的各个模块映射成 Rust 的 crate（包），并维护一份 **PARITY.md** 记录「哪些行为已经对齐、哪些还没」。"),
    ("table", ["TS 模块（Claude Code）", "Rust crate（claw-code）", "职责"],
      [["src/cli/*", "claw（主程序）", "命令行入口"],
       ["src/session/*", "会话 crate", "会话保存 / 恢复"],
       ["src/tools/*", "工具 crate", "工具注册与执行"],
       ["src/permissions/*", "权限 crate", "YOLO 分级 / 确认流程"],
       ["src/context/*", "上下文 crate", "token 估算与压缩"]]),
    ("h2", "Rust 侧长什么样", "sec-rust"),
    ("p", "Rust 移植强调**类型安全**：每个工具、每条消息都有明确的类型。示意："),
    ("code", None, "rust", r'''// 工具 = 一个带 schema 的函数（示意）
pub struct Tool {
    pub name: &'static str,
    pub description: &'static str,
    pub run: fn(&ToolInput) -> Result<String, ToolError>,
}

pub enum Message {
    User(String),
    Assistant { text: String, tool_use: Option<ToolUse> },
    ToolResult { id: String, content: String },
}'''),
    ("p", "构建与检查："),
    ("envtabs", [
      ("pwsh", "PowerShell", "bash", "cargo build --workspace\ncargo run --bin claw -- doctor"),
      ("mac", "macOS", "bash", "cargo build --workspace\ncargo run --bin claw -- doctor"),
      ("linux", "Linux", "bash", "cargo build --workspace\ncargo run --bin claw -- doctor"),
    ]),
    ("quiz", [
      {"q": "cli.js.map 为什么能还原出 1,884 个 TS 文件？", "opts": [("A", "它是加密文件，破解后得到源码"), ("B", "Source Map 里本来就有源码映射信息"), ("C", "它包含完整数据库")], "ans": "B",
       "explain": "Source Map 是调试用的映射文件，记录了压缩代码与原始源码的对应关系，甚至可能内嵌源码。", "back": ("cli.js.map", "sec-sourcemap")},
      {"q": "PARITY.md 在 claw-code 里是干嘛的？", "opts": [("A", "记录 Rust 版与原始行为对齐的清单"), ("B", "Rust 的构建配置"), ("C", "一份广告文档")], "ans": "A",
       "explain": "PARITY 即「对齐」：逐项记录哪些行为已复刻、哪些还没，是移植项目的路线图。", "back": ("PARITY", "sec-parity")},
      {"q": "claw-code 用 Rust 重写时为什么强调「类型安全」？", "opts": [("A", "用明确类型表达消息和工具，编译期就发现错误"), ("B", "Rust 必然比 TypeScript 快"), ("C", "为了兼容所有操作系统")], "ans": "A",
       "explain": "每个工具、每条消息都有明确类型（struct / enum），编译期检查代替运行时猜错。", "back": ("Rust 侧", "sec-rust")},
    ]),
    ("summary", [
      "cli.js.map 是 Source Map，公开分析源头；还原出 1,884 个 TS 文件。",
      "claw-code 用 Rust 重写，TS 模块 ↔ Rust crate 一一对应。",
      "PARITY.md 是移植对齐清单，也是读移植项目的最佳入口。",
    ]),
]}# ================= 第 10 章 =================
CH10 = {"blocks": [
    ("h2", "读源码的三步法", "sec-read"),
    ("p", "面对几千个文件，别从头读到尾。用三步走："),
    ("steps", [
      ("找入口", "先从 `cli.js` / `main` / README 找到程序从哪开始跑，画出调用链。"),
      ("追数据流", "盯住「一条用户输入」如何变成请求、如何变成工具调用，把主线走通。"),
      ("再看支线", "主线懂了以后，再去看权限、压缩、配置这些旁路，逐个击破。"),
    ]),
    ("h2", "最小复刻路线", "sec-clone"),
    ("p", "想自己动手，不要一上来就复刻全部。按这个顺序做，每一步都对应前面章节的封装代码："),
    ("steps", [
      ("最小代理循环", "拿第 3 章的 `agent_loop.py`，把「模拟模型」换成真实 API 调用。"),
      ("加工具", "把第 4 章的 `tools.py` 接进来：注册表 + 分派。"),
      ("加权限", "把第 5 章的 `permissions.py` 插在工具执行之前。"),
      ("加会话", "用第 6 章的 `session.py` 支持断点续聊。"),
      ("加 CLI", "用第 7 章的 `cli_repl.py` 包一层交互界面。"),
      ("加配置", "用第 8 章的 `config.py` 让行为可配置。"),
    ]),
    ("h2", "安全与伦理边界", "sec-boundary"),
    ("callout", "warn", "红线", "公开源码分析的用途是**学习原理**，不是照抄发布、也不是用于绕过付费或攻击。别把非公开功能当承诺：代码里有不代表能上线、更不代表官方支持。"),
    ("ul", [
      "**版权**：源码分析可以谈原理，转载 / 商用要谨慎。",
      "**安全**：永远不要在 bypassPermissions 下跑不确定的命令。",
      "**伦理**：不做绕过鉴权、滥用 API 的实验。",
      "**预期管理**：分析出来的功能随时可能变化或消失。",
    ]),
    ("h2", "推荐练习清单", "sec-practice"),
    ("ul", [
      "把 `agent_loop.py` 改成「最多循环 N 次就停止」，观察终止条件的作用。",
      "给 `tools.py` 加一个自定义工具，比如「统计代码行数」。",
      "用 `context_manager.py` 打印出压缩前后各占多少 token。",
      "给 `cli_repl.py` 加一个 `/model` 命令，模拟切换模型。",
      "把各章封装代码组装成一个完整的最小 CLI 工具。",
    ]),
    ("quiz", [
      {"q": "读一份大源码，正确顺序是？", "opts": [("A", "从第一个文件读到最后一个"), ("B", "找入口 → 追数据流 → 再看支线"), ("C", "只看 README")], "ans": "B",
       "explain": "先找入口、追主线数据流，主线通了再处理支线，效率最高。", "back": ("三步法", "sec-read")},
      {"q": "关于公开源码分析，下面哪种态度是对的？", "opts": [("A", "照抄发布，反正开源"), ("B", "只用于学习原理，不绕过付费、不攻击、不商用转载"), ("C", "分析里的功能一定会上线")], "ans": "B",
       "explain": "源码分析用于学习；非公开功能不代表承诺，安全与伦理边界要守住。", "back": ("安全与伦理", "sec-boundary")},
      {"q": "按「最小复刻路线」，第一步应该做什么？", "opts": [("A", "先做一个最小代理循环，再把模拟模型换成真实 API"), ("B", "一上来就复刻全部功能"), ("C", "先写配置系统")], "ans": "A",
       "explain": "从第 3 章的 agent_loop.py 起步，再逐步加工具、权限、会话、CLI、配置。", "back": ("最小复刻", "sec-clone")},
    ]),
    ("summary", [
      "读源码三步法：找入口 → 追数据流 → 再看支线。",
      "最小复刻从 agent loop 起步，逐步加工具、权限、会话、CLI、配置。",
      "守住安全与伦理边界：学习原理，不照抄滥用。",
    ]),
]}

CHAPTER_CONTENT.update({"ch06": CH06, "ch07": CH07, "ch08": CH08, "ch09": CH09, "ch10": CH10})

# ================= 拓展篇 · Agent 与 Harness =================
EXT_BLOCKS = [
    ("h2", "先分清三个词：模型、Agent、Harness", "sec-what"),
    ("p", "聊 AI 代理时，这三个词最容易被混着用。其实它们是三层东西，各管一段："),
    ("table", ["维度", "模型 Model", "Agent 代理", "Harness 代理外壳"],
      [["它是什么", "只会「想」的神经网络", "一套「想 → 做 → 看 → 再想」的循环", "把前两者装成整机的那层工程代码"],
       ["负责什么", "理解文字、做决策", "决定下一步做什么并反复迭代", "把决策变成真实动作，并保证安全、可恢复、可配置"],
       ["类比", "大脑", "实习生的工作方式", "工位：电脑、权限卡、资料库、门禁、流程"],
       ["对应章节", "第 2 章 API 请求", "第 3 章 代理循环", "本篇主题 + 第 4–8 章"]]),
    ("callout", "tip", "一句话", "模型负责「想」，Agent 负责「循环」，Harness 负责「把想法变成现实」——Claude Code 是三者合体。"),
    ("h2", "Agent：不是聊天，是一套循环", "sec-agent"),
    ("p", "判断一个程序是不是「Agent」，不看它用没用大模型，而看它有没有这三个特征："),
    ("ul", [
      "**目标驱动**：你给它一个目标，而不是一段话。",
      "**自主多步**：它自己拆步骤、自己决定下一步，不需要你每一步都指挥。",
      "**能观察反馈**：每做一步都能看到结果，并根据结果调整。",
    ]),
    ("p", "对照第 3 章的循环：感知 → 决策 → 行动 → 观察。聊天机器人不是 Agent（它只有「说」），Claude Code 是 Agent（它真的在做）。"),
    ("h3", "Agent vs Workflow：自主和固定是两种路线"),
    ("p", "**Workflow（工作流）**把步骤写死：A 做完做 B，B 做完做 C，像走迷宫前先画好地图。**Agent** 不预设每一步，像边走边看路：遇到岔路自己判断。"),
    ("table", ["维度", "Workflow 工作流", "Agent 代理"],
      [["步骤", "预先写死", "运行时自己决定"],
       ["容错", "步骤出错就卡住", "看到结果可调整"],
       ["可预测性", "高，结果稳定", "低，结果有随机性"],
       ["适合场景", "流程固定、规则清楚（如发邮件）", "情况多变、需要临场发挥（如修 bug）"]]),
    ("callout", "note", "怎么选", "不是 Agent 一定更好：能写死的工作流更省钱、更稳定；变化多的任务才值得上 Agent。Claude Code 里两种都能用（比如用斜杠命令或自定义子代理）。"),
    ("h2", "Harness：把模型变成「有手有脚」的那层代码", "sec-harness"),
    ("p", "大模型本身只会输出文字。要让它「真的干活」，外面必须包一层工程代码——这层代码就叫 **Harness（代理外壳）**。它至少负责下面这些事："),
    ("ul", [
      "**跑循环**：驱动模型反复「想 → 做 → 看」，直到完成（第 3 章）。",
      "**管工具**：注册工具、执行工具、把结果送回上下文（第 4 章）。",
      "**把关安全**：权限模式、YOLO 分级、危险命令拦截（第 5 章）。",
      "**管上下文**：组装系统提示、管理 token、满了自动压缩（第 2、6 章）。",
      "**管记忆**：保存 / 恢复会话，读写 CLAUDE.md（第 6 章）。",
      "**提供界面**：CLI、斜杠命令、配置与开关（第 7、8 章）。",
    ]),
    ("callout", "tip", "类比", "模型是**发动机**，Harness 是**整车**：方向盘、刹车、仪表盘、外壳都是车的一部分。只有发动机，车跑不起来。"),
    ("h2", "从源码看 Harness 的三层结构", "sec-layers"),
    ("p", "社区在拆解 Claude Code 源码时，常把 Harness 分成三层。这三层正好对应你学过的章节："),
    ("table", ["层级", "干什么", "对应章节"],
      [["执行层 Action", "工具注册表、tool_use / tool_result、Bash / Read / Edit / Grep", "第 4 章"],
       ["上下文层 Context", "系统提示、CLAUDE.md、会话历史、token 预算、compact 压缩", "第 2、6 章"],
       ["治理层 Governance", "权限模式、YOLO、allowlist / denylist、配置、特性门控、Hooks", "第 5、8 章"]]),
    ("p", "从下往上看：**执行层**决定它能做什么，**上下文层**决定它看到什么，**治理层**决定什么被允许。三层叠起来，就是一个完整的 Harness。"),
    ("h2", "记忆：Harness 给模型配的「笔记本」", "sec-memory"),
    ("p", "模型本身没有记忆——每次请求都要把历史重新发给它（第 2 章说过）。所以「记不记得」这件事，其实是 Harness 在管。它提供两种记忆："),
    ("table", ["记忆类型", "存在哪", "什么时候用"],
      [["短期记忆", "上下文窗口内的消息历史", "每一轮请求都带上"],
       ["项目记忆", "项目根目录的 CLAUDE.md", "每次会话开始自动读入"],
       ["个人记忆", "~/.claude/CLAUDE.md 等全局文件", "所有项目都会读"],
       ["长期记忆", "会话文件、设置文件、自定义记忆命令", "断点续聊 / 跨会话复用"]]),
    ("callout", "note", "大白话", "短期记忆像「这轮对话的草稿纸」，项目记忆像「公司发的项目入职手册」，长期记忆像「你的工作档案」。模型负责看，Harness 负责递。"),
    ("h2", "子代理与多代理团队：一个人干不完，就组队", "sec-subagent"),
    ("p", "复杂任务可以拆给多个**子代理（Subagents）**：每个子代理有自己独立的角色设定和上下文，主代理把任务分包出去，再回收结果。这样每个「同事」只记自己那摊事，上下文更省、更专注。"),
    ("p", "子代理之间怎么配合，有几种常见「团队模式」："),
    ("table", ["模式", "一句话", "适合场景"],
      [["Pipeline 流水线", "A 做完交给 B，B 做完交给 C", "步骤有先后依赖"],
       ["Supervisor 主管", "一个主管拆活、验收、返工", "任务需要统一调度"],
       ["Fan-out / Fan-in 分头并行", "同时派多个子代理，最后汇总", "几块活互不依赖"],
       ["Expert Pool 专家池", "按问题类型找对应专家", "领域多样、各有所长"],
       ["Hierarchical 层级委派", "主管下面还有小主管", "任务规模很大"]]),
    ("callout", "tip", "记忆点", "主代理 = 项目经理，子代理 = 各司其职的组员，团队模式 = 怎么分工协作。你在终端里看到的多代理流程，本质就是这套。"),
    ("h2", "Hooks 与 MCP：Harness 的「插槽」", "sec-hooks"),
    ("p", "一套 Harness 不可能覆盖所有需求，所以它留了两个「插槽」给你扩展："),
    ("h3", "Hooks：到点就响的「闹钟 + 哨兵」"),
    ("p", "**Hook（钩子）**是在固定时机触发外部脚本的机制，比如：工具调用前（PreToolUse）、工具调用后（PostToolUse）、任务结束时（Stop）。你可以用它做「每次改文件前自动备份」「每次跑命令前记录日志」这类事情。"),
    ("h3", "MCP：万能「USB 口」"),
    ("p", "**MCP（Model Context Protocol）**是接入外部工具和数据源的标准协议：数据库、浏览器、内部 API，接上就能用。它让 Harness 的工具系统不再局限于内置的那几个。"),
    ("table", ["维度", "Hooks", "MCP"],
      [["改变什么", "改变 Harness 在某个时机的行为", "给 Harness 增加新能力"],
       ["触发方式", "事件驱动（时机到了就触发）", "按需调用（模型决定用不用）"],
       ["类比", "闹钟 + 门卫哨", "万能 USB 口"]]),
    ("h2", "代码实验室：一个迷你 Harness", "sec-lab"),
    ("p", "把上面所有概念浓缩成一个能跑的小程序 `harness.py`：大脑（假模型）+ 手脚（工具）+ 门卫（权限）+ 记忆（会话），由一个 Harness 串起来。跑一遍，你就把第 2–8 章串起来了。"),
    ("code", "harness.py", "python", None),
    ("steps", [
      ("保存文件", "把上面的 `harness.py` 保存到任意目录。"),
      ("运行", "在终端执行 `python harness.py`。"),
      ("观察输出", "会看到：读文件 → 统计行数 → 危险命令被门卫拦截 → 模型收尾 → 会话存盘。"),
    ]),
    ("callout", "tip", "换成真实模型", "想换成真实模型？看 `harness.py` 里 `FakeModel.think` 下方的注释：把假模型换成一次真实 API 调用即可，循环、门卫、记忆都不用改——这正是 Harness 的意义：换大脑，不动外壳。"),
    ("quiz", [
      {"q": "模型、Agent、Harness 三者的关系，哪个说法对？", "opts": [("A", "模型会动手，Agent 负责想，Harness 是界面"), ("B", "模型负责想，Agent 负责循环，Harness 把前两者装成能安全干活的整机"), ("C", "三者是一回事")], "ans": "B",
       "explain": "模型只会输出文字；Agent 是循环；Harness 是包含工具、权限、记忆、界面的一切工程代码。", "back": ("先分清三个词", "sec-what")},
      {"q": "Workflow 和 Agent 的本质区别是？", "opts": [("A", "Workflow 步骤写死，Agent 运行时自主决策"), ("B", "Workflow 更智能"), ("C", "Agent 不需要模型")], "ans": "A",
       "explain": "Workflow 走固定流程，Agent 边走边看、根据反馈调整。", "back": ("Agent vs Workflow", "sec-agent")},
      {"q": "Harness 的「上下文层」主要负责什么？", "opts": [("A", "组装系统提示、CLAUDE.md、历史，管理 token 与压缩"), ("B", "执行工具调用"), ("C", "决定权限放不放行")], "ans": "A",
       "explain": "执行层管工具、治理层管权限、上下文层管「它看到什么」。", "back": ("三层结构", "sec-layers")},
      {"q": "子代理（Subagent）最大的好处是？", "opts": [("A", "每个子代理有独立上下文，更专注、更省"), ("B", "可以让模型跑得更快"), ("C", "不需要主代理")], "ans": "A",
       "explain": "子代理各自记各自的事，上下文更小更专注，主代理负责调度汇总。", "back": ("子代理", "sec-subagent")},
      {"q": "Hooks 和 MCP 的区别是？", "opts": [("A", "Hooks 在固定时机触发脚本，MCP 接入外部工具 / 数据源"), ("B", "它们完全一样"), ("C", "MCP 只能读文件")], "ans": "A",
       "explain": "Hooks 改行为（时机触发），MCP 加能力（按需调用外部服务）。", "back": ("Hooks 与 MCP", "sec-hooks")},
    ]),
    ("summary", [
      "模型负责想，Agent 负责循环，Harness 负责把想法变成真实动作并保证安全。",
      "Workflow 走固定流程，Agent 自主决策；能写死的用工作流，变化多的用 Agent。",
      "Harness 三层：执行层（工具）、上下文层（看到什么）、治理层（允许什么）。",
      "记忆分短期（上下文）与长期（CLAUDE.md、会话文件），都由 Harness 管。",
      "子代理 = 专人专岗，团队模式 = 分工协作；Hooks = 时机插槽，MCP = 万能接口。",
    ]),
]

# ================= 构建入口 =================
def build_ext():
    hero = (
        '<div class="hero"><span class="watermark">拓</span>'
        '<div class="chapter-tag">EXTENSION · PART 5 · AGENT & HARNESS</div>'
        "<h1>拓展篇 · Agent 与 Harness</h1>"
        '<p class="goal">正文十章把 Claude Code 拆开讲；这一篇把它们再装回去：Agent 是什么、'
        "Harness（代理外壳）又是什么。读完你会有一种「哦，原来整台机器是这样拼起来的」的感觉。</p></div>"
    )
    body = hero + render_blocks(EXT_BLOCKS, "拓")
    body += '<div class="prevnext" id="prevNext"></div>'
    return page_shell(
        "拓展篇 · Agent 与 Harness",
        "Agent 与 Harness（代理外壳）拓展阅读",
        body, "ext-ah", "../", "nav-ext")

def render_chapter(ch):
    part = next(p for p in PARTS if p["n"] == ch["part"])
    hero = (
        '<div class="hero"><span class="watermark">{num}</span>'
        '<div class="chapter-tag">PART {pnum} · {ptitle} · {psub}</div>'
        '<h1>{num} · {title}</h1>'
        '<p class="goal">{goal}</p></div>'
    ).format(
        num=ch["num"], pnum=ch["part"], ptitle=part["title"], psub=part["sub"],
        title=esc(ch["title"]), goal=esc(ch["goal"]),
    )
    meta = (
        '<div class="meta-card"><span><b>本章目标</b>　{goal}</span>'
        '<span><b>前置依赖</b>　{prereq}</span>'
        '<button id="markDone" class="btn mark-done">标记完成</button></div>'
    ).format(goal=esc(ch["goal"]), prereq=inline_md(ch["prereq"]))
    content = CHAPTER_CONTENT[ch["id"]]
    body = hero + meta + render_blocks(content["blocks"], ch["num"])
    body += '<div class="prevnext" id="prevNext"></div>'
    title = "第 {} 章 · {}".format(ch["num"], ch["title"])
    return page_shell(title, ch["summary"], body, ch["id"], "../", "nav-ch")

def build_docs():
    for ch in CHAPTERS:
        out = ROOT / ch["path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_chapter(ch), encoding="utf-8")

def main():
    (ROOT / "index.html").write_text(build_home(), encoding="utf-8")
    (ROOT / "glossary.html").write_text(build_glossary(), encoding="utf-8")
    (ROOT / "toolbox.html").write_text(build_toolbox(), encoding="utf-8")
    (ROOT / "about.html").write_text(build_about(), encoding="utf-8")
    build_docs()
    (ROOT / "docs" / "ext-ah.html").write_text(build_ext(), encoding="utf-8")
    print("OK: 已生成 index / glossary / toolbox / about、docs/ch01..ch10 与 docs/ext-ah.html")

if __name__ == "__main__":
    main()