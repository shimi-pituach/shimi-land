#!/bin/bash
set -e
D="$HOME/ShimiWorkerCmd"
mkdir -p "$D"
curl -s -o "$D/worker.py" https://aidoor.shimi.land/workers/worker_cmd.py
python3 - << 'PYEOF'
import json, os
src = json.load(open(os.path.expanduser("~/ShimiWorker/config.json")))
src["worker_id"] = "sun-mac-1-cmd"
src["source"] = "mac-commands"
dst = os.path.expanduser("~/ShimiWorkerCmd/config.json")
json.dump(src, open(dst, "w"))
print("config written")
PYEOF
PLIST="$HOME/Library/LaunchAgents/com.shimi.worker.cmd.plist"
cat > "$PLIST" << PLEOF
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>Label</key><string>com.shimi.worker.cmd</string>
  <key>ProgramArguments</key><array><string>python3</string><string>$D/worker.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>WorkingDirectory</key><string>$D</string>
  <key>StandardOutPath</key><string>$D/worker_log.txt</string>
  <key>StandardErrorPath</key><string>$D/worker_err.txt</string>
</dict></plist>
PLEOF
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
sleep 3
echo "MAC_CMD_DEPLOYED"
