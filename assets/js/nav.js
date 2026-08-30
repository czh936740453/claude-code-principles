/* ============================================================
   nav.js —— 导航 / 学习进度 / 主题 / 字号 / 阅读记忆 / 滚动高亮
   所有数据只存本机 localStorage，不上传。
   ============================================================ */
(function () {
  "use strict";

  /* ---------- 章节数据（单一数据源） ---------- */
  var CHAPTERS = [
    { id: "ch01", num: "01", title: "认识 Claude Code", path: "docs/ch01.html", part: 1,
      goal: "搞懂 Claude Code 是什么、解决什么问题，以及它和聊天机器人 / IDE 插件的本质区别。",
      prereq: "无，零基础可读。",
      summary: "终端里的 AI 编程代理：你说目标，它自己动手。和聊天机器人、IDE 插件有什么本质区别？",
      keywords: "claude code 介绍 终端 代理 agent cli 命令行 是什么" },
    { id: "ch02", num: "02", title: "一次对话的完整旅程", path: "docs/ch02.html", part: 1,
      goal: "跟着一次真实对话走一遍：从你按下回车，到它给出答案，中间到底发生了什么。",
      prereq: "建议先读第 1 章。",
      summary: "端到端数据流：输入 → 上下文组装 → API → 工具调用 → 循环，一张图看懂全流程。",
      keywords: "数据流 上下文 api 请求 响应 会话 流程图 端到端" },
    { id: "ch03", num: "03", title: "代理循环 Agent Loop", path: "docs/ch03.html", part: 2,
      goal: "掌握 Claude Code 的心脏——while 循环：感知、决策、行动、观察，循环往复直到完成。",
      prereq: "建议先读第 2 章。",
      summary: "核心 while 循环：为什么它是「代理」而不是「单次问答」，用伪代码和可运行例子讲透。",
      keywords: "agent loop 代理循环 while 工具调用 迭代 终止条件 伪代码" },
    { id: "ch04", num: "04", title: "工具系统", path: "docs/ch04.html", part: 2,
      goal: "理解「工具 = 函数 + 说明」：模型怎么知道能用什么工具、怎么调用、结果怎么回来。",
      prereq: "建议先读第 3 章。",
      summary: "工具注册表、tool_use / tool_result 协议、内置工具清单，以及权限怎么拦在中间。",
      keywords: "工具 tool_use tool_result schema 注册表 bash read edit grep 调度" },
    { id: "ch05", num: "05", title: "权限与安全", path: "docs/ch05.html", part: 2,
      goal: "搞懂「Claude 凭什么能跑我的命令」：权限模式、YOLO 分类器、命令注入检查。",
      prereq: "建议先读第 3、4 章。",
      summary: "四种权限模式、YOLO 风险分级、allowlist / denylist，安全边界如何工作。",
      keywords: "权限 permission yolo 安全 命令注入 allowlist denylist bypass acceptEdits plan" },
    { id: "ch06", num: "06", title: "会话与上下文管理", path: "docs/ch06.html", part: 2,
      goal: "理解「上下文窗口」这个稀缺资源：会话怎么恢复、token 怎么算、快满了怎么办。",
      prereq: "建议先读第 2、3 章。",
      summary: "会话持久化、上下文窗口（200K / 1M）、token 预算与压缩机制（compact）。",
      keywords: "会话 session 上下文 context token 窗口 compact 压缩 历史 恢复" },
    { id: "ch07", num: "07", title: "CLI 与斜杠命令", path: "docs/ch07.html", part: 3,
      goal: "掌握 Claude Code 的「人机界面」：启动方式、交互模式、斜杠命令与隐藏命令。",
      prereq: "建议先读第 2 章。",
      summary: "启动参数、REPL 交互、常用斜杠命令，以及 26 个隐藏命令里的代表。",
      keywords: "cli 命令行 repl 斜杠命令 slash 启动参数 flags 交互 隐藏命令" },
    { id: "ch08", num: "08", title: "配置、环境变量与特性门控", path: "docs/ch08.html", part: 3,
      goal: "看懂它「怎么被开关控制」：配置文件层级、120+ 环境变量、build flags 与 tengu 门控。",
      prereq: "建议先读第 3 章。",
      summary: "~/.claude/ 配置、环境变量分类、GrowthBook tengu_* 灰度开关、anthropic-beta 头。",
      keywords: "配置 config 环境变量 env 特性开关 feature flag tengu growthbook beta" },
    { id: "ch09", num: "09", title: "从公开源码到 Rust 移植", path: "docs/ch09.html", part: 4,
      goal: "了解「源码长什么样、怎么读」：从 cli.js.map 到 1,884 个 TS 文件，再到 Rust 移植的对照。",
      prereq: "建议先读第 3–6 章。",
      summary: "sourcemap 原理、TS 架构模块、TS ↔ Rust 对照表、PARITY 思路。",
      keywords: "源码 sourcemap cli.js.map typescript rust 移植 claw-code parity crate" },
    { id: "ch10", num: "10", title: "自学路线图与实践建议", path: "docs/ch10.html", part: 4,
      goal: "拿到一份可执行的行动清单：怎么读源码、怎么动手复刻、注意什么边界。",
      prereq: "建议学完全部章节。",
      summary: "读源码三步法、最小复刻路线、安全与伦理边界、推荐练习。",
      keywords: "自学 路线图 实践 复刻 阅读源码 练习 安全 伦理" }
  ];

  var PARTS = [
    { n: 1, title: "认知篇", sub: "它是什么" },
    { n: 2, title: "核心机制篇", sub: "它怎么工作" },
    { n: 3, title: "外围系统篇", sub: "支撑它的系统" },
    { n: 4, title: "研究与移植篇", sub: "怎么读源码 / 怎么复刻" }
  ];

  var K = {
    theme: "cc_theme", font: "cc_font",
    visited: "cc_visited", completed: "cc_completed", last: "cc_last", pos: "cc_pos_"
  };
  var FONT_LEVELS = ["A-", "A", "A+"];

  /* ---------- localStorage 工具 ---------- */
  function lsGet(key, def) { try { var v = localStorage.getItem(key); return v === null ? def : v; } catch (e) { return def; } }
  function lsSet(key, val) { try { localStorage.setItem(key, val); } catch (e) {} }
  function readJSON(key, def) { try { var v = JSON.parse(lsGet(key, null)); return Array.isArray(v) ? v : def; } catch (e) { return def; } }
  function writeJSON(key, arr) { lsSet(key, JSON.stringify(arr)); }

  function getPage() { return document.body.getAttribute("data-page") || ""; }
  function curChapter() {
    var p = getPage();
    for (var i = 0; i < CHAPTERS.length; i++) if (CHAPTERS[i].id === p) return CHAPTERS[i];
    return null;
  }

  /* 页面相对路径：章节页 / 拓展页位于 docs/ 子目录，链接需加 ../ 前缀；
     根级页面（首页/术语表/代码库/关于）直接用相对路径。 */
  function isDocsPage() {
    var page = getPage();
    return page.indexOf("ch") === 0 || page.indexOf("ext") === 0;
  }
  function pageHref(ch) {
    var prefix = isDocsPage() ? "../" : "";
    return prefix + ch.path;
  }

  /* ---------- 主题 ---------- */
  function applyTheme(t) { document.documentElement.setAttribute("data-theme", t); }
  function paintThemeBtn() {
    var btn = document.getElementById("themeToggle");
    if (!btn) return;
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    btn.textContent = dark ? "\u2600" : "\u263E";   // ☀ / ☾
    btn.title = dark ? "切换到浅色模式" : "切换到深色模式";
    btn.setAttribute("aria-label", btn.title);
  }
  function initTheme() {
    var t = lsGet(K.theme, "light");
    if (t !== "dark" && t !== "light") t = "light";
    applyTheme(t); paintThemeBtn();
  }

  /* ---------- 字号 ---------- */
  function applyFont(level) {
    document.documentElement.setAttribute("data-font", String(level));
    var btns = document.querySelectorAll("[data-fontbtn]");
    for (var i = 0; i < btns.length; i++) {
      var lv = parseInt(btns[i].getAttribute("data-fontbtn"), 10);
      btns[i].classList.toggle("active", lv === level);
    }
  }
  function initFont() {
    var lv = parseInt(lsGet(K.font, "1"), 10);
    if (isNaN(lv) || lv < 0 || lv > 2) lv = 1;
    applyFont(lv);
    var btns = document.querySelectorAll("[data-fontbtn]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener("click", function () {
        var lv = parseInt(this.getAttribute("data-fontbtn"), 10);
        lsSet(K.font, String(lv)); applyFont(lv);
      });
    }
  }

  /* ---------- 进度 ---------- */
  function getVisited() { return readJSON(K.visited, []); }
  function getCompleted() { return readJSON(K.completed, []); }
  function setVisited(a) { writeJSON(K.visited, a); }
  function setCompleted(a) { writeJSON(K.completed, a); }
  function completedCount() { return getCompleted().length; }

  function markVisited() {
    var ch = curChapter(); if (!ch) return;
    var v = getVisited();
    if (v.indexOf(ch.id) === -1) { v.push(ch.id); setVisited(v); }
    lsSet(K.last, ch.id);
  }

  /* 进度 UI：顶部导航条 + 首页面板 + 侧边栏勾选 */
  function renderProgress() {
    var done = completedCount();
    var cur = curChapter();
    var curIdx = cur ? parseInt(cur.num, 10) : 0;

    var tb = document.querySelector(".tb-progress");
    if (tb) {
      var txt = tb.querySelector(".tb-txt");
      var bar = tb.querySelector(".bar i");
      if (txt) txt.textContent = done + " / " + CHAPTERS.length;
      if (bar) bar.style.width = (done / CHAPTERS.length * 100) + "%";
    }
    var panel = document.getElementById("homeProgress");
    if (panel) {
      var big = panel.querySelector(".big");
      var pbar = panel.querySelector(".bar i");
      var hint = panel.querySelector(".hint");
      if (big) big.textContent = done + " / " + CHAPTERS.length;
      if (pbar) pbar.style.width = (done / CHAPTERS.length * 100) + "%";
      if (hint) {
        if (done === CHAPTERS.length) hint.textContent = "恭喜！全部章节已标记完成，可以去动手实践了。";
        else if (cur) hint.textContent = "进行到「" + cur.title + "」（第 " + cur.num + " 章），继续加油。";
        else hint.textContent = "从第 01 章开始，按顺序学习效果最好。";
      }
    }
    var ticks = document.querySelectorAll("[data-tick]");
    for (var i = 0; i < ticks.length; i++) {
      var id = ticks[i].getAttribute("data-tick");
      var isDone = getCompleted().indexOf(id) !== -1;
      ticks[i].textContent = isDone ? "\u2713" : "";
      ticks[i].classList.toggle("done", isDone);
    }

    /* 通知首页「章节多面体」刷新颜色（仅首页监听） */
    try { window.dispatchEvent(new CustomEvent("cc:progress")); } catch (e) {}
  }

  /* ---------- 首页「继续学习」卡片 ---------- */
  function renderContinueCard() {
    var card = document.getElementById("continueCard");
    if (!card) return;
    var done = getCompleted();
    if (done.length >= CHAPTERS.length) { card.hidden = true; return; }
    var last = lsGet(K.last, null);
    var next = null;
    for (var i = 0; i < CHAPTERS.length; i++) {
      if (CHAPTERS[i].id === last) {
        if (i + 1 < CHAPTERS.length) next = CHAPTERS[i + 1];
        break;
      }
    }
    if (!next) next = CHAPTERS[0];
    var title = document.getElementById("continueTitle");
    var meta = document.getElementById("continueMeta");
    var link = document.getElementById("continueLink");
    if (title) title.textContent = "上次学到：第 " + next.num + " 章 · " + next.title;
    if (meta) meta.textContent = done.length > 0
      ? "已标记完成 " + done.length + " / " + CHAPTERS.length + " 章"
      : "从第 1 章开始，按顺序学习";
    if (link) link.href = pageHref(next);
    card.hidden = false;
  }

  /* ---------- 侧边栏 ---------- */
  function buildSidebar() {
    var box = document.getElementById("sidebarNav");
    if (!box) return;
    var cur = curChapter();
    var html = '<div class="side-head">学习目录</div>';

    for (var p = 0; p < PARTS.length; p++) {
      html += '<div class="part">' + PARTS[p].title + " · " + PARTS[p].sub + "</div>";
      for (var c = 0; c < CHAPTERS.length; c++) {
        var ch = CHAPTERS[c];
        if (ch.part !== PARTS[p].n) continue;
        var active = cur && cur.id === ch.id ? " active" : "";
        var done = getCompleted().indexOf(ch.id) !== -1 ? " done" : "";
        html += '<a class="ch' + active + '" href="' + pageHref(ch) + '">' +
          '<span class="num">' + ch.num + "</span>" +
          "<span>" + ch.title + "</span>" +
          '<span class="tick' + done + '" data-tick="' + ch.id + '"></span></a>';
      }
    }

    /* 拓展篇（独立于 10 章进度） */
    var extActive = getPage() === "ext-ah" ? " active" : "";
    html += '<a class="ch' + extActive + '" href="' + (isDocsPage() ? "../" : "") + 'docs/ext-ah.html">' +
      '<span class="num">拓</span><span>Agent 与 Harness（拓展篇）</span></a>';

    /* 本页小节（滚动高亮用） */
    if (cur || isDocsPage()) {
      var secs = [];
      var hs = document.querySelectorAll(".content h2[id], .content h3[id]");
      for (var h = 0; h < hs.length; h++) secs.push(hs[h]);
      if (secs.length) {
        html += '<div class="part">本页小节</div>';
        for (var s = 0; s < secs.length; s++) {
          var tag = secs[s].tagName === "H2" ? "02" : "03";
          html += '<a class="ch sec" data-sec href="#' + secs[s].id + '">' +
            '<span class="num">' + tag + "</span><span>" + secs[s].textContent + "</span></a>";
        }
      }
    }
    box.innerHTML = html;
  }

  /* 滚动高亮：当前小节 */
  function initScrollspy() {
    var secLinks = document.querySelectorAll("#sidebarNav a[data-sec]");
    if (!secLinks.length) return;
    var map = [];
    for (var i = 0; i < secLinks.length; i++) {
      var href = secLinks[i].getAttribute("href");
      var el = document.querySelector(href);
      if (el) map.push({ link: secLinks[i], el: el });
    }
    function onScroll() {
      var pos = window.scrollY + 90;
      var current = null;
      for (var i = 0; i < map.length; i++) {
        if (map[i].el.offsetTop <= pos) current = map[i].link;
      }
      for (var j = 0; j < map.length; j++) map[j].link.classList.toggle("active", map[j].link === current);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ---------- 标记完成 ---------- */
  function initMarkDone() {
    var btn = document.getElementById("markDone");
    var cur = curChapter();
    if (!btn || !cur) return;
    function paint() {
      var done = getCompleted().indexOf(cur.id) !== -1;
      btn.classList.toggle("done", done);
      btn.textContent = done ? "已完成 \u2713" : "标记完成";
    }
    btn.addEventListener("click", function () {
      var a = getCompleted();
      var i = a.indexOf(cur.id);
      if (i === -1) a.push(cur.id); else a.splice(i, 1);
      setCompleted(a);
      paint(); renderProgress();
    });
    paint();
  }

  /* ---------- 上下章 ---------- */
  function initPrevNext() {
    var box = document.getElementById("prevNext");
    var cur = curChapter();
    if (!box) return;
    if (!cur && isDocsPage()) {
      box.innerHTML = '<a href="../index.html"><span class="dir">← 返回首页</span><b>学习目录</b></a>' +
        '<a href="../toolbox.html"><span class="dir">去动手 →</span><b>代码库 · 迷你 Harness</b></a>';
      return;
    }
    if (!cur) return;
    var i = parseInt(cur.num, 10) - 1;
    var prev = i > 0 ? CHAPTERS[i - 1] : null;
    var next = i < CHAPTERS.length - 1 ? CHAPTERS[i + 1] : null;
    var html = "";
    html += prev
      ? '<a href="' + pageHref(prev) + '"><span class="dir">\u2190 上一章</span><b>' + prev.num + " · " + prev.title + "</b></a>"
      : '<a href="../index.html"><span class="dir">\u2190 返回首页</span><b>学习目录</b></a>';
    html += next
      ? '<a href="' + pageHref(next) + '"><span class="dir">下一章 \u2192</span><b>' + next.num + " · " + next.title + "</b></a>"
      : '<a href="../toolbox.html"><span class="dir">全部学完 \u2192</span><b>去代码库动手</b></a>';
    box.innerHTML = html;
  }

  /* ---------- 阅读位置记忆 ---------- */
  function initReadingPos() {
    if (!isDocsPage()) return;
    var page = getPage();
    var key = K.pos + page;
    var saved = parseInt(lsGet(key, "0"), 10) || 0;
    if (location.hash) {
      var t = document.querySelector(location.hash);
      if (t) setTimeout(function () { t.scrollIntoView({ block: "start" }); }, 30);
      return;
    }
    if (saved > 8) setTimeout(function () { window.scrollTo(0, saved); }, 30);
    var timer = null;
    window.addEventListener("scroll", function () {
      if (timer) return;
      timer = setTimeout(function () {
        timer = null;
        lsSet(key, String(window.scrollY));
      }, 400);
    }, { passive: true });
  }

  /* ---------- 汉堡菜单 ---------- */
  function initHamburger() {
    var hb = document.getElementById("hamburger");
    var scrim = document.querySelector(".scrim");
    function set(open) { document.body.classList.toggle("sidebar-open", open); }
    if (hb) hb.addEventListener("click", function () { set(!document.body.classList.contains("sidebar-open")); });
    if (scrim) scrim.addEventListener("click", function () { set(false); });
  }

  /* ---------- 首页重置进度 ---------- */
  function initReset() {
    var btn = document.getElementById("resetProgress");
    if (!btn) return;
    btn.addEventListener("click", function () {
      if (confirm("确定要清空全部学习进度吗？")) {
        setVisited([]); setCompleted([]);
        renderProgress(); buildSidebar();
      }
    });
  }

  /* ---------- 初始化 ---------- */
  function init() {
    initTheme();
    initFont();
    initHamburger();
    buildSidebar();
    initScrollspy();
    initMarkDone();
    initPrevNext();
    initReadingPos();
    initReset();
    markVisited();
    renderProgress();
    renderContinueCard();

    var tt = document.getElementById("themeToggle");
    if (tt) tt.addEventListener("click", function () {
      var dark = document.documentElement.getAttribute("data-theme") === "dark";
      applyTheme(dark ? "light" : "dark");
      lsSet(K.theme, dark ? "light" : "dark");
      paintThemeBtn();
    });

    /* 跨页面进度同步 */
    window.addEventListener("storage", function (e) {
      if (e.key === K.completed || e.key === K.visited || e.key === K.last) { renderProgress(); buildSidebar(); renderContinueCard(); }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();