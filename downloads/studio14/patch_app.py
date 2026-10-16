# -*- coding: utf-8 -*-
"""שדרוג אדיטיבי ל-app.py של הסטודיו (שום דבר לא נמחק): מוסיף עורך וידאו + העלאות.
שימוש: python patch_app.py <נתיב app.py>"""
import os, re, shutil, sys, py_compile

p = sys.argv[1]
bak = p + ".bak14"
if not os.path.exists(bak):
    shutil.copy(p, bak)
s = open(p, encoding="utf-8").read()
r = []

# 1. יבוא editor
if "\nimport editor" not in s:
    if "\nimport characters" in s:
        s = s.replace("\nimport characters", "\nimport characters\nimport editor", 1)
    else:
        s = s.replace("\nimport json", "\nimport json\nimport editor", 1)
    r.append("import:OK" if "\nimport editor" in s else "import:FAIL")

# 2. נתיבי GET (לפני האנקר /api/history או בסוף do_GET לפי זמינות)
if 'p == "/editor"' not in s:
    gb = ('        elif p == "/editor":\n'
          '            self._serve_file(os.path.join(UI_DIR, "editor.html"), "text/html; charset=utf-8")\n'
          '        elif p == "/api/files":\n'
          '            files = []\n'
          '            for base in [os.path.join(OUTPUT, "edit"), OUTPUT]:\n'
          '                if os.path.isdir(base):\n'
          '                    files += [(os.path.basename(base) + "/" + f) for f in sorted(os.listdir(base), reverse=True)\n'
          '                              if f.endswith((".mp4", ".png", ".gif", ".webm", ".mov"))][:100]\n'
          '            self._send(200, {"files": files[:200]})\n')
    anch = '        elif p == "/api/history":'
    if anch in s:
        s = s.replace(anch, gb + anch, 1)
    else:
        s = s.replace("    def do_POST(self):", gb.replace("        elif", "        if", 1) + "\n    def do_POST(self):", 1)
    r.append("get:OK" if 'p == "/editor"' in s else "get:FAIL")

# 3. נתיבי POST אחרי /api/video
if 'p == "/api/edit"' not in s and 'u.path == "/api/edit"' not in s:
    a2 = '            if u.path == "/api/video":\n                return self._send(200, do_video(body))'
    b2 = a2 + ('\n            if u.path == "/api/edit":\n                return self._send(200, editor.handle(body))\n'
               '            if u.path == "/api/upload":\n                return self._send(200, self._save_upload())')
    if a2 in s:
        s = s.replace(a2, b2, 1)
        r.append("post:OK")
    else:
        r.append("post:FAIL-NO-VIDEO-ANCHOR")

# 4. פונקציות עזר לפני do_GET
if "def _serve_file" not in s:
    hp = ('    def _serve_file(self, path, ctype):\n'
          '        try:\n'
          '            with open(path, "rb") as f:\n'
          '                data = f.read()\n'
          '            self.send_response(200)\n'
          '            self.send_header("Content-Type", ctype)\n'
          '            self.send_header("Content-Length", str(len(data)))\n'
          '            self.end_headers()\n'
          '            self.wfile.write(data)\n'
          '        except Exception:\n'
          '            self._send(404, {"error": "not found"})\n'
          '\n'
          '    def _save_upload(self):\n'
          '        import base64 as b64mod\n'
          '        n = int(self.headers.get("Content-Length") or 0)\n'
          '        body = json.loads(self.rfile.read(n) or b"{}")\n'
          '        name = os.path.basename(body.get("name") or ("upload_" + str(int(time.time()))))\n'
          '        data = b64mod.b64decode(body.get("data_b64") or "")\n'
          '        if not data:\n'
          '            return {"error": "empty"}\n'
          '        if not name.endswith((".mp4", ".mov", ".png", ".jpg", ".jpeg", ".gif", ".webm", ".mp3", ".wav")):\n'
          '            return {"error": "unsupported"}\n'
          '        with open(os.path.join(OUTPUT, name), "wb") as f:\n'
          '            f.write(data)\n'
          '        return {"ok": True, "file": name, "size": len(data)}\n'
          '\n')
    anchor = "    def do_GET(self):"
    if anchor in s:
        s = s.replace(anchor, hp + anchor, 1)
    else:
        s = s.replace("    def do_POST(self):", hp + "    def do_POST(self):", 1)
    r.append("helpers:OK" if "def _serve_file" in s else "helpers:FAIL")

open(p, "w", encoding="utf-8").write(s)
try:
    py_compile.compile(p, doraise=True)
    r.append("compile:OK")
except Exception as e:
    r.append("compile:FAIL " + str(e)[:80])
print("PATCH " + " | ".join(r))
