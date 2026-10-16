# ShimiWorker watchdog v1.0 (16/10) — מופעל דרך Task Scheduler כל 2 דקות
$hb = "C:\ShimiWorker\heartbeat.txt"
$dead = $true
if (Test-Path $hb) {
    $age = ((Get-Date) - (Get-Item $hb).LastWriteTime).TotalMinutes
    if ($age -lt 5) { $dead = $false }
}
if ($dead) {
    $p = Get-Process python -ErrorAction SilentlyContinue
    if ($p) { Stop-Process -Name python -Force -ErrorAction SilentlyContinue }
    Start-Process wscript.exe -ArgumentList '"C:\ShimiWorker\start_worker.vbs"'
}
