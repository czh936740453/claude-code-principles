/* ============================================================
   poly.js —— 首页「章节多面体」
   纯 CSS 3D 十棱柱：可拖动旋转，每面对应一章；
   未完成 = 灰色渐变，已完成 = 不同色相的彩色渐变。
   进度数据与 nav.js 共用 localStorage（cc_completed）。
   ============================================================ */
(function () {
  "use strict";
  var scene = document.getElementById("polyScene");
  var poly = document.getElementById("poly");
  var spin = document.getElementById("polySpin");
  if (!scene || !poly || !spin) return;

  var CHAPTERS = window.__CHAPTERS__ || [];
  if (!CHAPTERS.length) return;

  var faces = [];
  var rx = -16, ry = 0;                 // 初始俯仰角：让顶面微微朝向读者
  var dragging = false, moved = false;
  var startX = 0, startY = 0, baseRx = 0, baseRy = 0;
  var downFace = null;
  var resumeTimer = null;

  /* 从 CSS 变量读取当前尺寸（响应式：手机端更小） */
  function dims() {
    var s = window.getComputedStyle(scene);
    return {
      w: parseFloat(s.getPropertyValue("--pf-w")) || 112,
      h: parseFloat(s.getPropertyValue("--pf-h")) || 200,
      r: parseFloat(s.getPropertyValue("--pf-r")) || 176
    };
  }

  /* 生成 10 个面，每面对应一章 */
  function build() {
    var html = "";
    for (var i = 0; i < CHAPTERS.length; i++) {
      var ch = CHAPTERS[i];
      var id = "ch" + ch.num;
      html +=
        '<div class="poly-face" data-id="' + id + '" data-href="' + ch.path + '">' +
        '<div class="poly-card">' +
        '<span class="pf-ch">CH ' + ch.num + '</span>' +
        '<b class="pf-num">' + ch.num + '</b>' +
        '<span class="pf-bar"></span>' +
        '<span class="pf-title">' + ch.title + '</span>' +
        "</div></div>";
    }
    poly.innerHTML = html;
    faces = poly.querySelectorAll(".poly-face");
  }

  /* 按当前 CSS 变量把 10 个面摆成正十边形 */
  function layout() {
    var d = dims();
    var n = faces.length;
    for (var i = 0; i < n; i++) {
      var a = (360 / n) * i;
      var f = faces[i];
      f.style.width = d.w + "px";
      f.style.height = d.h + "px";
      f.style.left = (-d.w / 2) + "px";
      f.style.top = (-d.h / 2) + "px";
      f.style.transform = "rotateY(" + a + "deg) translateZ(" + d.r + "px)";
    }
  }

  /* 已完成章节集合 */
  function completedSet() {
    var arr = [];
    try { arr = JSON.parse(localStorage.getItem("cc_completed") || "[]"); } catch (e) {}
    var set = {};
    for (var i = 0; i < arr.length; i++) set[arr[i]] = true;
    return set;
  }

  /* 按进度上色：完成 = 彩色渐变，未完成 = 灰色渐变 */
  function paint() {
    var done = completedSet();
    var cards = poly.querySelectorAll(".poly-card");
    for (var i = 0; i < cards.length; i++) {
      var face = cards[i].parentNode;
      var id = face.getAttribute("data-id");
      var num = parseInt((id || "ch1").replace(/^ch/, ""), 10) || 1;
      var isDone = !!done[id];
      cards[i].classList.toggle("done", isDone);
      if (isDone) {
        var hue = ((num - 1) * 36) % 360;
        cards[i].style.background =
          "linear-gradient(160deg, hsl(" + hue + ", 68%, 62%), hsl(" +
          ((hue + 42) % 360) + ", 74%, 44%))";
      } else {
        cards[i].style.background = "";
      }
    }
  }

  function update() {
    poly.style.transform = "rotateX(" + rx + "deg) rotateY(" + ry + "deg)";
  }

  /* 自动旋转：空闲时缓慢自转，拖动/按键后暂停，数秒后恢复 */
  function pauseSpin() {
    spin.classList.add("paused");
    if (resumeTimer) clearTimeout(resumeTimer);
  }
  function resumeSpin() {
    /* 无论系统是否偏好减少动效，交互结束后都恢复自动旋转；
       减动画效的用户由 CSS 用更慢的速度呈现（见 style.css）。 */
    if (resumeTimer) clearTimeout(resumeTimer);
    resumeTimer = setTimeout(function () {
      spin.classList.remove("paused");
      resumeTimer = null;
    }, 2800);
  }

  /* 拖动旋转 + 点击跳转 */
  scene.addEventListener("pointerdown", function (e) {
    dragging = true; moved = false;
    startX = e.clientX; startY = e.clientY;
    baseRx = rx; baseRy = ry;
    downFace = e.target && e.target.closest ? e.target.closest(".poly-face") : null;
    scene.classList.add("dragging");
    pauseSpin();
    try { scene.setPointerCapture(e.pointerId); } catch (err) {}
    e.preventDefault();
  });
  scene.addEventListener("pointermove", function (e) {
    if (!dragging) return;
    var dx = e.clientX - startX, dy = e.clientY - startY;
    if (Math.abs(dx) + Math.abs(dy) > 4) moved = true;
    ry = baseRy + dx * 0.35;
    rx = Math.max(-75, Math.min(75, baseRx - dy * 0.35));
    update();
  });
  function endDrag(e) {
    if (!dragging) return;
    dragging = false;
    scene.classList.remove("dragging");
    try { scene.releasePointerCapture(e.pointerId); } catch (err) {}
    if (moved) { resumeSpin(); return; }
    if (downFace) {
      var href = downFace.getAttribute("data-href");
      if (href) { location.href = href; return; }
    }
    resumeSpin();
  }
  scene.addEventListener("pointerup", endDrag);
  scene.addEventListener("pointercancel", function () {
    dragging = false; moved = false;
    scene.classList.remove("dragging");
    resumeSpin();
  });

  /* 键盘：方向键旋转（无障碍） */
  scene.setAttribute("tabindex", "0");
  scene.setAttribute("role", "group");
  scene.setAttribute("aria-label", "章节多面体：可拖动旋转，点击任意面进入对应章节；方向键也可旋转");
  scene.addEventListener("keydown", function (e) {
    var step = e.shiftKey ? 30 : 8;
    if (e.key === "ArrowLeft") ry -= step;
    else if (e.key === "ArrowRight") ry += step;
    else if (e.key === "ArrowUp") rx = Math.max(-75, rx - step);
    else if (e.key === "ArrowDown") rx = Math.min(75, rx + step);
    else return;
    e.preventDefault();
    pauseSpin(); update(); resumeSpin();
  });

  /* 进度联动：nav.js 每次渲染进度后广播 cc:progress；跨页用 storage 事件兜底 */
  window.addEventListener("cc:progress", paint);
  window.addEventListener("storage", function (e) {
    if (e.key === "cc_completed") paint();
  });

  /* 窗口尺寸变化时按响应式变量重新摆放 */
  var resizeTimer = null;
  window.addEventListener("resize", function () {
    if (resizeTimer) return;
    resizeTimer = setTimeout(function () { resizeTimer = null; layout(); }, 120);
  });

  spin.classList.add("auto");
  build(); layout(); paint(); update();
})();