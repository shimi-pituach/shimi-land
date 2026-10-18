# ═══ ShimiWorker — מסלול התקנה אחד לכל ═══
# שורה אחת שמורידה, חולצת ומתקינה הכל. רצה מתוך PowerShell פתוח (לא דאבל-קליק!).
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host ""
Write-Host "═══ ShimiWorker — התקנה אוטומטית מלאה ═══" -ForegroundColor Yellow
$dir = "C:\ShimiWorker"
Write-Host "1/4 — מוריד את החבילה האחרונה..."
$zip = "$env:TEMP\ShimiWorker-Windows.zip"
Invoke-WebRequest -Uri "https://aidoor.shimi.land/worker-v2/ShimiWorker-v2.0-Windows.zip" -OutFile $zip -UseBasicParsing
Write-Host "2/4 — חולץ ל-$dir..."
Expand-Archive -Path $zip -DestinationPath $dir -Force
Write-Host "3/4 — פותח חלון התקנה ייעודי..."
Start-Process powershell -ArgumentList '-ExecutionPolicy','Bypass','-NoExit','-Command',"Set-Location $dir; .\install_worker_windows.ps1" -WorkingDirectory $dir
Write-Host "4/4 — החלון הייעודי נפתח ומריץ את ההתקנה עם כל השלבים." -ForegroundColor Green
Write-Host ""
Write-Host "אחרי סיום ההתקנה, הרץ מהחלון הייעודי:" -ForegroundColor Yellow
Write-Host "  python shimi_worker.py self-test" -ForegroundColor White
Write-Host "  python shimi_worker.py daemon" -ForegroundColor White
Write-Host ""
Read-Host "לחץ Enter לסיום"
