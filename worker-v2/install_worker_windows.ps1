# ShimiWorker v2 — התקנת Windows (PowerShell)
# הרצה: קליק ימני ← Run with PowerShell, או:
#   powershell -ExecutionPolicy Bypass -File install_worker_windows.ps1
# דורש: Windows 10/11, כרטיס NVIDIA מומלץ (עובד גם בלי, על CPU, לאט), אינטרנט.

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "═══ ShimiWorker v2.0 — התקנה ל-Windows ═══" -ForegroundColor Yellow

# 1) Python
try { $py = (python --version) } catch { $py = $null }
if (-not $py) {
  Write-Host "[1/6] Python לא נמצא — מתקין דרך winget..."
  winget install -e --id Python.Python.3.11
  if ($LASTEXITCODE -ne 0) { Write-Host "התקן Python 3.11 מ-python.org והרץ שוב." -ForegroundColor Red; pause; exit 1 }
} else { Write-Host "[1/6] Python: $py" }

# 2) PyTorch — CUDA אם יש כרטיס, אחרת CPU
Write-Host "[2/6] מתקין PyTorch..."
$nvidia = Get-WmiObject Win32_VideoController | Where-Object { $_.Name -match "NVIDIA" }
if ($nvidia) {
  python -m pip install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cu121
  Write-Host "      כרטיס NVIDIA: $($nvidia.Name) — הותקן CUDA build"
} else {
  python -m pip install --quiet torch torchvision
  Write-Host "      לא זוהה NVIDIA — הותקן CPU build (רנדר יעבוד, לאט יותר)" -ForegroundColor DarkYellow
}
python -m pip install --quiet diffusers transformers accelerate safetensors ftfy toml einops voluptuous requests

# 3) Git + sd-scripts (מנוע kohya)
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "[3/6] מתקין Git..."
  winget install -e --id Git.Git
}
if (-not (Test-Path "sd-scripts")) { git clone --quiet --depth 1 https://github.com/kohya-ss/sd-scripts }

# 4) הוורקר עצמו
Write-Host "[4/6] מכין תיקיות והגדרות..."
New-Item -ItemType Directory -Force -Path models, loras, jobs, renders | Out-Null
if (-not (Test-Path "shimi_worker.py")) {
  Write-Host "שים את shimi_worker.py באותה תיקייה לפני ההרצה!" -ForegroundColor Red; pause; exit 1
}
if (-not (Test-Path "config.json")) {
  @{ netboard_author = "sun-worker"; poll_seconds = 15; network_share = $true } | ConvertTo-Json | Out-File -Encoding utf8 config.json
}

# 5) מודל בסיס + לורות הרשת (~7GB חד-פעמי — יכול לקחת דקות)
Write-Host "[5/6] מוריד נכסים (מודל בסיס 7GB + לורות לאה ושני)..."
python shimi_worker.py fetch-model
python shimi_worker.py fetch-loras

# 6) בדיקה עצמית
Write-Host "[6/6] בדיקה עצמית..."
python shimi_worker.py status
Write-Host ""
Write-Host "═══ מוכן! ═══" -ForegroundColor Green
Write-Host "רנדר קנוני מלא:  python shimi_worker.py canon lea"
Write-Host "רנדר חופשי:      python shimi_worker.py render --lora lea --prompt '...' --seed 1"
Write-Host "מצב שירות:        python shimi_worker.py daemon   (מאזין לתור + מדווח ללוח)"
Write-Host "בדיקה עצמית:      python shimi_worker.py self-test"
pause
