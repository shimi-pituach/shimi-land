#!/bin/bash
# ShimiWorker v1.3 (GitHub-native) — התקנת מאק בשורה אחת. בלי בייס44, בלי טוקנים.
set -e
NAME="${1:-mac-1}"
SECRET="${2:?חובה להעביר את סוד החתימה}"
D="$HOME/ShimiWorker"
mkdir -p "$D"
curl -fsSL -o "$D/worker_cmd.py" https://raw.githubusercontent.com/sunraz/shimi-land/main/workers/worker_cmd.py
curl -fsSL -o "$D/watchdog.sh" https://raw.githubusercontent.com/sunraz/shimi-land/main/workers/watchdog.sh 2>/dev/null || true
cat > "$D/config.json" << EOF
{"worker_id": "sun-$NAME", "cmd_secret": "$SECRET", "queue_path": "mac-commands.json",
 "poll_seconds": 15, "studio_path": "$HOME/ShimiStudio/ShimiStudio-Local/studio", "gallery_local_repo": ""}
EOF
python3 -m pip install --break-system-packages -q requests 2>/dev/null || pip3 install --user -q requests 2>/dev/null || true
cd "$D"
nohup python3 worker_cmd.py >> worker_out.log 2>&1 &
# שומר עדכוני-על (launchd): כל 5 דקות מרים את הוורקר אם אינו חי
cat > "$HOME/Library/LaunchAgents/land.shimi.worker.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>Label</key><string>land.shimi.worker</string><key>ProgramArguments</key><array><string>python3</string><string>$D/worker_cmd.py</string></array><key>StartInterval</key><integer>300</integer><key>RunAtLoad</key><true/></array></dict></plist>
EOF
launchctl unload "$HOME/Library/LaunchAgents/land.shimi.worker.plist" 2>/dev/null || true
launchctl load "$HOME/Library/LaunchAgents/land.shimi.worker.plist" 2>/dev/null || true
echo "✔ ShimiWorker v1.3 מותקן ורץ כ-sun-$NAME (GitHub-native)"
