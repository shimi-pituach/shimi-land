$ErrorActionPreference = "Stop"
$d = "C:\ShimiWorkerCmd"
New-Item -ItemType Directory -Force -Path $d | Out-Null
Invoke-WebRequest -Uri "https://aidoor.shimi.land/workers/worker_cmd.py" -OutFile "$d\worker.py" -UseBasicParsing
$vbs = 'CreateObject("WScript.Shell").Run "python """C:\ShimiWorkerCmd\worker.py""""", 0, False'
[IO.File]::WriteAllText("$d\start.vbs", $vbs)
$src = Get-Content C:\ShimiWorker\config.json -Raw | ConvertFrom-Json
$src | Add-Member -Force NoteProperty worker_id "sun-windows-1-cmd"
$src | Add-Member -Force NoteProperty source "windows-commands"
$src | Select-Object -Property * -ExcludeProperty studio_path | ConvertTo-Json | Set-Content "$d\config.json"
schtasks /Create /F /TN ShimiWorkerCmdWatchdog /SC MINUTE /MO 5 /TR "wscript.exe C:\ShimiWorkerCmd\start.vbs" | Out-Null
Start-Process wscript.exe -ArgumentList '"C:\ShimiWorkerCmd\start.vbs"'
Write-Output "CMD_WORKER_DEPLOYED"
