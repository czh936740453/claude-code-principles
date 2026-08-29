/* ============================================================
   main.js —— 页面交互：代码高亮 / 行号 / 复制 / 下载 /
   环境切换 / 自测题 / 首页搜索 / 交互演示 / 代码库筛选
   ============================================================ */
(function () {
  "use strict";

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  /* ---------- 语法高亮规则（VSCode Dark+ 配色由 CSS 类控制） ---------- */
  var LANGS = {
    python: {
      label: "Python",
      rules: [
        { re: /#[^\n]*/, cls: "tok-cmt" },
        { re: /(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')/, cls: "tok-str" },
        { re: /\b(?:def|class|return|if|elif|else|for|while|import|from|as|try|except|finally|with|lambda|not|and|or|in|is|None|True|False|pass|break|continue|raise|yield|global|nonlocal|del|assert|async|await|print)\b/, cls: "tok-kw" },
        { re: /@[A-Za-z_][A-Za-z0-9_.]*/, cls: "tok-kw" },
        { re: /\b\d+(?:\.\d+)?\b/, cls: "tok-num" },
        { re: /[A-Za-z_][A-Za-z0-9_]*(?=\s*\()/, cls: "tok-fn" },
        { re: /\b[A-Z][A-Za-z0-9_]*\b/, cls: "tok-typ" }
      ]
    },
    bash: {
      label: "Shell",
      rules: [
        { re: /#[^\n]*/, cls: "tok-cmt" },
        { re: /"(?:\\.|[^"\\\n])*"|'(?:[^'\\\n])*'/, cls: "tok-str" },
        { re: /\$\{?[A-Za-z_][A-Za-z0-9_]*\}?/, cls: "tok-var" },
        { re: /\b(?:echo|if|then|else|elif|fi|for|do|done|while|until|case|esac|function|export|cd|set|return|local|read|exit|true|false)\b/, cls: "tok-kw" },
        { re: /\b\d+\b/, cls: "tok-num" }
      ]
    },
    json: {
      label: "JSON",
      rules: [
        { re: /"(?:\\.|[^"\\])*"(?=\s*:)/, cls: "tok-var" },
        { re: /"(?:\\.|[^"\\])*"/, cls: "tok-str" },
        { re: /-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/, cls: "tok-num" },
        { re: /\b(?:true|false|null)\b/, cls: "tok-kw" }
      ]
    },
    typescript: {
      label: "TypeScript",
      rules: [
        { re: /\/\/[^\n]*|\/\*[\s\S]*?\*\//, cls: "tok-cmt" },
        { re: /"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`/, cls: "tok-str" },
        { re: /\b(?:const|let|var|function|return|if|else|for|while|import|from|export|interface|type|class|new|async|await|try|catch|throw|readonly|implements|extends|of|in|switch|case|default|break|continue|yield|void|any|never|unknown)\b/, cls: "tok-kw" },
        { re: /\b\d+(?:\.\d+)?\b/, cls: "tok-num" },
        { re: /[A-Za-z_$][A-Za-z0-9_$]*(?=\s*\()/, cls: "tok-fn" },
        { re: /\b[A-Z][A-Za-z0-9_]*\b/, cls: "tok-typ" }
      ]
    },
    rust: {
      label: "Rust",
      rules: [
        { re: /\/\/[^\n]*|\/\*[\s\S]*?\*\//, cls: "tok-cmt" },
        { re: /"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/, cls: "tok-str" },
        { re: /\b(?:fn|let|mut|impl|struct|enum|match|if|else|for|while|loop|return|pub|use|mod|crate|trait|async|await|move|ref|self|where|type|const|static|unsafe|dyn)\b/, cls: "tok-kw" },
        { re: /[a-z_][a-zA-Z0-9_]*!/, cls: "tok-fn" },
        { re: /\b\d+(?:_\d+)*(?:\.\d+)?\b/, cls: "tok-num" },
        { re: /[a-z_][a-zA-Z0-9_]*(?=\s*\()/, cls: "tok-fn" },
        { re: /\b[A-Z][A-Za-z0-9_]*\b/, cls: "tok-typ" }
      ]
    },
    text: { label: "文本", rules: [] }
  };

  function langInfo(lang) {
    return LANGS[lang] || LANGS.text;
  }
  function langFromName(name) {
    if (!name) return "text";
    var n = name.toLowerCase();
    if (n.indexOf("python") !== -1 || n.indexOf(".py") !== -1) return "python";
    if (n.indexOf("bash") !== -1 || n.indexOf("shell") !== -1 || n.indexOf("sh") !== -1) return "bash";
    if (n.indexOf("json") !== -1) return "json";
    if (n.indexOf("typescript") !== -1 || n.indexOf("ts") !== -1) return "typescript";
    if (n.indexOf("rust") !== -1 || n.indexOf(".rs") !== -1) return "rust";
    return "text";
  }

  function highlight(text, lang) {
    var L = langInfo(lang);
    if (!L.rules.length) return escapeHtml(text);
    var src = L.rules.map(function (r) { return "(" + r.re.source + ")"; }).join("|");
    var re = new RegExp(src, "gm");
    var out = "", last = 0, m;
    while ((m = re.exec(text)) !== null) {
      out += escapeHtml(text.slice(last, m.index));
      var cls = null;
      for (var i = 0; i < L.rules.length; i++) {
        if (m[i + 1] !== undefined) { cls = L.rules[i].cls; break; }
      }
      out += '<span class="' + cls + '">' + escapeHtml(m[0]) + "</span>";
      last = m.index + m[0].length;
      if (m[0].length === 0) re.lastIndex++;
    }
    out += escapeHtml(text.slice(last));
    return out;
  }

  /* 把高亮后的 HTML 按行包裹（跨行 span 自动开闭），配合 CSS 行号计数 */
  function wrapLines(html) {
    var out = "", open = [], i = 0, n = html.length;
    while (i < n) {
      var ch = html[i];
      if (ch === "\n") {
        for (var k = open.length - 1; k >= 0; k--) out += "</span>";
        out += "\n";
        for (var j = 0; j < open.length; j++) out += '<span class="' + open[j] + '">';
        i++; continue;
      }
      if (html.slice(i, i + 13) === '<span class="') {
        var e = html.indexOf('">', i);
        var cls = html.slice(i + 13, e);
        open.push(cls);
        out += html.slice(i, e + 2);
        i = e + 2; continue;
      }
      if (html.slice(i, i + 7) === "</span>") {
        open.pop();
        out += "</span>";
        i += 7; continue;
      }
      out += ch; i++;
    }
    return out;
  }

  /* ---------- 代码块增强：头部 / 行号 / 复制 / 下载 ---------- */
  function enhanceCodeBlocks(root) {
    var blocks = (root || document).querySelectorAll("figure.codeblock");
    for (var i = 0; i < blocks.length; i++) {
      var fig = blocks[i];
      if (fig.getAttribute("data-enhanced")) continue;
      fig.setAttribute("data-enhanced", "1");
      var pre = fig.querySelector("pre.codebody");
      var codeEl = fig.querySelector("code");
      if (!pre || !codeEl) continue;

      var raw = codeEl.textContent.replace(/\n+$/, "");
      var lang = fig.getAttribute("data-lang") || langFromName(fig.getAttribute("data-file") || "");
      var label = langInfo(lang).label;

      var head = document.createElement("div");
      head.className = "codeblock-head";
      head.innerHTML =
        '<span class="fname">' + escapeHtml(fig.getAttribute("data-file") || "code") + "</span>" +
        '<span class="lang">' + label + "</span>" +
        '<span class="actions">' +
        '<button type="button" class="btn btn-copy">复制</button>' +
        (fig.getAttribute("data-file") ? '<button type="button" class="btn btn-download">下载</button>' : "") +
        "</span>";
      fig.insertBefore(head, pre);

      codeEl.innerHTML = wrapLines(highlight(raw, lang))
        .split("\n").map(function (seg) { return '<span class="line">' + seg + "</span>"; }).join("");

      var copyBtn = head.querySelector(".btn-copy");
      if (copyBtn) copyBtn.addEventListener("click", function () {
        var target = raw;
        function done(ok) { copyBtn.textContent = ok ? "已复制 \u2713" : "复制失败"; setTimeout(function () { copyBtn.textContent = "复制"; }, 1500); }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(target).then(function () { done(true); }, function () { fallbackCopy(target, done); });
        } else fallbackCopy(target, done);
      });

      var dlBtn = head.querySelector(".btn-download");
      if (dlBtn) dlBtn.addEventListener("click", function () {
        var name = fig.getAttribute("data-file") || "code.txt";
        var blob = new Blob([raw], { type: "text/plain;charset=utf-8" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url; a.download = name;
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 800);
      });
    }
  }

  function fallbackCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    done(ok);
  }

  /* ---------- 环境切换标签 ---------- */
  function initEnvTabs() {
    var groups = document.querySelectorAll(".envtabs");
    for (var g = 0; g < groups.length; g++) {
      var box = groups[g];
      var btns = box.querySelectorAll(".tabbar button");
      var panes = box.querySelectorAll(".env-pane");
      for (var b = 0; b < btns.length; b++) {
        btns[b].addEventListener("click", function () {
          var key = this.getAttribute("data-pane");
          for (var x = 0; x < btns.length; x++) btns[x].classList.toggle("active", btns[x] === this);
          for (var y = 0; y < panes.length; y++) panes[y].classList.toggle("active", panes[y].getAttribute("data-pane") === key);
        });
      }
    }
  }

  /* ---------- 自测题 ---------- */
  function initQuiz() {
    var items = document.querySelectorAll(".quiz-item");
    for (var i = 0; i < items.length; i++) {
      (function (item) {
        var answer = item.getAttribute("data-answer");
        var opts = item.querySelectorAll(".quiz-opts button");
        var feedback = item.querySelector(".quiz-feedback");
        for (var o = 0; o < opts.length; o++) {
          opts[o].addEventListener("click", function () {
            if (this.disabled) return;
            var chosen = this.getAttribute("data-opt");
            var ok = chosen === answer;
            for (var x = 0; x < opts.length; x++) {
              opts[x].disabled = true;
              if (opts[x].getAttribute("data-opt") === answer) opts[x].classList.add("correct");
              if (opts[x] === this && !ok) this.classList.add("wrong");
            }
            if (feedback) {
              feedback.classList.add("show");
              feedback.classList.toggle("ok", ok);
              feedback.classList.toggle("no", !ok);
              var mark = feedback.querySelector(".mark");
              if (mark) mark.textContent = ok ? "\u2713 答对了" : "\u2717 答错了";
            }
          });
        }
      })(items[i]);
    }
  }

  /* ---------- 首页搜索 ---------- */
  function initSearch() {
    var input = document.getElementById("searchInput");
    var results = document.getElementById("searchResults");
    if (!input || !results) return;
    var chapters = window.__CHAPTERS__ || [];
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      results.innerHTML = "";
      if (!q) return;
      var hits = chapters.filter(function (c) {
        return (c.title + " " + c.summary + " " + c.keywords + " " + c.num).toLowerCase().indexOf(q) !== -1;
      });
      if (!hits.length) {
        results.innerHTML = '<a style="cursor:default">没有匹配的章节，换个关键词试试（如：工具、权限、上下文）</a>';
        return;
      }
      hits.forEach(function (c) {
        var a = document.createElement("a");
        a.href = c.path;
        a.innerHTML = "<b>" + c.num + " · " + c.title + "</b><br>" + c.summary;
        results.appendChild(a);
      });
    });
  }

  /* ---------- 代码库筛选 ---------- */
  function initToolbox() {
    var sel = document.getElementById("toolFilterChapter");
    var txt = document.getElementById("toolFilterText");
    if (!sel || !txt) return;
    var cards = document.querySelectorAll(".tool-card");
    function apply() {
      var ch = sel.value;
      var q = txt.value.trim().toLowerCase();
      for (var i = 0; i < cards.length; i++) {
        var card = cards[i];
        var okCh = ch === "all" || card.getAttribute("data-ch") === ch;
        var okTxt = !q || (card.textContent || "").toLowerCase().indexOf(q) !== -1;
        card.style.display = okCh && okTxt ? "" : "none";
      }
    }
    sel.addEventListener("change", apply);
    txt.addEventListener("input", apply);
  }

  /* ---------- 第 3 章：代理循环演示 ---------- */
  function initLoopDemo() {
    var box = document.getElementById("loopDemo");
    if (!box) return;
    var cells = box.querySelectorAll(".loop-cell");
    var log = box.querySelector(".demo-log");
    var status = box.querySelector(".status");
    var nextBtn = box.querySelector(".btn-next");
    var resetBtn = box.querySelector(".btn-reset");
    var lines = [];
    var cur = -1;

    function paint() {
      for (var i = 0; i < cells.length; i++) cells[i].classList.toggle("on", i === cur);
      log.innerHTML = lines.map(function (l) { return l; }).join("\n");
      status.textContent = cur === -1 ? "准备就绪" : "步骤 " + (cur + 1) + " / " + cells.length;
      nextBtn.disabled = cur >= cells.length - 1;
    }
    function reset() { cur = -1; lines = []; paint(); }
    nextBtn.addEventListener("click", function () {
      if (cur >= cells.length - 1) return;
      cur++;
      if (cur === 0) { lines.push('<span class="dim"># 用户：把 notes.txt 里所有字母变成大写</span>'); lines.push("[感知] 读取当前状态：看到任务和文件内容"); }
      if (cur === 1) { lines.push("[决策] 模型决定：需要调用 read_file 工具"); }
      if (cur === 2) { lines.push("[行动] 调用工具 read_file(\"notes.txt\") -> 文件内容"); }
      if (cur === 3) { lines.push("[观察] 结果放回上下文，继续下一轮…"); lines.push('<span class="dim"># 循环直到模型返回普通文本，不再调用工具</span>'); }
      paint();
    });
    resetBtn.addEventListener("click", reset);
    reset();
  }

  /* ---------- 第 5 章：权限决策树演示 ---------- */
  function initTreeDemo() {
    var box = document.getElementById("treeDemo");
    if (!box) return;
    var root = box.querySelector(".tree-root");
    var status = box.querySelector(".status");
    var resetBtn = box.querySelector(".btn-reset");
    var steps = {
      start: {
        q: "当前权限模式是哪种？", opts: [
          { t: "default（默认）", next: "cmd" },
          { t: "plan（只规划不执行）", next: "plan" },
          { t: "bypassPermissions（全放行）", next: "bypass" }
        ]
      },
      cmd: {
        q: "模型想执行一条命令：rm -rf /tmp/build。风险如何？", opts: [
          { t: "低风险，直接放行", next: "low" },
          { t: "中高风险，需要用户确认", next: "high" }
        ]
      },
      plan: { answer: "plan 模式不会执行任何命令，只会输出计划等待你批准。所有工具调用被拒绝。" },
      bypass: { answer: "bypassPermissions 模式跳过所有确认，直接执行。这也是为什么它很危险，别在工作目录外乱用。" },
      low: { answer: "YOLO 分类器判为低风险 → 自动放行。命令记录进会话，但不打断你。" },
      high: { answer: "YOLO 分类器判为高风险 → 弹窗询问，你确认后才执行（或直接拒绝）。这就是安全边界。" }
    };
    function show(node) {
      root.innerHTML = "";
      var d = steps[node];
      var div = document.createElement("div");
      div.className = "tree-node";
      if (d.opts) {
        div.innerHTML = '<div class="q">' + d.q + "</div><div class='branch'></div>";
        var br = div.querySelector(".branch");
        d.opts.forEach(function (o) {
          var b = document.createElement("button");
          b.className = "btn"; b.textContent = o.t;
          b.addEventListener("click", function () { show(o.next); });
          br.appendChild(b);
        });
        status.textContent = "正在演示";
      } else {
        div.innerHTML = '<div class="q">结论</div><div class="tree-answer show">' + d.answer + "</div>";
        status.textContent = "演示完成，可重新开始";
      }
      root.appendChild(div);
    }
    resetBtn.addEventListener("click", function () { show("start"); });
    show("start");
  }

  /* ---------- 第 6 章：上下文压缩可视化 ---------- */
  function initCtxDemo() {
    var box = document.getElementById("ctxDemo");
    if (!box) return;
    var slider = box.querySelector('input[type="range"]');
    var bar = box.querySelector(".ctx-bar i");
    var thresh = box.querySelector(".ctx-bar .thresh");
    var meta = box.querySelector(".ctx-meta");
    var info = box.querySelector(".ctx-info");
    var WINDOW = 200000;
    function paint() {
      var pct = parseInt(slider.value, 10);
      bar.style.width = pct + "%";
      var tokens = Math.round(WINDOW * pct / 100);
      var compacting = pct >= 80;
      meta.innerHTML = "已用 " + tokens.toLocaleString() + " / " + WINDOW.toLocaleString() + " tokens · 阈值 80%";
      info.innerHTML = compacting
        ? "已到达阈值：触发 auto-compact，把最早的消息压缩成摘要，腾出空间继续工作。"
        : "还在安全区：继续累积历史。到达 80% 时自动压缩。";
      info.style.fontWeight = compacting ? "700" : "400";
    }
    slider.addEventListener("input", paint);
    paint();
  }

  /* ---------- 初始化 ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    enhanceCodeBlocks(document);
    initEnvTabs();
    initQuiz();
    initSearch();
    initToolbox();
    initLoopDemo();
    initTreeDemo();
    initCtxDemo();
  });
})();