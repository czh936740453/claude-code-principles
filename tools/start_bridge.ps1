# start_bridge.ps1 —— 启动「Codex 直连」桥接服务
# 用法：
#   1) 右键此文件 → 使用 PowerShell 运行
#   2) 或：powershell -ExecutionPolicy Bypass -File .\tools\start_bridge.ps1
# 启动成功后，刷新网站页面，「问 Codex」窗口会显示「Codex 已直连」。
# 停止：在窗口里按 Ctrl+C。
$ErrorActionPreference = "Stop"

$env:HOME = $env:USERPROFILE
$env:CODEX_HOME = Join-Path $env:USERPROFILE ".codex"

$bridge = Join-Path $PSScriptRoot "codex_bridge.py"
if (-not (Test-Path $bridge)) {
    Write-Host "找不到 $bridge，请确认在仓库根目录运行。" -ForegroundColor Red
    exit 1
}

Write-Host "正在启动 Codex 直连桥接服务…" -ForegroundColor Cyan
python $bridge