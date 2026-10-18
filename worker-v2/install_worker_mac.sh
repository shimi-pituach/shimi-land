#!/bin/bash
# ShimiWorker v2 — התקנת macOS (Apple Silicon) ולינוקס
# הרצה: bash install_worker_mac.sh
# דורש: macOS על Apple Silicon (M1/M2/M3/M4) מומלץ, אינטרנט.

set -e
echo "═══ ShimiWorker v2.0 — התקנה ל-macOS ═══"

# 1) Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "[1/6] Python לא נמצא — מתקין דרך Homebrew..."
  if ! command -v brew >/dev/null 2>&1; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  brew install python@3.11
fi
echo "[1/6] Python: $(python3 --version)"

# 2) PyTorch — על מאק זה MPS (כרטיס הגרפיקה של Apple בתוך השבב)
echo "[2/6] מתקין PyTorch (MPS)..."
python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet torch torchvision
python3 -m pip install --quiet diffusers transformers accelerate safetensors ftfy toml einops voluptuous requests

# 3) Git + מנוע kohya
echo "[3/6] מתקין מנוע kohya (sd-scripts)..."
if ! command -v git >/dev/null 2>&1; then
  echo "מתקין Git דרך Homebrew..."; brew install git
fi
[ -d sd-scripts ] || git clone --quiet --depth 1 https://github.com/kohya-ss/sd-scripts

# 4) תיקיות והגדרות
echo "[4/6] מכין תיקיות..."
mkdir -p models loras jobs renders
[ -f shimi_worker.py ] || { echo "שים את shimi_worker.py באותה תיקייה לפני ההרצה!"; exit 1; }
[ -f config.json ] || cat > config.json <<'EOF'
{
  "netboard_author": "sun-worker",
  "poll_seconds": 15,
  "network_share": true
}
EOF

# 5) נכסים
echo "[5/6] מוריד נכסים (מודל בסיס 7GB + לורות לאה ושני) — יכול לקחת דקות..."
python3 shimi_worker.py fetch-model
python3 shimi_worker.py fetch-loras

# 6) בדיקה
echo "[6/6] מצב:"
python3 shimi_worker.py status
echo ""
echo "═══ מוכן! ═══"
echo "רנדר קנוני מלא:  python3 shimi_worker.py canon lea"
echo "רנדר חופשי:      python3 shimi_worker.py render --lora lea --prompt '...' --seed 1"
echo "מצב שירות:        python3 shimi_worker.py daemon"
echo "בדיקה עצמית:      python3 shimi_worker.py self-test"
