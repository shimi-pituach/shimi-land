# Shimi LoRA Studio — התקנה מקומית (PowerShell)
# דורש: Windows, כרטיס NVIDIA (8GB זיכרון מומלץ), אינטרנט.
# הרצה: קליק ימני על הקובץ ← "Run with PowerShell", או: powershell -ExecutionPolicy Bypass -File setup_lora_studio.ps1

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "═══ Shimi LoRA Studio — התקנת סטודיו לוקאלי עם הלורות שלנו ═══" -ForegroundColor Yellow

# 1) Python
try { $py = (python --version) } catch { $py = $null }
if (-not $py) {
  Write-Host "[1/5] Python לא נמצא. מתקין דרך winget..."
  winget install -e --id Python.Python.3.11
  if ($LASTEXITCODE -ne 0) { Write-Host "התקן Python 3.11 ידנית מ-python.org והרץ שוב." -ForegroundColor Red; pause; exit 1 }
} else { Write-Host "[1/5] Python קיים: $py" }

# 2) ComfyUI
Write-Host "[2/5] מתקין ComfyUI (ממשק רנדר עם תמיכת LoRA מובנית)..."
if (-not (Test-Path "ComfyUI")) { git clone https://github.com/comfyanonymous/ComfyUI }

# 3) PyTorch CUDA
Write-Host "[3/5] מתקין תלויות (PyTorch CUDA) — לוקח כמה דקות..."
python -m pip install --quiet torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -m pip install --quiet -r ComfyUI\requirements.txt

# 4) הלורות שלנו
Write-Host "[4/5] מוריד את הלורות של לאה ושני לתיקיית הלורות..."
python "$PSScriptRoot\shimi_lora_fetch.py" "$PWD"

# 5) הפעלה
Write-Host "[5/5] מפעיל את הסטודיו..."
Start-Process python -ArgumentList "main.py" -WorkingDirectory "$PWD\ComfyUI"
Start-Sleep -Seconds 6
Start-Process "http://127.0.0.1:8188"

Write-Host ""
Write-Host "═══ מוכן! הדפדפן נפתח בכתובת http://127.0.0.1:8188 ═══" -ForegroundColor Green
Write-Host "לרנדר מלורה: טען ערכת ברירת מחדל (Load Default), הוסף צומת Load LoRA:"
Write-Host "  lea_lora.safetensors  ← פרומפט עם: lea shimi"
Write-Host "  shani_lora.safetensors ← פרומפט עם: shani shimi"
Write-Host "הכל רץ אצלך על המכונה: בלי תורים, בלי עלות, בלי מסננים."
pause
