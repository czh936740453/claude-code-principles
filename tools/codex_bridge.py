# -*- coding: utf-8 -*-
"""
codex_bridge.py —— 本机「Codex 直连」桥接服务
================================================
让静态网站里的「问 Codex」窗口真正调用本机 Codex CLI。

用法：
    python tools/codex_bridge.py            # 默认监听 127.0.0.1:8001
    python tools/codex_bridge.py 8002       # 自定义端口

接口：
    GET  /api/health   -> {"ok": true, "service": "codex-bridge", ...}
    POST /api/ask      -> {"ok": true, "reply": "...", "usage": {...}}
    GET  /             -> 服务信息

安全设计：
    * 只绑定 127.0.0.1（本机回环），不对外网开放。
    * 每次提问都以「只读沙箱（read-only）」运行 Codex，不会修改任何文件。
    * CORS 只放行本站来源（127.0.0.1:8000 / localhost:8000 / file://）。
    * 同一时间只处理一个问题，防止把本机资源打满。
"""
import json
import os
import shutil
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

HOST = "127.0.0.1"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 仓库根目录

ALLOWED_ORIGINS = {
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:8001",
    "http://localhost:8001",
    "null",  # file:// 直接打开网页时的 Origin
}

_lock = threading.Lock()


def codex_env():
    """补全 HOME / CODEX_HOME，让 codex CLI 能找到桌面版的登录态与配置。"""
    env = os.environ.copy()
    home = env.get("USERPROFILE") or env.get("HOME") or ""
    env.setdefault("HOME", home)
    env.setdefault("CODEX_HOME", os.path.join(home, ".codex"))
    return env


def find_codex():
    return shutil.which("codex") or "codex"


def ask_codex(question, page):
    """调用 `codex exec` 执行一次只读问答，返回 (reply, usage, error)。"""
    sys_prompt = (
        "你是「Claude Code 原理图解」学习站的答疑助手，由本机 Codex 驱动。\n"
        "回答要求：\n"
        "1. 用通俗易懂的中文，紧扣 Claude Code 的原理与本站内容"
        "（代理循环、工具系统、权限与安全、上下文管理、CLI、配置与特性门控、公开源码分析、Rust 移植等）。\n"
        "2. 先给结论，再简要解释，能举例子更好；控制在 300 字以内。\n"
        "3. 如果问题与本站主题无关，礼貌说明，并建议一个相关的问题。\n"
        "4. 不要修改任何文件，只回答问题。\n"
        f"用户当前浏览的页面：{page}\n"
        "用户的问题：\n" + question
    )
    cmd = [find_codex(), "exec", "--json", "-s", "read-only", sys_prompt]
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env=codex_env(),
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return "", {}, "Codex 回答超时（超过 5 分钟）。请重试，或换一个更短的问题。"
    except Exception as exc:  # noqa: BLE001
        return "", {}, "调用 Codex 失败：%s" % exc

    reply = ""
    usage = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            continue
        if evt.get("type") == "item.completed":
            item = evt.get("item", {})
            if item.get("type") == "agent_message" and item.get("text"):
                reply = item["text"]
        elif evt.get("type") == "turn.completed":
            usage = evt.get("usage", {})

    if not reply:
        tail = (proc.stderr or "").strip()[-600:]
        return "", usage, "Codex 没有返回内容（退出码 %s）。\n%s" % (proc.returncode, tail)

    return reply, usage, ""


class Handler(BaseHTTPRequestHandler):
    server_version = "CodexBridge/1.0"

    def _cors(self):
        origin = self.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS or not origin:
            self.send_header("Access-Control-Allow-Origin", origin or "*")
        else:
            self.send_header("Access-Control-Allow-Origin", "null")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Cache-Control", "no-store")

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self._json(200, {"ok": True, "service": "codex-bridge", "mode": "codex-cli"})
        elif path == "/":
            self._json(200, {
                "ok": True,
                "service": "codex-bridge",
                "hint": "POST /api/ask 传入 {\"question\": \"...\", \"page\": \"...\"}",
            })
        else:
            self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/ask":
            self._json(404, {"ok": False, "error": "not found"})
            return
        if not _lock.acquire(blocking=False):
            self._json(429, {"ok": False, "error": "上一个问题还在回答中，请稍等。"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"ok": False, "error": "请求体不是合法 JSON"})
                return
            question = (data.get("question") or "").strip()
            page = (data.get("page") or "").strip()
            if not question:
                self._json(400, {"ok": False, "error": "缺少 question 字段"})
                return
            reply, usage, err = ask_codex(question, page)
            if err:
                self._json(500, {"ok": False, "error": err})
            else:
                self._json(200, {"ok": True, "reply": reply, "usage": usage})
        finally:
            _lock.release()

    def log_message(self, fmt, *args):
        sys.stderr.write("[codex-bridge] %s\n" % (fmt % args))


if __name__ == "__main__":
    print("Codex Bridge 已启动：http://%s:%d" % (HOST, PORT))
    print("配合网站「问 Codex」窗口使用；按 Ctrl+C 停止。")
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")