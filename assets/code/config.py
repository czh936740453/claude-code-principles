"""
config.py —— 环境变量解析 + 特性开关（配合第 8 章）

真实 Claude Code 用环境变量和 feature flag 控制行为。
这里演示：读环境变量 -> 分层（默认 < 环境变量）-> 决定某个特性开不开。

用法:
    python config.py
    CLAUDE_CODE_COORDINATOR_MODE=1 python config.py   # 试试开启协调者模式
"""
from __future__ import annotations
import os

# 特性开关表：名字 -> (默认值, 说明)
FEATURES = {
    "COORDINATOR_MODE": (False, "多代理协调模式（manager 拆任务给多个 worker）"),
    "DAEMON":           (False, "后台守护模式（像系统服务一样跑会话）"),
    "KAIROS":           (False, "跨会话记忆（KAIROS）"),
    "BUDDY":            (False, "宠物彩蛋（BUDDY）"),
}

def feature_enabled(name: str) -> bool:
    """环境变量覆盖默认值：CLAUDECODE_<NAME>=1 即开启。"""
    if name not in FEATURES:
        return False
    default, _ = FEATURES[name]
    key = f"CLAUDECODE_{name}"
    if key in os.environ:
        return os.environ[key] not in ("0", "false", "")
    return default

def main() -> None:
    print("当前特性开关状态：")
    for name, (default, desc) in FEATURES.items():
        state = "开" if feature_enabled(name) else "关"
        print(f"  {name:<18} {state}  (默认{'开' if default else '关'}，{desc})")


if __name__ == "__main__":
    main()