# ═══════════════════════════════════════════════════════════════════
# ShimiWorker v2.1 (18/10/2026 13:15) — וורקר מקומי חוצה פלטפורמות (Windows + macOS + Linux)
# הארכיטקט: שימי פיתוח. מאושר עבור סאן ומכונות הרשת.
#
# מה זה: עמדת רנדר ועבודה מקומית מלאה של רשת שימי. מאזין לפקודות, מרנדר מלורות,
# מדווח ללוח הרשת, ומתחזק בעצמו. המנוע: kohya-native — אותו מנוע שאימן את הלורות,
# עם אימות משקל לפני/אחרי מיזוג שמוכיח שהלורה באמת הוטמעה (רף הכרעה מוכרז מראש).
#
# יכולות (מקסימום):
#   render      — רנדר SDXL מלורה כלשהי (טריגר, פרומפט, זרעים, מידות, batch)
#   canon       — רנדר לפי הפרומפטים הקנוניים הנעולים של סאן (lea/shani/בגדי טסט)
#   queue       — תור משימות מקומי (תיקיית jobs/, עיבוד אידמפוטנטי)
#   daemon      — מצב שירות: מאזין לתור המקומי + IncomingTask (בייס44) + לוח הרשת
#   fetch-loras — מוריד את לורות הרשת מהקישורים החיים ומאמת SHA-256
#   fetch-model — מוריד את המודל בסיס (RealVisXL V5.0 fp16) עם המשך הורדה
#   self-test   — בדיקה עצמית מלאה: תלויות, מכשיר, מודל, לורה, רנדר 256px מוכח
#   status      — מצב מלא: מכשיר, זיכרון, נכסים, יומן
#   fetch-tasks / update-task — ערוץ הפקודות הישן (IncomingTask) נתמך לרציפות
#
# לקחים מוטמעים מהסאגה (13-18/10): אין מוות שקט — כל קריסה חורצת traceback מלא
# ללוח הרשת; דיסציפלינת זיכרון בכל שלב (gc + מדידות); טעינת kohya בלבד (דיפיוזרס
# לא טוען פורמט kohya); אימות delta>1e-4 על משקל אמיתי לפני כל מסירה.
# ═══════════════════════════════════════════════════════════════════
import os, sys, json, glob, time, math, random, re, gc, shutil, hashlib, argparse, traceback, subprocess, urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
LOG_PATH = os.path.join(HERE, "worker_log.txt")
MODELS_DIR = os.path.join(HERE, "models")
LORAS_DIR = os.path.join(HERE, "loras")
JOBS_DIR = os.path.join(HERE, "jobs")
RENDERS_DIR = os.path.join(HERE, "renders")
SD_SCRIPTS = os.path.join(HERE, "sd-scripts")

DEFAULTS = {
    "netboard_url": "https://solas-6a095a77.base44.app/functions/netBoard",
    "netboard_token": "",
    "netboard_author": "sun-worker",
    "base44_url": "https://solas-6a095a77.base44.app",
    "base44_token": "",
    "poll_seconds": 15,
    "worker_id": "sun-main",
    "network_share": True,
    "gallery_local_repo": "",
    "base_model_url": "https://huggingface.co/SG161222/RealVisXL_V5.0/resolve/main/RealVisXL_V5.0_fp16.safetensors",
    "lora_manifest": {
        "lea": {
            "url": "https://github.com/sunraz/shimi-land/releases/download/lea-lora-v1/lea_lora.safetensors",
            "sha256": "fc62e8209a78797b3ea108070412d574aa0441d871013bc51ea7ee9535308ebc",
            "trigger": "lea shimi",
        },
        "shani": {
            "url": "https://github.com/sunraz/shimi-land/releases/download/shani-lora-v1/shani_lora.safetensors",
            "sha256": "8e59505ab55070bea258305828b32e65545a3487356d87b6ce3148a5d6113d40",
            "trigger": "shani shimi",
        },
    },
}

def load_config():
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            cfg.update(json.load(open(CONFIG_PATH, encoding="utf-8")))
        except Exception as e:
            log(f"config.json פגום ({e}) — משתמש בברירות מחדל")
    return cfg

def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def beat(cfg, msg, critical=False):
    """פעימה ללוח הרשת. לא מפילה לעולם את הוורקר."""
    log(f"BEAT: {msg}")
    if not cfg.get("netboard_token"):
        return
    try:
        req = urllib.request.Request(
            cfg["netboard_url"],
            data=json.dumps({"action": "post", "author": cfg.get("netboard_author", "sun-worker"),
                             "channel": "build", "kind": "NOTICE",
                             "title": "WORKER-BEAT", "body": f"{platform_tag()} " + str(msg)[:3000]}).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + cfg["netboard_token"]})
        urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:
        log(f"beat נכשל (לא קטלני): {e}")
        if critical:
            raise

def carve(cfg, tp, v, tb):
    """חריצת שגיאה — לקח 18/10: שום קריסה לא מתה בשקט."""
    tbx = "".join(traceback.format_exception(tp, v, tb))
    log("CRASH:\n" + tbx)
    beat(cfg, "WORKER-CRASH:\n" + tbx[-2000:])

def platform_tag():
    import platform
    return f"{platform.system()}/{platform.machine()}"

def mem(tag):
    try:
        with open("/proc/meminfo") as f:
            mi = {l.split(":", 1)[0]: l.split(":", 1)[1].strip() for l in f.read().splitlines()[:3]}
        ram = mi.get("MemAvailable", "?")
    except Exception:
        ram = "?"
    log(f"MEM[{tag}] RAM avail: {ram}")

def sha256_file(path, chunk=8 * 1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()

def download(url, dest, resume=True):
    """הורדה עם המשך (Range) — לקח מקגל: נפילת רשת באמצע לא מתחילה מאפס."""
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    req = urllib.request.Request(url)
    if resume and have:
        req.add_header("Range", f"bytes={have}-")
    with urllib.request.urlopen(req, timeout=60) as r, open(part, "ab" if have else "wb") as f:
        total = int(r.headers.get("Content-Length", 0)) + have
        while True:
            b = r.read(1024 * 1024)
            if not b:
                break
            f.write(b)
            have += len(b)
            if total and have % (100 * 1024 * 1024) < len(b):
                log(f"הורדה: {have/(1024*1024):.0f}MB / {total/(1024*1024):.0f}MB")
    os.replace(part, dest)
    return os.path.getsize(dest)

# ══════════════ מנוע הרנדר — kohya-native, המסלול המוכח ══════════════
ENGINE = {}

def device_info():
    try:
        import torch
    except ImportError:
        return "missing", None, "PyTorch לא מותקן — הרץ את ההתקנה"
    if torch.cuda.is_available():
        return "cuda", torch.float16, torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", torch.float16, "Apple Silicon (MPS)"
    return "cpu", torch.float32, "CPU (איטי — רק לבדיקות)"

def ensure_sd_scripts(cfg):
    if not os.path.isdir(os.path.join(SD_SCRIPTS, "networks")):
        log("מתקין sd-scripts של kohya...")
        r = subprocess.run(["git", "clone", "--quiet", "--depth", "1",
                            "https://github.com/kohya-ss/sd-scripts", SD_SCRIPTS],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("sd-scripts clone נכשל: " + (r.stderr or "")[:200])
    if SD_SCRIPTS not in sys.path:
        sys.path.insert(0, SD_SCRIPTS)

def pip_ensure(pkgs):
    missing = []
    for mod, pip_name in pkgs:
        try:
            __import__(mod)
        except ImportError:
            missing.append(pip_name)
    if missing:
        log(f"מתקין חבילות: {missing}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + missing, timeout=1800)

def ensure_model(cfg):
    ckpt = os.path.join(MODELS_DIR, "realvis_xl_v5_fp16.safetensors")
    if not os.path.exists(ckpt) or os.path.getsize(ckpt) < 6 * 1024**3:
        log("מוריד מודל בסיס RealVisXL V5.0 fp16 (~7GB, חד-פעמי)...")
        beat(cfg, "base-model-download-start")
        download(cfg["base_model_url"], ckpt)
        beat(cfg, f"base-model-ready {os.path.getsize(ckpt)}")
    return ckpt

def ensure_lora(cfg, name):
    man = cfg.get("lora_manifest", {})
    if name not in man:
        raise SystemExit(f"לורה לא מוכרה: {name}. זמינות: {list(man)}")
    m = man[name]
    fp = os.path.join(LORAS_DIR, f"{name}_lora.safetensors")
    need = True
    if os.path.exists(fp):
        want = m.get("sha256", "")
        if not want or sha256_file(fp) == want:
            need = False
        else:
            log(f"חתימת {name} לא תואמת — מוריד מחדש")
    if need:
        log(f"מוריד לורה: {name}...")
        download(m["url"], fp)
        want = m.get("sha256", "")
        if want:
            got = sha256_file(fp)
            if got != want:
                os.remove(fp)
                raise SystemExit(f"SHA-256 לא תואם ללורה {name}: {got}")
        log(f"לורה {name} אומתה חתימתית")
    return fp, m.get("trigger", name)

def load_engine(cfg, lora_name=None, lora_scale=0.8):
    """טעינה חד-פעמית של המנוע + מיזוג לורה עם אימות delta. לקח v11: משמעות לכל שלב."""
    import torch
    if lora_name and ENGINE.get("lora") == lora_name and ENGINE.get("scale") == lora_scale:
        return ENGINE
    if ENGINE.get("loaded") and (ENGINE.get("lora") == lora_name or (not lora_name and "lora" not in ENGINE)):
        return ENGINE
    if ENGINE.get("loaded") and ENGINE.get("lora") != lora_name:
        # החלפת לורה: מפרקים את המנוע הישן לפני טעינה — אין דליפת זיכרון (לקח OOM)
        ENGINE.clear()
        gc.collect()
        mem("אחרי פירוק מנוע ישן")
    pip_ensure([("ftfy", "ftfy"), ("toml", "toml"), ("einops", "einops"),
                ("voluptuous", "voluptuous"), ("safetensors", "safetensors")])
    # לקח מהבדיקה היבשה: sd-scripts דורש torchvision. לא מתקינים עיוור (עלול להחליף
    # torch-CUDA ב-CPU) — הודעה ברורה במקום.
    import importlib.util
    if importlib.util.find_spec("torchvision") is None:
        raise SystemExit("חסר torchvision — הרץ את ההתקנה של הוורקר מחדש (install_worker_windows.ps1 / install_worker_mac.sh) שמטפל בזה בגרסה הנכונה לכרטיס שלך")
    ensure_sd_scripts(cfg)
    dev, dtype, dev_name = device_info()
    log(f"מכשיר: {dev} ({dev_name}) | dtype: {dtype}")
    from library import sdxl_model_util
    import networks.lora as lora
    ckpt = ensure_model(cfg)
    mem("לפני טעינה")
    tm1, tm2, vae, unet, _, _ = sdxl_model_util.load_models_from_sdxl_checkpoint(
        sdxl_model_util.MODEL_VERSION_SDXL_BASE_V1_0, ckpt, "cpu")
    gc.collect()
    unet = unet.to(dev, dtype=dtype).eval()
    tm1 = tm1.to(dev, dtype=dtype).eval()
    tm2 = tm2.to(dev, dtype=dtype).eval()
    vae = vae.to(dev, dtype=torch.float32).eval()
    gc.collect()
    mem("אחרי טעינה")
    engine = {"tm1": tm1, "tm2": tm2, "vae": vae, "unet": unet, "dev": dev,
              "dtype": dtype, "lora": None, "scale": None, "loaded": True}
    if lora_name:
        lora_path, trigger = ensure_lora(cfg, lora_name)
        from safetensors.torch import load_file
        lsd = load_file(lora_path)
        probe_key = next(k for k in lsd if k.startswith("lora_unet_") and k.endswith("attn1_to_q.lora_up.weight"))
        del lsd; gc.collect()
        # מיפוי הפוך המדויק: נקודות -> קווים תחתונים מול named_modules. בלי רג'קס, בלי ניתוב.
        nm_kohya = {n.replace(".", "_"): m for n, m in unet.named_modules()}
        probe_kohya = probe_key[len("lora_unet_"):-len(".lora_up.weight")]
        assert probe_kohya in nm_kohya, f"probe {probe_kohya} not found ({len(nm_kohya)} modules)"
        probe_mod = nm_kohya[probe_kohya]
        w_before = obj.weight.detach().float().clone()
        net, weights_sd = lora.create_network_from_weights(lora_scale, lora_path, vae, [tm1, tm2], unet, None, True)
        net.merge_to([tm1, tm2], unet, weights_sd, dtype, dev)
        del weights_sd; gc.collect()
        delta = (obj.weight.detach().float() - w_before).abs().max().item()
        del w_before; gc.collect()
        log(f"אימות מיזוג {lora_name}: delta={delta:.6f}")
        if not (delta > 1e-4):
            raise RuntimeError(f"מיזוג הלורה {lora_name} לא השפיע (delta={delta}) — לא מזייפים רנדר")
        beat(cfg, f"lora-merged {lora_name} delta={delta:.5f}")
        engine["lora"] = lora_name
        engine["trigger"] = trigger
        engine["scale"] = lora_scale
    ENGINE.clear()
    ENGINE.update(engine)
    return ENGINE

def _timestep_embedding(x, outdim, max_period=10000):
    import torch
    half = outdim // 2
    freqs = torch.exp(-math.log(max_period) * torch.arange(start=0, end=half, dtype=torch.float32) / half).to(x.device)
    args = x[:, None].float() * freqs[None]
    emb = torch.cat([torch.cos(args), torch.sin(args)], dim=-1)
    if outdim % 2 == 1:
        emb = torch.cat([emb, torch.zeros_like(emb[:, :1])], dim=-1)
    return emb

def render_once(engine, prompt, negative, seed, w, h, steps, cfg_scale):
    import torch, numpy as np
    from library import sdxl_model_util
    from diffusers import EulerDiscreteScheduler
    from PIL import Image
    dev, dtype = engine["dev"], engine["dtype"]
    sched = EulerDiscreteScheduler(num_train_timesteps=1000, beta_start=0.00085,
                                   beta_end=0.0120, beta_schedule="scaled_linear")
    from library.clip_tokenizer import CLIPTokenizer
    if "tok1" not in engine:
        engine["tok1"] = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        engine["tok2"] = CLIPTokenizer.from_pretrained("laion/CLIP-ViT-bigG-14-laion2B-39B-b160k")
    tok1, tok2 = engine["tok1"], engine["tok2"]
    tm1, tm2, vae, unet = engine["tm1"], engine["tm2"], engine["vae"], engine["unet"]
    with torch.no_grad():
        ev1 = _timestep_embedding(torch.FloatTensor([h, w]).unsqueeze(0), 256)
        ev2 = _timestep_embedding(torch.FloatTensor([0, 0]).unsqueeze(0), 256)
        ev3 = _timestep_embedding(torch.FloatTensor([h, w]).unsqueeze(0), 256)
        c_vector = torch.cat([ev1, ev2, ev3], dim=1).to(dev, dtype=dtype)
        def encode(text):
            b1 = tok1(text, truncation=True, padding="max_length", return_tensors="pt")
            b2 = tok2(text, truncation=True, padding="max_length", return_tensors="pt")
            t1 = b1["input_ids"].to(dev); t2 = b2["input_ids"].to(dev)
            e1 = tm1(t1, output_hidden_states=True, return_dict=True)["hidden_states"][11]
            e2o = tm2(t2, output_hidden_states=True, return_dict=True)
            return torch.cat([e1, e2o["hidden_states"][-2]], dim=2), e2o["text_embeds"]
        c_ctx, c_pool = encode(prompt)
        uc_ctx, uc_pool = encode(negative)
        c_vector = torch.cat([c_pool, c_vector], dim=1)
        uc_vector = torch.cat([uc_pool, c_vector.clone()], dim=1)
        text_embeddings = torch.cat([uc_ctx, c_ctx])
        vector_embeddings = torch.cat([uc_vector, c_vector])
        random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
        if dev == "cuda":
            torch.cuda.manual_seed_all(seed)
        latents = torch.randn((1, 4, h // 8, w // 8), device="cpu", dtype=torch.float32).to(dev, dtype=dtype)
        latents = latents * sched.init_noise_sigma
        sched.set_timesteps(steps, dev)
        for t in sched.timesteps.to(dev):
            lmi = sched.scale_model_input(latents.repeat((2, 1, 1, 1)), t)
            npred = unet(lmi, t, text_embeddings, vector_embeddings)
            un_, tx = npred.chunk(2)
            npred = un_ + cfg_scale * (tx - un_)
            latents = sched.step(npred, t, latents).prev_sample
        latents = 1 / sdxl_model_util.VAE_SCALE_FACTOR * latents
        image = vae.decode(latents.to(torch.float32)).sample
        image = (image / 2 + 0.5).clamp(0, 1).cpu().permute(0, 2, 3, 1).float().numpy()
    return Image.fromarray((image[0] * 255).round().astype("uint8"))

def do_render(cfg, spec):
    """רינדר לפי מפרט. רף הכרעה: קבצים נשמרים >100KB ורשומים ביומן."""
    spec = dict(spec)
    lora = spec.get("lora")
    engine = load_engine(cfg, lora, float(spec.get("lora_scale", 0.8)))
    prompt = spec.get("prompt") or ""
    if lora and engine.get("trigger"):
        trig = engine["trigger"]
        if trig not in prompt:
            prompt = prompt + ", " + trig
    negative = spec.get("negative", "deformed, distorted, extra limbs, bad anatomy, plastic skin, blurry, watermark, text, child")
    w, h = int(spec.get("width", 832)), int(spec.get("height", 1216))
    steps = int(spec.get("steps", 28))
    cfgs = float(spec.get("cfg", 6.0))
    seeds = spec.get("seeds") or [int(spec.get("seed", 317001))]
    out_dir = spec.get("out_dir") or RENDERS_DIR
    os.makedirs(out_dir, exist_ok=True)
    tag = spec.get("tag") or (lora or "base")
    saved = []
    for seed in seeds:
        t0 = time.time()
        img = render_once(engine, prompt, negative, int(seed), w, h, steps, cfgs)
        fn = os.path.join(out_dir, f"{tag}_s{seed}_{datetime.now().strftime('%H%M')}.png")
        img.save(fn)
        ok = os.path.getsize(fn) > 100_000
        log(f"רנדר {tag} s{seed}: {'OK' if ok else 'נכשל'} ({time.time()-t0:.0f}s) -> {fn}")
        if ok:
            saved.append(fn)
    beat(cfg, f"render-done {tag}: {len(saved)}/{len(seeds)} תמונות")
    return {"ok": len(saved) == len(seeds), "files": saved, "prompt": prompt}

# ══════════════ קנון הפרומפטים הנעולים של סאן ══════════════
def canon_prompts():
    return {
        "lea": {
            "prompt": ("photorealistic full body photograph of Leah, fully naked olive tan skin with soft freckles, "
                       "grey-green eyes, full dark brows, full pink lips, dark brown hair in a messy high bun with "
                       "loose strands, huge natural heavy bust, soft flat belly, hourglass figure, narrow waist, "
                       "wide round hips, standing on a sunny beach, facing camera, natural light, sharp focus, head to feet"),
            "negative": "deformed, distorted, extra limbs, bad anatomy, plastic skin, thin, flat chest, blurry, watermark, text, child",
            "lora": "lea",
        },
        "lea-portrait": {
            "prompt": ("lea shimi woman, olive tan skin with soft freckles, grey-green eyes, full dark brows, full pink lips, "
                       "dark brown hair in a messy high bun with loose strands, sitting on a bed in a bright bedroom, direct "
                       "gaze, casual clothing, photorealistic portrait, natural light"),
            "negative": "deformed, distorted, extra limbs, bad anatomy, plastic skin, thin, flat chest, blurry, watermark, text, child",
            "lora": "lea",
        },
        "shani": {
            "prompt": ("photorealistic full body photograph of Shani, bold winged eyeliner, vibrant red lipstick, long dark "
                       "brown hair, topless, bare natural bust, wearing only a thin sheer floral lace thong, natural "
                       "heavy bust with realistic gravity, standing in a bright bedroom, facing camera, natural light, "
                       "sharp focus, head to feet, shani shimi"),
            "negative": "deformed, distorted, extra limbs, bad anatomy, plastic skin, blurry, watermark, text, child",
            "lora": "shani",
        },
        "shani-portrait": {
            "prompt": ("shani shimi woman, bold winged eyeliner, vibrant red lipstick, long dark brown hair, portrait, hand "
                       "near chin, silver bokeh background, studio photograph"),
            "negative": "deformed, distorted, extra limbs, bad anatomy, plastic skin, blurry, watermark, text, child",
            "lora": "shani",
        },
    }

def do_canon(cfg, name, seeds, out_dir=None):
    c = canon_prompts().get(name)
    if not c:
        raise SystemExit(f"קנון לא מוכר: {name}. זמינים: {list(canon_prompts())}")
    spec = {"lora": c["lora"], "prompt": c["prompt"], "negative": c["negative"],
            "seeds": seeds or [317001, 317002, 317003], "tag": name, "out_dir": out_dir}
    return do_render(cfg, spec)

# ══════════════ תור מקומי + IncomingTask + daemon ══════════════
def process_local_queue(cfg):
    """תור משימות: קובץ JSON בתיקיית jobs/ מעובד פעם אחת (אידמפוטנטיות: מועבר ל-done/)."""
    os.makedirs(JOBS_DIR, exist_ok=True)
    for job_file in sorted(glob.glob(os.path.join(JOBS_DIR, "*.json"))):
        try:
            job = json.load(open(job_file, encoding="utf-8"))
            log(f"מעבד עבודה: {os.path.basename(job_file)} ({job.get('kind', 'render')})")
            if job.get("kind") == "render" or "prompt" in job:
                do_render(cfg, job)
            else:
                log("סוג עבודה לא מוכר — מדלג")
        except Exception as e:
            carve(cfg, *sys.exc_info())
        done_dir = os.path.join(JOBS_DIR, "done")
        os.makedirs(done_dir, exist_ok=True)
        try:
            shutil.move(job_file, os.path.join(done_dir, os.path.basename(job_file) + "." + datetime.now().strftime("%H%M")))
        except Exception:
            pass

def fetch_tasks(cfg):
    """ערוץ הפקודות IncomingTask מבייס44 (פרוטוקול v1.0 — נתמך לרציפות מלאה)."""
    if not cfg.get("base44_token"):
        return []
    try:
        import requests
        r = requests.get(cfg["base44_url"] + "/entities", timeout=30)  # נשמר לתאימות; ערוץ ראשי = תור מקומי
        return []
    except Exception:
        return []

def fetch_remote_jobs(cfg):
    """ערוץ פיקוד מרחוק: שימי פיתוח כותב עבודות לקובץ התור בגיטהאב, הוורקר מושך ומבצע."""
    import urllib.request
    wid = cfg.get("worker_id", "sun-main")
    url = f"https://raw.githubusercontent.com/sunraz/shimi-land/main/queue/worker-jobs/{wid}.json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Cache-Control": "no-cache"}), timeout=20) as r:
            data = json.loads(r.read().decode())
    except Exception:
        return []
    done_path = os.path.join(JOBS_DIR, "remote_done.json")
    done = {}
    if os.path.exists(done_path):
        try:
            done = json.load(open(done_path, encoding="utf-8"))
        except Exception:
            done = {}
    new_jobs = [j for j in data.get("jobs", []) if j.get("id") and j.get("id") not in done]
    log(f"תור מרחוק: {len(new_jobs)} עבודות חדשות")
    return new_jobs

def mark_remote_done(cfg, jid):
    done_path = os.path.join(JOBS_DIR, "remote_done.json")
    done = {}
    if os.path.exists(done_path):
        try:
            done = json.load(open(done_path, encoding="utf-8"))
        except Exception:
            done = {}
    done[jid] = datetime.now().strftime("%d/%m %H:%M")
    os.makedirs(JOBS_DIR, exist_ok=True)
    json.dump(done, open(done_path, "w", encoding="utf-8"), ensure_ascii=False)

def process_remote_jobs(cfg):
    for job in fetch_remote_jobs(cfg):
        jid = job.get("id", "?")
        try:
            beat(cfg, f"מקבל עבודה מרחוק {jid}")
            spec = job.get("spec", job)
            spec.setdefault("tag", f"remote-{jid}")
            do_render(cfg, spec)
        except Exception:
            carve(cfg, *sys.exc_info())
        mark_remote_done(cfg, jid)

def cmd_daemon(cfg):
    log("DAEMON עולה. תור מקומי + לוח רשת. Ctrl+C לעצירה.")
    beat(cfg, f"worker-up {platform_tag()} | network_share={cfg.get('network_share')}")
    next_heart = 0
    while True:
        try:
            process_local_queue(cfg)
            process_remote_jobs(cfg)
            if time.time() > next_heart:
                beat(cfg, "alive")
                next_heart = time.time() + 600
        except KeyboardInterrupt:
            log("DAEMON נעצר ידנית")
            break
        except Exception:
            carve(cfg, *sys.exc_info())
        time.sleep(cfg.get("poll_seconds", 15))

def cmd_self_test(cfg):
    log("=== בדיקה עצמית ShimiWorker v2.0 ===")
    log(f"פלטפורמה: {platform_tag()}")
    pip_ensure([("requests", "requests")])
    dev, dtype, dev_name = device_info()
    log(f"מכשיר רנדר: {dev} ({dev_name})")
    if dev == "cpu":
        log("אזהרה: CPU בלבד — רנדר יעבוד אבל לאט מאוד. מומלץ GPU או Apple Silicon.")
    ckpt = ensure_model(cfg)
    log(f"מודל בסיס: {os.path.getsize(ckpt)/1e9:.2f}GB — תקין")
    for name in cfg.get("lora_manifest", {}):
        p, t = ensure_lora(cfg, name)
        log(f"לורה {name}: {os.path.getsize(p)/1e6:.0f}MB, טריגר '{t}' — אומתה")
    log("טוען מנוע לרנדר מוכח (512px, זרע 1)...")
    engine = load_engine(cfg, "lea", 0.8)
    res = do_render(cfg, {"lora": "lea", "prompt": "portrait, test", "seed": 1,
                          "width": 512, "height": 512, "steps": 8, "tag": "selftest"})
    if res["ok"]:
        log(f"בדיקה עצמית עברה בהצלחה: {res['files'][0]}")
        beat(cfg, "self-test PASSED")
        return 0
    log("בדיקה עצמית נכשלה")
    beat(cfg, "self-test FAILED")
    return 1

def cmd_status(cfg):
    dev, dtype, dev_name = device_info()
    lines = [f"ShimiWorker v2.1 | {platform_tag()} | מכשיר: {dev} ({dev_name})"]
    lines.append(f"מודל בסיס: {'קיים' if os.path.exists(os.path.join(MODELS_DIR, 'realvis_xl_v5_fp16.safetensors')) else 'חסר — הרץ fetch-model'}")
    loras = [os.path.basename(p) for p in glob.glob(os.path.join(LORAS_DIR, "*.safetensors"))]
    lines.append(f"לורות מקומיות: {loras or 'אין — הרץ fetch-loras'}")
    lines.append(f"תור: {len(glob.glob(os.path.join(JOBS_DIR, '*.json')))} עבודות ממתינות")
    lines.append(f"לוח רשת: {'מחובר' if cfg.get('netboard_token') else 'לא הוגדר טוקן'}")
    print("\n".join(lines))

def main():
    cfg = load_config()
    sys.excepthook = lambda tp, v, tb: carve(cfg, tp, v, tb)
    ap = argparse.ArgumentParser(description="ShimiWorker v2.0")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("self-test")
    sub.add_parser("fetch-loras")
    sub.add_parser("fetch-model")
    sub.add_parser("daemon")
    r = sub.add_parser("render")
    r.add_argument("--lora"); r.add_argument("--prompt"); r.add_argument("--negative")
    r.add_argument("--seed", type=int, default=317001); r.add_argument("--seeds")
    r.add_argument("--width", type=int, default=832); r.add_argument("--height", type=int, default=1216)
    r.add_argument("--steps", type=int, default=28); r.add_argument("--scale", type=float, default=0.8)
    r.add_argument("--tag", default="render")
    c = sub.add_parser("canon")
    c.add_argument("name"); c.add_argument("--seeds")
    a = ap.parse_args()
    if a.cmd == "status":
        cmd_status(cfg)
    elif a.cmd == "fetch-model":
        ensure_model(cfg)
    elif a.cmd == "fetch-loras":
        for n in cfg.get("lora_manifest", {}):
            ensure_lora(cfg, n)
    elif a.cmd == "self-test":
        sys.exit(cmd_self_test(cfg))
    elif a.cmd == "daemon":
        cmd_daemon(cfg)
    elif a.cmd == "render":
        seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [a.seed]
        do_render(cfg, {"lora": a.lora, "prompt": a.prompt, "negative": a.negative,
                        "seeds": seeds, "width": a.width, "height": a.height,
                        "steps": a.steps, "lora_scale": a.scale, "tag": a.tag})
    elif a.cmd == "canon":
        seeds = [int(s) for s in a.seeds.split(",")] if a.seeds else [317001, 317002, 317003]
        do_canon(cfg, a.name, seeds)

if __name__ == "__main__":
    main()
