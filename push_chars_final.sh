#!/usr/bin/env bash
# push_chars_final.sh — דחיפת גלריית הדמויות chars_final לפונח shimi-pituach/shimi-land
# שימוש (משורת השרת, אחרי שליפת הטוקן מהכספת):
#   export GITHUB_PUSH_SHIMI_SUN=ghp_...   # הערך מהכספת, מפתח GITHUB_PUSH_SHIMI_SUN
#   bash push_chars_final.sh
set -euo pipefail
SRC="${1:-/home/rxsbeewori/private_storage/chars_final}"
TOK="${GITHUB_PUSH_SHIMI_SUN:?חסר הטוקן — הגדירי export GITHUB_PUSH_SHIMI_SUN=ghp_...}"
WORK=$(mktemp -d)
echo "[1/5] משיכת הפונח…"
git clone -q "https://x-access-token:${TOK}@github.com/shimi-pituach/shimi-land.git" "$WORK/repo"
cd "$WORK/repo"
mkdir -p gallery
echo "[2/5] העתקת 9 תיקיות התמונות (מיזוג ללא קינון — cp -rT)…"
cp -rT "$SRC/noa"      gallery/noa-extra-22-10
cp -rT "$SRC/roni"     gallery/roni-22-10
cp -rT "$SRC/tal"      gallery/tal-22-10
cp -rT "$SRC/naama"    gallery/naama-22-10
cp -rT "$SRC/sapir"    gallery/sapir-22-10
cp -rT "$SRC/almog"    gallery/almog-22-10
cp -rT "$SRC/romi"     gallery/romi-22-10
cp -rT "$SRC/shira"    gallery/shira-22-10
cp -rT "$SRC/lea_extra" gallery/lea-extra-22-10
echo "[3/5] העתקת דפי הדמויות לשורש…"
cp "$SRC"/*.html .
echo "[4/5] קומיט ודחיפה…"
git add -A
git -c user.name="shimi-sun" -c user.email="shimi-sun@shimi.land" \
  commit -qm "chars_final gallery: 9 folders + 12 character pages (sun order, via push_chars_final.sh)" || true
git push -q origin main
echo "[5/5] אימות מקומי — ספירת קבצים שהועלו:"
for d in noa-extra-22-10 roni-22-10 tal-22-10 naama-22-10 sapir-22-10 almog-22-10 romi-22-10 shira-22-10 lea-extra-22-10; do
  echo "  gallery/$d: $(ls gallery/$d | wc -l) קבצים"
done
echo "OK — הדחיפה הושלמה. שימי פיתוח יפתח PR ויאמת נחיתה."
