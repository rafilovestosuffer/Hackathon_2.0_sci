# SkinAI Bangladesh - Telegram bot launcher
# Run when you want the bot live for a demo. Ctrl+C stops everything.
#
# Usage:
#   cd C:\Users\Rafi\Desktop\skinai-bangladesh
#   powershell -ExecutionPolicy Bypass -File scripts\start_bot.ps1

$ErrorActionPreference = 'Stop'

$RepoRoot       = Split-Path -Parent $PSScriptRoot
$EnvFile        = Join-Path $RepoRoot ".env"
$LogDir         = Join-Path $env:TEMP "skinai_bot"
$UvicornLog     = Join-Path $LogDir "uvicorn.log"
$TunnelLog      = Join-Path $LogDir "cloudflared.log"
$CloudflaredExe = "C:\Program Files (x86)\cloudflared\cloudflared.exe"
$Port           = 8765

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
Clear-Content $UvicornLog -ErrorAction SilentlyContinue
Clear-Content $TunnelLog  -ErrorAction SilentlyContinue

if (-not (Test-Path $EnvFile)) {
    Write-Host "ERROR: .env not found at $EnvFile" -ForegroundColor Red
    exit 1
}
$tokenLine = Get-Content $EnvFile | Where-Object { $_ -match '^TELEGRAM_BOT_TOKEN=' }
if (-not $tokenLine) {
    Write-Host "ERROR: TELEGRAM_BOT_TOKEN not found in .env" -ForegroundColor Red
    exit 1
}
$Token = $tokenLine -replace '^TELEGRAM_BOT_TOKEN=', ''

Write-Host ""
Write-Host "=============================================="  -ForegroundColor Cyan
Write-Host " SkinAI Bangladesh - Telegram Bot Launcher"    -ForegroundColor Cyan
Write-Host "=============================================="  -ForegroundColor Cyan
Write-Host ""

# 1. Start uvicorn
Write-Host "[1/4] Starting uvicorn on 127.0.0.1:$Port ..." -ForegroundColor Yellow
$uvProc = Start-Process -FilePath "python" `
    -ArgumentList "-m","uvicorn","webhook.server:app","--host","127.0.0.1","--port","$Port","--log-level","info" `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $UvicornLog `
    -RedirectStandardError  "$UvicornLog.err" `
    -PassThru -WindowStyle Hidden

$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Write-Host "      uvicorn failed to start. Check $UvicornLog" -ForegroundColor Red
    exit 1
}
Write-Host ("      uvicorn ready, PID=" + $uvProc.Id) -ForegroundColor Green

# 2. Start cloudflared
Write-Host "[2/4] Starting Cloudflare Tunnel ..." -ForegroundColor Yellow
if (-not (Test-Path $CloudflaredExe)) {
    Write-Host "      cloudflared not found at $CloudflaredExe" -ForegroundColor Red
    Stop-Process -Id $uvProc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}
$tunProc = Start-Process -FilePath $CloudflaredExe `
    -ArgumentList "tunnel","--url","http://127.0.0.1:$Port","--no-autoupdate" `
    -RedirectStandardOutput $TunnelLog `
    -RedirectStandardError  "$TunnelLog.err" `
    -PassThru -WindowStyle Hidden

# 3. Wait for tunnel URL
Write-Host "[3/4] Waiting for tunnel URL ..." -ForegroundColor Yellow
$tunnelUrl = $null
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Seconds 1
    foreach ($f in @($TunnelLog, "$TunnelLog.err")) {
        if (Test-Path $f) {
            $m = Select-String -Path $f -Pattern "https://[a-z0-9-]+\.trycloudflare\.com" -AllMatches | Select-Object -Last 1
            if ($m) { $tunnelUrl = $m.Matches[0].Value; break }
        }
    }
    if ($tunnelUrl) { break }
}
if (-not $tunnelUrl) {
    Write-Host "      Tunnel never produced a URL. Check $TunnelLog and $TunnelLog.err" -ForegroundColor Red
    Stop-Process -Id $uvProc.Id  -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $tunProc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "      Tunnel URL: $tunnelUrl" -ForegroundColor Green

# 4. Register Telegram webhook (with retry — trycloudflare DNS can take up to 60s to propagate)
Write-Host "[4/4] Registering Telegram webhook ..." -ForegroundColor Yellow
$webhookUrl = "$tunnelUrl/webhook/telegram"
$payload = '{"url":"' + $webhookUrl + '","max_connections":10,"drop_pending_updates":true}'
$registered = $false
$lastErr = ""
for ($attempt = 1; $attempt -le 20; $attempt++) {
    $raw = & curl.exe -s -X POST "https://api.telegram.org/bot$Token/setWebhook" `
        -H "Content-Type: application/json" -d $payload 2>&1
    if ($raw -match '"ok"\s*:\s*true') { $registered = $true; break }
    $lastErr = $raw
    Write-Host ("      attempt " + $attempt + "/20: " + $raw.Substring(0, [Math]::Min(110, $raw.Length))) -ForegroundColor DarkGray
    Start-Sleep -Seconds 6
}
if (-not $registered) {
    Write-Host "      Telegram refused webhook after 20 attempts (2 min)." -ForegroundColor Red
    Write-Host "      Last error: $lastErr" -ForegroundColor Red
    Write-Host "      Tunnel URL was: $tunnelUrl" -ForegroundColor Yellow
    Write-Host "      Try: curl $tunnelUrl/health" -ForegroundColor Yellow
    Stop-Process -Id $uvProc.Id  -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $tunProc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}
Write-Host "      Webhook registered." -ForegroundColor Green

Write-Host ""
Write-Host "=============================================="  -ForegroundColor Cyan
Write-Host " BOT IS LIVE"                                    -ForegroundColor Green
Write-Host "=============================================="  -ForegroundColor Cyan
Write-Host "  Open Telegram and message:  @SkinAIBDBot"
Write-Host "  Direct link:                https://t.me/SkinAIBDBot"
Write-Host "  Tunnel URL:                 $tunnelUrl"
Write-Host "  Webhook:                    $webhookUrl"
Write-Host ""
Write-Host "  Logs:"
Write-Host "    uvicorn      $UvicornLog"
Write-Host "    cloudflared  $TunnelLog"
Write-Host ""
Write-Host "  Press Ctrl+C to stop the bot." -ForegroundColor Yellow
Write-Host "=============================================="  -ForegroundColor Cyan
Write-Host ""

try {
    Get-Content $UvicornLog -Wait -Tail 20
} finally {
    Write-Host ""
    Write-Host "Shutting down..." -ForegroundColor Yellow
    try { Invoke-WebRequest -Uri "https://api.telegram.org/bot$Token/deleteWebhook?drop_pending_updates=true" -UseBasicParsing | Out-Null } catch {}
    Stop-Process -Id $uvProc.Id  -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $tunProc.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Stopped." -ForegroundColor Green
}
