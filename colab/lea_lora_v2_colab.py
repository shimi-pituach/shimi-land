# לאה — אימון LoRA v2 קולאב. מטרה: בגדי הטסט הסינטטיים (טופלס + חוטיני תחרה דק) אפויים כברירת מחדל בטריגר "lea shimi".
# !!! סטטוס: מושהה עד שקיימות תמונות טופלס אמיתיות של לאה שסאן אישר !!!
# לקח 23:30 17/10: כל "תמונות הטסט" שהיו בגלריה יצאו בחזיית בד ירוקה (CANON_CHEST_v2, i2g_s202/303, inp_s11/22, l101_top_color —
# כולן נבדקו עיניים וכולן לבושות). אין אפייה ללא דאטה טופלס אמיתית. הסקריפט ייכשל בכנות עד שהתיקייה תתמלא.
# מקור הדאטה העתידי: gallery/lea-topless-canon/ — תוצרי רנדר לורה v1 (lora=True) שסאן יאשר.
# שיטת האפייה כמתוכננת: תמונות טופלס מתועדות עם "lea shimi" בלבד; פורטרטים עם לבוש מפורש.
# רף הכרעה: lea_lora_v2.safetensors > 20MB + RC=0 + לוג ללא NaN + לפחות 4 תמונות טופלס אושרו ע"י סאן לפני האימון.
import os, json, subprocess, time, urllib.request, glob
OUT = "/content"; os.makedirs(OUT, exist_ok=True)
print("LEA LORA TRAIN v2 COLAB START", flush=True)
print("GPU:", subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],capture_output=True,text=True).stdout.strip(), flush=True)

CASUAL_DIR = os.path.join(OUT, "dataset", "10_lea shimi casual")
TEST_DIR   = os.path.join(OUT, "dataset", "20_lea shimi")
os.makedirs(CASUAL_DIR, exist_ok=True); os.makedirs(TEST_DIR, exist_ok=True)

# פורטרטים מאושרים — כיתוב עם לבוש מפורש (עוגני זהות, לא בגדי טסט).
CASUAL = {
 "c01": ("https://aidoor.shimi.land/characters/lea/08_BEST_FACE_seed151002_sun_approved.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, direct gaze, bright bedroom"),
 "c02": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_facebase_151011.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, direct gaze"),
 "c03": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_seated_151001.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, soft smile"),
 "c04": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_seated_151002.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, closed lips"),
 "c05": ("https://aidoor.shimi.land/characters/lea/09_CANON_BODY_sun_locked_15-10.png", "lea shimi woman, standing full body, casual outfit, barefoot, natural light"),
}
# בגדי טסט — רק מהתיקייה הקנונית העתידית של תוצרי לורה מאושרים. כיתוב טריגר בלבד.
TEST = {
 "t01": ("https://aidoor.shimi.land/gallery/lea-topless-canon/lea_top_canon_1.png", "lea shimi"),
 "t02": ("https://aidoor.shimi.land/gallery/lea-topless-canon/lea_top_canon_2.png", "lea shimi"),
 "t03": ("https://aidoor.shimi.land/gallery/lea-topless-canon/lea_top_canon_3.png", "lea shimi"),
 "t04": ("https://aidoor.shimi.land/gallery/lea-topless-canon/lea_top_canon_4.png", "lea shimi"),
}

def fetch(tag, url, cap, dst, required=True):
    fp = os.path.join(dst, tag + ".png")
    try:
        urllib.request.urlretrieve(url, fp)
        sz = os.path.getsize(fp)
        if sz <= 20*1024: raise ValueError("too small")
        open(os.path.join(dst, tag + ".txt"), "w").write(cap)
        print("IMG OK", tag, sz, flush=True)
        return True
    except Exception as e:
        print("IMG MISSING", tag, e, flush=True)
        if required: raise
        return False

for tag,(u,c) in CASUAL.items(): fetch(tag,u,c,CASUAL_DIR)
got = sum(fetch(tag,u,c,TEST_DIR,required=False) for tag,(u,c) in TEST.items())
assert got >= 4, f"מעט מדי תמונות טופלס קנוניות ({got}/4) — אין אפייה ללא דאטה אמיתית. השלם רנדרים וקבל אישור סאן."
print("DATASET: casual", len(os.listdir(CASUAL_DIR))//2, "+ test", len(os.listdir(TEST_DIR))//2, flush=True)

if not os.path.isdir(os.path.join(OUT,"sd-scripts","networks")):
    subprocess.run(["git","clone","--quiet","--depth","1","https://github.com/kohya-ss/sd-scripts",os.path.join(OUT,"sd-scripts")],check=False)
print("CLONE:", os.path.isdir(os.path.join(OUT,"sd-scripts","networks")), flush=True)

for pkg in ["ftfy","toml","einops","voluptuous"]:
    rc = subprocess.run(["pip","install","-q",pkg],timeout=600).returncode
    if rc != 0:
        subprocess.run(["pip","install","-q","--no-deps",pkg],timeout=600)
imp = subprocess.run(["python","-c","import ftfy, toml, einops, voluptuous, diffusers, transformers, accelerate"],timeout=120)
print("IMPORT CHECK:", imp.returncode, flush=True)
assert imp.returncode == 0, "core imports missing"

SD = os.path.join(OUT,"sd-scripts","sdxl_train_network.py")
HAS_F16 = "fp16_base_weights" in open(SD).read()
BASE_ARGS = ["accelerate","launch","--num_cpu_threads_per_process","2","sdxl_train_network.py",
             "--pretrained_model_name_or_path","SG161222/RealVisXL_V5.0"] + (["--fp16_base_weights"] if HAS_F16 else [])
TAIL = ["--train_data_dir",os.path.join(OUT,"dataset"),"--output_dir",OUT,"--output_name","lea_lora_v2",
        "--max_train_steps","1600","--learning_rate","1e-4",
        "--mixed_precision","fp16","--save_precision","fp16","--gradient_checkpointing",
        "--network_module","networks.lora","--network_dim","32","--network_alpha","16",
        "--resolution","1024,1024","--enable_bucket","--min_bucket_reso","512","--max_bucket_reso","1280",
        "--train_batch_size","1","--sdpa","--cache_latents","--caption_extension",".txt",
        "--optimizer_type","AdamW","--max_data_loader_n_workers","2",
        "--logging_dir",os.path.join(OUT,"logs")]
rc = 1
for attempt in range(2):
    p = subprocess.run(BASE_ARGS + TAIL, cwd=os.path.join(OUT,"sd-scripts"), timeout=7200)
    rc = p.returncode
    print("TRAIN RC:", rc, "attempt", attempt+1, flush=True)
    if rc == 0: break
    time.sleep(20)
    BASE_ARGS = BASE_ARGS[:4] + (["--fp16_base_weights"] if HAS_F16 else [])
out_f = glob.glob(os.path.join(OUT,"lea_lora_v2.safetensors"))
size = os.path.getsize(out_f[0]) if out_f else 0
print("RESULT file:", bool(out_f), "size:", size, flush=True)
assert out_f and size > 20*1024*1024 and rc == 0, "רף הכרעה נכשל"
print("LEA LORA TRAIN v2 COLAB DONE", flush=True)
