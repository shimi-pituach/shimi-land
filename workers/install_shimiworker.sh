#!/bin/bash
# ═══ שימי וורקר — התקנה בפקודה אחת (macOS) ═══
# שימוש: bash install_shimiworker.sh <שם-מכונה> <טוקן>
# הטוקן מתקבל ב-base64 או גולמי — הסקריפט מזהה לבד.
set -e
NAME="${1:?שימוש: bash install_shimiworker.sh <שם-מכונה> <טוקן>}"
TOKEN="${2:?חסר טוקן}"
if echo "$TOKEN" | grep -qE '^[A-Za-z0-9+/=]+$' && [ "${#TOKEN}" -gt 60 ]; then
  TOKEN=$(echo "$TOKEN" | base64 -d)
fi
D="$HOME/ShimiWorker"
if [ -f "$D/config.json" ]; then echo "כבר מותקן ב-$D — לא דורס. לעדכון פנה לשימי פיתוח."; exit 1; fi
mkdir -p "$D"
echo "[1/5] מוריד את קוד הוורקר v1.2.1..."
curl -fsSL https://aidoor.shimi.land/workers/worker_cmd.py -o "$D/worker.py"
SECRET=$(LC_ALL=C tr -dc 'a-z0-9' </dev/urandom | head -c 10)
echo "[2/5] כותב קונפיג (תור: ${NAME}-worker)..."
cat > "$D/config.json" <<CFG
{"base_url": "https://solas-6a095a77.base44.app", "token": "$TOKEN", "cmd_secret": "$SECRET", "poll_seconds": 10, "worker_id": "sun-$NAME", "source": "$NAME-worker"}
CFG
echo "[3/5] מאתר פייתון עם requests..."
PY=$(command -v /opt/homebrew/bin/python3 || command -v python3)
$PY -c 'import requests' 2>/dev/null || {
  $PY -m pip install --user -q requests 2>/dev/null || $PY -m pip install --break-system-packages -q requests 2>/dev/null || true
}
$PY -c 'import requests' 2>/dev/null && echo "      requests OK ($PY)" || echo "      אזהרה: requests עדיין חסר — הוורקר ינסה להתקין לבד"
echo "[4/5] רושם הפעלה אוטומטית (launchd, KeepAlive)..."
PLIST="$HOME/Library/LaunchAgents/com.shimi.worker.plist"
if command -v launchctl >/dev/null 2>&1; then
  mkdir -p "$HOME/Library/LaunchAgents"
  cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict>
<key>Label</key><string>com.shimi.worker</string>
<key>ProgramArguments</key><array><string>$PY</string><string>$D/worker.py</string></array>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
<key>WorkingDirectory</key><string>$D</string>
<key>StandardOutPath</key><string>$D/worker_log.txt</string>
<key>StandardErrorPath</key><string>$D/worker_err.txt</string>
</dict></plist>
PL
  launchctl unload "$PLIST" 2>/dev/null || true
  launchctl load "$PLIST"
else
  echo "      launchctl לא נמצא (לא macOS) — מדלג על רישום ההפעלה"
fi
echo "[5/5] מריץ ומאמת..."
sleep 6
echo "═══ יומן העלייה ═══"
tail -5 "$D/worker_log.txt" 2>/dev/null || echo "(יומן ייווצר בעלייה הבאה)"
echo "═══════════════════════════════════"
echo "worker_id : sun-$NAME"
echo "תור       : $NAME-worker"
echo "סוד משימה : $SECRET   ← יש להעביר לשימי פיתוח"
echo "═══════════════════════════════════"
