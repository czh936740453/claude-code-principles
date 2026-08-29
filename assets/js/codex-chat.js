/* codex-chat.js —— 网站「问 Codex」直连窗口
 * 通过本机桥接服务 (tools/codex_bridge.py) 调用 Codex CLI，
 * 以只读沙箱运行；桥接未启动时提供「复制问题」兜底。 */
(function () {
  "use strict";
  var FAB = document.getElementById("codexFab");
  var PANEL = document.getElementById("codexChat");
  var MSG = document.getElementById("codexMessages");
  var INPUT = document.getElementById("codexInput");
  var SEND = document.getElementById("codexSend");
  var STATUS = document.getElementById("codexStatus");
  var CLOSE = document.getElementById("codexClose");
  var CHIPS = document.getElementById("codexChips");
  if (!FAB || !PANEL || !MSG || !INPUT || !SEND || !STATUS) return;

  var BRIDGE = "http://127.0.0.1:8001";
  var LOCAL_HOSTS = ["127.0.0.1", "localhost", "[::1]", ""];
  var LOCAL = location.protocol === "file:" || LOCAL_HOSTS.indexOf(location.hostname) !== -1;
  var state = "connecting"; // connecting | online | offline | remote
  var busy = false;

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = String(s);
    return d.innerHTML;
  }

  function setStatus(cls, text) {
    STATUS.className = "codex-status " + cls;
    STATUS.textContent = text;
  }

  function bubble(role, html) {
    var div = document.createElement("div");
    div.className = "codex-msg " + role;
    div.innerHTML = html;
    MSG.appendChild(div);
    MSG.scrollTop = MSG.scrollHeight;
    return div;
  }

  function typing(on) {
    var t = document.getElementById("codexTyping");
    if (on && !t) {
      t = bubble("bot", '<span class="dot"></span><span class="dot"></span><span class="dot"></span>');
      t.id = "codexTyping";
    } else if (!on && t) {
      t.remove();
    }
  }

  function postAsk(question, page) {
    return fetch(BRIDGE + "/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question, page: page || "" })
    }).then(function (r) { return r.json(); });
  }

  function fallbackCopy(question) {
    var wrap = document.createElement("div");
    wrap.className = "codex-fallback";
    var hint = document.createElement("p");
    hint.textContent = "也可以把问题复制到 Codex 窗口提问：";
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-copy";
    btn.textContent = "复制问题";
    btn.addEventListener("click", function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(question).then(function () {
          btn.textContent = "已复制 ✓";
        }, function () { btn.textContent = "复制失败，请手动选中"; });
      } else {
        btn.textContent = "当前浏览器不支持自动复制";
      }
    });
    wrap.appendChild(hint);
    wrap.appendChild(btn);
    return wrap;
  }

  function send(question) {
    question = (question || "").trim();
    if (!question || busy) return;
    busy = true;
    SEND.disabled = true;
    bubble("user", esc(question));
    if (state === "offline" || state === "remote") {
      var b = bubble("bot", esc(
        state === "remote"
          ? "当前是通过公网地址打开的，浏览器无法访问你电脑上的 Codex。"
          : "本机 Codex 桥接未启动。请先运行 tools\\start_bridge.ps1（或 python tools\\codex_bridge.py），然后刷新本页。"
      ));
      b.appendChild(fallbackCopy(question));
      busy = false;
      SEND.disabled = false;
      return;
    }
    typing(true);
    postAsk(question, document.title).then(function (res) {
      typing(false);
      if (res && res.ok && res.reply) {
        bubble("bot", esc(res.reply));
      } else {
        var msg = (res && res.error) || "未知错误";
        var b2 = bubble("bot", esc("Codex 暂时无法回答：\n" + msg));
        b2.appendChild(fallbackCopy(question));
      }
    }).catch(function (e) {
      typing(false);
      setStatus("offline", "直连中断 · 请检查桥接服务");
      var b3 = bubble("bot", esc("连接桥接服务失败：" + e));
      b3.appendChild(fallbackCopy(question));
    }).then(function () {
      busy = false;
      SEND.disabled = false;
      INPUT.focus();
    });
  }

  function init() {
    FAB.addEventListener("click", function () {
      var open = PANEL.classList.toggle("open");
      FAB.classList.toggle("active", open);
      if (open) INPUT.focus();
    });
    CLOSE.addEventListener("click", function () {
      PANEL.classList.remove("open");
      FAB.classList.remove("active");
    });
    SEND.addEventListener("click", function () {
      send(INPUT.value);
      INPUT.value = "";
      autoGrow();
    });
    INPUT.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send(INPUT.value);
        INPUT.value = "";
        autoGrow();
      }
    });
    INPUT.addEventListener("input", autoGrow);
    [].forEach.call(CHIPS.querySelectorAll("button"), function (btn) {
      btn.addEventListener("click", function () { send(btn.textContent); });
    });

    if (!LOCAL) {
      state = "remote";
      setStatus("remote", "公网打开 · 无法直连本机");
      return;
    }
    setStatus("connecting", "正在连接本机 Codex…");
    var timer = setTimeout(function () { afterHealth({ ok: false }); }, 3500);
    fetch(BRIDGE + "/api/health")
      .then(function (r) { return r.json(); })
      .then(afterHealth, function () { afterHealth({ ok: false }); });
    function afterHealth(res) {
      clearTimeout(timer);
      if (res && res.ok) {
        state = "online";
        setStatus("online", "Codex 已直连 · 可以提问");
      } else {
        state = "offline";
        setStatus("offline", "桥接未启动 · 先运行 tools\\start_bridge.ps1");
      }
    }
  }

  function autoGrow() {
    INPUT.style.height = "auto";
    INPUT.style.height = Math.min(INPUT.scrollHeight, 96) + "px";
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();