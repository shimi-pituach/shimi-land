# תלויות + פאטץ' 1.5 לסטודיו בווינדוז (מרוץ מהתור, v1.3.3+)
$ErrorActionPreference = "Continue"
Write-Output "PYVER"; python --version 2>&1
Write-Output "STEP_NUMPY"
python -m pip install -q --no-input numpy 2>&1 | Select-Object -Last 1
python -c "import numpy; print('NUMPY_OK', numpy.__version__)" 2>&1 | Select-Object -First 1
Write-Output "STEP_DIFF"
python -m pip install -q --no-input diffusers transformers accelerate safetensors 2>&1 | Select-Object -Last 1
python -c "import diffusers; print('DIFFUSERS_OK', diffusers.__version__)" 2>&1 | Select-Object -First 1
Write-Output "STEP_TORCH"
python -c "import torch; print('TORCH_OK', torch.__version__, torch.cuda.is_available())" 2>&1 | Select-Object -First 1
Write-Output "STEP_PATCH"
$d = "C:\ShimiStudio\ShimiStudio-Local\studio"
curl.exe -s -o "$d\patch15.py" https://raw.githubusercontent.com/sunraz/shimi-land/main/downloads/studio15/patch15.py
python "$d\patch15.py"
Write-Output "STEP_RESTART"
Get-CimInstance Win32_Process -Filter "name='python.exe'" | Where-Object {$_.CommandLine -like "*app.py*"} | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep 2
Start-Process -WindowStyle Hidden python -ArgumentList "app.py" -WorkingDirectory $d
Start-Sleep 10
Write-Output ("SRV=" + (curl.exe -s -o NUL -w "%{http_code}" http://localhost:7861/editor --max-time 8))
Write-Output "DONE"
