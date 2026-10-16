# -*- coding: utf-8 -*-
"""ShimiWorker v1.3.0 (16/10) — GitHub-native: אפס תלות בבייס44.
מה השתנה מ-v1.2.1 (פקודת סאן 16/10 18:17: "רק מהשרת שלנו"):
- תור הפקודות: קובץ JSON ב-GitHub (raw.githubusercontent.com) במקום API של בייס44. קריאה חינמית, בלי טוקן.
- מניעת כפילויות: רשימת משימות שבוצעו נשמרת מקומית (done.json) — בלי צורך בכתיבה לשרת.
- תוצאות ודופק: דרך ntfy.sh (חינמי, HTTPS, בלי חשבון) — שימי פיתוח מנווט ורואה הכל חי.
- חתימה: פקודות נדחות אם אינן חתומות ב-cmd_secret (התור ציבורי — זו ההגנה).
- gh_token אופציונלי ב-config: אם קיים, התוצאות גם נכתבות לקובץ התור עצמו.
שמור מ-v1.2.1: אנטי-קריסה, עדכון עצמי, מלקט יומן, טיימאאוט לכל משימה, ניתוב win-/mac-.
"""
import sys, os, json, time, subprocess, platform, traceback, threading, glob
import urllib.request
from datetime import datetime, timezone

VERSION = "1.3.0"
REMOTE_VERSION_URL = "https://aidoor.shimi.land/worker_version.txt"
REMOTE_CODE_URL = "https://aidoor.shimi.land/worker_latest.py"

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "worker_log.txt")
HB_FILE = os.path.join(HERE, "heartbeat.txt")
DONE_FILE = os.path.join(HERE, "done.json")

DEFAULTS = {
    "repo": "sunraz/shimi-land",
    "queue_base": "https://raw.githubusercontent.com/sunraz/shimi-land/main/queue/",
    "queue_path": "windows-commands.json",
    "cmd_secret": "",
    "poll_seconds": 15,
    "worker_id": "unknown-worker",
    "studio_path": "",
    "gallery_local_repo": "",
    "ntfy_topic": "",
    "gh_token": "",
}

TASKS_DONE = [0]
START_TS = time.time()


def platform_tag():
    if os.name == "nt":
        return "win"
    return "mac"


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(datetime.now().strftime("%m-%d %H:%M:%S | ") + msg + "\n")
    except Exception:
        pass


def trim_log():
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 200000:
            with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                tail = f.read()[-100000:]
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write(tail)
    except Exception:
        pass


def load_config():
    cfg = dict(DEFAULTS)
    p = os.path.join(HERE, "config.json")
    try:
        with open(p, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def done_ids(cfg):
    try:
        with open(DONE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def mark_done(cfg, tid):
    ids = done_ids(cfg)
    ids.add(tid)
    keep = list(ids)[-500:]
    with open(DONE_FILE, "w", encoding="utf-8") as f:
        json.dump(keep, f)


def touch_heartbeat(cfg):
    try:
        with open(HB_FILE, "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())
    except Exception:
        pass


def ntfy(cfg, title, body):
    topic = cfg.get("ntfy_topic") or ("shimiw-" + str(cfg.get("worker_id") or "x"))
    try:
        req = urllib.request.Request(
            "https://ntfy.sh/" + topic,
            data=(title + "\n" + str(body)[:3000]).encode("utf-8"),
            headers={"Title": "ShimiWorker", "Priority": "default"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def gh_raw(cfg, path):
    url = (cfg.get("queue_base") or DEFAULTS["queue_base"]) + path + "?v=" + str(int(time.time()))
    r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
    return json.loads(r.read().decode("utf-8"))


def fetch_tasks(cfg):
    try:
        d = gh_raw(cfg, cfg.get("queue_path") or "windows-commands.json")
    except Exception as e:
        log("קריאת תור נכשלה: " + str(e)[:120])
        return []
    if not isinstance(d, dict) or not isinstance(d.get("items"), list):
        return []
    done = done_ids(cfg)
    return [t for t in d["items"]
            if t.get("status") == "pending" and t.get("id") not in done]


def gh_commit(cfg, path, obj, msg):
    """כתיבה אופציונלית לתור (רק אם gh_token ב-config)."""
    tok = cfg.get("gh_token") or ""
    if not tok:
        return False
    try:
        import base64
        api = "https://api.github.com/repos/%s/contents/queue/%s" % (cfg.get("repo"), path)
        hr = urllib.request.Request(api, headers={"Authorization": "token " + tok, "User-Agent": "shimiworker"})
        j = json.loads(urllib.request.urlopen(hr, timeout=20).read().decode())
        body = json.dumps({"message": msg[:100], "content": base64.b64encode(
            json.dumps(obj, ensure_ascii=False, indent=1).encode()).decode(), "sha": j["sha"]}).encode()
        req = urllib.request.Request(api, data=body, method="PUT",
                                     headers={"Authorization": "token " + tok, "User-Agent": "shimiworker",
                                              "Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        log("כתיבה ל-GitHub נכשלה (לא קריטי): " + str(e)[:120])
        return False


def update_task(cfg, task_id, data):
    """מדווח תוצאה: ntfy תמיד; כתיבה לקובץ התור רק אם יש gh_token."""
    ntfy(cfg, "✔ " + str(data.get("title") or task_id)[:80],
          "result: " + str(data.get("result") or "")[:2500])
    if cfg.get("gh_token"):
        try:
            d = gh_raw(cfg, cfg.get("queue_path"))
            for t in d.get("items", []):
                if t.get("id") == task_id:
                    t.update({"status": "done", "result": str(data.get("result"))[:2000],
                              "updated_date": datetime.now(timezone.utc).isoformat()})
            gh_commit(cfg, cfg.get("queue_path"), d, "worker: result " + str(task_id)[:12])
        except Exception:
            pass


def cmd_status(cfg, args):
    lines = ["v" + VERSION + " | " + platform_tag() + " | up " + str(int((time.time() - START_TS) // 60)) + "m",
             "done=" + str(TASKS_DONE[0]) + " | worker_id=" + str(cfg.get("worker_id"))]
    try:
        import requests
        r = requests.get("http://localhost:7861/api/history", timeout=10)
        lines.append("studio history items: " + str(len((r.json() or {}).get("items", []))))
    except Exception:
        lines.append("studio: לא פעיל")
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=10)
        if gpu.returncode == 0 and gpu.stdout.strip():
            lines.append("gpu: " + gpu.stdout.strip())
    except Exception:
        lines.append("gpu: אין")
    return "\n".join(lines)


def cmd_run(cfg, args):
    if not args:
        return "אין פקודה. שימוש: run <פקודה>"
    shell = args[0]
    cmd_args = args[1:]
    try:
        r = subprocess.run([shell] + cmd_args, capture_output=True, text=True, timeout=840, shell=False)
        out = (r.stdout or "")[-3000:]
        err = (r.stderr or "")[-800:]
        return "rc=%s\n%s%s" % (r.returncode, out, ("\n[stderr] " + err) if err.strip() else "")
    except Exception as e:
        return "שגיאת הרצה: " + str(e)[:300]


def cmd_find(cfg, args):
    if len(args) < 2:
        return "שימוש: find <תיקיה> <תבנית>"
    d, pat = args[0], args[1]
    out = []
    for root, dirs, files in os.walk(d):
        for f in files:
            if pat.lower() in f.lower():
                out.append(os.path.join(root, f))
            if len(out) >= 30:
                return "\n".join(out) + "\n(עצרתי ב-30)"
    return "\n".join(out) or "לא נמצא"


def cmd_readfile(cfg, args):
    if not args:
        return "שימוש: readfile <נתיב>"
    try:
        with open(args[0], "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[-4000:]
    except Exception as e:
        return "שגיאה: " + str(e)[:200]


def cmd_render(cfg, args):
    sp = cfg.get("studio_path") or ""
    if not sp or not os.path.isdir(sp):
        return "studio_path לא מוגדר ב-config"
    r = subprocess.run([sys.executable, os.path.join(sp, "app.py")],
                       capture_output=True, text=True, timeout=300)
    return ("rc=" + str(r.returncode) + "\n" + (r.stdout or "")[-2000:])


def cmd_gallery_push(cfg, args):
    repo = cfg.get("gallery_local_repo") or ""
    if not repo or not os.path.isdir(repo):
        return "gallery_local_repo לא מוגדר ב-config"
    r = subprocess.run(["git", "-C", repo, "add", "."], capture_output=True, text=True, timeout=30)
    r2 = subprocess.run(["git", "-C", repo, "commit", "-m", "worker gallery", "--allow-empty"],
                         capture_output=True, text=True, timeout=30)
    r3 = subprocess.run(["git", "-C", repo, "push"], capture_output=True, text=True, timeout=60)
    return "add rc=%s commit rc=%s push rc=%s\n%s" % (r.returncode, r2.returncode, r3.returncode, r3.stdout[-500:])


HANDLERS = {"status": cmd_status, "run": cmd_run, "find": cmd_find,
            "readfile": cmd_readfile, "render": cmd_render, "gallery_push": cmd_gallery_push}


def execute(cfg, task):
    instruction = (task.get("instruction") or "").strip()
    secret = str(cfg.get("cmd_secret") or "")
    if secret:
        if not instruction.startswith(secret + ":"):
            return "denied", "נדחה: הפקודה לא חתומה בסוד המשותף."
        instruction = instruction[len(secret) + 1:].strip()
    parts = instruction.split()
    verb = parts[0].lower() if parts else "status"
    args = parts[1:] if verb in HANDLERS else parts
    handler = HANDLERS.get(verb, cmd_run)
    box = {}

    def work():
        try:
            box["r"] = handler(cfg, args)
        except Exception:
            box["r"] = "ERROR: " + traceback.format_exc()[-1500:]

    try:
        cap = int((args[0].split("=")[1]) if args and args[0].startswith("timeout=") else 900)
    except Exception:
        cap = 900
    cap = min(cap + 60, 14460)
    t = threading.Thread(target=work, daemon=True)
    t.start()
    t.join(cap)
    if t.is_alive():
        return verb, "ERROR: הפקודה נתקעה מעבר ל-%ds — הלולאה ממשיכה, התהליך ננטש" % cap
    return verb, box.get("r", "ERROR: אין תוצאה")


def routing_ok(task):
    code = (task.get("task_code") or "")
    me = platform_tag()
    if code.startswith("win-"):
        return me == "win"
    if code.startswith("mac-"):
        return me == "mac"
    return True


def self_update(cfg):
    try:
        r = urllib.request.urlopen(REMOTE_VERSION_URL, timeout=15)
        remote = r.read().decode().strip()
        if tuple(int(x) for x in remote.split(".")) <= tuple(int(x) for x in VERSION.split(".")):
            return False
        tmp = os.path.join(HERE, "worker.py.new")
        urllib.request.urlretrieve(REMOTE_CODE_URL, tmp)
        if os.path.getsize(tmp) < 5000:
            log("עדכון עצמי: קובץ חשוד קטן — בוטל")
            return False
        import py_compile
        py_compile.compile(tmp, doraise=True)
        me = os.path.abspath(__file__)
        os.replace(tmp, me)
        log("עדכון עצמי ל-v" + remote + " — מריץ גרסה חדשה במקום")
        os.execv(sys.executable, [sys.executable, me])
    except Exception as e:
        log("בדיקת עדכון עצמי נכשלה (לא קריטי): " + str(e)[:150])
    return False


def main():
    cfg = load_config()
    trim_log()
    log("שימי וורקר v" + VERSION + " (GitHub-native) עלה. worker_id=" + str(cfg.get("worker_id")))
    ntfy(cfg, "hb " + str(cfg.get("worker_id")), "v" + VERSION + " up (github-native)")
    last_hb = 0.0
    last_check = 0.0
    while True:
        try:
            if time.time() - last_hb > 300:
                touch_heartbeat(cfg)
                ntfy(cfg, "hb " + str(cfg.get("worker_id")),
                     "v" + VERSION + " up " + str(int((time.time() - START_TS) // 60)) + "m done=" + str(TASKS_DONE[0]))
                last_hb = time.time()
            cfg = load_config()
            if time.time() - last_check > 600:
                last_check = time.time()
                self_update(cfg)
                trim_log()
            tasks = fetch_tasks(cfg)
            for t in tasks:
                tid = t.get("id")
                if not routing_ok(t):
                    continue
                verb, result = execute(cfg, t)
                mark_done(cfg, tid)
                TASKS_DONE[0] += 1
                log("משימה " + str(tid)[:12] + " [" + verb + "] בוצעה: " + str(result)[:150])
                update_task(cfg, tid, {"title": t.get("title"), "result": result})
            time.sleep(cfg.get("poll_seconds", 15))
        except Exception:
            log("חריגה בלולאה (לא מת): " + traceback.format_exc()[-300:])
            time.sleep(20)


if __name__ == "__main__":
    main()
