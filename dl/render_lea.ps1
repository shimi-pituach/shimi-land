$ErrorActionPreference = 'Continue'
$base = 'http://localhost:7861'
$st = curl.exe -s -o NUL -w "%{http_code}" "$base/"
Write-Output "STUDIO=$st"
if ($st -ne '200') { Write-Output 'RESULT: studio_down'; exit 0 }
$body = '{"character":"lea","pose":"front","engine":"realvisxl_v5","seed":151011,"prompt":"wearing a bikini, standing on a sunny beach at golden hour sunset, ocean waves","orientation":"portrait"}'
$r = curl.exe -s -X POST -H 'Content-Type: application/json' -d $body "$base/api/generate" --max-time 900
Write-Output "GEN=$r"
try { $j = $r | ConvertFrom-Json } catch { Write-Output 'RESULT: bad_json'; exit 0 }
if (-not $j.ok) {
  Write-Output ("RESULT: gen_fail:" + $j.error)
  # ניסיון חוזר אחרי הורדת מודלים אם חסרים
  if ($j.error -match 'model|download|file') {
    Write-Output 'RETRY: running download_models.py'
    Set-Location C:\ShimiStudio\ShimiStudio-Local\studio
    python download_models.py 2>&1 | Select-Object -Last 5
    $r2 = curl.exe -s -X POST -H 'Content-Type: application/json' -d $body "$base/api/generate" --max-time 900
    Write-Output "GEN2=$r2"
    try { $j = $r2 | ConvertFrom-Json } catch { exit 0 }
  }
  if (-not $j.ok) { exit 0 }
}
$f = $j.file; if (-not $f) { $f = $j.output }
$cands = @("C:\ShimiStudio\ShimiStudio-Local\studio\output\$f", "C:\ShimiStudio\ShimiStudio-Local\studio\$f")
$src = $null
foreach ($c in $cands) { if (Test-Path $c) { $src = $c; break } }
if (-not $src) { Write-Output 'RESULT: file_not_found'; exit 0 }
Write-Output "SRC=$src"
$u = curl.exe -s -F "fileToUpload=@$src" -F 'reqtype=fileupload' 'https://catbox.moe/user/api.php' --max-time 300
Write-Output "CATBOX=$u"
if ($u -match '^https://') { Write-Output 'RESULT: render_ok' } else { Write-Output 'RESULT: upload_fail' }
