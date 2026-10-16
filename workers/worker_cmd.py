# -*- coding: utf-8 -*-
"""ShimiWorker v1.2.1 (16/10) — עמידות מלאה: לא מת לעולם.
חידושי v1.2:
- ניתוב פלטפורמות: משימות עם קידומת task_code "win-"/"mac-" רצות רק על המכונה המתאימה.
- אנטי-קריסה: אף חריגה לא מפילה את הלולאה; config חסר לא מסיים תהליך; API שוקל עם backoff.
- טאץ'-אלייב: דופק לשרת כל 60 שניות + קובץ heartbeat מקומי לשומר ה-Windows.
- מלקט תקועים (reaper): בעלייה, משימות in_progress קפואות מעל 3 שעות חוזרות ל-pending.
- עדכון עצמי: כל 10 דקות בודק גרסה ב-aidoor ומחליף את עצמו מבלי למות (execv).
- תלישת יומן: היומן נחתך ל-200KB בעלייה וכל 6 שעות — לא ממלא דיסק.
- טיימאאוט מובנה לכל משימה — לולאה חיה גם אם פקודה נתקעה (thread daemon).
v1.2.1: דופק תואם טוקנים קבועים (PAT) + config חי בכל לולאה (החלפת טוקן בלי אתחול). חתימה: פקודות עם קידומת "<סוד>:" כש-cmd_secret מוגדר.
"""
import sys, os, json, time, subprocess, platform, traceback, threading, glob
import urllib.request
from datetime import datetime, timezone, timedelta

VERSION = "1.2.1"
REMOTE_VERSION_URL = "https://aidoor.shimi.land/worker_version.txt"
REMOTE_CODE_URL = "https://aidoor.shimi.land/worker_latest.py"

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "worker_log.txt")
HB_FILE = os.path.join(HERE, "heartbeat.txt")

DEFAULTS = {
    "base_url": "https://solas-6a095a77.base44.app",
    "token": "",
    "cmd_secret": "",
    "poll_seconds": 10,
    "worker_id": "unknown-worker",
    "studio_path": "",
    "gallery_local_repo": "",
}

TASKS_DONE = [0]
START_TS = time.time()


def platform_tag():
    if os.name == "nt":
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "any"


def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass
    try:
        print(msg, flush=True)
    except Exception:
        pass


def trim_log():
    try:
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 300_000:
            with open(LOG_FILE, "rb") as f:
                f.seek(-200_000, 2)
                tail = f.read()
            with open(LOG_FILE, "wb") as f:
                f.write(tail)
    except Exception:
        pass


def load_config():
    cfg = dict(DEFAULTS)
    try:
        with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
            cfg.update(json.load(f))
    except Exception as e:
        log("config.json חסר/פגום — עובדים עם ברירות מחדל: " + str(e)[:120])
    return cfg


def api(cfg, method, path, params=None, payload=None, retries=3):
    import requests
    url = cfg["base_url"].rstrip("/") + path
    last = None
    for attempt in range(retries):
        try:
            r = requests.request(method, url, headers={
                "Authorization": "Bearer " + cfg["token"],
                "User-Agent": "Mozilla/5.0",
            }, params=params, json=payload, timeout=30)
            if r.status_code in (200, 201):
                return r.json()
            if r.status_code in (401, 403):
                log(f"API {r.status_code} ב{path} — טוקן/הרשאה (נמשיך לנסות)")
                time.sleep(30)
                return None
            last = f"HTTP {r.status_code}"
        except Exception as e:
            last = str(e)[:120]
        time.sleep(2 * (attempt + 1))
    log(f"API נכשל אחרי {retries} ניסיונות ({path}): {last}")
    return None


def touch_heartbeat(cfg):
    try:
        with open(HB_FILE, "w") as f:
            f.write(datetime.now(timezone.utc).isoformat())
    except Exception:
        pass
    value = f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} | v{VERSION} | {platform_tag()} | done={TASKS_DONE[0]}'
    key = f"worker_heartbeat_{cfg['worker_id']}"
    recs = api(cfg, "GET", "/api/entities/SystemSettings", params={"key": key, "limit": "1"})
    if isinstance(recs, list) and recs:
        api(cfg, "PUT", f"/api/entities/SystemSettings/{recs[0]['id']}", payload={"value": value})
    else:
        api(cfg, "POST", "/api/entities/SystemSettings", payload={"key": key, "value": value})


def fetch_tasks(cfg):
    d = api(cfg, "GET", "/api/entities/IncomingTask",
            params={"source": cfg.get("source", "windows-commands"), "status": "pending", "limit": "20"})
    return d if isinstance(d, list) else []


def update_task(cfg, task_id, data):
    for i in range(3):
        if api(cfg, "PUT", f"/api/entities/IncomingTask/{task_id}", payload=data) is not None:
            return True
        time.sleep(3)
    log(f"כתיבת תוצאה למשימה {task_id} נכשלה סופית — תישאר למלקט")
    return False


def cmd_status(cfg, args):
    info = {
        "worker_id": cfg.get("worker_id"), "version": VERSION,
        "platform_tag": platform_tag(),
        "hostname": platform.node(), "os": platform.platform(),
        "python": sys.version.split()[0],
        "uptime_minutes": round((time.time() - START_TS) / 60, 1),
        "tasks_done": TASKS_DONE[0],
        "time": datetime.now().isoformat(timespec="seconds"),
    }
    if platform.system() == "Darwin":
        try:
            chip = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                                   capture_output=True, text=True, timeout=10).stdout.strip()
            try:
                m = subprocess.run(["system_profiler", "SPDisplaysDataType"],
                                    capture_output=True, text=True, timeout=15).stdout
                import re as _re
                mm = _re.search(r"Chipset Model:\s*(.+)", m)
                if mm:
                    chip = mm.group(1).strip() + " | " + chip
            except Exception:
                pass
            info["gpu"] = chip
        except Exception:
            info["gpu"] = "Apple Silicon"
    else:
        try:
            gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                                  "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
            info["gpu"] = gpu.stdout.strip()
        except Exception:
            info["gpu"] = "לא זוהה כרטיס NVIDIA / nvidia-smi לא זמין"
    try:
        import shutil
        du = shutil.disk_usage(HERE if os.name == "nt" else os.path.expanduser("~"))
        info["disk_free_gb"] = round(du.free / 1e9, 1)
    except Exception:
        pass
    return json.dumps(info, ensure_ascii=False, indent=1)


def cmd_run(cfg, args):
    timeout = 600
    if args and args[0].startswith("timeout="):
        try:
            timeout = min(int(args[0].split("=")[1]), 14400)
        except Exception:
            pass
        args = args[1:]
    if not args:
        return "ERROR: חסרה פקודה"
    command = " ".join(args)
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True,
                            timeout=timeout, encoding="utf-8", errors="replace")
        out = (r.stdout or "")[-4000:] + ("\n[stderr]\n" + (r.stderr or "")[-2000:] if r.stderr else "")
        return (f"exit={r.returncode}\n" + out) or "exit=0 (ללא פלט)"
    except subprocess.TimeoutExpired:
        return f"ERROR: timeout — הפקודה לא הסתיימה בתוך {timeout}s"


def cmd_find(cfg, args):
    if len(args) < 2:
        return "ERROR: שימוש: find <pattern> <dir>"
    pattern, root = args[0], " ".join(args[1:])
    hits = []
    try:
        if os.path.isfile(root):
            for line in open(root, encoding="utf-8", errors="replace"):
                if pattern.lower() in line.lower():
                    hits.append(line.rstrip()[:200])
                if len(hits) >= 50:
                    break
        else:
            for dirpath, dirs, files in os.walk(root, topdown=True):
                dirs[:] = [d for d in dirs if d not in
                           ("AppData", "Library", "node_modules", "__pycache__", ".git", "venv")]
                for name in files:
                    if glob.fnmatch.fnmatch(name.lower(), pattern.lower()):
                        hits.append(os.path.join(dirpath, name))
                        if len(hits) >= 200:
                            break
                if len(hits) >= 200:
                    break
    except Exception as e:
        return "ERROR: " + str(e)[:200]
    return "\n".join(hits) if hits else "לא נמצאו התאמות"


def cmd_readfile(cfg, args):
    if not args:
        return "ERROR: חסר נתיב"
    path, limit = " ".join(args), 4000
    if args and args[-1].isdigit():
        limit = int(args[-1]); path = " ".join(args[:-1])
    try:
        content = open(path, encoding="utf-8", errors="replace").read(limit)
        secret = str(cfg.get("token") or "")
        if secret:
            content = content.replace(secret, "[TOKEN מוסתר]")
        return content or "(קובץ ריק)"
    except Exception as e:
        return "ERROR: " + str(e)[:200]


def cmd_render(cfg, args):
    studio = cfg.get("studio_path") or ""
    script = os.path.join(studio, "studio", "render_one.py")
    if not os.path.isfile(script):
        return "ERROR: חסר render_one — הגדר studio_path ב-config או התקן סטודיו"
    try:
        spec = json.loads(" ".join(args))
    except Exception as e:
        return "ERROR: spec לא תקין: " + str(e)[:150]
    spec.setdefault("out_dir", os.path.join(studio, "renders"))
    try:
        r = subprocess.run([sys.executable, script], cwd=studio,
                            input=json.dumps(spec), capture_output=True, text=True,
                            timeout=1800, encoding="utf-8", errors="replace")
        return (r.stdout or "")[-3000:] + ("\n[stderr]\n" + (r.stderr or "")[-1500:] if r.stderr else "")
    except subprocess.TimeoutExpired:
        return "ERROR: render לא הסתיים ב-30 דקות"


def cmd_gallery_push(cfg, args):
    repo = cfg.get("gallery_local_repo") or ""
    if not repo or not os.path.isdir(repo):
        return "ERROR: gallery_local_repo לא מוגדר ב-config"
    if len(args) < 2:
        return "ERROR: שימוש: gallery_push <file> <target-relative-path>"
    src, rel = args[0], " ".join(args[1:])
    dst = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    import shutil
    shutil.copy(src, dst)
    r = subprocess.run(f'git -C "{repo}" add . && git -C "{repo}" commit -m "gallery: {os.path.basename(src)}" '
                       f'&& git -C "{repo}" pull --rebase -q && git -C "{repo}" push -q',
                       shell=True, capture_output=True, text=True, timeout=300)
    return f"exit={r.returncode}\n{ (r.stdout or '') + (r.stderr or '') }[-1500:]"


HANDLERS = {
    "status": cmd_status,
    "run": cmd_run,
    "find": cmd_find,
    "readfile": cmd_readfile,
    "render": cmd_render,
    "gallery_push": cmd_gallery_push,
}


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
        return verb, f"ERROR: הפקודה נתקעה מעבר ל-{cap}s — הלולאה ממשיכה, התהליך ננטש"
    return verb, box.get("r", "ERROR: אין תוצאה")


def routing_ok(task):
    """ניתוב פלטפורמות: win-*/mac-* רק למכונה שלהן; ניטרלי — לכולם."""
    code = (task.get("task_code") or "")
    me = platform_tag()
    if code.startswith("win-"):
        return me == "win"
    if code.startswith("mac-"):
        return me == "mac"
    return True


def reap_stuck(cfg):
    """בעלייה: משימות in_progress קפואות מעל 3 שעות חוזרות ל-pending."""
    try:
        d = api(cfg, "GET", "/api/entities/IncomingTask",
                params={"source": cfg.get("source", "windows-commands"), "status": "in_progress", "limit": "20"})
        if not isinstance(d, list):
            return
        cutoff = datetime.now(timezone.utc) - timedelta(hours=3)
        for t in d:
            try:
                upd = datetime.fromisoformat((t.get("updated_date") or "").replace("Z", "+00:00"))
                if upd < cutoff:
                    update_task(cfg, t["id"], {"status": "pending"})
                    log(f"מלקט: משימה תקועה {t.get('id','')[:8]} הוחזרה ל-pending")
            except Exception:
                pass
    except Exception:
        pass


def self_update(cfg):
    """עדכון עצמי: בודק גרסה מרחוק ומחליף את הקוד בלי למות."""
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
        log(f"עדכון עצמי ל-v{remote} — מריץ גרסה חדשה במקום")
        os.execv(sys.executable, [sys.executable, me])
    except Exception as e:
        log("בדיקת עדכון עצמי נכשלה (לא קריטי): " + str(e)[:150])
    return False


def main():
    cfg = load_config()
    trim_log()
    log(f"שימי וורקר v{VERSION} עלה. worker_id={cfg['worker_id']} platform={platform_tag()}")
    if not cfg["token"]:
        log("אין טוקן ב-config — ממתין שהטוקן יוכנס (לא מתים לעולם)...")
        while not cfg["token"]:
            time.sleep(30)
            cfg = load_config()
    reap_stuck(cfg)
    last_hb = 0.0
    last_check = 0.0
    fails = 0
    while True:
        try:
            if time.time() - last_hb > 60:
                touch_heartbeat(cfg)
                last_hb = time.time()
            cfg = load_config()
            if time.time() - last_check > 600:
                last_check = time.time()
                self_update(cfg)
                trim_log()
            tasks = fetch_tasks(cfg)
            fails = 0
            for t in tasks:
                tid = t.get("id")
                if not routing_ok(t):
                    continue
                fresh = api(cfg, "GET", f"/api/entities/IncomingTask/{tid}")
                if not fresh or fresh.get("status") != "pending":
                    continue
                if not update_task(cfg, tid, {"status": "in_progress"}):
                    continue
                log(f"פקודה התקבלה [{str(tid)[:8]}]: {(t.get('instruction') or '')[:110]}")
                try:
                    verb, result = execute(cfg, t)
                except Exception:
                    result = "ERROR: " + traceback.format_exc()[-2000:]
                    verb = "error"
                update_task(cfg, tid, {
                    "status": "done", "processed": True,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "task_code": t.get("task_code") or verb,
                    "title": ((t.get("title") or "פקודה") + " | בוצע " + datetime.now().strftime("%H:%M")),
                    "instruction": (t.get("instruction") or "") + "\n─── RESULT ───\n" + str(result)[:7000],
                })
                TASKS_DONE[0] += 1
                log(f"פקודה [{str(tid)[:8]}] הושלמה ({verb})")
        except Exception as e:
            fails += 1
            wait = min(15 * fails, 120)
            log(f"שגיאת לולאה (כישלון {fails}, המתנה {wait}s): " + str(e)[:250])
            time.sleep(wait)
            if fails % 50 == 0:
                log("עדיין בחיים ומנסה — הוורקר לא מת.")
        time.sleep(max(3, int(cfg.get("poll_seconds", 10))))


if __name__ == "__main__":
    main()
