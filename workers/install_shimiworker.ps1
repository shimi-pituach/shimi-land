# ═══ שימי וורקר — התקנה בפקודה אחת (Windows) ═══
# שימוש: powershell -ExecutionPolicy Bypass -File install_shimiworker.ps1 -Name <שם-מכונה> -Token <טוקן>
# הטוקן מתקבל ב-base64 או גולמי — הסקריפט מזהה לבד.
param([Parameter(Mandatory=$true)][string]$Name, [Parameter(Mandatory=$true)][string]$Token)
$ErrorActionPreference = "Stop"
$d = "C:\ShimiWorker"
if (Test-Path "$d\config.json") { Write-Output "כבר מותקן ב-$d — לא דורס. לעדכון פנה לשימי פיתוח."; exit 1 }
if ($Token -match '^[A-Za-z0-9+/=]+$' -and $Token.Length -gt 60) {
  $Token = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($Token))
}
New-Item -ItemType Directory -Force -Path $d | Out-Null
Write-Output "[1/5] מוריד את קוד הוורקר v1.2.1..."
Invoke-WebRequest -Uri "https://aidoor.shimi.land/workers/worker_cmd.py" -OutFile "$d\worker.py" -UseBasicParsing
$secret = -join ((48..57)+(97..122) | Get-Random -Count 10 | ForEach-Object {[char]$_})
Write-Output "[2/5] כותב קונפיג (תור: $Name-worker)..."
@{base_url="https://solas-6a095a77.base44.app"; token=$Token; cmd_secret=$secret; poll_seconds=10; worker_id="sun-$Name"; source="$Name-worker"} | ConvertTo-Json | Set-Content "$d\config.json"
Write-Output "[3/5] כותב את מנגנון השומר (מוכח בווינדוז של סאן)..."
# watchdog.ps1 — בדיקת דופק + הקפצה, זהיר למופעים מרובים
$wd = @"
`$hb = "C:\ShimiWorker\heartbeat.txt"
`$dead = `$true
if (Test-Path `$hb) {
    `$age = ((Get-Date) - (Get-Item `$hb).LastWriteTime).TotalMinutes
    if (`$age -lt 5) { `$dead = `$false }
}
if (`$dead) {
    `$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { `$_.CommandLine -like "*ShimiWorker\worker.py*" }
    if (-not `$running) { Start-Process wscript.exe -ArgumentList '"C:\ShimiWorker\start_worker.vbs"' }
}
"@
[IO.File]::WriteAllText("$d\watchdog.ps1", $wd)
# watchdog.vbs — מעטפת נסתרת (מוכח)
$wv = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell -NoProfile -ExecutionPolicy Bypass -File ""C:\ShimiWorker\watchdog.ps1""", 0, False
"@
[IO.File]::WriteAllText("$d\watchdog.vbs", $wv)
# start_worker.vbs — ההפעלה הנסתרת (מוכח)
$sv = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\ShimiWorker"
WshShell.Run """" & "python" & """" & " " & """" & "C:\ShimiWorker\worker.py" & """", 0, False
"@
[IO.File]::WriteAllText("$d\start_worker.vbs", $sv)
Write-Output "[4/5] רושם שומר שעון כל 2 דקות..."
schtasks /Create /F /TN ShimiWorkerWatchdog /SC MINUTE /MO 2 /TR "wscript.exe C:\ShimiWorker\watchdog.vbs" | Out-Null
Write-Output "[5/5] מריץ ומאמת..."
Start-Process wscript.exe -ArgumentList '"C:\ShimiWorker\start_worker.vbs"'
Start-Sleep 10
Write-Output "═══ יומן העלייה ═══"
if (Test-Path "$d\worker_log.txt") { Get-Content "$d\worker_log.txt" -Tail 5 }
Write-Output "═══════════════════════════════════"
Write-Output "worker_id : sun-$Name"
Write-Output "תור       : $Name-worker"
Write-Output "סוד משימה : $secret   ← יש להעביר לשימי פיתוח"
Write-Output "═══════════════════════════════════"
