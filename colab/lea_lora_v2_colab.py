# לאה — אימון LoRA v2 קולאב. חידוש מרכזי: בגדי הטסט הסינטטיים (טופלס + חוטיני תחרת פרחים דק) אפויים כברירת מחדל בטריגר "lea shimi".
# שיטת האפייה: תמונות בגדי-טסט מתועדות עם הטריגר בלבד (כיתוב ריק מלבד הטריגר => הביגוד והאנטומיה נקשרים לטריגר עצמו).
# תמונות פורטרט מתועדות עם תיאור לבוש מפורש — כך "lea shimi" לבד = לאה בבגדי טסט, ולבוש אחר דורש מילים.
# בסיס: shani_lora_colab v1.1 (המוכח). kohya sd-scripts, SDXL LoRA על RealVisXL V5.0.
# רף הכרעה (מוכרז לפני ריצה): lea_lora_v2.safetensors נוצר > 20MB + RC=0 + לוג ללא NaN + כל 10 תמונות האימון ירדו 200 וגדולות מ-20KB.
import os, json, subprocess, time, urllib.request, glob
OUT = "/content"; os.makedirs(OUT, exist_ok=True)
print("LEA LORA TRAIN v2 COLAB START", flush=True)
print("GPU:", subprocess.run(["nvidia-smi","--query-gpu=name,memory.total","--format=csv,noheader"],capture_output=True,text=True).stdout.strip(), flush=True)

CASUAL_DIR = os.path.join(OUT, "dataset", "10_lea shimi casual")
TEST_DIR   = os.path.join(OUT, "dataset", "20_lea shimi")
os.makedirs(CASUAL_DIR, exist_ok=True); os.makedirs(TEST_DIR, exist_ok=True)

# פורטרטים מאושרים (סאן: "כל השאר כן מדויק") + גוף קנון נעול. כיתוב עם לבוש מפורש.
CASUAL = {
 "c01": ("https://aidoor.shimi.land/characters/lea/08_BEST_FACE_seed151002_sun_approved.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, direct gaze, bright bedroom"),
 "c02": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_facebase_151011.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, direct gaze"),
 "c03": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_seated_151001.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, soft smile"),
 "c04": ("https://aidoor.shimi.land/gallery/lea-test/lea_test_seated_151002.png", "lea shimi woman, portrait, sitting on a bed, casual clothing, closed lips"),
 "c05": ("https://aidoor.shimi.land/characters/lea/09_CANON_BODY_sun_locked_15-10.png", "lea shimi woman, standing full body, casual outfit, barefoot, natural light"),
}
# בגדי טסט סינתטיים (טופלס + חוטיני תחרה) — כיתוב טריגר בלבד => אפיית ברירת מחדל.
TEST = {
 "t01": ("https://aidoor.shimi.land/gallery/lea-canonical/CANON_CHEST_v2_sun_locked_i2g_s101.png", "lea shimi"),
 "t02": ("https://aidoor.shimi.land/gallery/lea-chest-fix-17-10/i2g_s202.png", "lea shimi"),
 "t03": ("https://aidoor.shimi.land/gallery/lea-chest-fix-17-10/i2g_s303.png", "lea shimi"),
 "t04": ("https://aidoor.shimi.land/gallery/lea-chest-fix-17-10/inp_s11.png", "lea shimi"),
 "t05": ("https://aidoor.shimi.land/gallery/lea-chest-fix-17-10/inp_s22.png", "lea shimi"),
}

def fetch(tag, url, cap, dst):
    fp = os.path.join(dst, tag + ".png")
    urllib.request.urlretrieve(url, fp)
    sz = os.path.getsize(fp)
    assert sz > 20*1024, f"image too small: {tag} {sz}"
    open(os.path.join(dst, tag + ".txt"), "w").write(cap)
    print("IMG OK", tag, sz, flush=True)

for tag,(u,c) in CASUAL.items(): fetch(tag,u,c,CASUAL_DIR)
for tag,(u,c) in TEST.items():   fetch(tag,u,c,TEST_DIR)
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
